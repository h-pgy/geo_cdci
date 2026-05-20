from pydantic import BaseModel


class Tab(BaseModel):

    name: str
    warning_message: str
    state_key: str
    tab_widget: object | None = None
    
