# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging

from keycloak import KeycloakAdmin

from ansys.rep.client.jms.resource.base import Object

from ..schema.user import UserSchema

log = logging.getLogger(__name__)


class User(Object):
    """User resource

    Args:
        **kwargs: Arbitrary keyword arguments, see the User schema below.

    Example:

        >>> new_user = User(username='test_user', password='dummy',
        >>>         email='test_user@test.com', fullname='Test User',
        >>>         is_admin=False)

    The User schema has the following fields:

    .. jsonschema:: schemas/User.json

    """

    class Meta:
        schema = UserSchema

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


UserSchema.Meta.object_class = User


def _admin_client(client):
    raise NotImplementedError("KeycloakAdmin currently doesn't support a token auth workflow. TODO")
    keycloak_admin = KeycloakAdmin(
        server_url=client.auth_api_url,
        username=None,
        password=None,
        realm_name=client.realm,
        # refresh_token=client.refresh_token,
        # access_token=client.access_token,
        client_id=client.client_id,
        verify=False,
    )
    return keycloak_admin


def get_users(client, as_objects=True):
    admin = _admin_client(client)
    data = admin.get_users({})
    for d in data:
        uid = d["id"]
        groups = admin.get_user_groups(uid)
        d["groups"] = [g["name"] for g in groups]
        realm_roles = admin.get_realm_roles_of_user(uid)
        d["realm_roles"] = [r["name"] for r in realm_roles]
        d["is_admin"] = d  # Force admin check

    schema = UserSchema(many=True)
    users = schema.load(data)
    return users


def create_user(client, user, as_objects=True):
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

    admin = _admin_client(client)
    uid = admin.create_user(data)
    data = admin.get_user(uid)
    user = schema.load(data)
    return user


def update_user(client, user, as_objects=True):
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

    admin = _admin_client(client)
    data = admin.update_user(user.id, data)
    user = schema.load(data)
    return user


def delete_user(client, user):
    admin = _admin_client(client)
    admin.delete_user(user.id)
