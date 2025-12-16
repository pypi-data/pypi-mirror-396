from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.simulation_options_country import SimulationOptionsCountry
from ..models.simulation_options_scope import SimulationOptionsScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parametric_reform import ParametricReform
    from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1


T = TypeVar("T", bound="SimulationOptions")


@_attrs_define
class SimulationOptions:
    """
    Attributes:
        country (SimulationOptionsCountry): The country to simulate.
        scope (SimulationOptionsScope): The scope of the simulation.
        data (Any | None | SimulationOptionsDataType1 | str | Unset): The data to simulate.
        time_period (int | Unset): The time period to simulate. Default: 2025.
        reform (Any | None | ParametricReform | Unset): The reform to simulate.
        baseline (Any | None | ParametricReform | Unset): The baseline to simulate.
        region (None | str | Unset): The region to simulate within the country.
        subsample (int | None | Unset): How many, if a subsample, households to randomly simulate.
        title (None | str | Unset): The title of the analysis (for charts). If not provided, a default title will be
            generated. Default: '[Analysis title]'.
        include_cliffs (bool | None | Unset): Whether to include tax-benefit cliffs in the simulation analyses. If True,
            cliffs will be included. Default: False.
        model_version (None | str | Unset): The version of the country model used in the simulation. If not provided,
            the current package version will be used. If provided, this package will throw an error if the package version
            does not match. Use this as an extra safety check.
        data_version (None | str | Unset): The version of the data used in the simulation. If not provided, the current
            data version will be used. If provided, this package will throw an error if the data version does not match. Use
            this as an extra safety check.
    """

    country: SimulationOptionsCountry
    scope: SimulationOptionsScope
    data: Any | None | SimulationOptionsDataType1 | str | Unset = UNSET
    time_period: int | Unset = 2025
    reform: Any | None | ParametricReform | Unset = UNSET
    baseline: Any | None | ParametricReform | Unset = UNSET
    region: None | str | Unset = UNSET
    subsample: int | None | Unset = UNSET
    title: None | str | Unset = "[Analysis title]"
    include_cliffs: bool | None | Unset = False
    model_version: None | str | Unset = UNSET
    data_version: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.parametric_reform import ParametricReform
        from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1

        country = self.country.value

        scope = self.scope.value

        data: Any | dict[str, Any] | None | str | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, SimulationOptionsDataType1):
            data = self.data.to_dict()
        else:
            data = self.data

        time_period = self.time_period

        reform: Any | dict[str, Any] | None | Unset
        if isinstance(self.reform, Unset):
            reform = UNSET
        elif isinstance(self.reform, ParametricReform):
            reform = self.reform.to_dict()
        else:
            reform = self.reform

        baseline: Any | dict[str, Any] | None | Unset
        if isinstance(self.baseline, Unset):
            baseline = UNSET
        elif isinstance(self.baseline, ParametricReform):
            baseline = self.baseline.to_dict()
        else:
            baseline = self.baseline

        region: None | str | Unset
        if isinstance(self.region, Unset):
            region = UNSET
        else:
            region = self.region

        subsample: int | None | Unset
        if isinstance(self.subsample, Unset):
            subsample = UNSET
        else:
            subsample = self.subsample

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        include_cliffs: bool | None | Unset
        if isinstance(self.include_cliffs, Unset):
            include_cliffs = UNSET
        else:
            include_cliffs = self.include_cliffs

        model_version: None | str | Unset
        if isinstance(self.model_version, Unset):
            model_version = UNSET
        else:
            model_version = self.model_version

        data_version: None | str | Unset
        if isinstance(self.data_version, Unset):
            data_version = UNSET
        else:
            data_version = self.data_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "country": country,
                "scope": scope,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data
        if time_period is not UNSET:
            field_dict["time_period"] = time_period
        if reform is not UNSET:
            field_dict["reform"] = reform
        if baseline is not UNSET:
            field_dict["baseline"] = baseline
        if region is not UNSET:
            field_dict["region"] = region
        if subsample is not UNSET:
            field_dict["subsample"] = subsample
        if title is not UNSET:
            field_dict["title"] = title
        if include_cliffs is not UNSET:
            field_dict["include_cliffs"] = include_cliffs
        if model_version is not UNSET:
            field_dict["model_version"] = model_version
        if data_version is not UNSET:
            field_dict["data_version"] = data_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parametric_reform import ParametricReform
        from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1

        d = dict(src_dict)
        country = SimulationOptionsCountry(d.pop("country"))

        scope = SimulationOptionsScope(d.pop("scope"))

        def _parse_data(data: object) -> Any | None | SimulationOptionsDataType1 | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = SimulationOptionsDataType1.from_dict(data)

                return data_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Any | None | SimulationOptionsDataType1 | str | Unset, data)

        data = _parse_data(d.pop("data", UNSET))

        time_period = d.pop("time_period", UNSET)

        def _parse_reform(data: object) -> Any | None | ParametricReform | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reform_type_0 = ParametricReform.from_dict(data)

                return reform_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Any | None | ParametricReform | Unset, data)

        reform = _parse_reform(d.pop("reform", UNSET))

        def _parse_baseline(data: object) -> Any | None | ParametricReform | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                baseline_type_0 = ParametricReform.from_dict(data)

                return baseline_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Any | None | ParametricReform | Unset, data)

        baseline = _parse_baseline(d.pop("baseline", UNSET))

        def _parse_region(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_subsample(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        subsample = _parse_subsample(d.pop("subsample", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_include_cliffs(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        include_cliffs = _parse_include_cliffs(d.pop("include_cliffs", UNSET))

        def _parse_model_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_version = _parse_model_version(d.pop("model_version", UNSET))

        def _parse_data_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        data_version = _parse_data_version(d.pop("data_version", UNSET))

        simulation_options = cls(
            country=country,
            scope=scope,
            data=data,
            time_period=time_period,
            reform=reform,
            baseline=baseline,
            region=region,
            subsample=subsample,
            title=title,
            include_cliffs=include_cliffs,
            model_version=model_version,
            data_version=data_version,
        )

        simulation_options.additional_properties = d
        return simulation_options

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
