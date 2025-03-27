"""
Démo du système de hacking et de génération procédurale de missions
"""

import logging
import sys
import os
import time

# Ajout du répertoire parent au path pour l'importation des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yaktaa.terminal.command_processor import CommandProcessor
from yaktaa.terminal.hacking_system import HackingSystem, SecurityLevel
from yaktaa.terminal.hacking_commands import HackingCommands
from yaktaa.missions.procedural_generator import MissionGenerator
from yaktaa.terminal.mission_commands import MissionCommands
from yaktaa.world.locations import WorldMap, Location
from yaktaa.characters.character import Character
from yaktaa.missions.mission import Mission, MissionStatus

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("YakTaa.Demo")

class DemoGame:
    """Classe de démonstration pour le jeu YakTaa"""
    
    def __init__(self):
        """Initialise la démo"""
        self.command_processor = CommandProcessor()
        self.hacking_system = HackingSystem(game=self)
        self.world_map = self._create_demo_world_map()
        self.characters = self._create_demo_characters()
        self.mission_generator = MissionGenerator(self.world_map, self.characters)
        self.missions = []
        self.player = self._create_player()
        
        # Initialisation des commandes
        self.hacking_commands = HackingCommands(self.command_processor, self.hacking_system, game=self)
        self.mission_commands = MissionCommands(self.command_processor, self.mission_generator, game=self)
        
        # Génération de missions initiales
        self._generate_initial_missions()
        
        logger.info("Démo initialisée")
    
    def _create_demo_world_map(self) -> WorldMap:
        """Crée une carte du monde de démonstration"""
        world_map = WorldMap()
        
        # Création de quelques lieux
        locations = [
            Location("Night City", "Une métropole cyberpunk", location_type="city"),
            Location("Quartier de Watson", "Un quartier industriel", location_type="district"),
            Location("Quartier de Westbrook", "Un quartier luxueux", location_type="district"),
            Location("Quartier de Pacifica", "Un quartier dangereux", location_type="district"),
            Location("Arasaka Tower", "Le siège d'Arasaka Corporation", location_type="corporation"),
            Location("The Afterlife", "Un bar populaire", location_type="special"),
            Location("Jig-Jig Street", "Une rue animée", location_type="special")
        ]
        
        # Ajout des lieux à la carte
        for location in locations:
            world_map.add_location(location)
        
        return world_map
    
    def _create_demo_characters(self) -> Dict[str, Character]:
        """Crée des personnages de démonstration"""
        characters = {}
        
        # Création de quelques personnages
        char_data = [
            {"name": "Rogue", "description": "Une fixeuse légendaire", "character_type": "fixer"},
            {"name": "T-Bug", "description": "Une netrunner talentueuse", "character_type": "hacker"},
            {"name": "Dexter DeShawn", "description": "Un fixer ambitieux", "character_type": "fixer"},
            {"name": "Meredith Stout", "description": "Une corpo de Militech", "character_type": "corporate"},
            {"name": "Jackie Welles", "description": "Un mercenaire loyal", "character_type": "mercenary"}
        ]
        
        for data in char_data:
            character = Character(data["name"])
            character.description = data["description"]
            character.character_type = data["character_type"]
            characters[character.name] = character
        
        return characters
    
    def _create_player(self) -> Character:
        """Crée le personnage du joueur"""
        player = Character("V")
        player.description = "Un mercenaire en quête de gloire"
        
        # Initialisation des attributs et compétences
        player.add_attribute("strength", 5)
        player.add_attribute("reflexes", 6)
        player.add_attribute("intelligence", 7)
        player.add_attribute("technical", 8)
        
        player.improve_skill("hacking", 20)
        player.improve_skill("cryptography", 15)
        player.improve_skill("network_security", 10)
        player.improve_skill("exploitation", 12)
        
        # Initialisation des crédits et de la réputation
        player.credits = 1000
        player.reputation = {
            "Netrunners": 10,
            "Fixers": 5,
            "Corporations": -5,
            "Nomades": 0,
            "Gangs": 0
        }
        
        # Initialisation de l'inventaire
        player.inventory = []
        
        return player
    
    def _generate_initial_missions(self) -> None:
        """Génère les missions initiales"""
        initial_missions = self.mission_generator.generate_mission_batch(5)
        
        # Toutes les missions initiales sont disponibles
        for mission in initial_missions:
            mission.status = MissionStatus.AVAILABLE
            self.missions.append(mission)
        
        logger.info(f"Généré {len(initial_missions)} missions initiales")
    
    def run(self) -> None:
        """Exécute la démo"""
        print("\n" + "="*80)
        print("DÉMO DU SYSTÈME DE HACKING ET DE GÉNÉRATION DE MISSIONS - YAKTAA")
        print("="*80 + "\n")
        
        print("Bienvenue dans la démo du système de hacking et de génération de missions de YakTaa!")
        print("Cette démo vous permet de tester les commandes de hacking et de gestion des missions.\n")
        
        print("Commandes disponibles:")
        print("- scan <cible>: Analyse un système pour détecter les vulnérabilités")
        print("- hack <cible> [niveau_sécurité]: Tente de hacker un système")
        print("- tools: Affiche les outils de hacking disponibles")
        print("- use <id_outil>: Utilise un outil de hacking")
        print("- solve <solution>: Soumet une solution pour le hack en cours")
        print("- abort: Annule le hack en cours")
        print("- missions [status]: Affiche la liste des missions disponibles")
        print("- mission <id>: Affiche les détails d'une mission")
        print("- accept <id>: Accepte une mission")
        print("- abandon <id>: Abandonne une mission en cours")
        print("- complete <mission_id> <objective_index>: Marque un objectif comme complété")
        print("- generate [count=3]: Génère de nouvelles missions")
        print("- help: Affiche l'aide")
        print("- exit: Quitte la démo\n")
        
        print("Commencez par utiliser 'missions' pour voir les missions disponibles, ou 'scan <cible>' pour analyser un système.\n")
        
        # Boucle principale
        running = True
        while running:
            try:
                # Lecture de la commande
                command = input("> ").strip()
                
                # Commande de sortie
                if command.lower() == "exit":
                    running = False
                    continue
                
                # Commande d'aide
                if command.lower() == "help":
                    print("\nCommandes disponibles:")
                    for cmd_name, cmd_info in self.command_processor.commands.items():
                        print(f"- {cmd_name}: {cmd_info['description']}")
                    print()
                    continue
                
                # Traitement de la commande
                result = self.command_processor.process_command(command)
                print(f"\n{result}\n")
                
            except KeyboardInterrupt:
                print("\nInterruption détectée. Utilisez 'exit' pour quitter.")
            except Exception as e:
                logger.error(f"Erreur: {e}")
                print(f"Une erreur est survenue: {e}")
        
        print("\nMerci d'avoir testé la démo de YakTaa!")


if __name__ == "__main__":
    # Exécution de la démo
    demo = DemoGame()
    demo.run()
