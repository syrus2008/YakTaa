"""
Module pour la génération des connexions entre lieux
Contient la fonction pour créer des connexions entre les lieux du monde
"""

import uuid
import json
import logging
from typing import List
import random

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Connections")

def generate_connections(db, world_id: str, location_ids: List[str], random) -> None:
    """
    Génère des connexions entre les lieux
    
    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs de tous les lieux
        random: Instance de random pour la génération aléatoire
    """
    # Récupérer les informations sur les lieux
    cursor = db.conn.cursor()
    locations_info = {}
    
    for loc_id in location_ids:
        cursor.execute('''
        SELECT id, name, parent_location_id, is_virtual, is_special, security_level, coordinates
        FROM locations WHERE id = ?
        ''', (loc_id,))
        loc_data = cursor.fetchone()
        if loc_data:
            locations_info[loc_id] = dict(loc_data)
            locations_info[loc_id]["coordinates"] = json.loads(loc_data["coordinates"])
    
    # Créer un graphe de connexions
    # 1. Connecter chaque lieu à son parent (si existe)
    # 2. Connecter les grandes villes entre elles
    # 3. Connecter les districts d'une même ville
    # 4. Ajouter quelques connexions aléatoires
    
    connections_added = 0
    
    # 1. Connexions parent-enfant
    for loc_id, loc_info in locations_info.items():
        parent_id = loc_info.get("parent_location_id")
        if parent_id and parent_id in locations_info:
            # Créer une connexion bidirectionnelle
            connection_id = str(uuid.uuid4())
            travel_type = "Transport local"
            travel_time = 0.2  # Heures
            travel_cost = random.randint(10, 100)
            
            cursor.execute('''
            INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                    travel_time, travel_cost, requires_hacking, requires_special_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                connection_id, world_id, loc_id, parent_id, travel_type,
                travel_time, travel_cost, 0, 0
            ))
            
            # Connexion inverse
            connection_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                    travel_time, travel_cost, requires_hacking, requires_special_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                connection_id, world_id, parent_id, loc_id, travel_type,
                travel_time, travel_cost, 0, 0
            ))
            
            connections_added += 2
    
    # 2. Connexions entre grandes villes (lieux sans parent)
    cities = [loc_id for loc_id, info in locations_info.items() 
             if not info.get("parent_location_id") and not info.get("is_virtual") and not info.get("is_special")]
    
    # Créer un graphe connexe (chaque ville est accessible)
    if len(cities) > 1:
        # D'abord, créer un arbre couvrant
        connected_cities = {cities[0]}
        unconnected_cities = set(cities[1:])
        
        while unconnected_cities:
            source_id = random.choice(list(connected_cities))
            dest_id = random.choice(list(unconnected_cities))
            
            # Créer une connexion bidirectionnelle
            connection_id = str(uuid.uuid4())
            
            # Déterminer le type de transport basé sur la distance
            source_coords = locations_info[source_id]["coordinates"]
            dest_coords = locations_info[dest_id]["coordinates"]
            
            distance = ((source_coords[0] - dest_coords[0])**2 + 
                       (source_coords[1] - dest_coords[1])**2)**0.5
            
            if distance > 50:
                travel_type = "Vol international"
                travel_time = random.uniform(5, 15)  # Heures
                travel_cost = random.randint(5000, 15000)
            elif distance > 10:
                travel_type = "Vol régional"
                travel_time = random.uniform(1, 5)  # Heures
                travel_cost = random.randint(1000, 5000)
            else:
                travel_type = "Train à grande vitesse"
                travel_time = random.uniform(0.5, 3)  # Heures
                travel_cost = random.randint(500, 2000)
            
            cursor.execute('''
            INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                    travel_time, travel_cost, requires_hacking, requires_special_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                connection_id, world_id, source_id, dest_id, travel_type,
                travel_time, travel_cost, 0, 0
            ))
            
            # Connexion inverse
            connection_id = str(uuid.uuid4())
            cursor.execute('''
            INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                    travel_time, travel_cost, requires_hacking, requires_special_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                connection_id, world_id, dest_id, source_id, travel_type,
                travel_time, travel_cost, 0, 0
            ))
            
            connected_cities.add(dest_id)
            unconnected_cities.remove(dest_id)
            connections_added += 2
        
        # Ajouter quelques connexions supplémentaires entre villes
        num_extra = min(len(cities) // 2, 5)
        for _ in range(num_extra):
            source_id = random.choice(cities)
            dest_id = random.choice([c for c in cities if c != source_id])
            
            # Vérifier si la connexion existe déjà
            cursor.execute('''
            SELECT COUNT(*) FROM connections 
            WHERE source_id = ? AND destination_id = ?
            ''', (source_id, dest_id))
            
            if cursor.fetchone()[0] == 0:
                # Créer une connexion bidirectionnelle
                connection_id = str(uuid.uuid4())
                
                # Déterminer le type de transport
                source_coords = locations_info[source_id]["coordinates"]
                dest_coords = locations_info[dest_id]["coordinates"]
                
                distance = ((source_coords[0] - dest_coords[0])**2 + 
                           (source_coords[1] - dest_coords[1])**2)**0.5
                
                if distance > 50:
                    travel_type = "Vol international"
                    travel_time = random.uniform(5, 15)
                    travel_cost = random.randint(5000, 15000)
                elif distance > 10:
                    travel_type = "Vol régional"
                    travel_time = random.uniform(1, 5)
                    travel_cost = random.randint(1000, 5000)
                else:
                    travel_type = "Train à grande vitesse"
                    travel_time = random.uniform(0.5, 3)
                    travel_cost = random.randint(500, 2000)
                
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, source_id, dest_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                # Connexion inverse
                connection_id = str(uuid.uuid4())
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, dest_id, source_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                connections_added += 2
    
    # 3. Connexions entre districts d'une même ville
    # Regrouper les districts par ville parent
    districts_by_city = {}
    for loc_id, info in locations_info.items():
        parent_id = info.get("parent_location_id")
        if parent_id:
            if parent_id not in districts_by_city:
                districts_by_city[parent_id] = []
            districts_by_city[parent_id].append(loc_id)
    
    # Connecter les districts entre eux
    for city_id, district_ids in districts_by_city.items():
        if len(district_ids) > 1:
            # Créer un graphe connexe entre les districts
            connected_districts = {district_ids[0]}
            unconnected_districts = set(district_ids[1:])
            
            while unconnected_districts:
                source_id = random.choice(list(connected_districts))
                dest_id = random.choice(list(unconnected_districts))
                
                # Créer une connexion bidirectionnelle
                connection_id = str(uuid.uuid4())
                travel_type = "Métro"
                travel_time = random.uniform(0.1, 0.5)  # Heures
                travel_cost = random.randint(10, 100)
                
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, source_id, dest_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                # Connexion inverse
                connection_id = str(uuid.uuid4())
                cursor.execute('''
                INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                        travel_time, travel_cost, requires_hacking, requires_special_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    connection_id, world_id, dest_id, source_id, travel_type,
                    travel_time, travel_cost, 0, 0
                ))
                
                connected_districts.add(dest_id)
                unconnected_districts.remove(dest_id)
                connections_added += 2
            
            # Ajouter quelques connexions supplémentaires entre districts
            num_extra = min(len(district_ids) // 2, 3)
            for _ in range(num_extra):
                source_id = random.choice(district_ids)
                dest_id = random.choice([d for d in district_ids if d != source_id])
                
                # Vérifier si la connexion existe déjà
                cursor.execute('''
                SELECT COUNT(*) FROM connections 
                WHERE source_id = ? AND destination_id = ?
                ''', (source_id, dest_id))
                
                if cursor.fetchone()[0] == 0:
                    # Créer une connexion bidirectionnelle
                    connection_id = str(uuid.uuid4())
                    travel_type = "Métro"
                    travel_time = random.uniform(0.1, 0.5)
                    travel_cost = random.randint(10, 100)
                    
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, source_id, dest_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    # Connexion inverse
                    connection_id = str(uuid.uuid4())
                    cursor.execute('''
                    INSERT INTO connections (id, world_id, source_id, destination_id, travel_type, 
                                            travel_time, travel_cost, requires_hacking, requires_special_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        connection_id, world_id, dest_id, source_id, travel_type,
                        travel_time, travel_cost, 0, 0
                    ))
                    
                    connections_added += 2
    db.conn.commit()
    logger.info(f"Connexions générées: {connections_added}")