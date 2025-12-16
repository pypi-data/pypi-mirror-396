# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

import pydantic
from pydantic import Field

from ... import types


class Service(types.Service, service_name="powa"):
    password: Annotated[
        pydantic.SecretStr | None,
        Field(description="Password of PostgreSQL role for PoWA.", exclude=True),
    ] = None
