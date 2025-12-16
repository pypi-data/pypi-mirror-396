from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.uk_local_authority_breakdown_by_local_authority import UKLocalAuthorityBreakdownByLocalAuthority


T = TypeVar("T", bound="UKLocalAuthorityBreakdownWithValuesByLocalAuthority")


@_attrs_define
class UKLocalAuthorityBreakdownWithValuesByLocalAuthority:
    """ """

    additional_properties: dict[str, UKLocalAuthorityBreakdownByLocalAuthority] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.uk_local_authority_breakdown_by_local_authority import UKLocalAuthorityBreakdownByLocalAuthority

        d = dict(src_dict)
        uk_local_authority_breakdown_with_values_by_local_authority = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = UKLocalAuthorityBreakdownByLocalAuthority.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        uk_local_authority_breakdown_with_values_by_local_authority.additional_properties = additional_properties
        return uk_local_authority_breakdown_with_values_by_local_authority

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> UKLocalAuthorityBreakdownByLocalAuthority:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: UKLocalAuthorityBreakdownByLocalAuthority) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
