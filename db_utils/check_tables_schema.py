import sqlite3

# Chemin vers la base de données
DB_PATH = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

def check_table_schema(table_name):
    """Vérifie le schéma d'une table spécifique"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Schéma de la table {table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_value, pk = col
        constraints = []
        if pk:
            constraints.append("PRIMARY KEY")
        if not_null:
            constraints.append("NOT NULL")
        if default_value is not None:
            constraints.append(f"DEFAULT {default_value}")
            
        constraints_str = ", ".join(constraints)
        print(f"   - {col_name} ({col_type}) {constraints_str}")
    
    conn.close()

# Vérifier les tables qui posent problème
print("Vérification des schémas des tables qui posent problème...")
check_table_schema("consumable_items")
print("\n")
check_table_schema("hardware_items")
