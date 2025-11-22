from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductResponse

router = APIRouter(tags=["Products"])

@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    new_product = Product(
        name=product.name,
        sku=product.sku,
        category=product.category,
        uom=product.uom,
        stock=product.stock,
        price=product.price # <--- Save Price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# --- NEW: Endpoint to get single product details by SKU (For Auto-fill) ---
@router.get("/products/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product