
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserLoginSсhema(BaseModel):
   username: str
   email: EmailStr = Field(pattern=r".+@*\.com$")
   password: str

class UserLoginSсhema(BaseModel):
   code: str






