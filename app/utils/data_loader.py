from pathlib import Path
import json
import logging
from typing import Dict, List
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class TaxRulesLoader:
    def __init__(self):
        self.rules_dir = Path("app/data/tax_rules")
        self.cache = {}
        
    def _similarity_score(self, a: str, b: str) -> float:
        """Calculate string similarity score"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def load_rules_for_profession(self, profession: str, profession_mapper=None) -> List[Dict]:
        """Load rules specific to a profession"""
        # First try loading from cache
        if profession in self.cache:
            return self.cache[profession]
            
        # Load all rules
        all_rules = self.load_all_rules()
        
        # Get mapped profession if available
        mapped_profession = profession
        if profession_mapper:
            mapped_profession = profession_mapper.get_matching_profession(profession)
            
        logger.info(f"Looking for rules for profession: {profession} (mapped to: {mapped_profession})")
        
        # Try exact match first
        relevant_rules = [
            rule for rule in all_rules
            if rule["profession"].lower() == mapped_profession.lower()
        ]
        
        # If no exact match, try fuzzy matching
        if not relevant_rules:
            threshold = 0.85  # Adjust this threshold as needed
            for rule in all_rules:
                similarity = self._similarity_score(rule["profession"], mapped_profession)
                if similarity >= threshold:
                    logger.info(f"Found fuzzy match: {rule['profession']} for {mapped_profession} (score: {similarity:.2f})")
                    if rule not in relevant_rules:
                        relevant_rules.append(rule)
        
        # Log the results
        if relevant_rules:
            logger.info(f"Found {len(relevant_rules)} rules for {mapped_profession}")
        else:
            logger.warning(f"No rules found for {mapped_profession}")
            
        # Cache the results
        self.cache[profession] = relevant_rules
        return relevant_rules

    def load_all_rules(self) -> List[Dict]:
        """Load all tax rules from all category files"""
        all_rules = []
        
        try:
            for file_path in self.rules_dir.glob("*_rules.json"):
                with open(file_path) as f:
                    rules = json.load(f)
                    all_rules.extend(rules)
            return all_rules
        except Exception as e:
            logger.error(f"Error loading tax rules: {str(e)}")
            return []

    def clear_cache(self):
        """Clear the rules cache"""
        self.cache = {}

# Create a singleton instance
_rules_loader = TaxRulesLoader()

def load_tax_rules() -> List[Dict]:
    """Legacy function to maintain compatibility"""
    return _rules_loader.load_all_rules()

def get_rules_loader() -> TaxRulesLoader:
    """Get the TaxRulesLoader instance"""
    return _rules_loader
