"""
Module pour les commandes de hacking dans le terminal YakTaa
"""

import logging
import time
import random
from typing import Dict, List, Any, Optional, Callable

from yaktaa.terminal.command_processor import CommandProcessor
from yaktaa.terminal.hacking_system import HackingSystem, SecurityLevel, HackingPuzzleType
from yaktaa.ui.widgets.hacking_minigames import (
    HackingMinigameBase, PasswordBruteforceMinigame, BufferOverflowMinigame,
    SequenceMatchingMinigame, NetworkReroutingMinigame
)

logger = logging.getLogger("YakTaa.Terminal.HackingCommands")

class HackingCommands:
    """Gestionnaire des commandes de hacking pour le terminal"""
    
    def __init__(self, command_processor: CommandProcessor, hacking_system: HackingSystem, game=None):
        """
        Initialise les commandes de hacking
        
        Args:
            command_processor: Processeur de commandes du terminal
            hacking_system: Système de hacking
            game: Instance du jeu (optionnel)
        """
        self.command_processor = command_processor
        self.hacking_system = hacking_system
        self.game = game
        
        # Enregistrement des commandes
        self._register_commands()
        
        logger.info("Commandes de hacking initialisées")
    
    def _register_commands(self) -> None:
        """Enregistre les commandes de hacking dans le processeur de commandes"""
        self.command_processor.register_command(
            "scan", self.cmd_scan, 
            "Analyse un système ou les réseaux disponibles dans le bâtiment actuel. Usage: scan <cible> ou scan"
        )
        
        self.command_processor.register_command(
            "hack", self.cmd_hack, 
            "Tente de hacker un système. Usage: hack <cible> [niveau_sécurité]"
        )
        
        self.command_processor.register_command(
            "tools", self.cmd_tools, 
            "Affiche les outils de hacking disponibles. Usage: tools [type]"
        )
        
        self.command_processor.register_command(
            "use", self.cmd_use, 
            "Utilise un outil de hacking. Usage: use <id_outil>"
        )
        
        self.command_processor.register_command(
            "solve", self.cmd_solve, 
            "Soumet une solution pour le hack en cours. Usage: solve <solution>"
        )
        
        self.command_processor.register_command(
            "abort", self.cmd_abort, 
            "Annule le hack en cours. Usage: abort"
        )
    
    def cmd_scan(self, args: List[str]) -> str:
        """
        Commande pour scanner un système ou les réseaux disponibles dans le bâtiment actuel
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        # Si aucun argument n'est spécifié, scanner les réseaux du bâtiment actuel
        if not args:
            result = self._scan_current_building_networks()
            
            # Notifier le jeu de l'événement de scan
            if self.game and hasattr(self.game, 'handle_hack_event'):
                event_data = {
                    "action": "scan_building_networks",
                    "building_id": getattr(self.game.player, 'current_building_id', None)
                }
                self.game.handle_hack_event("network_scan", event_data)
            
            return result
        
        target = args[0]
        
        # Simulation d'analyse
        time.sleep(1)  # Délai pour simuler l'analyse
        
        # Détermination aléatoire du niveau de sécurité
        security_levels = list(SecurityLevel)
        security_level = security_levels[min(len(security_levels) - 1, int(len(target) % len(security_levels)))]
        
        # Détermination du type de système
        system_types = ["server", "database", "network", "mainframe"]
        system_type = system_types[int(len(target) % len(system_types))]
        
        # Formatage de la réponse
        response = f"Analyse de {target} terminée.\n\n"
        response += f"Type de système: {system_type.capitalize()}\n"
        response += f"Niveau de sécurité: {security_level.name}\n"
        response += f"Vulnérabilités détectées: {3 - min(2, security_level.value // 2)}\n\n"
        
        # Suggestion d'attaque
        response += "Recommandation: "
        if security_level.value <= SecurityLevel.MEDIUM.value:
            response += "Ce système présente des vulnérabilités exploitables. Utilisez 'hack' pour tenter une intrusion."
        else:
            response += "Ce système est bien protégé. Une tentative de hack nécessitera des outils avancés."
        
        # Notifier le jeu de l'événement de scan
        if self.game and hasattr(self.game, 'handle_hack_event'):
            event_data = {
                "target": target,
                "security_level": security_level.value,
                "system_type": system_type,
                "vulnerabilities": 3 - min(2, security_level.value // 2)
            }
            self.game.handle_hack_event("system_scan", event_data)
        
        return response
    
    def _scan_current_building_networks(self) -> str:
        """
        Scanne les réseaux disponibles dans le bâtiment actuel
        
        Returns:
            str: Résultat du scan des réseaux
        """
        # Vérifier si le jeu est disponible
        if not self.game:
            return "Erreur: Impossible d'accéder aux données du jeu."
        
        # Vérifier si le joueur est dans un bâtiment
        if not hasattr(self.game, 'player') or not hasattr(self.game.player, 'current_building_id'):
            return "Aucun réseau détecté. Vous devez être à l'intérieur d'un bâtiment pour scanner les réseaux locaux."
        
        current_building_id = getattr(self.game.player, 'current_building_id', None)
        current_room_id = getattr(self.game.player, 'current_room_id', None)
        
        if not current_building_id:
            return "Aucun réseau détecté. Vous devez être à l'intérieur d'un bâtiment pour scanner les réseaux locaux."
        
        # Récupérer le bâtiment actuel
        building = None
        if hasattr(self.game, 'city_manager'):
            building = self.game.city_manager.get_building(current_building_id)
        
        if not building:
            return "Aucun réseau détecté. Erreur lors de l'accès aux données du bâtiment."
        
        # Générer des réseaux en fonction du type de bâtiment
        networks = self._generate_networks_for_building(building, current_room_id)
        
        # Formatage de la réponse
        response = f"Scan des réseaux dans {building.name} terminé.\n\n"
        
        if not networks:
            response += "Aucun réseau détecté dans ce bâtiment."
            return response
        
        response += f"{len(networks)} réseau(x) détecté(s):\n\n"
        
        for i, network in enumerate(networks):
            response += f"{i+1}. {network['name']} ({network['type']})\n"
            response += f"   SSID: {network['ssid']}\n"
            response += f"   Sécurité: {network['security']}\n"
            response += f"   Force du signal: {network['signal_strength']}%\n"
            if network['encrypted']:
                response += f"   Chiffrement: {network['encryption']}\n"
            if network['open']:
                response += "   Réseau ouvert: Oui\n"
            else:
                response += "   Réseau ouvert: Non\n"
            response += "\n"
        
        response += "Pour vous connecter à un réseau, utilisez 'connect <ssid>'.\n"
        response += "Pour hacker un réseau sécurisé, utilisez 'hack <ssid>'."
        
        return response
    
    def _generate_networks_for_building(self, building, current_room_id) -> List[Dict[str, Any]]:
        """
        Génère des réseaux pour un bâtiment donné
        
        Args:
            building: Le bâtiment pour lequel générer des réseaux
            current_room_id: L'ID de la pièce actuelle
            
        Returns:
            Liste des réseaux générés
        """
        networks = []
        
        # Déterminer le nombre de réseaux en fonction du type de bâtiment
        num_networks = 0
        if building.building_type.name == "CORPORATE":
            num_networks = 3 + (building.security_level // 2)
        elif building.building_type.name == "RESIDENTIAL":
            num_networks = 1 + (building.security_level // 3)
        elif building.building_type.name == "COMMERCIAL":
            num_networks = 2 + (building.security_level // 3)
        elif building.building_type.name == "GOVERNMENT":
            num_networks = 4 + (building.security_level // 2)
        elif building.building_type.name == "SECURITY":
            num_networks = 3 + (building.security_level // 2)
        else:
            num_networks = 1 + (building.security_level // 4)
        
        # Noms de réseaux en fonction du type de bâtiment
        network_names = {
            "CORPORATE": [
                f"{building.owner}_CORP", 
                f"{building.owner}_SECURE", 
                f"{building.owner}_GUEST", 
                "ADMIN_NET", 
                "SECURE_INTERNAL"
            ],
            "RESIDENTIAL": [
                "HOME_NETWORK", 
                "PRIVATE_WIFI", 
                f"APT_{building.id[-4:]}"
            ],
            "COMMERCIAL": [
                f"{building.name.replace(' ', '')}_PUBLIC", 
                f"{building.name.replace(' ', '')}_STAFF", 
                "CUSTOMER_WIFI"
            ],
            "GOVERNMENT": [
                "GOV_SECURE", 
                "ADMIN_NET", 
                "PUBLIC_ACCESS", 
                "RESTRICTED_NET", 
                "CLASSIFIED"
            ],
            "SECURITY": [
                "SECURITY_NET", 
                "SURVEILLANCE", 
                "RESTRICTED", 
                "EMERGENCY_NET"
            ],
            "DEFAULT": [
                "NETWORK", 
                "WIFI", 
                "PUBLIC", 
                "GUEST"
            ]
        }
        
        # Types de réseaux
        network_types = ["WiFi", "LAN", "WAN", "VPN", "IoT"]
        
        # Sécurités possibles
        securities = ["WEP", "WPA", "WPA2", "WPA3", "Enterprise", "Aucune"]
        
        # Chiffrements possibles
        encryptions = ["AES", "TKIP", "CCMP", "RC4", "Aucun"]
        
        # Générer les réseaux
        for i in range(num_networks):
            # Déterminer le nom du réseau
            if building.building_type.name in network_names:
                name_list = network_names[building.building_type.name]
            else:
                name_list = network_names["DEFAULT"]
            
            name = name_list[i % len(name_list)]
            if i >= len(name_list):
                name = f"{name}_{i - len(name_list) + 1}"
            
            # Générer un SSID
            ssid = f"{name}_{building.id[-4:]}".upper()
            
            # Déterminer le type de réseau
            network_type = network_types[i % len(network_types)]
            
            # Déterminer la sécurité
            security_index = min(i, len(securities) - 1)
            security = securities[security_index]
            
            # Déterminer si le réseau est ouvert
            open_network = security == "Aucune"
            
            # Déterminer le chiffrement
            encryption = "Aucun" if open_network else encryptions[i % (len(encryptions) - 1)]
            
            # Déterminer la force du signal (plus forte dans la pièce actuelle)
            base_signal = 50 + (i * 5) % 30
            signal_boost = 0
            
            if current_room_id and current_room_id in building.rooms:
                current_floor = building.rooms[current_room_id]["floor"]
                # Les réseaux sont plus forts à certains étages
                network_floor = i % building.floors
                floor_diff = abs(current_floor - network_floor)
                signal_boost = 30 - (floor_diff * 10)
            
            signal_strength = min(100, max(10, base_signal + signal_boost))
            
            # Créer le réseau
            network = {
                "name": name,
                "ssid": ssid,
                "type": network_type,
                "security": security,
                "encrypted": not open_network,
                "encryption": encryption,
                "open": open_network,
                "signal_strength": signal_strength,
                "floor": i % building.floors
            }
            
            networks.append(network)
        
        # Trier les réseaux par force de signal décroissante
        networks.sort(key=lambda x: x["signal_strength"], reverse=True)
        
        return networks
    
    def cmd_hack(self, args: List[str]) -> str:
        """
        Commande pour tenter de hacker un système
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not args:
            return "Erreur: Cible non spécifiée. Usage: hack <cible> [niveau_sécurité]"
        
        target = args[0]
        
        # Vérifier si un niveau de sécurité est spécifié
        security_level = SecurityLevel.MEDIUM
        if len(args) > 1:
            try:
                security_level_value = int(args[1])
                security_levels = list(SecurityLevel)
                if 0 <= security_level_value < len(security_levels):
                    security_level = security_levels[security_level_value]
                else:
                    return f"Erreur: Niveau de sécurité invalide. Doit être entre 0 et {len(security_levels) - 1}."
            except ValueError:
                return "Erreur: Le niveau de sécurité doit être un nombre. Usage: hack <cible> [niveau_sécurité]"
        
        # Simuler une tentative de connexion
        response = f"Tentative de connexion à {target}...\n"
        time.sleep(1)  # Délai pour simuler la connexion
        
        # Créer un puzzle de hacking
        system_type = "server" if "." in target else "network"
        puzzle = self.hacking_system.create_puzzle(system_type, security_level)
        
        # Stocker le puzzle en cours pour les commandes ultérieures
        self.hacking_system.current_puzzle = puzzle
        self.hacking_system.current_target = target
        
        # Déterminer si on utilise l'interface visuelle ou textuelle
        use_visual_interface = self._should_use_visual_interface(puzzle.type, security_level)
        
        if use_visual_interface and self.game and hasattr(self.game, 'ui_manager'):
            # Lancer le mini-jeu visuel de hacking approprié
            return self._launch_visual_hacking_minigame(puzzle, target)
        else:
            # Interface textuelle traditionnelle
            return self._handle_text_based_hacking(puzzle, target)
    
    def _should_use_visual_interface(self, puzzle_type: HackingPuzzleType, security_level: SecurityLevel) -> bool:
        """
        Détermine si le hack doit utiliser l'interface visuelle
        
        Args:
            puzzle_type: Type de puzzle
            security_level: Niveau de sécurité
            
        Returns:
            bool: True si l'interface visuelle doit être utilisée
        """
        # Vérifier si l'interface graphique est disponible
        if not self.game or not hasattr(self.game, 'ui_manager'):
            return False
        
        # Pour certains types de puzzles, toujours utiliser l'interface visuelle
        visual_puzzle_types = [
            HackingPuzzleType.PASSWORD_BRUTEFORCE,
            HackingPuzzleType.BUFFER_OVERFLOW,
            HackingPuzzleType.SEQUENCE_MATCHING,
            HackingPuzzleType.NETWORK_REROUTING
        ]
        
        if puzzle_type in visual_puzzle_types:
            # Pour les niveaux de sécurité élevés, toujours visuel
            if security_level.value >= SecurityLevel.HIGH.value:
                return True
                
            # Pour les niveaux inférieurs, chance aléatoire d'utiliser le visuel
            return random.random() < 0.7  # 70% de chance d'utiliser le visuel
        
        return False
    
    def _launch_visual_hacking_minigame(self, puzzle, target: str) -> str:
        """
        Lance le mini-jeu visuel de hacking approprié
        
        Args:
            puzzle: Le puzzle de hacking
            target: La cible du hack
            
        Returns:
            str: Message de lancement du mini-jeu
        """
        logger.info(f"Lancement du mini-jeu visuel pour {target} avec le puzzle de type {puzzle.type.name}")
        
        # Vérifier que nous avons accès au game et au ui_manager
        if not self.game or not hasattr(self.game, 'ui_manager'):
            return "Impossible de lancer l'interface visuelle. Mode texte uniquement disponible."
        
        try:
            # Importer la fabrique de mini-jeux
            from yaktaa.ui.widgets.hacking_minigames import HackingMinigameFactory
            
            # Créer le mini-jeu approprié pour ce type de puzzle
            minigame = HackingMinigameFactory.create_minigame(puzzle, self.game.main_window)
            
            # Définir le nom de la cible et les callbacks
            minigame.target_name = target
            minigame.puzzle_completed.connect(lambda success, time_used: self._handle_minigame_completion(success, target))
            
            # Afficher le mini-jeu via le gestionnaire d'UI
            self.game.ui_manager.show_hacking_minigame(minigame)
            
            # Définir le puzzle et la cible comme étant actuellement en cours de hack
            self.hacking_system.current_puzzle = puzzle
            self.hacking_system.current_target = target
            
            return f"Lancement de l'interface de hacking pour {target}..."
            
        except Exception as e:
            logger.error(f"Erreur lors du lancement du mini-jeu: {e}")
            return f"Erreur lors du lancement de l'interface visuelle: {e}. Tentative de hack en mode texte..."
    
    def _handle_minigame_completion(self, success: bool, target: str) -> None:
        """
        Gère la complétion d'un mini-jeu
        
        Args:
            success: True si le hack a réussi, False sinon
            target: La cible du hack
        """
        # Récupérer le puzzle en cours
        puzzle = self.hacking_system.current_puzzle
        
        if not puzzle:
            logger.warning(f"Puzzle non trouvé lors de la complétion du mini-jeu pour {target}")
            return
        
        # Gérer le résultat du hack
        if success:
            self._on_minigame_success(puzzle, target)
        else:
            self._on_minigame_failure(puzzle, target)
    
    def _on_minigame_success(self, puzzle, target: str) -> None:
        """
        Appelé lorsqu'un mini-jeu de hacking est réussi
        
        Args:
            puzzle: Le puzzle de hacking
            target: La cible du hack
        """
        logger.info(f"Hack réussi sur {target}")
        
        # Réinitialiser le hack en cours
        self.hacking_system.current_puzzle = None
        self.hacking_system.current_target = None
        
        # Message dans le terminal
        if self.game and hasattr(self.game, 'terminal'):
            self.game.terminal.add_output(
                f"\n[Système] Hack réussi sur {target}!"
            )
        
        # Notifier le jeu de l'événement de hack réussi
        if self.game and hasattr(self.game, 'handle_hack_event'):
            event_data = {
                "target": target,
                "puzzle_type": puzzle.type.name,
                "security_level": puzzle.security_level.value,
                "difficulty": puzzle.security_level.value + 1,
                "system_type": puzzle.system_type
            }
            self.game.handle_hack_event("hack_success", event_data)
    
    def _on_minigame_failure(self, puzzle, target: str) -> None:
        """
        Appelé lorsqu'un mini-jeu de hacking échoue
        
        Args:
            puzzle: Le puzzle de hacking
            target: La cible du hack
        """
        logger.info(f"Hack échoué sur {target}")
        
        # Réinitialiser le hack en cours
        self.hacking_system.current_puzzle = None
        self.hacking_system.current_target = None
        
        # Possibles conséquences de l'échec
        if self.game and hasattr(self.game, 'terminal'):
            if random.random() < 0.3:  # 30% de chance de déclencher une alerte
                self.game.terminal.add_output(
                    "\n[ALERTE] Intrusion détectée! Les administrateurs système ont été notifiés."
                )
                # TODO: Implémenter les conséquences d'une alerte
            else:
                self.game.terminal.add_output(
                    "\n[Système] Tentative de hack échouée. La connexion a été interrompue."
                )
        
        # Notifier le jeu de l'événement de hack échoué
        if self.game and hasattr(self.game, 'handle_hack_event'):
            event_data = {
                "target": target,
                "puzzle_type": puzzle.type.name,
                "security_level": puzzle.security_level.value,
                "system_type": puzzle.system_type,
                "alert_triggered": random.random() < 0.3  # Si une alerte a été déclenchée
            }
            self.game.handle_hack_event("hack_failed", event_data)
    
    def _handle_text_based_hacking(self, puzzle, target: str) -> str:
        """
        Gère un hack basé sur le terminal (non visuel)
        
        Args:
            puzzle: Le puzzle de hacking
            target: La cible du hack
            
        Returns:
            str: Message de hack en mode texte
        """
        response = f"Connexion établie avec {target}.\n\n"
        response += f"Système de type: {puzzle.system_type}\n"
        response += f"Niveau de sécurité: {puzzle.security_level.name}\n\n"
        
        # Informations spécifiques au type de puzzle
        if puzzle.type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            response += "Type d'attaque: Bruteforce de mot de passe\n\n"
            response += "Le système est protégé par un mot de passe. Utilisez 'solve <mot_de_passe>' pour tenter de le cracker."
            
            # Donner un indice
            if hasattr(puzzle, 'password_options') and puzzle.password_options:
                sample_size = min(3, len(puzzle.password_options))
                password_hints = random.sample(puzzle.password_options, sample_size)
                response += f"\n\nMots de passe possibles détectés dans la base de données: {', '.join(password_hints)}"
        
        elif puzzle.type == HackingPuzzleType.BUFFER_OVERFLOW:
            response += "Type d'attaque: Débordement de tampon\n\n"
            response += "Le système présente une vulnérabilité de débordement de tampon. "
            response += "Utilisez 'solve <payload>' pour exploiter cette faille."
            
            # Donner un indice
            response += "\n\nTaille du tampon: " + str(getattr(puzzle, 'buffer_size', 32))
            response += "\nPayload suggéré: \"" + "A" * (getattr(puzzle, 'buffer_size', 32) - 10) + "\""
        
        elif puzzle.type == HackingPuzzleType.SEQUENCE_MATCHING:
            response += "Type d'attaque: Correspondance de séquence\n\n"
            response += "Le système nécessite une séquence d'initialisation correcte. "
            response += "Utilisez 'solve <séquence>' pour tenter de la reproduire."
            
            # Donner un indice
            if hasattr(puzzle, 'sequence_fragments') and puzzle.sequence_fragments:
                fragments = getattr(puzzle, 'sequence_fragments', [])
                response += f"\n\nFragments détectés: {' | '.join(fragments[:3])}"
        
        else:
            response += f"Type d'attaque: {puzzle.type.name}\n\n"
            response += "Utilisez 'solve <solution>' pour tenter de résoudre ce puzzle."
        
        return response
    
    def cmd_solve(self, args: List[str]) -> str:
        """
        Commande pour soumettre une solution pour le hack en cours
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        if not self.hacking_system.current_puzzle:
            return "Erreur: Aucun hack en cours. Utilisez d'abord 'hack <cible>'."
        
        if not args:
            return "Erreur: Solution non spécifiée. Usage: solve <solution>"
        
        solution = " ".join(args)
        puzzle = self.hacking_system.current_puzzle
        target = self.hacking_system.current_target
        
        # Simuler un temps de calcul
        response = "Vérification de la solution...\n"
        time.sleep(1.5)  # Délai pour simuler la vérification
        
        # Vérifier si la solution est correcte (logique de vérification simplifiée)
        success = False
        
        if puzzle.type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            # Vérifier le mot de passe
            if hasattr(puzzle, 'correct_password') and solution.lower() == puzzle.correct_password.lower():
                success = True
            elif hasattr(puzzle, 'password_options') and solution.lower() in [p.lower() for p in puzzle.password_options]:
                # Test pour déterminer le succès basé sur la difficulté
                success_chance = self.hacking_system.get_success_chance(puzzle)
                success = random.random() < success_chance
        
        elif puzzle.type == HackingPuzzleType.BUFFER_OVERFLOW:
            # Vérifier le payload de débordement
            buffer_size = getattr(puzzle, 'buffer_size', 32)
            if len(solution) >= buffer_size:
                success_chance = self.hacking_system.get_success_chance(puzzle)
                success = random.random() < success_chance
        
        elif puzzle.type == HackingPuzzleType.SEQUENCE_MATCHING:
            # Vérifier la séquence
            if hasattr(puzzle, 'correct_sequence') and solution == puzzle.correct_sequence:
                success = True
            else:
                # Test partiel de la séquence
                fragments = getattr(puzzle, 'sequence_fragments', [])
                matching_parts = sum(1 for f in fragments if f in solution)
                success_chance = (matching_parts / len(fragments)) * self.hacking_system.get_success_chance(puzzle)
                success = random.random() < success_chance
        
        else:
            # Pour les autres types, vérification générique
            success_chance = self.hacking_system.get_success_chance(puzzle) * 0.5  # Plus difficile sans type spécifique
            success = random.random() < success_chance
        
        # Mettre à jour la réponse en fonction du résultat
        if success:
            response += f"\nAccès accordé! Vous avez réussi à hacker {target}.\n\n"
            
            # Récompenser le joueur
            if self.game and hasattr(self.game, 'player'):
                xp_reward = 50 * (puzzle.security_level.value + 1)
                self.game.player.add_xp(xp_reward)
                response += f"Vous gagnez {xp_reward} XP.\n"
            
            # Vérifier si ce hack fait partie d'une mission
            if self.game and hasattr(self.game, 'mission_manager'):
                mission_updated = self.game.mission_manager.update_hacking_objectives(target, True)
                if mission_updated:
                    response += "Objectif de mission mis à jour!\n"
            
            # Réinitialiser le hack en cours
            self.hacking_system.current_puzzle = None
            self.hacking_system.current_target = None
            
        else:
            response += "\nAccès refusé. Tentative de hack échouée.\n"
            
            # Possibles conséquences de l'échec
            trigger_alert = random.random() < 0.3  # 30% de chance de déclencher une alerte
            if trigger_alert:
                response += "\nALERTE! Intrusion détectée! Les administrateurs système ont été notifiés.\n"
                # TODO: Implémenter les conséquences d'une alerte
            
            # Incrémenter le compteur d'essais
            puzzle.attempts = getattr(puzzle, 'attempts', 0) + 1
            
            # Vérifier s'il y a trop d'essais
            if puzzle.attempts >= 3:
                response += "\nTrop de tentatives échouées. La connexion a été interrompue.\n"
                # Réinitialiser le hack en cours
                self.hacking_system.current_puzzle = None
                self.hacking_system.current_target = None
                
                # Vérifier si ce hack fait partie d'une mission
                if self.game and hasattr(self.game, 'mission_manager'):
                    self.game.mission_manager.update_hacking_objectives(target, False)
        
        return response
    
    def cmd_abort(self, args: List[str]) -> str:
        """
        Commande pour annuler le hack en cours
        
        Args:
            args: Arguments de la commande
            
        Returns:
            str: Résultat de la commande
        """
        # Vérification qu'un hack est en cours
        if not self.hacking_system.current_puzzle:
            return "Aucun hack en cours."
        
        # Annulation du hack
        result = self.hacking_system.cancel_hacking()
        
        return f"Hack annulé: {result['puzzle_type']}"
