import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.join('yaktaa_world_editor', 'worlds.db')

# Vérifier si le fichier existe
if not os.path.exists(db_path):
    print(f"La base de données {db_path} n'existe pas.")
    exit(1)

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtenir la liste des tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables dans la base de données:")
for table in tables:
    print(f"- {table[0]}")

# Vérifier si la table shops existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops';")
if cursor.fetchone():
    print("\nStructure de la table shops:")
    cursor.execute("PRAGMA table_info(shops)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
else:
    print("\nLa table shops n'existe pas dans cette base de données.")

# Fermer la connexion
conn.close()
