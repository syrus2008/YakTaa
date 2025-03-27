"""
Module pour la gestion des objets dans YakTaa
Ce module définit la classe de base pour tous les objets du jeu.
"""

import logging
from typing import Dict, List, Optional, Any
import uuid

logger = logging.getLogger("YakTaa.Items.Item")

class Item:
    """
    Classe de base pour tous les objets du jeu
    """
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Objet inconnu", 
                 description: str = "Un objet mystérieux.",
                 type: str = "misc", 
                 item_type: str = None,  
                 quantity: int = 1,
                 value: int = 0,
                 price: int = None,  
                 icon: str = "default_item",
                 level: int = 1,  
                 weight: float = 1.0,  
                 is_illegal: bool = False,  
                 rarity: str = "COMMON",  
                 properties: Dict[str, Any] = None):
        """Initialise un objet"""
        # Générer un ID unique si non fourni
        if id is None:
            id = f"item_{uuid.uuid4().hex[:8]}"
            
        self.id = id
        self.name = name
        self.description = description
        self.type = item_type if item_type is not None else type  
        self.quantity = quantity
        self.value = price if price is not None else value  
        self.icon = icon
        self.properties = properties or {}
        self.level = level
        self.weight = weight
        self.is_illegal = is_illegal
        self.rarity = rarity
        
        logger.debug(f"Nouvel objet créé : {name} (Type: {self.type}, ID: {id})")
    
    def use(self) -> Dict[str, Any]:
        """Utilise l'objet et retourne le résultat"""
        return {
            "success": False,
            "message": "Cet objet ne peut pas être utilisé directement."
        }
    
    def get_display_info(self) -> Dict[str, Any]:
        """Retourne les informations à afficher dans l'interface"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type.title(),
            "quantity": self.quantity,
            "value": f"{self.value} ¥",
            "icon": self.icon
        }
    
    def __str__(self) -> str:
        """Représentation sous forme de chaîne de caractères"""
        return f"{self.name} ({self.type})"
    
    def __repr__(self) -> str:
        """Représentation pour le débogage"""
        return f"Item(id='{self.id}', name='{self.name}', type='{self.type}', quantity={self.quantity})"
    
    @staticmethod
    def generate_random(level: int = 1, item_type: Optional[str] = None) -> 'Item':
        """Génère un objet aléatoire"""
        import random
        
        # Types d'objets disponibles
        types = ["misc", "consumable", "quest"]
        if item_type is None:
            item_type = random.choice(types)
        
        # Noms génériques selon le type
        names = {
            "misc": ["Gadget", "Composant", "Artefact", "Relique", "Babiole"],
            "consumable": ["Stimulant", "Médicament", "Nourriture", "Boisson", "Drogue"],
            "quest": ["Disque de données", "Document", "Badge", "Clé", "Carte d'accès"]
        }
        
        # Descriptions génériques selon le type
        descriptions = {
            "misc": ["Un objet étrange de fonction inconnue.", 
                     "Un petit gadget électronique.", 
                     "Un composant mystérieux."],
            "consumable": ["Un produit consommable qui pourrait être utile.", 
                           "Une substance aux effets inconnus.", 
                           "Un produit qui semble avoir des propriétés médicinales."],
            "quest": ["Un objet qui semble important pour une mission.", 
                      "Un artefact lié à une quête spécifique.", 
                      "Un objet qui pourrait intéresser quelqu'un."]
        }
        
        # Sélectionner un nom et une description aléatoires
        name = random.choice(names.get(item_type, names["misc"]))
        description = random.choice(descriptions.get(item_type, descriptions["misc"]))
        
        # Valeur de base selon le niveau
        value = level * 10 * random.randint(1, 5)
        
        # Quantité aléatoire pour les consommables
        quantity = 1
        if item_type == "consumable":
            quantity = random.randint(1, 3)
        
        # Créer et retourner l'objet
        return Item(
            name=name,
            description=description,
            type=item_type,
            quantity=quantity,
            value=value
        )
