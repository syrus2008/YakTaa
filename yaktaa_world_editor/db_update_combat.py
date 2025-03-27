#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de mise à jour du schéma de base de données pour ajouter les attributs de combat
"""

import os
import logging
import sqlite3
from pathlib import Path
import sys

from database import get_database, WorldDatabase

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.DBUpdate")

def update_characters_table(db: WorldDatabase):
    """
    Met à jour la table 'characters' pour ajouter les colonnes nécessaires au combat
    
    Args:
        db: Instance de la base de données
    
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    try:
        cursor = db.conn.cursor()
        
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(characters)")
        columns = {column['name'] for column in cursor.fetchall()}
        
        # Liste des nouvelles colonnes à ajouter
        new_columns = [
            ("enemy_type", "TEXT DEFAULT 'HUMAN'"),
            ("health", "INTEGER DEFAULT 50"),
            ("accuracy", "REAL DEFAULT 0.7"),
            ("initiative", "INTEGER DEFAULT 5"),
            ("damage", "INTEGER DEFAULT 5"),
            ("resistance_physical", "INTEGER DEFAULT 0"),
            ("resistance_energy", "INTEGER DEFAULT 0"),
            ("resistance_emp", "INTEGER DEFAULT 0"),
            ("resistance_biohazard", "INTEGER DEFAULT 0"),
            ("resistance_cyber", "INTEGER DEFAULT 0"),
            ("resistance_viral", "INTEGER DEFAULT 0"),
            ("resistance_nanite", "INTEGER DEFAULT 0"),
            ("hostility", "INTEGER DEFAULT 0"),
            ("ai_behavior", "TEXT DEFAULT 'defensive'"),
            ("combat_style", "TEXT DEFAULT 'balanced'"),
            ("special_abilities", "TEXT")
        ]
        
        # Ajouter chaque colonne si elle n'existe pas déjà
        for column_name, column_def in new_columns:
            if column_name not in columns:
                try:
                    logger.info(f"Ajout de la colonne {column_name} à la table 'characters'")
                    cursor.execute(f"ALTER TABLE characters ADD COLUMN {column_name} {column_def}")
                except sqlite3.Error as e:
                    logger.error(f"Erreur lors de l'ajout de la colonne {column_name}: {e}")
                    return False
        
        # Vérifier si les indices existent déjà
        cursor.execute("PRAGMA index_list(characters)")
        indices = {index['name'] for index in cursor.fetchall()}
        
        # Ajouter des indices pour les nouvelles colonnes critiques
        index_columns = [
            ("idx_characters_enemy_type", "enemy_type"),
            ("idx_characters_is_hostile", "is_hostile")
        ]
        
        for index_name, column in index_columns:
            if index_name not in indices:
                try:
                    logger.info(f"Création de l'index {index_name} sur la colonne {column}")
                    cursor.execute(f"CREATE INDEX {index_name} ON characters({column})")
                except sqlite3.Error as e:
                    logger.error(f"Erreur lors de la création de l'index {index_name}: {e}")
                    # Non critique, continuer
        
        db.conn.commit()
        logger.info("Mise à jour de la table 'characters' terminée avec succès")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {e}")
        db.conn.rollback()
        return False

def update_database_schema():
    """
    Met à jour le schéma de la base de données pour supporter les fonctionnalités de combat
    """
    logger.info("Début de la mise à jour du schéma de base de données pour le combat")
    
    # Chemin explicite vers la base de données de l'application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        logger.error(f"La base de données n'existe pas: {db_path}")
        return False
    
    # Ouvrir la connexion à la base de données
    db = get_database(db_path)
    
    try:
        # Mettre à jour la table des personnages
        if not update_characters_table(db):
            logger.error("Échec de la mise à jour de la table 'characters'")
            return False
        
        logger.info("Mise à jour du schéma terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du schéma: {e}")
        return False
    finally:
        if db.conn:
            db.conn.close()

if __name__ == "__main__":
    success = update_database_schema()
    sys.exit(0 if success else 1)
