#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer les tables d'items manquantes dans la base de données
et les remplir avec les données existantes si possible.
"""

import sqlite3
import json
import uuid
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_item_tables(db_path):
    """
    Crée les tables d'objets manquantes dans la base de données
    
    Args:
        db_path: Chemin vers la base de données
    """
    if not os.path.exists(db_path):
        logger.error(f"Base de données non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Vérifier quelles tables existent déjà
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    logger.info(f"Tables existantes: {existing_tables}")
    
    # Récupérer les IDs des mondes existants
    world_ids = []
    if 'worlds' in existing_tables:
        cursor.execute("SELECT id FROM worlds")
        world_ids = [row[0] for row in cursor.fetchall()]
        logger.info(f"Mondes trouvés: {len(world_ids)}")
    
    # Définir les tables à créer si elles n'existent pas
    tables_to_create = {
        "weapon_items": """
            CREATE TABLE IF NOT EXISTS weapon_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                weapon_type TEXT NOT NULL,
                damage INTEGER DEFAULT 10,
                damage_type TEXT DEFAULT 'physical',
                range INTEGER DEFAULT 1,
                accuracy REAL DEFAULT 0.7,
                rate_of_fire REAL DEFAULT 1.0,
                ammo_type TEXT,
                ammo_capacity INTEGER DEFAULT 8,
                mods_slots INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 100,
                is_legal INTEGER DEFAULT 1,
                location_type TEXT DEFAULT 'world',
                location_id TEXT,
                metadata TEXT,
                stats TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id)
            )
        """,
        "hardware_items": """
            CREATE TABLE IF NOT EXISTS hardware_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                hardware_type TEXT NOT NULL,
                performance INTEGER DEFAULT 5,
                power_consumption INTEGER DEFAULT 2,
                compatibility TEXT, -- JSON
                upgrade_slots INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                quality INTEGER DEFAULT 3,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 100,
                is_legal INTEGER DEFAULT 1,
                device_id TEXT,
                character_id TEXT,
                building_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id),
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (character_id) REFERENCES characters (id),
                FOREIGN KEY (building_id) REFERENCES buildings (id)
            )
        """,
        "software_items": """
            CREATE TABLE IF NOT EXISTS software_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                software_type TEXT NOT NULL,
                version TEXT DEFAULT '1.0',
                license_type TEXT DEFAULT 'standard',
                system_requirements TEXT, -- JSON
                capabilities TEXT, -- JSON 
                level INTEGER DEFAULT 1,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 100,
                is_legal INTEGER DEFAULT 1,
                device_id TEXT,
                character_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id),
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (character_id) REFERENCES characters (id)
            )
        """,
        "consumable_items": """
            CREATE TABLE IF NOT EXISTS consumable_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                consumable_type TEXT NOT NULL,
                effect_type TEXT DEFAULT 'health',
                effect_power INTEGER DEFAULT 10,
                duration INTEGER DEFAULT 60,
                cooldown INTEGER DEFAULT 0,
                addiction_chance REAL DEFAULT 0.0,
                level INTEGER DEFAULT 1,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 30,
                is_legal INTEGER DEFAULT 1,
                location_type TEXT DEFAULT 'world',
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id)
            )
        """,
        "clothing_items": """
            CREATE TABLE IF NOT EXISTS clothing_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                clothing_type TEXT NOT NULL,
                defense INTEGER DEFAULT 1,
                defense_type TEXT DEFAULT 'physical',
                slots TEXT NOT NULL,
                weight INTEGER DEFAULT 1,
                durability INTEGER DEFAULT 100,
                mod_slots INTEGER DEFAULT 0,
                style INTEGER DEFAULT 5,
                level INTEGER DEFAULT 1,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 50,
                is_legal INTEGER DEFAULT 1,
                location_type TEXT DEFAULT 'world',
                location_id TEXT,
                metadata TEXT,
                stats TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id)
            )
        """,
        "implant_items": """
            CREATE TABLE IF NOT EXISTS implant_items (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                implant_type TEXT NOT NULL,
                body_location TEXT NOT NULL,
                surgery_difficulty INTEGER DEFAULT 2,
                side_effects TEXT, -- JSON
                compatibility TEXT, -- JSON
                level INTEGER DEFAULT 1,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 500,
                is_legal INTEGER DEFAULT 1,
                hacking_boost INTEGER DEFAULT 0,
                combat_boost INTEGER DEFAULT 0,
                location_type TEXT DEFAULT 'world',
                location_id TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id)
            )
        """
    }
    
    # Créer les tables manquantes ou recréer celles qui ont une structure incorrecte
    for table_name, create_query in tables_to_create.items():
        should_create = False
        
        if table_name not in existing_tables:
            logger.info(f"La table {table_name} n'existe pas, création...")
            should_create = True
        else:
            # Vérifier la structure de la table existante
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {row[1]: row for row in cursor.fetchall()}
            
            # Vérifier les colonnes requises selon le type de table
            missing_columns = []
            if table_name == "weapon_items":
                if "damage" not in columns:
                    missing_columns.append("damage")
                if "stats" not in columns:
                    missing_columns.append("stats")
            elif table_name == "clothing_items" and "clothing_type" not in columns:
                missing_columns.append("clothing_type")
            elif table_name == "implant_items" and "implant_type" not in columns:
                missing_columns.append("implant_type")
            
            if missing_columns:
                logger.warning(f"La table {table_name} existe mais ne contient pas les colonnes: {', '.join(missing_columns)}")
                
                # Sauvegarder les données existantes avant de recréer la table
                try:
                    cursor.execute(f"SELECT * FROM {table_name}")
                    existing_data = cursor.fetchall()
                    logger.info(f"Sauvegarde de {len(existing_data)} entrées de la table {table_name} avant recréation")
                    
                    # Supprimer la table
                    cursor.execute(f"DROP TABLE {table_name}")
                    conn.commit()
                    
                    # Marquer pour création
                    should_create = True
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde/suppression de la table {table_name}: {e}")
                    should_create = True
            else:
                logger.info(f"La table {table_name} existe et sa structure est correcte")
        
        if should_create:
            try:
                logger.info(f"Création de la table {table_name}")
                cursor.execute(create_query)
                conn.commit()
            except Exception as e:
                logger.error(f"Erreur lors de la création de la table {table_name}: {e}")
    
    # Vérifier si l'inventaire des boutiques existe
    if 'shop_inventory' in existing_tables:
        logger.info("Récupération des articles depuis l'inventaire des boutiques")
        
        # Récupérer tous les articles de boutique par type
        cursor.execute("""
            SELECT item_id, item_type, price, quantity, metadata 
            FROM shop_inventory
        """)
        
        inventory_items = cursor.fetchall()
        logger.info(f"Articles trouvés dans l'inventaire: {len(inventory_items)}")
        
        # Créer un dictionnaire pour organiser les articles par type
        items_by_type = {}
        for item_id, item_type, price, quantity, metadata_str in inventory_items:
            # Déterminer le type d'article à partir de l'ID
            prefix = item_id.split('_')[0] if item_id else ""
            
            # Créer une entrée pour ce type s'il n'existe pas
            if prefix not in items_by_type:
                items_by_type[prefix] = []
            
            # Ajouter l'article à la liste
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except:
                metadata = {}
            
            # Ajouter à la liste
            items_by_type[prefix].append({
                'id': item_id,
                'name': metadata.get('name', f"Article {item_id}"),
                'description': metadata.get('description', f"Description de {item_id}"),
                'price': price,
                'quantity': quantity,
                'metadata': metadata
            })
        
        # Traiter chaque type d'article
        for item_type, items in items_by_type.items():
            logger.info(f"Traitement de {len(items)} articles de type {item_type}")
            
            # Insérer des articles dans les tables correspondantes
            for item in items:
                if not item['id']:
                    continue
                
                # Choisir un monde aléatoire si disponible
                world_id = world_ids[0] if world_ids else None
                
                # Aucune donnée extraite, créer des données fictives dans les tables
                if item_type == 'weapon':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO weapon_items (
                                id, world_id, name, description, weapon_type, 
                                damage, price, rarity, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'PISTOL', 10, item['price'], 'COMMON', metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'une arme: {e}")
                
                elif item_type == 'hardware':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO hardware_items (
                                id, world_id, name, description, hardware_type, 
                                price, quality, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'PROCESSOR', item['price'], 3, metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'un hardware: {e}")
                
                elif item_type == 'software':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO software_items (
                                id, world_id, name, description, software_type, 
                                price, version, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'UTILITY', item['price'], '1.0', metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'un software: {e}")
                
                elif item_type == 'consumable':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO consumable_items (
                                id, world_id, name, description, consumable_type, 
                                price, effect_power, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'HEALTH', item['price'], 10, metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'un consommable: {e}")
                
                elif item_type == 'clothing':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO clothing_items (
                                id, world_id, name, description, clothing_type, 
                                price, slots, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'JACKET', item['price'], 'torso', metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'un vêtement: {e}")
                
                elif item_type == 'implant':
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO implant_items (
                                id, world_id, name, description, implant_type, 
                                price, body_location, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['id'], world_id, item['name'], item['description'],
                            'NEURAL', item['price'], 'head', metadata_str
                        ))
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'insertion d'un implant: {e}")
    
    # Si les tables sont vides et qu'aucun objet n'a été récupéré des boutiques,
    # générer quelques exemples pour chaque type d'objet
    for table_name in tables_to_create.keys():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        if count == 0 and world_ids:
            logger.info(f"La table {table_name} est vide, génération d'articles d'exemple")
            
            # Générer 5 exemples pour chaque type
            for i in range(5):
                item_id = f"{table_name.split('_')[0]}_{uuid.uuid4()}"
                name = f"Example {table_name.split('_')[0]} {i+1}"
                description = f"Un exemple de {table_name.split('_')[0]} généré automatiquement"
                world_id = world_ids[0]
                
                if table_name == "weapon_items":
                    cursor.execute("""
                        INSERT INTO weapon_items (
                            id, world_id, name, description, weapon_type, 
                            damage, damage_type, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['PISTOL', 'RIFLE', 'SHOTGUN', 'SMG', 'MELEE'][i % 5],
                        10 + i * 5, 'physical', 'COMMON', 100 + i * 50, 1
                    ))
                
                elif table_name == "hardware_items":
                    cursor.execute("""
                        INSERT INTO hardware_items (
                            id, world_id, name, description, hardware_type, 
                            performance, quality, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['PROCESSOR', 'MEMORY', 'STORAGE', 'DISPLAY', 'PERIPHERAL'][i % 5],
                        5 + i, 3 + i % 3, 'COMMON', 100 + i * 30, 1
                    ))
                
                elif table_name == "software_items":
                    cursor.execute("""
                        INSERT INTO software_items (
                            id, world_id, name, description, software_type, 
                            version, license_type, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['UTILITY', 'SECURITY', 'HACKING', 'GAME', 'PRODUCTIVITY'][i % 5],
                        f"1.{i}", ['free', 'standard', 'pro', 'enterprise', 'illegal'][i % 5],
                        'COMMON', 50 + i * 25, 1
                    ))
                
                elif table_name == "consumable_items":
                    cursor.execute("""
                        INSERT INTO consumable_items (
                            id, world_id, name, description, consumable_type, 
                            effect_type, effect_power, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['HEALTH', 'STAMINA', 'FOCUS', 'BUFF', 'ANTIDOTE'][i % 5],
                        ['health', 'stamina', 'focus', 'strength', 'resistance'][i % 5],
                        10 + i * 5, 'COMMON', 20 + i * 10, 1
                    ))
                
                elif table_name == "clothing_items":
                    cursor.execute("""
                        INSERT INTO clothing_items (
                            id, world_id, name, description, clothing_type, 
                            defense, slots, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['JACKET', 'PANTS', 'HELMET', 'BOOTS', 'GLOVES'][i % 5],
                        2 + i, ['torso', 'legs', 'head', 'feet', 'hands'][i % 5],
                        'COMMON', 50 + i * 20, 1
                    ))
                
                elif table_name == "implant_items":
                    cursor.execute("""
                        INSERT INTO implant_items (
                            id, world_id, name, description, implant_type, 
                            body_location, surgery_difficulty, rarity, price, is_legal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, world_id, name, description, 
                        ['NEURAL', 'OPTICAL', 'SKELETAL', 'DERMAL', 'CIRCULATORY'][i % 5],
                        ['head', 'eyes', 'limbs', 'skin', 'torso'][i % 5],
                        2 + i % 3, 'COMMON', 500 + i * 100, 1
                    ))
    
    conn.commit()
    conn.close()
    
    logger.info("Création et remplissage des tables d'objets terminés")

if __name__ == "__main__":
    db_path = "worlds.db"
    create_item_tables(db_path)
