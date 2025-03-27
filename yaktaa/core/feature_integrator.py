"""
Module d'intégration des fonctionnalités avancées de YakTaa
Ce module permet d'intégrer les systèmes de hacking avancé et de génération procédurale de missions
"""

import logging
from typing import Optional

from yaktaa.core.game import Game
from yaktaa.terminal.command_processor import CommandProcessor
from yaktaa.terminal.hacking_system import HackingSystem
from yaktaa.terminal.hacking_commands import HackingCommands
from yaktaa.missions.procedural_generator import MissionGenerator, generate_mission_batch
from yaktaa.terminal.mission_commands import MissionCommands
from yaktaa.world.locations import WorldMap
from yaktaa.characters.character import Character

logger = logging.getLogger("YakTaa.Core.FeatureIntegrator")

class FeatureIntegrator:
    """
    Classe d'intégration des fonctionnalités avancées
    Cette classe permet d'initialiser et d'intégrer les systèmes de hacking avancé
    et de génération procédurale de missions dans le jeu YakTaa
    """
    
    def __init__(self, game: Game):
        """
        Initialise l'intégrateur de fonctionnalités
        
        Args:
            game: Instance du jeu YakTaa
        """
        self.game = game
        self.hacking_system = None
        self.mission_generator = None
        
        logger.info("Intégrateur de fonctionnalités initialisé")
    
    def integrate_hacking_system(self, command_processor: CommandProcessor) -> None:
        """
        Intègre le système de hacking avancé au jeu
        
        Args:
            command_processor: Processeur de commandes du terminal
        """
        # Initialisation du système de hacking
        self.hacking_system = HackingSystem(game=self.game)
        
        # Enregistrement des commandes de hacking
        hacking_commands = HackingCommands(command_processor, self.hacking_system, game=self.game)
        
        logger.info("Système de hacking avancé intégré avec succès")
    
    def integrate_mission_system(self, command_processor: CommandProcessor) -> None:
        """
        Intègre le système de génération procédurale de missions au jeu
        
        Args:
            command_processor: Processeur de commandes du terminal
        """
        # Vérification que le jeu a une carte du monde et des personnages
        if not hasattr(self.game, 'world_map') or not self.game.world_map:
            logger.warning("Carte du monde non disponible, création d'une carte par défaut")
            self.game.world_map = WorldMap()
        
        if not hasattr(self.game, 'characters') or not self.game.characters:
            logger.warning("Personnages non disponibles, création d'un dictionnaire vide")
            self.game.characters = {}
        
        # Initialisation du générateur de missions
        self.mission_generator = MissionGenerator(self.game.world_map, self.game.characters)
        
        # Vérification que le jeu a une liste de missions
        if not hasattr(self.game, 'missions'):
            logger.warning("Liste de missions non disponible, création d'une liste vide")
            self.game.missions = []
        
        # Enregistrement des commandes de missions
        mission_commands = MissionCommands(command_processor, self.mission_generator, game=self.game)
        
        # Génération de missions initiales si la liste est vide
        if not self.game.missions:
            # Utiliser la fonction utilitaire generate_mission_batch
            initial_missions = generate_mission_batch(self.mission_generator, 5)
            self.game.missions.extend(initial_missions)
            logger.info(f"Généré {len(initial_missions)} missions initiales")
        
        logger.info("Système de génération procédurale de missions intégré avec succès")
    
    def integrate_all_features(self, command_processor: CommandProcessor) -> None:
        """
        Intègre toutes les fonctionnalités avancées au jeu
        
        Args:
            command_processor: Processeur de commandes du terminal
        """
        self.integrate_hacking_system(command_processor)
        self.integrate_mission_system(command_processor)
        
        logger.info("Toutes les fonctionnalités avancées ont été intégrées avec succès")


def integrate_features(game: Game, command_processor: Optional[CommandProcessor] = None) -> FeatureIntegrator:
    """
    Fonction utilitaire pour intégrer rapidement toutes les fonctionnalités
    
    Args:
        game: Instance du jeu YakTaa
        command_processor: Processeur de commandes du terminal (optionnel)
        
    Returns:
        FeatureIntegrator: Instance de l'intégrateur de fonctionnalités
    """
    integrator = FeatureIntegrator(game)
    
    if command_processor:
        integrator.integrate_all_features(command_processor)
    
    return integrator
