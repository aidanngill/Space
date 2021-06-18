from marshmallow import Schema, fields, EXCLUDE
from marshmallow.validate import Length

from .fields import Email

# auth.py
class AuthRegisterPost(Schema):
    class Meta:
        unknown = EXCLUDE

    email = Email(required=True, validate=Length(max=128))
    username = fields.String(required=True, validate=Length(min=2, max=32))
    password = fields.String(required=True, validate=Length(min=8))
    invite = fields.String(required=False, validate=Length(equal=32))

class AuthLoginPost(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True, validate=Length(max=32))
    password = fields.String(required=True)

register_post = AuthRegisterPost()
login_post = AuthLoginPost()

# user.py
class UserInfoPost(Schema):
    class Meta:
        unknown = EXCLUDE

    email = Email(validate=Length(max=128))
    username = fields.String(validate=Length(max=32))

info_post = UserInfoPost()
