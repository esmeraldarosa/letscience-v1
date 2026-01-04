from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Session, create_engine, select
from typing import List, Optional
from pydantic import BaseModel
from .models import Product, Patent, ScientificArticle, ClinicalTrial, Conference, User, AlertSubscription
from .auth import (
    hash_password, verify_password, 
    create_token, verify_token,
    generate_totp_secret, verify_totp, get_totp_uri
)
from contextlib import asynccontextmanager
from datetime import datetime

sqlite_file_name = "database.db"
# Use absolute path to ensure we access the same DB as the seed script (which placed it in backend/)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Enable CORS just in case
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# We expect a 'frontend' directory at the root or parallel to backend
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(static_path):
    app.mount("/app", StaticFiles(directory=static_path, html=True), name="static")

# --- Endpoints ---

@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@app.get("/products/", response_model=List[Product])
def read_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

@app.get("/products/{product_id}/intelligence")
def get_product_intelligence(product_id: int, session: Session = Depends(get_session)):
    """
    Returns a unified view of all intelligence for a product.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_info": product,
        "patents": product.patents,
        "scientific_articles": product.articles,
        "clinical_trials": product.trials,
        "conferences": product.conferences,
        "side_effects": [se.effect for se in product.side_effects],
        "synthesis_steps": [s.step_description for s in product.synthesis_steps],
        "milestones": [{"date": m.date.isoformat(), "event": m.event, "phase": m.phase} for m in product.milestones],
        "indications": [{"disease": i.disease_name, "status": i.approval_status, "ref_title": i.reference_title, "ref_url": i.reference_url} for i in product.indications],
        "synthesis_schemes": [{"name": s.scheme_name, "description": s.scheme_description, "image_url": s.scheme_image_url} for s in product.synthesis_schemes],
        "summary": {
            "total_patents": len(product.patents),
            "total_articles": len(product.articles),
            "total_trials": len(product.trials),
            "latest_phase": product.development_phase
        }
    }


# =====================
# Authentication Endpoints
# =====================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class Verify2FARequest(BaseModel):
    code: str
    temp_token: str

def get_current_user(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)) -> Optional[User]:
    """Get current authenticated user from token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return None
    user = session.exec(select(User).where(User.id == payload["user_id"])).first()
    return user

@app.post("/auth/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new user (admin only in production)"""
    # Check if username exists
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = session.exec(select(User).where(User.email == data.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        is_admin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": "User registered successfully", "user_id": user.id}

@app.post("/auth/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    """Login with username and password"""
    user = session.exec(select(User).where(User.username == data.username)).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Check if 2FA is enabled
    if user.is_2fa_enabled:
        # Return temporary token that requires 2FA verification
        temp_token = create_token(user.id, user.username)
        return {
            "requires_2fa": True,
            "temp_token": temp_token,
            "message": "Please enter your 2FA code"
        }
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # Return full access token
    token = create_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

@app.post("/auth/verify-2fa")
def verify_2fa(data: Verify2FARequest, session: Session = Depends(get_session)):
    """Verify 2FA code to complete login"""
    payload = verify_token(data.temp_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = session.exec(select(User).where(User.id == payload["user_id"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_totp(user.totp_secret, data.code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # Return full access token
    token = create_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

@app.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_2fa_enabled": user.is_2fa_enabled
    }

@app.post("/auth/setup-2fa")
def setup_2fa(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Generate 2FA secret and return QR code URI"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Generate new TOTP secret
    secret = generate_totp_secret()
    user.totp_secret = secret
    session.add(user)
    session.commit()
    
    # Return URI for QR code
    uri = get_totp_uri(secret, user.username)
    return {
        "secret": secret,
        "qr_uri": uri,
        "message": "Scan this QR code with Google Authenticator"
    }

@app.post("/auth/enable-2fa")
def enable_2fa(code: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Enable 2FA after verifying a code"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="Please setup 2FA first")
    
    if not verify_totp(user.totp_secret, code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    user.is_2fa_enabled = True
    session.add(user)
    session.commit()
    
    return {"message": "2FA enabled successfully"}


# =====================
# Alert Subscription Endpoints
# =====================

@app.post("/alerts/subscribe/{product_id}")
def subscribe_to_product(product_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Subscribe to alerts for a product"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if already subscribed
    existing = session.exec(
        select(AlertSubscription).where(
            AlertSubscription.user_id == user.id,
            AlertSubscription.product_id == product_id
        )
    ).first()
    
    if existing:
        return {"message": "Already subscribed", "subscribed": True}
    
    # Create new subscription
    subscription = AlertSubscription(
        user_id=user.id,
        product_id=product_id
    )
    session.add(subscription)
    session.commit()
    
    return {"message": "Subscribed to product alerts", "subscribed": True}

@app.delete("/alerts/unsubscribe/{product_id}")
def unsubscribe_from_product(product_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Unsubscribe from alerts for a product"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscription = session.exec(
        select(AlertSubscription).where(
            AlertSubscription.user_id == user.id,
            AlertSubscription.product_id == product_id
        )
    ).first()
    
    if subscription:
        session.delete(subscription)
        session.commit()
    
    return {"message": "Unsubscribed from product alerts", "subscribed": False}

@app.get("/alerts/check/{product_id}")
def check_subscription(product_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Check if user is subscribed to a product"""
    if not user:
        return {"subscribed": False}
    
    subscription = session.exec(
        select(AlertSubscription).where(
            AlertSubscription.user_id == user.id,
            AlertSubscription.product_id == product_id
        )
    ).first()
    
    return {"subscribed": subscription is not None}

@app.get("/alerts/my-subscriptions")
def get_my_subscriptions(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Get all products user is subscribed to"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscriptions = session.exec(
        select(AlertSubscription).where(AlertSubscription.user_id == user.id)
    ).all()
    
    product_ids = [s.product_id for s in subscriptions]
    products = session.exec(select(Product).where(Product.id.in_(product_ids))).all() if product_ids else []
    
    return {
        "subscriptions": [
            {"product_id": p.id, "product_name": p.name, "indication": p.target_indication}
            for p in products
        ]
    }
