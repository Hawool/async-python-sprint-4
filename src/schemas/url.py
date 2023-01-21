from datetime import datetime

from pydantic import BaseModel


# Shared properties
class UrlBase(BaseModel):
    url: str | None


# Properties to receive on entity creation
class UrlCreate(UrlBase):
    name: str | None


# Properties to receive on entity update
class UrlUpdate(UrlBase):
    name: str | None
    number_of_transitions: int | None
    is_deleted: bool | None


# Properties shared by models stored in DB
class UrlInDBBase(UrlBase):
    id: int
    name: str | None
    url: str
    number_of_transitions: int
    created_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True


# Properties to return to client
class Url(UrlInDBBase):
    pass


# Properties stored in DB
class UrlInDB(UrlInDBBase):
    pass
