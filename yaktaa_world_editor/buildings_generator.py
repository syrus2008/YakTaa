"""
Module pour la génération des bâtiments
Contient les fonctions pour créer des bâtiments et des pièces
"""

import uuid
import json
import logging
from typing import List

from constants import BUILDING_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Buildings")

def generate_buildings(db, world_id: str, location_ids: List[str], random) -> List[str]:
    """
    Génère des bâtiments pour les lieux
    
    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des bâtiments générés
    """
    building_ids = []
    cursor = db.conn.cursor()
    
    # Nombre de bâtiments par lieu (basé sur la population)
    for loc_id in location_ids:
        cursor.execute('''
        SELECT name, population, security_level, is_virtual
        FROM locations WHERE id = ?
        ''', (loc_id,))
        
        loc_data = cursor.fetchone()
        if not loc_data or loc_data["is_virtual"]:
            continue  # Ignorer les lieux virtuels
            
        location_name = loc_data["name"]
        population = loc_data["population"]
        security_level = loc_data["security_level"]
        
        # Déterminer le nombre de bâtiments basé sur la population
        if population > 1000000:  # Grande ville
            num_buildings = random.randint(5, 10)
        elif population > 100000:  # Ville moyenne
            num_buildings = random.randint(3, 7)
        elif population > 10000:  # Petite ville
            num_buildings = random.randint(2, 5)
        else:  # Village ou lieu spécial
            num_buildings = random.randint(1, 3)
        
        # Générer les bâtiments
        for _ in range(num_buildings):
            building_id = str(uuid.uuid4())
            
            # Sélectionner un type de bâtiment
            building_type = random.choice(BUILDING_TYPES)
            
            # Générer un nom basé sur le type
            if building_type == "Corporate HQ":
                corps = ["NeoTech", "CyberSys", "QuantumCorp", "SynthInc", "MegaData"]
                name = f"{random.choice(corps)} Headquarters"
            elif building_type == "Research Lab":
                prefixes = ["Advanced", "Quantum", "Cyber", "Neural", "Bio"]
                name = f"{random.choice(prefixes)} Research Laboratory"
            elif building_type == "Nightclub":
                names = ["Neon Dreams", "Pulse", "Circuit", "Zero Day", "The Matrix"]
                name = random.choice(names)
            else:
                # Nom générique pour les autres types
                name = f"{location_name} {building_type}"
            
            # Nombre d'étages
            if building_type in ["Corporate HQ", "Apartment Complex", "Hotel"]:
                floors = random.randint(10, 50)
            else:
                floors = random.randint(1, 10)
            
            # Niveau de sécurité (influencé par le niveau de sécurité du lieu)
            if building_type in ["Corporate HQ", "Government Building", "Police Station", "Military Base"]:
                # Bâtiments à haute sécurité
                building_security = min(5, security_level + random.randint(0, 2))
            elif building_type in ["Nightclub", "Shopping Mall", "Restaurant"]:
                # Bâtiments à sécurité moyenne/basse
                building_security = max(1, security_level - random.randint(0, 2))
            else:
                # Autres bâtiments
                building_security = security_level
            
            # Propriétaire
            if building_type in ["Corporate HQ", "Research Lab", "Data Center"]:
                corps = ["NeoTech Corp", "CyberSys Inc", "QuantumCorp", "SynthInc", "MegaData Ltd"]
                owner_name = random.choice(corps)
            elif building_type in ["Government Building", "Police Station", "Military Base"]:
                owner_name = "Gouvernement"
            else:
                owner_name = ""  # Propriétaire non spécifié
            
            # Description
            descriptions = []
            
            # Description de base
            descriptions.append(f"Un {building_type.lower()} de {floors} étages situé à {location_name}.")
            
            if building_security >= 4:
                descriptions.append("La sécurité y est extrêmement stricte avec des systèmes de surveillance avancés.")
            elif building_security <= 2:
                descriptions.append("La sécurité y est minimale, ce qui en fait une cible facile.")
            
            if owner_name:
                descriptions.append(f"Propriété de {owner_name}.")
            
            description = " ".join(descriptions)
            
            # Métadonnées pour stocker des informations supplémentaires
            metadata = {
                "building_id": building_id,
                "room_id": None,
                "owner_name": owner_name  # Stockage du nom du propriétaire dans les métadonnées
            }
            
            # Insérer le bâtiment dans la base de données
            cursor.execute('''
            INSERT INTO buildings (id, world_id, location_id, name, description, building_type,
                                 floors, security_level, owner_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                building_id, world_id, loc_id, name, description, building_type,
                floors, building_security, None, json.dumps(metadata)  # owner_id est NULL
            ))
            
            building_ids.append(building_id)
            
            # Générer des pièces pour le bâtiment
            generate_rooms(db, building_id, building_type, floors, building_security, random)
            
            logger.debug(f"Bâtiment généré: {name} à {location_name} (ID: {building_id})")
    
    db.conn.commit()
    return building_ids

def generate_rooms(db, building_id: str, building_type: str, floors: int, security_level: int, random) -> None:
    """
    Génère des pièces pour un bâtiment
    
    Args:
        db: Base de données
        building_id: ID du bâtiment
        building_type: Type du bâtiment
        floors: Nombre d'étages
        security_level: Niveau de sécurité du bâtiment
        random: Instance de random pour la génération aléatoire
    """
    cursor = db.conn.cursor()
    
    # Types de pièces par type de bâtiment
    room_types_by_building = {
        "Corporate HQ": ["Office", "Meeting Room", "Server Room", "Executive Suite", "Lobby", "Cafeteria"],
        "Apartment Complex": ["Apartment", "Lobby", "Maintenance Room", "Rooftop"],
        "Shopping Mall": ["Store", "Food Court", "Security Office", "Storage Room"],
        "Research Lab": ["Laboratory", "Office", "Server Room", "Testing Chamber", "Storage"],
        "Data Center": ["Server Room", "Control Room", "Cooling System", "Security Office"],
        "Hospital": ["Patient Room", "Operating Room", "Pharmacy", "Reception", "Doctor's Office"],
        "Police Station": ["Office", "Holding Cell", "Interrogation Room", "Evidence Room"],
        "Nightclub": ["Dance Floor", "Bar", "VIP Area", "DJ Booth", "Storage"],
        "Restaurant": ["Dining Area", "Kitchen", "Storage", "Office"],
        "Hotel": ["Room", "Lobby", "Restaurant", "Pool", "Gym"],
        "Factory": ["Production Floor", "Office", "Storage", "Control Room"],
        "Warehouse": ["Storage Area", "Loading Dock", "Office"],
        "Government Building": ["Office", "Meeting Room", "Archive", "Security Checkpoint"],
        "School": ["Classroom", "Office", "Cafeteria", "Gym", "Library"],
        "University": ["Lecture Hall", "Laboratory", "Office", "Library", "Student Center"]
    }
    
    # Obtenir les types de pièces pour ce bâtiment
    room_types = room_types_by_building.get(building_type, ["Room", "Office", "Storage"])
    
    # Nombre de pièces par étage
    rooms_per_floor = random.randint(1, 5)
    
    # Générer des pièces pour chaque étage
    for floor in range(floors):
        for _ in range(rooms_per_floor):
            room_id = str(uuid.uuid4())
            
            # Sélectionner un type de pièce
            room_type = random.choice(room_types)
            
            # Nom de la pièce
            if room_type == "Server Room" and random.random() < 0.5:
                name = f"Serveur {random.choice(['A', 'B', 'C', 'D'])}-{floor+1}"
            elif room_type == "Office" and random.random() < 0.5:
                name = f"Bureau {floor+1}-{random.randint(1, 10)}"
            elif room_type == "Room" or room_type == "Apartment":
                name = f"{room_type} {floor+1}-{random.randint(1, 20)}"
            else:
                name = f"{room_type} (Étage {floor+1})"
            
            # Accès
            is_locked = 0
            is_restricted = 0
            security_level_room = 1
            
            # Les pièces sensibles sont moins accessibles
            if room_type in ["Server Room", "Executive Suite", "Evidence Room", "Security Office", "Control Room"]:
                if security_level >= 3 or random.random() < 0.7:
                    is_locked = 1
                    security_level_room = min(security_level + 1, 5)
                    if random.random() < 0.5:
                        is_restricted = 1
            
            # Taille de la pièce (estimation relative en mètres carrés)
            if room_type in ["Warehouse", "Factory Floor", "Production Floor"]:
                size = random.randint(100, 500)
            elif room_type in ["Server Room", "Executive Suite", "Conference Room", "Lecture Hall"]:
                size = random.randint(40, 100)
            else:
                size = random.randint(15, 40)
            
            # Description
            descriptions = [f"Un(e) {room_type.lower()} situé(e) au {floor+1}e étage."]
            
            if is_locked:
                descriptions.append("Cette pièce est verrouillée et nécessite une autorisation spéciale.")
                
            if is_restricted:
                descriptions.append("L'accès est hautement restreint et peut nécessiter des moyens techniques pour y accéder.")
            
            description = " ".join(descriptions)
            
            # Métadonnées (pour stocker des informations supplémentaires)
            metadata = {
                "importance": "high" if room_type in ["Server Room", "Executive Suite", "Evidence Room"] else "normal",
                "requires_hacking": 1 if is_restricted else 0  # Conservons cette info dans les métadonnées
            }
            
            # Insérer la pièce dans la base de données
            cursor.execute('''
            INSERT INTO rooms (id, building_id, name, description, floor, room_type,
                             size, security_level, is_locked, is_restricted, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                room_id, building_id, name, description, floor, room_type,
                size, security_level_room, is_locked, is_restricted, json.dumps(metadata)
            ))