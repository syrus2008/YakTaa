#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de gestion des boutiques pour YakTaa

Contient les classes et fonctions pour représenter et gérer les boutiques
et leurs articles dans le jeu, avec une esthétique cyberpunk.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any, Tuple, Union
from enum import Enum, auto

# Configuration du logger
logger = logging.getLogger(__name__)

class ShopType(Enum):
    """Types de boutiques disponibles dans le jeu"""
    TECH = auto()          # Équipements technologiques, hardware, logiciels
    WEAPONS = auto()        # Armes, munitions
    CLOTHING = auto()       # Vêtements, armures, équipements corporels
    IMPLANTS = auto()       # Implants cybernétiques
    DRUGS = auto()          # Médicaments, drogues de rue
    FOOD = auto()           # Nourriture, boissons
    GENERAL = auto()        # Articles divers
    BLACK_MARKET = auto()   # Marché noir, articles illégaux
    HACKING = auto()        # Outils de hacking, logiciels spécialisés
    SERVICES = auto()       # Services divers (médical, réparation)

class ItemCategory(Enum):
    """Catégories d'articles disponibles dans les boutiques"""
    WEAPON = auto()        # Armes
    ARMOR = auto()         # Armures et protection
    TOOL = auto()          # Outils divers
    CONSUMABLE = auto()    # Objets consommables
    SOFTWARE = auto()      # Logiciels
    HARDWARE = auto()      # Matériel informatique
    IMPLANT = auto()       # Implants cybernétiques
    CLOTHING = auto()      # Vêtements
    DRUG = auto()          # Drogues et médicaments
    MISC = auto()          # Divers

class Shop:
    """Représente une boutique dans le jeu YakTaa"""
    
    def __init__(self, shop_id: str = None, name: str = "", shop_type: ShopType = ShopType.GENERAL, 
                 city_id: str = "", description: str = "", owner: str = ""):
        """
        Initialise une nouvelle boutique
        
        Args:
            shop_id: Identifiant unique de la boutique (généré automatiquement si non fourni)
            name: Nom de la boutique
            shop_type: Type de boutique
            city_id: Identifiant de la ville où se trouve la boutique
            description: Description de la boutique
            owner: Nom du propriétaire de la boutique
        """
        self.shop_id = shop_id or f"shop_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.shop_type = shop_type
        self.city_id = city_id
        self.description = description
        self.owner = owner
        self.inventory = []
        self.markup_factor = 1.0  # Facteur de majoration des prix (1.0 = prix standard)
        self.discount_factor = 0.5  # Facteur de réduction à l'achat d'articles des joueurs
        
        logger.debug(f"Nouvelle boutique créée: {self.name} (ID: {self.shop_id})")
    
    def add_item(self, item) -> bool:
        """
        Ajoute un article à l'inventaire de la boutique
        
        Args:
            item: L'article à ajouter
            
        Returns:
            bool: True si l'ajout est réussi, False sinon
        """
        try:
            self.inventory.append(item)
            logger.debug(f"Article ajouté à la boutique {self.name}: {item.name}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'un article à la boutique {self.name}: {str(e)}")
            return False
    
    def remove_item(self, item_id: str) -> bool:
        """
        Retire un article de l'inventaire de la boutique
        
        Args:
            item_id: Identifiant de l'article à retirer
            
        Returns:
            bool: True si le retrait est réussi, False sinon
        """
        try:
            for i, item in enumerate(self.inventory):
                if item.item_id == item_id:
                    del self.inventory[i]
                    logger.debug(f"Article retiré de la boutique {self.name}: {item.name}")
                    return True
            logger.warning(f"Article non trouvé dans la boutique {self.name}: {item_id}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du retrait d'un article de la boutique {self.name}: {str(e)}")
            return False
    
    def get_item(self, item_id: str):
        """
        Récupère un article de l'inventaire par son ID
        
        Args:
            item_id: Identifiant de l'article à récupérer
            
        Returns:
            L'article si trouvé, None sinon
        """
        for item in self.inventory:
            if item.item_id == item_id:
                return item
        return None
    
    def get_sell_price(self, item) -> int:
        """
        Calcule le prix de vente d'un article (de la boutique au joueur)
        
        Args:
            item: L'article dont on veut connaître le prix de vente
            
        Returns:
            int: Prix de vente
        """
        base_price = getattr(item, 'value', 0)
        return int(base_price * self.markup_factor)
    
    def get_buy_price(self, item) -> int:
        """
        Calcule le prix d'achat d'un article (du joueur à la boutique)
        
        Args:
            item: L'article dont on veut connaître le prix d'achat
            
        Returns:
            int: Prix d'achat
        """
        base_price = getattr(item, 'value', 0)
        return int(base_price * self.discount_factor)
    
    def filter_items_by_category(self, category: ItemCategory) -> List[Any]:
        """
        Filtre les articles de l'inventaire par catégorie
        
        Args:
            category: Catégorie d'articles à filtrer
            
        Returns:
            List: Liste des articles de la catégorie spécifiée
        """
        return [item for item in self.inventory if getattr(item, 'category', None) == category]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la boutique en dictionnaire pour le stockage ou l'affichage
        
        Returns:
            Dict: Dictionnaire représentant la boutique
        """
        return {
            'shop_id': self.shop_id,
            'name': self.name,
            'shop_type': self.shop_type.name if isinstance(self.shop_type, ShopType) else self.shop_type,
            'city_id': self.city_id,
            'description': self.description,
            'owner': self.owner,
            'markup_factor': self.markup_factor,
            'discount_factor': self.discount_factor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shop':
        """
        Crée une instance de boutique à partir d'un dictionnaire
        
        Args:
            data: Dictionnaire contenant les données de la boutique
            
        Returns:
            Shop: Instance de boutique créée
        """
        # Conversion du type de boutique de chaîne à enum si nécessaire
        shop_type = data.get('shop_type')
        if isinstance(shop_type, str):
            try:
                shop_type = ShopType[shop_type]
            except (KeyError, ValueError):
                shop_type = ShopType.GENERAL
                logger.warning(f"Type de boutique inconnu: {data.get('shop_type')}, utilisation du type GENERAL")
        
        shop = cls(
            shop_id=data.get('shop_id'),
            name=data.get('name', ''),
            shop_type=shop_type,
            city_id=data.get('city_id', ''),
            description=data.get('description', ''),
            owner=data.get('owner', '')
        )
        
        # Ajout des propriétés supplémentaires
        if 'markup_factor' in data:
            shop.markup_factor = float(data['markup_factor'])
        if 'discount_factor' in data:
            shop.discount_factor = float(data['discount_factor'])
        
        return shop
    
    def __str__(self) -> str:
        return f"{self.name} ({self.shop_type.name if isinstance(self.shop_type, ShopType) else self.shop_type})"
    
    def __repr__(self) -> str:
        return f"Shop(shop_id={self.shop_id}, name={self.name}, city_id={self.city_id})"


class ShopItem:
    """Représente un article dans une boutique"""
    
    def __init__(self, item_id: str = None, name: str = "", description: str = "", 
                 category: ItemCategory = ItemCategory.MISC, value: int = 0, 
                 properties: Dict[str, Any] = None):
        """
        Initialise un nouvel article de boutique
        
        Args:
            item_id: Identifiant unique de l'article (généré automatiquement si non fourni)
            name: Nom de l'article
            description: Description de l'article
            category: Catégorie de l'article
            value: Valeur de base de l'article en crédits
            properties: Propriétés supplémentaires de l'article
        """
        self.item_id = item_id or f"item_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.category = category
        self.value = value
        self.properties = properties or {}
        self.quantity = 1
        
        logger.debug(f"Nouvel article créé: {self.name} (ID: {self.item_id})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'article en dictionnaire pour le stockage ou l'affichage
        
        Returns:
            Dict: Dictionnaire représentant l'article
        """
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.name if isinstance(self.category, ItemCategory) else self.category,
            'value': self.value,
            'properties': self.properties,
            'quantity': self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShopItem':
        """
        Crée une instance d'article à partir d'un dictionnaire
        
        Args:
            data: Dictionnaire contenant les données de l'article
            
        Returns:
            ShopItem: Instance d'article créée
        """
        # Conversion de la catégorie de chaîne à enum si nécessaire
        category = data.get('category')
        if isinstance(category, str):
            try:
                category = ItemCategory[category]
            except (KeyError, ValueError):
                category = ItemCategory.MISC
                logger.warning(f"Catégorie d'article inconnue: {data.get('category')}, utilisation de la catégorie MISC")
        
        item = cls(
            item_id=data.get('item_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=category,
            value=data.get('value', 0),
            properties=data.get('properties', {})
        )
        
        # Ajout des propriétés supplémentaires
        if 'quantity' in data:
            item.quantity = int(data['quantity'])
        
        return item
    
    def __str__(self) -> str:
        return f"{self.name} ({self.value} crédits)"
    
    def __repr__(self) -> str:
        return f"ShopItem(item_id={self.item_id}, name={self.name}, value={self.value})"


# Fonctions utilitaires
def create_default_item(category: ItemCategory, tier: int = 1) -> ShopItem:
    """
    Crée un article par défaut selon la catégorie et le niveau
    
    Args:
        category: Catégorie de l'article à créer
        tier: Niveau de l'article (1-5, 5 étant le plus puissant)
        
    Returns:
        ShopItem: Article créé
    """
    tier = max(1, min(5, tier))  # Limiter le niveau entre 1 et 5
    
    # Facteur de valeur basé sur le niveau
    value_factor = tier * 50
    
    # Configuration selon la catégorie
    if category == ItemCategory.WEAPON:
        weapons = [
            ("Pistolet de base", "Un pistolet léger standard. Précis et fiable."),
            ("Fusil d'assaut", "Fusil d'assaut militaire standard. Bonne cadence de tir."),
            ("Fusil de précision", "Fusil de tireur d'élite. Haute précision et dégâts."),
            ("Fusil à pompe", "Arme à courte portée mais dévastatrice."),
            ("Arme de mêlée", "Lame mono-moléculaire. Silencieuse et mortelle.")
        ]
        name, desc = weapons[tier % len(weapons)]
        prefix = ["Standard", "Avancé", "Militaire", "Prototype", "Légendaire"][tier-1]
        name = f"{prefix} {name}"
        props = {
            "damage": 5 * tier,
            "accuracy": min(95, 60 + 5 * tier),
            "durability": 100,
            "range": 10 * tier
        }
        value = 100 * tier + value_factor
    
    elif category == ItemCategory.ARMOR:
        armors = [
            ("Veste renforcée", "Protection légère contre les attaques mineures."),
            ("Armure tactique", "Équipement de protection standard pour situations dangereuses."),
            ("Exosquelette léger", "Armure avec renforcement musculaire intégré."),
            ("Combinaison militaire", "Armure lourde avec protection balistique avancée."),
            ("Blindage corporel", "Système de défense intégral avec bouclier énergétique.")
        ]
        name, desc = armors[tier % len(armors)]
        prefix = ["Basique", "Amélioré", "Avancé", "Expérimental", "Ultime"][tier-1]
        name = f"{prefix} {name}"
        props = {
            "defense": 5 * tier,
            "durability": 100,
            "mobility": max(50, 100 - 10 * tier),
            "tech_resist": 5 * tier
        }
        value = 80 * tier + value_factor
    
    elif category == ItemCategory.SOFTWARE:
        softwares = [
            ("Outil de déchiffrement", "Logiciel de base pour décrypter des codes simples."),
            ("Suite de hacking", "Collection d'outils pour accéder à des systèmes protégés."),
            ("IA assistante", "Intelligence artificielle d'aide au hacking et à l'analyse."),
            ("Virus polymorphe", "Programme malveillant évolutif pour infiltrer des systèmes sécurisés."),
            ("Framework d'intrusion quantique", "Technologie de pointe pour le hacking de niveau militaire.")
        ]
        name, desc = softwares[tier % len(softwares)]
        version = f"v{tier}.{tier*2}.{tier*3}"
        name = f"{name} {version}"
        props = {
            "power": 10 * tier,
            "stealth": min(95, 50 + 10 * tier),
            "compatibility": max(50, 100 - 10 * tier),
            "complexity": tier
        }
        value = 120 * tier + value_factor
    
    elif category == ItemCategory.HARDWARE:
        hardwares = [
            ("Module mémoire", "Augmente la capacité de stockage des appareils."),
            ("Processeur amélioré", "Améliore la vitesse de traitement des données."),
            ("Antenne longue portée", "Étend la portée des communications sans fil."),
            ("Décodeur de signal", "Intercepte et décode les transmissions cryptées."),
            ("Interface neurale", "Permet une connexion directe entre le cerveau et les systèmes informatiques.")
        ]
        name, desc = hardwares[tier % len(hardwares)]
        prefix = ["Bas de gamme", "Standard", "Pro", "Enterprise", "Militaire"][tier-1]
        name = f"{name} {prefix}"
        props = {
            "performance": 20 * tier,
            "reliability": min(95, 60 + 7 * tier),
            "power_usage": max(20, 100 - 15 * tier),
            "heat": max(20, 100 - 15 * tier)
        }
        value = 90 * tier + value_factor
    
    elif category == ItemCategory.IMPLANT:
        implants = [
            ("Implant oculaire", "Améliore la vision et permet l'affichage de données."),
            ("Amplificateur neuronal", "Augmente les capacités cognitives et la mémoire."),
            ("Renforcement musculaire", "Améliore la force et l'endurance physique."),
            ("Système immunitaire synthétique", "Protège contre les toxines et les maladies."),
            ("Interface cerveau-machine", "Permet le contrôle mental des appareils électroniques.")
        ]
        name, desc = implants[tier % len(implants)]
        grade = ["Génération I", "Génération II", "Génération III", "Prototype", "Militaire Classifié"][tier-1]
        name = f"{name} {grade}"
        props = {
            "effectiveness": 15 * tier,
            "integration": min(95, 60 + 8 * tier),
            "side_effects": max(5, 40 - 7 * tier),
            "maintenance": max(10, 50 - 8 * tier)
        }
        value = 150 * tier + value_factor
    
    else:  # ItemCategory.MISC et autres
        items = [
            ("Kit de réparation", "Outils de base pour réparer les équipements endommagés."),
            ("Médikit", "Fournitures médicales pour soigner les blessures mineures."),
            ("Dispositif de piratage", "Appareil portable pour le hacking rapide."),
            ("Terminal portable", "Ordinateur compact pour accéder aux réseaux."),
            ("Implant jetable", "Amélioration temporaire des capacités.")
        ]
        name, desc = items[tier % len(items)]
        quality = ["Basique", "Standard", "Avancé", "Premium", "Elite"][tier-1]
        name = f"{name} {quality}"
        props = {
            "utility": 10 * tier,
            "durability": 20 * tier,
            "rarity": tier
        }
        value = 50 * tier + value_factor
    
    return ShopItem(
        name=name,
        description=desc,
        category=category,
        value=value,
        properties=props
    )
