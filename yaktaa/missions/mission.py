"""
Module pour la gestion des missions dans YakTaa
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum, auto

from yaktaa.world.locations import Location
from yaktaa.characters.player import Player

logger = logging.getLogger("YakTaa.Missions.Mission")

class MissionStatus(Enum):
    """Statut d'une mission"""
    AVAILABLE = auto()    # Mission disponible mais non acceptée
    ACTIVE = auto()       # Mission acceptée et en cours
    COMPLETED = auto()    # Mission terminée avec succès
    FAILED = auto()       # Mission échouée
    EXPIRED = auto()      # Mission expirée (délai dépassé)
    HIDDEN = auto()       # Mission cachée (conditions non remplies)


class MissionDifficulty(Enum):
    """Difficulté d'une mission"""
    TRIVIAL = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    MASTER = 6


class MissionType(Enum):
    """Type de mission"""
    MAIN = auto()         # Mission principale (histoire)
    SIDE = auto()         # Mission secondaire
    CONTRACT = auto()     # Contrat (mission rémunérée)
    FACTION = auto()      # Mission de faction
    TUTORIAL = auto()     # Tutoriel
    CHALLENGE = auto()    # Défi spécial


class Mission:
    """
    Classe représentant une mission dans le jeu
    Une mission est composée d'objectifs à accomplir
    """
    
    def __init__(self, 
                 title: str, 
                 description: str, 
                 mission_type: MissionType = MissionType.SIDE,
                 difficulty: MissionDifficulty = MissionDifficulty.MEDIUM,
                 location_id: Optional[str] = None,
                 giver_id: Optional[str] = None,
                 faction: Optional[str] = None,
                 time_limit: Optional[int] = None,  # en minutes
                 prerequisites: Optional[List[str]] = None,
                 mission_id: Optional[str] = None,
                 progress: int = 0, 
                 metadata: Optional[Dict[str, Any]] = None):  
        """Initialise une mission"""
        self.id = mission_id or f"mission_{uuid.uuid4().hex[:8]}"
        self.title = title
        self.description = description
        self.mission_type = mission_type
        self.difficulty = difficulty
        self.location_id = location_id
        self.giver_id = giver_id
        self.faction = faction
        
        self.status = MissionStatus.AVAILABLE
        self.objectives: List[Objective] = []
        self.rewards: Dict[str, Any] = {
            "credits": 0,
            "xp": 0,
            "items": [],
            "reputation": {}
        }
        
        # Métadonnées additionnelles pour les missions spécialistes
        self.metadata: Dict[str, Any] = metadata or {}
        
        self.prerequisites = prerequisites or []
        self.time_limit = time_limit
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        self.tags: Set[str] = set()
        
        # Progression de la mission (0-100%)
        self.progress = progress
        
        # Calcul automatique des récompenses en fonction de la difficulté
        self._calculate_default_rewards()
        
        logger.info(f"Nouvelle mission créée : {self.title} (ID: {self.id})")
    
    def _calculate_default_rewards(self):
        """Calcule les récompenses par défaut en fonction de la difficulté"""
        # Gère le cas où difficulty est un entier ou une énumération
        if isinstance(self.difficulty, int):
            difficulty_multiplier = self.difficulty
        else:
            difficulty_multiplier = self.difficulty.value
            
        base_credits = 100 * difficulty_multiplier
        base_xp = 50 * difficulty_multiplier
        
        # Ajustement en fonction du type de mission
        if self.mission_type == MissionType.MAIN:
            base_credits *= 1.5
            base_xp *= 2.0
        elif self.mission_type == MissionType.CONTRACT:
            base_credits *= 2.0
            base_xp *= 1.2
            
        self.rewards["credits"] = int(base_credits)
        self.rewards["xp"] = int(base_xp)
        
        # Réputation de faction si applicable
        if self.faction:
            self.rewards["reputation"][self.faction] = difficulty_multiplier * 5
    
    def add_objective(self, objective: 'Objective') -> None:
        """Ajoute un objectif à la mission"""
        self.objectives.append(objective)
        logger.info(f"Objectif ajouté à la mission {self.title} : {objective.description}")
    
    def set_reward(self, reward_type: str, value: Any) -> None:
        """Définit une récompense pour la mission"""
        if reward_type == "reputation" and isinstance(value, tuple) and len(value) == 2:
            faction, amount = value
            self.rewards["reputation"][faction] = amount
        else:
            self.rewards[reward_type] = value
    
    def start(self) -> bool:
        """Démarre la mission"""
        if self.status != MissionStatus.AVAILABLE:
            logger.warning(f"Tentative de démarrer une mission non disponible : {self.title}")
            return False
        
        self.status = MissionStatus.ACTIVE
        self.start_time = datetime.now()
        
        # Définir la date d'expiration si un délai est spécifié
        if self.time_limit:
            self.end_time = self.start_time + timedelta(minutes=self.time_limit)
        
        logger.info(f"Mission démarrée : {self.title}")
        return True
    
    def complete(self) -> bool:
        """Marque la mission comme terminée"""
        if self.status != MissionStatus.ACTIVE:
            logger.warning(f"Tentative de terminer une mission non active : {self.title}")
            return False
        
        # Vérifier que tous les objectifs sont terminés
        if not all(obj.is_completed() for obj in self.objectives):
            logger.warning(f"Tentative de terminer une mission avec des objectifs non terminés : {self.title}")
            return False
        
        self.status = MissionStatus.COMPLETED
        logger.info(f"Mission terminée : {self.title}")
        return True
    
    def fail(self) -> bool:
        """Marque la mission comme échouée"""
        if self.status != MissionStatus.ACTIVE:
            logger.warning(f"Tentative d'échouer une mission non active : {self.title}")
            return False
        
        self.status = MissionStatus.FAILED
        logger.info(f"Mission échouée : {self.title}")
        return True
    
    def check_expiration(self) -> bool:
        """Vérifie si la mission a expiré"""
        if self.status != MissionStatus.ACTIVE or not self.end_time:
            return False
        
        if datetime.now() > self.end_time:
            self.status = MissionStatus.EXPIRED
            logger.info(f"Mission expirée : {self.title}")
            return True
        
        return False
    
    def is_available_for_player(self, player: Player) -> bool:
        """Vérifie si la mission est disponible pour le joueur"""
        # Vérifier les prérequis (missions terminées)
        for prereq_id in self.prerequisites:
            mission_completed = False
            for mission in player.mission_history:
                if mission["mission_id"] == prereq_id and mission["status"] == "completed":
                    mission_completed = True
                    break
            
            if not mission_completed:
                return False
        
        # Vérifier le niveau du joueur par rapport à la difficulté
        min_level = max(1, self.difficulty.value * 2)
        if player.level < min_level:
            return False
        
        return True
    
    def get_progress(self) -> float:
        """Calcule la progression globale de la mission"""
        if not self.objectives:
            return 0.0
        
        total_progress = sum(obj.progress for obj in self.objectives)
        return total_progress / len(self.objectives)
    
    def get_remaining_time(self) -> Optional[timedelta]:
        """Récupère le temps restant avant expiration"""
        if not self.end_time or self.status != MissionStatus.ACTIVE:
            return None
        
        remaining = self.end_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la mission en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "mission_type": self.mission_type.name,
            "difficulty": self.difficulty.name,
            "location_id": self.location_id,
            "giver_id": self.giver_id,
            "faction": self.faction,
            "status": self.status.name,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            "time_limit": self.time_limit,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "tags": list(self.tags),
            "progress": self.progress,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mission':
        """Crée une mission à partir d'un dictionnaire"""
        mission = cls(
            title=data["title"],
            description=data["description"],
            mission_type=MissionType[data["mission_type"]],
            difficulty=MissionDifficulty[data["difficulty"]],
            location_id=data["location_id"],
            giver_id=data["giver_id"],
            faction=data["faction"],
            time_limit=data["time_limit"],
            prerequisites=data["prerequisites"],
            mission_id=data["id"],
            progress=data.get("progress", 0),
            metadata=data.get("metadata", {})
        )
        
        mission.status = MissionStatus[data["status"]]
        mission.rewards = data["rewards"]
        mission.tags = set(data["tags"])
        
        if data["start_time"]:
            mission.start_time = datetime.fromisoformat(data["start_time"])
        
        if data["end_time"]:
            mission.end_time = datetime.fromisoformat(data["end_time"])
        
        # Charger les objectifs
        for obj_data in data["objectives"]:
            mission.objectives.append(Objective.from_dict(obj_data))
        
        return mission


class ObjectiveType(Enum):
    """Type d'objectif"""
    TRAVEL = auto()       # Se rendre à un lieu
    HACK = auto()         # Hacker un système
    COLLECT = auto()      # Collecter un objet
    TALK = auto()         # Parler à un personnage
    ELIMINATE = auto()    # Éliminer une cible
    PROTECT = auto()      # Protéger une cible
    ESCORT = auto()       # Escorter une cible
    INVESTIGATE = auto()  # Enquêter sur quelque chose
    CRAFT = auto()        # Fabriquer un objet
    INSTALL = auto()      # Installer un logiciel/matériel
    CUSTOM = auto()       # Objectif personnalisé


class Objective:
    """
    Classe représentant un objectif de mission
    Un objectif est une tâche spécifique à accomplir dans le cadre d'une mission
    """
    
    def __init__(self, 
                 description: str, 
                 objective_type: ObjectiveType = ObjectiveType.CUSTOM,
                 target_id: Optional[str] = None,
                 quantity: int = 1,
                 optional: bool = False,
                 objective_id: Optional[str] = None):
        """Initialise un objectif"""
        self.id = objective_id or f"obj_{uuid.uuid4().hex[:8]}"
        self.description = description
        self.objective_type = objective_type
        self.target_id = target_id
        self.quantity = quantity
        self.optional = optional
        
        self.progress = 0.0  # Progression de 0 à 100
        self.completed = False
        
        logger.info(f"Nouvel objectif créé : {self.description} (ID: {self.id})")
    
    def update_progress(self, value: float) -> None:
        """Met à jour la progression de l'objectif"""
        old_progress = self.progress
        self.progress = min(100.0, max(0.0, value))
        
        if self.progress >= 100.0 and not self.completed:
            self.completed = True
            logger.info(f"Objectif terminé : {self.description}")
        
        logger.info(f"Progression de l'objectif {self.description} mise à jour : {old_progress:.1f}% -> {self.progress:.1f}%")
    
    def increment_progress(self, increment: float = 10.0) -> None:
        """Incrémente la progression de l'objectif"""
        self.update_progress(self.progress + increment)
    
    def complete(self) -> None:
        """Marque l'objectif comme terminé"""
        self.update_progress(100.0)
    
    def reset(self) -> None:
        """Réinitialise l'objectif"""
        self.progress = 0.0
        self.completed = False
        logger.info(f"Objectif réinitialisé : {self.description}")
    
    def is_completed(self) -> bool:
        """Vérifie si l'objectif est terminé"""
        return self.completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objectif en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "description": self.description,
            "objective_type": self.objective_type.name,
            "target_id": self.target_id,
            "quantity": self.quantity,
            "optional": self.optional,
            "progress": self.progress,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Objective':
        """Crée un objectif à partir d'un dictionnaire"""
        objective = cls(
            description=data["description"],
            objective_type=ObjectiveType[data["objective_type"]],
            target_id=data["target_id"],
            quantity=data["quantity"],
            optional=data["optional"],
            objective_id=data["id"]
        )
        
        objective.progress = data["progress"]
        objective.completed = data["completed"]
        
        return objective


class MissionManager:
    """
    Classe pour gérer les missions du jeu
    Gère la création, le suivi et la complétion des missions
    """
    
    def __init__(self, game=None):
        """Initialise le gestionnaire de missions"""
        self.game = game
        self.available_missions: Dict[str, Mission] = {}
        self.active_missions: Dict[str, Mission] = {}
        self.completed_missions: Dict[str, Mission] = {}
        self.failed_missions: Dict[str, Mission] = {}
        
        # Charger les missions de test pour le développement
        self._load_test_missions()
    
    def _load_test_missions(self):
        """Charge des missions de test pour le développement"""
        # Mission principale
        main_mission = Mission(
            title="Trouver l'informateur",
            description="Un informateur prétend avoir des informations cruciales sur le projet secret d'Arasaka. Trouvez-le à Tokyo avant qu'il ne soit trop tard.",
            mission_type=MissionType.MAIN,
            difficulty=MissionDifficulty.MEDIUM,
            location_id="tokyo",
            faction="NetRunners"
        )
        
        main_mission.add_objective(Objective(
            description="Se rendre à Tokyo",
            objective_type=ObjectiveType.TRAVEL,
            target_id="tokyo"
        ))
        
        main_mission.add_objective(Objective(
            description="Localiser l'informateur dans le quartier de Shibuya",
            objective_type=ObjectiveType.INVESTIGATE,
            target_id="shibuya"
        ))
        
        main_mission.add_objective(Objective(
            description="Rencontrer l'informateur",
            objective_type=ObjectiveType.TALK,
            target_id="informer_npc"
        ))
        
        # Mission secondaire
        side_mission = Mission(
            title="Récupérer les données volées",
            description="Un client vous a engagé pour récupérer des données volées à Arasaka Corp. Infiltrez leur système et récupérez les fichiers.",
            mission_type=MissionType.CONTRACT,
            difficulty=MissionDifficulty.HARD,
            location_id="tokyo",
            faction="Fixers"
        )
        
        side_mission.add_objective(Objective(
            description="Infiltrer le réseau d'Arasaka",
            objective_type=ObjectiveType.HACK,
            target_id="arasaka_network"
        ))
        
        side_mission.add_objective(Objective(
            description="Localiser les fichiers volés",
            objective_type=ObjectiveType.INVESTIGATE,
            target_id="stolen_files"
        ))
        
        side_mission.add_objective(Objective(
            description="Télécharger les fichiers",
            objective_type=ObjectiveType.COLLECT,
            target_id="stolen_files"
        ))
        
        side_mission.add_objective(Objective(
            description="Effacer vos traces",
            objective_type=ObjectiveType.HACK,
            target_id="arasaka_logs"
        ))
        
        # Mission tutoriel
        tutorial_mission = Mission(
            title="Premiers pas dans le réseau",
            description="Apprenez les bases du hacking et de la navigation dans le réseau.",
            mission_type=MissionType.TUTORIAL,
            difficulty=MissionDifficulty.TRIVIAL,
            location_id="tokyo"
        )
        
        tutorial_mission.add_objective(Objective(
            description="Connectez-vous à votre premier réseau",
            objective_type=ObjectiveType.HACK,
            target_id="tutorial_network"
        ))
        
        tutorial_mission.add_objective(Objective(
            description="Exécutez votre premier scan",
            objective_type=ObjectiveType.CUSTOM,
            target_id="scan_command"
        ))
        
        # Ajouter les missions au gestionnaire
        self.available_missions[main_mission.id] = main_mission
        self.available_missions[side_mission.id] = side_mission
        self.available_missions[tutorial_mission.id] = tutorial_mission
        
        logger.info(f"Missions de test chargées : {len(self.available_missions)}")
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Récupère une mission par son ID"""
        # Chercher dans toutes les listes de missions
        for mission_list in [self.available_missions, self.active_missions, 
                           self.completed_missions, self.failed_missions]:
            if mission_id in mission_list:
                return mission_list[mission_id]
        
        return None
    
    def get_available_missions(self, player: Optional[Player] = None) -> List[Mission]:
        """Récupère toutes les missions disponibles pour le joueur"""
        if not player:
            return list(self.available_missions.values())
        
        # Filtrer les missions disponibles pour le joueur
        return [mission for mission in self.available_missions.values() 
                if mission.is_available_for_player(player)]
    
    def get_active_missions(self) -> List[Mission]:
        """Récupère toutes les missions actives"""
        return list(self.active_missions.values())
    
    def get_completed_missions(self) -> List[Mission]:
        """Récupère toutes les missions terminées"""
        return list(self.completed_missions.values())
    
    def get_failed_missions(self) -> List[Mission]:
        """Récupère toutes les missions échouées"""
        return list(self.failed_missions.values())
    
    def start_mission(self, mission_id: str) -> bool:
        """Démarre une mission"""
        if mission_id not in self.available_missions:
            logger.warning(f"Tentative de démarrer une mission non disponible : {mission_id}")
            return False
        
        mission = self.available_missions.pop(mission_id)
        if mission.start():
            self.active_missions[mission_id] = mission
            logger.info(f"Mission démarrée : {mission.title}")
            return True
        
        # En cas d'échec, remettre la mission dans les disponibles
        self.available_missions[mission_id] = mission
        return False
    
    def complete_mission(self, mission_id: str, player: Optional[Player] = None) -> bool:
        """Termine une mission"""
        if mission_id not in self.active_missions:
            logger.warning(f"Tentative de terminer une mission non active : {mission_id}")
            return False
        
        mission = self.active_missions.pop(mission_id)
        if mission.complete():
            self.completed_missions[mission_id] = mission
            
            # Attribuer les récompenses au joueur si fourni
            if player:
                player.complete_mission(
                    mission_id=mission_id,
                    reward_xp=mission.rewards["xp"],
                    reward_credits=mission.rewards["credits"]
                )
                
                # Mettre à jour la réputation
                for faction, amount in mission.rewards["reputation"].items():
                    player.update_reputation(faction, amount)
            
            logger.info(f"Mission terminée : {mission.title}")
            return True
        
        # En cas d'échec, remettre la mission dans les actives
        self.active_missions[mission_id] = mission
        return False
    
    def fail_mission(self, mission_id: str, player: Optional[Player] = None) -> bool:
        """Échoue une mission"""
        if mission_id not in self.active_missions:
            logger.warning(f"Tentative d'échouer une mission non active : {mission_id}")
            return False
        
        mission = self.active_missions.pop(mission_id)
        if mission.fail():
            self.failed_missions[mission_id] = mission
            
            # Mettre à jour l'historique du joueur si fourni
            if player:
                player.fail_mission(mission_id)
            
            logger.info(f"Mission échouée : {mission.title}")
            return True
        
        # En cas d'échec, remettre la mission dans les actives
        self.active_missions[mission_id] = mission
        return False
    
    def update_mission_objective(self, mission_id: str, objective_id: str, progress: float) -> bool:
        """Met à jour la progression d'un objectif de mission"""
        mission = self.get_mission(mission_id)
        if not mission:
            logger.warning(f"Tentative de mettre à jour un objectif d'une mission inexistante : {mission_id}")
            return False
        
        # Trouver l'objectif
        for objective in mission.objectives:
            if objective.id == objective_id:
                objective.update_progress(progress)
                
                # Vérifier si tous les objectifs sont terminés
                if all(obj.is_completed() for obj in mission.objectives):
                    logger.info(f"Tous les objectifs de la mission {mission.title} sont terminés")
                
                return True
        
        logger.warning(f"Objectif non trouvé : {objective_id}")
        return False
    
    def check_mission_expirations(self) -> List[str]:
        """Vérifie les missions actives pour les expirations"""
        expired_missions = []
        
        for mission_id, mission in list(self.active_missions.items()):
            if mission.check_expiration():
                self.active_missions.pop(mission_id)
                self.failed_missions[mission_id] = mission
                expired_missions.append(mission_id)
        
        return expired_missions
    
    def add_mission(self, mission: Mission) -> None:
        """Ajoute une nouvelle mission au gestionnaire"""
        self.available_missions[mission.id] = mission
        logger.info(f"Nouvelle mission ajoutée : {mission.title}")
    
    def remove_mission(self, mission_id: str) -> bool:
        """Supprime une mission du gestionnaire"""
        # Chercher dans toutes les listes de missions
        for mission_list in [self.available_missions, self.active_missions, 
                           self.completed_missions, self.failed_missions]:
            if mission_id in mission_list:
                mission_list.pop(mission_id)
                logger.info(f"Mission supprimée : {mission_id}")
                return True
        
        logger.warning(f"Tentative de supprimer une mission inexistante : {mission_id}")
        return False
    
    def reset_mission(self, mission_id: str) -> bool:
        """Réinitialise une mission (la rend à nouveau disponible)"""
        mission = self.get_mission(mission_id)
        if not mission:
            logger.warning(f"Tentative de réinitialiser une mission inexistante : {mission_id}")
            return False
        
        # Supprimer la mission de sa liste actuelle
        self.remove_mission(mission_id)
        
        # Réinitialiser les objectifs
        for objective in mission.objectives:
            objective.reset()
        
        # Réinitialiser le statut
        mission.status = MissionStatus.AVAILABLE
        mission.start_time = None
        mission.end_time = None
        
        # Ajouter aux missions disponibles
        self.available_missions[mission_id] = mission
        
        logger.info(f"Mission réinitialisée : {mission.title}")
        return True
