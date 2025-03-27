import sqlite3
import os

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Vérification de la base de données: {db_path}")
print(f"Le fichier existe: {os.path.exists(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nTables dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Vérifier si les nouvelles tables existent
    new_tables = ['hardware_items', 'consumable_items', 'networks', 'hacking_puzzles']
    for table in new_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"\nTable '{table}' trouvée! Examinons sa structure:")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print(f"\nTable '{table}' NON trouvée!")
    
    conn.close()
    print("\nAnalyse terminée!")
    
except Exception as e:
    print(f"Erreur lors de l'analyse de la base de données: {str(e)}")
