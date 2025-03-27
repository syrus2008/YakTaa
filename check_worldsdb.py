import sqlite3
import os

def main():
    db_path = os.path.join("yaktaa_world_editor", "worlds.db")
    print(f"Vérification de la base de données: {db_path}")
    print(f"Existence du fichier: {'Trouvé' if os.path.exists(db_path) else 'Non trouvé'}")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Chercher les boutiques pour Paris
    for table_name in [row[0] for row in tables]:
        if "shop" in table_name.lower():
            print(f"\nExamen de la table {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Colonnes: {', '.join(column_names)}")
            
            # Chercher les boutiques liées à Paris (a4276b20)
            try:
                location_cols = [col for col in column_names if "location" in col.lower() or "city" in col.lower()]
                if location_cols:
                    for loc_col in location_cols:
                        print(f"\nRecherche de boutiques à Paris via colonne {loc_col}:")
                        cursor.execute(f"SELECT * FROM {table_name} WHERE {loc_col} LIKE '%a4276b20%'")
                        shops = cursor.fetchall()
                        print(f"Nombre de boutiques trouvées: {len(shops)}")
                        for shop in shops:
                            print(shop)
                else:
                    print("Aucune colonne de localisation trouvée dans cette table")
            except sqlite3.Error as e:
                print(f"Erreur lors de la recherche: {e}")
    
    # Rechercher aussi les informations sur Paris
    for table_name in [row[0] for row in tables]:
        if "location" in table_name.lower() or "city" in table_name.lower():
            print(f"\nExamen de la table {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Colonnes: {', '.join(column_names)}")
            
            # Chercher Paris
            try:
                cursor.execute(f"SELECT * FROM {table_name} WHERE name LIKE '%Paris%' OR id LIKE '%a4276b20%'")
                locations = cursor.fetchall()
                print(f"Nombre de résultats pour Paris: {len(locations)}")
                for location in locations:
                    print(location)
            except sqlite3.Error as e:
                print(f"Erreur lors de la recherche: {e}")
    
    # Fermeture de la connexion
    conn.close()

if __name__ == "__main__":
    main()
