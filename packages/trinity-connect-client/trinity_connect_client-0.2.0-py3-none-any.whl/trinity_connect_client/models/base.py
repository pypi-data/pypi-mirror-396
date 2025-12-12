"""
Base classes for Connect API models.
"""

from typing import Any, Dict


class BaseModel:
    """Base class for all Connect API models."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create a model instance from a dictionary.

        :param data: Dictionary containing model data
        :return: Model instance
        """
        raise NotImplementedError("Subclasses must implement from_dict")
