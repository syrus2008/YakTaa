"""
Module pour la gestion du monde de YakTaa
Ce module contient la classe WorldManager qui gère l'ensemble du monde du jeu.
"""

import logging
from typing import Dict, List, Optional, Any, Set

from yaktaa.world.locations import WorldMap, Location
from yaktaa.world.test_world import create_test_world, setup_test_missions
from yaktaa.world.world_loader import load_world, load_default_world, get_available_worlds

logger = logging.getLogger("YakTaa.World.WorldManager")

class WorldManager:
    """
    Classe pour gérer le monde du jeu YakTaa
    Gère les lieux, les connexions, et les déplacements du joueur
    """
    
    def __init__(self, game=None):
        """Initialise le gestionnaire de monde"""
        self.game = game
        self.world_map = WorldMap()
        self.current_location_id = None
        self.visited_locations: Set[str] = set()
        self.discovered_locations: Set[str] = set()
        self.characters: Dict[str, Any] = {}  # Stockage des personnages du monde
        
        # Charger un monde depuis la base de données ou un monde de test par défaut
        self._load_world()
    
    def _load_world(self, world_id: Optional[str] = None):
        """
        Charge un monde depuis la base de données ou un monde de test par défaut
        
        Args:
            world_id: ID du monde à charger, ou None pour charger le monde par défaut
        """
        try:
            if world_id:
                # Charger un monde spécifique depuis la base de données
                logger.info(f"Chargement du monde depuis la base de données: {world_id}")
                self.world_map, self.characters = load_world(world_id)
                
                if not self.world_map:
                    # Fallback sur le monde de test si le chargement échoue
                    logger.warning(f"Échec du chargement du monde {world_id}, utilisation du monde de test")
                    self._load_test_world()
                    return
            else:
                # Charger le monde par défaut (premier monde trouvé ou monde de test)
                logger.info("Chargement du monde par défaut")
                self.world_map, self.characters = load_default_world()
            
            # Définir le lieu de départ (Premier lieu valide dans la base de données)
            location_found = False
            
            # Liste des lieux à essayer, par ordre de priorité
            locations_to_try = []
            
            # Si des lieux sont disponibles dans la carte
            if self.world_map.locations:
                # Ajouter tous les IDs de villes de la base de données
                try:
                    from yaktaa.world.world_loader import WorldLoader
                    world_loader = WorldLoader()
                    conn = world_loader.get_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM locations WHERE type = 'CITY' OR type = 'city'")
                        for row in cursor.fetchall():
                            location_id = row[0]
                            if location_id not in locations_to_try and location_id in self.world_map.locations:
                                locations_to_try.append(location_id)
                except Exception as e:
                    logger.warning(f"Impossible de récupérer les villes depuis la base de données: {str(e)}")
                
                # Ajouter tous les autres lieux de la carte comme fallback
                for location_id in self.world_map.locations:
                    if location_id not in locations_to_try:
                        locations_to_try.append(location_id)
                
                # Essayer chaque lieu dans l'ordre jusqu'à en trouver un valide
                for location_id in locations_to_try:
                    if location_id in self.world_map.locations:
                        self.current_location_id = location_id
                        location_found = True
                        logger.info(f"Position de départ définie: {location_id}")
                        break
                
                # Si aucun lieu n'a été trouvé, prendre le premier disponible
                if not location_found:
                    self.current_location_id = next(iter(self.world_map.locations))
                    logger.warning(f"Aucun lieu prioritaire trouvé, utilisation de: {self.current_location_id}")
            else:
                logger.warning("Aucun lieu trouvé dans le monde chargé")
                self.current_location_id = None
            
            if self.current_location_id:
                self.visited_locations.add(self.current_location_id)
                self._discover_connected_locations()
            
            # Charger les missions de test si le jeu est initialisé
            if self.game and hasattr(self.game, 'mission_manager'):
                self.load_test_missions()
            
            logger.info(f"Monde '{self.world_map.name}' chargé avec {len(self.world_map.locations)} lieux et {len(self.characters)} personnages")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du monde: {str(e)}", exc_info=True)
            # Fallback sur le monde de test en cas d'erreur
            self._load_test_world()
    
    def _load_test_world(self):
        """Charge une carte de test pour le développement"""
        # Utiliser notre nouveau générateur de monde de test
        self.world_map, self.characters = create_test_world()
        
        # Sélectionner le premier emplacement disponible, pas d'ID codé en dur
        if self.world_map.locations:
            self.current_location_id = next(iter(self.world_map.locations))
            # Initialiser l'ensemble des lieux visités
            if not hasattr(self, 'visited_locations') or self.visited_locations is None:
                self.visited_locations = set()
            self.visited_locations.add(self.current_location_id)
            logger.info(f"Position de départ définie au premier lieu disponible: {self.current_location_id}")
            
            # Découvrir les lieux connectés
            self._discover_connected_locations()
        else:
            logger.warning("Aucun lieu trouvé dans le monde de test")
            self.current_location_id = None
        
        # Charger les missions de test si le jeu est initialisé
        if self.game and hasattr(self.game, 'mission_manager'):
            self.load_test_missions()
        
        logger.info(f"Monde de test chargé avec {len(self.world_map.locations)} lieux et {len(self.characters)} personnages")
    
    def load_test_missions(self):
        """Charge les missions de test dans le gestionnaire de missions"""
        if not self.game or not hasattr(self.game, 'mission_manager'):
            logger.warning("Impossible de charger les missions de test : gestionnaire de missions non disponible")
            return
        
        setup_test_missions(self.game.mission_manager, self.world_map, self.characters)
        logger.info("Missions de test chargées")
    
    def get_available_worlds(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des mondes disponibles dans la base de données
        
        Returns:
            Liste des mondes disponibles
        """
        return get_available_worlds()
    
    def load_specific_world(self, world_id: str) -> bool:
        """
        Charge un monde spécifique depuis la base de données
        
        Args:
            world_id: ID du monde à charger
            
        Returns:
            True si le chargement a réussi, False sinon
        """
        try:
            # Réinitialiser l'état
            self.visited_locations.clear()
            self.discovered_locations.clear()
            
            # Charger le monde
            self._load_world(world_id)
            
            return self.world_map is not None
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du monde {world_id}: {str(e)}", exc_info=True)
            return False
    
    def _discover_connected_locations(self):
        """Découvre les lieux connectés au lieu actuel"""
        if not self.current_location_id:
            return
        
        current_location = self.world_map.get_location(self.current_location_id)
        if not current_location:
            return
        
        # Ajouter tous les lieux connectés aux lieux découverts
        self.discovered_locations.update(current_location.connections)
        logger.info(f"Lieux découverts depuis {current_location.name}: {len(current_location.connections)}")
    
    def get_current_location(self) -> Optional[Location]:
        """Récupère le lieu actuel du joueur"""
        if not self.current_location_id:
            return None
        return self.world_map.get_location(self.current_location_id)
    
    def travel_to(self, location_id: str) -> bool:
        """Déplace le joueur vers un nouveau lieu"""
        # Vérifier que le lieu existe
        if location_id not in self.world_map.locations:
            logger.warning(f"Tentative de voyage vers un lieu inexistant: {location_id}")
            return False
        
        # Vérifier que le lieu est accessible depuis le lieu actuel
        current_location = self.get_current_location()
        if current_location and location_id not in current_location.connections:
            logger.warning(f"Tentative de voyage vers un lieu non connecté: {location_id}")
            return False
        
        # Déplacer le joueur
        self.current_location_id = location_id
        self.visited_locations.add(location_id)
        
        # Découvrir les lieux connectés
        self._discover_connected_locations()
        
        logger.info(f"Voyage vers {self.world_map.locations[location_id].name} réussi")
        return True
    
    def get_available_destinations(self) -> List[Location]:
        """Récupère les destinations disponibles depuis le lieu actuel"""
        if not self.current_location_id:
            return []
        
        return self.world_map.get_connected_locations(self.current_location_id)
    
    def get_all_locations(self) -> List[Location]:
        """Récupère tous les lieux de la carte"""
        return self.world_map.get_all_locations()
    
    def get_visited_locations(self) -> List[Location]:
        """Récupère tous les lieux visités par le joueur"""
        return [self.world_map.get_location(loc_id) for loc_id in self.visited_locations 
                if loc_id in self.world_map.locations]
    
    def get_discovered_locations(self) -> List[Location]:
        """Récupère tous les lieux découverts par le joueur"""
        return [self.world_map.get_location(loc_id) for loc_id in self.discovered_locations 
                if loc_id in self.world_map.locations]
    
    def add_location(self, location: Location) -> None:
        """Ajoute un nouveau lieu à la carte"""
        self.world_map.add_location(location)
    
    def connect_locations(self, location_id1: str, location_id2: str, bidirectional: bool = True) -> bool:
        """Connecte deux lieux entre eux"""
        return self.world_map.connect_locations(location_id1, location_id2, bidirectional)
