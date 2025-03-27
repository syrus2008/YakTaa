import sqlite3
import os
import sys

# Chemin vers la base de données
db_path = os.path.join(os.path.dirname(__file__), 'worlds.db')

# Vérifier si le fichier existe
if not os.path.exists(db_path):
    print(f"La base de données n'existe pas à l'emplacement: {db_path}")
    sys.exit(1)

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Afficher les tables disponibles
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables disponibles dans la base de données:")
for table in tables:
    print(f"- {table[0]}")

# Vérifier si les tables shop et shop_inventory existent
shop_table_exists = any(table[0] == 'shops' for table in tables)
shop_inventory_table_exists = any(table[0] == 'shop_inventory' for table in tables)

print(f"\nTable 'shops' existe: {shop_table_exists}")
print(f"Table 'shop_inventory' existe: {shop_inventory_table_exists}")

# Si les tables existent, afficher leur structure
if shop_table_exists:
    cursor.execute("PRAGMA table_info(shops)")
    columns = cursor.fetchall()
    print("\nStructure de la table 'shops':")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Compter le nombre de magasins
    cursor.execute("SELECT COUNT(*) FROM shops")
    shop_count = cursor.fetchone()[0]
    print(f"\nNombre de magasins dans la base de données: {shop_count}")
    
    # Afficher quelques magasins
    cursor.execute("SELECT * FROM shops LIMIT 5")
    shops = cursor.fetchall()
    if shops:
        print("\nExemples de magasins:")
        for shop in shops:
            print(f"- {shop}")

if shop_inventory_table_exists:
    cursor.execute("PRAGMA table_info(shop_inventory)")
    columns = cursor.fetchall()
    print("\nStructure de la table 'shop_inventory':")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Compter le nombre d'articles dans l'inventaire des magasins
    cursor.execute("SELECT COUNT(*) FROM shop_inventory")
    inventory_count = cursor.fetchone()[0]
    print(f"\nNombre d'articles dans l'inventaire des magasins: {inventory_count}")
    
    # Afficher quelques articles d'inventaire
    cursor.execute("SELECT * FROM shop_inventory LIMIT 5")
    inventory_items = cursor.fetchall()
    if inventory_items:
        print("\nExemples d'articles d'inventaire:")
        for item in inventory_items:
            print(f"- {item}")

# Vérifier si la table items existe
items_table_exists = any(table[0] == 'items' for table in tables)
print(f"\nTable 'items' existe: {items_table_exists}")

if items_table_exists:
    cursor.execute("PRAGMA table_info(items)")
    columns = cursor.fetchall()
    print("\nStructure de la table 'items':")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Compter le nombre d'articles
    cursor.execute("SELECT COUNT(*) FROM items")
    items_count = cursor.fetchone()[0]
    print(f"\nNombre d'articles dans la base de données: {items_count}")
    
    # Afficher quelques articles
    cursor.execute("SELECT * FROM items LIMIT 5")
    items = cursor.fetchall()
    if items:
        print("\nExemples d'articles:")
        for item in items:
            print(f"- {item}")

# Fermer la connexion
conn.close()
