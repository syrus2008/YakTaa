"""
Module pour le système de hacking avancé dans YakTaa
Implémente un système de puzzles de hacking procéduraux et dynamiques
"""

import logging
import random
import time
import math
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum, auto
from dataclasses import dataclass

logger = logging.getLogger("YakTaa.Terminal.HackingSystem")

class SecurityLevel(Enum):
    """Niveau de sécurité d'un système"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4
    MILITARY = 5
    CORPORATE = 6
    EXPERIMENTAL = 7


class HackingPuzzleType(Enum):
    """Types de puzzles de hacking disponibles"""
    PASSWORD_BRUTEFORCE = auto()
    BUFFER_OVERFLOW = auto()
    SEQUENCE_MATCHING = auto()
    NETWORK_REROUTING = auto()
    CODE_INJECTION = auto()
    ENCRYPTION_BREAKING = auto()
    FIREWALL_BYPASS = auto()
    MEMORY_MANIPULATION = auto()


@dataclass
class HackingTool:
    """Outil de hacking utilisable par le joueur"""
    id: str
    name: str
    description: str
    level: int
    puzzle_types: List[HackingPuzzleType]
    success_modifier: float  # Modificateur de chance de succès (1.0 = normal)
    time_modifier: float     # Modificateur de temps (1.0 = normal)
    cooldown: int            # Temps de recharge en secondes
    last_used: float = 0     # Timestamp de dernière utilisation
    
    def is_available(self) -> bool:
        """Vérifie si l'outil est disponible (cooldown terminé)"""
        return time.time() - self.last_used >= self.cooldown
    
    def use(self) -> None:
        """Utilise l'outil et met à jour le timestamp"""
        self.last_used = time.time()


class HackingPuzzle:
    """Classe de base pour les puzzles de hacking"""
    
    def __init__(self, 
                 puzzle_type: HackingPuzzleType,
                 difficulty: int,
                 time_limit: int = 60,
                 description: str = ""):
        """Initialise un puzzle de hacking"""
        self.id = f"puzzle_{uuid.uuid4().hex[:8]}"
        self.puzzle_type = puzzle_type
        self.difficulty = difficulty  # 1-10
        self.time_limit = time_limit  # en secondes
        self.description = description or f"Puzzle de hacking de type {puzzle_type.name}"
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.success: Optional[bool] = None
        
        # Données spécifiques au puzzle
        self.data: Dict[str, Any] = {}
        
        # Génération du puzzle
        self._generate()
        
    def _generate(self) -> None:
        """Génère le puzzle (à implémenter dans les sous-classes)"""
        pass
    
    def start(self) -> None:
        """Démarre le puzzle"""
        self.start_time = time.time()
        
    def end(self, success: bool) -> None:
        """Termine le puzzle"""
        self.end_time = time.time()
        self.success = success
        
    def get_remaining_time(self) -> float:
        """Retourne le temps restant en secondes"""
        if not self.start_time:
            return self.time_limit
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        return remaining
    
    def is_time_expired(self) -> bool:
        """Vérifie si le temps est écoulé"""
        return self.get_remaining_time() <= 0
    
    def get_success_chance(self, player_skill: int, tools: List[HackingTool] = None) -> float:
        """
        Calcule la chance de succès du hack basée sur la compétence du joueur et les outils
        
        Args:
            player_skill: Niveau de compétence du joueur (1-100)
            tools: Liste des outils de hacking utilisés
            
        Returns:
            float: Chance de succès (0.0 - 1.0)
        """
        # Calcul de base: plus la compétence est élevée par rapport à la difficulté, plus la chance est grande
        base_chance = min(0.95, max(0.05, (player_skill / 100) * (1 - (self.difficulty / 10))))
        
        # Bonus des outils
        tool_modifier = 1.0
        if tools:
            for tool in tools:
                if self.puzzle_type in tool.puzzle_types:
                    tool_modifier *= tool.success_modifier
        
        return min(0.95, base_chance * tool_modifier)


class PasswordBruteforcePuzzle(HackingPuzzle):
    """Puzzle de bruteforce de mot de passe"""
    
    def __init__(self, difficulty: int, time_limit: int = 60):
        """Initialise un puzzle de bruteforce de mot de passe"""
        super().__init__(
            puzzle_type=HackingPuzzleType.PASSWORD_BRUTEFORCE,
            difficulty=difficulty,
            time_limit=time_limit,
            description="Bruteforce d'un mot de passe. Trouvez le mot de passe correct parmi les options."
        )
    
    def _generate(self) -> None:
        """Génère le puzzle de bruteforce"""
        # Longueur du mot de passe basée sur la difficulté
        password_length = 4 + math.floor(self.difficulty / 2)
        
        # Caractères possibles
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if self.difficulty > 5:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        
        # Génération du mot de passe
        password = ''.join(random.choice(chars) for _ in range(password_length))
        
        # Génération des options (incluant le mot de passe correct)
        num_options = 4 + self.difficulty
        options = [password]
        
        # Génération des faux mots de passe
        while len(options) < num_options:
            fake_password = ''.join(random.choice(chars) for _ in range(password_length))
            if fake_password not in options:
                options.append(fake_password)
        
        # Mélange des options
        random.shuffle(options)
        
        # Stockage des données
        self.data = {
            "password": password,
            "options": options,
            "attempts_allowed": 3 if self.difficulty < 5 else 2
        }


class BufferOverflowPuzzle(HackingPuzzle):
    """Puzzle d'exploitation de buffer overflow"""
    
    def __init__(self, difficulty: int, time_limit: int = 90):
        """Initialise un puzzle de buffer overflow"""
        super().__init__(
            puzzle_type=HackingPuzzleType.BUFFER_OVERFLOW,
            difficulty=difficulty,
            time_limit=time_limit,
            description="Exploitez une vulnérabilité de buffer overflow en trouvant la séquence d'entrée correcte."
        )
    
    def _generate(self) -> None:
        """Génère le puzzle de buffer overflow"""
        # Taille du buffer basée sur la difficulté
        buffer_size = 8 + self.difficulty * 2
        
        # Génération de la séquence d'exploitation
        exploit_chars = "0123456789ABCDEF"
        exploit_sequence = ''.join(random.choice(exploit_chars) for _ in range(4 + self.difficulty))
        
        # Génération du code vulnérable
        code_template = f"""
void vulnerable_function(char* input) {{
    char buffer[{buffer_size}];
    strcpy(buffer, input);  // Vulnérabilité: pas de vérification de taille
}}

int main() {{
    char* user_input = get_user_input();
    vulnerable_function(user_input);
    return 0;
}}
        """
        
        # Indices sur l'exploitation basés sur la difficulté
        hints = []
        if self.difficulty <= 3:
            hints.append(f"Le buffer a une taille de {buffer_size} octets.")
            hints.append("Utilisez des caractères hexadécimaux pour l'exploitation.")
        elif self.difficulty <= 6:
            hints.append(f"Le buffer a une taille d'environ {buffer_size} octets.")
        
        # Stockage des données
        self.data = {
            "code": code_template,
            "buffer_size": buffer_size,
            "exploit_sequence": exploit_sequence,
            "hints": hints
        }


class SequenceMatchingPuzzle(HackingPuzzle):
    """Puzzle de correspondance de séquences"""
    
    def __init__(self, difficulty: int, time_limit: int = 60):
        """Initialise un puzzle de correspondance de séquences"""
        super().__init__(
            puzzle_type=HackingPuzzleType.SEQUENCE_MATCHING,
            difficulty=difficulty,
            time_limit=time_limit,
            description="Trouvez la séquence correcte parmi les fragments de code."
        )
    
    def _generate(self) -> None:
        """Génère le puzzle de correspondance de séquences"""
        # Nombre de fragments basé sur la difficulté
        num_fragments = 3 + self.difficulty
        
        # Génération de la séquence complète
        sequence_length = num_fragments * 4
        sequence = ''.join(random.choice("0123456789ABCDEF") for _ in range(sequence_length))
        
        # Découpage en fragments
        fragments = []
        for i in range(0, sequence_length, 4):
            fragments.append(sequence[i:i+4])
        
        # Mélange des fragments
        random.shuffle(fragments)
        
        # Stockage des données
        self.data = {
            "original_sequence": sequence,
            "fragments": fragments,
            "correct_order": [sequence[i:i+4] for i in range(0, sequence_length, 4)]
        }


class NetworkReroutingPuzzle(HackingPuzzle):
    """Puzzle de réacheminement de réseau"""
    
    def __init__(self, difficulty: int, time_limit: int = 120):
        """Initialise un puzzle de réacheminement de réseau"""
        super().__init__(
            puzzle_type=HackingPuzzleType.NETWORK_REROUTING,
            difficulty=difficulty,
            time_limit=time_limit,
            description="Réacheminez le trafic réseau pour contourner les défenses."
        )
    
    def _generate(self) -> None:
        """Génère le puzzle de réacheminement de réseau"""
        # Nombre de nœuds basé sur la difficulté
        num_nodes = 5 + self.difficulty
        
        # Génération des nœuds
        nodes = [f"Node-{chr(65+i)}" for i in range(num_nodes)]
        
        # Génération des connexions
        connections = []
        for i in range(num_nodes):
            # Chaque nœud est connecté à 2-4 autres nœuds
            num_connections = random.randint(2, min(4, num_nodes-1))
            connected_nodes = random.sample([n for n in range(num_nodes) if n != i], num_connections)
            for j in connected_nodes:
                if (j, i) not in connections:  # Éviter les doublons
                    connections.append((i, j))
        
        # Sélection du nœud de départ et d'arrivée
        start_node = random.randint(0, num_nodes-1)
        end_node = random.randint(0, num_nodes-1)
        while end_node == start_node:
            end_node = random.randint(0, num_nodes-1)
        
        # Génération des nœuds surveillés (à éviter)
        num_monitored = 1 + math.floor(self.difficulty / 2)
        monitored_nodes = random.sample([n for n in range(num_nodes) if n != start_node and n != end_node], 
                                       min(num_monitored, num_nodes-2))
        
        # Stockage des données
        self.data = {
            "nodes": nodes,
            "connections": connections,
            "start_node": start_node,
            "end_node": end_node,
            "monitored_nodes": monitored_nodes
        }


class HackingSystem:
    """Système principal de hacking"""
    
    def __init__(self, game=None):
        """Initialise le système de hacking"""
        self.game = game
        self.active_puzzle: Optional[HackingPuzzle] = None
        self.available_tools: Dict[str, HackingTool] = {}
        self.player_tools: Dict[str, HackingTool] = {}
        
        # Initialisation des outils de base
        self._init_base_tools()
        
        logger.info("Système de hacking initialisé")
    
    def _init_base_tools(self) -> None:
        """Initialise les outils de hacking de base"""
        base_tools = [
            HackingTool(
                id="basic_decryptor",
                name="Décrypteur basique",
                description="Un outil simple pour décrypter des mots de passe faibles.",
                level=1,
                puzzle_types=[HackingPuzzleType.PASSWORD_BRUTEFORCE],
                success_modifier=1.1,
                time_modifier=1.0,
                cooldown=30
            ),
            HackingTool(
                id="packet_sniffer",
                name="Analyseur de paquets",
                description="Capture et analyse le trafic réseau pour détecter des vulnérabilités.",
                level=1,
                puzzle_types=[HackingPuzzleType.NETWORK_REROUTING],
                success_modifier=1.1,
                time_modifier=1.0,
                cooldown=60
            ),
            HackingTool(
                id="code_analyzer",
                name="Analyseur de code",
                description="Analyse le code source pour trouver des failles d'exploitation.",
                level=1,
                puzzle_types=[HackingPuzzleType.BUFFER_OVERFLOW],
                success_modifier=1.1,
                time_modifier=1.0,
                cooldown=45
            ),
            HackingTool(
                id="sequence_matcher",
                name="Comparateur de séquences",
                description="Aide à identifier et à organiser des séquences de code.",
                level=1,
                puzzle_types=[HackingPuzzleType.SEQUENCE_MATCHING],
                success_modifier=1.1,
                time_modifier=1.0,
                cooldown=30
            )
        ]
        
        for tool in base_tools:
            self.available_tools[tool.id] = tool
            # Les outils de niveau 1 sont disponibles dès le début
            if tool.level == 1:
                self.player_tools[tool.id] = tool
    
    def create_puzzle(self, system_type: str, security_level: SecurityLevel) -> HackingPuzzle:
        """
        Crée un puzzle de hacking adapté au type de système et au niveau de sécurité
        
        Args:
            system_type: Type de système (server, database, mainframe, etc.)
            security_level: Niveau de sécurité du système
            
        Returns:
            HackingPuzzle: Un puzzle de hacking généré
        """
        # Conversion du niveau de sécurité en difficulté (1-10)
        difficulty = min(10, max(1, security_level.value * 1.5))
        
        # Sélection du type de puzzle en fonction du type de système
        puzzle_types = []
        if system_type.lower() in ["server", "serveur", "host", "hôte"]:
            puzzle_types = [HackingPuzzleType.PASSWORD_BRUTEFORCE, HackingPuzzleType.BUFFER_OVERFLOW]
        elif system_type.lower() in ["database", "base de données", "db"]:
            puzzle_types = [HackingPuzzleType.SEQUENCE_MATCHING, HackingPuzzleType.ENCRYPTION_BREAKING]
        elif system_type.lower() in ["network", "réseau"]:
            puzzle_types = [HackingPuzzleType.NETWORK_REROUTING, HackingPuzzleType.FIREWALL_BYPASS]
        elif system_type.lower() in ["mainframe", "système central"]:
            puzzle_types = [HackingPuzzleType.MEMORY_MANIPULATION, HackingPuzzleType.CODE_INJECTION]
        else:
            # Type par défaut
            puzzle_types = list(HackingPuzzleType)
        
        # Sélection aléatoire du type de puzzle
        puzzle_type = random.choice(puzzle_types)
        
        # Création du puzzle en fonction du type
        if puzzle_type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            return PasswordBruteforcePuzzle(difficulty=int(difficulty))
        elif puzzle_type == HackingPuzzleType.BUFFER_OVERFLOW:
            return BufferOverflowPuzzle(difficulty=int(difficulty))
        elif puzzle_type == HackingPuzzleType.SEQUENCE_MATCHING:
            return SequenceMatchingPuzzle(difficulty=int(difficulty))
        elif puzzle_type == HackingPuzzleType.NETWORK_REROUTING:
            return NetworkReroutingPuzzle(difficulty=int(difficulty))
        else:
            # Fallback sur un type de base
            return PasswordBruteforcePuzzle(difficulty=int(difficulty))
    
    def start_hacking(self, system_type: str, security_level: SecurityLevel) -> Dict[str, Any]:
        """
        Démarre une tentative de hacking sur un système
        
        Args:
            system_type: Type de système à hacker
            security_level: Niveau de sécurité du système
            
        Returns:
            Dict: Informations sur la tentative de hacking
        """
        # Création du puzzle
        puzzle = self.create_puzzle(system_type, security_level)
        self.active_puzzle = puzzle
        
        # Démarrage du puzzle
        puzzle.start()
        
        # Retour des informations initiales
        return {
            "puzzle_id": puzzle.id,
            "puzzle_type": puzzle.puzzle_type.name,
            "description": puzzle.description,
            "difficulty": puzzle.difficulty,
            "time_limit": puzzle.time_limit,
            "data": puzzle.data
        }
    
    def get_available_tools(self, puzzle_type: Optional[HackingPuzzleType] = None) -> List[HackingTool]:
        """
        Récupère les outils disponibles pour le joueur, filtré par type de puzzle si spécifié
        
        Args:
            puzzle_type: Type de puzzle pour filtrer les outils
            
        Returns:
            List[HackingTool]: Liste des outils disponibles
        """
        tools = list(self.player_tools.values())
        
        # Filtrage par type de puzzle
        if puzzle_type:
            tools = [tool for tool in tools if puzzle_type in tool.puzzle_types]
        
        # Filtrage par disponibilité (cooldown)
        tools = [tool for tool in tools if tool.is_available()]
        
        return tools
    
    def use_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Utilise un outil de hacking
        
        Args:
            tool_id: ID de l'outil à utiliser
            
        Returns:
            Dict: Résultat de l'utilisation de l'outil
        """
        if not self.active_puzzle:
            return {"success": False, "message": "Aucun hack en cours"}
        
        if tool_id not in self.player_tools:
            return {"success": False, "message": "Outil non disponible"}
        
        tool = self.player_tools[tool_id]
        
        if not tool.is_available():
            cooldown_remaining = int(tool.cooldown - (time.time() - tool.last_used))
            return {
                "success": False, 
                "message": f"Outil en recharge ({cooldown_remaining}s restantes)"
            }
        
        # Vérification de la compatibilité avec le puzzle
        if self.active_puzzle.puzzle_type not in tool.puzzle_types:
            return {
                "success": False,
                "message": f"Cet outil n'est pas adapté pour ce type de hack ({self.active_puzzle.puzzle_type.name})"
            }
        
        # Utilisation de l'outil
        tool.use()
        
        # Effet de l'outil (à personnaliser selon le type de puzzle)
        effect = {}
        if self.active_puzzle.puzzle_type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            # Révéler un indice sur le mot de passe
            password = self.active_puzzle.data["password"]
            if len(password) > 2:
                revealed_index = random.randint(0, len(password) - 1)
                effect["hint"] = f"Le caractère à la position {revealed_index + 1} est '{password[revealed_index]}'"
            else:
                effect["hint"] = "Le mot de passe est très court"
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.BUFFER_OVERFLOW:
            # Révéler une partie de la séquence d'exploitation
            exploit = self.active_puzzle.data["exploit_sequence"]
            if len(exploit) > 4:
                revealed_part = exploit[:4]
                effect["hint"] = f"La séquence d'exploitation commence par '{revealed_part}'"
            else:
                effect["hint"] = "La séquence d'exploitation est très courte"
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.SEQUENCE_MATCHING:
            # Révéler la position correcte d'un fragment
            fragments = self.active_puzzle.data["fragments"]
            correct_order = self.active_puzzle.data["correct_order"]
            if fragments and correct_order:
                fragment = random.choice(fragments)
                correct_index = correct_order.index(fragment)
                effect["hint"] = f"Le fragment '{fragment}' doit être en position {correct_index + 1}"
            else:
                effect["hint"] = "Les fragments doivent être réorganisés dans l'ordre croissant"
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.NETWORK_REROUTING:
            # Révéler un nœud à éviter
            monitored_nodes = self.active_puzzle.data["monitored_nodes"]
            nodes = self.active_puzzle.data["nodes"]
            if monitored_nodes and nodes:
                node_index = random.choice(monitored_nodes)
                effect["hint"] = f"Évitez le nœud '{nodes[node_index]}', il est surveillé"
            else:
                effect["hint"] = "Certains nœuds sont surveillés, évitez-les"
        
        return {
            "success": True,
            "message": f"Outil {tool.name} utilisé avec succès",
            "effect": effect
        }
    
    def submit_solution(self, solution: Any) -> Dict[str, Any]:
        """
        Soumet une solution pour le puzzle actif
        
        Args:
            solution: Solution proposée (format dépendant du type de puzzle)
            
        Returns:
            Dict: Résultat de la tentative
        """
        if not self.active_puzzle:
            return {"success": False, "message": "Aucun hack en cours"}
        
        if self.active_puzzle.is_time_expired():
            self.active_puzzle.end(False)
            return {"success": False, "message": "Temps écoulé"}
        
        # Vérification de la solution selon le type de puzzle
        result = False
        
        if self.active_puzzle.puzzle_type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            # Vérification du mot de passe
            correct_password = self.active_puzzle.data["password"]
            result = solution == correct_password
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.BUFFER_OVERFLOW:
            # Vérification de la séquence d'exploitation
            correct_sequence = self.active_puzzle.data["exploit_sequence"]
            result = solution == correct_sequence
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.SEQUENCE_MATCHING:
            # Vérification de l'ordre des fragments
            correct_order = self.active_puzzle.data["correct_order"]
            result = solution == correct_order
        
        elif self.active_puzzle.puzzle_type == HackingPuzzleType.NETWORK_REROUTING:
            # Vérification du chemin
            start_node = self.active_puzzle.data["start_node"]
            end_node = self.active_puzzle.data["end_node"]
            monitored_nodes = self.active_puzzle.data["monitored_nodes"]
            connections = self.active_puzzle.data["connections"]
            
            # Vérification que le chemin est valide
            valid_path = True
            for i in range(len(solution) - 1):
                if (solution[i], solution[i+1]) not in connections and (solution[i+1], solution[i]) not in connections:
                    valid_path = False
                    break
            
            # Vérification que le chemin commence et termine aux bons nœuds
            correct_endpoints = solution[0] == start_node and solution[-1] == end_node
            
            # Vérification qu'aucun nœud surveillé n'est traversé
            avoids_monitored = all(node not in monitored_nodes for node in solution[1:-1])
            
            result = valid_path and correct_endpoints and avoids_monitored
        
        # Fin du puzzle
        self.active_puzzle.end(result)
        
        # Calcul du temps écoulé
        elapsed_time = self.active_puzzle.end_time - self.active_puzzle.start_time
        
        # Calcul de l'XP gagnée (si succès)
        xp_gained = 0
        if result:
            # Base XP selon la difficulté
            base_xp = 10 * self.active_puzzle.difficulty
            
            # Bonus de temps
            time_ratio = elapsed_time / self.active_puzzle.time_limit
            time_bonus = 1.0
            if time_ratio < 0.5:
                time_bonus = 1.5  # +50% si terminé en moins de la moitié du temps
            elif time_ratio < 0.75:
                time_bonus = 1.2  # +20% si terminé en moins des 3/4 du temps
            
            xp_gained = int(base_xp * time_bonus)
            
            # Attribution de l'XP au joueur si le jeu est disponible
            if self.game and hasattr(self.game, 'player') and self.game.player:
                # Amélioration de la compétence appropriée
                if self.active_puzzle.puzzle_type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
                    self.game.player.improve_skill("cryptography", xp_gained)
                elif self.active_puzzle.puzzle_type == HackingPuzzleType.BUFFER_OVERFLOW:
                    self.game.player.improve_skill("exploitation", xp_gained)
                elif self.active_puzzle.puzzle_type == HackingPuzzleType.SEQUENCE_MATCHING:
                    self.game.player.improve_skill("pattern_analysis", xp_gained)
                elif self.active_puzzle.puzzle_type == HackingPuzzleType.NETWORK_REROUTING:
                    self.game.player.improve_skill("network_security", xp_gained)
                else:
                    self.game.player.improve_skill("hacking", xp_gained)
        
        # Réinitialisation du puzzle actif
        puzzle_type = self.active_puzzle.puzzle_type.name
        self.active_puzzle = None
        
        return {
            "success": result,
            "message": "Hack réussi!" if result else "Hack échoué!",
            "puzzle_type": puzzle_type,
            "time_elapsed": elapsed_time,
            "xp_gained": xp_gained
        }
    
    def cancel_hacking(self) -> Dict[str, Any]:
        """
        Annule la tentative de hacking en cours
        
        Returns:
            Dict: Confirmation de l'annulation
        """
        if not self.active_puzzle:
            return {"success": False, "message": "Aucun hack en cours"}
        
        puzzle_type = self.active_puzzle.puzzle_type.name
        self.active_puzzle.end(False)
        self.active_puzzle = None
        
        return {
            "success": True,
            "message": "Tentative de hack annulée",
            "puzzle_type": puzzle_type
        }
