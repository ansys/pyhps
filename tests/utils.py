# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import Tuple
import uuid

from keycloak import KeycloakAdmin

from ansys.hps.client import Client
from ansys.hps.client.auth import User
from ansys.hps.client.auth.schema.user import UserSchema


def create_user(keycloak_client: KeycloakAdmin, user: User) -> User:

    schema = UserSchema(many=False)
    data = schema.dump(user)

    pwd = data.pop("password", None)
    if pwd is not None:
        data["credentials"] = [
            {
                "type": "password",
                "value": pwd,
            }
        ]
    data["enabled"] = True

    uid = keycloak_client.create_user(data)

    user = keycloak_client.get_user(user_id=uid)
    schema = UserSchema(many=False)
    return schema.load(user)


def delete_user(keycloak_client: KeycloakAdmin, user: User) -> User:
    return keycloak_client.delete_user(user.id)


def create_new_user_client(
    url,
    keycloak_client: KeycloakAdmin,
    username=None,
    password="test",
) -> Tuple[User, Client]:
    if username is None:
        username = f"testuser-{uuid.uuid4().hex[:8]}"
    user = create_user(keycloak_client, User(username=username, password=password))
    client = Client(
        url=url,
        username=user.username,
        password=password,
    )
    return user, client
