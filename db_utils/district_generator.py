
"""
Module pour la génération des districts
Contient la fonction pour créer des districts dans les villes
"""

import uuid
import json
import logging
from typing import List

from constants import DISTRICT_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.District")

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
