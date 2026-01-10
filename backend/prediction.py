from pydantic import BaseModel
from typing import List, Optional

class TrialParams(BaseModel):
    product_name: str
    is_biologic: bool = False
    phase: str  # "Phase 1", "Phase 2", "Phase 3"
    n_participants: int
    therapeutic_area: Optional[str] = "General"

class PredictionResult(BaseModel):
    probability_of_success: float
    confidence_interval: List[float]  # [low, high]
    risk_factors: List[str]
    recommendations: List[str]

def predict_trial_outcome(params: TrialParams) -> PredictionResult:
    """
    Calculates the Probability of Success (PoS) based on heuristic industry benchmarks.
    """
    base_pos = 0.50
    risks = []
    recs = []

    # 1. Phase Base Rates (Industry averages)
    # Phase 1: High success (safety focus) ~ 60-70%
    # Phase 2: The "Valley of Death" (efficacy proof) ~ 30%
    # Phase 3: Confirmation ~ 50-60%
    if "1" in params.phase:
        base_pos = 0.65
        recs.append("Focus on safety signals and PK/PD correlation.")
    elif "2" in params.phase:
        base_pos = 0.35
        risks.append("Phase 2 historically has the highest attrition rate.")
        recs.append("Ensure robust dose-finding to avoid Phase 3 failure.")
    elif "3" in params.phase:
        base_pos = 0.55
        recs.append("Statistical power is critical here.")
    
    # 2. Modality Modifiers
    if params.is_biologic:
        base_pos += 0.10  # Biologics generally have higher approval rates than small molecules
        recs.append("Biologics historically show higher approval rates than small molecules.")
    else:
        # Small molecule
        pass 

    # 3. Sample Size Power Heuristic
    # Very rough heuristic: extremely small studies risk being underpowered
    if params.n_participants < 30:
        base_pos -= 0.15
        risks.append(f"Very low sample size (N={params.n_participants}) significantly increases risk of being underpowered.")
    elif params.n_participants < 100 and "3" in params.phase:
        base_pos -= 0.20
        risks.append("Sample size appears critically low for a Phase 3 study.")
        recs.append("Consider increasing enrollment to reach statistical significance.")
    elif params.n_participants > 500:
        base_pos += 0.05
        recs.append("Robust sample size increases confidence in detecting effect size.")

    # 4. Therapeutic Area (Mock modifiers)
    area = params.therapeutic_area.lower()
    if "oncology" in area:
        base_pos -= 0.05  # High failure rate in oncology
        risks.append("Oncology trials have historically higher failure rates.")
    elif "cardio" in area:
        # CV trials usually need HUGE sample sizes to show benefit
        if params.n_participants < 1000 and "3" in params.phase:
             base_pos -= 0.10
             risks.append("Cardiovascular outcomes usually require N > 1000.")
    
    # Clamp result
    final_pos = max(0.01, min(0.99, base_pos))
    
    # Confidence Interval (Mock)
    ci_low = max(0.0, final_pos - 0.10)
    ci_high = min(1.0, final_pos + 0.10)

    return PredictionResult(
        probability_of_success=round(final_pos * 100, 1),
        confidence_interval=[round(ci_low * 100, 1), round(ci_high * 100, 1)],
        risk_factors=risks,
        recommendations=recs
    )
