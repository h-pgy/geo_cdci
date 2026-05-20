from pydantic import BaseModel


class ComponentError(BaseModel):
    internal_message: str
    user_message: str