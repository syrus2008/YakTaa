"""
Module pour la gestion du matériel informatique (hardware) dans YakTaa
Ce module définit les différents types de composants que le joueur peut équiper.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid

logger = logging.getLogger("YakTaa.Items.Hardware")

class HardwareRarity(Enum):
    """Rareté des composants matériels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    UNIQUE = "unique"

class HardwareType(Enum):
    """Types de composants matériels"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    SECURITY = "security"
    TOOL = "tool"

class Hardware:
    """Classe de base pour tous les composants matériels"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Composant inconnu", 
                 description: str = "Un composant matériel standard", 
                 type: HardwareType = HardwareType.CPU,
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 stats: Dict[str, int] = None,
                 abilities: List[str] = None,
                 icon: str = "default_hardware"):
        """
        Initialise un composant matériel
        
        Args:
            id: Identifiant unique du composant
            name: Nom du composant
            description: Description du composant
            type: Type de composant (CPU, mémoire, etc.)
            rarity: Rareté du composant
            level: Niveau requis pour utiliser le composant
            price: Prix du composant
            stats: Statistiques du composant
            abilities: Capacités spéciales du composant
            icon: Icône du composant
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.type = type
        self.rarity = rarity
        self.level = level
        self.price = price
        self.stats = stats or {}
        self.abilities = abilities or []
        self.icon = icon
        
        logger.debug(f"Composant matériel créé: {self.name} ({self.type.value})")
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """Récupère la valeur d'une statistique"""
        return self.stats.get(stat_name, default)
    
    def has_ability(self, ability_name: str) -> bool:
        """Vérifie si le composant a une capacité spécifique"""
        return ability_name in self.abilities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le composant en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "rarity": self.rarity.value,
            "level": self.level,
            "price": self.price,
            "stats": self.stats,
            "abilities": self.abilities,
            "icon": self.icon
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hardware':
        """Crée un composant à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            name=data.get("name", "Composant inconnu"),
            description=data.get("description", "Un composant matériel standard"),
            type=HardwareType(data.get("type", "cpu")),
            rarity=HardwareRarity(data.get("rarity", "common")),
            level=data.get("level", 1),
            price=data.get("price", 100),
            stats=data.get("stats", {}),
            abilities=data.get("abilities", []),
            icon=data.get("icon", "default_hardware")
        )

# Alias de la classe Hardware pour la compatibilité avec d'autres modules
HardwareItem = Hardware

class CPU(Hardware):
    """Processeur (CPU) pour améliorer la vitesse de calcul et de hacking"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "CPU standard", 
                 description: str = "Un processeur de base pour les opérations de hacking", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 clock_speed: int = 1,  # GHz
                 cores: int = 1,
                 architecture: str = "x86",
                 abilities: List[str] = None,
                 icon: str = "cpu"):
        """
        Initialise un CPU
        
        Args:
            clock_speed: Vitesse d'horloge en GHz
            cores: Nombre de cœurs
            architecture: Architecture du processeur
        """
        stats = {
            "clock_speed": clock_speed,
            "cores": cores,
            "processing_power": clock_speed * cores,
            "hack_speed_bonus": int(clock_speed * cores * 0.5)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.CPU,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )
        
        self.architecture = architecture

class Memory(Hardware):
    """Mémoire RAM pour améliorer la capacité à exécuter plusieurs tâches simultanément"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "RAM standard", 
                 description: str = "Module de mémoire vive pour les opérations simultanées", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 capacity: int = 4,  # GB
                 speed: int = 1600,  # MHz
                 type: str = "DDR3",
                 abilities: List[str] = None,
                 icon: str = "memory"):
        """
        Initialise un module de mémoire
        
        Args:
            capacity: Capacité en GB
            speed: Vitesse en MHz
            type: Type de mémoire (DDR3, DDR4, etc.)
        """
        stats = {
            "capacity": capacity,
            "speed": speed,
            "multitasking": int(capacity * 0.5),
            "buffer_size": int(capacity * speed / 1000)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.MEMORY,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )
        
        self.memory_type = type

class Storage(Hardware):
    """Stockage pour améliorer la capacité à stocker des données et des programmes"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Disque standard", 
                 description: str = "Stockage de données de base", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 capacity: int = 256,  # GB
                 speed: int = 100,  # MB/s
                 type: str = "HDD",
                 abilities: List[str] = None,
                 icon: str = "storage"):
        """
        Initialise un périphérique de stockage
        
        Args:
            capacity: Capacité en GB
            speed: Vitesse en MB/s
            type: Type de stockage (HDD, SSD, etc.)
        """
        stats = {
            "capacity": capacity,
            "speed": speed,
            "download_speed": int(speed * 0.8),
            "upload_speed": int(speed * 0.6)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.STORAGE,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )
        
        self.storage_type = type

class Network(Hardware):
    """Interface réseau pour améliorer la connectivité et la vitesse de connexion"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Carte réseau standard", 
                 description: str = "Interface réseau de base", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 bandwidth: int = 100,  # Mbps
                 range: int = 10,  # mètres
                 protocols: List[str] = None,
                 abilities: List[str] = None,
                 icon: str = "network"):
        """
        Initialise une interface réseau
        
        Args:
            bandwidth: Bande passante en Mbps
            range: Portée en mètres
            protocols: Protocoles supportés
        """
        protocols = protocols or ["WiFi", "Ethernet"]
        
        stats = {
            "bandwidth": bandwidth,
            "range": range,
            "connection_strength": int(bandwidth * 0.1),
            "signal_boost": int(range * 0.5)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.NETWORK,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )
        
        self.protocols = protocols

class Security(Hardware):
    """Module de sécurité pour améliorer la défense contre les attaques et la discrétion"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Module de sécurité standard", 
                 description: str = "Protection de base contre les intrusions", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 encryption: int = 1,  # niveau d'encryption
                 firewall: int = 1,  # niveau de pare-feu
                 stealth: int = 1,  # niveau de discrétion
                 abilities: List[str] = None,
                 icon: str = "security"):
        """
        Initialise un module de sécurité
        
        Args:
            encryption: Niveau d'encryption
            firewall: Niveau de pare-feu
            stealth: Niveau de discrétion
        """
        stats = {
            "encryption": encryption,
            "firewall": firewall,
            "stealth": stealth,
            "detection_resistance": int((encryption + stealth) * 0.5)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.SECURITY,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )

class Tool(Hardware):
    """Outil spécialisé pour des fonctionnalités de hacking avancées"""
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Outil standard", 
                 description: str = "Outil de base pour le hacking", 
                 rarity: HardwareRarity = HardwareRarity.COMMON,
                 level: int = 1,
                 price: int = 100,
                 function: str = "generic",
                 power: int = 1,
                 cooldown: int = 60,  # secondes
                 abilities: List[str] = None,
                 icon: str = "tool"):
        """
        Initialise un outil spécialisé
        
        Args:
            function: Fonction principale de l'outil
            power: Puissance de l'outil
            cooldown: Temps de recharge en secondes
        """
        stats = {
            "power": power,
            "cooldown": cooldown,
            "effectiveness": int(power * 100 / cooldown)
        }
        
        super().__init__(
            id=id,
            name=name,
            description=description,
            type=HardwareType.TOOL,
            rarity=rarity,
            level=level,
            price=price,
            stats=stats,
            abilities=abilities,
            icon=icon
        )
        
        self.function = function

# Générateur de composants matériels prédéfinis
def generate_hardware_catalog() -> Dict[str, List[Hardware]]:
    """
    Génère un catalogue de composants matériels prédéfinis
    
    Returns:
        Dictionnaire de composants par type
    """
    catalog = {
        HardwareType.CPU.value: [],
        HardwareType.MEMORY.value: [],
        HardwareType.STORAGE.value: [],
        HardwareType.NETWORK.value: [],
        HardwareType.SECURITY.value: [],
        HardwareType.TOOL.value: []
    }
    
    # CPUs
    catalog[HardwareType.CPU.value].extend([
        CPU(
            name="Processeur NanoCore 1000",
            description="Un processeur d'entrée de gamme pour les débutants en hacking.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=200,
            clock_speed=1.5,
            cores=2,
            architecture="x86"
        ),
        CPU(
            name="QuantumByte QX-200",
            description="Processeur de milieu de gamme avec une bonne balance performance/prix.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=500,
            clock_speed=2.5,
            cores=4,
            architecture="x64"
        ),
        CPU(
            name="CyberTech Nexus 3000",
            description="Processeur haut de gamme pour les hackers professionnels.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=1200,
            clock_speed=3.8,
            cores=8,
            architecture="x64",
            abilities=["overclock", "parallel_processing"]
        ),
        CPU(
            name="SynthSys Quantum Core",
            description="Processeur quantique expérimental offrant des performances inégalées.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=3000,
            clock_speed=5.0,
            cores=16,
            architecture="quantum",
            abilities=["quantum_calculation", "overclock", "parallel_processing"]
        )
    ])
    
    # Mémoire
    catalog[HardwareType.MEMORY.value].extend([
        Memory(
            name="Module RAM Standard",
            description="Module de mémoire basique pour les opérations simples.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=150,
            capacity=4,
            speed=1600,
            type="DDR3"
        ),
        Memory(
            name="HyperRAM 8GB",
            description="Module de mémoire rapide pour une meilleure multitâche.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=400,
            capacity=8,
            speed=2400,
            type="DDR4"
        ),
        Memory(
            name="NexusRAM Extreme",
            description="Mémoire haute performance avec dissipation thermique avancée.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=900,
            capacity=16,
            speed=3200,
            type="DDR4",
            abilities=["quick_access", "memory_compression"]
        ),
        Memory(
            name="QuantumRAM Infinity",
            description="Technologie de mémoire révolutionnaire avec capacité quasi-illimitée.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=2500,
            capacity=32,
            speed=4800,
            type="DDR5",
            abilities=["quantum_caching", "quick_access", "memory_compression"]
        )
    ])
    
    # Stockage
    catalog[HardwareType.STORAGE.value].extend([
        Storage(
            name="Disque dur basique",
            description="Stockage mécanique standard pour les données non-critiques.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=100,
            capacity=500,
            speed=80,
            type="HDD"
        ),
        Storage(
            name="SSD NeoStore 256",
            description="Stockage SSD offrant de bonnes performances pour le prix.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=350,
            capacity=256,
            speed=500,
            type="SSD"
        ),
        Storage(
            name="CyberDrive Pro",
            description="SSD NVMe ultra-rapide pour les transferts de données critiques.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=800,
            capacity=1000,
            speed=2000,
            type="NVMe",
            abilities=["quick_access", "data_compression"]
        ),
        Storage(
            name="QuantumCube Storage",
            description="Stockage holographique quantique avec vitesse et capacité exceptionnelles.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=2200,
            capacity=4000,
            speed=5000,
            type="Quantum",
            abilities=["instant_access", "data_compression", "quantum_encryption"]
        )
    ])
    
    # Réseau
    catalog[HardwareType.NETWORK.value].extend([
        Network(
            name="Adaptateur WiFi standard",
            description="Interface réseau basique pour les connexions sans fil.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=120,
            bandwidth=100,
            range=15,
            protocols=["WiFi", "Bluetooth"]
        ),
        Network(
            name="NetRunner 500",
            description="Carte réseau polyvalente avec bonne portée et vitesse.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=380,
            bandwidth=500,
            range=30,
            protocols=["WiFi", "Bluetooth", "5G", "Ethernet"]
        ),
        Network(
            name="CyberLink Ultra",
            description="Interface réseau avancée avec amplificateur de signal intégré.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=950,
            bandwidth=1000,
            range=50,
            protocols=["WiFi", "Bluetooth", "5G", "Ethernet", "Satellite"],
            abilities=["signal_boost", "frequency_hopping"]
        ),
        Network(
            name="QuantumLink Nexus",
            description="Technologie de communication quantique permettant des connexions instantanées.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=2800,
            bandwidth=10000,
            range=100,
            protocols=["WiFi", "Bluetooth", "5G", "Ethernet", "Satellite", "Quantum"],
            abilities=["quantum_tunneling", "signal_boost", "frequency_hopping", "stealth_connection"]
        )
    ])
    
    # Sécurité
    catalog[HardwareType.SECURITY.value].extend([
        Security(
            name="Module de cryptage basique",
            description="Protection élémentaire contre les intrusions simples.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=150,
            encryption=1,
            firewall=1,
            stealth=1
        ),
        Security(
            name="FireShield 2.0",
            description="Module de sécurité intermédiaire avec pare-feu renforcé.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=450,
            encryption=2,
            firewall=3,
            stealth=2
        ),
        Security(
            name="StealthGuard Elite",
            description="Système de sécurité avancé avec masquage d'adresse et cryptage multicouche.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=1100,
            encryption=4,
            firewall=4,
            stealth=5,
            abilities=["ip_masking", "intrusion_detection"]
        ),
        Security(
            name="QuantumShield Absolute",
            description="Sécurité quantique inviolable avec contre-mesures actives.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=3200,
            encryption=8,
            firewall=7,
            stealth=8,
            abilities=["quantum_encryption", "active_countermeasures", "ip_masking", "intrusion_detection"]
        )
    ])
    
    # Outils
    catalog[HardwareType.TOOL.value].extend([
        Tool(
            name="Multi-outil de hacking basique",
            description="Outil simple pour les opérations de hacking élémentaires.",
            rarity=HardwareRarity.COMMON,
            level=1,
            price=200,
            function="brute_force",
            power=1,
            cooldown=60
        ),
        Tool(
            name="CrackMaster 3000",
            description="Outil spécialisé dans le craquage de mots de passe.",
            rarity=HardwareRarity.UNCOMMON,
            level=5,
            price=550,
            function="password_cracking",
            power=3,
            cooldown=45
        ),
        Tool(
            name="Infiltrator Pro",
            description="Dispositif avancé permettant de contourner la plupart des systèmes de sécurité.",
            rarity=HardwareRarity.RARE,
            level=10,
            price=1300,
            function="system_bypass",
            power=5,
            cooldown=30,
            abilities=["backdoor_implant", "log_eraser"]
        ),
        Tool(
            name="OmniHack Nexus",
            description="L'outil ultime de hacking, capable de s'adapter à n'importe quelle situation.",
            rarity=HardwareRarity.EPIC,
            level=15,
            price=3500,
            function="universal",
            power=10,
            cooldown=15,
            abilities=["adaptive_algorithms", "backdoor_implant", "log_eraser", "system_override"]
        )
    ])
    
    logger.info(f"Catalogue de matériel généré avec {sum(len(items) for items in catalog.values())} composants")
    return catalog
