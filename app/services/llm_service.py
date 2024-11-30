from typing import List, Dict, Optional
from transformers import pipeline
from fastapi import HTTPException
import logging
from functools import lru_cache
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        try:
            logger.info("Initializing LLM model...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU
            )
            self._cache = {}
            logger.info("LLM model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_cache_key(self, profession: str, questions: str) -> str:
        """Generate a unique cache key for the request"""
        content = f"{profession.lower()}:{questions.lower()}"
        return hashlib.md5(content.encode()).hexdigest()

    @lru_cache(maxsize=1000)
    def _classify_text(self, questions: str, criteria_tuple: tuple) -> dict:
        """Cached classification method"""
        return self.classifier(
            sequences=questions,
            candidate_labels=list(criteria_tuple),
            multi_label=True
        )

    def generate_recommendations(
        self,
        profession: str,
        questions: str,
        tax_rules: List[Dict[str, str]]
    ) -> List[str]:
        """Generate tax relief recommendations with caching"""
        cache_key = self._generate_cache_key(profession, questions)
        
        # Check cache first
        if cache_key in self._cache:
            logger.info("Cache hit for recommendations")
            return self._cache[cache_key]

        # Filter rules by profession
        relevant_rules = [
            rule for rule in tax_rules 
            if rule["profession"].lower() == profession.lower()
        ]

        if not relevant_rules:
            return []

        try:
            # Prepare criteria for classification
            criteria_texts = tuple(rule["criteria"] for rule in relevant_rules)
            
            # Get classification results (cached)
            result = self._classify_text(questions, criteria_texts)

            # Generate recommendations
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

            # Cache the results
            self._cache[cache_key] = recommendations
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
