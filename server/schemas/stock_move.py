from pydantic import BaseModel
from datetime import datetime

class StockMoveCreate(BaseModel):
    sku: str
    move_type: str
    quantity: int
    location: str
    # Note: We don't ask for name/price from frontend, backend finds it

class StockMoveResponse(BaseModel):
    id: int
    product_name: str
    sku: str
    move_type: str
    quantity: int
    location: str = None
    unit_price: float
    total_value: float
    created_at: datetime

    class Config:
        from_attributes = True