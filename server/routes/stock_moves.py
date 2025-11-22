from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.stock_move import StockMove
from models.product import Product 
from schemas.stock_move import StockMoveCreate, StockMoveResponse

# This is the missing variable causing your error
router = APIRouter(tags=["Stock Moves"])

@router.post("/stock-moves", response_model=StockMoveResponse)
def create_stock_move(move: StockMoveCreate, db: Session = Depends(get_db)):
    # 1. Find the Product
    product = db.query(Product).filter(Product.sku == move.sku).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"SKU {move.sku} not found")

    # 2. Update Product Stock
    if move.move_type == "IN":
        product.stock += move.quantity
    elif move.move_type == "OUT":
        if product.stock < move.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        product.stock -= move.quantity

    # 3. Calculate Values
    # Ensure price is not None (handle potential legacy data)
    current_price = product.price if product.price else 0.0
    total_val = current_price * move.quantity

    # 4. Create Record
    new_move = StockMove(
        product_name=product.name,
        sku=product.sku,
        move_type=move.move_type,
        quantity=move.quantity,
        location=move.location,
        unit_price=current_price,
        total_value=total_val
    )

    db.add(new_move)
    db.commit()
    db.refresh(new_move)
    return new_move

@router.get("/stock-moves", response_model=List[StockMoveResponse])
def get_stock_moves(db: Session = Depends(get_db)):
    return db.query(StockMove).order_by(StockMove.created_at.desc()).all()