import sqlite3
import json
import sys

def check_items_tables():
    """Vérifie le contenu de toutes les tables d'objets dans la base de données."""
    conn = sqlite3.connect('worlds.db')
    cursor = conn.cursor()
    
    # Liste des tables d'objets à vérifier
    item_tables = [
        "hardware_items", 
        "consumable_items", 
        "software_items", 
        "weapon_items", 
        "armors",
        "implant_items"
    ]
    
    # Récupérer tous les world_id existants
    cursor.execute("SELECT id, name FROM worlds")
    worlds = cursor.fetchall()
    world_ids = [w[0] for w in worlds]
    
    print(f"Mondes dans la base de données:")
    for world in worlds:
        print(f"  - {world[0]} ({world[1]})")
    
    # Vérifier chaque table
    for table_name in item_tables:
        print(f"\n{'='*80}")
        print(f"VÉRIFICATION DE LA TABLE: {table_name}")
        print(f"{'='*80}")
        
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"La table {table_name} n'existe pas dans la base de données!")
            continue
        
        # Obtenir les informations sur les colonnes
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        print(f"Colonnes de la table {table_name}:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Vérifier si world_id existe dans la table
        has_world_id = 'world_id' in col_names
        
        # Compter le nombre d'éléments total
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        print(f"Nombre total d'éléments dans {table_name}: {total_count}")
        
        # Si world_id existe, compter par monde
        if has_world_id:
            for world_id in world_ids:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE world_id = ?", (world_id,))
                world_count = cursor.fetchone()[0]
                print(f"  - Items pour le monde {world_id}: {world_count}")
            
            # Compter les éléments sans world_id
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE world_id IS NULL OR world_id = ''")
            null_count = cursor.fetchone()[0]
            print(f"  - Items sans world_id: {null_count}")
            
            # Vérifier les world_id qui ne correspondent pas à des mondes existants
            cursor.execute(f"SELECT DISTINCT world_id FROM {table_name} WHERE world_id NOT IN ({','.join(['?']*len(world_ids))})", world_ids)
            invalid_worlds = cursor.fetchall()
            if invalid_worlds:
                print(f"  - World IDs invalides dans {table_name}:")
                for iw in invalid_worlds:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE world_id = ?", (iw[0],))
                    count = cursor.fetchone()[0]
                    print(f"    - {iw[0]}: {count} items")
        
        # Afficher les 5 premiers éléments comme exemple
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_items = cursor.fetchall()
        
        if sample_items:
            print(f"\nExemples d'éléments (5 premiers):")
            for idx, item in enumerate(sample_items):
                print(f"  Item {idx+1}:")
                for i, col in enumerate(col_names):
                    value = item[i]
                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                        try:
                            # Essayer de formater comme JSON pour plus de lisibilité
                            value = json.dumps(json.loads(value), indent=2, ensure_ascii=False)
                        except:
                            pass
                    print(f"    - {col}: {value}")
        
    conn.close()
    print("\nAnalyse terminée!")

if __name__ == "__main__":
    check_items_tables()
