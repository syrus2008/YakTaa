"""
Module pour le chargement des données test depuis la base de données
Ce module sert de passerelle vers les données de la base de données et ne génère pas de contenu.
Conformément à l'architecture YakTaa, tout le contenu est chargé depuis la base de données.
"""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from yaktaa.world.locations import Location, WorldMap
from yaktaa.characters.character import Character

logger = logging.getLogger("YakTaa.World.TestWorld")

def _get_db_path() -> Path:
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

def create_test_world() -> Tuple[WorldMap, Dict[str, Character]]:
    """
    Charge le monde de test depuis la base de données
    
    Returns:
        Tuple[WorldMap, Dict[str, Character]]: La carte du monde et les personnages
    """
    logger.info("Chargement du monde de test depuis la base de données")
    
    # Création d'une carte vide
    world_map = WorldMap(name="Monde de Test")
    characters = {}
    
    db_path = _get_db_path()
    if not db_path.exists():
        logger.error(f"Base de données non trouvée: {db_path}")
        return world_map, characters
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Charger les lieux
        cursor.execute("SELECT id, name, description, type, coordinates FROM locations")
        rows = cursor.fetchall()
        
        for row in rows:
            location_id = row["id"]
            name = row["name"]
            description = row["description"]
            location_type = row["type"]
            
            # Traitement des coordonnées
            coordinates = row["coordinates"]
            x, y = 0.0, 0.0
            if coordinates:
                try:
                    if coordinates.startswith('[') and coordinates.endswith(']'):
                        import json
                        coords = json.loads(coordinates)
                        if isinstance(coords, list) and len(coords) >= 2:
                            x, y = float(coords[0]), float(coords[1])
                    elif ',' in coordinates:
                        x, y = map(float, coordinates.strip("()").split(","))
                except (ValueError, json.JSONDecodeError) as e:
                    logger.error(f"Erreur de parsing des coordonnées: {str(e)}")
            
            # Création du lieu avec les paramètres compatibles
            location = Location(
                id=location_id,
                name=name,
                description=description,
                coordinates=(x, y),
                security_level=1,
                population=0,
                tags=[location_type] if location_type else []
            )
            
            world_map.add_location(location)
        
        # Charger les connexions
        cursor.execute("SELECT source_id, target_id, description FROM connections")
        rows = cursor.fetchall()
        
        for row in rows:
            source_id = row["source_id"]
            target_id = row["target_id"]
            description = row["description"]
            
            if source_id in world_map.locations and target_id in world_map.locations:
                world_map.add_connection(source_id, target_id, description)
        
        # Charger les personnages
        cursor.execute("SELECT id, name, description, location_id FROM characters")
        rows = cursor.fetchall()
        
        for row in rows:
            character_id = row["id"]
            name = row["name"]
            description = row["description"]
            location_id = row["location_id"]
            
            character = Character(
                id=character_id,
                name=name,
                description=description
            )
            
            characters[character_id] = character
        
        conn.close()
        logger.info(f"Monde de test chargé: {len(world_map.locations)} lieux, {len(world_map.connections)} connexions, {len(characters)} personnages")
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors du chargement du monde de test: {str(e)}")
    
    return world_map, characters

def setup_test_missions(game_or_mission_manager, world_map=None, characters=None) -> None:
    """
    Configure les missions de test depuis la base de données
    
    Args:
        game_or_mission_manager: L'instance du jeu ou du gestionnaire de missions
        world_map: La carte du monde (optionnel)
        characters: Les personnages (optionnel)
    """
    logger.info("Configuration des missions de test depuis la base de données")
    
    # Déterminer le gestionnaire de missions
    mission_manager = None
    if hasattr(game_or_mission_manager, 'mission_manager'):
        # Si c'est une instance de jeu
        mission_manager = game_or_mission_manager.mission_manager
    else:
        # Si c'est directement le gestionnaire de missions
        mission_manager = game_or_mission_manager
    
    if mission_manager is None:
        logger.error("Le gestionnaire de missions n'est pas disponible")
        return
    
    db_path = _get_db_path()
    if not db_path.exists():
        logger.error(f"Base de données non trouvée: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Charger les missions
        cursor.execute("SELECT id, title, description, xp_reward, credit_reward, status FROM missions")
        rows = cursor.fetchall()
        
        for row in rows:
            mission_id = row["id"]
            title = row["title"]
            description = row["description"]
            xp_reward = row["xp_reward"]
            credit_reward = row["credit_reward"]
            status = row["status"]
            
            # Ajouter la mission au gestionnaire de missions
            mission_manager.add_mission_from_db(
                mission_id=mission_id,
                title=title,
                description=description,
                xp_reward=xp_reward,
                credit_reward=credit_reward,
                status=status
            )
        
        # Charger les objectifs des missions
        cursor.execute("""
            SELECT mission_id, id, description, is_completed, is_optional
            FROM mission_objectives
        """)
        rows = cursor.fetchall()
        
        for row in rows:
            mission_id = row["mission_id"]
            objective_id = row["id"]
            description = row["description"]
            is_completed = bool(row["is_completed"])
            is_optional = bool(row["is_optional"])
            
            # Ajouter l'objectif à la mission
            mission_manager.add_objective_to_mission(
                mission_id=mission_id,
                objective_id=objective_id,
                description=description,
                is_completed=is_completed,
                is_optional=is_optional
            )
        
        conn.close()
        logger.info(f"Missions de test configurées")
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la configuration des missions de test: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la configuration des missions: {str(e)}")

class TestWorldGenerator:
    """
    Classe pour générer un monde de test depuis la base de données
    """
    
    @staticmethod
    def generate() -> Tuple[WorldMap, Dict[str, Character]]:
        """
        Génère un monde de test depuis la base de données
        
        Returns:
            Tuple[WorldMap, Dict[str, Character]]: La carte du monde et les personnages
        """
        return create_test_world()
