"""
Module de gestion de base de données pour l'éditeur de monde YakTaa
Ce module gère la connexion à la base de données SQLite et fournit des fonctions
pour créer, lire, mettre à jour et supprimer des données de monde.
"""

import os
import logging
import sqlite3
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.Database")

class WorldDatabase:
    """
    Classe pour gérer la base de données des mondes YakTaa
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données. Si None, utilise le chemin par défaut.
        """
        if db_path is None:
            # Chemin par défaut dans le dossier utilisateur
            db_path = os.path.join(Path.home(), "yaktaa_worlds.db")
        
        self.db_path = db_path
        self.conn = None
        
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialiser la base de données
        self._connect()
        self._create_tables()
        self._update_schema()
        
        logger.info(f"Base de données initialisée: {db_path}")
    
    def _connect(self) -> None:
        """Établit la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Activer les clés étrangères
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Configurer pour retourner les résultats comme des dictionnaires
            self.conn.row_factory = sqlite3.Row
            logger.debug("Connexion à la base de données établie")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
            raise
    
    def _create_tables(self) -> None:
        """Crée les tables nécessaires si elles n'existent pas"""
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
                coordinates TEXT,
                security_level INTEGER,
                population INTEGER,
                services TEXT,
                tags TEXT,
                parent_location_id TEXT,
                is_virtual INTEGER DEFAULT 0,
                is_special INTEGER DEFAULT 0,
                is_dangerous INTEGER DEFAULT 0,
                location_type TEXT DEFAULT 'unknown',
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_location_id) REFERENCES locations(id) ON DELETE SET NULL
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
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES locations(id) ON DELETE CASCADE,
                FOREIGN KEY (destination_id) REFERENCES locations(id) ON DELETE CASCADE
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
                faction TEXT,
                role TEXT,
                profession TEXT,
                gender TEXT,
                importance INTEGER DEFAULT 1,
                hacking_level INTEGER DEFAULT 0,
                combat_level INTEGER DEFAULT 0,
                charisma INTEGER DEFAULT 0,
                wealth INTEGER DEFAULT 0,
                attributes TEXT,
                skills TEXT,
                inventory TEXT,
                is_quest_giver INTEGER DEFAULT 0,
                is_vendor INTEGER DEFAULT 0,
                is_hostile INTEGER DEFAULT 0,
                dialog_tree TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
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
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (giver_id) REFERENCES characters(id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des objectifs de mission
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
                FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des appareils (PC, smartphones, etc.)
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
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des fichiers
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                file_type TEXT,
                extension TEXT,
                size_kb INTEGER DEFAULT 1,
                size INTEGER DEFAULT 1,
                device_id TEXT,
                file_path TEXT,
                is_hidden INTEGER DEFAULT 0,
                is_encrypted INTEGER DEFAULT 0,
                security_level INTEGER DEFAULT 1,
                importance INTEGER DEFAULT 1,
                content TEXT,
                owner TEXT,
                creation_date TEXT,
                modified_date TEXT,
                permission_read INTEGER DEFAULT 1,
                permission_write INTEGER DEFAULT 1,
                permission_execute INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
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
                power_level INTEGER DEFAULT 5,
                territory TEXT,
                relationships TEXT,
                notable_members TEXT,
                icon TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des relations entre factions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS faction_relationships (
                id TEXT PRIMARY KEY,
                faction_id TEXT NOT NULL,
                related_faction_id TEXT NOT NULL,
                relationship_level INTEGER DEFAULT 0,
                relationship_status TEXT DEFAULT 'neutral',
                metadata TEXT,
                FOREIGN KEY (faction_id) REFERENCES factions(id) ON DELETE CASCADE,
                FOREIGN KEY (related_faction_id) REFERENCES factions(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des armes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                damage INTEGER,
                damage_type TEXT,
                weapon_range INTEGER,
                accuracy INTEGER,
                rate_of_fire INTEGER,
                ammo_type TEXT,
                ammo_capacity INTEGER,
                mod_slots INTEGER,
                rarity TEXT,
                value INTEGER,
                vendor_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (vendor_id) REFERENCES buildings(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des objets matériels (hardware)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardware_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                hardware_type TEXT NOT NULL,
                quality TEXT NOT NULL,
                rarity TEXT,
                level INTEGER NOT NULL DEFAULT 1,
                price INTEGER NOT NULL DEFAULT 0,
                is_legal BOOLEAN NOT NULL DEFAULT 1,
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
                rarity TEXT NOT NULL,
                uses INTEGER NOT NULL DEFAULT 1,
                duration INTEGER NOT NULL DEFAULT 15,
                price INTEGER NOT NULL DEFAULT 0,
                is_legal BOOLEAN NOT NULL DEFAULT 1,
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
            
            # Table des armures
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS armors (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                defense INTEGER,
                defense_type TEXT,
                slots TEXT,
                weight INTEGER,
                durability INTEGER,
                mod_slots INTEGER,
                rarity TEXT,
                value INTEGER,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des implants
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS implants (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                implant_type TEXT,
                body_location TEXT,
                surgery_difficulty INTEGER,
                side_effects TEXT,
                compatibility TEXT,
                rarity TEXT,
                value INTEGER,
                location_type TEXT,
                location_id TEXT,
                manufacturer TEXT,
                bonus TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des logiciels
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS software (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                software_type TEXT NOT NULL,
                version TEXT,
                developer TEXT,
                license_type TEXT DEFAULT 'commercial',
                level INTEGER DEFAULT 1,
                price INTEGER DEFAULT 0,
                is_malware INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'commun',
                metadata TEXT,
                release_date TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des vulnérabilités
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                code_name TEXT NOT NULL,
                description TEXT,
                vuln_type TEXT,
                difficulty INTEGER,
                impact INTEGER,
                cve TEXT,
                target_type TEXT,
                requirements TEXT,
                payloads TEXT,
                rewards TEXT,
                rarity TEXT,
                location_type TEXT,
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des magasins
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                location_id TEXT,
                building_id TEXT,
                owner_id TEXT,
                shop_type TEXT,
                price_modifier REAL DEFAULT 1.0,
                reputation INTEGER DEFAULT 5,
                specialty TEXT,
                inventory_rotation TEXT,
                is_legal INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE SET NULL,
                FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des inventaires de magasin
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_inventory (
                id TEXT PRIMARY KEY,
                shop_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                price INTEGER DEFAULT 0,
                price_modifier REAL DEFAULT 1.0,
                condition INTEGER DEFAULT 100,
                is_special INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                is_limited_time INTEGER DEFAULT 0,
                expiry_date TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                restock_quantity INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des inventaires des personnages
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_inventory (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                equipped INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des bâtiments
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS buildings (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                location_id TEXT NOT NULL,
                building_type TEXT,
                size INTEGER,
                height INTEGER,
                floors INTEGER,
                security_level INTEGER,
                owner_id TEXT,
                coordinates TEXT,
                is_restricted INTEGER DEFAULT 0,
                is_abandoned INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des pièces dans les bâtiments
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                building_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                room_type TEXT,
                floor INTEGER,
                size INTEGER,
                security_level INTEGER,
                is_locked INTEGER DEFAULT 0,
                is_restricted INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE
            )
            ''')
            
            # Table des réseaux
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                network_type TEXT,
                ssid TEXT,
                security_type TEXT,
                encryption TEXT,
                password TEXT,
                owner_id TEXT,
                location_id TEXT,
                building_id TEXT,
                is_hidden INTEGER DEFAULT 0,
                is_honeypot INTEGER DEFAULT 0,
                security_level INTEGER DEFAULT 1,
                requires_hacking INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE SET NULL
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
                target_id TEXT,
                target_type TEXT,
                solution TEXT,
                rewards TEXT,
                attempts_allowed INTEGER DEFAULT 3,
                time_limit INTEGER,
                hints TEXT,
                requires_hacking INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
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
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (related_location_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (related_character_id) REFERENCES characters(id) ON DELETE SET NULL,
                FOREIGN KEY (related_mission_id) REFERENCES missions(id) ON DELETE SET NULL
            )
            ''')
            
            # Table des logiciels installés sur les appareils
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_software (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                software_id TEXT NOT NULL,
                installation_date TEXT,
                is_active INTEGER DEFAULT 1,
                is_running INTEGER DEFAULT 0,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                FOREIGN KEY (software_id) REFERENCES software(id) ON DELETE CASCADE
            )
            ''')
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Erreur lors de la création des tables: {str(e)}")
            raise
    
    def _update_schema(self) -> None:
        """Vérifie et met à jour le schéma de la base de données si nécessaire"""
        try:
            cursor = self.conn.cursor()
            
            # Vérifier si la colonne location_type existe dans la table locations
            cursor.execute("PRAGMA table_info(locations)")
            location_columns = [col[1] for col in cursor.fetchall()]
            
            if "location_type" not in location_columns:
                logger.info("Ajout de la colonne location_type à la table locations")
                cursor.execute('''
                ALTER TABLE locations ADD COLUMN location_type TEXT DEFAULT 'unknown'
                ''')
                self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table characters
            cursor.execute("PRAGMA table_info(characters)")
            character_columns = [col[1] for col in cursor.fetchall()]
            
            missing_character_columns = {
                "profession": "TEXT",
                "gender": "TEXT",
                "importance": "INTEGER DEFAULT 1",
                "hacking_level": "INTEGER DEFAULT 0",
                "combat_level": "INTEGER DEFAULT 0",
                "charisma": "INTEGER DEFAULT 0",
                "wealth": "INTEGER DEFAULT 0"
            }
            
            for col_name, col_type in missing_character_columns.items():
                if col_name not in character_columns:
                    logger.info(f"Ajout de la colonne {col_name} à la table characters")
                    cursor.execute(f'''
                    ALTER TABLE characters ADD COLUMN {col_name} {col_type}
                    ''')
                    self.conn.commit()
            
            # Ajouter les colonnes liées au combat dans la table characters
            missing_combat_columns = {
                "enemy_type": "TEXT DEFAULT 'HUMAN'",
                "health": "INTEGER DEFAULT 50",
                "accuracy": "REAL DEFAULT 0.7",
                "initiative": "INTEGER DEFAULT 5",
                "damage": "INTEGER DEFAULT 5",
                "resistance_physical": "INTEGER DEFAULT 0",
                "resistance_energy": "INTEGER DEFAULT 0",
                "resistance_emp": "INTEGER DEFAULT 0",
                "resistance_biohazard": "INTEGER DEFAULT 0",
                "resistance_cyber": "INTEGER DEFAULT 0",
                "resistance_viral": "INTEGER DEFAULT 0",
                "resistance_nanite": "INTEGER DEFAULT 0",
                "hostility": "INTEGER DEFAULT 0",
                "ai_behavior": "TEXT DEFAULT 'defensive'",
                "combat_style": "TEXT DEFAULT 'balanced'",
                "special_abilities": "TEXT",
                "equipment_slots": "TEXT DEFAULT 'weapon,armor,accessory'"
            }
            
            for col_name, col_type in missing_combat_columns.items():
                if col_name not in character_columns:
                    logger.info(f"Ajout de la colonne de combat {col_name} à la table characters")
                    cursor.execute(f'''
                    ALTER TABLE characters ADD COLUMN {col_name} {col_type}
                    ''')
                    self.conn.commit()
            
            # Vérifier si les tables d'équipement existent
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment'")
            if not cursor.fetchone():
                logger.info("Création de la table 'equipment'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    subtype TEXT,
                    rarity TEXT,
                    price INTEGER DEFAULT 0,
                    level_required INTEGER DEFAULT 1,
                    base_damage INTEGER DEFAULT 0,
                    damage_type TEXT,
                    accuracy REAL DEFAULT 0,
                    critical_chance REAL DEFAULT 0,
                    critical_multiplier REAL DEFAULT 1.5,
                    range_max INTEGER DEFAULT 0,
                    base_armor INTEGER DEFAULT 0,
                    armor_type TEXT,
                    health_bonus INTEGER DEFAULT 0,
                    initiative_modifier INTEGER DEFAULT 0,
                    stealth_modifier REAL DEFAULT 0,
                    resistance_physical INTEGER DEFAULT 0,
                    resistance_energy INTEGER DEFAULT 0,
                    resistance_emp INTEGER DEFAULT 0,
                    resistance_biohazard INTEGER DEFAULT 0,
                    resistance_cyber INTEGER DEFAULT 0,
                    resistance_viral INTEGER DEFAULT 0,
                    resistance_nanite INTEGER DEFAULT 0,
                    special_abilities TEXT,
                    is_cybernetic BOOLEAN DEFAULT 0,
                    is_unique BOOLEAN DEFAULT 0,
                    slot TEXT,
                    weight REAL DEFAULT 1.0,
                    durability INTEGER DEFAULT 100,
                    tags TEXT,
                    icon_path TEXT,
                    model_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_world_id ON equipment(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_rarity ON equipment(rarity)")
                self.conn.commit()
            
            # Vérifier si la table character_equipment existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_equipment'")
            if not cursor.fetchone():
                logger.info("Création de la table 'character_equipment'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_equipment (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    equipment_id TEXT NOT NULL,
                    slot TEXT NOT NULL,
                    is_equipped BOOLEAN DEFAULT 0,
                    durability_current INTEGER DEFAULT 100,
                    modification_level INTEGER DEFAULT 0,
                    custom_name TEXT,
                    custom_properties TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
                    UNIQUE(character_id, equipment_id)
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_equip_char_id ON character_equipment(character_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_equip_is_equipped ON character_equipment(is_equipped)")
                self.conn.commit()
            
            # Vérifier si la table equipment_mods existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_mods'")
            if not cursor.fetchone():
                logger.info("Création de la table 'equipment_mods'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_mods (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    compatibility TEXT NOT NULL,
                    rarity TEXT,
                    price INTEGER DEFAULT 0,
                    level_required INTEGER DEFAULT 1,
                    damage_modifier INTEGER DEFAULT 0,
                    accuracy_modifier REAL DEFAULT 0,
                    critical_chance_modifier REAL DEFAULT 0,
                    critical_multiplier_modifier REAL DEFAULT 0,
                    range_modifier INTEGER DEFAULT 0,
                    defense_modifier INTEGER DEFAULT 0,
                    health_modifier INTEGER DEFAULT 0,
                    initiative_modifier INTEGER DEFAULT 0,
                    stealth_modifier REAL DEFAULT 0,
                    resistance_physical_modifier INTEGER DEFAULT 0,
                    resistance_energy_modifier INTEGER DEFAULT 0,
                    resistance_emp_modifier INTEGER DEFAULT 0,
                    resistance_biohazard_modifier INTEGER DEFAULT 0,
                    resistance_cyber_modifier INTEGER DEFAULT 0,
                    resistance_viral_modifier INTEGER DEFAULT 0,
                    resistance_nanite_modifier INTEGER DEFAULT 0,
                    effect_type TEXT,
                    effect_value INTEGER DEFAULT 0,
                    icon_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_mods_world_id ON equipment_mods(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_mods_compatibility ON equipment_mods(compatibility)")
                self.conn.commit()
            
            # Vérifier si la table equipment_installed_mods existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment_installed_mods'")
            if not cursor.fetchone():
                logger.info("Création de la table 'equipment_installed_mods'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_installed_mods (
                    id TEXT PRIMARY KEY,
                    character_equipment_id TEXT NOT NULL,
                    equipment_mod_id TEXT NOT NULL,
                    slot INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_equipment_id) REFERENCES character_equipment(id) ON DELETE CASCADE,
                    FOREIGN KEY (equipment_mod_id) REFERENCES equipment_mods(id) ON DELETE CASCADE,
                    UNIQUE(character_equipment_id, equipment_mod_id)
                )
                """)
                self.conn.commit()
            
            # Vérifier si les tables d'effets de statut existent
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='status_effects'")
            if not cursor.fetchone():
                logger.info("Création de la table 'status_effects'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS status_effects (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    duration INTEGER DEFAULT 3,
                    effect_value INTEGER,
                    effect_type TEXT NOT NULL,
                    is_debuff BOOLEAN DEFAULT 0,
                    visual_effect TEXT,
                    tick_frequency INTEGER DEFAULT 1,
                    stackable BOOLEAN DEFAULT 0,
                    max_stacks INTEGER DEFAULT 1,
                    icon_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_world_id ON status_effects(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_type ON status_effects(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_is_debuff ON status_effects(is_debuff)")
                self.conn.commit()
            
            # Vérifier si la table character_status_effects existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_status_effects'")
            if not cursor.fetchone():
                logger.info("Création de la table 'character_status_effects'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_status_effects (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    status_effect_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_remaining INTEGER,
                    current_stacks INTEGER DEFAULT 1,
                    source_character_id TEXT,
                    source_equipment_id TEXT,
                    source_ability_id TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_tick TIMESTAMP,
                    custom_properties TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                    FOREIGN KEY (status_effect_id) REFERENCES status_effects(id) ON DELETE CASCADE,
                    FOREIGN KEY (source_character_id) REFERENCES characters(id) ON DELETE SET NULL,
                    FOREIGN KEY (source_equipment_id) REFERENCES equipment(id) ON DELETE SET NULL
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_status_char_id ON character_status_effects(character_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_status_is_active ON character_status_effects(is_active)")
                self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table files
            cursor.execute("PRAGMA table_info(files)")
            file_columns = [col[1] for col in cursor.fetchall()]
            
            missing_file_columns = {
                "description": "TEXT",
                "extension": "TEXT",
                "size": "INTEGER DEFAULT 1",
                "importance": "INTEGER DEFAULT 1"
            }
            
            for col_name, col_type in missing_file_columns.items():
                if col_name not in file_columns:
                    logger.info(f"Ajout de la colonne {col_name} à la table files")
                    cursor.execute(f'''
                    ALTER TABLE files ADD COLUMN {col_name} {col_type}
                    ''')
                    self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table networks
            cursor.execute("PRAGMA table_info(networks)")
            network_columns = [col[1] for col in cursor.fetchall()]
            
            missing_network_columns = {
                "id": "TEXT PRIMARY KEY",
                "world_id": "TEXT NOT NULL",
                "name": "TEXT NOT NULL",
                "description": "TEXT",
                "network_type": "TEXT",
                "ssid": "TEXT",
                "security_type": "TEXT",
                "encryption": "TEXT",
                "password": "TEXT",
                "owner_id": "TEXT",
                "location_id": "TEXT",
                "building_id": "TEXT",
                "is_hidden": "INTEGER DEFAULT 0",
                "is_honeypot": "INTEGER DEFAULT 0",
                "security_level": "INTEGER DEFAULT 1",
                "requires_hacking": "INTEGER DEFAULT 0",
                "metadata": "TEXT"
            }
            
            # On vérifie d'abord si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='networks'")
            if cursor.fetchone():
                # La table existe, mais peut-être sans la colonne id
                if "id" not in network_columns:
                    # La colonne id n'existe pas, nous devons recréer la table
                    logger.info("Recréation de la table 'networks' avec la colonne id")
                    
                    # Créer une table temporaire avec la structure correcte
                    cursor.execute("""
                    CREATE TABLE networks_temp (
                        id TEXT PRIMARY KEY,
                        world_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        network_type TEXT,
                        ssid TEXT,
                        security_type TEXT,
                        encryption TEXT,
                        password TEXT,
                        owner_id TEXT,
                        location_id TEXT,
                        building_id TEXT,
                        is_hidden INTEGER DEFAULT 0,
                        is_honeypot INTEGER DEFAULT 0,
                        security_level INTEGER DEFAULT 1,
                        requires_hacking INTEGER DEFAULT 0,
                        metadata TEXT,
                        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                        FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL,
                        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
                        FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE SET NULL
                    )
                    """)
                    
                    # Insérer les données de l'ancienne table dans la nouvelle
                    # Si l'ancienne table n'a pas de colonne id, on en génère un avec uuid
                    try:
                        cursor.execute("SELECT * FROM networks")
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Récupérer les noms de colonnes
                            old_columns = [desc[0] for desc in cursor.description]
                            
                            for row in rows:
                                # Construire un dictionnaire avec les données existantes
                                data = {old_columns[i]: value for i, value in enumerate(row)}
                                
                                # Ajouter un id s'il n'existe pas
                                if "id" not in data or data["id"] is None:
                                    data["id"] = str(uuid.uuid4())
                                
                                # Construire la requête d'insertion
                                columns = []
                                placeholders = []
                                values = []
                                
                                for col, val in data.items():
                                    if col in missing_network_columns:
                                        columns.append(col)
                                        placeholders.append("?")
                                        values.append(val)
                                
                                # Insérer dans la table temporaire
                                cursor.execute(f"""
                                INSERT INTO networks_temp ({', '.join(columns)})
                                VALUES ({', '.join(placeholders)})
                                """, values)
                    except Exception as e:
                        logger.error(f"Erreur lors de la copie des données networks: {str(e)}")
                    
                    # Supprimer l'ancienne table
                    cursor.execute("DROP TABLE networks")
                    
                    # Renommer la table temporaire
                    cursor.execute("ALTER TABLE networks_temp RENAME TO networks")
                    
                    # Créer les index
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_networks_world_id ON networks(world_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_networks_location_id ON networks(location_id)")
                    self.conn.commit()
                else:
                    # La colonne id existe déjà, on vérifie les autres colonnes
                    for col_name, col_type in missing_network_columns.items():
                        if col_name not in network_columns:
                            logger.info(f"Ajout de la colonne {col_name} à la table networks")
                            cursor.execute(f'''
                            ALTER TABLE networks ADD COLUMN {col_name} {col_type}
                            ''')
                            self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table factions
            cursor.execute("PRAGMA table_info(factions)")
            faction_columns = [col[1] for col in cursor.fetchall()]
            
            missing_faction_columns = {
                "power_level": "INTEGER DEFAULT 5"
            }
            
            for col_name, col_type in missing_faction_columns.items():
                if col_name not in faction_columns:
                    logger.info(f"Ajout de la colonne {col_name} à la table factions")
                    cursor.execute(f'''
                    ALTER TABLE factions ADD COLUMN {col_name} {col_type}
                    ''')
                    self.conn.commit()
            
            # Vérifier si la table implants existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implants'")
            if not cursor.fetchone():
                logger.info("Création de la table 'implants'")
                cursor.execute("""
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
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_implants_world_id ON implants(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_implants_type ON implants(type)")
                self.conn.commit()
            else:
                # Vérifier si les colonnes nécessaires existent dans la table implants
                cursor.execute("PRAGMA table_info(implants)")
                implant_columns = [col[1] for col in cursor.fetchall()]
                
                missing_implant_columns = {
                    "type": "TEXT",
                    "level": "INTEGER DEFAULT 1",
                    "price": "INTEGER DEFAULT 0",
                    "rarity": "TEXT DEFAULT 'commun'",
                    "hacking_boost": "INTEGER DEFAULT 0",
                    "combat_boost": "INTEGER DEFAULT 0",
                    "legality": "TEXT DEFAULT 'legal'",
                    "manufacturer": "TEXT",
                    "bonus": "TEXT"
                }
                
                for col_name, col_type in missing_implant_columns.items():
                    if col_name not in implant_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table implants")
                        cursor.execute(f'''
                        ALTER TABLE implants ADD COLUMN {col_name} {col_type}
                        ''')
                        self.conn.commit()
            
            # Vérifier si la table character_implants existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_implants'")
            if not cursor.fetchone():
                logger.info("Création de la table 'character_implants'")
                cursor.execute("""
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
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_implants_character_id ON character_implants(character_id)")
                self.conn.commit()
            
            # Vérifier si la table vulnerabilities existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vulnerabilities'")
            if not cursor.fetchone():
                logger.info("Création de la table 'vulnerabilities'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT,
                    description TEXT,
                    vuln_type TEXT NOT NULL,
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
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_world_id ON vulnerabilities(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_target_id ON vulnerabilities(target_id)")
                self.conn.commit()
            else:
                # Vérifier si les colonnes nécessaires existent dans la table vulnerabilities
                cursor.execute("PRAGMA table_info(vulnerabilities)")
                vuln_columns = [col[1] for col in cursor.fetchall()]
                
                missing_vuln_columns = {
                    "id": "TEXT PRIMARY KEY",
                    "world_id": "TEXT NOT NULL",
                    "name": "TEXT",
                    "description": "TEXT",
                    "vuln_type": "TEXT NOT NULL",
                    "difficulty": "INTEGER DEFAULT 1",
                    "target_id": "TEXT",
                    "target_type": "TEXT",
                    "discovery_date": "TEXT",
                    "is_public": "INTEGER DEFAULT 0",
                    "is_patched": "INTEGER DEFAULT 0",
                    "exploits": "TEXT",
                    "code_name": "TEXT",
                    "impact": "INTEGER DEFAULT 1",
                    "rarity": "TEXT DEFAULT 'commun'"
                }
                
                for col_name, col_type in missing_vuln_columns.items():
                    if col_name not in vuln_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table vulnerabilities")
                        cursor.execute(f'''
                        ALTER TABLE vulnerabilities ADD COLUMN {col_name} {col_type}
                        ''')
                        self.conn.commit()
            
            # Vérifier si la table software existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='software'")
            if not cursor.fetchone():
                logger.info("Création de la table 'software'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS software (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    software_type TEXT NOT NULL,
                    version TEXT,
                    developer TEXT,
                    license_type TEXT DEFAULT 'commercial',
                    level INTEGER DEFAULT 1,
                    price INTEGER DEFAULT 0,
                    is_malware INTEGER DEFAULT 0,
                    rarity TEXT DEFAULT 'commun',
                    metadata TEXT,
                    release_date TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_software_world_id ON software(world_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_software_type ON software(software_type)")
                self.conn.commit()
            else:
                # Vérifier si les colonnes nécessaires existent dans la table software
                cursor.execute("PRAGMA table_info(software)")
                software_columns = [col[1] for col in cursor.fetchall()]
                
                missing_software_columns = {
                    "id": "TEXT PRIMARY KEY",
                    "world_id": "TEXT NOT NULL",
                    "name": "TEXT NOT NULL",
                    "description": "TEXT",
                    "software_type": "TEXT NOT NULL",
                    "version": "TEXT",
                    "developer": "TEXT",
                    "license_type": "TEXT DEFAULT 'commercial'",
                    "level": "INTEGER DEFAULT 1",
                    "price": "INTEGER DEFAULT 0",
                    "is_malware": "INTEGER DEFAULT 0",
                    "rarity": "TEXT DEFAULT 'commun'",
                    "metadata": "TEXT",
                    "release_date": "TEXT"
                }
                
                for col_name, col_type in missing_software_columns.items():
                    if col_name not in software_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table software")
                        cursor.execute(f'''
                        ALTER TABLE software ADD COLUMN {col_name} {col_type}
                        ''')
                        self.conn.commit()
            
            # Vérifier si la table device_software existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='device_software'")
            if not cursor.fetchone():
                logger.info("Création de la table 'device_software'")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_software (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    software_id TEXT NOT NULL,
                    installation_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_running INTEGER DEFAULT 0,
                    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                    FOREIGN KEY (software_id) REFERENCES software(id) ON DELETE CASCADE
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_software_device_id ON device_software(device_id)")
                self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table hacking_puzzles
            cursor.execute("PRAGMA table_info(hacking_puzzles)")
            hacking_puzzles_columns = [col[1] for col in cursor.fetchall()]
            
            missing_hacking_puzzles_columns = {
                "id": "TEXT PRIMARY KEY",
                "world_id": "TEXT NOT NULL",
                "name": "TEXT NOT NULL",
                "description": "TEXT",
                "puzzle_type": "TEXT",
                "difficulty": "INTEGER",
                "target_id": "TEXT",
                "target_type": "TEXT",
                "solution": "TEXT",
                "rewards": "TEXT",
                "attempts_allowed": "INTEGER DEFAULT 3",
                "time_limit": "INTEGER",
                "hints": "TEXT",
                "requires_hacking": "INTEGER DEFAULT 0",
                "metadata": "TEXT"
            }
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hacking_puzzles'")
            if cursor.fetchone():
                # La table existe, vérifier si les colonnes nécessaires sont présentes
                for col_name, col_type in missing_hacking_puzzles_columns.items():
                    if col_name not in hacking_puzzles_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table hacking_puzzles")
                        try:
                            cursor.execute(f'''
                            ALTER TABLE hacking_puzzles ADD COLUMN {col_name} {col_type}
                            ''')
                            self.conn.commit()
                        except sqlite3.Error as e:
                            # Ignorer si la colonne existe déjà ou autre erreur similaire
                            logger.warning(f"Erreur lors de l'ajout de la colonne {col_name}: {str(e)}")
            
            # Vérifier si les colonnes nécessaires existent dans la table hardware_items
            cursor.execute("PRAGMA table_info(hardware_items)")
            hardware_items_columns = [col[1] for col in cursor.fetchall()]
            
            missing_hardware_items_columns = {
                "id": "TEXT PRIMARY KEY",
                "name": "TEXT NOT NULL",
                "description": "TEXT",
                "hardware_type": "TEXT NOT NULL",
                "quality": "TEXT NOT NULL",
                "rarity": "TEXT",
                "level": "INTEGER NOT NULL DEFAULT 1",
                "price": "INTEGER NOT NULL DEFAULT 0",
                "is_legal": "BOOLEAN NOT NULL DEFAULT 1",
                "is_installed": "INTEGER DEFAULT 0",
                "is_available": "INTEGER DEFAULT 1",
                "stats": "TEXT",
                "world_id": "TEXT NOT NULL",
                "building_id": "TEXT",
                "character_id": "TEXT",
                "device_id": "TEXT",
                "location_type": "TEXT",
                "location_id": "TEXT",
                "metadata": "TEXT"
            }
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hardware_items'")
            if cursor.fetchone():
                # La table existe, vérifier si les colonnes nécessaires sont présentes
                for col_name, col_type in missing_hardware_items_columns.items():
                    if col_name not in hardware_items_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table hardware_items")
                        cursor.execute(f'''
                        ALTER TABLE hardware_items ADD COLUMN {col_name} {col_type}
                        ''')
                        self.conn.commit()
            
            # Vérifier si les colonnes nécessaires existent dans la table consumable_items
            cursor.execute("PRAGMA table_info(consumable_items)")
            consumable_items_columns = [col[1] for col in cursor.fetchall()]
            
            missing_consumable_items_columns = {
                "consumable_type": "TEXT NOT NULL DEFAULT 'Consommable'",
                "rarity": "TEXT NOT NULL",
                "uses": "INTEGER NOT NULL DEFAULT 1",
                "duration": "INTEGER NOT NULL DEFAULT 15",
                "price": "INTEGER NOT NULL DEFAULT 0",
                "is_legal": "BOOLEAN NOT NULL DEFAULT 1",
                "is_available": "INTEGER DEFAULT 1",
                "effects": "TEXT",
                "world_id": "TEXT NOT NULL",
                "building_id": "TEXT",
                "character_id": "TEXT",
                "device_id": "TEXT",
                "location_type": "TEXT",
                "location_id": "TEXT",
                "metadata": "TEXT"
            }
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='consumable_items'")
            if cursor.fetchone():
                # La table existe, vérifier si les colonnes nécessaires sont présentes
                for col_name, col_type in missing_consumable_items_columns.items():
                    if col_name not in consumable_items_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table consumable_items")
                        try:
                            cursor.execute(f'''
                            ALTER TABLE consumable_items ADD COLUMN {col_name} {col_type}
                            ''')
                            self.conn.commit()
                        except sqlite3.Error as e:
                            logger.error(f"Erreur lors de l'ajout de la colonne {col_name}: {e}")
            
            # Vérifier si les colonnes nécessaires existent dans la table shops
            cursor.execute("PRAGMA table_info(shops)")
            shops_columns = [col[1] for col in cursor.fetchall()]
            
            missing_shops_columns = {
                "building_id": "TEXT",
                "reputation": "INTEGER DEFAULT 5",
                "is_legal": "INTEGER DEFAULT 1"
            }
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
            if cursor.fetchone():
                # La table existe, vérifier si les colonnes nécessaires sont présentes
                for col_name, col_type in missing_shops_columns.items():
                    if col_name not in shops_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table shops")
                        try:
                            cursor.execute(f'''
                            ALTER TABLE shops ADD COLUMN {col_name} {col_type}
                            ''')
                            self.conn.commit()
                        except sqlite3.Error as e:
                            # Ignorer si la colonne existe déjà ou autre erreur similaire
                            logger.warning(f"Erreur lors de l'ajout de la colonne {col_name} à shops: {str(e)}")
            
            # Vérifier si les colonnes nécessaires existent dans la table shop_inventory
            cursor.execute("PRAGMA table_info(shop_inventory)")
            shop_inventory_columns = [col[1] for col in cursor.fetchall()]
            
            missing_shop_inventory_columns = {
                "price": "INTEGER DEFAULT 0",
                "is_featured": "INTEGER DEFAULT 0",
                "is_limited_time": "INTEGER DEFAULT 0",
                "expiry_date": "TEXT",
                "added_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
            }
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shop_inventory'")
            if cursor.fetchone():
                # La table existe, vérifier si les colonnes nécessaires sont présentes
                for col_name, col_type in missing_shop_inventory_columns.items():
                    if col_name not in shop_inventory_columns:
                        logger.info(f"Ajout de la colonne {col_name} à la table shop_inventory")
                        try:
                            cursor.execute(f'''
                            ALTER TABLE shop_inventory ADD COLUMN {col_name} {col_type}
                            ''')
                            self.conn.commit()
                        except sqlite3.Error as e:
                            # Ignorer si la colonne existe déjà ou autre erreur similaire
                            logger.warning(f"Erreur lors de l'ajout de la colonne {col_name} à shop_inventory: {str(e)}")
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la mise à jour du schéma: {str(e)}")
            raise
    
    def close(self) -> None:
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.debug("Connexion à la base de données fermée")
    
    def create_world(self, name: str, description: str = "", author: str = "", 
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        Crée un nouveau monde dans la base de données
        
        Args:
            name: Nom du monde
            description: Description du monde
            author: Auteur du monde
            tags: Liste de tags pour le monde
            metadata: Métadonnées supplémentaires
            
        Returns:
            ID du monde créé
        """
        try:
            world_id = str(uuid.uuid4())
            cursor = self.conn.cursor()
            
            tags_str = json.dumps(tags or [])
            metadata_str = json.dumps(metadata or {})
            
            cursor.execute('''
            INSERT INTO worlds (id, name, description, author, tags, metadata, version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (world_id, name, description, author, tags_str, metadata_str, "1.0"))
            
            self.conn.commit()
            logger.info(f"Monde créé: {name} (ID: {world_id})")
            return world_id
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création du monde: {str(e)}")
            raise
    
    def get_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un monde
        
        Args:
            world_id: ID du monde à récupérer
            
        Returns:
            Dictionnaire des informations du monde, ou None si non trouvé
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM worlds WHERE id = ?", (world_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            world_data = dict(row)
            
            # Convertir les champs JSON
            world_data["tags"] = json.loads(world_data["tags"])
            world_data["metadata"] = json.loads(world_data["metadata"])
            
            return world_data
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération du monde: {str(e)}")
            raise
    
    def get_all_worlds(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les mondes de la base de données
        
        Returns:
            Liste des mondes
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM worlds ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            
            worlds = []
            for row in rows:
                world_data = dict(row)
                world_data["tags"] = json.loads(world_data["tags"])
                world_data["metadata"] = json.loads(world_data["metadata"])
                worlds.append(world_data)
            
            return worlds
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des mondes: {str(e)}")
            raise
    
    def update_world(self, world_id: str, name: Optional[str] = None, 
                    description: Optional[str] = None, tags: Optional[List[str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Met à jour les informations d'un monde
        
        Args:
            world_id: ID du monde à mettre à jour
            name: Nouveau nom (si None, conserve l'ancien)
            description: Nouvelle description (si None, conserve l'ancienne)
            tags: Nouveaux tags (si None, conserve les anciens)
            metadata: Nouvelles métadonnées (si None, conserve les anciennes)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            # Récupérer les données actuelles
            current_data = self.get_world(world_id)
            if not current_data:
                logger.warning(f"Monde non trouvé pour mise à jour: {world_id}")
                return False
            
            # Préparer les données à mettre à jour
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if tags is not None:
                update_data["tags"] = json.dumps(tags)
            if metadata is not None:
                update_data["metadata"] = json.dumps(metadata)
            
            if not update_data:
                logger.debug(f"Aucune donnée à mettre à jour pour le monde: {world_id}")
                return True
            
            # Ajouter la date de mise à jour
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Construire la requête SQL
            fields = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(world_id)
            
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE worlds SET {fields} WHERE id = ?", values)
            
            self.conn.commit()
            logger.info(f"Monde mis à jour: {world_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la mise à jour du monde: {str(e)}")
            raise
    
    def delete_world(self, world_id: str) -> bool:
        """
        Supprime un monde et toutes ses données associées
        
        Args:
            world_id: ID du monde à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            # Ensure we get detailed error information
            self.conn.set_trace_callback(lambda sql: logger.debug(f"SQL executed: {sql}"))
            
            # Start a transaction to ensure all deletions happen atomically
            cursor = self.conn.cursor()
            
            # First check if the world exists
            cursor.execute("SELECT id FROM worlds WHERE id = ?", (world_id,))
            if not cursor.fetchone():
                logger.warning(f"Monde non trouvé pour suppression: {world_id}")
                return False
                
            # Get all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            tables.remove('worlds') if 'worlds' in tables else None
            
            # Log all tables for diagnostic purposes
            logger.debug(f"Tables in database: {tables}")
            
            # Try a different approach - temporarily disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Delete from all tables that might have world_id
            for table in tables:
                try:
                    logger.debug(f"Checking table {table} for world_id column...")
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if table == 'shop_inventory':
                        # First find all shops for this world
                        logger.info(f"Cleaning up shop_inventory for world {world_id}")
                        cursor.execute("SELECT id FROM shops WHERE world_id = ?", (world_id,))
                        shop_ids = [row[0] for row in cursor.fetchall()]
                        
                        if shop_ids:
                            # Delete inventory items for shops in this world
                            shop_ids_str = ','.join(['?'] * len(shop_ids))
                            cursor.execute(f"DELETE FROM shop_inventory WHERE shop_id IN ({shop_ids_str})", shop_ids)
                            count = cursor.rowcount
                            logger.debug(f"Deleted {count} shop inventory items for shops in world {world_id}")
                    
                    elif 'world_id' in columns:
                        logger.info(f"Deleting data from {table} for world {world_id}")
                        cursor.execute(f"DELETE FROM {table} WHERE world_id = ?", (world_id,))
                        count = cursor.rowcount
                        logger.debug(f"Deleted {count} rows from {table}")
                except sqlite3.Error as e:
                    logger.warning(f"Error processing table {table}: {str(e)}")
            
            # Now delete the world itself
            logger.info(f"Deleting world {world_id}")
            cursor.execute("DELETE FROM worlds WHERE id = ?", (world_id,))
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Commit all changes
            self.conn.commit()
            
            # Remove the trace callback
            self.conn.set_trace_callback(None)
            
            logger.info(f"Monde supprimé: {world_id}")
            return True
            
        except sqlite3.Error as e:
            # Get detailed information about the error
            logger.error(f"Erreur lors de la suppression du monde: {str(e)}")
            
            # Try to identify which foreign key constraint failed
            try:
                cursor.execute("PRAGMA foreign_key_check")
                fk_violations = cursor.fetchall()
                if fk_violations:
                    for violation in fk_violations:
                        logger.error(f"Foreign key violation: {violation}")
            except sqlite3.Error:
                pass
                
            # Remove the trace callback
            self.conn.set_trace_callback(None)
            
            # Roll back any changes
            try:
                self.conn.rollback()
            except:
                pass
                
            raise
    
    def set_active_world(self, world_id: str) -> bool:
        """
        Définit un monde comme actif (désactive tous les autres)
        
        Args:
            world_id: ID du monde à activer
            
        Returns:
            True si l'activation a réussi, False sinon
        """
        try:
            cursor = self.conn.cursor()
            
            # Désactiver tous les mondes
            cursor.execute("UPDATE worlds SET is_active = 0")
            
            # Activer le monde spécifié
            cursor.execute("UPDATE worlds SET is_active = 1 WHERE id = ?", (world_id,))
            
            rows_affected = cursor.rowcount
            self.conn.commit()
            
            if rows_affected > 0:
                logger.info(f"Monde activé: {world_id}")
                return True
            else:
                logger.warning(f"Monde non trouvé pour activation: {world_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'activation du monde: {str(e)}")
            raise
    
    def get_active_world(self) -> Optional[Dict[str, Any]]:
        """
        Récupère le monde actif
        
        Returns:
            Dictionnaire des informations du monde actif, ou None si aucun monde actif
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM worlds WHERE is_active = 1")
            row = cursor.fetchone()
            
            if not row:
                return None
            
            world_data = dict(row)
            world_data["tags"] = json.loads(world_data["tags"])
            world_data["metadata"] = json.loads(world_data["metadata"])
            
            return world_data
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération du monde actif: {str(e)}")
            raise

# Fonction pour obtenir une instance de la base de données
_db_instances = {}
import threading

def get_database(db_path: Optional[str] = None) -> WorldDatabase:
    """
    Récupère l'instance de la base de données pour le thread actuel
    
    Args:
        db_path: Chemin vers le fichier de base de données
        
    Returns:
        Instance de WorldDatabase
    """
    global _db_instances
    thread_id = threading.get_ident()
    
    if thread_id not in _db_instances:
        logger.debug(f"Création d'une nouvelle instance de base de données pour le thread {thread_id}")
        _db_instances[thread_id] = WorldDatabase(db_path)
    
    return _db_instances[thread_id]
