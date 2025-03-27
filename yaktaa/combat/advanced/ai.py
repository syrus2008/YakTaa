"""
Système d'intelligence artificielle pour les ennemis en combat dans YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.EnemyAI")

class TacticType(Enum):
    """Types de tactiques pour les ennemis"""
    AGGRESSIVE = auto()    # Attaques prioritaires
    DEFENSIVE = auto()     # Défense prioritaire
    BALANCED = auto()      # Équilibre attaque/défense
    SUPPORT = auto()       # Soutien des alliés
    FLANKING = auto()      # Contournement et attaques à revers
    RANGED = auto()        # Attaques à distance
    BERSERKER = auto()     # Attaques puissantes sans défense
    TACTICAL = auto()      # Utilisation intelligente de l'environnement

class EnemyAISystem:
    """
    Système qui gère l'intelligence artificielle des ennemis en combat
    """
    
    def __init__(self):
        """Initialise le système d'IA des ennemis"""
        self.enemy_tactics = {}  # Ennemi -> tactique
        self.threat_levels = {}  # Ennemi -> dict de menaces (cible -> niveau)
        self.group_tactics = {}  # Groupe -> tactique de groupe
        self.action_history = {}  # Ennemi -> historique des actions
        
        logger.debug("Système d'IA des ennemis initialisé")
    
    def register_enemy(self, enemy: Any) -> None:
        """
        Enregistre un ennemi dans le système d'IA
        
        Args:
            enemy: L'ennemi à enregistrer
        """
        if enemy in self.enemy_tactics:
            return
            
        # Déterminer la tactique en fonction du type d'ennemi
        enemy_type = getattr(enemy, "enemy_type", "STANDARD")
        enemy_class = getattr(enemy, "enemy_class", "GRUNT")
        
        tactic = self._determine_tactic(enemy_type, enemy_class)
        
        self.enemy_tactics[enemy] = tactic
        self.threat_levels[enemy] = {}
        self.action_history[enemy] = []
        
        logger.debug(f"Ennemi {getattr(enemy, 'name', str(enemy))} enregistré avec la tactique {tactic.name}")
    
    def _determine_tactic(self, enemy_type: str, enemy_class: str) -> TacticType:
        """Détermine la tactique en fonction du type et de la classe d'ennemi"""
        # Tactiques par type d'ennemi
        type_tactics = {
            "HUMAN": TacticType.BALANCED,
            "ROBOT": TacticType.TACTICAL,
            "DRONE": TacticType.RANGED,
            "CYBORG": TacticType.AGGRESSIVE,
            "MUTANT": TacticType.BERSERKER,
            "SECURITY": TacticType.DEFENSIVE,
            "HACKER": TacticType.SUPPORT
        }
        
        # Tactiques par classe d'ennemi
        class_tactics = {
            "GRUNT": TacticType.AGGRESSIVE,
            "ELITE": TacticType.TACTICAL,
            "SNIPER": TacticType.RANGED,
            "TANK": TacticType.DEFENSIVE,
            "SUPPORT": TacticType.SUPPORT,
            "ASSASSIN": TacticType.FLANKING,
            "BOSS": TacticType.BALANCED
        }
        
        # Déterminer la tactique de base
        base_tactic = type_tactics.get(enemy_type, TacticType.BALANCED)
        
        # Ajuster en fonction de la classe
        class_tactic = class_tactics.get(enemy_class, TacticType.BALANCED)
        
        # 70% de chance d'utiliser la tactique de classe, 30% la tactique de type
        if random.random() < 0.7:
            return class_tactic
        else:
            return base_tactic
    
    def register_group(self, enemies: List[Any], group_id: str = None) -> str:
        """
        Enregistre un groupe d'ennemis pour la coordination
        
        Args:
            enemies: Liste des ennemis du groupe
            group_id: Identifiant du groupe (généré si None)
            
        Returns:
            Identifiant du groupe
        """
        # Générer un ID de groupe si non fourni
        if group_id is None:
            group_id = f"group_{random.randint(1000, 9999)}"
            
        # Enregistrer chaque ennemi
        for enemy in enemies:
            self.register_enemy(enemy)
            
        # Déterminer la tactique de groupe
        group_tactic = self._determine_group_tactic(enemies)
        
        self.group_tactics[group_id] = {
            "enemies": enemies,
            "tactic": group_tactic,
            "leader": self._select_group_leader(enemies),
            "formation": "STANDARD"
        }
        
        logger.debug(f"Groupe d'ennemis {group_id} enregistré avec la tactique {group_tactic.name}")
        
        return group_id
    
    def _determine_group_tactic(self, enemies: List[Any]) -> TacticType:
        """Détermine la tactique de groupe en fonction des ennemis"""
        # Compter les types de tactiques individuelles
        tactic_counts = {}
        
        for enemy in enemies:
            if enemy in self.enemy_tactics:
                tactic = self.enemy_tactics[enemy]
                tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1
        
        # Si le groupe est vide, utiliser une tactique par défaut
        if not tactic_counts:
            return TacticType.BALANCED
            
        # Trouver la tactique la plus commune
        most_common_tactic = max(tactic_counts.items(), key=lambda x: x[1])[0]
        
        # 70% de chance d'utiliser la tactique la plus commune
        if random.random() < 0.7:
            return most_common_tactic
        else:
            # 30% de chance de choisir une tactique aléatoire
            return random.choice(list(TacticType))
    
    def _select_group_leader(self, enemies: List[Any]) -> Optional[Any]:
        """Sélectionne le leader du groupe"""
        if not enemies:
            return None
            
        # Critères de sélection du leader
        leader_scores = {}
        
        for enemy in enemies:
            score = 0
            
            # Le niveau est un bon indicateur
            score += getattr(enemy, "level", 1) * 10
            
            # Les ennemis d'élite ou boss sont de meilleurs leaders
            enemy_class = getattr(enemy, "enemy_class", "GRUNT")
            if enemy_class == "ELITE":
                score += 50
            elif enemy_class == "BOSS":
                score += 100
                
            # Les ennemis avec plus de PV sont de meilleurs leaders
            score += getattr(enemy, "max_health", 100) / 10
            
            # Les ennemis avec de meilleures statistiques mentales sont de meilleurs leaders
            if hasattr(enemy, "get_effective_stats"):
                stats = enemy.get_effective_stats()
                score += stats.get("intelligence", 0) * 5
                score += stats.get("perception", 0) * 3
            
            leader_scores[enemy] = score
        
        # Sélectionner l'ennemi avec le score le plus élevé
        return max(leader_scores.items(), key=lambda x: x[1])[0]
    
    def update_threat_levels(self, enemy: Any, targets: List[Any], combat_data: Dict[str, Any]) -> None:
        """
        Met à jour les niveaux de menace pour un ennemi
        
        Args:
            enemy: L'ennemi concerné
            targets: Liste des cibles potentielles
            combat_data: Données du combat
        """
        if enemy not in self.threat_levels:
            self.register_enemy(enemy)
            
        # Initialiser les niveaux de menace si nécessaire
        for target in targets:
            if target not in self.threat_levels[enemy]:
                self.threat_levels[enemy][target] = 50  # Niveau de base
        
        # Mettre à jour les niveaux de menace en fonction des actions récentes
        recent_actions = combat_data.get("recent_actions", [])
        
        for action in recent_actions:
            actor = action.get("actor")
            target = action.get("target")
            action_type = action.get("type")
            
            # Ignorer les actions non pertinentes
            if actor is None or target is None:
                continue
                
            # Si l'action est dirigée contre l'ennemi
            if target == enemy:
                # Augmenter le niveau de menace de l'acteur
                threat_increase = 0
                
                if action_type == "ATTACK":
                    damage = action.get("damage", 0)
                    # Plus les dégâts sont élevés, plus la menace augmente
                    threat_increase = min(30, damage / 2)
                elif action_type == "DEBUFF":
                    # Les débuffs sont menaçants
                    threat_increase = 15
                elif action_type == "CONTROL":
                    # Les effets de contrôle sont très menaçants
                    threat_increase = 25
                
                if actor in self.threat_levels[enemy]:
                    self.threat_levels[enemy][actor] += threat_increase
            
            # Si l'ennemi observe une action de soin
            elif action_type == "HEAL" and actor in targets:
                # Les soigneurs deviennent des cibles prioritaires
                if actor in self.threat_levels[enemy]:
                    self.threat_levels[enemy][actor] += 10
        
        # Limiter les niveaux de menace
        for target, level in self.threat_levels[enemy].items():
            self.threat_levels[enemy][target] = max(10, min(100, level))
            
        logger.debug(f"Niveaux de menace mis à jour pour {getattr(enemy, 'name', str(enemy))}")
    
    def select_target(self, enemy: Any, potential_targets: List[Any]) -> Any:
        """
        Sélectionne une cible pour l'ennemi
        
        Args:
            enemy: L'ennemi qui sélectionne une cible
            potential_targets: Liste des cibles potentielles
            
        Returns:
            La cible sélectionnée
        """
        if not potential_targets:
            return None
            
        if enemy not in self.enemy_tactics:
            self.register_enemy(enemy)
            
        tactic = self.enemy_tactics[enemy]
        
        # Calculer les scores de cible pour chaque cible potentielle
        target_scores = {}
        
        for target in potential_targets:
            score = 0
            
            # Le niveau de menace est le facteur principal
            threat_level = self.threat_levels.get(enemy, {}).get(target, 50)
            score += threat_level
            
            # Ajuster en fonction de la tactique
            if tactic == TacticType.AGGRESSIVE:
                # Préférer les cibles avec peu de PV
                health_ratio = getattr(target, "health", 100) / getattr(target, "max_health", 100)
                score += (1 - health_ratio) * 30
            elif tactic == TacticType.DEFENSIVE:
                # Préférer les cibles proches
                if hasattr(enemy, "position") and hasattr(target, "position"):
                    distance = self._calculate_distance(enemy.position, target.position)
                    score += (1 - min(1, distance / 10)) * 20
            elif tactic == TacticType.SUPPORT:
                # Préférer les cibles qui menacent les alliés
                for ally in self._get_allies(enemy):
                    ally_threat = self.threat_levels.get(ally, {}).get(target, 0)
                    score += ally_threat * 0.5
            elif tactic == TacticType.FLANKING:
                # Préférer les cibles qui ne sont pas en garde
                if hasattr(target, "is_guarding") and not target.is_guarding:
                    score += 30
            elif tactic == TacticType.RANGED:
                # Préférer les cibles à distance
                if hasattr(enemy, "position") and hasattr(target, "position"):
                    distance = self._calculate_distance(enemy.position, target.position)
                    score += min(30, distance * 3)
            
            # Les soigneurs sont généralement des cibles prioritaires
            if self._is_healer(target):
                score += 20
                
            # Les cibles avec peu de PV sont plus faciles à éliminer
            health_ratio = getattr(target, "health", 100) / getattr(target, "max_health", 100)
            score += (1 - health_ratio) * 15
            
            target_scores[target] = score
        
        # Sélectionner la cible avec le score le plus élevé
        if target_scores:
            return max(target_scores.items(), key=lambda x: x[1])[0]
        else:
            return random.choice(potential_targets)
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calcule la distance entre deux positions"""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def _get_allies(self, enemy: Any) -> List[Any]:
        """Récupère les alliés d'un ennemi"""
        allies = []
        
        # Chercher dans les groupes
        for group_data in self.group_tactics.values():
            if enemy in group_data["enemies"]:
                allies.extend([e for e in group_data["enemies"] if e != enemy])
                break
                
        return allies
    
    def _is_healer(self, target: Any) -> bool:
        """Vérifie si une cible est un soigneur"""
        # Vérifier les actions récentes
        for action in self.action_history.get(target, []):
            if action.get("type") == "HEAL":
                return True
                
        # Vérifier les capacités
        if hasattr(target, "abilities"):
            for ability in target.abilities:
                if "heal" in ability.lower() or "soin" in ability.lower():
                    return True
                    
        return False
    
    def select_action(self, enemy: Any, target: Any, available_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sélectionne une action pour l'ennemi
        
        Args:
            enemy: L'ennemi qui agit
            target: La cible de l'action
            available_actions: Liste des actions disponibles
            
        Returns:
            L'action sélectionnée
        """
        if not available_actions:
            return None
            
        if enemy not in self.enemy_tactics:
            self.register_enemy(enemy)
            
        tactic = self.enemy_tactics[enemy]
        
        # Calculer les scores d'action pour chaque action disponible
        action_scores = {}
        
        for action in available_actions:
            # Ignorer les actions non disponibles
            if not action.get("is_available", True):
                continue
                
            score = 50  # Score de base
            action_id = action.get("id", "")
            action_category = action.get("category", None)
            
            # Ajuster en fonction de la tactique
            if tactic == TacticType.AGGRESSIVE:
                if action_category and "ATTACK" in str(action_category):
                    score += 30
            elif tactic == TacticType.DEFENSIVE:
                if action_category and "DEFENSE" in str(action_category):
                    score += 30
            elif tactic == TacticType.BALANCED:
                # Pas d'ajustement spécifique
                pass
            elif tactic == TacticType.SUPPORT:
                if action_category and "SUPPORT" in str(action_category):
                    score += 30
            elif tactic == TacticType.FLANKING:
                if action_category and "MOVEMENT" in str(action_category):
                    score += 20
                if "flanking" in action_id.lower() or "backstab" in action_id.lower():
                    score += 30
            elif tactic == TacticType.RANGED:
                if "ranged" in action_id.lower() or "shot" in action_id.lower():
                    score += 30
            elif tactic == TacticType.BERSERKER:
                if "power" in action_id.lower() or "rage" in action_id.lower():
                    score += 30
                # Les berserkers se soucient peu de la défense
                if action_category and "DEFENSE" in str(action_category):
                    score -= 20
            elif tactic == TacticType.TACTICAL:
                # Préférer les actions qui exploitent l'environnement
                if "environment" in action_id.lower() or "tactical" in action_id.lower():
                    score += 30
            
            # Ajuster en fonction de la situation de combat
            health_ratio = getattr(enemy, "health", 100) / getattr(enemy, "max_health", 100)
            
            # À faible santé, préférer les actions défensives ou de fuite
            if health_ratio < 0.3:
                if action_category and "DEFENSE" in str(action_category):
                    score += 40
                if "heal" in action_id.lower() or "retreat" in action_id.lower():
                    score += 50
            
            # Préférer les capacités ultimes contre les cibles importantes
            if action_category and "ULTIMATE" in str(action_category):
                if self._is_high_value_target(target):
                    score += 40
                elif health_ratio < 0.4:  # Ou en dernier recours
                    score += 30
                else:
                    score -= 20  # Économiser pour plus tard
            
            # Ajouter une part d'aléatoire pour éviter la prévisibilité
            score += random.randint(-10, 10)
            
            action_scores[action_id] = (score, action)
        
        # Sélectionner l'action avec le score le plus élevé
        if action_scores:
            return max(action_scores.items(), key=lambda x: x[1][0])[1][1]
        else:
            return random.choice(available_actions)
    
    def _is_high_value_target(self, target: Any) -> bool:
        """Vérifie si une cible est de haute valeur"""
        # Les joueurs sont toujours des cibles de haute valeur
        if hasattr(target, "is_player") and target.is_player:
            return True
            
        # Les soigneurs sont des cibles de haute valeur
        if self._is_healer(target):
            return True
            
        # Les cibles avec beaucoup de PV sont des cibles de haute valeur
        if getattr(target, "max_health", 100) > 150:
            return True
            
        # Les cibles de haut niveau sont des cibles de haute valeur
        if getattr(target, "level", 1) > 5:
            return True
            
        return False
    
    def coordinate_group_actions(self, group_id: str, potential_targets: List[Any]) -> Dict[Any, Dict[str, Any]]:
        """
        Coordonne les actions d'un groupe d'ennemis
        
        Args:
            group_id: Identifiant du groupe
            potential_targets: Liste des cibles potentielles
            
        Returns:
            Dictionnaire des actions coordonnées (ennemi -> action)
        """
        if group_id not in self.group_tactics:
            return {}
            
        group_data = self.group_tactics[group_id]
        enemies = group_data["enemies"]
        tactic = group_data["tactic"]
        leader = group_data["leader"]
        
        # Initialiser les actions coordonnées
        coordinated_actions = {}
        
        # Sélectionner les cibles en fonction de la tactique de groupe
        if tactic == TacticType.AGGRESSIVE:
            # Concentrer les attaques sur une seule cible
            main_target = self.select_target(leader or enemies[0], potential_targets)
            
            for enemy in enemies:
                # 80% de chance de cibler la cible principale
                if random.random() < 0.8:
                    coordinated_actions[enemy] = {"target": main_target, "focus": True}
                else:
                    # 20% de chance de choisir une cible différente
                    other_targets = [t for t in potential_targets if t != main_target]
                    if other_targets:
                        coordinated_actions[enemy] = {"target": random.choice(other_targets), "focus": False}
                    else:
                        coordinated_actions[enemy] = {"target": main_target, "focus": True}
                        
        elif tactic == TacticType.DEFENSIVE:
            # Former un périmètre défensif
            for i, enemy in enumerate(enemies):
                # Répartir les cibles équitablement
                target_index = i % len(potential_targets)
                coordinated_actions[enemy] = {"target": potential_targets[target_index], "defensive": True}
                
        elif tactic == TacticType.FLANKING:
            # Diviser le groupe pour attaquer de plusieurs côtés
            main_target = self.select_target(leader or enemies[0], potential_targets)
            
            # Diviser les ennemis en deux groupes
            group1 = enemies[:len(enemies)//2]
            group2 = enemies[len(enemies)//2:]
            
            for enemy in group1:
                coordinated_actions[enemy] = {"target": main_target, "flank_left": True}
                
            for enemy in group2:
                coordinated_actions[enemy] = {"target": main_target, "flank_right": True}
                
        elif tactic == TacticType.TACTICAL:
            # Utiliser l'environnement et les positions tactiques
            high_value_targets = [t for t in potential_targets if self._is_high_value_target(t)]
            normal_targets = [t for t in potential_targets if t not in high_value_targets]
            
            # Assigner des rôles tactiques
            for i, enemy in enumerate(enemies):
                if i < len(high_value_targets):
                    # Cibler les cibles de haute valeur en priorité
                    coordinated_actions[enemy] = {"target": high_value_targets[i], "priority": True}
                else:
                    # Répartir sur les cibles normales
                    target_index = i % max(1, len(normal_targets))
                    target = normal_targets[target_index] if normal_targets else random.choice(potential_targets)
                    coordinated_actions[enemy] = {"target": target, "support": True}
        
        else:  # Tactiques par défaut ou non coordonnées
            for enemy in enemies:
                target = self.select_target(enemy, potential_targets)
                coordinated_actions[enemy] = {"target": target}
        
        logger.debug(f"Actions coordonnées générées pour le groupe {group_id}")
        
        return coordinated_actions
    
    def record_action(self, actor: Any, action_data: Dict[str, Any]) -> None:
        """
        Enregistre une action dans l'historique
        
        Args:
            actor: L'acteur qui a effectué l'action
            action_data: Données de l'action
        """
        if actor not in self.action_history:
            self.action_history[actor] = []
            
        self.action_history[actor].append(action_data)
        
        # Limiter la taille de l'historique
        if len(self.action_history[actor]) > 10:
            self.action_history[actor].pop(0)
    
    def adapt_tactics(self, enemy: Any, combat_data: Dict[str, Any]) -> None:
        """
        Adapte les tactiques d'un ennemi en fonction de la situation
        
        Args:
            enemy: L'ennemi concerné
            combat_data: Données du combat
        """
        if enemy not in self.enemy_tactics:
            self.register_enemy(enemy)
            return
            
        current_tactic = self.enemy_tactics[enemy]
        health_ratio = getattr(enemy, "health", 100) / getattr(enemy, "max_health", 100)
        
        # Adapter la tactique en fonction de la santé
        if health_ratio < 0.3:
            # À faible santé, devenir plus défensif ou agressif selon le type
            enemy_type = getattr(enemy, "enemy_type", "STANDARD")
            
            if enemy_type in ["HUMAN", "SECURITY", "ROBOT"]:
                # Types plus rationnels deviennent défensifs
                new_tactic = TacticType.DEFENSIVE
            else:
                # Types plus instinctifs deviennent berserkers
                new_tactic = TacticType.BERSERKER
                
            if current_tactic != new_tactic:
                self.enemy_tactics[enemy] = new_tactic
                logger.debug(f"{getattr(enemy, 'name', str(enemy))} adapte sa tactique: {current_tactic.name} -> {new_tactic.name}")
        
        # Adapter en fonction des actions des alliés
        allies = self._get_allies(enemy)
        if allies:
            ally_tactics = [self.enemy_tactics.get(ally, TacticType.BALANCED) for ally in allies]
            
            # Si tous les alliés utilisent la même tactique, envisager de la compléter
            if len(set(ally_tactics)) == 1 and ally_tactics[0] != current_tactic:
                if ally_tactics[0] == TacticType.AGGRESSIVE:
                    # Compléter avec du soutien
                    new_tactic = TacticType.SUPPORT
                elif ally_tactics[0] == TacticType.DEFENSIVE:
                    # Compléter avec des attaques à distance
                    new_tactic = TacticType.RANGED
                else:
                    # Par défaut, rester sur la tactique actuelle
                    new_tactic = current_tactic
                    
                # 30% de chance d'adapter la tactique
                if random.random() < 0.3 and current_tactic != new_tactic:
                    self.enemy_tactics[enemy] = new_tactic
                    logger.debug(f"{getattr(enemy, 'name', str(enemy))} adapte sa tactique pour compléter les alliés: {current_tactic.name} -> {new_tactic.name}")
    
    def reset_combat_ai(self) -> None:
        """Réinitialise les données d'IA de combat"""
        self.threat_levels = {}
        self.action_history = {}
