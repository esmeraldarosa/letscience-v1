import re
from typing import List

def extract_side_effects(text: str) -> List[str]:
    """
    Extracts potential side effects based on common keywords.
    In a real system, this would use a named entity recognition (NER) model trained on medical text.
    """
    common_effects = [
        "nausea", "vomiting", "fatigue", "headache", "rash", "hypertension", 
        "anemia", "neutropenia", "diarrhea", "constipation", "insomnia"
    ]
    
    found = []
    text_lower = text.lower()
    for effect in common_effects:
        if effect in text_lower:
            found.append(effect.capitalize())
            
    return list(set(found))

def extract_synthesis_steps(text: str) -> List[str]:
    """
    Extracts sentences that look like chemical synthesis steps.
    """
    steps = []
    # Split by sentence
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    keywords = ["reacted with", "synthesized", "purified", "obtained by", "mixture was", "added to", "yielded"]
    
    for sent in sentences:
        if any(k in sent.lower() for k in keywords):
            steps.append(sent.strip())
            
    return steps
