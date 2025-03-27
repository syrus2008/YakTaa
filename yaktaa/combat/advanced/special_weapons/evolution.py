"""
Système d'évolution des armes spéciales pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

from .core import SpecialWeaponSystem, SpecialWeaponRarity

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialWeapons.Evolution")

class EvolutionTrigger(Enum):
    """Types de déclencheurs pour l'évolution des armes"""
    KILL_COUNT = auto()      # Nombre d'éliminations
    DAMAGE_DEALT = auto()    # Dégâts infligés
    EFFECT_USES = auto()     # Utilisations d'effets spéciaux
    CRITICAL_HITS = auto()   # Coups critiques
    COMBAT_TIME = auto()     # Temps en combat
    PLAYER_LEVEL = auto()    # Niveau du joueur

class WeaponEvolutionSystem:
    """
    Système qui gère l'évolution des armes spéciales
    """
    
    def __init__(self, special_weapon_system: SpecialWeaponSystem):
        """
        Initialise le système d'évolution des armes
        
        Args:
            special_weapon_system: Le système d'armes spéciales à utiliser
        """
        self.weapon_system = special_weapon_system
        self.evolution_thresholds = {}  # Type de déclencheur -> seuil
        self.available_evolutions = {}  # Arme ID -> évolutions disponibles
        self.applied_evolutions = {}    # (joueur_id, arme_id) -> évolutions appliquées
        
        # Initialiser les seuils d'évolution par défaut
        self._init_evolution_thresholds()
        
        logger.debug("Système d'évolution des armes spéciales initialisé")
    
    def _init_evolution_thresholds(self) -> None:
        """Initialise les seuils d'évolution par défaut"""
        self.evolution_thresholds = {
            EvolutionTrigger.KILL_COUNT: {
                "small": 10,
                "medium": 25,
                "large": 50
            },
            EvolutionTrigger.DAMAGE_DEALT: {
                "small": 1000,
                "medium": 5000,
                "large": 15000
            },
            EvolutionTrigger.EFFECT_USES: {
                "small": 5,
                "medium": 15,
                "large": 30
            },
            EvolutionTrigger.CRITICAL_HITS: {
                "small": 5,
                "medium": 15,
                "large": 30
            },
            EvolutionTrigger.COMBAT_TIME: {  # En minutes
                "small": 30,
                "medium": 120,
                "large": 360
            },
            EvolutionTrigger.PLAYER_LEVEL: {
                "small": 5,
                "medium": 15,
                "large": 30
            }
        }
    
    def check_evolution_eligibility(self, player_id: str, weapon_id: str, 
                                 player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie si une arme est éligible pour une évolution
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            player_stats: Statistiques du joueur
            
        Returns:
            Résultat de la vérification
        """
        # Récupérer l'instance de l'arme
        weapon_instance = self.weapon_system.get_player_weapon(player_id, weapon_id)
        if not weapon_instance:
            return {
                "eligible": False,
                "message": "Arme non trouvée"
            }
            
        # Récupérer les données d'évolution de l'arme
        instance_key = (player_id, weapon_id)
        evolution_progress = self.weapon_system.evolution_progress.get(instance_key)
        
        if not evolution_progress:
            return {
                "eligible": False,
                "message": "Données d'évolution non trouvées"
            }
            
        # Vérifier si des évolutions sont disponibles
        if evolution_progress["evolutions_available"] <= 0:
            # Vérifier le niveau actuel de l'arme
            current_level = evolution_progress["level"]
            
            # Calculer le niveau requis pour la prochaine évolution
            next_evolution_level = (current_level // 3 + 1) * 3
            
            # Calculer l'expérience restante
            current_exp = evolution_progress["experience"]
            next_level_exp = evolution_progress["next_level"]
            
            return {
                "eligible": False,
                "message": "Pas d'évolution disponible actuellement",
                "current_level": current_level,
                "next_evolution_level": next_evolution_level,
                "levels_needed": next_evolution_level - current_level,
                "current_exp": current_exp,
                "next_level_exp": next_level_exp,
                "exp_progress_percent": int((current_exp / next_level_exp) * 100)
            }
            
        # Récupérer les évolutions disponibles pour cette arme
        weapon_data = weapon_instance["weapon_data"]
        evolution_paths = weapon_data.get("evolution_paths", [])
        
        if not evolution_paths:
            return {
                "eligible": False,
                "message": "Aucun chemin d'évolution disponible pour cette arme"
            }
            
        # Filtrer les évolutions déjà appliquées
        applied_evos = self.applied_evolutions.get(instance_key, [])
        applied_evo_ids = [evo["id"] for evo in applied_evos]
        
        available_evos = []
        for evolution in evolution_paths:
            # Vérifier si cette évolution est déjà appliquée
            if evolution["id"] in applied_evo_ids:
                continue
                
            # Vérifier le niveau requis
            if evolution.get("level_requirement", 1) > evolution_progress["level"]:
                continue
                
            # Vérifier les autres conditions
            prereq_evolutions = evolution.get("prerequisites", [])
            prerequisites_met = True
            
            for prereq_id in prereq_evolutions:
                if prereq_id not in applied_evo_ids:
                    prerequisites_met = False
                    break
                    
            if not prerequisites_met:
                continue
                
            # Cette évolution est disponible
            available_evos.append(evolution)
        
        if not available_evos:
            return {
                "eligible": False,
                "message": "Aucune évolution disponible actuellement",
                "current_level": evolution_progress["level"],
                "evolutions_available": evolution_progress["evolutions_available"]
            }
            
        return {
            "eligible": True,
            "message": f"{len(available_evos)} évolution(s) disponible(s)",
            "evolutions_available": evolution_progress["evolutions_available"],
            "available_evolutions": available_evos,
            "weapon_instance": weapon_instance
        }
    
    def apply_evolution(self, player_id: str, weapon_id: str, 
                      evolution_id: str) -> Dict[str, Any]:
        """
        Applique une évolution à une arme
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            evolution_id: Identifiant de l'évolution à appliquer
            
        Returns:
            Résultat de l'application
        """
        # Vérifier l'éligibilité
        player_stats = {}  # Normalement, récupérer les stats du joueur
        eligibility = self.check_evolution_eligibility(player_id, weapon_id, player_stats)
        
        if not eligibility["eligible"]:
            return {
                "success": False,
                "message": eligibility["message"]
            }
            
        # Vérifier si l'évolution spécifiée est disponible
        available_evos = eligibility.get("available_evolutions", [])
        target_evolution = None
        
        for evolution in available_evos:
            if evolution["id"] == evolution_id:
                target_evolution = evolution
                break
                
        if not target_evolution:
            return {
                "success": False,
                "message": f"Évolution {evolution_id} non disponible pour cette arme"
            }
            
        # Récupérer l'instance de l'arme
        instance_key = (player_id, weapon_id)
        weapon_instance = self.weapon_system.get_player_weapon(player_id, weapon_id)
        evolution_progress = self.weapon_system.evolution_progress.get(instance_key)
        
        if not weapon_instance or not evolution_progress:
            return {
                "success": False,
                "message": "Arme ou données d'évolution non trouvées"
            }
            
        # Appliquer les effets de l'évolution
        evolution_effects = target_evolution.get("effects", {})
        
        # 1. Modifier les attributs de base de l'arme
        for attribute, value in evolution_effects.items():
            if attribute not in ["effects", "new_effect"]:
                if isinstance(value, (int, float, str, bool)):
                    # Attribut simple
                    weapon_instance["weapon_data"][attribute] = value
        
        # 2. Modifier les effets existants
        if "effects" in evolution_effects:
            for effect_id, effect_changes in evolution_effects["effects"].items():
                # Trouver l'effet correspondant
                for i, effect in enumerate(weapon_instance["weapon_data"]["effects"]):
                    if effect.get("id") == effect_id:
                        # Appliquer les changements
                        for attribute, value in effect_changes.items():
                            if isinstance(value, dict) and attribute in effect and isinstance(effect[attribute], dict):
                                # Fusion de dictionnaires pour les attributs imbriqués
                                effect[attribute].update(value)
                            else:
                                # Remplacement simple
                                effect[attribute] = value
                        break
        
        # 3. Ajouter un nouvel effet
        if "new_effect" in evolution_effects:
            new_effect = evolution_effects["new_effect"]
            weapon_instance["weapon_data"]["effects"].append(new_effect)
        
        # Mettre à jour les évolutions appliquées
        if instance_key not in self.applied_evolutions:
            self.applied_evolutions[instance_key] = []
            
        self.applied_evolutions[instance_key].append(target_evolution)
        
        # Décrémenter le compteur d'évolutions disponibles
        evolution_progress["evolutions_available"] -= 1
        evolution_progress["evolutions_applied"].append(target_evolution["id"])
        
        logger.info(f"Évolution {target_evolution['name']} appliquée à l'arme {weapon_id} du joueur {player_id}")
        
        return {
            "success": True,
            "message": f"Évolution {target_evolution['name']} appliquée avec succès",
            "evolution": target_evolution,
            "remaining_evolutions": evolution_progress["evolutions_available"]
        }
    
    def get_applied_evolutions(self, player_id: str, weapon_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les évolutions appliquées à une arme
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            
        Returns:
            Liste des évolutions appliquées
        """
        instance_key = (player_id, weapon_id)
        return self.applied_evolutions.get(instance_key, [])
    
    def update_weapon_experience(self, player_id: str, weapon_id: str, 
                               combat_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour l'expérience d'une arme en fonction des résultats de combat
        
        Args:
            player_id: Identifiant du joueur
            weapon_id: Identifiant de l'arme
            combat_result: Résultat du combat
            
        Returns:
            Résultat de la mise à jour
        """
        # Récupérer l'instance de l'arme
        weapon_instance = self.weapon_system.get_player_weapon(player_id, weapon_id)
        if not weapon_instance:
            return {
                "success": False,
                "message": "Arme non trouvée"
            }
            
        # Extraire les données pertinentes du résultat de combat
        damage_dealt = combat_result.get("damage_dealt", 0)
        kills = combat_result.get("kills", 0)
        critical_hits = combat_result.get("critical_hits", 0)
        effects_triggered = combat_result.get("effects_triggered", 0)
        combat_duration = combat_result.get("combat_duration", 0)  # en secondes
        
        # Calculer l'expérience à ajouter
        exp_from_damage = int(damage_dealt * 0.1)
        exp_from_kills = kills * 100
        exp_from_criticals = critical_hits * 20
        exp_from_effects = effects_triggered * 50
        exp_from_duration = int(combat_duration / 60) * 5  # 5 XP par minute
        
        total_exp = exp_from_damage + exp_from_kills + exp_from_criticals + exp_from_effects + exp_from_duration
        
        # Appliquer un modificateur basé sur la rareté de l'arme
        weapon_data = weapon_instance["weapon_data"]
        rarity = weapon_data.get("rarity", SpecialWeaponRarity.UNCOMMON)
        
        rarity_multipliers = {
            SpecialWeaponRarity.UNCOMMON: 1.0,
            SpecialWeaponRarity.RARE: 0.8,
            SpecialWeaponRarity.EPIC: 0.6,
            SpecialWeaponRarity.LEGENDARY: 0.4,
            SpecialWeaponRarity.ARTIFACT: 0.2
        }
        
        rarity_multiplier = rarity_multipliers.get(rarity, 1.0)
        total_exp = int(total_exp * rarity_multiplier)
        
        # Mettre à jour les statistiques de l'arme
        weapon_instance["damage_dealt"] += damage_dealt
        weapon_instance["kill_count"] += kills
        weapon_instance["special_triggers"] += effects_triggered
        
        # Mettre à jour l'expérience de l'arme
        instance_key = (player_id, weapon_id)
        if instance_key in self.weapon_system.evolution_progress:
            evolution_data = self.weapon_system.evolution_progress[instance_key]
            old_level = evolution_data["level"]
            old_evolutions_available = evolution_data["evolutions_available"]
            
            # Ajouter l'expérience
            evolution_data["experience"] += total_exp
            
            # Vérifier les niveaux
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
            
            # Vérifier si des évolutions sont devenues disponibles
            new_evolutions_available = evolution_data["evolutions_available"] - old_evolutions_available
            
            return {
                "success": True,
                "message": f"Expérience mise à jour: +{total_exp} XP",
                "experience_gained": total_exp,
                "current_level": evolution_data["level"],
                "level_up": evolution_data["level"] > old_level,
                "levels_gained": evolution_data["level"] - old_level,
                "current_exp": evolution_data["experience"],
                "next_level_exp": evolution_data["next_level"],
                "new_evolutions_available": new_evolutions_available,
                "total_evolutions_available": evolution_data["evolutions_available"]
            }
        
        return {
            "success": False,
            "message": "Données d'évolution non trouvées"
        }
    
    def generate_random_evolution(self, weapon_instance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère une évolution aléatoire pour une arme
        
        Args:
            weapon_instance: Instance de l'arme
            
        Returns:
            Évolution générée ou None si impossible
        """
        weapon_data = weapon_instance["weapon_data"]
        weapon_type = weapon_data.get("type")
        
        # Base pour une nouvelle évolution
        evolution = {
            "id": f"random_evolution_{random.randint(1000, 9999)}",
            "name": "",
            "description": "",
            "level_requirement": 3,
            "effects": {}
        }
        
        # Types d'évolutions possibles
        evolution_types = [
            "damage_boost",
            "accuracy_improvement",
            "durability_increase",
            "charge_enhancement",
            "effect_power_up",
            "cooldown_reduction",
            "new_minor_effect"
        ]
        
        # Sélectionner un type aléatoire
        evo_type = random.choice(evolution_types)
        
        # Générer l'évolution en fonction du type
        if evo_type == "damage_boost":
            damage_increase = random.randint(5, 15)
            evolution["name"] = "Amplification de Puissance"
            evolution["description"] = f"Augmente les dégâts de base de {damage_increase}"
            evolution["effects"]["base_damage"] = weapon_data.get("base_damage", 20) + damage_increase
            
        elif evo_type == "accuracy_improvement":
            accuracy_increase = round(random.uniform(0.05, 0.15), 2)
            evolution["name"] = "Ciblage Amélioré"
            evolution["description"] = f"Augmente la précision de {int(accuracy_increase * 100)}%"
            evolution["effects"]["accuracy"] = min(0.95, weapon_data.get("accuracy", 0.7) + accuracy_increase)
            
        elif evo_type == "durability_increase":
            durability_increase = random.randint(20, 50)
            evolution["name"] = "Structure Renforcée"
            evolution["description"] = f"Augmente la durabilité de {durability_increase}"
            evolution["effects"]["durability"] = weapon_data.get("durability", 100) + durability_increase
            
        elif evo_type == "charge_enhancement":
            charge_increase = random.randint(20, 50)
            charge_rate_increase = random.randint(2, 8)
            evolution["name"] = "Capacitance Étendue"
            evolution["description"] = f"Augmente la charge maximale de {charge_increase} et le taux de charge de {charge_rate_increase}"
            evolution["effects"]["max_charge"] = weapon_data.get("max_charge", 100) + charge_increase
            evolution["effects"]["charge_rate"] = weapon_data.get("charge_rate", 10) + charge_rate_increase
            
        elif evo_type == "effect_power_up":
            # Sélectionner un effet aléatoire à améliorer
            effects = weapon_data.get("effects", [])
            if effects:
                effect = random.choice(effects)
                effect_id = effect.get("id", "unknown")
                
                evolution["name"] = f"Amélioration: {effect.get('name', 'Effet')}"
                evolution["description"] = f"Renforce les capacités de l'effet {effect.get('name', 'spécial')}"
                
                evolution["effects"]["effects"] = {
                    effect_id: {}
                }
                
                # Améliorer l'effet en fonction de sa catégorie
                if effect.get("category") == "damage":
                    damage_increase = int(effect.get("damage", 20) * 0.2)
                    evolution["effects"]["effects"][effect_id]["damage"] = effect.get("damage", 20) + damage_increase
                    
                elif effect.get("category") == "status":
                    duration_increase = 1
                    strength_increase = 1
                    evolution["effects"]["effects"][effect_id]["status_duration"] = effect.get("status_duration", 3) + duration_increase
                    evolution["effects"]["effects"][effect_id]["status_strength"] = effect.get("status_strength", 1) + strength_increase
                    
                elif effect.get("category") == "utility":
                    # Améliorer en fonction du type d'utilité
                    utility_type = effect.get("utility_type", "UNKNOWN")
                    
                    if utility_type == "SHIELD":
                        shield_increase = int(effect.get("amount", 50) * 0.3)
                        evolution["effects"]["effects"][effect_id]["amount"] = effect.get("amount", 50) + shield_increase
                        
                    elif utility_type == "TELEPORT":
                        distance_increase = 2
                        evolution["effects"]["effects"][effect_id]["distance"] = effect.get("distance", 5) + distance_increase
                        
                    elif utility_type == "HEAL":
                        heal_increase = int(effect.get("amount", 20) * 0.3)
                        evolution["effects"]["effects"][effect_id]["amount"] = effect.get("amount", 20) + heal_increase
            else:
                # Pas d'effet à améliorer, passer à un autre type
                return self.generate_random_evolution(weapon_instance)
                
        elif evo_type == "cooldown_reduction":
            # Sélectionner un effet aléatoire pour réduire son cooldown
            effects = weapon_data.get("effects", [])
            if effects:
                effect = random.choice(effects)
                effect_id = effect.get("id", "unknown")
                
                cooldown_reduction = max(1, int(effect.get("cooldown", 5) * 0.25))
                
                evolution["name"] = "Refroidissement Accéléré"
                evolution["description"] = f"Réduit le temps de recharge de {effect.get('name', 'l''effet spécial')} de {cooldown_reduction} tour(s)"
                
                evolution["effects"]["effects"] = {
                    effect_id: {
                        "cooldown": max(1, effect.get("cooldown", 5) - cooldown_reduction)
                    }
                }
            else:
                # Pas d'effet à améliorer, passer à un autre type
                return self.generate_random_evolution(weapon_instance)
                
        elif evo_type == "new_minor_effect":
            # Créer un petit effet supplémentaire basé sur le type d'arme
            effect_options = []
            
            if weapon_type == SpecialWeaponType.ENERGY:
                effect_options = [
                    {
                        "id": f"energy_spark_{random.randint(1000, 9999)}",
                        "name": "Étincelle Énergétique",
                        "description": "Chance d'infliger des dégâts supplémentaires d'énergie",
                        "category": "damage",
                        "damage": 15,
                        "damage_type": "ENERGY",
                        "max_targets": 1,
                        "trigger_conditions": {
                            "trigger_chance": 0.25,
                            "cooldown_ready": True
                        },
                        "cooldown": 3,
                        "duration": 1
                    }
                ]
            elif weapon_type == SpecialWeaponType.MELEE:
                effect_options = [
                    {
                        "id": f"bleeding_strike_{random.randint(1000, 9999)}",
                        "name": "Frappe Hémorragique",
                        "description": "Chance d'infliger un saignement à la cible",
                        "category": "status",
                        "status_type": "BLEEDING",
                        "status_duration": 3,
                        "status_strength": 2,
                        "application_chance": 0.3,
                        "max_targets": 1,
                        "trigger_conditions": {
                            "trigger_chance": 0.3,
                            "cooldown_ready": True
                        },
                        "cooldown": 4,
                        "duration": 3
                    }
                ]
            elif weapon_type == SpecialWeaponType.PROJECTILE:
                effect_options = [
                    {
                        "id": f"ricocheting_shot_{random.randint(1000, 9999)}",
                        "name": "Tir Ricochet",
                        "description": "Chance que le projectile ricoche vers une cible supplémentaire",
                        "category": "damage",
                        "damage": 10,
                        "damage_multiplier": 0.6,
                        "max_targets": 1,
                        "trigger_conditions": {
                            "trigger_chance": 0.2,
                            "cooldown_ready": True
                        },
                        "cooldown": 5,
                        "duration": 1
                    }
                ]
            elif weapon_type in [SpecialWeaponType.TECH, SpecialWeaponType.EXPERIMENTAL]:
                effect_options = [
                    {
                        "id": f"system_glitch_{random.randint(1000, 9999)}",
                        "name": "Dysfonctionnement Système",
                        "description": "Chance de perturber les systèmes de la cible",
                        "category": "status",
                        "status_type": "DISORIENTED",
                        "status_duration": 2,
                        "status_strength": 1,
                        "application_chance": 0.25,
                        "max_targets": 1,
                        "trigger_conditions": {
                            "trigger_chance": 0.25,
                            "cooldown_ready": True
                        },
                        "cooldown": 6,
                        "duration": 2
                    }
                ]
            
            if effect_options:
                new_effect = random.choice(effect_options)
                evolution["name"] = f"Ajout: {new_effect['name']}"
                evolution["description"] = f"Ajoute un nouvel effet: {new_effect['description']}"
                evolution["effects"]["new_effect"] = new_effect
            else:
                # Pas d'effet disponible pour ce type d'arme, essayer un autre type
                return self.generate_random_evolution(weapon_instance)
        
        return evolution
