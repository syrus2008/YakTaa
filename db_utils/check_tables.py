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
        print("\nTables dans la base de données:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Vérifie la table shop_inventory
        print("\nVérification de shop_inventory:")
        cursor.execute("SELECT COUNT(*) FROM shop_inventory;")
        count = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements dans shop_inventory: {count}")
        
        if count > 0:
            # Montre les premiers enregistrements
            cursor.execute("SELECT * FROM shop_inventory LIMIT 5;")
            records = cursor.fetchall()
            print("\nExemples d'enregistrements:")
            # Obtenir les noms des colonnes
            column_names = [description[0] for description in cursor.description]
            print(column_names)
            for record in records:
                print(record)
            
            # Vérifier la distribution des types d'objets
            cursor.execute("SELECT item_type, COUNT(*) FROM shop_inventory GROUP BY item_type;")
            type_distribution = cursor.fetchall()
            print("\nDistribution des types d'objets:")
            for type_info in type_distribution:
                print(f"- {type_info[0]}: {type_info[1]} objets")
        
        # Vérifier les tables d'objets spécifiques
        item_tables = ['hardware_items', 'software_items', 'consumable_items', 'weapon_items', 'implant_items']
        print("\nVérification des tables d'objets:")
        for table in item_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"- {table}: {count} objets")
                
                if count > 0:
                    cursor.execute(f"SELECT id FROM {table} LIMIT 1;")
                    item_id = cursor.fetchone()[0]
                    print(f"  Exemple d'ID: {item_id}")
                    
                    # Vérifier si cet objet est dans un inventaire de boutique
                    cursor.execute(f"SELECT COUNT(*) FROM shop_inventory WHERE item_id = ?;", (item_id,))
                    inventory_count = cursor.fetchone()[0]
                    print(f"  Dans {inventory_count} inventaires de boutique")
            except Exception as e:
                print(f"- {table}: Erreur - {str(e)}")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'accès à la base de données: {str(e)}")

# Vérifier la base de données de l'éditeur de monde
world_editor_db = "c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_data\\world.db"
check_database(world_editor_db)

# Vérifier si une autre base existe
yaktaa_world_editor_db = "c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\data\\world.db"
check_database(yaktaa_world_editor_db)
