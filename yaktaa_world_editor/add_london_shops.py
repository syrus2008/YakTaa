#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour ajouter des boutiques à Londres.
"""

import sqlite3
import logging
import uuid
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AddLondonShops")

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

def add_london_shops():
    """Ajoute des boutiques à Londres"""
    conn, cursor = connect_to_db()
    if not conn:
        return
    
    try:
        # Vérifier que Londres existe
        cursor.execute("SELECT id, name FROM locations WHERE id = ?", 
                       ("6bb2342c-2b34-4548-b87a-a730407254d7",))
        location = cursor.fetchone()
        if not location:
            logger.error("L'emplacement de Londres n'existe pas dans la base de données.")
            return
        
        london_id, london_name = location
        logger.info(f"Ajout de boutiques à {london_name} (ID: {london_id})")
        
        # Récupérer l'ID du monde associé à Londres
        cursor.execute("SELECT world_id FROM locations WHERE id = ?", (london_id,))
        world_id = cursor.fetchone()[0]
        
        # Liste des boutiques à ajouter
        new_shops = [
            {
                "id": str(uuid.uuid4()),
                "name": "London Tech Exchange",
                "description": "Un magasin spécialisé dans les équipements technologiques de pointe.",
                "shop_type": "HARDWARE",
                "price_modifier": 1.2,
                "reputation": 75,
                "specialty": "Périphériques réseau",
                "is_legal": 1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Hackney Software Solutions",
                "description": "Le meilleur endroit pour trouver des logiciels rares et des outils de programmation.",
                "shop_type": "SOFTWARE",
                "price_modifier": 1.1,
                "reputation": 85,
                "specialty": "Logiciels de sécurité",
                "is_legal": 1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Thames Black Market",
                "description": "Un marché clandestin caché sous les quais de la Tamise. Marchandises de qualité douteuse.",
                "shop_type": "BLACK_MARKET",
                "price_modifier": 1.5,
                "reputation": 40,
                "specialty": "Articles illégaux",
                "is_legal": 0
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Royal Arms",
                "description": "Une armurerie d'élite proposant des armes de haute qualité pour les professionnels.",
                "shop_type": "WEAPON",
                "price_modifier": 1.3,
                "reputation": 70,
                "specialty": "Armes personnalisées",
                "is_legal": 1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "CyberMod Clinic",
                "description": "Clinique spécialisée dans les implants cybernétiques et les modifications corporelles.",
                "shop_type": "IMPLANT",
                "price_modifier": 1.4,
                "reputation": 80,
                "specialty": "Implants neurologiques",
                "is_legal": 1
            }
        ]
        
        # Ajouter les boutiques
        shops_added = 0
        for shop in new_shops:
            try:
                cursor.execute(
                    """
                    INSERT INTO shops 
                    (id, world_id, name, description, location_id, shop_type, 
                     price_modifier, reputation, specialty, is_legal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        shop["id"],
                        world_id,
                        shop["name"],
                        shop["description"],
                        london_id,
                        shop["shop_type"],
                        shop["price_modifier"],
                        shop["reputation"],
                        shop["specialty"],
                        shop["is_legal"]
                    )
                )
                shops_added += 1
                logger.info(f"Boutique ajoutée: {shop['name']} (Type: {shop['shop_type']})")
            except sqlite3.Error as e:
                logger.error(f"Erreur lors de l'ajout de la boutique {shop['name']}: {e}")
        
        # Valider les changements
        conn.commit()
        logger.info(f"{shops_added} boutiques ajoutées à Londres avec succès")
        
    except sqlite3.Error as e:
        logger.error(f"Erreur de base de données: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("=== Début de l'ajout des boutiques à Londres ===")
    add_london_shops()
    logger.info("=== Fin de l'ajout des boutiques à Londres ===")
