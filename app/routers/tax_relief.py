from fastapi import APIRouter, Depends
from typing import List

from app.models.tax_request import TaxRequest, TaxResponse
from app.utils.data_loader import load_tax_rules
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

@router.post("/tax-relief", response_model=TaxResponse)
async def get_tax_relief(request: TaxRequest):
    """
    Generate tax relief recommendations based on profession and questions.
    """
    # Load tax rules
    tax_rules = load_tax_rules()
    
    # Convert questions to string if it's a dictionary
    questions = (
        request.questions 
        if isinstance(request.questions, str) 
        else " ".join(request.questions.values())
    )
    
    # Generate recommendations
    recommendations = llm_service.generate_recommendations(
        profession=request.profession,
        questions=questions,
        tax_rules=tax_rules
    )
    
    return TaxResponse(recommendations=recommendations)
