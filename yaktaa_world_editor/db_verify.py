#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de la structure de la base de données YakTaa
Ce script vérifie que toutes les tables et colonnes nécessaires existent dans la base de données.
Si la base de données n'existe pas, elle sera créée avec la structure complète.
"""

import os
import sys
import sqlite3
import logging
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union, Set

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_verify')

class DatabaseVerifier:
    """Classe pour vérifier et créer la structure de la base de données YakTaa"""
    
    def __init__(self, db_path: Optional[str] = None, create_if_missing: bool = True):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données. Si None, utilise le chemin par défaut.
            create_if_missing: Si True, crée la base de données si elle n'existe pas
        """
        if db_path is None:
            # Chemin par défaut dans le dossier utilisateur
            db_path = os.path.join(Path.home(), "yaktaa_worlds.db")
        
        self.db_path = db_path
        self.conn = None
        
        # Vérifier si le fichier existe
        db_exists = os.path.exists(db_path)
        
        if not db_exists and not create_if_missing:
            logger.error(f"Base de données non trouvée: {db_path}")
            raise FileNotFoundError(f"Base de données non trouvée: {db_path}")
        
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connecter à la base de données
        self._connect()
        
        # Si la base de données n'existait pas, créer toutes les tables
        if not db_exists:
            logger.info(f"Création d'une nouvelle base de données: {db_path}")
            self._create_all_tables()
    
    def _connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Activer les clés étrangères
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Connecté à la base de données: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            raise
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.info("Connexion à la base de données fermée")
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Récupère les informations sur les colonnes d'une table
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des informations de colonnes
        """
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [dict(row) for row in cursor.fetchall()]
        return columns
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifie si une table existe dans la base de données
        
        Args:
            table_name: Nom de la table à vérifier
            
        Returns:
            True si la table existe, False sinon
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Vérifie si une colonne existe dans une table
        
        Args:
            table_name: Nom de la table
            column_name: Nom de la colonne
            
        Returns:
            True si la colonne existe, False sinon
        """
        if not self.table_exists(table_name):
            return False
        
        columns = self.get_table_info(table_name)
        return any(col['name'] == column_name for col in columns)
    
    def get_all_tables(self) -> List[str]:
        """
        Récupère la liste de toutes les tables dans la base de données
        
        Returns:
            Liste des noms de tables
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row['name'] for row in cursor.fetchall()]
    
    def _create_all_tables(self):
        """Crée toutes les tables nécessaires avec la structure complète"""
        try:
            cursor = self.conn.cursor()
            
            # Table des mondes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS worlds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                author TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version TEXT,
                tags TEXT,
                is_active INTEGER DEFAULT 0,
                metadata TEXT,
                complexity INTEGER DEFAULT 3
            )
            ''')
            
            # Table des lieux
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                coordinates TEXT,
                x_coord REAL,
                y_coord REAL,
                security_level INTEGER,
                population INTEGER,
                services TEXT,
                tags TEXT,
                parent_location_id TEXT,
                is_virtual INTEGER DEFAULT 0,
                is_discoverable INTEGER DEFAULT 1,
                discovery_requirements TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_location_id) REFERENCES locations (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des connexions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                source_location_id TEXT NOT NULL,
                target_location_id TEXT NOT NULL,
                travel_method TEXT,
                travel_time INTEGER,
                travel_cost INTEGER,
                requirements TEXT,
                is_bidirectional INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (source_location_id) REFERENCES locations (id) ON DELETE CASCADE,
                FOREIGN KEY (target_location_id) REFERENCES locations (id) ON DELETE CASCADE
            )
            ''')
            
            # Table des bâtiments
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS buildings (
                id TEXT PRIMARY KEY,
                location_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                security_level INTEGER,
                floors INTEGER DEFAULT 1,
                has_basement INTEGER DEFAULT 0,
                x_coord REAL,
                y_coord REAL,
                icon TEXT,
                metadata TEXT,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
            )
            ''')
            
            # Table des personnages
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                faction_id TEXT,
                profession TEXT,
                level INTEGER DEFAULT 1,
                hacking_level INTEGER DEFAULT 1,
                location_id TEXT,
                building_id TEXT,
                is_merchant INTEGER DEFAULT 0,
                is_enemy INTEGER DEFAULT 0,
                dialog_options TEXT,
                loot_table TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (faction_id) REFERENCES factions (id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des factions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS factions (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                ideology TEXT,
                power_level INTEGER,
                territory TEXT,
                relationships TEXT,
                notable_members TEXT,
                icon TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
            ''')
            
            # Table des appareils
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                network_id TEXT,
                name TEXT NOT NULL,
                device_type TEXT,
                os TEXT,
                os_version TEXT,
                security_level INTEGER,
                ip_address TEXT,
                mac_address TEXT,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                location_id TEXT,
                vulnerabilities TEXT,
                accessible_data TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (network_id) REFERENCES networks (id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des réseaux
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                id TEXT PRIMARY KEY,
                building_id TEXT,
                name TEXT NOT NULL,
                ssid TEXT,
                network_type TEXT,
                security_level INTEGER,
                security_type TEXT,
                encryption TEXT,
                signal_strength INTEGER,
                connected_devices TEXT,
                vulnerabilities TEXT,
                world_id TEXT NOT NULL,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des fichiers
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT,
                file_type TEXT,
                size INTEGER,
                device_id TEXT,
                world_id TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des missions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                giver_id TEXT,
                location_id TEXT,
                type TEXT,
                difficulty INTEGER,
                prerequisite_missions TEXT,
                objectives TEXT,
                rewards TEXT,
                consequences TEXT,
                time_limit INTEGER,
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
                description TEXT,
                target_type TEXT,
                target_id TEXT,
                completion_conditions TEXT,
                order_index INTEGER,
                metadata TEXT,
                FOREIGN KEY (mission_id) REFERENCES missions (id) ON DELETE CASCADE
            )
            ''')
            
            # Table des magasins
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                location_id TEXT,
                building_id TEXT,
                owner_id TEXT,
                name TEXT NOT NULL,
                type TEXT,
                description TEXT,
                reputation_requirement INTEGER DEFAULT 0,
                price_modifier REAL DEFAULT 1.0,
                restock_time INTEGER,
                world_id TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (owner_id) REFERENCES characters (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des inventaires de magasin
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_inventory (
                id TEXT PRIMARY KEY,
                shop_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                price_modifier REAL DEFAULT 1.0,
                condition REAL DEFAULT 100.0,
                is_special INTEGER DEFAULT 0,
                restock_quantity INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE CASCADE
            )
            ''')
            
            # Table des objets matériels (hardware)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardware_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                hardware_type TEXT NOT NULL,
                quality INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'Commun',
                level INTEGER DEFAULT 1,
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                is_installed INTEGER DEFAULT 0,
                is_available INTEGER DEFAULT 1,
                stats TEXT,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                device_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL,
                FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des objets consommables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumable_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                consumable_type TEXT NOT NULL,
                rarity TEXT DEFAULT 'Commun',
                uses INTEGER DEFAULT 1,
                duration INTEGER DEFAULT 15,
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                is_available INTEGER DEFAULT 1,
                effects TEXT,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                device_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL,
                FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des objets logiciels (software)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS software_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                software_type TEXT NOT NULL,
                version TEXT DEFAULT 'N/A',
                license_type TEXT DEFAULT 'Standard',
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                capabilities TEXT,
                world_id TEXT NOT NULL,
                device_id TEXT,
                file_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des armes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapon_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                weapon_type TEXT NOT NULL,
                damage INTEGER DEFAULT 1,
                damage_type TEXT,
                range INTEGER,
                accuracy INTEGER,
                rate_of_fire INTEGER,
                ammo_type TEXT,
                ammo_capacity INTEGER,
                mod_slots INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'Commun',
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des armures
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS armor_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                armor_type TEXT NOT NULL,
                defense INTEGER DEFAULT 1,
                defense_type TEXT,
                slots TEXT,
                weight INTEGER,
                durability INTEGER,
                mod_slots INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'Commun',
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des implants
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS implant_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                implant_type TEXT NOT NULL,
                body_location TEXT,
                surgery_difficulty INTEGER,
                side_effects TEXT,
                compatibility TEXT,
                rarity TEXT DEFAULT 'Commun',
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des équipements
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                equipment_type TEXT NOT NULL,
                slot TEXT,
                stats TEXT,
                requirements TEXT,
                rarity TEXT DEFAULT 'Commun',
                price INTEGER DEFAULT 0,
                is_legal INTEGER DEFAULT 1,
                world_id TEXT NOT NULL,
                building_id TEXT,
                character_id TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE SET NULL
            )
            ''')
            
            # Table des effets de statut
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_effects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                effect_type TEXT,
                duration INTEGER,
                strength INTEGER,
                is_positive INTEGER,
                stats_affected TEXT,
                world_id TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
            ''')
            
            logger.info("Toutes les tables ont été créées avec succès")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            raise
    
    def verify_table_structure(self, table_name: str, expected_columns: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        Vérifie si une table a la structure attendue
        
        Args:
            table_name: Nom de la table à vérifier
            expected_columns: Liste des colonnes attendues avec leurs types
            
        Returns:
            Tuple (succès, liste des problèmes détectés)
        """
        if not self.table_exists(table_name):
            return False, [f"Table {table_name} n'existe pas"]
        
        problems = []
        columns = self.get_table_info(table_name)
        column_names = {col['name'] for col in columns}
        
        # Vérifier si toutes les colonnes attendues sont présentes
        for expected in expected_columns:
            if expected['name'] not in column_names:
                problems.append(f"Colonne {expected['name']} manquante dans {table_name}")
        
        return len(problems) == 0, problems
    
    def verify_database_structure(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Vérifie la structure complète de la base de données
        
        Returns:
            Tuple (succès global, dictionnaire des problèmes par table)
        """
        # Définir les colonnes attendues pour chaque table
        expected_structure = {
            "worlds": [
                {"name": "id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "author", "type": "TEXT"},
                {"name": "created_at", "type": "TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP"},
                {"name": "version", "type": "TEXT"},
                {"name": "tags", "type": "TEXT"},
                {"name": "is_active", "type": "INTEGER"},
                {"name": "metadata", "type": "TEXT"},
                {"name": "complexity", "type": "INTEGER"}
            ],
            "locations": [
                {"name": "id", "type": "TEXT"},
                {"name": "world_id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "type", "type": "TEXT"},
                {"name": "coordinates", "type": "TEXT"},
                {"name": "x_coord", "type": "REAL"},
                {"name": "y_coord", "type": "REAL"},
                {"name": "security_level", "type": "INTEGER"},
                {"name": "population", "type": "INTEGER"},
                {"name": "is_discoverable", "type": "INTEGER"},
                {"name": "discovery_requirements", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ],
            "buildings": [
                {"name": "id", "type": "TEXT"},
                {"name": "location_id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "type", "type": "TEXT"},
                {"name": "security_level", "type": "INTEGER"},
                {"name": "floors", "type": "INTEGER"},
                {"name": "has_basement", "type": "INTEGER"},
                {"name": "x_coord", "type": "REAL"},
                {"name": "y_coord", "type": "REAL"},
                {"name": "icon", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ],
            "hardware_items": [
                {"name": "id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "hardware_type", "type": "TEXT"},
                {"name": "quality", "type": "INTEGER"},
                {"name": "level", "type": "INTEGER"},
                {"name": "price", "type": "INTEGER"},
                {"name": "is_legal", "type": "INTEGER"},
                {"name": "world_id", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ],
            "consumable_items": [
                {"name": "id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "consumable_type", "type": "TEXT"},
                {"name": "rarity", "type": "TEXT"},
                {"name": "duration", "type": "INTEGER"},
                {"name": "price", "type": "INTEGER"},
                {"name": "is_legal", "type": "INTEGER"},
                {"name": "world_id", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ],
            "software_items": [
                {"name": "id", "type": "TEXT"},
                {"name": "name", "type": "TEXT"},
                {"name": "description", "type": "TEXT"},
                {"name": "software_type", "type": "TEXT"},
                {"name": "version", "type": "TEXT"},
                {"name": "license_type", "type": "TEXT"},
                {"name": "price", "type": "INTEGER"},
                {"name": "is_legal", "type": "INTEGER"},
                {"name": "capabilities", "type": "TEXT"},
                {"name": "world_id", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ]
        }
        
        problems = {}
        all_success = True
        
        # Vérifier chaque table
        for table_name, expected_columns in expected_structure.items():
            success, table_problems = self.verify_table_structure(table_name, expected_columns)
            if not success:
                all_success = False
                problems[table_name] = table_problems
        
        return all_success, problems
    
    def fix_database_structure(self) -> bool:
        """
        Corrige la structure de la base de données en ajoutant les tables et colonnes manquantes
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        try:
            # Vérifier la structure actuelle
            success, problems = self.verify_database_structure()
            
            if success:
                logger.info("La structure de la base de données est correcte, aucune correction nécessaire")
                return True
            
            # Créer les tables manquantes et ajouter les colonnes manquantes
            logger.info("Correction de la structure de la base de données...")
            
            # Créer toutes les tables si elles n'existent pas
            self._create_all_tables()
            
            # Vérifier à nouveau
            success, remaining_problems = self.verify_database_structure()
            
            if success:
                logger.info("Structure de la base de données corrigée avec succès")
                return True
            else:
                logger.warning(f"Problèmes restants après correction: {remaining_problems}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la correction de la structure: {e}")
            return False


def main():
    """Fonction principale"""
    try:
        # Récupérer le chemin de la base de données depuis les arguments
        db_path = None
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
        
        # Créer l'instance de vérification
        verifier = DatabaseVerifier(db_path)
        
        # Vérifier la structure
        success, problems = verifier.verify_database_structure()
        
        if success:
            print("[OK] La structure de la base de données est correcte")
            return 0
        else:
            print("[ERREUR] Problèmes détectés dans la structure de la base de données:")
            for table, table_problems in problems.items():
                print(f"  Table {table}:")
                for problem in table_problems:
                    print(f"    - {problem}")
            
            # Corriger automatiquement les problèmes
            print("Correction automatique des problèmes...")
            if verifier.fix_database_structure():
                print("[OK] Structure corrigée avec succès")
                return 0
            else:
                print("[ERREUR] Échec de la correction de la structure")
                return 1
    
    except Exception as e:
        logger.error(f"Erreur non gérée: {e}")
        print(f"Erreur: {e}")
        return 1
    finally:
        # Fermer la connexion
        if 'verifier' in locals():
            verifier.close()


if __name__ == "__main__":
    sys.exit(main())
