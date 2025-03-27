import sqlite3
import os

def check_database_structure(db_path):
    """Vérifie la structure de la base de données et affiche les tables et leurs colonnes"""
    if not os.path.exists(db_path):
        print(f"La base de données {db_path} n'existe pas.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer la liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"Base de données: {db_path}")
    print(f"Nombre de tables: {len(tables)}")
    print("\n=== STRUCTURE DE LA BASE DE DONNÉES ===")
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Récupérer les informations sur les colonnes
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("Colonnes:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            pk_str = "PRIMARY KEY" if is_pk else ""
            null_str = "NOT NULL" if not_null else ""
            default_str = f"DEFAULT {default_val}" if default_val is not None else ""
            print(f"  - {col_name} ({col_type}) {pk_str} {null_str} {default_str}".strip())
        
        # Vérifier s'il y a des données dans la table
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements: {count}")
    
    conn.close()

if __name__ == "__main__":
    db_path = "worlds.db"
    check_database_structure(db_path)
