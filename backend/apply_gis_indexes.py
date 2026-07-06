import sys
import os
from sqlalchemy import text

# Add current folder to path
sys.path.insert(0, os.getcwd())

from database.database import engine

def main():
    print("Checking and applying database indexes for Lat/Lng GIS queries...")
    with engine.connect() as conn:
        # Check if ix_complaints_lat_lng exists
        result_comp = conn.execute(text(
            "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE c.relname = 'ix_complaints_lat_lng' AND n.nspname = 'public';"
        )).scalar()
        
        if not result_comp:
            print("Creating index ix_complaints_lat_lng...")
            conn.execute(text("CREATE INDEX ix_complaints_lat_lng ON complaints (lat, lng);"))
            conn.commit()
            print("[OK] ix_complaints_lat_lng created.")
        else:
            print("[OK] ix_complaints_lat_lng already exists.")

        # Check if ix_resources_lat_lng exists
        result_res = conn.execute(text(
            "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE c.relname = 'ix_resources_lat_lng' AND n.nspname = 'public';"
        )).scalar()
        
        if not result_res:
            print("Creating index ix_resources_lat_lng...")
            conn.execute(text("CREATE INDEX ix_resources_lat_lng ON resources (lat, lng);"))
            conn.commit()
            print("[OK] ix_resources_lat_lng created.")
        else:
            print("[OK] ix_resources_lat_lng already exists.")
            
    print("Database GIS indexes verification completed.")

if __name__ == "__main__":
    main()
