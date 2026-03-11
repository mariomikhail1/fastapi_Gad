from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator


app = FastAPI(
    title="Product API",
    description="API für Produktverwaltung (Starter-Version)",
    version="0.1.0",
)

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


@app.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """
    Erstellt ein neues Produkt.

    - **name**: Produktname (required)
    - **description**: Produktbeschreibung (optional)
    - **price**: Preis in Euro (required, > 0)
    - **category**: Kategorie (required)
    """
    product_dict = product.dict()
    new_id = len(products_db) + 1
    now = datetime.utcnow()

    product_dict.update(
        {
            "id": new_id,
            "created_at": now,
            "updated_at": now,
        }
    )

    products_db.append(product_dict)
    return product_dict


@app.get("/products/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """
    Gibt eine Liste von Produkten zurück.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price darf nicht größer als max_price sein",
        )

    items = products_db

    if category is not None:
        items = [p for p in items if p["category"] == category]

    if min_price is not None:
        items = [p for p in items if p["price"] >= min_price]

    if max_price is not None:
        items = [p for p in items if p["price"] <= max_price]

    return items[skip : skip + limit]


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Gibt ein spezifisches Produkt zurück.
    """
    product = next((p for p in products_db if p["id"] == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate):
    """
    Aktualisiert ein bestehendes Produkt.
    """
    product_index = next(
        (i for i, p in enumerate(products_db) if p["id"] == product_id), None
    )
    if product_index is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    update_data = product_update.dict(exclude_unset=True)

    products_db[product_index].update(update_data)
    products_db[product_index]["updated_at"] = datetime.utcnow()

    return products_db[product_index]


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """
    Löscht ein Produkt.
    """
    product_index = next(
        (i for i, p in enumerate(products_db) if p["id"] == product_id), None
    )
    if product_index is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    products_db.pop(product_index)
    return None

