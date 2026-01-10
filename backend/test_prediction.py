from backend.prediction import predict_trial_outcome, TrialParams
import json

def test_prediction():
    print("Testing Clinical Trial Success Predictor...")

    # Case 1: Ideal Phase 1 study
    params1 = TrialParams(
        product_name="SafeMol",
        phase="Phase 1",
        n_participants=50,
        is_biologic=True
    )
    result1 = predict_trial_outcome(params1)
    print(f"\nCase 1 (Phase 1 Biologic): {result1.probability_of_success}%")
    assert result1.probability_of_success > 60

    # Case 2: High Risk Phase 2
    params2 = TrialParams(
        product_name="RiskySmallMol",
        phase="Phase 2",
        n_participants=40,
        is_biologic=False
    )
    result2 = predict_trial_outcome(params2)
    print(f"Case 2 (Phase 2 Small Mol): {result2.probability_of_success}%")
    print(f"Risks: {result2.risk_factors}")
    assert result2.probability_of_success < 50
    assert "Phase 2" in result2.risk_factors[0]

    # Case 3: Underpowered Phase 3
    params3 = TrialParams(
        product_name="UnderpoweredOnco",
        phase="Phase 3",
        n_participants=80,
        is_biologic=False,
        therapeutic_area="Oncology"
    )
    result3 = predict_trial_outcome(params3)
    print(f"Case 3 (Phase 3 Oncology Low N): {result3.probability_of_success}%")
    assert result3.probability_of_success < 40
    assert any("low sample size" in r.lower() or "critically low" in r.lower() for r in result3.risk_factors)

    print("\nAll prediction tests passed!")

if __name__ == "__main__":
    test_prediction()
