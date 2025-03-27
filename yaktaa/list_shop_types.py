import sqlite3
import os

# Chemin de la base de données
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                      "yaktaa_world_editor", "worlds.db")

print(f"Connexion à la base de données: {db_path}")
print(f"Le fichier existe: {os.path.exists(db_path)}")

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier la structure de la table shops
cursor.execute("PRAGMA table_info(shops)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Colonnes de la table shops: {columns}")

# Déterminer le nom de la colonne pour le type de boutique
type_column = "shop_type" if "shop_type" in columns else "type"

# Récupérer tous les types de boutiques
cursor.execute(f"SELECT DISTINCT {type_column} FROM shops")
shop_types = cursor.fetchall()

print("\n=== Types de boutiques dans la base de données ===")
for shop_type in shop_types:
    print(f"- {shop_type[0]}")

# Chemin de base des icônes
icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets", "icons", "shop_type")
os.makedirs(icon_path, exist_ok=True)

print(f"\nVous devez créer les icônes suivantes dans le dossier: {icon_path}")
print("Fichiers d'icônes nécessaires:")
for shop_type in shop_types:
    type_name = shop_type[0].lower()
    print(f"- {type_name}.png")
print("- default.png (icône par défaut pour les types manquants)")

# Fermer la connexion
conn.close()
