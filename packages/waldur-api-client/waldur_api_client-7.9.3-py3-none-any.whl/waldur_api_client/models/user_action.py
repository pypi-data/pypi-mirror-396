import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.urgency_enum import UrgencyEnum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.corrective_action import CorrectiveAction


T = TypeVar("T", bound="UserAction")


@_attrs_define
class UserAction:
    """
    Attributes:
        uuid (UUID):
        action_type (str): Type of action, e.g. 'pending_order', 'expiring_resource'
        title (str):
        description (str):
        urgency (UrgencyEnum):
        is_temporarily_silenced (bool):
        is_effectively_silenced (bool):
        created (datetime.datetime):
        modified (datetime.datetime):
        related_object_name (str):
        related_object_type (str):
        corrective_actions (list['CorrectiveAction']):
        days_until_due (Union[None, int]):
        due_date (Union[None, Unset, datetime.datetime]):
        action_url (Union[Unset, str]):
        metadata (Union[Unset, str]):
        is_silenced (Union[Unset, bool]):
        silenced_until (Union[None, Unset, datetime.datetime]):
    """

    uuid: UUID
    action_type: str
    title: str
    description: str
    urgency: UrgencyEnum
    is_temporarily_silenced: bool
    is_effectively_silenced: bool
    created: datetime.datetime
    modified: datetime.datetime
    related_object_name: str
    related_object_type: str
    corrective_actions: list["CorrectiveAction"]
    days_until_due: Union[None, int]
    due_date: Union[None, Unset, datetime.datetime] = UNSET
    action_url: Union[Unset, str] = UNSET
    metadata: Union[Unset, str] = UNSET
    is_silenced: Union[Unset, bool] = UNSET
    silenced_until: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        action_type = self.action_type

        title = self.title

        description = self.description

        urgency = self.urgency.value

        is_temporarily_silenced = self.is_temporarily_silenced

        is_effectively_silenced = self.is_effectively_silenced

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        related_object_name = self.related_object_name

        related_object_type = self.related_object_type

        corrective_actions = []
        for corrective_actions_item_data in self.corrective_actions:
            corrective_actions_item = corrective_actions_item_data.to_dict()
            corrective_actions.append(corrective_actions_item)

        days_until_due: Union[None, int]
        days_until_due = self.days_until_due

        due_date: Union[None, Unset, str]
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        elif isinstance(self.due_date, datetime.datetime):
            due_date = self.due_date.isoformat()
        else:
            due_date = self.due_date

        action_url = self.action_url

        metadata = self.metadata

        is_silenced = self.is_silenced

        silenced_until: Union[None, Unset, str]
        if isinstance(self.silenced_until, Unset):
            silenced_until = UNSET
        elif isinstance(self.silenced_until, datetime.datetime):
            silenced_until = self.silenced_until.isoformat()
        else:
            silenced_until = self.silenced_until

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "action_type": action_type,
                "title": title,
                "description": description,
                "urgency": urgency,
                "is_temporarily_silenced": is_temporarily_silenced,
                "is_effectively_silenced": is_effectively_silenced,
                "created": created,
                "modified": modified,
                "related_object_name": related_object_name,
                "related_object_type": related_object_type,
                "corrective_actions": corrective_actions,
                "days_until_due": days_until_due,
            }
        )
        if due_date is not UNSET:
            field_dict["due_date"] = due_date
        if action_url is not UNSET:
            field_dict["action_url"] = action_url
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if is_silenced is not UNSET:
            field_dict["is_silenced"] = is_silenced
        if silenced_until is not UNSET:
            field_dict["silenced_until"] = silenced_until

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.corrective_action import CorrectiveAction

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        action_type = d.pop("action_type")

        title = d.pop("title")

        description = d.pop("description")

        urgency = UrgencyEnum(d.pop("urgency"))

        is_temporarily_silenced = d.pop("is_temporarily_silenced")

        is_effectively_silenced = d.pop("is_effectively_silenced")

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        related_object_name = d.pop("related_object_name")

        related_object_type = d.pop("related_object_type")

        corrective_actions = []
        _corrective_actions = d.pop("corrective_actions")
        for corrective_actions_item_data in _corrective_actions:
            corrective_actions_item = CorrectiveAction.from_dict(corrective_actions_item_data)

            corrective_actions.append(corrective_actions_item)

        def _parse_days_until_due(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        days_until_due = _parse_days_until_due(d.pop("days_until_due"))

        def _parse_due_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                due_date_type_0 = isoparse(data)

                return due_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        action_url = d.pop("action_url", UNSET)

        metadata = d.pop("metadata", UNSET)

        is_silenced = d.pop("is_silenced", UNSET)

        def _parse_silenced_until(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                silenced_until_type_0 = isoparse(data)

                return silenced_until_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        silenced_until = _parse_silenced_until(d.pop("silenced_until", UNSET))

        user_action = cls(
            uuid=uuid,
            action_type=action_type,
            title=title,
            description=description,
            urgency=urgency,
            is_temporarily_silenced=is_temporarily_silenced,
            is_effectively_silenced=is_effectively_silenced,
            created=created,
            modified=modified,
            related_object_name=related_object_name,
            related_object_type=related_object_type,
            corrective_actions=corrective_actions,
            days_until_due=days_until_due,
            due_date=due_date,
            action_url=action_url,
            metadata=metadata,
            is_silenced=is_silenced,
            silenced_until=silenced_until,
        )

        user_action.additional_properties = d
        return user_action

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
