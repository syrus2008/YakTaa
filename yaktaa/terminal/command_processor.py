"""
Module pour le traitement des commandes du terminal YakTaa
"""

import logging
import shlex
import re
import time
import random
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum

from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.Terminal.CommandProcessor")

# Définition de SecurityLevel ici pour éviter l'import circulaire
class SecurityLevel(Enum):
    """Niveaux de sécurité pour les systèmes informatiques"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4
    MAXIMUM = 5

class CommandProcessor:
    """Classe pour le traitement des commandes du terminal"""
    
    def __init__(self, game: Game):
        """Initialise le processeur de commandes"""
        self.game = game
        
        # État du terminal
        self.current_directory = "/"
        self.connected_system = None
        self.admin_access = False
        
        # Registre des commandes
        self.commands = {}
        
        # Suppression de l'initialisation de HackingCommands
        # self.hacking_commands = HackingCommands(game)
        
        # Enregistrement des commandes de base
        self._register_base_commands()
        
        logger.info("Processeur de commandes initialisé")
    
    def _register_base_commands(self) -> None:
        """Enregistre les commandes de base du terminal"""
        # Commandes d'aide
        self.register_command("help", self._cmd_help, "Affiche l'aide des commandes disponibles")
        self.register_command("man", self._cmd_man, "Affiche le manuel d'une commande")
        
        # Commandes de navigation
        self.register_command("ls", self._cmd_ls, "Liste le contenu du répertoire courant")
        self.register_command("dir", self._cmd_ls, "Alias de ls")
        self.register_command("cd", self._cmd_cd, "Change de répertoire")
        self.register_command("pwd", self._cmd_pwd, "Affiche le répertoire courant")
        
        # Commandes de fichiers
        self.register_command("cat", self._cmd_cat, "Affiche le contenu d'un fichier")
        self.register_command("type", self._cmd_cat, "Alias de cat")
        
        # Commandes réseau
        self.register_command("ping", self._cmd_ping, "Vérifie la connectivité avec un hôte")
        self.register_command("scan", self._cmd_scan, "Analyse un réseau ou un hôte")
        self.register_command("connect", self._cmd_connect, "Se connecte à un système distant")
        self.register_command("disconnect", self._cmd_disconnect, "Se déconnecte du système distant")
        
        # Commandes de hacking
        self.register_command("hack", self._cmd_hack, "Tente de pirater un système")
        self.register_command("crack", self._cmd_crack, "Tente de cracker un mot de passe")
        self.register_command("exploit", self._cmd_exploit, "Exploite une vulnérabilité")
        
        # Commandes système
        self.register_command("whoami", self._cmd_whoami, "Affiche l'identité actuelle")
        self.register_command("date", self._cmd_date, "Affiche la date et l'heure du système")
        self.register_command("clear", self._cmd_clear, "Efface l'écran du terminal")
        
        # Commandes de jeu
        self.register_command("status", self._cmd_status, "Affiche le statut du joueur")
        self.register_command("missions", self._cmd_missions, "Affiche les missions disponibles")
        self.register_command("inventory", self._cmd_inventory, "Affiche l'inventaire du joueur")
        self.register_command("skills", self._cmd_skills, "Affiche les compétences du joueur")
    
    def register_command(self, name: str, handler: Callable, description: str) -> None:
        """Enregistre une nouvelle commande"""
        self.commands[name.lower()] = {
            "handler": handler,
            "description": description
        }
    
    def process(self, command_line: str) -> Union[str, Dict[str, Any], None]:
        """Traite une ligne de commande"""
        if not command_line:
            return None
        
        # Analyse de la ligne de commande
        try:
            args = shlex.split(command_line)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la commande: {str(e)}", exc_info=True)
            return {"type": "error", "message": f"Erreur de syntaxe: {str(e)}"}
        
        # Extraction de la commande
        cmd = args[0].lower()
        
        # Vérification de l'existence de la commande
        if cmd not in self.commands:
            return {"type": "error", "message": f"Commande inconnue: {cmd}"}
        
        # Exécution de la commande
        try:
            return self.commands[cmd]["handler"](args[1:])
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la commande {cmd}: {str(e)}", exc_info=True)
            return {"type": "error", "message": f"Erreur: {str(e)}"}
    
    # Implémentation des commandes
    
    def _cmd_help(self, args: List[str]) -> Dict[str, Any]:
        """Affiche l'aide des commandes disponibles"""
        if args and args[0].lower() in self.commands:
            # Aide pour une commande spécifique
            cmd = args[0].lower()
            return {
                "type": "success",
                "message": f"Aide pour la commande '{cmd}':\n{self.commands[cmd]['description']}"
            }
        
        # Liste de toutes les commandes
        headers = ["Commande", "Description"]
        rows = []
        
        for cmd, info in sorted(self.commands.items()):
            rows.append([cmd, info["description"]])
        
        return {
            "type": "table",
            "headers": headers,
            "rows": rows
        }
    
    def _cmd_man(self, args: List[str]) -> Dict[str, Any]:
        """Affiche le manuel d'une commande"""
        if not args:
            return {"type": "error", "message": "Usage: man <commande>"}
        
        cmd = args[0].lower()
        if cmd not in self.commands:
            return {"type": "error", "message": f"Commande inconnue: {cmd}"}
        
        # TODO: Implémenter un système de manuel plus détaillé
        return {
            "type": "success",
            "message": f"Manuel de la commande '{cmd}':\n{self.commands[cmd]['description']}"
        }
    
    def _cmd_ls(self, args: List[str]) -> Dict[str, Any]:
        """Liste le contenu du répertoire courant"""
        # Récupération du chemin
        path = args[0] if args else self.current_directory
        
        # Si connecté à un système distant
        if self.connected_system:
            # TODO: Implémenter la navigation dans les systèmes distants
            files = [
                {"name": "readme.txt", "type": "file", "size": 1024},
                {"name": "config", "type": "directory", "size": 0},
                {"name": "data", "type": "directory", "size": 0},
                {"name": "system", "type": "directory", "size": 0}
            ]
        else:
            # Système local (joueur)
            files = [
                {"name": "home", "type": "directory", "size": 0},
                {"name": "bin", "type": "directory", "size": 0},
                {"name": "etc", "type": "directory", "size": 0},
                {"name": "var", "type": "directory", "size": 0},
                {"name": "welcome.txt", "type": "file", "size": 512}
            ]
        
        # Formatage de la sortie
        headers = ["Nom", "Type", "Taille"]
        rows = []
        
        for file in files:
            file_type = "[DIR]" if file["type"] == "directory" else "[FILE]"
            size = "-" if file["type"] == "directory" else f"{file['size']} o"
            rows.append([file["name"], file_type, size])
        
        return {
            "type": "table",
            "headers": headers,
            "rows": rows
        }
    
    def _cmd_cd(self, args: List[str]) -> Dict[str, Any]:
        """Change de répertoire"""
        if not args:
            return {"type": "success", "message": f"Répertoire courant: {self.current_directory}"}
        
        path = args[0]
        
        # Gestion des chemins relatifs et absolus
        if path.startswith("/"):
            new_path = path
        elif path == "..":
            # Remonter d'un niveau
            if self.current_directory == "/":
                new_path = "/"
            else:
                new_path = "/".join(self.current_directory.split("/")[:-1])
                if not new_path:
                    new_path = "/"
        else:
            # Chemin relatif
            if self.current_directory.endswith("/"):
                new_path = f"{self.current_directory}{path}"
            else:
                new_path = f"{self.current_directory}/{path}"
        
        # Vérification de l'existence du répertoire
        # TODO: Implémenter la vérification réelle
        
        # Mise à jour du répertoire courant
        self.current_directory = new_path
        
        return {"type": "success", "message": f"Répertoire courant: {self.current_directory}"}
    
    def _cmd_pwd(self, args: List[str]) -> Dict[str, Any]:
        """Affiche le répertoire courant"""
        return {"type": "success", "message": self.current_directory}
    
    def _cmd_cat(self, args: List[str]) -> Dict[str, Any]:
        """Affiche le contenu d'un fichier"""
        if not args:
            return {"type": "error", "message": "Usage: cat <fichier>"}
        
        filename = args[0]
        
        # Vérification de l'existence du fichier
        # TODO: Implémenter la vérification réelle
        
        # Contenu du fichier (exemple)
        if filename == "welcome.txt":
            content = """Bienvenue dans le système YakTaa OS!

Ce système est conçu pour vous aider dans vos missions de hacking et d'exploration.
Utilisez les commandes disponibles pour naviguer et interagir avec le monde.

Bon jeu!
"""
            return {"type": "success", "message": content}
        
        return {"type": "error", "message": f"Fichier non trouvé: {filename}"}
    
    def _cmd_ping(self, args: List[str]) -> Dict[str, Any]:
        """Vérifie la connectivité avec un hôte"""
        if not args:
            return {"type": "error", "message": "Usage: ping <hôte>"}
        
        host = args[0]
        
        # Simulation de ping
        return {
            "type": "success",
            "message": f"Ping vers {host}...\n"
                      f"Réponse de {host}: temps=10ms\n"
                      f"Réponse de {host}: temps=12ms\n"
                      f"Réponse de {host}: temps=9ms\n"
                      f"Réponse de {host}: temps=11ms\n\n"
                      f"Statistiques de ping pour {host}:\n"
                      f"    Paquets: envoyés = 4, reçus = 4, perdus = 0 (0% de perte),\n"
                      f"Durée approximative des boucles en millisecondes:\n"
                      f"    Minimum = 9ms, Maximum = 12ms, Moyenne = 10ms"
        }
    
    def _cmd_scan(self, args: List[str]) -> Dict[str, Any]:
        """Analyse un réseau ou un hôte"""
        # Si aucun argument n'est spécifié, scanner les réseaux du bâtiment actuel
        if not args:
            return self._scan_current_building_networks()
        
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
        message = f"Analyse de {target} terminée.\n\n"
        message += f"Type de système: {system_type.capitalize()}\n"
        message += f"Niveau de sécurité: {security_level.name}\n"
        message += f"Vulnérabilités détectées: {3 - min(2, security_level.value // 2)}\n\n"
        
        # Suggestion d'attaque
        message += "Recommandation: "
        if security_level.value <= SecurityLevel.MEDIUM.value:
            message += "Ce système présente des vulnérabilités exploitables. Utilisez 'hack' pour tenter une intrusion."
        else:
            message += "Ce système est bien protégé. Une tentative de hack nécessitera des outils avancés."
        
        return {
            "type": "info",
            "message": message
        }
    
    def _scan_current_building_networks(self) -> Dict[str, Any]:
        """
        Scanne les réseaux disponibles dans le bâtiment actuel
        
        Returns:
            Dict[str, Any]: Résultat du scan des réseaux
        """
        # Vérifier si le jeu est disponible
        if not self.game:
            return {"type": "error", "message": "Erreur: Impossible d'accéder aux données du jeu."}
        
        # Vérifier si le city_manager est disponible
        if not hasattr(self.game, 'city_manager'):
            return {"type": "error", "message": "Erreur: Impossible d'accéder au gestionnaire de ville."}
        
        # Récupérer le bâtiment actuel depuis le city_manager
        current_building = self.game.city_manager.get_current_building()
        
        # Si aucun bâtiment n'est actif, retourner une erreur
        if not current_building:
            return {"type": "error", "message": "Aucun réseau détecté. Vous devez être à l'intérieur d'un bâtiment pour scanner les réseaux locaux."}
        
        # Récupérer l'ID de la pièce actuelle (si disponible)
        current_room_id = None
        if hasattr(self.game.city_manager, 'current_room_id'):
            current_room_id = self.game.city_manager.current_room_id
        
        # Générer des réseaux en fonction du type de bâtiment
        networks = self._generate_networks_for_building(current_building, current_room_id)
        
        # Formatage de la réponse
        message = f"Scan des réseaux dans {current_building.name} terminé.\n\n"
        
        if not networks:
            return {"type": "info", "message": message + "Aucun réseau détecté dans ce bâtiment."}
        
        message += f"{len(networks)} réseau(x) détecté(s):"
        
        # Créer une table pour les réseaux
        headers = ["Nom", "SSID", "Type", "Sécurité", "Signal", "Chiffrement", "Ouvert"]
        rows = []
        
        for network in networks:
            rows.append([
                network['name'],
                network['ssid'],
                network['type'],
                network['security'],
                f"{network['signal_strength']}%",
                network['encryption'],
                "Oui" if network['open'] else "Non"
            ])
        
        return {
            "type": "complex",
            "message": message,
            "table": {
                "headers": headers,
                "rows": rows
            },
            "footer": "Pour vous connecter à un réseau, utilisez 'connect <ssid>'.\nPour hacker un réseau sécurisé, utilisez 'hack <ssid>'."
        }
    
    def _generate_networks_for_building(self, building, current_room_id):
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
        building_type = getattr(building, 'building_type', None)
        building_type_name = getattr(building_type, 'name', "DEFAULT") if building_type else "DEFAULT"
        security_level = getattr(building, 'security_level', 1)
        
        if building_type_name == "CORPORATE":
            num_networks = 3 + (security_level // 2)
        elif building_type_name == "RESIDENTIAL":
            num_networks = 1 + (security_level // 3)
        elif building_type_name == "COMMERCIAL":
            num_networks = 2 + (security_level // 3)
        elif building_type_name == "GOVERNMENT":
            num_networks = 4 + (security_level // 2)
        elif building_type_name == "SECURITY":
            num_networks = 3 + (security_level // 2)
        else:
            num_networks = 1 + (security_level // 4)
        
        # Noms de réseaux en fonction du type de bâtiment
        network_names = {
            "CORPORATE": [
                f"{getattr(building, 'owner', 'Corp')}_CORP", 
                f"{getattr(building, 'owner', 'Corp')}_SECURE", 
                f"{getattr(building, 'owner', 'Corp')}_GUEST", 
                "ADMIN_NET", 
                "SECURE_INTERNAL"
            ],
            "RESIDENTIAL": [
                "HOME_NETWORK", 
                "PRIVATE_WIFI", 
                f"APT_{getattr(building, 'id', '0000')[-4:]}"
            ],
            "COMMERCIAL": [
                f"{getattr(building, 'name', 'Shop').replace(' ', '')}_PUBLIC", 
                f"{getattr(building, 'name', 'Shop').replace(' ', '')}_STAFF", 
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
            if building_type_name in network_names:
                name_list = network_names[building_type_name]
            else:
                name_list = network_names["DEFAULT"]
            
            name = name_list[i % len(name_list)]
            if i >= len(name_list):
                name = f"{name}_{i - len(name_list) + 1}"
            
            # Générer un SSID
            building_id = getattr(building, 'id', '0000')
            ssid = f"{name}_{building_id[-4:]}".upper()
            
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
            
            if current_room_id and hasattr(building, 'rooms'):
                rooms = getattr(building, 'rooms', {})
                if current_room_id in rooms:
                    current_floor = rooms[current_room_id].get("floor", 0)
                    # Les réseaux sont plus forts à certains étages
                    floors = getattr(building, 'floors', 1)
                    network_floor = i % floors
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
                "floor": i % getattr(building, 'floors', 1)
            }
            
            networks.append(network)
        
        # Trier les réseaux par force de signal décroissante
        networks.sort(key=lambda x: x['signal_strength'], reverse=True)
        
        return networks
    
    def _cmd_connect(self, args: List[str]) -> Dict[str, Any]:
        """Se connecte à un système distant"""
        if not args:
            return {"type": "error", "message": "Usage: connect <hôte> [--user <utilisateur>] [--password <mot_de_passe>]"}
        
        host = args[0]
        user = "guest"
        password = ""
        
        # Analyse des arguments
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                if args[i] == "--user":
                    user = args[i + 1]
                elif args[i] == "--password":
                    password = args[i + 1]
        
        # Simulation de connexion
        self.connected_system = {
            "host": host,
            "user": user,
            "admin": user == "admin" and password == "admin123"  # Simulation simpliste
        }
        
        self.admin_access = self.connected_system["admin"]
        
        return {
            "type": "success",
            "message": f"Connecté à {host} en tant que {user}" + (" (accès administrateur)" if self.admin_access else "")
        }
    
    def _cmd_disconnect(self, args: List[str]) -> Dict[str, Any]:
        """Se déconnecte du système distant"""
        if not self.connected_system:
            return {"type": "error", "message": "Vous n'êtes pas connecté à un système distant"}
        
        host = self.connected_system["host"]
        self.connected_system = None
        self.admin_access = False
        
        return {"type": "success", "message": f"Déconnecté de {host}"}
    
    def _cmd_hack(self, args: List[str]) -> Dict[str, Any]:
        """Tente de pirater un système"""
        if not args:
            return {"type": "error", "message": "Usage: hack <cible> [--method <méthode>]"}
        
        target = args[0]
        method = "brute_force"
        
        # Analyse des arguments
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                if args[i] == "--method":
                    method = args[i + 1]
        
        # Vérification des compétences du joueur
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        hacking_skill = self.game.player.get_skill("hacking", 0)
        
        # Simulation de hacking
        success_chance = min(hacking_skill * 10, 90)  # Max 90% de chance
        
        # TODO: Implémenter un mini-jeu de hacking
        
        if hacking_skill < 3:
            return {"type": "error", "message": "Compétence de hacking insuffisante (niveau 3 requis)"}
        
        return {
            "type": "success",
            "message": f"Tentative de piratage de {target} avec la méthode {method}...\n"
                      f"Accès obtenu! Vous pouvez maintenant vous connecter avec 'connect {target} --user admin --password admin123'"
        }
    
    def _cmd_crack(self, args: List[str]) -> Dict[str, Any]:
        """Tente de cracker un mot de passe"""
        if not args:
            return {"type": "error", "message": "Usage: crack <fichier|hash>"}
        
        target = args[0]
        
        # Vérification des compétences du joueur
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        crypto_skill = self.game.player.get_skill("cryptography", 0)
        
        # Simulation de cracking
        if crypto_skill < 2:
            return {"type": "error", "message": "Compétence de cryptographie insuffisante (niveau 2 requis)"}
        
        return {
            "type": "success",
            "message": f"Cracking de {target}...\n"
                      f"Mot de passe trouvé: admin123"
        }
    
    def _cmd_exploit(self, args: List[str]) -> Dict[str, Any]:
        """Exploite une vulnérabilité"""
        if not args:
            return {"type": "error", "message": "Usage: exploit <vulnérabilité> [--target <cible>]"}
        
        vulnerability = args[0]
        target = "localhost"
        
        # Analyse des arguments
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                if args[i] == "--target":
                    target = args[i + 1]
        
        # Vérification des compétences du joueur
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        exploit_skill = self.game.player.get_skill("exploitation", 0)
        
        # Simulation d'exploitation
        if exploit_skill < 4:
            return {"type": "error", "message": "Compétence d'exploitation insuffisante (niveau 4 requis)"}
        
        return {
            "type": "success",
            "message": f"Exploitation de la vulnérabilité {vulnerability} sur {target}...\n"
                      f"Exploitation réussie! Accès root obtenu."
        }
    
    def _cmd_whoami(self, args: List[str]) -> Dict[str, Any]:
        """Affiche l'identité actuelle"""
        if self.connected_system:
            user = self.connected_system["user"]
            host = self.connected_system["host"]
            return {"type": "success", "message": f"{user}@{host}"}
        else:
            if self.game.player:
                return {"type": "success", "message": f"{self.game.player.name}@localhost"}
            else:
                return {"type": "success", "message": "utilisateur@localhost"}
    
    def _cmd_date(self, args: List[str]) -> Dict[str, Any]:
        """Affiche la date et l'heure du système"""
        if self.game:
            return {"type": "success", "message": f"Date du jeu: {self.game.format_game_time(include_date=True)}"}
        else:
            return {"type": "success", "message": "Date système non disponible"}
    
    def _cmd_clear(self, args: List[str]) -> Dict[str, Any]:
        """Efface l'écran du terminal"""
        # Cette commande est traitée directement par le widget de terminal
        return {"type": "success", "message": ""}
    
    def _cmd_status(self, args: List[str]) -> Dict[str, Any]:
        """Affiche le statut du joueur"""
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        player = self.game.player
        
        return {
            "type": "success",
            "message": f"Statut de {player.name}:\n"
                      f"Niveau: {player.level}\n"
                      f"XP: {player.xp}/{player.xp_for_next_level()}\n"
                      f"Santé: {player.health}/{player.max_health}\n"
                      f"Argent: {player.money} credits\n"
                      f"Réputation: {player.reputation}\n"
                      f"Emplacement: {self.game.world_manager.get_current_location().name if self.game.world_manager else 'Inconnu'}"
        }
    
    def _cmd_missions(self, args: List[str]) -> Dict[str, Any]:
        """Affiche les missions disponibles"""
        if not self.game.mission_manager:
            return {"type": "error", "message": "Erreur système: gestionnaire de missions non initialisé"}
        
        # Récupération des missions
        active_missions = self.game.mission_manager.get_active_missions()
        available_missions = self.game.mission_manager.get_available_missions()
        
        if not active_missions and not available_missions:
            return {"type": "success", "message": "Aucune mission disponible pour le moment"}
        
        result = "Missions actives:\n"
        if active_missions:
            for mission in active_missions:
                result += f"- {mission.title} ({mission.difficulty}★) - {mission.description}\n"
        else:
            result += "Aucune mission active\n"
        
        result += "\nMissions disponibles:\n"
        if available_missions:
            for mission in available_missions:
                result += f"- {mission.title} ({mission.difficulty}★) - {mission.description}\n"
        else:
            result += "Aucune mission disponible"
        
        return {"type": "success", "message": result}
    
    def _cmd_inventory(self, args: List[str]) -> Dict[str, Any]:
        """Affiche l'inventaire du joueur"""
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        # Récupération de l'inventaire
        inventory = self.game.player.inventory
        
        if not inventory or not inventory.items:
            return {"type": "success", "message": "Inventaire vide"}
        
        headers = ["Nom", "Type", "Quantité", "Description"]
        rows = []
        
        for item in inventory.items:
            rows.append([
                item.name,
                item.type,
                item.quantity,
                item.description
            ])
        
        return {
            "type": "table",
            "headers": headers,
            "rows": rows
        }
    
    def _cmd_skills(self, args: List[str]) -> Dict[str, Any]:
        """Affiche les compétences du joueur"""
        if not self.game.player:
            return {"type": "error", "message": "Erreur système: joueur non initialisé"}
        
        # Récupération des compétences
        skills = self.game.player.skills
        
        if not skills:
            return {"type": "success", "message": "Aucune compétence développée"}
        
        headers = ["Compétence", "Niveau", "XP", "Description"]
        rows = []
        
        for skill_name, skill in skills.items():
            rows.append([
                skill.name,
                skill.level,
                f"{skill.xp}/{skill.xp_for_next_level()}",
                skill.description
            ])
        
        return {
            "type": "table",
            "headers": headers,
            "rows": rows
        }
