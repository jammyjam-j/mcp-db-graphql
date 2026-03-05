from marshmallow import Schema, fields, validate, ValidationError, post_load
from app.models.user import User

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=30))
    email = fields.Email(required=True)
    full_name = fields.Str(validate=validate.Length(max=100))
    is_active = fields.Bool(default=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

    def load_from_dict(self, data: dict) -> User:
        try:
            user = self.load(data)
        except ValidationError as err:
            raise ValueError(f"Invalid user data: {err.messages}") from err
        return user

    def dump_to_dict(self, obj: User) -> dict:
        return self.dump(obj)

    @staticmethod
    def validate_email_uniqueness(email: str, session):
        existing = session.query(User).filter_by(email=email).first()
        if existing:
            raise ValidationError("Email already exists.")

    @staticmethod
    def validate_username_uniqueness(username: str, session):
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            raise ValidationError("Username already taken.")