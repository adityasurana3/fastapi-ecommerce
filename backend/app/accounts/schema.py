import string

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing_extensions import Self


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    model_config = {"from_attribute": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    current_password: str = Field(...)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isupper() for char in value):
            raise ValueError("There should be capital letter")
        if not any(char.islower() for char in value):
            raise ValueError("There should be small letter")
        if not any(char in string.punctuation for char in value):
            raise ValueError("Password must contains special character")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contains digits")
        return value

    @model_validator(mode="after")
    def validate_password(self) -> Self:
        if self.confirm_password != self.new_password:
            raise ValueError("Confirm and new password must be same")
        return self
