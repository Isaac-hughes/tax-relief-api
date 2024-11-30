from pydantic import BaseModel
from typing import Dict, List, Union

class TaxRequest(BaseModel):
    profession: str
    questions: Union[str, Dict[str, str]]

class TaxResponse(BaseModel):
    recommendations: List[str]
