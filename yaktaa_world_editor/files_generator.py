"""
Module pour la génération des fichiers
Contient la fonction pour créer des fichiers sur les appareils
"""

import uuid
import json
import logging
import random
from typing import List

from constants import FILE_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Files")

def generate_files(db, world_id: str, device_ids: List[str], random) -> List[str]:
    """
    Génère des fichiers pour les appareils
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des fichiers générés
    """
    file_ids = []
    cursor = db.conn.cursor()
    
    # Récupérer les informations sur les appareils
    devices_by_id = {}
    for device_id in device_ids:
        cursor.execute('''
        SELECT name, device_type, os_type, security_level
        FROM devices WHERE id = ?
        ''', (device_id,))
        
        device_data = cursor.fetchone()
        if device_data:
            devices_by_id[device_id] = device_data
    
    # Générer les fichiers
    for device_id, device_data in devices_by_id.items():
        # Nombre de fichiers basé sur le type d'appareil
        if device_data["device_type"] == "Server":
            num_files = random.randint(5, 10)
        elif device_data["device_type"] in ["Desktop PC", "Laptop"]:
            num_files = random.randint(3, 7)
        else:
            num_files = random.randint(1, 4)
        
        for _ in range(num_files):
            file_id = str(uuid.uuid4())
            
            # Type de fichier
            file_type = random.choice(FILE_TYPES)
            
            # Nom du fichier
            if file_type == "Text":
                extension = ".txt"
                prefix = random.choice(["note", "memo", "document", "report", "log"])
            elif file_type == "Spreadsheet":
                extension = ".xlsx"
                prefix = random.choice(["data", "budget", "inventory", "analysis", "report"])
            elif file_type == "Database":
                extension = ".db"
                prefix = random.choice(["data", "records", "system", "users", "transactions"])
            elif file_type == "Image":
                extension = random.choice([".jpg", ".png", ".gif"])
                prefix = random.choice(["image", "photo", "picture", "scan", "screenshot"])
            elif file_type == "Audio":
                extension = random.choice([".mp3", ".wav", ".ogg"])
                prefix = random.choice(["recording", "audio", "voice", "sound", "music"])
            elif file_type == "Video":
                extension = random.choice([".mp4", ".avi", ".mkv"])
                prefix = random.choice(["video", "recording", "footage", "movie", "clip"])
            elif file_type == "Archive":
                extension = random.choice([".zip", ".rar", ".tar.gz"])
                prefix = random.choice(["archive", "backup", "package", "data", "files"])
            elif file_type == "Executable":
                extension = random.choice([".exe", ".bat", ".sh"])
                prefix = random.choice(["program", "installer", "setup", "tool", "utility"])
            elif file_type == "Script":
                extension = random.choice([".py", ".js", ".sh", ".bat"])
                prefix = random.choice(["script", "automation", "tool", "utility", "helper"])
            elif file_type == "Configuration":
                extension = random.choice([".ini", ".cfg", ".conf", ".json", ".xml"])
                prefix = random.choice(["config", "settings", "preferences", "options", "setup"])
            else:
                extension = ".dat"
                prefix = random.choice(["data", "file", "document", "item", "object"])
            
            # Générer un nom de fichier unique
            file_name = f"{prefix}_{random.randint(1, 999)}{extension}"
            
            # Taille du fichier (en Ko)
            if file_type in ["Video", "Archive", "Database"]:
                size = random.randint(1000, 10000)  # 1-10 Mo
            elif file_type in ["Audio", "Image", "Executable"]:
                size = random.randint(100, 2000)  # 100 Ko - 2 Mo
            else:
                size = random.randint(1, 500)  # 1-500 Ko
            
            # Niveau de sécurité (0-5)
            security_level = min(5, max(0, device_data["security_level"] - random.randint(0, 2)))
            
            # Contenu du fichier (simulé)
            content = None
            if file_type == "Text":
                # Générer un contenu de texte simulé
                content_length = min(500, size * 100)  # Environ 100 caractères par Ko
                content = "Lorem ipsum dolor sit amet..." if content_length > 30 else "Empty file"
            
            # Description
            descriptions = [f"Un fichier {file_type.lower()} nommé {file_name}."]
            
            if security_level >= 3:
                descriptions.append("Ce fichier est protégé par un chiffrement de haut niveau.")
            elif security_level <= 1:
                descriptions.append("Ce fichier n'est pas protégé.")
            
            if size > 5000:
                descriptions.append("Ce fichier est particulièrement volumineux.")
            
            description = " ".join(descriptions)
            
            # Métadonnées
            metadata = {
                "content_preview": content,
                "creation_date": "2023-01-01",  # Date fictive
                "last_modified": "2023-01-02",  # Date fictive
                "owner": "Unknown",
                "permissions": "rw-r--r--" if security_level < 3 else "rw-------",
                "is_hidden": security_level >= 4,
                "is_system": random.random() < 0.2,  # 20% de chance d'être un fichier système
                "is_readonly": random.random() < 0.3,  # 30% de chance d'être en lecture seule
                "is_encrypted": security_level >= 2,  # Encrypté si niveau de sécurité >= 2
                "encryption_type": "AES-256" if security_level >= 2 else None,
                "checksum": "abc123"  # Checksum fictif
            }
            
            # Insérer le fichier dans la base de données
            cursor.execute('''
            INSERT INTO files (id, world_id, device_id, name, description, file_type,
                             size, security_level, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_id, world_id, device_id, file_name, description, file_type,
                size, security_level, json.dumps(metadata)
            ))
            
            file_ids.append(file_id)
            logger.debug(f"Fichier généré: {file_name} (ID: {file_id}) sur appareil {device_id}")
    
    db.conn.commit()
    return file_ids