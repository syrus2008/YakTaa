import sqlite3
import os
from pathlib import Path

def main():
    db_path = Path("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")
    print(f"Vérification des boutiques de Paris dans {db_path}")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Afficher toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Trouver Paris
    cursor.execute("SELECT * FROM locations WHERE name LIKE '%Paris%'")
    paris = cursor.fetchone()
    if paris:
        paris_id = paris[0]
        print(f"Paris trouvé avec ID: {paris_id}")
        
        # Vérifier la structure de la table shops
        cursor.execute("PRAGMA table_info(shops)")
        columns = cursor.fetchall()
        print("Structure de la table shops:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Rechercher les boutiques à Paris directement par ID
        cursor.execute("SELECT * FROM shops WHERE location_id = ?", (paris_id,))
        shops = cursor.fetchall()
        print(f"Nombre de boutiques à Paris (recherche directe): {len(shops)}")
        
        # Rechercher les boutiques à Paris par nom
        cursor.execute("SELECT * FROM shops WHERE location_id IN (SELECT id FROM locations WHERE name LIKE '%Paris%')")
        shops_by_name = cursor.fetchall()
        print(f"Nombre de boutiques à Paris (recherche par nom): {len(shops_by_name)}")
        
        # Lister toutes les boutiques pour comprendre
        cursor.execute("SELECT id, name, location_id FROM shops")
        all_shops = cursor.fetchall()
        print(f"Nombre total de boutiques dans la base: {len(all_shops)}")
        print("Liste de toutes les boutiques:")
        for shop in all_shops:
            shop_id, shop_name, shop_location = shop
            cursor.execute("SELECT name FROM locations WHERE id = ?", (shop_location,))
            location_name = cursor.fetchone()
            print(f"- {shop_id}: {shop_name} (Location ID: {shop_location}, Nom: {location_name[0] if location_name else 'Inconnu'})")
        
        # Tester une requête plus large
        print("\nRecherche avancée de boutiques pour Paris:")
        query = """
        SELECT s.id, s.name, s.location_id, l.name 
        FROM shops s
        LEFT JOIN locations l ON s.location_id = l.id
        WHERE l.name LIKE '%Paris%' OR s.location_id = ?
        """
        cursor.execute(query, (paris_id,))
        advanced_shops = cursor.fetchall()
        print(f"Nombre de boutiques trouvées (jointure): {len(advanced_shops)}")
        for shop in advanced_shops:
            print(f"- {shop[0]}: {shop[1]} (Location ID: {shop[2]}, Nom: {shop[3]})")
        
    else:
        print("Paris non trouvé dans la base de données")
        # Chercher toutes les locations pour voir ce qui est disponible
        cursor.execute("SELECT id, name FROM locations")
        locations = cursor.fetchall()
        print("Locations disponibles:")
        for location in locations:
            print(f"- {location[0]}: {location[1]}")
    
    # Fermeture de la connexion
    conn.close()

if __name__ == "__main__":
    main()
