"""
Module pour la génération d'inventaires de boutiques
Contient les fonctions pour créer des inventaires pour les boutiques
"""

import uuid
import json
import logging
import random
import sys
import os
from typing import List, Optional, Dict, Any

# Importations adaptatives pour fonctionner dans différents contextes
try:
    # Essayer d'abord les importations relatives
    from database import get_database
    from shop_item_generator import ShopItemGenerator
except ImportError:
    try:
        # Essayer ensuite les importations avec le préfixe complet
        from yaktaa_world_editor.database import get_database
        from yaktaa_world_editor.shop_item_generator import ShopItemGenerator
    except ImportError:
        # Si toujours pas possible, ajouter le répertoire parent au chemin
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from yaktaa_world_editor.database import get_database
        from yaktaa_world_editor.shop_item_generator import ShopItemGenerator

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ShopInventory")

def generate_shop_inventory(db, world_id: str, shop_id: str, random_instance=None):
    """
    Génère un inventaire aléatoire pour une boutique spécifique
    
    Args:
        db: Base de données
        world_id: ID du monde
        shop_id: ID de la boutique
        random_instance: Instance de random pour la génération aléatoire
        
    Returns:
        Nombre d'articles générés
    """
    # Utiliser l'instance random fournie ou en créer une nouvelle
    random_gen = random_instance or random.Random()
    
    # Créer un générateur d'objets
    item_generator = ShopItemGenerator(random_gen)
    
    # Vérifier si la table worlds existe et si le monde spécifié existe
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worlds'")
    if not cursor.fetchone():
        logger.error("La table 'worlds' n'existe pas dans la base de données")
        # Créer la table worlds si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS worlds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                creation_date TEXT,
                is_active INTEGER DEFAULT 1,
                settings TEXT
            )
        ''')
        db.conn.commit()
        logger.info("Table 'worlds' créée")
    
    # Vérifier si le monde existe
    cursor.execute("SELECT id FROM worlds WHERE id = ?", (world_id,))
    if not cursor.fetchone():
        logger.error(f"Le monde {world_id} n'existe pas, création d'un monde de test")
        # Créer un monde de test avec une requête SQL simplifiée
        cursor.execute('''
            INSERT INTO worlds (id, name, description)
            VALUES (?, ?, ?)
        ''', (world_id, "Monde de test", "Un monde de test pour la génération d'inventaire"))
        db.conn.commit()
        logger.info(f"Monde de test créé avec ID: {world_id}")
    
    # Vérifier si la table shops existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
    if not cursor.fetchone():
        logger.error("La table 'shops' n'existe pas dans la base de données")
        # Créer la table shops si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                shop_type TEXT NOT NULL,
                location_id TEXT,
                building_id TEXT,
                owner_id TEXT,
                description TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (owner_id) REFERENCES characters (id) ON DELETE SET NULL
            )
        ''')
        db.conn.commit()
        logger.info("Table 'shops' créée")
    
    # Vérifier si la boutique existe
    cursor.execute("SELECT id FROM shops WHERE id = ?", (shop_id,))
    if not cursor.fetchone():
        logger.error(f"La boutique {shop_id} n'existe pas, création d'une boutique de test")
        # Créer une boutique de test
        cursor.execute('''
            INSERT INTO shops (id, world_id, name, shop_type, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (shop_id, world_id, "Boutique de test", "WEAPONS", "Une boutique de test", json.dumps({"is_legal": True})))
        db.conn.commit()
        logger.info(f"Boutique de test créée avec ID: {shop_id}")
    
    # Récupérer les informations de la boutique
    cursor.execute("SELECT shop_type, metadata FROM shops WHERE id = ? AND world_id = ?", (shop_id, world_id))
    shop_data = cursor.fetchone()
    
    if not shop_data:
        logger.error(f"Boutique non trouvée: {shop_id} dans le monde {world_id}")
        # Vérifier si la boutique existe mais avec un world_id différent
        cursor.execute("SELECT id, world_id FROM shops WHERE id = ?", (shop_id,))
        other_shop = cursor.fetchone()
        if other_shop:
            logger.error(f"Une boutique avec cet ID existe mais dans un autre monde: {other_shop[1]}")
        
        # Vérifier si d'autres boutiques existent dans ce monde
        cursor.execute("SELECT id, shop_type FROM shops WHERE world_id = ?", (world_id,))
        other_shops = cursor.fetchall()
        if other_shops:
            logger.info(f"Autres boutiques dans ce monde: {other_shops}")
            # Utiliser la première boutique trouvée
            shop_id = other_shops[0][0]
            logger.info(f"Utilisation de la boutique alternative: {shop_id}")
            cursor.execute("SELECT shop_type, metadata FROM shops WHERE id = ?", (shop_id,))
            shop_data = cursor.fetchone()
        else:
            logger.error("Impossible de trouver ou de créer une boutique valide")
            return 0
    
    shop_type = shop_data[0]
    logger.info(f"Type de boutique: {shop_type}")
    
    # Extraire les métadonnées (si disponibles)
    is_legal = True  # Par défaut, considérer la boutique comme légale
    try:
        if shop_data[1]:
            metadata = json.loads(shop_data[1])
            is_legal = metadata.get("is_legal", True)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Métadonnées invalides pour la boutique {shop_id}, utilisation des valeurs par défaut")
    
    # Vérifier si la table d'inventaire existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_inventory (
            id TEXT PRIMARY KEY,
            shop_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price_modifier REAL DEFAULT 1.0,
            is_featured INTEGER DEFAULT 0,
            is_limited_time INTEGER DEFAULT 0,
            expiry_date TEXT,
            metadata TEXT,
            added_at TEXT,
            price REAL,
            FOREIGN KEY (shop_id) REFERENCES shops(id)
        )
    ''')
    
    # Supprimer l'inventaire existant
    cursor.execute("DELETE FROM shop_inventory WHERE shop_id = ?", (shop_id,))
    
    # Nombre d'articles à générer selon le type de boutique
    num_items = random_gen.randint(5, 20)
    logger.info(f"Génération de {num_items} articles pour la boutique {shop_id}")
    
    # Compteur d'articles générés
    generated_items = 0
    
    # Générer des articles en fonction du type de boutique
    for i in range(num_items):
        item_id = None
        item_type = ""
        
        # Déterminer le type d'article à générer en fonction du type de boutique
        if shop_type == "HARDWARE":
            item_id = item_generator.generate_random_hardware_item(db, world_id, not is_legal)
            item_type = "HARDWARE"
        elif shop_type == "SOFTWARE":
            item_id = item_generator.generate_random_software_item(db, world_id, not is_legal)
            item_type = "SOFTWARE"
        elif shop_type == "WEAPONS":
            item_id = item_generator.generate_random_weapon_item(db, world_id, not is_legal)
            item_type = "WEAPON"
        elif shop_type == "IMPLANTS":
            # Utiliser la nouvelle méthode generate_random_implant
            item_id = item_generator.generate_random_implant(db, world_id, not is_legal)
            item_type = "IMPLANT"
        elif shop_type == "CLOTHING":
            # Utiliser la méthode generate_random_clothing pour les vêtements
            item_id = item_generator.generate_random_clothing(db, world_id, not is_legal)
            item_type = "CLOTHING"
        elif shop_type == "FOOD":
            # Utiliser la méthode generate_random_food_item pour les aliments
            item_id = item_generator.generate_random_food_item(db, world_id, not is_legal)
            item_type = random_gen.choice(["FOOD", "DRINK"])  # Le type sera déterminé par la méthode
        elif shop_type == "BLACK_MARKET":
            # Pour le marché noir, générer un mélange d'articles
            item_types = ["SOFTWARE", "WEAPON", "IMPLANT", "HARDWARE", "CLOTHING", "FOOD"]
            selected_type = random_gen.choice(item_types)
            
            if selected_type == "SOFTWARE":
                item_id = item_generator.generate_random_software_item(db, world_id, True)  # Toujours illégal
                item_type = "SOFTWARE"
            elif selected_type == "WEAPON":
                item_id = item_generator.generate_random_weapon_item(db, world_id, True)  # Toujours illégal
                item_type = "WEAPON"
            elif selected_type == "IMPLANT":
                item_id = item_generator.generate_random_implant(db, world_id, True)  # Toujours illégal
                item_type = "IMPLANT"
            elif selected_type == "HARDWARE":
                item_id = item_generator.generate_random_hardware_item(db, world_id, True)  # Toujours illégal
                item_type = "HARDWARE"
            elif selected_type == "CLOTHING":
                item_id = item_generator.generate_random_clothing(db, world_id, True)  # Toujours illégal
                item_type = "CLOTHING"
            elif selected_type == "FOOD":
                item_id = item_generator.generate_random_food_item(db, world_id, True)  # Toujours illégal
                item_type = random_gen.choice(["FOOD", "DRINK"])
        elif shop_type == "GENERAL":
            # Pour les magasins généraux, générer un mélange d'articles légaux
            item_types = ["SOFTWARE", "HARDWARE", "CLOTHING", "FOOD"]
            selected_type = random_gen.choice(item_types)
            
            if selected_type == "SOFTWARE":
                item_id = item_generator.generate_random_software_item(db, world_id, not is_legal)
                item_type = "SOFTWARE"
            elif selected_type == "HARDWARE":
                item_id = item_generator.generate_random_hardware_item(db, world_id, not is_legal)
                item_type = "HARDWARE"
            elif selected_type == "CLOTHING":
                item_id = item_generator.generate_random_clothing(db, world_id, not is_legal)
                item_type = "CLOTHING"
            elif selected_type == "FOOD":
                item_id = item_generator.generate_random_food_item(db, world_id, not is_legal)
                item_type = random_gen.choice(["FOOD", "DRINK"])
        elif shop_type == "CONSUMABLES":
            # Utiliser la méthode generate_random_food_item pour les consommables
            item_id = item_generator.generate_random_food_item(db, world_id, not is_legal)
            item_type = random_gen.choice(["FOOD", "DRINK"])
        else:
            # Type de boutique inconnu, générer un article aléatoire
            logger.warning(f"Type de boutique inconnu: {shop_type}, génération d'un article aléatoire")
            random_type = random_gen.choice(["SOFTWARE", "WEAPON", "IMPLANT", "HARDWARE", "CLOTHING", "FOOD"])
            
            if random_type == "SOFTWARE":
                item_id = item_generator.generate_random_software_item(db, world_id, not is_legal)
                item_type = "SOFTWARE"
            elif random_type == "WEAPON":
                item_id = item_generator.generate_random_weapon_item(db, world_id, not is_legal)
                item_type = "WEAPON"
            elif random_type == "IMPLANT":
                item_id = item_generator.generate_random_implant(db, world_id, not is_legal)
                item_type = "IMPLANT"
            elif random_type == "HARDWARE":
                item_id = item_generator.generate_random_hardware_item(db, world_id, not is_legal)
                item_type = "HARDWARE"
            elif random_type == "CLOTHING":
                item_id = item_generator.generate_random_clothing(db, world_id, not is_legal)
                item_type = "CLOTHING"
            elif random_type == "FOOD":
                item_id = item_generator.generate_random_food_item(db, world_id, not is_legal)
                item_type = random_gen.choice(["FOOD", "DRINK"])
        
        if item_id:
            logger.info(f"Article {i+1}/{num_items} généré: {item_type} {item_id}")
            # Générer un prix aléatoire
            base_price = random_gen.randint(10, 1000)  # Prix de base aléatoire
            price_modifier = random_gen.uniform(0.8, 2.0)  # Modificateur de prix
            
            # Calculer le prix réel de l'article
            price = base_price * (1 + price_modifier / 100)  # Appliquer le modificateur
            
            # Déterminer si l'article est mis en avant ou limité dans le temps
            is_featured = 1 if random_gen.random() < 0.2 else 0
            is_limited_time = 1 if random_gen.random() < 0.1 else 0
            
            # Date d'expiration pour les articles à durée limitée
            expiry_date = None
            if is_limited_time:
                # Date d'expiration aléatoire dans les 30 prochains jours
                import datetime
                days_to_add = random_gen.randint(7, 30)
                expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days_to_add)).strftime("%Y-%m-%d")
            
            # Définir les métadonnées de l'article
            metadata = {
                "last_restock": "2025-03-26",
                "quality": random_gen.choice(["common", "uncommon", "rare", "epic", "legendary"]),
                "condition": int(random_gen.uniform(50, 100)),  # Déplacer condition dans les métadonnées
                "restock_quantity": random_gen.randint(1, 3)  # Déplacer restock_quantity dans les métadonnées
            }
            
            # Ajouter l'article à l'inventaire
            inventory_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO shop_inventory (id, shop_id, item_type, item_id, quantity, price_modifier, 
                                           is_featured, is_limited_time, expiry_date, metadata, added_at, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            ''', (inventory_id, shop_id, item_type, item_id, random_gen.randint(1, 5), price_modifier, 
                 is_featured, is_limited_time, expiry_date, json.dumps(metadata), price))
            
            generated_items += 1
        else:
            logger.warning(f"Échec de la génération de l'article {i+1}/{num_items} de type {item_type}")
    
    db.conn.commit()
    logger.info(f"Inventaire généré pour la boutique {shop_id}: {generated_items} articles")
    
    return generated_items
