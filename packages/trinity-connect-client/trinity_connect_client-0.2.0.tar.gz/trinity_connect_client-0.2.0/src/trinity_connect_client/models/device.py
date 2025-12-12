"""
Device-related models for Connect API.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import BaseModel


@dataclass
class Device(BaseModel):
    """Represents a device from the Connect API."""

    id: int
    url: str
    name: str
    description: str
    state: int
    t_type: int
    tpp_id: Optional[int]
    company: int
    folder: int
    state_display: str
    t_type_display: str
    company_name: str
    folder_name: str
    company_url: str
    folder_url: str
    aux_values_url: str
    uid: str
    imei: str
    imei2: str
    serial_number: str
    comm_interval_contract: int
    comm_state: int
    comm_state_display: str
    youngest_comm_timestamp: str
    command_model: int
    data_lens: int
    event_lens: Optional[int]
    profile: Optional[int]
    commands_url: str
    latest_data_url: str
    events_url: str
    meta_url: str
    geo_url: str
    category_url: str
    tags_url: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        """
        Create a Device instance from a dictionary.

        :param data: Dictionary containing device data
        :return: Device instance
        """
        return cls(
            id=data["id"],
            url=data["url"],
            name=data["name"],
            description=data["description"],
            state=data["state"],
            t_type=data["t_type"],
            tpp_id=data.get("tpp_id"),
            company=data["company"],
            folder=data["folder"],
            state_display=data["state_display"],
            t_type_display=data["t_type_display"],
            company_name=data["company_name"],
            folder_name=data["folder_name"],
            company_url=data["company_url"],
            folder_url=data["folder_url"],
            aux_values_url=data["aux_values_url"],
            uid=data["uid"],
            imei=data["imei"],
            imei2=data["imei2"],
            serial_number=data["serial_number"],
            comm_interval_contract=data["comm_interval_contract"],
            comm_state=data["comm_state"],
            comm_state_display=data["comm_state_display"],
            youngest_comm_timestamp=data["youngest_comm_timestamp"],
            command_model=data["command_model"],
            data_lens=data["data_lens"],
            event_lens=data.get("event_lens"),
            profile=data.get("profile"),
            commands_url=data["commands_url"],
            latest_data_url=data["latest_data_url"],
            events_url=data["events_url"],
            meta_url=data["meta_url"],
            geo_url=data["geo_url"],
            category_url=data["category_url"],
            tags_url=data["tags_url"],
        )


@dataclass
class DeviceData(BaseModel):
    """Represents device data/telemetry from the Connect API."""

    # Generic structure for device data - can be extended based on actual API response
    data: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceData":
        """
        Create a DeviceData instance from a dictionary.

        :param data: Dictionary containing device data
        :return: DeviceData instance
        """
        return cls(data=data)


@dataclass
class DeviceEvent(BaseModel):
    """Represents a device event from the Connect API."""

    # Generic structure for device events - can be extended based on actual API response
    events: list[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceEvent":
        """
        Create a DeviceEvent instance from a dictionary.

        :param data: Dictionary containing event data
        :return: DeviceEvent instance
        """
        # If data is already a list, wrap it
        if isinstance(data, list):
            return cls(events=data)
        # If data has an 'events' key, use that
        return cls(events=data.get("events", []))


@dataclass
class DeviceCommand(BaseModel):
    """Represents a device command from the Connect API."""

    # Generic structure for device commands - can be extended based on actual API response
    commands: list[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceCommand":
        """
        Create a DeviceCommand instance from a dictionary.

        :param data: Dictionary containing command data
        :return: DeviceCommand instance
        """
        # If data is already a list, wrap it
        if isinstance(data, list):
            return cls(commands=data)
        # If data has a 'commands' key, use that
        return cls(commands=data.get("commands", []))
