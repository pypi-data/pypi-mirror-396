from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.uk_local_authority_breakdown_with_values_by_local_authority import (
        UKLocalAuthorityBreakdownWithValuesByLocalAuthority,
    )


T = TypeVar("T", bound="UKLocalAuthorityBreakdownWithValues")


@_attrs_define
class UKLocalAuthorityBreakdownWithValues:
    """
    Attributes:
        by_local_authority (UKLocalAuthorityBreakdownWithValuesByLocalAuthority):
    """

    by_local_authority: UKLocalAuthorityBreakdownWithValuesByLocalAuthority
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        by_local_authority = self.by_local_authority.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "by_local_authority": by_local_authority,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.uk_local_authority_breakdown_with_values_by_local_authority import (
            UKLocalAuthorityBreakdownWithValuesByLocalAuthority,
        )

        d = dict(src_dict)
        by_local_authority = UKLocalAuthorityBreakdownWithValuesByLocalAuthority.from_dict(d.pop("by_local_authority"))

        uk_local_authority_breakdown_with_values = cls(
            by_local_authority=by_local_authority,
        )

        uk_local_authority_breakdown_with_values.additional_properties = d
        return uk_local_authority_breakdown_with_values

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
