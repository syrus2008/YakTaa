"""
Module pour la génération procédurale de missions dans YakTaa
"""

import logging
import random
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta

from yaktaa.missions.mission import Mission, MissionType, MissionDifficulty, Objective, ObjectiveType
from yaktaa.world.locations import Location, WorldMap
from yaktaa.characters.character import Character

logger = logging.getLogger("YakTaa.Missions.ProceduralGenerator")

class MissionTemplate:
    """Modèle pour la génération procédurale de missions"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 mission_type: MissionType,
                 objective_templates: List[Dict[str, Any]],
                 difficulty_range: Tuple[MissionDifficulty, MissionDifficulty],
                 required_locations: List[str] = None,
                 required_characters: List[str] = None,
                 reward_multipliers: Dict[str, float] = None):
        """Initialise un modèle de mission"""
        self.id = f"template_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.mission_type = mission_type
        self.objective_templates = objective_templates
        self.difficulty_range = difficulty_range
        self.required_locations = required_locations or []
        self.required_characters = required_characters or []
        self.reward_multipliers = reward_multipliers or {
            "credits": 1.0,
            "xp": 1.0,
            "reputation": 1.0
        }


class MissionGenerator:
    """Générateur procédural de missions"""
    
    def __init__(self, world_map: WorldMap, characters: Dict[str, Character]):
        """Initialise le générateur de missions"""
        self.world_map = world_map
        self.characters = characters
        self.templates: List[MissionTemplate] = []
        
        # Initialisation des templates de base
        self._init_templates()
        
        logger.info("Générateur de missions procédurales initialisé")
    
    def _init_templates(self) -> None:
        """Initialise les templates de missions de base"""
        # Template: Récupération de données
        data_retrieval = MissionTemplate(
            name="Récupération de données",
            description="Infiltrez un système pour récupérer des données sensibles.",
            mission_type=MissionType.CONTRACT,
            objective_templates=[
                {
                    "type": ObjectiveType.TRAVEL,
                    "description_template": "Se rendre à {location}",
                    "location_types": ["city", "district"]
                },
                {
                    "type": ObjectiveType.HACK,
                    "description_template": "Infiltrer le système de {target}",
                    "target_types": ["corporation", "government"]
                },
                {
                    "type": ObjectiveType.COLLECT,
                    "description_template": "Localiser et télécharger les données sur {subject}",
                    "subjects": ["projet secret", "transactions financières", "dossiers confidentiels"]
                },
                {
                    "type": ObjectiveType.HACK,
                    "description_template": "Effacer les traces de votre intrusion",
                    "optional": True
                }
            ],
            difficulty_range=(MissionDifficulty.EASY, MissionDifficulty.HARD)
        )
        
        # Template: Rencontre avec informateur
        informant_meeting = MissionTemplate(
            name="Rencontre avec informateur",
            description="Rencontrez un informateur qui détient des informations cruciales.",
            mission_type=MissionType.SIDE,
            objective_templates=[
                {
                    "type": ObjectiveType.TRAVEL,
                    "description_template": "Se rendre à {location}",
                    "location_types": ["city", "district", "special"]
                },
                {
                    "type": ObjectiveType.INVESTIGATE,
                    "description_template": "Localiser l'informateur dans {location}",
                    "location_types": ["district", "special"]
                },
                {
                    "type": ObjectiveType.TALK,
                    "description_template": "Rencontrer l'informateur",
                    "character_types": ["fixer", "hacker", "corporate"]
                },
                {
                    "type": ObjectiveType.PROTECT,
                    "description_template": "Protéger l'informateur des agents hostiles",
                    "optional": True
                }
            ],
            difficulty_range=(MissionDifficulty.TRIVIAL, MissionDifficulty.MEDIUM)
        )
        
        # Template: Piratage de réseau
        network_hack = MissionTemplate(
            name="Piratage de réseau",
            description="Infiltrez un réseau sécurisé pour y installer un backdoor.",
            mission_type=MissionType.CONTRACT,
            objective_templates=[
                {
                    "type": ObjectiveType.TRAVEL,
                    "description_template": "Se rendre à proximité du réseau cible à {location}",
                    "location_types": ["city", "corporation"]
                },
                {
                    "type": ObjectiveType.HACK,
                    "description_template": "Analyser les défenses du réseau",
                    "target_types": ["network", "security_system"]
                },
                {
                    "type": ObjectiveType.HACK,
                    "description_template": "Contourner le pare-feu",
                    "target_types": ["firewall", "security_layer"]
                },
                {
                    "type": ObjectiveType.INSTALL,
                    "description_template": "Installer un backdoor dans le système",
                    "target_types": ["server", "mainframe"]
                },
                {
                    "type": ObjectiveType.HACK,
                    "description_template": "Masquer vos traces",
                    "optional": True
                }
            ],
            difficulty_range=(MissionDifficulty.MEDIUM, MissionDifficulty.EXPERT)
        )
        
        # Ajout des templates
        self.templates.extend([data_retrieval, informant_meeting, network_hack])
    
    def generate_mission(self, template_id: Optional[str] = None, difficulty: Optional[MissionDifficulty] = None) -> Mission:
        """
        Génère une mission procédurale
        
        Args:
            template_id: ID du template à utiliser (None = aléatoire)
            difficulty: Difficulté souhaitée (None = aléatoire)
            
        Returns:
            Mission: Mission générée
        """
        # Sélection du template
        template = None
        if template_id:
            template = next((t for t in self.templates if t.id == template_id), None)
        
        if not template:
            template = random.choice(self.templates)
        
        # Sélection de la difficulté
        if not difficulty:
            min_diff, max_diff = template.difficulty_range
            difficulty_values = [d for d in MissionDifficulty if min_diff.value <= d.value <= max_diff.value]
            difficulty = random.choice(difficulty_values)
        
        # Génération du titre
        title_templates = [
            f"{template.name}: Opération {self._generate_code_name()}",
            f"Mission {template.name.lower()}",
            f"Contrat: {template.name}",
            f"Opération {self._generate_code_name()}"
        ]
        title = random.choice(title_templates)
        
        # Génération de la description
        description_templates = [
            f"{template.description} Cette mission requiert discrétion et compétence.",
            f"Une mission de {template.name.lower()}. {template.description}",
            f"{template.description} La réussite sera bien récompensée.",
            f"Mission classifiée: {template.description}"
        ]
        description = random.choice(description_templates)
        
        # Création de la mission
        mission = Mission(
            title=title,
            description=description,
            mission_type=template.mission_type,
            difficulty=difficulty
        )
        
        # Sélection des lieux et personnages
        available_locations = self._get_suitable_locations(template.required_locations)
        available_characters = self._get_suitable_characters(template.required_characters)
        
        # Génération des objectifs
        for obj_template in template.objective_templates:
            # Vérification si l'objectif est optionnel
            is_optional = obj_template.get("optional", False)
            
            # Si l'objectif est optionnel, on a une chance de ne pas l'inclure
            if is_optional and random.random() < 0.3:
                continue
            
            # Génération de la description de l'objectif
            description = self._generate_objective_description(obj_template, available_locations, available_characters)
            
            # Création de l'objectif
            objective = Objective(
                description=description,
                objective_type=obj_template["type"],
                optional=is_optional
            )
            
            # Ajout de l'objectif à la mission
            mission.add_objective(objective)
        
        # Calcul des récompenses en fonction de la difficulté et des multiplicateurs
        self._calculate_rewards(mission, template.reward_multipliers)
        
        logger.info(f"Mission procédurale générée: {mission.title} (ID: {mission.id})")
        return mission
    
    def _generate_code_name(self) -> str:
        """Génère un nom de code aléatoire pour une mission"""
        adjectives = ["Noir", "Silencieux", "Rapide", "Fantôme", "Cyber", "Digital", "Quantique", "Furtif", "Éclair", "Sombre"]
        nouns = ["Serpent", "Ombre", "Loup", "Phoenix", "Dragon", "Spectre", "Vautour", "Corbeau", "Tempête", "Écho"]
        
        return f"{random.choice(adjectives)} {random.choice(nouns)}"
    
    def _get_suitable_locations(self, required_types: List[str]) -> List[Location]:
        """Récupère les lieux adaptés aux types requis"""
        if not required_types:
            return list(self.world_map.locations.values())
        
        return [loc for loc in self.world_map.locations.values() 
                if hasattr(loc, 'location_type') and loc.location_type in required_types]
    
    def _get_suitable_characters(self, required_types: List[str]) -> List[Character]:
        """Récupère les personnages adaptés aux types requis"""
        if not required_types:
            return list(self.characters.values())
        
        return [char for char in self.characters.values() 
                if hasattr(char, 'character_type') and char.character_type in required_types]
    
    def _generate_objective_description(self, 
                                       obj_template: Dict[str, Any],
                                       available_locations: List[Location],
                                       available_characters: List[Character]) -> str:
        """Génère la description d'un objectif à partir du template"""
        description_template = obj_template["description_template"]
        
        # Remplacement des variables dans le template
        if "{location}" in description_template and available_locations:
            location = random.choice(available_locations)
            description_template = description_template.replace("{location}", location.name)
        
        if "{target}" in description_template:
            targets = ["Arasaka", "Militech", "NightCorp", "Kang Tao", "Gouvernement", "Mafia", "Yakuza"]
            description_template = description_template.replace("{target}", random.choice(targets))
        
        if "{subject}" in description_template and "subjects" in obj_template:
            description_template = description_template.replace("{subject}", random.choice(obj_template["subjects"]))
        
        if "{character}" in description_template and available_characters:
            character = random.choice(available_characters)
            description_template = description_template.replace("{character}", character.name)
        
        return description_template
    
    def _calculate_rewards(self, mission: Mission, multipliers: Dict[str, float]) -> None:
        """Calcule les récompenses de la mission en fonction de la difficulté et des multiplicateurs"""
        # Base de récompense selon la difficulté
        base_credits = 500 * mission.difficulty.value
        base_xp = 100 * mission.difficulty.value
        
        # Application des multiplicateurs
        mission.rewards["credits"] = int(base_credits * multipliers.get("credits", 1.0))
        mission.rewards["xp"] = int(base_xp * multipliers.get("xp", 1.0))
        
        # Récompenses de réputation
        factions = ["Netrunners", "Fixers", "Corporations", "Nomades", "Gangs"]
        primary_faction = random.choice(factions)
        opposing_faction = random.choice([f for f in factions if f != primary_faction])
        
        mission.rewards["reputation"] = {
            primary_faction: int(10 * mission.difficulty.value * multipliers.get("reputation", 1.0)),
            opposing_faction: int(-5 * mission.difficulty.value * multipliers.get("reputation", 1.0))
        }
        
        # Objets de récompense pour les missions plus difficiles
        if mission.difficulty.value >= MissionDifficulty.HARD.value:
            items = [
                {"id": "advanced_cyberdeck", "name": "Cyberdeck avancé", "rarity": "rare"},
                {"id": "encryption_key", "name": "Clé de chiffrement", "rarity": "uncommon"},
                {"id": "hacking_tool", "name": "Outil de hacking spécialisé", "rarity": "rare"},
                {"id": "access_codes", "name": "Codes d'accès", "rarity": "uncommon"}
            ]
            mission.rewards["items"] = [random.choice(items)]


# Fonction utilitaire pour générer un lot de missions
def generate_mission_batch(generator: MissionGenerator, count: int = 5) -> List[Mission]:
    """
    Génère un lot de missions procédurales
    
    Args:
        generator: Générateur de missions
        count: Nombre de missions à générer
        
    Returns:
        List[Mission]: Liste des missions générées
    """
    missions = []
    for _ in range(count):
        mission = generator.generate_mission()
        missions.append(mission)
    
    logger.info(f"Lot de {count} missions procédurales généré")
    return missions
