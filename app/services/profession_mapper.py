from typing import Dict, Set, List
import difflib
from app.utils.data_loader import load_tax_rules
import logging

logger = logging.getLogger(__name__)

class ProfessionMapper:
    def __init__(self):
        self.profession_groups = {
            "IT_Digital": {
                "IT Consultant", "Software Developer", "Software Engineer",
                "Programmer", "Web Developer", "DevOps Engineer", "Systems Architect",
                "Network Engineer", "Data Scientist", "Database Administrator",
                "UI/UX Designer", "Motion Designer", "Game Developer", "Web Designer",
                "Cybersecurity Specialist", "Cloud Architect", "Full Stack Developer",
                "Front End Developer", "Back End Developer", "AI Engineer",
                "Machine Learning Engineer", "Data Engineer", "IT Technician"
            },
            "Medical_Healthcare": {
                "Doctor", "Physician", "Surgeon", "Medical Practitioner",
                "GP", "Consultant", "Nurse", "Dental Nurse", "Dentist",
                "Physiotherapist", "Optometrist", "Paramedic", "Veterinarian",
                "Dental Hygienist", "Occupational Therapist", "Speech Therapist"
            },
            "Construction_Trades": {
                "Construction Worker", "Builder", "Carpenter", "Electrician",
                "Plumber", "Site Manager", "Plasterer", "Bricklayer",
                "Painter", "Decorator", "Roofer", "Glazier", "Scaffolder",
                "Civil Engineer", "Structural Engineer"
            },
            "Creative_Arts": {
                "Artist", "Graphic Designer", "UI Designer", "Photographer",
                "Illustrator", "Voice Actor", "Actor", "Musician",
                "Interior Designer", "Fashion Designer", "Animator",
                "Sound Engineer", "Video Editor", "Content Creator"
            },
            "Education_Training": {
                "Teacher", "Lecturer", "Professor", "Teaching Assistant",
                "Tutor", "Sports Coach", "Dance Teacher", "Yoga Instructor",
                "Driving Instructor", "Personal Trainer", "Music Teacher",
                "Language Teacher", "Special Needs Teacher"
            },
            "Finance_Business": {
                "Financial Advisor", "Accountant", "Investment Banker",
                "Insurance Broker", "Business Analyst", "Management Consultant",
                "Tax Consultant", "Mortgage Advisor", "Risk Analyst",
                "Project Manager", "Marketing Manager"
            },
            "Transportation": {
                "Taxi Driver", "Bus Driver", "Pilot", "Train Driver",
                "Courier", "Delivery Driver", "HGV Driver", "Fleet Manager",
                "Driving Instructor", "Transport Manager"
            },
            "Service_Hospitality": {
                "Chef", "Beautician", "Hairdresser", "Hotel Manager",
                "Restaurant Manager", "Event Planner", "Barber",
                "Spa Therapist", "Wedding Planner", "Catering Manager"
            },
            "Legal_Professional": {
                "Lawyer", "Solicitor", "Barrister", "Legal Executive",
                "Paralegal", "Conveyancer", "Patent Attorney",
                "Legal Secretary", "Court Clerk"
            },
            "Wellness_Fitness": {
                "Personal Trainer", "Yoga Instructor", "Physiotherapist",
                "Sports Therapist", "Nutritionist", "Fitness Instructor",
                "Life Coach", "Sports Massage Therapist"
            },
            "Property_Real_Estate": {
                "Estate Agent", "Property Manager", "Surveyor",
                "Letting Agent", "Property Developer", "Building Inspector",
                "Facilities Manager", "Real Estate Consultant"
            },
            "Media_Communications": {
                "Journalist", "Freelance Writer", "Public Relations Manager",
                "Social Media Manager", "Copywriter", "Broadcasting Professional",
                "Media Producer", "Communications Consultant"
            },
            "Transportation_Logistics": {
                "HGV Driver", "Pilot", "Taxi Driver", "Courier",
                "Fleet Manager", "Logistics Coordinator"
            },
            "Scientific_Research": {
                "Research Scientist", "Biochemist", "Laboratory Technician",
                "Research Assistant", "Clinical Researcher"
            },
            "Sports_Fitness": {
                "Professional Athlete", "Sports Physiotherapist",
                "Personal Trainer", "Sports Coach", "Fitness Instructor"
            },
            "Media_Broadcasting": {
                "Journalist", "TV Producer", "Radio Presenter",
                "News Reporter", "Broadcasting Engineer"
            },
            "Agriculture_Environmental": {
                "Farmer", "Environmental Consultant", "Veterinarian",
                "Agricultural Advisor", "Conservation Officer"
            },
            "Security_Emergency": {
                "Security Guard", "Private Investigator", "Paramedic",
                "Emergency Response Officer", "Fire Safety Officer"
            }
        }

        # Add common variations and aliases
        self.profession_aliases = {
             "Software Engineer": ["Programmer", "Developer", "Coder", "Software Dev", "SWE", "Software Developer"],
            "IT Consultant": ["Tech Consultant", "Technical Consultant", "IT Advisor", "Technology Consultant"],
            "Systems Architect": ["Solutions Architect", "Technical Architect", "Enterprise Architect", "CTO"],
            "Web Developer": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "Website Developer"],
            "Data Scientist": ["ML Engineer", "Machine Learning Specialist", "AI Scientist"],
            "UI/UX Designer": ["UX Designer", "UI Designer", "Product Designer", "UX/UI Designer"],
            "Game Developer": ["Game Programmer", "Video Game Developer", "Unity Developer", "Unreal Developer"],
            "Motion Designer": ["Motion Graphics Artist", "Animator", "Visual Effects Artist"],
            
            "Doctor": ["Physician", "Medical Doctor", "GP", "General Practitioner", "Medical Officer"],
            "Physiotherapist": ["Physical Therapist", "PT", "Sports Therapist", "Rehab Therapist"],
            "Speech Therapist": ["Speech Pathologist", "Speech and Language Therapist", "SLT"],
            
            "Financial Advisor": ["Financial Planner", "Financial Consultant", "Investment Advisor", "Wealth Manager"],
            "Accountant": ["Bookkeeper", "Accounts Manager", "Financial Controller", "Chartered Accountant"],
            "Management Consultant": ["Business Consultant", "Strategy Consultant", "Business Advisor"],
            
            "Graphic Designer": ["Digital Designer", "Visual Designer", "Brand Designer"],
            "UI/UX Designer": ["Product Designer", "Interface Designer", "UX/UI Designer", "Digital Product Designer"],
            "Content Creator": ["YouTuber", "Social Media Creator", "Digital Content Producer", "Influencer"]
        }

        # Add category relationships
        self.related_categories = {
            "Medical_Healthcare": ["Therapy_Counselling", "Alternative_Health"],
            "IT_Digital": ["Creative_Arts"],  # For UI/UX designers etc.
            "Finance_Business": ["Legal_Professional"],
            "Transportation_Logistics": ["Service_Hospitality"],
            "Scientific_Research": ["Medical_Healthcare", "IT_Digital"],
            "Sports_Fitness": ["Education_Training", "Medical_Healthcare"],
            "Media_Broadcasting": ["Creative_Arts", "IT_Digital"],
            "Agriculture_Environmental": ["Scientific_Research"],
            "Security_Emergency": ["Medical_Healthcare"]
        }

    def get_matching_profession(self, input_profession: str) -> str:
        tax_rules = load_tax_rules()
        valid_professions = {rule["profession"] for rule in tax_rules}
        input_lower = input_profession.lower()
        
        # 1. Direct match
        if input_profession in valid_professions:
            return input_profession
        
        # 2. Check aliases
        for main_profession, aliases in self.profession_aliases.items():
            if input_lower in [alias.lower() for alias in aliases]:
                if main_profession in valid_professions:
                    logger.info(f"Alias matched '{input_profession}' to '{main_profession}'")
                    return main_profession
        
        # Improve group matching
        best_match = None
        highest_ratio = 0
        matched_group = None
        
        # First try exact group matches
        for group_name, professions in self.profession_groups.items():
            for profession in professions:
                ratio = difflib.SequenceMatcher(None, input_lower, profession.lower()).ratio()
                if ratio > highest_ratio and profession in valid_professions:
                    highest_ratio = ratio
                    best_match = profession
                    matched_group = group_name
        
        # If we found a good match (over 0.8 similarity)
        if highest_ratio > 0.8:
            logger.info(f"Found close match '{input_profession}' to '{best_match}' ({highest_ratio:.2f}) via {matched_group} group")
            return best_match
        
        # If no good match, try fuzzy matching within appropriate groups
        potential_groups = []
        for group_name, professions in self.profession_groups.items():
            group_words = set(' '.join(professions).lower().split())
            input_words = set(input_lower.split())
            if len(input_words & group_words) > 0:  # If any words overlap
                potential_groups.append(group_name)
        
        # Try fuzzy matching only within relevant groups
        if potential_groups:
            for group_name in potential_groups:
                valid_group_profs = [p for p in self.profession_groups[group_name] if p in valid_professions]
                matches = difflib.get_close_matches(input_profession, valid_group_profs, n=1, cutoff=0.6)
                if matches:
                    logger.info(f"Group fuzzy matched '{input_profession}' to '{matches[0]}' via {group_name}")
                    return matches[0]
        
        # Fall back to general fuzzy matching with higher cutoff
        matches = difflib.get_close_matches(input_profession, valid_professions, n=1, cutoff=0.7)
        if matches:
            logger.info(f"General fuzzy matched '{input_profession}' to '{matches[0]}'")
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

    def get_profession_category(self, profession: str) -> str:
        """Get the category for a profession"""
        normalized_prof = self._normalize_profession_name(profession)
        
        for category, professions in self.profession_groups.items():
            if any(self._normalize_profession_name(p) == normalized_prof 
                  for p in professions):
                return category
        return None
        
    def get_related_categories(self, category: str) -> List[str]:
        """Get related categories for a given category"""
        return self.related_categories.get(category, [])

    def _normalize_profession_name(self, profession: str) -> str:
        """Normalize the profession name for comparison"""
        return profession.lower().replace(" ", "")