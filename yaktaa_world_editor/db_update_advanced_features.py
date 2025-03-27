"""
Script de mise à jour de la base de données pour les fonctionnalités avancées de YakTaa
Ce script ajoute les tables pour les implants, vulnérabilités et logiciels
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_database(db_path: str) -> None:
    """
    Met à jour la base de données pour ajouter les tables nécessaires aux fonctionnalités avancées
    
    Args:
        db_path: Chemin vers la base de données à mettre à jour
    """
    conn = None
    try:
        db_path = os.path.abspath(db_path)
        logger.info(f"Mise à jour de la base de données: {db_path}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(db_path):
            logger.error(f"La base de données n'existe pas: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tables pour les implants
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS implants (
            id TEXT PRIMARY KEY,
            world_id TEXT,
            name TEXT,
            description TEXT,
            type TEXT,
            level INTEGER DEFAULT 1,
            price INTEGER DEFAULT 0,
            rarity TEXT DEFAULT 'commun',
            hacking_boost INTEGER DEFAULT 0,
            combat_boost INTEGER DEFAULT 0,
            legality TEXT DEFAULT 'legal',
            manufacturer TEXT,
            bonus TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_implants (
            id TEXT PRIMARY KEY,
            character_id TEXT,
            implant_id TEXT,
            installation_date TEXT,
            is_active INTEGER DEFAULT 1,
            condition INTEGER DEFAULT 100,
            FOREIGN KEY (character_id) REFERENCES characters(id),
            FOREIGN KEY (implant_id) REFERENCES implants(id)
        )
        ''')
        
        # Tables pour les vulnérabilités
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id TEXT PRIMARY KEY,
            world_id TEXT,
            name TEXT,
            description TEXT,
            type TEXT,
            difficulty INTEGER DEFAULT 1,
            target_id TEXT,
            target_type TEXT,
            discovery_date TEXT,
            is_public INTEGER DEFAULT 0,
            is_patched INTEGER DEFAULT 0,
            exploits TEXT,
            code_name TEXT,
            impact INTEGER DEFAULT 1,
            rarity TEXT DEFAULT 'commun',
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        ''')
        
        # Tables pour les logiciels
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS software (
            id TEXT PRIMARY KEY,
            world_id TEXT,
            name TEXT,
            description TEXT,
            type TEXT,
            version TEXT,
            developer TEXT,
            license_type TEXT DEFAULT 'commercial',
            level INTEGER DEFAULT 1,
            price INTEGER DEFAULT 0,
            is_malware INTEGER DEFAULT 0,
            metadata TEXT,
            release_date TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_software (
            id TEXT PRIMARY KEY,
            device_id TEXT,
            software_id TEXT,
            installation_date TEXT,
            is_active INTEGER DEFAULT 1,
            is_running INTEGER DEFAULT 0,
            FOREIGN KEY (device_id) REFERENCES devices(id),
            FOREIGN KEY (software_id) REFERENCES software(id)
        )
        ''')
        
        conn.commit()
        logger.info("Base de données mise à jour avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    """
    Point d'entrée principal du script
    """
    # Chemin par défaut de la base de données
    default_db_path = os.path.join(Path.home(), "yaktaa_worlds.db")
    
    # Utiliser le chemin spécifié en argument ou le chemin par défaut
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = default_db_path
    
    # Mettre à jour la base de données
    update_database(db_path)

if __name__ == "__main__":
    main()
