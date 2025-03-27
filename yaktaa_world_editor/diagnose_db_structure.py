#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour analyser la structure détaillée de la base de données YakTaa
"""

import sqlite3
import json
import sys
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DB_Diagnosis')

def analyze_db_structure():
    """Analyse détaillée de la structure de la base de données"""
    
    db_path = 'worlds.db'
    logger.info(f"Analyse de la base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        logger.info(f"Tables trouvées ({len(table_names)}): {', '.join(table_names)}")
        
        # Tables importantes pour les objets
        item_tables = [
            "hardware_items", 
            "consumable_items", 
            "software_items", 
            "weapon_items", 
            "armors",
            "implant_items"
        ]
        
        # Analyser chaque table d'objets
        for table in item_tables:
            if table in table_names:
                logger.info(f"\n=== Analyse de la table: {table} ===")
                
                # Structure de la table
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                logger.info(f"Structure de la table {table}:")
                for col in columns:
                    logger.info(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] else ''}")
                
                # Nombre d'enregistrements
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"Nombre d'enregistrements: {count}")
                
                # Exemple d'enregistrement (premier)
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                    sample = cursor.fetchone()
                    col_names = [desc[0] for desc in cursor.description]
                    
                    logger.info(f"Exemple d'enregistrement:")
                    for i, col in enumerate(col_names):
                        value = sample[i]
                        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                            try:
                                # Essayer de formater comme JSON pour plus de lisibilité
                                value = json.dumps(json.loads(value), indent=2, ensure_ascii=False)
                                logger.info(f"  - {col} (JSON): {value}")
                            except:
                                logger.info(f"  - {col}: {value}")
                        else:
                            logger.info(f"  - {col}: {value}")
                    
                    # Vérifier les valeurs de world_id
                    if 'world_id' in col_names:
                        cursor.execute(f"SELECT DISTINCT world_id FROM {table}")
                        world_ids = cursor.fetchall()
                        logger.info(f"World IDs distincts: {[w[0] for w in world_ids]}")
                
            else:
                logger.warning(f"La table {table} n'existe pas dans la base de données!")
        
        conn.close()
        logger.info("\nAnalyse de la base de données terminée.")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la base de données: {e}", exc_info=True)

if __name__ == "__main__":
    analyze_db_structure()
