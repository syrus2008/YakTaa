#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger les métadonnées des objets hardware et consumables.
Ce script utilise uniquement les colonnes qui existent réellement dans la base de données.
"""

import json
import logging
import sqlite3
import random
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FixHardwareConsumables")

# Chemin vers la base de données
DB_PATH = Path("worlds.db")

def connect_to_db():
    """Se connecte à la base de données"""
    try:
        logger.info(f"Connexion à la base de données: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        return None, None

def fix_hardware_items(conn, cursor):
    """Corrige les métadonnées des objets hardware"""
    try:
        logger.info("Mise à jour des métadonnées du matériel informatique...")
        
        # Récupérer les colonnes existantes pour le matériel informatique
        cursor.execute("PRAGMA table_info(hardware_items)")
        columns = {row[1] for row in cursor.fetchall()}
        logger.info(f"Colonnes existantes dans hardware_items: {columns}")
        
        # Récupérer tout le matériel informatique avec les colonnes disponibles
        query = "SELECT id, name, hardware_type, metadata"
        if "performance" in columns:
            query += ", performance"
        query += " FROM hardware_items"
        
        cursor.execute(query)
        hardware_items = cursor.fetchall()
        
        updated_count = 0
        for item_data in hardware_items:
            item_id = item_data[0]
            name = item_data[1]
            hardware_type = item_data[2]
            metadata_str = item_data[3]
            performance = item_data[4] if len(item_data) > 4 else random.randint(1, 10)
            
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "hardware_type" not in metadata:
                    metadata["hardware_type"] = hardware_type
                if "performance" not in metadata:
                    metadata["performance"] = performance
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE hardware_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(hardware_items)} matériels informatiques mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du matériel {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du matériel {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(hardware_items)} matériels informatiques mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées du matériel informatique: {e}")
        conn.rollback()
        return 0

def fix_consumable_items(conn, cursor):
    """Corrige les métadonnées des consommables"""
    try:
        logger.info("Mise à jour des métadonnées des consommables...")
        
        # Récupérer les colonnes existantes pour les consommables
        cursor.execute("PRAGMA table_info(consumable_items)")
        columns = {row[1] for row in cursor.fetchall()}
        logger.info(f"Colonnes existantes dans consumable_items: {columns}")
        
        # Récupérer tous les consommables avec les colonnes disponibles
        query = "SELECT id, name, consumable_type, metadata"
        if "effect_type" in columns:
            query += ", effect_type"
        if "effect_power" in columns:
            query += ", effect_power"
        query += " FROM consumable_items"
        
        cursor.execute(query)
        consumable_items = cursor.fetchall()
        
        updated_count = 0
        for item_data in consumable_items:
            item_id = item_data[0]
            name = item_data[1]
            consumable_type = item_data[2]
            metadata_str = item_data[3]
            
            # Valeurs par défaut
            effect_type = "health" 
            effect_power = random.randint(5, 30)
            
            # Déterminer l'effet en fonction du type de consommable
            if "food" in consumable_type.lower() or "drink" in consumable_type.lower():
                effect_type = "nutrition"
            elif "med" in consumable_type.lower() or "health" in consumable_type.lower():
                effect_type = "healing"
            elif "stim" in consumable_type.lower() or "boost" in consumable_type.lower():
                effect_type = "boost"
            elif "antidote" in consumable_type.lower() or "cure" in consumable_type.lower():
                effect_type = "cure"
            
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "effect_type" not in metadata:
                    metadata["effect_type"] = effect_type
                if "effect_power" not in metadata:
                    metadata["effect_power"] = effect_power
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE consumable_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(consumable_items)} consommables mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du consommable {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du consommable {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(consumable_items)} consommables mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des consommables: {e}")
        conn.rollback()
        return 0

def main():
    """Fonction principale pour corriger les métadonnées"""
    logger.info("=== Début de la correction des métadonnées ===")
    
    conn, cursor = connect_to_db()
    if not conn or not cursor:
        logger.error("Impossible de se connecter à la base de données")
        return
    
    try:
        # Corriger les métadonnées du matériel informatique
        fix_hardware_items(conn, cursor)
        
        # Corriger les métadonnées des consommables
        fix_consumable_items(conn, cursor)
        
        logger.info("=== Correction des métadonnées terminée avec succès ===")
    except Exception as e:
        logger.error(f"Erreur lors de la correction des métadonnées: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
