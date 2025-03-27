"""
Module principal pour la génération de mondes
Contient la méthode principale generate_world et les appels aux sous-générateurs
"""

import uuid
import json
import logging
from typing import Optional, List

from database import get_database
from constants import *

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Main")

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
        name = self.generate_world_name()
    
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
        city_ids = self.generate_cities(db, world_id, num_cities)
        
        # Générer les districts
        logger.info("Génération des districts...")
        district_ids = self.generate_districts(db, world_id, city_ids, num_districts_per_city)
        
        # Générer les lieux spéciaux
        special_location_ids = []
        if num_special_locations > 0:
            logger.info("Génération des lieux spéciaux...")
            special_location_ids = self.generate_special_locations(db, world_id, num_special_locations)
        
        # Combiner tous les lieux
        all_location_ids = city_ids + district_ids + special_location_ids
        
        # Générer les connexions entre lieux
        logger.info("Génération des connexions...")
        self.generate_connections(db, world_id, all_location_ids)
        
        # Générer les bâtiments
        logger.info("Génération des bâtiments...")
        building_ids = self.generate_buildings(db, world_id, all_location_ids)
        
        # Générer les personnages
        logger.info("Génération des personnages...")
        character_ids = self.generate_characters(db, world_id, all_location_ids, num_characters)
        
        # Générer les appareils électroniques
        logger.info("Génération des appareils...")
        device_ids = self.generate_devices(db, world_id, all_location_ids, character_ids, num_devices)
        
        # Générer les réseaux
        logger.info("Génération des réseaux...")
        network_ids = self.generate_networks(db, world_id, building_ids)
        
        # Générer les puzzles de hacking
        logger.info("Génération des puzzles de hacking...")
        puzzle_ids = self.generate_hacking_puzzles(db, world_id, device_ids, network_ids)
        
        # Générer les fichiers
        logger.info("Génération des fichiers...")
        file_ids = self.generate_files(db, world_id, device_ids)
        
        # Générer les missions
        logger.info("Génération des missions...")
        mission_ids = self.generate_missions(db, world_id, all_location_ids, character_ids, num_missions)
        
        # Générer les éléments d'histoire
        if num_story_elements > 0:
            logger.info("Génération des éléments d'histoire...")
            self.generate_story_elements(db, world_id, all_location_ids, character_ids, mission_ids, num_story_elements)
        
        # Générer les objets hardware
        logger.info("Génération des objets hardware...")
        hardware_ids = self.generate_hardware_items(db, world_id, device_ids, building_ids, character_ids, num_hardware_items)
        
        # Générer les objets consommables
        logger.info("Génération des objets consommables...")
        consumable_ids = self.generate_consumable_items(db, world_id, device_ids, building_ids, character_ids, num_consumable_items)
        
        # Générer les boutiques
        logger.info("Génération des boutiques...")
        shop_ids = self.generate_shops(db, world_id, all_location_ids, building_ids, 10)
        
        db.conn.commit()
        logger.info(f"Monde '{name}' (ID: {world_id}) généré avec succès")
        
        return world_id
        
    except Exception as e:
        db.conn.rollback()
        logger.error(f"Erreur lors de la génération du monde: {str(e)}")
        raise