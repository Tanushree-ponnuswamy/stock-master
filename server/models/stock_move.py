from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from core.database import Base

class StockMove(Base):
    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)
    
    product_name = Column(String, nullable=False)
    sku = Column(String, index=True, nullable=False)
    
    move_type = Column(String, nullable=False) # "IN" or "OUT"
    quantity = Column(Integer, nullable=False)
    
    # --- NEW COLUMNS ---
    location = Column(String, nullable=True) # "From Loc" or "To Loc"
    unit_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())