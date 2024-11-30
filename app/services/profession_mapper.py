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
        tax_rules = load_tax_rules()
        valid_professions = {rule["profession"] for rule in tax_rules}
        input_lower = input_profession.lower()
        
        # 1. Direct match
        if input_profession in valid_professions:
            return input_profession
        
        # 2. Find profession group
        matched_group = None
        for group_name, professions in self.profession_groups.items():
            if any(p.lower() == input_lower for p in professions):
                matched_group = group_name
                break
            
        if matched_group:
            # Find valid professions from the same group
            group_professions = self.profession_groups[matched_group]
            valid_group_profs = [p for p in group_professions if p in valid_professions]
            
            if valid_group_profs:
                matched_prof = valid_group_profs[0]
                logger.info(f"Group matched '{input_profession}' to '{matched_prof}' via {matched_group} group")
                return matched_prof
        
        # 3. Fuzzy match within profession groups first
        for group_name, professions in self.profession_groups.items():
            if any(
                input_lower in p.lower() or p.lower() in input_lower 
                for p in professions
            ):
                # Find valid professions from this group
                valid_group_profs = [p for p in professions if p in valid_professions]
                if valid_group_profs:
                    matched_prof = valid_group_profs[0]
                    logger.info(f"Fuzzy group matched '{input_profession}' to '{matched_prof}' via {group_name} group")
                    return matched_prof
        
        # 4. General fuzzy matching as last resort
        matches = difflib.get_close_matches(
            input_profession,
            valid_professions,
            n=1,
            cutoff=0.6
        )
        
        if matches:
            logger.info(f"Fuzzy matched '{input_profession}' to '{matches[0]}'")
            return matches[0]
        
        logger.warning(f"No profession mapping found for '{input_profession}'")
        return input_profession

    def get_related_professions(self, profession: str) -> Set[str]:
        """Get related professions from the same group"""
        # Find which group the profession belongs to
        for group_name, professions in self.profession_groups.items():
            if any(p.lower() == profession.lower() for p in professions):
                logger.info(f"Found related professions in {group_name} group")
                return professions

        # If no group found, return empty set
        logger.warning(f"No related professions found for {profession}")
        return set()