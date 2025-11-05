from pydantic import BaseModel

class AnalyzePayload(BaseModel):
    identifier: str
