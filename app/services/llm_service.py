from typing import List, Dict, Optional
from transformers import pipeline
from fastapi import HTTPException
import logging
from functools import lru_cache
import hashlib
import json
from app.services.profession_mapper import ProfessionMapper
from app.utils.data_loader import TaxRulesLoader

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
            self.rules_loader = TaxRulesLoader()
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
        """Cached classification method for zero-shot classification"""
        # Add common tax relief phrases as candidate labels
        candidate_labels = [
            "work uniform expenses",
            "professional equipment costs",
            "vehicle and travel expenses",
            "home office costs",
            "professional memberships",
            "training and education expenses",
            "tools and supplies",
            "licensing and registration fees",
            "protective equipment",
            "workspace rental"
        ]
        
        # Add specific criteria from rules
        candidate_labels.extend(criteria_tuple)
        
        return self.classifier(
            sequences=questions,
            candidate_labels=candidate_labels,
            multi_label=True,
            hypothesis_template="This text describes {}"
        )

    def generate_recommendations(
        self,
        profession: str,
        questions: str,
        tax_rules: List[Dict[str, str]] = None
    ) -> List[str]:
        cache_key = self._generate_cache_key(profession, questions)
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Map profession first
        mapped_profession = self.profession_mapper.get_matching_profession(profession)
        logger.info(f"Mapped profession '{profession}' to '{mapped_profession}'")
        
        # Load relevant rules using mapped profession
        relevant_tax_rules = self.rules_loader.load_rules_for_profession(
            mapped_profession,  # Use mapped profession here
            self.profession_mapper
        )
        
        if not relevant_tax_rules:
            logger.warning(f"No tax rules found for profession: {mapped_profession}")
            return ["Sorry, we couldn't find any tax relief recommendations for your profession."]

        try:
            # Generate human readable intro
            intro = (
                f"Based on our data regarding the {mapped_profession} profession, "
                "here are some potential tax relief opportunities you may be eligible for:\n\n"
            )

            # Enhanced user questions
            enhanced_questions = (
                f"I am a {profession} and want to know about tax relief for: {questions}. "
                "This includes equipment, travel, uniforms, and professional expenses."
            )
            
            # Prepare criteria with enhanced context
            criteria_texts = [
                f"{rule['name']}: {rule['criteria']}"
                for rule in relevant_tax_rules
            ]
            
            result = self._classify_text(
                enhanced_questions,
                tuple(criteria_texts)
            )

            # Generate recommendations
            recommendations = [intro]
            
            for score, criteria in zip(result['scores'], criteria_texts):
                if score > 0.3:  # Confidence threshold
                    recommendations.append(
                        f"• {criteria}\n"
                        f"  (Relevance: {score:.0%})"
                    )
            
            if len(recommendations) == 1:  # Only has intro
                recommendations.append(
                    "While we have information about your profession, none of the "
                    "available tax relief options seem to directly match your situation. "
                    "Consider consulting with a tax professional for personalized advice."
                )

            self._cache[cache_key] = recommendations
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Sorry, there was an error processing your request. Please try again."]
