"""
Module pour la génération des armes
Contient les fonctions pour créer des armes dans le monde
"""

import uuid
import json
import logging
import random
from typing import List, Dict, Any

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.WeaponItems")

def generate_weapon_items(db, world_id: str, device_ids: List[str], 
                         building_ids: List[str], character_ids: List[str], 
                         num_items: int, random) -> List[str]:
    """
    Génère des armes pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre d'armes à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des armes générées
    """
    weapon_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table weapon_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='weapon_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table weapon_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE weapon_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                weapon_type TEXT NOT NULL,
                damage INTEGER DEFAULT 10,
                accuracy INTEGER DEFAULT 70,
                range INTEGER DEFAULT 10,
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
        logger.info("Table weapon_items créée")
    
    # Types d'armes
    weapon_types = {
        "MELEE": ["KNIFE", "SWORD", "AXE", "HAMMER", "CLUB", "STAFF", "KATANA", "MACHETE", "CHAINSAW"],
        "RANGED": ["PISTOL", "RIFLE", "SHOTGUN", "SMG", "SNIPER", "ASSAULT_RIFLE", "GRENADE_LAUNCHER", "ROCKET_LAUNCHER"],
        "ENERGY": ["LASER_PISTOL", "PLASMA_RIFLE", "ENERGY_CANNON", "PULSE_RIFLE", "ION_BLASTER", "TESLA_GUN"],
        "SMART": ["SMART_PISTOL", "SMART_RIFLE", "GUIDED_MISSILE", "DRONE_CONTROLLER", "NANOBLADE", "NEURAL_DISRUPTOR"],
        "EXOTIC": ["SONIC_EMITTER", "GRAVITY_GUN", "FREEZE_RAY", "ANTIMATTER_PROJECTOR", "QUANTUM_DISRUPTOR"]
    }
    
    # Composants de noms pour générer des noms réalistes
    prefixes = {
        "MELEE": ["Razor", "Blade", "Edge", "Slash", "Hack", "Crush", "Smash", "Slice", "Cleave", "Rend"],
        "RANGED": ["Thunder", "Storm", "Bullet", "Shot", "Trigger", "Barrel", "Hammer", "Recoil", "Scope", "Muzzle"],
        "ENERGY": ["Plasma", "Laser", "Pulse", "Ion", "Beam", "Flux", "Glow", "Charge", "Volt", "Photon"],
        "SMART": ["Neural", "Cyber", "Synth", "Logic", "Cortex", "Chip", "Link", "Net", "Code", "Data"],
        "EXOTIC": ["Void", "Chaos", "Quantum", "Warp", "Phase", "Rift", "Nexus", "Vortex", "Dimension", "Paradox"]
    }
    
    suffixes = {
        "MELEE": ["Blade", "Edge", "Cutter", "Slicer", "Chopper", "Smasher", "Crusher", "Ripper", "Cleaver", "Slasher"],
        "RANGED": ["Shot", "Blaster", "Cannon", "Shooter", "Gunner", "Sniper", "Hunter", "Marksman", "Ranger", "Gunslinger"],
        "ENERGY": ["Beam", "Ray", "Blaster", "Emitter", "Projector", "Cannon", "Discharger", "Generator", "Radiator", "Pulser"],
        "SMART": ["Brain", "Mind", "Cortex", "System", "Network", "Interface", "Protocol", "Algorithm", "Matrix", "Processor"],
        "EXOTIC": ["Disruptor", "Shifter", "Warper", "Bender", "Twister", "Distorter", "Manipulator", "Controller", "Bender", "Shaper"]
    }
    
    # Fabricants d'armes
    manufacturers = {
        "MELEE": ["BladeWorks", "EdgeForge", "SteelCraft", "IronWorks", "CarbonEdge"],
        "RANGED": ["GunTech", "BarrelIndustries", "TriggerCorp", "AmmoSystems", "RecoilArms"],
        "ENERGY": ["PlasmaCore", "LaserTech", "EnergyDynamics", "FluxSystems", "PhotonIndustries"],
        "SMART": ["NeuralWeapons", "CyberArms", "SynthTech", "LogicFire", "CortexSystems"],
        "EXOTIC": ["QuantumArms", "VoidTech", "ChaosSystems", "WarpIndustries", "RiftWeapons"]
    }
    
    # Raretés
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    rarity_weights = [40, 30, 20, 8, 2]
    
    # Types de dégâts
    damage_types = {
        "MELEE": ["PHYSICAL", "SLASHING", "BLUNT", "PIERCING"],
        "RANGED": ["PHYSICAL", "PIERCING", "EXPLOSIVE", "IMPACT"],
        "ENERGY": ["ENERGY", "THERMAL", "PLASMA", "ELECTRICAL", "RADIATION"],
        "SMART": ["PHYSICAL", "ENERGY", "NEURAL", "NANITE", "GUIDED"],
        "EXOTIC": ["SONIC", "GRAVITATIONAL", "TEMPORAL", "QUANTUM", "DIMENSIONAL"]
    }
    
    for i in range(num_items):
        # Générer un ID unique avec préfixe weapon_
        weapon_id = f"weapon_{uuid.uuid4()}"
        
        # Déterminer si on place cette arme dans un appareil, un bâtiment ou sur un personnage
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
        
        # Sélectionner une catégorie d'arme
        weapon_category = random.choice(list(weapon_types.keys()))
        
        # Sélectionner un type d'arme dans cette catégorie
        weapon_type = random.choice(weapon_types[weapon_category])
        
        # Générer un nom en fonction du type d'arme
        prefix = random.choice(prefixes[weapon_category])
        suffix = random.choice(suffixes[weapon_category])
        manufacturer = random.choice(manufacturers[weapon_category])
        
        # Version du produit
        model = f"Mk{random.randint(1, 9)}"
        
        # Nom complet
        name = f"{manufacturer} {prefix}-{suffix} {model}"
        
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
            "COMMON": 100,
            "UNCOMMON": 500,
            "RARE": 2000,
            "EPIC": 8000,
            "LEGENDARY": 25000
        }
        price_multiplier = 1 + (level * 0.2)
        price = int(price_base.get(rarity, 100) * price_multiplier)
        
        # Dégâts, précision et portée basés sur le type d'arme et la rareté
        damage_base = {
            "MELEE": 15,
            "RANGED": 10,
            "ENERGY": 12,
            "SMART": 8,
            "EXOTIC": 20
        }
        
        accuracy_base = {
            "MELEE": 90,  # Les armes de mêlée ont une précision élevée à courte portée
            "RANGED": 70,
            "ENERGY": 80,
            "SMART": 95,  # Les armes intelligentes ont une précision très élevée
            "EXOTIC": 60   # Les armes exotiques sont moins précises
        }
        
        range_base = {
            "MELEE": 2,    # Portée très courte pour les armes de mêlée
            "RANGED": 20,
            "ENERGY": 15,
            "SMART": 25,
            "EXOTIC": 10
        }
        
        # Multiplicateurs de rareté
        rarity_multiplier = {
            "COMMON": 1.0,
            "UNCOMMON": 1.3,
            "RARE": 1.7,
            "EPIC": 2.2,
            "LEGENDARY": 3.0
        }
        
        # Calculer les statistiques finales
        damage = int(damage_base.get(weapon_category, 10) * rarity_multiplier.get(rarity, 1.0))
        accuracy = min(100, int(accuracy_base.get(weapon_category, 70) * (1 + (rarity_multiplier.get(rarity, 1.0) - 1) * 0.5)))
        weapon_range = int(range_base.get(weapon_category, 10) * rarity_multiplier.get(rarity, 1.0))
        
        # Type de dégâts
        damage_type = random.choice(damage_types[weapon_category])
        
        # Effets spéciaux basés sur la rareté
        special_effects = _generate_special_effects(weapon_category, weapon_type, rarity, random)
        
        # Bonus de combat
        combat_bonus = _generate_combat_bonus(weapon_category, weapon_type, rarity, random)
        
        # Illégalité
        is_legal = 0 if (rarity in ["EPIC", "LEGENDARY"] and random.random() < 0.4) or weapon_category == "EXOTIC" else 1
        
        # Description
        description = _generate_description(weapon_category, weapon_type, rarity, name, manufacturer, special_effects, random)
        
        # Générer les métadonnées standardisées
        metadata = MetadataStandardizer.standardize_weapon_metadata(
            weapon_type=weapon_type,
            damage_type=damage_type,
            damage=damage,
            accuracy=accuracy,
            range=weapon_range,
            fire_rate=random.randint(1, 10),
            reload_time=random.randint(1, 5) if weapon_category in ["RANGED", "ENERGY", "SMART"] else 0,
            ammo_capacity=random.randint(5, 30) if weapon_category in ["RANGED", "ENERGY", "SMART"] else 0,
            ammo_type=_get_ammo_type(weapon_category, weapon_type) if weapon_category in ["RANGED", "ENERGY", "SMART"] else None,
            weight=random.randint(10, 100) / 10.0,  # en kg
            durability=random.randint(50, 100),
            special_effects=special_effects,
            combat_bonus=combat_bonus,
            required_level=level,
            manufacturer=manufacturer,
            model=model,
            is_two_handed=_is_two_handed(weapon_category, weapon_type)
        )
        
        # Convertir en JSON
        metadata_json = MetadataStandardizer.to_json(metadata)
        
        # Insérer l'arme dans la base de données
        cursor.execute("""
            INSERT INTO weapon_items (
                id, name, description, weapon_type, damage, accuracy, range,
                rarity, price, is_legal, world_id, location_type, 
                location_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            weapon_id, name, description, weapon_type, damage, accuracy, weapon_range,
            rarity, price, is_legal, world_id, location_type, 
            location_id, metadata_json
        ))
        
        weapon_ids.append(weapon_id)
    
    db.conn.commit()
    logger.info(f"{len(weapon_ids)} armes générées")
    
    return weapon_ids

def _generate_special_effects(weapon_category: str, weapon_type: str, rarity: str, random) -> List[str]:
    """
    Génère des effets spéciaux pour une arme en fonction de sa catégorie, son type et sa rareté
    
    Args:
        weapon_category: Catégorie d'arme
        weapon_type: Type d'arme
        rarity: Rareté de l'arme
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste d'effets spéciaux
    """
    # Effets spéciaux par catégorie d'arme
    effects_by_category = {
        "MELEE": [
            "Saignement",
            "Coup critique",
            "Étourdissement",
            "Désarmement",
            "Coup puissant",
            "Frappe rapide",
            "Coup tournoyant",
            "Pénétration d'armure",
            "Drain de vie",
            "Empoisonnement"
        ],
        "RANGED": [
            "Tir perforant",
            "Tir rapide",
            "Tir précis",
            "Tir explosif",
            "Tir en rafale",
            "Rechargement rapide",
            "Tir à longue portée",
            "Tir incendiaire",
            "Tir anti-armure",
            "Tir silencieux"
        ],
        "ENERGY": [
            "Surchauffe",
            "Décharge électrique",
            "Radiation résiduelle",
            "Surcharge d'énergie",
            "Tir à rebond",
            "Tir traversant",
            "Champ d'énergie",
            "Impulsion EMP",
            "Rayon continu",
            "Tir à dispersion"
        ],
        "SMART": [
            "Verrouillage de cible",
            "Tir guidé",
            "Analyse de faiblesse",
            "Contre-mesures électroniques",
            "Piratage d'implants",
            "Tir automatique",
            "Adaptation tactique",
            "Reconnaissance biométrique",
            "Tir de précision",
            "Neutralisation de défenses"
        ],
        "EXOTIC": [
            "Distorsion temporelle",
            "Manipulation gravitationnelle",
            "Déchirure dimensionnelle",
            "Altération quantique",
            "Onde sonique",
            "Gel moléculaire",
            "Téléportation de projectile",
            "Inversion de phase",
            "Désintégration",
            "Anomalie spatiale"
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
    available_effects = effects_by_category.get(weapon_category, [])
    
    if not available_effects:
        return []
    
    return random.sample(available_effects, min(num_effects, len(available_effects)))

def _generate_combat_bonus(weapon_category: str, weapon_type: str, rarity: str, random) -> Dict[str, Any]:
    """
    Génère des bonus de combat pour une arme en fonction de sa catégorie, son type et sa rareté
    
    Args:
        weapon_category: Catégorie d'arme
        weapon_type: Type d'arme
        rarity: Rareté de l'arme
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Dictionnaire de bonus de combat
    """
    # Bonus de combat par catégorie d'arme
    combat_bonuses = {
        "MELEE": {
            "critical_chance": (5, 20),
            "critical_damage": (10, 50),
            "attack_speed": (5, 20),
            "bleed_chance": (5, 25),
            "stun_chance": (5, 15)
        },
        "RANGED": {
            "headshot_damage": (10, 50),
            "reload_speed": (5, 25),
            "fire_rate": (5, 20),
            "armor_penetration": (5, 30),
            "stability": (5, 25)
        },
        "ENERGY": {
            "charge_speed": (5, 25),
            "heat_reduction": (5, 30),
            "energy_efficiency": (5, 25),
            "shield_damage": (10, 50),
            "aoe_damage": (5, 20)
        },
        "SMART": {
            "target_acquisition": (5, 30),
            "tracking_speed": (5, 25),
            "lock_duration": (5, 30),
            "multi_target": (1, 3),
            "hack_chance": (5, 25)
        },
        "EXOTIC": {
            "effect_duration": (5, 30),
            "cooldown_reduction": (5, 25),
            "area_of_effect": (5, 30),
            "status_chance": (5, 25),
            "reality_distortion": (5, 20)
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
        "EPIC": 3,
        "LEGENDARY": 4
    }.get(rarity, 0)
    
    result = {}
    
    if num_bonuses == 0:
        return result
    
    # Sélectionner des bonus aléatoires
    available_bonuses = combat_bonuses.get(weapon_category, {})
    
    if not available_bonuses:
        return result
    
    selected_bonuses = random.sample(list(available_bonuses.keys()), 
                                    min(num_bonuses, len(available_bonuses)))
    
    for bonus in selected_bonuses:
        min_val, max_val = available_bonuses[bonus]
        value = random.randint(min_val, max_val)
        result[bonus] = int(value * multiplier)
    
    return result

def _generate_description(weapon_category: str, weapon_type: str, rarity: str, name: str, 
                         manufacturer: str, special_effects: List[str], random) -> str:
    """
    Génère une description pour une arme
    
    Args:
        weapon_category: Catégorie d'arme
        weapon_type: Type d'arme
        rarity: Rareté de l'arme
        name: Nom de l'arme
        manufacturer: Fabricant de l'arme
        special_effects: Effets spéciaux de l'arme
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Description de l'arme
    """
    # Descriptions de base par catégorie d'arme
    base_descriptions = {
        "MELEE": [
            "Une arme de corps à corps redoutable conçue pour infliger des dégâts maximaux à courte portée.",
            "Cette arme de mêlée allie puissance et précision pour des combats rapprochés.",
            "Un chef-d'œuvre d'artisanat conçu pour exceller dans les combats au corps à corps."
        ],
        "RANGED": [
            "Une arme à distance fiable offrant un bon équilibre entre puissance et précision.",
            "Cette arme à feu combine technologie moderne et design ergonomique pour une efficacité maximale.",
            "Une arme à distance conçue pour offrir des performances optimales sur le champ de bataille."
        ],
        "ENERGY": [
            "Une arme à énergie avancée utilisant les dernières technologies pour des dégâts dévastateurs.",
            "Ce système d'armement à énergie transforme la puissance brute en destruction ciblée.",
            "Une merveille technologique qui canalise l'énergie pure en un instrument de combat mortel."
        ],
        "SMART": [
            "Une arme intelligente équipée de systèmes de ciblage avancés pour une précision inégalée.",
            "Ce chef-d'œuvre de technologie intègre des systèmes d'IA pour optimiser chaque tir.",
            "Une arme de nouvelle génération qui utilise des algorithmes complexes pour maximiser l'efficacité au combat."
        ],
        "EXOTIC": [
            "Une arme expérimentale utilisant des technologies au-delà de la compréhension commune.",
            "Ce dispositif d'armement manipule les lois fondamentales de la physique pour des effets dévastateurs.",
            "Une arme unique exploitant des phénomènes exotiques pour créer des effets de combat sans précédent."
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
    base_desc = random.choice(base_descriptions.get(weapon_category, 
                                                  ["Une arme puissante conçue pour l'efficacité au combat."]))
    
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
        f"Le {name} représente l'avenir de la technologie d'armement.",
        f"Faites passer vos capacités de combat au niveau supérieur avec le {name}.",
        f"Conçu pour ceux qui exigent le meilleur en matière d'armement.",
        f"La fusion parfaite entre puissance et précision.",
        f"Redéfinissez votre approche du combat avec cette arme de pointe."
    ]
    
    description += f" {random.choice(marketing_notes)}"
    
    return description

def _get_ammo_type(weapon_category: str, weapon_type: str) -> str:
    """
    Détermine le type de munitions pour une arme
    
    Args:
        weapon_category: Catégorie d'arme
        weapon_type: Type d'arme
        
    Returns:
        Type de munitions
    """
    ammo_types = {
        "RANGED": {
            "PISTOL": "9MM",
            "RIFLE": "5.56MM",
            "SHOTGUN": "12GAUGE",
            "SMG": "9MM",
            "SNIPER": "7.62MM",
            "ASSAULT_RIFLE": "5.56MM",
            "GRENADE_LAUNCHER": "40MM",
            "ROCKET_LAUNCHER": "ROCKET"
        },
        "ENERGY": {
            "LASER_PISTOL": "ENERGY_CELL",
            "PLASMA_RIFLE": "PLASMA_CARTRIDGE",
            "ENERGY_CANNON": "ENERGY_CORE",
            "PULSE_RIFLE": "PULSE_CELL",
            "ION_BLASTER": "ION_CELL",
            "TESLA_GUN": "TESLA_COIL"
        },
        "SMART": {
            "SMART_PISTOL": "SMART_ROUNDS",
            "SMART_RIFLE": "SMART_ROUNDS",
            "GUIDED_MISSILE": "GUIDED_ROCKET",
            "DRONE_CONTROLLER": "MICRO_DRONE",
            "NANOBLADE": "NANITE_CARTRIDGE",
            "NEURAL_DISRUPTOR": "NEURAL_CHARGE"
        }
    }
    
    return ammo_types.get(weapon_category, {}).get(weapon_type, "STANDARD")

def _is_two_handed(weapon_category: str, weapon_type: str) -> bool:
    """
    Détermine si une arme est à deux mains
    
    Args:
        weapon_category: Catégorie d'arme
        weapon_type: Type d'arme
        
    Returns:
        True si l'arme est à deux mains, False sinon
    """
    two_handed_types = {
        "MELEE": ["SWORD", "AXE", "HAMMER", "CLUB", "STAFF", "KATANA", "MACHETE", "CHAINSAW"],
        "RANGED": ["RIFLE", "SHOTGUN", "SNIPER", "ASSAULT_RIFLE", "GRENADE_LAUNCHER", "ROCKET_LAUNCHER"],
        "ENERGY": ["PLASMA_RIFLE", "ENERGY_CANNON", "PULSE_RIFLE"],
        "SMART": ["SMART_RIFLE", "GUIDED_MISSILE", "DRONE_CONTROLLER"],
        "EXOTIC": ["GRAVITY_GUN", "ANTIMATTER_PROJECTOR", "QUANTUM_DISRUPTOR"]
    }
    
    return weapon_type in two_handed_types.get(weapon_category, [])
