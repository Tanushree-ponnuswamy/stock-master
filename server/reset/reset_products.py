from sqlalchemy import text
from core.database import engine

def reset_products_table():
    print("Connecting to database...")
    with engine.connect() as connection:
        print("Dropping table 'product_details'...")
        connection.execute(text("DROP TABLE IF EXISTS product_details CASCADE"))
        connection.commit()
        print("Table 'product_details' deleted successfully.")
        print("Please restart your server to recreate it with new columns.")

if __name__ == "__main__":
    reset_products_table()