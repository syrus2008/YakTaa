#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de débogage pour corriger les problèmes d'inventaires de boutiques vides dans YakTaa.
Ce script vérifie tous les mondes dans la base de données et s'assure que chaque boutique a un inventaire.
Si une boutique n'a pas d'inventaire, il utilise le générateur d'objets pour en créer un.
"""

import os
import sys
import sqlite3
import logging
import uuid
import random
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import traceback

# Configurer le logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("YakTaa.DebugShopInventory")

# Ajouter le répertoire parent au chemin Python pour pouvoir importer les modules
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Importer les modules nécessaires
try:
    from yaktaa_world_editor.database import WorldDatabase, get_database
    from yaktaa_world_editor.shop_item_generator import ShopItemGenerator
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
    traceback.print_exc()
    sys.exit(1)

class ShopInventoryFixer:
    """Classe pour corriger les problèmes d'inventaires de boutiques vides"""
    
    def __init__(self, db_path=None):
        """Initialise le correcteur d'inventaires
        
        Args:
            db_path: Chemin vers la base de données (optionnel)
        """
        self.db_path = db_path
        self.db = get_database(db_path)
        self.random = random.Random()
        self.shop_item_generator = ShopItemGenerator(random_instance=self.random)
        
        logger.info(f"Correcteur d'inventaires initialisé avec base de données: {db_path}")
    
    def fix_all_shop_inventories(self):
        """Vérifie et corrige les inventaires de toutes les boutiques"""
        logger.info("Démarrage de la vérification des inventaires de boutiques...")
        
        # Récupérer tous les mondes
        worlds = self._get_all_worlds()
        logger.info(f"Nombre de mondes trouvés: {len(worlds)}")
        
        total_fixed = 0
        
        # Pour chaque monde, vérifier toutes les boutiques
        for world_id, world_name in worlds:
            logger.info(f"Vérification du monde '{world_name}' (ID: {world_id})")
            shops = self._get_all_shops_in_world(world_id)
            logger.info(f"Nombre de boutiques dans ce monde: {len(shops)}")
            
            fixed_count = 0
            for shop_id, shop_name, shop_type, is_legal, price_modifier in shops:
                has_inventory = self._check_shop_inventory(shop_id)
                if not has_inventory:
                    logger.warning(f"La boutique '{shop_name}' (ID: {shop_id}) n'a pas d'inventaire. Correction en cours...")
                    items_added = self._generate_inventory_for_shop(world_id, shop_id, shop_type, is_legal, price_modifier)
                    if items_added > 0:
                        logger.info(f"Inventaire créé pour la boutique '{shop_name}': {items_added} objets ajoutés")
                        fixed_count += 1
                    else:
                        logger.error(f"Échec de la création d'inventaire pour la boutique '{shop_name}'")
                else:
                    logger.info(f"La boutique '{shop_name}' (ID: {shop_id}) a déjà un inventaire")
            
            logger.info(f"Nombre de boutiques corrigées dans ce monde: {fixed_count}/{len(shops)}")
            total_fixed += fixed_count
        
        logger.info(f"Correction terminée. Nombre total de boutiques corrigées: {total_fixed}")
        return total_fixed
    
    def _get_all_worlds(self) -> List[Tuple[str, str]]:
        """Récupère tous les mondes dans la base de données
        
        Returns:
            Liste de tuples (world_id, world_name)
        """
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, name FROM worlds')
        return cursor.fetchall()
    
    def _get_all_shops_in_world(self, world_id: str) -> List[Tuple[str, str, str, int, float]]:
        """Récupère toutes les boutiques dans un monde
        
        Args:
            world_id: ID du monde
            
        Returns:
            Liste de tuples (shop_id, shop_name, shop_type, is_legal, price_modifier)
        """
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, name, shop_type, is_legal, price_modifier 
            FROM shops 
            WHERE world_id = ?
        ''', (world_id,))
        return cursor.fetchall()
    
    def _check_shop_inventory(self, shop_id: str) -> bool:
        """Vérifie si une boutique a un inventaire
        
        Args:
            shop_id: ID de la boutique
            
        Returns:
            True si la boutique a au moins un objet dans son inventaire, False sinon
        """
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM shop_inventory WHERE shop_id = ?', (shop_id,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def _generate_inventory_for_shop(self, world_id: str, shop_id: str, shop_type: str, 
                                     is_legal: int, price_modifier: float) -> int:
        """Génère un inventaire pour une boutique
        
        Args:
            world_id: ID du monde
            shop_id: ID de la boutique
            shop_type: Type de la boutique
            is_legal: Si la boutique est légale
            price_modifier: Modificateur de prix de la boutique
            
        Returns:
            Nombre d'objets ajoutés à l'inventaire
        """
        cursor = self.db.conn.cursor()
        items_added = 0
        
        # Déterminer le nombre d'articles à générer en fonction du type de boutique
        num_items = {
            "hardware": self.random.randint(10, 25),
            "software": self.random.randint(15, 30),
            "black_market": self.random.randint(5, 15),
            "consumables": self.random.randint(20, 40),
            "weapons": self.random.randint(8, 20),
            "implants": self.random.randint(5, 15),
            "general": self.random.randint(15, 35),
            "electronics": self.random.randint(10, 25),
            "digital_services": self.random.randint(5, 15),
            "datachips": self.random.randint(10, 20),
            "cybernetics": self.random.randint(5, 15)
        }.get(shop_type, self.random.randint(10, 20))
        
        # Mapper les types de boutiques aux types d'articles qu'elles vendent
        item_types_map = {
            "hardware": [
                ("hardware", 0.7),  # (type, probabilité)
                ("consumable", 0.2),
                ("software", 0.1)
            ],
            "software": [
                ("software", 0.8),
                ("hardware", 0.1),
                ("consumable", 0.1)
            ],
            "black_market": [
                ("hardware", 0.3),
                ("consumable", 0.3),
                ("weapon", 0.3),
                ("implant", 0.1)
            ],
            "consumables": [
                ("consumable", 0.9),
                ("hardware", 0.1)
            ],
            "weapons": [
                ("weapon", 0.8),
                ("hardware", 0.1),
                ("consumable", 0.1)
            ],
            "implants": [
                ("implant", 0.8),
                ("consumable", 0.1),
                ("hardware", 0.1)
            ],
            "general": [
                ("hardware", 0.3),
                ("consumable", 0.3),
                ("software", 0.2),
                ("weapon", 0.1),
                ("implant", 0.1)
            ],
            "electronics": [
                ("hardware", 0.8),
                ("software", 0.2)
            ],
            "digital_services": [
                ("software", 0.9),
                ("hardware", 0.1)
            ],
            "datachips": [
                ("software", 0.6),
                ("hardware", 0.4)
            ],
            "cybernetics": [
                ("implant", 0.7),
                ("hardware", 0.2),
                ("consumable", 0.1)
            ]
        }
        
        # Utiliser une distribution par défaut si le type de boutique n'est pas dans la carte
        item_types_distribution = item_types_map.get(shop_type, [
            ("hardware", 0.4),
            ("consumable", 0.3),
            ("software", 0.3)
        ])
        
        # Générer les articles
        for _ in range(num_items):
            try:
                # Choisir le type d'article selon la distribution de probabilité
                item_types, weights = zip(*item_types_distribution)
                item_type = self.random.choices(item_types, weights=weights, k=1)[0]
                
                # Générer un nouvel article
                item_id = None
                legal = bool(is_legal)
                
                if item_type == "hardware":
                    # Créer un objet hardware directement
                    hardware_type = self.random.choice(["CPU", "RAM", "GPU", "Motherboard", "HDD", "SSD", "Network Card"])
                    quality = self.random.choice(["Normal", "Good", "Excellent", "Superior", "Legendary"])
                    level = self.random.randint(1, 10)
                    name = f"{self.random.choice(['Quantum', 'Cyber', 'Tech'])} {hardware_type} {self.random.choice(['XL', 'Pro', 'Elite'])}"
                    description = f"Un {hardware_type} de qualité {quality}"
                    base_price = int(level * 100 * (1 + {"Normal": 0, "Good": 0.5, "Excellent": 1, "Superior": 2, "Legendary": 4}[quality]))
                    
                    item_id = f"hardware_{str(uuid.uuid4())}"
                    stats = {"processing": level * 2, "memory": level * 3, "speed": level * 1.5}
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS hardware_items (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            type TEXT,
                            description TEXT,
                            level INTEGER,
                            quality TEXT,
                            stats TEXT,
                            price INTEGER,
                            world_id TEXT,
                            is_legal INTEGER DEFAULT 1,
                            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                        )
                    ''')
                    
                    cursor.execute('''
                        INSERT INTO hardware_items (id, name, type, description, level, quality, 
                                                  stats, price, world_id, is_legal)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (item_id, name, hardware_type, description, level, quality, 
                         json.dumps(stats), base_price, world_id, 1 if legal else 0))
                
                elif item_type == "consumable":
                    # Créer un objet consommable directement
                    consumable_type = self.random.choice(["Data Chip", "Neural Booster", "Code Fragment", "Energy Drink"])
                    rarity = self.random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
                    name = f"{self.random.choice(['Neo', 'Cyber', 'Tech'])} {consumable_type}"
                    description = f"Un {consumable_type} de rareté {rarity}"
                    base_price = int(50 * {"Common": 1, "Uncommon": 2, "Rare": 5, "Epic": 10, "Legendary": 20}[rarity])
                    
                    item_id = f"consumable_{str(uuid.uuid4())}"
                    effects = {"health": self.random.randint(1, 10), "energy": self.random.randint(1, 10)}
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS consumable_items (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            type TEXT,
                            description TEXT,
                            rarity TEXT,
                            effects TEXT,
                            price INTEGER,
                            world_id TEXT,
                            is_legal INTEGER DEFAULT 1,
                            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                        )
                    ''')
                    
                    cursor.execute('''
                        INSERT INTO consumable_items (id, name, type, description, rarity, 
                                                   effects, price, world_id, is_legal)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (item_id, name, consumable_type, description, rarity, 
                         json.dumps(effects), base_price, world_id, 1 if legal else 0))
                
                elif item_type == "software":
                    # Utiliser le générateur d'objets pour les logiciels
                    item_id = self.shop_item_generator.generate_random_software_item(self.db, world_id, legal)
                
                elif item_type == "weapon":
                    # Utiliser le générateur d'objets pour les armes
                    try:
                        item_id = self.shop_item_generator.generate_random_weapon_item(self.db, world_id, legal)
                    except Exception as e:
                        logger.error(f"Erreur lors de la génération d'une arme: {e}")
                        # Fallback: créer une arme simple
                        item_id = f"weapon_{str(uuid.uuid4())}"
                        name = f"{self.random.choice(['Laser', 'Plasma', 'Sonic'])} Gun"
                        description = "Une arme futuriste"
                        
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS weapon_items (
                                id TEXT PRIMARY KEY,
                                name TEXT,
                                description TEXT,
                                damage INTEGER,
                                accuracy REAL,
                                price INTEGER,
                                world_id TEXT,
                                is_legal INTEGER DEFAULT 0,
                                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                            )
                        ''')
                        
                        cursor.execute('''
                            INSERT INTO weapon_items (id, name, description, damage, accuracy, 
                                                    price, world_id, is_legal)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (item_id, name, description, self.random.randint(5, 20), 
                             self.random.uniform(0.5, 1.0), self.random.randint(500, 2000), 
                             world_id, 0))
                
                elif item_type == "implant":
                    # Utiliser le générateur d'objets pour les implants
                    try:
                        item_id = self.shop_item_generator.generate_random_implant_item(self.db, world_id, legal)
                    except Exception as e:
                        logger.error(f"Erreur lors de la génération d'un implant: {e}")
                        # Fallback: créer un implant simple
                        item_id = f"implant_{str(uuid.uuid4())}"
                        name = f"{self.random.choice(['Neural', 'Cyber', 'Bio'])} Implant"
                        description = "Un implant cybernétique"
                        
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS implant_items (
                                id TEXT PRIMARY KEY,
                                name TEXT,
                                description TEXT,
                                boost_type TEXT,
                                boost_value INTEGER,
                                price INTEGER,
                                world_id TEXT,
                                is_legal INTEGER DEFAULT 1,
                                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                            )
                        ''')
                        
                        cursor.execute('''
                            INSERT INTO implant_items (id, name, description, boost_type, boost_value, 
                                                    price, world_id, is_legal)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (item_id, name, description, self.random.choice(["strength", "intelligence", "reflex"]), 
                             self.random.randint(1, 10), self.random.randint(1000, 5000), 
                             world_id, 1 if legal else 0))
                
                if item_id:
                    # Ajouter l'article à l'inventaire de la boutique
                    inventory_id = f"inv_{str(uuid.uuid4())}"
                    item_price_modifier = price_modifier * self.random.uniform(0.8, 1.2)
                    item_price_modifier = round(item_price_modifier, 2)
                    
                    # Déterminer la quantité
                    quantity = 1
                    if item_type == "consumable":
                        quantity = self.random.randint(1, 10)
                    elif item_type == "software":
                        quantity = self.random.randint(1, 5)
                    
                    cursor.execute('''
                        INSERT INTO shop_inventory (id, shop_id, item_id, item_type, quantity, price_modifier, added_at)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (inventory_id, shop_id, item_id, item_type, quantity, item_price_modifier))
                    
                    items_added += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de la génération d'un article: {e}")
                traceback.print_exc()
        
        self.db.conn.commit()
        return items_added


def main():
    """Fonction principale"""
    logger.info("Démarrage du correcteur d'inventaires de boutiques YakTaa")
    
    try:
        # Utiliser le chemin correct de la base de données
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaktaa_world_editor", "worlds.db")
        if os.path.exists(db_path):
            logger.info(f"Base de données trouvée: {db_path}")
            fixer = ShopInventoryFixer(db_path)
            shops_fixed = fixer.fix_all_shop_inventories()
            logger.info(f"Opération terminée. {shops_fixed} boutiques ont été corrigées.")
        else:
            logger.error(f"Base de données non trouvée: {db_path}")
            logger.info("Recherche d'autres bases de données...")
            
            # Essayer de trouver d'autres bases de données
            other_db_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaktaa.db"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"),
                os.path.join(os.path.expanduser("~"), ".yaktaa", "data", "yaktaa.db")
            ]
            
            for path in other_db_paths:
                if os.path.exists(path):
                    logger.info(f"Base de données alternative trouvée: {path}")
                    fixer = ShopInventoryFixer(path)
                    shops_fixed = fixer.fix_all_shop_inventories()
                    logger.info(f"Opération terminée. {shops_fixed} boutiques ont été corrigées.")
                    break
            else:
                logger.error("Aucune base de données trouvée. Veuillez spécifier le chemin manuellement.")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du correcteur: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
