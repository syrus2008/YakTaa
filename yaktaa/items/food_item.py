"""
Module pour la gestion des aliments dans YakTaa.
Définit les différents types d'aliments que le joueur peut acquérir et consommer.
"""

import logging
from typing import Dict, Any, Optional

from .item import Item

logger = logging.getLogger("YakTaa.Items.FoodItem")

class FoodItem(Item):
    """
    Classe représentant un aliment dans le jeu
    """
    
    FOOD_TYPES = [
        "SNACK", "MEAL", "DRINK", "FRUIT", "VEGETABLE", 
        "MEAT", "DESSERT", "ENERGY_BAR", "MEDICINE", "SPECIAL"
    ]
    
    RARITY_LEVELS = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Aliment inconnu", 
                 description: str = "Un aliment mystérieux.",
                 food_type: str = "SNACK",
                 price: int = 10,
                 health_restore: int = 5,
                 energy_restore: int = 5,
                 mental_restore: int = 0,
                 is_legal: bool = True,
                 rarity: str = "COMMON",
                 uses: int = 1,
                 icon: str = "food",
                 properties: Dict[str, Any] = None):
        """
        Initialise un aliment
        
        Args:
            id: Identifiant unique de l'aliment
            name: Nom de l'aliment
            description: Description de l'aliment
            food_type: Type d'aliment
            price: Prix de base en crédits
            health_restore: Quantité de santé restaurée
            energy_restore: Quantité d'énergie restaurée
            mental_restore: Quantité de santé mentale restaurée
            is_legal: Si l'aliment est légal ou non
            rarity: Rareté de l'aliment
            uses: Nombre d'utilisations disponibles
            icon: Icône représentant l'aliment
            properties: Propriétés supplémentaires
        """
        # Normaliser le type d'aliment
        if food_type and food_type.upper() in [t.upper() for t in self.FOOD_TYPES]:
            for t in self.FOOD_TYPES:
                if food_type.upper() == t.upper():
                    food_type = t
                    break
        else:
            food_type = "SNACK"  # Type par défaut
            
        # Normaliser la rareté
        if rarity and rarity.upper() in [r.upper() for r in self.RARITY_LEVELS]:
            for r in self.RARITY_LEVELS:
                if rarity.upper() == r.upper():
                    rarity = r
                    break
        else:
            rarity = "COMMON"  # Rareté par défaut
            
        # Initialiser la classe parente
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="food",
            quantity=1,
            value=price,
            icon=f"food_{food_type.lower()}" if food_type else "food",
            properties=properties or {}
        )
        
        # Attributs spécifiques à l'aliment
        self.food_type = food_type
        self.health_restore = health_restore
        self.energy_restore = energy_restore
        self.mental_restore = mental_restore
        self.is_legal = is_legal
        self.rarity = rarity
        self.uses = uses
        self.price = price
        
        logger.debug(f"Nouvel aliment créé : {name} (Type: {food_type}, Santé: +{health_restore}, Énergie: +{energy_restore}, Mental: +{mental_restore})")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Retourne les informations à afficher dans l'interface"""
        base_info = super().get_display_info()
        
        # Ajouter les informations spécifiques à l'aliment
        food_info = {
            "type": f"Aliment - {self.food_type}",
            "rarity": self.rarity,
            "uses": f"{self.uses} utilisation(s)",
            "health_restore": f"+{self.health_restore} PV",
            "energy_restore": f"+{self.energy_restore} Énergie",
            "mental_restore": f"+{self.mental_restore} Mental" if self.mental_restore > 0 else "Aucun effet mental",
            "legal_status": "Légal" if self.is_legal else "Illégal"
        }
        
        return {**base_info, **food_info}
    
    def use(self) -> Dict[str, Any]:
        """
        Consomme l'aliment et retourne le résultat
        
        Returns:
            Dictionnaire contenant le résultat de la consommation
        """
        if self.uses <= 0:
            return {
                "success": False,
                "message": f"Ce {self.name} a déjà été entièrement consommé."
            }
        
        self.uses -= 1
        
        # Préparer les informations de retour
        result = {
            "success": True,
            "message": f"Vous avez consommé {self.name}.",
            "health_restored": self.health_restore,
            "energy_restored": self.energy_restore,
            "mental_restored": self.mental_restore,
            "uses_left": self.uses
        }
        
        # Message personnalisé selon les effets
        effects_text = []
        if self.health_restore > 0:
            effects_text.append(f"+{self.health_restore} PV")
        if self.energy_restore > 0:
            effects_text.append(f"+{self.energy_restore} Énergie")
        if self.mental_restore > 0:
            effects_text.append(f"+{self.mental_restore} Mental")
            
        if effects_text:
            effects_str = ", ".join(effects_text)
            result["message"] = f"Vous avez consommé {self.name}. Effets: {effects_str}"
        
        return result
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'FoodItem':
        """
        Crée une instance de FoodItem à partir d'une ligne de la base de données
        
        Args:
            row: Dictionnaire contenant les données de la base de données
            
        Returns:
            Une instance de FoodItem
        """
        # Convertir les types si nécessaire
        health_restore = int(row.get('health_restore', 0))
        energy_restore = int(row.get('energy_restore', 0))
        mental_restore = int(row.get('mental_restore', 0))
        price = int(row.get('price', 10))
        is_legal = bool(int(row.get('is_legal', 1)))
        uses = int(row.get('uses', 1))
        
        # Créer l'instance
        return cls(
            id=row.get('id'),
            name=row.get('name', 'Aliment inconnu'),
            description=row.get('description', 'Un aliment mystérieux.'),
            food_type=row.get('food_type', 'SNACK'),
            price=price,
            health_restore=health_restore,
            energy_restore=energy_restore,
            mental_restore=mental_restore,
            is_legal=is_legal,
            rarity=row.get('rarity', 'COMMON'),
            uses=uses
        )
