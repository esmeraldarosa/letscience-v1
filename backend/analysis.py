from typing import List, Dict, Optional
from sqlmodel import Session, select
from backend.models import Product, ProductPharmacodynamics, DrugInteraction

def infer_mechanism_type(description: str) -> str:
    """Infers if a drug is an Agonist or Antagonist/Inhibitor based on description."""
    desc = description.lower() if description else ""
    if any(k in desc for k in ["inhibitor", "blocker", "antagonist", "antibody", "mab", "reduce", "suppress"]):
        return "Antagonist"
    if any(k in desc for k in ["agonist", "activator", "analogue", "mimetic", "induce", "stimulate"]):
        return "Agonist"
    return "Unknown"

def analyze_combination(session: Session, drug_a_id: int, drug_b_id: int) -> Dict:
    """
    Analyzes the potential interaction between two drugs.
    Combines known database interactions with heuristic simulation based on mechanism/targets.
    """
    drug_a = session.get(Product, drug_a_id)
    drug_b = session.get(Product, drug_b_id)
    
    if not drug_a or not drug_b:
        return {"error": "Drugs not found"}

    mech_a = infer_mechanism_type(drug_a.description)
    mech_b = infer_mechanism_type(drug_b.description)

    result = {
        "drug_a": {
            "name": drug_a.name,
            "mechanism_type": mech_a,
            "indication": drug_a.target_indication
        },
        "drug_b": {
            "name": drug_b.name,
            "mechanism_type": mech_b,
            "indication": drug_b.target_indication
        },
        "synergy_score": 5, # Baseline
        "interaction_type": "Neutral",
        "analysis": [],
        "safety_warnings": []
    }

    # 1. Check Known Interactions (Database)
    known = session.exec(select(DrugInteraction).where(
        ((DrugInteraction.drug_a_id == drug_a_id) & (DrugInteraction.drug_b_id == drug_b_id)) |
        ((DrugInteraction.drug_a_id == drug_b_id) & (DrugInteraction.drug_b_id == drug_a_id))
    )).first()
    
    if known:
        result["interaction_type"] = known.interaction_type
        result["analysis"].append(f"KNOWN INTERACTION: {known.effect_description}")
        if known.interaction_type == "Synergy":
            result["synergy_score"] += 3
        elif known.interaction_type == "Antagonism":
            result["synergy_score"] -= 3
            
        if known.severity == "High":
             result["safety_warnings"].append("Critical known interaction detected.")

    # 2. Simulation Heuristics (Targets & Mechanism)
    targets_a = session.exec(select(ProductPharmacodynamics).where(ProductPharmacodynamics.product_id == drug_a_id)).all()
    targets_b = session.exec(select(ProductPharmacodynamics).where(ProductPharmacodynamics.product_id == drug_b_id)).all()
    
    set_a_targets = {t.target.lower() for t in targets_a if t.target}
    set_b_targets = {t.target.lower() for t in targets_b if t.target}
    
    # Heuristic 1: Target Overlap
    common_targets = set_a_targets.intersection(set_b_targets)
    if common_targets:
        target_names = ", ".join(common_targets)
        
        # Check for Antagonism (Agonist + Antagonist on same target)
        if (mech_a == "Agonist" and mech_b == "Antagonist") or (mech_a == "Antagonist" and mech_b == "Agonist"):
            result["analysis"].append(f"DIRECT ANTAGONISM: Opposing actions (Agonist vs Antagonist) on shared target {target_names}.")
            result["synergy_score"] -= 4
            result["interaction_type"] = "Antagonistic"
        # Check for Redundancy (Same action on same target)
        elif mech_a == mech_b and mech_a != "Unknown":
             result["analysis"].append(f"MECHANISM REDUNDANCY: Both drugs act as {mech_a}s on {target_names}.")
             result["synergy_score"] -= 2
             result["safety_warnings"].append(f"High risk of cumulative toxicity due to redundant targeting of {target_names}.")
        else:
             result["analysis"].append(f"MECHANISM OVERLAP: Shared target {target_names} detected.")
             result["synergy_score"] -= 1

            
    # Heuristic 2: Complementary Mechanisms (e.g. VEGF + PD-1)
    desc_a = (drug_a.description or "").lower()
    desc_b = (drug_b.description or "").lower()
    
    is_pd1_a = "pd-1" in desc_a or "pd-l1" in desc_a or "checkpoint" in desc_a
    is_pd1_b = "pd-1" in desc_b or "pd-l1" in desc_b
    
    is_vegf_a = "vegf" in desc_a or "angiogenesis" in desc_a
    is_vegf_b = "vegf" in desc_b or "angiogenesis" in desc_b
    
    is_chemo_a = "chemotherapy" in desc_a or "cytotoxic" in desc_a
    is_chemo_b = "chemotherapy" in desc_b or "cytotoxic" in desc_b
    
    if (is_pd1_a and is_vegf_b) or (is_pd1_b and is_vegf_a):
        result["analysis"].append("MECHANISTIC SYNERGY: Immune checkpoint inhibition combined with anti-angiogenesis agents has shown clinical synergy by normalizing tumor vasculature.")
        result["synergy_score"] += 4
        result["interaction_type"] = "Potentially Synergistic"

    if (is_pd1_a and is_chemo_b) or (is_pd1_b and is_chemo_a):
        result["analysis"].append("IMMUNOGENIC PRIMING: Chemotherapy may release tumor antigens, enhancing the efficacy of the checkpoint inhibitor.")
        result["synergy_score"] += 2
        result["interaction_type"] = "Additive / Synergistic"
        
    # 3. Side Effect Stacking
    se_a = {se.effect.lower() for se in drug_a.side_effects}
    se_b = {se.effect.lower() for se in drug_b.side_effects}
    
    common_se = se_a.intersection(se_b)
    if common_se:
        count = len(common_se)
        se_list = ", ".join(list(common_se)[:3]).title()
        if count > 3: se_list += f", and {count-3} others"
        
        severity_label = "High" if count > 3 else "Moderate"
        
        result["safety_warnings"].append(f"TOXICITY OVERLAP ({severity_label}): Shared risk of {se_list}. Cumulative burden may require dose reduction.")
        result["synergy_score"] = max(0, result["synergy_score"] - (1 if count <=2 else 2))
        
    # Final clamping
    result["synergy_score"] = max(0, min(10, result["synergy_score"]))
    
    return result
