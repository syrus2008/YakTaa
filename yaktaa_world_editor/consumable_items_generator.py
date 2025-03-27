"""
Module pour la génération des objets consommables
Contient les fonctions pour créer des consommables dans le monde
"""

import uuid
import json
import logging
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

from constants import CONSUMABLE_TYPES
# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ConsumableItems")

def generate_consumable_items(db, world_id: str, device_ids: List[str], 
                             building_ids: List[str], character_ids: List[str], 
                             num_items: int, random) -> List[str]:
    """
    Génère des objets consommables pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre d'objets à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des objets générés
    """
    consumable_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table consumable_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='consumable_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table consumable_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE consumable_items (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                consumable_type TEXT NOT NULL,
                rarity TEXT DEFAULT 'Common',
                uses INTEGER DEFAULT 1,
                effects TEXT,  -- JSON
                location_type TEXT,
                location_id TEXT,
                price INTEGER DEFAULT 50,
                is_available INTEGER DEFAULT 1,
                metadata TEXT,  -- JSON
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
        """)
        db.conn.commit()
        logger.info("Table consumable_items créée")
    
    # Composants de noms pour générer des noms réalistes
    prefixes = ["Cyber", "Neuro", "Quantum", "Data", "Code", "Synth", "Hack", "Pulse", "Crypt", "Ghost"]
    suffixes = ["Boost", "Chip", "Key", "Pack", "Patch", "Wave", "Surge", "Lock", "Break", "Link"]
    
    # Noms pour les objets de type FOOD
    food_prefixes = ["Synth", "Nutri", "Vita", "Protein", "Energy", "Bio", "Eco", "Hydra", "Calori", "Macro"]
    food_suffixes = ["Bar", "Pack", "Meal", "Ration", "Cube", "Drink", "Snack", "Pill", "Capsule", "Powder"]
    food_flavors = ["Original", "Spicy", "Sweet", "Savory", "Tangy", "Bitter", "Umami", "Fruity", "Herbal", "Neutral"]
    
    # Fabricants de consommables
    manufacturers = ["DataDynamics", "NeuraSoft", "CyberWare", "CodeFlow", "PulseTech", 
                    "SynthLogic", "QuantumByte", "NetRunner", "GhostSec", "CryptoCorp"]
    
    # Fabricants de nourriture
    food_manufacturers = ["NutriCorp", "SynthMeal", "VitaFoods", "ProteinTech", "MealMatrix", 
                         "BioNutrients", "EcoFeeds", "HydraFuel", "CaloriSystems", "MacroNourish"]
    
    for i in range(num_items):
        # Déterminer si on place cet objet dans un appareil, un bâtiment ou sur un personnage
        location_type = random.choice(["device", "building", "character", "shop", "loot"])
        location_id = None
        
        if location_type == "device" and device_ids:
            location_id = random.choice(device_ids)
        elif location_type == "building" and building_ids:
            location_id = random.choice(building_ids)
        elif location_type == "character" and character_ids:
            location_id = random.choice(character_ids)
        elif location_type == "shop":
            if building_ids:
                location_id = random.choice(building_ids)
            else:
                location_type = "loot"
                location_id = "world"
        else:  # loot
            location_type = "loot"
            location_id = "world"
            
        # Sélectionner un type de consommable
        consumable_type = random.choice(CONSUMABLE_TYPES)
        
        # Générer un nom en fonction du type de consommable
        if consumable_type == "FOOD":
            prefix = random.choice(food_prefixes)
            suffix = random.choice(food_suffixes)
            flavor = random.choice(food_flavors)
            manufacturer = random.choice(food_manufacturers)
            name = f"{manufacturer} {prefix}{suffix} {flavor}"
        else:
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            manufacturer = random.choice(manufacturers)
            # Version du produit
            version = f"v{random.randint(1, 9)}.{random.randint(0, 9)}"
            # Nom complet
            name = f"{manufacturer} {prefix}{suffix} {consumable_type} {version}"
        
        # Déterminer la rareté
        rarity = random.choices(
            ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"],
            weights=[40, 30, 20, 8, 2],
            k=1
        )[0]
        
        # Nombre d'utilisations
        uses = 1
        if consumable_type in ["DATA_CHIP", "CRYPTO_KEY", "SECURITY_TOKEN"]:
            uses = random.randint(1, 3)
            if rarity in ["RARE", "EPIC", "LEGENDARY"]:
                uses += random.randint(1, 3)
        elif consumable_type in ["NEURAL_BOOSTER", "BATTERY_PACK"]:
            uses = random.randint(2, 5)
            if rarity in ["RARE", "EPIC", "LEGENDARY"]:
                uses += random.randint(2, 5)
        elif consumable_type == "FOOD":
            uses = random.randint(1, 3)
            if rarity in ["RARE", "EPIC", "LEGENDARY"]:
                uses += random.randint(1, 2)
                
        # Prix basé sur la rareté et le nombre d'utilisations
        rarity_multiplier = {
            "COMMON": 1, "UNCOMMON": 1.5, "RARE": 3, 
            "EPIC": 6, "LEGENDARY": 10
        }
        base_price = 50 + random.randint(10, 50)
        price = int(base_price * rarity_multiplier.get(rarity, 1) * (uses * 0.5 + 0.5) * (0.8 + random.random() * 0.4))
        
        # Générer des effets en fonction du type
        effects = _generate_consumable_effects(consumable_type, rarity)
        
        # Description
        if consumable_type == "FOOD":
            calories = random.randint(100, 500)
            shelf_life = random.randint(30, 365)
            description = f"Un aliment synthétique de qualité {rarity.lower()} avec {uses} portion(s). Fabriqué par {manufacturer}. Contient {calories} calories. Se conserve {shelf_life} jours."
        else:
            description = f"Un {consumable_type} de qualité {rarity.lower()} avec {uses} utilisation(s). Fabriqué par {manufacturer}."
        
        # Générer des effets secondaires pour les objets rares
        side_effects = []
        if rarity in ["RARE", "EPIC", "LEGENDARY"] and random.random() < 0.4:
            possible_side_effects = [
                "Légère nausée", "Maux de tête temporaires", "Étourdissements", 
                "Vision floue", "Augmentation de la température corporelle",
                "Confusion temporaire", "Hyperactivité", "Fatigue"
            ]
            
            num_side_effects = random.randint(1, 2)
            side_effects = random.sample(possible_side_effects, k=num_side_effects)
        
        # Générer les métadonnées standardisées
        if consumable_type == "FOOD":
            metadata = MetadataStandardizer.standardize_food_metadata(
                food_type=random.choice(["MEAL", "SNACK", "DRINK", "SUPPLEMENT"]),
                calories=calories,
                nutrition_value=random.randint(1, 10),
                taste=random.choice(["SWEET", "SALTY", "SOUR", "BITTER", "UMAMI"]),
                shelf_life=shelf_life,
                effects=effects,
                side_effects=side_effects,
                manufacturer=manufacturer,
                weight=random.randint(10, 200) / 100.0,  # en kg
                is_perishable=(shelf_life < 60),
                allergens=random.sample(["GLUTEN", "LACTOSE", "SOY", "NUTS"], k=random.randint(0, 2))
            )
        else:
            # Pour les autres types de consommables
            metadata = MetadataStandardizer.standardize_consumable_metadata(
                consumable_type=consumable_type,
                uses_remaining=uses,
                effects=effects,
                side_effects=side_effects,
                manufacturer=manufacturer,
                version=version if consumable_type != "FOOD" else None,
                expiration_date=(datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                weight=random.randint(1, 20) / 10.0,  # en kg
                size=random.choice(["TINY", "SMALL", "MEDIUM"]),
                storage_condition=random.choice(["NORMAL", "COOL", "DRY", "SECURE"])
            )
        
        # Convertir en JSON
        metadata_json = MetadataStandardizer.to_json(metadata)
        
        # ID unique pour l'objet
        if consumable_type == "FOOD":
            consumable_id = f"food_{uuid.uuid4()}"
        else:
            consumable_id = f"consumable_{uuid.uuid4()}"
        
        # Insérer l'objet dans la base de données
        cursor.execute('''
        INSERT INTO consumable_items 
        (id, world_id, name, description, consumable_type, rarity, uses, 
        effects, location_type, location_id, price, is_available, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consumable_id, world_id, name, description, consumable_type, rarity, uses,
            json.dumps(effects), location_type, location_id, price, 1, metadata_json
        ))
        
        consumable_ids.append(consumable_id)
        
    logger.info(f"{len(consumable_ids)} objets consommables générés")
    db.conn.commit()
    return consumable_ids

def _generate_consumable_effects(consumable_type: str, rarity: str) -> Dict[str, Any]:
    """
    Génère des effets pour un objet consommable en fonction de son type et de sa rareté
    
    Args:
        consumable_type: Type de consommable
        rarity: Rareté du consommable
        
    Returns:
        Dictionnaire d'effets
    """
    effects = {}
    
    # Multiplicateur de puissance basé sur la rareté
    power_multiplier = {
        "COMMON": 1.0,
        "UNCOMMON": 1.5,
        "RARE": 2.5,
        "EPIC": 4.0,
        "LEGENDARY": 6.0
    }.get(rarity, 1.0)
    
    # Effets basés sur le type de consommable
    if consumable_type == "FOOD":
        # Effets de base pour la nourriture
        effects["health_restore"] = int(10 * power_multiplier)
        effects["stamina_restore"] = int(15 * power_multiplier)
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            effects["buff_duration"] = int(300 * power_multiplier)  # en secondes
            effects["stat_boost"] = {
                "strength": int(1 * power_multiplier),
                "endurance": int(1 * power_multiplier)
            }
            
        # Effets spéciaux pour les raretés légendaires
        if rarity == "LEGENDARY":
            effects["special_effect"] = "REGENERATION"
            effects["special_duration"] = int(600 * power_multiplier)  # en secondes
    
    elif consumable_type in ["STIM_PACK", "NEURAL_BOOSTER"]:
        # Effets pour les boosters
        effects["stat_boost"] = {
            "reflexes": int(2 * power_multiplier),
            "perception": int(2 * power_multiplier),
            "intelligence": int(1 * power_multiplier)
        }
        effects["buff_duration"] = int(180 * power_multiplier)  # en secondes
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["EPIC", "LEGENDARY"]:
            effects["special_effect"] = "SLOW_TIME"
            effects["special_duration"] = int(30 * power_multiplier)  # en secondes
    
    elif consumable_type in ["MED_KIT", "HEALTH_PACK"]:
        # Effets pour les kits médicaux
        effects["health_restore"] = int(30 * power_multiplier)
        effects["remove_status"] = ["BLEEDING", "POISONED"]
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            effects["regeneration_rate"] = int(5 * power_multiplier)
            effects["regeneration_duration"] = int(60 * power_multiplier)  # en secondes
    
    elif consumable_type in ["ANTIDOTE", "ANTI_VIRUS"]:
        # Effets pour les antidotes
        effects["remove_status"] = ["POISONED", "INFECTED", "CORRUPTED"]
        effects["immunity_duration"] = int(300 * power_multiplier)  # en secondes
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["EPIC", "LEGENDARY"]:
            effects["health_restore"] = int(15 * power_multiplier)
    
    elif consumable_type in ["DATA_CHIP", "CRYPTO_KEY", "SECURITY_TOKEN"]:
        # Effets pour les objets de hacking
        effects["hacking_bonus"] = int(10 * power_multiplier)
        effects["security_bypass_level"] = int(1 * power_multiplier)
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            effects["trace_reduction"] = int(25 * power_multiplier)  # en pourcentage
            effects["unlock_special_access"] = True
    
    elif consumable_type == "BATTERY_PACK":
        # Effets pour les batteries
        effects["energy_restore"] = int(50 * power_multiplier)
        
        # Effets supplémentaires pour les raretés plus élevées
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            effects["overcharge"] = True
            effects["overcharge_duration"] = int(120 * power_multiplier)  # en secondes
    
    else:
        # Effets génériques pour les autres types
        effects["utility_value"] = int(5 * power_multiplier)
        effects["duration"] = int(60 * power_multiplier)  # en secondes
    
    return effects