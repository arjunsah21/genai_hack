import os
import pandas as pd
from sqlalchemy import create_engine, text
import time

def import_data():
    """Import CSV data into MariaDB database"""
    # DB connection settings from environment variables
    user = os.getenv('MARIA_USER', 'root')
    password = os.getenv('MARIA_PASS', 'rootpassword')
    host = os.getenv('MARIADB_HOST', 'mariadb')
    port = os.getenv('MARIADB_PORT', '3306')
    database = os.getenv('MARIA_DB', 'imdb_db')
    
    # Folder where CSVs are present
    csv_folder = '/app/data/output_csvs'
    
    print(f"Connecting to MariaDB at {host}:{port}...")
    
    # Wait for database to be ready
    max_retries = 30
    retry_interval = 2  # seconds
    
    for i in range(max_retries):
        try:
            # Try to create connection
            engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
            conn = engine.connect()
            conn.close()
            print("✅ Successfully connected to MariaDB!")
            break
        except Exception as e:
            print(f"⏳ Database not ready yet (attempt {i+1}/{max_retries}): {str(e)}")
            if i == max_retries - 1:
                print("❌ Failed to connect to database after maximum retries.")
                return
            time.sleep(retry_interval)
    
    # Create connection to database
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    conn = engine.connect()
    
    # Disable foreign key checks to avoid constraint issues during import
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    print("Foreign key checks disabled for import")
    
    # Check if CSV folder exists
    if not os.path.exists(csv_folder):
        print(f"❌ CSV folder not found at {csv_folder}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        conn.close()
        return
    
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    if not csv_files:
        print(f"❌ No CSV files found in {csv_folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to import")
    
    # Process each CSV file
    for file in csv_files:
        table_name = os.path.splitext(file)[0].lower()  # table name = filename in lowercase
        csv_path = os.path.join(csv_folder, file)
        
        print(f"➡️ Processing {file} into table `{table_name}`")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Print column information for debugging
            print(f"   Columns: {', '.join(df.columns)}")
            print(f"   Data types: {df.dtypes}")
            
            # Dump CSV into MariaDB table
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            
            print(f"✅ Dumped {len(df)} rows into table `{table_name}`")
        except Exception as e:
            print(f"❌ Error importing {file}: {str(e)}")
    
    # Re-enable foreign key checks
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    print("Foreign key checks re-enabled")
    conn.close()
    
    print("\n🎯 CSV import process completed!")

if __name__ == "__main__":
    import_data()
