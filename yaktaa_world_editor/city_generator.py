"""
Module pour la génération des villes et districts
Contient les fonctions pour créer des villes et des districts dans le monde
"""

import uuid
import json
import logging
from typing import List

from constants import CITY_PREFIXES, CITY_NAMES, DISTRICT_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.City")

def generate_cities(db, world_id: str, num_cities: int, random) -> List[str]:
    """
    Génère des villes pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        num_cities: Nombre de villes à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des villes générées
    """
    city_ids = []
    
    # Mélanger les noms de villes pour éviter les doublons
    city_names = random.sample(CITY_NAMES, min(len(CITY_NAMES), num_cities))
    
    for i in range(num_cities):
        city_id = str(uuid.uuid4())
        
        # Générer un nom unique
        if i < len(city_names):
            base_name = city_names[i]
        else:
            # Si on a épuisé les noms prédéfinis, générer un nom aléatoire
            base_name = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5))
        
        # 50% de chance d'ajouter un préfixe
        if random.random() < 0.5:
            name = f"{random.choice(CITY_PREFIXES)}{base_name}"
        else:
            name = base_name
        
        # Générer des coordonnées aléatoires (latitude entre -90 et 90, longitude entre -180 et 180)
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        coordinates = (lat, lon)
        
        # Générer une population aléatoire (entre 100,000 et 20 millions)
        population = random.randint(100000, 20000000)
        
        # Générer un niveau de sécurité aléatoire (1-5)
        security_level = random.randint(1, 5)
        
        # Générer des services disponibles
        available_services = ["commerce", "transport"]
        optional_services = ["hacking", "médical", "finance", "divertissement", "information", "marché noir"]
        num_optional = random.randint(0, len(optional_services))
        services = available_services + random.sample(optional_services, num_optional)
        
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
            f"{name} est une ville {random.choice(['animée', 'grouillante', 'imposante', 'tentaculaire'])} avec une population de {population:,} habitants.",
            f"Connue pour {random.choice(['ses gratte-ciels vertigineux', 'ses marchés animés', 'sa technologie de pointe', 'son architecture unique'])}.",
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

def generate_districts(db, world_id: str, city_ids: List[str], num_districts_per_city: int, random) -> List[str]:
    """
    Génère des districts pour les villes
    
    Args:
        db: Base de données
        world_id: ID du monde
        city_ids: Liste des IDs des villes
        num_districts_per_city: Nombre de districts par ville
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des districts générés
    """
    district_ids = []
    
    for city_id in city_ids:
        # Récupérer les informations de la ville
        cursor = db.conn.cursor()
        cursor.execute("SELECT name, security_level, population, coordinates FROM locations WHERE id = ?", (city_id,))
        city_data = cursor.fetchone()
        
        if not city_data:
            continue
            
        city_name = city_data["name"]
        city_security = city_data["security_level"]
        city_population = city_data["population"]
        city_coords = json.loads(city_data["coordinates"])
        
        # Générer des districts pour cette ville
        for _ in range(num_districts_per_city):
            district_id = str(uuid.uuid4())
            
            # Type de district
            district_type = random.choice(DISTRICT_TYPES)
            
            # Nom du district
            district_name = f"{city_name} - {district_type}"
            
            # Sécurité du district (variation par rapport à la ville)
            security_variation = random.choice([-1, 0, 0, 1])
            security_level = max(1, min(5, city_security + security_variation))
            
            # Population (10-30% de la population de la ville)
            population = int(city_population * random.uniform(0.1, 0.3))
            
            # Services disponibles selon le type de district
            services = ["commerce"]
            if district_type == "Résidentiel":
                services.extend(["transport", "médical"])
            elif district_type == "Commercial":
                services.extend(["transport", "divertissement", "finance"])
            elif district_type == "Industriel":
                services.extend(["transport", "technologie"])
            elif district_type == "Technologique":
                services.extend(["transport", "technologie", "hacking", "médical"])
            elif district_type == "Divertissement":
                services.extend(["transport", "divertissement", "marché noir"])
            
            # Tags
            tags = ["district", district_type.lower()]
            if security_level <= 2:
                tags.append("zone dangereuse")
            
            # Description
            descriptions = [
                f"{district_name} est un district {random.choice(['animé', 'grouillant', 'calme', 'bruyant'])} de {city_name}.",
                f"Ce quartier {district_type.lower()} abrite environ {population:,} habitants.",
                f"Le niveau de sécurité y est {['minimal', 'faible', 'modéré', 'élevé', 'maximal'][security_level-1]}.",
                f"On y trouve principalement {', '.join(services[:-1]) + ' et ' + services[-1] if len(services) > 1 else services[0]}."  
            ]
            description = " ".join(descriptions)
            
            # Coordonnées relatives à la ville
            # Variation de ±0.05 degrés par rapport à la ville
            lat = city_coords[0] + random.uniform(-0.05, 0.05)
            lon = city_coords[1] + random.uniform(-0.05, 0.05)
            coordinates = (lat, lon)
            
            # Insérer le district dans la base de données
            cursor.execute('''
            INSERT INTO locations (id, world_id, name, description, coordinates, security_level, 
                                  population, services, tags, is_virtual, is_special, is_dangerous, 
                                  location_type, parent_location_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                district_id, world_id, district_name, description, json.dumps(coordinates), security_level,
                population, json.dumps(services), json.dumps(tags), 0, 0, 1 if security_level <= 2 else 0, 
                "district", city_id
            ))
            
            district_ids.append(district_id)
            logger.debug(f"District généré: {district_name} (ID: {district_id})")
    
    db.conn.commit()
    return district_ids
