#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier la structure des tables d'objets dans la base de données
"""

import sqlite3
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_table_structure(db_path):
    """
    Vérifie la structure des tables d'objets existantes dans la base de données
    
    Args:
        db_path: Chemin vers la base de données
    """
    if not os.path.exists(db_path):
        logger.error(f"Base de données non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables à vérifier
    tables = [
        "weapon_items", 
        "hardware_items", 
        "software_items",
        "consumable_items", 
        "clothing_items", 
        "implant_items"
    ]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        if columns:
            logger.info(f"Structure de la table {table}:")
            for col in columns:
                logger.info(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
            
            # Compter les enregistrements dans cette table
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"  Nombre d'enregistrements: {count}")
            
            # Si la table est vide, vérifier si elle est référencée dans shop_inventory
            if count == 0:
                item_type = table.split('_')[0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM shop_inventory 
                    WHERE item_id LIKE '{item_type}_%'
                """)
                shop_count = cursor.fetchone()[0]
                logger.info(f"  Articles de type {item_type} dans shop_inventory: {shop_count}")
        else:
            logger.info(f"La table {table} existe mais n'a pas de colonnes ou n'existe pas")
    
    conn.close()

if __name__ == "__main__":
    db_path = "worlds.db"
    check_table_structure(db_path)
