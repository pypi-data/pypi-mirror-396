"""
Organisation-related models for Connect API.
"""

from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseModel


@dataclass
class Company(BaseModel):
    """Represents a company from the Connect API."""

    id: int
    url: str
    name: str
    state: int
    state_display: str
    is_ee: bool
    url_profile: str
    folder_url: str
    url_folder_tree: str
    url_sims: str
    apn_urls: str
    url_devices: str
    url_budgets: str
    url_access: str
    url_tags: str
    url_contracts: str
    url_adaptations: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Company":
        """
        Create a Company instance from a dictionary.

        :param data: Dictionary containing company data
        :return: Company instance
        """
        return cls(
            id=data["id"],
            url=data["url"],
            name=data["name"],
            state=data["state"],
            state_display=data["state_display"],
            is_ee=data["is_ee"],
            url_profile=data["url_profile"],
            folder_url=data["folder_url"],
            url_folder_tree=data["url_folder_tree"],
            url_sims=data["url_sims"],
            apn_urls=data["apn_urls"],
            url_devices=data["url_devices"],
            url_budgets=data["url_budgets"],
            url_access=data["url_access"],
            url_tags=data["url_tags"],
            url_contracts=data["url_contracts"],
            url_adaptations=data["url_adaptations"],
        )


@dataclass
class Folder(BaseModel):
    """Represents a folder from the Connect API."""

    id: int
    url: str
    name: str
    path: str
    human_path: str
    parent: int
    url_sims: str
    url_devices: str
    tree_id: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Folder":
        """
        Create a Folder instance from a dictionary.

        :param data: Dictionary containing folder data
        :return: Folder instance
        """
        return cls(
            id=data["id"],
            url=data["url"],
            name=data["name"],
            path=data["path"],
            human_path=data["human_path"],
            parent=data["parent"],
            url_sims=data["url_sims"],
            url_devices=data["url_devices"],
            tree_id=data["tree_id"],
        )
