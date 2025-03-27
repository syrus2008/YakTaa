#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion des effets de statut pour le système de combat YakTaa
"""

import logging
import json
import uuid
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Callable, Any

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Combat.StatusEffects")

class StatusEffectType(Enum):
    """Types d'effets de statut disponibles"""
    BUFF = auto()          # Effet positif (augmentation des statistiques)
    DEBUFF = auto()        # Effet négatif (diminution des statistiques)
    DOT = auto()           # Damage Over Time (dégâts sur la durée)
    HOT = auto()           # Heal Over Time (guérison sur la durée)
    CC = auto()            # Crowd Control (contrôle: stun, immobilisation, etc.)
    SPECIAL = auto()       # Effets spéciaux divers


class DamageType(Enum):
    """Types de dégâts disponibles"""
    PHYSICAL = auto()      # Dégâts physiques (coups, balles, etc.)
    ENERGY = auto()        # Dégâts énergétiques (laser, électrique, etc.)
    EMP = auto()           # Dégâts électromagnétiques (contre électronique)
    BIOHAZARD = auto()     # Dégâts biologiques (poison, acide, etc.)
    CYBER = auto()         # Dégâts aux systèmes cyber (hacking, etc.)
    VIRAL = auto()         # Dégâts par virus informatiques
    NANITE = auto()        # Dégâts par nanites (micro-machines)
    MENTAL = auto()        # Dégâts mentaux/psychiques
    PURE = auto()          # Dégâts purs (ignorent les résistances)


class StatusEffect:
    """
    Classe de base pour tous les effets de statut
    
    Attributes:
        id: Identifiant unique de l'effet
        name: Nom de l'effet
        description: Description de l'effet
        icon_name: Nom de l'icône à afficher
        effect_type: Type d'effet (buff, debuff, etc.)
        duration: Durée en tours (0 = permanent jusqu'à suppression)
        stacks: Nombre de stacks de l'effet (si cumulable)
        max_stacks: Nombre maximum de stacks (si cumulable)
        is_visible: Si l'effet est visible dans l'interface
        is_removable: Si l'effet peut être supprimé
        source_id: ID de la source de l'effet (personnage, objet, etc.)
        target_id: ID de la cible de l'effet
        custom_data: Données personnalisées pour l'effet
    """
    
    def __init__(self, name: str, description: str = "", 
                 effect_type: StatusEffectType = StatusEffectType.DEBUFF,
                 duration: int = 1, stacks: int = 1, max_stacks: int = 1,
                 is_visible: bool = True, is_removable: bool = True,
                 source_id: str = None, target_id: str = None,
                 icon_name: str = "default_effect", custom_data: Dict = None):
        """
        Initialise un nouvel effet de statut
        
        Args:
            name: Nom de l'effet
            description: Description de l'effet
            effect_type: Type d'effet (buff, debuff, etc.)
            duration: Durée en tours (0 = permanent jusqu'à suppression)
            stacks: Nombre de stacks de l'effet (si cumulable)
            max_stacks: Nombre maximum de stacks (si cumulable)
            is_visible: Si l'effet est visible dans l'interface
            is_removable: Si l'effet peut être supprimé
            source_id: ID de la source de l'effet (personnage, objet, etc.)
            target_id: ID de la cible de l'effet
            icon_name: Nom de l'icône à afficher
            custom_data: Données personnalisées pour l'effet
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.icon_name = icon_name
        self.effect_type = effect_type
        self.duration = duration
        self.stacks = stacks
        self.max_stacks = max(1, max_stacks)
        self.is_visible = is_visible
        self.is_removable = is_removable
        self.source_id = source_id
        self.target_id = target_id
        self.custom_data = custom_data or {}
        self.remaining_duration = duration
        
    def on_apply(self, target: Dict) -> Dict:
        """
        Appelé lorsque l'effet est appliqué
        
        Args:
            target: Dictionnaire des données de la cible
            
        Returns:
            Dictionnaire des données de la cible modifiées
        """
        return target
    
    def on_remove(self, target: Dict) -> Dict:
        """
        Appelé lorsque l'effet est retiré
        
        Args:
            target: Dictionnaire des données de la cible
            
        Returns:
            Dictionnaire des données de la cible modifiées
        """
        return target
    
    def on_turn_start(self, target: Dict) -> Dict:
        """
        Appelé au début du tour de la cible
        
        Args:
            target: Dictionnaire des données de la cible
            
        Returns:
            Dictionnaire des données de la cible modifiées
        """
        return target
    
    def on_turn_end(self, target: Dict) -> Dict:
        """
        Appelé à la fin du tour de la cible
        
        Args:
            target: Dictionnaire des données de la cible
            
        Returns:
            Dictionnaire des données de la cible modifiées
        """
        if self.duration > 0:
            self.remaining_duration -= 1
        return target
    
    def is_expired(self) -> bool:
        """
        Vérifie si l'effet est expiré
        
        Returns:
            True si l'effet est expiré, False sinon
        """
        return self.duration > 0 and self.remaining_duration <= 0
    
    def add_stack(self, count: int = 1) -> int:
        """
        Ajoute des stacks à l'effet
        
        Args:
            count: Nombre de stacks à ajouter
            
        Returns:
            Nombre de stacks après ajout
        """
        self.stacks = min(self.stacks + count, self.max_stacks)
        return self.stacks
    
    def remove_stack(self, count: int = 1) -> int:
        """
        Retire des stacks à l'effet
        
        Args:
            count: Nombre de stacks à retirer
            
        Returns:
            Nombre de stacks après retrait
        """
        self.stacks = max(0, self.stacks - count)
        return self.stacks
    
    def reset_duration(self, new_duration: Optional[int] = None) -> int:
        """
        Réinitialise la durée de l'effet
        
        Args:
            new_duration: Nouvelle durée (utilise la durée initiale si None)
            
        Returns:
            Nouvelle durée restante
        """
        if new_duration is not None:
            self.duration = new_duration
            self.remaining_duration = new_duration
        else:
            self.remaining_duration = self.duration
            
        return self.remaining_duration
    
    def to_dict(self) -> Dict:
        """
        Convertit l'effet en dictionnaire pour stockage
        
        Returns:
            Dictionnaire représentant l'effet
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_name": self.icon_name,
            "effect_type": self.effect_type.name,
            "duration": self.duration,
            "remaining_duration": self.remaining_duration,
            "stacks": self.stacks,
            "max_stacks": self.max_stacks,
            "is_visible": self.is_visible,
            "is_removable": self.is_removable,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "custom_data": self.custom_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StatusEffect':
        """
        Crée un effet à partir d'un dictionnaire
        
        Args:
            data: Dictionnaire représentant l'effet
            
        Returns:
            Instance de StatusEffect
        """
        effect = cls(
            name=data["name"],
            description=data.get("description", ""),
            effect_type=StatusEffectType[data["effect_type"]],
            duration=data["duration"],
            stacks=data["stacks"],
            max_stacks=data["max_stacks"],
            is_visible=data["is_visible"],
            is_removable=data["is_removable"],
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            icon_name=data.get("icon_name", "default_effect"),
            custom_data=data.get("custom_data", {})
        )
        effect.id = data["id"]
        effect.remaining_duration = data["remaining_duration"]
        return effect


class StatModifier(StatusEffect):
    """Effet qui modifie une ou plusieurs statistiques"""
    
    def __init__(self, name: str, modifiers: Dict[str, Union[int, float]], 
                 is_percentage: bool = False, **kwargs):
        """
        Initialise un modificateur de statistiques
        
        Args:
            name: Nom de l'effet
            modifiers: Dictionnaire des modificateurs (stat: valeur)
            is_percentage: Si True, les modificateurs sont des pourcentages
            **kwargs: Arguments supplémentaires pour StatusEffect
        """
        super().__init__(name, **kwargs)
        self.modifiers = modifiers
        self.is_percentage = is_percentage
        self.applied_modifiers = {}
    
    def on_apply(self, target: Dict) -> Dict:
        """Applique les modificateurs lors de l'application de l'effet"""
        for stat, value in self.modifiers.items():
            if stat in target:
                original_value = target[stat]
                
                if self.is_percentage:
                    if isinstance(original_value, (int, float)):
                        # Calculer la modification comme un pourcentage
                        modifier = original_value * (value / 100.0)
                        target[stat] += modifier
                        self.applied_modifiers[stat] = modifier
                else:
                    # Modification directe
                    target[stat] += value
                    self.applied_modifiers[stat] = value
                    
        return target
    
    def on_remove(self, target: Dict) -> Dict:
        """Retire les modificateurs lors du retrait de l'effet"""
        for stat, value in self.applied_modifiers.items():
            if stat in target:
                target[stat] -= value
                
        self.applied_modifiers = {}
        return target


class DamageOverTime(StatusEffect):
    """Effet qui inflige des dégâts sur la durée"""
    
    def __init__(self, name: str, damage_per_turn: int, 
                 damage_type: DamageType = DamageType.PHYSICAL, **kwargs):
        """
        Initialise un effet de dégâts sur la durée
        
        Args:
            name: Nom de l'effet
            damage_per_turn: Dégâts infligés par tour
            damage_type: Type de dégâts
            **kwargs: Arguments supplémentaires pour StatusEffect
        """
        super().__init__(name, effect_type=StatusEffectType.DOT, **kwargs)
        self.damage_per_turn = damage_per_turn
        self.damage_type = damage_type
    
    def on_turn_end(self, target: Dict) -> Dict:
        """Inflige des dégâts à la fin du tour"""
        # Calculer les dégâts en fonction des stacks
        total_damage = self.damage_per_turn * self.stacks
        
        # Appliquer la résistance appropriée en fonction du type de dégâts
        resistance_key = f"resistance_{self.damage_type.name.lower()}"
        if resistance_key in target:
            resistance = target[resistance_key] / 100.0  # Convertir le pourcentage
            total_damage = max(1, int(total_damage * (1 - resistance)))
        
        # Appliquer les dégâts
        if "health" in target:
            target["health"] = max(0, target["health"] - total_damage)
            
        # Log pour le débogage
        logger.debug(f"DoT {self.name} inflige {total_damage} dégâts à {target.get('name', 'cible')}")
        
        # Mettre à jour la durée
        return super().on_turn_end(target)


class HealOverTime(StatusEffect):
    """Effet qui soigne sur la durée"""
    
    def __init__(self, name: str, heal_per_turn: int, **kwargs):
        """
        Initialise un effet de soin sur la durée
        
        Args:
            name: Nom de l'effet
            heal_per_turn: Soins apportés par tour
            **kwargs: Arguments supplémentaires pour StatusEffect
        """
        super().__init__(name, effect_type=StatusEffectType.HOT, **kwargs)
        self.heal_per_turn = heal_per_turn
    
    def on_turn_start(self, target: Dict) -> Dict:
        """Applique les soins au début du tour"""
        # Calculer les soins en fonction des stacks
        total_heal = self.heal_per_turn * self.stacks
        
        # Appliquer les soins
        if "health" in target and "max_health" in target:
            target["health"] = min(target["max_health"], target["health"] + total_heal)
            
        # Log pour le débogage
        logger.debug(f"HoT {self.name} soigne {total_heal} PV à {target.get('name', 'cible')}")
        
        return target


class CrowdControl(StatusEffect):
    """Effet de contrôle (stun, immobilisation, etc.)"""
    
    def __init__(self, name: str, cc_type: str, **kwargs):
        """
        Initialise un effet de contrôle
        
        Args:
            name: Nom de l'effet
            cc_type: Type de contrôle (stun, root, silence, etc.)
            **kwargs: Arguments supplémentaires pour StatusEffect
        """
        super().__init__(name, effect_type=StatusEffectType.CC, **kwargs)
        self.cc_type = cc_type
    
    def on_apply(self, target: Dict) -> Dict:
        """Applique l'effet de contrôle"""
        # Ajouter l'état de contrôle à la cible
        if "status_flags" not in target:
            target["status_flags"] = {}
            
        target["status_flags"][self.cc_type] = True
        
        # Appliquer des effets spécifiques selon le type
        if self.cc_type == "stun":
            # Stun: ne peut pas agir
            target["can_act"] = False
        elif self.cc_type == "root":
            # Root: ne peut pas se déplacer
            target["can_move"] = False
        elif self.cc_type == "silence":
            # Silence: ne peut pas utiliser de capacités spéciales
            target["can_use_abilities"] = False
            
        return target
    
    def on_remove(self, target: Dict) -> Dict:
        """Retire l'effet de contrôle"""
        # Supprimer l'état de contrôle
        if "status_flags" in target and self.cc_type in target["status_flags"]:
            del target["status_flags"][self.cc_type]
            
        # Restaurer les capacités
        if self.cc_type == "stun":
            target["can_act"] = True
        elif self.cc_type == "root":
            target["can_move"] = True
        elif self.cc_type == "silence":
            target["can_use_abilities"] = True
            
        return target


class StatusEffectFactory:
    """Fabrique pour créer des effets prédéfinis"""
    
    @staticmethod
    def create_bleeding(source_id: str = None, target_id: str = None, 
                       duration: int = 3, damage: int = 5) -> StatusEffect:
        """Crée un effet de saignement"""
        return DamageOverTime(
            name="Saignement",
            description="La cible perd des points de vie à chaque tour",
            damage_per_turn=damage,
            damage_type=DamageType.PHYSICAL,
            duration=duration,
            icon_name="effect_bleeding",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_poison(source_id: str = None, target_id: str = None,
                     duration: int = 4, damage: int = 4) -> StatusEffect:
        """Crée un effet de poison"""
        return DamageOverTime(
            name="Poison",
            description="La cible est empoisonnée et perd des points de vie à chaque tour",
            damage_per_turn=damage,
            damage_type=DamageType.BIOHAZARD,
            duration=duration,
            icon_name="effect_poison",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_burn(source_id: str = None, target_id: str = None,
                   duration: int = 3, damage: int = 6) -> StatusEffect:
        """Crée un effet de brûlure"""
        return DamageOverTime(
            name="Brûlure",
            description="La cible est en feu et perd des points de vie à chaque tour",
            damage_per_turn=damage,
            damage_type=DamageType.ENERGY,
            duration=duration,
            icon_name="effect_burn",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_stun(source_id: str = None, target_id: str = None,
                   duration: int = 1) -> StatusEffect:
        """Crée un effet d'étourdissement"""
        return CrowdControl(
            name="Étourdissement",
            description="La cible est étourdie et ne peut pas agir",
            cc_type="stun",
            duration=duration,
            icon_name="effect_stun",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_weakness(source_id: str = None, target_id: str = None,
                       duration: int = 2, penalty: int = 25) -> StatusEffect:
        """Crée un effet de faiblesse"""
        return StatModifier(
            name="Faiblesse",
            description=f"La cible a {penalty}% de dégâts en moins",
            modifiers={"damage": -penalty},
            is_percentage=True,
            duration=duration,
            icon_name="effect_weakness",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_strength(source_id: str = None, target_id: str = None,
                       duration: int = 3, bonus: int = 20) -> StatusEffect:
        """Crée un effet de force"""
        return StatModifier(
            name="Force",
            description=f"La cible a {bonus}% de dégâts en plus",
            modifiers={"damage": bonus},
            is_percentage=True,
            effect_type=StatusEffectType.BUFF,
            duration=duration,
            icon_name="effect_strength",
            source_id=source_id,
            target_id=target_id
        )
    
    @staticmethod
    def create_regeneration(source_id: str = None, target_id: str = None,
                          duration: int = 3, heal: int = 5) -> StatusEffect:
        """Crée un effet de régénération"""
        return HealOverTime(
            name="Régénération",
            description="La cible récupère des points de vie à chaque tour",
            heal_per_turn=heal,
            duration=duration,
            icon_name="effect_regeneration",
            effect_type=StatusEffectType.BUFF,
            source_id=source_id,
            target_id=target_id
        )


class StatusEffectManager:
    """Gestionnaire d'effets de statut pour un personnage"""
    
    def __init__(self):
        """Initialise un nouveau gestionnaire d'effets"""
        self.effects: List[StatusEffect] = []
    
    def add_effect(self, effect: StatusEffect) -> bool:
        """
        Ajoute un effet au personnage
        
        Args:
            effect: Effet à ajouter
            
        Returns:
            True si l'effet a été ajouté, False sinon
        """
        # Vérifier si l'effet existe déjà
        existing_effect = self.get_effect_by_name(effect.name)
        
        if existing_effect:
            # Si l'effet existe, renouveler sa durée et ajouter un stack
            existing_effect.reset_duration()
            existing_effect.add_stack()
            return True
        else:
            # Sinon, ajouter le nouvel effet
            self.effects.append(effect)
            return True
    
    def remove_effect(self, effect_id: str) -> bool:
        """
        Retire un effet par son ID
        
        Args:
            effect_id: ID de l'effet à retirer
            
        Returns:
            True si l'effet a été retiré, False sinon
        """
        for i, effect in enumerate(self.effects):
            if effect.id == effect_id:
                self.effects.pop(i)
                return True
        return False
    
    def remove_effect_by_name(self, effect_name: str) -> bool:
        """
        Retire un effet par son nom
        
        Args:
            effect_name: Nom de l'effet à retirer
            
        Returns:
            True si l'effet a été retiré, False sinon
        """
        for i, effect in enumerate(self.effects):
            if effect.name == effect_name:
                self.effects.pop(i)
                return True
        return False
    
    def get_effect(self, effect_id: str) -> Optional[StatusEffect]:
        """
        Récupère un effet par son ID
        
        Args:
            effect_id: ID de l'effet à récupérer
            
        Returns:
            L'effet correspondant, ou None s'il n'existe pas
        """
        for effect in self.effects:
            if effect.id == effect_id:
                return effect
        return None
    
    def get_effect_by_name(self, effect_name: str) -> Optional[StatusEffect]:
        """
        Récupère un effet par son nom
        
        Args:
            effect_name: Nom de l'effet à récupérer
            
        Returns:
            L'effet correspondant, ou None s'il n'existe pas
        """
        for effect in self.effects:
            if effect.name == effect_name:
                return effect
        return None
    
    def get_effects_by_type(self, effect_type: StatusEffectType) -> List[StatusEffect]:
        """
        Récupère tous les effets d'un type donné
        
        Args:
            effect_type: Type d'effet à récupérer
            
        Returns:
            Liste des effets correspondants
        """
        return [effect for effect in self.effects if effect.effect_type == effect_type]
    
    def has_effect(self, effect_name: str) -> bool:
        """
        Vérifie si le personnage a un effet donné
        
        Args:
            effect_name: Nom de l'effet à vérifier
            
        Returns:
            True si l'effet existe, False sinon
        """
        return any(effect.name == effect_name for effect in self.effects)
    
    def has_effect_type(self, effect_type: StatusEffectType) -> bool:
        """
        Vérifie si le personnage a un effet d'un type donné
        
        Args:
            effect_type: Type d'effet à vérifier
            
        Returns:
            True si un effet du type existe, False sinon
        """
        return any(effect.effect_type == effect_type for effect in self.effects)
    
    def update_turn_start(self, target: Dict) -> Dict:
        """
        Met à jour tous les effets au début du tour
        
        Args:
            target: Données du personnage
            
        Returns:
            Données du personnage mises à jour
        """
        for effect in self.effects:
            target = effect.on_turn_start(target)
        return target
    
    def update_turn_end(self, target: Dict) -> Dict:
        """
        Met à jour tous les effets à la fin du tour et retire les effets expirés
        
        Args:
            target: Données du personnage
            
        Returns:
            Données du personnage mises à jour
        """
        # Mettre à jour les effets
        for effect in self.effects:
            target = effect.on_turn_end(target)
        
        # Retirer les effets expirés
        self.effects = [effect for effect in self.effects if not effect.is_expired()]
        
        return target
    
    def clear_all_effects(self, target: Dict) -> Dict:
        """
        Supprime tous les effets du personnage
        
        Args:
            target: Données du personnage
            
        Returns:
            Données du personnage mises à jour
        """
        # Appeler on_remove pour chaque effet
        for effect in self.effects:
            target = effect.on_remove(target)
        
        # Vider la liste d'effets
        self.effects = []
        
        return target
    
    def clear_removable_effects(self, target: Dict) -> Dict:
        """
        Supprime tous les effets supprimables du personnage
        
        Args:
            target: Données du personnage
            
        Returns:
            Données du personnage mises à jour
        """
        # Appeler on_remove pour chaque effet supprimable
        for effect in self.effects[:]:
            if effect.is_removable:
                target = effect.on_remove(target)
                self.effects.remove(effect)
        
        return target
    
    def to_dict(self) -> Dict:
        """
        Convertit le gestionnaire en dictionnaire pour stockage
        
        Returns:
            Dictionnaire représentant le gestionnaire
        """
        return {
            "effects": [effect.to_dict() for effect in self.effects]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StatusEffectManager':
        """
        Crée un gestionnaire à partir d'un dictionnaire
        
        Args:
            data: Dictionnaire représentant le gestionnaire
            
        Returns:
            Instance de StatusEffectManager
        """
        manager = cls()
        
        if "effects" in data:
            for effect_data in data["effects"]:
                # Déterminer le type d'effet
                effect_type = effect_data.get("effect_type", "DEBUFF")
                
                if effect_type == "DOT":
                    effect = DamageOverTime.from_dict(effect_data)
                elif effect_type == "HOT":
                    effect = HealOverTime.from_dict(effect_data)
                elif effect_type == "CC":
                    effect = CrowdControl.from_dict(effect_data)
                else:
                    # Par défaut, utiliser StatModifier ou StatusEffect
                    if "modifiers" in effect_data.get("custom_data", {}):
                        effect = StatModifier.from_dict(effect_data)
                    else:
                        effect = StatusEffect.from_dict(effect_data)
                
                manager.effects.append(effect)
        
        return manager
