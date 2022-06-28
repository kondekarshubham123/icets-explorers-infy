from wsgiref.validate import validator
from pydantic import BaseModel

class AnalyzeSentimentDTO(BaseModel):
    sentence: str
    language: str