# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import BaseModel, Field

from pglift.models import helpers
from pglift.models import testing as models


def test_argspec_from_model() -> None:
    argspec = helpers.argspec_from_model(models.Person)
    assert argspec == {
        "name": {"required": True, "type": "str"},
        "nickname": {
            "description": ["Your secret nickname"],
            "no_log": True,
            "required": True,
            "type": "str",
        },
        "relation": {"choices": ["friend", "family", "other"], "required": True},
        "age": {"type": "int", "description": ["age"]},
        "birth": {
            "description": ["birth information"],
            "options": {
                "date": {"description": ["date of birth"], "required": True},
                "place": {"description": ["place of birth"], "type": "str"},
            },
            "required": True,
            "type": "dict",
        },
        "address": {
            "description": ["address"],
            "options": {
                "city": {
                    "description": ["the city"],
                    "required": True,
                    "type": "str",
                },
                "coords": {
                    "description": ["coordinates"],
                    "options": {
                        "lat": {
                            "description": ["latitude"],
                            "required": True,
                            "type": "float",
                        },
                        "long": {
                            "description": ["longitude"],
                            "required": True,
                            "type": "float",
                        },
                        "system": {
                            "choices": ["4326"],
                            "default": "4326",
                            "description": ["coordinates system"],
                        },
                    },
                    "type": "dict",
                },
                "country": {
                    "choices": ["fr", "gb"],
                    "required": True,
                },
                "primary": {
                    "default": False,
                    "description": ["is this person's primary address?"],
                    "type": "bool",
                },
                "street": {
                    "description": ["street lines"],
                    "elements": "str",
                    "required": True,
                    "type": "list",
                },
            },
            "type": "dict",
        },
        "phone_numbers": {
            "type": "list",
            "elements": "dict",
            "description": ["Phone numbers"],
            "options": {
                "label": {
                    "description": ["Type of phone number"],
                    "type": "str",
                },
                "number": {
                    "description": ["Number"],
                    "type": "str",
                    "required": True,
                },
            },
        },
        "pets": {
            "type": "list",
            "elements": "dict",
            "default": [],
            "description": ["Owned pets"],
            "options": {
                "name": {
                    "required": True,
                    "type": "str",
                },
                "state": {
                    "choices": ["present", "absent"],
                    "default": "present",
                },
                "species": {
                    "type": "str",
                },
            },
        },
        "is_dead": {
            "default": False,
            "description": [
                "Is dead",
            ],
            "type": "bool",
        },
        "memberships": {
            "default": [],
            "description": ["Groups the person is a member of"],
            "elements": "dict",
            "options": {
                "name": {"required": True, "type": "str"},
                "state": {"choices": ["present", "absent"], "default": "present"},
            },
            "type": "list",
        },
    }


class Sub(BaseModel):
    f: int


class Nested(BaseModel):
    s: Sub


def test_argspec_from_model_nested_optional() -> None:
    """An optional nested model should propagate non-required on all nested models."""
    assert helpers.argspec_from_model(Nested) == {
        "s": {
            "description": ["s"],
            "options": {"f": {"required": True, "type": "int"}},
            "required": True,
            "type": "dict",
        }
    }

    class Model(BaseModel):
        n: Nested | None = None

    assert helpers.argspec_from_model(Model) == {
        "n": {
            "description": ["n"],
            "options": {
                "s": {
                    "description": ["s"],
                    "options": {
                        "f": {
                            "required": True,
                            "type": "int",
                        }
                    },
                    "required": True,
                    "type": "dict",
                }
            },
            "type": "dict",
        }
    }


class Nested1(BaseModel):
    r: Annotated[
        int, Field(description="Look, a.word.with.dots. And a second sentence.")
    ]
    d: int = 42


class Model(BaseModel):
    n: Nested1 | None = None


def test_argspec_from_model_nested_default() -> None:
    """A default value on a optional nested model should not be set as "default" in ansible"""
    assert helpers.argspec_from_model(Model) == {
        "n": {
            "description": ["n"],
            "options": {
                "d": {
                    "default": 42,
                    "type": "int",
                },
                "r": {
                    "description": ["Look, a.word.with.dots", "And a second sentence"],
                    "required": True,
                    "type": "int",
                },
            },
            "type": "dict",
        }
    }


class Nested2(BaseModel):
    f: int = 42


class Model2(BaseModel):
    n: Nested2 = Nested2()


def test_argspec_from_model_keep_default() -> None:
    """A non-required field with a default value should keep the "default" in ansible"""
    assert helpers.argspec_from_model(Model2) == {
        "n": {
            "default": {"f": 42},
            "description": ["n"],
            "options": {"f": {"default": 42, "type": "int"}},
            "type": "dict",
        }
    }
