from typing import List, Dict
from transformers import pipeline
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            logger.info("Initializing LLM model... This may take a few minutes on first run")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU
            )
            logger.info("LLM model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LLM model: {str(e)}"
            )

    def generate_recommendations(
        self,
        profession: str,
        questions: str,
        tax_rules: List[Dict[str, str]]
    ) -> List[str]:
        """
        Generate tax relief recommendations based on profession and questions.
        """
        # Filter rules by profession
        relevant_rules = [
            rule for rule in tax_rules 
            if rule["profession"].lower() == profession.lower()
        ]

        if not relevant_rules:
            return []

        # Prepare criteria for classification
        criteria_texts = [rule["criteria"] for rule in relevant_rules]
        
        try:
            # Classify user questions against criteria
            result = self.classifier(
                sequences=questions,
                candidate_labels=criteria_texts,
                multi_label=True
            )

            # Generate recommendations based on matching criteria
            recommendations = []
            for score, criteria in zip(result['scores'], criteria_texts):
                if score > 0.5:  # Confidence threshold
                    matching_rule = next(
                        rule for rule in relevant_rules 
                        if rule["criteria"] == criteria
                    )
                    recommendations.append(
                        f"{matching_rule['name']}: {matching_rule['criteria']}"
                    )

            return recommendations

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating recommendations: {str(e)}"
            )
