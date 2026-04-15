from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pathlib import Path
import sys

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from . import models, schemas
    from .auth import (
        create_access_token,
        get_current_active_user,
        get_db,
        get_password_hash,
        get_user_by_username,
        verify_password,
    )
    from .database import Base, SessionLocal, engine
except ImportError:
    # Fallback for direct script execution: `python app/main.py`
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from app import models, schemas
    from app.auth import (
        create_access_token,
        get_current_active_user,
        get_db,
        get_password_hash,
        get_user_by_username,
        verify_password,
    )
    from app.database import Base, SessionLocal, engine

app = FastAPI(
    title="Product API mit Dependency Injection + Auth",
    description="Product API mit SQLite, JWT und protected Endpoints",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_username = "test@test.com"
        seed_password = "test"
        if not get_user_by_username(db, seed_username):
            seed_user = models.User(
                username=seed_username,
                hashed_password=get_password_hash(seed_password),
                is_active=True,
            )
            db.add(seed_user)
            db.commit()
    finally:
        db.close()


def product_to_dict(product: models.Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "stock": product.stock,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/users/", response_model=schemas.UserRead, status_code=201)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username already registered"
        )

    user = models.User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
):
    return current_user


@app.get("/products/", response_model=List[schemas.ProductRead])
def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price darf nicht größer als max_price sein",
        )

    stmt = select(models.Product)

    if category is not None:
        stmt = stmt.where(models.Product.category == category)
    if min_price is not None:
        stmt = stmt.where(models.Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(models.Product.price <= max_price)

    stmt = stmt.offset(skip).limit(limit)
    products = db.execute(stmt).scalars().all()
    return [product_to_dict(p) for p in products]


@app.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return product_to_dict(product)


@app.post("/products/", response_model=schemas.ProductRead, status_code=201)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    now = datetime.utcnow()
    db_product = models.Product(**product.model_dump())
    db_product.created_at = now
    db_product.updated_at = now

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return product_to_dict(db_product)


@app.put("/products/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    product.updated_at = datetime.utcnow()
    db.add(product)
    db.commit()
    db.refresh(product)
    return product_to_dict(product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    db.delete(product)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

