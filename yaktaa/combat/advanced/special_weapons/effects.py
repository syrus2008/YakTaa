"""
Effets des armes spéciales pour le système de combat avancé
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialWeapons.Effects")

class EffectTriggerType(Enum):
    """Types de déclencheurs pour les effets spéciaux"""
    ON_HIT = auto()            # À l'impact
    ON_CRITICAL = auto()       # Lors d'un coup critique
    ON_KILL = auto()           # Lors d'une élimination
    ON_CHARGE = auto()         # Lorsque chargé
    ON_LOW_HEALTH = auto()     # À santé basse
    ON_DODGE = auto()          # Après une esquive
    ON_DAMAGE_TAKEN = auto()   # Après avoir subi des dégâts
    ON_COMMAND = auto()        # Sur commande manuelle
    PASSIVE = auto()           # Effet passif permanent

class SpecialWeaponEffect:
    """
    Classe pour gérer les effets des armes spéciales
    """
    
    @staticmethod
    def calculate_effect_damage(effect_data: Dict[str, Any], weapon_instance: Dict[str, Any], 
                              target_stats: Dict[str, Any]) -> int:
        """
        Calcule les dégâts d'un effet spécial
        
        Args:
            effect_data: Données de l'effet
            weapon_instance: Instance de l'arme
            target_stats: Statistiques de la cible
            
        Returns:
            Dégâts calculés
        """
        # Récupérer les données de base
        base_damage = effect_data.get("damage", 0)
        damage_type = effect_data.get("damage_type", "PHYSICAL")
        
        # Multiplicateur de dégâts de l'effet
        damage_multiplier = effect_data.get("damage_multiplier", 1.0)
        
        # Dégâts de base de l'arme
        weapon_base_damage = weapon_instance["weapon_data"].get("base_damage", 0)
        
        # Calculer les dégâts de base
        total_base_damage = base_damage + int(weapon_base_damage * damage_multiplier)
        
        # Appliquer les résistances de la cible
        resist_key = f"{damage_type.lower()}_resist"
        resistance = target_stats.get(resist_key, 0.0)
        
        # Si l'effet ignore l'armure, réduire la résistance
        armor_penetration = effect_data.get("armor_penetration", 0.0)
        if armor_penetration > 0:
            resistance = max(0, resistance - armor_penetration)
            
        # Calculer les dégâts finaux
        damage_multiplier = 1.0 - resistance
        final_damage = int(total_base_damage * damage_multiplier)
        
        # Assurer un minimum de dégâts
        final_damage = max(1, final_damage)
        
        return final_damage
    
    @staticmethod
    def apply_damage_effect(effect_instance_id: str, effect_data: Dict[str, Any], 
                          weapon_instance: Dict[str, Any], targets: List[Dict[str, Any]],
                          combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique un effet de dégâts
        
        Args:
            effect_instance_id: Identifiant de l'instance d'effet
            effect_data: Données de l'effet
            weapon_instance: Instance de l'arme
            targets: Cibles affectées
            combat_context: Contexte du combat
            
        Returns:
            Résultat de l'application
        """
        # Initialiser les résultats
        results = {
            "effect_id": effect_instance_id,
            "effect_type": "damage",
            "targets_affected": 0,
            "total_damage": 0,
            "target_results": []
        }
        
        # Vérifier s'il y a des cibles
        if not targets:
            return results
            
        # Déterminer le nombre de cibles à affecter
        max_targets = effect_data.get("max_targets", 1)
        actual_targets = targets[:max_targets]
        
        # Zone d'effet
        aoe_radius = effect_data.get("aoe_radius", 0)
        if aoe_radius > 0 and len(targets) > 1:
            # Trouver des cibles supplémentaires dans la zone
            primary_target = targets[0]
            aoe_targets = []
            
            for potential_target in targets[1:]:
                # Calculer la distance (simplifiée)
                # Dans un vrai jeu, utiliser la distance réelle basée sur la position
                if "distance" in combat_context:
                    target_distance = combat_context["distance"].get(potential_target.get("id"), 100)
                    if target_distance <= aoe_radius:
                        aoe_targets.append(potential_target)
            
            # Ajouter les cibles de zone à la liste des cibles réelles
            if aoe_targets:
                # Respecter le nombre maximum de cibles
                remaining_slots = max_targets - 1  # -1 pour la cible principale
                aoe_targets_to_add = aoe_targets[:remaining_slots]
                actual_targets.extend(aoe_targets_to_add)
        
        # Appliquer les dégâts à chaque cible
        for target in actual_targets:
            # Calculer les dégâts pour cette cible
            target_stats = target.get("stats", {})
            damage = SpecialWeaponEffect.calculate_effect_damage(effect_data, weapon_instance, target_stats)
            
            # Appliquer les dégâts
            if "health" in target:
                target["health"] = max(0, target["health"] - damage)
            
            # Ajouter aux statistiques
            results["targets_affected"] += 1
            results["total_damage"] += damage
            
            # Ajouter les détails pour cette cible
            target_result = {
                "target_id": target.get("id", "unknown"),
                "damage": damage,
                "health_remaining": target.get("health", 0)
            }
            
            results["target_results"].append(target_result)
            
            # Mettre à jour les statistiques de l'arme
            weapon_instance["damage_dealt"] += damage
            
            # Vérifier si la cible a été éliminée
            if target.get("health", 0) <= 0:
                weapon_instance["kill_count"] += 1
        
        return results
    
    @staticmethod
    def apply_status_effect(effect_instance_id: str, effect_data: Dict[str, Any], 
                          weapon_instance: Dict[str, Any], targets: List[Dict[str, Any]],
                          combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique un effet de statut
        
        Args:
            effect_instance_id: Identifiant de l'instance d'effet
            effect_data: Données de l'effet
            weapon_instance: Instance de l'arme
            targets: Cibles affectées
            combat_context: Contexte du combat
            
        Returns:
            Résultat de l'application
        """
        # Initialiser les résultats
        results = {
            "effect_id": effect_instance_id,
            "effect_type": "status",
            "targets_affected": 0,
            "target_results": []
        }
        
        # Vérifier s'il y a des cibles
        if not targets:
            return results
            
        # Récupérer le type de statut
        status_type = effect_data.get("status_type", "UNKNOWN")
        status_duration = effect_data.get("status_duration", 3)  # 3 tours par défaut
        status_strength = effect_data.get("status_strength", 1)  # Puissance 1 par défaut
        
        # Déterminer le nombre de cibles à affecter
        max_targets = effect_data.get("max_targets", 1)
        actual_targets = targets[:max_targets]
        
        # Appliquer l'effet de statut à chaque cible
        for target in actual_targets:
            # Vérifier si la cible peut recevoir des effets de statut
            if not target.get("can_receive_status_effects", True):
                continue
                
            # Vérifier les résistances aux effets de statut
            target_stats = target.get("stats", {})
            status_resist_key = f"{status_type.lower()}_status_resist"
            status_resistance = target_stats.get(status_resist_key, 0.0)
            
            # Calculer la chance d'application
            base_chance = effect_data.get("application_chance", 1.0)
            final_chance = max(0.05, base_chance - status_resistance)  # Minimum 5% de chance
            
            # Déterminer si l'effet s'applique
            effect_applied = random.random() < final_chance
            
            target_result = {
                "target_id": target.get("id", "unknown"),
                "status_type": status_type,
                "effect_applied": effect_applied,
                "application_chance": final_chance
            }
            
            if effect_applied:
                # Appliquer l'effet de statut
                if "status_effects" not in target:
                    target["status_effects"] = {}
                    
                # Ajouter ou mettre à jour l'effet de statut
                current_time = combat_context.get("combat_time", 0)
                
                target["status_effects"][status_type] = {
                    "type": status_type,
                    "strength": status_strength,
                    "duration": status_duration,
                    "start_time": current_time,
                    "end_time": current_time + status_duration,
                    "source": {
                        "player_id": weapon_instance.get("player_id"),
                        "weapon_id": weapon_instance.get("weapon_id"),
                        "effect_id": effect_instance_id
                    }
                }
                
                # Mettre à jour le compteur
                results["targets_affected"] += 1
                
                # Ajouter des détails supplémentaires
                target_result["duration"] = status_duration
                target_result["strength"] = status_strength
            
            results["target_results"].append(target_result)
        
        return results
    
    @staticmethod
    def apply_utility_effect(effect_instance_id: str, effect_data: Dict[str, Any], 
                           weapon_instance: Dict[str, Any], targets: List[Dict[str, Any]],
                           player_data: Dict[str, Any], combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique un effet utilitaire (non offensif)
        
        Args:
            effect_instance_id: Identifiant de l'instance d'effet
            effect_data: Données de l'effet
            weapon_instance: Instance de l'arme
            targets: Cibles affectées
            player_data: Données du joueur
            combat_context: Contexte du combat
            
        Returns:
            Résultat de l'application
        """
        # Initialiser les résultats
        results = {
            "effect_id": effect_instance_id,
            "effect_type": "utility",
            "utility_type": effect_data.get("utility_type", "UNKNOWN"),
            "success": True,
            "details": {}
        }
        
        utility_type = effect_data.get("utility_type", "UNKNOWN")
        
        # Traiter différents types d'effets utilitaires
        if utility_type == "TELEPORT":
            # Effet de téléportation
            teleport_distance = effect_data.get("distance", 5)
            teleport_direction = effect_data.get("direction", "FORWARD")
            
            # Simuler la téléportation (dans un vrai jeu, modifier la position)
            results["details"] = {
                "teleport_distance": teleport_distance,
                "teleport_direction": teleport_direction,
                "message": f"Téléporté de {teleport_distance} mètres vers {teleport_direction}"
            }
            
        elif utility_type == "STEALTH":
            # Effet de furtivité
            stealth_duration = effect_data.get("duration", 3)
            stealth_level = effect_data.get("level", 1)
            
            # Appliquer l'effet de furtivité au joueur
            if "status_effects" not in player_data:
                player_data["status_effects"] = {}
                
            player_data["status_effects"]["STEALTH"] = {
                "type": "STEALTH",
                "level": stealth_level,
                "duration": stealth_duration,
                "start_time": combat_context.get("combat_time", 0),
                "end_time": combat_context.get("combat_time", 0) + stealth_duration
            }
            
            results["details"] = {
                "stealth_duration": stealth_duration,
                "stealth_level": stealth_level,
                "message": f"Mode furtif activé pour {stealth_duration} tours (niveau {stealth_level})"
            }
            
        elif utility_type == "SHIELD":
            # Effet de bouclier
            shield_amount = effect_data.get("amount", 50)
            shield_duration = effect_data.get("duration", 3)
            
            # Appliquer le bouclier
            if "shields" not in player_data:
                player_data["shields"] = []
                
            shield_data = {
                "id": f"shield_{effect_instance_id}",
                "amount": shield_amount,
                "current": shield_amount,
                "duration": shield_duration,
                "start_time": combat_context.get("combat_time", 0),
                "end_time": combat_context.get("combat_time", 0) + shield_duration
            }
            
            player_data["shields"].append(shield_data)
            
            results["details"] = {
                "shield_amount": shield_amount,
                "shield_duration": shield_duration,
                "message": f"Bouclier d'énergie activé: {shield_amount} points pour {shield_duration} tours"
            }
            
        elif utility_type == "SCAN":
            # Effet de scan des ennemis
            scan_range = effect_data.get("range", 10)
            reveal_weakness = effect_data.get("reveal_weakness", False)
            
            # Dans un vrai jeu, cela révélerait les ennemis à proximité
            # Pour cette simulation, juste retourner les informations de scan
            
            num_enemies_scanned = min(len(targets), effect_data.get("max_targets", 5))
            
            results["details"] = {
                "scan_range": scan_range,
                "enemies_scanned": num_enemies_scanned,
                "reveal_weakness": reveal_weakness,
                "message": f"Scan terminé: {num_enemies_scanned} ennemis détectés"
            }
            
            if reveal_weakness and targets:
                # Simuler la révélation des faiblesses
                weaknesses = []
                for i, target in enumerate(targets[:num_enemies_scanned]):
                    target_stats = target.get("stats", {})
                    # Trouver la résistance la plus faible
                    resist_types = ["physical", "energy", "thermal", "chemical", "emp"]
                    lowest_resist = "physical"
                    lowest_value = 1.0
                    
                    for resist_type in resist_types:
                        resist_key = f"{resist_type}_resist"
                        resist_value = target_stats.get(resist_key, 0.0)
                        if resist_value < lowest_value:
                            lowest_value = resist_value
                            lowest_resist = resist_type
                    
                    weaknesses.append({
                        "target_id": target.get("id", f"enemy_{i}"),
                        "weakness": lowest_resist.upper(),
                        "resist_value": lowest_value
                    })
                
                results["details"]["weaknesses"] = weaknesses
            
        elif utility_type == "HEAL":
            # Effet de soin
            heal_amount = effect_data.get("amount", 20)
            heal_percentage = effect_data.get("percentage", 0.0)
            
            # Calculer la quantité de soin
            total_heal = heal_amount
            if heal_percentage > 0 and "max_health" in player_data:
                total_heal += int(player_data["max_health"] * heal_percentage)
                
            # Appliquer les soins
            if "health" in player_data and "max_health" in player_data:
                old_health = player_data["health"]
                player_data["health"] = min(player_data["max_health"], player_data["health"] + total_heal)
                actual_heal = player_data["health"] - old_health
                
                results["details"] = {
                    "heal_amount": total_heal,
                    "actual_heal": actual_heal,
                    "new_health": player_data["health"],
                    "message": f"Soins appliqués: +{actual_heal} PV"
                }
            else:
                results["success"] = False
                results["details"] = {
                    "message": "Impossible d'appliquer les soins: données de santé manquantes"
                }
        
        else:
            # Type d'effet utilitaire non reconnu
            results["success"] = False
            results["details"] = {
                "message": f"Type d'effet utilitaire non pris en charge: {utility_type}"
            }
        
        return results
    
    @staticmethod
    def process_effect(effect_instance_id: str, effect_data: Dict[str, Any], 
                     weapon_instance: Dict[str, Any], targets: List[Dict[str, Any]],
                     player_data: Dict[str, Any], combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite un effet spécial en fonction de son type
        
        Args:
            effect_instance_id: Identifiant de l'instance d'effet
            effect_data: Données de l'effet
            weapon_instance: Instance de l'arme
            targets: Cibles affectées
            player_data: Données du joueur
            combat_context: Contexte du combat
            
        Returns:
            Résultat du traitement
        """
        effect_category = effect_data.get("category", "damage")
        
        if effect_category == "damage":
            return SpecialWeaponEffect.apply_damage_effect(
                effect_instance_id, effect_data, weapon_instance, targets, combat_context)
        elif effect_category == "status":
            return SpecialWeaponEffect.apply_status_effect(
                effect_instance_id, effect_data, weapon_instance, targets, combat_context)
        elif effect_category == "utility":
            return SpecialWeaponEffect.apply_utility_effect(
                effect_instance_id, effect_data, weapon_instance, targets, player_data, combat_context)
        else:
            # Catégorie d'effet non reconnue
            return {
                "effect_id": effect_instance_id,
                "effect_type": "unknown",
                "success": False,
                "message": f"Catégorie d'effet non reconnue: {effect_category}"
            }
