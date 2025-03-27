"""
Module pour la gestion des consommables dans YakTaa.
Définit les différents types d'objets consommables que le joueur peut acquérir et utiliser.
"""

import logging
import random
from typing import Dict, List, Optional, Any

from .item import Item

logger = logging.getLogger("YakTaa.Items.ConsumableItem")

class ConsumableItem(Item):
    """
    Classe représentant un item consommable dans le jeu
    """
    
    CONSUMABLE_TYPES = [
        "HEALTH", "ENERGY", "FOCUS", "MEMORY", "ANTIVIRUS", 
        "BOOSTER", "STIMPACK", "FOOD", "DRINK", "DRUG"
    ]
    
    RARITY_LEVELS = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Consommable inconnu", 
                 description: str = "Un consommable mystérieux.",
                 item_type: str = "HEALTH",
                 rarity: str = "Common",
                 uses: int = 1,
                 effects: Dict[str, Any] = None,
                 duration: int = 0,  # en secondes, 0 = effet instantané
                 cooldown: int = 0,  # en secondes
                 price: int = 50,
                 icon: str = "consumable",
                 properties: Dict[str, Any] = None):
        """
        Initialise un item consommable
        
        Args:
            id: Identifiant unique de l'item
            name: Nom de l'item
            description: Description de l'item
            item_type: Type de consommable
            rarity: Rareté du consommable
            uses: Nombre d'utilisations disponibles
            effects: Effets produits lors de l'utilisation
            duration: Durée des effets en secondes
            cooldown: Temps d'attente entre deux utilisations
            price: Prix de base en crédits
            icon: Icône représentant l'item
            properties: Propriétés supplémentaires
        """
        # Normaliser le type de consommable
        if item_type.upper() in [t.upper() for t in self.CONSUMABLE_TYPES]:
            for t in self.CONSUMABLE_TYPES:
                if item_type.upper() == t.upper():
                    item_type = t
                    break
        else:
            item_type = "HEALTH"  # Type par défaut
            
        # Normaliser la rareté
        if rarity not in self.RARITY_LEVELS:
            rarity = "Common"  # Rareté par défaut
            
        # Initialiser les effets par défaut selon le type
        if effects is None:
            effects = self._generate_default_effects(item_type, rarity)
        
        # Calculer le prix en fonction des caractéristiques
        price = self._calculate_price(item_type, rarity, uses, duration, price)
        
        # Initialiser la classe parente
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="consumable",
            quantity=1,
            value=price,
            icon=f"consumable_{item_type.lower()}",
            properties=properties or {}
        )
        
        # Attributs spécifiques au consommable
        self.item_type = item_type
        self.rarity = rarity
        self.uses = uses
        self.effects = effects
        self.duration = duration
        self.cooldown = cooldown
        self.price = price
        
        logger.debug(f"Nouvel item consommable créé : {name} (Type: {item_type}, Rareté: {rarity}, Utilisations: {uses})")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Retourne les informations à afficher dans l'interface"""
        base_info = super().get_display_info()
        
        # Ajouter les informations spécifiques au consommable
        consumable_info = {
            "type": f"Consommable - {self.item_type}",
            "rarity": self.rarity,
            "uses": f"{self.uses} utilisation(s)",
            "effects": self.effects,
            "duration": f"{self.duration}s" if self.duration > 0 else "Instantané",
            "cooldown": f"{self.cooldown}s" if self.cooldown > 0 else "Aucun"
        }
        
        return {**base_info, **consumable_info}
    
    def use(self) -> Dict[str, Any]:
        """
        Utilise le consommable et retourne le résultat
        
        Returns:
            Dictionnaire contenant le résultat de l'utilisation
        """
        if self.uses <= 0:
            return {
                "success": False,
                "message": f"Ce {self.name} est épuisé et ne peut plus être utilisé."
            }
        
        self.uses -= 1
        
        # Préparer les informations de retour
        result = {
            "success": True,
            "message": f"Vous avez utilisé {self.name}.",
            "effects": self.effects,
            "duration": self.duration,
            "cooldown": self.cooldown,
            "uses_left": self.uses
        }
        
        # Ajouter des messages spécifiques selon le type
        if self.item_type == "HEALTH":
            result["message"] = f"Vous avez utilisé {self.name}. Santé restaurée: +{self.effects.get('health', 0)}"
        elif self.item_type == "ENERGY":
            result["message"] = f"Vous avez utilisé {self.name}. Énergie restaurée: +{self.effects.get('energy', 0)}"
        elif self.item_type == "FOCUS":
            result["message"] = f"Vous avez utilisé {self.name}. Concentration améliorée: +{self.effects.get('focus', 0)}"
        elif self.item_type == "MEMORY":
            result["message"] = f"Vous avez utilisé {self.name}. Mémoire augmentée: +{self.effects.get('memory', 0)}"
        elif self.item_type == "ANTIVIRUS":
            result["message"] = f"Vous avez utilisé {self.name}. Système nettoyé avec une efficacité de {self.effects.get('cleaning', 0)}%"
        elif self.item_type == "BOOSTER":
            result["message"] = f"Vous avez utilisé {self.name}. Performances améliorées pour {self.duration} secondes."
        elif self.item_type == "STIMPACK":
            result["message"] = f"Vous avez utilisé {self.name}. Effets stimulants activés."
        
        return result
    
    def _generate_default_effects(self, item_type: str, rarity: str) -> Dict[str, Any]:
        """
        Génère des effets par défaut selon le type de consommable
        
        Args:
            item_type: Type de consommable
            rarity: Rareté du consommable
            
        Returns:
            Dictionnaire d'effets
        """
        # Facteur de rareté
        rarity_factor = self.RARITY_LEVELS.index(rarity) + 1
        
        # Effets de base selon le type
        base_effects = {
            "HEALTH": {
                "health": 10 * rarity_factor,
                "regeneration": rarity_factor > 2
            },
            "ENERGY": {
                "energy": 15 * rarity_factor,
                "stamina": 5 * rarity_factor
            },
            "FOCUS": {
                "focus": 20 * rarity_factor,
                "precision": 5 * rarity_factor,
                "reaction": 2 * rarity_factor
            },
            "MEMORY": {
                "memory": 50 * rarity_factor,
                "processing": 10 * rarity_factor
            },
            "ANTIVIRUS": {
                "cleaning": min(95, 50 + 10 * rarity_factor),
                "protection": rarity_factor > 3,
                "repair": rarity_factor > 4
            },
            "BOOSTER": {
                "cpu": 20 * rarity_factor,
                "ram": 15 * rarity_factor,
                "network": 10 * rarity_factor
            },
            "STIMPACK": {
                "reflexes": 20 * rarity_factor,
                "strength": 15 * rarity_factor,
                "perception": 10 * rarity_factor,
                "side_effects": rarity_factor < 4
            },
            "FOOD": {
                "satiety": 30 * rarity_factor,
                "health": 5 * rarity_factor
            },
            "DRINK": {
                "hydration": 30 * rarity_factor,
                "energy": 10 * rarity_factor
            },
            "DRUG": {
                "effect_power": 25 * rarity_factor,
                "addiction_risk": max(1, 10 - rarity_factor),
                "side_effects": rarity_factor < 5
            }
        }
        
        return base_effects.get(item_type, {"power": rarity_factor * 10})
    
    def _calculate_price(self, item_type: str, rarity: str, uses: int, duration: int, base_price: int) -> int:
        """
        Calcule le prix en fonction des caractéristiques
        
        Args:
            item_type: Type de consommable
            rarity: Rareté du consommable
            uses: Nombre d'utilisations
            duration: Durée des effets
            base_price: Prix de base
            
        Returns:
            Prix calculé
        """
        # Facteurs de prix selon le type
        type_factors = {
            "HEALTH": 1.0,
            "ENERGY": 1.1,
            "FOCUS": 1.3,
            "MEMORY": 1.5,
            "ANTIVIRUS": 1.4,
            "BOOSTER": 1.6,
            "STIMPACK": 1.8,
            "FOOD": 0.6,
            "DRINK": 0.5,
            "DRUG": 2.0
        }
        
        # Facteur de rareté
        rarity_factor = self.RARITY_LEVELS.index(rarity) + 1
        
        # Calcul du prix
        calculated_price = base_price * type_factors.get(item_type, 1.0) * (rarity_factor ** 1.5)
        
        # Ajustement selon le nombre d'utilisations
        calculated_price *= max(1, uses * 0.8)
        
        # Ajustement selon la durée
        if duration > 0:
            duration_factor = min(3, 1 + (duration / 60) * 0.1)  # Plafonné à x3 pour les effets très longs
            calculated_price *= duration_factor
        
        # Ajouter une variation aléatoire de +/- 10%
        variation = random.uniform(0.9, 1.1)
        
        return max(1, int(calculated_price * variation))
    
    @staticmethod
    def generate_random(level: int = 1, item_type: Optional[str] = None, rarity: Optional[str] = None) -> 'ConsumableItem':
        """
        Génère un item consommable aléatoire
        
        Args:
            level: Niveau de l'item (1-10)
            item_type: Type spécifique de consommable (optionnel)
            rarity: Rareté spécifique (optionnel)
            
        Returns:
            Instance de ConsumableItem
        """
        # Limiter le niveau
        level = max(1, min(10, level))
        
        # Sélectionner un type aléatoire si non spécifié
        if item_type is None:
            item_type = random.choice(ConsumableItem.CONSUMABLE_TYPES)
        
        # Sélectionner une rareté en fonction du niveau si non spécifiée
        if rarity is None:
            # Plus le niveau est élevé, plus la chance d'avoir une rareté élevée est grande
            max_rarity_index = min(len(ConsumableItem.RARITY_LEVELS) - 1, 
                                   (level - 1) // 2)  # Niveau 1-2: Common, 3-4: Uncommon, etc.
            rarity_weights = [max(1, 10 - i*2) for i in range(max_rarity_index + 1)]
            rarity = random.choices(
                ConsumableItem.RARITY_LEVELS[:max_rarity_index + 1],
                weights=rarity_weights
            )[0]
        
        # Noms possibles selon le type
        type_names = {
            "HEALTH": ["Médikit", "Bandage", "Stimulant médical", "Patch de soin"],
            "ENERGY": ["Booster d'énergie", "Cellule énergétique", "Concentré stimulant", "Batterie neurale"],
            "FOCUS": ["Amplificateur de focus", "Nootropique", "Concentrateur mental", "Stabilisateur synaptique"],
            "MEMORY": ["Booster de mémoire", "Optimiseur RAM", "Harmoniseur neuronal", "Enhanceur cognitif"],
            "ANTIVIRUS": ["Antivirus", "Nettoyeur système", "Purificateur de code", "Anti-malware"],
            "BOOSTER": ["Accélérateur système", "Optimiseur de performance", "Amplificateur", "Catalyseur"],
            "STIMPACK": ["Stimpack", "Injecteur de combat", "Accélérateur réflexe", "Cocktail d'adrénaline"],
            "FOOD": ["Ration", "Conserve", "Barre protéinée", "Synthétiseur nutritif"],
            "DRINK": ["Boisson énergisante", "Eau purifiée", "Électrolytes", "Smoothie"],
            "DRUG": ["Psychostimulant", "Neuroamplifiant", "Substrat expérimental", "Composé chimique"]
        }
        
        # Marques fictives
        brands = ["MedTech", "EnergCore", "NeuraSyn", "QuickFix", "BioBoost", 
                 "SynthLife", "StimTech", "PureFuel", "NeoNutri", "ChemPro"]
        
        # Sélectionner un nom de base et une marque
        name_base = random.choice(type_names.get(item_type, ["Consommable"]))
        brand = random.choice(brands)
        
        # Modifier selon la rareté
        rarity_prefix = {
            "Common": "",
            "Uncommon": "Amélioré",
            "Rare": "Supérieur",
            "Epic": "Premium",
            "Legendary": "Ultime",
            "Mythic": "Transcendant"
        }
        
        # Construire le nom complet
        prefix = rarity_prefix.get(rarity, "")
        name = f"{brand} {name_base}{' ' + prefix if prefix else ''}"
        
        # Générer la description
        rarity_descriptors = {
            "Common": "de qualité standard",
            "Uncommon": "de qualité supérieure",
            "Rare": "de grande qualité",
            "Epic": "d'une qualité exceptionnelle",
            "Legendary": "d'une qualité légendaire",
            "Mythic": "d'une qualité transcendante, presque mythique"
        }
        
        description = f"Un {name_base.lower()} {rarity_descriptors.get(rarity, '')} fabriqué par {brand}. "
        
        if item_type == "HEALTH":
            description += "Restaure les points de vie et accélère la guérison."
        elif item_type == "ENERGY":
            description += "Restaure l'énergie et améliore l'endurance."
        elif item_type == "FOCUS":
            description += "Améliore la concentration et la précision pendant un temps limité."
        elif item_type == "MEMORY":
            description += "Augmente temporairement la mémoire disponible pour les programmes et processus."
        elif item_type == "ANTIVIRUS":
            description += "Nettoie le système des virus et malwares."
        elif item_type == "BOOSTER":
            description += "Améliore les performances système pendant un temps limité."
        elif item_type == "STIMPACK":
            description += "Améliore les réflexes et capacités physiques en situation de combat."
        elif item_type == "FOOD":
            description += "Fournit de l'énergie et des nutriments essentiels."
        elif item_type == "DRINK":
            description += "Hydrate et restaure l'énergie."
        elif item_type == "DRUG":
            description += "Augmente temporairement certaines capacités, avec des risques d'effets secondaires."
        
        # Nombre d'utilisations
        uses = 1
        if level > 3 and random.random() < 0.3:
            uses = random.randint(2, 3)
        if level > 6 and random.random() < 0.2:
            uses = random.randint(3, 5)
        
        # Durée des effets
        duration = 0  # Instantané par défaut
        if item_type in ["FOCUS", "MEMORY", "BOOSTER", "STIMPACK", "DRUG"]:
            base_duration = 30  # 30 secondes
            duration = base_duration * (1 + (level // 2))
        
        # Temps de recharge
        cooldown = 0
        if item_type in ["STIMPACK", "BOOSTER", "DRUG"]:
            cooldown = 60 * (3 - min(2, level // 4))  # Diminue avec le niveau
        
        # Prix de base qui augmente avec le niveau
        base_price = 20 * level
        
        # Créer et retourner l'objet
        return ConsumableItem(
            name=name,
            description=description,
            item_type=item_type,
            rarity=rarity,
            uses=uses,
            duration=duration,
            cooldown=cooldown,
            price=base_price
        )
