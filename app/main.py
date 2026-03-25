from datetime import datetime
from typing import Generator, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from .database import Base, SessionLocal, engine
from .models import Product
from . import schemas as product_schemas


app = FastAPI(
    title="Product API",
    description="API für Produktverwaltung (Starter-Version)",
    version="0.1.0",
)

# ---------- DB dependency ----------
@app.on_event("startup")
def on_startup() -> None:
    # Create tables if they don't exist yet.
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def product_to_dict(product: Product) -> dict:
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


# In-Memory Database (nur für Demo, geht beim Neustart verloren)
products_db: list[dict] = []


# ---------- Pydantic Models ----------


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    category: str
    stock: int = Field(..., ge=0)

    @validator("price")
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Preis muss positiv sein")
        return v


class ProductCreate(ProductBase):
    """Input-Modell für Produkt-Erstellung"""

    pass


class ProductUpdate(BaseModel):
    """Input-Modell für Produkt-Update (alle Felder optional)"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Output-Modell für API-Responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---------- Endpoints ----------


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def root_redirect():
    # Allow opening the API in a browser via `/` by redirecting to Swagger UI.
    return RedirectResponse(url="/docs")


@app.post("/products/", response_model=product_schemas.ProductRead, status_code=201)
async def create_product(
    product: product_schemas.ProductCreate, db: Session = Depends(get_db)
):
    """
    Erstellt ein neues Produkt.

    - **name**: Produktname (required)
    - **description**: Produktbeschreibung (optional)
    - **price**: Preis in Euro (required, > 0)
    - **category**: Kategorie (required)
    """
    now = datetime.utcnow()

    db_product = Product(**product.model_dump())
    db_product.created_at = now
    db_product.updated_at = now

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return product_to_dict(db_product)


@app.get("/products/", response_model=List[product_schemas.ProductRead])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """
    Gibt eine Liste von Produkten zurück.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price darf nicht größer als max_price sein",
        )

    stmt = select(Product)

    if category is not None:
        stmt = stmt.where(Product.category == category)

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    stmt = stmt.offset(skip).limit(limit)

    products = db.execute(stmt).scalars().all()
    return [product_to_dict(p) for p in products]


@app.get("/products/{product_id}", response_model=product_schemas.ProductRead)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Gibt ein spezifisches Produkt zurück.
    """
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return product_to_dict(product)


@app.put("/products/{product_id}", response_model=product_schemas.ProductRead)
async def update_product(
    product_id: int,
    product_update: product_schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    """
    Aktualisiert ein bestehendes Produkt.
    """
    product = db.get(Product, product_id)
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
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Löscht ein Produkt.
    """
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    db.delete(product)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn

    # When starting via `python app/main.py`, uvicorn's `reload=True` spawns a
    # subprocess where the import path can differ and lead to
    # `ModuleNotFoundError: No module named 'app'`.
    # For local development, use `uvicorn app.main:app --reload` from the
    # project root instead.
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

