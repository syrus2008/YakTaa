"""
Système de défense pour le combat dans YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.Defense")

class DefenseType(Enum):
    """Types de défense disponibles"""
    DODGE = auto()      # Esquive
    PARRY = auto()      # Parade
    BLOCK = auto()      # Blocage
    COUNTER = auto()    # Contre-attaque
    ABSORB = auto()     # Absorption

class DefenseSystem:
    """
    Système qui gère les mécanismes de défense en combat
    """
    
    def __init__(self):
        """Initialise le système de défense"""
        self.defense_stats = {}  # Acteur -> statistiques de défense
        self.defense_history = {}  # Acteur -> historique des défenses
        
        logger.debug("Système de défense initialisé")
    
    def register_actor(self, actor: Any) -> None:
        """
        Enregistre un acteur dans le système de défense
        
        Args:
            actor: L'acteur à enregistrer
        """
        if actor in self.defense_stats:
            return
            
        # Initialiser les statistiques de défense
        self.defense_stats[actor] = {
            "dodge_chance": self._calculate_dodge_chance(actor),
            "parry_chance": self._calculate_parry_chance(actor),
            "block_chance": self._calculate_block_chance(actor),
            "counter_chance": self._calculate_counter_chance(actor),
            "damage_reduction": self._calculate_damage_reduction(actor)
        }
        
        # Initialiser l'historique des défenses
        self.defense_history[actor] = []
        
        logger.debug(f"Acteur {getattr(actor, 'name', str(actor))} enregistré dans le système de défense")
    
    def _calculate_dodge_chance(self, actor: Any) -> float:
        """Calcule la chance d'esquive d'un acteur"""
        base_chance = 0.05  # 5% de base
        
        # Bonus basé sur l'agilité
        if hasattr(actor, "get_effective_stats"):
            stats = actor.get_effective_stats()
            agility = stats.get("agility", 0)
            reflexes = stats.get("reflexes", 0)
            
            # Formule: 5% + 1% par point d'agilité + 0.5% par point de réflexes
            return base_chance + (agility * 0.01) + (reflexes * 0.005)
        
        # Pour les acteurs sans statistiques détaillées
        if hasattr(actor, "agility"):
            return base_chance + (actor.agility * 0.01)
            
        return base_chance
    
    def _calculate_parry_chance(self, actor: Any) -> float:
        """Calcule la chance de parade d'un acteur"""
        # Vérifier si l'acteur a une arme de mêlée
        weapon = self._get_equipped_weapon(actor)
        if not weapon or not hasattr(weapon, "weapon_type") or weapon.weapon_type != "MELEE":
            return 0.0  # Pas de parade sans arme de mêlée
            
        base_chance = 0.1  # 10% de base avec une arme de mêlée
        
        # Bonus basé sur les réflexes et la force
        if hasattr(actor, "get_effective_stats"):
            stats = actor.get_effective_stats()
            reflexes = stats.get("reflexes", 0)
            strength = stats.get("strength", 0)
            
            # Formule: 10% + 0.8% par point de réflexes + 0.4% par point de force
            return base_chance + (reflexes * 0.008) + (strength * 0.004)
        
        # Pour les acteurs sans statistiques détaillées
        if hasattr(actor, "reflexes"):
            return base_chance + (actor.reflexes * 0.008)
            
        return base_chance
    
    def _calculate_block_chance(self, actor: Any) -> float:
        """Calcule la chance de blocage d'un acteur"""
        base_chance = 0.0  # 0% de base sans bouclier
        
        # Vérifier si l'acteur a un bouclier
        if hasattr(actor, "active_equipment") and "shield" in actor.active_equipment:
            shield = actor.active_equipment["shield"]
            if shield:
                base_chance = getattr(shield, "block_chance", 0.15)  # 15% de base avec un bouclier standard
        
        # Bonus basé sur la force et l'endurance
        if hasattr(actor, "get_effective_stats"):
            stats = actor.get_effective_stats()
            strength = stats.get("strength", 0)
            endurance = stats.get("endurance", 0)
            
            # Formule: base + 0.5% par point de force + 0.7% par point d'endurance
            return base_chance + (strength * 0.005) + (endurance * 0.007)
        
        # Pour les acteurs sans statistiques détaillées
        if hasattr(actor, "endurance"):
            return base_chance + (actor.endurance * 0.007)
            
        return base_chance
    
    def _calculate_counter_chance(self, actor: Any) -> float:
        """Calcule la chance de contre-attaque d'un acteur"""
        # La contre-attaque nécessite une parade réussie
        parry_chance = self._calculate_parry_chance(actor)
        if parry_chance <= 0:
            return 0.0
            
        # Chance de contre-attaquer après une parade réussie
        base_counter_chance = 0.3  # 30% de base
        
        # Bonus basé sur les réflexes et la précision
        if hasattr(actor, "get_effective_stats"):
            stats = actor.get_effective_stats()
            reflexes = stats.get("reflexes", 0)
            precision = stats.get("precision", 0)
            
            # Formule: 30% + 0.6% par point de réflexes + 0.8% par point de précision
            return base_counter_chance + (reflexes * 0.006) + (precision * 0.008)
        
        # Pour les acteurs sans statistiques détaillées
        if hasattr(actor, "reflexes"):
            return base_counter_chance + (actor.reflexes * 0.006)
            
        return base_counter_chance
    
    def _calculate_damage_reduction(self, actor: Any) -> float:
        """Calcule la réduction de dégâts passive d'un acteur"""
        base_reduction = 0.0  # 0% de base
        
        # Bonus basé sur l'armure et l'endurance
        if hasattr(actor, "get_effective_stats"):
            stats = actor.get_effective_stats()
            armor = stats.get("armor", 0)
            endurance = stats.get("endurance", 0)
            
            # Formule: 0.5% par point d'armure + 0.2% par point d'endurance
            return base_reduction + (armor * 0.005) + (endurance * 0.002)
        
        # Pour les acteurs sans statistiques détaillées
        if hasattr(actor, "armor"):
            return base_reduction + (actor.armor * 0.005)
            
        return base_reduction
    
    def _get_equipped_weapon(self, actor: Any) -> Optional[Any]:
        """Récupère l'arme équipée d'un acteur"""
        if hasattr(actor, "active_equipment") and "weapon" in actor.active_equipment:
            return actor.active_equipment["weapon"]
        return None
    
    def update_defense_stats(self, actor: Any) -> None:
        """
        Met à jour les statistiques de défense d'un acteur
        
        Args:
            actor: L'acteur concerné
        """
        if actor not in self.defense_stats:
            self.register_actor(actor)
            return
            
        # Mettre à jour les statistiques
        self.defense_stats[actor] = {
            "dodge_chance": self._calculate_dodge_chance(actor),
            "parry_chance": self._calculate_parry_chance(actor),
            "block_chance": self._calculate_block_chance(actor),
            "counter_chance": self._calculate_counter_chance(actor),
            "damage_reduction": self._calculate_damage_reduction(actor)
        }
        
        logger.debug(f"Statistiques de défense mises à jour pour {getattr(actor, 'name', str(actor))}")
    
    def get_defense_stats(self, actor: Any) -> Dict[str, float]:
        """
        Récupère les statistiques de défense d'un acteur
        
        Args:
            actor: L'acteur concerné
            
        Returns:
            Dictionnaire des statistiques de défense
        """
        if actor not in self.defense_stats:
            self.register_actor(actor)
            
        return self.defense_stats[actor]
    
    def process_attack(self, attacker: Any, defender: Any, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une attaque en tenant compte des mécanismes de défense
        
        Args:
            attacker: L'attaquant
            defender: Le défenseur
            attack_data: Données de l'attaque
            
        Returns:
            Résultat de l'attaque après défense
        """
        # Vérifier si le défenseur est enregistré
        if defender not in self.defense_stats:
            self.register_actor(defender)
            
        # Récupérer les statistiques de défense
        defense_stats = self.defense_stats[defender]
        
        # Récupérer les données de l'attaque
        base_damage = attack_data.get("damage", 0)
        is_critical = attack_data.get("critical", False)
        attack_type = attack_data.get("attack_type", "NORMAL")
        
        # Initialiser le résultat
        result = {
            "original_damage": base_damage,
            "final_damage": base_damage,
            "defense_type": None,
            "is_successful": True,
            "counter_attack": None
        }
        
        # Vérifier si l'attaque peut être évitée
        if self._can_avoid_attack(defender, attack_data):
            # Déterminer le type de défense à utiliser
            defense_type = self._choose_defense_type(defender, attack_data)
            
            # Appliquer la défense
            if defense_type == DefenseType.DODGE:
                # Tentative d'esquive
                if random.random() < defense_stats["dodge_chance"]:
                    result["is_successful"] = False
                    result["defense_type"] = DefenseType.DODGE
                    result["final_damage"] = 0
                    
                    logger.debug(f"{getattr(defender, 'name', str(defender))} esquive l'attaque de {getattr(attacker, 'name', str(attacker))}")
                    
                    # Ajouter à l'historique
                    self._add_to_history(defender, DefenseType.DODGE, True)
                    
            elif defense_type == DefenseType.PARRY:
                # Tentative de parade
                if random.random() < defense_stats["parry_chance"]:
                    result["is_successful"] = False
                    result["defense_type"] = DefenseType.PARRY
                    result["final_damage"] = 0
                    
                    logger.debug(f"{getattr(defender, 'name', str(defender))} pare l'attaque de {getattr(attacker, 'name', str(attacker))}")
                    
                    # Ajouter à l'historique
                    self._add_to_history(defender, DefenseType.PARRY, True)
                    
                    # Vérifier si une contre-attaque est possible
                    if random.random() < defense_stats["counter_chance"]:
                        # Générer une contre-attaque
                        counter_damage = self._generate_counter_attack(defender, attacker)
                        
                        result["counter_attack"] = {
                            "damage": counter_damage,
                            "message": f"{getattr(defender, 'name', str(defender))} contre-attaque et inflige {counter_damage} dégâts"
                        }
                        
                        # Appliquer les dégâts de la contre-attaque
                        attacker.health -= counter_damage
                        
                        logger.debug(f"{getattr(defender, 'name', str(defender))} contre-attaque et inflige {counter_damage} dégâts à {getattr(attacker, 'name', str(attacker))}")
                        
                        # Ajouter à l'historique
                        self._add_to_history(defender, DefenseType.COUNTER, True)
                        
            elif defense_type == DefenseType.BLOCK:
                # Tentative de blocage
                if random.random() < defense_stats["block_chance"]:
                    # Le blocage réduit les dégâts mais ne les annule pas complètement
                    block_reduction = 0.7  # 70% de réduction
                    
                    result["defense_type"] = DefenseType.BLOCK
                    result["final_damage"] = int(base_damage * (1 - block_reduction))
                    
                    logger.debug(f"{getattr(defender, 'name', str(defender))} bloque partiellement l'attaque de {getattr(attacker, 'name', str(attacker))}")
                    
                    # Ajouter à l'historique
                    self._add_to_history(defender, DefenseType.BLOCK, True)
        
        # Si aucune défense active n'a réussi, appliquer la réduction de dégâts passive
        if result["is_successful"] and result["defense_type"] is None:
            damage_reduction = defense_stats["damage_reduction"]
            
            if damage_reduction > 0:
                result["final_damage"] = int(base_damage * (1 - damage_reduction))
                result["defense_type"] = DefenseType.ABSORB
                
                logger.debug(f"{getattr(defender, 'name', str(defender))} absorbe {int(base_damage * damage_reduction)} dégâts")
                
                # Ajouter à l'historique
                self._add_to_history(defender, DefenseType.ABSORB, True)
        
        return result
    
    def _can_avoid_attack(self, defender: Any, attack_data: Dict[str, Any]) -> bool:
        """Vérifie si une attaque peut être évitée"""
        # Certaines attaques ne peuvent pas être évitées
        if attack_data.get("unavoidable", False):
            return False
            
        # Vérifier si le défenseur peut agir
        if hasattr(defender, "status_effects"):
            if "stunned" in defender.status_effects:
                return False
            if "frozen" in defender.status_effects:
                return False
                
        return True
    
    def _choose_defense_type(self, defender: Any, attack_data: Dict[str, Any]) -> DefenseType:
        """Choisit le type de défense le plus approprié"""
        # Récupérer les statistiques de défense
        defense_stats = self.defense_stats[defender]
        
        # Déterminer les chances de chaque type de défense
        dodge_chance = defense_stats["dodge_chance"]
        parry_chance = defense_stats["parry_chance"]
        block_chance = defense_stats["block_chance"]
        
        # Ajuster en fonction du type d'attaque
        attack_type = attack_data.get("attack_type", "NORMAL")
        
        if attack_type == "RANGED":
            # Plus difficile de parer les attaques à distance
            parry_chance = 0
            # Plus facile d'esquiver les attaques à distance
            dodge_chance *= 1.2
        elif attack_type == "AREA":
            # Plus difficile d'esquiver les attaques de zone
            dodge_chance *= 0.5
            # Plus difficile de parer les attaques de zone
            parry_chance *= 0.5
            # Le blocage reste efficace contre les attaques de zone
        
        # Choisir le type de défense avec la meilleure chance
        if parry_chance >= dodge_chance and parry_chance >= block_chance:
            return DefenseType.PARRY
        elif dodge_chance >= block_chance:
            return DefenseType.DODGE
        else:
            return DefenseType.BLOCK
    
    def _generate_counter_attack(self, defender: Any, attacker: Any) -> int:
        """Génère une contre-attaque"""
        # Utiliser le système de dégâts standard si disponible
        if hasattr(defender, "calculate_weapon_damage"):
            damage_result = defender.calculate_weapon_damage(attacker)
            base_damage = damage_result.get("damage", 0)
            
            # Les contre-attaques infligent généralement moins de dégâts
            counter_multiplier = 0.7
            
            return int(base_damage * counter_multiplier)
        
        # Calcul simplifié si le système standard n'est pas disponible
        weapon = self._get_equipped_weapon(defender)
        if weapon and hasattr(weapon, "damage"):
            return int(weapon.damage * 0.7)
            
        # Dégâts par défaut
        return 5
    
    def _add_to_history(self, actor: Any, defense_type: DefenseType, success: bool) -> None:
        """Ajoute une entrée à l'historique des défenses"""
        if actor not in self.defense_history:
            self.defense_history[actor] = []
            
        self.defense_history[actor].append({
            "type": defense_type,
            "success": success,
            "timestamp": 0  # À remplacer par un timestamp réel si nécessaire
        })
        
        # Limiter la taille de l'historique
        if len(self.defense_history[actor]) > 10:
            self.defense_history[actor].pop(0)
    
    def get_defense_history(self, actor: Any) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des défenses d'un acteur
        
        Args:
            actor: L'acteur concerné
            
        Returns:
            Liste des défenses récentes
        """
        return self.defense_history.get(actor, [])
    
    def reset_combat_defense(self) -> None:
        """Réinitialise les données de défense de combat"""
        self.defense_history = {}
