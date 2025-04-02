"""
Module pour la gestion des villes de YakTaa
Ce module contient la classe CityManager qui gère les villes et leurs caractéristiques.
"""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from yaktaa.world.locations import Location

logger = logging.getLogger("YakTaa.World.CityManager")

class CityManager:
    """
    Classe pour gérer les villes du jeu YakTaa
    Gère les caractéristiques des villes, les quartiers, et les points d'intérêt
    """
    
    def __init__(self, game=None):
        """
        Initialise le gestionnaire de villes
        
        Args:
            game: Référence au jeu principal
        """
        self.game = game
        self.cities = {}  # Dictionnaire des villes {city_id: city_data}
        self.districts = {}  # Dictionnaire des quartiers {district_id: district_data}
        self.points_of_interest = {}  # Dictionnaire des points d'intérêt {poi_id: poi_data}
        
        # Charger les villes depuis la base de données
        self._load_cities()
    
    def _get_db_path(self) -> Path:
        """
        Récupère le chemin vers la base de données
        
        Returns:
            Path: Chemin vers la base de données
        """
        # Chemin vers la base de données dans le dossier dbworld
        db_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "dbworld" / "worlds.db"
        
        if db_path.exists():
            logger.info(f"Base de données trouvée: {db_path}")
            return db_path
        
        logger.warning(f"Base de données non trouvée: {db_path}")
        return db_path
    
    def _load_cities(self):
        """
        Charge les villes depuis la base de données
        """
        logger.info("Chargement des villes depuis la base de données")
        
        db_path = self._get_db_path()
        if not db_path.exists():
            logger.error(f"Base de données non trouvée: {db_path}")
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Vérifier si la table cities existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cities'")
            if not cursor.fetchone():
                logger.warning("Table 'cities' non trouvée dans la base de données")
                conn.close()
                return
            
            # Charger les villes
            try:
                cursor.execute("""
                    SELECT id, name, description, population, security_level, 
                           tech_level, prosperity, location_id
                    FROM cities
                """)
                rows = cursor.fetchall()
                
                for row in rows:
                    city_id = row["id"]
                    self.cities[city_id] = {
                        "id": city_id,
                        "name": row["name"],
                        "description": row["description"],
                        "population": row["population"],
                        "security_level": row["security_level"],
                        "tech_level": row["tech_level"],
                        "prosperity": row["prosperity"],
                        "location_id": row["location_id"],
                        "districts": []
                    }
            except sqlite3.OperationalError:
                logger.warning("Structure de table 'cities' incomplète ou incompatible")
            
            # Vérifier si la table districts existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='districts'")
            if cursor.fetchone():
                try:
                    # Charger les quartiers
                    cursor.execute("""
                        SELECT id, name, description, city_id, security_level
                        FROM districts
                    """)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        district_id = row["id"]
                        city_id = row["city_id"]
                        
                        district_data = {
                            "id": district_id,
                            "name": row["name"],
                            "description": row["description"],
                            "city_id": city_id,
                            "security_level": row["security_level"],
                            "points_of_interest": []
                        }
                        
                        self.districts[district_id] = district_data
                        
                        # Ajouter le quartier à la ville correspondante
                        if city_id in self.cities:
                            self.cities[city_id]["districts"].append(district_id)
                except sqlite3.OperationalError:
                    logger.warning("Structure de table 'districts' incomplète ou incompatible")
            
            # Vérifier si la table points_of_interest existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='points_of_interest'")
            if cursor.fetchone():
                try:
                    # Charger les points d'intérêt
                    cursor.execute("""
                        SELECT id, name, description, district_id, type, is_accessible
                        FROM points_of_interest
                    """)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        poi_id = row["id"]
                        district_id = row["district_id"]
                        
                        poi_data = {
                            "id": poi_id,
                            "name": row["name"],
                            "description": row["description"],
                            "district_id": district_id,
                            "type": row["type"],
                            "is_accessible": bool(row["is_accessible"])
                        }
                        
                        self.points_of_interest[poi_id] = poi_data
                        
                        # Ajouter le point d'intérêt au quartier correspondant
                        if district_id in self.districts:
                            self.districts[district_id]["points_of_interest"].append(poi_id)
                except sqlite3.OperationalError:
                    logger.warning("Structure de table 'points_of_interest' incomplète ou incompatible")
            
            conn.close()
            logger.info(f"Chargement terminé: {len(self.cities)} villes, {len(self.districts)} quartiers, {len(self.points_of_interest)} points d'intérêt")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur SQLite lors du chargement des villes: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des villes: {str(e)}")
    
    def get_city(self, city_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'une ville
        
        Args:
            city_id: Identifiant de la ville
            
        Returns:
            Dict[str, Any]: Informations sur la ville ou None si non trouvée
        """
        return self.cities.get(city_id)
    
    def get_district(self, district_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un quartier
        
        Args:
            district_id: Identifiant du quartier
            
        Returns:
            Dict[str, Any]: Informations sur le quartier ou None si non trouvé
        """
        return self.districts.get(district_id)
    
    def get_point_of_interest(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un point d'intérêt
        
        Args:
            poi_id: Identifiant du point d'intérêt
            
        Returns:
            Dict[str, Any]: Informations sur le point d'intérêt ou None si non trouvé
        """
        return self.points_of_interest.get(poi_id)
    
    def get_city_districts(self, city_id: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les quartiers d'une ville
        
        Args:
            city_id: Identifiant de la ville
            
        Returns:
            List[Dict[str, Any]]: Liste des quartiers de la ville
        """
        city = self.get_city(city_id)
        if not city:
            return []
        
        return [self.districts.get(district_id) for district_id in city["districts"]]
    
    def get_district_pois(self, district_id: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les points d'intérêt d'un quartier
        
        Args:
            district_id: Identifiant du quartier
            
        Returns:
            List[Dict[str, Any]]: Liste des points d'intérêt du quartier
        """
        district = self.get_district(district_id)
        if not district:
            return []
        
        return [self.points_of_interest.get(poi_id) for poi_id in district["points_of_interest"]]
    
    def get_city_for_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère la ville associée à un lieu
        
        Args:
            location_id: Identifiant du lieu
            
        Returns:
            Dict[str, Any]: Informations sur la ville ou None si aucune ville n'est associée
        """
        for city_id, city_data in self.cities.items():
            if city_data.get("location_id") == location_id:
                return city_data
        return None
