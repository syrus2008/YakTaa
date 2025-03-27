#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour la génération d'inventaire de boutique
"""

import sys
import os
import logging
import sqlite3
import uuid
import json

# Configurer le logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("YakTaa.Test")

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les modules nécessaires
from yaktaa_world_editor.database import WorldDatabase
from yaktaa_world_editor.shop_inventory_generator import generate_shop_inventory

def main():
    """Fonction principale du script de test"""
    
    # Chemin vers la base de données de test
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_world.db")
    
    # Créer une base de données temporaire pour les tests
    db = WorldDatabase(db_path)
    
    # Créer les tables nécessaires
    create_test_database(db)
    
    # Créer un monde de test
    world_id = create_test_world(db)
    
    # Créer une boutique de test
    shop_id = create_test_shop(db, world_id)
    
    # Générer un inventaire pour la boutique
    logger.info(f"Génération de l'inventaire pour la boutique {shop_id}...")
    num_items = generate_shop_inventory(db, world_id, shop_id)
    
    # Afficher les résultats
    logger.info(f"Inventaire généré avec succès: {num_items} articles")
    
    # Afficher les articles générés
    display_inventory(db, shop_id)
    
    logger.info("Test terminé avec succès")

def create_test_database(db):
    """Crée les tables nécessaires pour les tests"""
    
    cursor = db.conn.cursor()
    
    # Table des mondes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS worlds (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des boutiques
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            location_id TEXT,
            owner_id TEXT,
            shop_type TEXT,
            price_modifier REAL DEFAULT 1.0,
            specialty TEXT,
            inventory_rotation TEXT,
            metadata TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
        )
    ''')
    
    # Table des inventaires de boutique
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_inventory (
            id TEXT PRIMARY KEY,
            shop_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price_modifier REAL DEFAULT 1.0,
            condition INTEGER DEFAULT 100,
            is_special INTEGER DEFAULT 0,
            restock_quantity INTEGER DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY (shop_id) REFERENCES shops(id)
        )
    ''')
    
    db.conn.commit()

def create_test_world(db):
    """Crée un monde de test et retourne son ID"""
    
    cursor = db.conn.cursor()
    
    # Vérifier si un monde existe déjà
    cursor.execute("SELECT id FROM worlds LIMIT 1")
    existing_world = cursor.fetchone()
    
    if existing_world:
        return existing_world["id"]
    
    # Créer un nouveau monde
    world_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO worlds (id, name, description)
        VALUES (?, ?, ?)
    ''', (world_id, "Monde de test", "Un monde créé pour tester la génération d'inventaire"))
    
    db.conn.commit()
    logger.info(f"Monde de test créé avec l'ID: {world_id}")
    
    return world_id

def create_test_shop(db, world_id):
    """Crée une boutique de test et retourne son ID"""
    
    cursor = db.conn.cursor()
    
    # Vérifier si une boutique existe déjà
    cursor.execute("SELECT id FROM shops WHERE world_id = ? LIMIT 1", (world_id,))
    existing_shop = cursor.fetchone()
    
    if existing_shop:
        return existing_shop["id"]
    
    # Créer différents types de boutiques pour tester
    shop_types = ["HARDWARE", "SOFTWARE", "WEAPONS", "IMPLANTS", "CONSUMABLES", "BLACK_MARKET"]
    
    # Choisir un type aléatoire
    import random
    shop_type = random.choice(shop_types)
    
    # Créer des métadonnées pour la boutique
    metadata = {
        "is_legal": shop_type != "BLACK_MARKET",
        "security_level": random.randint(1, 10),
        "popularity": random.randint(1, 100)
    }
    
    # Créer une nouvelle boutique
    shop_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO shops (id, world_id, name, description, shop_type, price_modifier, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (shop_id, world_id, f"Boutique {shop_type}", 
          f"Une boutique de type {shop_type}", shop_type, 
          random.uniform(0.8, 1.2), json.dumps(metadata)))
    
    db.conn.commit()
    logger.info(f"Boutique de test créée avec l'ID: {shop_id} (Type: {shop_type}, Légale: {metadata['is_legal']})")
    
    return shop_id

def display_inventory(db, shop_id):
    """Affiche l'inventaire de la boutique"""
    
    cursor = db.conn.cursor()
    
    # Récupérer les informations de la boutique
    cursor.execute("SELECT name, shop_type FROM shops WHERE id = ?", (shop_id,))
    shop = cursor.fetchone()
    
    if not shop:
        logger.error(f"Boutique {shop_id} non trouvée")
        return
    
    logger.info(f"Inventaire de la boutique: {shop['name']} (Type: {shop['shop_type']})")
    
    # Récupérer l'inventaire
    cursor.execute('''
        SELECT item_type, quantity, price_modifier, condition, is_special
        FROM shop_inventory
        WHERE shop_id = ?
        ORDER BY item_type, price_modifier DESC
    ''', (shop_id,))
    
    items = cursor.fetchall()
    
    if not items:
        logger.info("Aucun article dans l'inventaire")
        return
    
    # Afficher les articles
    logger.info(f"Nombre total d'articles: {len(items)}")
    
    # Statistiques par type
    types_count = {}
    for item in items:
        item_type = item["item_type"]
        if item_type not in types_count:
            types_count[item_type] = 0
        types_count[item_type] += 1
    
    # Afficher les statistiques
    for item_type, count in types_count.items():
        logger.info(f"- {item_type}: {count} articles")
    
    # Afficher quelques articles en exemple
    logger.info("\nExemples d'articles:")
    for i, item in enumerate(items[:5]):  # Limiter à 5 exemples
        logger.info(f"{i+1}. Type: {item['item_type']}, Prix: {item['price_modifier']}, "
                   f"Quantité: {item['quantity']}, Condition: {item['condition']}, "
                   f"Spécial: {'Oui' if item['is_special'] else 'Non'}")

if __name__ == "__main__":
    main()
