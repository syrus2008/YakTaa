"""
Module pour la génération des implants cybernétiques
Contient les fonctions pour créer des implants dans le monde
"""

import uuid
import json
import logging
import random
from typing import List, Dict, Any

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ImplantItems")

def generate_implant_items(db, world_id: str, device_ids: List[str], 
                          building_ids: List[str], character_ids: List[str], 
                          num_items: int, random) -> List[str]:
    """
    Génère des implants cybernétiques pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre d'implants à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des implants générés
    """
    implant_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table implant_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='implant_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table implant_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE implant_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                implant_type TEXT NOT NULL,
                body_location TEXT,
                surgery_difficulty INTEGER,
                side_effects TEXT,
                compatibility TEXT,
                rarity TEXT DEFAULT 'Commun',
                price INTEGER DEFAULT 0,
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
        logger.info("Table implant_items créée")
    
    # Types d'implants
    implant_types = ["NEURAL", "OPTICAL", "SKELETAL", "DERMAL", "CIRCULATORY"]
    
    # Composants de noms pour générer des noms réalistes
    prefixes = ["Neuro", "Cyber", "Bio", "Synth", "Quantum", "Nano", "Hyper", "Mecha", "Tech", "Pulse"]
    mid_parts = ["Link", "Core", "Mesh", "Net", "Wave", "Sync", "Flex", "Boost", "Sense", "Guard"]
    suffixes = ["X", "Pro", "Elite", "Plus", "Max", "Alpha", "Prime", "Ultra", "Omega", "Zero"]
    
    # Fabricants d'implants
    manufacturers = ["NeuraTech", "CyberSystems", "BioForge", "SynthCorp", "QuantumWare", 
                    "NanoMedics", "HyperLogic", "MechaLife", "TechFusion", "PulseGen"]
    
    # Raretés
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    rarity_weights = [40, 30, 20, 8, 2]
    
    for i in range(num_items):
        # Générer un ID unique avec préfixe implant_
        implant_id = f"implant_{uuid.uuid4()}"
        
        # Déterminer si on place cet implant dans un appareil, un bâtiment ou sur un personnage
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
        
        # Sélectionner un type d'implant
        implant_type = random.choice(implant_types)
        
        # Générer un nom en fonction du type d'implant
        prefix = random.choice(prefixes)
        mid_part = random.choice(mid_parts)
        suffix = random.choice(suffixes)
        manufacturer = random.choice(manufacturers)
        
        # Version du produit
        version = f"v{random.randint(1, 9)}.{random.randint(0, 9)}"
        
        # Nom complet
        name = f"{manufacturer} {prefix}{mid_part} {implant_type} {suffix} {version}"
        
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
        
        # Coût en humanité basé sur le type et la rareté
        humanity_base = {
            "NEURAL": 8,
            "OPTICAL": 6,
            "SKELETAL": 10,
            "DERMAL": 4,
            "CIRCULATORY": 7
        }
        humanity_multiplier = {
            "COMMON": 0.8,
            "UNCOMMON": 1.0,
            "RARE": 1.2,
            "EPIC": 1.5,
            "LEGENDARY": 2.0
        }
        humanity_cost = int(humanity_base.get(implant_type, 5) * humanity_multiplier.get(rarity, 1.0))
        
        # Difficulté d'installation
        surgery_difficulty = {
            "NEURAL": random.randint(6, 10),
            "OPTICAL": random.randint(4, 8),
            "SKELETAL": random.randint(5, 9),
            "DERMAL": random.randint(2, 6),
            "CIRCULATORY": random.randint(5, 9)
        }.get(implant_type, random.randint(3, 7))
        
        # Bonus de statistiques
        stats_bonus = _generate_stats_bonus(implant_type, rarity, random)
        
        # Effets spéciaux
        special_effects = _generate_special_effects(implant_type, rarity, random)
        
        # Bonus de combat
        combat_bonus = _generate_combat_bonus(implant_type, rarity, random)
        
        # Illégalité
        is_legal = 0 if rarity in ["EPIC", "LEGENDARY"] and random.random() < 0.4 else 1
        
        # Description
        description = _generate_description(implant_type, rarity, name, manufacturer, special_effects, random)
        
        # Icône
        icon = f"implant_{implant_type.lower()}"
        
        # Emplacement sur le corps
        body_location = implant_type.lower()
        
        # Compatibilité
        compatibility = json.dumps(["HUMAN", "CYBORG"])
        
        # Effets secondaires
        side_effects = json.dumps(_generate_side_effects(implant_type, rarity, random))
        
        # Générer les métadonnées standardisées
        metadata = MetadataStandardizer.standardize_implant_metadata(
            implant_type=implant_type,
            stats_bonus=stats_bonus,
            humanity_cost=humanity_cost,
            surgery_difficulty=surgery_difficulty,
            side_effects=special_effects,
            compatibility=["HUMAN", "CYBORG"],
            special_abilities=special_effects,
            power_consumption=random.randint(1, 5),
            combat_bonus=combat_bonus
        )
        
        # Convertir en JSON
        metadata_json = MetadataStandardizer.to_json(metadata)
        
        # Insérer l'implant dans la base de données
        cursor.execute("""
            INSERT INTO implant_items (
                id, name, description, implant_type, body_location,
                surgery_difficulty, side_effects, compatibility,
                rarity, price, is_legal, world_id, location_type, 
                location_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            implant_id, name, description, implant_type, body_location,
            surgery_difficulty, side_effects, compatibility,
            rarity, price, is_legal, world_id, location_type, 
            location_id, metadata_json
        ))
        
        implant_ids.append(implant_id)
    
    db.conn.commit()
    logger.info(f"{len(implant_ids)} implants générés")
    
    return implant_ids

def _generate_stats_bonus(implant_type: str, rarity: str, random) -> Dict[str, int]:
    """
    Génère des bonus de statistiques pour un implant en fonction de son type et de sa rareté
    
    Args:
        implant_type: Type d'implant
        rarity: Rareté de l'implant
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Dictionnaire de bonus de statistiques
    """
    # Statistiques de base
    stats = ["STRENGTH", "AGILITY", "INTELLIGENCE", "PERCEPTION", "CHARISMA"]
    
    # Statistiques principales par type d'implant
    primary_stats = {
        "NEURAL": ["INTELLIGENCE", "PERCEPTION"],
        "OPTICAL": ["PERCEPTION"],
        "SKELETAL": ["STRENGTH", "AGILITY"],
        "DERMAL": ["STRENGTH"],
        "CIRCULATORY": ["AGILITY", "STRENGTH"]
    }
    
    # Nombre de bonus en fonction de la rareté
    num_bonuses = {
        "COMMON": 1,
        "UNCOMMON": 2,
        "RARE": 3,
        "EPIC": 4,
        "LEGENDARY": 5
    }.get(rarity, 1)
    
    # Valeur maximale des bonus en fonction de la rareté
    max_bonus = {
        "COMMON": 1,
        "UNCOMMON": 2,
        "RARE": 3,
        "EPIC": 4,
        "LEGENDARY": 5
    }.get(rarity, 1)
    
    # Initialiser les bonus
    stats_bonus = {}
    
    # Ajouter des bonus aux statistiques principales
    primary = primary_stats.get(implant_type, [random.choice(stats)])
    for stat in primary:
        if len(stats_bonus) < num_bonuses:
            stats_bonus[stat] = random.randint(1, max_bonus)
    
    # Compléter avec des statistiques aléatoires si nécessaire
    remaining_stats = [s for s in stats if s not in stats_bonus]
    while len(stats_bonus) < num_bonuses and remaining_stats:
        stat = random.choice(remaining_stats)
        remaining_stats.remove(stat)
        stats_bonus[stat] = random.randint(1, max(1, max_bonus - 1))
    
    return stats_bonus

def _generate_special_effects(implant_type: str, rarity: str, random) -> List[str]:
    """
    Génère des effets spéciaux pour un implant en fonction de son type et de sa rareté
    
    Args:
        implant_type: Type d'implant
        rarity: Rareté de l'implant
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste d'effets spéciaux
    """
    # Effets spéciaux par type d'implant
    effects_by_type = {
        "NEURAL": [
            "Accès direct à la matrice",
            "Interface neurale améliorée",
            "Mémoire photographique",
            "Traitement de données accéléré",
            "Analyse prédictive",
            "Connexion sans fil aux réseaux",
            "Traduction instantanée",
            "Calcul avancé",
            "Résistance aux intrusions mentales",
            "Apprentissage accéléré"
        ],
        "OPTICAL": [
            "Vision nocturne",
            "Zoom optique",
            "Analyse spectrale",
            "Détection thermique",
            "Réalité augmentée",
            "Enregistrement visuel",
            "Reconnaissance faciale",
            "Scanner de vulnérabilités",
            "Vision à rayons X",
            "Détection de mensonges"
        ],
        "SKELETAL": [
            "Force augmentée",
            "Réflexes améliorés",
            "Résistance aux dégâts",
            "Absorption des chocs",
            "Saut amplifié",
            "Stabilisation du tir",
            "Endurance accrue",
            "Articulations renforcées",
            "Vitesse de course augmentée",
            "Résistance aux toxines"
        ],
        "DERMAL": [
            "Armure sous-cutanée",
            "Thermorégulation",
            "Camouflage actif",
            "Résistance électrique",
            "Auto-réparation",
            "Absorption d'énergie",
            "Filtration des toxines",
            "Interface tactile",
            "Résistance au feu",
            "Conductivité améliorée"
        ],
        "CIRCULATORY": [
            "Oxygénation améliorée",
            "Coagulation rapide",
            "Filtration des toxines",
            "Adrénaline synthétique",
            "Régulation thermique",
            "Immunité renforcée",
            "Récupération accélérée",
            "Distribution de nanobots",
            "Résistance à la fatigue",
            "Adaptation environnementale"
        ]
    }
    
    # Nombre d'effets en fonction de la rareté
    num_effects = {
        "COMMON": 1,
        "UNCOMMON": 1,
        "RARE": 2,
        "EPIC": 3,
        "LEGENDARY": 4
    }.get(rarity, 1)
    
    # Sélectionner des effets aléatoires
    available_effects = effects_by_type.get(implant_type, [])
    
    if not available_effects:
        return []
    
    return random.sample(available_effects, min(num_effects, len(available_effects)))

def _generate_combat_bonus(implant_type: str, rarity: str, random) -> Dict[str, Any]:
    """
    Génère des bonus de combat pour un implant en fonction de son type et de sa rareté
    
    Args:
        implant_type: Type d'implant
        rarity: Rareté de l'implant
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Dictionnaire de bonus de combat
    """
    # Bonus de combat par type d'implant
    combat_bonuses = {
        "NEURAL": {
            "aim_assist": (0, 15),
            "hack_speed": (5, 30),
            "reaction_time": (5, 25)
        },
        "OPTICAL": {
            "critical_chance": (1, 10),
            "accuracy": (5, 20),
            "target_acquisition": (5, 25)
        },
        "SKELETAL": {
            "melee_damage": (5, 25),
            "reload_speed": (5, 20),
            "movement_speed": (5, 15)
        },
        "DERMAL": {
            "damage_reduction": (2, 15),
            "energy_resistance": (5, 20),
            "physical_resistance": (5, 20)
        },
        "CIRCULATORY": {
            "health_regen": (1, 10),
            "stamina": (10, 30),
            "bleed_resistance": (10, 50)
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
    
    # Sélectionner des bonus aléatoires
    available_bonuses = combat_bonuses.get(implant_type, {})
    num_bonuses = {
        "COMMON": 1,
        "UNCOMMON": 1,
        "RARE": 2,
        "EPIC": 2,
        "LEGENDARY": 3
    }.get(rarity, 1)
    
    result = {}
    
    if not available_bonuses:
        return result
    
    # Sélectionner des bonus aléatoires
    selected_bonuses = random.sample(list(available_bonuses.keys()), 
                                    min(num_bonuses, len(available_bonuses)))
    
    for bonus in selected_bonuses:
        min_val, max_val = available_bonuses[bonus]
        value = random.randint(min_val, max_val)
        result[bonus] = int(value * multiplier)
    
    return result

def _generate_description(implant_type: str, rarity: str, name: str, manufacturer: str, 
                         special_effects: List[str], random) -> str:
    """
    Génère une description pour un implant
    
    Args:
        implant_type: Type d'implant
        rarity: Rareté de l'implant
        name: Nom de l'implant
        manufacturer: Fabricant de l'implant
        special_effects: Effets spéciaux de l'implant
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Description de l'implant
    """
    # Descriptions de base par type d'implant
    base_descriptions = {
        "NEURAL": [
            "Un implant neural de pointe qui améliore les capacités cognitives.",
            "Cet implant se connecte directement au cortex cérébral pour augmenter les performances mentales.",
            "Une interface neurale qui optimise le traitement de l'information et la prise de décision."
        ],
        "OPTICAL": [
            "Un implant oculaire avancé qui améliore considérablement la vision.",
            "Ces lentilles cybernétiques offrent des capacités visuelles surhumaines.",
            "Un système optique intégré qui transforme la façon dont vous percevez le monde."
        ],
        "SKELETAL": [
            "Un renforcement du squelette qui augmente la force et l'endurance.",
            "Ces implants osseux en alliage de titane offrent une résistance exceptionnelle.",
            "Un système d'amélioration musculo-squelettique pour des performances physiques accrues."
        ],
        "DERMAL": [
            "Un implant sous-cutané qui renforce la peau et offre une protection supplémentaire.",
            "Cette armure dermique intégrée réduit les dommages physiques.",
            "Un système de défense épidermique qui transforme votre peau en une barrière protectrice."
        ],
        "CIRCULATORY": [
            "Un implant qui optimise la circulation sanguine et les fonctions cardiovasculaires.",
            "Ce système circulatoire amélioré augmente l'endurance et la récupération.",
            "Une amélioration du système sanguin qui filtre les toxines et améliore l'oxygénation."
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
    base_desc = random.choice(base_descriptions.get(implant_type, 
                                                  ["Un implant cybernétique de haute technologie."]))
    
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
        f"Le {name} représente l'avenir de l'augmentation humaine.",
        f"Faites passer vos capacités au niveau supérieur avec le {name}.",
        f"Conçu pour ceux qui ne se contentent pas de l'ordinaire.",
        f"La fusion parfaite entre technologie et biologie humaine.",
        f"Redéfinissez vos limites avec cette technologie de pointe."
    ]
    
    description += f" {random.choice(marketing_notes)}"
    
    return description

def _generate_side_effects(implant_type: str, rarity: str, random) -> List[str]:
    """
    Génère des effets secondaires pour un implant
    
    Args:
        implant_type: Type d'implant
        rarity: Rareté de l'implant
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste d'effets secondaires
    """
    # Effets secondaires par type d'implant
    side_effects = {
        "NEURAL": [
            "Migraines occasionnelles",
            "Troubles du sommeil",
            "Flashs de mémoire aléatoires",
            "Sensibilité aux interférences électromagnétiques",
            "Rêves lucides incontrôlables"
        ],
        "OPTICAL": [
            "Vision floue temporaire",
            "Sensibilité à la lumière",
            "Hallucinations visuelles mineures",
            "Fatigue oculaire",
            "Distorsion des couleurs"
        ],
        "SKELETAL": [
            "Douleurs articulaires",
            "Raideur musculaire",
            "Cliquetis audibles lors des mouvements",
            "Sensibilité aux changements de température",
            "Crampes occasionnelles"
        ],
        "DERMAL": [
            "Décoloration de la peau",
            "Sensibilité tactile réduite",
            "Transpiration excessive",
            "Réactions allergiques",
            "Cicatrisation lente"
        ],
        "CIRCULATORY": [
            "Fluctuations de la pression artérielle",
            "Sensation de chaleur",
            "Palpitations cardiaques",
            "Soif excessive",
            "Sensibilité aux stimulants"
        ]
    }
    
    # Probabilité d'avoir des effets secondaires en fonction de la rareté
    probability = {
        "COMMON": 0.8,
        "UNCOMMON": 0.6,
        "RARE": 0.4,
        "EPIC": 0.3,
        "LEGENDARY": 0.2
    }.get(rarity, 0.5)
    
    # Nombre maximum d'effets secondaires en fonction de la rareté
    max_effects = {
        "COMMON": 3,
        "UNCOMMON": 2,
        "RARE": 2,
        "EPIC": 1,
        "LEGENDARY": 1
    }.get(rarity, 2)
    
    # Déterminer si l'implant a des effets secondaires
    if random.random() > probability:
        return []
    
    # Sélectionner des effets secondaires aléatoires
    available_effects = side_effects.get(implant_type, [])
    
    if not available_effects:
        return []
    
    num_effects = random.randint(1, min(max_effects, len(available_effects)))
    return random.sample(available_effects, num_effects)
