"""Security utilities"""
from passlib.context import CryptContext
from pydantic_core import core_schema

from microblog.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


def verify_password(plain_password, hashed_password) -> bool:
    """Verifies a hash against a password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Generates a hash from plain text"""
    return pwd_context.hash(password)


class HashedPassword(str):
    """Takes a plain text password and hashes it.
    use this as a field in your SQLModel
    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.str_schema()

    def __new__(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("string required")
        hashed_password = get_password_hash(value)
        return super().__new__(cls, hashed_password)