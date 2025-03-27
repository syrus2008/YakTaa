import sqlite3
import json

def check_database_structure():
    """Check the structure of the database tables."""
    conn = sqlite3.connect('worlds.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check item tables
    item_tables = [
        "hardware_items", 
        "consumable_items", 
        "software_items", 
        "weapon_items", 
        "clothing_items", 
        "implant_items"
    ]
    
    print("\nChecking item tables:")
    missing_tables = []
    
    for table_name in item_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"- {table_name}: MISSING")
            missing_tables.append(table_name)
        else:
            print(f"- {table_name}: EXISTS")
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"  Columns: {', '.join([col[1] for col in columns])}")
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Row count: {count}")
    
    conn.close()
    return missing_tables

if __name__ == "__main__":
    check_database_structure()
