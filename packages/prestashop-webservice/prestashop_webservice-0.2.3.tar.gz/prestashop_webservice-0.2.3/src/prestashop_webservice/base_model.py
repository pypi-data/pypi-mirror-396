from dataclasses import fields
from typing import Any, TypeVar

from prestashop_webservice.client import Client
from prestashop_webservice.params import Params

T = TypeVar("T")


class BaseModel:
    """Base class for model queries with automatic dataclass conversion."""

    _data_class: type[Any] | None = None

    def __init__(self, client: Client):
        self.client = client

    @staticmethod
    def _to_list(result: dict | list) -> list[dict]:
        """Ensure result is always a list.

        Args:
            result: Result from API call (dict or list)

        Returns:
            List of dictionaries
        """
        if isinstance(result, dict):
            return [result] if result else []
        return result or []

    def _query(self, endpoint: str, params: Params | None = None, response_key: str = "") -> Any:
        """Override Client._query to return dataclass instances instead of dicts.

        Args:
            endpoint: API endpoint to query
            params: Query parameters
            response_key: Key to extract from JSON response

        Returns:
            Single dataclass instance or list of dataclass instances
        """
        # Call parent's _query to get raw dict/list
        result = self.client._query(endpoint, params, response_key)

        # If no data_class is set, return raw result
        if self._data_class is None:
            return result

        # Convert to list and instantiate dataclasses
        results = self._to_list(result)
        instances = []
        for r in results:
            # Filter out unknown fields to avoid TypeError
            if self._data_class:
                field_names = {f.name for f in fields(self._data_class)}
                filtered = {k: v for k, v in r.items() if k in field_names}
                instances.append(self._data_class(**filtered))

        # Return single instance if result was dict, list if it was list
        if isinstance(result, dict):
            return instances[0] if instances else None
        return instances
