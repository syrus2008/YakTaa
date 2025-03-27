"""
Module pour la génération des lieux spéciaux
Contient la fonction pour créer des lieux spéciaux dans le monde
"""

import uuid
import json
import logging
from typing import List
import random

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.SpecialLocations")

def generate_special_locations(db, world_id: str, num_locations: int, random) -> List[str]:
    """
    Génère des lieux spéciaux pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        num_locations: Nombre de lieux spéciaux à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des lieux spéciaux générés
    """
    special_location_ids = []
    
    # Types de lieux spéciaux
    special_types = [
        ("Darknet Hub", "Un lieu virtuel accessible uniquement via le réseau, point central du darknet mondial.", True, False),
        ("Orbital Station", "Station spatiale en orbite terrestre, réservée à l'élite et aux recherches de pointe.", False, True),
        ("Wasteland", "Ancien centre urbain dévasté par les guerres corporatives, maintenant habité par des marginaux.", False, False),
        ("Underground Bunker", "Bunker souterrain fortifié, vestige des anciennes guerres, reconverti en refuge.", False, False),
        ("AI Nexus", "Centre de calcul quantique où résident les IA les plus avancées du monde.", False, True),
        ("Black Market", "Marché noir international, accessible uniquement aux initiés avec les bonnes connexions.", False, False),
        ("Corporate Island", "Île artificielle détenue par une mégacorporation, avec ses propres lois.", False, True),
        ("Virtual Resort", "Paradis virtuel où les riches peuvent vivre leurs fantasmes sans limites.", True, False)
    ]
    
    # Sélectionner des types aléatoires
    selected_types = random.sample(special_types, min(len(special_types), num_locations))
    
    for name_base, desc_base, is_virtual, is_special in selected_types:
        location_id = str(uuid.uuid4())
        
        # Personnaliser le nom
        if random.random() < 0.3:
            name = f"{name_base} {random.choice(['Alpha', 'Prime', 'Zero', 'Omega', 'X'])}"
        else:
            name = name_base
        
        # Coordonnées (aléatoires ou nulles pour les lieux virtuels)
        if is_virtual:
            coordinates = [0, 0]
        else:
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)
            coordinates = [lat, lon]
        
        # Population
        if is_virtual:
            population = 0
        elif is_special:
            population = random.randint(100, 10000)
        else:
            population = random.randint(1000, 100000)
        
        # Niveau de sécurité
        if is_special:
            security_level = random.randint(4, 5)
        elif name_base in ["Wasteland", "Black Market"]:
            security_level = random.randint(1, 2)
        else:
            security_level = random.randint(1, 5)
        
        # Services
        if is_virtual:
            base_services = ["information", "hacking"]
        elif is_special:
            base_services = ["recherche", "sécurité"]
        elif name_base == "Black Market":
            base_services = ["marché noir", "contrebande"]
        else:
            base_services = ["commerce"]
            
        optional_services = ["médical", "transport", "divertissement", "luxe", "information"]
        num_optional = random.randint(0, 3)
        services = base_services + random.sample(optional_services, num_optional)
        
        # Tags
        tags = []
        if is_virtual:
            tags.append("virtuel")
        if is_special:
            tags.append("spécial")
        if security_level <= 2:
            tags.append("dangereux")
        if name_base == "Orbital Station":
            tags.append("espace")
        if name_base == "AI Nexus":
            tags.append("intelligence artificielle")
        
        # Description
        description = desc_base
        if is_virtual:
            description += f" {random.choice(['Accessible uniquement par des connexions sécurisées.', 'Un monde numérique avec ses propres règles.', 'La réalité y est malléable et dangereuse.'])}"
        if is_special:
            description += f" {random.choice(['Accès strictement contrôlé.', 'Réservé à une élite privilégiée.', 'Protégé par des systèmes de sécurité avancés.'])}"
        if security_level <= 2:
            description += f" {random.choice(['Un lieu où la loi est absente.', 'Dangereux pour les non-initiés.', 'La survie y est une lutte quotidienne.'])}"
        
        # Insérer le lieu spécial dans la base de données
        cursor = db.conn.cursor()
        cursor.execute('''
        INSERT INTO locations (id, world_id, name, description, coordinates, security_level, 
                              population, services, tags, is_virtual, is_special, is_dangerous, location_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            location_id, world_id, name, description, json.dumps(coordinates), security_level,
            population, json.dumps(services), json.dumps(tags), 1 if is_virtual else 0, 
            1 if is_special else 0, 1 if security_level <= 2 else 0, "virtual" if is_virtual else "special"
        ))
        
        special_location_ids.append(location_id)
        logger.debug(f"Lieu spécial généré: {name} (ID: {location_id})")
    
    db.conn.commit()
    return special_location_ids