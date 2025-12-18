from datetime import date
from pydantic import BaseModel, Field
from typing import Annotated
from nexo.enums.identity import OptRhesus, RhesusMixin
from nexo.enums.organization import (
    OrganizationRelation,
    SimpleOrganizationRelationMixin,
)
from nexo.enums.status import DataStatus as DataStatusEnum, SimpleDataStatusMixin
from maleo.metadata.schemas.blood_type import (
    OptKeyOrStandardSchema as BloodTypeOptKeyOrStandardSchema,
    FullBloodTypeMixin,
)
from maleo.metadata.schemas.gender import (
    OptKeyOrStandardSchema as GenderOptKeyOrStandardSchema,
    KeyOrStandardSchema as GenderKeyOrStandardSchema,
    FullGenderMixin,
)
from maleo.metadata.schemas.medical_role import (
    KeyOrStandardSchema as MedicalRoleKeyOrStandardSchema,
    FullMedicalRoleMixin,
)
from maleo.metadata.schemas.organization_role import (
    KeyOrStandardSchema as OrganizationRoleKeyOrStandardSchema,
    FullOrganizationRoleMixin,
)
from maleo.metadata.schemas.organization_type import (
    KeyOrStandardSchema as OrganizationTypeKeyOrStandardSchema,
    FullOrganizationTypeMixin,
)
from maleo.metadata.schemas.system_role import (
    KeyOrStandardSchema as SystemRoleKeyOrStandardSchema,
    FullSystemRoleMixin,
)
from maleo.metadata.schemas.user_type import (
    KeyOrStandardSchema as UserTypeKeyOrStandardSchema,
    FullUserTypeMixin,
)
from nexo.schemas.mixins.identity import (
    DataIdentifier,
    IntOrganizationId,
    IntUserId,
    BirthDate,
    DateOfBirth,
)
from nexo.types.datetime import OptDate
from nexo.types.integer import OptInt
from nexo.types.string import OptStr
from ..mixins.common import IdCard, FullName, BirthPlace, PlaceOfBirth
from ..mixins.api_key import APIKey
from ..mixins.organization_registration_code import Code, CurrentUses
from ..mixins.organization_relation import IsBidirectional, Meta
from ..mixins.organization import Key as OrganizationKey, Name as OrganizationName
from ..mixins.patient import PatientIdentity
from ..mixins.user_profile import (
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    AvatarName,
    AvatarUrl,
)
from ..mixins.user import Username, Email, Phone


class APIKeySchema(
    APIKey,
    IntOrganizationId[OptInt],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class PatientSchema(
    RhesusMixin[OptRhesus],
    FullBloodTypeMixin[BloodTypeOptKeyOrStandardSchema],
    FullGenderMixin[GenderKeyOrStandardSchema],
    DateOfBirth[date],
    PlaceOfBirth[OptStr],
    FullName[str],
    PatientIdentity,
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class OrganizationRegistrationCodeSchema(
    CurrentUses,
    Code[str],
    IntOrganizationId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


OptOrganizationRegistrationCodeSchema = OrganizationRegistrationCodeSchema | None


class OrganizationRegistrationCodeSchemaMixin(BaseModel):
    registration_code: Annotated[
        OptOrganizationRegistrationCodeSchema,
        Field(None, description="Organization's registration code"),
    ] = None


class OrganizationSchema(
    OrganizationName[str],
    OrganizationKey[str],
    FullOrganizationTypeMixin[OrganizationTypeKeyOrStandardSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class OrganizationSchemaMixin(BaseModel):
    organization: Annotated[OrganizationSchema, Field(..., description="Organization")]


class SourceOrganizationSchemaMixin(BaseModel):
    source: Annotated[OrganizationSchema, Field(..., description="Source organization")]


class SourceOrganizationRelationSchema(
    Meta,
    IsBidirectional[bool],
    SimpleOrganizationRelationMixin[OrganizationRelation],
    SourceOrganizationSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class SourceOrganizationRelationsSchemaMixin(BaseModel):
    sources: Annotated[
        list[SourceOrganizationRelationSchema],
        Field(list[SourceOrganizationRelationSchema](), description="Sources"),
    ] = list[SourceOrganizationRelationSchema]()


class TargetOrganizationSchemaMixin(BaseModel):
    target: Annotated[OrganizationSchema, Field(..., description="Target organization")]


class TargetOrganizationRelationSchema(
    Meta,
    IsBidirectional[bool],
    SimpleOrganizationRelationMixin[OrganizationRelation],
    TargetOrganizationSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class TargetOrganizationRelationsSchemaMixin(BaseModel):
    targets: Annotated[
        list[TargetOrganizationRelationSchema],
        Field(list[TargetOrganizationRelationSchema](), description="Targets"),
    ] = list[TargetOrganizationRelationSchema]()


class OrganizationRelationSchema(
    Meta,
    IsBidirectional[bool],
    SimpleOrganizationRelationMixin[OrganizationRelation],
    TargetOrganizationSchemaMixin,
    SourceOrganizationSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class UserMedicalRoleSchema(
    FullMedicalRoleMixin[MedicalRoleKeyOrStandardSchema],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class UserMedicalRolesSchemaMixin(BaseModel):
    medical_roles: Annotated[
        list[UserMedicalRoleSchema],
        Field(list[UserMedicalRoleSchema](), description="Medical roles"),
    ] = list[UserMedicalRoleSchema]()


class UserOrganizationRoleSchema(
    FullOrganizationRoleMixin[OrganizationRoleKeyOrStandardSchema],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class UserOrganizationRolesSchemaMixin(BaseModel):
    organization_roles: Annotated[
        list[UserOrganizationRoleSchema],
        Field(list[UserOrganizationRoleSchema](), description="Organization roles"),
    ] = list[UserOrganizationRoleSchema]()


class UserProfileSchema(
    AvatarUrl[OptStr],
    AvatarName[str],
    FullBloodTypeMixin[BloodTypeOptKeyOrStandardSchema],
    FullGenderMixin[GenderOptKeyOrStandardSchema],
    BirthDate[OptDate],
    BirthPlace[OptStr],
    FullName[str],
    EndingTitle[OptStr],
    LastName[str],
    MiddleName[OptStr],
    FirstName[str],
    LeadingTitle[OptStr],
    IdCard[OptStr],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    avatar_url: Annotated[OptStr, Field(None, description="Avatar URL")]


OptUserProfileSchema = UserProfileSchema | None


class UserProfileSchemaMixin(BaseModel):
    profile: Annotated[
        OptUserProfileSchema, Field(None, description="User's Profile")
    ] = None


class UserSystemRoleSchema(
    FullSystemRoleMixin[SystemRoleKeyOrStandardSchema],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class UserSystemRolesSchemaMixin(BaseModel):
    system_roles: Annotated[
        list[UserSystemRoleSchema],
        Field(
            list[UserSystemRoleSchema](),
            description="User's system roles",
            min_length=1,
        ),
    ] = list[UserSystemRoleSchema]()


class UserSchema(
    UserProfileSchemaMixin,
    Phone[str],
    Email[str],
    Username[str],
    FullUserTypeMixin[UserTypeKeyOrStandardSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass


class UserSchemaMixin(BaseModel):
    user: Annotated[UserSchema, Field(..., description="User")]


class UserAndOrganizationSchema(
    UserMedicalRolesSchemaMixin,
    UserOrganizationRolesSchemaMixin,
    OrganizationSchemaMixin,
    UserSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    DataIdentifier,
):
    pass
