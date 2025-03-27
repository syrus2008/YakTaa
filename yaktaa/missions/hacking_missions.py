"""
Module pour les missions de hacking dans YakTaa
Ce module permet de générer des missions de hacking procédurales qui s'intègrent
au système de missions principal.
"""

import logging
import random
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable

from yaktaa.missions.mission import Mission, Objective, MissionType, ObjectiveType
from yaktaa.terminal.hacking_system import (
    HackingSystem, SecurityLevel, HackingPuzzleType,
    HackingPuzzle, PasswordBruteforcePuzzle, BufferOverflowPuzzle,
    SequenceMatchingPuzzle, NetworkReroutingPuzzle
)
from yaktaa.world.locations import Location, BuildingType

logger = logging.getLogger("YakTaa.Missions.HackingMissions")

class HackingObjective(Objective):
    """Objectif spécifique aux missions de hacking"""
    
    def __init__(self, 
                 title: str, 
                 description: str, 
                 target_system: str,
                 security_level: SecurityLevel,
                 puzzle_type: Optional[HackingPuzzleType] = None,
                 location_id: Optional[str] = None,
                 reward_xp: int = 100,
                 reward_money: int = 500):
        """
        Initialise un objectif de hacking
        
        Args:
            title: Titre de l'objectif
            description: Description détaillée de l'objectif
            target_system: Identifiant du système à hacker
            security_level: Niveau de sécurité du système
            puzzle_type: Type de puzzle spécifique (si None, sera choisi en fonction du niveau)
            location_id: Identifiant de l'emplacement où se trouve le système
            reward_xp: Points d'expérience gagnés à la complétion
            reward_money: Argent gagné à la complétion
        """
        # Appel du constructeur parent avec les paramètres corrects
        super().__init__(
            description=description,
            objective_type=ObjectiveType.HACK,
            target_id=target_system
        )
        
        # Stockage des attributs spécifiques aux objectifs de hacking
        self.title = title  # Stocké comme attribut local car non présent dans la classe parente
        self.target_system = target_system
        self.security_level = security_level
        self.puzzle_type = puzzle_type
        self.location_id = location_id
        
        # Stockage des récompenses spécifiques
        self.reward_xp = reward_xp
        self.reward_money = reward_money
        
        # Métadonnées spécifiques au hacking
        self.metadata = {
            "system_type": target_system.split(".")[-1] if "." in target_system else "unknown",
            "security_level": security_level.name,
            "attempts": 0,
            "successful": False
        }
    
    def get_puzzle_hint(self) -> str:
        """Retourne un indice sur le puzzle à résoudre"""
        hints = {
            HackingPuzzleType.PASSWORD_BRUTEFORCE: [
                "Analysez les motifs communs dans les mots de passe.",
                "Les administrateurs utilisent souvent des mots-clés liés à l'entreprise.",
                "Cherchez des indices dans les documents accessibles."
            ],
            HackingPuzzleType.BUFFER_OVERFLOW: [
                "Recherchez les fonctions de traitement d'entrée sans validation.",
                "Les tampons de taille fixe sont vulnérables aux dépassements.",
                "Une séquence de caractères bien choisie peut rediriger l'exécution."
            ],
            HackingPuzzleType.SEQUENCE_MATCHING: [
                "Analysez attentivement l'ordre logique des fragments.",
                "Certaines séquences d'initialisation suivent un motif standard.",
                "Commencez par identifier les fragments de début et de fin."
            ],
            HackingPuzzleType.NETWORK_REROUTING: [
                "Évitez les nœuds hautement surveillés.",
                "Le chemin le plus court n'est pas toujours le plus sûr.",
                "Identifiez les points d'entrée et de sortie avant de planifier votre route."
            ]
        }
        
        if self.puzzle_type and self.puzzle_type in hints:
            return random.choice(hints[self.puzzle_type])
        else:
            return "Analysez le système avant de tenter une intrusion."


class HackingMission(Mission):
    """Mission spécialisée dans le hacking"""
    
    def __init__(self, 
                 title: str, 
                 description: str,
                 difficulty: int = 1,
                 target_corporation: Optional[str] = None,
                 reward_xp: int = 500,
                 reward_money: int = 2000,
                 reward_items: Optional[List[str]] = None):
        """
        Initialise une mission de hacking
        
        Args:
            title: Titre de la mission
            description: Description détaillée de la mission
            difficulty: Niveau de difficulté (1-10)
            target_corporation: Corporation ciblée (si applicable)
            reward_xp: Points d'expérience gagnés à la complétion
            reward_money: Argent gagné à la complétion
            reward_items: Liste d'identifiants d'objets gagnés à la complétion
        """
        # Création des métadonnées avant d'appeler le constructeur parent
        metadata = {
            "type": "hacking",
            "difficulty": difficulty,
            "target_corporation": target_corporation,
            "stealth_required": difficulty > 5
        }
        
        # Initialisation des récompenses
        rewards = {
            "xp": reward_xp,
            "credits": reward_money,
            "items": reward_items or []
        }
        
        # Appel du constructeur parent avec les paramètres corrects
        super().__init__(
            title=title, 
            description=description,
            mission_type=MissionType.CONTRACT,  # Les missions de hacking sont des contrats par défaut
            difficulty=difficulty,
            metadata=metadata
        )
        
        # Mise à jour des récompenses
        self.rewards.update(rewards)
        
        # Stockage des attributs spécifiques aux missions de hacking
        self.difficulty = difficulty
        self.target_corporation = target_corporation
        
        # Note: Déjà initialisées dans le constructeur
        # self.metadata.update({
        #     "type": "hacking",
        #     "difficulty": difficulty,
        #     "target_corporation": target_corporation,
        #     "stealth_required": difficulty > 5
        # })
    
    def add_hacking_objective(self, 
                             title: str, 
                             description: str, 
                             target_system: str,
                             security_level: SecurityLevel,
                             puzzle_type: Optional[HackingPuzzleType] = None,
                             location_id: Optional[str] = None) -> HackingObjective:
        """
        Ajoute un objectif de hacking à la mission
        
        Args:
            title: Titre de l'objectif
            description: Description détaillée de l'objectif
            target_system: Identifiant du système à hacker
            security_level: Niveau de sécurité du système
            puzzle_type: Type de puzzle spécifique (si None, sera choisi en fonction du niveau)
            location_id: Identifiant de l'emplacement où se trouve le système
            
        Returns:
            HackingObjective: L'objectif créé et ajouté
        """
        # Calculer les récompenses basées sur le niveau de sécurité
        reward_xp = 50 * (security_level.value + 1)
        reward_money = 200 * (security_level.value + 1)
        
        objective = HackingObjective(
            title=title,
            description=description,
            target_system=target_system,
            security_level=security_level,
            puzzle_type=puzzle_type,
            location_id=location_id,
            reward_xp=reward_xp,
            reward_money=reward_money
        )
        
        self.add_objective(objective)
        return objective


class HackingMissionGenerator:
    """Générateur de missions de hacking procédurales"""
    
    # Types de missions de hacking
    MISSION_TYPES = [
        "data_extraction",
        "system_breach",
        "sabotage",
        "information_gathering",
        "asset_recovery",
        "surveillance"
    ]
    
    # Corporations avec leurs domaines d'activité
    CORPORATIONS = {
        "ArasaCorp": {"domain": "military", "security": SecurityLevel.MILITARY},
        "NeoTech": {"domain": "technology", "security": SecurityLevel.HIGH},
        "GlobalFinance": {"domain": "finance", "security": SecurityLevel.VERY_HIGH},
        "MediCore": {"domain": "medical", "security": SecurityLevel.MEDIUM},
        "InfoSphere": {"domain": "media", "security": SecurityLevel.LOW},
        "OmniSys": {"domain": "infrastructure", "security": SecurityLevel.HIGH},
        "QuantumDynamics": {"domain": "research", "security": SecurityLevel.EXPERIMENTAL},
        "CyberLink": {"domain": "communications", "security": SecurityLevel.MEDIUM}
    }
    
    # Systèmes par corporation et domaine
    SYSTEMS = {
        "military": ["weapon.control", "defense.grid", "personnel.database", "surveillance.network"],
        "technology": ["research.database", "product.blueprint", "user.accounts", "cloud.storage"],
        "finance": ["transaction.logs", "client.database", "investment.portfolio", "security.vault"],
        "medical": ["patient.records", "research.data", "pharmacy.inventory", "staff.database"],
        "media": ["content.server", "subscriber.database", "broadcast.system", "analytics.database"],
        "infrastructure": ["power.grid", "traffic.control", "water.management", "security.cameras"],
        "research": ["experiment.data", "personnel.files", "prototype.specs", "funding.records"],
        "communications": ["message.server", "user.profiles", "routing.system", "encryption.keys"]
    }
    
    def __init__(self, game=None):
        """Initialise le générateur de missions"""
        self.game = game
        self.hacking_system = HackingSystem(game)
        logger.info("Générateur de missions de hacking initialisé")
    
    def generate_mission(self, 
                         difficulty: int = None, 
                         corporation: str = None,
                         location: Location = None) -> HackingMission:
        """
        Génère une mission de hacking procédurale
        
        Args:
            difficulty: Niveau de difficulté (1-10)
            corporation: Corporation ciblée spécifique
            location: Emplacement spécifique pour la mission
            
        Returns:
            HackingMission: Une mission de hacking générée
        """
        # Choisir une difficulté si non spécifiée
        if difficulty is None:
            difficulty = random.randint(1, 10)
        
        # Choisir une corporation si non spécifiée
        if corporation is None:
            corporation = random.choice(list(self.CORPORATIONS.keys()))
        
        # Déterminer le type de mission
        mission_type = random.choice(self.MISSION_TYPES)
        
        # Générer le titre et la description
        title, description = self._generate_mission_text(mission_type, corporation, difficulty)
        
        # Créer la mission
        mission = HackingMission(
            title=title,
            description=description,
            difficulty=difficulty,
            target_corporation=corporation,
            reward_xp=300 * difficulty,
            reward_money=1000 * difficulty
        )
        
        # Ajouter les objectifs
        self._add_mission_objectives(mission, mission_type, corporation, difficulty, location)
        
        logger.info(f"Mission de hacking générée: {title} (difficulté: {difficulty})")
        return mission
    
    def _generate_mission_text(self, mission_type: str, corporation: str, difficulty: int) -> Tuple[str, str]:
        """Génère le titre et la description d'une mission"""
        titles = {
            "data_extraction": [
                f"Vol de données chez {corporation}",
                f"Extraction d'informations de {corporation}",
                f"Récupération de données sensibles"
            ],
            "system_breach": [
                f"Infiltration des systèmes de {corporation}",
                f"Brèche dans la sécurité de {corporation}",
                f"Accès non autorisé au réseau principal"
            ],
            "sabotage": [
                f"Sabotage des opérations de {corporation}",
                f"Perturbation des systèmes critiques",
                f"Opération de déstabilisation"
            ],
            "information_gathering": [
                f"Collecte d'informations sur {corporation}",
                f"Reconnaissance des systèmes internes",
                f"Analyse du réseau corporatif"
            ],
            "asset_recovery": [
                f"Récupération d'actifs volés",
                f"Extraction de technologie propriétaire",
                f"Récupération de données perdues"
            ],
            "surveillance": [
                f"Mise en place d'une surveillance sur {corporation}",
                f"Implantation de logiciels espions",
                f"Opération d'écoute à long terme"
            ]
        }
        
        descriptions = {
            "data_extraction": [
                f"Un client anonyme vous a engagé pour extraire des données sensibles des serveurs de {corporation}. "
                f"La mission nécessite discrétion et précision. Les données doivent être récupérées sans laisser de traces.",
                
                f"Des informations cruciales sont stockées dans les serveurs de {corporation}. "
                f"Votre objectif est de pénétrer leurs systèmes et d'extraire ces données sans être détecté."
            ],
            "system_breach": [
                f"Votre mission est d'infiltrer le réseau principal de {corporation} et d'établir un accès permanent. "
                f"Cette brèche servira de point d'entrée pour de futures opérations.",
                
                f"Les systèmes de {corporation} doivent être compromis pour permettre à votre client d'y accéder à volonté. "
                f"Créez une porte dérobée discrète et indétectable."
            ],
            "sabotage": [
                f"{corporation} a causé des torts à votre client. Votre mission est de perturber leurs opérations "
                f"en compromettant leurs systèmes critiques. Restez discret pour maximiser l'impact.",
                
                f"Sabotez les systèmes principaux de {corporation} pour causer des dysfonctionnements dans leurs opérations. "
                f"Le chaos doit sembler être le résultat d'une défaillance interne, pas d'une attaque."
            ],
            "information_gathering": [
                f"Recueillez des informations stratégiques sur les opérations de {corporation}. "
                f"Ces données serviront à planifier de futures actions contre eux.",
                
                f"Votre client a besoin d'informations précises sur la structure interne et les vulnérabilités de {corporation}. "
                f"Infiltrez leurs systèmes et récupérez autant de données que possible."
            ],
            "asset_recovery": [
                f"Des actifs numériques précieux ont été volés par {corporation}. "
                f"Votre mission est de les récupérer et d'effacer toute trace de leur existence dans leurs systèmes.",
                
                f"Une technologie propriétaire a été illégalement acquise par {corporation}. "
                f"Infiltrez leurs serveurs, récupérez les données et supprimez toute copie de leurs systèmes."
            ],
            "surveillance": [
                f"Établissez un système de surveillance discrète dans le réseau de {corporation}. "
                f"Votre client a besoin d'un flux constant d'informations sur leurs activités.",
                
                f"Implantez des logiciels espions sophistiqués dans l'infrastructure de {corporation}. "
                f"Ces outils doivent permettre une surveillance à long terme sans être détectés."
            ]
        }
        
        title = random.choice(titles.get(mission_type, [f"Mission de hacking contre {corporation}"]))
        description = random.choice(descriptions.get(mission_type, [f"Infiltrez les systèmes de {corporation} pour accomplir vos objectifs."]))
        
        # Ajouter des détails sur la difficulté
        if difficulty <= 3:
            description += "\n\nCette mission semble relativement simple, avec des défenses basiques."
        elif difficulty <= 6:
            description += "\n\nLes systèmes sont bien protégés, mais des failles existent. Soyez méthodique."
        else:
            description += "\n\nAttention, cette mission est extrêmement dangereuse. Les systèmes sont hautement sécurisés avec plusieurs couches de protection."
        
        return title, description
    
    def _add_mission_objectives(self, 
                               mission: HackingMission, 
                               mission_type: str, 
                               corporation: str, 
                               difficulty: int,
                               location: Optional[Location] = None) -> None:
        """Ajoute les objectifs à une mission de hacking"""
        # Déterminer le domaine et le niveau de sécurité de la corporation
        corp_info = self.CORPORATIONS.get(corporation, {"domain": "technology", "security": SecurityLevel.MEDIUM})
        domain = corp_info["domain"]
        base_security = corp_info["security"]
        
        # Sélectionner les systèmes potentiels
        potential_systems = self.SYSTEMS.get(domain, ["server.main", "database.central"])
        
        # Créer une séquence d'objectifs basée sur le type de mission
        if mission_type == "data_extraction":
            # 1. Trouver un point d'accès
            mission.add_hacking_objective(
                title="Trouver un point d'accès",
                description="Identifiez un point d'entrée vulnérable dans le réseau de " + corporation,
                target_system=f"{corporation.lower()}.access.point",
                security_level=SecurityLevel(max(0, base_security.value - 2)),
                puzzle_type=HackingPuzzleType.NETWORK_REROUTING,
                location_id=location.id if location else None
            )
            
            # 2. Contourner les défenses
            mission.add_hacking_objective(
                title="Contourner le pare-feu",
                description="Désactivez ou contournez le pare-feu principal pour accéder au réseau interne",
                target_system=f"{corporation.lower()}.firewall",
                security_level=SecurityLevel(min(7, base_security.value)),
                puzzle_type=HackingPuzzleType.FIREWALL_BYPASS,
                location_id=location.id if location else None
            )
            
            # 3. Trouver les données
            target_system = random.choice(potential_systems)
            mission.add_hacking_objective(
                title="Localiser les données cibles",
                description="Naviguez dans le système pour trouver l'emplacement exact des données recherchées",
                target_system=f"{corporation.lower()}.{target_system}",
                security_level=base_security,
                puzzle_type=HackingPuzzleType.SEQUENCE_MATCHING,
                location_id=location.id if location else None
            )
            
            # 4. Extraire les données
            mission.add_hacking_objective(
                title="Extraire les données",
                description="Téléchargez les données cibles tout en évitant la détection",
                target_system=f"{corporation.lower()}.{target_system}.download",
                security_level=SecurityLevel(min(7, base_security.value + 1)),
                puzzle_type=HackingPuzzleType.BUFFER_OVERFLOW,
                location_id=location.id if location else None
            )
            
            # 5. Effacer les traces
            mission.add_hacking_objective(
                title="Effacer vos traces",
                description="Supprimez tous les journaux d'activité liés à votre intrusion",
                target_system=f"{corporation.lower()}.logs",
                security_level=SecurityLevel(min(7, base_security.value)),
                puzzle_type=HackingPuzzleType.MEMORY_MANIPULATION,
                location_id=location.id if location else None
            )
            
        elif mission_type == "system_breach":
            # 1. Scanner les vulnérabilités
            mission.add_hacking_objective(
                title="Scanner les vulnérabilités",
                description="Identifiez les failles dans les systèmes de " + corporation,
                target_system=f"{corporation.lower()}.external.scan",
                security_level=SecurityLevel(max(0, base_security.value - 1)),
                puzzle_type=HackingPuzzleType.SEQUENCE_MATCHING,
                location_id=location.id if location else None
            )
            
            # 2. Exploiter une vulnérabilité
            mission.add_hacking_objective(
                title="Exploiter une vulnérabilité",
                description="Utilisez une faille identifiée pour pénétrer dans le système",
                target_system=f"{corporation.lower()}.vulnerability",
                security_level=base_security,
                puzzle_type=HackingPuzzleType.BUFFER_OVERFLOW,
                location_id=location.id if location else None
            )
            
            # 3. Élever les privilèges
            mission.add_hacking_objective(
                title="Élever vos privilèges",
                description="Obtenez des droits administrateur sur le système",
                target_system=f"{corporation.lower()}.admin.access",
                security_level=SecurityLevel(min(7, base_security.value + 1)),
                puzzle_type=HackingPuzzleType.PASSWORD_BRUTEFORCE,
                location_id=location.id if location else None
            )
            
            # 4. Installer une porte dérobée
            mission.add_hacking_objective(
                title="Installer une porte dérobée",
                description="Implantez un accès permanent et discret dans le système",
                target_system=f"{corporation.lower()}.backdoor.install",
                security_level=SecurityLevel(min(7, base_security.value + 2)),
                puzzle_type=HackingPuzzleType.CODE_INJECTION,
                location_id=location.id if location else None
            )
        
        elif mission_type == "sabotage":
            # Objectifs spécifiques au sabotage
            target_system = random.choice(potential_systems)
            
            # 1. Infiltrer le réseau
            mission.add_hacking_objective(
                title="Infiltrer le réseau",
                description="Pénétrez discrètement dans le réseau de " + corporation,
                target_system=f"{corporation.lower()}.network",
                security_level=base_security,
                puzzle_type=HackingPuzzleType.NETWORK_REROUTING,
                location_id=location.id if location else None
            )
            
            # 2. Identifier les systèmes critiques
            mission.add_hacking_objective(
                title="Identifier les systèmes critiques",
                description="Localisez les systèmes vitaux dont la perturbation aura le plus d'impact",
                target_system=f"{corporation.lower()}.systems.scan",
                security_level=SecurityLevel(max(0, base_security.value - 1)),
                puzzle_type=HackingPuzzleType.SEQUENCE_MATCHING,
                location_id=location.id if location else None
            )
            
            # 3. Modifier les paramètres système
            mission.add_hacking_objective(
                title="Modifier les paramètres système",
                description="Altérez les configurations pour causer des dysfonctionnements",
                target_system=f"{corporation.lower()}.{target_system}.config",
                security_level=SecurityLevel(min(7, base_security.value + 1)),
                puzzle_type=HackingPuzzleType.MEMORY_MANIPULATION,
                location_id=location.id if location else None
            )
            
            # 4. Implanter un virus
            mission.add_hacking_objective(
                title="Implanter un virus",
                description="Introduisez un malware sophistiqué dans le système principal",
                target_system=f"{corporation.lower()}.{target_system}.virus",
                security_level=SecurityLevel(min(7, base_security.value + 2)),
                puzzle_type=HackingPuzzleType.CODE_INJECTION,
                location_id=location.id if location else None
            )
        
        else:
            # Pour les autres types, créer des objectifs génériques
            # 1. Infiltration initiale
            mission.add_hacking_objective(
                title="Accès initial",
                description=f"Établissez un premier accès aux systèmes de {corporation}",
                target_system=f"{corporation.lower()}.entry",
                security_level=SecurityLevel(max(0, base_security.value - 1)),
                puzzle_type=random.choice([
                    HackingPuzzleType.PASSWORD_BRUTEFORCE, 
                    HackingPuzzleType.NETWORK_REROUTING
                ]),
                location_id=location.id if location else None
            )
            
            # 2. Objectif principal basé sur le type de mission
            target_system = random.choice(potential_systems)
            puzzle_type = random.choice([
                HackingPuzzleType.BUFFER_OVERFLOW,
                HackingPuzzleType.SEQUENCE_MATCHING,
                HackingPuzzleType.ENCRYPTION_BREAKING
            ])
            
            mission.add_hacking_objective(
                title=f"Pirater {target_system.replace('.', ' ')}",
                description=f"Accédez au système {target_system} pour accomplir l'objectif principal",
                target_system=f"{corporation.lower()}.{target_system}",
                security_level=base_security,
                puzzle_type=puzzle_type,
                location_id=location.id if location else None
            )
            
            # 3. Finaliser l'opération
            mission.add_hacking_objective(
                title="Finaliser l'opération",
                description="Terminez l'opération et sécurisez votre sortie du système",
                target_system=f"{corporation.lower()}.exit",
                security_level=SecurityLevel(max(0, base_security.value - 1)),
                puzzle_type=HackingPuzzleType.MEMORY_MANIPULATION,
                location_id=location.id if location else None
            )


# Exemple d'utilisation dans une mission
def create_sample_hacking_mission(game):
    """Crée une mission de hacking d'exemple"""
    generator = HackingMissionGenerator(game)
    mission = generator.generate_mission(difficulty=5, corporation="NeoTech")
    return mission
