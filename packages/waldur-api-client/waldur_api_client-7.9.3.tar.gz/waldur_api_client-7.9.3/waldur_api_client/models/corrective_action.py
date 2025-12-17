from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.category_enum import CategoryEnum
from ..models.severity_enum import SeverityEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.corrective_action_metadata import CorrectiveActionMetadata


T = TypeVar("T", bound="CorrectiveAction")


@_attrs_define
class CorrectiveAction:
    """
    Attributes:
        label (str):
        url (str):
        category (CategoryEnum):
        severity (SeverityEnum):
        method (Union[Unset, str]):  Default: 'GET'.
        api_endpoint (Union[Unset, bool]):  Default: False.
        confirmation_required (Union[Unset, bool]):  Default: False.
        permissions_required (Union[Unset, list[str]]):
        metadata (Union[Unset, CorrectiveActionMetadata]):
    """

    label: str
    url: str
    category: CategoryEnum
    severity: SeverityEnum
    method: Union[Unset, str] = "GET"
    api_endpoint: Union[Unset, bool] = False
    confirmation_required: Union[Unset, bool] = False
    permissions_required: Union[Unset, list[str]] = UNSET
    metadata: Union[Unset, "CorrectiveActionMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        url = self.url

        category = self.category.value

        severity = self.severity.value

        method = self.method

        api_endpoint = self.api_endpoint

        confirmation_required = self.confirmation_required

        permissions_required: Union[Unset, list[str]] = UNSET
        if not isinstance(self.permissions_required, Unset):
            permissions_required = self.permissions_required

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "url": url,
                "category": category,
                "severity": severity,
            }
        )
        if method is not UNSET:
            field_dict["method"] = method
        if api_endpoint is not UNSET:
            field_dict["api_endpoint"] = api_endpoint
        if confirmation_required is not UNSET:
            field_dict["confirmation_required"] = confirmation_required
        if permissions_required is not UNSET:
            field_dict["permissions_required"] = permissions_required
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.corrective_action_metadata import CorrectiveActionMetadata

        d = dict(src_dict)
        label = d.pop("label")

        url = d.pop("url")

        category = CategoryEnum(d.pop("category"))

        severity = SeverityEnum(d.pop("severity"))

        method = d.pop("method", UNSET)

        api_endpoint = d.pop("api_endpoint", UNSET)

        confirmation_required = d.pop("confirmation_required", UNSET)

        permissions_required = cast(list[str], d.pop("permissions_required", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CorrectiveActionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CorrectiveActionMetadata.from_dict(_metadata)

        corrective_action = cls(
            label=label,
            url=url,
            category=category,
            severity=severity,
            method=method,
            api_endpoint=api_endpoint,
            confirmation_required=confirmation_required,
            permissions_required=permissions_required,
            metadata=metadata,
        )

        corrective_action.additional_properties = d
        return corrective_action

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
