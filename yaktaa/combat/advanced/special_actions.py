"""
Système d'actions spéciales pour le combat dans YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialActions")

class ActionCategory(Enum):
    """Catégories d'actions spéciales"""
    ATTACK = auto()      # Attaques spéciales
    DEFENSE = auto()     # Actions défensives
    SUPPORT = auto()     # Actions de soutien
    MOVEMENT = auto()    # Actions de mouvement
    UTILITY = auto()     # Actions utilitaires
    ULTIMATE = auto()    # Capacités ultimes

class ActionCost(Enum):
    """Types de coûts pour les actions spéciales"""
    ACTION_POINTS = auto()  # Points d'action
    ENERGY = auto()         # Énergie
    HEALTH = auto()         # Points de vie
    COOLDOWN = auto()       # Temps de recharge
    RESOURCE = auto()       # Ressource spécifique
    ITEM = auto()           # Objet consommable

class SpecialActionSystem:
    """
    Système qui gère les actions spéciales en combat
    """
    
    def __init__(self):
        """Initialise le système d'actions spéciales"""
        self.available_actions = {}  # Acteur -> liste d'actions disponibles
        self.cooldowns = {}          # Acteur -> dict d'actions en recharge
        self.action_definitions = self._create_action_definitions()
        
        logger.debug("Système d'actions spéciales initialisé")
    
    def _create_action_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Crée les définitions des actions spéciales
        
        Returns:
            Dictionnaire des définitions d'actions
        """
        return {
            # Attaques spéciales
            "power_strike": {
                "name": "Frappe puissante",
                "description": "Une attaque puissante qui inflige des dégâts supplémentaires",
                "category": ActionCategory.ATTACK,
                "damage_multiplier": 1.5,
                "accuracy_modifier": 0.9,
                "cost": {ActionCost.ACTION_POINTS: 2},
                "cooldown": 1,
                "icon": "power_strike",
                "animation": "heavy_strike",
                "requirements": {"strength": 5},
                "weapon_types": ["MELEE"]
            },
            "rapid_fire": {
                "name": "Tir rapide",
                "description": "Tire plusieurs fois rapidement avec une précision réduite",
                "category": ActionCategory.ATTACK,
                "num_attacks": 3,
                "damage_multiplier": 0.7,
                "accuracy_modifier": 0.8,
                "cost": {ActionCost.ACTION_POINTS: 2},
                "cooldown": 2,
                "icon": "rapid_fire",
                "animation": "rapid_shots",
                "requirements": {"reflexes": 6},
                "weapon_types": ["RANGED"]
            },
            "precision_shot": {
                "name": "Tir de précision",
                "description": "Un tir précis qui ignore une partie de l'armure",
                "category": ActionCategory.ATTACK,
                "damage_multiplier": 1.2,
                "armor_penetration": 0.5,
                "critical_chance_bonus": 0.2,
                "cost": {ActionCost.ACTION_POINTS: 2, ActionCost.ENERGY: 10},
                "cooldown": 2,
                "icon": "precision_shot",
                "animation": "precision_aim",
                "requirements": {"precision": 7},
                "weapon_types": ["RANGED", "SMART"]
            },
            
            # Actions défensives
            "defensive_stance": {
                "name": "Posture défensive",
                "description": "Adopte une posture défensive, réduisant les dégâts subis",
                "category": ActionCategory.DEFENSE,
                "damage_reduction": 0.5,
                "duration": 2,
                "cost": {ActionCost.ACTION_POINTS: 1},
                "cooldown": 3,
                "icon": "defensive_stance",
                "animation": "defense_up",
                "requirements": {"endurance": 5}
            },
            "parry": {
                "name": "Parade",
                "description": "Tente de parer la prochaine attaque et de contre-attaquer",
                "category": ActionCategory.DEFENSE,
                "parry_chance": 0.7,
                "counter_damage_multiplier": 0.8,
                "cost": {ActionCost.ACTION_POINTS: 1},
                "cooldown": 1,
                "icon": "parry",
                "animation": "parry_stance",
                "requirements": {"reflexes": 6},
                "weapon_types": ["MELEE"]
            },
            
            # Actions de soutien
            "first_aid": {
                "name": "Premiers soins",
                "description": "Utilise un kit de premiers soins pour récupérer des PV",
                "category": ActionCategory.SUPPORT,
                "healing": lambda level: 20 + (level * 5),
                "cost": {ActionCost.ACTION_POINTS: 2, ActionCost.ITEM: "medkit"},
                "cooldown": 3,
                "icon": "first_aid",
                "animation": "healing",
                "requirements": {"medical": 3}
            },
            "combat_stim": {
                "name": "Stimulant de combat",
                "description": "Utilise un stimulant pour augmenter temporairement les statistiques",
                "category": ActionCategory.SUPPORT,
                "stat_boosts": {"strength": 3, "reflexes": 3, "agility": 3},
                "duration": 3,
                "cost": {ActionCost.ACTION_POINTS: 1, ActionCost.ITEM: "combat_stim"},
                "cooldown": 5,
                "icon": "combat_stim",
                "animation": "inject_stim",
                "side_effects": {"health": -5}
            },
            
            # Actions de mouvement
            "tactical_retreat": {
                "name": "Repli tactique",
                "description": "Se replie rapidement pour éviter les attaques",
                "category": ActionCategory.MOVEMENT,
                "movement_distance": 3,
                "dodge_bonus": 0.3,
                "cost": {ActionCost.ACTION_POINTS: 1},
                "cooldown": 2,
                "icon": "tactical_retreat",
                "animation": "quick_dodge",
                "requirements": {"agility": 5}
            },
            "charge": {
                "name": "Charge",
                "description": "Charge un ennemi pour l'attaquer avec un bonus de dégâts",
                "category": ActionCategory.MOVEMENT,
                "movement_distance": 4,
                "damage_multiplier": 1.3,
                "stun_chance": 0.3,
                "cost": {ActionCost.ACTION_POINTS: 2},
                "cooldown": 3,
                "icon": "charge",
                "animation": "charging_attack",
                "requirements": {"strength": 6, "agility": 4}
            },
            
            # Capacités ultimes
            "adrenaline_rush": {
                "name": "Poussée d'adrénaline",
                "description": "Déclenche une poussée d'adrénaline, permettant d'agir deux fois",
                "category": ActionCategory.ULTIMATE,
                "extra_actions": 1,
                "stat_boosts": {"reflexes": 5, "agility": 5},
                "duration": 1,
                "cost": {ActionCost.ENERGY: 50, ActionCost.HEALTH: 10},
                "cooldown": 5,
                "icon": "adrenaline_rush",
                "animation": "adrenaline_pulse",
                "requirements": {"level": 10}
            },
            "critical_overload": {
                "name": "Surcharge critique",
                "description": "Augmente considérablement les chances de coup critique",
                "category": ActionCategory.ULTIMATE,
                "critical_chance_bonus": 0.5,
                "critical_damage_bonus": 0.5,
                "duration": 2,
                "cost": {ActionCost.ENERGY: 40},
                "cooldown": 5,
                "icon": "critical_overload",
                "animation": "system_overload",
                "requirements": {"hacking": 8, "level": 8}
            }
        }
    
    def register_actions(self, actor: Any) -> None:
        """
        Enregistre les actions disponibles pour un acteur
        
        Args:
            actor: L'acteur concerné
        """
        if actor in self.available_actions:
            return
            
        self.available_actions[actor] = []
        self.cooldowns[actor] = {}
        
        # Vérifier chaque action
        for action_id, action_def in self.action_definitions.items():
            # Vérifier les prérequis
            if self._meets_requirements(actor, action_def.get("requirements", {})):
                # Vérifier les types d'armes compatibles
                if "weapon_types" in action_def:
                    weapon = self._get_equipped_weapon(actor)
                    if not weapon or not hasattr(weapon, "weapon_type"):
                        continue
                        
                    if weapon.weapon_type not in action_def["weapon_types"]:
                        continue
                
                # Ajouter l'action
                self.available_actions[actor].append(action_id)
                logger.debug(f"Action {action_id} disponible pour {getattr(actor, 'name', str(actor))}")
    
    def _meets_requirements(self, actor: Any, requirements: Dict[str, int]) -> bool:
        """Vérifie si un acteur remplit les prérequis d'une action"""
        for stat, value in requirements.items():
            actor_value = 0
            
            # Récupérer la valeur de la statistique
            if hasattr(actor, "get_effective_stats"):
                actor_value = actor.get_effective_stats().get(stat, 0)
            elif hasattr(actor, stat):
                actor_value = getattr(actor, stat)
            elif hasattr(actor, "level") and stat == "level":
                actor_value = actor.level
            
            # Vérifier si la valeur est suffisante
            if actor_value < value:
                return False
        
        return True
    
    def _get_equipped_weapon(self, actor: Any) -> Optional[Any]:
        """Récupère l'arme équipée d'un acteur"""
        if hasattr(actor, "active_equipment") and "weapon" in actor.active_equipment:
            return actor.active_equipment["weapon"]
        return None
    
    def get_available_actions(self, actor: Any) -> List[Dict[str, Any]]:
        """
        Récupère les actions disponibles pour un acteur
        
        Args:
            actor: L'acteur concerné
            
        Returns:
            Liste des actions disponibles avec leurs détails
        """
        if actor not in self.available_actions:
            self.register_actions(actor)
            
        actions = []
        
        for action_id in self.available_actions[actor]:
            # Récupérer la définition de l'action
            action_def = self.action_definitions[action_id]
            
            # Vérifier si l'action est en recharge
            cooldown_remaining = self.cooldowns[actor].get(action_id, 0)
            
            # Créer l'objet action
            action = {
                "id": action_id,
                "name": action_def["name"],
                "description": action_def["description"],
                "category": action_def["category"],
                "icon": action_def.get("icon", "default_action"),
                "cooldown_remaining": cooldown_remaining,
                "is_available": cooldown_remaining == 0 and self._can_pay_cost(actor, action_def.get("cost", {}))
            }
            
            actions.append(action)
            
        return actions
    
    def _can_pay_cost(self, actor: Any, costs: Dict[ActionCost, Any]) -> bool:
        """Vérifie si un acteur peut payer le coût d'une action"""
        for cost_type, cost_value in costs.items():
            if cost_type == ActionCost.ACTION_POINTS:
                if getattr(actor, "action_points", 0) < cost_value:
                    return False
            elif cost_type == ActionCost.ENERGY:
                if getattr(actor, "energy", 0) < cost_value:
                    return False
            elif cost_type == ActionCost.HEALTH:
                if actor.health <= cost_value:  # Ne pas permettre de se tuer
                    return False
            elif cost_type == ActionCost.ITEM:
                if not self._has_item(actor, cost_value):
                    return False
        
        return True
    
    def _has_item(self, actor: Any, item_id: str) -> bool:
        """Vérifie si un acteur possède un objet"""
        if hasattr(actor, "inventory"):
            return item_id in actor.inventory
        return False
    
    def use_action(self, actor: Any, target: Any, action_id: str) -> Dict[str, Any]:
        """
        Utilise une action spéciale
        
        Args:
            actor: L'acteur qui utilise l'action
            target: La cible de l'action
            action_id: Identifiant de l'action
            
        Returns:
            Résultat de l'action
        """
        # Vérifier si l'action existe
        if action_id not in self.action_definitions:
            return {"success": False, "message": f"Action inconnue: {action_id}"}
            
        # Vérifier si l'acteur a accès à cette action
        if actor not in self.available_actions or action_id not in self.available_actions[actor]:
            return {"success": False, "message": f"{getattr(actor, 'name', str(actor))} n'a pas accès à cette action"}
            
        # Vérifier si l'action est en recharge
        if self.cooldowns[actor].get(action_id, 0) > 0:
            return {"success": False, "message": f"L'action {action_id} est en recharge ({self.cooldowns[actor][action_id]} tours restants)"}
            
        # Récupérer la définition de l'action
        action_def = self.action_definitions[action_id]
        
        # Vérifier si l'acteur peut payer le coût
        if not self._can_pay_cost(actor, action_def.get("cost", {})):
            return {"success": False, "message": "Ressources insuffisantes pour utiliser cette action"}
            
        # Payer le coût
        self._pay_cost(actor, action_def.get("cost", {}))
        
        # Appliquer le temps de recharge
        cooldown = action_def.get("cooldown", 0)
        if cooldown > 0:
            self.cooldowns[actor][action_id] = cooldown
            
        # Exécuter l'action en fonction de sa catégorie
        category = action_def.get("category")
        
        if category == ActionCategory.ATTACK:
            result = self._execute_attack_action(actor, target, action_def)
        elif category == ActionCategory.DEFENSE:
            result = self._execute_defense_action(actor, action_def)
        elif category == ActionCategory.SUPPORT:
            result = self._execute_support_action(actor, target, action_def)
        elif category == ActionCategory.MOVEMENT:
            result = self._execute_movement_action(actor, target, action_def)
        elif category == ActionCategory.ULTIMATE:
            result = self._execute_ultimate_action(actor, action_def)
        else:
            result = {"success": True, "message": f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']}"}
            
        logger.debug(f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']} sur {getattr(target, 'name', str(target))}")
        
        return result
    
    def _pay_cost(self, actor: Any, costs: Dict[ActionCost, Any]) -> None:
        """Fait payer le coût d'une action à un acteur"""
        for cost_type, cost_value in costs.items():
            if cost_type == ActionCost.ACTION_POINTS:
                actor.action_points -= cost_value
            elif cost_type == ActionCost.ENERGY:
                actor.energy -= cost_value
            elif cost_type == ActionCost.HEALTH:
                actor.health -= cost_value
            elif cost_type == ActionCost.ITEM:
                if hasattr(actor, "remove_item"):
                    actor.remove_item(cost_value)
    
    def _execute_attack_action(self, actor: Any, target: Any, action_def: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action d'attaque"""
        # Récupérer les modificateurs
        damage_multiplier = action_def.get("damage_multiplier", 1.0)
        accuracy_modifier = action_def.get("accuracy_modifier", 1.0)
        armor_penetration = action_def.get("armor_penetration", 0.0)
        critical_chance_bonus = action_def.get("critical_chance_bonus", 0.0)
        num_attacks = action_def.get("num_attacks", 1)
        
        total_damage = 0
        hits = 0
        criticals = 0
        
        # Effectuer les attaques
        for _ in range(num_attacks):
            # Calculer les dégâts de base
            if hasattr(actor, "calculate_weapon_damage"):
                damage_result = actor.calculate_weapon_damage(target)
                base_damage = damage_result.get("damage", 0)
                is_critical = damage_result.get("critical", False) or (random.random() < critical_chance_bonus)
                
                # Appliquer le multiplicateur de dégâts
                modified_damage = base_damage * damage_multiplier
                
                # Appliquer les dégâts critiques
                if is_critical:
                    modified_damage *= action_def.get("critical_damage_bonus", 1.5)
                    criticals += 1
                
                # Vérifier si l'attaque touche
                hit_chance = getattr(actor, "accuracy", 70) * accuracy_modifier / 100
                if random.random() < hit_chance:
                    # Appliquer la pénétration d'armure
                    if armor_penetration > 0 and hasattr(target, "armor"):
                        effective_armor = target.armor * (1 - armor_penetration)
                        damage_reduction = min(0.8, effective_armor / 100)
                        modified_damage *= (1 - damage_reduction)
                    
                    # Appliquer les dégâts
                    target.health -= int(modified_damage)
                    total_damage += int(modified_damage)
                    hits += 1
        
        # Créer le message de résultat
        if hits == 0:
            message = f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']} mais rate complètement!"
        else:
            message = f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']} et touche {hits}/{num_attacks} fois"
            message += f" pour {total_damage} dégâts"
            
            if criticals > 0:
                message += f" (dont {criticals} coups critiques)"
        
        return {
            "success": True,
            "message": message,
            "damage": total_damage,
            "hits": hits,
            "criticals": criticals,
            "target_health": target.health
        }
    
    def _execute_defense_action(self, actor: Any, action_def: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action défensive"""
        # Récupérer les modificateurs
        damage_reduction = action_def.get("damage_reduction", 0.0)
        duration = action_def.get("duration", 1)
        parry_chance = action_def.get("parry_chance", 0.0)
        
        # Appliquer les effets
        if hasattr(actor, "combat_modifiers"):
            if damage_reduction > 0:
                actor.combat_modifiers["damage_reduction"] = damage_reduction
                actor.combat_modifiers["damage_reduction_duration"] = duration
            
            if parry_chance > 0:
                actor.combat_modifiers["parry_chance"] = parry_chance
                actor.combat_modifiers["parry_duration"] = 1  # Généralement jusqu'au prochain tour
        
        return {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} adopte une posture défensive",
            "damage_reduction": damage_reduction,
            "duration": duration,
            "parry_chance": parry_chance
        }
    
    def _execute_support_action(self, actor: Any, target: Any, action_def: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action de soutien"""
        # Récupérer les effets
        healing = action_def.get("healing", 0)
        stat_boosts = action_def.get("stat_boosts", {})
        duration = action_def.get("duration", 1)
        side_effects = action_def.get("side_effects", {})
        
        # Calculer les soins
        heal_amount = 0
        if callable(healing):
            heal_amount = healing(getattr(actor, "level", 1))
        else:
            heal_amount = healing
            
        # Appliquer les soins
        if heal_amount > 0:
            old_health = target.health
            target.health = min(target.health + heal_amount, target.max_health)
            actual_healing = target.health - old_health
        
        # Appliquer les bonus de stats
        if stat_boosts and hasattr(target, "temporary_stat_boosts"):
            for stat, value in stat_boosts.items():
                if stat not in target.temporary_stat_boosts:
                    target.temporary_stat_boosts[stat] = []
                    
                target.temporary_stat_boosts[stat].append({
                    "value": value,
                    "duration": duration,
                    "source": action_def["name"]
                })
        
        # Appliquer les effets secondaires
        for stat, value in side_effects.items():
            if stat == "health":
                target.health += value  # Peut être négatif
        
        return {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']} sur {getattr(target, 'name', str(target))}",
            "healing": actual_healing if heal_amount > 0 else 0,
            "stat_boosts": stat_boosts,
            "duration": duration,
            "side_effects": side_effects
        }
    
    def _execute_movement_action(self, actor: Any, target: Any, action_def: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action de mouvement"""
        # Récupérer les modificateurs
        movement_distance = action_def.get("movement_distance", 0)
        dodge_bonus = action_def.get("dodge_bonus", 0.0)
        damage_multiplier = action_def.get("damage_multiplier", 0.0)
        stun_chance = action_def.get("stun_chance", 0.0)
        
        result = {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} utilise {action_def['name']}",
            "movement_distance": movement_distance
        }
        
        # Appliquer les effets spécifiques
        if dodge_bonus > 0 and hasattr(actor, "combat_modifiers"):
            actor.combat_modifiers["dodge_bonus"] = dodge_bonus
            actor.combat_modifiers["dodge_duration"] = 1
            result["dodge_bonus"] = dodge_bonus
        
        # Si c'est une charge avec attaque
        if damage_multiplier > 0 and target:
            # Calculer les dégâts
            if hasattr(actor, "calculate_weapon_damage"):
                damage_result = actor.calculate_weapon_damage(target)
                base_damage = damage_result.get("damage", 0)
                
                # Appliquer le multiplicateur
                final_damage = int(base_damage * damage_multiplier)
                
                # Appliquer les dégâts
                target.health -= final_damage
                
                result["damage"] = final_damage
                result["message"] += f" et inflige {final_damage} dégâts à {getattr(target, 'name', str(target))}"
                
                # Appliquer l'étourdissement
                if stun_chance > 0 and random.random() < stun_chance:
                    # Ajouter un effet d'étourdissement
                    if hasattr(target, "status_effects"):
                        target.status_effects["stunned"] = 1  # 1 tour
                    
                    result["stunned"] = True
                    result["message"] += " et l'étourdit"
        
        return result
    
    def _execute_ultimate_action(self, actor: Any, action_def: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une capacité ultime"""
        # Récupérer les effets
        extra_actions = action_def.get("extra_actions", 0)
        stat_boosts = action_def.get("stat_boosts", {})
        critical_chance_bonus = action_def.get("critical_chance_bonus", 0.0)
        critical_damage_bonus = action_def.get("critical_damage_bonus", 0.0)
        duration = action_def.get("duration", 1)
        
        # Appliquer les effets
        if hasattr(actor, "combat_modifiers"):
            if extra_actions > 0:
                actor.combat_modifiers["extra_actions"] = extra_actions
                actor.combat_modifiers["extra_actions_duration"] = duration
            
            if critical_chance_bonus > 0:
                actor.combat_modifiers["critical_chance_bonus"] = critical_chance_bonus
                actor.combat_modifiers["critical_chance_duration"] = duration
            
            if critical_damage_bonus > 0:
                actor.combat_modifiers["critical_damage_bonus"] = critical_damage_bonus
                actor.combat_modifiers["critical_damage_duration"] = duration
        
        # Appliquer les bonus de stats
        if stat_boosts and hasattr(actor, "temporary_stat_boosts"):
            for stat, value in stat_boosts.items():
                if stat not in actor.temporary_stat_boosts:
                    actor.temporary_stat_boosts[stat] = []
                    
                actor.temporary_stat_boosts[stat].append({
                    "value": value,
                    "duration": duration,
                    "source": action_def["name"]
                })
        
        return {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} déclenche {action_def['name']}!",
            "extra_actions": extra_actions,
            "stat_boosts": stat_boosts,
            "critical_chance_bonus": critical_chance_bonus,
            "critical_damage_bonus": critical_damage_bonus,
            "duration": duration
        }
    
    def update_cooldowns(self, actor: Any) -> None:
        """
        Met à jour les temps de recharge pour un acteur
        
        Args:
            actor: L'acteur concerné
        """
        if actor not in self.cooldowns:
            return
            
        # Réduire les temps de recharge
        for action_id in list(self.cooldowns[actor].keys()):
            self.cooldowns[actor][action_id] -= 1
            
            # Supprimer les temps de recharge expirés
            if self.cooldowns[actor][action_id] <= 0:
                del self.cooldowns[actor][action_id]
                logger.debug(f"Action {action_id} rechargée pour {getattr(actor, 'name', str(actor))}")
    
    def reset_combat_actions(self) -> None:
        """Réinitialise les actions de combat"""
        self.cooldowns = {}
