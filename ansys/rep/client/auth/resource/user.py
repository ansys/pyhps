# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging

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
