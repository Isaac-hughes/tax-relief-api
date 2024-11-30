from pydantic import BaseModel, Field, validator
from typing import Dict, List, Union
import re
from app.utils.data_loader import load_tax_rules

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
        # Allow any profession - mapping will handle it
        if len(v.strip()) < 2:
            raise ValueError("Profession must be at least 2 characters")
        return v.strip()

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
