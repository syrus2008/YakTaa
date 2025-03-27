#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de démonstration des fonctionnalités avancées de YakTaa
Ce script permet de tester le système de hacking avancé et la génération procédurale de missions
sans avoir à lancer l'interface graphique complète
"""

import sys
import os
import logging
import time
import random
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / 'yaktaa_demo.log')
    ]
)

logger = logging.getLogger("YakTaa.Demo")

def setup_environment():
    """Configure l'environnement pour la démo"""
    # Ajouter le répertoire parent au chemin de recherche des modules
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    logger.info("Environnement configuré")

def create_mock_game():
    """Crée un mock de l'objet Game pour la démo"""
    from yaktaa.core.game import Game
    from yaktaa.characters.character import Character
    from yaktaa.world.locations import WorldMap, Location
    
    # Création du jeu
    game = Game()
    game.running = True
    
    # Création d'un joueur
    player = Character(name="Joueur Test", character_type="hacker")
    
    # Initialisation des compétences
    player._init_skills()  # S'assurer que les compétences sont initialisées
    player.improve_skill("hacking", 40)
    player.improve_skill("stealth", 30)
    player.improve_skill("charisma", 20)
    player.improve_skill("strength", 15)
    player.improve_skill("intelligence", 50)
    
    # Ajout du joueur au jeu
    game.player = player
    
    # Création d'une carte du monde
    game.world_map = WorldMap()
    
    # Création des lieux
    tokyo = Location(
        id="tokyo",
        name="Tokyo",
        description="Une métropole cyberpunk",
        coordinates=(139.6917, 35.6895),
        security_level=3,
        population=15000000
    )
    
    shanghai = Location(
        id="shanghai",
        name="Neo Shanghai",
        description="Centre financier d'Asie",
        coordinates=(121.4737, 31.2304),
        security_level=4,
        population=25000000
    )
    
    night_city = Location(
        id="night_city",
        name="Night City",
        description="Ville dangereuse et corrompue",
        coordinates=(-122.4194, 37.7749),
        security_level=5,
        population=7000000,
        is_dangerous=True
    )
    
    berlin = Location(
        id="berlin",
        name="New Berlin",
        description="Capitale technologique d'Europe",
        coordinates=(13.4050, 52.5200),
        security_level=2,
        population=5000000
    )
    
    # Ajout des lieux à la carte
    game.world_map.add_location(tokyo)
    game.world_map.add_location(shanghai)
    game.world_map.add_location(night_city)
    game.world_map.add_location(berlin)
    
    # Ajout des connexions entre les lieux
    game.world_map.add_connection("tokyo", "shanghai", travel_type="vol", travel_time=3.0)
    game.world_map.add_connection("shanghai", "night_city", travel_type="vol", travel_time=12.0)
    game.world_map.add_connection("night_city", "berlin", travel_type="vol", travel_time=10.0)
    game.world_map.add_connection("berlin", "tokyo", travel_type="vol", travel_time=11.0)
    
    # Création de personnages non-joueurs
    game.characters = {}
    
    fixer = Character(name="Raven", character_type="fixer")
    fixer._init_skills()
    fixer.improve_skill("charisma", 60)
    fixer.improve_skill("intelligence", 55)
    game.characters["raven"] = fixer
    
    corpo = Character(name="Mr. Smith", character_type="corporate")
    corpo._init_skills()
    corpo.improve_skill("intelligence", 65)
    corpo.improve_skill("charisma", 50)
    game.characters["smith"] = corpo
    
    netrunner = Character(name="Ghost", character_type="netrunner")
    netrunner._init_skills()
    netrunner.improve_skill("hacking", 75)
    netrunner.improve_skill("stealth", 60)
    game.characters["ghost"] = netrunner
    
    # Initialisation de la liste des missions
    game.missions = []
    
    logger.info("Mock du jeu créé avec succès")
    return game

def create_command_processor(game):
    """Crée un processeur de commandes pour la démo"""
    from yaktaa.terminal.command_processor import CommandProcessor
    
    # Création du processeur de commandes
    command_processor = CommandProcessor(game)
    
    logger.info("Processeur de commandes créé avec succès")
    return command_processor

def integrate_advanced_features(game, command_processor):
    """Intègre les fonctionnalités avancées pour la démo"""
    from yaktaa.core.feature_integrator import integrate_features
    
    # Intégration des fonctionnalités avancées
    integrator = integrate_features(game, command_processor)
    
    logger.info("Fonctionnalités avancées intégrées avec succès")
    return integrator

def simulate_terminal_input(command_processor, command):
    """Simule une entrée utilisateur dans le terminal"""
    print(f"\n> {command}")
    try:
        result = command_processor.process(command)
        # Remplacer les caractères Unicode problématiques par des alternatives ASCII
        if result:
            if isinstance(result, str):
                # Remplacer les emojis et autres caractères Unicode spéciaux par des alternatives ASCII
                result = result.replace('\U0001f534', '[X]')  # 🔴 -> [X]
                result = result.replace('\U0001f7e2', '[O]')  # 🟢 -> [O]
                result = result.replace('\U0001f7e1', '[!]')  # 🟡 -> [!]
                # Ajouter d'autres remplacements si nécessaire
                print(result)
            elif isinstance(result, dict):
                # Traitement des résultats structurés
                if result.get("type") == "table":
                    # Affichage d'un tableau
                    headers = result.get("headers", [])
                    rows = result.get("rows", [])
                    
                    # Calcul de la largeur des colonnes
                    col_widths = [len(h) for h in headers]
                    for row in rows:
                        for i, cell in enumerate(row):
                            if i < len(col_widths):
                                col_widths[i] = max(col_widths[i], len(str(cell)))
                    
                    # Affichage des en-têtes
                    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
                    print(header_line)
                    print("-" * len(header_line))
                    
                    # Affichage des lignes
                    for row in rows:
                        row_line = " | ".join(str(cell).ljust(col_widths[i]) if i < len(col_widths) else str(cell) 
                                             for i, cell in enumerate(row))
                        print(row_line)
                else:
                    # Affichage d'un message simple
                    message_type = result.get("type", "info")
                    message = result.get("message", "")
                    
                    if message_type == "error":
                        print(f"Erreur: {message}")
                    elif message_type == "success":
                        print(f"Succès: {message}")
                    else:
                        print(message)
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande: {e}")
    
    time.sleep(0.5)  # Pause pour simuler l'interaction

def run_hacking_demo(command_processor):
    """Exécute une démo du système de hacking"""
    print("\n=== DÉMO DU SYSTÈME DE HACKING ===\n")
    
    # Affichage de l'aide des commandes de hacking
    simulate_terminal_input(command_processor, "help")
    
    # Scan d'un système
    simulate_terminal_input(command_processor, "scan 192.168.1.100")
    
    # Affichage des outils de hacking disponibles
    simulate_terminal_input(command_processor, "tools")
    
    # Utilisation d'un outil
    simulate_terminal_input(command_processor, "use bruteforcer")
    
    # Tentative de hacking
    simulate_terminal_input(command_processor, "hack 192.168.1.100")
    
    # Résolution d'un puzzle
    simulate_terminal_input(command_processor, "solve bruteforce 1234")
    
    # Abandon d'une tentative de hacking
    simulate_terminal_input(command_processor, "abort")

def run_mission_demo(command_processor):
    """Exécute une démo du système de missions"""
    print("\n=== DÉMO DU SYSTÈME DE MISSIONS ===\n")
    
    # Affichage des missions disponibles
    simulate_terminal_input(command_processor, "missions")
    
    # Génération de nouvelles missions
    simulate_terminal_input(command_processor, "generate missions 3")
    
    # Affichage des détails d'une mission
    simulate_terminal_input(command_processor, "mission details 1")
    
    # Acceptation d'une mission
    simulate_terminal_input(command_processor, "accept mission 1")
    
    # Affichage des missions actives
    simulate_terminal_input(command_processor, "active missions")
    
    # Complétion d'une mission
    simulate_terminal_input(command_processor, "complete mission 1")
    
    # Abandon d'une mission
    simulate_terminal_input(command_processor, "accept mission 2")
    simulate_terminal_input(command_processor, "abandon mission 2")

def main():
    """Point d'entrée principal de la démo"""
    try:
        # Configuration de l'environnement
        setup_environment()
        
        # Création du mock du jeu
        game = create_mock_game()
        
        # Création du processeur de commandes
        command_processor = create_command_processor(game)
        
        # Intégration des fonctionnalités avancées
        integrate_advanced_features(game, command_processor)
        
        print("=== DÉMO DES FONCTIONNALITÉS AVANCÉES DE YAKTAA ===")
        print("Cette démo présente le système de hacking avancé et la génération procédurale de missions")
        
        # Exécution de la démo du système de hacking
        run_hacking_demo(command_processor)
        
        # Exécution de la démo du système de missions
        run_mission_demo(command_processor)
        
        print("\n=== FIN DE LA DÉMO ===")
        print("Les fonctionnalités avancées ont été testées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la démo: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
