"""Core client for Fiddler instrumentation."""

import os
import uuid
from typing import Any
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import Compression, OTLPSpanExporter
from opentelemetry.sdk.resources import (
    OTELResourceDetector,
    ProcessResourceDetector,
    Resource,
    get_aggregated_resources,
)
from opentelemetry.sdk.trace import SpanLimits, TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from fiddler_langgraph.core.attributes import FiddlerResourceAttributes
from fiddler_langgraph.core.span_processor import FiddlerSpanProcessor
from fiddler_langgraph.tracing.jsonl_capture import JSONLSpanExporter, initialize_jsonl_capture

# Defaults are too permissive.
# Set restrictive defaults for span limits - can be overridden by the user
# See https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-sdk/src/opentelemetry/sdk/environment_variables/__init__.py
_default_span_limits = SpanLimits(
    max_events=32,
    max_links=32,
    max_span_attributes=32,
    max_event_attributes=32,
    max_link_attributes=32,
    max_span_attribute_length=2048,
)


class FiddlerClient:
    """The main client for instrumenting Generative AI applications with Fiddler observability.

    This client configures and manages the OpenTelemetry tracer that sends telemetry data
    to the Fiddler platform for monitoring, analysis, and debugging of your AI agents
    and workflows.

    Attributes:
        application_id (str): The UUID4 identifier for the application.
        url (str): The Fiddler backend URL.
        api_key (str): The API key for Fiddler.
        resource (Resource): The OpenTelemetry resource for the client.
        span_limits (SpanLimits | None): OpenTelemetry span limits configuration.
        sampler (sampling.Sampler | None): OpenTelemetry sampling configuration.
        compression (Compression): OTLP export compression type.
        jsonl_capture_enabled (bool): Whether JSONL capture is enabled.
        jsonl_file_path (str): Path to the JSONL file for trace data capture.
    """

    def __init__(
        self,
        api_key: str,
        application_id: str,
        url: str,
        console_tracer: bool = False,
        span_limits: SpanLimits | None = _default_span_limits,
        sampler: sampling.Sampler | None = None,
        compression: Compression = Compression.Gzip,
        jsonl_capture_enabled: bool = False,
        jsonl_file_path: str = 'fiddler_trace_data.jsonl',
    ):
        """Initializes the FiddlerClient.

        This sets up the configuration for the OpenTelemetry tracer that will
        be used to send data to Fiddler.

        Args:
            api_key (str): The API key for authenticating with the Fiddler backend. **Required**.
            application_id (str): The unique identifier (UUID4) for the application. **Required**.
            url (str): The base URL for your Fiddler instance. This is specific to your
                deployment, whether hosted, VPC-deployed, on-premise, or local development
                (e.g., `https://your-instance.fiddler.ai`, `http://localhost:4318`). **Required**.
            console_tracer (bool): If True, traces will be printed to the console
                instead of being sent to the Fiddler backend. Useful for debugging.
                Defaults to `False`.
            span_limits (SpanLimits | None): Configuration for span limits, such as the
                maximum number of attributes or events. Defaults to a restrictive
                set of internal limits (32 events/links/attributes, 2048 char limit).
            sampler (sampling.Sampler | None): The sampler for deciding which spans to record.
                Defaults to `None`, which uses the parent-based always-on OpenTelemetry sampler
                (100% sampling).
            compression (Compression): The compression for exporting traces.
                Can be `Compression.Gzip`, `Compression.Deflate`, or `Compression.NoCompression`.
                Defaults to `Compression.Gzip` (recommended for production).
            jsonl_capture_enabled (bool): Whether to enable JSONL capture of trace data.
                When enabled, all span data will be captured and saved to a JSONL file
                in OpenTelemetry format for offline analysis. Defaults to `False`.
            jsonl_file_path (str): Path to the JSONL file where trace data will be saved.
                Only used when `jsonl_capture_enabled` is `True`. Defaults to
                "fiddler_trace_data.jsonl".

        Raises:
            ValueError: If `application_id` is not a valid UUID4 or if the
                `url` is not a valid HTTP/HTTPS URL.

        Examples:
            Basic connection to your Fiddler instance:

            .. code-block:: python

                client = FiddlerClient(
                    api_key='YOUR_API_KEY',
                    application_id='YOUR_APPLICATION_ID',
                    url='https://your-instance.fiddler.ai',
                )

            High-volume applications with custom configuration:

            .. code-block:: python

                from opentelemetry.sdk.trace import SpanLimits, sampling
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import Compression

                client = FiddlerClient(
                    api_key='YOUR_API_KEY',
                    application_id='YOUR_APPLICATION_ID',
                    url='https://your-instance.fiddler.ai',
                    span_limits=SpanLimits(max_span_attributes=64),
                    sampler=sampling.TraceIdRatioBased(0.1),  # Sample 10% of traces
                    compression=Compression.Gzip,
                )

            Local development with console output:

            .. code-block:: python

                client = FiddlerClient(
                    api_key='dev-key',
                    application_id='00000000-0000-0000-0000-000000000000',
                    url='http://localhost:4318',
                    console_tracer=True,  # Print traces to console for debugging
                )
        """
        # Validate application_id is a valid UUID4

        parsed_uuid = uuid.UUID(application_id)
        if parsed_uuid.version != 4:
            raise ValueError(
                f'application_id must be a valid UUID4 (version 4), got version {parsed_uuid.version}'
            )
        # Store the validated UUID as a string
        self.application_id = str(parsed_uuid)

        # Validate URL is a valid URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError('URL must have a valid scheme and netloc')
        if parsed_url.scheme not in ('http', 'https'):
            raise ValueError('URL scheme must be http or https')
        self.url = url.rstrip('/')

        self.api_key = api_key

        # fiddler sdk must have its own tracer provider and tracer
        # so we can have a separate configuration for the tracer provider than the global one.
        # Additionally, other otel libraries maybe active who may override configs of the global tracer provider.
        # we will initialize the provider and tracer when get_tracer is called
        # we need to wait for any resources to be set before initializing the provider
        # and tracer
        self._provider: TracerProvider | None = None
        self._tracer: trace.Tracer | None = None
        self._console_tracer = console_tracer

        self.span_limits = span_limits
        self.sampler = sampler
        self.compression = compression
        self.jsonl_capture_enabled = jsonl_capture_enabled
        self.jsonl_file_path = jsonl_file_path

        # Create OpenTelemetry resource with service information
        # we will update the resource with any additional attributes later
        resource = Resource.create({FiddlerResourceAttributes.APPLICATION_ID: self.application_id})
        self.resource = self._get_aggregated_resources_with_fallback(resource)

    def get_tracer_provider(self) -> TracerProvider:
        """Gets the OpenTelemetry TracerProvider instance.

        Initializes the provider on the first call.

        Returns:
            TracerProvider: The configured OpenTelemetry TracerProvider.

        Raises:
            RuntimeError: If tracer provider initialization fails.
        """
        if self._provider is None:
            self._initialize_provider()
            if self._provider is None:
                raise RuntimeError('Failed to initialize tracer provider')
        return self._provider

    def _get_aggregated_resources_with_fallback(self, initial_resource: Resource) -> Resource:
        """Gets aggregated resources with a fallback for different OpenTelemetry versions.

        This method tries to use `get_aggregated_resources` and dynamically imports
        `OsResourceDetector` if available. It falls back to the initial resource if
        aggregation fails.

        Args:
            initial_resource (Resource): The initial resource to start with.

        Returns:
            Resource: The aggregated resource.
        """
        detectors = [OTELResourceDetector(), ProcessResourceDetector()]

        # Try to add OsResourceDetector if available (OpenTelemetry >= 1.19)
        try:
            from opentelemetry.sdk.resources import OsResourceDetector

            detectors.append(OsResourceDetector())
        except ImportError:
            # OsResourceDetector not available in this version, skip it
            pass

        try:
            return get_aggregated_resources(detectors, initial_resource=initial_resource)
        except Exception:
            # Fallback to initial resource if aggregation fails
            return initial_resource

    def update_resource(self, attributes: dict[str, Any]) -> None:
        """Updates the OpenTelemetry resource with additional attributes.

        Use this to add metadata that applies to all spans, such as version numbers
        or environment names.

        > [!IMPORTANT]
        > Must be called before `get_tracer()` is invoked.

        Args:
            attributes (dict[str, Any]): Key-value pairs to add to the resource. **Required**.

        Raises:
            ValueError: If the tracer has already been initialized.

        Examples:
            .. code-block:: python

                from fiddler_langgraph import FiddlerClient
                client = FiddlerClient(api_key='...', application_id='...', url='https://your-instance.fiddler.ai')
                client.update_resource({'service.version': '1.2.3'})
        """
        if self._tracer is not None:
            raise ValueError('Cannot update resource after tracer is initialized')

        if (
            self.resource.attributes.get('service.name', '') != 'unknown_service'
            and attributes.get('service.name') is None
        ):
            # service.name defaults to unknown_service in a new resource. When merging, the new resource will override the old one.
            # so we need to keep the old service.name if it exists.
            attributes['service.name'] = self.resource.attributes['service.name']

        self.resource = self.resource.merge(Resource.create(attributes))

    def _initialize_provider(self) -> None:
        """Initializes the tracer provider.

        We are not using the default tracer provider because we want to have a
        separate configuration for the tracer provider than the global one.
        Additionally, other OTEL libraries may be active and override configs
        of the global tracer provider.
        """
        if self._provider is not None:
            return

        self._provider = TracerProvider(
            resource=self.resource,
            span_limits=self.span_limits,
            sampler=self.sampler,
        )

    def _initialize_tracer(self) -> None:
        """Initializes the OpenTelemetry tracer and registers span processors."""
        if self._tracer is not None:
            return

        # Ensure provider is initialized
        self._initialize_provider()
        assert self._provider is not None  # Type guard for mypy

        # processors are executed in order, so we add the FiddlerSpanProcessor first
        # so that it can inject the session ID and custom attributes into the spans
        self._provider.add_span_processor(FiddlerSpanProcessor())

        if self._console_tracer:
            self._provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

        otlp_exporter = OTLPSpanExporter(
            endpoint=f'{self.url}/v1/traces',
            headers={
                'authorization': f'Bearer {self.api_key}',
                'fiddler-application-id': self.application_id,
            },
            compression=self.compression,
        )
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=int(os.environ.get('OTEL_BSP_MAX_QUEUE_SIZE', '100')),
            schedule_delay_millis=int(os.environ.get('OTEL_BSP_SCHEDULE_DELAY_MILLIS', '1000')),
            max_export_batch_size=int(os.environ.get('OTEL_BSP_MAX_EXPORT_BATCH_SIZE', '10')),
            export_timeout_millis=int(os.environ.get('OTEL_BSP_EXPORT_TIMEOUT', '5000')),
        )

        self._provider.add_span_processor(span_processor)

        # Add JSONL capture if enabled
        if self.jsonl_capture_enabled:
            jsonl_capture = initialize_jsonl_capture(self.jsonl_file_path)
            jsonl_exporter = JSONLSpanExporter(jsonl_capture)
            self._provider.add_span_processor(SimpleSpanProcessor(jsonl_exporter))

        self._tracer = trace.get_tracer('fiddler.langgraph.tracer', tracer_provider=self._provider)

    def get_tracer(self) -> trace.Tracer:
        """Returns an OpenTelemetry tracer instance for creating spans.

        Initializes the tracer on the first call. This is the primary method
        for developers to get a tracer for custom instrumentation.

        Returns:
            trace.Tracer: OpenTelemetry tracer instance.

        Raises:
            RuntimeError: If tracer initialization fails.

        Examples:
            .. code-block:: python

                from fiddler_langgraph import FiddlerClient
                client = FiddlerClient(api_key='...', application_id='...', url='https://your-instance.fiddler.ai')
                tracer = client.get_tracer()
                with tracer.start_as_current_span('my-operation'):
                    print('Doing some work...')
        """
        if self._tracer is None:
            self._initialize_tracer()
            if self._tracer is None:
                raise RuntimeError('Failed to initialize tracer')
        return self._tracer
