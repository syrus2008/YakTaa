#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier si la base de données contient tous les éléments nécessaires
"""

import os
import sqlite3
import logging
from pathlib import Path
import sys

from database import get_database, WorldDatabase

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.DBDiagnostic")

def check_character_combat_columns(db: WorldDatabase):
    """
    Vérifie si la table 'characters' contient toutes les colonnes nécessaires pour le combat
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, list): Succès et liste des colonnes manquantes
    """
    required_columns = [
        "enemy_type",
        "health",
        "accuracy", 
        "initiative",
        "damage",
        "resistance_physical",
        "resistance_energy",
        "resistance_emp",
        "resistance_biohazard", 
        "resistance_cyber",
        "resistance_viral",
        "resistance_nanite",
        "hostility",
        "ai_behavior",
        "combat_style",
        "special_abilities",
        "is_hostile"  # Colonne qui devrait déjà exister dans le schéma de base
    ]
    
    cursor = db.conn.cursor()
    cursor.execute("PRAGMA table_info(characters)")
    existing_columns = {column[1] for column in cursor.fetchall()}
    
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        logger.warning(f"Colonnes manquantes dans la table 'characters': {missing_columns}")
        return False, missing_columns
    else:
        logger.info("Toutes les colonnes nécessaires pour le combat sont présentes dans la table 'characters'")
        return True, []

def check_equipment_tables(db: WorldDatabase):
    """
    Vérifie si les tables nécessaires pour l'équipement sont présentes
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, list): Succès et liste des tables manquantes
    """
    required_tables = [
        "equipment",
        "character_equipment",
        "equipment_mods", 
        "equipment_installed_mods"
    ]
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {table[0] for table in cursor.fetchall()}
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        logger.warning(f"Tables d'équipement manquantes: {missing_tables}")
        return False, missing_tables
    else:
        logger.info("Toutes les tables nécessaires pour l'équipement sont présentes")
        return True, []

def check_equipment_columns(db: WorldDatabase):
    """
    Vérifie si les tables d'équipement contiennent toutes les colonnes nécessaires
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, dict): Succès et dictionnaire des tables avec colonnes manquantes
    """
    required_columns = {
        "equipment": [
            "id", "world_id", "name", "description", "type", "subtype", 
            "rarity", "base_damage", "base_armor", "slot", "price",
            "level_required", "weight", "durability", "is_unique", "tags"
        ],
        "character_equipment": [
            "id", "character_id", "equipment_id", "is_equipped", "durability_current", 
            "custom_name", "custom_properties"
        ],
        "equipment_mods": [
            "id", "world_id", "name", "description", "type", "compatibility",
            "effect_type", "effect_value", "rarity", "price", "level_required"
        ],
        "equipment_installed_mods": [
            "id", "character_equipment_id", "equipment_mod_id", "installation_date"
        ]
    }
    
    cursor = db.conn.cursor()
    missing_by_table = {}
    success = True
    
    for table, columns in required_columns.items():
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = {column[1] for column in cursor.fetchall()}
            
            missing_columns = [col for col in columns if col not in existing_columns]
            
            if missing_columns:
                logger.warning(f"Colonnes manquantes dans la table '{table}': {missing_columns}")
                missing_by_table[table] = missing_columns
                success = False
            else:
                logger.info(f"Toutes les colonnes nécessaires pour la table '{table}' sont présentes")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la vérification des colonnes de la table '{table}': {e}")
            missing_by_table[table] = ["Table non accessible"]
            success = False
    
    return success, missing_by_table

def check_status_effects_tables(db: WorldDatabase):
    """
    Vérifie si les tables nécessaires pour les effets de statut sont présentes
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, list): Succès et liste des tables manquantes
    """
    required_tables = [
        "status_effects",
        "character_status_effects"
    ]
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {table[0] for table in cursor.fetchall()}
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        logger.warning(f"Tables d'effets de statut manquantes: {missing_tables}")
        return False, missing_tables
    else:
        logger.info("Toutes les tables nécessaires pour les effets de statut sont présentes")
        return True, []

def check_status_effects_columns(db: WorldDatabase):
    """
    Vérifie si les tables d'effets de statut contiennent toutes les colonnes nécessaires
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, dict): Succès et dictionnaire des tables avec colonnes manquantes
    """
    required_columns = {
        "status_effects": [
            "id", "world_id", "name", "description", "type", "duration",
            "effect_value", "effect_type", "is_debuff", "visual_effect"
        ],
        "character_status_effects": [
            "id", "character_id", "status_effect_id", "start_time", 
            "duration_remaining", "source_character_id", "source_equipment_id"
        ]
    }
    
    cursor = db.conn.cursor()
    missing_by_table = {}
    success = True
    
    for table, columns in required_columns.items():
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = {column[1] for column in cursor.fetchall()}
            
            missing_columns = [col for col in columns if col not in existing_columns]
            
            if missing_columns:
                logger.warning(f"Colonnes manquantes dans la table '{table}': {missing_columns}")
                missing_by_table[table] = missing_columns
                success = False
            else:
                logger.info(f"Toutes les colonnes nécessaires pour la table '{table}' sont présentes")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la vérification des colonnes de la table '{table}': {e}")
            missing_by_table[table] = ["Table non accessible"]
            success = False
    
    return success, missing_by_table

def check_characters_equipment_slot(db: WorldDatabase):
    """
    Vérifie si la table 'characters' contient la colonne pour les emplacements d'équipement
    
    Args:
        db: Instance de la base de données
    
    Returns:
        Tuple (bool, list): Succès et liste des colonnes manquantes
    """
    required_columns = ["equipment_slots"]
    
    cursor = db.conn.cursor()
    cursor.execute("PRAGMA table_info(characters)")
    existing_columns = {column[1] for column in cursor.fetchall()}
    
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        logger.warning(f"Colonne d'emplacements d'équipement manquante dans la table 'characters': {missing_columns}")
        return False, missing_columns
    else:
        logger.info("La colonne d'emplacements d'équipement est présente dans la table 'characters'")
        return True, []

def run_diagnostic():
    """
    Exécute tous les diagnostics sur la base de données
    
    Returns:
        bool: True si tous les diagnostics passent, False sinon
    """
    logger.info("Démarrage du diagnostic de la base de données...")
    
    # Chemin explicite vers la base de données de l'application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        logger.error(f"La base de données n'existe pas: {db_path}")
        return False
    
    # Ouvrir la connexion à la base de données
    db = get_database(db_path)
    
    try:
        all_checks_passed = True
        
        # 1. Vérifier les colonnes de combat dans la table characters
        combat_check, missing_combat_columns = check_character_combat_columns(db)
        all_checks_passed &= combat_check
        
        # 2. Vérifier la présence des tables d'équipement
        equipment_tables_check, missing_equipment_tables = check_equipment_tables(db)
        all_checks_passed &= equipment_tables_check
        
        # 3. Vérifier les colonnes des tables d'équipement (si elles existent)
        if equipment_tables_check:
            equipment_columns_check, missing_equipment_columns = check_equipment_columns(db)
            all_checks_passed &= equipment_columns_check
        
        # 4. Vérifier la présence des tables d'effets de statut
        status_tables_check, missing_status_tables = check_status_effects_tables(db)
        all_checks_passed &= status_tables_check
        
        # 5. Vérifier les colonnes des tables d'effets de statut (si elles existent)
        if status_tables_check:
            status_columns_check, missing_status_columns = check_status_effects_columns(db)
            all_checks_passed &= status_columns_check
        
        # 6. Vérifier la colonne equipment_slots dans la table characters
        equipment_slot_check, missing_equipment_slot = check_characters_equipment_slot(db)
        all_checks_passed &= equipment_slot_check
        
        # Résumé des résultats
        if all_checks_passed:
            logger.info("✓ Tous les diagnostics ont été passés avec succès!")
            logger.info("La base de données contient tous les éléments nécessaires pour le système de combat")
        else:
            logger.warning("✗ Certains éléments sont manquants dans la base de données:")
            
            if not combat_check:
                logger.warning(f"  - Colonnes de combat manquantes dans la table 'characters': {missing_combat_columns}")
            
            if not equipment_tables_check:
                logger.warning(f"  - Tables d'équipement manquantes: {missing_equipment_tables}")
            
            if equipment_tables_check and 'equipment_columns_check' in locals() and not equipment_columns_check:
                for table, columns in missing_equipment_columns.items():
                    if columns:
                        logger.warning(f"  - Colonnes manquantes dans la table '{table}': {columns}")
            
            if not status_tables_check:
                logger.warning(f"  - Tables d'effets de statut manquantes: {missing_status_tables}")
            
            if status_tables_check and 'status_columns_check' in locals() and not status_columns_check:
                for table, columns in missing_status_columns.items():
                    if columns:
                        logger.warning(f"  - Colonnes manquantes dans la table '{table}': {columns}")
            
            if not equipment_slot_check:
                logger.warning(f"  - Colonne d'emplacements d'équipement manquante: {missing_equipment_slot}")
        
        return all_checks_passed
        
    except Exception as e:
        logger.error(f"Erreur inattendue lors du diagnostic: {e}")
        return False
    finally:
        if db.conn:
            db.conn.close()

if __name__ == "__main__":
    success = run_diagnostic()
    sys.exit(0 if success else 1)
