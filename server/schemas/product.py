from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    sku: str
    category: str
    uom: str
    stock: int
    price: float # <--- NEW

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    uom: str
    stock: int
    price: float # <--- NEW

    class Config:
        from_attributes = True