"""
Module pour la gestion des lieux dans le monde de YakTaa
"""

import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger("YakTaa.World.Locations")


class BuildingType(Enum):
    """Types de bâtiments disponibles dans le jeu"""
    RESIDENTIAL = auto()       # Résidentiel (appartements, habitations)
    COMMERCIAL = auto()        # Commercial (boutiques, centres commerciaux)
    INDUSTRIAL = auto()        # Industriel (usines, entrepôts) 
    CORPORATE = auto()         # Corporate (bureaux, sièges sociaux)
    GOVERNMENT = auto()        # Gouvernemental (bâtiments officiels)
    SECURITY = auto()          # Sécurité (commissariats, postes de garde)
    MEDICAL = auto()           # Médical (hôpitaux, cliniques)
    ENTERTAINMENT = auto()     # Divertissement (clubs, bars)
    EDUCATION = auto()         # Éducation (écoles, universités)
    TECH = auto()              # Technologie (data centers, laboratoires)
    TRANSPORT = auto()         # Transport (gares, aéroports)
    ABANDONED = auto()         # Abandonné (ruines, bâtiments désaffectés)
    UNDERGROUND = auto()       # Souterrain (bunkers, tunnels)
    SPECIAL = auto()           # Spécial (lieux uniques, points d'intérêt)

    @classmethod
    def from_string(cls, s: str) -> 'BuildingType':
        """Convertit une chaîne en type de bâtiment"""
        mapping = {
            'residential': cls.RESIDENTIAL,
            'commercial': cls.COMMERCIAL,
            'industrial': cls.INDUSTRIAL,
            'corporate': cls.CORPORATE,
            'government': cls.GOVERNMENT,
            'security': cls.SECURITY,
            'medical': cls.MEDICAL,
            'entertainment': cls.ENTERTAINMENT,
            'education': cls.EDUCATION,
            'tech': cls.TECH,
            'transport': cls.TRANSPORT,
            'abandoned': cls.ABANDONED,
            'underground': cls.UNDERGROUND,
            'special': cls.SPECIAL
        }
        return mapping.get(s.lower(), cls.SPECIAL)


class Location:
    """Classe représentant un lieu dans le monde du jeu"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 coordinates: Tuple[float, float] = (0.0, 0.0),
                 security_level: int = 1,
                 population: int = 0,
                 services: List[str] = None,
                 tags: List[str] = None,
                 parent_location_id: Optional[str] = None,
                 is_virtual: bool = False,
                 is_special: bool = False,
                 is_dangerous: bool = False):
        """Initialise un lieu"""
        self.id = id
        self.name = name
        self.description = description
        self.coordinates = coordinates
        self.security_level = security_level
        self.population = population
        self.services = services or []
        self.tags = tags or []
        self.parent_location_id = parent_location_id
        self.is_virtual = is_virtual
        self.is_special = is_special
        self.is_dangerous = is_dangerous
        
        # Connexions vers d'autres lieux
        self.connections: Set[str] = set()
        # Informations sur les connexions (temps, coût, etc.)
        self.connection_info: Dict[str, Dict[str, Any]] = {}
    
    def add_connection(self, location_id: str, 
                       travel_type: str = "standard", 
                       travel_time: float = 1.0, 
                       travel_cost: int = 0,
                       requires_hacking: bool = False,
                       requires_special_access: bool = False) -> None:
        """
        Ajoute une connexion vers un autre lieu
        
        Args:
            location_id: ID du lieu de destination
            travel_type: Type de voyage (vol, train, métro, etc.)
            travel_time: Temps de voyage en heures
            travel_cost: Coût du voyage en crédits
            requires_hacking: Si vrai, nécessite des compétences de hacking pour accéder
            requires_special_access: Si vrai, nécessite un accès spécial
        """
        self.connections.add(location_id)
        self.connection_info[location_id] = {
            "travel_type": travel_type,
            "travel_time": travel_time,
            "travel_cost": travel_cost,
            "requires_hacking": requires_hacking,
            "requires_special_access": requires_special_access
        }
    
    def remove_connection(self, location_id: str) -> None:
        """Supprime une connexion vers un autre lieu"""
        if location_id in self.connections:
            self.connections.remove(location_id)
            if location_id in self.connection_info:
                del self.connection_info[location_id]
    
    def get_connection_info(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur une connexion"""
        return self.connection_info.get(location_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le lieu en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates,
            "security_level": self.security_level,
            "population": self.population,
            "services": self.services,
            "tags": self.tags,
            "parent_location_id": self.parent_location_id,
            "is_virtual": self.is_virtual,
            "is_special": self.is_special,
            "is_dangerous": self.is_dangerous,
            "connections": {loc_id: info for loc_id, info in self.connection_info.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Crée un lieu à partir d'un dictionnaire"""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            coordinates=data["coordinates"],
            security_level=data["security_level"],
            population=data["population"],
            services=data["services"],
            tags=data["tags"],
            parent_location_id=data["parent_location_id"],
            is_virtual=data["is_virtual"],
            is_special=data["is_special"],
            is_dangerous=data["is_dangerous"]
        )
        
        # Ajouter les connexions
        for loc_id, info in data.get("connections", {}).items():
            location.add_connection(
                loc_id,
                travel_type=info.get("travel_type", "standard"),
                travel_time=info.get("travel_time", 1.0),
                travel_cost=info.get("travel_cost", 0),
                requires_hacking=info.get("requires_hacking", False),
                requires_special_access=info.get("requires_special_access", False)
            )
        
        return location


class WorldMap:
    """Classe pour gérer la carte du monde et les lieux"""
    
    def __init__(self, name: str = "Monde"):
        """Initialise la carte du monde"""
        self.name = name
        self.locations: Dict[str, Location] = {}
        self.connections: List[Tuple[str, str, Dict[str, Any]]] = []
        
    def add_location(self, location: Location) -> None:
        """Ajoute un lieu à la carte"""
        self.locations[location.id] = location
        logger.info(f"Lieu ajouté à la carte: {location.name} (ID: {location.id})")
    
    def remove_location(self, location_id: str) -> None:
        """Supprime un lieu de la carte"""
        if location_id in self.locations:
            location = self.locations.pop(location_id)
            # Supprimer les connexions vers ce lieu
            for loc in self.locations.values():
                loc.remove_connection(location_id)
            # Supprimer les connexions depuis ce lieu
            self.connections = [conn for conn in self.connections 
                               if conn[0] != location_id and conn[1] != location_id]
            logger.info(f"Lieu supprimé de la carte: {location.name} (ID: {location.id})")
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Récupère un lieu par son ID"""
        return self.locations.get(location_id)
    
    def add_connection(self, from_id: str, to_id: str, 
                      travel_type: str = "standard", 
                      travel_time: float = 1.0, 
                      travel_cost: int = 0,
                      requires_hacking: bool = False,
                      requires_special_access: bool = False,
                      bidirectional: bool = True) -> bool:
        """
        Ajoute une connexion entre deux lieux
        
        Args:
            from_id: ID du lieu de départ
            to_id: ID du lieu d'arrivée
            travel_type: Type de voyage (vol, train, métro, etc.)
            travel_time: Temps de voyage en heures
            travel_cost: Coût du voyage en crédits
            requires_hacking: Si vrai, nécessite des compétences de hacking pour accéder
            requires_special_access: Si vrai, nécessite un accès spécial
            bidirectional: Si vrai, crée une connexion dans les deux sens
        
        Returns:
            True si la connexion a été ajoutée avec succès, False sinon
        """
        if from_id not in self.locations or to_id not in self.locations:
            logger.warning(f"Impossible d'ajouter une connexion: lieu(x) inexistant(s) {from_id} -> {to_id}")
            return False
        
        # Ajouter la connexion au lieu de départ
        self.locations[from_id].add_connection(
            to_id, travel_type, travel_time, travel_cost, 
            requires_hacking, requires_special_access
        )
        
        # Ajouter la connexion à la liste des connexions
        connection_info = {
            "travel_type": travel_type,
            "travel_time": travel_time,
            "travel_cost": travel_cost,
            "requires_hacking": requires_hacking,
            "requires_special_access": requires_special_access
        }
        self.connections.append((from_id, to_id, connection_info))
        
        # Si bidirectionnelle, ajouter la connexion inverse
        if bidirectional:
            self.locations[to_id].add_connection(
                from_id, travel_type, travel_time, travel_cost, 
                requires_hacking, requires_special_access
            )
            self.connections.append((to_id, from_id, connection_info))
        
        logger.info(f"Connexion ajoutée: {self.locations[from_id].name} -> {self.locations[to_id].name}")
        return True
    
    def connect_locations(self, location_id1: str, location_id2: str, bidirectional: bool = True) -> bool:
        """
        Connecte deux lieux entre eux (version simplifiée de add_connection)
        """
        return self.add_connection(location_id1, location_id2, bidirectional=bidirectional)
    
    def get_all_locations(self) -> List[Location]:
        """Récupère tous les lieux de la carte"""
        return list(self.locations.values())
    
    def get_connected_locations(self, location_id: str) -> List[Location]:
        """Récupère tous les lieux connectés à un lieu donné"""
        if location_id not in self.locations:
            return []
        
        connected_ids = self.locations[location_id].connections
        return [self.locations[loc_id] for loc_id in connected_ids if loc_id in self.locations]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la carte en dictionnaire pour la sauvegarde"""
        return {
            "name": self.name,
            "locations": {loc_id: loc.to_dict() for loc_id, loc in self.locations.items()},
            "connections": [(from_id, to_id, info) for from_id, to_id, info in self.connections]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldMap':
        """Crée une carte à partir d'un dictionnaire"""
        world_map = cls(name=data.get("name", "Monde"))
        
        # Ajouter les lieux
        for loc_data in data.get("locations", {}).values():
            location = Location.from_dict(loc_data)
            world_map.add_location(location)
        
        # Ajouter les connexions
        for from_id, to_id, info in data.get("connections", []):
            world_map.add_connection(
                from_id, to_id,
                travel_type=info.get("travel_type", "standard"),
                travel_time=info.get("travel_time", 1.0),
                travel_cost=info.get("travel_cost", 0),
                requires_hacking=info.get("requires_hacking", False),
                requires_special_access=info.get("requires_special_access", False),
                bidirectional=False  # Éviter les doublons
            )
        
        return world_map
