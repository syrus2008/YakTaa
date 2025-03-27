import sqlite3
import os

def main():
    db_path = os.path.join("yaktaa_world_editor", "worlds.db")
    print(f"Vérification des boutiques de Moscou dans {db_path}")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Trouver Moscou
    cursor.execute("SELECT * FROM locations WHERE name LIKE '%Moscow%'")
    moscow = cursor.fetchone()
    if moscow:
        moscow_id = moscow[0]
        print(f"Moscou trouvé avec ID: {moscow_id}")
        
        # Rechercher les boutiques à Moscou
        cursor.execute("SELECT * FROM shops WHERE location_id = ?", (moscow_id,))
        shops = cursor.fetchall()
        print(f"Nombre de boutiques à Moscou: {len(shops)}")
        for shop in shops:
            print(f"- ID: {shop[0]}, Nom: {shop[2]}, Type: {shop[7]}")
            
            # Vérifier l'inventaire de cette boutique
            cursor.execute("SELECT * FROM shop_inventory WHERE shop_id = ? LIMIT 5", (shop[0],))
            inventory = cursor.fetchall()
            print(f"  Inventaire: {len(inventory)} articles")
            for item in inventory[:5]:  # Afficher 5 premiers articles
                print(f"  - Type: {item[2]}, ID: {item[3]}, Quantité: {item[4]}, Prix: {item[5]}")
    else:
        print("Moscou non trouvé dans la base de données")
    
    # Fermeture de la connexion
    conn.close()

if __name__ == "__main__":
    main()
