from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Subscriptions")


@_attrs_define
class Subscriptions:
    """Describes peer's subscriptions in manual mode

    Attributes:
        peers (list[str]): List of peer IDs this peer subscribes to
        tracks (list[str]): List of track IDs this peer subscribes to
    """

    peers: list[str]
    tracks: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        peers = self.peers

        tracks = self.tracks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "peers": peers,
            "tracks": tracks,
        })

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        peers = cast(list[str], d.pop("peers"))

        tracks = cast(list[str], d.pop("tracks"))

        subscriptions = cls(
            peers=peers,
            tracks=tracks,
        )

        subscriptions.additional_properties = d
        return subscriptions

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
