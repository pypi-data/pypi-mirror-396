# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from typing import Annotated

from pydantic import BeforeValidator, Field, SecretStr, ValidationInfo

from ... import types


def check_listen(value: str, info: ValidationInfo) -> str:
    """Set 'listen' from 'connect_address' if unspecified.

    >>> RESTAPI()  # doctest: +ELLIPSIS
    RESTAPI(connect_address='...:8008', listen='...:8008', authentication=None)
    >>> RESTAPI(connect_address="localhost:8008")
    RESTAPI(connect_address='localhost:8008', listen='localhost:8008', authentication=None)
    >>> RESTAPI(connect_address="localhost:8008", listen="server:123")
    RESTAPI(connect_address='localhost:8008', listen='server:123', authentication=None)
    >>> r = RESTAPI(
    ...     connect_address="localhost:8008",
    ...     listen="server:123",
    ...     authentication={"username": "t", "password": "m"},
    ... )
    >>> r.authentication
    Authentication(username='t', password=SecretStr('**********'))
    >>> r.authentication.password.get_secret_value()
    'm'
    """
    if not value:
        value = types.info_data_get(info, "connect_address")
        assert isinstance(value, str)
    return value


class Authentication(types.BaseModel):
    username: Annotated[
        str, Field(description="Basic authentication username for Patroni's REST API.")
    ]
    password: Annotated[
        SecretStr,
        Field(description="Basic authentication password for Patroni's REST API."),
    ]


class RESTAPI(types.BaseModel):
    connect_address: Annotated[
        types.Address,
        Field(
            default_factory=functools.partial(types.local_address, port=8008),
            description="IP address (or hostname) and port, to access the Patroni's REST API.",
        ),
    ]
    listen: Annotated[
        types.Address,
        Field(
            default_factory=types.unspecified_address,
            description="IP address (or hostname) and port that Patroni will listen to for the REST API. Defaults to connect_address if not provided.",
            validate_default=True,
        ),
        BeforeValidator(check_listen),
    ]
    authentication: Annotated[
        Authentication | None,
        Field(description="Basic authentication for Patroni's REST API."),
    ] = None
