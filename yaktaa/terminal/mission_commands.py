"""
Module pour les commandes de gestion des missions dans le terminal YakTaa
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from tabulate import tabulate

from yaktaa.terminal.command_processor import CommandProcessor
from yaktaa.missions.procedural_generator import MissionGenerator
from yaktaa.missions.mission import Mission, MissionStatus, MissionType, MissionDifficulty

logger = logging.getLogger("YakTaa.Terminal.MissionCommands")

class MissionCommands:
    """Gestionnaire des commandes de missions pour le terminal"""
    
    def __init__(self, command_processor: CommandProcessor, mission_generator: MissionGenerator, game=None):
        """
        Initialise les commandes de missions
        
        Args:
            command_processor: Processeur de commandes du terminal
            mission_generator: Générateur de missions procédurales
            game: Instance du jeu (optionnel)
        """
        self.command_processor = command_processor
        self.mission_generator = mission_generator
        self.game = game
        
        # Enregistrement des commandes
        self._register_commands()
        
        logger.info("Commandes de missions initialisées")
    
    def _register_commands(self) -> None:
        """Enregistre les commandes de missions dans le processeur de commandes"""
        self.command_processor.register_command(
            "missions", self.cmd_missions, 
            "Affiche la liste des missions disponibles. Usage: missions [status]"
        )
        
        self.command_processor.register_command(
            "mission", self.cmd_mission, 
            "Affiche les détails d'une mission. Usage: mission <id>"
        )
        
        self.command_processor.register_command(
            "accept", self.cmd_accept, 
            "Accepte une mission. Usage: accept <id>"
        )
        
        self.command_processor.register_command(
            "abandon", self.cmd_abandon, 
            "Abandonne une mission en cours. Usage: abandon <id>"
        )
        
        self.command_processor.register_command(
            "complete", self.cmd_complete, 
            "Marque un objectif comme complété. Usage: complete <mission_id> <objective_index>"
        )
        
        self.command_processor.register_command(
            "generate", self.cmd_generate, 
            "Génère de nouvelles missions. Usage: generate [count=3]"
        )
    
    def cmd_missions(self, args: List[str]) -> str:
        """
        Commande pour afficher la liste des missions
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        # Filtrage par statut si spécifié
        status_filter = None
        if args and args[0].upper() in [s.name for s in MissionStatus]:
            status_filter = MissionStatus[args[0].upper()]
        
        # Récupération des missions
        missions = self.game.missions
        
        if status_filter:
            missions = [m for m in missions if m.status == status_filter]
        
        if not missions:
            return f"Aucune mission{' avec ce statut' if status_filter else ''} disponible."
        
        # Préparation des données pour le tableau
        table_data = []
        for mission in missions:
            # Calcul de la progression
            total_objectives = len(mission.objectives)
            completed_objectives = len([o for o in mission.objectives if o.completed])
            progress = f"{completed_objectives}/{total_objectives}"
            
            # Formatage des récompenses
            rewards = []
            if "credits" in mission.rewards:
                rewards.append(f"{mission.rewards['credits']} ¥")
            if "xp" in mission.rewards:
                rewards.append(f"{mission.rewards['xp']} XP")
            
            # Ajout à la table
            table_data.append([
                mission.id[:8],
                mission.title,
                mission.mission_type.name,
                mission.difficulty.name,
                mission.status.name,
                progress,
                ", ".join(rewards)
            ])
        
        # Création du tableau
        headers = ["ID", "Titre", "Type", "Difficulté", "Statut", "Progression", "Récompenses"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        response = "Liste des missions:\n\n"
        response += table
        response += "\n\nUtilisez 'mission <id>' pour voir les détails d'une mission."
        
        return response
    
    def cmd_mission(self, args: List[str]) -> str:
        """
        Commande pour afficher les détails d'une mission
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not args:
            return "Usage: mission <id>"
        
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        mission_id = args[0]
        
        # Recherche de la mission
        mission = None
        for m in self.game.missions:
            if m.id.startswith(mission_id):
                mission = m
                break
        
        if not mission:
            return f"Mission avec ID '{mission_id}' non trouvée."
        
        # Formatage de la réponse
        response = f"Mission: {mission.title}\n"
        response += f"ID: {mission.id}\n"
        response += f"Type: {mission.mission_type.name}\n"
        response += f"Difficulté: {mission.difficulty.name}\n"
        response += f"Statut: {mission.status.name}\n\n"
        
        response += f"Description:\n{mission.description}\n\n"
        
        # Objectifs
        response += "Objectifs:\n"
        for i, objective in enumerate(mission.objectives):
            status = "✅" if objective.completed else "⬜"
            optional = " (Optionnel)" if objective.optional else ""
            response += f"{i+1}. {status} {objective.description}{optional}\n"
        
        # Récompenses
        response += "\nRécompenses:\n"
        if "credits" in mission.rewards:
            response += f"- {mission.rewards['credits']} ¥\n"
        if "xp" in mission.rewards:
            response += f"- {mission.rewards['xp']} XP\n"
        if "reputation" in mission.rewards:
            for faction, rep in mission.rewards["reputation"].items():
                symbol = "+" if rep > 0 else ""
                response += f"- {symbol}{rep} réputation avec {faction}\n"
        if "items" in mission.rewards and mission.rewards["items"]:
            for item in mission.rewards["items"]:
                response += f"- {item['name']} ({item['rarity']})\n"
        
        # Actions disponibles
        response += "\nActions disponibles:\n"
        if mission.status == MissionStatus.AVAILABLE:
            response += "- 'accept <id>' pour accepter cette mission\n"
        elif mission.status == MissionStatus.ACTIVE:
            response += "- 'complete <mission_id> <objective_index>' pour marquer un objectif comme complété\n"
            response += "- 'abandon <id>' pour abandonner cette mission\n"
        
        return response
    
    def cmd_accept(self, args: List[str]) -> str:
        """
        Commande pour accepter une mission
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not args:
            return "Usage: accept <id>"
        
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        mission_id = args[0]
        
        # Recherche de la mission
        mission = None
        for m in self.game.missions:
            if m.id.startswith(mission_id):
                mission = m
                break
        
        if not mission:
            return f"Mission avec ID '{mission_id}' non trouvée."
        
        # Vérification du statut
        if mission.status != MissionStatus.AVAILABLE:
            return f"Cette mission n'est pas disponible (statut: {mission.status.name})."
        
        # Acceptation de la mission
        mission.status = MissionStatus.ACTIVE
        
        return f"Mission '{mission.title}' acceptée. Utilisez 'mission {mission_id}' pour voir les détails."
    
    def cmd_abandon(self, args: List[str]) -> str:
        """
        Commande pour abandonner une mission
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not args:
            return "Usage: abandon <id>"
        
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        mission_id = args[0]
        
        # Recherche de la mission
        mission = None
        for m in self.game.missions:
            if m.id.startswith(mission_id):
                mission = m
                break
        
        if not mission:
            return f"Mission avec ID '{mission_id}' non trouvée."
        
        # Vérification du statut
        if mission.status != MissionStatus.ACTIVE:
            return f"Cette mission n'est pas en cours (statut: {mission.status.name})."
        
        # Abandon de la mission
        mission.status = MissionStatus.FAILED
        
        return f"Mission '{mission.title}' abandonnée."
    
    def cmd_complete(self, args: List[str]) -> str:
        """
        Commande pour marquer un objectif comme complété
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if len(args) < 2:
            return "Usage: complete <mission_id> <objective_index>"
        
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        mission_id = args[0]
        
        # Vérification de l'index d'objectif
        try:
            objective_index = int(args[1]) - 1  # -1 car l'affichage commence à 1
        except ValueError:
            return "L'index d'objectif doit être un nombre."
        
        # Recherche de la mission
        mission = None
        for m in self.game.missions:
            if m.id.startswith(mission_id):
                mission = m
                break
        
        if not mission:
            return f"Mission avec ID '{mission_id}' non trouvée."
        
        # Vérification du statut
        if mission.status != MissionStatus.ACTIVE:
            return f"Cette mission n'est pas en cours (statut: {mission.status.name})."
        
        # Vérification de l'index d'objectif
        if objective_index < 0 or objective_index >= len(mission.objectives):
            return f"Index d'objectif invalide. La mission a {len(mission.objectives)} objectifs."
        
        # Marquage de l'objectif comme complété
        objective = mission.objectives[objective_index]
        
        if objective.completed:
            return f"Cet objectif est déjà complété."
        
        objective.completed = True
        
        # Vérification si tous les objectifs obligatoires sont complétés
        all_required_completed = True
        for obj in mission.objectives:
            if not obj.optional and not obj.completed:
                all_required_completed = False
                break
        
        response = f"Objectif '{objective.description}' marqué comme complété."
        
        # Si tous les objectifs obligatoires sont complétés, la mission est terminée
        if all_required_completed:
            mission.status = MissionStatus.COMPLETED
            
            # Attribution des récompenses
            if self.game and hasattr(self.game, 'player') and self.game.player:
                # Crédits
                if "credits" in mission.rewards:
                    self.game.player.credits += mission.rewards["credits"]
                    response += f"\nCrédits reçus: {mission.rewards['credits']} ¥"
                
                # XP
                if "xp" in mission.rewards:
                    self.game.player.add_xp(mission.rewards["xp"])
                    response += f"\nXP reçue: {mission.rewards['xp']}"
                
                # Réputation
                if "reputation" in mission.rewards:
                    for faction, rep in mission.rewards["reputation"].items():
                        if hasattr(self.game.player, 'reputation'):
                            if faction not in self.game.player.reputation:
                                self.game.player.reputation[faction] = 0
                            self.game.player.reputation[faction] += rep
                            symbol = "+" if rep > 0 else ""
                            response += f"\nRéputation {faction}: {symbol}{rep}"
                
                # Items
                if "items" in mission.rewards and mission.rewards["items"]:
                    for item in mission.rewards["items"]:
                        if hasattr(self.game.player, 'inventory'):
                            self.game.player.inventory.add_item(item)
                            response += f"\nItem reçu: {item['name']}"
            
            response += f"\n\nMission '{mission.title}' complétée!"
        
        return response
    
    def cmd_generate(self, args: List[str]) -> str:
        """
        Commande pour générer de nouvelles missions
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        # Nombre de missions à générer
        count = 3
        if args:
            try:
                count = int(args[0])
                count = max(1, min(10, count))  # Limiter entre 1 et 10
            except ValueError:
                return "Le nombre de missions doit être un entier."
        
        if not self.game or not hasattr(self.game, 'missions'):
            return "Système de missions non disponible."
        
        # Génération des missions
        new_missions = []
        for _ in range(count):
            mission = self.mission_generator.generate_mission()
            mission.status = MissionStatus.AVAILABLE
            self.game.missions.append(mission)
            new_missions.append(mission)
        
        # Formatage de la réponse
        response = f"{count} nouvelles missions générées:\n\n"
        
        for mission in new_missions:
            response += f"- {mission.title} (ID: {mission.id[:8]}, Type: {mission.mission_type.name}, Difficulté: {mission.difficulty.name})\n"
        
        response += "\nUtilisez 'missions' pour voir toutes les missions disponibles."
        
        return response
