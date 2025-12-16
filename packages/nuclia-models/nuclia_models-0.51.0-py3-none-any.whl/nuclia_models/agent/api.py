from pydantic import BaseModel

from nuclia_models.common.formats import TextFormat


class SessionData(BaseModel):
    slug: str
    name: str
    summary: str
    data: str
    format: TextFormat
