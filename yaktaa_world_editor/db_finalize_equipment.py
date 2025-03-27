#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour finaliser la structure de la base de données pour le combat
"""

import os
import logging
import sqlite3
from database import get_database, WorldDatabase

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.DBFinalize")

def update_equipment_columns():
    """
    Met à jour les colonnes des tables d'équipement pour correspondre à la structure attendue
    
    Returns:
        bool: True si la mise à jour est réussie, False sinon
    """
    # Chemin explicite vers la base de données de l'application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        logger.error(f"La base de données n'existe pas: {db_path}")
        return False
    
    # Ouvrir la connexion à la base de données
    db = get_database(db_path)
    
    try:
        cursor = db.conn.cursor()
        
        # 1. Ajouter les colonnes manquantes à la table 'equipment'
        logger.info("Mise à jour de la table 'equipment'")
        
        # Colonnes à ajouter
        equipment_columns = [
            ("type", "TEXT", "equipment_type"),  # Renommage
            ("base_damage", "INTEGER DEFAULT 0", "damage"),  # Renommage
            ("base_armor", "INTEGER DEFAULT 0", "defense"),  # Renommage
            ("slot", "TEXT", None),  # Nouvelle colonne
            ("level_required", "INTEGER DEFAULT 1", "level_requirement"),  # Renommage
            ("weight", "REAL DEFAULT 1.0", None),  # Nouvelle colonne
            ("durability", "INTEGER DEFAULT 100", "condition"),  # Renommage
            ("tags", "TEXT", None)  # Nouvelle colonne
        ]
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(equipment)")
        existing_equipment_columns = {col[1] for col in cursor.fetchall()}
        
        # Créer les nouvelles colonnes
        for col_name, col_type, rename_from in equipment_columns:
            if col_name not in existing_equipment_columns:
                if rename_from and rename_from in existing_equipment_columns:
                    logger.info(f"Création d'une vue temporaire pour renommer {rename_from} en {col_name}")
                    # SQLite ne permet pas de renommer les colonnes directement, nous devons recréer la table
                    # Pour simplifier, nous ajoutons simplement les colonnes manquantes
                    cursor.execute(f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}")
                    cursor.execute(f"UPDATE equipment SET {col_name} = {rename_from}")
                else:
                    logger.info(f"Ajout de la colonne {col_name} à la table 'equipment'")
                    cursor.execute(f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}")
        
        # 2. Ajouter les colonnes manquantes à la table 'character_equipment'
        logger.info("Mise à jour de la table 'character_equipment'")
        
        # Colonnes à ajouter
        char_equipment_columns = [
            ("durability_current", "INTEGER DEFAULT 100", "condition"),  # Renommage
            ("custom_properties", "TEXT", "custom_stats")  # Renommage
        ]
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(character_equipment)")
        existing_char_equipment_columns = {col[1] for col in cursor.fetchall()}
        
        # Créer les nouvelles colonnes
        for col_name, col_type, rename_from in char_equipment_columns:
            if col_name not in existing_char_equipment_columns:
                if rename_from and rename_from in existing_char_equipment_columns:
                    logger.info(f"Création d'une vue temporaire pour renommer {rename_from} en {col_name}")
                    cursor.execute(f"ALTER TABLE character_equipment ADD COLUMN {col_name} {col_type}")
                    cursor.execute(f"UPDATE character_equipment SET {col_name} = {rename_from}")
                else:
                    logger.info(f"Ajout de la colonne {col_name} à la table 'character_equipment'")
                    cursor.execute(f"ALTER TABLE character_equipment ADD COLUMN {col_name} {col_type}")
        
        # 3. Ajouter les colonnes manquantes à la table 'equipment_mods'
        logger.info("Mise à jour de la table 'equipment_mods'")
        
        # Colonnes à ajouter
        equipment_mods_columns = [
            ("type", "TEXT", "mod_type"),  # Renommage
            ("effect_type", "TEXT", "special_effect"),  # Renommage
            ("effect_value", "INTEGER DEFAULT 0", None),  # Nouvelle colonne
            ("level_required", "INTEGER DEFAULT 1", "level_requirement")  # Renommage
        ]
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(equipment_mods)")
        existing_equipment_mods_columns = {col[1] for col in cursor.fetchall()}
        
        # Créer les nouvelles colonnes
        for col_name, col_type, rename_from in equipment_mods_columns:
            if col_name not in existing_equipment_mods_columns:
                if rename_from and rename_from in existing_equipment_mods_columns:
                    logger.info(f"Création d'une vue temporaire pour renommer {rename_from} en {col_name}")
                    cursor.execute(f"ALTER TABLE equipment_mods ADD COLUMN {col_name} {col_type}")
                    cursor.execute(f"UPDATE equipment_mods SET {col_name} = {rename_from}")
                else:
                    logger.info(f"Ajout de la colonne {col_name} à la table 'equipment_mods'")
                    cursor.execute(f"ALTER TABLE equipment_mods ADD COLUMN {col_name} {col_type}")
        
        # 4. Ajouter les colonnes manquantes à la table 'equipment_installed_mods'
        logger.info("Mise à jour de la table 'equipment_installed_mods'")
        
        # Colonnes à ajouter
        installed_mods_columns = [
            ("equipment_mod_id", "TEXT", "mod_id"),  # Renommage
            ("installation_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "created_at")  # Renommage
        ]
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(equipment_installed_mods)")
        existing_installed_mods_columns = {col[1] for col in cursor.fetchall()}
        
        # Créer les nouvelles colonnes
        for col_name, col_type, rename_from in installed_mods_columns:
            if col_name not in existing_installed_mods_columns:
                if rename_from and rename_from in existing_installed_mods_columns:
                    logger.info(f"Création d'une vue temporaire pour renommer {rename_from} en {col_name}")
                    cursor.execute(f"ALTER TABLE equipment_installed_mods ADD COLUMN {col_name} {col_type}")
                    cursor.execute(f"UPDATE equipment_installed_mods SET {col_name} = {rename_from}")
                else:
                    logger.info(f"Ajout de la colonne {col_name} à la table 'equipment_installed_mods'")
                    cursor.execute(f"ALTER TABLE equipment_installed_mods ADD COLUMN {col_name} {col_type}")
        
        # Enregistrer les modifications
        db.conn.commit()
        logger.info("Mise à jour finale des tables d'équipement terminée avec succès")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la finalisation des tables d'équipement: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False
    finally:
        if db and db.conn:
            db.conn.close()

def main():
    """
    Fonction principale
    """
    logger.info("Début de la finalisation de la base de données pour le combat")
    
    # Mettre à jour les colonnes d'équipement
    if update_equipment_columns():
        logger.info("✓ Finalisation de la base de données terminée avec succès")
        return True
    else:
        logger.error("✗ Échec de la finalisation de la base de données")
        return False

if __name__ == "__main__":
    main()
