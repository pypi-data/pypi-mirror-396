# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Sample models for testing purpose."""

from datetime import date
from functools import partial
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    Field,
    SecretStr,
    ValidationInfo,
    model_validator,
)

from pglift._compat import Self
from pglift.annotations import ansible, cli
from pglift.exceptions import MutuallyExclusiveError
from pglift.models.interface import PresenceState, as_dict

CountryValues = Literal["fr", "be", "gb"]


class Location(BaseModel):
    system: Annotated[Literal["4326"], Field(description="coordinates system")] = "4326"
    long_: Annotated[float, Field(alias="long", description="longitude")]
    lat: Annotated[float, Field(description="latitude")]


def validate_city_and_country(
    value: CountryValues, info: ValidationInfo
) -> CountryValues:
    if value == "fr" and info.data["city"] == "bruxelles":
        raise ValueError("Bruxelles is in Belgium!")
    return value


class Address(BaseModel, extra="forbid"):
    street: Annotated[list[str], Field(description="street lines", min_length=1)]
    building: Annotated[str | None, cli.HIDDEN, ansible.HIDDEN] = None
    zip_code: Annotated[int, ansible.HIDDEN, Field(description="ZIP code")] = 0
    city: Annotated[
        str,
        cli.Argument(name="town", metavar="city"),
        ansible.Spec({"type": "str", "description": ["the city"]}),
        Field(description="city"),
    ]
    country: Annotated[
        CountryValues,
        AfterValidator(validate_city_and_country),
        cli.Choices(choices=["fr", "be"]),
        ansible.Choices(["fr", "gb"]),
    ]
    primary: Annotated[bool, Field(description="is this person's primary address?")] = (
        False
    )
    coords: Annotated[Location | None, Field(description="coordinates")] = None


class PhoneNumber(BaseModel):
    label: Annotated[str | None, Field(description="Type of phone number")] = None
    number: Annotated[str, Field(description="Number")]


class BirthInformation(BaseModel):
    date_: Annotated[date, Field(alias="date", description="date of birth")]
    place: Annotated[
        str | None,
        Field(description="place of birth", json_schema_extra={"readOnly": True}),
    ] = None


class Pet(BaseModel):
    name: str
    species: str | None = None
    state: PresenceState = "present"


class GroupMembership(BaseModel):
    name: str
    state: PresenceState = "present"


class Person(BaseModel, extra="forbid"):
    name: Annotated[str, Field(min_length=3)]
    nickname: Annotated[
        SecretStr,
        cli.Option(),
        Field(description="Your secret nickname"),
    ]
    relation: Literal["friend", "family", "other"]
    age: Annotated[int | None, Field(description="age")] = None
    address: Address | None = None
    birth: Annotated[BirthInformation, Field(description="birth information")]
    is_dead: Annotated[bool, Field(description="Is dead")] = False
    phone_numbers: Annotated[
        list[Annotated[PhoneNumber, BeforeValidator(partial(as_dict, key="number"))]],
        Field(
            default_factory=list,
            description="Phone numbers",
        ),
    ]
    pets: Annotated[
        list[Annotated[Pet, BeforeValidator(as_dict)]],
        cli.ListOption(
            name="pet",
            descriptions={"add": "Add pet", "remove": "Remove pet"},
        ),
        Field(
            description="Owned pets",
        ),
    ] = []
    memberships: Annotated[
        list[Annotated[GroupMembership, BeforeValidator(as_dict)]],
        cli.ListOption(
            name="member_of",
            metavar="group",
            names={"add": "--add-to", "remove": "--remove-from"},
            descriptions={"add": "Add to group", "remove": "Remove from group"},
        ),
        Field(
            description="Groups the person is a member of",
        ),
    ] = []

    @model_validator(mode="after")
    def __validate_age(self: Self) -> Self:
        if self.is_dead and self.age is not None:
            raise MutuallyExclusiveError(("is_dead", "age"))
        return self
