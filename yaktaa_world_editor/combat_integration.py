#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'intégration du système de combat dans l'éditeur de monde YakTaa
Ce script vérifie et met à jour la base de données, puis teste les fonctionnalités de combat
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path
import argparse

from database import get_database, WorldDatabase
from db_update_combat import update_database_schema

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.CombatIntegration")

def test_combat_system(db_path=None):
    """
    Teste les fonctionnalités du système de combat avec la base de données
    
    Args:
        db_path: Chemin de la base de données (optionnel)
    """
    db = get_database(db_path)
    
    try:
        # 1. Vérifie si la table characters a bien les colonnes de combat
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(characters)")
        columns = {column['name'] for column in cursor.fetchall()}
        
        combat_columns = {
            "enemy_type", "health", "damage", "accuracy", "initiative", "hostility",
            "resistance_physical", "resistance_energy", "resistance_emp", 
            "resistance_biohazard", "resistance_cyber", "resistance_viral", 
            "resistance_nanite", "ai_behavior", "combat_style", "special_abilities"
        }
        
        missing_columns = combat_columns - columns
        if missing_columns:
            logger.error(f"Il manque des colonnes de combat dans la table 'characters': {missing_columns}")
            logger.info("Exécutez d'abord le script db_update_combat.py pour mettre à jour le schéma de la base de données")
            return False
        
        # 2. Récupère un monde actif
        cursor.execute("SELECT id, name FROM worlds WHERE is_active = 1 LIMIT 1")
        active_world = cursor.fetchone()
        
        if not active_world:
            cursor.execute("SELECT id, name FROM worlds LIMIT 1")
            world = cursor.fetchone()
            if not world:
                logger.error("Aucun monde trouvé dans la base de données")
                return False
            
            world_id = world["id"]
            logger.info(f"Aucun monde actif trouvé, utilisation du monde: {world['name']} ({world_id})")
        else:
            world_id = active_world["id"]
            logger.info(f"Monde actif: {active_world['name']} ({world_id})")
        
        # 3. Récupère les personnages avec leurs attributs de combat
        cursor.execute("""
        SELECT id, name, location_id, enemy_type, health, damage, accuracy, 
               initiative, hostility, is_hostile, combat_level
        FROM characters
        WHERE world_id = ?
        LIMIT 10
        """, (world_id,))
        
        characters = cursor.fetchall()
        
        if not characters:
            logger.warning(f"Aucun personnage trouvé pour le monde {world_id}")
            logger.info("Vous pouvez générer des personnages avec le script characters_generator.py")
            return False
        
        # 4. Affiche les statistiques de combat des personnages
        logger.info(f"Statistiques de combat pour {len(characters)} personnages:")
        
        for char in characters:
            logger.info(f"- {char['name']} (ID: {char['id']})")
            logger.info(f"  Type: {char['enemy_type']}, Santé: {char['health']}, Dégâts: {char['damage']}")
            logger.info(f"  Précision: {char['accuracy']:.2f}, Initiative: {char['initiative']}")
            logger.info(f"  Niveau de combat: {char['combat_level']}, Hostilité: {char['hostility']}%")
            logger.info(f"  Est hostile: {'Oui' if char['is_hostile'] else 'Non'}")
            logger.info("  ---")
        
        # 5. Récupère les lieux pour ces personnages
        location_ids = {char["location_id"] for char in characters if char["location_id"]}
        
        if location_ids:
            placeholders = ",".join(["?" for _ in location_ids])
            cursor.execute(f"""
            SELECT id, name, security_level
            FROM locations
            WHERE id IN ({placeholders})
            """, tuple(location_ids))
            
            locations = cursor.fetchall()
            
            logger.info(f"Lieux associés ({len(locations)}):")
            for loc in locations:
                logger.info(f"- {loc['name']} (ID: {loc['id']}), Niveau de sécurité: {loc['security_level']}")
        
        logger.info("Test du système de combat terminé avec succès")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Erreur SQLite lors du test: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors du test: {e}")
        return False
    finally:
        db.conn.close()

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Intégration du système de combat dans l'éditeur de monde YakTaa")
    parser.add_argument("--db-path", help="Chemin vers la base de données")
    parser.add_argument("--update-schema", action="store_true", help="Met à jour le schéma de la base de données")
    parser.add_argument("--test", action="store_true", help="Teste le système de combat")
    
    args = parser.parse_args()
    
    # Si aucune option n'est spécifiée, afficher l'aide
    if not (args.update_schema or args.test):
        parser.print_help()
        return
    
    # Mise à jour du schéma
    if args.update_schema:
        logger.info("Mise à jour du schéma de la base de données...")
        if update_database_schema():
            logger.info("Schéma mis à jour avec succès")
        else:
            logger.error("Échec de la mise à jour du schéma")
            sys.exit(1)
    
    # Test du système de combat
    if args.test:
        logger.info("Test du système de combat...")
        if test_combat_system(args.db_path):
            logger.info("Test réussi")
        else:
            logger.error("Échec du test")
            sys.exit(1)

if __name__ == "__main__":
    main()
