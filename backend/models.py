from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class ProductBase(SQLModel):
    name: str # e.g. "Pembrolizumab"
    description: Optional[str] = None
    target_indication: Optional[str] = None # e.g. "Melanoma"
    development_phase: Optional[str] = None # e.g. "Approved"
    moa_video_url: Optional[str] = None # YouTube Embed URL

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    patents: List["Patent"] = Relationship(back_populates="product")
    articles: List["ScientificArticle"] = Relationship(back_populates="product")
    trials: List["ClinicalTrial"] = Relationship(back_populates="product")
    conferences: List["Conference"] = Relationship(back_populates="product")
    
    side_effects: List["ProductSideEffect"] = Relationship(back_populates="product")
    synthesis_steps: List["ProductSynthesis"] = Relationship(back_populates="product")
    
    # New enhanced relationships
    milestones: List["ProductMilestone"] = Relationship(back_populates="product")
    indications: List["ProductIndication"] = Relationship(back_populates="product")
    synthesis_schemes: List["ProductSynthesisScheme"] = Relationship(back_populates="product")
    pharmacokinetics: List["ProductPharmacokinetics"] = Relationship(back_populates="product")
    pharmacodynamics: List["ProductPharmacodynamics"] = Relationship(back_populates="product")
    experimental_models: List["ProductExperimentalModel"] = Relationship(back_populates="product")

class ProductSideEffect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    effect: str
    product: Optional[Product] = Relationship(back_populates="side_effects")

class ProductSynthesis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    step_description: str
    product: Optional[Product] = Relationship(back_populates="synthesis_steps")

class Patent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    source_id: str
    title: str
    abstract: Optional[str]
    assignee: Optional[str]
    status: Optional[str]
    publication_date: Optional[datetime]
    url: Optional[str]
    
    # Enhanced fields
    claim_summary: Optional[str] = None  # Summary of key claims
    diseases_in_claims: Optional[str] = None  # Comma-separated diseases from claims
    patent_type: Optional[str] = None  # "Product", "Combination", "Use"
    expiry_date: Optional[datetime] = None
    
    product: Optional[Product] = Relationship(back_populates="patents")

class ScientificArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    doi: str
    title: str
    abstract: Optional[str]
    authors: Optional[str] # Comma separated
    publication_date: Optional[datetime]
    url: Optional[str]
    
    product: Optional[Product] = Relationship(back_populates="articles")

class ClinicalTrial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    nct_id: str
    title: str
    status: str
    phase: str
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None # Added for Gantt Chart
    sponsor: Optional[str] = None
    url: Optional[str]
    
    product: Optional[Product] = Relationship(back_populates="trials")

class Conference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    title: str
    abstract: Optional[str]
    conference_name: str
    date: Optional[datetime]
    url: Optional[str]

    product: Optional[Product] = Relationship(back_populates="conferences")

# --- Enhanced Models ---

class ProductMilestone(SQLModel, table=True):
    """Development timeline milestones"""
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    date: datetime
    event: str  # e.g., "Phase 1 Start", "FDA Approval"
    phase: Optional[str] = None  # e.g., "Preclinical", "Phase 1", "Approved"
    
    product: Optional[Product] = Relationship(back_populates="milestones")

class ProductIndication(SQLModel, table=True):
    """Disease indications with references"""
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    disease_name: str  # e.g., "Melanoma"
    approval_status: Optional[str] = None  # e.g., "Approved", "Phase 3", "Investigational"
    reference_url: Optional[str] = None
    reference_title: Optional[str] = None
    
    product: Optional[Product] = Relationship(back_populates="indications")

class ProductSynthesisScheme(SQLModel, table=True):
    """Visual synthesis schemes"""
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    
    scheme_name: str  # e.g., "Primary Synthesis Route"
    scheme_description: Optional[str] = None
    scheme_image_url: Optional[str] = None  # Path to diagram
    source_url: Optional[str] = None # External link to scheme source
    
    
    product: Optional[Product] = Relationship(back_populates="synthesis_schemes")

class ProductRead(ProductBase):
    id: int
    target_indication: Optional[str] = None
    indications: List["ProductIndication"] = []
class ProductPharmacokinetics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    parameter: str # e.g. "Tmax", "Cmax", "Bioavailability"
    value: str # e.g. "2-4 hours", "95%"
    unit: Optional[str] = None
    conditions: Optional[str] = None # e.g. "Healthy Volunteers", "Mouse Model"
    product: Optional[Product] = Relationship(back_populates="pharmacokinetics")

class ProductPharmacodynamics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    parameter: str # e.g. "Ki", "IC50", "EC50"
    value: str # e.g. "0.5 nM", "12 nM"
    unit: Optional[str] = None
    target: Optional[str] = None # e.g. "Factor Xa", "TNF-alpha"
    mechanism_of_action_type: Optional[str] = None # e.g. "Agonist", "Antagonist", "Inhibitor"
    product: Optional[Product] = Relationship(back_populates="pharmacodynamics")

class ProductExperimentalModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    model_name: str # e.g. "MC38 murine colon cancer model"
    model_type: str # e.g. "In Vivo", "In Vitro"
    description: str
    product: Optional[Product] = Relationship(back_populates="experimental_models")


# =====================
# Authentication Models
# =====================

class User(SQLModel, table=True):
    """User model for authentication"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str  # bcrypt hashed password
    
    # 2FA
    totp_secret: Optional[str] = None  # TOTP secret for 2FA
    is_2fa_enabled: bool = Field(default=False)
    
    # User status
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class AlertSubscription(SQLModel, table=True):
    """User subscriptions for product update alerts"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    
    # Alert preferences
    alert_patents: bool = Field(default=True)
    alert_trials: bool = Field(default=True)
    alert_articles: bool = Field(default=True)
    alert_conferences: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Unique constraint: one subscription per user per product
        pass

# =====================
# SaaS / Subscription Models
# =====================

class SubscriptionPlan(SQLModel, table=True):
    """Available subscription tiers"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g., "Free", "Pro", "Enterprise"
    price_monthly: float  # e.g., 0.0, 29.99
    currency: str = "USD"
    features: str  # JSON string of features, e.g. '["search", "predictor"]'
    stripe_price_id: Optional[str] = None

class UserSubscription(SQLModel, table=True):
    """Tracks a user's active subscription"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    plan_id: int = Field(foreign_key="subscriptionplan.id")
    
    status: str = "active" # active, past_due, canceled
    start_date: datetime = Field(default_factory=datetime.utcnow)
    next_billing_date: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None


class DrugInteraction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    drug_a_id: int = Field(foreign_key="product.id")
    drug_b_id: int = Field(foreign_key="product.id")
    
    interaction_type: str # "Synergy", "Antagonism", etc.
    effect_description: str
    severity: str # "High", "Moderate", "Low"

class RegulatoryDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    
    title: str = Field(description="Document title, e.g. 'Protocol v2.1'")
    type: str = Field(description="Document type: 'Protocol', 'IB', 'Ethics', 'Contract'")
    status: str = Field(description="Status: 'Pending', 'In Review', 'Approved', 'Expired'")
    
    submission_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

class ClinicalBudget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trial_id: int = Field(foreign_key="clinicaltrial.id")
    
    site_name: str = Field(description="Name of the hospital/center")
    allocated_amount: float = Field(default=0.0)
    spent_amount: float = Field(default=0.0)
    
    currency: str = Field(default="EUR")
    status: str = Field(default="Active") # Active, Closed, Hold
