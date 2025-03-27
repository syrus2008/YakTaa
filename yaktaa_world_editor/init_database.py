#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données YakTaa
Vérifie et crée toutes les tables nécessaires pour le fonctionnement de l'éditeur
"""

import sqlite3
import logging
import os
from create_item_tables import create_item_tables

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database(db_path='worlds.db'):
    """
    Initialise la base de données avec toutes les tables nécessaires
    
    Args:
        db_path: Chemin vers la base de données
    """
    logger.info(f"Initialisation de la base de données: {db_path}")
    
    if not os.path.exists(db_path):
        logger.warning(f"La base de données n'existe pas, création d'une nouvelle base: {db_path}")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Vérifier les tables existantes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    logger.info(f"Tables existantes: {existing_tables}")
    
    # Créer les tables de base si elles n'existent pas
    create_core_tables(conn, cursor, existing_tables)
    
    # Fermer la connexion à la base de données
    conn.close()
    
    # Créer les tables d'objets
    create_item_tables(db_path)
    
    logger.info("Initialisation de la base de données terminée")

def create_core_tables(conn, cursor, existing_tables):
    """
    Crée les tables de base nécessaires
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la base de données
        existing_tables: Liste des tables existantes
    """
    # Table worlds
    if 'worlds' not in existing_tables:
        logger.info("Création de la table worlds")
        cursor.execute('''
        CREATE TABLE worlds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            creation_date TEXT,
            is_active INTEGER DEFAULT 0,
            settings TEXT
        )
        ''')
    
    # Table locations
    if 'locations' not in existing_tables:
        logger.info("Création de la table locations")
        cursor.execute('''
        CREATE TABLE locations (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT,
            description TEXT,
            x_coord REAL,
            y_coord REAL,
            population INTEGER DEFAULT 0,
            security_level INTEGER DEFAULT 5,
            is_discoverable INTEGER DEFAULT 1,
            discovery_requirements TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id)
        )
        ''')
    
    # Table buildings
    if 'buildings' not in existing_tables:
        logger.info("Création de la table buildings")
        cursor.execute('''
        CREATE TABLE buildings (
            id TEXT PRIMARY KEY,
            location_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT,
            description TEXT,
            security_level INTEGER DEFAULT 5,
            floors INTEGER DEFAULT 1,
            has_basement INTEGER DEFAULT 0,
            x_coord REAL,
            y_coord REAL,
            icon TEXT,
            metadata TEXT,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
        ''')
    
    # Valider les changements
    conn.commit()

if __name__ == "__main__":
    init_database()
