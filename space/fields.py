from email.utils import parseaddr
from marshmallow import fields, ValidationError

def extract_email(string):
    try:
        _, email = parseaddr(string)

        if email in ("", None):
            raise ValueError

        return email
    except ValueError as error:
        raise ValidationError("Invalid email address was given.") from error

class Email(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return extract_email(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return extract_email(value)
