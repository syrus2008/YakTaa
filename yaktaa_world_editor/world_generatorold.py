"""
Module de génération aléatoire de mondes pour YakTaa
Ce module permet de créer des mondes complets avec lieux, connexions, personnages, etc.
"""

import random
import string
import uuid
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import ipaddress

from database import get_database
from shop_item_generator import ShopItemGenerator  # Import pour la génération d'objets de boutique

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator")

# Constantes pour la génération
CITY_PREFIXES = ["Neo-", "Cyber-", "Mega-", "Tech-", "Digi-", "Synth-", "Quantum-", "Hyper-"]
CITY_NAMES = ["Tokyo", "Shanghai", "New York", "Berlin", "London", "Paris", "Moscow", "Sydney", 
              "Seoul", "Mumbai", "Cairo", "Rio", "Lagos", "Singapore", "Dubai", "Bangkok"]

DISTRICT_TYPES = ["Financial", "Industrial", "Residential", "Entertainment", "Commercial", 
                 "Research", "Military", "Slums", "Underground", "Port", "Corporate"]

BUILDING_TYPES = [
    "Corporate HQ", "Apartment Complex", "Shopping Mall", "Research Lab", 
    "Data Center", "Hospital", "Police Station", "Nightclub", "Restaurant",
    "Hotel", "Factory", "Warehouse", "Government Building", "School", "University",
    "Military Base"
]

DEVICE_TYPES = [
    "Desktop PC", "Laptop", "Smartphone", "Tablet", "Server", 
    "Security System", "Smart Device", "Terminal", "ATM", "Router"
]

OS_TYPES = [
    "Windows 11", "Windows 10", "Linux Debian", "Linux Ubuntu", "Linux Kali",
    "macOS", "Android", "iOS", "Custom OS", "Legacy System"
]

# Nouvelles constantes pour les réseaux et hacking
NETWORK_TYPES = [
    "WiFi", "LAN", "WAN", "VPN", "IoT", "Corporate", "Secured", "Public"
]

SECURITY_LEVELS = [
    "WEP", "WPA", "WPA2", "WPA3", "Enterprise", "None", "Custom"
]

ENCRYPTION_TYPES = [
    "None", "WEP", "TKIP", "AES-128", "AES-256", "Custom", "Military-Grade"
]

HACKING_PUZZLE_TYPES = [
    "PasswordBruteforce", "BufferOverflow", "SequenceMatching", 
    "NetworkRerouting", "BasicTerminal", "CodeInjection", "FirewallBypass"
]

HACKING_PUZZLE_DIFFICULTIES = [
    "Easy", "Medium", "Hard", "Expert", "Master"
]

FACTION_NAMES = ["NetRunners", "Corporate Security", "Street Gangs", "Hacktivists", 
                "Black Market", "Government Agents", "Mercenaries", "AI Collective", 
                "Resistance", "Cyber Cultists", "Tech Nomads", "Data Pirates"]

CHARACTER_ROLES = ["Hacker", "Corporate Executive", "Street Vendor", "Mercenary", "Doctor", 
                  "Engineer", "Journalist", "Smuggler", "Police Officer", "Bartender", 
                  "Fixer", "Information Broker", "Cyber Surgeon", "Tech Dealer", "Assassin"]

CHARACTER_PROFESSIONS = ["Hacker", "Security Specialist", "Programmer", "Engineer", "Corporate Executive", 
                         "Government Agent", "Police Officer", "Mercenary", "Smuggler", "Fixer", 
                         "Information Broker", "Journalist", "Doctor", "Bartender", "Street Vendor"]

FILE_TYPES = ["text", "document", "spreadsheet", "image", "audio", "video", 
             "executable", "archive", "database", "script", "log", "config"]

MISSION_TYPES = ["Hacking", "Retrieval", "Assassination", "Protection", "Infiltration", 
                "Escort", "Sabotage", "Investigation", "Delivery", "Heist", "Rescue"]

MISSION_DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert", "Legendary"]

OBJECTIVE_TYPES = ["Hack", "Retrieve", "Eliminate", "Protect", "Infiltrate", 
                  "Escort", "Sabotage", "Investigate", "Deliver", "Steal", "Rescue"]

STORY_ELEMENT_TYPES = ["Background", "Main Plot", "Side Plot", "Character Story", 
                      "Location History", "World Event", "Lore", "Faction Conflict"]

DIFFICULTY_LEVELS = [
    "Very Easy", "Easy", "Medium", "Hard", "Very Hard"
]

# Constantes pour les hardware et objets
HARDWARE_TYPES = [
    "CPU", "RAM", "GPU", "Motherboard", "HDD", "SSD", "Network Card", 
    "Cooling System", "Power Supply", "USB Drive", "External HDD",
    "Router", "Bluetooth Adapter", "WiFi Antenna", "Raspberry Pi"
]

HARDWARE_QUALITIES = [
    "Broken", "Poor", "Standard", "High-End", "Military-Grade", "Prototype", "Custom"
]

HARDWARE_RARITIES = [
    "Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"
]

CONSUMABLE_TYPES = [
    "Data Chip", "Neural Booster", "Code Fragment", "Crypto Key", 
    "Access Card", "Security Token", "Firewall Bypass", "Signal Jammer",
    "Decryption Tool", "Memory Cleaner", "Battery Pack"
]

# Constantes pour les boutiques
SHOP_TYPES = [
    "hardware", "software", "black_market", "consumables", 
    "weapons", "implants", "general", "electronics", 
    "digital_services", "datachips", "cybernetics"
]

SHOP_NAME_PREFIXES = [
    "Neo", "Cyber", "Digital", "Tech", "Quantum", "Synth", "Hyper", 
    "Mega", "Nano", "Net", "Data", "Pulse", "Virtual", "Chrome", "Holo"
]

SHOP_NAME_SUFFIXES = [
    "Shop", "Mart", "Market", "Store", "Hub", "Center", "Emporium", 
    "Outlet", "Depot", "Exchange", "Haven", "Corner", "Bazaar", "Bay"
]

SHOP_BRANDS = [
    "NeoCorp", "CyberTech", "QuantumByte", "SynthWare", "ChromeLogic", 
    "DataPulse", "NanoSystems", "VirtualEdge", "MegaByte", "NetDynamics", 
    "HyperLink", "DigiForge", "TechNexus", "PulseSoft", "ByteHaven"
]

class WorldGenerator:
    """
    Classe pour générer aléatoirement des mondes complets pour YakTaa
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialise le générateur de monde
        
        Args:
            db_path: Chemin vers la base de données (optionnel)
        """
        self.db_path = db_path
        self.random = random.Random()  # Pour permettre de définir une seed
        
        logger.info("Générateur de monde initialisé")
    
    def set_seed(self, seed: Optional[int] = None) -> int:
        """
        Définit une seed pour la génération aléatoire
        
        Args:
            seed: Seed à utiliser (si None, utilise une seed aléatoire)
            
        Returns:
            La seed utilisée
        """
        if seed is None:
            seed = random.randint(1, 1000000)
        
        self.random.seed(seed)
        logger.info(f"Seed définie: {seed}")
        return seed
    
    def generate_world(self, name: Optional[str] = None, complexity: int = 3, 
                      author: str = "YakTaa Generator", seed: Optional[int] = None) -> str:
        """
        Génère un monde complet avec lieux, connexions, personnages, etc.
        
        Args:
            name: Nom du monde (si None, génère un nom aléatoire)
            complexity: Niveau de complexité du monde (1-5)
            author: Auteur du monde
            seed: Seed pour la génération aléatoire
            
        Returns:
            ID du monde généré
        """
        seed = self.set_seed(seed)
        logger.info(f"Génération d'un nouveau monde (seed: {seed}, complexité: {complexity})")
        
        # Obtenir la base de données
        db = get_database(self.db_path)
        
        # Générer un nom si non fourni
        if name is None:
            name = self._generate_world_name()
        
        # Insérer le monde dans la base de données
        world_id = str(uuid.uuid4())
        cursor = db.conn.cursor()
        cursor.execute('''
        INSERT INTO worlds (id, name, description, author, version, is_active, metadata, complexity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            world_id, name, f"Un monde généré automatiquement avec complexité {complexity}",
            author, "1.0", 1, json.dumps({"seed": seed}), complexity
        ))
        db.conn.commit()
        
        # Générer les différents éléments du monde
        try:
            # Définir les quantités en fonction de la complexité
            num_cities = max(1, min(8, complexity + 1))
            num_districts_per_city = max(1, min(6, complexity + 1))
            num_special_locations = max(0, min(5, complexity - 1))
            num_devices = max(10, min(100, complexity * 25))
            num_characters = max(5, min(50, complexity * 15))
            num_missions = max(3, min(20, complexity * 5))
            num_story_elements = max(1, min(10, complexity * 3))
            
            num_hardware_items = max(10, min(50, complexity * 10))
            num_consumable_items = max(10, min(50, complexity * 10))
            
            # Générer les villes
            logger.info("Génération des villes...")
            city_ids = self._generate_cities(db, world_id, num_cities)
            
            # Générer les districts
            logger.info("Génération des districts...")
            district_ids = self._generate_districts(db, world_id, city_ids, num_districts_per_city)
            
            # Générer les lieux spéciaux
            special_location_ids = []
            if num_special_locations > 0:
                logger.info("Génération des lieux spéciaux...")
                special_location_ids = self._generate_special_locations(db, world_id, num_special_locations)
            
            # Combiner tous les lieux
            all_location_ids = city_ids + district_ids + special_location_ids
            
            # Générer les connexions entre lieux
            logger.info("Génération des connexions...")
            self._generate_connections(db, world_id, all_location_ids)
            
            # Générer les bâtiments
            logger.info("Génération des bâtiments...")
            building_ids = self._generate_buildings(db, world_id, all_location_ids)
            
            # Générer les personnages
            logger.info("Génération des personnages...")
            character_ids = self._generate_characters(db, world_id, all_location_ids, num_characters)
            
            # Générer les appareils électroniques
            logger.info("Génération des appareils...")
            device_ids = self._generate_devices(db, world_id, all_location_ids, character_ids, num_devices)
            
            # Générer les réseaux
            logger.info("Génération des réseaux...")
            network_ids = self._generate_networks(db, world_id, building_ids)
            
            # Générer les puzzles de hacking
            logger.info("Génération des puzzles de hacking...")
            puzzle_ids = self._generate_hacking_puzzles(db, world_id, device_ids, network_ids)
            
            # Générer les fichiers
            logger.info("Génération des fichiers...")
            file_ids = self._generate_files(db, world_id, device_ids)
            
            # Générer les missions
            logger.info("Génération des missions...")
            mission_ids = self._generate_missions(db, world_id, all_location_ids, character_ids, num_missions)
            
            # Générer les éléments d'histoire
            if num_story_elements > 0:
                logger.info("Génération des éléments d'histoire...")
                self._generate_story_elements(db, world_id, all_location_ids, character_ids, mission_ids, num_story_elements)
            
            # Générer les objets hardware
            logger.info("Génération des objets hardware...")
            hardware_ids = self._generate_hardware_items(db, world_id, device_ids, building_ids, character_ids, num_hardware_items)
            
            # Générer les objets consommables
            logger.info("Génération des objets consommables...")
            consumable_ids = self._generate_consumable_items(db, world_id, device_ids, building_ids, character_ids, num_consumable_items)
            
            # Générer les boutiques
            logger.info("Génération des boutiques...")
            shop_ids = self._generate_shops(db, world_id, all_location_ids, building_ids, 10)
            
            db.conn.commit()
            logger.info(f"Monde '{name}' (ID: {world_id}) généré avec succès")
            
            return world_id
            
        except Exception as e:
            db.conn.rollback()
            logger.error(f"Erreur lors de la génération du monde: {str(e)}")
            raise
    
    def _generate_world_name(self) -> str:
        """Génère un nom aléatoire pour le monde"""
        adjectives = ["Cyber", "Digital", "Neon", "Shadow", "Chrome", "Quantum", "Synthetic", "Virtual"]
        nouns = ["Realm", "Nexus", "Matrix", "Grid", "Domain", "Sphere", "Network", "Pulse"]
        
        return f"{self.random.choice(adjectives)} {self.random.choice(nouns)}"
    
    def _generate_cities(self, db, world_id: str, num_cities: int) -> List[str]:
        """
        Génère des villes pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            num_cities: Nombre de villes à générer
            
        Returns:
            Liste des IDs des villes générées
        """
        city_ids = []
        
        # Mélanger les noms de villes pour éviter les doublons
        city_names = self.random.sample(CITY_NAMES, min(len(CITY_NAMES), num_cities))
        
        for i in range(num_cities):
            city_id = str(uuid.uuid4())
            
            # Générer un nom unique
            if i < len(city_names):
                base_name = city_names[i]
            else:
                # Si on a épuisé les noms prédéfinis, générer un nom aléatoire
                base_name = ''.join(self.random.choice(string.ascii_uppercase) for _ in range(5))
            
            # 50% de chance d'ajouter un préfixe
            if self.random.random() < 0.5:
                name = f"{self.random.choice(CITY_PREFIXES)}{base_name}"
            else:
                name = base_name
            
            # Générer des coordonnées aléatoires (latitude entre -90 et 90, longitude entre -180 et 180)
            lat = self.random.uniform(-90, 90)
            lon = self.random.uniform(-180, 180)
            coordinates = (lat, lon)
            
            # Générer une population aléatoire (entre 100,000 et 20 millions)
            population = self.random.randint(100000, 20000000)
            
            # Générer un niveau de sécurité aléatoire (1-5)
            security_level = self.random.randint(1, 5)
            
            # Générer des services disponibles
            available_services = ["commerce", "transport"]
            optional_services = ["hacking", "médical", "finance", "divertissement", "information", "marché noir"]
            num_optional = self.random.randint(0, len(optional_services))
            services = available_services + self.random.sample(optional_services, num_optional)
            
            # Tags
            tags = ["ville"]
            if population > 10000000:
                tags.append("mégalopole")
            
            if security_level >= 4:
                tags.append("haute sécurité")
            elif security_level <= 2:
                tags.append("zone dangereuse")
            
            # Description
            descriptions = [
                f"{name} est une ville {self.random.choice(['animée', 'grouillante', 'imposante', 'tentaculaire'])} avec une population de {population:,} habitants.",
                f"Connue pour {self.random.choice(['ses gratte-ciels vertigineux', 'ses marchés animés', 'sa technologie de pointe', 'son architecture unique'])}.",
                f"Le niveau de sécurité y est {['minimal', 'faible', 'modéré', 'élevé', 'maximal'][security_level-1]}.",
                f"On y trouve {', '.join(services[:-1]) + ' et ' + services[-1] if len(services) > 1 else services[0]}."
            ]
            description = " ".join(descriptions)
            
            # Insérer la ville dans la base de données
            cursor = db.conn.cursor()
            cursor.execute('''
            INSERT INTO locations (id, world_id, name, description, coordinates, security_level, 
                                  population, services, tags, is_virtual, is_special, is_dangerous, location_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                city_id, world_id, name, description, json.dumps(coordinates), security_level,
                population, json.dumps(services), json.dumps(tags), 0, 0, 1 if security_level <= 2 else 0, "city"
            ))
            
            city_ids.append(city_id)
            logger.debug(f"Ville générée: {name} (ID: {city_id})")
        
        db.conn.commit()
        return city_ids
    
    def _generate_districts(self, db, world_id: str, city_ids: List[str], num_districts_per_city: int) -> List[str]:
        """
        Génère des districts pour chaque ville
        
        Args:
            db: Base de données
            world_id: ID du monde
            city_ids: Liste des IDs des villes
            num_districts_per_city: Nombre de districts à générer par ville
            
        Returns:
            Liste des IDs des districts générés
        """
        district_ids = []
        
        for city_id in city_ids:
            # Récupérer les informations de la ville
            cursor = db.conn.cursor()
            cursor.execute("SELECT name, coordinates FROM locations WHERE id = ?", (city_id,))
            city_data = cursor.fetchone()
            
            if not city_data:
                continue
                
            city_name = city_data["name"]
            city_coords = json.loads(city_data["coordinates"])
            
            # Générer des districts pour cette ville
            district_types = self.random.sample(DISTRICT_TYPES, min(len(DISTRICT_TYPES), num_districts_per_city))
            
            for district_type in district_types:
                district_id = str(uuid.uuid4())
                
                # Générer un nom pour le district
                name = f"{district_type} District"
                if self.random.random() < 0.3:
                    # Parfois, utiliser un nom plus créatif
                    if district_type == "Financial":
                        name = f"Wall Street {self.random.randint(2, 5)}"
                    elif district_type == "Entertainment":
                        name = f"Neon Valley"
                    elif district_type == "Slums":
                        name = f"The Pit"
                    elif district_type == "Underground":
                        name = f"Subterranea"
                    elif district_type == "Corporate":
                        name = f"Corp Row"
                
                # Générer des coordonnées proches de la ville
                lat_offset = self.random.uniform(-0.05, 0.05)
                lon_offset = self.random.uniform(-0.05, 0.05)
                district_coords = (city_coords[0] + lat_offset, city_coords[1] + lon_offset)
                
                # Générer une population (10-30% de la ville)
                cursor.execute("SELECT population FROM locations WHERE id = ?", (city_id,))
                city_pop = cursor.fetchone()["population"]
                district_population = int(city_pop * self.random.uniform(0.1, 0.3))
                
                # Niveau de sécurité basé sur le type de district
                security_mapping = {
                    "Financial": (4, 5),
                    "Corporate": (4, 5),
                    "Military": (5, 5),
                    "Research": (3, 5),
                    "Commercial": (3, 4),
                    "Entertainment": (2, 4),
                    "Residential": (2, 4),
                    "Industrial": (2, 3),
                    "Port": (2, 3),
                    "Underground": (1, 2),
                    "Slums": (1, 2)
                }
                security_range = security_mapping.get(district_type, (1, 5))
                security_level = self.random.randint(security_range[0], security_range[1])
                
                # Services basés sur le type de district
                services_mapping = {
                    "Financial": ["finance", "commerce"],
                    "Corporate": ["commerce", "information"],
                    "Military": ["sécurité"],
                    "Research": ["recherche", "médical"],
                    "Commercial": ["commerce", "divertissement"],
                    "Entertainment": ["divertissement", "commerce"],
                    "Residential": ["logement", "commerce"],
                    "Industrial": ["production", "transport"],
                    "Port": ["transport", "commerce"],
                    "Underground": ["marché noir", "hacking"],
                    "Slums": ["marché noir"]
                }
                base_services = services_mapping.get(district_type, [])
                optional_services = ["médical", "transport", "divertissement", "luxe", "information"]
                num_optional = self.random.randint(0, 2)
                services = base_services + self.random.sample(optional_services, num_optional)
                
                # Tags
                tags = ["district", district_type.lower(), city_name.lower()]
                if security_level >= 4:
                    tags.append("haute sécurité")
                elif security_level <= 2:
                    tags.append("zone dangereuse")
                
                # Description
                descriptions = [
                    f"{name} est un district {self.random.choice(['animé', 'actif', 'important', 'notable'])} de {city_name}.",
                    f"Ce quartier {self.random.choice(['abrite', 'héberge', 'accueille'])} environ {district_population:,} habitants.",
                    f"Le niveau de sécurité y est {['minimal', 'faible', 'modéré', 'élevé', 'maximal'][security_level-1]}.",
                ]
                
                # Ajouter des détails spécifiques au type de district
                if district_type == "Financial":
                    descriptions.append("Les gratte-ciels des grandes corporations dominent le paysage urbain.")
                elif district_type == "Entertainment":
                    descriptions.append("Les néons colorés illuminent les rues jour et nuit, attirant les fêtards.")
                elif district_type == "Slums":
                    descriptions.append("La pauvreté et la criminalité règnent dans ce quartier délaissé par les autorités.")
                elif district_type == "Underground":
                    descriptions.append("Un réseau complexe de tunnels et de passages secrets forme ce district caché.")
                elif district_type == "Research":
                    descriptions.append("Des laboratoires high-tech et des centres de recherche avancée sont regroupés ici.")
                
                description = " ".join(descriptions)
                
                # Insérer le district dans la base de données
                cursor.execute('''
                INSERT INTO locations (id, world_id, name, description, coordinates, security_level, 
                                      population, services, tags, parent_location_id, is_virtual, is_special, is_dangerous, location_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    district_id, world_id, name, description, json.dumps(district_coords), security_level,
                    district_population, json.dumps(services), json.dumps(tags), city_id, 0, 0, 1 if security_level <= 2 else 0, "district"
                ))
                
                district_ids.append(district_id)
                logger.debug(f"District généré: {name} dans {city_name} (ID: {district_id})")
        
        db.conn.commit()
        return district_ids

    def _generate_special_locations(self, db, world_id: str, num_locations: int) -> List[str]:
        """
        Génère des lieux spéciaux pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            num_locations: Nombre de lieux spéciaux à générer
            
        Returns:
            Liste des IDs des lieux spéciaux générés
        """
        special_location_ids = []
        
        # Types de lieux spéciaux
        special_types = [
            ("Darknet Hub", "Un lieu virtuel accessible uniquement via le réseau, point central du darknet mondial.", True, False),
            ("Orbital Station", "Station spatiale en orbite terrestre, réservée à l'élite et aux recherches de pointe.", False, True),
            ("Wasteland", "Ancien centre urbain dévasté par les guerres corporatives, maintenant habité par des marginaux.", False, False),
            ("Underground Bunker", "Bunker souterrain fortifié, vestige des anciennes guerres, reconverti en refuge.", False, False),
            ("AI Nexus", "Centre de calcul quantique où résident les IA les plus avancées du monde.", False, True),
            ("Black Market", "Marché noir international, accessible uniquement aux initiés avec les bonnes connexions.", False, False),
            ("Corporate Island", "Île artificielle détenue par une mégacorporation, avec ses propres lois.", False, True),
            ("Virtual Resort", "Paradis virtuel où les riches peuvent vivre leurs fantasmes sans limites.", True, False)
        ]
        
        # Sélectionner des types aléatoires
        selected_types = self.random.sample(special_types, min(len(special_types), num_locations))
        
        for name_base, desc_base, is_virtual, is_special in selected_types:
            location_id = str(uuid.uuid4())
            
            # Personnaliser le nom
            if self.random.random() < 0.3:
                name = f"{name_base} {self.random.choice(['Alpha', 'Prime', 'Zero', 'Omega', 'X'])}"
            else:
                name = name_base
            
            # Coordonnées (aléatoires ou nulles pour les lieux virtuels)
            if is_virtual:
                coordinates = [0, 0]
            else:
                lat = self.random.uniform(-90, 90)
                lon = self.random.uniform(-180, 180)
                coordinates = [lat, lon]
            
            # Population
            if is_virtual:
                population = 0
            elif is_special:
                population = self.random.randint(100, 10000)
            else:
                population = self.random.randint(1000, 100000)
            
            # Niveau de sécurité
            if is_special:
                security_level = self.random.randint(4, 5)
            elif name_base in ["Wasteland", "Black Market"]:
                security_level = self.random.randint(1, 2)
            else:
                security_level = self.random.randint(1, 5)
            
            # Services
            if is_virtual:
                base_services = ["information", "hacking"]
            elif is_special:
                base_services = ["recherche", "sécurité"]
            elif name_base == "Black Market":
                base_services = ["marché noir", "contrebande"]
            else:
                base_services = ["commerce"]
                
            optional_services = ["médical", "transport", "divertissement", "luxe", "information"]
            num_optional = self.random.randint(0, 3)
            services = base_services + self.random.sample(optional_services, num_optional)
            
            # Tags
            tags = []
            if is_virtual:
                tags.append("virtuel")
            if is_special:
                tags.append("spécial")
            if security_level <= 2:
                tags.append("dangereux")
            if name_base == "Orbital Station":
                tags.append("espace")
            if name_base == "AI Nexus":
                tags.append("intelligence artificielle")
            
            # Description
            description = desc_base
            if is_virtual:
                description += f" {self.random.choice(['Accessible uniquement par des connexions sécurisées.', 'Un monde numérique avec ses propres règles.', 'La réalité y est malléable et dangereuse.'])}"
            if is_special:
                description += f" {self.random.choice(['Accès strictement contrôlé.', 'Réservé à une élite privilégiée.', 'Protégé par des systèmes de sécurité avancés.'])}"
            if security_level <= 2:
                description += f" {self.random.choice(['Un lieu où la loi est absente.', 'Dangereux pour les non-initiés.', 'La survie y est une lutte quotidienne.'])}"
            
            # Insérer le lieu spécial dans la base de données
            cursor = db.conn.cursor()
            cursor.execute('''
            INSERT INTO locations (id, world_id, name, description, coordinates, security_level, 
                                  population, services, tags, is_virtual, is_special, is_dangerous, location_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location_id, world_id, name, description, json.dumps(coordinates), security_level,
                population, json.dumps(services), json.dumps(tags), 1 if is_virtual else 0, 
                1 if is_special else 0, 1 if security_level <= 2 else 0, "virtual" if is_virtual else "special"
            ))
            
            special_location_ids.append(location_id)
            logger.debug(f"Lieu spécial généré: {name} (ID: {location_id})")
        
        db.conn.commit()
        return special_location_ids
    
    def _generate_connections(self, db, world_id: str, location_ids: List[str]) -> None:
        """
        Génère des connexions entre les lieux
        
        Args:
            db: Base de données
            world_id: ID du monde
            location_ids: Liste des IDs de tous les lieux
        """
        # Récupérer les informations sur les lieux
        cursor = db.conn.cursor()
        locations_info = {}
        
        for loc_id in location_ids:
            cursor.execute('''
            SELECT id, name, parent_location_id, is_virtual, is_special, security_level, coordinates
            FROM locations WHERE id = ?
            ''', (loc_id,))
            loc_data = cursor.fetchone()
            if loc_data:
                locations_info[loc_id] = dict(loc_data)
                locations_info[loc_id]["coordinates"] = json.loads(loc_data["coordinates"])
        
        # Créer un graphe de connexions
        # 1. Connecter chaque lieu à son parent (si existe)
        # 2. Connecter les grandes villes entre elles
        # 3. Connecter les districts d'une même ville
        # 4. Ajouter quelques connexions aléatoires
        
        connections_added = 0
        
        # 1. Connexions parent-enfant
        for loc_id, loc_info in locations_info.items():
            parent_id = loc_info.get("parent_location_id")
            if parent_id and parent_id in locations_info:
                # Créer une connexion bidirectionnelle
                connection_id = str(uuid.uuid4())
                travel_type = "Transport local"
                travel_time = 0.2  # Heures
                travel_cost = self.random.randint(10, 100)
                
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, loc_id, parent_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                # Connexion inverse
                connection_id = str(uuid.uuid4())
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, parent_id, loc_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                connections_added += 2
        
        # 2. Connexions entre grandes villes (lieux sans parent)
        cities = [loc_id for loc_id, info in locations_info.items() 
                 if not info.get("parent_location_id") and not info.get("is_virtual") and not info.get("is_special")]
        
        # Créer un graphe connexe (chaque ville est accessible)
        if len(cities) > 1:
            # D'abord, créer un arbre couvrant
            connected_cities = {cities[0]}
            unconnected_cities = set(cities[1:])
            
            while unconnected_cities:
                source_id = self.random.choice(list(connected_cities))
                dest_id = self.random.choice(list(unconnected_cities))
                
                # Créer une connexion bidirectionnelle
                connection_id = str(uuid.uuid4())
                
                # Déterminer le type de transport basé sur la distance
                source_coords = locations_info[source_id]["coordinates"]
                dest_coords = locations_info[dest_id]["coordinates"]
                
                distance = ((source_coords[0] - dest_coords[0])**2 + 
                           (source_coords[1] - dest_coords[1])**2)**0.5
                
                if distance > 50:
                    travel_type = "Vol international"
                    travel_time = self.random.uniform(5, 15)  # Heures
                    travel_cost = self.random.randint(5000, 15000)
                elif distance > 10:
                    travel_type = "Vol régional"
                    travel_time = self.random.uniform(1, 5)  # Heures
                    travel_cost = self.random.randint(1000, 5000)
                else:
                    travel_type = "Train à grande vitesse"
                    travel_time = self.random.uniform(0.5, 3)  # Heures
                    travel_cost = self.random.randint(500, 2000)
                
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, source_id, dest_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                # Connexion inverse
                connection_id = str(uuid.uuid4())
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, dest_id, source_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                connected_cities.add(dest_id)
                unconnected_cities.remove(dest_id)
                connections_added += 2
            
            # Ajouter quelques connexions supplémentaires entre villes
            num_extra = min(len(cities) // 2, 5)
            for _ in range(num_extra):
                source_id = self.random.choice(cities)
                dest_id = self.random.choice([c for c in cities if c != source_id])
                
                # Vérifier si la connexion existe déjà
                cursor.execute('''
                SELECT COUNT(*) FROM connections 
                WHERE source_id = ? AND destination_id = ?
                ''', (source_id, dest_id))
                
                if cursor.fetchone()[0] == 0:
                    # Créer une connexion bidirectionnelle
                    connection_id = str(uuid.uuid4())
                    
                    # Déterminer le type de transport
                    source_coords = locations_info[source_id]["coordinates"]
                    dest_coords = locations_info[dest_id]["coordinates"]
                    
                    distance = ((source_coords[0] - dest_coords[0])**2 + 
                               (source_coords[1] - dest_coords[1])**2)**0.5
                    
                    if distance > 50:
                        travel_type = "Vol international"
                        travel_time = self.random.uniform(5, 15)
                        travel_cost = self.random.randint(5000, 15000)
                    elif distance > 10:
                        travel_type = "Vol régional"
                        travel_time = self.random.uniform(1, 5)
                        travel_cost = self.random.randint(1000, 5000)
                    else:
                        travel_type = "Train à grande vitesse"
                        travel_time = self.random.uniform(0.5, 3)
                        travel_cost = self.random.randint(500, 2000)
                    
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, source_id, dest_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    # Connexion inverse
                    connection_id = str(uuid.uuid4())
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, dest_id, source_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    connections_added += 2
        
        # 3. Connexions entre districts d'une même ville
        # Regrouper les districts par ville parent
        districts_by_city = {}
        for loc_id, info in locations_info.items():
            parent_id = info.get("parent_location_id")
            if parent_id:
                if parent_id not in districts_by_city:
                    districts_by_city[parent_id] = []
                districts_by_city[parent_id].append(loc_id)
        
        # Connecter les districts entre eux
        for city_id, district_ids in districts_by_city.items():
            if len(district_ids) > 1:
                # Créer un graphe connexe entre les districts
                connected_districts = {district_ids[0]}
                unconnected_districts = set(district_ids[1:])
                
                while unconnected_districts:
                    source_id = self.random.choice(list(connected_districts))
                    dest_id = self.random.choice(list(unconnected_districts))
                    
                    # Créer une connexion bidirectionnelle
                    connection_id = str(uuid.uuid4())
                    travel_type = "Métro"
                    travel_time = self.random.uniform(0.1, 0.5)  # Heures
                    travel_cost = self.random.randint(10, 100)
                    
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, source_id, dest_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    # Connexion inverse
                    connection_id = str(uuid.uuid4())
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, dest_id, source_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    connected_districts.add(dest_id)
                    unconnected_districts.remove(dest_id)
                    connections_added += 2
                
                # Ajouter quelques connexions supplémentaires entre districts
                num_extra = min(len(district_ids) // 2, 3)
                for _ in range(num_extra):
                    source_id = self.random.choice(district_ids)
                    dest_id = self.random.choice([d for d in district_ids if d != source_id])
                    
                    # Vérifier si la connexion existe déjà
                    cursor.execute('''
                    SELECT COUNT(*) FROM connections 
                    WHERE source_id = ? AND destination_id = ?
                    ''', (source_id, dest_id))
                    
                    if cursor.fetchone()[0] == 0:
                        # Créer une connexion bidirectionnelle
                        connection_id = str(uuid.uuid4())
                        travel_type = "Métro"
                        travel_time = self.random.uniform(0.1, 0.5)
                        travel_cost = self.random.randint(10, 100)
                        
                        cursor.execute('''
                        INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                                travel_time, travel_cost, requires_hacking, requires_special_access)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            connection_id, world_id, source_id, dest_id, travel_type,
                            travel_time, travel_cost, 0, 0
                        ))
                        
                        # Connexion inverse
                        connection_id = str(uuid.uuid4())
                        cursor.execute('''
                        INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                                travel_time, travel_cost, requires_hacking, requires_special_access)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            connection_id, world_id, dest_id, source_id, travel_type,
                            travel_time, travel_cost, 0, 0
                        ))
                        
                        connections_added += 2
        db.conn.commit()
        logger.info(f"Connexions générées: {connections_added}")
    
    def _generate_buildings(self, db, world_id: str, location_ids: List[str]) -> List[str]:
        """
        Génère des bâtiments pour les lieux
        
        Args:
            db: Base de données
            world_id: ID du monde
            location_ids: Liste des IDs des lieux
            
        Returns:
            Liste des IDs des bâtiments générés
        """
        building_ids = []
        cursor = db.conn.cursor()
        
        # Nombre de bâtiments par lieu (basé sur la population)
        for loc_id in location_ids:
            cursor.execute('''
            SELECT name, population, security_level, is_virtual
            FROM locations WHERE id = ?
            ''', (loc_id,))
            
            loc_data = cursor.fetchone()
            if not loc_data or loc_data["is_virtual"]:
                continue  # Ignorer les lieux virtuels
                
            location_name = loc_data["name"]
            population = loc_data["population"]
            security_level = loc_data["security_level"]
            
            # Déterminer le nombre de bâtiments basé sur la population
            if population > 1000000:  # Grande ville
                num_buildings = self.random.randint(5, 10)
            elif population > 100000:  # Ville moyenne
                num_buildings = self.random.randint(3, 7)
            elif population > 10000:  # Petite ville
                num_buildings = self.random.randint(2, 5)
            else:  # Village ou lieu spécial
                num_buildings = self.random.randint(1, 3)
            
            # Générer les bâtiments
            for _ in range(num_buildings):
                building_id = str(uuid.uuid4())
                
                # Sélectionner un type de bâtiment
                building_type = self.random.choice(BUILDING_TYPES)
                
                # Générer un nom basé sur le type
                if building_type == "Corporate HQ":
                    corps = ["NeoTech", "CyberSys", "QuantumCorp", "SynthInc", "MegaData"]
                    name = f"{self.random.choice(corps)} Headquarters"
                elif building_type == "Research Lab":
                    prefixes = ["Advanced", "Quantum", "Cyber", "Neural", "Bio"]
                    name = f"{self.random.choice(prefixes)} Research Laboratory"
                elif building_type == "Nightclub":
                    names = ["Neon Dreams", "Pulse", "Circuit", "Zero Day", "The Matrix"]
                    name = self.random.choice(names)
                else:
                    # Nom générique pour les autres types
                    name = f"{location_name} {building_type}"
                
                # Nombre d'étages
                if building_type in ["Corporate HQ", "Apartment Complex", "Hotel"]:
                    floors = self.random.randint(10, 50)
                else:
                    floors = self.random.randint(1, 10)
                
                # Niveau de sécurité (influencé par le niveau de sécurité du lieu)
                if building_type in ["Corporate HQ", "Government Building", "Police Station", "Military Base"]:
                    # Bâtiments à haute sécurité
                    building_security = min(5, security_level + self.random.randint(0, 2))
                elif building_type in ["Nightclub", "Shopping Mall", "Restaurant"]:
                    # Bâtiments à sécurité moyenne/basse
                    building_security = max(1, security_level - self.random.randint(0, 2))
                else:
                    # Autres bâtiments
                    building_security = security_level
                
                # Services disponibles
                services = []
                if building_type == "Shopping Mall":
                    services = ["commerce", "divertissement", "restauration"]
                elif building_type == "Hospital":
                    services = ["médical", "pharmacie"]
                elif building_type == "Police Station":
                    services = ["sécurité", "information"]
                elif building_type == "Nightclub":
                    services = ["divertissement", "restauration"]
                elif building_type == "Hotel":
                    services = ["logement", "restauration", "divertissement"]
                elif building_type == "Data Center":
                    services = ["information", "réseau"]
                
                # Propriétaire
                if building_type in ["Corporate HQ", "Research Lab", "Data Center"]:
                    corps = ["NeoTech Corp", "CyberSys Inc", "QuantumCorp", "SynthInc", "MegaData Ltd"]
                    owner = self.random.choice(corps)
                elif building_type in ["Government Building", "Police Station", "Military Base"]:
                    owner = "Gouvernement"
                else:
                    owner = ""  # Propriétaire non spécifié
                
                # Accès spécial requis?
                requires_special_access = 0
                if building_type in ["Military Base", "Government Building", "Corporate HQ"] and self.random.random() < 0.7:
                    requires_special_access = 1
                
                # Hacking requis?
                requires_hacking = 0
                if building_security >= 4 and self.random.random() < 0.3:
                    requires_hacking = 1
                
                # Description
                descriptions = []
                
                # Description de base
                descriptions.append(f"Un {building_type.lower()} de {floors} étages situé à {location_name}.")
                
                if building_security >= 4:
                    descriptions.append("La sécurité y est extrêmement stricte avec des systèmes de surveillance avancés.")
                elif building_security <= 2:
                    descriptions.append("La sécurité y est minimale, ce qui en fait une cible facile.")
                
                if requires_special_access:
                    descriptions.append("L'accès est strictement contrôlé et nécessite une autorisation spéciale.")
                
                if requires_hacking:
                    descriptions.append("Les systèmes de sécurité peuvent être contournés par un hacker compétent.")
                
                if owner:
                    descriptions.append(f"Propriété de {owner}.")
                
                description = " ".join(descriptions)
                
                # Métadonnées pour stocker des informations supplémentaires
                metadata = {
                    "building_id": building_id,
                    "room_id": None
                }
                
                # Insérer le bâtiment dans la base de données
                cursor.execute('''
                INSERT INTO buildings (id, world_id, location_id, name, description, building_type,
                                     floors, security_level, owner, services, is_accessible,
                                     requires_special_access, requires_hacking)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    building_id, world_id, loc_id, name, description, building_type,
                    floors, building_security, owner, json.dumps(services),
                    1 if building_security < 4 else 0,
                    requires_special_access, requires_hacking
                ))
                
                building_ids.append(building_id)
                
                # Générer des pièces pour le bâtiment
                self._generate_rooms(db, building_id, building_type, floors, building_security)
                
                logger.debug(f"Bâtiment généré: {name} à {location_name} (ID: {building_id})")
        
        db.conn.commit()
        return building_ids
    
    def _generate_rooms(self, db, building_id: str, building_type: str, floors: int, security_level: int) -> None:
        """
        Génère des pièces pour un bâtiment
        
        Args:
            db: Base de données
            building_id: ID du bâtiment
            building_type: Type du bâtiment
            floors: Nombre d'étages
            security_level: Niveau de sécurité du bâtiment
        """
        cursor = db.conn.cursor()
        
        # Types de pièces par type de bâtiment
        room_types_by_building = {
            "Corporate HQ": ["Office", "Meeting Room", "Server Room", "Executive Suite", "Lobby", "Cafeteria"],
            "Apartment Complex": ["Apartment", "Lobby", "Maintenance Room", "Rooftop"],
            "Shopping Mall": ["Store", "Food Court", "Security Office", "Storage Room"],
            "Research Lab": ["Laboratory", "Office", "Server Room", "Testing Chamber", "Storage"],
            "Data Center": ["Server Room", "Control Room", "Cooling System", "Security Office"],
            "Hospital": ["Patient Room", "Operating Room", "Pharmacy", "Reception", "Doctor's Office"],
            "Police Station": ["Office", "Holding Cell", "Interrogation Room", "Evidence Room"],
            "Nightclub": ["Dance Floor", "Bar", "VIP Area", "DJ Booth", "Storage"],
            "Restaurant": ["Dining Area", "Kitchen", "Storage", "Office"],
            "Hotel": ["Room", "Lobby", "Restaurant", "Pool", "Gym"],
            "Factory": ["Production Floor", "Office", "Storage", "Control Room"],
            "Warehouse": ["Storage Area", "Loading Dock", "Office"],
            "Government Building": ["Office", "Meeting Room", "Archive", "Security Checkpoint"],
            "School": ["Classroom", "Office", "Cafeteria", "Gym", "Library"],
            "University": ["Lecture Hall", "Laboratory", "Office", "Library", "Student Center"]
        }
        
        # Obtenir les types de pièces pour ce bâtiment
        room_types = room_types_by_building.get(building_type, ["Room", "Office", "Storage"])
        
        # Nombre de pièces par étage
        rooms_per_floor = self.random.randint(1, 5)
        
        # Générer des pièces pour chaque étage
        for floor in range(floors):
            for _ in range(rooms_per_floor):
                room_id = str(uuid.uuid4())
                
                # Sélectionner un type de pièce
                room_type = self.random.choice(room_types)
                
                # Nom de la pièce
                if room_type == "Server Room" and self.random.random() < 0.5:
                    name = f"Serveur {self.random.choice(['A', 'B', 'C', 'D'])}-{floor+1}"
                elif room_type == "Office" and self.random.random() < 0.5:
                    name = f"Bureau {floor+1}-{self.random.randint(1, 10)}"
                elif room_type == "Room" or room_type == "Apartment":
                    name = f"{room_type} {floor+1}-{self.random.randint(1, 20)}"
                else:
                    name = f"{room_type} (Étage {floor+1})"
                
                # Accès
                is_accessible = 1
                requires_hacking = 0
                
                # Les pièces sensibles sont moins accessibles
                if room_type in ["Server Room", "Executive Suite", "Evidence Room", "Security Office", "Control Room"]:
                    if security_level >= 3 or self.random.random() < 0.7:
                        is_accessible = 0
                        if self.random.random() < 0.5:
                            requires_hacking = 1
                
                # Description
                descriptions = [f"Un(e) {room_type.lower()} situé(e) au {floor+1}e étage."]
                
                if not is_accessible:
                    descriptions.append("Cette pièce est verrouillée et nécessite une autorisation spéciale.")
                    
                if requires_hacking:
                    descriptions.append("Le système de verrouillage peut être piraté.")
                
                description = " ".join(descriptions)
                
                # Métadonnées (pour stocker des informations supplémentaires)
                metadata = {
                    "importance": "high" if room_type in ["Server Room", "Executive Suite", "Evidence Room"] else "normal"
                }
                
                # Insérer la pièce dans la base de données
                cursor.execute('''
                INSERT INTO rooms (id, building_id, name, description, floor, room_type,
                                 is_accessible, requires_hacking, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    room_id, building_id, name, description, floor, room_type,
                    is_accessible, requires_hacking, json.dumps(metadata)
                ))
    
    def _generate_devices(self, db, world_id: str, location_ids: List[str], character_ids: List[str], num_devices: int) -> List[str]:
        """
        Génère des appareils électroniques (PC, smartphones, etc.)
        
        Args:
            db: Base de données
            world_id: ID du monde
            location_ids: Liste des IDs des lieux
            character_ids: Liste des IDs des personnages
            num_devices: Nombre d'appareils à générer
            
        Returns:
            Liste des IDs des appareils générés
        """
        device_ids = []
        cursor = db.conn.cursor()
        
        # Récupérer les informations sur les bâtiments
        cursor.execute('''
        SELECT id, location_id, name, building_type, security_level
        FROM buildings WHERE world_id = ?
        ''', (world_id,))
        
        buildings = cursor.fetchall()
        
        if not buildings:
            logger.warning("Aucun bâtiment trouvé pour générer des appareils")
            return device_ids
        
        # Récupérer les informations sur les pièces
        rooms_by_building = {}
        for building in buildings:
            cursor.execute('''
            SELECT id, name, room_type
            FROM rooms WHERE building_id = ?
            ''', (building["id"],))
            
            rooms = cursor.fetchall()
            if rooms:
                rooms_by_building[building["id"]] = rooms
        
        # Générer les appareils
        for _ in range(num_devices):
            device_id = str(uuid.uuid4())
            
            # Sélectionner un type d'appareil
            device_type = self.random.choice(DEVICE_TYPES)
            
            # Sélectionner un système d'exploitation
            os_type = self.random.choice(OS_TYPES)
            
            # Nom de l'appareil
            if device_type == "Server":
                name = f"SRV-{self.random.choice(['MAIN', 'DATA', 'WEB', 'AUTH', 'DB'])}-{self.random.randint(1, 999):03d}"
            elif device_type == "Desktop PC":
                name = f"PC-{self.random.choice(['WORK', 'DEV', 'ADMIN', 'USER'])}-{self.random.randint(1, 999):03d}"
            elif device_type == "Laptop":
                name = f"LT-{self.random.choice(['WORK', 'PERSONAL', 'TRAVEL'])}-{self.random.randint(1, 999):03d}"
            elif device_type == "Smartphone":
                name = f"PHONE-{self.random.choice(['PERSONAL', 'WORK', 'SECURE'])}-{self.random.randint(1, 999):03d}"
            else:
                name = f"{device_type.upper()}-{self.random.randint(1, 999):03d}"
            
            # Niveau de sécurité (1-5)
            if device_type in ["Server", "Security System"]:
                security_level = self.random.randint(3, 5)
            elif device_type in ["Desktop PC", "Laptop"] and "ADMIN" in name:
                security_level = self.random.randint(3, 4)
            else:
                security_level = self.random.randint(1, 3)
            
            # Emplacement de l'appareil
            # 70% dans un bâtiment, 30% avec un personnage
            if self.random.random() < 0.7:
                # Dans un bâtiment
                building = self.random.choice(buildings)
                location_id = building["location_id"]
                
                # Sélectionner une pièce si disponible
                room_id = None
                if building["id"] in rooms_by_building:
                    room = self.random.choice(rooms_by_building[building["id"]])
                    room_id = room["id"]
                
                owner_id = None
                
                # Métadonnées pour stocker des informations supplémentaires
                metadata = {
                    "building_id": building["id"],
                    "room_id": room_id
                }
            else:
                # Avec un personnage
                if character_ids:
                    owner_id = self.random.choice(character_ids)
                    
                    # Récupérer l'emplacement du personnage
                    cursor.execute("SELECT location_id FROM characters WHERE id = ?", (owner_id,))
                    character_data = cursor.fetchone()
                    
                    if character_data:
                        location_id = character_data["location_id"]
                    else:
                        # Si le personnage n'a pas d'emplacement, choisir un lieu aléatoire
                        location_id = self.random.choice(location_ids)
                    
                    metadata = {}
                else:
                    # Si pas de personnages, mettre l'appareil dans un lieu aléatoire
                    location_id = self.random.choice(location_ids)
                    owner_id = None
                    metadata = {}
            
            # Adresse IP
            ip_address = str(ipaddress.IPv4Address(self.random.randint(0, 2**32-1)))
            
            # Description
            descriptions = [f"Un {device_type.lower()} exécutant {os_type}."]
            
            if security_level >= 4:
                descriptions.append("Cet appareil dispose d'une sécurité de haut niveau avec plusieurs couches de protection.")
            elif security_level <= 2:
                descriptions.append("La sécurité de cet appareil est minimale et présente plusieurs vulnérabilités.")
            
            if device_type == "Server":
                descriptions.append(f"Ce serveur héberge des services critiques et est accessible via l'adresse {ip_address}.")
            elif device_type == "Security System":
                descriptions.append("Ce système contrôle les accès et la surveillance d'une zone sécurisée.")
            
            description = " ".join(descriptions)
            
            # Insérer l'appareil dans la base de données
            cursor.execute('''
            INSERT INTO devices (id, world_id, name, description, location_id, owner_id,
                               device_type, os_type, security_level, is_connected, ip_address, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id, world_id, name, description, location_id, owner_id,
                device_type, os_type, security_level, 1, ip_address, json.dumps(metadata)
            ))
            
            device_ids.append(device_id)
            logger.debug(f"Appareil généré: {name} (ID: {device_id})")
        
        db.conn.commit()
        return device_ids

    def _generate_characters(self, db, world_id: str, location_ids: List[str], num_characters: int) -> List[str]:
        """
        Génère des personnages pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            location_ids: Liste des IDs des lieux
            num_characters: Nombre de personnages à générer
            
        Returns:
            Liste des IDs des personnages générés
        """
        character_ids = []
        cursor = db.conn.cursor()
        
        # Récupérer les informations sur les lieux
        locations_by_id = {}
        for loc_id in location_ids:
            cursor.execute('''
            SELECT name, security_level, is_virtual, is_special, is_dangerous, tags
            FROM locations WHERE id = ?
            ''', (loc_id,))
            
            loc_data = cursor.fetchone()
            if loc_data:
                locations_by_id[loc_id] = loc_data
        
        # Générer les personnages
        for _ in range(num_characters):
            character_id = str(uuid.uuid4())
            
            # Sélectionner un lieu pour le personnage
            location_id = self.random.choice(location_ids)
            location_data = locations_by_id.get(location_id, {})
            
            # Générer un nom
            gender = self.random.choice(["M", "F"])
            
            if gender == "M":
                first_names = ["Adam", "Alex", "Benjamin", "Chen", "David", "Ethan", "Felix", "Gabriel", 
                              "Hiro", "Ian", "Jack", "Kenji", "Liam", "Miguel", "Noah", "Omar", 
                              "Paul", "Quentin", "Ryan", "Sanjay", "Thomas", "Umar", "Victor", "Wei", 
                              "Xavier", "Yuri", "Zack"]
                name = f"{self.random.choice(first_names)} {self.random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'])}"
            else:
                first_names = ["Alice", "Bianca", "Claire", "Diana", "Emma", "Fiona", "Grace", "Hannah", 
                              "Iris", "Julia", "Kate", "Lily", "Maria", "Nina", "Olivia", "Penny", 
                              "Quinn", "Rose", "Sophia", "Tara", "Uma", "Victoria", "Wendy", "Xena", 
                              "Yasmine", "Zoe"]
                name = f"{self.random.choice(first_names)} {self.random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'])}"
            
            # Sélectionner une profession
            profession = self.random.choice(CHARACTER_PROFESSIONS)
            
            # Déterminer la faction
            faction = self.random.choice(FACTION_NAMES)
            
            # Niveau d'importance (1-5)
            importance = self.random.randint(1, 5)
            
            # Niveau de hacking (0-10)
            if profession in ["Hacker", "Security Specialist", "Programmer", "Engineer"]:
                hacking_level = self.random.randint(5, 10)
            elif profession in ["Corporate Executive", "Government Agent", "Police Officer"]:
                hacking_level = self.random.randint(2, 5)
            else:
                hacking_level = self.random.randint(0, 3)
            
            # Niveau de combat (0-10)
            if profession in ["Mercenary", "Soldier", "Police Officer", "Assassin"]:
                combat_level = self.random.randint(5, 10)
            elif profession in ["Security Specialist", "Smuggler", "Fixer"]:
                combat_level = self.random.randint(3, 7)
            else:
                combat_level = self.random.randint(0, 3)
            
            # Niveau de charisme (0-10)
            if profession in ["Fixer", "Corporate Executive", "Information Broker", "Journalist"]:
                charisma = self.random.randint(5, 10)
            else:
                charisma = self.random.randint(1, 8)
            
            # Niveau de richesse (0-10)
            if profession in ["Corporate Executive", "Fixer", "Information Broker"]:
                wealth = self.random.randint(6, 10)
            elif profession in ["Hacker", "Mercenary", "Smuggler", "Tech Dealer"]:
                wealth = self.random.randint(3, 8)
            else:
                wealth = self.random.randint(1, 5)
            
            # Génération de la description
            descriptions = []
            
            # Description de base
            descriptions.append(f"{name} est un(e) {profession.lower()} travaillant pour {faction}.")
            
            # Description basée sur les compétences
            if hacking_level >= 8:
                descriptions.append("Ses compétences en hacking sont légendaires.")
            elif hacking_level >= 5:
                descriptions.append("Possède de solides compétences en informatique et en hacking.")
            
            if combat_level >= 8:
                descriptions.append("C'est un combattant redoutable que peu osent défier.")
            elif combat_level >= 5:
                descriptions.append("Sait se défendre et n'hésite pas à utiliser la force si nécessaire.")
            
            if charisma >= 8:
                descriptions.append("Son charisme naturel lui ouvre de nombreuses portes.")
            
            if wealth >= 8:
                descriptions.append("Sa fortune considérable lui permet d'accéder aux cercles les plus exclusifs.")
            elif wealth <= 2:
                descriptions.append("Vit dans la précarité, cherchant constamment des moyens de survivre.")
            
            # Description basée sur l'importance
            if importance >= 4:
                descriptions.append("C'est une figure importante dans le monde de YakTaa.")
            
            # Description basée sur le lieu
            if location_data:
                descriptions.append(f"On peut généralement le trouver à {location_data['name']}.")
            
            description = " ".join(descriptions)
            
            # Métadonnées (pour stocker des informations supplémentaires)
            metadata = {
                "background": self.random.choice([
                    "Ancien militaire reconverti dans le civil.",
                    "A grandi dans les bas-fonds, s'est fait un nom par la force.",
                    "Diplômé d'une prestigieuse université, a choisi une voie non conventionnelle.",
                    "Ancien employé corporatif qui a changé de camp après avoir découvert la vérité.",
                    "Autodidacte qui a appris sur le tas dans les rues de la ville.",
                    "Issu d'une famille influente mais a renié son héritage."
                ]),
                "motivations": self.random.choice([
                    "Recherche la richesse à tout prix.",
                    "Veut changer le système de l'intérieur.",
                    "Cherche à se venger d'une corporation.",
                    "Protège les plus faibles contre les puissants.",
                    "Poursuit le pouvoir et l'influence.",
                    "Cherche simplement à survivre dans ce monde hostile."
                ]),
                "secrets": self.random.choice([
                    "Cache une identité secrète.",
                    "Travaille secrètement pour une faction rivale.",
                    "Possède des informations compromettantes sur des personnalités importantes.",
                    "A participé à un événement tragique dont personne ne connaît son implication.",
                    "Est atteint d'une maladie rare et cherche désespérément un remède.",
                    "Est en réalité un agent infiltré."
                ])
            }
            
            # Insérer le personnage dans la base de données
            cursor.execute('''
            INSERT INTO characters (id, world_id, name, description, location_id, profession,
                                  faction, gender, importance, hacking_level, combat_level,
                                  charisma, wealth, is_hostile, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                character_id, world_id, name, description, location_id, profession,
                faction, gender, importance, hacking_level, combat_level,
                charisma, wealth, 0, json.dumps(metadata)
            ))
            
            character_ids.append(character_id)
            logger.debug(f"Personnage généré: {name} (ID: {character_id})")
        
        db.conn.commit()
        return character_ids
    
    def _generate_files(self, db, world_id: str, device_ids: List[str]) -> List[str]:
        """
        Génère des fichiers pour les appareils
        
        Args:
            db: Base de données
            world_id: ID du monde
            device_ids: Liste des IDs des appareils
            
        Returns:
            Liste des IDs des fichiers générés
        """
        file_ids = []
        cursor = db.conn.cursor()
        
        # Récupérer les informations sur les appareils
        devices_by_id = {}
        for device_id in device_ids:
            cursor.execute('''
            SELECT name, device_type, os_type, security_level
            FROM devices WHERE id = ?
            ''', (device_id,))
            
            device_data = cursor.fetchone()
            if device_data:
                devices_by_id[device_id] = device_data
        
        # Générer les fichiers
        for device_id, device_data in devices_by_id.items():
            # Nombre de fichiers basé sur le type d'appareil
            if device_data["device_type"] == "Server":
                num_files = self.random.randint(5, 10)
            elif device_data["device_type"] in ["Desktop PC", "Laptop"]:
                num_files = self.random.randint(3, 7)
            else:
                num_files = self.random.randint(1, 4)
            
            for _ in range(num_files):
                file_id = str(uuid.uuid4())
                
                # Type de fichier
                file_type = self.random.choice(FILE_TYPES)
                
                # Extension basée sur le type
                if file_type == "text":
                    extension = self.random.choice([".txt", ".md", ".log"])
                elif file_type == "document":
                    extension = self.random.choice([".doc", ".docx", ".pdf", ".odt"])
                elif file_type == "spreadsheet":
                    extension = self.random.choice([".xls", ".xlsx", ".csv"])
                elif file_type == "image":
                    extension = self.random.choice([".jpg", ".png", ".gif", ".bmp"])
                elif file_type == "audio":
                    extension = self.random.choice([".mp3", ".wav", ".ogg"])
                elif file_type == "video":
                    extension = self.random.choice([".mp4", ".avi", ".mkv"])
                elif file_type == "executable":
                    extension = self.random.choice([".exe", ".bat", ".sh"])
                elif file_type == "archive":
                    extension = self.random.choice([".zip", ".rar", ".tar.gz"])
                elif file_type == "database":
                    extension = self.random.choice([".db", ".sqlite", ".sql"])
                elif file_type == "script":
                    extension = self.random.choice([".py", ".js", ".php", ".rb"])
                elif file_type == "config":
                    extension = self.random.choice([".ini", ".cfg", ".json", ".xml"])
                else:
                    extension = ".dat"
                
                # Nom du fichier
                if file_type == "document":
                    prefixes = ["rapport", "memo", "contrat", "projet", "plan", "analyse"]
                    name = f"{self.random.choice(prefixes)}_{self.random.randint(1, 999):03d}{extension}"
                elif file_type == "image":
                    prefixes = ["photo", "image", "capture", "scan"]
                    name = f"{self.random.choice(prefixes)}_{self.random.randint(1, 999):03d}{extension}"
                elif file_type == "executable":
                    prefixes = ["install", "setup", "app", "tool", "utility"]
                    name = f"{self.random.choice(prefixes)}_{self.random.randint(1, 999):03d}{extension}"
                elif file_type == "log":
                    services = ["system", "security", "network", "app", "error"]
                    name = f"{self.random.choice(services)}_log_{self.random.randint(1, 999):03d}{extension}"
                else:
                    name = f"file_{self.random.randint(1, 9999):04d}{extension}"
                
                # Taille du fichier (en Ko)
                if file_type in ["video", "database", "archive"]:
                    size = self.random.randint(1000, 10000)
                elif file_type in ["image", "audio", "executable"]:
                    size = self.random.randint(100, 2000)
                else:
                    size = self.random.randint(1, 500)
                
                # Niveau de sécurité (1-5)
                # Influencé par le niveau de sécurité de l'appareil
                base_security = device_data["security_level"]
                security_level = max(1, min(5, base_security + self.random.randint(-1, 1)))
                
                # Chiffrement
                is_encrypted = 0
                if security_level >= 4 or (security_level >= 3 and self.random.random() < 0.5):
                    is_encrypted = 1
                
                # Importance (1-5)
                importance = self.random.randint(1, 5)
                
                # Contenu du fichier
                content = ""
                if file_type == "text":
                    paragraphs = []
                    for _ in range(self.random.randint(1, 5)):
                        if importance >= 4:  # Fichier important
                            paragraphs.append(self.random.choice([
                                "Ces données sont strictement confidentielles. Toute divulgation est passible de poursuites.",
                                "Le projet Nexus avance comme prévu. Les premiers tests sont concluants.",
                                "Les coordonnées d'accès au serveur central: 192.168.1.1, port 22, user: admin, password: ********",
                                "La livraison aura lieu le 15 du mois à minuit au point de rendez-vous habituel.",
                                "Les fonds ont été transférés sur le compte offshore. Confirmation attendue dans 24h."
                            ]))
                        else:  # Fichier standard
                            paragraphs.append(self.random.choice([
                                "Rapport hebdomadaire des activités du département.",
                                "Liste des tâches à accomplir pour le projet en cours.",
                                "Notes de réunion du comité de direction.",
                                "Inventaire des ressources disponibles.",
                                "Procédure standard d'opération pour le système."
                            ]))
                    content = "\n\n".join(paragraphs)
                
                # Description
                descriptions = [f"Un fichier {file_type} de {size} Ko."]
                
                if is_encrypted:
                    descriptions.append("Ce fichier est chiffré et nécessite une clé de déchiffrement.")
                
                if importance >= 4:
                    descriptions.append("Ce fichier semble contenir des informations importantes.")
                
                description = " ".join(descriptions)
                
                # Métadonnées pour stocker des informations supplémentaires
                metadata = {
                    "creation_date": f"2023-{self.random.randint(1, 12):02d}-{self.random.randint(1, 28):02d}",
                    "last_modified": f"2023-{self.random.randint(1, 12):02d}-{self.random.randint(1, 28):02d}",
                    "author": self.random.choice(["admin", "user", "system", "unknown"]),
                    "permissions": "rw-r--r--" if security_level <= 3 else "rw-------"
                }
                
                # Insérer le fichier dans la base de données
                cursor.execute('''
                INSERT INTO files (id, world_id, device_id, name, description, file_type,
                                 extension, size, content, security_level, is_encrypted,
                                 importance, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id, world_id, device_id, name, description, file_type,
                    extension, size, content, security_level, is_encrypted,
                    importance, json.dumps(metadata)
                ))
                
                file_ids.append(file_id)
                logger.debug(f"Fichier généré: {name} sur {device_data['name']} (ID: {file_id})")
        
        db.conn.commit()
        return file_ids

    def _generate_missions(self, db, world_id: str, location_ids: List[str], character_ids: List[str], num_missions: int) -> List[str]:
        """Génère des missions pour le monde"""
        mission_ids = []
        
        # Obtenir une nouvelle connexion à la base de données
        db = get_database(db.db_path)
        
        cursor = db.conn.cursor()
        
        # Types de missions possibles
        mission_types = [
            'infiltration', 'récupération', 'hacking', 'protection', 'livraison',
            'élimination', 'sabotage', 'espionnage', 'escorte', 'investigation'
        ]
        
        # Niveaux de difficulté
        difficulty_levels = ['facile', 'moyen', 'difficile', 'très difficile', 'extrême']
        
        # Générer les missions
        for _ in range(num_missions):
            mission_id = str(uuid.uuid4())
            
            # Sélectionner un type de mission aléatoire
            mission_type = random.choice(mission_types)
            
            # Générer un titre pour la mission
            title_prefixes = {
                'infiltration': ['Infiltration', 'Accès', 'Pénétration'],
                'récupération': ['Récupération', 'Extraction', 'Sauvetage'],
                'hacking': ['Piratage', 'Intrusion', 'Bypass'],
                'protection': ['Protection', 'Défense', 'Sécurisation'],
                'livraison': ['Livraison', 'Transport', 'Transfert'],
                'élimination': ['Neutralisation', 'Élimination', 'Suppression'],
                'sabotage': ['Sabotage', 'Destruction', 'Dysfonctionnement'],
                'espionnage': ['Espionnage', 'Surveillance', 'Observation'],
                'escorte': ['Escorte', 'Accompagnement', 'Protection'],
                'investigation': ['Enquête', 'Investigation', 'Recherche']
            }
            
            title_objects = {
                'infiltration': ['du système', 'du bâtiment', 'de la zone sécurisée'],
                'récupération': ['des données', 'du prototype', 'de l\'otage'],
                'hacking': ['de la base de données', 'du réseau', 'du serveur'],
                'protection': ['du VIP', 'des données', 'du convoi'],
                'livraison': ['du colis', 'des informations', 'du prototype'],
                'élimination': ['de la cible', 'du témoin', 'de la menace'],
                'sabotage': ['de l\'infrastructure', 'du système', 'de la production'],
                'espionnage': ['de la réunion', 'des communications', 'des activités'],
                'escorte': ['du VIP', 'du convoi', 'du témoin'],
                'investigation': ['sur la disparition', 'sur le meurtre', 'sur le vol']
            }
            
            title_prefix = random.choice(title_prefixes[mission_type])
            title_object = random.choice(title_objects[mission_type])
            
            title = f"{title_prefix} {title_object}"
            
            # Générer une description pour la mission
            descriptions = []
            
            if mission_type == 'infiltration':
                descriptions.append("Infiltrez-vous dans un lieu hautement sécurisé pour accomplir un objectif.")
            elif mission_type == 'récupération':
                descriptions.append("Récupérez un objet ou des données importantes et ramenez-les à votre contact.")
            elif mission_type == 'hacking':
                descriptions.append("Piratez un système informatique pour extraire des informations ou modifier des données.")
            elif mission_type == 'protection':
                descriptions.append("Protégez une cible contre des menaces potentielles.")
            elif mission_type == 'livraison':
                descriptions.append("Livrez un colis ou des informations à un destinataire spécifique.")
            elif mission_type == 'élimination':
                descriptions.append("Éliminez une cible spécifique discrètement ou non.")
            elif mission_type == 'sabotage':
                descriptions.append("Sabotez un équipement ou une infrastructure pour perturber les opérations.")
            elif mission_type == 'espionnage':
                descriptions.append("Espionnez une cible pour recueillir des informations sensibles.")
            elif mission_type == 'escorte':
                descriptions.append("Escortez une personne ou un convoi jusqu'à sa destination en toute sécurité.")
            elif mission_type == 'investigation':
                descriptions.append("Enquêtez sur un événement mystérieux pour découvrir la vérité.")
            
            description = " ".join(descriptions)
            
            # Sélectionner un personnage aléatoire comme donneur de mission
            giver_id = random.choice(character_ids) if character_ids else None
            
            # Sélectionner un lieu aléatoire pour la mission
            location_id = random.choice(location_ids) if location_ids else None
            
            # Générer un niveau de difficulté aléatoire
            difficulty = random.choice(difficulty_levels)
            
            # Générer des récompenses aléatoires
            rewards = {
                'credits': random.randint(100, 10000),
                'items': random.randint(0, 3),
                'reputation': random.randint(1, 10)
            }
            
            # Déterminer si c'est une quête principale
            is_main_quest = 1 if random.random() < 0.2 else 0
            
            # Déterminer si la mission est répétable
            is_repeatable = 1 if random.random() < 0.1 else 0
            
            # Déterminer si la mission est cachée
            is_hidden = 1 if random.random() < 0.15 else 0
            
            # Métadonnées supplémentaires
            metadata = {
                'time_limit': random.randint(0, 72) if random.random() < 0.3 else None,  # Limite de temps en heures
                'failure_consequences': random.choice(['none', 'reputation_loss', 'item_loss', 'game_over']) if random.random() < 0.5 else None,
                'alternate_endings': random.randint(1, 3) if random.random() < 0.2 else 1
            }
            
            # Insérer la mission dans la base de données
            cursor.execute('''
            INSERT INTO missions (id, world_id, title, description, giver_id, location_id,
                               mission_type, difficulty, rewards, prerequisites,
                               is_main_quest, is_repeatable, is_hidden, story_elements, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mission_id, world_id, title, description, giver_id, location_id,
                mission_type, difficulty, json.dumps(rewards), None,
                is_main_quest, is_repeatable, is_hidden, None, json.dumps(metadata)
            ))
            
            # Générer des objectifs pour la mission
            num_objectives = random.randint(1, 5)
            
            for i in range(num_objectives):
                objective_id = str(uuid.uuid4())
                
                # Générer un titre pour l'objectif
                objective_titles = {
                    'infiltration': ['Accéder à la zone', 'Trouver une entrée', 'Éviter les gardes'],
                    'récupération': ['Localiser la cible', 'Récupérer l\'objet', 'S\'échapper avec l\'objet'],
                    'hacking': ['Trouver un point d\'accès', 'Contourner le pare-feu', 'Extraire les données'],
                    'protection': ['Éliminer les menaces', 'Sécuriser le périmètre', 'Escorter la cible'],
                    'livraison': ['Récupérer le colis', 'Éviter les embuscades', 'Livrer le colis'],
                    'élimination': ['Localiser la cible', 'Éliminer la cible', 'Effacer les traces'],
                    'sabotage': ['Accéder au système', 'Planter le virus', 'S\'échapper discrètement'],
                    'espionnage': ['Observer la cible', 'Enregistrer la conversation', 'Transmettre les informations'],
                    'escorte': ['Rencontrer la cible', 'Protéger pendant le trajet', 'Arriver à destination'],
                    'investigation': ['Interroger les témoins', 'Recueillir des preuves', 'Identifier le coupable']
                }
                
                objective_title = objective_titles[mission_type][i % len(objective_titles[mission_type])]
                
                # Générer une description pour l'objectif
                objective_description = f"Objectif {i+1} de la mission: {objective_title}"
                
                # Déterminer le type d'objectif
                objective_types = ['goto', 'interact', 'collect', 'hack', 'eliminate', 'protect', 'escape']
                objective_type = random.choice(objective_types)
                
                # Déterminer si l'objectif est optionnel
                is_optional = 1 if random.random() < 0.2 else 0
                
                # Insérer l'objectif dans la base de données
                cursor.execute('''
                INSERT INTO objectives (id, mission_id, title, description, objective_type,
                                     target_id, target_count, is_optional, order_index, completion_script, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    objective_id, mission_id, objective_title, objective_description, objective_type,
                    None, random.randint(1, 5), is_optional, i, None, None
                ))
            
            mission_ids.append(mission_id)
            logger.debug(f"Mission générée: {title} (ID: {mission_id})")
        
        db.conn.commit()
        return mission_ids

    def _generate_story_elements(self, db, world_id: str, location_ids: List[str], character_ids: List[str], mission_ids: List[str], num_elements: int) -> List[str]:
        """Génère des éléments d'histoire pour le monde"""
        story_element_ids = []
        
        # Obtenir une nouvelle connexion à la base de données
        db = get_database(db.db_path)
        
        cursor = db.conn.cursor()
        
        # Types d'éléments d'histoire
        element_types = [
            'background', 'event', 'lore', 'character_story', 'location_history',
            'faction_info', 'technology', 'mystery', 'rumor', 'legend'
        ]
        
        # Générer les éléments d'histoire
        for i in range(num_elements):
            element_id = str(uuid.uuid4())
            
            # Sélectionner un type d'élément aléatoire
            element_type = random.choice(element_types)
            
            # Générer un titre pour l'élément d'histoire
            title_prefixes = {
                'background': ['Histoire de', 'Origines de', 'Passé de'],
                'event': ['Incident de', 'Événement de', 'Catastrophe de'],
                'lore': ['Mythes de', 'Légendes de', 'Traditions de'],
                'character_story': ['Histoire de', 'Passé de', 'Secrets de'],
                'location_history': ['Histoire de', 'Fondation de', 'Évolution de'],
                'faction_info': ['Idéologie de', 'Structure de', 'Objectifs de'],
                'technology': ['Développement de', 'Innovation de', 'Avancées en'],
                'mystery': ['Mystère de', 'Énigme de', 'Secret de'],
                'rumor': ['Rumeurs sur', 'On dit que', 'Il paraît que'],
                'legend': ['Légende de', 'Mythe de', 'Conte de']
            }
            
            # Sélectionner des éléments liés aléatoires
            related_location_id = random.choice(location_ids) if location_ids and random.random() < 0.7 else None
            related_character_id = random.choice(character_ids) if character_ids and random.random() < 0.5 else None
            related_mission_id = random.choice(mission_ids) if mission_ids and random.random() < 0.3 else None
            
            # Récupérer les noms des éléments liés pour générer un titre pertinent
            location_name = "un lieu inconnu"
            character_name = "quelqu'un"
            mission_title = "une mission"
            
            if related_location_id:
                cursor.execute("SELECT name FROM locations WHERE id = ?", (related_location_id,))
                result = cursor.fetchone()
                if result:
                    location_name = result[0]
            
            if related_character_id:
                cursor.execute("SELECT name FROM characters WHERE id = ?", (related_character_id,))
                result = cursor.fetchone()
                if result:
                    character_name = result[0]
            
            if related_mission_id:
                cursor.execute("SELECT title FROM missions WHERE id = ?", (related_mission_id,))
                result = cursor.fetchone()
                if result:
                    mission_title = result[0]
            
            # Générer le titre en fonction du type et des éléments liés
            if element_type == 'character_story' and related_character_id:
                title = f"{random.choice(title_prefixes[element_type])} {character_name}"
            elif element_type == 'location_history' and related_location_id:
                title = f"{random.choice(title_prefixes[element_type])} {location_name}"
            elif related_mission_id:
                title = f"{random.choice(title_prefixes[element_type])} {mission_title}"
            elif related_location_id:
                title = f"{random.choice(title_prefixes[element_type])} {location_name}"
            elif related_character_id:
                title = f"{random.choice(title_prefixes[element_type])} {character_name}"
            else:
                # Définir les options en dehors de la f-string pour éviter les problèmes d'échappement
                location_options = ['la ville', 'la région', 'l\'époque', 'la technologie', 'la corporation']
                selected_location = random.choice(location_options)
                title = f"{random.choice(title_prefixes[element_type])} {selected_location}"
            
            # Générer le contenu de l'élément d'histoire
            content_templates = {
                'background': [
                    "Il y a longtemps, cette région était connue pour ses ressources naturelles abondantes.",
                    "Avant la grande catastrophe, cet endroit était un centre technologique florissant.",
                    "Les origines de cette zone remontent à l'époque des premières colonies spatiales."
                ],
                'event': [
                    "Un incident majeur s'est produit ici il y a quelques années, changeant à jamais la dynamique locale.",
                    "La grande panne de 2077 a paralysé les systèmes pendant des semaines.",
                    "L'attaque du réseau central a révélé des vulnérabilités critiques dans l'infrastructure."
                ],
                'lore': [
                    "Les anciens racontent que des créatures mystérieuses habitaient autrefois ces lieux.",
                    "Selon la tradition locale, celui qui contrôle l'information contrôle le monde.",
                    "Les légendes parlent d'un trésor de données caché quelque part dans les profondeurs du réseau."
                ],
                'character_story': [
                    "Né dans les bas-fonds, ce personnage a gravi les échelons grâce à son intelligence exceptionnelle.",
                    "Ancien agent de sécurité, cette personne a changé de camp après avoir découvert la vérité.",
                    "Mystérieux et solitaire, peu de gens connaissent le véritable passé de cet individu."
                ],
                'location_history': [
                    "Autrefois un simple avant-poste, cet endroit s'est transformé en centre névralgique.",
                    "Construit sur les ruines d'une ancienne mégalopole, ce lieu conserve des secrets enfouis.",
                    "Ce quartier a changé de mains de nombreuses fois au cours des guerres corporatives."
                ],
                'faction_info': [
                    "Cette organisation opère dans l'ombre, manipulant l'économie mondiale à son avantage.",
                    "Fondée par d'anciens militaires, cette faction prône un retour à l'ordre traditionnel.",
                    "Collectif de hackers idéalistes, ce groupe lutte pour la liberté de l'information."
                ],
                'technology': [
                    "Cette innovation révolutionnaire a changé la façon dont les gens interagissent avec le réseau.",
                    "Développée initialement à des fins militaires, cette technologie s'est répandue dans la société civile.",
                    "Les implants neuraux de dernière génération permettent une connexion instantanée au cyberespace."
                ],
                'mystery': [
                    "Personne ne sait ce qui est arrivé aux habitants originels de cette zone.",
                    "Les disparitions mystérieuses continuent d'intriguer les autorités locales.",
                    "Le code source original n'a jamais été retrouvé, alimentant de nombreuses théories."
                ],
                'rumor': [
                    "On raconte que certains hackers peuvent accéder à des niveaux de réseau dont l'existence est niée.",
                    "Des témoins affirment avoir vu des agents gouvernementaux tester des technologies inconnues.",
                    "Selon les rumeurs, une IA autonome se cacherait quelque part dans le réseau mondial."
                ],
                'legend': [
                    "La légende du Fantôme du Réseau continue de fasciner les jeunes hackers.",
                    "L'histoire du Gardien des Codes est transmise de génération en génération.",
                    "Le mythe de la Clé Universelle inspire encore aujourd'hui de nombreux technophiles."
                ]
            }
            
            content = random.choice(content_templates[element_type])
            
            # Déterminer si l'élément est révélé dès le début
            is_revealed = 1 if random.random() < 0.6 else 0
            
            # Conditions de révélation pour les éléments cachés
            reveal_condition = None
            if not is_revealed:
                conditions = [
                    "complete_mission:{}".format(related_mission_id) if related_mission_id else None,
                    "visit_location:{}".format(related_location_id) if related_location_id else None,
                    "meet_character:{}".format(related_character_id) if related_character_id else None,
                    "player_level:{}".format(random.randint(5, 20)),
                    "hacking_skill:{}".format(random.randint(3, 10))
                ]
                reveal_condition = next((c for c in conditions if c is not None), "player_level:5")
            
            # Insérer l'élément d'histoire dans la base de données
            cursor.execute('''
            INSERT INTO story_elements (id, world_id, title, content, element_type,
                                     related_location_id, related_character_id, related_mission_id,
                                     order_index, is_revealed, reveal_condition, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                element_id, world_id, title, content, element_type,
                related_location_id, related_character_id, related_mission_id,
                i, is_revealed, reveal_condition, None
            ))
            
            story_element_ids.append(element_id)
            logger.debug(f"Élément d'histoire généré: {title} (ID: {element_id})")
        
        db.conn.commit()
        return story_element_ids

    def _generate_networks(self, db, world_id: str, building_ids: List[str]) -> List[str]:
        """
        Génère des réseaux pour les bâtiments
        
        Args:
            db: Base de données
            world_id: ID du monde
            building_ids: Liste des IDs des bâtiments
            
        Returns:
            Liste des IDs des réseaux générés
        """
        network_ids = []
        cursor = db.conn.cursor()
        
        # Obtenir des informations sur les bâtiments
        for building_id in building_ids:
            cursor.execute('''
            SELECT id, building_type, security_level, name 
            FROM buildings WHERE id = ?
            ''', (building_id,))
            
            building = cursor.fetchone()
            if not building:
                continue
                
            # Déterminer le nombre de réseaux à générer en fonction du type de bâtiment
            num_networks = 0
            if building["building_type"] in ["Corporate HQ", "Data Center", "Research Lab"]:
                num_networks = self.random.randint(3, 6)
            elif building["building_type"] in ["Government Building", "Police Station", "Military Base"]:
                num_networks = self.random.randint(2, 4)
            elif building["building_type"] in ["Shopping Mall", "Hotel", "University"]:
                num_networks = self.random.randint(2, 5)
            else:
                num_networks = self.random.randint(1, 3)
            
            # Générer des réseaux pour ce bâtiment
            for _ in range(num_networks):
                network_id = str(uuid.uuid4())
                
                # Choisir un type de réseau adapté au type de bâtiment
                network_type = None
                if building["building_type"] in ["Corporate HQ", "Data Center"]:
                    network_type = self.random.choice(["Corporate", "LAN", "WAN", "VPN", "Secured"])
                elif building["building_type"] in ["Shopping Mall", "Hotel"]:
                    network_type = self.random.choice(["WiFi", "Public", "IoT"])
                elif building["building_type"] in ["Apartment Complex", "Residential"]:
                    network_type = self.random.choice(["WiFi", "IoT"])
                else:
                    network_type = self.random.choice(NETWORK_TYPES)
                
                # Générer un nom et un SSID
                if network_type == "WiFi":
                    if "Corporate" in building["building_type"]:
                        name = f"{building['name'][:10]}_WIFI"
                    elif "Hotel" in building["building_type"]:
                        name = f"Guest_WiFi_{self.random.randint(100, 999)}"
                    else:
                        name = f"Network_{self.random.randint(1000, 9999)}"
                    
                    ssid = name.replace(" ", "_").upper()
                elif network_type in ["Corporate", "Secured"]:
                    name = f"{building['name'][:10]}_{network_type.upper()}"
                    ssid = f"{name.replace(' ', '_').upper()}"
                else:
                    name = f"{network_type}_{self.random.randint(1000, 9999)}"
                    ssid = name
                
                # Déterminer le niveau de sécurité en fonction du type de bâtiment et de réseau
                security_level = None
                if building["security_level"] >= 4 or network_type in ["Corporate", "Secured", "VPN"]:
                    security_level = self.random.choice(["WPA3", "Enterprise"])
                elif building["security_level"] >= 3 or network_type in ["LAN", "WAN"]:
                    security_level = self.random.choice(["WPA2", "WPA3"])
                elif building["security_level"] >= 2:
                    security_level = self.random.choice(["WPA", "WPA2"])
                elif network_type == "Public":
                    security_level = "None"
                else:
                    security_level = self.random.choice(SECURITY_LEVELS)
                
                # Déterminer le type de chiffrement
                encryption_type = None
                if security_level == "WPA3":
                    encryption_type = "AES-256"
                elif security_level in ["WPA2", "Enterprise"]:
                    encryption_type = self.random.choice(["AES-128", "AES-256"])
                elif security_level == "WPA":
                    encryption_type = self.random.choice(["TKIP", "AES-128"])
                elif security_level == "WEP":
                    encryption_type = "WEP"
                elif security_level == "None":
                    encryption_type = "None"
                else:
                    encryption_type = self.random.choice(ENCRYPTION_TYPES)
                
                # Force du signal (1-5)
                signal_strength = self.random.randint(1, 5)
                
                # Est-ce que le réseau est caché?
                is_hidden = 0
                if network_type in ["Corporate", "Secured", "VPN"] and self.random.random() < 0.3:
                    is_hidden = 1
                
                # Nécessite-t-il un hacking?
                requires_hacking = 0
                if security_level in ["WPA3", "Enterprise"] or network_type in ["Corporate", "Secured", "VPN"]:
                    requires_hacking = 1
                
                # Description
                description = f"Un réseau {network_type.lower()} situé dans le bâtiment."
                
                # Métadonnées pour stocker des informations supplémentaires
                metadata = {
                    "building_id": building_id
                }
                
                # Insérer le réseau dans la base de données
                cursor.execute('''
                INSERT INTO networks (id, world_id, building_id, name, ssid, network_type, 
                                    security_level, encryption_type, signal_strength, 
                                    is_hidden, requires_hacking, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    network_id, world_id, building_id, name, ssid, network_type,
                    security_level, encryption_type, signal_strength,
                    is_hidden, requires_hacking, json.dumps(metadata)
                ))
                
                network_ids.append(network_id)
                logger.debug(f"Réseau généré: {name} ({network_type}, {security_level}) pour bâtiment {building_id}")
        
        logger.info(f"Réseaux générés: {len(network_ids)}")
        db.conn.commit()
        return network_ids

    def _generate_hacking_puzzles(self, db, world_id: str, device_ids: List[str], network_ids: List[str]) -> List[str]:
        """Génère des puzzles de hacking pour les appareils et les réseaux"""
        puzzle_ids = []
        
        # Obtenir une nouvelle connexion à la base de données
        db = get_database(db.db_path)
        
        cursor = db.conn.cursor()
        
        # Types de puzzles de hacking
        puzzle_types = [
            'PasswordBruteforce', 'BufferOverflow', 'SequenceMatching', 
            'NetworkRerouting', 'BasicTerminal', 'CodeInjection', 'FirewallBypass'
        ]
        
        # Générer des puzzles pour les appareils
        for device_id in device_ids:
            # Ne pas créer de puzzle pour tous les appareils
            if self.random.random() > 0.3:  # Seulement 30% des appareils ont des puzzles
                continue
                
            # Obtenir des informations sur l'appareil
            cursor.execute('''
            SELECT id, device_type, name, security_level
            FROM devices WHERE id = ?
            ''', (device_id,))
            
            device = cursor.fetchone()
            if not device:
                continue
                
            # Choisir un type de puzzle approprié pour cet appareil
            puzzle_type = None
            if device["device_type"] in ["Server", "MainFrame", "SecuritySystem"]:
                puzzle_type = self.random.choice(["FirewallBypass", "CodeInjection", "BufferOverflow"])
            elif device["device_type"] in ["Laptop", "Desktop"]:
                puzzle_type = self.random.choice(["PasswordBruteforce", "BasicTerminal", "SequenceMatching"])
            elif device["device_type"] == "SmartPhone":
                puzzle_type = self.random.choice(["PasswordBruteforce", "NetworkRerouting"])
            elif device["device_type"] in ["Camera", "SmartDevice"]:
                puzzle_type = self.random.choice(["BasicTerminal", "SequenceMatching"])
            else:
                puzzle_type = self.random.choice(HACKING_PUZZLE_TYPES)
                
            # Difficulté basée sur le niveau de sécurité de l'appareil
            try:
                security_level = device["security_level"]
                if security_level is None:
                    security_level = 1
            except (IndexError, KeyError):
                security_level = 1
                
            difficulty = min(5, max(1, security_level))
            if difficulty < 1:
                difficulty = self.random.randint(1, 3)
                
            # Nom et description
            puzzle_id = str(uuid.uuid4())
            name = f"{puzzle_type} Challenge"
            description = f"Un puzzle de hacking de type {puzzle_type} pour l'appareil {device['name']}."
            
            # Récompenses potentielles
            xp_reward = difficulty * self.random.randint(10, 20)
            credit_reward = difficulty * self.random.randint(50, 200)
            
            # Points d'intérêt connectés à ce puzzle
            connected_poi = self.random.randint(0, 3) if difficulty > 3 else 0
            
            # Métadonnées pour stocker des informations supplémentaires
            metadata = {
                "device_id": device_id,
                "rewards": {
                    "xp": xp_reward,
                    "credits": credit_reward
                },
                "connected_poi": connected_poi,
                "hints": [
                    f"Indice 1 pour {name}",
                    f"Indice 2 pour {name}" if difficulty < 4 else None
                ],
                "solution_steps": self.random.randint(3, 5 + difficulty),
                "failure_consequences": "data_loss" if difficulty > 3 else "none"
            }
            
            # Insérer le puzzle dans la base de données
            cursor.execute('''
            INSERT INTO hacking_puzzles (id, world_id, name, description, puzzle_type, 
                                       difficulty, target_type, target_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                puzzle_id, world_id, name, description, puzzle_type,
                difficulty, "device", device_id, json.dumps(metadata)
            ))
            
            puzzle_ids.append(puzzle_id)
            logger.debug(f"Puzzle de hacking généré: {name} (difficulté: {difficulty}) pour appareil {device_id}")
        
        # Générer des puzzles pour les réseaux
        for network_id in network_ids:
            # Ne pas créer de puzzle pour tous les réseaux
            if self.random.random() > 0.5:  # 50% des réseaux ont des puzzles
                continue
                
            # Obtenir des informations sur le réseau
            cursor.execute('''
            SELECT id, name, network_type, security_level, requires_hacking
            FROM networks WHERE id = ?
            ''', (network_id,))
            
            network = cursor.fetchone()
            if not network:
                continue
                
            # Si le réseau ne nécessite pas de hacking, continuer
            try:
                if network["requires_hacking"] == 0:
                    continue
            except (IndexError, KeyError):
                # Si la colonne n'existe pas ou n'est pas accessible, on utilise 0 par défaut
                continue
                
            # Choisir un type de puzzle approprié pour ce réseau
            puzzle_type = None
            if network["network_type"] in ["Corporate", "VPN", "Secured"]:
                puzzle_type = self.random.choice(["FirewallBypass", "NetworkRerouting", "CodeInjection"])
            elif network["network_type"] in ["WiFi"]:
                puzzle_type = self.random.choice(["PasswordBruteforce", "SequenceMatching"])
            elif network["network_type"] in ["IoT"]:
                puzzle_type = self.random.choice(["BasicTerminal", "SequenceMatching"])
            else:
                puzzle_type = self.random.choice(HACKING_PUZZLE_TYPES)
                
            # Difficulté basée sur le niveau de sécurité du réseau
            try:
                sec_level = network["security_level"]
                if sec_level is None:
                    sec_level = "WEP"
            except (IndexError, KeyError):
                sec_level = "WEP"
                
            if sec_level == "WPA3" or sec_level == "Enterprise":
                difficulty = self.random.randint(4, 5)
            elif sec_level == "WPA2":
                difficulty = self.random.randint(3, 4)
            elif sec_level == "WPA":
                difficulty = self.random.randint(2, 3)
            elif sec_level == "WEP":
                difficulty = self.random.randint(1, 2)
            else:
                difficulty = self.random.randint(1, 3)
                
            # Nom et description
            puzzle_id = str(uuid.uuid4())
            name = f"{network['name']} Access Challenge"
            description = f"Un puzzle de hacking pour accéder au réseau {network['name']}."
            
            # Récompenses potentielles
            xp_reward = difficulty * self.random.randint(15, 25)
            credit_reward = difficulty * self.random.randint(75, 250)
            
            # Nombres de machines accessibles après résolution
            num_accessible_devices = self.random.randint(1, 5)
            
            # Métadonnées pour stocker des informations supplémentaires
            metadata = {
                "network_id": network_id,
                "rewards": {
                    "xp": xp_reward,
                    "credits": credit_reward,
                    "accessible_devices": num_accessible_devices
                },
                "hints": [
                    f"Indice 1 pour {name}",
                    f"Indice 2 pour {name}" if difficulty < 4 else None
                ],
                "solution_steps": self.random.randint(2, 4 + difficulty),
                "trap": True if difficulty > 3 and self.random.random() < 0.3 else False,
                "alarm_trigger_chance": 0.1 * difficulty if difficulty > 2 else 0
            }
            
            # Insérer le puzzle dans la base de données
            cursor.execute('''
            INSERT INTO hacking_puzzles (id, world_id, name, description, puzzle_type, 
                                       difficulty, target_type, target_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                puzzle_id, world_id, name, description, puzzle_type,
                difficulty, "network", network_id, json.dumps(metadata)
            ))
            
            puzzle_ids.append(puzzle_id)
            logger.debug(f"Puzzle de hacking généré: {name} (difficulté: {difficulty}) pour réseau {network_id}")
        
        logger.info(f"Puzzles de hacking générés: {len(puzzle_ids)}")
        db.conn.commit()
        return puzzle_ids

    def _generate_hardware_items(self, db, world_id: str, device_ids: List[str], 
                               building_ids: List[str], character_ids: List[str], 
                               num_items: int) -> List[str]:
        """
        Génère des objets hardware pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            device_ids: Liste des IDs des appareils
            building_ids: Liste des IDs des bâtiments
            character_ids: Liste des IDs des personnages
            num_items: Nombre d'objets à générer
            
        Returns:
            Liste des IDs des objets générés
        """
        hardware_ids = []
        cursor = db.conn.cursor()
        
        # Composants de noms pour générer des noms réalistes
        prefixes = ["Quantum", "Cyber", "Neuro", "Hyper", "Nano", "Tech", "Mega", "Ultra", "Fusion", "Synth"]
        mid_parts = ["Core", "Wave", "Link", "Net", "Sync", "Pulse", "Matrix", "Node", "Flux", "Grid"]
        suffixes = ["XL", "Pro", "Elite", "Max", "Zero", "Nova", "Prime", "Plus", "Alpha", "Omega"]
        
        # Marques connues dans l'univers cyberpunk
        manufacturers = ["NeoTech", "SynthCorp", "QuantumDynamics", "HyperSystems", "FusionTech", 
                        "CyberIndustries", "MegaCorp", "UltraTech", "NanoWorks", "SyncSystems"]
        
        for i in range(num_items):
            # Déterminer si on place cet objet dans un appareil, un bâtiment ou sur un personnage
            location_type = self.random.choice(["device", "building", "character", "shop", "loot"])
            location_id = None
            
            if location_type == "device" and device_ids:
                location_id = self.random.choice(device_ids)
            elif location_type == "building" and building_ids:
                location_id = self.random.choice(building_ids)
            elif location_type == "character" and character_ids:
                location_id = self.random.choice(character_ids)
            elif location_type == "shop":
                if building_ids:
                    location_id = self.random.choice(building_ids)
                else:
                    location_type = "loot"
                    location_id = "world"
            else:  # loot
                location_type = "loot"
                location_id = "world"
                
            # Sélectionner un type de matériel
            hardware_type = self.random.choice(HARDWARE_TYPES)
            
            # Générer un nom en fonction du type de matériel
            prefix = self.random.choice(prefixes)
            mid_part = self.random.choice(mid_parts)
            suffix = self.random.choice(suffixes)
            manufacturer = self.random.choice(manufacturers)
            
            # Nom complet
            name = f"{manufacturer} {prefix}{mid_part} {hardware_type} {suffix}"
            
            # Déterminer la qualité et la rareté
            quality = self.random.choice(HARDWARE_QUALITIES)
            quality_map = {
                "Broken": 0, "Poor": 1, "Standard": 2, 
                "High-End": 3, "Military-Grade": 4, "Prototype": 5, "Custom": 5
            }
            
            quality_level = quality_map.get(quality, 2)
            
            # La rareté dépend de la qualité
            rarity = None
            if quality in ["Prototype", "Custom"]:
                rarity = self.random.choice(["Epic", "Legendary", "Unique"])
            elif quality == "Military-Grade":
                rarity = self.random.choice(["Rare", "Epic"])
            elif quality == "High-End":
                rarity = self.random.choice(["Uncommon", "Rare"])
            elif quality == "Standard":
                rarity = "Common"
            elif quality == "Poor":
                rarity = "Common"
            else:  # Broken
                rarity = self.random.choice(["Common", "Uncommon"])  # Peut être rare si pièce vintage
                
            # Niveau de l'objet (1-10)
            level = min(10, max(1, quality_level * 2 + self.random.randint(-1, 2)))
            
            # Prix basé sur la qualité, la rareté et le niveau
            rarity_multiplier = {
                "Common": 1, "Uncommon": 1.5, "Rare": 3, 
                "Epic": 6, "Legendary": 10, "Unique": 20
            }
            base_price = 100 * level
            price = int(base_price * rarity_multiplier.get(rarity, 1) * (quality_level + 1) * (0.8 + self.random.random() * 0.4))
            
            # Générer des statistiques en fonction du type et de la qualité
            stats = self._generate_hardware_stats(hardware_type, quality, level)
            
            # Description
            if quality in ["Broken", "Poor"]:
                condition = "en mauvais état"
            elif quality == "Standard":
                condition = "en bon état"
            else:
                condition = "en excellent état"
                
            description = f"Un {hardware_type} {condition} de niveau {level}, fabriqué par {manufacturer}."
            
            # Est-ce que l'objet est installé? (pertinent seulement pour les appareils)
            is_installed = 0
            if location_type == "device" and self.random.random() < 0.7:  # 70% des objets dans des appareils sont installés
                is_installed = 1
                
            # Métadonnées supplémentaires
            metadata = {
                "manufacturer": manufacturer,
                "model": f"{prefix}{mid_part} {suffix}",
                "year": 2075 + self.random.randint(-20, 10),
                "weight": self.random.randint(1, 50) / 10.0,  # en kg
                "dimensions": f"{self.random.randint(1, 30)}x{self.random.randint(1, 20)}x{self.random.randint(1, 10)} cm",
                "power_consumption": self.random.randint(5, 100) if hardware_type not in ["USB Drive", "External HDD"] else 0,
                "compatibility": self.random.sample(["Windows", "Linux", "Custom OS", "Any"], k=self.random.randint(1, 4)),
                "special_features": []
            }
            
            # Ajouter des fonctionnalités spéciales pour les objets de haute qualité
            if quality in ["High-End", "Military-Grade", "Prototype", "Custom"]:
                possible_features = [
                    "Encryption intégrée", "Refroidissement avancé", "Overclocking", 
                    "Auto-réparation", "Camouflage EM", "Résistance EMP", 
                    "Boost de performance", "IA assistante", "Cryptominage"
                ]
                
                num_features = min(3, max(1, quality_level - 2))
                metadata["special_features"] = self.random.sample(possible_features, k=num_features)
            
            # ID unique pour l'objet
            hardware_id = str(uuid.uuid4())
            
            # Insérer l'objet dans la base de données
            cursor.execute('''
            INSERT INTO hardware_items 
            (id, world_id, name, description, hardware_type, quality, rarity, level, 
            stats, location_type, location_id, price, is_installed, is_available, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hardware_id, world_id, name, description, hardware_type, quality, rarity, level,
                json.dumps(stats), location_type, location_id, price, is_installed, 1, json.dumps(metadata)
            ))
            
            hardware_ids.append(hardware_id)
            
        logger.info(f"Objets hardware générés: {len(hardware_ids)}")
        db.conn.commit()
        return hardware_ids
        
    def _generate_hardware_stats(self, hardware_type: str, quality: str, level: int) -> Dict:
        """
        Génère des statistiques pour un objet hardware en fonction de son type et de sa qualité
        
        Args:
            hardware_type: Type de hardware
            quality: Qualité du hardware
            level: Niveau du hardware
            
        Returns:
            Dictionnaire de statistiques
        """
        stats = {}
        quality_multiplier = {
            "Broken": 0.3, "Poor": 0.7, "Standard": 1.0, 
            "High-End": 1.5, "Military-Grade": 2.0, "Prototype": 2.5, "Custom": 2.3
        }.get(quality, 1.0)
        
        # Modifier légèrement le multiplicateur pour chaque hardware
        quality_multiplier *= 0.9 + self.random.random() * 0.2
        
        if hardware_type == "CPU":
            stats["processing_power"] = int(level * 10 * quality_multiplier)
            stats["cores"] = min(32, max(1, int(level * 0.8 * quality_multiplier)))
            stats["clock_speed"] = round(2.0 + (level * 0.4 + self.random.random()) * quality_multiplier, 1)
            stats["thermal_output"] = int(10 + level * 5 * (1.1 - quality_multiplier * 0.1))
            
        elif hardware_type == "RAM":
            stats["capacity"] = int(4 * 2 ** (int(level * 0.4 * quality_multiplier)))  # en GB
            stats["speed"] = int(1600 + level * 200 * quality_multiplier)
            stats["latency"] = max(1, int(12 - level * 0.5 * quality_multiplier))
            
        elif hardware_type == "GPU":
            stats["vram"] = int(2 * 2 ** (int(level * 0.4 * quality_multiplier)))  # en GB
            stats["cuda_cores"] = int(500 * level * quality_multiplier)
            stats["clock_speed"] = round(1.0 + (level * 0.2 + self.random.random()) * quality_multiplier, 1)
            stats["thermal_output"] = int(20 + level * 7 * (1.1 - quality_multiplier * 0.1))
            
        elif hardware_type == "Motherboard":
            stats["expansion_slots"] = min(10, max(2, int(2 + level * 0.5 * quality_multiplier)))
            stats["max_ram"] = int(16 * 2 ** (int(level * 0.3 * quality_multiplier)))
            stats["chipset_quality"] = int(level * 10 * quality_multiplier)
            
        elif hardware_type in ["HDD", "SSD", "External HDD", "USB Drive"]:
            capacity_map = {"HDD": 2, "SSD": 1, "External HDD": 2, "USB Drive": 0}
            capacity_base = capacity_map.get(hardware_type, 1)
            stats["capacity"] = int(250 * 2 ** (capacity_base + int(level * 0.3 * quality_multiplier)))  # en GB
            
            if hardware_type == "SSD":
                stats["read_speed"] = int(300 + level * 100 * quality_multiplier)
                stats["write_speed"] = int(200 + level * 80 * quality_multiplier)
            elif hardware_type == "HDD":
                stats["read_speed"] = int(50 + level * 15 * quality_multiplier)
                stats["write_speed"] = int(40 + level * 10 * quality_multiplier)
            else:
                stats["transfer_speed"] = int(30 + level * 20 * quality_multiplier)
                
        elif hardware_type == "Network Card":
            stats["bandwidth"] = int(100 * 2 ** int(level * 0.3 * quality_multiplier))  # en Mbps
            stats["encryption_level"] = int(level * quality_multiplier)
            stats["firewall_strength"] = int(level * quality_multiplier)
            
        elif hardware_type in ["Router", "WiFi Antenna"]:
            stats["range"] = int(20 + level * 5 * quality_multiplier)
            stats["connections"] = int(5 + level * 3 * quality_multiplier)
            stats["encryption_level"] = int(level * quality_multiplier)
            
        elif hardware_type == "Cooling System":
            stats["cooling_capacity"] = int(20 + level * 10 * quality_multiplier)
            stats["noise_level"] = max(1, int(10 - level * 0.5 * quality_multiplier))
            
        elif hardware_type == "Power Supply":
            stats["wattage"] = int(300 + level * 100 * quality_multiplier)
            stats["efficiency"] = min(99, int(70 + level * 2 * quality_multiplier))
            
        elif hardware_type == "Raspberry Pi":
            stats["processing_power"] = int(level * 8 * quality_multiplier)
            stats["memory"] = int(1 * 2 ** (int(level * 0.4 * quality_multiplier)))
            stats["gpio_pins"] = min(40, max(8, int(8 + level * 3 * quality_multiplier)))
            
        else:  # Types génériques ou non listés
            stats["quality_score"] = int(level * 10 * quality_multiplier)
            stats["durability"] = int(level * 5 * quality_multiplier)
            
        # Ajouter des bonus/malus aléatoires
        bonus_stat = self.random.choice(list(stats.keys()))
        bonus_value = stats[bonus_stat] * (0.1 + self.random.random() * 0.2)
        stats[bonus_stat] = int(stats[bonus_stat] + bonus_value)
        
        # Si l'objet est cassé, réduire les stats
        if quality == "Broken":
            for stat in stats:
                if self.random.random() < 0.7:  # 70% de chance que chaque stat soit affectée
                    stats[stat] = int(stats[stat] * (0.1 + self.random.random() * 0.3))
                    
        return stats

    def _generate_consumable_items(self, db, world_id: str, device_ids: List[str], 
                                 building_ids: List[str], character_ids: List[str], 
                                 num_items: int) -> List[str]:
        """
        Génère des objets consommables pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            device_ids: Liste des IDs des appareils
            building_ids: Liste des IDs des bâtiments
            character_ids: Liste des IDs des personnages
            num_items: Nombre d'objets à générer
            
        Returns:
            Liste des IDs des objets générés
        """
        consumable_ids = []
        cursor = db.conn.cursor()
        
        # Composants de noms pour générer des noms réalistes
        prefixes = ["Cyber", "Neuro", "Quantum", "Data", "Code", "Synth", "Hack", "Pulse", "Crypt", "Ghost"]
        suffixes = ["Boost", "Chip", "Key", "Pack", "Patch", "Wave", "Surge", "Lock", "Break", "Link"]
        
        # Fabricants de consommables
        manufacturers = ["DataDynamics", "NeuraSoft", "CyberWare", "CodeFlow", "PulseTech", 
                        "SynthLogic", "QuantumByte", "NetRunner", "GhostSec", "CryptoCorp"]
        
        for i in range(num_items):
            # Déterminer si on place cet objet dans un appareil, un bâtiment ou sur un personnage
            location_type = self.random.choice(["device", "building", "character", "shop", "loot"])
            location_id = None
            
            if location_type == "device" and device_ids:
                location_id = self.random.choice(device_ids)
            elif location_type == "building" and building_ids:
                location_id = self.random.choice(building_ids)
            elif location_type == "character" and character_ids:
                location_id = self.random.choice(character_ids)
            elif location_type == "shop":
                if building_ids:
                    location_id = self.random.choice(building_ids)
                else:
                    location_type = "loot"
                    location_id = "world"
            else:  # loot
                location_type = "loot"
                location_id = "world"
                
            # Sélectionner un type de consommable
            item_type = self.random.choice(CONSUMABLE_TYPES)
            
            # Générer un nom en fonction du type de consommable
            prefix = self.random.choice(prefixes)
            suffix = self.random.choice(suffixes)
            manufacturer = self.random.choice(manufacturers)
            
            # Version du produit
            version = f"v{self.random.randint(1, 9)}.{self.random.randint(0, 9)}"
            
            # Nom complet
            name = f"{manufacturer} {prefix}{suffix} {item_type} {version}"
            
            # Déterminer la rareté
            rarity = self.random.choices(
                ["Common", "Uncommon", "Rare", "Epic", "Legendary"],
                weights=[40, 30, 20, 8, 2],
                k=1
            )[0]
            
            # Nombre d'utilisations
            uses = 1
            if item_type in ["Data Chip", "Crypto Key", "Security Token"]:
                uses = self.random.randint(1, 3)
                if rarity in ["Rare", "Epic", "Legendary"]:
                    uses += self.random.randint(1, 3)
            elif item_type in ["Neural Booster", "Battery Pack"]:
                uses = self.random.randint(2, 5)
                if rarity in ["Rare", "Epic", "Legendary"]:
                    uses += self.random.randint(2, 5)
                    
            # Prix basé sur la rareté et le nombre d'utilisations
            rarity_multiplier = {
                "Common": 1, "Uncommon": 1.5, "Rare": 3, 
                "Epic": 6, "Legendary": 10
            }
            base_price = 50 + self.random.randint(10, 50)
            price = int(base_price * rarity_multiplier.get(rarity, 1) * (uses * 0.5 + 0.5) * (0.8 + self.random.random() * 0.4))
            
            # Générer des effets en fonction du type
            effects = self._generate_consumable_effects(item_type, rarity)
            
            # Description
            description = f"Un {item_type} de qualité {rarity.lower()} avec {uses} utilisation(s). Fabriqué par {manufacturer}."
            
            # Métadonnées supplémentaires
            metadata = {
                "manufacturer": manufacturer,
                "version": version,
                "creation_date": datetime.now().isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=self.random.randint(30, 365))).isoformat(),
                "weight": self.random.randint(1, 20) / 10.0,  # en kg
                "size": self.random.choice(["Tiny", "Small", "Medium"]),
                "storage_condition": self.random.choice(["Normal", "Cool", "Dry", "Secure"]),
                "side_effects": []
            }
            
            # Ajouter des effets secondaires pour les objets rares
            if rarity in ["Rare", "Epic", "Legendary"] and self.random.random() < 0.4:
                possible_side_effects = [
                    "Légère nausée", "Maux de tête temporaires", "Étourdissements", 
                    "Vision floue", "Augmentation de la température corporelle",
                    "Confusion temporaire", "Hyperactivité", "Fatigue"
                ]
                
                num_side_effects = self.random.randint(1, 2)
                metadata["side_effects"] = self.random.sample(possible_side_effects, k=num_side_effects)
            
            # ID unique pour l'objet
            consumable_id = str(uuid.uuid4())
            
            # Insérer l'objet dans la base de données
            cursor.execute('''
            INSERT INTO consumable_items 
            (id, world_id, name, description, item_type, rarity, uses, 
            effects, location_type, location_id, price, is_available, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                consumable_id, world_id, name, description, item_type, rarity, uses,
                json.dumps(effects), location_type, location_id, price, 1, json.dumps(metadata)
            ))
            
            consumable_ids.append(consumable_id)
            
        logger.info(f"Objets consommables générés: {len(consumable_ids)}")
        db.conn.commit()
        return consumable_ids
        
    def _generate_consumable_effects(self, item_type: str, rarity: str) -> Dict:
        """
        Génère des effets pour un objet consommable en fonction de son type et de sa rareté
        
        Args:
            item_type: Type de consommable
            rarity: Rareté du consommable
            
        Returns:
            Dictionnaire d'effets
        """
        effects = {}
        rarity_multiplier = {
            "Common": 1.0, "Uncommon": 1.3, "Rare": 1.8, 
            "Epic": 2.5, "Legendary": 4.0
        }.get(rarity, 1.0)
        
        # Modifier légèrement le multiplicateur pour chaque item
        rarity_multiplier *= 0.9 + self.random.random() * 0.2
        
        if item_type == "Data Chip":
            effects["knowledge_boost"] = int(10 * rarity_multiplier)
            effects["skill_xp"] = int(50 * rarity_multiplier)
            effects["target_skill"] = self.random.choice(["Hacking", "Cryptography", "Programming", "Networks", "Security"])
            
        elif item_type == "Neural Booster":
            effects["mental_boost"] = int(15 * rarity_multiplier)
            effects["focus_duration"] = int(30 * rarity_multiplier)  # en minutes
            effects["cooldown"] = int(240 - 30 * rarity_multiplier)  # en minutes
            
        elif item_type == "Code Fragment":
            effects["unlock_level"] = int(1 + 1 * rarity_multiplier)
            effects["code_quality"] = int(10 * rarity_multiplier)
            effects["bypass_chance"] = min(90, int(30 * rarity_multiplier))  # en %
            
        elif item_type == "Crypto Key":
            effects["encryption_level"] = int(2 * rarity_multiplier)
            effects["unlock_time"] = int(30 - 5 * rarity_multiplier)  # en secondes
            effects["detection_reduction"] = min(90, int(20 * rarity_multiplier))  # en %
            
        elif item_type == "Access Card":
            effects["access_level"] = int(1 + 1 * rarity_multiplier)
            effects["building_types"] = self.random.sample(["Corporate", "Government", "Military", "Research", "Commercial"], 
                                                        k=min(5, max(1, int(1 + rarity_multiplier))))
            effects["duration"] = int(60 * rarity_multiplier)  # en minutes
            
        elif item_type == "Security Token":
            effects["security_level"] = int(2 * rarity_multiplier)
            effects["valid_duration"] = int(30 * rarity_multiplier)  # en minutes
            effects["traceback_protection"] = min(95, int(30 * rarity_multiplier))  # en %
            
        elif item_type == "Firewall Bypass":
            effects["bypass_strength"] = int(15 * rarity_multiplier)
            effects["firewall_levels"] = int(1 + 1 * rarity_multiplier)
            effects["stealth_bonus"] = min(75, int(15 * rarity_multiplier))  # en %
            
        elif item_type == "Signal Jammer":
            effects["jamming_radius"] = int(10 * rarity_multiplier)  # en mètres
            effects["duration"] = int(30 * rarity_multiplier)  # en secondes
            effects["effectiveness"] = min(95, int(50 * rarity_multiplier))  # en %
            
        elif item_type == "Decryption Tool":
            effects["decryption_power"] = int(10 * rarity_multiplier)
            effects["compatible_encryptions"] = min(5, max(1, int(1 + rarity_multiplier)))
            effects["time_reduction"] = min(90, int(20 * rarity_multiplier))  # en %
            
        elif item_type == "Memory Cleaner":
            effects["trace_removal"] = min(100, int(60 * rarity_multiplier))  # en %
            effects["system_optimization"] = int(10 * rarity_multiplier)
            effects["cooldown_reduction"] = min(50, int(10 * rarity_multiplier))  # en %
            
        elif item_type == "Battery Pack":
            effects["energy_boost"] = int(20 * rarity_multiplier)
            effects["duration"] = int(60 * rarity_multiplier)  # en minutes
            effects["device_types"] = min(5, max(1, int(1 + rarity_multiplier)))
            
        else:  # Types génériques ou non listés
            effects["general_boost"] = int(10 * rarity_multiplier)
            effects["duration"] = int(30 * rarity_multiplier)  # en minutes
            
        # Ajouter des bonus/malus aléatoires
        if self.random.random() < 0.3:  # 30% de chance d'avoir un bonus
            if "duration" in effects:
                effects["duration"] = int(effects["duration"] * (1.1 + self.random.random() * 0.3))
            elif list(effects.keys()):
                bonus_stat = self.random.choice(list(effects.keys()))
                if isinstance(effects[bonus_stat], int):
                    bonus_value = effects[bonus_stat] * (0.1 + self.random.random() * 0.2)
                    effects[bonus_stat] = int(effects[bonus_stat] + bonus_value)
                    
        # Ajouter des effets spéciaux pour les objets légendaires et épiques
        if rarity in ["Legendary", "Epic"]:
            if self.random.random() < 0.7:  # 70% de chance d'avoir un effet spécial
                special_effects = {
                    "Data Chip": "Débloque une compétence cachée",
                    "Neural Booster": "Permet de visualiser les flux de données en réalité augmentée",
                    "Code Fragment": "Contourne automatiquement certaines sécurités",
                    "Crypto Key": "Auto-adaptation aux systèmes de sécurité",
                    "Access Card": "Permet d'accéder à des zones restreintes",
                    "Security Token": "Usurpe l'identité d'un admin système",
                    "Firewall Bypass": "Invisibilité temporaire aux systèmes de surveillance",
                    "Signal Jammer": "Peut désactiver temporairement des caméras de sécurité",
                    "Decryption Tool": "Révèle des informations cachées dans les fichiers",
                    "Memory Cleaner": "Efface complètement les traces de votre passage",
                    "Battery Pack": "Surcharge temporaire des systèmes électroniques"
                }
                
                effects["special_effect"] = special_effects.get(item_type, "Effet spécial personnalisé")
                    
        return effects

    def _generate_shops(self, db, world_id: str, location_ids: List[str], building_ids: List[str], num_shops: int) -> List[str]:
        """
        Génère des boutiques pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            location_ids: Liste des IDs des lieux
            building_ids: Liste des IDs des bâtiments
            num_shops: Nombre de boutiques à générer
            
        Returns:
            Liste des IDs des boutiques générées
        """
        shop_ids = []
        cursor = db.conn.cursor()
        
        # Vérifier si la table des boutiques existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                world_id TEXT,
                name TEXT,
                description TEXT,
                shop_type TEXT,
                location_id TEXT,
                building_id TEXT,
                owner_id TEXT DEFAULT NULL,
                faction_id TEXT DEFAULT NULL,
                reputation INTEGER DEFAULT 5,
                price_modifier REAL DEFAULT 1.0,
                is_legal INTEGER DEFAULT 1,
                special_items TEXT DEFAULT NULL,
                services TEXT DEFAULT NULL,
                open_hours TEXT DEFAULT '{"open": "08:00", "close": "20:00"}',
                inventory_refresh_rate INTEGER DEFAULT 24,
                requires_reputation INTEGER DEFAULT 0,
                required_reputation_level INTEGER DEFAULT 0,
                metadata TEXT DEFAULT NULL,
                created_at TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE SET NULL,
                FOREIGN KEY (building_id) REFERENCES buildings (id) ON DELETE SET NULL,
                FOREIGN KEY (owner_id) REFERENCES characters (id) ON DELETE SET NULL,
                FOREIGN KEY (faction_id) REFERENCES factions (id) ON DELETE SET NULL
            )
        ''')
        
        # Vérifier si la table d'inventaire des boutiques existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_inventory (
                id TEXT PRIMARY KEY,
                shop_id TEXT,
                item_id TEXT,
                item_type TEXT,
                quantity INTEGER DEFAULT 1,
                price_modifier REAL DEFAULT 1.0,
                added_at TEXT,
                FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE CASCADE
            )
        ''')
        
        db.conn.commit()
        
        # Association des types de boutiques aux types de bâtiments
        shop_type_building_map = {
            "hardware": ["Shopping Mall", "Commercial", "Corporate HQ"],
            "software": ["Shopping Mall", "Commercial", "Corporate HQ", "Research Lab"],
            "black_market": ["Warehouse", "Apartment Complex", "Nightclub", "Underground"],
            "consumables": ["Shopping Mall", "Convenience Store", "Commercial"],
            "weapons": ["Warehouse", "Military Base", "Underground"],
            "implants": ["Hospital", "Research Lab", "Corporate HQ"],
            "general": ["Shopping Mall", "Commercial"],
            "electronics": ["Shopping Mall", "Commercial", "Research Lab"],
            "digital_services": ["Corporate HQ", "Commercial"],
            "datachips": ["Shopping Mall", "Commercial", "Research Lab"],
            "cybernetics": ["Hospital", "Research Lab", "Corporate HQ"]
        }
        
        # Récupérer les bâtiments disponibles et leurs types
        buildings_with_types = {}
        for building_id in building_ids:
            cursor.execute('SELECT id, building_type, location_id FROM buildings WHERE id = ?', (building_id,))
            building_data = cursor.fetchone()
            if building_data:
                buildings_with_types[building_id] = {
                    "building_type": building_data[1],
                    "location_id": building_data[2]
                }
        
        # Récupérer les types de districts pour une personnalisation de boutique plus précise
        locations_with_types = {}
        for location_id in location_ids:
            cursor.execute('SELECT id, location_type FROM locations WHERE id = ?', (location_id,))
            location_data = cursor.fetchone()
            if location_data:
                locations_with_types[location_id] = location_data[1]
        
        # Définir une fonction pour générer un nom de boutique unique et thématique
        def generate_shop_name(shop_type, district_type=None):
            if self.random.random() < 0.3:  # 30% de chance d'utiliser une marque existante
                brand = self.random.choice(SHOP_BRANDS)
                if self.random.random() < 0.5:  # 50% de chance d'ajouter un suffixe au nom de la marque
                    suffix = self.random.choice(SHOP_NAME_SUFFIXES)
                    return f"{brand} {suffix}"
                return brand
            
            # Sinon, générer un nom unique
            prefix = self.random.choice(SHOP_NAME_PREFIXES)
            suffix = self.random.choice(SHOP_NAME_SUFFIXES)
            
            # Parfois ajouter un élément lié au type de boutique
            if self.random.random() < 0.7:  # 70% de chance
                type_words = {
                    "hardware": ["Gear", "Hardware", "Components", "Parts"],
                    "software": ["Code", "Programs", "Apps", "Software"],
                    "black_market": ["Shadow", "Underground", "Smuggler", "Dark"],
                    "consumables": ["Snack", "Refresh", "Boost", "Supply"],
                    "weapons": ["Arms", "Arsenal", "Defense", "Combat"],
                    "implants": ["Implant", "Augment", "Enhance", "Bio"],
                    "general": ["General", "Goods", "Supply", "Stuff"],
                    "electronics": ["Circuit", "Gadget", "Device", "Tech"],
                    "digital_services": ["Service", "Virtual", "Cloud", "Digital"],
                    "datachips": ["Data", "Memory", "Storage", "Chip"],
                    "cybernetics": ["Cyber", "Enhancement", "Augment", "Neural"]
                }
                
                type_word = self.random.choice(type_words.get(shop_type, ["Tech"]))
                
                # Format aléatoire du nom
                formats = [
                    f"{prefix}{type_word} {suffix}",  # Ex: CyberGear Shop
                    f"{prefix} {type_word} {suffix}",  # Ex: Cyber Gear Shop
                    f"{type_word} {suffix}",  # Ex: Gear Shop
                    f"{prefix} {suffix}"  # Ex: Cyber Shop
                ]
                
                return self.random.choice(formats)
            
            return f"{prefix} {suffix}"  # Ex: Cyber Shop
        
        # Générer le nombre de boutiques demandé
        for i in range(num_shops):
            shop_id = f"shop_{str(uuid.uuid4())}"
            
            # Sélectionner un type de boutique
            shop_type = self.random.choice(SHOP_TYPES)
            
            # Trouver un bâtiment approprié pour ce type de boutique
            suitable_buildings = []
            for b_id, b_info in buildings_with_types.items():
                if b_info["building_type"] in shop_type_building_map.get(shop_type, ["Commercial"]):
                    suitable_buildings.append((b_id, b_info))
            
            # Si aucun bâtiment approprié, choisir un bâtiment aléatoire
            building_id = None
            location_id = None
            if suitable_buildings:
                building_id, building_info = self.random.choice(suitable_buildings)
                location_id = building_info["location_id"]
            elif buildings_with_types:
                building_id, building_info = self.random.choice(list(buildings_with_types.items()))
                location_id = building_info["location_id"]
            elif location_ids:
                location_id = self.random.choice(location_ids)
            
            # Déterminer le district pour adapter le nom de la boutique
            district_type = None
            if location_id and location_id in locations_with_types:
                district_type = locations_with_types[location_id]
            
            # Générer un nom pour la boutique
            shop_name = generate_shop_name(shop_type, district_type)
            
            # Déterminer si la boutique est légale en fonction du type et du district
            is_legal = 1
            if shop_type == "black_market" or shop_type == "weapons":
                is_legal = 0
            elif district_type and "Slums" in district_type:
                is_legal = self.random.choices([0, 1], weights=[0.7, 0.3])[0]
            elif district_type and "Underground" in district_type:
                is_legal = self.random.choices([0, 1], weights=[0.8, 0.2])[0]
            
            # Générer une description
            descriptions = {
                "hardware": [
                    "Une boutique spécialisée dans les composants informatiques et équipements électroniques.",
                    "Vend des pièces détachées pour ordinateurs et autres appareils électroniques.",
                    "Le paradis des bricoleurs à la recherche de composants tech."
                ],
                "software": [
                    "Propose des logiciels pour tous les systèmes d'exploitation courants et personnalisés.",
                    "Spécialiste en programmes de sécurité, utilitaires et logiciels de productivité.",
                    "Applications, jeux et systèmes d'exploitation à la pointe de la technologie."
                ],
                "black_market": [
                    "Un marché clandestin proposant des articles difficiles à trouver par les voies légales.",
                    "Commerce d'articles illégaux ou non traçables. Entrée discrète conseillée.",
                    "Lieu d'échange pour ceux qui préfèrent rester dans l'ombre du système."
                ],
                "consumables": [
                    "Vend des boosts, stimulants et autres consommables pour améliorer vos performances.",
                    "Produits consommables pour restaurer la santé, l'énergie et les capacités cognitives.",
                    "Supplements, boosters, et snacks tech pour tous vos besoins quotidiens."
                ],
                "weapons": [
                    "Arsenal d'armes conventionnelles et high-tech pour la défense personnelle.",
                    "Spécialiste en équipement de combat et de défense pour tous les budgets.",
                    "Armement de pointe pour ceux qui veulent rester en sécurité dans un monde dangereux."
                ],
                "implants": [
                    "Boutique d'implants cybernétiques pour améliorer les capacités humaines.",
                    "Augmentations corporelles et implants nouvelle génération.",
                    "Technologies d'amélioration humaine, des basiques aux plus avancées."
                ],
                "general": [
                    "Propose une variété de produits tech et non-tech pour tous les jours.",
                    "Un peu de tout, de l'équipement électronique aux articles ménagers.",
                    "Fournitures générales et articles divers pour tous vos besoins."
                ]
            }
            
            # Utiliser une description par défaut si le type n'a pas de descriptions spécifiques
            shop_description = self.random.choice(descriptions.get(shop_type, [
                "Une boutique vendant divers produits technologiques.",
                "Un magasin proposant des articles spécialisés.",
                "Un commerce local avec une sélection de produits variés."
            ]))
            
            # Déterminer la réputation et le modificateur de prix
            reputation = self.random.randint(1, 10)
            price_modifier = 1.0
            
            # Ajuster le modificateur de prix en fonction de divers facteurs
            if is_legal == 0:
                price_modifier *= self.random.uniform(1.2, 2.0)  # Plus cher sur le marché noir
            
            if reputation <= 3:
                price_modifier *= self.random.uniform(0.8, 1.1)  # Légèrement moins cher pour les boutiques mal réputées
            elif reputation >= 8:
                price_modifier *= self.random.uniform(1.05, 1.3)  # Plus cher pour les boutiques bien réputées
            
            if district_type:
                if "Financial" in district_type or "Corporate" in district_type:
                    price_modifier *= self.random.uniform(1.1, 1.4)  # Plus cher dans les quartiers riches
                elif "Slums" in district_type:
                    price_modifier *= self.random.uniform(0.6, 0.9)  # Moins cher dans les quartiers pauvres
            
            # Arrondir le modificateur à 2 décimales
            price_modifier = round(price_modifier, 2)
            
            # Insérer la boutique dans la base de données
            cursor.execute('''
                INSERT INTO shops (id, world_id, name, description, shop_type, location_id, building_id,
                                  reputation, price_modifier, is_legal, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (shop_id, world_id, shop_name, shop_description, shop_type, location_id, 
                 building_id, reputation, price_modifier, is_legal))
            
            shop_ids.append(shop_id)
            logger.info(f"Boutique générée: {shop_name} (ID: {shop_id}, Type: {shop_type}, Légal: {bool(is_legal)})")
        
        db.conn.commit()
        return shop_ids
    


    
    def _generate_shop_inventories(self, db, world_id: str, shop_ids: List[str]) -> None:
        """
        Génère des inventaires aléatoires pour les boutiques
        
        Args:
            db: Base de données
            world_id: ID du monde
            shop_ids: Liste des IDs des boutiques
        """
        cursor = db.conn.cursor()
        
        for shop_id in shop_ids:
            # Récupérer les informations de la boutique
            cursor.execute('SELECT shop_type, is_legal, price_modifier FROM shops WHERE id = ?', (shop_id,))
            shop_data = cursor.fetchone()
            
            if not shop_data:
                logger.warning(f"Impossible de générer l'inventaire: boutique {shop_id} non trouvée")
                continue
            
            shop_type, is_legal, price_modifier = shop_data
            
            # Déterminer le nombre d'articles à générer en fonction du type de boutique
            num_items = {
                "hardware": self.random.randint(10, 25),
                "software": self.random.randint(15, 30),
                "black_market": self.random.randint(5, 15),
                "consumables": self.random.randint(20, 40),
                "weapons": self.random.randint(8, 20),
                "implants": self.random.randint(5, 15),
                "general": self.random.randint(15, 35),
                "electronics": self.random.randint(10, 25),
                "digital_services": self.random.randint(5, 15),
                "datachips": self.random.randint(10, 20),
                "cybernetics": self.random.randint(5, 15)
            }.get(shop_type, self.random.randint(10, 20))
            
            # Générer les articles en fonction du type de boutique
            items_added = 0
            
            # Mapper les types de boutiques aux types d'articles qu'elles vendent
            item_types_map = {
                "hardware": [
                    ("hardware", 0.7),  # (type, probabilité)
                    ("consumable", 0.2),
                    ("software", 0.1)
                ],
                "software": [
                    ("software", 0.8),
                    ("hardware", 0.1),
                    ("consumable", 0.1)
                ],
                "black_market": [
                    ("hardware", 0.3),
                    ("consumable", 0.3),
                    ("weapon", 0.3),
                    ("implant", 0.1)
                ],
                "consumables": [
                    ("consumable", 0.9),
                    ("hardware", 0.1)
                ],
                "weapons": [
                    ("weapon", 0.8),
                    ("hardware", 0.1),
                    ("consumable", 0.1)
                ],
                "implants": [
                    ("implant", 0.8),
                    ("consumable", 0.1),
                    ("hardware", 0.1)
                ],
                "general": [
                    ("hardware", 0.3),
                    ("consumable", 0.3),
                    ("software", 0.2),
                    ("weapon", 0.1),
                    ("implant", 0.1)
                ],
                "electronics": [
                    ("hardware", 0.8),
                    ("software", 0.2)
                ],
                "digital_services": [
                    ("software", 0.9),
                    ("hardware", 0.1)
                ],
                "datachips": [
                    ("software", 0.6),
                    ("hardware", 0.4)
                ],
                "cybernetics": [
                    ("implant", 0.7),
                    ("hardware", 0.2),
                    ("consumable", 0.1)
                ]
            }
            
            # Utiliser une distribution par défaut si le type de boutique n'est pas dans la carte
            item_types_distribution = item_types_map.get(shop_type, [
                ("hardware", 0.4),
                ("consumable", 0.3),
                ("software", 0.3)
            ])
            
            # Générer les articles
            for _ in range(num_items):
                # Choisir le type d'article selon la distribution de probabilité
                item_types, weights = zip(*item_types_distribution)
                item_type = self.random.choices(item_types, weights=weights, k=1)[0]
                
                # Générer un nouvel article
                item_id = None
                
                if item_type == "hardware":
                    item_id = self._generate_random_hardware_item(db, world_id, is_legal)
                elif item_type == "consumable":
                    item_id = self._generate_random_consumable_item(db, world_id, is_legal)
                elif item_type == "software":
                    item_id = self._generate_random_software_item(db, world_id, is_legal)
                elif item_type == "weapon":
                    item_id = self._generate_random_weapon_item(db, world_id, is_legal)
                elif item_type == "implant":
                    item_id = self._generate_random_implant_item(db, world_id, is_legal)
                
                if item_id:
                    # Générer un modificateur de prix spécifique à l'article
                    item_price_modifier = price_modifier * self.random.uniform(0.8, 1.2)
                    item_price_modifier = round(item_price_modifier, 2)
                    
                    # Déterminer la quantité
                    quantity = 1
                    if item_type == "consumable":
                        quantity = self.random.randint(1, 10)
                    elif item_type == "software":
                        quantity = self.random.randint(1, 5)
                    
                    # Ajouter l'article à l'inventaire de la boutique
                    inventory_id = f"inv_{str(uuid.uuid4())}"
                    cursor.execute('''
                        INSERT INTO shop_inventory (id, shop_id, item_id, item_type, quantity, price_modifier, added_at)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (inventory_id, shop_id, item_id, item_type, quantity, item_price_modifier))
                    
                    items_added += 1
            
            logger.info(f"Inventaire généré pour boutique {shop_id}: {items_added} articles ajoutés")
        
        db.conn.commit()
    
    def _generate_random_hardware_item(self, db, world_id: str, is_legal: bool) -> Optional[str]:
        """
        Génère un composant hardware aléatoire
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_legal: Si le composant doit être légal
            
        Returns:
            ID du composant généré ou None si échec
        """
        cursor = db.conn.cursor()
        
        # Types de hardware
        hardware_types = HARDWARE_TYPES
        
        # Préfixes pour les noms (marques, séries, etc.)
        prefixes = ["Quantum", "Cyber", "Neuro", "Hyper", "Nano", "Tech", "Mega", "Ultra", "Fusion", "Synth"]
        
        # Suffixes pour les versions, modèles, etc.
        suffixes = ["XL", "Pro", "Elite", "Max", "Zero", "Nova", "Prime", "Plus", "Alpha", "Omega"]
        
        # Niveaux de qualité
        qualities = ["Normal", "Good", "Excellent", "Superior", "Legendary"]
        
        # Choisir un type de hardware
        hardware_type = self.random.choice(hardware_types)
        
        # Générer un nom réaliste
        prefix = self.random.choice(prefixes)
        suffix = self.random.choice(suffixes)
        model = f"{prefix} {hardware_type} {suffix}"
        
        # Choisir une qualité et un niveau
        quality = self.random.choice(qualities)
        level = self.random.randint(1, 10)
        
        # Générer des statistiques en fonction du type et de la qualité
        stats = self._generate_hardware_stats(hardware_type, quality, level)
        
        # Déterminer le prix de base
        base_price = int(level * 100 * (1 + {"Normal": 0, "Good": 0.5, "Excellent": 1, "Superior": 2, "Legendary": 4}[quality]))
        
        # Si non légal, ajuster le nom et le prix
        if not is_legal and self.random.random() < 0.7:  # 70% de chance pour un item illégal dans une boutique illégale
            model = f"Black Market {model}"
            base_price = int(base_price * 1.5)  # Prix plus élevé pour les items illégaux
        
        # Générer une description appropriée
        descriptions = {
            "CPU": ["Processeur haute performance", "Unité de traitement central", "Cerveau de votre système"],
            "RAM": ["Mémoire vive ultra-rapide", "Module de mémoire d'accès aléatoire", "Pour le multitâche intensif"],
            "GPU": ["Carte graphique puissante", "Processeur graphique avancé", "Pour visualisation et gaming"],
            "Motherboard": ["Carte mère de qualité", "Plateforme système centrale", "Base solide pour votre configuration"],
            "HDD": ["Disque dur capacitif", "Stockage de masse", "Pour vos archives importantes"],
            "SSD": ["Disque SSD ultra-rapide", "Stockage à état solide", "Accès données instantané"],
            "Network Card": ["Adaptateur réseau avancé", "Interface de connectivité", "Pour une connexion stable"],
            "Cooling System": ["Système de refroidissement performant", "Contrôle thermique", "Maintient votre système au frais"],
            "Power Supply": ["Alimentation stable", "Source d'énergie fiable", "Alimente vos composants en toute sécurité"],
            "USB Drive": ["Clé USB cryptée", "Stockage portable", "Transporter vos données en sécurité"],
            "External HDD": ["Disque dur externe", "Stockage portable", "Sauvegarde sécurisée"],
            "Router": ["Routeur haut débit", "Hub de connectivité", "Centre de votre réseau personnel"],
            "Bluetooth Adapter": ["Adaptateur Bluetooth", "Connectivité sans fil", "Pour périphériques sans fil"],
            "WiFi Antenna": ["Antenne WiFi amplifiée", "Récepteur sans fil", "Améliore votre portée réseau"],
            "Raspberry Pi": ["Mini-ordinateur polyvalent", "Plateforme de développement", "Pour vos projets DIY"]
        }
        
        description = self.random.choice(descriptions.get(hardware_type, ["Composant matériel de qualité"]))
        
        # Créer l'ID de l'item
        item_id = f"hardware_{str(uuid.uuid4())}"
        
        # Insérer dans la base de données
        try:
            cursor.execute('''
                INSERT INTO hardware_items (id, name, type, description, level, quality, 
                                          stats, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_id, model, hardware_type, description, level, quality, 
                json.dumps(stats), base_price, world_id, 1 if is_legal else 0))
            
            return item_id
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'un item hardware: {e}")
            return None
    
    def _generate_random_consumable_item(self, db, world_id: str, is_legal: bool) -> Optional[str]:
        """
        Génère un objet consommable aléatoire
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_legal: Si l'objet doit être légal
            
        Returns:
            ID de l'objet généré ou None si échec
        """
        cursor = db.conn.cursor()
        
        # Types de consommables
        consumable_types = ["HEALTH", "ENERGY", "FOCUS", "MEMORY", "ANTIVIRUS", 
                           "BOOSTER", "STIMPACK", "FOOD", "DRINK", "DRUG"]
        
        # Niveaux de rareté
        rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        
        # Préfixes pour les noms
        prefixes = ["Cyber", "Neuro", "Quantum", "Data", "Code", "Synth", "Hack", "Pulse", "Crypt", "Ghost"]
        
        # Suffixes basés sur les types
        type_suffixes = {
            "HEALTH": ["Heal", "Medkit", "Bandage", "Cure", "Recovery"],
            "ENERGY": ["Boost", "Battery", "Cell", "Power", "Charge"],
            "FOCUS": ["Focus", "Concentration", "Mind", "Clarity", "Attention"],
            "MEMORY": ["RAM", "Storage", "Cache", "Buffer", "Mem"],
            "ANTIVIRUS": ["Shield", "Protect", "Scan", "Clean", "Defence"],
            "BOOSTER": ["Enhancer", "Amplifier", "Catalyst", "Accelerator", "Intensifier"],
            "STIMPACK": ["Stim", "Injection", "Shot", "Dose", "Formula"],
            "FOOD": ["Ration", "Meal", "Snack", "Bar", "Cube"],
            "DRINK": ["Cola", "Energy", "Hydro", "Refresh", "Liquid"],
            "DRUG": ["Pill", "Capsule", "Tab", "Inhaler", "Patch"]
        }
        
        # Choisir un type et une rareté
        item_type = self.random.choice(consumable_types)
        rarity = self.random.choices(
            ["Common", "Uncommon", "Rare", "Epic", "Legendary"],
            weights=[0.5, 0.3, 0.15, 0.04, 0.01],
            k=1
        )[0]
        
        # Si non légal, privilégier les types plus controversés
        if not is_legal and self.random.random() < 0.8:  # 80% de chance pour un item illégal dans une boutique illégale
            item_type = self.random.choice(["FOCUS", "BOOSTER", "STIMPACK", "DRUG"])
            
            # Augmenter les chances d'avoir un item rare
            rarity = self.random.choices(
                ["Common", "Uncommon", "Rare", "Epic", "Legendary"],
                weights=[0.2, 0.3, 0.3, 0.15, 0.05],
                k=1
            )[0]
        
        # Générer un nom réaliste
        prefix = self.random.choice(prefixes)
        type_suffix = self.random.choice(type_suffixes.get(item_type, ["Tech"]))
        
        # Format du nom selon la rareté
        if rarity in ["Epic", "Legendary"]:
            name = f"{prefix}-X {type_suffix} {rarity}"
        else:
            name = f"{prefix} {type_suffix}"
        
        # Nombre d'utilisations
        uses = {
            "Common": self.random.randint(1, 2),
            "Uncommon": self.random.randint(1, 3),
            "Rare": self.random.randint(2, 4),
            "Epic": self.random.randint(3, 5),
            "Legendary": self.random.randint(4, 6)
        }[rarity]
        
        # Durée des effets (en secondes)
        duration = {
            "HEALTH": 0,  # instantané
            "ENERGY": self.random.randint(30, 120),
            "FOCUS": self.random.randint(60, 300),
            "MEMORY": self.random.randint(60, 300),
            "ANTIVIRUS": self.random.randint(60, 180),
            "BOOSTER": self.random.randint(30, 180),
            "STIMPACK": self.random.randint(30, 120),
            "FOOD": self.random.randint(60, 300),
            "DRINK": self.random.randint(30, 180),
            "DRUG": self.random.randint(120, 600)
        }.get(item_type, 0)
        
        # Temps de recharge (en secondes)
        cooldown = {
            "Common": self.random.randint(5, 30),
            "Uncommon": self.random.randint(10, 60),
            "Rare": self.random.randint(30, 120),
            "Epic": self.random.randint(60, 300),
            "Legendary": self.random.randint(300, 900)
        }[rarity]
        
        # Effets du consommable
        effects = {}
        
        # Effets de base selon le type
        if item_type == "HEALTH":
            effects["health"] = int(10 * (1 + {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 5, "Legendary": 10}[rarity]))
        elif item_type == "ENERGY":
            effects["energy"] = int(10 * (1 + {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 5, "Legendary": 10}[rarity]))
        elif item_type == "FOCUS":
            effects["focus"] = int(5 * (1 + {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 5, "Legendary": 10}[rarity]))
            effects["perception"] = int(2 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
        elif item_type == "MEMORY":
            effects["memory"] = int(10 * (1 + {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 5, "Legendary": 10}[rarity]))
        elif item_type == "ANTIVIRUS":
            effects["defense"] = int(5 * (1 + {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 5, "Legendary": 10}[rarity]))
        elif item_type == "BOOSTER":
            effects["strength"] = int(3 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["agility"] = int(3 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
        elif item_type == "STIMPACK":
            effects["health"] = int(5 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["energy"] = int(5 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
        elif item_type == "FOOD":
            effects["health"] = int(3 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["energy"] = int(7 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
        elif item_type == "DRINK":
            effects["energy"] = int(5 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["focus"] = int(2 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
        elif item_type == "DRUG":
            effects["strength"] = int(5 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["focus"] = int(5 * (1 + {"Common": 1, "Uncommon": 1.5, "Rare": 2, "Epic": 3, "Legendary": 5}[rarity]))
            effects["side_effect"] = "temporary_debuff"  # Effet secondaire négatif
        
        # Ajouter des effets spéciaux pour les raretés supérieures
        if rarity in ["Rare", "Epic", "Legendary"]:
            special_effects = {
                "HEALTH": {"regeneration": True},
                "ENERGY": {"stamina_boost": 10 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},
                "FOCUS": {"critical_chance": 5 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},
                "MEMORY": {"hack_speed": 10 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},
                "ANTIVIRUS": {"firewall": True},
                "BOOSTER": {"speed_boost": 10 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},
                "STIMPACK": {"instant_effect": True},
                "FOOD": {"satiation": 24 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},  # en heures
                "DRINK": {"hydration": 12 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])},  # en heures
                "DRUG": {"enhanced_perception": 10 * ({"Rare": 1, "Epic": 2, "Legendary": 3}[rarity])}
            }
            
            if item_type in special_effects:
                effects.update(special_effects[item_type])
        
        # Générer une description
        descriptions = {
            "HEALTH": ["Restaure la santé instantanément", "Soigne les blessures", "Kit médical d'urgence"],
            "ENERGY": ["Restaure l'énergie", "Donne un coup de boost", "Combat la fatigue"],
            "FOCUS": ["Améliore la concentration", "Aiguise les sens", "Clarifie l'esprit"],
            "MEMORY": ["Améliore la mémoire temporairement", "Augmente la capacité de traitement mental", "Boost cognitif"],
            "ANTIVIRUS": ["Protection contre les logiciels malveillants", "Renforce les défenses numériques", "Bouclier anti-virus"],
            "BOOSTER": ["Augmente temporairement les capacités physiques", "Amplificateur de performance", "Améliore la force"],
            "STIMPACK": ["Combinaison de stimulants", "Injection d'amélioration rapide", "Cocktail de performance"],
            "FOOD": ["Aliment nutritif", "Ration de survie", "Repas complet"],
            "DRINK": ["Boisson énergisante", "Rafraîchissement revigorant", "Hydratation optimale"],
            "DRUG": ["Substance amélioratrice de performance", "Composé neuro-actif", "Stimulant cognitif puissant"]
        }
        
        description = self.random.choice(descriptions.get(item_type, ["Consommable à effet immédiat"]))
        
        # Ajouter des détails selon la rareté
        if rarity == "Uncommon":
            description += " avec effet amélioré."
        elif rarity == "Rare":
            description += " avec effets prolongés et améliorés."
        elif rarity == "Epic":
            description += " de qualité supérieure avec effets multiples."
        elif rarity == "Legendary":
            description += " Produit de qualité exceptionnelle aux effets puissants."
        
        # Déterminer le prix de base
        price_factors = {
            "Common": 1,
            "Uncommon": 2,
            "Rare": 5,
            "Epic": 15,
            "Legendary": 50
        }
        
        base_price = int(50 * price_factors[rarity] * (1 + (uses - 1) * 0.5) * (1 + duration / 300))
        
        # Si non légal, ajuster le prix
        if not is_legal:
            base_price = int(base_price * 1.5)  # Prix plus élevé pour les items illégaux
        
        # Créer l'ID de l'item
        item_id = f"consumable_{str(uuid.uuid4())}"
        
        # Insérer dans la base de données
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consumable_items (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    item_type TEXT,
                    rarity TEXT,
                    uses INTEGER,
                    effects TEXT,
                    duration INTEGER,
                    cooldown INTEGER,
                    price INTEGER,
                    world_id TEXT,
                    is_legal INTEGER DEFAULT 1,
                    FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                INSERT INTO consumable_items (id, name, description, item_type, rarity, 
                                           uses, effects, duration, cooldown, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_id, name, description, item_type, rarity, uses, json.dumps(effects), 
                duration, cooldown, base_price, world_id, 1 if is_legal else 0))
            
            return item_id
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'un item consommable: {e}")
            return None
