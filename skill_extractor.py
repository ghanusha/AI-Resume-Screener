import re

# Comprehensive list of valid skills to look for
AVAILABLE_SKILLS = [
    "java", "python", "sql", "aws", "html", "css", "javascript", 
    "react", "flask", "spring", "docker", "git", "linux"
]

def extract_skills(text):
    """
    Extracts skills from text based on a predefined list of skills.
    Returns a list of unique skills found.
    """
    if not text:
        return []
        
    text = text.lower()
    # Replace non-alphanumeric characters with spaces to ease exact word matching
    text = re.sub(r'[^a-z0-9]', ' ', text)
    
    words = set(text.split())
    
    extracted = []
    for skill in AVAILABLE_SKILLS:
        if skill in words:
            extracted.append(skill)
            
    return extracted
