"""
Module pour la gestion des missions dans YakTaa
Ce module contient la classe MissionManager qui gère toutes les missions du jeu.
"""

import logging
import json
import os
import random
from typing import Dict, List, Optional, Any, Set, Tuple, TYPE_CHECKING
from datetime import datetime

from yaktaa.missions.mission import Mission, Objective, MissionStatus, MissionType, MissionDifficulty, ObjectiveType
from yaktaa.missions.hacking_missions import HackingMission, HackingObjective, HackingMissionGenerator
from yaktaa.characters.player import Player
from yaktaa.terminal.hacking_system import SecurityLevel, HackingPuzzleType

# Import conditionnel pour éviter les imports circulaires
if TYPE_CHECKING:
    from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.Missions.Manager")

class MissionManager:
    """
    Classe pour gérer les missions du jeu
    Gère la création, le suivi et la complétion des missions
    """
    
    def __init__(self, game=None):
        """Initialise le gestionnaire de missions"""
        from yaktaa.core.game import Game  # Import local pour éviter les imports circulaires
        
        self.game = game
        self.available_missions: Dict[str, Mission] = {}
        self.active_missions: Dict[str, Mission] = {}
        self.completed_missions: Dict[str, Mission] = {}
        self.failed_missions: Dict[str, Mission] = {}
        
        # Charger les missions de test pour le développement
        self._load_test_missions()
        
        logger.info("Gestionnaire de missions initialisé")
    
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
        
        # Ajouter une mission de hacking avancée
        self._load_hacking_missions()
        
        # Ajouter les missions au gestionnaire
        self.available_missions[main_mission.id] = main_mission
        self.available_missions[side_mission.id] = side_mission
        self.available_missions[tutorial_mission.id] = tutorial_mission
        
        logger.info(f"Missions de test chargées : {len(self.available_missions)}")
    
    def _load_hacking_missions(self):
        """Charge des missions de hacking avancées pour le développement"""
        # Créer le générateur de missions de hacking
        self.hacking_mission_generator = HackingMissionGenerator(self.game)
        
        # Générer quelques missions de hacking avec différentes difficultés
        for difficulty in range(1, 8, 2):  # Difficultés 1, 3, 5, 7
            corporation = random.choice(list(self.hacking_mission_generator.CORPORATIONS.keys()))
            mission = self.hacking_mission_generator.generate_mission(difficulty, corporation)
            self.available_missions[mission.id] = mission
            logger.info(f"Mission de hacking générée: {mission.title} (difficulté: {difficulty})")
    
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
    
    def save_missions(self, save_path: str) -> bool:
        """Sauvegarde toutes les missions dans un fichier JSON"""
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Préparer les données
            data = {
                "available": {mission_id: mission.to_dict() for mission_id, mission in self.available_missions.items()},
                "active": {mission_id: mission.to_dict() for mission_id, mission in self.active_missions.items()},
                "completed": {mission_id: mission.to_dict() for mission_id, mission in self.completed_missions.items()},
                "failed": {mission_id: mission.to_dict() for mission_id, mission in self.failed_missions.items()}
            }
            
            # Sauvegarder dans un fichier JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Missions sauvegardées dans {save_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des missions : {e}")
            return False
    
    def load_missions(self, save_path: str) -> bool:
        """Charge les missions depuis un fichier JSON"""
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(save_path):
                logger.warning(f"Fichier de sauvegarde des missions non trouvé : {save_path}")
                return False
            
            # Charger depuis le fichier JSON
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Réinitialiser les missions actuelles
            self.available_missions.clear()
            self.active_missions.clear()
            self.completed_missions.clear()
            self.failed_missions.clear()
            
            # Charger les missions disponibles
            for mission_id, mission_data in data.get("available", {}).items():
                self.available_missions[mission_id] = Mission.from_dict(mission_data)
            
            # Charger les missions actives
            for mission_id, mission_data in data.get("active", {}).items():
                self.active_missions[mission_id] = Mission.from_dict(mission_data)
            
            # Charger les missions terminées
            for mission_id, mission_data in data.get("completed", {}).items():
                self.completed_missions[mission_id] = Mission.from_dict(mission_data)
            
            # Charger les missions échouées
            for mission_id, mission_data in data.get("failed", {}).items():
                self.failed_missions[mission_id] = Mission.from_dict(mission_data)
            
            logger.info(f"Missions chargées depuis {save_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des missions : {e}")
            return False
    
    def create_custom_mission(self, title: str, description: str, mission_type: MissionType, 
                            difficulty: MissionDifficulty, location_id: Optional[str] = None,
                            faction: Optional[str] = None) -> Mission:
        """Crée une mission personnalisée"""
        mission = Mission(
            title=title,
            description=description,
            mission_type=mission_type,
            difficulty=difficulty,
            location_id=location_id,
            faction=faction
        )
        
        self.add_mission(mission)
        logger.info(f"Mission personnalisée créée : {title}")
        return mission
    
    def get_missions_by_location(self, location_id: str) -> List[Mission]:
        """Récupère toutes les missions disponibles à un emplacement spécifique"""
        missions = []
        
        for mission in self.available_missions.values():
            if mission.location_id == location_id:
                missions.append(mission)
        
        return missions
    
    def get_missions_by_faction(self, faction: str) -> List[Mission]:
        """Récupère toutes les missions disponibles pour une faction spécifique"""
        missions = []
        
        for mission in self.available_missions.values():
            if mission.faction == faction:
                missions.append(mission)
        
        return missions
    
    def get_missions_by_type(self, mission_type: MissionType) -> List[Mission]:
        """Récupère toutes les missions disponibles d'un type spécifique"""
        missions = []
        
        for mission in self.available_missions.values():
            if mission.mission_type == mission_type:
                missions.append(mission)
        
        return missions
    
    def get_missions_by_difficulty(self, difficulty: MissionDifficulty) -> List[Mission]:
        """Récupère toutes les missions disponibles d'une difficulté spécifique"""
        missions = []
        
        for mission in self.available_missions.values():
            if mission.difficulty == difficulty:
                missions.append(mission)
        
        return missions
    
    def update_hacking_objectives(self, target: str, success: bool) -> bool:
        """
        Met à jour les objectifs de hacking liés à une cible spécifique
        
        Args:
            target: Identifiant de la cible du hack
            success: True si le hack a réussi, False sinon
            
        Returns:
            bool: True si au moins un objectif a été mis à jour
        """
        updated = False
        missions_to_update = []
        
        # Parcourir toutes les missions actives
        for mission_id, mission in self.active_missions.items():
            mission_updated = False
            
            # Vérifier s'il s'agit d'une mission de hacking spécialisée
            if isinstance(mission, HackingMission):
                for objective in mission.objectives:
                    if isinstance(objective, HackingObjective) and not objective.completed:
                        # Vérifier si l'objectif correspond à la cible
                        if objective.target_system.lower() in target.lower() or target.lower() in objective.target_system.lower():
                            if success:
                                objective.completed = True
                                objective.metadata["successful"] = True
                                logger.info(f"Objectif de hacking complété: {objective.description}")
                                mission_updated = True
                                updated = True
                            else:
                                objective.metadata["attempts"] = objective.metadata.get("attempts", 0) + 1
                                logger.info(f"Tentative de hack échouée pour l'objectif: {objective.description}")
            
            # Pour les missions standard, vérifier les objectifs de type HACK
            else:
                for objective in mission.objectives:
                    if objective.objective_type == ObjectiveType.HACK and not objective.completed:
                        # Vérifier si la cible correspond
                        if objective.target_id and (objective.target_id.lower() in target.lower() or target.lower() in objective.target_id.lower()):
                            if success:
                                objective.completed = True
                                logger.info(f"Objectif de hacking complété: {objective.description}")
                                mission_updated = True
                                updated = True
            
            # Si la mission a été mise à jour, vérifier si elle est complétée
            if mission_updated:
                missions_to_update.append(mission_id)
        
        # Vérifier si les missions mises à jour sont complétées
        for mission_id in missions_to_update:
            self.check_mission_completion(mission_id)
        
        return updated
    
    def generate_hacking_mission(self, difficulty: int = None, corporation: str = None, location_id: str = None) -> HackingMission:
        """
        Génère une nouvelle mission de hacking
        
        Args:
            difficulty: Niveau de difficulté (1-10)
            corporation: Corporation ciblée spécifique
            location_id: Emplacement de la mission
            
        Returns:
            HackingMission: La mission générée
        """
        if not hasattr(self, 'hacking_mission_generator'):
            self.hacking_mission_generator = HackingMissionGenerator(self.game)
        
        # Récupérer l'emplacement si possible
        location = None
        if self.game and hasattr(self.game, 'city_manager') and location_id:
            location = self.game.city_manager.get_location(location_id)
        
        # Générer la mission
        mission = self.hacking_mission_generator.generate_mission(difficulty, corporation, location)
        
        # Ajouter la mission aux missions disponibles
        self.available_missions[mission.id] = mission
        
        logger.info(f"Nouvelle mission de hacking générée: {mission.title}")
        return mission
    
    def process_hacking_events(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Traite les événements liés au hacking
        
        Args:
            event_type: Type d'événement
            data: Données de l'événement
        """
        if event_type == "network_scan":
            # Possibilité de générer des missions basées sur les réseaux découverts
            if random.random() < 0.2:  # 20% de chance
                network = data.get("network")
                if network and "owner" in network:
                    # Générer une mission liée à ce réseau
                    corporation = network["owner"]
                    security_level = network.get("security_level", SecurityLevel.MEDIUM)
                    difficulty = min(8, security_level.value + 3)
                    
                    mission = self.generate_hacking_mission(difficulty, corporation)
                    logger.info(f"Mission de hacking générée suite à un scan de réseau: {mission.title}")
                    
                    # Notifier le joueur
                    if self.game and hasattr(self.game, 'ui_manager'):
                        self.game.ui_manager.show_message(
                            "Nouvelle mission disponible",
                            f"Vous avez découvert une opportunité de hacking: {mission.title}"
                        )
        
        elif event_type == "hack_success":
            # Mettre à jour les objectifs des missions
            target = data.get("target")
            if target:
                self.update_hacking_objectives(target, True)
                
                # Possibilité de générer des missions suite à un hack réussi
                if random.random() < 0.3:  # 30% de chance
                    self.generate_follow_up_mission(target, data)
        
        elif event_type == "hack_failed":
            # Mettre à jour les objectifs des missions
            target = data.get("target")
            if target:
                self.update_hacking_objectives(target, False)
    
    def generate_follow_up_mission(self, target: str, data: Dict[str, Any]) -> Optional[Mission]:
        """
        Génère une mission de suivi après un hack réussi
        
        Args:
            target: Cible du hack
            data: Données du hack
            
        Returns:
            Mission: La mission générée, ou None
        """
        # Déterminer le type de mission de suivi
        follow_up_types = ["data_extraction", "system_breach", "sabotage", "surveillance"]
        mission_type = random.choice(follow_up_types)
        
        # Extraire la corporation à partir de la cible
        corporation = None
        if "." in target:
            corporation_part = target.split(".")[0]
            for corp in self.hacking_mission_generator.CORPORATIONS:
                if corporation_part.lower() in corp.lower():
                    corporation = corp
                    break
        
        if not corporation:
            # Choisir une corporation aléatoire
            corporation = random.choice(list(self.hacking_mission_generator.CORPORATIONS.keys()))
        
        # Déterminer la difficulté
        base_difficulty = data.get("security_level", 3)
        difficulty = min(10, base_difficulty + random.randint(1, 3))
        
        # Générer la mission
        mission = self.hacking_mission_generator.generate_mission(difficulty, corporation)
        
        # Ajouter une référence à la cible précédente
        mission.description += f"\n\nCette mission est liée à votre hack précédent sur {target}."
        
        # Ajouter la mission aux missions disponibles
        self.available_missions[mission.id] = mission
        
        logger.info(f"Mission de suivi générée après hack sur {target}: {mission.title}")
        
        # Notifier le joueur
        if self.game and hasattr(self.game, 'ui_manager'):
            self.game.ui_manager.show_message(
                "Nouvelle mission disponible",
                f"Suite à votre hack sur {target}, une nouvelle opportunité s'est présentée: {mission.title}"
            )
        
        return mission
