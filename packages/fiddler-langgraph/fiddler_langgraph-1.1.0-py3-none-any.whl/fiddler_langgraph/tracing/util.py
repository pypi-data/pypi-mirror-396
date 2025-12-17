import datetime
import importlib.metadata
import json
import logging
from dataclasses import asdict, is_dataclass
from typing import Any

from packaging import version as pkg_version
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class _LanggraphJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder for LangGraph objects.

    This encoder handles the serialization of common LangGraph and Pydantic
    objects into JSON-serializable formats.
    """

    # pylint: disable=too-many-return-statements
    def default(self, o: Any) -> Any:
        """Serializes an object to a JSON-compatible format.

        This method provides custom serialization for the following types:
        - Dataclasses
        - Objects with a `to_json` method
        - Pydantic models
        - Datetime objects

        If an object cannot be serialized, it is converted to an empty string.

        Args:
            o: The object to serialize.

        Returns:
            A JSON-serializable representation of the object.
        """
        if is_dataclass(o):
            return asdict(o)  # type: ignore[arg-type]

        if hasattr(o, 'to_json'):
            return o.to_json()

        if isinstance(o, BaseModel) and hasattr(o, 'model_dump_json'):
            return o.model_dump_json()

        if isinstance(o, datetime.datetime):
            return o.isoformat()

        try:
            return str(o)
        except (TypeError, ValueError) as e:
            logger.debug('Failed to serialize object of type %s: %s', type(o).__name__, str(e))
            return ''


def _get_package_version(package_name: str) -> pkg_version.Version:
    """Get the version of a package."""
    try:
        version = importlib.metadata.version(package_name)
        return pkg_version.parse(version)
    except importlib.metadata.PackageNotFoundError:
        raise ImportError(f'Package {package_name} is not installed')


def _check_langgraph_version(
    langgraph_version: pkg_version.Version,
) -> None:
    """Check if the installed LangGraph version is compatible with the version of fiddler-langgraph."""

    if langgraph_version is None:
        raise ImportError('Either langgraph or langchain_core should be installed')

    # check compatibility range
    min_langgraph_version = pkg_version.parse('0.3.28')
    max_langgraph_version = pkg_version.parse('1.1.0')

    if langgraph_version < min_langgraph_version or langgraph_version > max_langgraph_version:
        raise ImportError(
            f'langgraph version {langgraph_version.public} is not compatible. '
            f'fiddler-langgraph requires langgraph >= 0.3.28 and < 1.1.0. '
        )
