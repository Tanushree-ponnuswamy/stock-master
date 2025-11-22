from sqlalchemy import text
from core.database import engine

def reset_moves_table():
    print("Connecting to database...")
    with engine.connect() as connection:
        print("Dropping table 'stock_moves'...")
        connection.execute(text("DROP TABLE IF EXISTS stock_moves CASCADE"))
        connection.commit()
        print("Table 'stock_moves' deleted successfully.")
        print("Please restart your server to recreate it with new columns.")

if __name__ == "__main__":
    reset_moves_table()