import sqlite3
import os
import sys

# Path to the database
db_path = r'c:\Users\thibaut\Desktop\glata\yaktaa_world_editor\worlds.db'

def check_database():
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    print(f"Found database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        print("\n=== DATABASE TABLES ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Check for hardware_items table
        print("\n=== CHECKING HARDWARE ITEMS ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hardware_items'")
        if cursor.fetchone():
            print("hardware_items table exists")
            cursor.execute("PRAGMA table_info(hardware_items)")
            columns = cursor.fetchall()
            print("Columns:", ", ".join([col[1] for col in columns]))
            
            # Count items
            cursor.execute("SELECT COUNT(*) FROM hardware_items")
            count = cursor.fetchone()[0]
            print(f"Total hardware items: {count}")
            
            # Sample some items
            if count > 0:
                cursor.execute("SELECT id, name, hardware_type, price FROM hardware_items LIMIT 5")
                sample = cursor.fetchall()
                print("Sample items:")
                for item in sample:
                    print(f"  {item[0]} - {item[1]} (Type: {item[2]}, Price: {item[3]})")
        else:
            print("hardware_items table DOES NOT EXIST")
        
        # Check for software_items table
        print("\n=== CHECKING SOFTWARE ITEMS ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='software_items'")
        if cursor.fetchone():
            print("software_items table exists")
            cursor.execute("PRAGMA table_info(software_items)")
            columns = cursor.fetchall()
            print("Columns:", ", ".join([col[1] for col in columns]))
            
            # Count items
            cursor.execute("SELECT COUNT(*) FROM software_items")
            count = cursor.fetchone()[0]
            print(f"Total software items: {count}")
            
            # Sample some items
            if count > 0:
                cursor.execute("SELECT id, name, software_type, price FROM software_items LIMIT 5")
                sample = cursor.fetchall()
                print("Sample items:")
                for item in sample:
                    print(f"  {item[0]} - {item[1]} (Type: {item[2]}, Price: {item[3]})")
        else:
            print("software_items table DOES NOT EXIST")
            
        # Check shop_inventory table
        print("\n=== CHECKING SHOP INVENTORY ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shop_inventory'")
        if cursor.fetchone():
            print("shop_inventory table exists")
            cursor.execute("PRAGMA table_info(shop_inventory)")
            columns = cursor.fetchall()
            print("Columns:", ", ".join([col[1] for col in columns]))
            
            # Count inventory items
            cursor.execute("SELECT COUNT(*) FROM shop_inventory")
            count = cursor.fetchone()[0]
            print(f"Total inventory items: {count}")
            
            # Sample some inventory items
            if count > 0:
                cursor.execute("SELECT shop_id, item_id, item_type, price_modifier FROM shop_inventory LIMIT 5")
                sample = cursor.fetchall()
                print("Sample inventory entries:")
                for item in sample:
                    print(f"  Shop: {item[0]} - Item: {item[1]} (Type: {item[2]}, Price mod: {item[3]})")
        else:
            print("shop_inventory table DOES NOT EXIST")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
