"""
Système d'effets de statut pour le combat dans YakTaa
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import random

logger = logging.getLogger("YakTaa.Combat.Advanced.StatusEffects")

class StatusEffectType(Enum):
    """Types d'effets de statut"""
    BUFF = auto()      # Effet positif
    DEBUFF = auto()    # Effet négatif
    DAMAGE_OVER_TIME = auto()  # Dégâts sur la durée
    HEAL_OVER_TIME = auto()    # Soins sur la durée
    CONTROL = auto()   # Contrôle (stun, paralysie, etc.)
    SPECIAL = auto()   # Effets spéciaux

class StatusEffectSystem:
    """
    Système qui gère les effets de statut pendant le combat
    """
    
    def __init__(self):
        """Initialise le système d'effets de statut"""
        self.active_effects = {}  # Acteur -> liste d'effets actifs
        self.immunities = {}      # Acteur -> liste d'immunités
        self.resistances = {}     # Acteur -> dict de résistances (type -> pourcentage)
        
        # Définir les effets de statut standard
        self.effect_definitions = self._create_effect_definitions()
        
        logger.debug("Système d'effets de statut initialisé")
    
    def _create_effect_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Crée les définitions des effets de statut standard
        
        Returns:
            Dictionnaire des définitions d'effets
        """
        return {
            # Effets de dégâts sur la durée
            "bleeding": {
                "name": "Saignement",
                "description": "Inflige des dégâts physiques à chaque tour",
                "type": StatusEffectType.DAMAGE_OVER_TIME,
                "damage_type": "PHYSICAL",
                "damage_per_turn": lambda level: 3 * level,
                "base_duration": 3,
                "icon": "bleeding",
                "stackable": True,
                "max_stacks": 3,
                "on_stack": lambda effect: effect["damage_per_turn"] * 1.5,
                "can_be_cleansed": True
            },
            "burning": {
                "name": "Brûlure",
                "description": "Inflige des dégâts thermiques à chaque tour",
                "type": StatusEffectType.DAMAGE_OVER_TIME,
                "damage_type": "THERMAL",
                "damage_per_turn": lambda level: 5 * level,
                "base_duration": 2,
                "icon": "burning",
                "stackable": True,
                "max_stacks": 2,
                "on_stack": lambda effect: effect["damage_per_turn"] * 1.3,
                "can_be_cleansed": True
            },
            "poisoned": {
                "name": "Empoisonnement",
                "description": "Inflige des dégâts chimiques à chaque tour",
                "type": StatusEffectType.DAMAGE_OVER_TIME,
                "damage_type": "CHEMICAL",
                "damage_per_turn": lambda level: 4 * level,
                "base_duration": 4,
                "icon": "poisoned",
                "stackable": True,
                "max_stacks": 3,
                "on_stack": lambda effect: effect["damage_per_turn"] * 1.2,
                "can_be_cleansed": True
            },
            "electrocuted": {
                "name": "Électrocution",
                "description": "Inflige des dégâts électriques et réduit la précision",
                "type": StatusEffectType.DAMAGE_OVER_TIME,
                "damage_type": "SHOCK",
                "damage_per_turn": lambda level: 3 * level,
                "base_duration": 2,
                "icon": "electrocuted",
                "stackable": False,
                "stat_modifiers": {"accuracy": -10},
                "can_be_cleansed": True
            },
            
            # Effets de contrôle
            "stunned": {
                "name": "Étourdissement",
                "description": "Empêche d'agir pendant un tour",
                "type": StatusEffectType.CONTROL,
                "base_duration": 1,
                "icon": "stunned",
                "stackable": False,
                "prevents_actions": True,
                "can_be_cleansed": True
            },
            "frozen": {
                "name": "Gel",
                "description": "Immobilise la cible et augmente les dégâts subis",
                "type": StatusEffectType.CONTROL,
                "base_duration": 2,
                "icon": "frozen",
                "stackable": False,
                "prevents_movement": True,
                "damage_taken_modifier": 1.5,
                "can_be_cleansed": True
            },
            "confused": {
                "name": "Confusion",
                "description": "Chance de rater son action ou d'attaquer un allié",
                "type": StatusEffectType.CONTROL,
                "base_duration": 2,
                "icon": "confused",
                "stackable": False,
                "action_failure_chance": 0.3,
                "friendly_fire_chance": 0.2,
                "can_be_cleansed": True
            },
            
            # Débuffs
            "weakened": {
                "name": "Affaiblissement",
                "description": "Réduit les dégâts infligés",
                "type": StatusEffectType.DEBUFF,
                "base_duration": 3,
                "icon": "weakened",
                "stackable": True,
                "max_stacks": 3,
                "damage_dealt_modifier": lambda stacks: 1.0 - (0.1 * stacks),
                "can_be_cleansed": True
            },
            "vulnerable": {
                "name": "Vulnérabilité",
                "description": "Augmente les dégâts subis",
                "type": StatusEffectType.DEBUFF,
                "base_duration": 3,
                "icon": "vulnerable",
                "stackable": True,
                "max_stacks": 3,
                "damage_taken_modifier": lambda stacks: 1.0 + (0.15 * stacks),
                "can_be_cleansed": True
            },
            "slowed": {
                "name": "Ralentissement",
                "description": "Réduit la vitesse et l'initiative",
                "type": StatusEffectType.DEBUFF,
                "base_duration": 2,
                "icon": "slowed",
                "stackable": False,
                "stat_modifiers": {"agility": -5, "reflexes": -3},
                "can_be_cleansed": True
            },
            
            # Buffs
            "strengthened": {
                "name": "Force renforcée",
                "description": "Augmente les dégâts infligés",
                "type": StatusEffectType.BUFF,
                "base_duration": 3,
                "icon": "strengthened",
                "stackable": True,
                "max_stacks": 3,
                "damage_dealt_modifier": lambda stacks: 1.0 + (0.1 * stacks),
                "can_be_cleansed": False
            },
            "protected": {
                "name": "Protection",
                "description": "Réduit les dégâts subis",
                "type": StatusEffectType.BUFF,
                "base_duration": 3,
                "icon": "protected",
                "stackable": True,
                "max_stacks": 3,
                "damage_taken_modifier": lambda stacks: 1.0 - (0.1 * stacks),
                "can_be_cleansed": False
            },
            "hasted": {
                "name": "Hâte",
                "description": "Augmente la vitesse et l'initiative",
                "type": StatusEffectType.BUFF,
                "base_duration": 2,
                "icon": "hasted",
                "stackable": False,
                "stat_modifiers": {"agility": 5, "reflexes": 3},
                "can_be_cleansed": False
            },
            "regenerating": {
                "name": "Régénération",
                "description": "Récupère des points de vie à chaque tour",
                "type": StatusEffectType.HEAL_OVER_TIME,
                "heal_per_turn": lambda level: 5 * level,
                "base_duration": 3,
                "icon": "regenerating",
                "stackable": False,
                "can_be_cleansed": False
            },
            
            # Effets spéciaux
            "marked": {
                "name": "Marqué",
                "description": "Augmente les chances de coup critique contre cette cible",
                "type": StatusEffectType.SPECIAL,
                "base_duration": 2,
                "icon": "marked",
                "stackable": False,
                "crit_chance_modifier": 0.2,
                "can_be_cleansed": True
            },
            "hacked": {
                "name": "Piraté",
                "description": "Systèmes cybernétiques compromis, réduit l'efficacité",
                "type": StatusEffectType.SPECIAL,
                "base_duration": 3,
                "icon": "hacked",
                "stackable": False,
                "stat_modifiers": {"hacking_defense": -50},
                "can_be_cleansed": True,
                "applies_to": ["CYBER"]  # Ne s'applique qu'aux ennemis cybernétiques
            }
        }
    
    def apply_effect(self, target: Any, effect_id: str, source: Any = None, 
                    level: int = 1, duration_modifier: float = 1.0) -> bool:
        """
        Applique un effet de statut à une cible
        
        Args:
            target: La cible de l'effet
            effect_id: Identifiant de l'effet à appliquer
            source: Source de l'effet (joueur, ennemi, etc.)
            level: Niveau de puissance de l'effet
            duration_modifier: Modificateur de durée
            
        Returns:
            True si l'effet a été appliqué, False sinon
        """
        # Vérifier si l'effet existe
        if effect_id not in self.effect_definitions:
            logger.warning(f"Effet de statut inconnu: {effect_id}")
            return False
        
        # Récupérer la définition de l'effet
        effect_def = self.effect_definitions[effect_id]
        
        # Vérifier les restrictions d'application
        if "applies_to" in effect_def:
            target_type = getattr(target, "type", None)
            if target_type not in effect_def["applies_to"]:
                logger.debug(f"L'effet {effect_id} ne peut pas être appliqué à {getattr(target, 'name', str(target))} (type: {target_type})")
                return False
        
        # Vérifier l'immunité
        if self.is_immune(target, effect_id):
            logger.debug(f"{getattr(target, 'name', str(target))} est immunisé contre {effect_id}")
            return False
        
        # Vérifier la résistance et ajuster la durée
        resistance = self.get_resistance(target, effect_def.get("type", StatusEffectType.DEBUFF))
        if resistance >= 100:
            logger.debug(f"{getattr(target, 'name', str(target))} résiste complètement à {effect_id}")
            return False
        
        # Calculer la durée en fonction de la résistance
        base_duration = effect_def.get("base_duration", 1)
        final_duration = max(1, int(base_duration * duration_modifier * (1 - resistance / 100)))
        
        # Initialiser la liste des effets actifs pour la cible si nécessaire
        if target not in self.active_effects:
            self.active_effects[target] = []
        
        # Vérifier si l'effet est déjà actif
        existing_effect = None
        for effect in self.active_effects[target]:
            if effect["id"] == effect_id:
                existing_effect = effect
                break
        
        # Si l'effet est déjà actif et qu'il est cumulable
        if existing_effect and effect_def.get("stackable", False):
            # Incrémenter le nombre de cumuls
            existing_effect["stacks"] = min(existing_effect.get("stacks", 1) + 1, 
                                           effect_def.get("max_stacks", 1))
            
            # Mettre à jour la durée si la nouvelle est plus longue
            existing_effect["duration"] = max(existing_effect["duration"], final_duration)
            
            # Appliquer la fonction de cumul si elle existe
            if "on_stack" in effect_def and callable(effect_def["on_stack"]):
                existing_effect["power"] = effect_def["on_stack"](existing_effect)
            
            logger.debug(f"Effet {effect_id} cumulé sur {getattr(target, 'name', str(target))} "
                        f"(cumuls: {existing_effect['stacks']}, durée: {existing_effect['duration']})")
            return True
        
        # Si l'effet n'est pas cumulable et qu'il est déjà actif, mettre à jour la durée
        elif existing_effect:
            existing_effect["duration"] = max(existing_effect["duration"], final_duration)
            logger.debug(f"Durée de l'effet {effect_id} mise à jour pour {getattr(target, 'name', str(target))} "
                        f"(nouvelle durée: {existing_effect['duration']})")
            return True
        
        # Sinon, créer un nouvel effet
        else:
            # Calculer la puissance de l'effet en fonction du niveau
            power = None
            if "damage_per_turn" in effect_def and callable(effect_def["damage_per_turn"]):
                power = effect_def["damage_per_turn"](level)
            elif "heal_per_turn" in effect_def and callable(effect_def["heal_per_turn"]):
                power = effect_def["heal_per_turn"](level)
            
            # Créer l'effet
            new_effect = {
                "id": effect_id,
                "name": effect_def.get("name", effect_id),
                "type": effect_def.get("type", StatusEffectType.DEBUFF),
                "duration": final_duration,
                "source": source,
                "level": level,
                "power": power,
                "stacks": 1 if effect_def.get("stackable", False) else None,
                "icon": effect_def.get("icon", "default_effect")
            }
            
            # Ajouter les propriétés spécifiques
            for key, value in effect_def.items():
                if key not in ["name", "description", "type", "base_duration", "icon", 
                              "stackable", "max_stacks", "on_stack", "damage_per_turn", 
                              "heal_per_turn", "applies_to", "can_be_cleansed"]:
                    new_effect[key] = value
            
            # Ajouter l'effet à la liste
            self.active_effects[target].append(new_effect)
            
            logger.debug(f"Effet {effect_id} appliqué à {getattr(target, 'name', str(target))} "
                        f"(durée: {final_duration}, niveau: {level})")
            return True
    
    def remove_effect(self, target: Any, effect_id: str) -> bool:
        """
        Supprime un effet de statut d'une cible
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet à supprimer
            
        Returns:
            True si l'effet a été supprimé, False sinon
        """
        # Vérifier si la cible a des effets actifs
        if target not in self.active_effects:
            return False
        
        # Rechercher l'effet
        for effect in self.active_effects[target][:]:  # Copie de la liste pour éviter les problèmes de modification pendant l'itération
            if effect["id"] == effect_id:
                self.active_effects[target].remove(effect)
                logger.debug(f"Effet {effect_id} supprimé de {getattr(target, 'name', str(target))}")
                return True
        
        return False
    
    def cleanse_effects(self, target: Any, effect_types: List[StatusEffectType] = None) -> int:
        """
        Supprime tous les effets négatifs d'une cible
        
        Args:
            target: La cible
            effect_types: Types d'effets à supprimer (tous les débuffs par défaut)
            
        Returns:
            Nombre d'effets supprimés
        """
        if target not in self.active_effects:
            return 0
        
        # Types d'effets à supprimer par défaut
        if effect_types is None:
            effect_types = [StatusEffectType.DEBUFF, StatusEffectType.DAMAGE_OVER_TIME, 
                           StatusEffectType.CONTROL]
        
        count = 0
        for effect in self.active_effects[target][:]:  # Copie de la liste
            # Vérifier si l'effet peut être nettoyé
            effect_def = self.effect_definitions.get(effect["id"], {})
            if (effect["type"] in effect_types and 
                effect_def.get("can_be_cleansed", True)):
                self.active_effects[target].remove(effect)
                count += 1
        
        if count > 0:
            logger.debug(f"{count} effets supprimés de {getattr(target, 'name', str(target))}")
        
        return count
    
    def update_effects(self, target: Any) -> Dict[str, Any]:
        """
        Met à jour les effets actifs pour une cible (réduction de la durée, application des effets)
        
        Args:
            target: La cible
            
        Returns:
            Résultat des effets appliqués
        """
        if target not in self.active_effects:
            return {"damage": 0, "healing": 0, "effects_expired": []}
        
        total_damage = 0
        total_healing = 0
        effects_expired = []
        
        # Traiter chaque effet
        for effect in self.active_effects[target][:]:  # Copie de la liste
            # Appliquer les effets de dégâts sur la durée
            if effect["type"] == StatusEffectType.DAMAGE_OVER_TIME and "power" in effect:
                damage = effect["power"]
                damage_type = effect.get("damage_type", "PHYSICAL")
                
                # Appliquer les résistances
                resistance = getattr(target, f"resistance_{damage_type.lower()}", 0)
                final_damage = max(1, int(damage * (1 - resistance / 100)))
                
                # Infliger les dégâts
                target.health -= final_damage
                total_damage += final_damage
                
                logger.debug(f"{effect['name']} inflige {final_damage} dégâts à {getattr(target, 'name', str(target))}")
            
            # Appliquer les effets de soins sur la durée
            elif effect["type"] == StatusEffectType.HEAL_OVER_TIME and "power" in effect:
                healing = effect["power"]
                
                # Appliquer les soins
                target.health = min(target.health + healing, target.max_health)
                total_healing += healing
                
                logger.debug(f"{effect['name']} soigne {healing} PV à {getattr(target, 'name', str(target))}")
            
            # Réduire la durée
            effect["duration"] -= 1
            
            # Supprimer les effets expirés
            if effect["duration"] <= 0:
                self.active_effects[target].remove(effect)
                effects_expired.append(effect["id"])
                logger.debug(f"Effet {effect['name']} expiré pour {getattr(target, 'name', str(target))}")
        
        return {
            "damage": total_damage,
            "healing": total_healing,
            "effects_expired": effects_expired
        }
    
    def get_active_effects(self, target: Any) -> List[Dict[str, Any]]:
        """
        Récupère la liste des effets actifs pour une cible
        
        Args:
            target: La cible
            
        Returns:
            Liste des effets actifs
        """
        return self.active_effects.get(target, [])
    
    def has_effect(self, target: Any, effect_id: str) -> bool:
        """
        Vérifie si une cible a un effet spécifique
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet
            
        Returns:
            True si l'effet est actif, False sinon
        """
        for effect in self.active_effects.get(target, []):
            if effect["id"] == effect_id:
                return True
        return False
    
    def get_effect_stacks(self, target: Any, effect_id: str) -> int:
        """
        Récupère le nombre de cumuls d'un effet
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet
            
        Returns:
            Nombre de cumuls (0 si l'effet n'est pas actif)
        """
        for effect in self.active_effects.get(target, []):
            if effect["id"] == effect_id:
                return effect.get("stacks", 1)
        return 0
    
    def add_immunity(self, target: Any, effect_id: str) -> None:
        """
        Ajoute une immunité à un effet
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet
        """
        if target not in self.immunities:
            self.immunities[target] = []
            
        if effect_id not in self.immunities[target]:
            self.immunities[target].append(effect_id)
            logger.debug(f"{getattr(target, 'name', str(target))} est maintenant immunisé contre {effect_id}")
    
    def remove_immunity(self, target: Any, effect_id: str) -> None:
        """
        Supprime une immunité
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet
        """
        if target in self.immunities and effect_id in self.immunities[target]:
            self.immunities[target].remove(effect_id)
            logger.debug(f"Immunité contre {effect_id} supprimée pour {getattr(target, 'name', str(target))}")
    
    def is_immune(self, target: Any, effect_id: str) -> bool:
        """
        Vérifie si une cible est immunisée contre un effet
        
        Args:
            target: La cible
            effect_id: Identifiant de l'effet
            
        Returns:
            True si la cible est immunisée, False sinon
        """
        return target in self.immunities and effect_id in self.immunities[target]
    
    def add_resistance(self, target: Any, effect_type: StatusEffectType, value: int) -> None:
        """
        Ajoute une résistance à un type d'effet
        
        Args:
            target: La cible
            effect_type: Type d'effet
            value: Valeur de résistance (pourcentage)
        """
        if target not in self.resistances:
            self.resistances[target] = {}
            
        current = self.resistances[target].get(effect_type, 0)
        self.resistances[target][effect_type] = min(100, current + value)
        
        logger.debug(f"{getattr(target, 'name', str(target))} a maintenant {self.resistances[target][effect_type]}% "
                    f"de résistance aux effets de type {effect_type.name}")
    
    def get_resistance(self, target: Any, effect_type: StatusEffectType) -> int:
        """
        Récupère la résistance d'une cible à un type d'effet
        
        Args:
            target: La cible
            effect_type: Type d'effet
            
        Returns:
            Valeur de résistance (pourcentage)
        """
        if target not in self.resistances:
            return 0
            
        return self.resistances[target].get(effect_type, 0)
    
    def get_stat_modifiers(self, target: Any) -> Dict[str, int]:
        """
        Récupère les modificateurs de statistiques dus aux effets actifs
        
        Args:
            target: La cible
            
        Returns:
            Dictionnaire des modificateurs (stat -> valeur)
        """
        modifiers = {}
        
        for effect in self.active_effects.get(target, []):
            # Vérifier si l'effet a des modificateurs de stats
            if "stat_modifiers" in effect:
                for stat, value in effect["stat_modifiers"].items():
                    modifiers[stat] = modifiers.get(stat, 0) + value
        
        return modifiers
    
    def get_damage_modifiers(self, target: Any, is_attacker: bool = True) -> float:
        """
        Récupère les modificateurs de dégâts dus aux effets actifs
        
        Args:
            target: La cible
            is_attacker: True si la cible est l'attaquant, False si elle est la victime
            
        Returns:
            Multiplicateur de dégâts
        """
        modifier = 1.0
        
        for effect in self.active_effects.get(target, []):
            # Modificateur pour les dégâts infligés (attaquant)
            if is_attacker and "damage_dealt_modifier" in effect:
                if callable(effect["damage_dealt_modifier"]):
                    modifier *= effect["damage_dealt_modifier"](effect.get("stacks", 1))
                else:
                    modifier *= effect["damage_dealt_modifier"]
            
            # Modificateur pour les dégâts subis (victime)
            elif not is_attacker and "damage_taken_modifier" in effect:
                if callable(effect["damage_taken_modifier"]):
                    modifier *= effect["damage_taken_modifier"](effect.get("stacks", 1))
                else:
                    modifier *= effect["damage_taken_modifier"]
        
        return modifier
    
    def can_act(self, target: Any) -> bool:
        """
        Vérifie si une cible peut agir (non affectée par des effets de contrôle)
        
        Args:
            target: La cible
            
        Returns:
            True si la cible peut agir, False sinon
        """
        for effect in self.active_effects.get(target, []):
            if effect.get("prevents_actions", False):
                return False
        return True
    
    def can_move(self, target: Any) -> bool:
        """
        Vérifie si une cible peut se déplacer
        
        Args:
            target: La cible
            
        Returns:
            True si la cible peut se déplacer, False sinon
        """
        for effect in self.active_effects.get(target, []):
            if effect.get("prevents_movement", False):
                return False
        return True
    
    def get_action_failure_chance(self, target: Any) -> float:
        """
        Récupère la chance d'échec des actions due aux effets actifs
        
        Args:
            target: La cible
            
        Returns:
            Chance d'échec (0.0 - 1.0)
        """
        failure_chance = 0.0
        
        for effect in self.active_effects.get(target, []):
            failure_chance = max(failure_chance, effect.get("action_failure_chance", 0.0))
        
        return failure_chance
    
    def get_friendly_fire_chance(self, target: Any) -> float:
        """
        Récupère la chance de tir ami due aux effets actifs
        
        Args:
            target: La cible
            
        Returns:
            Chance de tir ami (0.0 - 1.0)
        """
        friendly_fire_chance = 0.0
        
        for effect in self.active_effects.get(target, []):
            friendly_fire_chance = max(friendly_fire_chance, effect.get("friendly_fire_chance", 0.0))
        
        return friendly_fire_chance
    
    def get_critical_chance_modifier(self, target: Any) -> float:
        """
        Récupère le modificateur de chance de coup critique
        
        Args:
            target: La cible
            
        Returns:
            Modificateur de chance de coup critique
        """
        modifier = 0.0
        
        for effect in self.active_effects.get(target, []):
            modifier += effect.get("crit_chance_modifier", 0.0)
        
        return modifier
    
    def reset_combat_effects(self) -> None:
        """Réinitialise tous les effets de combat"""
        self.active_effects = {}
