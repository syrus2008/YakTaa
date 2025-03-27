# YakTaa - Moteur de combat
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum, auto

# Configurer le logger
logger = logging.getLogger(__name__)

class CombatStatus(Enum):
    """Statuts possibles d'un combat"""
    PREPARATION = auto()
    IN_PROGRESS = auto()
    PLAYER_VICTORY = auto()
    ENEMY_VICTORY = auto()
    ESCAPED = auto()
    ABORTED = auto()

class DamageType(Enum):
    """Types de dégâts possibles"""
    PHYSICAL = auto()    # Dégâts physiques (armes à projectiles, lames)
    ENERGY = auto()      # Dégâts énergétiques (lasers, plasma)
    EMP = auto()         # Dégâts électromagnétiques (contre les ennemis robotiques ou cyborg)
    BIOHAZARD = auto()   # Dégâts biologiques (armes chimiques, toxines)
    CYBER = auto()       # Dégâts informatiques (contre les PNJ à forte intégration cybernétique)
    VIRAL = auto()       # Dégâts viraux (déstabilise les systèmes électroniques et biologiques)
    NANITE = auto()      # Dégâts par nanites (progressive, effets secondaires)

class ActionType(Enum):
    """Types d'actions possibles pendant un combat"""
    ATTACK = auto()      # Attaque avec l'arme équipée
    HACK = auto()        # Tentative de hacking d'un ennemi robotique ou cybernétique
    USE_ITEM = auto()    # Utilisation d'un objet de l'inventaire
    ACTIVATE_IMPLANT = auto() # Activation d'un implant spécial
    DEFEND = auto()      # Position défensive, réduction des dégâts reçus
    ESCAPE = auto()      # Tentative de fuite
    SCAN = auto()        # Analyse des points faibles de l'ennemi
    SPECIAL = auto()     # Action spéciale

class CombatEngine:
    """Moteur de gestion des combats"""
    
    def __init__(self, player: Any, enemies: List[Any], environment: Dict[str, Any] = None):
        """Initialise un nouveau combat
        
        Args:
            player: Le joueur participant au combat
            enemies: Liste des ennemis à combattre
            environment: Propriétés de l'environnement pouvant influencer le combat
        """
        self.player = player
        self.enemies = enemies
        self.environment = environment or {}
        self.status = CombatStatus.PREPARATION
        self.current_turn = 0
        self.initiative_order = []  # Liste ordonnée des participants selon leur initiative
        self.current_actor = None   # Participant dont c'est le tour
        self.log_messages = []      # Historique des messages de combat
        self.active_effects = {}    # Effets de statut actifs pour chaque participant
        
        # Initialisation des systèmes avancés
        self._init_advanced_systems()
        
        # Logging
        logger.info(f"Combat initialisé entre {player.name} et {len(enemies)} ennemi(s)")
        
    def _init_advanced_systems(self):
        """Initialise les systèmes de combat avancés"""
        try:
            # Import des systèmes avancés
            from .advanced import (
                InitiativeSystem, 
                TacticalCombatSystem,
                StatusEffectSystem,
                SpecialActionSystem,
                DefenseSystem,
                EnemyAISystem,
                CombatEnvironmentSystem,
                GroupCombatSystem,
                CombatProgressionSystem,
                SpecialWeaponSystem,
                WeaponEvolutionSystem,
                WeaponCraftingSystem,
                initialize_special_weapons
            )
            
            # Initialisation des systèmes
            self.initiative_system = InitiativeSystem()
            self.tactical_system = TacticalCombatSystem()
            self.status_effect_system = StatusEffectSystem()
            self.special_action_system = SpecialActionSystem()
            self.defense_system = DefenseSystem()
            self.ai_system = EnemyAISystem()
            self.environment_system = CombatEnvironmentSystem()
            self.group_system = GroupCombatSystem()
            self.progression_system = CombatProgressionSystem()
            
            # Initialisation du système d'armes spéciales
            self.special_weapon_system = SpecialWeaponSystem()
            initialize_special_weapons(self.special_weapon_system)
            self.weapon_evolution_system = WeaponEvolutionSystem(self.special_weapon_system)
            self.weapon_crafting_system = WeaponCraftingSystem(self.special_weapon_system)
            
            self.advanced_systems_enabled = True
            logger.info("Systèmes de combat avancés initialisés avec succès")
        except ImportError as e:
            logger.warning(f"Impossible d'initialiser les systèmes de combat avancés: {e}")
            self.advanced_systems_enabled = False
    
    def start_combat(self) -> None:
        """Démarre le combat"""
        if self.status != CombatStatus.PREPARATION:
            logger.warning("Impossible de démarrer un combat déjà en cours")
            return
            
        # Déterminer l'ordre d'initiative
        self._calculate_initiative()
        
        # Appliquer les effets des implants du joueur au début du combat
        player_effects = self.player.apply_implant_effects()
        if player_effects.get("active_effects"):
            self.active_effects[self.player] = player_effects.get("active_effects", [])
            for msg in player_effects.get("messages", []):
                self.log_message(msg)
        
        self.status = CombatStatus.IN_PROGRESS
        self.current_turn = 1
        self.current_actor = self.initiative_order[0]
        
        self.log_message(f"Combat démarré ! Tour {self.current_turn}")
        self.log_message(f"C'est au tour de {self.current_actor.name}")
        
    def _calculate_initiative(self) -> None:
        """Calcule l'ordre d'initiative pour le combat"""
        participants = [self.player] + self.enemies
        
        # Calculer le score d'initiative pour chaque participant
        initiative_scores = {}
        for participant in participants:
            # Base d'initiative
            if hasattr(participant, 'get_effective_stats'):
                # Pour le joueur et les PNJ avancés avec des stats
                stats = participant.get_effective_stats()
                base_initiative = stats.get('reflexes', 5) + stats.get('intelligence', 5)
            else:
                # Pour les ennemis simples
                base_initiative = getattr(participant, 'initiative', 10)
            
            # Ajouter un élément aléatoire
            roll = random.randint(1, 10)
            initiative_scores[participant] = base_initiative + roll
        
        # Trier les participants par score d'initiative décroissant
        self.initiative_order = sorted(
            participants,
            key=lambda p: initiative_scores.get(p, 0),
            reverse=True
        )
        
        # Journaliser l'ordre d'initiative
        initiative_log = "Ordre d'initiative : " + ", ".join([f"{p.name} ({initiative_scores[p]})" for p in self.initiative_order])
        self.log_message(initiative_log)
    
    def next_turn(self) -> Dict[str, Any]:
        """Passe au participant suivant ou au tour suivant si tout le monde a joué"""
        if self.status != CombatStatus.IN_PROGRESS:
            return {"status": self.status, "message": "Le combat est terminé"}
            
        # Trouver l'index du participant actuel
        current_index = self.initiative_order.index(self.current_actor)
        
        # Passer au participant suivant
        next_index = (current_index + 1) % len(self.initiative_order)
        self.current_actor = self.initiative_order[next_index]
        
        # Si on a fait le tour complet des participants, augmenter le compteur de tour
        if next_index == 0:
            self.current_turn += 1
            self.log_message(f"===== TOUR {self.current_turn} =====")
            
            # Appliquer les effets persistants (dégâts au fil du temps, etc.)
            self._apply_persistent_effects()
            
        # Vérifier les conditions de victoire/défaite à chaque début de tour
        self._check_combat_status()
            
        if self.status == CombatStatus.IN_PROGRESS:
            self.log_message(f"C'est au tour de {self.current_actor.name}")
        
        return {
            "status": self.status,
            "current_turn": self.current_turn,
            "current_actor": self.current_actor,
            "message": f"C'est au tour de {self.current_actor.name}"
        }
    
    def _apply_persistent_effects(self):
        """Applique les effets persistants à tous les participants"""
        # Implémentation des effets persistants comme saignement, poison, etc.
        pass
        
    def _check_combat_status(self) -> None:
        """Vérifie si le combat est terminé"""
        # Vérifier si le joueur est vaincu
        if self.player.health <= 0:
            self.status = CombatStatus.ENEMY_VICTORY
            self.log_message("Vous avez été vaincu !")
            return
            
        # Vérifier si tous les ennemis sont vaincus
        if all(enemy.health <= 0 for enemy in self.enemies):
            self.status = CombatStatus.PLAYER_VICTORY
            self.log_message("Vous avez vaincu tous les ennemis !")
            return
    
    def perform_action(self, action_type: ActionType, target: Any = None, item: Any = None) -> Dict[str, Any]:
        """
        Exécute une action pendant le combat
        
        Args:
            action_type: Type d'action à effectuer
            target: Cible de l'action (si applicable)
            item: Objet à utiliser (si applicable)
            
        Returns:
            Résultat de l'action
        """
        result = {"success": False, "message": "Action non reconnue"}
        
        # Vérifier si c'est bien le tour de ce participant
        if self.current_actor != self.player and action_type != ActionType.DEFEND:
            return {"success": False, "message": "Ce n'est pas votre tour"}
            
        # Exécuter l'action selon son type
        if action_type == ActionType.ATTACK:
            if target is None:
                return {"success": False, "message": "Pas de cible spécifiée pour l'attaque"}
                
            # Utiliser le système avancé si disponible
            if hasattr(self, 'advanced_systems_enabled') and self.advanced_systems_enabled:
                # Déterminer s'il faut utiliser un effet d'arme spéciale
                special_weapon = self._get_active_special_weapon()
                if special_weapon:
                    # Vérifier si des effets spéciaux peuvent s'activer
                    combat_context = self._create_combat_context(target)
                    activation_result = self.special_weapon_system.check_special_activation(
                        self.player.id, 
                        special_weapon["weapon_id"],
                        combat_context
                    )
                    
                    if activation_result["can_activate"] and activation_result.get("available_effects"):
                        # Utiliser le premier effet disponible
                        effect = activation_result["available_effects"][0]
                        effect_result = self.special_weapon_system.trigger_special_effect(
                            self.player.id,
                            special_weapon["weapon_id"],
                            effect["id"],
                            combat_context
                        )
                        
                        if effect_result["success"]:
                            result = effect_result
                            self.log_message(f"Effet spécial activé: {effect['name']}")
                            return result
            
            # Attaque standard si pas d'effet spécial
            result = self._perform_attack(target)
            
        elif action_type == ActionType.DEFEND:
            # TODO: Implémenter la défense
            result = {"success": True, "message": "Vous adoptez une posture défensive"}
            
        elif action_type == ActionType.USE_ITEM:
            if item is None:
                return {"success": False, "message": "Pas d'objet spécifié à utiliser"}
                
            # TODO: Implémenter l'utilisation d'objets
            result = {"success": False, "message": "Utilisation d'objets non implémentée"}
            
        elif action_type == ActionType.SPECIAL:
            if hasattr(self, 'advanced_systems_enabled') and self.advanced_systems_enabled:
                # Utiliser le système d'actions spéciales
                result = self.special_action_system.perform_special_action(self.player, target, self._create_combat_context(target))
            else:
                result = {"success": False, "message": "Actions spéciales non disponibles"}
                
        elif action_type == ActionType.ESCAPE:
            # Calcul de la chance de fuite
            escape_chance = 0.5  # 50% de base
            
            # Ajustements selon l'état du combat
            if len(self.enemies) > 3:
                escape_chance -= 0.2  # Plus difficile de fuir face à de nombreux ennemis
                
            # Tentative de fuite
            if random.random() < escape_chance:
                self.status = CombatStatus.ESCAPED
                result = {"success": True, "message": "Vous avez réussi à fuir le combat"}
            else:
                result = {"success": False, "message": "Vous n'avez pas réussi à fuir"}
                
        # Enregistrement du résultat dans les logs
        self.log_message(result["message"])
        
        # Passer au tour suivant si l'action a réussi
        if result["success"] and self.status == CombatStatus.IN_PROGRESS:
            self.next_turn()
            
        return result

    def _get_active_special_weapon(self) -> Optional[Dict[str, Any]]:
        """Récupère l'arme spéciale active du joueur s'il en possède une"""
        if not hasattr(self, 'special_weapon_system') or not hasattr(self.player, 'id'):
            return None
            
        # Vérifier si le joueur a une arme équipée
        if not hasattr(self.player, 'active_equipment') or 'weapon' not in self.player.active_equipment:
            return None
            
        active_weapon = self.player.active_equipment.get('weapon')
        if not active_weapon:
            return None
            
        # Vérifier si l'arme est une arme spéciale
        weapon_id = active_weapon.get('id')
        if not weapon_id:
            return None
            
        # Rechercher l'arme dans le système d'armes spéciales
        return self.special_weapon_system.get_player_weapon(self.player.id, weapon_id)
        
    def _create_combat_context(self, target: Any = None) -> Dict[str, Any]:
        """Crée un contexte de combat pour les systèmes avancés"""
        context = {
            "combat_time": self.current_turn,
            "player_health_percent": self.player.health / self.player.max_health * 100 if hasattr(self.player, 'max_health') else 100,
            "enemy_count": len(self.enemies),
            "current_actor": self.current_actor,
            "environment": self.environment,
            "is_critical": random.random() < 0.2,  # 20% de chance d'être critique pour ce contexte
        }
        
        if target:
            context["target"] = target
            
        return context

    def _perform_attack(self, target: Any) -> Dict[str, Any]:
        """Exécute une attaque contre une cible"""
        if not target:
            return {"success": False, "message": "Aucune cible sélectionnée pour l'attaque"}
            
        # Calculer les dégâts infligés
        damage_result = self.player.calculate_weapon_damage(target)
        
        # Appliquer les résistances de la cible
        damage_type = damage_result.get("type", "PHYSICAL")
        resistance = getattr(target, f"resistance_{damage_type.lower()}", 0)
        damage_multiplier = 1.0 - (resistance / 100)
        final_damage = max(1, int(damage_result["damage"] * damage_multiplier))
        
        # Appliquer les dégâts à la cible
        target.health -= final_damage
        
        # Appliquer les effets spéciaux de l'arme
        applied_effects = []
        for effect in damage_result.get("special_effects", []):
            if effect not in self.active_effects.get(target, []):
                self.active_effects.setdefault(target, []).append(effect)
                applied_effects.append(effect)
        
        # Créer le message de résultat
        message = f"{self.player.name} attaque {target.name} et inflige {final_damage} dégâts"
        if damage_result.get("critical", False):
            message += " (CRITIQUE!)"
        if resistance > 0:
            message += f" ({target.name} résiste à {resistance}% des dégâts {damage_type})"
        if applied_effects:
            message += f" Effets appliqués: {', '.join(applied_effects)}"
            
        return {
            "success": True,
            "message": message,
            "damage": final_damage,
            "critical": damage_result.get("critical", False),
            "effects_applied": applied_effects,
            "target_health": target.health
        }
    
    def log_message(self, message: str) -> None:
        """Ajoute un message à l'historique du combat"""
        self.log_messages.append(message)
        logger.debug(f"Combat log: {message}")
        
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du combat"""
        return {
            "status": self.status,
            "current_turn": self.current_turn,
            "current_actor": self.current_actor,
            "player_health": self.player.health,
            "enemies": [(enemy.name, enemy.health) for enemy in self.enemies],
            "active_effects": {getattr(participant, 'name', str(participant)): effects 
                               for participant, effects in self.active_effects.items()},
            "messages": self.log_messages[-5:] if self.log_messages else []
        }
