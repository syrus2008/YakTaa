import sqlite3
import os
import json

def main():
    print(f"Répertoire de travail actuel: {os.getcwd()}")
    print(f"Vérification de l'existence du fichier: {'database.db' if os.path.exists('database.db') else 'database.db non trouvé'}")
    
    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Trouver la table qui pourrait contenir les boutiques
    for table_name in [row[0] for row in tables]:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Cherche des colonnes qui pourraient indiquer que c'est une table de boutiques
        shop_related = any(col for col in column_names if "shop" in col.lower() or "boutique" in col.lower())
        has_name = "name" in column_names
        has_type = "type" in column_names or "shop_type" in column_names
        
        if shop_related or (has_name and has_type):
            print(f"\nTable potentielle de boutiques trouvée: {table_name}")
            print("Colonnes:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Affiche le contenu de la table
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
                rows = cursor.fetchall()
                print(f"\nContenu de la table {table_name} (10 premières lignes):")
                for row in rows:
                    print(row)
            except sqlite3.Error as e:
                print(f"Erreur lors de la récupération des données: {e}")
    
    # Cherchons aussi les villes
    for table_name in [row[0] for row in tables]:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        city_related = any(col for col in column_names if "city" in col.lower() or "ville" in col.lower() or "location" in col.lower())
        
        if city_related:
            print(f"\nTable potentielle de villes/locations trouvée: {table_name}")
            print("Colonnes:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Chercher Paris dans cette table
            try:
                cursor.execute(f"SELECT * FROM {table_name} WHERE name LIKE '%Paris%' OR id LIKE '%a4276b20%' LIMIT 5")
                rows = cursor.fetchall()
                if rows:
                    print(f"\nParis trouvé dans la table {table_name}:")
                    for row in rows:
                        print(row)
            except sqlite3.Error as e:
                print(f"Erreur lors de la recherche de Paris: {e}")
    
    # Fermeture de la connexion
    conn.close()

if __name__ == "__main__":
    main()
