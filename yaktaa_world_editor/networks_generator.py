"""
Module pour la génération des réseaux
Contient la fonction pour créer des réseaux dans les bâtiments
"""

import uuid
import json
import logging
from typing import List

from constants import NETWORK_TYPES, SECURITY_LEVELS, ENCRYPTION_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Networks")

def generate_networks(db, world_id: str, building_ids: List[str], random) -> List[str]:
    """
    Génère des réseaux pour les bâtiments
    
    Args:
        db: Base de données
        world_id: ID du monde
        building_ids: Liste des IDs des bâtiments
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des réseaux générés
    """
    network_ids = []
    cursor = db.conn.cursor()
    
    # Obtenir des informations sur les bâtiments
    for building_id in building_ids:
        cursor.execute('''
        SELECT id, building_type, security_level, name 
        FROM buildings WHERE id = ?
        ''', (building_id,))
        
        building = cursor.fetchone()
        if not building:
            continue
            
        # Déterminer le nombre de réseaux à générer en fonction du type de bâtiment
        num_networks = 0
        if building["building_type"] in ["Corporate HQ", "Data Center", "Research Lab"]:
            num_networks = random.randint(3, 6)
        elif building["building_type"] in ["Government Building", "Police Station", "Military Base"]:
            num_networks = random.randint(2, 4)
        elif building["building_type"] in ["Shopping Mall", "Hotel", "University"]:
            num_networks = random.randint(2, 5)
        else:
            num_networks = random.randint(1, 3)
        
        # Générer des réseaux pour ce bâtiment
        for _ in range(num_networks):
            network_id = str(uuid.uuid4())
            
            # Choisir un type de réseau adapté au type de bâtiment
            network_type = None
            if building["building_type"] in ["Corporate HQ", "Data Center"]:
                network_type = random.choice(["Corporate", "LAN", "WAN", "VPN", "Secured"])
            elif building["building_type"] in ["Shopping Mall", "Hotel"]:
                network_type = random.choice(["WiFi", "Public", "IoT"])
            elif building["building_type"] in ["Apartment Complex", "Residential"]:
                network_type = random.choice(["WiFi", "IoT"])
            else:
                network_type = random.choice(NETWORK_TYPES)
            
            # Générer un nom et un SSID
            if network_type == "WiFi":
                if "Corporate" in building["building_type"]:
                    name = f"{building['name'][:10]}_WIFI"
                elif "Hotel" in building["building_type"]:
                    name = f"Guest_WiFi_{random.randint(100, 999)}"
                else:
                    name = f"Network_{random.randint(1000, 9999)}"
                
                ssid = name.replace(" ", "_").upper()
            elif network_type in ["Corporate", "Secured"]:
                name = f"{building['name'][:10]}_{network_type.upper()}"
                ssid = f"{name.replace(' ', '_').upper()}"
            else:
                name = f"{network_type}_{random.randint(1000, 9999)}"
                ssid = name
            
            # Déterminer le niveau de sécurité en fonction du type de bâtiment et de réseau
            security_level = 0
            security_type = None
            
            if building["security_level"] >= 4 or network_type in ["Corporate", "Secured", "VPN"]:
                security_level = random.randint(7, 10)
                security_type = random.choice(["WPA3", "Enterprise"])
            elif building["security_level"] >= 3 or network_type in ["LAN", "WAN"]:
                security_level = random.randint(5, 7)
                security_type = random.choice(["WPA2", "WPA3"])
            elif building["security_level"] >= 2:
                security_level = random.randint(3, 5)
                security_type = random.choice(["WPA", "WPA2"])
            elif network_type == "Public":
                security_level = random.randint(1, 2)
                security_type = "None"
            else:
                security_level = random.randint(1, 10)
                security_type = random.choice(SECURITY_LEVELS)
            
            # Déterminer le type de chiffrement
            encryption_type = None
            if security_type == "WPA3":
                encryption_type = "AES-256"
            elif security_type == "WPA2":
                encryption_type = random.choice(["AES-128", "AES-256", "TKIP/AES"])
            elif security_type == "WPA":
                encryption_type = random.choice(["TKIP", "TKIP/AES"])
            elif security_type == "WEP":
                encryption_type = random.choice(["WEP-64", "WEP-128"])
            elif security_type == "Enterprise":
                encryption_type = random.choice(["AES-256", "AES-256-GCM"])
            else:
                encryption_type = random.choice(ENCRYPTION_TYPES)
            
            # Générer un mot de passe en fonction du niveau de sécurité
            password = None
            if security_type != "None":
                if security_level >= 8:
                    # Mot de passe très complexe
                    password = ''.join(random.choice(
                        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?"
                    ) for _ in range(16))
                elif security_level >= 5:
                    # Mot de passe moyennement complexe
                    password = ''.join(random.choice(
                        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                    ) for _ in range(12))
                else:
                    # Mot de passe simple
                    password = ''.join(random.choice(
                        "abcdefghijklmnopqrstuvwxyz0123456789"
                    ) for _ in range(8))
            
            # Déterminer si le réseau est caché
            is_hidden = 0
            if network_type in ["Corporate", "Secured", "VPN"] or security_level >= 7:
                is_hidden = 1 if random.random() < 0.4 else 0
            
            # Déterminer si c'est un honeypot
            is_honeypot = 0
            if building["security_level"] >= 4 and random.random() < 0.1:
                is_honeypot = 1
            
            # Insérer le réseau dans la base de données
            cursor.execute('''
            INSERT INTO networks (
                id, world_id, name, description, network_type, ssid, 
                security_level, security_type, encryption, password, 
                building_id, is_hidden, is_honeypot, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                network_id, world_id, name, 
                f"Réseau {network_type} dans {building['name']}", 
                network_type, ssid, security_level, security_type, encryption_type, 
                password, building_id, is_hidden, is_honeypot,
                json.dumps({
                    "signal_strength": random.randint(1, 5),
                    "connected_devices": random.randint(0, 20),
                    "bandwidth": random.randint(10, 1000)
                })
            ))
            
            network_ids.append(network_id)
            logger.debug(f"Réseau généré: {name} ({network_type}, {security_type}) pour bâtiment {building_id}")
    
    logger.info(f"Réseaux générés: {len(network_ids)}")
    db.conn.commit()
    return network_ids