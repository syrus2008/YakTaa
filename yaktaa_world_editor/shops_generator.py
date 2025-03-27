"""
Module pour la génération des boutiques
Contient les fonctions pour créer des boutiques et leur inventaire
"""

import uuid
import json
import logging
import random
from typing import List

from database import get_database
from constants import SHOP_TYPES, SHOP_NAME_PREFIXES, SHOP_NAME_SUFFIXES, SHOP_BRANDS

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Shops")

def generate_shops(db, world_id: str, location_ids: List[str], building_ids: List[str], num_shops: int, random, shop_types=None, shop_complexity=3) -> List[str]:
    """
    Génère des boutiques pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        building_ids: Liste des IDs des bâtiments
        num_shops: Nombre de boutiques à générer
        random: Instance de random pour la génération aléatoire
        shop_types: Liste des types de boutiques à générer (si None, tous les types)
        shop_complexity: Niveau de complexité des boutiques (1-5)
        
    Returns:
        Liste des IDs des boutiques générées
    """
    shop_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table des boutiques existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id TEXT PRIMARY KEY,
            world_id TEXT,
            name TEXT,
            description TEXT,
            shop_type TEXT,
            location_id TEXT,
            building_id TEXT,
            owner_id TEXT DEFAULT NULL,
            faction_id TEXT DEFAULT NULL,
            reputation INTEGER DEFAULT 5,
            price_modifier REAL DEFAULT 1.0,
            is_legal INTEGER DEFAULT 1,
            special_items TEXT DEFAULT NULL,
            metadata TEXT DEFAULT NULL,
            FOREIGN KEY (world_id) REFERENCES worlds(id),
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (building_id) REFERENCES buildings(id),
            FOREIGN KEY (owner_id) REFERENCES characters(id),
            FOREIGN KEY (faction_id) REFERENCES factions(id)
        )
    ''')
    
    # Vérifier si la table d'inventaire des boutiques existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_inventory (
            id TEXT PRIMARY KEY,
            shop_id TEXT,
            item_type TEXT,
            item_id TEXT,
            quantity INTEGER DEFAULT 1,
            price REAL,
            price_modifier REAL DEFAULT 1.0,
            is_featured INTEGER DEFAULT 0,
            is_limited_time INTEGER DEFAULT 0,
            expiry_date TEXT DEFAULT NULL,
            metadata TEXT DEFAULT NULL,
            added_at TEXT,
            FOREIGN KEY (shop_id) REFERENCES shops(id)
        )
    ''')
    
    # Si aucun lieu ou bâtiment n'est disponible, impossible de créer des boutiques
    if not location_ids or not building_ids:
        logger.warning("Impossible de générer des boutiques: aucun lieu ou bâtiment disponible")
        return shop_ids
    
    # Utiliser les types de boutiques spécifiés ou tous les types
    available_shop_types = shop_types if shop_types else SHOP_TYPES
    
    # Générer les boutiques
    for i in range(num_shops):
        shop_id = str(uuid.uuid4())
        
        # Sélectionner un lieu et un bâtiment aléatoire
        location_id = random.choice(location_ids)
        building_id = random.choice(building_ids)
        
        # Sélectionner un type de boutique aléatoire parmi ceux disponibles
        shop_type = random.choice(available_shop_types)
        
        # Déterminer si la boutique est légale en fonction du type
        is_legal = True
        if shop_type in ["WEAPON", "IMPLANT", "SOFTWARE"]:
            # Plus le niveau de complexité est élevé, plus il y a de chances d'avoir des magasins illégaux
            illegal_chance = 0.1 + (shop_complexity * 0.05)  # 15% à 35% selon la complexité
            is_legal = random.random() > illegal_chance
        elif shop_type == "BLACK_MARKET":
            is_legal = False  # Les marchés noirs sont toujours illégaux
        
        # Générer un nom pour la boutique
        shop_name = generate_shop_name(shop_type, random)
        
        # Générer une description pour la boutique
        description = generate_shop_description(shop_type, is_legal, random)
        
        # Générer des métadonnées pour la boutique
        metadata = {
            "founding_date": f"20{random.randint(30, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "popularity": random.randint(1, 10),
            "cleanliness": random.randint(1, 10),
            "security_level": random.randint(1, 10),
            "specialization": generate_shop_specialization(shop_type, random)
        }
        
        # Insérer la boutique dans la base de données
        cursor.execute('''
        INSERT INTO shops (
            id, world_id, name, description, shop_type, location_id, building_id,
            reputation, price_modifier, is_legal, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            shop_id, world_id, shop_name, description, shop_type, location_id, building_id,
            random.randint(1, 10),  # reputation
            random.uniform(0.8, 1.5),  # price_modifier
            1 if is_legal else 0,
            json.dumps(metadata)
        ))
        
        shop_ids.append(shop_id)
        
    db.conn.commit()
    logger.info(f"Généré {len(shop_ids)} boutiques pour le monde {world_id}")
    
    return shop_ids

def generate_shop_specialization(shop_type, random):
    """Génère une spécialisation pour la boutique en fonction de son type"""
    specializations = {
        "WEAPON": ["Armes de poing", "Fusils d'assaut", "Armes de précision", "Armes de mêlée", "Armes énergétiques", "Munitions spéciales", "Armes lourdes", "Armes non létales"],
        "IMPLANT": ["Implants cérébraux", "Implants oculaires", "Implants dermiques", "Implants musculaires", "Implants osseux", "Implants nerveux", "Implants cardiaques", "Implants expérimentaux"],
        "HARDWARE": ["Ordinateurs", "Périphériques", "Composants", "Réseaux", "Drones", "Robotique", "Électronique embarquée", "Matériel de surveillance"],
        "SOFTWARE": ["Systèmes d'exploitation", "Sécurité", "Productivité", "Multimédia", "Jeux", "Développement", "IA", "Hacking"],
        "CLOTHING": ["Vêtements urbains", "Vêtements tactiques", "Vêtements de luxe", "Vêtements de protection", "Accessoires", "Vêtements intelligents", "Vêtements rétro", "Haute couture"],
        "FOOD": ["Nourriture synthétique", "Cuisine traditionnelle", "Stimulants", "Boissons", "Nourriture exotique", "Compléments alimentaires", "Street food", "Épicerie fine"],
        "GENERAL": ["Articles divers", "Équipement de survie", "Électronique grand public", "Articles ménagers", "Fournitures", "Objets de collection", "Gadgets", "Nécessités quotidiennes"],
        "BLACK_MARKET": ["Marchandises volées", "Contrebande", "Implants illégaux", "Armes interdites", "Logiciels pirates", "Substances contrôlées", "Identités falsifiées", "Organes"]
    }
    
    return random.choice(specializations.get(shop_type, ["Divers"]))

def generate_shop_name(shop_type, random):
    if random.random() < 0.3:  # 30% de chance d'utiliser une marque existante
        brand = random.choice(SHOP_BRANDS)
        if random.random() < 0.5:  # 50% de chance d'ajouter un suffixe au nom de la marque
            suffix = random.choice(SHOP_NAME_SUFFIXES)
            return f"{brand} {suffix}"
        return brand
    
    # Sinon, générer un nom unique
    prefix = random.choice(SHOP_NAME_PREFIXES)
    suffix = random.choice(SHOP_NAME_SUFFIXES)
    
    # Parfois ajouter un élément lié au type de boutique
    if random.random() < 0.7:  # 70% de chance
        type_words = {
            "hardware": ["Gear", "Hardware", "Components", "Parts"],
            "software": ["Code", "Programs", "Apps", "Software"],
            "black_market": ["Shadow", "Underground", "Smuggler", "Dark"],
            "consumables": ["Snack", "Refresh", "Boost", "Supply"],
            "weapons": ["Arms", "Arsenal", "Defense", "Combat"],
            "implants": ["Implant", "Augment", "Enhance", "Bio"],
            "general": ["General", "Goods", "Supply", "Stuff"],
            "electronics": ["Circuit", "Gadget", "Device", "Tech"],
            "digital_services": ["Service", "Virtual", "Cloud", "Digital"],
            "datachips": ["Data", "Memory", "Storage", "Chip"],
            "cybernetics": ["Cyber", "Enhancement", "Augment", "Neural"]
        }
        
        type_word = random.choice(type_words.get(shop_type, ["Tech"]))
        
        # Format aléatoire du nom
        formats = [
            f"{prefix}{type_word} {suffix}",  # Ex: CyberGear Shop
            f"{prefix} {type_word} {suffix}",  # Ex: Cyber Gear Shop
            f"{type_word} {suffix}",  # Ex: Gear Shop
            f"{prefix} {suffix}"  # Ex: Cyber Shop
        ]
        
        return random.choice(formats)
    
    return f"{prefix} {suffix}"  # Ex: Cyber Shop

def generate_shop_description(shop_type, is_legal, random):
    descriptions = {
        "hardware": [
            "Une boutique spécialisée dans les composants informatiques et équipements électroniques.",
            "Vend des pièces détachées pour ordinateurs et autres appareils électroniques.",
            "Le paradis des bricoleurs à la recherche de composants tech."
        ],
        "software": [
            "Propose des logiciels pour tous les systèmes d'exploitation courants et personnalisés.",
            "Spécialiste en programmes de sécurité, utilitaires et logiciels de productivité.",
            "Applications, jeux et systèmes d'exploitation à la pointe de la technologie."
        ],
        "black_market": [
            "Un marché clandestin proposant des articles difficiles à trouver par les voies légales.",
            "Commerce d'articles illégaux ou non traçables. Entrée discrète conseillée.",
            "Lieu d'échange pour ceux qui préfèrent rester dans l'ombre du système."
        ],
        "consumables": [
            "Vend des boosts, stimulants et autres consommables pour améliorer vos performances.",
            "Produits consommables pour restaurer la santé, l'énergie et les capacités cognitives.",
            "Supplements, boosters, et snacks tech pour tous vos besoins quotidiens."
        ],
        "weapons": [
            "Arsenal d'armes conventionnelles et high-tech pour la défense personnelle.",
            "Spécialiste en équipement de combat et de défense pour tous les budgets.",
            "Armement de pointe pour ceux qui veulent rester en sécurité dans un monde dangereux."
        ],
        "implants": [
            "Boutique d'implants cybernétiques pour améliorer les capacités humaines.",
            "Augmentations corporelles et implants nouvelle génération.",
            "Technologies d'amélioration humaine, des basiques aux plus avancées."
        ],
        "general": [
            "Propose une variété de produits tech et non-tech pour tous les jours.",
            "Un peu de tout, de l'équipement électronique aux articles ménagers.",
            "Fournitures générales et articles divers pour tous vos besoins."
        ]
    }
    
    # Utiliser une description par défaut si le type n'a pas de descriptions spécifiques
    shop_description = random.choice(descriptions.get(shop_type, [
        "Une boutique vendant divers produits technologiques.",
        "Un magasin proposant des articles spécialisés.",
        "Un commerce local avec une sélection de produits variés."
    ]))
    
    if not is_legal:
        shop_description += " (Attention: boutique illégale)"
    
    return shop_description