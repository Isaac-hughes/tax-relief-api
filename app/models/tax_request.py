from pydantic import BaseModel, Field, validator
from typing import Dict, List, Union
import re

class TaxRequest(BaseModel):
    profession: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="The profession to get tax relief recommendations for"
    )
    questions: Union[str, Dict[str, str]] = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Questions about tax relief eligibility"
    )

    @validator('profession')
    def validate_profession(cls, v):
        valid_professions = {"Chef", "Construction Worker", "Teacher", "Nurse"}
        if v not in valid_professions:
            raise ValueError(f"Profession must be one of: {valid_professions}")
        return v

    @validator('questions')
    def validate_questions(cls, v):
        if isinstance(v, str):
            # Remove special characters and excessive spaces
            v = re.sub(r'[^\w\s]', '', v)
            v = ' '.join(v.split())
        return v

class TaxResponse(BaseModel):
    recommendations: List[str] = Field(
        ...,
        description="List of tax relief recommendations"
    )
