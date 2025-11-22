from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from core.database import Base

class Product(Base):
    __tablename__ = "product_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    uom = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    price = Column(Float, default=0.0) # <--- NEW COLUMN
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())