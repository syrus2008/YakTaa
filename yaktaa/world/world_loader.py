"""
Module pour charger des mondes depuis la base de données de l'éditeur YakTaa
Ce module permet au jeu de charger les mondes créés dans l'éditeur de monde YakTaa.
"""

import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from yaktaa.world.locations import Location, WorldMap
from yaktaa.characters.character import Character, Attribute, Skill
from yaktaa.world.test_world import TestWorldGenerator

logger = logging.getLogger("YakTaa.World.WorldLoader")

class WorldLoader:
    """
    Classe pour charger des mondes depuis la base de données de l'éditeur YakTaa
    """
    
    def __init__(self):
        """Initialise le chargeur de monde"""
        self.db_path = self._get_editor_db_path()
        logger.info(f"Chargeur de monde initialisé avec la base de données: {self.db_path}")
    
    def _get_editor_db_path(self) -> Path:
        """
        Récupère le chemin vers la base de données de l'éditeur
        Recherche la base de données dans plusieurs emplacements possibles
        """
        # Récupération du chemin de l'exécutable
        exe_dir = Path(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)))
        
        # Vérification du chemin après installation (dossier data/ à côté de l'exécutable)
        installed_db_path = exe_dir.parent / "data" / "worlds.db"
        if installed_db_path.exists():
            logger.info(f"Base de données trouvée dans le dossier d'installation: {installed_db_path}")
            return installed_db_path
            
        # Chemin absolu direct vers la base de données de l'éditeur
        editor_db_path = Path("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")
        
        if editor_db_path.exists():
            logger.info(f"Base de données de l'éditeur trouvée directement à: {editor_db_path}")
            return editor_db_path
        
        # Chemin absolu basé sur le chemin actuel
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        editor_db_path = base_dir / "yaktaa_world_editor" / "worlds.db"
        
        if editor_db_path.exists():
            logger.info(f"Base de données de l'éditeur trouvée à: {editor_db_path}")
            return editor_db_path
            
        # Liste des emplacements possibles pour la base de données
        possible_paths = [
            # Chemin dans le dossier d'installation
            exe_dir / "data" / "worlds.db",
            exe_dir / "worlds.db",
            
            # Chemins standards après installation
            Path(os.path.expandvars('%APPDATA%')) / "YakTaa" / "Worlds" / "worlds.db",
            Path(os.path.expandvars('%LOCALAPPDATA%')) / "YakTaa" / "Worlds" / "worlds.db",
            
            # Chemin relatif dans le dossier de l'éditeur
            Path("..") / "yaktaa_world_editor" / "worlds.db",
            Path("..") / "yaktaa_world_editor" / "yaktaa_worlds.db",
            
            # Chemin par défaut dans le dossier utilisateur
            Path.home() / "yaktaa_worlds.db",
            Path.home() / "worlds.db",
            
            # Chemin relatif dans le dossier courant
            Path("yaktaa_worlds.db"),
            Path("worlds.db"),
            
            # Chemin relatif dans le dossier parent
            Path("..") / "yaktaa_worlds.db",
            Path("..") / "worlds.db",
        ]
        
        # Vérifier chaque emplacement possible
        for path in possible_paths:
            if path.exists():
                logger.info(f"Base de données trouvée à: {path}")
                return path
        
        # Si aucune base de données n'est trouvée, utiliser le chemin par défaut et afficher un avertissement clair
        logger.warning(f"ATTENTION: Aucune base de données trouvée! Chemin par défaut utilisé: {editor_db_path}")
        logger.warning("Assurez-vous que la base de données existe à cet emplacement pour que les boutiques fonctionnent correctement.")
        return editor_db_path
    
    def _parse_coordinates(self, coordinates: str) -> Tuple[float, float]:
        """
        Parse les coordonnées depuis une chaîne de caractères ou un tableau JSON
        
        Args:
            coordinates: Coordonnées au format chaîne ou JSON
        
        Returns:
            Tuple contenant les coordonnées x et y
        """
        try:
            if coordinates is None:
                return 0.0, 0.0
                
            # Si les coordonnées sont au format JSON array
            if coordinates.startswith('[') and coordinates.endswith(']'):
                import json
                coords = json.loads(coordinates)
                if isinstance(coords, list) and len(coords) >= 2:
                    return float(coords[0]), float(coords[1])
            
            # Si les coordonnées sont au format (x,y)
            elif ',' in coordinates:
                x, y = map(float, coordinates.strip("()").split(","))
                return x, y
                
            logger.error(f"Format de coordonnées non reconnu: {coordinates}")
            return 0.0, 0.0
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors du parsing des coordonnées: {coordinates} - {str(e)}")
            return 0.0, 0.0
    
    def get_available_worlds(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des mondes disponibles dans la base de données
        
        Returns:
            Liste des mondes disponibles avec leur ID, nom et description
        """
        worlds = []
        
        if not self.db_path.exists():
            logger.warning(f"Base de données non trouvée: {self.db_path}")
            return worlds
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, description FROM worlds")
            rows = cursor.fetchall()
            
            for row in rows:
                worlds.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"]
                })
            
            conn.close()
            logger.info(f"{len(worlds)} mondes trouvés dans la base de données")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des mondes: {str(e)}")
        
        return worlds
    
    def load_world(self, world_id: str) -> Tuple[Optional[WorldMap], Dict[str, Character]]:
        """
        Charge un monde depuis la base de données
        
        Args:
            world_id: ID du monde à charger
            
        Returns:
            Tuple contenant la carte du monde et les personnages, ou (None, {}) en cas d'erreur
        """
        if not self.db_path.exists():
            logger.warning(f"Base de données non trouvée: {self.db_path}")
            return None, {}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Vérifier que le monde existe
            cursor.execute("SELECT * FROM worlds WHERE id = ?", (world_id,))
            world_data = cursor.fetchone()
            
            if not world_data:
                logger.warning(f"Monde non trouvé: {world_id}")
                conn.close()
                return None, {}
            
            # Créer la carte du monde
            world_map = WorldMap(world_data["name"])
            
            # Charger les lieux
            cursor.execute("SELECT * FROM locations WHERE world_id = ?", (world_id,))
            locations = cursor.fetchall()
            
            for loc_data in locations:
                location = Location(
                    id=loc_data["id"],
                    name=loc_data["name"],
                    description=loc_data["description"],
                    coordinates=self._parse_coordinates(loc_data["coordinates"]),
                    security_level=loc_data["security_level"],
                    population=loc_data["population"],
                    services=loc_data["services"].split(",") if loc_data["services"] else [],
                    tags=loc_data["tags"].split(",") if loc_data["tags"] else [],
                    parent_location_id=loc_data["parent_location_id"],
                    is_virtual=bool(loc_data["is_virtual"]),
                    is_special=bool(loc_data["is_special"]),
                    is_dangerous=bool(loc_data["is_dangerous"])
                )
                world_map.add_location(location)
            
            # Charger les connexions
            cursor.execute("""
                SELECT * FROM connections 
                WHERE world_id = ?
            """, (world_id,))
            connections = cursor.fetchall()
            
            for conn_data in connections:
                world_map.add_connection(
                    conn_data["source_id"],
                    conn_data["destination_id"],
                    conn_data["travel_type"],
                    conn_data["travel_time"],
                    conn_data["travel_cost"],
                    requires_hacking=bool(conn_data["requires_hacking"]),
                    requires_special_access=bool(conn_data["requires_special_access"])
                )
            
            # Charger les personnages
            cursor.execute("SELECT * FROM characters WHERE world_id = ?", (world_id,))
            character_rows = cursor.fetchall()
            
            characters = {}
            for char_data in character_rows:
                # Créer les attributs et compétences de base
                attributes = {}
                skills = {}
                
                # Charger les attributs depuis le JSON si disponible
                if char_data["attributes"]:
                    try:
                        import json
                        attrs_data = json.loads(char_data["attributes"])
                        for attr_name, attr_value in attrs_data.items():
                            attributes[attr_name] = Attribute(
                                id=attr_name,
                                name=attr_name.capitalize(),
                                description=f"Attribut {attr_name.capitalize()} du personnage",
                                value=attr_value
                            )
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Erreur lors du parsing des attributs: {e}")
                
                # Attributs par défaut si non définis
                if not attributes:
                    attributes = {
                        "intelligence": Attribute(
                            id="intelligence",
                            name="Intelligence",
                            description="Capacité à résoudre des problèmes complexes et à apprendre",
                            value=3
                        ),
                        "reflexes": Attribute(
                            id="reflexes",
                            name="Réflexes",
                            description="Vitesse de réaction et agilité physique",
                            value=3
                        ),
                        "technique": Attribute(
                            id="technique",
                            name="Technique",
                            description="Maîtrise des outils et technologies",
                            value=3
                        ),
                        "chance": Attribute(
                            id="chance",
                            name="Chance",
                            description="Probabilité que des événements aléatoires soient favorables",
                            value=3
                        )
                    }
                
                # Charger les compétences depuis le JSON si disponible
                if char_data["skills"]:
                    try:
                        import json
                        skills_data = json.loads(char_data["skills"])
                        for skill_name, skill_value in skills_data.items():
                            skills[skill_name] = Skill(
                                id=skill_name,
                                name=skill_name.capitalize(),
                                description=f"Compétence {skill_name.capitalize()} du personnage",
                                level=skill_value
                            )
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Erreur lors du parsing des compétences: {e}")
                
                # Compétences explicites de la base de données
                skills["hacking"] = Skill(
                    id="hacking",
                    name="Hacking",
                    description="Capacité à infiltrer des systèmes informatiques et à manipuler des données",
                    level=char_data["hacking_level"]
                )
                
                skills["combat"] = Skill(
                    id="combat",
                    name="Combat",
                    description="Aptitude au combat rapproché et à distance",
                    level=char_data["combat_level"]
                )
                
                # Compétence sociale (charisma dans la base de données)
                if "charisma" in char_data:
                    skills["social"] = Skill(
                        id="social",
                        name="Social",
                        description="Capacité à interagir efficacement avec d'autres personnes",
                        level=char_data["charisma"]
                    )
                else:
                    skills["social"] = Skill(
                        id="social",
                        name="Social",
                        description="Capacité à interagir efficacement avec d'autres personnes",
                        level=3
                    )
                
                # Créer le personnage avec les paramètres de base
                character = Character(
                    name=char_data["name"],
                    character_type="npc"  # Tous les personnages de la base de données sont des PNJ
                )
                
                # Ajouter les attributs supplémentaires
                character.attributes = attributes
                character.skills = skills
                
                # Ajouter les autres propriétés du personnage
                if "description" in char_data:
                    character.description = char_data["description"]
                if "profession" in char_data:
                    character.profession = char_data["profession"]
                if "faction" in char_data:
                    character.faction = char_data["faction"]
                if "location_id" in char_data:
                    character.location_id = char_data["location_id"]
                
                # Ajouter le personnage au dictionnaire avec son ID comme clé
                characters[char_data["id"]] = character
            
            # Charger les appareils
            cursor.execute("SELECT * FROM devices WHERE world_id = ?", (world_id,))
            device_rows = cursor.fetchall()
            
            # Créer un dictionnaire pour stocker les appareils par emplacement
            devices_by_location = {}
            
            for device_data in device_rows:
                location_id = device_data["location_id"]
                if location_id not in devices_by_location:
                    devices_by_location[location_id] = []
                
                # Créer un dictionnaire avec les données de l'appareil
                device = {
                    "id": device_data["id"],
                    "name": device_data["name"],
                    "description": device_data["description"] if "description" in device_data else "",
                    "device_type": device_data["device_type"] if "device_type" in device_data else "unknown",
                    "os": device_data["os"] if "os" in device_data else "unknown",
                    "security_level": device_data["security_level"] if "security_level" in device_data else 1,
                    "is_connected": bool(device_data["is_connected"]) if "is_connected" in device_data else False,
                    "owner_id": device_data["owner_id"] if "owner_id" in device_data else ""
                }
                
                # Ajouter l'appareil à la liste pour cet emplacement
                devices_by_location[location_id].append(device)
            
            logger.info(f"Chargé {len(device_rows)} appareils pour {len(devices_by_location)} emplacements")
            
            # Charger les fichiers
            try:
                cursor.execute("SELECT * FROM files WHERE world_id = ?", (world_id,))
                file_rows = cursor.fetchall()
                
                for file_data in file_rows:
                    device_id = file_data["device_id"]
                    # Parcourir tous les appareils dans notre dictionnaire devices_by_location
                    for location_id, devices in devices_by_location.items():
                        for device in devices:
                            if device["id"] == device_id:
                                if "files" not in device:
                                    device["files"] = []
                                
                                device["files"].append({
                                    "id": file_data["id"],
                                    "name": file_data["name"],
                                    "file_type": file_data["file_type"] if "file_type" in file_data else "txt",
                                    "content": file_data["content"] if "content" in file_data else "",
                                    "size": file_data["size"] if "size" in file_data else 0,
                                    "is_encrypted": bool(file_data["is_encrypted"]) if "is_encrypted" in file_data else False,
                                    "security_level": file_data["security_level"] if "security_level" in file_data else 1,
                                    "owner_id": file_data["owner_id"] if "owner_id" in file_data else ""
                                })
            except sqlite3.OperationalError:
                logger.warning("Table 'files' non trouvée dans la base de données. Les fichiers ne seront pas chargés.")
            
            conn.close()
            logger.info(f"Monde '{world_map.name}' chargé avec succès: {len(world_map.locations)} lieux, {len(characters)} personnages")
            
            return world_map, characters
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du chargement du monde: {str(e)}")
            return None, {}
    
    def load_default_world(self) -> Tuple[WorldMap, Dict[str, Character]]:
        """
        Charge le monde par défaut (premier monde trouvé ou monde de test)
        
        Returns:
            Tuple contenant la carte du monde et les personnages
        """
        worlds = self.get_available_worlds()
        
        if worlds:
            # Charger le premier monde trouvé
            world_id = worlds[0]["id"]
            world_map, characters = self.load_world(world_id)
            
            if world_map:
                return world_map, characters
        
        # Fallback: créer un monde de test
        logger.warning("Aucun monde trouvé dans la base de données, création d'un monde de test")
        generator = TestWorldGenerator()
        return generator.generate()
    
    def get_connection(self):
        """
        Fournit une connexion à la base de données des mondes.
        Cette méthode est utilisée par le ShopManager pour accéder aux données des boutiques.
        
        Returns:
            Un objet de connexion sqlite3
        
        Raises:
            Exception: Si la connexion à la base de données échoue
        """
        try:
            if not self.db_path.exists():
                logger.warning(f"Base de données non trouvable à {self.db_path}. Création d'une DB en mémoire avec structure minimale.")
                conn = sqlite3.connect(":memory:")
                cursor = conn.cursor()
                
                # Créer les tables minimales nécessaires pour éviter les erreurs
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    description TEXT,
                    x_coord REAL,
                    y_coord REAL
                )
                ''')
                
                # Insérer au moins une ville par défaut
                cursor.execute('''
                INSERT INTO locations (id, name, type, description, x_coord, y_coord)
                VALUES (1, 'Night City', 'CITY', 'Une métropole cyberpunk', 0.0, 0.0)
                ''')
                
                # Créer d'autres tables essentielles
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shops (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    description TEXT,
                    location_id INTEGER,
                    FOREIGN KEY (location_id) REFERENCES locations (id)
                )
                ''')
                
                conn.commit()
                return conn
            
            return sqlite3.connect(str(self.db_path))
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {e}")
            raise


def get_available_worlds() -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour récupérer les mondes disponibles
    
    Returns:
        Liste des mondes disponibles
    """
    loader = WorldLoader()
    return loader.get_available_worlds()


def load_world(world_id: str) -> Tuple[Optional[WorldMap], Dict[str, Character]]:
    """
    Fonction utilitaire pour charger un monde par son ID
    
    Args:
        world_id: ID du monde à charger
        
    Returns:
        Tuple contenant la carte du monde et les personnages
    """
    loader = WorldLoader()
    return loader.load_world(world_id)


def load_default_world() -> Tuple[WorldMap, Dict[str, Character]]:
    """
    Fonction utilitaire pour charger le monde par défaut
    
    Returns:
        Tuple contenant la carte du monde et les personnages
    """
    loader = WorldLoader()
    return loader.load_default_world()
