"""
Module pour la génération des puzzles de hacking
Contient la fonction pour créer des défis de hacking pour les appareils et réseaux
"""

import uuid
import json
import logging
import random
from typing import List

from constants import HACKING_PUZZLE_TYPES
from database import get_database

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.HackingPuzzles")

def generate_hacking_puzzles(db, world_id: str, device_ids: List[str], network_ids: List[str], random) -> List[str]:
    """
    Génère des puzzles de hacking pour les appareils et les réseaux

    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        network_ids: Liste des IDs des réseaux
        random: Instance de random pour la génération aléatoire

    Returns:
        Liste des IDs des puzzles générés
    """
    puzzle_ids = []
    
    # Obtenir une nouvelle connexion à la base de données
    db = get_database(db.db_path)
    
    cursor = db.conn.cursor()
    
    # Générer des puzzles pour les appareils
    for device_id in device_ids:
        # Ne pas créer de puzzle pour tous les appareils
        if random.random() > 0.3:  # Seulement 30% des appareils ont des puzzles
            continue
            
        # Obtenir des informations sur l'appareil
        cursor.execute('''
        SELECT id, device_type, name, security_level
        FROM devices WHERE id = ?
        ''', (device_id,))
        
        device = cursor.fetchone()
        if not device:
            continue
            
        # Choisir un type de puzzle approprié pour cet appareil
        puzzle_type = None
        if device["device_type"] in ["Server", "MainFrame", "SecuritySystem"]:
            puzzle_type = random.choice(["FirewallBypass", "CodeInjection", "BufferOverflow"])
        elif device["device_type"] in ["Laptop", "Desktop"]:
            puzzle_type = random.choice(["PasswordBruteforce", "BasicTerminal", "SequenceMatching"])
        elif device["device_type"] == "SmartPhone":
            puzzle_type = random.choice(["PasswordBruteforce", "NetworkRerouting"])
        elif device["device_type"] in ["Camera", "SmartDevice"]:
            puzzle_type = random.choice(["BasicTerminal", "SequenceMatching"])
        else:
            puzzle_type = random.choice(HACKING_PUZZLE_TYPES)
            
        # Difficulté basée sur le niveau de sécurité de l'appareil
        try:
            security_level = device["security_level"]
            if security_level is None:
                security_level = 1
        except (IndexError, KeyError):
            security_level = 1
            
        difficulty = min(5, max(1, security_level))
        if difficulty < 1:
            difficulty = random.randint(1, 3)
            
        # Nom et description
        puzzle_id = str(uuid.uuid4())
        name = f"{puzzle_type} Challenge"
        description = f"Un puzzle de hacking de type {puzzle_type} pour l'appareil {device['name']}."
        
        # Récompenses potentielles
        xp_reward = difficulty * random.randint(10, 20)
        credit_reward = difficulty * random.randint(50, 200)
        
        # Points d'intérêt connectés à ce puzzle
        connected_poi = random.randint(0, 3) if difficulty > 3 else 0
        
        # Métadonnées pour stocker des informations supplémentaires
        metadata = {
            "device_id": device_id,
            "rewards": {
                "xp": xp_reward,
                "credits": credit_reward
            },
            "connected_poi": connected_poi,
            "hints": [
                f"Indice 1 pour {name}",
                f"Indice 2 pour {name}" if difficulty < 4 else None
            ],
            "solution_steps": random.randint(3, 5 + difficulty),
            "failure_consequences": "data_loss" if difficulty > 3 else "none"
        }
        
        # Insérer le puzzle dans la base de données
        cursor.execute('''
        INSERT INTO hacking_puzzles (id, world_id, name, description, puzzle_type, 
                                   difficulty, target_type, target_id, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            puzzle_id, world_id, name, description, puzzle_type,
            difficulty, "device", device_id, json.dumps(metadata)
        ))
        
        puzzle_ids.append(puzzle_id)
        logger.debug(f"Puzzle de hacking généré: {name} (difficulté: {difficulty}) pour appareil {device_id}")
    
    # Générer des puzzles pour les réseaux
    for network_id in network_ids:
        # Ne pas créer de puzzle pour tous les réseaux
        if random.random() > 0.5:  # 50% des réseaux ont des puzzles
            continue
            
        # Obtenir des informations sur le réseau
        cursor.execute('''
        SELECT id, name, network_type, security_level, requires_hacking
        FROM networks WHERE id = ?
        ''', (network_id,))
        
        network = cursor.fetchone()
        if not network:
            continue
            
        # Si le réseau ne nécessite pas de hacking, continuer
        try:
            if network["requires_hacking"] == 0:
                continue
        except (IndexError, KeyError):
            # Si la colonne n'existe pas ou n'est pas accessible, on utilise 0 par défaut
            continue
            
        # Choisir un type de puzzle approprié pour ce réseau
        puzzle_type = None
        if network["network_type"] in ["Corporate", "VPN", "Secured"]:
            puzzle_type = random.choice(["FirewallBypass", "NetworkRerouting", "CodeInjection"])
        elif network["network_type"] in ["WiFi"]:
            puzzle_type = random.choice(["PasswordBruteforce", "SequenceMatching"])
        elif network["network_type"] in ["IoT"]:
            puzzle_type = random.choice(["BasicTerminal", "SequenceMatching"])
        else:
            puzzle_type = random.choice(HACKING_PUZZLE_TYPES)
            
        # Difficulté basée sur le niveau de sécurité du réseau
        try:
            sec_level = network["security_level"]
            if sec_level is None:
                sec_level = "WEP"
        except (IndexError, KeyError):
            sec_level = "WEP"
            
        if sec_level == "WPA3" or sec_level == "Enterprise":
            difficulty = random.randint(4, 5)
        elif sec_level == "WPA2":
            difficulty = random.randint(3, 4)
        elif sec_level == "WPA":
            difficulty = random.randint(2, 3)
        elif sec_level == "WEP":
            difficulty = random.randint(1, 2)
        else:
            difficulty = random.randint(1, 3)
            
        # Nom et description
        puzzle_id = str(uuid.uuid4())
        name = f"{network['name']} Access Challenge"
        description = f"Un puzzle de hacking pour accéder au réseau {network['name']}."
        
        # Récompenses potentielles
        xp_reward = difficulty * random.randint(15, 25)
        credit_reward = difficulty * random.randint(75, 250)
        
        # Nombres de machines accessibles après résolution
        num_accessible_devices = random.randint(1, 5)
        
        # Métadonnées pour stocker des informations supplémentaires
        metadata = {
            "network_id": network_id,
            "rewards": {
                "xp": xp_reward,
                "credits": credit_reward,
                "accessible_devices": num_accessible_devices
            },
            "hints": [
                f"Indice 1 pour {name}",
                f"Indice 2 pour {name}" if difficulty < 4 else None
            ],
            "solution_steps": random.randint(2, 4 + difficulty),
            "trap": True if difficulty > 3 and random.random() < 0.3 else False,
            "alarm_trigger_chance": 0.1 * difficulty if difficulty > 2 else 0
        }
        
        # Insérer le puzzle dans la base de données
        cursor.execute('''
        INSERT INTO hacking_puzzles (id, world_id, name, description, puzzle_type, 
                                   difficulty, target_type, target_id, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            puzzle_id, world_id, name, description, puzzle_type,
            difficulty, "network", network_id, json.dumps(metadata)
        ))
        
        puzzle_ids.append(puzzle_id)
        logger.debug(f"Puzzle de hacking généré: {name} (difficulté: {difficulty}) pour réseau {network_id}")
    
    logger.info(f"Puzzles de hacking générés: {len(puzzle_ids)}")
    db.conn.commit()
    return puzzle_ids