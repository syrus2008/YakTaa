import sqlite3
import json
from datetime import datetime, timedelta
import os

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Mise à jour de la base de données: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer la table des réseaux
    print("Création de la table 'networks'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS networks (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        building_id TEXT NOT NULL,
        name TEXT NOT NULL,
        ssid TEXT,
        network_type TEXT NOT NULL,
        security_level TEXT,
        encryption_type TEXT,
        signal_strength INTEGER,
        is_hidden INTEGER DEFAULT 0,
        password TEXT,
        description TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE
    )
    ''')
    
    # Créer la table des puzzles de hacking
    print("Création de la table 'hacking_puzzles'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hacking_puzzles (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        puzzle_type TEXT NOT NULL,
        difficulty INTEGER NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    # Créer la table des objets hardware
    print("Création de la table 'hardware_items'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hardware_items (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        hardware_type TEXT NOT NULL,
        quality TEXT NOT NULL,
        rarity TEXT NOT NULL,
        level INTEGER NOT NULL,
        stats TEXT,
        location_type TEXT NOT NULL,
        location_id TEXT NOT NULL,
        price INTEGER DEFAULT 0,
        is_installed INTEGER DEFAULT 0,
        is_available INTEGER DEFAULT 1,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    # Créer la table des objets consommables
    print("Création de la table 'consumable_items'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumable_items (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        item_type TEXT NOT NULL,
        rarity TEXT NOT NULL,
        uses INTEGER DEFAULT 1,
        effects TEXT,
        location_type TEXT NOT NULL,
        location_id TEXT NOT NULL,
        price INTEGER DEFAULT 0,
        is_available INTEGER DEFAULT 1,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    print("Base de données mise à jour avec succès!")
    
    # Vérifier que les tables ont bien été créées
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nTables dans la base de données après mise à jour:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"Erreur lors de la mise à jour de la base de données: {str(e)}")
