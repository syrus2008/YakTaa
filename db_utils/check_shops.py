import sqlite3
import os

# Chemin vers la base de donnu00e9es
db_path = os.path.join('yaktaa_world_editor', 'worlds.db')

# Vu00e9rifier si le fichier existe
if not os.path.exists(db_path):
    print(f"La base de donnu00e9es {db_path} n'existe pas.")
    exit(1)

# Connexion u00e0 la base de donnu00e9es
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vu00e9rifier si la table shops existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops';")
if not cursor.fetchone():
    print("La table shops n'existe pas dans cette base de donnu00e9es.")
    exit(1)

# Compter le nombre de magasins
cursor.execute("SELECT COUNT(*) FROM shops")
count = cursor.fetchone()[0]
print(f"Nombre total de magasins dans la base de donnu00e9es: {count}")

# Lister les magasins par monde
cursor.execute("SELECT DISTINCT world_id FROM shops")
worlds = cursor.fetchall()

for world in worlds:
    world_id = world[0]
    cursor.execute("SELECT COUNT(*) FROM shops WHERE world_id = ?", (world_id,))
    world_count = cursor.fetchone()[0]
    print(f"Monde '{world_id}': {world_count} magasins")

# Afficher les du00e9tails des magasins
print("\nDu00e9tails des magasins:")
cursor.execute("SELECT id, world_id, name, shop_type, location_id FROM shops LIMIT 20")
shops = cursor.fetchall()

if not shops:
    print("Aucun magasin trouvu00e9 dans la base de donnu00e9es.")
else:
    for shop in shops:
        shop_id, world_id, name, shop_type, location_id = shop
        print(f"ID: {shop_id}, Monde: {world_id}, Nom: {name}, Type: {shop_type}, Lieu: {location_id}")

# Vu00e9rifier les inventaires des magasins
print("\nInventaires des magasins:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shop_inventory';")
if not cursor.fetchone():
    print("La table shop_inventory n'existe pas dans cette base de donnu00e9es.")
else:
    cursor.execute("SELECT COUNT(*) FROM shop_inventory")
    inv_count = cursor.fetchone()[0]
    print(f"Nombre total d'articles dans les inventaires: {inv_count}")
    
    # Afficher quelques articles d'inventaire
    if inv_count > 0:
        cursor.execute("""SELECT s.name, si.item_id, si.item_type, si.quantity 
                        FROM shop_inventory si 
                        JOIN shops s ON si.shop_id = s.id 
                        LIMIT 10""")
        inventory_items = cursor.fetchall()
        for item in inventory_items:
            shop_name, item_id, item_type, quantity = item
            print(f"Magasin: {shop_name}, Article: {item_id}, Type: {item_type}, Quantitu00e9: {quantity}")

# Fermer la connexion
conn.close()
