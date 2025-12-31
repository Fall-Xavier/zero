from pydantic import BaseModel

class RefreshBody(BaseModel):
    refresh_token: str