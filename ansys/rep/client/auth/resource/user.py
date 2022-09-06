# autogenerated code based on UserSchema

from marshmallow.utils import missing
from ansys.rep.client.jms.resource.base import Object
from ..schema.user import UserSchema

class User(Object):
    """User resource.

    Parameters
    ----------
    id : str
        Unique user ID, generated internally by the server on creation.
    username : str
        Username.
    password : str
        Password.
    first_name : str, optional
        First name
    last_name : str, optional
        Last name
    email : str, optional
        E-mail address (optional).
    groups : str
        Groups the user belongs to
    realm_roles : str
        Realm roles assigned to the user
    is_admin        Whether the user has admin rights or not.

    """

    class Meta:
        schema = UserSchema
        rest_name = "None"

    def __init__(self, **kwargs):
        self.id = missing
        self.username = missing
        self.password = missing
        self.first_name = missing
        self.last_name = missing
        self.email = missing
        self.groups = missing
        self.realm_roles = missing
        self.is_admin = missing

        super().__init__(**kwargs)

UserSchema.Meta.object_class = User