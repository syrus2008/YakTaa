import sqlite3
import os
import sys

# Chemin vers la base de donnu00e9es
db_path = os.path.join(os.path.dirname(__file__), 'worlds.db')

# Vu00e9rifier si le fichier existe
if not os.path.exists(db_path):
    print(f"La base de donnu00e9es n'existe pas u00e0 l'emplacement: {db_path}")
    sys.exit(1)

# Connexion u00e0 la base de donnu00e9es
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fonction pour afficher la structure d'une table
def show_table_structure(table_name):
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\nStructure de la table '{table_name}':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # Afficher quelques donnu00e9es d'exemple
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"\nExemple de donnu00e9es dans '{table_name}':")
            column_names = [description[0] for description in cursor.description]
            for i, value in enumerate(row):
                print(f"- {column_names[i]}: {value}")
    except sqlite3.OperationalError as e:
        print(f"Erreur lors de l'accu00e8s u00e0 la table {table_name}: {e}")

# Ru00e9cupu00e9rer toutes les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables disponibles dans la base de donnu00e9es:")
for table in tables:
    print(f"- {table[0]}")

# Afficher la structure des tables qui nous intu00e9ressent
tables_of_interest = [
    'hardware_items', 
    'software_items', 
    'consumable_items', 
    'implant_items', 
    'weapon_items',
    'armors',
    'shops',
    'shop_inventory',
    'software'
]

for table in tables_of_interest:
    show_table_structure(table)

# Fermer la connexion
conn.close()
