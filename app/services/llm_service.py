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
        tax_rules: List[Dict[str, str]]
    ) -> List[str]:
        cache_key = self._generate_cache_key(profession, questions)
        
        if cache_key in self._cache:
            return self._cache[cache_key]

        mapped_profession = self.profession_mapper.get_matching_profession(profession)
        
        # Get both exact and related profession rules
        relevant_rules = []
        mapped_prof_lower = mapped_profession.lower()

        # First add exact matches
        relevant_rules.extend([
            rule for rule in tax_rules 
            if rule["profession"].lower() == mapped_prof_lower
        ])

        # Then add rules from related professions
        related_profs = self.profession_mapper.get_related_professions(mapped_profession)
        for rule in tax_rules:
            rule_prof = rule["profession"].lower()
            if (rule_prof != mapped_prof_lower and  # Skip already added exact matches
                any(prof.lower() == rule_prof for prof in related_profs)):
                relevant_rules.append(rule)

        if not relevant_rules:
            return []

        try:
            # Prepare criteria with enhanced context
            criteria_texts = [
                f"Tax relief for {rule['criteria'].lower()} in {rule['profession']}" 
                for rule in relevant_rules
            ]
            
            # Enhance user questions with more context
            enhanced_questions = (
                f"I am a {profession} and want to know about tax relief for: {questions}. "
                "This includes equipment, travel, uniforms, and professional expenses."
            )
            
            result = self._classify_text(
                enhanced_questions,
                tuple(criteria_texts)
            )

            # Use dynamic threshold based on confidence distribution
            scores = result['scores']
            mean_score = sum(scores) / len(scores)
            threshold = min(0.3, mean_score * 1.5)  # Adaptive threshold
            
            recommendations = []
            for score, criteria, rule in zip(scores, criteria_texts, relevant_rules):
                logger.debug(f"Score {score:.2f} for {criteria}")
                if score > threshold:
                    recommendations.append(
                        f"{rule['name']}: {rule['criteria']} ({score:.2f} confidence)"
                    )

            self._cache[cache_key] = recommendations
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
