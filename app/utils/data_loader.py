import json
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import HTTPException

class TaxRule:
    def __init__(self, profession: str, name: str, criteria: str):
        self.profession = profession
        self.name = name
        self.criteria = criteria

def load_tax_rules() -> List[Dict[str, str]]:
    """
    Loads tax rules from the tax_rules.json file.
    
    Returns:
        List[Dict[str, str]]: A list of tax rules with profession, name, and criteria
    
    Raises:
        HTTPException: If the file cannot be found or contains invalid data
    """
    try:
        file_path = Path(__file__).parent.parent.parent / "tax_rules.json"
        
        if not file_path.exists():
            raise FileNotFoundError("tax_rules.json not found in the root directory")
        
        with open(file_path, 'r') as file:
            rules = json.load(file)
            
        # Validate the structure of each rule
        validated_rules = []
        required_fields = {'profession', 'name', 'criteria'}
        
        for rule in rules:
            if not isinstance(rule, dict):
                raise ValueError("Each rule must be a dictionary")
                
            if not all(field in rule for field in required_fields):
                raise ValueError(f"Each rule must contain all required fields: {required_fields}")
                
            validated_rules.append(TaxRule(**rule).__dict__)
            
        return validated_rules
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in tax_rules.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tax rules: {str(e)}")
