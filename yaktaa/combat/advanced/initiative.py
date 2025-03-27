"""
Système d'initiative avancé pour le combat dans YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("YakTaa.Combat.Advanced.Initiative")

class InitiativeSystem:
    """
    Système d'initiative avancé qui gère l'ordre des tours en combat
    avec des modificateurs basés sur les statistiques, équipements et situations
    """
    
    def __init__(self):
        """Initialise le système d'initiative"""
        self.initiative_order = []
        self.surprise_status = {}  # Acteur -> booléen (surpris ou non)
        self.initiative_modifiers = {}  # Acteur -> modificateurs d'initiative
        self.interrupt_actions = {}  # Acteur -> actions d'interruption disponibles
        
        logger.debug("Système d'initiative avancé initialisé")
    
    def calculate_initiative(self, participants: List[Any]) -> List[Tuple[Any, int]]:
        """
        Calcule l'ordre d'initiative pour tous les participants au combat
        
        Args:
            participants: Liste des participants au combat (joueur et ennemis)
            
        Returns:
            Liste triée des participants avec leur valeur d'initiative
        """
        initiative_values = []
        
        for participant in participants:
            # Base d'initiative: réflexes + agilité/2
            base_initiative = self._get_attribute(participant, "reflexes", 5)
            base_initiative += self._get_attribute(participant, "agility", 5) // 2
            
            # Modificateurs d'équipement
            equipment_mod = self._calculate_equipment_modifier(participant)
            
            # Modificateurs de statut
            status_mod = self._calculate_status_modifier(participant)
            
            # Modificateur de surprise
            surprise_mod = -5 if self.surprise_status.get(participant, False) else 0
            
            # Jet de dé (1-10)
            dice_roll = random.randint(1, 10)
            
            # Initiative finale
            final_initiative = base_initiative + equipment_mod + status_mod + surprise_mod + dice_roll
            
            # Enregistrer la valeur
            initiative_values.append((participant, final_initiative))
            
            logger.debug(f"Initiative calculée pour {getattr(participant, 'name', str(participant))}: {final_initiative} "
                        f"(Base: {base_initiative}, Équipement: {equipment_mod}, Statut: {status_mod}, "
                        f"Surprise: {surprise_mod}, Dé: {dice_roll})")
        
        # Trier par initiative (décroissant)
        initiative_values.sort(key=lambda x: x[1], reverse=True)
        self.initiative_order = [p for p, _ in initiative_values]
        
        return initiative_values
    
    def _get_attribute(self, participant: Any, attribute_name: str, default: int = 0) -> int:
        """Récupère la valeur d'un attribut d'un participant"""
        # Pour le joueur, utiliser get_effective_stats
        if hasattr(participant, "get_effective_stats"):
            stats = participant.get_effective_stats()
            return stats.get(attribute_name, default)
        
        # Pour les autres personnages
        return getattr(participant, attribute_name, default)
    
    def _calculate_equipment_modifier(self, participant: Any) -> int:
        """Calcule le modificateur d'initiative basé sur l'équipement"""
        modifier = 0
        
        # Vérifier si le participant a un équipement actif
        if hasattr(participant, "active_equipment"):
            # Bonus des implants
            for slot, item in participant.active_equipment.items():
                if item and slot.startswith("implant_") and hasattr(item, "get_combat_bonus"):
                    initiative_bonus = item.get_combat_bonus("initiative")
                    modifier += initiative_bonus
            
            # Malus des armes lourdes
            weapon = participant.active_equipment.get("weapon")
            if weapon and hasattr(weapon, "weight"):
                if weapon.weight > 5.0:  # Arme lourde
                    modifier -= int(weapon.weight / 2)
        
        return modifier
    
    def _calculate_status_modifier(self, participant: Any) -> int:
        """Calcule le modificateur d'initiative basé sur les statuts actifs"""
        modifier = 0
        
        # Vérifier les statuts qui affectent l'initiative
        status_effects = getattr(participant, "status_effects", {})
        
        # Exemples de statuts affectant l'initiative
        if "stunned" in status_effects:
            modifier -= 5
        if "slowed" in status_effects:
            modifier -= 3
        if "haste" in status_effects:
            modifier += 5
        
        return modifier
    
    def register_interrupt_action(self, actor: Any, action_type: str, 
                                  condition: Dict[str, Any], cost: Dict[str, Any]) -> None:
        """
        Enregistre une action d'interruption pour un acteur
        
        Args:
            actor: L'acteur qui peut interrompre
            action_type: Type d'action d'interruption (contre-attaque, esquive, etc.)
            condition: Conditions pour déclencher l'interruption
            cost: Coût de l'interruption (points d'action, énergie, etc.)
        """
        if actor not in self.interrupt_actions:
            self.interrupt_actions[actor] = []
            
        self.interrupt_actions[actor].append({
            "type": action_type,
            "condition": condition,
            "cost": cost,
            "used": False
        })
        
        logger.debug(f"Action d'interruption {action_type} enregistrée pour {getattr(actor, 'name', str(actor))}")
    
    def check_interrupts(self, actor: Any, target: Any, action_type: str) -> List[Dict[str, Any]]:
        """
        Vérifie si des actions d'interruption se déclenchent
        
        Args:
            actor: L'acteur qui effectue l'action
            target: La cible de l'action
            action_type: Le type d'action effectuée
            
        Returns:
            Liste des interruptions déclenchées
        """
        triggered_interrupts = []
        
        # Vérifier les interruptions pour chaque acteur
        for interrupter, actions in self.interrupt_actions.items():
            # Ne pas interrompre ses propres actions
            if interrupter == actor:
                continue
                
            for action in actions:
                # Vérifier si l'action n'a pas déjà été utilisée
                if action["used"]:
                    continue
                    
                # Vérifier les conditions de déclenchement
                condition = action["condition"]
                
                # Condition: être la cible
                if condition.get("is_target", False) and interrupter != target:
                    continue
                    
                # Condition: type d'action
                if "action_types" in condition and action_type not in condition["action_types"]:
                    continue
                
                # Autres conditions possibles...
                
                # L'interruption est déclenchée
                triggered_interrupts.append({
                    "interrupter": interrupter,
                    "action": action
                })
                
                # Marquer comme utilisée
                action["used"] = True
                
                logger.debug(f"Interruption {action['type']} déclenchée par {getattr(interrupter, 'name', str(interrupter))}")
        
        return triggered_interrupts
    
    def reset_interrupts(self) -> None:
        """Réinitialise les actions d'interruption utilisées"""
        for actor, actions in self.interrupt_actions.items():
            for action in actions:
                action["used"] = False
    
    def set_surprise(self, actor: Any, is_surprised: bool) -> None:
        """
        Définit si un acteur est surpris au début du combat
        
        Args:
            actor: L'acteur concerné
            is_surprised: True si l'acteur est surpris
        """
        self.surprise_status[actor] = is_surprised
        logger.debug(f"{getattr(actor, 'name', str(actor))} est {'surpris' if is_surprised else 'prêt au combat'}")
    
    def add_initiative_modifier(self, actor: Any, modifier: int, reason: str, duration: int = 1) -> None:
        """
        Ajoute un modificateur temporaire à l'initiative d'un acteur
        
        Args:
            actor: L'acteur concerné
            modifier: Valeur du modificateur
            reason: Raison du modificateur
            duration: Durée en tours
        """
        if actor not in self.initiative_modifiers:
            self.initiative_modifiers[actor] = []
            
        self.initiative_modifiers[actor].append({
            "value": modifier,
            "reason": reason,
            "duration": duration
        })
        
        logger.debug(f"Modificateur d'initiative {modifier} ajouté à {getattr(actor, 'name', str(actor))} pour {duration} tours: {reason}")
    
    def update_modifiers(self) -> None:
        """Met à jour les modificateurs d'initiative (réduction de la durée)"""
        for actor, modifiers in self.initiative_modifiers.items():
            # Réduire la durée de chaque modificateur
            for modifier in modifiers[:]:  # Copie de la liste pour éviter les problèmes de modification pendant l'itération
                modifier["duration"] -= 1
                
                # Supprimer les modificateurs expirés
                if modifier["duration"] <= 0:
                    modifiers.remove(modifier)
                    logger.debug(f"Modificateur d'initiative {modifier['value']} expiré pour {getattr(actor, 'name', str(actor))}")
