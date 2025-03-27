"""
Module pour la gestion des villes et bâtiments de YakTaa
Ce module contient la classe CityManager qui gère les villes et leurs bâtiments.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Set
import uuid
from enum import Enum

from yaktaa.world.locations import Location

logger = logging.getLogger("YakTaa.World.CityManager")

class BuildingType(Enum):
    """Types de bâtiments disponibles dans le jeu"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    CORPORATE = "corporate"
    INDUSTRIAL = "industrial"
    GOVERNMENT = "government"
    ENTERTAINMENT = "entertainment"
    MEDICAL = "medical"
    EDUCATIONAL = "educational"

# Noms génériques pour les bâtiments
CORPORATE_NAMES = [
    "NeoTech", "CyberCorp", "Digitex", "SynthSys", "QuantumDyne",
    "VirtuCorp", "MegaSoft", "ByteWave", "NetSphere", "DataNex",
    "TechFusion", "CyberLink", "NeoCortex", "SiliconEdge", "QuantumPulse"
]

RESIDENTIAL_NAMES = [
    "Résidence Azure", "Tours Horizon", "Complexe Stellaire", "Jardins Suspendus",
    "Appartements Néo-Moderne", "Habitat Luxe", "Résidence Élysée",
    "Domaine Crystal", "Lofts Urbains", "Terrasses Célestes"
]

COMMERCIAL_NAMES = [
    "Cyber Marché", "Néo Bazaar", "Tech Boutique", "Implant Center",
    "Marché Noir", "Échange Digital", "Galerie Virtuelle", "Comptoir Quantique",
    "Arcade Commerciale", "Emporium Futuriste"
]

INDUSTRIAL_NAMES = [
    "Usine Automatisée", "Complexe Industriel", "Centre de Production",
    "Raffinerie Synthétique", "Manufacture Robotique", "Usine de Composants",
    "Centre Logistique", "Entrepôt Sécurisé", "Usine d'Assemblage",
    "Complexe de Fabrication"
]

MEDICAL_NAMES = [
    "Clinique Cybernétique", "Hôpital Central", "Centre Médical Avancé",
    "Institut de Biotech", "Laboratoire Génétique", "Clinique d'Augmentation",
    "Centre de Soins Intégrés", "Hôpital Virtuel", "Complexe Médical Néo",
    "Clinique Régénération"
]

ENTERTAINMENT_NAMES = [
    "Club Néon", "Arène Virtuelle", "Casino Quantique", "Théâtre Holographique",
    "Bar Cyberpunk", "Lounge Digital", "Salle VR Premium", "Discothèque Laser",
    "Cinéma Immersif", "Centre de Divertissement Futuriste"
]

GOVERNMENT_NAMES = [
    "Centre Administratif", "Complexe Gouvernemental", "Ministère de la Sécurité",
    "Bureau Central", "Département de Contrôle", "Agence de Régulation",
    "Quartier Général", "Palais de Justice", "Centre de Surveillance",
    "Administration Municipale"
]

EDUCATIONAL_NAMES = [
    "Académie Technique", "Université Virtuelle", "Institut de Recherche",
    "Centre d'Apprentissage", "École de Hacking", "Bibliothèque Numérique",
    "Campus Scientifique", "Centre de Formation", "Laboratoire Éducatif",
    "Conservatoire Digital"
]

# Descriptions génériques pour les bâtiments
BUILDING_DESCRIPTIONS = {
    BuildingType.RESIDENTIAL: [
        "Un complexe résidentiel moderne avec des appartements de différentes tailles.",
        "Une tour d'habitation luxueuse avec vue panoramique sur la ville.",
        "Un ensemble d'appartements abordables pour la classe moyenne.",
        "Un immeuble résidentiel sécurisé avec contrôle d'accès avancé.",
        "Un complexe d'habitations modulaires avec jardins suspendus."
    ],
    BuildingType.COMMERCIAL: [
        "Un centre commercial animé proposant une variété de boutiques et services.",
        "Un marché couvert où se mêlent vendeurs légitimes et marché noir.",
        "Une galerie marchande high-tech avec les dernières innovations.",
        "Un bazar cyberpunk où l'on trouve de tout, du légal à l'illégal.",
        "Un complexe commercial avec boutiques, restaurants et divertissements."
    ],
    BuildingType.CORPORATE: [
        "Un gratte-ciel imposant abritant le siège d'une mégacorporation.",
        "Un complexe de bureaux ultramoderne avec sécurité renforcée.",
        "Une tour corporative aux vitres teintées cachant des secrets bien gardés.",
        "Un bâtiment d'entreprise à l'architecture futuriste et intimidante.",
        "Un centre d'affaires abritant plusieurs filiales corporatives."
    ],
    BuildingType.INDUSTRIAL: [
        "Une usine automatisée produisant des composants électroniques.",
        "Un complexe industriel avec chaînes de montage robotisées.",
        "Un entrepôt logistique géré par des IA et des drones.",
        "Une raffinerie traitant des matériaux synthétiques avancés.",
        "Un centre de production avec sécurité et surveillance constante."
    ],
    BuildingType.MEDICAL: [
        "Un hôpital de pointe offrant des soins médicaux et augmentations cybernétiques.",
        "Une clinique spécialisée dans les implants et modifications corporelles.",
        "Un centre médical combinant médecine traditionnelle et technologies avancées.",
        "Un laboratoire de recherche médicale travaillant sur des traitements expérimentaux.",
        "Un complexe hospitalier avec différents départements spécialisés."
    ],
    BuildingType.ENTERTAINMENT: [
        "Un club nocturne populaire avec musique, danse et divertissements variés.",
        "Un casino high-tech proposant jeux traditionnels et expériences virtuelles.",
        "Un complexe de divertissement avec arcades, salles VR et bars.",
        "Un théâtre proposant spectacles holographiques et performances live.",
        "Un centre de loisirs avec diverses activités immersives."
    ],
    BuildingType.GOVERNMENT: [
        "Un bâtiment administratif gérant les affaires municipales.",
        "Un complexe gouvernemental hautement sécurisé.",
        "Un centre de contrôle surveillant la ville et ses habitants.",
        "Un palais de justice traitant les affaires légales et criminelles.",
        "Un bâtiment officiel abritant divers services publics."
    ],
    BuildingType.EDUCATIONAL: [
        "Une université moderne formant les esprits aux technologies de pointe.",
        "Un centre de recherche travaillant sur des projets innovants.",
        "Une bibliothèque numérique contenant d'immenses bases de données.",
        "Un campus éducatif avec salles de classe et laboratoires.",
        "Un institut spécialisé dans un domaine technique particulier."
    ]
}

def generate_random_building(building_type=None, city_name="", security_level=5):
    """
    Génère un bâtiment aléatoire
    
    Args:
        building_type: Type de bâtiment (aléatoire si None)
        city_name: Nom de la ville pour personnaliser le nom du bâtiment
        security_level: Niveau de sécurité de base (1-10)
        
    Returns:
        Dictionnaire contenant les informations du bâtiment
    """
    # Déterminer le type de bâtiment si non spécifié
    if building_type is None:
        building_type = random.choice(list(BuildingType))
    
    # Générer un nom en fonction du type
    if building_type == BuildingType.CORPORATE:
        name = random.choice(CORPORATE_NAMES)
    elif building_type == BuildingType.RESIDENTIAL:
        name = random.choice(RESIDENTIAL_NAMES)
    elif building_type == BuildingType.COMMERCIAL:
        name = random.choice(COMMERCIAL_NAMES)
    elif building_type == BuildingType.INDUSTRIAL:
        name = random.choice(INDUSTRIAL_NAMES)
    elif building_type == BuildingType.MEDICAL:
        name = random.choice(MEDICAL_NAMES)
    elif building_type == BuildingType.ENTERTAINMENT:
        name = random.choice(ENTERTAINMENT_NAMES)
    elif building_type == BuildingType.GOVERNMENT:
        name = random.choice(GOVERNMENT_NAMES)
    elif building_type == BuildingType.EDUCATIONAL:
        name = random.choice(EDUCATIONAL_NAMES)
    else:
        name = f"Bâtiment {random.randint(100, 999)}"
    
    # Ajouter le nom de la ville pour certains types de bâtiments
    if building_type in [BuildingType.GOVERNMENT, BuildingType.MEDICAL, BuildingType.EDUCATIONAL] and city_name:
        name = f"{name} de {city_name}"
    
    # Déterminer le nombre d'étages en fonction du type
    if building_type == BuildingType.CORPORATE:
        floors = random.randint(20, 50)
    elif building_type == BuildingType.RESIDENTIAL:
        floors = random.randint(5, 30)
    elif building_type == BuildingType.COMMERCIAL:
        floors = random.randint(2, 10)
    elif building_type == BuildingType.INDUSTRIAL:
        floors = random.randint(1, 5)
    elif building_type == BuildingType.MEDICAL:
        floors = random.randint(5, 15)
    elif building_type == BuildingType.ENTERTAINMENT:
        floors = random.randint(1, 8)
    elif building_type == BuildingType.GOVERNMENT:
        floors = random.randint(5, 20)
    elif building_type == BuildingType.EDUCATIONAL:
        floors = random.randint(3, 12)
    else:
        floors = random.randint(1, 10)
    
    # Ajuster le niveau de sécurité en fonction du type
    if building_type == BuildingType.CORPORATE:
        security_level = min(security_level + random.randint(1, 3), 10)
    elif building_type == BuildingType.GOVERNMENT:
        security_level = min(security_level + random.randint(2, 4), 10)
    elif building_type == BuildingType.ENTERTAINMENT:
        security_level = max(security_level - random.randint(0, 2), 1)
    
    # Générer une description
    if building_type in BUILDING_DESCRIPTIONS:
        description = random.choice(BUILDING_DESCRIPTIONS[building_type])
    else:
        description = f"Un bâtiment {building_type.value} standard."
    
    # Créer et retourner le dictionnaire du bâtiment
    return {
        "name": name,
        "type": building_type,
        "description": description,
        "security_level": security_level,
        "floors": floors
    }

class Building:
    """Classe représentant un bâtiment dans une ville"""
    
    def __init__(self, id: str, name: str, type: str, description: str, 
                 security_level: int = 1, floors: int = 1, city_id: str = None):
        """
        Initialise un bâtiment
        
        Args:
            id: Identifiant unique du bâtiment
            name: Nom du bâtiment
            type: Type du bâtiment (résidentiel, commercial, etc.)
            description: Description du bâtiment
            security_level: Niveau de sécurité (1-10)
            floors: Nombre d'étages
            city_id: ID de la ville où se trouve le bâtiment
        """
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        self.security_level = security_level
        self.floors = floors
        self.city_id = city_id
        self.networks = []  # Réseaux disponibles dans le bâtiment
        self.current_floor = 1  # Étage actuel
        self.explored_floors = set([1])  # Étages explorés
        self.rooms = {}  # Dictionnaire des pièces par ID
        
        # Génération automatique des pièces de base
        self._generate_basic_rooms()
    
    def _generate_basic_rooms(self):
        """Génère les pièces de base pour le bâtiment"""
        import random
        
        # Types de pièces possibles selon le type de bâtiment
        room_types = {
            "RESIDENTIAL": ["Entrée", "Salon", "Cuisine", "Chambre", "Salle de bain"],
            "CORPORATE": ["Hall d'entrée", "Bureau", "Salle de conférence", "Cafétéria", "Salle serveur"],
            "COMMERCIAL": ["Entrée", "Zone de vente", "Stockage", "Bureau", "Salle de pause"],
            "INDUSTRIAL": ["Entrée", "Zone de production", "Entrepôt", "Laboratoire", "Salle de contrôle"],
            "GOVERNMENT": ["Hall d'entrée", "Bureau", "Archive", "Salle de réunion", "Zone sécurisée"],
            "ENTERTAINMENT": ["Entrée", "Zone principale", "Coulisses", "Bar", "VIP"],
            "MEDICAL": ["Accueil", "Salle d'attente", "Cabinet", "Laboratoire", "Pharmacie"]
        }
        
        # Déterminer le type de bâtiment pour choisir les types de pièces
        building_type = self.type.upper() if hasattr(self, 'type') else "COMMERCIAL"
        if building_type not in room_types:
            building_type = "COMMERCIAL"  # Type par défaut
        
        # Nombre de pièces par étage (entre 2 et 5)
        rooms_per_floor = random.randint(2, 5)
        
        # Générer des pièces pour chaque étage
        for floor in range(1, self.floors + 1):
            for i in range(rooms_per_floor):
                # Choisir un type de pièce
                room_type = random.choice(room_types[building_type])
                
                # Générer un ID unique pour la pièce
                room_id = f"room_{self.id}_{floor}_{i}"
                
                # Nom de la pièce
                room_name = f"{room_type} {i+1}" if i > 0 else room_type
                
                # Description de la pièce
                descriptions = {
                    "Entrée": "Une entrée standard avec quelques sièges et un comptoir d'accueil.",
                    "Hall d'entrée": "Un grand hall avec un plafond haut et plusieurs portes.",
                    "Salon": "Une pièce confortable avec des canapés et une table basse.",
                    "Cuisine": "Une cuisine équipée avec des appareils modernes.",
                    "Chambre": "Une chambre simple avec un lit et une armoire.",
                    "Salle de bain": "Une petite salle de bain avec douche et lavabo.",
                    "Bureau": "Un bureau fonctionnel avec un ordinateur et des classeurs.",
                    "Salle de conférence": "Une grande salle avec une table de conférence et des écrans.",
                    "Cafétéria": "Un espace de restauration avec plusieurs tables et une zone de service.",
                    "Salle serveur": "Une pièce remplie de serveurs informatiques et de câbles, climatisée.",
                    "Zone de vente": "Un espace ouvert avec des présentoirs et des produits.",
                    "Stockage": "Une pièce remplie d'étagères et de boîtes.",
                    "Salle de pause": "Une petite pièce avec un distributeur et quelques chaises.",
                    "Zone de production": "Un grand espace avec des machines et des postes de travail.",
                    "Entrepôt": "Un vaste espace de stockage avec des étagères hautes.",
                    "Laboratoire": "Une pièce avec des équipements scientifiques et des postes de travail.",
                    "Salle de contrôle": "Une pièce avec plusieurs écrans et panneaux de contrôle.",
                    "Archive": "Une pièce remplie de dossiers et de documents.",
                    "Zone sécurisée": "Une zone à accès restreint avec des mesures de sécurité renforcées.",
                    "Zone principale": "L'espace principal où se déroulent les activités.",
                    "Coulisses": "Une zone réservée au personnel, cachée du public.",
                    "Bar": "Un comptoir avec des boissons et quelques tables.",
                    "VIP": "Une zone exclusive réservée aux clients importants.",
                    "Accueil": "Un comptoir d'accueil avec une salle d'attente.",
                    "Salle d'attente": "Une pièce avec des chaises et des magazines.",
                    "Cabinet": "Une pièce équipée pour les consultations médicales.",
                    "Pharmacie": "Un espace de stockage et de distribution de médicaments."
                }
                
                room_description = descriptions.get(room_type, f"Une pièce standard de type {room_type}.")
                
                # Ajouter la pièce au dictionnaire
                self.rooms[room_id] = {
                    "id": room_id,
                    "name": room_name,
                    "type": room_type,
                    "floor": floor,
                    "description": room_description,
                    "items": [],  # Liste des objets dans la pièce
                    "characters": [],  # Liste des personnages dans la pièce
                    "networks": []  # Réseaux disponibles dans la pièce
                }
    
    def get_all_rooms(self):
        """Retourne toutes les pièces du bâtiment"""
        return self.rooms
    
    def get_rooms_by_floor(self, floor: int):
        """Retourne les pièces d'un étage spécifique"""
        return {room_id: room for room_id, room in self.rooms.items() if room["floor"] == floor}
    
    def get_room(self, room_id: str):
        """Retourne une pièce spécifique par son ID"""
        return self.rooms.get(room_id)

class CityManager:
    """
    Classe pour gérer les villes et leurs bâtiments dans YakTaa
    """
    
    def __init__(self, game=None):
        """Initialise le gestionnaire de ville"""
        self.game = game
        self.buildings: Dict[str, Building] = {}  # Tous les bâtiments par ID
        self.city_buildings: Dict[str, Dict[str, Building]] = {}  # Bâtiments par ville
        self.current_building_id = None  # Bâtiment actuel
        
        logger.info("Gestionnaire de ville initialisé")
    
    def generate_buildings_for_city(self, city_id: str, city_name: str, city_type: str, 
                                   security_level: int, min_buildings: int = 5, max_buildings: int = 15) -> Dict[str, Building]:
        """
        Génère des bâtiments pour une ville
        
        Args:
            city_id: ID de la ville
            city_name: Nom de la ville
            city_type: Type de la ville (métropole, ville moyenne, etc.)
            security_level: Niveau de sécurité de la ville (1-10)
            min_buildings: Nombre minimum de bâtiments à générer
            max_buildings: Nombre maximum de bâtiments à générer
            
        Returns:
            Dictionnaire des bâtiments générés
        """
        # Déterminer le nombre de bâtiments en fonction du type de ville
        if city_type.lower() in ["metropole", "métropole", "capitale"]:
            num_buildings = random.randint(max(10, min_buildings), max(20, max_buildings))
        elif city_type.lower() in ["grande ville", "city"]:
            num_buildings = random.randint(max(7, min_buildings), max(15, max_buildings))
        else:  # Petite ville ou village
            num_buildings = random.randint(min_buildings, min(10, max_buildings))
        
        # Générer les bâtiments
        city_buildings = {}
        
        # Assurer une variété de types de bâtiments
        building_types = list(BuildingType)
        
        for i in range(num_buildings):
            # Sélectionner un type de bâtiment, avec une préférence pour certains types selon la ville
            if i < len(building_types):
                # Garantir au moins un bâtiment de chaque type
                building_type = building_types[i]
            else:
                # Pondérer les types en fonction du type de ville
                if city_type.lower() in ["metropole", "métropole", "capitale"]:
                    weights = {
                        BuildingType.CORPORATE: 3,
                        BuildingType.COMMERCIAL: 3,
                        BuildingType.RESIDENTIAL: 2,
                        BuildingType.INDUSTRIAL: 1,
                        BuildingType.GOVERNMENT: 2,
                        BuildingType.ENTERTAINMENT: 2,
                        BuildingType.MEDICAL: 1,
                        BuildingType.EDUCATIONAL: 1
                    }
                elif city_type.lower() in ["grande ville", "city"]:
                    weights = {
                        BuildingType.CORPORATE: 2,
                        BuildingType.COMMERCIAL: 3,
                        BuildingType.RESIDENTIAL: 3,
                        BuildingType.INDUSTRIAL: 2,
                        BuildingType.GOVERNMENT: 1,
                        BuildingType.ENTERTAINMENT: 2,
                        BuildingType.MEDICAL: 1,
                        BuildingType.EDUCATIONAL: 1
                    }
                else:  # Petite ville ou village
                    weights = {
                        BuildingType.CORPORATE: 1,
                        BuildingType.COMMERCIAL: 3,
                        BuildingType.RESIDENTIAL: 4,
                        BuildingType.INDUSTRIAL: 2,
                        BuildingType.GOVERNMENT: 1,
                        BuildingType.ENTERTAINMENT: 1,
                        BuildingType.MEDICAL: 1,
                        BuildingType.EDUCATIONAL: 1
                    }
                
                # Sélectionner un type en fonction des poids
                building_type = random.choices(
                    list(weights.keys()),
                    weights=list(weights.values()),
                    k=1
                )[0]
            
            # Générer un bâtiment aléatoire
            building_data = generate_random_building(
                building_type=building_type,
                city_name=city_name,
                security_level=min(security_level + random.randint(-2, 2), 10)
            )
            
            # Créer l'objet Building
            building_id = f"building_{city_id}_{uuid.uuid4().hex[:8]}"
            building = Building(
                id=building_id,
                name=building_data["name"],
                type=building_data["type"].name,
                description=building_data["description"],
                security_level=building_data["security_level"],
                floors=building_data["floors"],
                city_id=city_id
            )
            
            # Ajouter le bâtiment aux dictionnaires
            self.buildings[building_id] = building
            city_buildings[building_id] = building
        
        # Stocker les bâtiments pour cette ville
        self.city_buildings[city_id] = city_buildings
        
        logger.info(f"Généré {len(city_buildings)} bâtiments pour la ville {city_name} (ID: {city_id})")
        
        return city_buildings
    
    def get_buildings_in_city(self, city_id: str) -> Dict[str, Building]:
        """
        Récupère les bâtiments d'une ville
        
        Args:
            city_id: ID de la ville
            
        Returns:
            Dictionnaire des bâtiments dans la ville
        """
        # Vérifier si nous avons déjà généré des bâtiments pour cette ville
        if city_id in self.city_buildings:
            return self.city_buildings[city_id]
        
        # Si non, générer des bâtiments pour cette ville
        if self.game and hasattr(self.game, 'world_manager'):
            city = self.game.world_manager.world_map.get_location(city_id)
            if city:
                # Déterminer le type de ville en fonction des tags ou de la population
                city_type = "ville"  # Type par défaut
                
                # Si la ville a des tags, utiliser le premier comme type
                if hasattr(city, 'tags') and city.tags:
                    for tag in city.tags:
                        if tag in ["metropole", "métropole", "capitale", "grande ville", "city", "village"]:
                            city_type = tag
                            break
                # Sinon, déterminer le type en fonction de la population
                elif hasattr(city, 'population'):
                    if city.population > 1000000:
                        city_type = "métropole"
                    elif city.population > 100000:
                        city_type = "grande ville"
                    else:
                        city_type = "ville"
                
                logger.info(f"Génération de bâtiments pour {city.name} (type: {city_type})")
                
                return self.generate_buildings_for_city(
                    city_id=city_id,
                    city_name=city.name,
                    city_type=city_type,
                    security_level=getattr(city, 'security_level', 5)
                )
        
        # En cas d'échec, retourner un dictionnaire vide
        logger.warning(f"Impossible de générer des bâtiments pour la ville {city_id}")
        return {}
    
    def enter_building(self, building_id: str) -> bool:
        """
        Entre dans un bâtiment
        
        Args:
            building_id: ID du bâtiment
            
        Returns:
            True si l'entrée a réussi, False sinon
        """
        if building_id in self.buildings:
            self.current_building_id = building_id
            building = self.buildings[building_id]
            building.current_floor = 1  # Commencer au rez-de-chaussée
            logger.info(f"Entrée dans le bâtiment {building.name} (ID: {building_id})")
            return True
        else:
            logger.warning(f"Tentative d'entrée dans un bâtiment inconnu: {building_id}")
            return False
    
    def exit_building(self) -> bool:
        """
        Sort du bâtiment actuel
        
        Returns:
            True si la sortie a réussi, False sinon
        """
        if self.current_building_id:
            building = self.buildings.get(self.current_building_id)
            if building:
                logger.info(f"Sortie du bâtiment {building.name} (ID: {self.current_building_id})")
            self.current_building_id = None
            return True
        else:
            logger.warning("Tentative de sortie alors qu'aucun bâtiment n'est actif")
            return False
    
    def get_current_building(self) -> Optional[Building]:
        """
        Récupère le bâtiment actuel
        
        Returns:
            Objet Building actuel ou None si aucun bâtiment n'est actif
        """
        if self.current_building_id:
            return self.buildings.get(self.current_building_id)
        return None
    
    def change_floor(self, floor: int) -> bool:
        """
        Change d'étage dans le bâtiment actuel
        
        Args:
            floor: Numéro de l'étage cible
            
        Returns:
            True si le changement a réussi, False sinon
        """
        building = self.get_current_building()
        if not building:
            logger.warning("Tentative de changement d'étage sans bâtiment actif")
            return False
        
        if floor < 1 or floor > building.floors:
            logger.warning(f"Étage invalide: {floor} (bâtiment a {building.floors} étages)")
            return False
        
        building.current_floor = floor
        building.explored_floors.add(floor)
        logger.info(f"Changement vers l'étage {floor} dans {building.name}")
        return True
    
    def get_current_floor(self) -> int:
        """
        Récupère l'étage actuel
        
        Returns:
            Numéro de l'étage actuel ou 0 si aucun bâtiment n'est actif
        """
        building = self.get_current_building()
        if building:
            return building.current_floor
        return 0
        
    def update(self, delta_time: float) -> None:
        """
        Met à jour le gestionnaire de ville
        
        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour en secondes
        """
        # Pour l'instant, aucune mise à jour n'est nécessaire
        # Cette méthode pourrait être utilisée pour des événements aléatoires dans les bâtiments,
        # des changements de sécurité, etc.
        pass
    
    def get_building(self, building_id: str) -> Optional[Building]:
        """
        Récupère un bâtiment par son ID
        
        Args:
            building_id: ID du bâtiment à récupérer
            
        Returns:
            Le bâtiment correspondant à l'ID, ou None s'il n'existe pas
        """
        # Parcourir toutes les villes pour trouver le bâtiment
        for city_buildings in self.city_buildings.values():
            if building_id in city_buildings:
                return city_buildings[building_id]
        
        # Si le bâtiment n'est pas trouvé, retourner None
        logger.debug(f"Bâtiment non trouvé: {building_id}")
        return None
