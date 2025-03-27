"""
Module pour la génération des armures
Contient les fonctions pour créer des armures dans le monde
"""

import uuid
import json
import logging
import random
from typing import List, Dict, Any

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ArmorItems")

def generate_armor_items(db, world_id: str, device_ids: List[str], 
                        building_ids: List[str], character_ids: List[str], 
                        num_items: int, random) -> List[str]:
    """
    Génère des armures pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre d'armures à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des armures générées
    """
    armor_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table armor_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='armor_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table armor_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE armor_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                armor_type TEXT NOT NULL,
                defense INTEGER DEFAULT 5,
                weight INTEGER DEFAULT 10,
                slot TEXT NOT NULL,
                rarity TEXT DEFAULT 'COMMON',
                price INTEGER DEFAULT 100,
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
        """)
        db.conn.commit()
        logger.info("Table armor_items créée")
    
    # Types d'armures
    armor_types = {
        "LIGHT": ["CLOTH", "LEATHER", "PADDED", "SYNTHETIC", "STEALTH"],
        "MEDIUM": ["REINFORCED", "TACTICAL", "COMBAT", "SECURITY", "MILITARY"],
        "HEAVY": ["PLATED", "POWERED", "EXOSKELETON", "BALLISTIC", "RIOT"],
        "SPECIAL": ["HAZMAT", "EMP_PROOF", "THERMAL", "RADIATION", "NANO_FIBER"]
    }
    
    # Emplacements d'armure
    armor_slots = ["HEAD", "CHEST", "ARMS", "LEGS", "FEET", "FULL_BODY"]
    
    # Fabricants d'armures
    manufacturers = {
        "LIGHT": ["ShadowTech", "NimbleWear", "FlexArmor", "StealthSystems", "AgileSuit"],
        "MEDIUM": ["TacticalGear", "UrbanDefense", "CombatWear", "SecuriTech", "BattleReady"],
        "HEAVY": ["IronShield", "TitanArmor", "FortressWear", "MaxDefense", "BulletStop"],
        "SPECIAL": ["HazGuard", "EnviroSafe", "TechShield", "QuantumArmor", "NanoDefense"]
    }
    
    # Raretés
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    rarity_weights = [40, 30, 20, 8, 2]
    
    for i in range(num_items):
        # Générer un ID unique avec préfixe armor_
        armor_id = f"armor_{uuid.uuid4()}"
        
        # Déterminer si on place cette armure dans un appareil, un bâtiment ou sur un personnage
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
        
        # Sélectionner une catégorie d'armure
        armor_category = random.choice(list(armor_types.keys()))
        
        # Sélectionner un type d'armure dans cette catégorie
        armor_type = random.choice(armor_types[armor_category])
        
        # Sélectionner un emplacement d'armure
        slot = random.choice(armor_slots)
        
        # Sélectionner un fabricant
        manufacturer = random.choice(manufacturers[armor_category])
        
        # Version du produit
        model = f"Mk{random.randint(1, 9)}"
        
        # Nom complet
        name = f"{manufacturer} {armor_type} {slot.capitalize()} {model}"
        
        # Déterminer la rareté
        rarity = random.choices(rarities, weights=rarity_weights, k=1)[0]
        
        # Niveau requis basé sur la rareté
        level_map = {
            "COMMON": random.randint(1, 3),
            "UNCOMMON": random.randint(2, 5),
            "RARE": random.randint(4, 8),
            "EPIC": random.randint(7, 12),
            "LEGENDARY": random.randint(10, 15)
        }
        level = level_map.get(rarity, 1)
        
        # Prix basé sur la rareté et le niveau
        price_base = {
            "COMMON": 80,
            "UNCOMMON": 400,
            "RARE": 1600,
            "EPIC": 6000,
            "LEGENDARY": 20000
        }
        price_multiplier = 1 + (level * 0.2)
        price = int(price_base.get(rarity, 80) * price_multiplier)
        
        # Défense et poids basés sur le type d'armure et la rareté
        defense_base = {
            "LIGHT": 3,
            "MEDIUM": 6,
            "HEAVY": 10,
            "SPECIAL": 8
        }
        
        weight_base = {
            "LIGHT": 2,
            "MEDIUM": 5,
            "HEAVY": 10,
            "SPECIAL": 7
        }
        
        # Multiplicateurs de rareté
        rarity_multiplier = {
            "COMMON": 1.0,
            "UNCOMMON": 1.3,
            "RARE": 1.7,
            "EPIC": 2.2,
            "LEGENDARY": 3.0
        }
        
        # Multiplicateurs d'emplacement
        slot_defense_multiplier = {
            "HEAD": 0.7,
            "CHEST": 1.0,
            "ARMS": 0.6,
            "LEGS": 0.8,
            "FEET": 0.5,
            "FULL_BODY": 1.5
        }
        
        slot_weight_multiplier = {
            "HEAD": 0.5,
            "CHEST": 1.0,
            "ARMS": 0.6,
            "LEGS": 0.8,
            "FEET": 0.4,
            "FULL_BODY": 2.0
        }
        
        # Calculer les statistiques finales
        defense = int(defense_base.get(armor_category, 5) * 
                     rarity_multiplier.get(rarity, 1.0) * 
                     slot_defense_multiplier.get(slot, 1.0))
        
        weight = int(weight_base.get(armor_category, 5) * 
                    slot_weight_multiplier.get(slot, 1.0))
        
        # Effets spéciaux basés sur la rareté
        special_effects = _generate_special_effects(armor_category, armor_type, rarity, random)
        
        # Bonus de défense
        defense_bonus = _generate_defense_bonus(armor_category, armor_type, rarity, random)
        
        # Illégalité
        is_legal = 0 if (rarity in ["EPIC", "LEGENDARY"] and random.random() < 0.3) or armor_category == "SPECIAL" else 1
        
        # Description
        description = _generate_description(armor_category, armor_type, slot, rarity, name, manufacturer, special_effects, random)
        
        # Générer les métadonnées standardisées
        metadata = MetadataStandardizer.standardize_armor_metadata(
            armor_type=armor_type,
            slot=slot,
            defense=defense,
            weight=weight,
            durability=random.randint(50, 100),
            resistances=_generate_resistances(armor_category, armor_type),
            special_effects=special_effects,
            defense_bonus=defense_bonus,
            required_level=level,
            manufacturer=manufacturer,
            model=model,
            mobility_penalty=_calculate_mobility_penalty(armor_category, weight)
        )
        
        # Convertir en JSON
        metadata_json = MetadataStandardizer.to_json(metadata)
        
        # Insérer l'armure dans la base de données
        cursor.execute("""
            INSERT INTO armor_items (
                id, name, description, armor_type, defense, weight, slot,
                rarity, price, is_legal, world_id, location_type, 
                location_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            armor_id, name, description, armor_type, defense, weight, slot,
            rarity, price, is_legal, world_id, location_type, 
            location_id, metadata_json
        ))
        
        armor_ids.append(armor_id)
    
    db.conn.commit()
    logger.info(f"{len(armor_ids)} armures générées")
    
    return armor_ids

def _generate_special_effects(armor_category: str, armor_type: str, rarity: str, random) -> List[str]:
    """
    Génère des effets spéciaux pour une armure en fonction de sa catégorie, son type et sa rareté
    
    Args:
        armor_category: Catégorie d'armure
        armor_type: Type d'armure
        rarity: Rareté de l'armure
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste d'effets spéciaux
    """
    # Effets spéciaux par catégorie d'armure
    effects_by_category = {
        "LIGHT": [
            "Camouflage actif",
            "Silence des mouvements",
            "Augmentation de l'agilité",
            "Dissipation thermique",
            "Réduction de signature"
        ],
        "MEDIUM": [
            "Protection balistique",
            "Stabilisation tactique",
            "Assistance au mouvement",
            "Régulation thermique",
            "Système d'alerte"
        ],
        "HEAVY": [
            "Absorption des chocs",
            "Blindage renforcé",
            "Assistance hydraulique",
            "Résistance aux explosifs",
            "Stabilisation avancée"
        ],
        "SPECIAL": [
            "Protection environnementale",
            "Isolation électromagnétique",
            "Régulation biologique",
            "Adaptation climatique",
            "Filtration avancée"
        ]
    }
    
    # Nombre d'effets en fonction de la rareté
    num_effects = {
        "COMMON": 0,
        "UNCOMMON": 1,
        "RARE": 1,
        "EPIC": 2,
        "LEGENDARY": 3
    }.get(rarity, 0)
    
    if num_effects == 0:
        return []
    
    # Sélectionner des effets aléatoires
    available_effects = effects_by_category.get(armor_category, [])
    
    if not available_effects:
        return []
    
    return random.sample(available_effects, min(num_effects, len(available_effects)))

def _generate_defense_bonus(armor_category: str, armor_type: str, rarity: str, random) -> Dict[str, Any]:
    """
    Génère des bonus de défense pour une armure
    
    Args:
        armor_category: Catégorie d'armure
        armor_type: Type d'armure
        rarity: Rareté de l'armure
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Dictionnaire de bonus de défense
    """
    # Bonus de défense par catégorie d'armure
    defense_bonuses = {
        "LIGHT": {
            "dodge_chance": (5, 20),
            "stealth_bonus": (5, 25),
            "movement_speed": (5, 15),
            "critical_resistance": (5, 15),
            "heat_resistance": (5, 20)
        },
        "MEDIUM": {
            "damage_reduction": (5, 20),
            "stamina_efficiency": (5, 15),
            "balance": (5, 20),
            "status_resistance": (5, 15),
            "recovery_rate": (5, 15)
        },
        "HEAVY": {
            "physical_resistance": (10, 30),
            "impact_resistance": (10, 30),
            "stability": (5, 20),
            "knockback_resistance": (10, 30),
            "durability_bonus": (10, 30)
        },
        "SPECIAL": {
            "environmental_protection": (10, 30),
            "radiation_resistance": (10, 30),
            "electrical_resistance": (10, 30),
            "thermal_regulation": (10, 30),
            "chemical_resistance": (10, 30)
        }
    }
    
    # Multiplicateur de bonus en fonction de la rareté
    multiplier = {
        "COMMON": 0.6,
        "UNCOMMON": 0.8,
        "RARE": 1.0,
        "EPIC": 1.3,
        "LEGENDARY": 1.6
    }.get(rarity, 1.0)
    
    # Nombre de bonus en fonction de la rareté
    num_bonuses = {
        "COMMON": 0,
        "UNCOMMON": 1,
        "RARE": 2,
        "EPIC": 2,
        "LEGENDARY": 3
    }.get(rarity, 0)
    
    result = {}
    
    if num_bonuses == 0:
        return result
    
    # Sélectionner des bonus aléatoires
    available_bonuses = defense_bonuses.get(armor_category, {})
    
    if not available_bonuses:
        return result
    
    selected_bonuses = random.sample(list(available_bonuses.keys()), 
                                    min(num_bonuses, len(available_bonuses)))
    
    for bonus in selected_bonuses:
        min_val, max_val = available_bonuses[bonus]
        value = random.randint(min_val, max_val)
        result[bonus] = int(value * multiplier)
    
    return result

def _generate_description(armor_category: str, armor_type: str, slot: str, rarity: str, 
                         name: str, manufacturer: str, special_effects: List[str], random) -> str:
    """
    Génère une description pour une armure
    
    Args:
        armor_category: Catégorie d'armure
        armor_type: Type d'armure
        slot: Emplacement d'armure
        rarity: Rareté de l'armure
        name: Nom de l'armure
        manufacturer: Fabricant de l'armure
        special_effects: Effets spéciaux de l'armure
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Description de l'armure
    """
    # Descriptions de base par catégorie d'armure
    base_descriptions = {
        "LIGHT": [
            f"Une protection {slot.lower()} légère privilégiant la mobilité et la discrétion.",
            f"Cette armure {slot.lower()} légère offre une protection de base sans compromettre l'agilité.",
            f"Un équipement de protection {slot.lower()} léger conçu pour les utilisateurs privilégiant la vitesse."
        ],
        "MEDIUM": [
            f"Une armure {slot.lower()} tactique offrant un bon équilibre entre protection et mobilité.",
            f"Cette protection {slot.lower()} intermédiaire combine efficacité défensive et confort d'utilisation.",
            f"Un équipement de combat {slot.lower()} polyvalent adapté à diverses situations tactiques."
        ],
        "HEAVY": [
            f"Une armure {slot.lower()} lourde offrant une protection maximale contre les menaces graves.",
            f"Cette protection {slot.lower()} renforcée privilégie la défense au détriment de la mobilité.",
            f"Un équipement défensif {slot.lower()} robuste conçu pour résister aux attaques les plus violentes."
        ],
        "SPECIAL": [
            f"Une armure {slot.lower()} spécialisée conçue pour des environnements ou menaces spécifiques.",
            f"Cette protection {slot.lower()} avancée intègre des technologies de pointe pour des défenses spécifiques.",
            f"Un équipement {slot.lower()} hautement spécialisé offrant des capacités défensives uniques."
        ]
    }
    
    # Qualificatifs en fonction de la rareté
    rarity_adjectives = {
        "COMMON": ["standard", "basique", "fonctionnel"],
        "UNCOMMON": ["amélioré", "avancé", "performant"],
        "RARE": ["supérieur", "remarquable", "exceptionnel"],
        "EPIC": ["extraordinaire", "révolutionnaire", "ultramoderne"],
        "LEGENDARY": ["légendaire", "inégalé", "transcendant"]
    }
    
    # Sélectionner une description de base
    base_desc = random.choice(base_descriptions.get(armor_category, 
                                                  [f"Une armure {slot.lower()} conçue pour la protection au combat."]))
    
    # Ajouter un qualificatif de rareté
    adjective = random.choice(rarity_adjectives.get(rarity, ["standard"]))
    
    # Construire la description
    description = f"{base_desc} Ce modèle {adjective} de {manufacturer} "
    
    # Ajouter des informations sur les effets spéciaux
    if special_effects:
        if len(special_effects) == 1:
            description += f"offre {special_effects[0].lower()}."
        else:
            effects_text = ", ".join([e.lower() for e in special_effects[:-1]])
            description += f"offre {effects_text} et {special_effects[-1].lower()}."
    else:
        description += f"offre des performances optimales pour sa catégorie."
    
    # Ajouter une note marketing
    marketing_notes = [
        f"Le {name} représente l'avenir de la technologie de protection.",
        f"Faites passer votre sécurité au niveau supérieur avec le {name}.",
        f"Conçu pour ceux qui ne font aucun compromis sur leur protection.",
        f"La fusion parfaite entre sécurité et fonctionnalité.",
        f"Redéfinissez votre approche de la défense personnelle avec cette armure de pointe."
    ]
    
    description += f" {random.choice(marketing_notes)}"
    
    return description

def _generate_resistances(armor_category: str, armor_type: str) -> Dict[str, int]:
    """
    Génère des résistances pour une armure
    
    Args:
        armor_category: Catégorie d'armure
        armor_type: Type d'armure
        
    Returns:
        Dictionnaire de résistances
    """
    resistances = {}
    
    # Résistances de base par catégorie
    if armor_category == "LIGHT":
        resistances = {
            "PHYSICAL": 10,
            "ENERGY": 5,
            "THERMAL": 15,
            "ELECTRICAL": 5,
            "CHEMICAL": 0
        }
    elif armor_category == "MEDIUM":
        resistances = {
            "PHYSICAL": 20,
            "ENERGY": 15,
            "THERMAL": 10,
            "ELECTRICAL": 10,
            "CHEMICAL": 10
        }
    elif armor_category == "HEAVY":
        resistances = {
            "PHYSICAL": 30,
            "ENERGY": 20,
            "THERMAL": 15,
            "ELECTRICAL": 15,
            "CHEMICAL": 15
        }
    elif armor_category == "SPECIAL":
        if "HAZMAT" in armor_type:
            resistances = {
                "PHYSICAL": 10,
                "ENERGY": 10,
                "THERMAL": 20,
                "ELECTRICAL": 10,
                "CHEMICAL": 40
            }
        elif "EMP_PROOF" in armor_type:
            resistances = {
                "PHYSICAL": 10,
                "ENERGY": 20,
                "THERMAL": 10,
                "ELECTRICAL": 40,
                "CHEMICAL": 10
            }
        elif "THERMAL" in armor_type:
            resistances = {
                "PHYSICAL": 10,
                "ENERGY": 15,
                "THERMAL": 40,
                "ELECTRICAL": 10,
                "CHEMICAL": 10
            }
        elif "RADIATION" in armor_type:
            resistances = {
                "PHYSICAL": 10,
                "ENERGY": 30,
                "THERMAL": 20,
                "ELECTRICAL": 10,
                "CHEMICAL": 20
            }
        else:
            resistances = {
                "PHYSICAL": 15,
                "ENERGY": 15,
                "THERMAL": 15,
                "ELECTRICAL": 15,
                "CHEMICAL": 15
            }
    
    return resistances

def _calculate_mobility_penalty(armor_category: str, weight: int) -> int:
    """
    Calcule la pénalité de mobilité d'une armure
    
    Args:
        armor_category: Catégorie d'armure
        weight: Poids de l'armure
        
    Returns:
        Pénalité de mobilité (en pourcentage)
    """
    base_penalty = {
        "LIGHT": 0,
        "MEDIUM": 5,
        "HEAVY": 15,
        "SPECIAL": 10
    }.get(armor_category, 0)
    
    # Ajouter une pénalité basée sur le poids
    weight_penalty = max(0, (weight - 5) // 2)
    
    return base_penalty + weight_penalty
