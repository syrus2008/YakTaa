"""
Module de gestion de la base de données
Fournit des fonctions pour interagir avec la base de données SQLite
"""

import sqlite3
import os
import logging
from typing import Optional

# Configuration du logging
logger = logging.getLogger("YakTaa.Database")

class Database:
    """Classe pour gérer la connexion à la base de données SQLite"""
    
    def __init__(self, db_path: str):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        
    def _connect(self):
        """Établit la connexion à la base de données"""
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Établir la connexion
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Activer les clés étrangères
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Connexion établie à la base de données: {self.db_path}")
            
            # Initialiser la base de données si elle n'existe pas
            self._initialize_db()
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {e}")
            raise
    
    def _initialize_db(self):
        """Initialise la structure de la base de données si elle n'existe pas"""
        cursor = self.conn.cursor()
        
        # Table des mondes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS worlds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            author TEXT,
            version TEXT,
            is_active INTEGER DEFAULT 0,
            metadata TEXT,
            complexity INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des lieux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            coordinates TEXT,
            security_level INTEGER,
            population INTEGER,
            services TEXT,
            tags TEXT,
            parent_location_id TEXT,
            is_virtual INTEGER DEFAULT 0,
            is_special INTEGER DEFAULT 0,
            is_dangerous INTEGER DEFAULT 0,
            location_type TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_location_id) REFERENCES locations (id) ON DELETE SET NULL
        )
        ''')
        
        # Table des connexions entre lieux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            destination_id TEXT NOT NULL,
            travel_type TEXT,
            travel_time REAL,
            travel_cost INTEGER,
            requires_hacking INTEGER DEFAULT 0,
            requires_special_access INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (source_id) REFERENCES locations (id) ON DELETE CASCADE,
            FOREIGN KEY (destination_id) REFERENCES locations (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des bâtiments
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            building_type TEXT,
            floors INTEGER,
            security_level INTEGER,
            owner TEXT,
            services TEXT,
            is_accessible INTEGER DEFAULT 1,
            requires_special_access INTEGER DEFAULT 0,
            requires_hacking INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des pièces
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            building_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            floor INTEGER,
            room_type TEXT,
            is_accessible INTEGER DEFAULT 1,
            requires_hacking INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des personnages
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            location_id TEXT,
            profession TEXT,
            faction TEXT,
            gender TEXT,
            importance INTEGER,
            hacking_level INTEGER,
            combat_level INTEGER,
            charisma INTEGER,
            wealth INTEGER,
            is_hostile INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL
        )
        ''')
        
        # Table des appareils
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            location_id TEXT,
            owner_id TEXT,
            device_type TEXT,
            os_type TEXT,
            security_level INTEGER,
            is_connected INTEGER DEFAULT 1,
            ip_address TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL,
            FOREIGN KEY (owner_id) REFERENCES characters (id) ON DELETE SET NULL
        )
        ''')
        
        # Table des réseaux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            building_id TEXT,
            name TEXT NOT NULL,
            ssid TEXT,
            network_type TEXT,
            security_level TEXT,
            encryption_type TEXT,
            signal_strength INTEGER,
            is_hidden INTEGER DEFAULT 0,
            requires_hacking INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL
        )
        ''')
        
        # Table des fichiers
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            file_type TEXT,
            extension TEXT,
            size INTEGER,
            content TEXT,
            security_level INTEGER,
            is_encrypted INTEGER DEFAULT 0,
            importance INTEGER,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des puzzles de hacking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hacking_puzzles (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            puzzle_type TEXT,
            difficulty INTEGER,
            target_type TEXT,
            target_id TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des missions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            giver_id TEXT,
            location_id TEXT,
            mission_type TEXT,
            difficulty TEXT,
            rewards TEXT,
            prerequisites TEXT,
            is_main_quest INTEGER DEFAULT 0,
            is_repeatable INTEGER DEFAULT 0,
            is_hidden INTEGER DEFAULT 0,
            story_elements TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (giver_id) REFERENCES characters (id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL
        )
        ''')
        
        # Table des objectifs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS objectives (
            id TEXT PRIMARY KEY,
            mission_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            objective_type TEXT,
            target_id TEXT,
            target_count INTEGER DEFAULT 1,
            is_optional INTEGER DEFAULT 0,
            order_index INTEGER,
            completion_script TEXT,
            metadata TEXT,
            FOREIGN KEY (mission_id) REFERENCES missions (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des éléments d'histoire
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS story_elements (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            element_type TEXT,
            related_location_id TEXT,
            related_character_id TEXT,
            related_mission_id TEXT,
            order_index INTEGER,
            is_revealed INTEGER DEFAULT 0,
            reveal_condition TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (related_location_id) REFERENCES locations (id) ON DELETE SET NULL,
            FOREIGN KEY (related_character_id) REFERENCES characters (id) ON DELETE SET NULL,
            FOREIGN KEY (related_mission_id) REFERENCES missions (id) ON DELETE SET NULL
        )
        ''')
        
        # Tables pour les objets (hardware, software, consommables, etc.)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hardware_items (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            hardware_type TEXT,
            quality TEXT,
            rarity TEXT,
            level INTEGER,
            stats TEXT,
            location_type TEXT,
            location_id TEXT,
            price INTEGER,
            is_installed INTEGER DEFAULT 0,
            is_available INTEGER DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumable_items (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            item_type TEXT,
            rarity TEXT,
            uses INTEGER DEFAULT 1,
            effects TEXT,
            location_type TEXT,
            location_id TEXT,
            price INTEGER,
            is_available INTEGER DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
        ''')
        
        self.conn.commit()
        logger.debug("Structure de la base de données initialisée")
        
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.info("Connexion à la base de données fermée")
            
    def __del__(self):
        """Destructeur pour fermer la connexion automatiquement"""
        self.close()

def get_database(db_path: Optional[str] = None) -> Database:
    """
    Obtient une instance de la base de données
    
    Args:
        db_path: Chemin vers le fichier de base de données (optionnel)
        
    Returns:
        Instance de la base de données
    """
    if db_path is None:
        # Utiliser un chemin par défaut
        db_path = os.path.join(os.path.expanduser("~"), ".yaktaa", "yaktaa.db")
    
    # Créer le répertoire parent si nécessaire
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return Database(db_path)