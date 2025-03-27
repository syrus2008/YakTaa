"""
Module pour la création d'un monde de test dans YakTaa
Ce module contient les données nécessaires pour créer un monde de test complet
avec des lieux, des connexions, des PNJ et des missions.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple

from yaktaa.world.locations import Location, WorldMap
from yaktaa.characters.character import Character, Attribute, Skill
from yaktaa.missions.mission import Mission, Objective, MissionType, MissionDifficulty, ObjectiveType
from yaktaa.missions.mission_manager import MissionManager

logger = logging.getLogger("YakTaa.World.TestWorld")

class TestWorldGenerator:
    """
    Classe pour générer un monde de test complet pour YakTaa
    """
    
    def __init__(self):
        """Initialise le générateur de monde de test"""
        self.world_map = WorldMap("Monde Cyberpunk")
        self.characters: Dict[str, Character] = {}
        
        logger.info("Générateur de monde de test initialisé")
    
    def generate(self) -> Tuple[WorldMap, Dict[str, Character]]:
        """Génère un monde de test complet"""
        self._create_locations()
        self._create_connections()
        self._create_characters()
        
        logger.info(f"Monde de test généré avec {len(self.world_map.locations)} lieux et {len(self.characters)} personnages")
        return self.world_map, self.characters
    
    def _create_locations(self):
        """Crée les lieux du monde de test"""
        # Grandes villes
        tokyo = Location(
            id="tokyo",
            name="Tokyo",
            description="Mégalopole cyberpunk, centre technologique mondial avec ses néons et ses gratte-ciels.",
            coordinates=(35.6895, 139.6917),
            security_level=4,
            population=15000000,
            services=["hacking", "commerce", "médical", "transport"],
            tags=["mégalopole", "technologie", "asie"]
        )
        
        neo_york = Location(
            id="neo_york",
            name="Neo-York",
            description="Anciennement New York, cette ville est devenue un centre financier et criminel après la montée des eaux.",
            coordinates=(40.7128, -74.0060),
            security_level=3,
            population=12000000,
            services=["commerce", "finance", "transport", "divertissement"],
            tags=["mégalopole", "finance", "amérique"]
        )
        
        berlin_2 = Location(
            id="berlin_2",
            name="Berlin-2",
            description="Reconstruite après la guerre des corporations, Berlin-2 est un havre pour les hackers et les rebelles.",
            coordinates=(52.5200, 13.4050),
            security_level=2,
            population=5000000,
            services=["hacking", "marché noir", "transport", "information"],
            tags=["europe", "rebelles", "underground"]
        )
        
        neo_shanghai = Location(
            id="neo_shanghai",
            name="Neo-Shanghai",
            description="Centre de production d'implants cybernétiques et de technologies avancées.",
            coordinates=(31.2304, 121.4737),
            security_level=5,
            population=18000000,
            services=["cybernétique", "commerce", "médical", "transport"],
            tags=["mégalopole", "technologie", "asie"]
        )
        
        # Quartiers de Tokyo
        shibuya = Location(
            id="shibuya",
            name="Shibuya",
            description="Quartier animé de Tokyo, connu pour ses écrans géants et sa vie nocturne.",
            coordinates=(35.6580, 139.7016),
            security_level=3,
            population=500000,
            services=["commerce", "divertissement", "information"],
            tags=["quartier", "tokyo", "divertissement"],
            parent_location_id="tokyo"
        )
        
        akihabara = Location(
            id="akihabara",
            name="Akihabara",
            description="Quartier électronique de Tokyo, paradis des hackers et des otakus.",
            coordinates=(35.6980, 139.7710),
            security_level=2,
            population=300000,
            services=["hacking", "commerce", "information"],
            tags=["quartier", "tokyo", "technologie"],
            parent_location_id="tokyo"
        )
        
        shinjuku = Location(
            id="shinjuku",
            name="Shinjuku",
            description="Centre administratif et commercial de Tokyo, dominé par les tours des corporations.",
            coordinates=(35.6938, 139.7034),
            security_level=5,
            population=800000,
            services=["finance", "commerce", "transport", "médical"],
            tags=["quartier", "tokyo", "corporations"],
            parent_location_id="tokyo"
        )
        
        # Zones spéciales
        darknet_hub = Location(
            id="darknet_hub",
            name="Hub du Darknet",
            description="Un lieu virtuel accessible uniquement via le réseau, point central du darknet mondial.",
            coordinates=(0, 0),  # Coordonnées virtuelles
            security_level=1,
            population=0,  # Lieu virtuel
            services=["hacking", "marché noir", "information"],
            tags=["virtuel", "darknet", "hacking"],
            is_virtual=True
        )
        
        orbital_station = Location(
            id="orbital_station",
            name="Station Orbitale Alpha",
            description="Station spatiale en orbite terrestre, réservée à l'élite et aux recherches de pointe.",
            coordinates=(0, 0),  # En orbite
            security_level=5,
            population=10000,
            services=["recherche", "médical", "luxe"],
            tags=["espace", "élite", "recherche"],
            is_special=True
        )
        
        wasteland = Location(
            id="wasteland",
            name="Terres Désolées",
            description="Ancien centre urbain dévasté par les guerres corporatives, maintenant habité par des marginaux.",
            coordinates=(36.1699, -115.1398),  # Ancien Las Vegas
            security_level=1,
            population=500000,
            services=["marché noir", "contrebande"],
            tags=["ruines", "danger", "amérique"],
            is_dangerous=True
        )
        
        # Ajouter tous les lieux à la carte
        locations = [
            tokyo, neo_york, berlin_2, neo_shanghai,
            shibuya, akihabara, shinjuku,
            darknet_hub, orbital_station, wasteland
        ]
        
        for location in locations:
            self.world_map.add_location(location)
            logger.info(f"Lieu ajouté : {location.name}")
    
    def _create_connections(self):
        """Crée les connexions entre les lieux"""
        # Connexions entre les grandes villes
        self.world_map.add_connection("tokyo", "neo_york", "Vol international", 14, 10000)
        self.world_map.add_connection("tokyo", "berlin_2", "Vol international", 12, 9000)
        self.world_map.add_connection("tokyo", "neo_shanghai", "Train à grande vitesse", 5, 3000)
        
        self.world_map.add_connection("neo_york", "berlin_2", "Vol international", 8, 7000)
        self.world_map.add_connection("neo_york", "wasteland", "Vol intérieur", 5, 2000)
        
        self.world_map.add_connection("berlin_2", "neo_shanghai", "Vol international", 10, 8000)
        
        # Connexions entre Tokyo et ses quartiers
        self.world_map.add_connection("tokyo", "shibuya", "Métro", 0.1, 50)
        self.world_map.add_connection("tokyo", "akihabara", "Métro", 0.2, 50)
        self.world_map.add_connection("tokyo", "shinjuku", "Métro", 0.15, 50)
        
        self.world_map.add_connection("shibuya", "akihabara", "Métro", 0.3, 100)
        self.world_map.add_connection("shibuya", "shinjuku", "Métro", 0.2, 100)
        self.world_map.add_connection("akihabara", "shinjuku", "Métro", 0.25, 100)
        
        # Connexions spéciales
        self.world_map.add_connection("darknet_hub", "tokyo", "Connexion réseau", 0, 0, requires_hacking=True)
        self.world_map.add_connection("darknet_hub", "neo_york", "Connexion réseau", 0, 0, requires_hacking=True)
        self.world_map.add_connection("darknet_hub", "berlin_2", "Connexion réseau", 0, 0, requires_hacking=True)
        self.world_map.add_connection("darknet_hub", "neo_shanghai", "Connexion réseau", 0, 0, requires_hacking=True)
        
        self.world_map.add_connection("orbital_station", "tokyo", "Navette spatiale", 3, 50000, requires_special_access=True)
        self.world_map.add_connection("orbital_station", "neo_york", "Navette spatiale", 3, 50000, requires_special_access=True)
        
        logger.info(f"Connexions créées : {len(self.world_map.connections)}")
    
    def _create_characters(self):
        """Crée les personnages du monde de test"""
        # Fixers (donneurs de missions)
        raven = Character("Raven", "fixer")
        raven.location_id = "shibuya"
        raven.description = "Un fixer mystérieux avec des connexions dans tout Tokyo. Spécialisé dans les missions d'infiltration."
        raven.add_attribute("intelligence", 8)
        raven.add_attribute("charisme", 7)
        raven.improve_skill("négociation", 500)
        raven.improve_skill("réseau de contacts", 800)
        self.characters["raven"] = raven
        
        spider = Character("Spider", "fixer")
        spider.location_id = "berlin_2"
        spider.description = "Une hackeuse légendaire reconvertie en fixeuse. Propose les meilleures missions de hacking."
        spider.add_attribute("intelligence", 9)
        spider.add_attribute("technique", 8)
        spider.improve_skill("hacking", 1000)
        spider.improve_skill("cryptographie", 900)
        self.characters["spider"] = spider
        
        # Marchands
        chrome_doc = Character("Chrome Doc", "ripper_doc")
        chrome_doc.location_id = "shinjuku"
        chrome_doc.description = "Un médecin spécialisé dans les implants cybernétiques haut de gamme."
        chrome_doc.add_attribute("technique", 9)
        chrome_doc.add_attribute("intelligence", 7)
        chrome_doc.improve_skill("médecine", 1000)
        chrome_doc.improve_skill("cybernétique", 1200)
        self.characters["chrome_doc"] = chrome_doc
        
        black_market = Character("Shadow", "marchand")
        black_market.location_id = "akihabara"
        black_market.description = "Un marchand du marché noir qui peut vous procurer n'importe quoi... pour le bon prix."
        black_market.add_attribute("charisme", 8)
        black_market.add_attribute("chance", 6)
        black_market.improve_skill("négociation", 900)
        black_market.improve_skill("connaissance de la rue", 800)
        self.characters["black_market"] = black_market
        
        # Informateurs
        info_broker = Character("DataHawk", "informateur")
        info_broker.location_id = "darknet_hub"
        info_broker.description = "Un courtier en information qui connaît tous les secrets du réseau."
        info_broker.add_attribute("intelligence", 10)
        info_broker.add_attribute("perception", 9)
        info_broker.improve_skill("recherche d'information", 1500)
        info_broker.improve_skill("analyse de données", 1300)
        self.characters["info_broker"] = info_broker
        
        street_ear = Character("Whisper", "informateur")
        street_ear.location_id = "shibuya"
        street_ear.description = "Une informatrice qui entend tout ce qui se passe dans les rues de Tokyo."
        street_ear.add_attribute("perception", 8)
        street_ear.add_attribute("charisme", 7)
        street_ear.improve_skill("discrétion", 800)
        street_ear.improve_skill("connaissance de la rue", 1000)
        self.characters["street_ear"] = street_ear
        
        # Antagonistes
        corp_exec = Character("Tanaka", "corporate")
        corp_exec.location_id = "shinjuku"
        corp_exec.description = "Un cadre impitoyable d'Arasaka Corporation, prêt à tout pour gravir les échelons."
        corp_exec.add_attribute("intelligence", 8)
        corp_exec.add_attribute("charisme", 7)
        corp_exec.add_attribute("volonté", 9)
        corp_exec.improve_skill("intimidation", 900)
        corp_exec.improve_skill("négociation", 800)
        self.characters["corp_exec"] = corp_exec
        
        gang_leader = Character("Viper", "gang_leader")
        gang_leader.location_id = "wasteland"
        gang_leader.description = "Chef d'un gang cyberpunk redouté dans les Terres Désolées."
        gang_leader.add_attribute("force", 8)
        gang_leader.add_attribute("charisme", 7)
        gang_leader.add_attribute("endurance", 9)
        gang_leader.improve_skill("combat", 1000)
        gang_leader.improve_skill("intimidation", 900)
        self.characters["gang_leader"] = gang_leader
        
        logger.info(f"Personnages créés : {len(self.characters)}")


def create_test_world() -> Tuple[WorldMap, Dict[str, Character]]:
    """
    Crée un monde de test complet pour le jeu
    Retourne la carte du monde et les personnages
    """
    generator = TestWorldGenerator()
    return generator.generate()


def setup_test_missions(mission_manager: MissionManager, world_map: WorldMap, characters: Dict[str, Character]):
    """
    Configure des missions de test dans le gestionnaire de missions
    """
    # Mission principale
    main_mission = Mission(
        title="Le Projet Lazarus",
        description="Des rumeurs circulent à propos d'un projet secret d'Arasaka appelé 'Lazarus'. Découvrez ce qu'il cache.",
        mission_type=MissionType.MAIN,
        difficulty=MissionDifficulty.MEDIUM,
        location_id="tokyo",
        giver_id="raven",
        faction="NetRunners"
    )
    
    main_mission.add_objective(Objective(
        description="Rencontrer Raven à Shibuya",
        objective_type=ObjectiveType.TALK,
        target_id="raven"
    ))
    
    main_mission.add_objective(Objective(
        description="Infiltrer le réseau d'Arasaka",
        objective_type=ObjectiveType.HACK,
        target_id="arasaka_network"
    ))
    
    main_mission.add_objective(Objective(
        description="Localiser les fichiers du Projet Lazarus",
        objective_type=ObjectiveType.INVESTIGATE,
        target_id="lazarus_files"
    ))
    
    main_mission.add_objective(Objective(
        description="Télécharger les données",
        objective_type=ObjectiveType.COLLECT,
        target_id="lazarus_data"
    ))
    
    main_mission.add_objective(Objective(
        description="Échapper aux agents d'Arasaka",
        objective_type=ObjectiveType.TRAVEL,
        target_id="akihabara"
    ))
    
    main_mission.add_objective(Objective(
        description="Analyser les données avec DataHawk",
        objective_type=ObjectiveType.TALK,
        target_id="info_broker"
    ))
    
    # Mission secondaire - Hacking
    hack_mission = Mission(
        title="Brèche dans la matrice",
        description="Un système de sécurité avancé protège des données précieuses. Hackez-le pour prouver vos compétences.",
        mission_type=MissionType.SIDE,
        difficulty=MissionDifficulty.HARD,
        location_id="darknet_hub",
        giver_id="spider",
        faction="NetRunners"
    )
    
    hack_mission.add_objective(Objective(
        description="Accéder au Hub du Darknet",
        objective_type=ObjectiveType.TRAVEL,
        target_id="darknet_hub"
    ))
    
    hack_mission.add_objective(Objective(
        description="Contacter Spider",
        objective_type=ObjectiveType.TALK,
        target_id="spider"
    ))
    
    hack_mission.add_objective(Objective(
        description="Développer un outil de déchiffrement",
        objective_type=ObjectiveType.CRAFT,
        target_id="decrypt_tool"
    ))
    
    hack_mission.add_objective(Objective(
        description="Pénétrer le système de sécurité",
        objective_type=ObjectiveType.HACK,
        target_id="security_system"
    ))
    
    hack_mission.add_objective(Objective(
        description="Extraire les données protégées",
        objective_type=ObjectiveType.COLLECT,
        target_id="protected_data"
    ))
    
    # Mission secondaire - Combat
    combat_mission = Mission(
        title="Dette de sang",
        description="Un gang des Terres Désolées a kidnappé un ami. Infiltrez leur territoire et libérez-le.",
        mission_type=MissionType.CONTRACT,
        difficulty=MissionDifficulty.HARD,
        location_id="wasteland",
        faction="Fixers"
    )
    
    combat_mission.add_objective(Objective(
        description="Se rendre dans les Terres Désolées",
        objective_type=ObjectiveType.TRAVEL,
        target_id="wasteland"
    ))
    
    combat_mission.add_objective(Objective(
        description="Localiser le repaire du gang",
        objective_type=ObjectiveType.INVESTIGATE,
        target_id="gang_hideout"
    ))
    
    combat_mission.add_objective(Objective(
        description="Infiltrer le repaire",
        objective_type=ObjectiveType.TRAVEL,
        target_id="gang_hideout"
    ))
    
    combat_mission.add_objective(Objective(
        description="Éliminer les gardes",
        objective_type=ObjectiveType.ELIMINATE,
        target_id="gang_guards",
        quantity=5
    ))
    
    combat_mission.add_objective(Objective(
        description="Libérer le prisonnier",
        objective_type=ObjectiveType.TALK,
        target_id="prisoner"
    ))
    
    combat_mission.add_objective(Objective(
        description="S'échapper du repaire",
        objective_type=ObjectiveType.TRAVEL,
        target_id="wasteland"
    ))
    
    # Mission tutoriel
    tutorial_mission = Mission(
        title="Premiers pas dans le réseau",
        description="Apprenez les bases du hacking et de la navigation dans le réseau.",
        mission_type=MissionType.TUTORIAL,
        difficulty=MissionDifficulty.TRIVIAL,
        location_id="tokyo"
    )
    
    tutorial_mission.add_objective(Objective(
        description="Se connecter à un réseau public",
        objective_type=ObjectiveType.HACK,
        target_id="public_network"
    ))
    
    tutorial_mission.add_objective(Objective(
        description="Exécuter une commande de scan",
        objective_type=ObjectiveType.CUSTOM,
        target_id="scan_command"
    ))
    
    tutorial_mission.add_objective(Objective(
        description="Télécharger un fichier de test",
        objective_type=ObjectiveType.COLLECT,
        target_id="test_file"
    ))
    
    # Ajouter les missions au gestionnaire
    mission_manager.add_mission(main_mission)
    mission_manager.add_mission(hack_mission)
    mission_manager.add_mission(combat_mission)
    mission_manager.add_mission(tutorial_mission)
    
    logger.info(f"Missions de test configurées : {len(mission_manager.available_missions)}")
