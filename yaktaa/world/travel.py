"""
Module pour la gestion des déplacements dans le monde de YakTaa
Ce module contient les classes et fonctions nécessaires pour gérer les déplacements
entre les différents lieux du monde, ainsi que les animations et effets visuels associés.
"""

import logging
import random
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum, auto
from dataclasses import dataclass

from yaktaa.world.locations import Location, WorldMap

logger = logging.getLogger("YakTaa.World.Travel")

class TravelMethod(Enum):
    """Types de méthodes de déplacement disponibles"""
    WALK = auto()          # Marche à pied (courtes distances)
    SUBWAY = auto()        # Métro (intra-ville)
    BUS = auto()           # Bus (intra-ville)
    TRAIN = auto()         # Train (inter-villes)
    CAR = auto()           # Voiture (inter-villes)
    PLANE = auto()         # Avion (longues distances)
    HYPERLOOP = auto()     # Transport ultra-rapide (longues distances)
    TELEPORT = auto()      # Téléportation (virtuelle ou expérimentale)
    BOAT = auto()          # Bateau (traversées maritimes)
    DRONE = auto()         # Drone (zones dangereuses)

@dataclass
class TravelRoute:
    """Représente un itinéraire de voyage entre deux lieux"""
    source_id: str
    destination_id: str
    method: TravelMethod
    travel_time: float  # en heures
    travel_cost: int    # en crédits
    distance: float     # en km
    security_risk: int  # de 0 (sûr) à 10 (très dangereux)
    requires_hacking: bool = False
    requires_special_access: bool = False
    is_hidden: bool = False
    weather_affected: bool = True
    congestion_affected: bool = True

class WeatherCondition(Enum):
    """Conditions météorologiques possibles"""
    CLEAR = auto()         # Ciel dégagé
    CLOUDY = auto()        # Nuageux
    RAINY = auto()         # Pluvieux
    STORMY = auto()        # Orageux
    FOGGY = auto()         # Brouillard
    SNOWY = auto()         # Neigeux
    TOXIC_RAIN = auto()    # Pluie toxique (monde cyberpunk)
    SANDSTORM = auto()     # Tempête de sable
    HEATWAVE = auto()      # Canicule
    EMP_STORM = auto()     # Tempête électromagnétique

class TravelSystem:
    """
    Système de gestion des déplacements dans le monde
    Gère les itinéraires, les méthodes de transport, et les effets météorologiques
    """
    
    def __init__(self, world_map: WorldMap):
        """Initialise le système de déplacement"""
        self.world_map = world_map
        self.routes: Dict[str, Dict[str, List[TravelRoute]]] = {}
        self.current_weather: Dict[str, WeatherCondition] = {}
        self.congestion_levels: Dict[str, float] = {}  # 0.0 à 1.0 (0 = fluide, 1 = bloqué)
        self.player_favorite_routes: Set[Tuple[str, str]] = set()
        self.travel_history: List[Dict[str, Any]] = []
        
        # Initialiser les routes à partir des connexions existantes
        self._initialize_routes()
        self._initialize_weather()
        
        logger.info("Système de déplacement initialisé")
    
    def _initialize_routes(self):
        """Initialise les routes à partir des connexions existantes dans la carte"""
        for location_id, location in self.world_map.locations.items():
            if location_id not in self.routes:
                self.routes[location_id] = {}
            
            for connected_id in location.connections:
                if connected_id not in self.routes[location_id]:
                    self.routes[location_id][connected_id] = []
                
                # Récupérer les informations de connexion
                connection_info = location.get_connection_info(connected_id)
                if not connection_info:
                    continue
                
                # Créer une route par défaut basée sur les informations de connexion
                travel_method = self._determine_travel_method(location, self.world_map.get_location(connected_id))
                
                route = TravelRoute(
                    source_id=location_id,
                    destination_id=connected_id,
                    method=travel_method,
                    travel_time=connection_info.get("travel_time", 1.0),
                    travel_cost=connection_info.get("travel_cost", 0),
                    distance=self._calculate_distance(location, self.world_map.get_location(connected_id)),
                    security_risk=self._calculate_security_risk(location, self.world_map.get_location(connected_id)),
                    requires_hacking=connection_info.get("requires_hacking", False),
                    requires_special_access=connection_info.get("requires_special_access", False)
                )
                
                self.routes[location_id][connected_id].append(route)
        
        logger.info(f"Routes initialisées: {sum(len(dest) for src in self.routes.values() for dest in src.values())} routes au total")
    
    def _initialize_weather(self):
        """Initialise les conditions météorologiques pour chaque lieu"""
        for location_id in self.world_map.locations:
            self.current_weather[location_id] = random.choice(list(WeatherCondition))
            self.congestion_levels[location_id] = random.random() * 0.5  # Initialisation aléatoire entre 0 et 0.5
        
        logger.info("Conditions météorologiques initialisées")
    
    def _determine_travel_method(self, source: Location, destination: Location) -> TravelMethod:
        """Détermine la méthode de transport la plus appropriée entre deux lieux"""
        # Si même parent (même ville), privilégier les transports urbains
        if source.parent_location_id and source.parent_location_id == destination.parent_location_id:
            return random.choice([TravelMethod.WALK, TravelMethod.SUBWAY, TravelMethod.BUS])
        
        # Si lieux virtuels, utiliser la téléportation
        if source.is_virtual or destination.is_virtual:
            return TravelMethod.TELEPORT
        
        # Calculer la distance approximative
        distance = self._calculate_distance(source, destination)
        
        if distance < 5:
            return TravelMethod.WALK
        elif distance < 30:
            return TravelMethod.BUS
        elif distance < 500:
            return TravelMethod.TRAIN
        elif distance < 1000:
            return random.choice([TravelMethod.TRAIN, TravelMethod.CAR])
        else:
            return random.choice([TravelMethod.PLANE, TravelMethod.HYPERLOOP])
    
    def _calculate_distance(self, source: Location, destination: Location) -> float:
        """Calcule la distance approximative entre deux lieux en kilomètres"""
        # Formule de la distance euclidienne (simplifiée)
        x1, y1 = source.coordinates
        x2, y2 = destination.coordinates
        
        # Conversion approximative en kilomètres (très simplifié)
        # Dans un vrai jeu, on utiliserait une formule plus précise (Haversine)
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 * 111
    
    def _calculate_security_risk(self, source: Location, destination: Location) -> int:
        """Calcule le niveau de risque de sécurité pour un trajet"""
        # Moyenne des niveaux de sécurité, inversée (plus le niveau est élevé, moins il y a de risque)
        avg_security = (source.security_level + destination.security_level) / 2
        
        # Inverser l'échelle (10 - niveau) pour que 10 soit le plus risqué
        risk = 10 - avg_security
        
        # Ajuster en fonction des tags
        danger_tags = ["dangereux", "criminel", "radioactif", "toxique", "guerre"]
        for tag in danger_tags:
            if tag in source.tags or tag in destination.tags:
                risk += 1
        
        return max(0, min(10, int(risk)))
    
    def get_available_routes(self, source_id: str, player_hacking_level: int = 0) -> Dict[str, List[TravelRoute]]:
        """
        Récupère toutes les routes disponibles depuis un lieu source
        
        Args:
            source_id: ID du lieu de départ
            player_hacking_level: Niveau de hacking du joueur (pour les routes nécessitant du hacking)
            
        Returns:
            Dictionnaire des routes disponibles par destination
        """
        if source_id not in self.routes:
            return {}
        
        available_routes = {}
        for dest_id, routes in self.routes[source_id].items():
            available_routes[dest_id] = []
            for route in routes:
                # Vérifier si la route nécessite du hacking
                if route.requires_hacking and player_hacking_level < 1:
                    continue
                
                # Vérifier si la route est cachée
                if route.is_hidden:
                    continue
                
                available_routes[dest_id].append(route)
            
            # Si aucune route n'est disponible pour cette destination, supprimer l'entrée
            if not available_routes[dest_id]:
                del available_routes[dest_id]
        
        return available_routes
    
    def calculate_actual_travel_time(self, route: TravelRoute) -> float:
        """Calcule le temps de voyage réel en tenant compte des conditions actuelles"""
        base_time = route.travel_time
        
        # Ajuster en fonction de la météo
        if route.weather_affected and route.source_id in self.current_weather:
            weather = self.current_weather[route.source_id]
            if weather in [WeatherCondition.STORMY, WeatherCondition.TOXIC_RAIN, WeatherCondition.SANDSTORM, WeatherCondition.EMP_STORM]:
                base_time *= 1.5
            elif weather in [WeatherCondition.RAINY, WeatherCondition.FOGGY, WeatherCondition.SNOWY]:
                base_time *= 1.2
        
        # Ajuster en fonction de la congestion
        if route.congestion_affected and route.source_id in self.congestion_levels:
            congestion = self.congestion_levels[route.source_id]
            base_time *= (1 + congestion)
        
        return base_time
    
    def calculate_actual_travel_cost(self, route: TravelRoute) -> int:
        """Calcule le coût de voyage réel en tenant compte des conditions actuelles"""
        base_cost = route.travel_cost
        
        # Ajuster en fonction de la demande (congestion élevée = prix plus élevés)
        if route.congestion_affected and route.source_id in self.congestion_levels:
            congestion = self.congestion_levels[route.source_id]
            base_cost = int(base_cost * (1 + congestion * 0.5))
        
        return base_cost
    
    def travel(self, source_id: str, destination_id: str, route_index: int = 0) -> Dict[str, Any]:
        """
        Effectue un voyage entre deux lieux
        
        Args:
            source_id: ID du lieu de départ
            destination_id: ID du lieu d'arrivée
            route_index: Index de la route à utiliser (si plusieurs sont disponibles)
            
        Returns:
            Informations sur le voyage effectué
        """
        if source_id not in self.routes or destination_id not in self.routes[source_id]:
            return {"success": False, "message": "Route non disponible"}
        
        routes = self.routes[source_id][destination_id]
        if not routes or route_index >= len(routes):
            return {"success": False, "message": "Route non disponible"}
        
        route = routes[route_index]
        
        # Calculer le temps et le coût réels
        actual_time = self.calculate_actual_travel_time(route)
        actual_cost = self.calculate_actual_travel_cost(route)
        
        # Enregistrer le voyage dans l'historique
        travel_record = {
            "source_id": source_id,
            "destination_id": destination_id,
            "method": route.method,
            "time": actual_time,
            "cost": actual_cost,
            "timestamp": time.time(),
            "weather": self.current_weather.get(source_id, WeatherCondition.CLEAR),
            "congestion": self.congestion_levels.get(source_id, 0.0)
        }
        self.travel_history.append(travel_record)
        
        # Mettre à jour les conditions (météo, congestion)
        self._update_conditions()
        
        logger.info(f"Voyage effectué de {source_id} à {destination_id} en {actual_time:.1f} heures pour {actual_cost} crédits")
        
        return {
            "success": True,
            "route": route,
            "actual_time": actual_time,
            "actual_cost": actual_cost,
            "weather": self.current_weather.get(source_id, WeatherCondition.CLEAR),
            "congestion": self.congestion_levels.get(source_id, 0.0)
        }
    
    def _update_conditions(self):
        """Met à jour les conditions météorologiques et de congestion"""
        # Mise à jour aléatoire de la météo (10% de chance de changement)
        for location_id in self.current_weather:
            if random.random() < 0.1:
                self.current_weather[location_id] = random.choice(list(WeatherCondition))
        
        # Mise à jour de la congestion
        for location_id in self.congestion_levels:
            # Variation aléatoire entre -0.1 et +0.1
            variation = (random.random() - 0.5) * 0.2
            self.congestion_levels[location_id] = max(0.0, min(1.0, self.congestion_levels[location_id] + variation))
    
    def add_custom_route(self, source_id: str, destination_id: str, route: TravelRoute) -> bool:
        """Ajoute une route personnalisée entre deux lieux"""
        if source_id not in self.world_map.locations or destination_id not in self.world_map.locations:
            return False
        
        if source_id not in self.routes:
            self.routes[source_id] = {}
        
        if destination_id not in self.routes[source_id]:
            self.routes[source_id][destination_id] = []
        
        self.routes[source_id][destination_id].append(route)
        
        # S'assurer que la connexion existe aussi dans la carte du monde
        source_location = self.world_map.get_location(source_id)
        if source_location and destination_id not in source_location.connections:
            source_location.add_connection(
                destination_id,
                travel_type=route.method.name,
                travel_time=route.travel_time,
                travel_cost=route.travel_cost,
                requires_hacking=route.requires_hacking,
                requires_special_access=route.requires_special_access
            )
        
        logger.info(f"Route personnalisée ajoutée de {source_id} à {destination_id}")
        return True
    
    def unlock_hidden_route(self, source_id: str, destination_id: str, route_index: int) -> bool:
        """Déverrouille une route cachée"""
        if (source_id not in self.routes or 
            destination_id not in self.routes[source_id] or 
            route_index >= len(self.routes[source_id][destination_id])):
            return False
        
        route = self.routes[source_id][destination_id][route_index]
        if route.is_hidden:
            route.is_hidden = False
            logger.info(f"Route cachée déverrouillée de {source_id} à {destination_id}")
            return True
        
        return False
    
    def add_to_favorites(self, source_id: str, destination_id: str) -> bool:
        """Ajoute une route aux favoris du joueur"""
        if source_id not in self.world_map.locations or destination_id not in self.world_map.locations:
            return False
        
        self.player_favorite_routes.add((source_id, destination_id))
        logger.info(f"Route ajoutée aux favoris: {source_id} -> {destination_id}")
        return True
    
    def remove_from_favorites(self, source_id: str, destination_id: str) -> bool:
        """Retire une route des favoris du joueur"""
        if (source_id, destination_id) in self.player_favorite_routes:
            self.player_favorite_routes.remove((source_id, destination_id))
            logger.info(f"Route retirée des favoris: {source_id} -> {destination_id}")
            return True
        return False
    
    def get_favorites(self) -> List[Tuple[str, str]]:
        """Récupère la liste des routes favorites du joueur"""
        return list(self.player_favorite_routes)
    
    def get_travel_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère l'historique des voyages récents"""
        return self.travel_history[-limit:] if self.travel_history else []


class BuildingType(Enum):
    """Types de bâtiments disponibles dans le jeu"""
    RESIDENTIAL = auto()    # Résidentiel
    COMMERCIAL = auto()     # Commercial
    INDUSTRIAL = auto()     # Industriel
    GOVERNMENT = auto()     # Gouvernemental
    CORPORATE = auto()      # Corporatif
    MEDICAL = auto()        # Médical
    EDUCATIONAL = auto()    # Éducatif
    ENTERTAINMENT = auto()  # Divertissement
    SECURITY = auto()       # Sécurité
    UNDERGROUND = auto()    # Souterrain


class Building:
    """Représente un bâtiment dans une ville"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 building_type: BuildingType,
                 security_level: int = 1,
                 floors: int = 1,
                 owner: str = "",
                 services: List[str] = None,
                 tags: List[str] = None,
                 parent_location_id: str = None,
                 is_accessible: bool = True,
                 requires_hacking: bool = False,
                 requires_special_access: bool = False):
        """Initialise un bâtiment"""
        self.id = id
        self.name = name
        self.description = description
        self.building_type = building_type
        self.security_level = security_level
        self.floors = floors
        self.owner = owner
        self.services = services or []
        self.tags = tags or []
        self.parent_location_id = parent_location_id
        self.is_accessible = is_accessible
        self.requires_hacking = requires_hacking
        self.requires_special_access = requires_special_access
        
        # Pièces dans le bâtiment
        self.rooms: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Nouveau bâtiment créé: {self.name} (ID: {self.id})")
    
    def add_room(self, room_id: str, name: str, floor: int, description: str = "", 
                 is_accessible: bool = True, requires_hacking: bool = False) -> None:
        """Ajoute une pièce au bâtiment"""
        self.rooms[room_id] = {
            "name": name,
            "floor": floor,
            "description": description,
            "is_accessible": is_accessible,
            "requires_hacking": requires_hacking,
            "items": [],
            "characters": []
        }
        logger.info(f"Nouvelle pièce ajoutée au bâtiment {self.name}: {name} (ID: {room_id})")
    
    def get_room(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une pièce du bâtiment"""
        return self.rooms.get(room_id)
    
    def get_all_rooms(self) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les pièces du bâtiment"""
        return self.rooms
    
    def get_rooms_by_floor(self, floor: int) -> Dict[str, Dict[str, Any]]:
        """Récupère toutes les pièces d'un étage spécifique"""
        return {room_id: room for room_id, room in self.rooms.items() if room["floor"] == floor}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le bâtiment en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "building_type": self.building_type.name,
            "security_level": self.security_level,
            "floors": self.floors,
            "owner": self.owner,
            "services": self.services,
            "tags": self.tags,
            "parent_location_id": self.parent_location_id,
            "is_accessible": self.is_accessible,
            "requires_hacking": self.requires_hacking,
            "requires_special_access": self.requires_special_access,
            "rooms": self.rooms
        }


class CityManager:
    """
    Gestionnaire de villes et de bâtiments
    Permet de gérer les structures urbaines et les points d'intérêt
    """
    
    def __init__(self, world_map: WorldMap):
        """Initialise le gestionnaire de villes"""
        self.world_map = world_map
        self.buildings: Dict[str, Building] = {}
        self.city_districts: Dict[str, List[str]] = {}  # Mapping ville -> districts
        
        # Initialiser les districts à partir des lieux existants
        self._initialize_districts()
        
        logger.info("Gestionnaire de villes initialisé")
    
    def _initialize_districts(self):
        """Initialise les districts à partir des lieux existants"""
        for location_id, location in self.world_map.locations.items():
            if location.parent_location_id:
                # C'est un district ou un sous-lieu
                parent_id = location.parent_location_id
                if parent_id not in self.city_districts:
                    self.city_districts[parent_id] = []
                self.city_districts[parent_id].append(location_id)
        
        logger.info(f"Districts initialisés: {sum(len(districts) for districts in self.city_districts.values())} districts au total")
    
    def add_building(self, building: Building) -> bool:
        """Ajoute un bâtiment à une ville ou un district"""
        if not building.parent_location_id or building.parent_location_id not in self.world_map.locations:
            logger.warning(f"Impossible d'ajouter le bâtiment {building.name}: parent_location_id invalide")
            return False
        
        self.buildings[building.id] = building
        logger.info(f"Bâtiment {building.name} ajouté à {building.parent_location_id}")
        return True
    
    def get_building(self, building_id: str) -> Optional[Building]:
        """Récupère un bâtiment par son ID"""
        return self.buildings.get(building_id)
    
    def get_buildings_in_location(self, location_id: str) -> List[Building]:
        """Récupère tous les bâtiments dans un lieu spécifique"""
        return [building for building in self.buildings.values() if building.parent_location_id == location_id]
    
    def get_buildings_by_type(self, location_id: str, building_type: BuildingType) -> List[Building]:
        """Récupère tous les bâtiments d'un type spécifique dans un lieu"""
        return [building for building in self.buildings.values() 
                if building.parent_location_id == location_id and building.building_type == building_type]
    
    def get_districts(self, city_id: str) -> List[str]:
        """Récupère tous les districts d'une ville"""
        return self.city_districts.get(city_id, [])
    
    def get_all_cities(self) -> List[Location]:
        """Récupère toutes les villes principales (lieux sans parent)"""
        return [location for location_id, location in self.world_map.locations.items() 
                if not location.parent_location_id]
    
    def add_district(self, district: Location) -> bool:
        """Ajoute un district à une ville"""
        if not district.parent_location_id or district.parent_location_id not in self.world_map.locations:
            logger.warning(f"Impossible d'ajouter le district {district.name}: parent_location_id invalide")
            return False
        
        # Ajouter le district à la carte du monde
        self.world_map.add_location(district)
        
        # Ajouter le district à la liste des districts de la ville
        parent_id = district.parent_location_id
        if parent_id not in self.city_districts:
            self.city_districts[parent_id] = []
        self.city_districts[parent_id].append(district.id)
        
        # Créer une connexion entre la ville et le district
        parent_location = self.world_map.get_location(parent_id)
        if parent_location:
            parent_location.add_connection(district.id, travel_type="local", travel_time=0.1, travel_cost=0)
            district.add_connection(parent_id, travel_type="local", travel_time=0.1, travel_cost=0)
        
        logger.info(f"District {district.name} ajouté à {parent_id}")
        return True
