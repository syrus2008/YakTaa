#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'initialisation des tables pour les magasins et objets dans la base de données
"""

import logging
import sqlite3

logger = logging.getLogger(__name__)

def init_shop_tables(conn):
    """Initialise les tables pour les magasins dans la base de données"""
    
    cursor = conn.cursor()
    
    # Table des magasins
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shops (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        shop_type TEXT NOT NULL,
        is_legal BOOLEAN NOT NULL DEFAULT 1,
        world_id TEXT NOT NULL,
        building_id TEXT,
        location_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
        FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
        FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL
    )
    ''')
    
    # Table des inventaires de magasins
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shop_inventories (
        id TEXT PRIMARY KEY,
        shop_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        item_type TEXT NOT NULL,  -- hardware, consumable, software
        quantity INTEGER NOT NULL DEFAULT 1,
        discount_percent REAL NOT NULL DEFAULT 0,
        is_special BOOLEAN NOT NULL DEFAULT 0,
        world_id TEXT NOT NULL,
        FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE CASCADE,
        FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
    )
    ''')
    
    logger.info("Tables des magasins initialisées")

def init_item_tables(conn):
    """Initialise les tables pour les objets dans la base de données"""
    
    cursor = conn.cursor()
    
    # Table des objets matériels (hardware)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hardware_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        hardware_type TEXT NOT NULL,
        quality TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        price INTEGER NOT NULL DEFAULT 0,
        is_legal BOOLEAN NOT NULL DEFAULT 1,
        stats TEXT,  -- JSON
        world_id TEXT NOT NULL,
        building_id TEXT,
        character_id TEXT,
        device_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
        FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
        FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL,
        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
    )
    ''')
    
    # Table des objets consommables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumable_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        item_type TEXT NOT NULL,
        rarity TEXT NOT NULL,
        duration INTEGER NOT NULL DEFAULT 15,
        price INTEGER NOT NULL DEFAULT 0,
        is_legal BOOLEAN NOT NULL DEFAULT 1,
        effects TEXT,  -- JSON
        world_id TEXT NOT NULL,
        building_id TEXT,
        character_id TEXT,
        device_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
        FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
        FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL,
        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
    )
    ''')
    
    # Table des objets logiciels (software)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS software_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        software_type TEXT NOT NULL,
        version TEXT NOT NULL,
        license_type TEXT NOT NULL,
        price INTEGER NOT NULL DEFAULT 0,
        is_legal BOOLEAN NOT NULL DEFAULT 1,
        capabilities TEXT,  -- JSON
        world_id TEXT NOT NULL,
        device_id TEXT,
        file_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL,
        FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE SET NULL
    )
    ''')
    
    logger.info("Tables des objets initialisées")

def init_all(conn):
    """Initialise toutes les tables pour les magasins et objets"""
    init_shop_tables(conn)
    init_item_tables(conn)
    
    # Commit des changements
    conn.commit()
    
    logger.info("Initialisation des tables pour les magasins et objets terminée")

# Exécution du script directement
if __name__ == "__main__":
    import sys
    import os
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Vérifier si un chemin de base de données est fourni en argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Utiliser un chemin par défaut
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "yaktaa.db")
    
    # Vérifier si le fichier existe
    if not os.path.exists(db_path):
        logger.error(f"Base de données non trouvée : {db_path}")
        sys.exit(1)
    
    # Se connecter à la base de données
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Initialiser les tables
        init_all(conn)
        
        # Fermer la connexion
        conn.close()
        
        logger.info(f"Tables initialisées dans : {db_path}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des tables : {e}")
        sys.exit(1)
