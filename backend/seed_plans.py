from sqlmodel import Session, select
from backend.models import SubscriptionPlan
from backend.main import engine
import json

def seed_plans():
    with Session(engine) as session:
        # Check if plans exist
        existing = session.exec(select(SubscriptionPlan)).first()
        if existing:
            print("Plans already exist. Skipping.")
            return

        print("Seeding default subscription plans...")
        plans = [
            SubscriptionPlan(
                name="Free Tier",
                price_monthly=0.0,
                features=json.dumps(["basic_search", "view_products"]),
                stripe_price_id="price_free_test"
            ),
            SubscriptionPlan(
                name="Professional Analyst",
                price_monthly=49.99,
                features=json.dumps(["predictor", "patent_reports", "combination_lab"]),
                stripe_price_id="price_pro_test"
            ),
            SubscriptionPlan(
                name="Enterprise",
                price_monthly=299.00,
                features=json.dumps(["all_features", "api_access", "dedicated_support"]),
                stripe_price_id="price_enterprise_test"
            )
        ]
        session.add_all(plans)
        session.commit()
        print("Subscription plans seeded successfully.")

if __name__ == "__main__":
    seed_plans()
