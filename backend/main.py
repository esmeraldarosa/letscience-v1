from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import SQLModel, Session, create_engine, select
from typing import List, Optional
from pydantic import BaseModel
from .models import (
    Product, Patent, ScientificArticle, ClinicalTrial, Conference, User, AlertSubscription,
    ProductPharmacokinetics, ProductPharmacodynamics, ProductExperimentalModel, ProductSynthesisScheme,
    Product, Patent, ScientificArticle, ClinicalTrial, Conference, User, AlertSubscription,
    ProductPharmacokinetics, ProductPharmacodynamics, ProductExperimentalModel, ProductSynthesisScheme,
    ProductMilestone, ProductIndication
)
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

# Mount data images
backend_static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(backend_static_path):
    os.makedirs(backend_static_path)
app.mount("/static", StaticFiles(directory=backend_static_path), name="backend_static")

# --- Endpoints ---

@app.get("/")
def root():
    return RedirectResponse(url="/app/index.html")

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
        "synthesis_schemes": [{"name": s.scheme_name, "description": s.scheme_description, "image_url": s.scheme_image_url, "source_url": s.source_url} for s in product.synthesis_schemes],
        "summary": {
            "total_patents": len(product.patents),
            "total_articles": len(product.articles),
            "total_trials": len(product.trials),
            "latest_phase": product.development_phase
        },
        "pharmacokinetics": [{"parameter": p.parameter, "value": p.value, "unit": p.unit} for p in product.pharmacokinetics],
        "pharmacodynamics": [{"parameter": p.parameter, "value": p.value, "unit": p.unit, "target": p.target} for p in product.pharmacodynamics],
        "experimental_models": [{"model_name": m.model_name, "model_type": m.model_type, "description": m.description} for m in product.experimental_models]
    }


from fastapi import Query

@app.get("/products/compare")
def compare_products(ids: List[int] = Query(..., description="List of product IDs to compare"), session: Session = Depends(get_session)):
    """
    Returns aggregated data for comparing multiple products side-by-side.
    """
    # Fetch all requested products
    products = session.exec(select(Product).where(Product.id.in_(ids))).all()
    
    if not products:
        return {"products": [], "message": "No products found"}

    # Base Product Info
    products_info = []
    for p in products:
        products_info.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "phase": p.development_phase,
            "target": p.target_indication
        })
    
    # Pharmacokinetics Pivot
    # Structure: { "Tmax": { "Product A": "2h", "Product B": "4h" }, ... }
    pk_data = {}
    # First, gather all unique parameters existing across these products
    all_pks = session.exec(select(ProductPharmacokinetics).where(ProductPharmacokinetics.product_id.in_(ids))).all()
    
    for pk in all_pks:
        if pk.parameter not in pk_data:
            pk_data[pk.parameter] = {}
        # Find product name for this pk
        p_name = next((p.name for p in products if p.id == pk.product_id), "Unknown")
        pk_data[pk.parameter][p_name] = f"{pk.value} {pk.unit or ''}".strip()
        
    # Timeline Events (Milestones + Trials)
    timeline_events = []
    
    # 1. Milestones
    milestones = session.exec(select(ProductMilestone).where(ProductMilestone.product_id.in_(ids))).all()
    for m in milestones:
        p_name = next((p.name for p in products if p.id == m.product_id), "Unknown")
        timeline_events.append({
            "product": p_name,
            "date": m.date,
            "type": "Milestone",
            "title": m.event,
            "phase": m.phase
        })
        
    # 2. Trials
    # 2. Trials
    trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id.in_(ids))).all()
    for t in trials:
        if t.start_date: # Only include if we have a date
            p_name = next((p.name for p in products if p.id == t.product_id), "Unknown")
            
            # Estimate end date if missing (Phase 1=1yr, Ph2=2yr, Ph3=3yr)
            end = t.completion_date
            if not end:
                duration_days = 365
                if "Phase 2" in t.phase: duration_days = 730
                if "Phase 3" in t.phase: duration_days = 1095
                end = t.start_date.replace(year=t.start_date.year + (duration_days // 365)) # Rough approx
                
            timeline_events.append({
                "product": p_name,
                "date": t.start_date,
                "end_date": end,
                "type": "Trial Start",
                "title": t.title,
                "phase": t.phase
            })
            
    # Sort by date
    timeline_events.sort(key=lambda x: x["date"])
    
    # Earliest Patent Expiry per Product (Approximation)
    patent_cliffs = []
    patents = session.exec(select(Patent).where(Patent.product_id.in_(ids))).all()
    
    # Group by product
    from collections import defaultdict
    prod_patents = defaultdict(list)
    for pat in patents:
        prod_patents[pat.product_id].append(pat)
        
    for p in products:
        # Estimate: +20 years from earliest filing/publication (very rough proxy using publication date for demo)
        if prod_patents[p.id]:
            # Use the latest publication date + 20 years as a simple proxy for "cliff"
            # In reality, you'd use filing date, but we have pub date
            sorted_pats = sorted(prod_patents[p.id], key=lambda x: x.publication_date or datetime.min, reverse=True)
            if sorted_pats and sorted_pats[0].publication_date:
                latest_pub = sorted_pats[0].publication_date
                expiry_est = latest_pub.year + 20 
                patent_cliffs.append({
                    "product": p.name,
                    "year": expiry_est, 
                    "notes": "Estimated ~20 years from latest patent pub."
                })

    return {
        "products": products_info,
        "pk_comparison": pk_data,
        "timeline_events": timeline_events,
        "patent_cliffs": patent_cliffs
    }


# Import connector
from .pubmed_connector import fetch_pubmed_articles
from datetime import datetime

@app.post("/products/{product_id}/refresh-articles")
async def refresh_product_articles(product_id: int, session: Session = Depends(get_session)):
    """
    Triggers a real-time fetch of articles from PubMed for the given product.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Fetch real data
    print(f"Fetching PubMed data for {product.name}...")
    try:
        articles_data = await fetch_pubmed_articles(product.name, max_results=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"External API failed: {str(e)}")
        
    added_count = 0
    
    for item in articles_data:
        # Check duplicate by title (simple check)
        # In a real app, use DOI or hash
        exists = session.exec(select(ScientificArticle).where(
            ScientificArticle.product_id == product_id,
            ScientificArticle.title == item["title"]
        )).first()
        
        if not exists:
            # Parse date safely
            pub_date = datetime.now()
            try:
                # Try parsing "YYYY Mon DD" or "YYYY"
                # This is a naive parser for demo
                 pub_date = datetime.strptime(item["date"][0:4], "%Y")
            except:
                pass

            new_article = ScientificArticle(
                product_id=product_id,
                title=item["title"],
                doi=item["doi"],
                authors=item["authors"],
                abstract=item["desc"], # Summary from e-utils
                url=item["url"],
                publication_date=pub_date
            )
            session.add(new_article)
            added_count += 1
            
    session.commit()
    
    return {
        "message": f"Successfully refreshed data. Added {added_count} new articles.",
        "articles_found": len(articles_data),
        "articles_added": added_count
    }

class ChatRequest(BaseModel):
    query: str
    context_product_id: Optional[int] = None

@app.post("/chat")
def chat_with_science(request: ChatRequest, session: Session = Depends(get_session)):
    """
    Deterministic RAG-lite endpoint.
    Parses query for keywords and intents, searches DB, constructs a response.
    """
    q = request.query.lower()
    
    # Brand Name Mapping (Simple Dictionary for MVP)
    brand_map = {
        "keytruda": "pembrolizumab",
        "opdivo": "nivolumab", 
        "humira": "adalimumab",
        "ozempic": "semaglutide",
        "wegovy": "semaglutide",
        "eliquis": "apixaban"
    }
    
    # Replace brands in query with generics
    for brand, generic in brand_map.items():
        if brand in q:
            q = q.replace(brand, generic)

    # Intent 1: Comparatives (If users ask here instead of using the view)
    if "compare" in q or "vs" in q:
        return {
            "text": "For detailed comparisons, please use the 'Compare' tab in the sidebar. I can help you find specific data points here though!",
            "related_data": []
        }

    # Intent 2: Specific Data Search
    # Keywords: trial, patent, article, paper, study, side effect
    
    response_text = "I couldn't find specific data matching your query."
    related_data = [] # List of dicts { title, type, detail }
    
    products = session.exec(select(Product)).all()
    # Identify Product in Query
    target_product = None
    if request.context_product_id:
         target_product = session.get(Product, request.context_product_id)
    else:
        for p in products:
            if p.name.lower() in q:
                target_product = p
                break
    
    if not target_product and not "all" in q:
         return {
            "text": "Could you specify which product you are asking about? (e.g., 'Keytruda trials')",
            "related_data": []
        }

    p_id = target_product.id if target_product else None
    p_name = target_product.name if target_product else "all products"

    # Sub-intent: Clinical Trials
    if "trial" in q or "clinical" in q or "phase" in q:
        query = select(ClinicalTrial)
        if p_id:
            query = query.where(ClinicalTrial.product_id == p_id)
        
        # Filter by phase if mentioned
        if "phase 1" in q: query = query.where(ClinicalTrial.phase == "Phase 1")
        elif "phase 2" in q: query = query.where(ClinicalTrial.phase == "Phase 2")
        elif "phase 3" in q: query = query.where(ClinicalTrial.phase == "Phase 3")
        
        results = session.exec(query).all()
        count = len(results)
        response_text = f"I found {count} clinical trials for {p_name}."
        for t in results[:5]: # Top 5
            related_data.append({
                "type": "Trial",
                "title": t.title,
                "detail": f"{t.phase} - {t.status} ({t.start_date})"
            })

    # Sub-intent: Patents
    elif "patent" in q or "ip" in q or "expiry" in q:
        query = select(Patent)
        if p_id: 
            query = query.where(Patent.product_id == p_id)
        
        results = session.exec(query).all()
        count = len(results)
        response_text = f"I found {count} patents related to {p_name}."
        for p in results[:5]:
            related_data.append({
                "type": "Patent",
                "title": p.title,
                "detail": f"{p.patent_type} - {p.status}"
            })

    # Sub-intent: Scientific Articles
    elif "article" in q or "paper" in q or "study" in q or "publication" in q:
        query = select(ScientificArticle)
        if p_id:
            query = query.where(ScientificArticle.product_id == p_id)
        
        results = session.exec(query).all()
        count = len(results)
        response_text = f"There are {count} scientific articles associated with {p_name}."
        for a in results[:5]:
            related_data.append({
                "type": "Article",
                "title": a.title,
                "detail": f"{a.authors} ({a.publication_date.year if a.publication_date else 'N/A'})"
            })
            
    # Sub-intent: General Info / Description
    elif "what is" in q or "description" in q or "mechanism" in q:
        if target_product:
            response_text = f"**{target_product.name}** is currently in **{target_product.development_phase}** for **{target_product.target_indication}**.\n\n{target_product.description}"
        
    else:
        # Fallback search across everything for the product
        if target_product:
             response_text = f"Showing general intelligence for {target_product.name}. Please ask about 'trials', 'patents', or 'articles' for more specific lists."
             related_data.append({"type": "Info", "title": "Development Phase", "detail": target_product.development_phase})
             related_data.append({"type": "Info", "title": "Indication", "detail": target_product.target_indication})

    return {
        "text": response_text,
        "related_data": related_data
    }

# =====================
# Authentication Endpoints
# =====================

@app.get("/patents/")
def get_all_patents(session: Session = Depends(get_session)):
    """
    Returns a unified list of all patents across all products.
    """
    # Join Patent with Product to get product name
    results = session.exec(
        select(Patent, Product.name)
        .join(Product, Patent.product_id == Product.id)
    ).all()
    
    # Format response
    patents_data = []
    for patent, product_name in results:
        patents_data.append({
            "id": patent.id,
            "product_id": patent.product_id,
            "product_name": product_name,
            "source_id": patent.source_id,
            "title": patent.title,
            "abstract": patent.abstract,
            "assignee": patent.assignee,
            "status": patent.status,
            "publication_date": patent.publication_date,
            "url": patent.url,
            "claim_summary": patent.claim_summary,
            "patent_type": patent.patent_type,
            "diseases_in_claims": patent.diseases_in_claims
        })
        
    return patents_data

@app.get("/articles/")
def get_all_articles(session: Session = Depends(get_session)):
    """
    Returns a unified list of all scientific articles across all products.
    """
    results = session.exec(
        select(ScientificArticle, Product.name)
        .join(Product, ScientificArticle.product_id == Product.id)
    ).all()
    
    articles_data = []
    for article, product_name in results:
        articles_data.append({
            "id": article.id,
            "product_id": article.product_id,
            "product_name": product_name,
            "doi": article.doi,
            "title": article.title,
            "abstract": article.abstract,
            "authors": article.authors,
            "publication_date": article.publication_date,
            "url": article.url
        })
        
    return articles_data

@app.get("/conferences/")
def get_all_conferences(session: Session = Depends(get_session)):
    """Aggregates all conferences."""
    results = session.exec(select(Conference, Product.name).join(Product, Conference.product_id == Product.id)).all()
    data = []
    for conf, p_name in results:
        data.append({
            "id": conf.id, "product_id": conf.product_id, "product_name": p_name,
            "title": conf.title, "abstract": conf.abstract, 
            "conference_name": conf.conference_name, "date": conf.date, "url": conf.url
        })
    return data

@app.get("/adme/")
def get_all_adme(session: Session = Depends(get_session)):
    """Aggregates all PK (ADME) data."""
    results = session.exec(select(ProductPharmacokinetics, Product.name).join(Product, ProductPharmacokinetics.product_id == Product.id)).all()
    data = []
    for pk, p_name in results:
        data.append({
            "id": pk.id, "product_id": pk.product_id, "product_name": p_name,
            "parameter": pk.parameter, "value": pk.value, "unit": pk.unit
        })
    return data

@app.get("/models/")
def get_all_models(session: Session = Depends(get_session)):
    """Aggregates all Experimental Models."""
    results = session.exec(select(ProductExperimentalModel, Product.name).join(Product, ProductExperimentalModel.product_id == Product.id)).all()
    data = []
    for model, p_name in results:
        data.append({
            "id": model.id, "product_id": model.product_id, "product_name": p_name,
            "model_name": model.model_name, "model_type": model.model_type, "description": model.description
        })
    return data

@app.get("/preclinical/")
def get_all_preclinical(session: Session = Depends(get_session)):
    """Aggregates all PD (Preclinical) data."""
    results = session.exec(select(ProductPharmacodynamics, Product.name).join(Product, ProductPharmacodynamics.product_id == Product.id)).all()
    data = []
    for pd, p_name in results:
        data.append({
            "id": pd.id, "product_id": pd.product_id, "product_name": p_name,
            "parameter": pd.parameter, "value": pd.value, "unit": pd.unit, "target": pd.target
        })
    return data

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
    
@app.get("/clinical/")
def get_all_clinical_trials(session: Session = Depends(get_session)):
    """
    Returns a unified list of all clinical trials.
    """
    results = session.exec(
        select(ClinicalTrial, Product.name)
        .join(Product, ClinicalTrial.product_id == Product.id)
    ).all()
    
    trials_data = []
    for trial, product_name in results:
        trials_data.append({
            "id": trial.id,
            "product_id": trial.product_id,
            "product_name": product_name,
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "phase": trial.phase,
            "start_date": trial.start_date,
            "sponsor": trial.sponsor,
            "url": trial.url
        })
    return trials_data

@app.get("/synthesis/")
def get_all_synthesis(session: Session = Depends(get_session)):
    """
    Returns synthesis schemes. 
    """
    schemes_results = session.exec(
        select(ProductSynthesisScheme, Product.name)
        .join(Product, ProductSynthesisScheme.product_id == Product.id)
    ).all()
    
    schemes_data = []
    for scheme, product_name in schemes_results:
        # Filter: Exclude biological/recombinant manufacturing
        name_lower = scheme.scheme_name.lower()
        if "recombinant" in name_lower or "biologics" in name_lower:
            continue
            
        schemes_data.append({
            "type": "scheme",
            "id": scheme.id,
            "product_id": scheme.product_id,
            "product_name": product_name,
            "name": scheme.scheme_name,
            "description": scheme.scheme_description,
            "image_url": scheme.scheme_image_url,
            "source_url": scheme.source_url
        })
    
    return schemes_data

# Force reload for schema update
# --- Reporting ---
from backend.report_generator import create_dossier
from fastapi.responses import StreamingResponse
import io

@app.get("/products/{product_id}/dossier")
def download_dossier(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            return {"error": "Product not found"}
            
        trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id == product_id)).all()
        patents = session.exec(select(Patent).where(Patent.product_id == product_id)).all()
        articles = session.exec(select(ScientificArticle).where(ScientificArticle.product_id == product_id)).all()
        
        milestones = session.exec(select(ProductMilestone).where(ProductMilestone.product_id == product_id)).all()
        synthesis_schemes = session.exec(select(ProductSynthesisScheme).where(ProductSynthesisScheme.product_id == product_id)).all()
        indications = session.exec(select(ProductIndication).where(ProductIndication.product_id == product_id)).all()
        
        pdf = create_dossier(product, trials, patents, articles, milestones, synthesis_schemes, indications)
        
        # Output to stream
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={product.name}_Dossier.pdf"}
        )

from backend.report_generator import create_landscape_dossier

@app.get("/reports/landscape")
def generate_landscape_report(
    type: str = Query(..., description="Report type: disease, target, company, mechanism"),
    query: str = Query(..., description="Search query"),
    session: Session = Depends(get_session)
):
    """
    Generates an aggregated Landscape Report PDF.
    """
    # 1. Find Products
    products = []
    
    if type.lower() == "disease":
        # Search Indications and Target Indication
        # Get IDs from ProductIndication
        ind_Product_ids = session.exec(select(ProductIndication.product_id).where(ProductIndication.disease_name.contains(query))).all()
        # Get Products matching target_indication
        prod_results = session.exec(select(Product).where(Product.target_indication.contains(query))).all()
        
        # Combine
        all_ids = set(ind_Product_ids) | set([p.id for p in prod_results])
        if all_ids:
            products = session.exec(select(Product).where(Product.id.in_(all_ids))).all()
            
    elif type.lower() == "target":
        # Search PD targets and Product Description (heuristic)
        pd_ids = session.exec(select(ProductPharmacodynamics.product_id).where(ProductPharmacodynamics.target.contains(query))).all()
        prod_results = session.exec(select(Product).where(Product.description.contains(query))).all()
        
        all_ids = set(pd_ids) | set([p.id for p in prod_results])
        if all_ids:
            products = session.exec(select(Product).where(Product.id.in_(all_ids))).all()
            
    elif type.lower() == "company":
        # Infer from Sponsors and Assignees
        trial_ids = session.exec(select(ClinicalTrial.product_id).where(ClinicalTrial.sponsor.contains(query))).all()
        patent_ids = session.exec(select(Patent.product_id).where(Patent.assignee.contains(query))).all()
        
        all_ids = set(trial_ids) | set(patent_ids)
        if all_ids:
            products = session.exec(select(Product).where(Product.id.in_(all_ids))).all()
            
    elif type.lower() == "mechanism":
        # Heuristic search in description
        products = session.exec(select(Product).where(Product.description.contains(query))).all()
        
    elif type.lower() in ["drug", "drugs", "product", "products"]:
        products = session.exec(select(Product).where(Product.name.contains(query))).all()

        
    if not products:
        # Return 404 or empty report? Let's return error for now
        return JSONResponse(status_code=404, content={"message": f"No products found for {type}: {query}"})
        
    # 2. Gather Data for ALL products
    product_ids = [p.id for p in products]
    
    all_trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id.in_(product_ids))).all()
    all_patents = session.exec(select(Patent).where(Patent.product_id.in_(product_ids))).all()
    all_milestones = session.exec(select(ProductMilestone).where(ProductMilestone.product_id.in_(product_ids))).all()
    
    # 3. Generate PDF
    pdf = create_landscape_dossier(type.capitalize(), query, products, all_trials, all_patents, all_milestones)
    
    # 4. Stream Response
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    filename = f"Landscape_{type}_{query}.pdf".replace(" ", "_")
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ==========================
# Analysis Endpoints
# ==========================

from pydantic import BaseModel
from backend.analysis import analyze_combination

class CombinationRequest(BaseModel):
    drug_a_id: int
    drug_b_id: int

@app.post("/analysis/combine")
def analyze_drug_combination(
    request: CombinationRequest,
    session: Session = Depends(get_session)
):
    """
    Analyzes potential interactions (synergy, toxicity) between two drugs.
    """
    result = analyze_combination(session, request.drug_a_id, request.drug_b_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result

@app.post("/analysis/report")
def generate_analysis_report(
    request: CombinationRequest,
    session: Session = Depends(get_session)
):
    """
    Generates a PDF brief of the interaction analysis.
    """
    from backend.report_generator import create_combination_brief
    import io

    # 1. Run Analysis
    result = analyze_combination(session, request.drug_a_id, request.drug_b_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # 2. Generate PDF
    pdf_bytes = create_combination_brief(result)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Analysis_{result['drug_a']['name']}_vs_{result['drug_b']['name']}.pdf"}
    )
