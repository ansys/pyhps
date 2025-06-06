# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

# DO NOT EDIT.
# This file is automatically generated from the JMS schemas.

"""Module providing the user resource."""

from marshmallow.utils import missing

from ansys.hps.client.common import Object

from ..schema.user import UserSchema


class User(Object):
    """Provides the user resource.

    Parameters
    ----------
    id : str
        Unique user ID, generated internally by the server on creation.
    username : str
        Username.
    password : str
        Password.
    first_name : str, optional
        First name.
    last_name : str, optional
        Last name.
    email : str, optional
        E-mail address.

    """

    class Meta:
        schema = UserSchema
        rest_name = "None"

    def __init__(
        self,
        id: str = missing,
        username: str = missing,
        password: str = missing,
        first_name: str = missing,
        last_name: str = missing,
        email: str = missing,
        **kwargs,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        self.obj_type = self.__class__.__name__


UserSchema.Meta.object_class = User
