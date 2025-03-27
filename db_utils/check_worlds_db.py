import sqlite3
import os

def check_database(db_path):
    print(f"Checking database at: {db_path}")
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Liste toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables dans la base de donnu00e9es:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Vu00e9rifie la table des mondes
        print("\nMondes disponibles:")
        try:
            cursor.execute("SELECT id, name FROM worlds;")
            worlds = cursor.fetchall()
            for world in worlds:
                print(f"- ID: {world[0]}, Nom: {world[1]}")
                
                # Obtenir le nombre de magasins pour ce monde
                cursor.execute("SELECT COUNT(*) FROM shops WHERE world_id = ?;", (world[0],))
                shop_count = cursor.fetchone()[0]
                print(f"  Nombre de magasins: {shop_count}")
                
                if shop_count > 0:
                    # Obtenir un exemple de magasin
                    cursor.execute("SELECT id, name, shop_type FROM shops WHERE world_id = ? LIMIT 1;", (world[0],))
                    shop = cursor.fetchone()
                    print(f"  Exemple de magasin: ID: {shop[0]}, Nom: {shop[1]}, Type: {shop[2]}")
                    
                    # Compter les objets dans l'inventaire de ce magasin
                    cursor.execute("SELECT COUNT(*) FROM shop_inventory WHERE shop_id = ?;", (shop[0],))
                    inventory_count = cursor.fetchone()[0]
                    print(f"  Objets dans l'inventaire du magasin: {inventory_count}")
                    
                    if inventory_count > 0:
                        # Vu00e9rifier les types d'objets dans l'inventaire
                        cursor.execute("SELECT item_type, COUNT(*) FROM shop_inventory WHERE shop_id = ? GROUP BY item_type;", (shop[0],))
                        type_distribution = cursor.fetchall()
                        print("  Distribution des types d'objets dans l'inventaire:")
                        for type_info in type_distribution:
                            print(f"   - {type_info[0]}: {type_info[1]} objets")
                        
                        # Prendre un exemple d'objet de l'inventaire
                        cursor.execute("SELECT item_id, item_type FROM shop_inventory WHERE shop_id = ? LIMIT 1;", (shop[0],))
                        inventory_item = cursor.fetchone()
                        item_id, item_type = inventory_item
                        print(f"  Exemple d'objet dans l'inventaire: ID: {item_id}, Type: {item_type}")
                        
                        # Vu00e9rifier si l'objet existe dans sa table correspondante
                        table_name = f"{item_type}_items"
                        try:
                            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?;", (item_id,))
                            item = cursor.fetchone()
                            if item:
                                print(f"  Cet objet existe dans la table {table_name}")
                            else:
                                print(f"  PROBLÈME: Cet objet n'existe PAS dans la table {table_name}")
                        except Exception as e:
                            print(f"  ERREUR lors de la vérification de l'objet dans la table {table_name}: {str(e)}")
                
                # Vérifier les types de tables d'objets disponibles
                item_tables = ['hardware_items', 'software_items', 'consumable_items', 'weapon_items', 'implant_items']
                print("  Vérification des tables d'objets:")
                for table in item_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE world_id = ?;", (world[0],))
                        count = cursor.fetchone()[0]
                        print(f"   - {table}: {count} objets")
                    except Exception as e:
                        print(f"   - {table}: Erreur - {str(e)}")
                        
        except Exception as e:
            print(f"Erreur lors de la vu00e9rification des mondes: {str(e)}")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'accu00e8s u00e0 la base de donnu00e9es: {str(e)}")

# Vu00e9rifier la base de donnu00e9es worlds.db
worlds_db = "c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db"
check_database(worlds_db)
