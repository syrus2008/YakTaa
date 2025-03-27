#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des vêtements pour YakTaa.
Ce module définit les classes et fonctions pour gérer les vêtements dans le jeu.
"""

import json
import enum
import logging
from typing import Dict, Any, Optional, List
from .item import Item

logger = logging.getLogger(__name__)

class ClothingType(enum.Enum):
    """Types de vêtements disponibles dans le jeu."""
    HAT = "hat"
    HELMET = "helmet"
    JACKET = "jacket"
    COAT = "coat"
    VEST = "vest"
    ARMOR = "armor"
    SHIRT = "shirt"
    PANTS = "pants"
    SKIRT = "skirt"
    SHORTS = "shorts"
    BOOTS = "boots"
    SHOES = "shoes"
    GLOVES = "gloves"
    ACCESSORY = "accessory"
    OUTFIT = "outfit"
    OTHER = "other"

class ClothingRarity(enum.Enum):
    """Rareté des vêtements dans le jeu."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ClothingItem(Item):
    """Classe représentant un vêtement dans le jeu."""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 description: str = "",
                 clothing_type: str = "OTHER",
                 price: int = 100,
                 rarity: str = "COMMON",
                 stats: Optional[Dict[str, Any]] = None,
                 level: int = 1,
                 equipped: bool = False):
        """
        Initialise un nouvel objet de type vêtement.
        
        Args:
            id: Identifiant unique du vêtement
            name: Nom du vêtement
            description: Description du vêtement
            clothing_type: Type de vêtement (HAT, JACKET, etc.)
            price: Prix du vêtement
            rarity: Rareté du vêtement (COMMON, RARE, etc.)
            stats: Statistiques du vêtement (style, comfort, protection, etc.)
            level: Niveau requis pour utiliser le vêtement
            equipped: Si le vêtement est équipé ou non
        """
        super().__init__(id, name, "clothing", description, price)
        
        # Convertir le type en énumération si c'est une chaîne
        if isinstance(clothing_type, str):
            try:
                for t in ClothingType:
                    if t.value == clothing_type.lower():
                        clothing_type = t
                        break
                if isinstance(clothing_type, str):
                    clothing_type = ClothingType.OTHER
            except Exception:
                clothing_type = ClothingType.OTHER
        
        # Convertir la rareté en énumération si c'est une chaîne
        if isinstance(rarity, str):
            try:
                for r in ClothingRarity:
                    if r.value == rarity.lower():
                        rarity = r
                        break
                if isinstance(rarity, str):
                    rarity = ClothingRarity.COMMON
            except Exception:
                rarity = ClothingRarity.COMMON
        
        self.clothing_type = clothing_type
        self.rarity = rarity
        self.stats = stats or {}
        self.level = level
        self.equipped = equipped
        
        # Déterminer l'emplacement d'équipement en fonction du type
        if isinstance(self.clothing_type, ClothingType):
            if self.clothing_type in [ClothingType.HAT, ClothingType.HELMET]:
                self.slot = "head"
            elif self.clothing_type in [ClothingType.JACKET, ClothingType.COAT, ClothingType.VEST, ClothingType.ARMOR, ClothingType.SHIRT]:
                self.slot = "body"
            elif self.clothing_type in [ClothingType.PANTS, ClothingType.SKIRT, ClothingType.SHORTS]:
                self.slot = "legs"
            elif self.clothing_type in [ClothingType.BOOTS, ClothingType.SHOES]:
                self.slot = "feet"
            elif self.clothing_type == ClothingType.GLOVES:
                self.slot = "hands"
            elif self.clothing_type == ClothingType.OUTFIT:
                self.slot = "full_body"
            else:
                self.slot = "accessory"
        else:
            self.slot = "accessory"
    
    @property
    def style(self) -> int:
        """Retourne la valeur de style du vêtement."""
        return self.stats.get("style", 0)
    
    @property
    def comfort(self) -> int:
        """Retourne la valeur de confort du vêtement."""
        return self.stats.get("comfort", 0)
    
    @property
    def protection(self) -> int:
        """Retourne la valeur de protection du vêtement."""
        return self.stats.get("protection", 0)
    
    @property
    def charisma(self) -> int:
        """Retourne le bonus de charisme du vêtement."""
        return self.stats.get("charisma", 0)
    
    @property
    def status(self) -> int:
        """Retourne la valeur de statut social du vêtement."""
        return self.stats.get("status", 0)
    
    def can_equip(self, player_level: int) -> bool:
        """
        Vérifie si le joueur peut équiper ce vêtement.
        
        Args:
            player_level: Niveau actuel du joueur
            
        Returns:
            True si le joueur peut équiper ce vêtement, False sinon
        """
        return player_level >= self.level
    
    def use(self, player=None) -> Dict[str, Any]:
        """
        Utilise le vêtement (l'équipe).
        
        Args:
            player: Instance du joueur qui utilise le vêtement
            
        Returns:
            Dictionnaire avec les résultats de l'utilisation
        """
        if player and not self.can_equip(player.level):
            return {
                "success": False,
                "message": f"Vous devez être au moins niveau {self.level} pour équiper {self.name}."
            }
        
        self.equipped = not self.equipped
        status = "équipé" if self.equipped else "retiré"
        
        result = {
            "success": True,
            "message": f"{self.name} a été {status}.",
            "equipped": self.equipped
        }
        
        if self.equipped and player:
            # Appliquer les effets lorsque équipé
            result["effects"] = []
            if self.protection > 0:
                result["effects"].append(f"+{self.protection} protection")
            if self.charisma > 0:
                result["effects"].append(f"+{self.charisma} charisme")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'objet en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'objet
        """
        base_dict = super().to_dict()
        base_dict.update({
            "clothing_type": self.clothing_type.value if isinstance(self.clothing_type, ClothingType) else str(self.clothing_type),
            "rarity": self.rarity.value if isinstance(self.rarity, ClothingRarity) else str(self.rarity),
            "level": self.level,
            "stats": self.stats,
            "slot": self.slot,
            "equipped": self.equipped,
            "style": self.style,
            "comfort": self.comfort,
            "protection": self.protection,
            "charisma": self.charisma,
            "status": self.status
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClothingItem':
        """
        Crée une instance à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données de l'objet
            
        Returns:
            Instance de ClothingItem
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "Vêtement inconnu"),
            description=data.get("description", ""),
            clothing_type=data.get("clothing_type", "OTHER"),
            price=data.get("price", 100),
            rarity=data.get("rarity", "COMMON"),
            stats=data.get("stats", {}),
            level=data.get("level", 1),
            equipped=data.get("equipped", False)
        )
