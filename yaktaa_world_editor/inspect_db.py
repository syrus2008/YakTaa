import sqlite3
import json

# Connexion à la base de données
conn = sqlite3.connect('worlds.db')
conn.row_factory = sqlite3.Row

# Obtenir la structure de la table buildings
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(buildings)")
columns = cursor.fetchall()

print("Structure de la table buildings:")
for col in columns:
    print(f"- {col['name']} ({col['type']})")

# Vérifier si la table contient des données
cursor.execute("SELECT COUNT(*) FROM buildings")
count = cursor.fetchone()[0]
print(f"\nNombre d'enregistrements dans la table buildings: {count}")

if count > 0:
    # Afficher quelques enregistrements pour comprendre la structure
    cursor.execute("SELECT * FROM buildings LIMIT 3")
    buildings = cursor.fetchall()
    
    print("\nExemples d'enregistrements:")
    for building in buildings:
        print(json.dumps({key: building[key] for key in building.keys()}, indent=2))

# Fermer la connexion
conn.close()
