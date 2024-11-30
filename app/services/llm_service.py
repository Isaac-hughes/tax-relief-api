from typing import List, Dict, Optional
from transformers import pipeline
from fastapi import HTTPException
import logging
from functools import lru_cache
import hashlib
import json
from app.services.profession_mapper import ProfessionMapper

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
            self.profession_mapper = ProfessionMapper()
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
        """Generate tax relief recommendations with improved matching"""
        cache_key = self._generate_cache_key(profession, questions)
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Map profession to closest match
        mapped_profession = self.profession_mapper.get_matching_profession(profession)
        
        # Get relevant rules
        relevant_rules = [
            rule for rule in tax_rules 
            if rule["profession"].lower() == mapped_profession.lower()
        ]

        if not relevant_rules:
            return []

        try:
            # Prepare criteria with more context
            criteria_texts = [
                f"Tax relief for {rule['criteria'].lower()}" 
                for rule in relevant_rules
            ]
            
            # Enhance user questions with context
            enhanced_questions = f"I want to know about tax relief for: {questions}"
            
            # Get classification with lower threshold
            result = self._classify_text(
                enhanced_questions,
                tuple(criteria_texts)
            )

            # Generate recommendations with lower threshold
            recommendations = []
            for score, criteria, rule in zip(
                result['scores'],
                criteria_texts,
                relevant_rules
            ):
                logger.debug(f"Score {score:.2f} for {criteria}")
                if score > 0.3:  # Lower threshold for better matching
                    recommendations.append(
                        f"{rule['name']}: {rule['criteria']}"
                    )

            self._cache[cache_key] = recommendations
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
