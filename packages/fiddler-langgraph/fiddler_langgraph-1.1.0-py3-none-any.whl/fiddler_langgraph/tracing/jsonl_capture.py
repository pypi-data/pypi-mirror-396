"""JSONL data capture module for simplified span data in structured format."""

import json
import os
import threading
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from fiddler_langgraph.core.attributes import FiddlerSpanAttributes, SpanType


class JSONLSpanCapture:
    """Captures OpenTelemetry span data and saves it to JSONL format with structured fields."""

    def __init__(self, jsonl_file_path: str | None = None):
        """Initialize JSONL capture.

        Args:
            jsonl_file_path: Path to the JSONL file. If None, uses FIDDLER_JSONL_FILE env var (default: 'fiddler_trace_data.jsonl')
        """
        if jsonl_file_path is None:
            jsonl_file_path = os.getenv('FIDDLER_JSONL_FILE', 'fiddler_trace_data.jsonl')

        self.jsonl_file_path = Path(jsonl_file_path)
        self._lock = threading.Lock()
        self._ensure_jsonl_file()

    def _ensure_jsonl_file(self) -> None:
        """Ensure the JSONL file exists and has proper headers."""
        try:
            if not self.jsonl_file_path.exists():
                self.jsonl_file_path.parent.mkdir(parents=True, exist_ok=True)
                self.jsonl_file_path.touch()
        except Exception as e:
            print(f'Warning: Could not create JSONL file {self.jsonl_file_path}: {e}')

    def capture_span(self, span: ReadableSpan) -> None:
        """Capture a span and write it to JSONL file."""
        try:
            span_data = self._convert_span_to_structured_format(span)
            self._write_span_to_jsonl(span_data)
        except Exception as e:
            print(f'Error capturing span to JSONL: {e}')

    def _convert_span_to_structured_format(self, span: ReadableSpan) -> dict[str, Any]:
        """Convert ReadableSpan to structured format for JSONL export."""
        # Extract basic span information
        span_data = {
            'trace_id': format(span.get_span_context().trace_id, '032x'),
            'span_id': format(span.get_span_context().span_id, '016x'),
            'parent_span_id': format(span.parent.span_id, '016x') if span.parent else '',
            'root_span_id': format(
                span.get_span_context().trace_id, '032x'
            ),  # Use trace_id as root_span_id
            'span_name': span.name,
            'span_kind': span.kind.name if span.kind else 'CLIENT',
            'start_time': (
                datetime.fromtimestamp(span.start_time / 1_000_000_000, tz=timezone.utc).isoformat()
                if span.start_time is not None
                else ''
            ),
            'end_time': (
                datetime.fromtimestamp(span.end_time / 1_000_000_000, tz=timezone.utc).isoformat()
                if span.end_time is not None
                else ''
            ),
            'duration_ms': (
                int((span.end_time - span.start_time) / 1_000_000)
                if span.end_time is not None and span.start_time is not None
                else 0
            ),
            'status_code': span.status.status_code.name if span.status else 'OK',
            'status_message': (
                span.status.description if span.status and span.status.description else ''
            ),
        }

        # Extract attributes and map them to structured fields
        attributes = dict(span.attributes) if span.attributes else {}

        # Span type and agent info
        span_data['span_type'] = attributes.get(FiddlerSpanAttributes.TYPE, SpanType.OTHER)
        span_data['agent_name'] = attributes.get(FiddlerSpanAttributes.AGENT_NAME, '')
        span_data['agent_id'] = attributes.get(FiddlerSpanAttributes.AGENT_ID, '')
        span_data['conversation_id'] = attributes.get(FiddlerSpanAttributes.CONVERSATION_ID, '')

        # Model information
        span_data['model_name'] = attributes.get(FiddlerSpanAttributes.LLM_REQUEST_MODEL, '')
        span_data['model_provider'] = attributes.get(FiddlerSpanAttributes.LLM_SYSTEM, '')

        # LLM inputs/outputs
        span_data['llm_input_system'] = attributes.get(FiddlerSpanAttributes.LLM_INPUT_SYSTEM, '')
        span_data['llm_input_user'] = attributes.get(FiddlerSpanAttributes.LLM_INPUT_USER, '')
        span_data['llm_output'] = attributes.get(FiddlerSpanAttributes.LLM_OUTPUT, '')
        span_data['llm_context'] = attributes.get(FiddlerSpanAttributes.LLM_CONTEXT, '')

        # Tool information
        span_data['tool_name'] = attributes.get(FiddlerSpanAttributes.TOOL_NAME, '')
        span_data['tool_input'] = attributes.get(FiddlerSpanAttributes.TOOL_INPUT, '')
        span_data['tool_output'] = attributes.get(FiddlerSpanAttributes.TOOL_OUTPUT, '')
        span_data['tool_definitions'] = attributes.get(FiddlerSpanAttributes.TOOL_DEFINITIONS, '')

        # Library versions (from resource if available)
        resource_attributes = (
            dict(span.resource.attributes) if span.resource and span.resource.attributes else {}
        )
        span_data['service_name'] = resource_attributes.get('service.name', '')
        span_data['service_version'] = resource_attributes.get('service.version', '')
        span_data['telemetry_sdk_name'] = resource_attributes.get('telemetry.sdk.name', '')
        span_data['telemetry_sdk_version'] = resource_attributes.get('telemetry.sdk.version', '')
        span_data['application_id'] = resource_attributes.get('application.id', '')

        # Custom metadata and tags
        custom_attributes = {}
        for key, value in attributes.items():
            if not key.startswith(('gen_ai.', 'fiddler.', 'service.', 'telemetry.')):
                custom_attributes[key] = value

        span_data['custom_attributes'] = json.dumps(custom_attributes) if custom_attributes else ''

        # Exception information
        exception_info = []
        if hasattr(span, 'events') and span.events:
            for event in span.events:
                if event.name == 'exception':
                    event_attrs = dict(event.attributes) if event.attributes else {}
                    exception_info.append(
                        {
                            'type': event_attrs.get('exception.type', ''),
                            'message': event_attrs.get('exception.message', ''),
                            'stacktrace': event_attrs.get('exception.stacktrace', ''),
                        }
                    )

        span_data['exception_info'] = json.dumps(exception_info) if exception_info else ''

        return span_data

    def _write_span_to_jsonl(self, span_data: dict[str, Any]) -> None:
        """Write span data to JSONL file."""
        with self._lock:
            try:
                with self.jsonl_file_path.open('a', encoding='utf-8') as f:
                    json.dump(span_data, f, ensure_ascii=False)
                    f.write('\n')
            except Exception as e:
                print(f'Error writing to JSONL file {self.jsonl_file_path}: {e}')


class JSONLSpanExporter(SpanExporter):
    """SpanExporter that captures spans using JSONLSpanCapture."""

    def __init__(self, jsonl_capture: JSONLSpanCapture):
        """Initialize the exporter.

        Args:
            jsonl_capture: The JSONLSpanCapture instance to use for capturing spans
        """
        self.jsonl_capture = jsonl_capture

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans by capturing them with JSONLSpanCapture."""
        try:
            for span in spans:
                self.jsonl_capture.capture_span(span)
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f'Error exporting spans to JSONL: {e}')
            return SpanExportResult.FAILURE


def initialize_jsonl_capture(jsonl_file_path: str | None = None) -> JSONLSpanCapture:
    """Initialize a JSONLSpanCapture instance.

    Args:
        jsonl_file_path: Path to the JSONL file. If None, uses FIDDLER_JSONL_FILE env var

    Returns:
        JSONLSpanCapture: The initialized capture instance
    """
    return JSONLSpanCapture(jsonl_file_path=jsonl_file_path)
