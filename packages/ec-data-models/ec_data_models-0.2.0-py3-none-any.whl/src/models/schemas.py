from datetime import datetime

from sqlmodel import SQLModel

"""
Schemas are used to abstract the internal Datamodel from external endpoints
like APIs and provides seperation of concerns
  - the internal datamodel could be heavily altered and only these schemas would need
    to be adapted to keep an API running
  - Public API responses etc. should sometimes not expose all fields of a table
However, since we currently only have out "Internal API" as public facing endpoints,
this should maybe be moved to that repo
Currently outdated and incomplete
"""


class PersonRead(SQLModel):
    id: int
    email: str
    username: str | None
    first_name: str | None
    last_name: str | None
    created_at: datetime


class PersonCreate(SQLModel):
    email: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class PersonUpdate(SQLModel):
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class OrganisationRead(SQLModel):
    id: int
    name: str | None


class OrganisationCreate(SQLModel):
    name: str | None = None
