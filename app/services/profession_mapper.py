from typing import Dict, Set
import difflib
from app.utils.data_loader import load_tax_rules
import logging

logger = logging.getLogger(__name__)

class ProfessionMapper:
    def __init__(self):
        self.profession_groups = {
            "IT": {
                "IT Consultant", "Software Developer", "Software Engineer",
                "Programmer", "Web Developer", "DevOps Engineer"
            },
            "Medical": {
                "Doctor", "Physician", "Surgeon", "Medical Practitioner",
                "GP", "Consultant"
            },
            "Construction": {
                "Construction Worker", "Builder", "Carpenter",
                "Electrician", "Plumber", "Site Manager"
            },
            "Creative": {
                "Artist", "Graphic Designer", "UI Designer", 
                "Photographer", "Illustrator"
            },
            "Education": {
                "Teacher", "Lecturer", "Professor", 
                "Teaching Assistant", "Tutor"
            }
        }

    def get_matching_profession(self, input_profession: str) -> str:
        # First, try exact match from tax rules
        tax_rules = load_tax_rules()
        valid_professions = {rule["profession"] for rule in tax_rules}
        
        if input_profession in valid_professions:
            return input_profession

        # Check profession groups
        input_lower = input_profession.lower()
        for group in self.profession_groups.values():
            for profession in group:
                if profession.lower() in valid_professions and (
                    profession.lower() == input_lower or
                    input_lower in profession.lower() or
                    profession.lower() in input_lower
                ):
                    logger.info(f"Mapped '{input_profession}' to '{profession}'")
                    return profession

        # Use fuzzy matching as fallback
        matches = difflib.get_close_matches(
            input_profession,
            valid_professions,
            n=1,
            cutoff=0.6
        )
        
        if matches:
            logger.info(f"Fuzzy matched '{input_profession}' to '{matches[0]}'")
            return matches[0]
            
        # If no match found, return original (will result in empty recommendations)
        logger.warning(f"No profession mapping found for '{input_profession}'")
        return input_profession 