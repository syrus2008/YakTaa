import sqlite3
import os

def check_database(db_path):
    """Examine la structure d'une base de données SQLite et affiche les tables et leurs colonnes."""
    print(f"Examen de la base de données: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"La base de données {db_path} n'existe pas.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Nombre de tables trouvées: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Récupérer les informations sur les colonnes
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Colonnes:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
            
            # Compter le nombre d'enregistrements
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Nombre d'enregistrements: {count}")
            
            # Si c'est une table d'items, afficher quelques exemples
            if "item" in table_name.lower():
                print("Exemples d'enregistrements:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                records = cursor.fetchall()
                for record in records:
                    print(f"  - {record}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")

# Vérifier les bases de données
check_database("test_world.db")
print("\n" + "="*50 + "\n")
check_database("yaktaa_world_editor/worlds.db")
