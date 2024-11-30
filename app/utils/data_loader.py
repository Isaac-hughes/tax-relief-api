import json
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import HTTPException
from functools import lru_cache

class TaxRule:
    def __init__(self, profession: str, name: str, criteria: str):
        self.profession = profession
        self.name = name
        self.criteria = criteria

@lru_cache(maxsize=1)
def load_tax_rules() -> List[Dict[str, str]]:
    """Cached version of tax rules loader"""
    try:
        file_path = Path(__file__).parent.parent.parent / "tax_rules.json"
        
        if not file_path.exists():
            raise FileNotFoundError("tax_rules.json not found")
        
        with open(file_path, 'r') as file:
            rules = json.load(file)
            
        return rules
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
