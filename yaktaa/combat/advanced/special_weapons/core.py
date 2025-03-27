"""
Classes de base pour le système d'armes spéciales
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialWeapons")

class SpecialWeaponType(Enum):
    """Types d'armes spéciales"""
    ENERGY = auto()       # Armes à énergie
    MELEE = auto()        # Armes de corps à corps
    PROJECTILE = auto()   # Armes à projectiles
    TECH = auto()         # Armes technologiques
    EXPERIMENTAL = auto() # Armes expérimentales

class SpecialWeaponRarity(Enum):
    """Raretés des armes spéciales"""
    UNCOMMON = 1     # Peu commun
    RARE = 2         # Rare
    EPIC = 3         # Épique
    LEGENDARY = 4    # Légendaire
    ARTIFACT = 5     # Artefact unique

class SpecialWeaponSystem:
    """
    Système qui gère les armes spéciales et leurs effets
    """
    
    def __init__(self):
        """Initialise le système d'armes spéciales"""
        self.weapons_catalog = {}  # ID -> arme spéciale
        self.weapon_instances = {}  # (joueur_id, arme_id) -> infos de l'instance
        self.active_effects = {}   # ID -> effet actif
        self.evolution_progress = {}  # (joueur_id, arme_id) -> progression
        
        logger.debug("Système d'armes spéciales initialisé")
    
    def register_special_weapon(self, weapon_data: Dict[str, Any]) -> bool:
        """
        Enregistre une arme spéciale dans le catalogue
        
        Args:
            weapon_data: Données de l'arme
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        weapon_id = weapon_data.get("id")
        if not weapon_id:
            logger.error("Tentative d'enregistrement d'une arme sans ID")
            return False
            
        if weapon_id in self.weapons_catalog:
            logger.warning(f"L'arme spéciale {weapon_id} existe déjà dans le catalogue")
            return False
            
        # Valider les données minimales requises
        required_fields = ["name", "description", "type", "rarity", "base_damage", "effects"]
        
        for field in required_fields:
            if field not in weapon_data:
                logger.error(f"Arme spéciale {weapon_id} manque le champ requis: {field}")
                return False
        
        # Ajouter l'arme au catalogue
        self.weapons_catalog[weapon_id] = weapon_data
        
        logger.info(f"Arme spéciale enregistrée: {weapon_data['name']} (ID: {weapon_id})")
        return True
    
    def get_special_weapon(self, weapon_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une arme spéciale du catalogue
        
        Args:
            weapon_id: Identifiant de l'arme
            
        Returns:
            Données de l'arme ou None si elle n'existe pas
        """
        return self.weapons_catalog.get(weapon_id)
    
    def list_special_weapons(self, weapon_type: Optional[SpecialWeaponType] = None, 
                           min_rarity: Optional[SpecialWeaponRarity] = None) -> List[Dict[str, Any]]:
        """
        Liste les armes spéciales disponibles, avec filtres optionnels
        
        Args:
            weapon_type: Type d'arme pour filtrer (optionnel)
            min_rarity: Rareté minimale pour filtrer (optionnel)
            
        Returns:
            Liste des armes correspondant aux critères
        """
        results = []
        
        for weapon_id, weapon_data in self.weapons_catalog.items():
            # Appliquer le filtre de type
            if weapon_type is not None and weapon_data["type"] != weapon_type:
                continue
                
            # Appliquer le filtre de rareté
            if min_rarity is not None and weapon_data["rarity"].value < min_rarity.value:
                continue
                
            results.append(weapon_data)
            
        return results
    
    def assign_weapon_to_player(self, player_id: str, weapon_id: str) -> Dict[str, Any]:
        """
        Assigne une arme spéciale à un joueur
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            
        Returns:
            Résultat de l'assignation
        """
        # Vérifier si l'arme existe
        weapon_data = self.get_special_weapon(weapon_id)
        if not weapon_data:
            return {
                "success": False,
                "message": f"Arme spéciale {weapon_id} non trouvée"
            }
            
        # Créer l'instance de l'arme
        instance_key = (player_id, weapon_id)
        
        # Vérifier si cette arme est déjà assignée
        if instance_key in self.weapon_instances:
            return {
                "success": False, 
                "message": f"L'arme {weapon_data['name']} est déjà assignée à ce joueur"
            }
            
        # Créer une nouvelle instance
        weapon_instance = {
            "player_id": player_id,
            "weapon_id": weapon_id,
            "weapon_data": weapon_data.copy(),
            "current_charge": 0,
            "max_charge": weapon_data.get("max_charge", 100),
            "cooldowns": {},
            "current_durability": weapon_data.get("durability", 100),
            "modifications": [],
            "kill_count": 0,
            "damage_dealt": 0,
            "special_triggers": 0
        }
        
        # Enregistrer l'instance
        self.weapon_instances[instance_key] = weapon_instance
        
        # Initialiser la progression d'évolution
        self.evolution_progress[instance_key] = {
            "level": 1,
            "experience": 0,
            "next_level": 1000,
            "evolutions_available": 0,
            "evolutions_applied": []
        }
        
        logger.info(f"Arme spéciale {weapon_data['name']} assignée au joueur {player_id}")
        
        return {
            "success": True,
            "message": f"Arme spéciale {weapon_data['name']} assignée avec succès",
            "weapon_instance": weapon_instance
        }
    
    def get_player_weapon(self, player_id: str, weapon_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère l'instance d'une arme spéciale d'un joueur
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            
        Returns:
            Instance de l'arme ou None si elle n'existe pas
        """
        instance_key = (player_id, weapon_id)
        return self.weapon_instances.get(instance_key)
    
    def list_player_weapons(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Liste toutes les armes spéciales d'un joueur
        
        Args:
            player_id: Identifiant du joueur
            
        Returns:
            Liste des armes du joueur
        """
        results = []
        
        for (pid, wid), weapon_instance in self.weapon_instances.items():
            if pid == player_id:
                results.append(weapon_instance)
                
        return results
    
    def check_special_activation(self, player_id: str, weapon_id: str, 
                               combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie si un effet spécial peut s'activer dans un contexte de combat
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            combat_context: Contexte du combat
            
        Returns:
            Résultat de la vérification
        """
        # Récupérer l'instance de l'arme
        weapon_instance = self.get_player_weapon(player_id, weapon_id)
        if not weapon_instance:
            return {"can_activate": False, "message": "Arme non trouvée"}
            
        # Récupérer les effets de l'arme
        weapon_data = weapon_instance["weapon_data"]
        effects = weapon_data.get("effects", [])
        
        # Si aucun effet, pas d'activation possible
        if not effects:
            return {"can_activate": False, "message": "Aucun effet spécial disponible"}
            
        # Vérifier les cooldowns
        cooldowns = weapon_instance["cooldowns"]
        current_time = combat_context.get("combat_time", 0)
        
        # Vérifier chaque effet
        available_effects = []
        
        for effect in effects:
            effect_id = effect.get("id")
            
            # Vérifier le cooldown
            if effect_id in cooldowns and current_time < cooldowns[effect_id]:
                continue
                
            # Vérifier les conditions d'activation
            trigger_conditions = effect.get("trigger_conditions", {})
            
            # Par défaut, considérer que l'effet peut s'activer
            can_trigger = True
            
            # Vérifier chaque condition
            for condition_key, condition_value in trigger_conditions.items():
                if condition_key == "min_charge":
                    if weapon_instance["current_charge"] < condition_value:
                        can_trigger = False
                        break
                elif condition_key == "health_below":
                    player_health_percent = combat_context.get("player_health_percent", 100)
                    if player_health_percent >= condition_value:
                        can_trigger = False
                        break
                elif condition_key == "consecutive_hits":
                    consecutive_hits = combat_context.get("consecutive_hits", 0)
                    if consecutive_hits < condition_value:
                        can_trigger = False
                        break
                elif condition_key == "enemy_count":
                    enemy_count = combat_context.get("enemy_count", 0)
                    if enemy_count < condition_value:
                        can_trigger = False
                        break
                elif condition_key == "critical_hit":
                    is_critical = combat_context.get("is_critical", False)
                    if condition_value and not is_critical:
                        can_trigger = False
                        break
                elif condition_key == "trigger_chance":
                    # Une chance aléatoire d'activation
                    if random.random() > condition_value:
                        can_trigger = False
                        break
            
            # Si toutes les conditions sont remplies, ajouter l'effet à la liste des disponibles
            if can_trigger:
                available_effects.append(effect)
        
        # Déterminer si au moins un effet peut s'activer
        if not available_effects:
            return {"can_activate": False, "message": "Aucun effet activable actuellement"}
            
        return {
            "can_activate": True,
            "message": f"{len(available_effects)} effet(s) disponible(s)",
            "available_effects": available_effects
        }
    
    def trigger_special_effect(self, player_id: str, weapon_id: str, effect_id: str,
                             combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Déclenche un effet spécial d'une arme
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            effect_id: Identifiant de l'effet à déclencher
            combat_context: Contexte du combat
            
        Returns:
            Résultat du déclenchement
        """
        # Récupérer l'instance de l'arme
        instance_key = (player_id, weapon_id)
        weapon_instance = self.weapon_instances.get(instance_key)
        
        if not weapon_instance:
            return {
                "success": False,
                "message": "Arme non trouvée"
            }
            
        # Récupérer l'effet spécifié
        weapon_data = weapon_instance["weapon_data"]
        effects = weapon_data.get("effects", [])
        
        target_effect = None
        for effect in effects:
            if effect.get("id") == effect_id:
                target_effect = effect
                break
                
        if not target_effect:
            return {
                "success": False,
                "message": f"Effet {effect_id} non trouvé pour cette arme"
            }
            
        # Vérifier si l'effet peut s'activer
        activation_check = self.check_special_activation(player_id, weapon_id, combat_context)
        if not activation_check["can_activate"]:
            return {
                "success": False,
                "message": activation_check["message"]
            }
            
        # Vérifier si l'effet spécifique est disponible
        effect_available = False
        for available_effect in activation_check.get("available_effects", []):
            if available_effect.get("id") == effect_id:
                effect_available = True
                break
                
        if not effect_available:
            return {
                "success": False,
                "message": f"L'effet {effect_id} n'est pas disponible actuellement"
            }
            
        # Appliquer les coûts de l'effet
        costs = target_effect.get("costs", {})
        
        # Coût en charge
        charge_cost = costs.get("charge", 0)
        if charge_cost > 0:
            if weapon_instance["current_charge"] < charge_cost:
                return {
                    "success": False,
                    "message": f"Charge insuffisante ({weapon_instance['current_charge']}/{charge_cost})"
                }
            weapon_instance["current_charge"] -= charge_cost
            
        # Coût en durabilité
        durability_cost = costs.get("durability", 0)
        if durability_cost > 0:
            if weapon_instance["current_durability"] < durability_cost:
                return {
                    "success": False,
                    "message": f"Durabilité insuffisante ({weapon_instance['current_durability']}/{durability_cost})"
                }
            weapon_instance["current_durability"] -= durability_cost
        
        # Appliquer le cooldown
        cooldown_duration = target_effect.get("cooldown", 0)
        if cooldown_duration > 0:
            current_time = combat_context.get("combat_time", 0)
            weapon_instance["cooldowns"][effect_id] = current_time + cooldown_duration
        
        # Créer un ID unique pour l'effet actif
        effect_instance_id = f"{player_id}_{weapon_id}_{effect_id}_{random.randint(1000, 9999)}"
        
        # Enregistrer l'effet actif
        effect_duration = target_effect.get("duration", 1)
        current_time = combat_context.get("combat_time", 0)
        
        active_effect = {
            "id": effect_instance_id,
            "player_id": player_id,
            "weapon_id": weapon_id,
            "effect_id": effect_id,
            "effect_data": target_effect,
            "start_time": current_time,
            "end_time": current_time + effect_duration,
            "targets": combat_context.get("targets", []),
            "applied_effects": []
        }
        
        self.active_effects[effect_instance_id] = active_effect
        
        # Incrémenter le compteur de déclenchements spéciaux
        weapon_instance["special_triggers"] += 1
        
        # Mettre à jour l'expérience de l'arme
        self._update_weapon_experience(player_id, weapon_id, "effect_triggered", 
                                      target_effect.get("rarity", 1) * 100)
        
        logger.info(f"Effet spécial {effect_id} déclenché pour l'arme {weapon_data['name']}")
        
        return {
            "success": True,
            "message": f"Effet spécial {target_effect.get('name', effect_id)} activé",
            "effect": target_effect,
            "effect_instance_id": effect_instance_id,
            "remaining_charge": weapon_instance["current_charge"],
            "remaining_durability": weapon_instance["current_durability"]
        }
    
    def _update_weapon_experience(self, player_id: str, weapon_id: str, 
                                action: str, base_exp: int) -> None:
        """
        Met à jour l'expérience d'une arme spéciale
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            action: Type d'action réalisée
            base_exp: Expérience de base pour cette action
        """
        instance_key = (player_id, weapon_id)
        if instance_key not in self.evolution_progress:
            return
            
        # Récupérer les données d'évolution
        evolution_data = self.evolution_progress[instance_key]
        
        # Calculer l'expérience à ajouter en fonction de l'action
        exp_multiplier = 1.0
        if action == "damage_dealt":
            exp_multiplier = 0.1  # Moins d'XP pour les dégâts normaux
        elif action == "critical_hit":
            exp_multiplier = 0.5  # Plus d'XP pour les critiques
        elif action == "kill":
            exp_multiplier = 2.0  # Beaucoup d'XP pour les éliminations
        elif action == "effect_triggered":
            exp_multiplier = 1.5  # Bon montant pour l'utilisation d'effets
            
        exp_gained = int(base_exp * exp_multiplier)
        
        # Ajouter l'expérience
        evolution_data["experience"] += exp_gained
        
        # Vérifier le niveau
        while evolution_data["experience"] >= evolution_data["next_level"]:
            # Monter de niveau
            evolution_data["level"] += 1
            evolution_data["experience"] -= evolution_data["next_level"]
            
            # Augmenter les exigences pour le niveau suivant
            evolution_data["next_level"] = int(evolution_data["next_level"] * 1.5)
            
            # Accorder une évolution disponible tous les 3 niveaux
            if evolution_data["level"] % 3 == 0:
                evolution_data["evolutions_available"] += 1
                
            logger.info(f"Arme {weapon_id} passée au niveau {evolution_data['level']}")
    
    def update_special_effects(self, combat_time: int) -> List[Dict[str, Any]]:
        """
        Met à jour tous les effets spéciaux actifs et retire ceux qui sont expirés
        
        Args:
            combat_time: Temps actuel du combat
            
        Returns:
            Liste des effets expirés lors de cette mise à jour
        """
        expired_effects = []
        
        # Parcourir tous les effets actifs
        for effect_id, effect_data in list(self.active_effects.items()):
            # Vérifier si l'effet est expiré
            if combat_time >= effect_data["end_time"]:
                # Ajouter à la liste des expirés
                expired_effects.append(effect_data)
                
                # Retirer de la liste des actifs
                del self.active_effects[effect_id]
        
        return expired_effects
