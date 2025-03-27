"""
Module principal du jeu YakTaa qui gère l'état global et la logique du jeu
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from yaktaa.core.config import Config
from yaktaa.core.save_manager import SaveManager
from yaktaa.world.world_manager import WorldManager
from yaktaa.world.city_manager import CityManager
from yaktaa.characters.player import Player
from yaktaa.missions.mission_manager import MissionManager
from yaktaa.ui.ui_manager import UIManager
from yaktaa.items.shop_manager import ShopManager
from yaktaa.world.world_loader import WorldLoader

logger = logging.getLogger("YakTaa.Game")

class Game:
    """Classe principale qui gère l'état global du jeu et coordonne les différents systèmes"""
    
    def __init__(self):
        """Initialise une nouvelle instance du jeu"""
        self.config = Config()
        self.save_manager = SaveManager()
        self.player = Player(name="Joueur")  # Créer un joueur par défaut
        self.mission_manager = MissionManager(self)
        self.world_manager = WorldManager(self)  # Initialiser le gestionnaire de monde
        self.city_manager = CityManager(self)  # Initialiser le gestionnaire de ville
        
        # Créer le chargeur de monde
        world_loader = WorldLoader()
        self.shop_manager = ShopManager(world_loader)  # Initialiser le gestionnaire de boutiques
        
        # Charger les boutiques pour le monde disponible dans la base de données
        world_id = self.shop_manager.get_first_world_id()
        self.shop_manager.load_shops_for_world(world_id)
        
        self.ui_manager = None  # Sera initialisé plus tard car il a besoin d'une référence au MainWindow
        self.running = False
        self.start_time = 0
        self.game_time = 0
        self.paused = False
        
        # Référence à l'interface de combat active (le cas échéant)
        self.active_combat_ui = None
        
        logger.info("Instance de jeu initialisée avec un monde par défaut")
    
    def new_game(self, player_name: str) -> bool:
        """Démarre une nouvelle partie avec un nouveau joueur"""
        try:
            logger.info(f"Création d'une nouvelle partie pour le joueur: {player_name}")
            
            # Création du joueur
            self.player = Player(name=player_name)
            
            # Initialisation du gestionnaire de missions (avant le monde pour que les missions puissent être chargées)
            self.mission_manager = MissionManager(self)
            
            # Initialisation du monde
            self.world_manager = WorldManager(self)
            
            # Initialisation du gestionnaire de ville
            self.city_manager = CityManager(self)
            
            # Initialisation du gestionnaire de boutiques
            from yaktaa.world.world_loader import WorldLoader
            world_loader = WorldLoader()
            self.shop_manager = ShopManager(world_loader)
            
            # Charger les boutiques pour le monde disponible dans la base de données
            world_id = self.shop_manager.get_first_world_id()
            self.shop_manager.load_shops_for_world(world_id)
            
            # Chargement explicite des missions de test
            if hasattr(self.world_manager, 'load_test_missions'):
                self.world_manager.load_test_missions()
                logger.info("Missions de test chargées explicitement")
            
            # Démarrage du jeu
            self.running = True
            self.start_time = time.time()
            
            logger.info("Nouvelle partie créée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création d'une nouvelle partie: {str(e)}", exc_info=True)
            return False
    
    def load_game(self, save_id: str) -> bool:
        """Charge une partie sauvegardée"""
        try:
            logger.info(f"Chargement de la sauvegarde: {save_id}")
            
            # Chargement des données de sauvegarde
            save_data = self.save_manager.load_game(save_id)
            if not save_data:
                logger.error(f"Impossible de charger la sauvegarde: {save_id}")
                return False
            
            # Restauration de l'état du jeu
            self.player = Player.from_save_data(save_data.get("player", {}))
            self.world_manager = WorldManager.from_save_data(self, save_data.get("world", {}))
            self.mission_manager = MissionManager.from_save_data(self, save_data.get("missions", {}))
            self.city_manager = CityManager(self)  # Initialiser un nouveau gestionnaire de ville
            self.game_time = save_data.get("game_time", 0)
            
            # Démarrage du jeu
            self.running = True
            self.start_time = time.time() - self.game_time
            
            logger.info("Partie chargée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la partie: {str(e)}", exc_info=True)
            return False
    
    def save_game(self, save_id: Optional[str] = None) -> bool:
        """Sauvegarde l'état actuel du jeu"""
        try:
            if not self.running:
                logger.warning("Tentative de sauvegarde alors que le jeu n'est pas en cours")
                return False
            
            # Mise à jour du temps de jeu
            self.update_game_time()
            
            # Préparation des données de sauvegarde
            save_data = {
                "player": self.player.to_save_data(),
                "world": self.world_manager.to_save_data(),
                "missions": self.mission_manager.to_save_data(),
                "game_time": self.game_time,
                "timestamp": time.time()
            }
            
            # Sauvegarde des données
            save_id = self.save_manager.save_game(save_data, save_id)
            
            logger.info(f"Partie sauvegardée avec succès (ID: {save_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la partie: {str(e)}", exc_info=True)
            return False
    
    def update(self, delta_time: float) -> None:
        """Met à jour l'état du jeu"""
        if not self.running or self.paused:
            return
        
        # Mise à jour du temps de jeu
        self.update_game_time()
        
        # Mise à jour des systèmes du jeu
        if self.world_manager:
            self.world_manager.update(delta_time)
        
        if self.mission_manager:
            self.mission_manager.update(delta_time)
        
        if self.player:
            self.player.update(delta_time)
        
        if self.city_manager:
            self.city_manager.update(delta_time)
    
    def update_game_time(self) -> None:
        """Met à jour le compteur de temps de jeu"""
        if self.running and not self.paused:
            self.game_time = time.time() - self.start_time
    
    def pause(self) -> None:
        """Met le jeu en pause"""
        if self.running and not self.paused:
            self.paused = True
            self.update_game_time()
            logger.info("Jeu mis en pause")
    
    def resume(self) -> None:
        """Reprend le jeu après une pause"""
        if self.running and self.paused:
            self.paused = False
            self.start_time = time.time() - self.game_time
            logger.info("Jeu repris")
    
    def quit(self) -> None:
        """Quitte le jeu proprement"""
        logger.info("Arrêt du jeu")
        self.running = False
        self.update_game_time()
        
        # Sauvegarde automatique si configurée
        if self.config.get("auto_save_on_quit", True):
            self.save_game("auto_save")
        
        # Nettoyage des ressources
        if self.world_manager:
            self.world_manager.cleanup()
        
        logger.info(f"Jeu terminé. Temps de jeu total: {self.format_game_time()}")
    
    def format_game_time(self) -> str:
        """Formate le temps de jeu en une chaîne lisible"""
        hours = int(self.game_time // 3600)
        minutes = int((self.game_time % 3600) // 60)
        seconds = int(self.game_time % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def handle_hack_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Gère les événements liés au hacking
        
        Args:
            event_type: Type d'événement ("network_scan", "hack_success", "hack_failed", etc.)
            data: Données associées à l'événement
        """
        logger.info(f"Événement de hacking reçu: {event_type}")
        
        # Transmettre l'événement au gestionnaire de missions
        if self.mission_manager:
            self.mission_manager.process_hacking_events(event_type, data)
        
        # Autres traitements possibles (notifications, statistiques, etc.)
        if event_type == "hack_success":
            target = data.get("target", "système inconnu")
            logger.info(f"Hack réussi sur {target}")
            
            # Ajouter de l'expérience au joueur
            if self.player:
                skill_points = data.get("difficulty", 1) * 5
                self.player.add_experience(skill_points)
                
                # Notification
                if self.ui_manager:
                    self.ui_manager.show_message(
                        "Hack réussi!", 
                        f"Vous avez réussi à hacker {target} et gagné {skill_points} points d'expérience."
                    )
        
        elif event_type == "hack_failed":
            target = data.get("target", "système inconnu")
            logger.info(f"Échec du hack sur {target}")
            
            # Notification
            if self.ui_manager:
                self.ui_manager.show_message(
                    "Hack échoué", 
                    f"Votre tentative de hacking sur {target} a échoué."
                )
    
    def set_ui_manager(self, ui_manager: UIManager) -> None:
        """
        Définit le gestionnaire d'interface utilisateur
        
        Args:
            ui_manager: Instance du gestionnaire d'interface
        """
        self.ui_manager = ui_manager
        logger.info("UI Manager attaché au jeu")
    
    def start_combat(self, enemies: list, environment: dict = None) -> bool:
        """
        Démarre un combat entre le joueur et les ennemis spécifiés
        
        Args:
            enemies: Liste des ennemis à combattre
            environment: Propriétés de l'environnement de combat (optionnel)
            
        Returns:
            True si le combat a démarré avec succès, False sinon
        """
        if not self.player:
            logger.error("Impossible de démarrer un combat: pas de joueur défini")
            return False
            
        if not enemies:
            logger.error("Impossible de démarrer un combat: pas d'ennemis spécifiés")
            return False
            
        if self.active_combat_ui:
            logger.warning("Un combat est déjà en cours")
            return False
            
        logger.info(f"Démarrage d'un combat contre {len(enemies)} ennemis")
        
        try:
            # Importer le module de combat pour ne pas avoir d'importation circulaire
            from yaktaa.combat.ui_qt import create_combat_ui
            
            # Créer l'interface de combat
            if self.ui_manager and self.ui_manager.main_window:
                self.active_combat_ui = create_combat_ui(
                    self.ui_manager.main_window,  # Fenêtre parent
                    self.player,                   # Joueur
                    enemies,                       # Ennemis
                    self._on_combat_ended          # Callback de fin de combat
                )
                return True
            else:
                logger.error("Impossible de démarrer un combat: UI Manager non initialisé")
                return False
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du combat: {e}")
            return False
    
    def _on_combat_ended(self, status):
        """
        Gère la fin d'un combat
        
        Args:
            status: Statut final du combat
        """
        from yaktaa.combat.engine import CombatStatus
        
        logger.info(f"Combat terminé avec statut: {status}")
        
        # Traiter le résultat du combat
        if status == CombatStatus.PLAYER_VICTORY:
            # Récompenses, expérience, etc.
            self.player.add_experience(50)  # Valeur basique, à ajuster selon la difficulté
            
            # Notification
            if self.ui_manager:
                self.ui_manager.show_message(
                    "Victoire!",
                    "Vous avez remporté le combat et gagné de l'expérience."
                )
                
        elif status == CombatStatus.ENEMY_VICTORY:
            # Conséquences de la défaite
            # Dans un jeu avec permadeath, on pourrait terminer la partie ici
            if self.ui_manager:
                self.ui_manager.show_message(
                    "Défaite!",
                    "Vous avez été vaincu. Vous vous réveillez plus tard, affaibli mais en vie."
                )
                
            # Réduire les ressources du joueur comme pénalité
            if self.player:
                credits_loss = int(self.player.credits * 0.1)  # Perte de 10% des crédits
                self.player.remove_credits(credits_loss)
                
        elif status == CombatStatus.ESCAPED:
            # Le joueur a fui
            if self.ui_manager:
                self.ui_manager.show_message(
                    "Fuite",
                    "Vous avez réussi à vous échapper du combat."
                )
                
        # Nettoyage
        self.active_combat_ui = None
        
        # Mettre à jour l'état du jeu
        self.update(0.1)
    
    def player_attack_npc(self, npc_id: str) -> bool:
        """
        Déclenche une attaque du joueur contre un PNJ, initiant un combat
        
        Args:
            npc_id: Identifiant du PNJ à attaquer
            
        Returns:
            True si le combat a été déclenché avec succès, False sinon
        """
        logger.info(f"Le joueur attaque le PNJ: {npc_id}")
        
        # Récupérer les données du PNJ depuis la carte
        npc_data = None
        if hasattr(self.ui_manager, "main_window"):
            if hasattr(self.ui_manager.main_window, "game_screen"):
                if hasattr(self.ui_manager.main_window.game_screen, "map_view"):
                    map_view = self.ui_manager.main_window.game_screen.map_view
                    if hasattr(map_view, "npc_manager"):
                        npc_data = map_view.npc_manager.get_npc(npc_id)
        
        # Si on a récupéré les données du PNJ, générer un ennemi à partir de celles-ci
        if npc_data:
            from yaktaa.combat.enemy import generate_enemy_from_npc
            enemy = generate_enemy_from_npc(npc_data)
            logger.info(f"Ennemi généré pour le combat: {enemy.name} (Niveau {enemy.level})")
        else:
            # Fallback: créer un ennemi générique si on n'a pas trouvé les données du PNJ
            from yaktaa.combat.enemy import Enemy, EnemyType
            enemy = Enemy(f"Ennemi-{npc_id}", EnemyType.HUMAN)
            logger.warning(f"Données du PNJ {npc_id} non trouvées, création d'un ennemi générique")
        
        # Démarrer le combat avec cet ennemi
        return self.start_combat([enemy])
    
    def trigger_random_encounter(self) -> bool:
        """
        Déclenche une rencontre aléatoire qui peut mener à un combat
        
        Returns:
            True si une rencontre a été déclenchée, False sinon
        """
        # Vérifier si on est dans une zone propice aux rencontres aléatoires
        if not self._is_dangerous_area():
            return False
            
        # Calculer la probabilité de rencontre (selon le lieu, l'heure, etc.)
        encounter_chance = 0.05  # 5% de base
        
        # Ajuster la probabilité selon les circonstances
        if self.city_manager and hasattr(self.city_manager, 'get_current_crime_rate'):
            crime_rate = self.city_manager.get_current_crime_rate()
            encounter_chance += crime_rate / 100  # Augmenter avec le taux de criminalité
            
        # Lancer les dés
        import random
        if random.random() < encounter_chance:
            # Générer des ennemis aléatoires
            from yaktaa.combat.enemy import generate_random_enemies
            enemies = generate_random_enemies(
                difficulty=self.player.level,
                count=random.randint(1, 3)
            )
            
            # Notification
            if self.ui_manager:
                self.ui_manager.show_message(
                    "Rencontre hostile!",
                    "Vous êtes attaqué par des individus hostiles!"
                )
                
            # Démarrer le combat
            return self.start_combat(enemies)
            
        return False
    
    def _is_dangerous_area(self) -> bool:
        """
        Détermine si le joueur se trouve dans une zone propice aux rencontres hostiles
        
        Returns:
            True si la zone est dangereuse, False sinon
        """
        # TODO: Implémentation complète avec vérification des zones
        # Pour l'instant, on suppose que certaines zones sont dangereuses de façon prédéfinie
        dangerous_zones = ["slums", "abandoned_district", "industrial_area", "outskirts"]
        
        # Récupérer la zone actuelle du joueur
        current_area = None
        if self.player:
            current_area = getattr(self.player, 'location_id', None)
            
        return current_area in dangerous_zones
