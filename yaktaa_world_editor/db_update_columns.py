#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module pour mettre u00e0 jour les colonnes manquantes dans les tables d'objets
"""

import logging
import sqlite3
import os
import sys

logger = logging.getLogger(__name__)

def add_missing_columns(conn):
    """Ajoute les colonnes manquantes aux tables d'objets"""
    
    cursor = conn.cursor()
    
    # Ajout des colonnes manquantes pour hardware_items
    hardware_columns = [
        ("building_id", "TEXT"),
        ("character_id", "TEXT"),
        ("device_id", "TEXT")
    ]
    
    for col_name, col_type in hardware_columns:
        try:
            cursor.execute(f"ALTER TABLE hardware_items ADD COLUMN {col_name} {col_type}")
            logger.info(f"Colonne {col_name} ajoutu00e9e u00e0 la table hardware_items")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info(f"La colonne {col_name} existe du00e9ju00e0 dans hardware_items")
            else:
                logger.error(f"Erreur lors de l'ajout de la colonne {col_name} : {e}")
    
    # Ajout des colonnes manquantes pour consumable_items
    consumable_columns = [
        ("duration", "INTEGER NOT NULL DEFAULT 15"),
        ("building_id", "TEXT"),
        ("character_id", "TEXT"),
        ("device_id", "TEXT")
    ]
    
    for col_name, col_type in consumable_columns:
        try:
            cursor.execute(f"ALTER TABLE consumable_items ADD COLUMN {col_name} {col_type}")
            logger.info(f"Colonne {col_name} ajoutu00e9e u00e0 la table consumable_items")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info(f"La colonne {col_name} existe du00e9ju00e0 dans consumable_items")
            else:
                logger.error(f"Erreur lors de l'ajout de la colonne {col_name} : {e}")
    
    # Ajout des colonnes manquantes pour software_items
    software_columns = [
        ("version", "TEXT NOT NULL DEFAULT '1.0'"),
        ("license_type", "TEXT NOT NULL DEFAULT 'commercial'"),
        ("capabilities", "TEXT"),
        ("device_id", "TEXT"),
        ("file_id", "TEXT")
    ]
    
    for col_name, col_type in software_columns:
        try:
            cursor.execute(f"ALTER TABLE software_items ADD COLUMN {col_name} {col_type}")
            logger.info(f"Colonne {col_name} ajoutu00e9e u00e0 la table software_items")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info(f"La colonne {col_name} existe du00e9ju00e0 dans software_items")
            else:
                logger.error(f"Erreur lors de l'ajout de la colonne {col_name} : {e}")
    
    # Ajout des clu00e9s u00e9trangu00e8res
    try:
        # PRAGMA pour activer les clu00e9s u00e9trangu00e8res
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Nous ne pouvons pas ajouter directement des contraintes de clu00e9 u00e9trangu00e8re via ALTER TABLE en SQLite
        # Pour ajouter des clu00e9s u00e9trangu00e8res, nous devrions recru00e9er la table complu00e8tement
        # Ce code ne fait qu'ajouter les colonnes, pas les contraintes de clu00e9 u00e9trangu00e8re
        
        logger.info("Colonnes ajoutu00e9es avec succu00e8s, mais les contraintes de clu00e9 u00e9trangu00e8re nu00e9cessitent de recru00e9er les tables")
    except Exception as e:
        logger.error(f"Erreur lors de la configuration des clu00e9s u00e9trangu00e8res : {e}")
    
    # Appliquer les changements
    conn.commit()
    logger.info("Mise u00e0 jour des colonnes terminu00e9e")

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Vu00e9rifier si un chemin de base de donnu00e9es est fourni en argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Utiliser un chemin par du00e9faut
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vu00e9rifier si le fichier existe
    if not os.path.exists(db_path):
        logger.error(f"Base de donnu00e9es non trouvu00e9e : {db_path}")
        sys.exit(1)
    
    # Se connecter u00e0 la base de donnu00e9es
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Ajouter les colonnes manquantes
        add_missing_columns(conn)
        
        # Fermer la connexion
        conn.close()
        
        logger.info(f"Colonnes mises u00e0 jour dans : {db_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la mise u00e0 jour des colonnes : {e}")
        sys.exit(1)
