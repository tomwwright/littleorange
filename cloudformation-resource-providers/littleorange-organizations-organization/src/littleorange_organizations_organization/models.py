# DO NOT modify this file by hand, changes will be overwritten
import sys
from dataclasses import dataclass
from inspect import getmembers, isclass
from typing import (
    AbstractSet,
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
)
from cloudformation_cli_python_lib.recast import recast_object
from cloudformation_cli_python_lib.utils import deserialize_list

T = TypeVar("T")


def set_or_none(value: Optional[Sequence[T]]) -> Optional[AbstractSet[T]]:
    if value:
        return set(value)
    return None


@dataclass
class ResourceHandlerRequest(BaseResourceHandlerRequest):
    # pylint: disable=invalid-name
    desiredResourceState: Optional["ResourceModel"]
    previousResourceState: Optional["ResourceModel"]


@dataclass
class ResourceModel(BaseModel):
    Arn: Optional[str]
    Id: Optional[str]
    MasterAccountArn: Optional[str]
    MasterAccountId: Optional[str]
    MasterAccountEmail: Optional[str]
    EnabledPolicyTypes: Optional[Sequence["_EnabledPolicyTypes"]]
    FeatureSet: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_ResourceModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_ResourceModel"]:
        if not json_data:
            return None
        dataclasses = {n: o for n, o in getmembers(sys.modules[__name__]) if isclass(o)}
        recast_object(cls, json_data, dataclasses)
        return cls(
            Arn=json_data.get("Arn"),
            Id=json_data.get("Id"),
            MasterAccountArn=json_data.get("MasterAccountArn"),
            MasterAccountId=json_data.get("MasterAccountId"),
            MasterAccountEmail=json_data.get("MasterAccountEmail"),
            EnabledPolicyTypes=deserialize_list(json_data.get("EnabledPolicyTypes"), EnabledPolicyTypes),
            FeatureSet=json_data.get("FeatureSet"),
        )


# work around possible type aliasing issues when variable has same name as a model
_ResourceModel = ResourceModel


@dataclass
class EnabledPolicyTypes(BaseModel):
    Type: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_EnabledPolicyTypes"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_EnabledPolicyTypes"]:
        if not json_data:
            return None
        return cls(
            Type=json_data.get("Type"),
        )


# work around possible type aliasing issues when variable has same name as a model
_EnabledPolicyTypes = EnabledPolicyTypes


