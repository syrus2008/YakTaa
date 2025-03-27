"""
Système de combat tactique pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.Tactical")

class CoverType(Enum):
    """Types de couverture disponibles en combat"""
    NONE = auto()
    PARTIAL = auto()  # Couverture partielle (25% de réduction des dégâts)
    MEDIUM = auto()   # Couverture moyenne (50% de réduction des dégâts)
    HEAVY = auto()    # Couverture lourde (75% de réduction des dégâts)

class Position(Enum):
    """Positions possibles en combat"""
    PRONE = auto()    # Au sol (bonus défense, malus attaque)
    CROUCHED = auto() # Accroupi (bonus discrétion, malus mobilité)
    STANDING = auto() # Debout (position standard)
    ELEVATED = auto() # En hauteur (bonus attaque, malus défense)

class TacticalCombatSystem:
    """
    Système de combat tactique qui gère les positions, couvertures et zones de contrôle
    """
    
    def __init__(self):
        """Initialise le système de combat tactique"""
        self.cover_status = {}  # Acteur -> type de couverture
        self.positions = {}     # Acteur -> position
        self.control_zones = {} # Acteur -> liste de zones contrôlées
        self.flanking = {}      # Acteur -> liste d'acteurs qu'il prend à revers
        
        logger.debug("Système de combat tactique initialisé")
    
    def set_cover(self, actor: Any, cover_type: CoverType) -> None:
        """
        Définit le type de couverture d'un acteur
        
        Args:
            actor: L'acteur concerné
            cover_type: Type de couverture
        """
        self.cover_status[actor] = cover_type
        logger.debug(f"{getattr(actor, 'name', str(actor))} est maintenant en couverture {cover_type.name}")
    
    def get_cover_damage_reduction(self, actor: Any) -> float:
        """
        Calcule la réduction de dégâts due à la couverture
        
        Args:
            actor: L'acteur concerné
            
        Returns:
            Multiplicateur de dégâts (1.0 = pas de réduction)
        """
        cover_type = self.cover_status.get(actor, CoverType.NONE)
        
        if cover_type == CoverType.PARTIAL:
            return 0.75  # 25% de réduction
        elif cover_type == CoverType.MEDIUM:
            return 0.5   # 50% de réduction
        elif cover_type == CoverType.HEAVY:
            return 0.25  # 75% de réduction
        else:
            return 1.0   # Pas de réduction
    
    def set_position(self, actor: Any, position: Position) -> None:
        """
        Définit la position d'un acteur
        
        Args:
            actor: L'acteur concerné
            position: Position à adopter
        """
        self.positions[actor] = position
        logger.debug(f"{getattr(actor, 'name', str(actor))} est maintenant en position {position.name}")
    
    def get_position_modifiers(self, actor: Any) -> Dict[str, float]:
        """
        Récupère les modificateurs liés à la position
        
        Args:
            actor: L'acteur concerné
            
        Returns:
            Dictionnaire de modificateurs
        """
        position = self.positions.get(actor, Position.STANDING)
        
        if position == Position.PRONE:
            return {
                "attack": 0.8,    # -20% aux attaques
                "defense": 1.2,   # +20% à la défense
                "mobility": 0.5,  # -50% à la mobilité
                "stealth": 1.5    # +50% à la discrétion
            }
        elif position == Position.CROUCHED:
            return {
                "attack": 0.9,    # -10% aux attaques
                "defense": 1.1,   # +10% à la défense
                "mobility": 0.8,  # -20% à la mobilité
                "stealth": 1.3    # +30% à la discrétion
            }
        elif position == Position.ELEVATED:
            return {
                "attack": 1.2,    # +20% aux attaques
                "defense": 0.9,   # -10% à la défense
                "mobility": 0.7,  # -30% à la mobilité
                "stealth": 0.8    # -20% à la discrétion
            }
        else:  # STANDING
            return {
                "attack": 1.0,
                "defense": 1.0,
                "mobility": 1.0,
                "stealth": 1.0
            }
    
    def add_control_zone(self, actor: Any, zone_id: str, radius: int = 2) -> None:
        """
        Ajoute une zone de contrôle pour un acteur
        
        Args:
            actor: L'acteur qui contrôle la zone
            zone_id: Identifiant de la zone
            radius: Rayon de la zone en unités
        """
        if actor not in self.control_zones:
            self.control_zones[actor] = []
            
        self.control_zones[actor].append({
            "id": zone_id,
            "radius": radius
        })
        
        logger.debug(f"{getattr(actor, 'name', str(actor))} contrôle maintenant la zone {zone_id} (rayon: {radius})")
    
    def is_in_control_zone(self, actor: Any, target_position: Tuple[int, int]) -> List[Any]:
        """
        Vérifie si une position est dans une zone de contrôle
        
        Args:
            actor: L'acteur à exclure (on ne vérifie pas ses propres zones)
            target_position: Position à vérifier (x, y)
            
        Returns:
            Liste des acteurs qui contrôlent cette position
        """
        controllers = []
        
        for controller, zones in self.control_zones.items():
            # Ne pas compter ses propres zones
            if controller == actor:
                continue
                
            # Position du contrôleur
            controller_position = getattr(controller, "position", (0, 0))
            
            # Vérifier chaque zone
            for zone in zones:
                # Calculer la distance
                distance = self._calculate_distance(controller_position, target_position)
                
                # Vérifier si la position est dans la zone
                if distance <= zone["radius"]:
                    controllers.append(controller)
                    break  # Un acteur ne peut contrôler qu'une fois
        
        return controllers
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calcule la distance entre deux positions"""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def set_flanking(self, actor: Any, target: Any, is_flanking: bool) -> None:
        """
        Définit si un acteur prend un autre acteur à revers
        
        Args:
            actor: L'acteur qui prend à revers
            target: La cible prise à revers
            is_flanking: True si la cible est prise à revers
        """
        if actor not in self.flanking:
            self.flanking[actor] = []
            
        if is_flanking:
            if target not in self.flanking[actor]:
                self.flanking[actor].append(target)
                logger.debug(f"{getattr(actor, 'name', str(actor))} prend {getattr(target, 'name', str(target))} à revers")
        else:
            if target in self.flanking[actor]:
                self.flanking[actor].remove(target)
                logger.debug(f"{getattr(actor, 'name', str(actor))} ne prend plus {getattr(target, 'name', str(target))} à revers")
    
    def get_flanking_bonus(self, actor: Any, target: Any) -> float:
        """
        Récupère le bonus d'attaque pour prendre à revers
        
        Args:
            actor: L'attaquant
            target: La cible
            
        Returns:
            Multiplicateur de dégâts
        """
        if actor in self.flanking and target in self.flanking[actor]:
            return 1.5  # +50% de dégâts en prenant à revers
        else:
            return 1.0
    
    def get_tactical_advantage(self, actor: Any, target: Any) -> Dict[str, Any]:
        """
        Calcule l'avantage tactique global d'un acteur sur une cible
        
        Args:
            actor: L'attaquant
            target: La cible
            
        Returns:
            Dictionnaire d'avantages tactiques
        """
        # Récupérer les modificateurs de position
        position_mods = self.get_position_modifiers(actor)
        target_position_mods = self.get_position_modifiers(target)
        
        # Calculer la réduction de dégâts due à la couverture
        cover_reduction = self.get_cover_damage_reduction(target)
        
        # Vérifier si la cible est prise à revers
        flanking_bonus = self.get_flanking_bonus(actor, target)
        
        # Calculer l'avantage final
        attack_modifier = position_mods["attack"] * flanking_bonus
        defense_modifier = target_position_mods["defense"] * cover_reduction
        
        # Rapport attaque/défense
        advantage_ratio = attack_modifier / defense_modifier if defense_modifier > 0 else attack_modifier
        
        return {
            "attack_modifier": attack_modifier,
            "defense_modifier": defense_modifier,
            "advantage_ratio": advantage_ratio,
            "is_flanking": flanking_bonus > 1.0,
            "cover_reduction": cover_reduction,
            "position_attack": position_mods["attack"],
            "position_defense": target_position_mods["defense"]
        }
    
    def apply_tactical_modifiers(self, base_damage: int, actor: Any, target: Any) -> int:
        """
        Applique les modificateurs tactiques aux dégâts
        
        Args:
            base_damage: Dégâts de base
            actor: L'attaquant
            target: La cible
            
        Returns:
            Dégâts modifiés
        """
        advantage = self.get_tactical_advantage(actor, target)
        
        # Appliquer les modificateurs
        modified_damage = base_damage * advantage["attack_modifier"] / advantage["defense_modifier"]
        
        # Arrondir au nombre entier
        return int(modified_damage)
    
    def reset_combat_positions(self) -> None:
        """Réinitialise les positions de combat"""
        self.cover_status = {}
        self.positions = {}
        self.control_zones = {}
        self.flanking = {}
