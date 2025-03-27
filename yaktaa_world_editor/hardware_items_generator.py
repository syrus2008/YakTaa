"""
Module pour la génération des objets hardware
Contient les fonctions pour créer des objets matériels dans le monde
"""

import uuid
import json
import logging
from typing import List, Dict
import random

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata
from constants import HARDWARE_TYPES, HARDWARE_QUALITIES, HARDWARE_RARITIES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.HardwareItems")

def generate_hardware_items(db, world_id: str, device_ids: List[str], 
                           building_ids: List[str], character_ids: List[str], 
                           num_items: int, random) -> List[str]:
    """
    Génère des objets hardware pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre d'objets à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des objets générés
    """
    hardware_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table hardware_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='hardware_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table hardware_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE hardware_items (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                hardware_type TEXT NOT NULL,
                quality TEXT,
                rarity TEXT,
                level INTEGER,
                stats TEXT,
                location_type TEXT,
                location_id TEXT,
                price INTEGER,
                is_installed INTEGER DEFAULT 0,
                is_available INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
        """)
        db.conn.commit()
        logger.info("Table hardware_items créée")
    
    # Composants de noms pour générer des noms réalistes
    prefixes = ["Quantum", "Cyber", "Neuro", "Hyper", "Nano", "Tech", "Mega", "Ultra", "Fusion", "Synth"]
    mid_parts = ["Core", "Wave", "Link", "Net", "Sync", "Pulse", "Matrix", "Node", "Flux", "Grid"]
    suffixes = ["XL", "Pro", "Elite", "Max", "Zero", "Nova", "Prime", "Plus", "Alpha", "Omega"]
    
    # Marques connues dans l'univers cyberpunk
    manufacturers = ["NeoTech", "SynthCorp", "QuantumDynamics", "HyperSystems", "FusionTech", 
                    "CyberIndustries", "MegaCorp", "UltraTech", "NanoWorks", "SyncSystems"]
    
    for i in range(num_items):
        # Déterminer si on place cet objet dans un appareil, un bâtiment ou sur un personnage
        location_type = random.choice(["device", "building", "character", "shop", "loot"])
        location_id = None
        
        if location_type == "device" and device_ids:
            location_id = random.choice(device_ids)
        elif location_type == "building" and building_ids:
            location_id = random.choice(building_ids)
        elif location_type == "character" and character_ids:
            location_id = random.choice(character_ids)
        elif location_type == "shop":
            if building_ids:
                location_id = random.choice(building_ids)
            else:
                location_type = "loot"
                location_id = "world"
        else:  # loot
            location_type = "loot"
            location_id = "world"
            
        # Sélectionner un type de matériel
        hardware_type = random.choice(HARDWARE_TYPES)
        
        # Générer un nom en fonction du type de matériel
        prefix = random.choice(prefixes)
        mid_part = random.choice(mid_parts)
        suffix = random.choice(suffixes)
        manufacturer = random.choice(manufacturers)
        
        # Nom complet
        name = f"{manufacturer} {prefix}{mid_part} {hardware_type} {suffix}"
        
        # Déterminer la qualité et la rareté
        quality = random.choice(HARDWARE_QUALITIES)
        quality_map = {
            "Broken": 0, "Poor": 1, "Standard": 2, 
            "High-End": 3, "Military-Grade": 4, "Prototype": 5, "Custom": 5
        }
        
        quality_level = quality_map.get(quality, 2)
        
        # La rareté dépend de la qualité
        rarity = None
        if quality in ["Prototype", "Custom"]:
            rarity = random.choice(["Epic", "Legendary", "Unique"])
        elif quality == "Military-Grade":
            rarity = random.choice(["Rare", "Epic"])
        elif quality == "High-End":
            rarity = random.choice(["Uncommon", "Rare"])
        elif quality == "Standard":
            rarity = "Common"
        elif quality == "Poor":
            rarity = "Common"
        else:  # Broken
            rarity = random.choice(["Common", "Uncommon"])  # Peut être rare si pièce vintage
            
        # Niveau de l'objet (1-10)
        level = min(10, max(1, quality_level * 2 + random.randint(-1, 2)))
        
        # Prix basé sur la qualité, la rareté et le niveau
        rarity_multiplier = {
            "Common": 1, "Uncommon": 1.5, "Rare": 3, 
            "Epic": 6, "Legendary": 10, "Unique": 20
        }
        base_price = 100 * level
        price = int(base_price * rarity_multiplier.get(rarity, 1) * (quality_level + 1) * (0.8 + random.random() * 0.4))
        
        # Générer des statistiques en fonction du type et de la qualité
        stats = _generate_hardware_stats(hardware_type, quality, level, random)
        
        # Description
        if quality in ["Broken", "Poor"]:
            condition = "en mauvais état"
        elif quality == "Standard":
            condition = "en bon état"
        else:
            condition = "en excellent état"
            
        description = f"Un {hardware_type} {condition} de niveau {level}, fabriqué par {manufacturer}."
        
        # Est-ce que l'objet est installé? (pertinent seulement pour les appareils)
        is_installed = 0
        if location_type == "device" and random.random() < 0.7:  # 70% des objets dans des appareils sont installés
            is_installed = 1
            
        # Fonctionnalités spéciales pour les objets de haute qualité
        special_features = []
        if quality in ["High-End", "Military-Grade", "Prototype", "Custom"]:
            possible_features = [
                "Encryption intégrée", "Refroidissement avancé", "Overclocking", 
                "Auto-réparation", "Camouflage EM", "Résistance EMP", 
                "Boost de performance", "IA assistante", "Cryptominage"
            ]
            
            num_features = min(3, max(1, quality_level - 2))
            special_features = random.sample(possible_features, k=num_features)
        
        # ID unique pour l'objet
        hardware_id = f"hardware_{uuid.uuid4()}"
        
        # Standardiser les métadonnées
        metadata = MetadataStandardizer.standardize_hardware_metadata(
            hardware_type=hardware_type,
            quality=quality,
            manufacturer=manufacturer,
            model=f"{prefix}{mid_part} {suffix}",
            year=2075 + random.randint(-20, 10),
            weight=random.randint(1, 50) / 10.0,  # en kg
            dimensions=f"{random.randint(1, 30)}x{random.randint(1, 20)}x{random.randint(1, 10)} cm",
            power_consumption=random.randint(5, 100) if hardware_type not in ["USB Drive", "External HDD"] else 0,
            compatibility=random.sample(["Windows", "Linux", "Custom OS", "Any"], k=random.randint(1, 4)),
            special_features=special_features,
            stats=stats,
            level=level,
            is_installed=bool(is_installed)
        )
        
        # Convertir en JSON
        metadata_json = MetadataStandardizer.to_json(metadata)
        
        # Insérer l'objet dans la base de données
        cursor.execute('''
        INSERT INTO hardware_items 
        (id, world_id, name, description, hardware_type, quality, rarity, level, 
        stats, location_type, location_id, price, is_installed, is_available, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            hardware_id, world_id, name, description, hardware_type, quality, rarity, level,
            json.dumps(stats), location_type, location_id, price, is_installed, 1, metadata_json
        ))
        
        hardware_ids.append(hardware_id)
        
    logger.info(f"Objets hardware générés: {len(hardware_ids)}")
    db.conn.commit()
    return hardware_ids

def _generate_hardware_stats(hardware_type: str, quality: str, level: int, random) -> Dict:
    """
    Génère des statistiques pour un objet hardware en fonction de son type et de sa qualité
    
    Args:
        hardware_type: Type de hardware
        quality: Qualité du hardware
        level: Niveau du hardware
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Dictionnaire de statistiques
    """
    stats = {}
    quality_multiplier = {
        "Broken": 0.3, "Poor": 0.7, "Standard": 1.0, 
        "High-End": 1.5, "Military-Grade": 2.0, "Prototype": 2.5, "Custom": 2.3
    }.get(quality, 1.0)
    
    # Modifier légèrement le multiplicateur pour chaque hardware
    quality_multiplier *= 0.9 + random.random() * 0.2
    
    if hardware_type == "CPU":
        stats["processing_power"] = int(level * 10 * quality_multiplier)
        stats["cores"] = min(32, max(1, int(level * 0.8 * quality_multiplier)))
        stats["clock_speed"] = round(2.0 + (level * 0.4 + random.random()) * quality_multiplier, 1)
        stats["architecture"] = random.choice(["x86", "x64", "ARM", "RISC", "Quantum"])
        stats["cache"] = f"{min(64, int(level * quality_multiplier))}MB"
        
    elif hardware_type == "RAM":
        stats["capacity"] = int(4 * (2 ** (int(level / 2) - 1)) * quality_multiplier)  # 4, 8, 16, 32, 64, 128 GB
        stats["speed"] = int(2400 + level * 400 * quality_multiplier)
        stats["type"] = random.choice(["DDR4", "DDR5", "LPDDR5", "HBM", "Quantum"])
        stats["latency"] = max(1, int(20 - level * quality_multiplier * 0.5))
        
    elif hardware_type == "GPU":
        stats["processing_power"] = int(level * 15 * quality_multiplier)
        stats["vram"] = int(2 * (2 ** (int(level / 2) - 1)) * quality_multiplier)  # 2, 4, 8, 16, 32 GB
        stats["cores"] = int(512 * level * quality_multiplier)
        stats["ray_tracing"] = random.choice([0, 0, 0, 1, 1]) if level > 5 else 0
        stats["clock_speed"] = int(1000 + level * 200 * quality_multiplier)
        
    elif hardware_type == "Motherboard":
        stats["form_factor"] = random.choice(["ATX", "Micro-ATX", "Mini-ITX", "Extended-ATX"])
        stats["chipset"] = f"Z{random.randint(5, 9)}00"
        stats["ram_slots"] = min(8, max(2, int(level / 2 * quality_multiplier)))
        stats["pcie_slots"] = min(6, max(1, int(level / 2 * quality_multiplier)))
        stats["sata_ports"] = min(12, max(2, int(level * quality_multiplier)))
        stats["usb_ports"] = min(12, max(4, int(level * 1.5 * quality_multiplier)))
        
    elif hardware_type in ["HDD", "SSD", "External HDD", "USB Drive"]:
        # Capacité en GB pour les petits stockages, en TB pour les grands
        if hardware_type == "USB Drive":
            base_capacity = 16 * (2 ** (int(level / 2) - 1))  # 16, 32, 64, 128, 256 GB
            stats["capacity"] = int(base_capacity * quality_multiplier)
            stats["unit"] = "GB"
        elif hardware_type == "SSD":
            base_capacity = 256 * (2 ** (int(level / 3) - 1))  # 256, 512, 1024, 2048 GB
            capacity = int(base_capacity * quality_multiplier)
            if capacity >= 1024:
                stats["capacity"] = capacity / 1024
                stats["unit"] = "TB"
            else:
                stats["capacity"] = capacity
                stats["unit"] = "GB"
        else:  # HDD, External HDD
            base_capacity = 1 * (2 ** (int(level / 2) - 1))  # 1, 2, 4, 8, 16 TB
            stats["capacity"] = int(base_capacity * quality_multiplier)
            stats["unit"] = "TB"
        
        # Vitesse
        if hardware_type == "SSD":
            stats["read_speed"] = int(500 + level * 300 * quality_multiplier)
            stats["write_speed"] = int(400 + level * 250 * quality_multiplier)
            stats["type"] = random.choice(["SATA", "NVMe", "M.2", "PCIe"])
        elif hardware_type == "USB Drive":
            stats["read_speed"] = int(30 + level * 20 * quality_multiplier)
            stats["write_speed"] = int(20 + level * 15 * quality_multiplier)
            stats["type"] = random.choice(["USB 2.0", "USB 3.0", "USB 3.1", "USB-C"])
        else:  # HDD, External HDD
            stats["read_speed"] = int(80 + level * 20 * quality_multiplier)
            stats["write_speed"] = int(70 + level * 15 * quality_multiplier)
            stats["rpm"] = random.choice([5400, 7200, 10000])
            
    elif hardware_type == "Network Card":
        stats["speed"] = random.choice([10, 100, 1000, 10000])  # Mbps
        stats["wifi"] = random.choice([0, 1])
        if stats["wifi"]:
            stats["wifi_standard"] = random.choice(["802.11n", "802.11ac", "802.11ax", "802.11be"])
        stats["bluetooth"] = random.choice([0, 1])
        if stats["bluetooth"]:
            stats["bluetooth_version"] = random.choice(["4.0", "5.0", "5.1", "5.2"])
        stats["ports"] = min(8, max(1, int(level / 2 * quality_multiplier)))
        
    elif hardware_type == "Cooling System":
        stats["type"] = random.choice(["Air", "Liquid", "Hybrid", "Nitrogen", "Phase-Change"])
        stats["rpm"] = int(1000 + level * 200 * quality_multiplier)
        stats["noise_level"] = max(5, int(30 - level * quality_multiplier))  # dB, lower is better
        stats["cooling_capacity"] = int(level * 10 * quality_multiplier)
        
    elif hardware_type == "Power Supply":
        stats["wattage"] = int(400 + level * 100 * quality_multiplier)
        stats["efficiency"] = random.choice(["80+ Bronze", "80+ Silver", "80+ Gold", "80+ Platinum", "80+ Titanium"])
        stats["modular"] = random.choice(["Non-Modular", "Semi-Modular", "Fully-Modular"])
        stats["fan_size"] = random.choice(["120mm", "140mm"])
        
    elif hardware_type == "Router":
        stats["wifi_standard"] = random.choice(["802.11n", "802.11ac", "802.11ax", "802.11be"])
        stats["speed"] = int(100 * (2 ** (int(level / 2) - 1)) * quality_multiplier)  # 100, 200, 400, 800 Mbps
        stats["range"] = int(level * 5 * quality_multiplier)  # meters
        stats["ports"] = min(8, max(1, int(level / 2 * quality_multiplier)))
        stats["dual_band"] = random.choice([0, 1])
        if stats["dual_band"]:
            stats["bands"] = ["2.4GHz", "5GHz"]
        else:
            stats["bands"] = ["2.4GHz"]
        
    elif hardware_type == "Bluetooth Adapter":
        stats["version"] = random.choice(["4.0", "5.0", "5.1", "5.2"])
        stats["range"] = int(level * 5 * quality_multiplier)  # meters
        stats["data_rate"] = int(1 + level * 0.5 * quality_multiplier)  # Mbps
        
    elif hardware_type == "WiFi Antenna":
        stats["gain"] = int(3 + level * quality_multiplier)  # dBi
        stats["range"] = int(level * 10 * quality_multiplier)  # meters
        stats["frequency_range"] = random.choice(["2.4GHz", "5GHz", "2.4GHz/5GHz"])
        
    elif hardware_type == "Raspberry Pi":
        stats["model"] = f"Raspberry Pi {random.randint(3, 5)} Model {random.choice(['A', 'B', 'B+'])}"
        stats["ram"] = int(1 * (2 ** (int(level / 3) - 1)) * quality_multiplier)  # 1, 2, 4, 8 GB
        stats["cores"] = min(8, max(1, int(level / 2 * quality_multiplier)))
        stats["clock_speed"] = round(1.0 + (level * 0.2 + random.random()) * quality_multiplier, 1)
        stats["usb_ports"] = min(6, max(2, int(level / 2 * quality_multiplier)))
        stats["hdmi_ports"] = random.choice([1, 2])
        stats["ethernet"] = random.choice([0, 1])
        stats["wifi"] = random.choice([0, 1])
        stats["bluetooth"] = random.choice([0, 1])
        
    else:  # Type générique
        stats["quality_level"] = quality_level
        stats["performance"] = int(level * 10 * quality_multiplier)
        stats["reliability"] = int(level * 5 * quality_multiplier)
        stats["power_efficiency"] = int(level * 3 * quality_multiplier)
        
    return stats