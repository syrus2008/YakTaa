#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer des armures de test et les ajouter à la base de données
"""

import sqlite3
import uuid
import json
import random
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ArmorGenerator')

def generate_armor_items(world_id, count=10):
    """Génère des armures de test et les ajoute à la base de données"""
    
    logger.info(f"Génération de {count} armures pour le monde {world_id}")
    
    # Types d'armure
    armor_types = ["HELMET", "CHEST", "LEGS", "BOOTS", "GLOVES", "SHIELD", "FULLBODY"]
    
    # Raretés
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    
    # Fabricants
    manufacturers = ["ArmorTech", "ShieldCorp", "MaxDefense", "BulletProof", "TitanGuard", "NanoProtect"]
    
    # Emplacements
    slots = ["HEAD", "TORSO", "LEGS", "FEET", "HANDS", "ARM", "FULL"]
    
    # Types de défense
    defense_types = ["PHYSICAL", "BALLISTIC", "ENERGY", "THERMAL", "CHEMICAL", "EMP"]
    
    # Connexion à la base de données
    try:
        conn = sqlite3.connect('worlds.db')
        cursor = conn.cursor()
        
        # Vérifier si la table armors existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='armors'")
        if not cursor.fetchone():
            logger.error("La table armors n'existe pas dans la base de données")
            return
        
        # Récupérer la structure de la table
        cursor.execute("PRAGMA table_info(armors)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        logger.info(f"Colonnes de la table armors: {column_names}")
        
        # Générer les armures
        armors = []
        for i in range(count):
            armor_type = random.choice(armor_types)
            rarity = random.choice(rarities)
            manufacturer = random.choice(manufacturers)
            defense = random.randint(10, 100)
            weight = random.randint(1, 20)
            durability = random.randint(50, 200)
            mod_slots = random.randint(0, 3)
            value = defense * 10 + (durability // 2) + (100 if rarity == "LEGENDARY" else 50 if rarity == "EPIC" else 20 if rarity == "RARE" else 10 if rarity == "UNCOMMON" else 5)
            
            # Générer un ID unique
            armor_id = f"armor_{str(uuid.uuid4())}"
            
            # Créer un nom pour l'armure
            suffix = ""
            if rarity == "LEGENDARY":
                suffix = " Omega"
            elif rarity == "EPIC":
                suffix = " Elite"
            elif rarity == "RARE":
                suffix = " Plus"
                
            name = f"{manufacturer} {armor_type.capitalize()}{suffix}"
            description = f"Une armure de type {armor_type} de qualité {rarity.lower()}. Fabriquée par {manufacturer}."
            
            # Préparer les métadonnées au format JSON
            metadata = {
                "materials": ["Steel", "Carbon Fiber", "Kevlar"] if rarity in ["EPIC", "LEGENDARY"] else ["Steel", "Leather"],
                "style": random.choice(["Military", "Civilian", "Corporate", "Street"]),
                "special_effects": ["Thermal Resistance", "Bullet Proof"] if rarity == "LEGENDARY" else []
            }
            
            # Emplacement aléatoire pour l'armure
            location_types = ["shop", "character", "building", "world"]
            location_type = random.choice(location_types)
            location_id = str(uuid.uuid4()) if location_type != "world" else None
            
            # Créer un dictionnaire pour l'armure
            armor = {
                "id": armor_id,
                "world_id": world_id,
                "name": name,
                "description": description,
                "defense": defense,
                "defense_type": random.choice(defense_types),
                "slots": slots[armor_types.index(armor_type)],
                "weight": weight,
                "durability": durability,
                "mod_slots": mod_slots,
                "rarity": rarity,
                "value": value,
                "location_type": location_type,
                "location_id": location_id,
                "metadata": json.dumps(metadata)
            }
            
            armors.append(armor)
            logger.debug(f"Armure générée: {name} ({armor_id})")
        
        # Insérer les armures dans la base de données
        for armor in armors:
            # Filtrer les clés qui correspondent aux colonnes de la table
            valid_keys = [key for key in armor.keys() if key in column_names]
            query = f"INSERT INTO armors ({', '.join(valid_keys)}) VALUES ({', '.join(['?' for _ in valid_keys])})"
            values = [armor[key] for key in valid_keys]
            
            cursor.execute(query, values)
        
        # Valider les changements
        conn.commit()
        logger.info(f"{len(armors)} armures générées et ajoutées à la base de données")
        
        # Vérifier que les armures ont bien été ajoutées
        cursor.execute("SELECT COUNT(*) FROM armors WHERE world_id = ?", (world_id,))
        count = cursor.fetchone()[0]
        logger.info(f"Nombre d'armures dans la base de données pour le monde {world_id}: {count}")
        
        conn.close()
        return True
    
    except sqlite3.Error as e:
        logger.error(f"Erreur SQL: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    # ID du monde à utiliser (celui utilisé dans nos tests)
    world_id = "e456e121-333f-4395-8d1a-cf2c19e67a0b"
    
    # Générer 15 armures
    success = generate_armor_items(world_id, 15)
    
    if success:
        logger.info("Génération d'armures terminée avec succès")
    else:
        logger.error("Échec de la génération d'armures")
