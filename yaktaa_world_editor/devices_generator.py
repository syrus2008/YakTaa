"""
Module pour la génération des appareils électroniques
Contient la fonction pour créer des appareils dans le monde
"""

import uuid
import json
import logging
import ipaddress
from typing import List
import random

from constants import DEVICE_TYPES, OS_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Devices")

def generate_devices(db, world_id: str, location_ids: List[str], character_ids: List[str], num_devices: int, random) -> List[str]:
    """
    Génère des appareils électroniques (PC, smartphones, etc.)
    
    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        character_ids: Liste des IDs des personnages
        num_devices: Nombre d'appareils à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des appareils générés
    """
    device_ids = []
    cursor = db.conn.cursor()
    
    # Récupérer les informations sur les bâtiments
    cursor.execute('''
    SELECT id, location_id, name, building_type, security_level
    FROM buildings WHERE world_id = ?
    ''', (world_id,))
    
    buildings = cursor.fetchall()
    
    if not buildings:
        logger.warning("Aucun bâtiment trouvé pour générer des appareils")
        return device_ids
    
    # Récupérer les informations sur les pièces
    rooms_by_building = {}
    for building in buildings:
        cursor.execute('''
        SELECT id, name, room_type
        FROM rooms WHERE building_id = ?
        ''', (building["id"],))
        
        rooms = cursor.fetchall()
        if rooms:
            rooms_by_building[building["id"]] = rooms
    
    # Générer les appareils
    for _ in range(num_devices):
        device_id = str(uuid.uuid4())
        
        # Sélectionner un type d'appareil
        device_type = random.choice(DEVICE_TYPES)
        
        # Sélectionner un système d'exploitation
        os_type = random.choice(OS_TYPES)
        
        # Nom de l'appareil
        if device_type == "Server":
            name = f"SRV-{random.choice(['MAIN', 'DATA', 'WEB', 'AUTH', 'DB'])}-{random.randint(1, 999):03d}"
        elif device_type == "Desktop PC":
            name = f"PC-{random.choice(['WORK', 'DEV', 'ADMIN', 'USER'])}-{random.randint(1, 999):03d}"
        elif device_type == "Laptop":
            name = f"LT-{random.choice(['WORK', 'PERSONAL', 'TRAVEL'])}-{random.randint(1, 999):03d}"
        elif device_type == "Smartphone":
            name = f"PHONE-{random.choice(['PERSONAL', 'WORK', 'SECURE'])}-{random.randint(1, 999):03d}"
        else:
            name = f"{device_type.upper()}-{random.randint(1, 999):03d}"
        
        # Niveau de sécurité (1-5)
        if device_type in ["Server", "Security System"]:
            security_level = random.randint(3, 5)
        elif device_type in ["Desktop PC", "Laptop"] and "ADMIN" in name:
            security_level = random.randint(3, 4)
        else:
            security_level = random.randint(1, 3)
        
        # Emplacement de l'appareil
        # 70% dans un bâtiment, 30% avec un personnage
        if random.random() < 0.7:
            # Dans un bâtiment
            building = random.choice(buildings)
            location_id = building["location_id"]
            
            # Sélectionner une pièce si disponible
            room_id = None
            if building["id"] in rooms_by_building:
                room = random.choice(rooms_by_building[building["id"]])
                room_id = room["id"]
            
            owner_id = None
            
            # Métadonnées pour stocker des informations supplémentaires
            metadata = {
                "building_id": building["id"],
                "room_id": room_id
            }
        else:
            # Avec un personnage
            if character_ids:
                owner_id = random.choice(character_ids)
                
                # Récupérer l'emplacement du personnage
                cursor.execute("SELECT location_id FROM characters WHERE id = ?", (owner_id,))
                character_data = cursor.fetchone()
                
                if character_data:
                    location_id = character_data["location_id"]
                else:
                    # Si le personnage n'a pas d'emplacement, choisir un lieu aléatoire
                    location_id = random.choice(location_ids)
                
                metadata = {}
            else:
                # Si pas de personnages, mettre l'appareil dans un lieu aléatoire
                location_id = random.choice(location_ids)
                owner_id = None
                metadata = {}
        
        # Adresse IP
        ip_address = str(ipaddress.IPv4Address(random.randint(0, 2**32-1)))
        
        # Description
        descriptions = [f"Un {device_type.lower()} exécutant {os_type}."]
        
        if security_level >= 4:
            descriptions.append("Cet appareil dispose d'une sécurité de haut niveau avec plusieurs couches de protection.")
        elif security_level <= 2:
            descriptions.append("La sécurité de cet appareil est minimale et présente plusieurs vulnérabilités.")
        
        if device_type == "Server":
            descriptions.append(f"Ce serveur héberge des services critiques et est accessible via l'adresse {ip_address}.")
        elif device_type == "Security System":
            descriptions.append("Ce système contrôle les accès et la surveillance d'une zone sécurisée.")
        
        description = " ".join(descriptions)
        
        # Insérer l'appareil dans la base de données
        cursor.execute('''
        INSERT INTO devices (id, world_id, name, description, location_id, owner_id,
                           device_type, os_type, security_level, is_connected, ip_address, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_id, world_id, name, description, location_id, owner_id,
            device_type, os_type, security_level, 1, ip_address, json.dumps(metadata)
        ))
        
        device_ids.append(device_id)
        logger.debug(f"Appareil généré: {name} (ID: {device_id})")
    
    db.conn.commit()
    return device_ids