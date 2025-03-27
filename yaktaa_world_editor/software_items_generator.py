"""
Module pour la génération des logiciels
Contient les fonctions pour créer des logiciels dans le monde
"""

import uuid
import json
import logging
import random
from typing import List, Dict, Any, Tuple

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.SoftwareItems")

def generate_software_items(db, world_id: str, device_ids: List[str], 
                           building_ids: List[str], character_ids: List[str], 
                           num_items: int, random) -> List[str]:
    """
    Génère des logiciels pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        device_ids: Liste des IDs des appareils
        building_ids: Liste des IDs des bâtiments
        character_ids: Liste des IDs des personnages
        num_items: Nombre de logiciels à générer
        random: Instance de random pour la génération aléatoire
        
    Returns:
        Liste des IDs des logiciels générés
    """
    software_ids = []
    cursor = db.conn.cursor()
    
    # Vérifier si la table software_items existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='software_items'
    """)
    
    if not cursor.fetchone():
        # Créer la table software_items si elle n'existe pas
        cursor.execute("""
            CREATE TABLE software_items (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                software_type TEXT NOT NULL,
                version TEXT,
                license_type TEXT,
                price INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'COMMON',
                location_type TEXT,
                location_id TEXT,
                is_installed INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 0,
                is_trial INTEGER DEFAULT 0,
                is_cracked INTEGER DEFAULT 0,
                system_requirements TEXT,
                capabilities TEXT,
                metadata TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
        """)
        db.conn.commit()
        logger.info("Table software_items créée")
    
    # Types de logiciels
    software_types = [
        "ANTIVIRUS", "FIREWALL", "OS", "BROWSER", "VPN", "HACKING_TOOL", 
        "CRYPTOGRAPHY", "DATABASE", "DEVELOPMENT", "MEDIA", "PRODUCTIVITY", 
        "COMMUNICATION", "AI_ASSISTANT", "DATA_BROKER", "CLOUD_STORAGE"
    ]
    
    # Fabricants de logiciels
    manufacturers = {
        "ANTIVIRUS": ["NetShield", "CyberGuard", "VirusZero", "SecureNet", "ThreatBlock"],
        "FIREWALL": ["FireWall", "NetBarrier", "DigitalFortress", "SecurityGate", "PacketGuard"],
        "OS": ["NexOS", "CyberSys", "QuantumOS", "CoreSystem", "NetrixOS"],
        "BROWSER": ["WebSurfer", "NetExplorer", "CyberBrowse", "DataStream", "QuantumNet"],
        "VPN": ["ShadowNet", "PrivacyTunnel", "SecureConnect", "NetCloak", "CyberShield"],
        "HACKING_TOOL": ["BlackHat", "NetBreaker", "CodeCracker", "SystemBreaker", "Infiltrator"],
        "CRYPTOGRAPHY": ["CryptoSafe", "QuantumCrypt", "SecureHash", "KeyMaster", "CipherLock"],
        "DATABASE": ["DataCore", "InfoBank", "QueryMaster", "DataVault", "RecordKeeper"],
        "DEVELOPMENT": ["CodeForge", "DevStudio", "ProgrammerPro", "LogicBuilder", "SyntaxMaster"],
        "MEDIA": ["MediaStream", "AudioVision", "PixelPlayer", "SoundSurge", "VideoVault"],
        "PRODUCTIVITY": ["TaskForce", "WorkFlow", "ProductivitySuite", "TimeManager", "ProjectMaster"],
        "COMMUNICATION": ["NetTalk", "CommLink", "MessageMaster", "ChatSphere", "VoiceNet"],
        "AI_ASSISTANT": ["BrainBot", "CyberAssist", "SmartAI", "LogicHelper", "ThinkTank"],
        "DATA_BROKER": ["DataTrader", "InfoMarket", "ByteBroker", "DataMerchant", "InfoExchange"],
        "CLOUD_STORAGE": ["SkyVault", "CloudKeeper", "NetStorage", "DataCloud", "ByteBank"]
    }
    
    # Niveaux de version
    version_patterns = [
        "{major}.{minor}", 
        "{major}.{minor}.{patch}", 
        "{major}.{minor} {codename}", 
        "{year} Edition", 
        "v{major} Build {build}"
    ]
    
    # Types de licences
    license_types = [
        "COMMERCIAL", "TRIAL", "SHAREWARE", "FREEWARE", "OPEN_SOURCE", 
        "SUBSCRIPTION", "ENTERPRISE", "EDUCATIONAL", "ILLEGAL_COPY"
    ]
    
    # Exigences système par type
    base_system_requirements = {
        "LOW": {
            "cpu": "1 GHz",
            "ram": "512 MB",
            "storage": "100 MB",
            "os": "Any"
        },
        "MEDIUM": {
            "cpu": "2 GHz Dual Core",
            "ram": "2 GB",
            "storage": "500 MB",
            "os": "Windows 7 / Linux / macOS 10.10+"
        },
        "HIGH": {
            "cpu": "3 GHz Quad Core",
            "ram": "4 GB",
            "storage": "2 GB",
            "os": "Windows 10 / Linux / macOS 11+"
        },
        "VERY_HIGH": {
            "cpu": "3.5 GHz Octa Core",
            "ram": "8 GB",
            "storage": "5 GB",
            "os": "Windows 10 64-bit / Linux / macOS 12+"
        }
    }
    
    # Raretés
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    rarity_weights = [40, 30, 20, 8, 2]
    
    # Générer les logiciels
    for i in range(num_items):
        # ID unique
        software_id = f"software_{uuid.uuid4()}"
        
        # Déterminer si on place ce logiciel dans un appareil, un bâtiment ou sur un personnage
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
        
        # Type de logiciel
        software_type = random.choice(software_types)
        
        # Fabricant
        manufacturer = random.choice(manufacturers.get(software_type, ["GenericSoft"]))
        
        # Nom du produit
        product_names = {
            "ANTIVIRUS": ["Protector", "Guardian", "Shield", "Defender", "Sentry"],
            "FIREWALL": ["Barrier", "Wall", "Fortress", "Guard", "Defense"],
            "OS": ["System", "Core", "Platform", "Environment", "Interface"],
            "BROWSER": ["Explorer", "Navigator", "Browser", "Surfer", "Voyager"],
            "VPN": ["Tunnel", "Cloak", "Shield", "Protector", "Secure"],
            "HACKING_TOOL": ["Infiltrator", "Breaker", "Cracker", "Master", "Kit"],
            "CRYPTOGRAPHY": ["Crypt", "Cipher", "Lock", "Vault", "Secure"],
            "DATABASE": ["Base", "Vault", "Storage", "Archive", "Repository"],
            "DEVELOPMENT": ["Studio", "Workshop", "Forge", "Lab", "Factory"],
            "MEDIA": ["Player", "View", "Stream", "Cast", "Suite"],
            "PRODUCTIVITY": ["Office", "Work", "Task", "Project", "Manager"],
            "COMMUNICATION": ["Talk", "Chat", "Message", "Connect", "Communicate"],
            "AI_ASSISTANT": ["AI", "Assistant", "Helper", "Mind", "Genius"],
            "DATA_BROKER": ["Broker", "Market", "Exchange", "Trader", "Dealer"],
            "CLOUD_STORAGE": ["Cloud", "Drive", "Storage", "Vault", "Backup"]
        }
        
        product_name = random.choice(product_names.get(software_type, ["Software"]))
        
        # Nom complet
        name = f"{manufacturer} {product_name}"
        
        # Version
        pattern = random.choice(version_patterns)
        major = random.randint(1, 20)
        minor = random.randint(0, 99)
        patch = random.randint(0, 99)
        build = random.randint(1000, 9999)
        year = 2070 + random.randint(0, 10)
        codenames = ["Alpha", "Beta", "Delta", "Gamma", "Omega", "Sigma", "Epsilon", "Zeta", "Eta", "Theta"]
        codename = random.choice(codenames)
        
        version = pattern.format(major=major, minor=minor, patch=patch, build=build, year=year, codename=codename)
        
        # Rareté
        rarity = random.choices(rarities, weights=rarity_weights, k=1)[0]
        
        # Licence
        if rarity == "LEGENDARY":
            license_candidates = ["ENTERPRISE", "EDUCATIONAL", "ILLEGAL_COPY"]
        elif rarity == "EPIC":
            license_candidates = ["COMMERCIAL", "ENTERPRISE", "ILLEGAL_COPY"]
        elif rarity == "RARE":
            license_candidates = ["COMMERCIAL", "SUBSCRIPTION", "TRIAL", "SHAREWARE"]
        elif rarity == "UNCOMMON":
            license_candidates = ["COMMERCIAL", "TRIAL", "SHAREWARE", "FREEWARE"]
        else:  # COMMON
            license_candidates = ["FREEWARE", "OPEN_SOURCE", "TRIAL", "SHAREWARE"]
            
        license_type = random.choice(license_candidates)
        
        # Exigences système selon le type et la rareté
        req_level = "LOW"
        if software_type in ["OS", "DEVELOPMENT", "MEDIA"]:
            if rarity in ["EPIC", "LEGENDARY"]:
                req_level = "VERY_HIGH"
            elif rarity == "RARE":
                req_level = "HIGH"
            else:
                req_level = "MEDIUM"
        elif software_type in ["ANTIVIRUS", "FIREWALL", "HACKING_TOOL", "AI_ASSISTANT"]:
            if rarity in ["EPIC", "LEGENDARY"]:
                req_level = "HIGH"
            elif rarity == "RARE":
                req_level = "MEDIUM"
            else:
                req_level = "LOW"
        
        system_requirements = base_system_requirements[req_level].copy()
        
        # Ajouter des exigences spécifiques selon le type
        if software_type == "OS":
            system_requirements["boot_time"] = f"{random.randint(5, 60)} seconds"
            system_requirements["supported_architectures"] = ["x86_64", "ARM64"] if random.random() > 0.5 else ["x86_64"]
        elif software_type == "ANTIVIRUS":
            system_requirements["background_scan"] = "Yes" if random.random() > 0.3 else "No"
        elif software_type == "FIREWALL":
            system_requirements["packet_inspection"] = "Deep" if rarity in ["RARE", "EPIC", "LEGENDARY"] else "Basic"
        
        # Capacités selon le type et la rareté
        capabilities = generate_capabilities(software_type, rarity, random)
        
        # Prix selon la rareté et le type
        base_prices = {
            "COMMON": 50,
            "UNCOMMON": 200,
            "RARE": 1000,
            "EPIC": 5000,
            "LEGENDARY": 25000
        }
        
        # Modificateurs de prix selon le type
        price_modifiers = {
            "OS": 2.0,
            "ANTIVIRUS": 1.5,
            "FIREWALL": 1.5,
            "HACKING_TOOL": 2.5,
            "AI_ASSISTANT": 2.0,
            "CRYPTOGRAPHY": 1.8,
            "DATABASE": 1.7,
            "DEVELOPMENT": 1.9,
            "VPN": 1.3,
            "BROWSER": 0.8,
            "MEDIA": 0.7,
            "PRODUCTIVITY": 1.2,
            "COMMUNICATION": 0.9,
            "DATA_BROKER": 2.2,
            "CLOUD_STORAGE": 1.0
        }
        
        # Réduction de prix selon la licence
        license_price_modifiers = {
            "COMMERCIAL": 1.0,
            "TRIAL": 0.1,
            "SHAREWARE": 0.5,
            "FREEWARE": 0.0,
            "OPEN_SOURCE": 0.0,
            "SUBSCRIPTION": 0.8,
            "ENTERPRISE": 3.0,
            "EDUCATIONAL": 0.4,
            "ILLEGAL_COPY": 0.3
        }
        
        base_price = base_prices[rarity]
        modifier = price_modifiers.get(software_type, 1.0)
        license_modifier = license_price_modifiers.get(license_type, 1.0)
        
        price = int(base_price * modifier * license_modifier)
        
        # Paramètres additionnels
        is_installed = 1 if location_type == "device" and random.random() > 0.5 else 0
        is_active = 1 if is_installed and random.random() > 0.3 else 0
        is_trial = 1 if license_type == "TRIAL" else 0
        is_cracked = 1 if license_type == "ILLEGAL_COPY" else 0
        
        # Description
        description = generate_description(name, software_type, version, rarity, random)
        
        # Standardisation des métadonnées - utilise la fonction de MetadataStandardizer
        metadata = MetadataStandardizer.standardize_software_metadata(
            software_type=software_type,
            version=version,
            license_type=license_type,
            manufacturer=manufacturer,
            system_requirements=system_requirements,
            capabilities=capabilities,
            rarity=rarity,
            is_installed=bool(is_installed),
            is_active=bool(is_active),
            is_trial=bool(is_trial),
            is_cracked=bool(is_cracked)
        )
        
        # Insertion dans la base de données
        cursor.execute("""
            INSERT INTO software_items (
                id, world_id, name, description, software_type, version, license_type,
                price, rarity, location_type, location_id, is_installed, is_active,
                is_trial, is_cracked, system_requirements, capabilities, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            software_id, world_id, name, description, software_type, version, license_type,
            price, rarity, location_type, location_id, is_installed, is_active,
            is_trial, is_cracked, json.dumps(system_requirements), json.dumps(capabilities), json.dumps(metadata)
        ))
        
        software_ids.append(software_id)
    
    db.conn.commit()
    logger.info(f"{len(software_ids)} logiciels générés pour le monde {world_id}")
    
    return software_ids

def generate_capabilities(software_type, rarity, random):
    capabilities = []
    
    if software_type == "ANTIVIRUS":
        capabilities.append("Virus Scanning")
        capabilities.append("Malware Detection")
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            capabilities.append("Rootkit Detection")
            capabilities.append("Real-time Protection")
    elif software_type == "FIREWALL":
        capabilities.append("Packet Filtering")
        capabilities.append("Stateful Inspection")
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            capabilities.append("Deep Packet Inspection")
            capabilities.append("Intrusion Detection")
    elif software_type == "HACKING_TOOL":
        capabilities.append("Password Cracking")
        capabilities.append("Network Scanning")
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            capabilities.append("Exploit Development")
            capabilities.append("Social Engineering")
    elif software_type == "AI_ASSISTANT":
        capabilities.append("Natural Language Processing")
        capabilities.append("Machine Learning")
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            capabilities.append("Speech Recognition")
            capabilities.append("Image Recognition")
    
    return capabilities

def generate_description(name, software_type, version, rarity, random):
    descriptions = {
        "ANTIVIRUS": [
            "Protect your device from malware and viruses with {}.",
            "Stay safe online with {}.",
            "{}: the ultimate antivirus solution."
        ],
        "FIREWALL": [
            "Block unwanted traffic with {}.",
            "Protect your network with {}.",
            "{}: the firewall you can trust."
        ],
        "HACKING_TOOL": [
            "Take your hacking skills to the next level with {}.",
            "Unleash your inner hacker with {}.",
            "{}: the ultimate hacking tool."
        ],
        "AI_ASSISTANT": [
            "Get assistance with {}.",
            "Make your life easier with {}.",
            "{}: your personal AI assistant."
        ]
    }
    
    description = random.choice(descriptions.get(software_type, ["{}: a software solution."]))
    description = description.format(name)
    
    return description
