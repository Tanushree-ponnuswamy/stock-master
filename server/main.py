from fastapi import FastAPI
from core.database import engine
from models import user, product, stock_move # <--- Import stock_move model
from routes import auth, products, stock_moves # <--- Import stock_moves route

# Create Tables
user.Base.metadata.create_all(bind=engine)
product.Base.metadata.create_all(bind=engine)
stock_move.Base.metadata.create_all(bind=engine) # <--- Create Table

app = FastAPI(title="Stock Master API")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(stock_moves.router)

@app.get("/")
def read_root():
    return {"message": "Stock Master Server is Running"}