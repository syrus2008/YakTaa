"""
Module pour la gestion des items logiciels dans YakTaa.
Définit les différents types de logiciels que le joueur peut acquérir et utiliser.
"""

import logging
import random
from typing import Dict, List, Optional, Any

from .item import Item

logger = logging.getLogger("YakTaa.Items.SoftwareItem")

class SoftwareItem(Item):
    """
    Classe représentant un logiciel (software) dans le jeu
    """
    
    SOFTWARE_TYPES = [
        "OS", "SECURITY", "CRYPTOGRAPHY", "VIRUS", "ANTIVIRUS", "FIREWALL", 
        "EXPLOIT", "UTILITY", "DATABASE", "AI", "VPN", "CRACKING"
    ]
    
    LICENSE_TYPES = ["Freeware", "Shareware", "Trial", "Personal", "Commercial", "Enterprise", "Military", "Black Market"]
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Logiciel inconnu", 
                 description: str = "Un programme informatique mystérieux.",
                 software_type: str = "UTILITY",
                 version: str = "1.0",
                 license_type: str = "Personal",
                 level: int = 1,
                 memory_usage: int = 100,
                 features: Dict[str, Any] = None,
                 requirements: Dict[str, Any] = None,
                 price: int = 100,
                 is_illegal: bool = False,
                 icon: str = "software",
                 properties: Dict[str, Any] = None):
        """
        Initialise un item logiciel
        
        Args:
            id: Identifiant unique de l'item
            name: Nom de l'item
            description: Description de l'item
            software_type: Type de logiciel
            version: Version du logiciel
            license_type: Type de licence
            level: Niveau/tier de l'item (1-10)
            memory_usage: Utilisation mémoire en Mo
            features: Fonctionnalités spécifiques au logiciel
            requirements: Prérequis système pour l'utilisation
            price: Prix de base en crédits
            is_illegal: Si le logiciel est illégal
            icon: Icône représentant l'item
            properties: Propriétés supplémentaires
        """
        # Normaliser le type de logiciel
        if software_type.upper() in [t.upper() for t in self.SOFTWARE_TYPES]:
            for t in self.SOFTWARE_TYPES:
                if software_type.upper() == t.upper():
                    software_type = t
                    break
        else:
            software_type = "UTILITY"  # Type par défaut
            
        # Normaliser le type de licence
        if license_type not in self.LICENSE_TYPES:
            license_type = "Personal"  # Licence par défaut
            
        # Initialiser les fonctionnalités par défaut selon le type
        if features is None:
            features = self._generate_default_features(software_type, level)
            
        # Initialiser les prérequis par défaut
        if requirements is None:
            requirements = self._generate_default_requirements(software_type, level, memory_usage)
        
        # Calculer le prix en fonction des caractéristiques
        price = self._calculate_price(software_type, license_type, level, price, is_illegal)
        
        # Déterminer si le logiciel est illégal s'il n'est pas déjà défini
        if not is_illegal:
            is_illegal = self._determine_illegality(software_type, license_type)
        
        # Initialiser la classe parente
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="software",
            quantity=1,  # Les items logiciels sont généralement des licences uniques
            value=price,
            icon=f"software_{software_type.lower()}",
            properties=properties or {}
        )
        
        # Attributs spécifiques au logiciel
        self.software_type = software_type
        self.version = version
        self.license_type = license_type
        self.level = level
        self.memory_usage = memory_usage
        self.features = features
        self.requirements = requirements
        self.price = price
        self.is_illegal = is_illegal
        
        logger.debug(f"Nouvel item logiciel créé : {name} (Type: {software_type}, Version: {version}, Niveau: {level})")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Retourne les informations à afficher dans l'interface"""
        base_info = super().get_display_info()
        
        # Ajouter les informations spécifiques au logiciel
        software_info = {
            "type": f"Software - {self.software_type}",
            "version": self.version,
            "license": self.license_type,
            "level": f"Niveau {self.level}",
            "memory": f"{self.memory_usage} Mo",
            "legal_status": "Illégal" if self.is_illegal else "Légal",
            "features": self.features,
            "requirements": self.requirements
        }
        
        return {**base_info, **software_info}
    
    def use(self) -> Dict[str, Any]:
        """
        Utilise le logiciel et retourne le résultat
        
        Returns:
            Dictionnaire contenant le résultat de l'utilisation
        """
        # Logique d'utilisation spécifique selon le type
        if self.software_type == "VIRUS":
            return {
                "success": True,
                "message": f"Virus {self.name} v{self.version} déployé. Attendez-vous à des répercussions...",
                "effect": "virus_deployed",
                "level": self.level
            }
        elif self.software_type == "ANTIVIRUS":
            return {
                "success": True,
                "message": f"Analyse antivirus lancée avec {self.name} v{self.version}.",
                "effect": "scan_initiated",
                "level": self.level
            }
        elif self.software_type == "CRYPTOGRAPHY":
            return {
                "success": True,
                "message": f"Outil de chiffrement {self.name} v{self.version} activé.",
                "effect": "encryption_active",
                "level": self.level
            }
        elif self.software_type == "EXPLOIT":
            return {
                "success": True,
                "message": f"Exploit {self.name} v{self.version} chargé et prêt à être utilisé.",
                "effect": "exploit_ready",
                "level": self.level
            }
        elif self.software_type == "VPN":
            return {
                "success": True,
                "message": f"VPN {self.name} v{self.version} activé. Votre connexion est maintenant sécurisée.",
                "effect": "vpn_active",
                "level": self.level
            }
        else:
            return {
                "success": True,
                "message": f"Logiciel {self.name} v{self.version} lancé.",
                "effect": "software_running",
                "level": self.level
            }
    
    def _generate_default_features(self, software_type: str, level: int) -> Dict[str, Any]:
        """
        Génère des fonctionnalités par défaut selon le type de logiciel
        
        Args:
            software_type: Type de logiciel
            level: Niveau de l'item
            
        Returns:
            Dictionnaire de fonctionnalités
        """
        # Fonctionnalités de base selon le type
        base_features = {
            "OS": {
                "interface": ["CLI"] if level < 3 else (["CLI", "GUI"] if level < 7 else ["CLI", "GUI", "VR"]),
                "multitâche": level > 2,
                "multi_utilisateur": level > 4,
                "sécurité": level * 10,
                "compatibilité": min(100, 50 + level * 5)
            },
            "SECURITY": {
                "chiffrement": min(256, 64 * level),
                "détection_intrusion": level > 3,
                "protection_temps_réel": level > 5,
                "niveau_sécurité": level * 10
            },
            "CRYPTOGRAPHY": {
                "algorithmes": ["Simple"] if level < 3 else (["Simple", "Avancé"] if level < 7 else ["Simple", "Avancé", "Quantique"]),
                "longueur_clé": min(4096, 128 * level),
                "vitesse": level * 10,
                "résistance": level * 12
            },
            "VIRUS": {
                "furtivité": level * 8,
                "persistance": level * 7,
                "dommages": level * 15,
                "propagation": min(10, level),
                "détectabilité": max(5, 50 - level * 5)
            },
            "ANTIVIRUS": {
                "détection": min(95, 50 + level * 5),
                "temps_réel": level > 2,
                "heuristique": level > 4,
                "mise_quarantaine": level > 3,
                "désinfection": level * 9
            },
            "FIREWALL": {
                "filtrage": min(10, level),
                "analyse_protocole": level > 3,
                "adaptabilité": level * 8,
                "blocage": min(95, 50 + level * 5)
            },
            "EXPLOIT": {
                "compatibilité": min(10, level),
                "succès": min(90, 40 + level * 5),
                "furtivité": level * 10,
                "type": ["Buffer Overflow"] if level < 3 else (["Buffer Overflow", "SQL Injection"] if level < 5 else 
                        ["Buffer Overflow", "SQL Injection", "Zero-day"])
            },
            "UTILITY": {
                "outils": min(20, level * 2),
                "performance": level * 10,
                "interface": "CLI" if level < 4 else ("GUI" if level < 8 else "VR")
            },
            "DATABASE": {
                "capacité": f"{min(10000, level * 1000)} entrées",
                "requêtes_complexes": level > 3,
                "chiffrement": level > 5,
                "redondance": level > 7
            },
            "AI": {
                "apprentissage": level > 2,
                "adaptation": level * 8,
                "prédiction": min(90, 30 + level * 6),
                "autonomie": level * 10
            },
            "VPN": {
                "serveurs": min(100, level * 10),
                "vitesse": min(1000, level * 100),
                "no_logs": level > 6,
                "chiffrement": min(256, 64 * level)
            },
            "CRACKING": {
                "succès": min(90, 30 + level * 6),
                "vitesse": level * 15,
                "versatilité": min(10, level),
                "détectabilité": max(5, 50 - level * 5)
            }
        }
        
        return base_features.get(software_type, {"niveau": level * 10})
    
    def _generate_default_requirements(self, software_type: str, level: int, memory_usage: int) -> Dict[str, Any]:
        """
        Génère des prérequis par défaut selon le type de logiciel
        
        Args:
            software_type: Type de logiciel
            level: Niveau de l'item
            memory_usage: Utilisation mémoire de base
            
        Returns:
            Dictionnaire de prérequis
        """
        # Facteur de ressources selon le type
        resource_factors = {
            "OS": 2.0,
            "SECURITY": 1.2,
            "CRYPTOGRAPHY": 1.5,
            "VIRUS": 0.7,
            "ANTIVIRUS": 1.3,
            "FIREWALL": 1.1,
            "EXPLOIT": 0.9,
            "UTILITY": 0.8,
            "DATABASE": 1.6,
            "AI": 2.5,
            "VPN": 1.0,
            "CRACKING": 1.4
        }
        
        # Facteur de base qui augmente avec le niveau
        factor = resource_factors.get(software_type, 1.0) * (1 + (level - 1) * 0.2)
        
        # Calculer les prérequis
        cpu_req = int(max(1, level * factor * 0.5))
        ram_req = int(max(64, memory_usage * factor))
        disk_req = int(max(10, memory_usage * factor * 2))
        
        return {
            "CPU": f"Niveau {cpu_req}+",
            "RAM": f"{ram_req} Mo",
            "Espace disque": f"{disk_req} Mo",
            "OS": f"Niveau {max(1, int(level/2))}+"
        }
    
    def _calculate_price(self, software_type: str, license_type: str, level: int, base_price: int, is_illegal: bool) -> int:
        """
        Calcule le prix en fonction des caractéristiques
        
        Args:
            software_type: Type de logiciel
            license_type: Type de licence
            level: Niveau de l'item
            base_price: Prix de base
            is_illegal: Si le logiciel est illégal
            
        Returns:
            Prix calculé
        """
        # Facteurs de prix selon le type
        type_factors = {
            "OS": 1.5,
            "SECURITY": 1.3,
            "CRYPTOGRAPHY": 1.4,
            "VIRUS": 1.8 if is_illegal else 0.8,
            "ANTIVIRUS": 1.2,
            "FIREWALL": 1.1,
            "EXPLOIT": 1.7 if is_illegal else 0.9,
            "UTILITY": 0.7,
            "DATABASE": 1.4,
            "AI": 2.0,
            "VPN": 1.0,
            "CRACKING": 1.6 if is_illegal else 0.8
        }
        
        # Facteurs de prix selon la licence
        license_factors = {
            "Freeware": 0.1,
            "Shareware": 0.3,
            "Trial": 0.5,
            "Personal": 1.0,
            "Commercial": 2.0,
            "Enterprise": 3.0,
            "Military": 5.0,
            "Black Market": 2.5 if is_illegal else 1.5
        }
        
        # Calcul du prix
        calculated_price = base_price * type_factors.get(software_type, 1.0) * license_factors.get(license_type, 1.0) * (level ** 1.5)
        
        # Ajouter une variation aléatoire de +/- 10%
        variation = random.uniform(0.9, 1.1)
        
        # Si illégal, ajuster le prix
        if is_illegal:
            # Les logiciels illégaux sont plus chers ou moins chers selon leur type
            calculated_price *= 1.5 if software_type in ["VIRUS", "EXPLOIT", "CRACKING"] else 0.7
        
        return max(1, int(calculated_price * variation))
    
    def _determine_illegality(self, software_type: str, license_type: str) -> bool:
        """
        Détermine si un logiciel est illégal en fonction de son type et de sa licence
        
        Args:
            software_type: Type de logiciel
            license_type: Type de licence
            
        Returns:
            True si le logiciel est illégal, False sinon
        """
        # Types considérés comme illégaux par défaut
        illegal_types = ["VIRUS", "EXPLOIT", "CRACKING"]
        
        # Licences qui rendent le logiciel illégal
        illegal_licenses = ["Black Market"]
        
        # Déterminer si illégal
        return (software_type in illegal_types) or (license_type in illegal_licenses)
    
    @staticmethod
    def generate_random(level: int = 1, software_type: Optional[str] = None, license_type: Optional[str] = None) -> 'SoftwareItem':
        """
        Génère un item logiciel aléatoire
        
        Args:
            level: Niveau de l'item (1-10)
            software_type: Type spécifique de logiciel (optionnel)
            license_type: Type de licence spécifique (optionnel)
            
        Returns:
            Instance de SoftwareItem
        """
        # Limiter le niveau
        level = max(1, min(10, level))
        
        # Sélectionner un type aléatoire si non spécifié
        if software_type is None:
            software_type = random.choice(SoftwareItem.SOFTWARE_TYPES)
        
        # Sélectionner une licence en fonction du niveau si non spécifiée
        if license_type is None:
            if level <= 2:
                # Niveau bas: plutôt des licences gratuites ou d'essai
                license_options = ["Freeware", "Shareware", "Trial", "Personal"]
            elif level <= 5:
                # Niveau moyen: licences personnelles ou commerciales
                license_options = ["Shareware", "Trial", "Personal", "Commercial"]
            elif level <= 8:
                # Niveau élevé: licences commerciales ou entreprise
                license_options = ["Personal", "Commercial", "Enterprise"]
            else:
                # Niveau très élevé: licences entreprise ou militaires
                license_options = ["Commercial", "Enterprise", "Military", "Black Market"]
                
            license_type = random.choice(license_options)
        
        # Noms possibles selon le type
        type_names = {
            "OS": ["Système d'exploitation", "OS", "Plateforme", "Environnement"],
            "SECURITY": ["Sécurité", "Protection", "Gardien", "Bouclier"],
            "CRYPTOGRAPHY": ["Crypteur", "Chiffreur", "Encodeur", "Vault"],
            "VIRUS": ["Virus", "Malware", "Infecteur", "Disrupteur"],
            "ANTIVIRUS": ["Antivirus", "Protecteur", "Scanner", "Nettoyeur"],
            "FIREWALL": ["Pare-feu", "Firewall", "Barrière", "Guardian"],
            "EXPLOIT": ["Exploit", "Brèche", "Infiltrateur", "Backdoor"],
            "UTILITY": ["Utilitaire", "Boîte à outils", "SwissKnife", "Assistant"],
            "DATABASE": ["Base de données", "DataVault", "Stockage", "Repository"],
            "AI": ["Intelligence artificielle", "IA", "Assistant cognitif", "Neural Net"],
            "VPN": ["VPN", "Tunneler", "PrivacyShield", "Anonymizer"],
            "CRACKING": ["Cracker", "Déchiffreur", "Forceur", "LockBreaker"]
        }
        
        # Sociétés fictives de développement de logiciels
        companies = ["CodeX", "ByteWorks", "NeuraSoft", "QuantumBits", "SynaptiCore", 
                    "VoidLogic", "CyberMind", "AlphaDev", "OmniSoft", "EtherCorp"]
        
        # Sélectionner un nom de base et une société
        name_base = random.choice(type_names.get(software_type, ["Logiciel"]))
        company = random.choice(companies)
        
        # Générer une version
        major = random.randint(1, 5)
        minor = random.randint(0, 9)
        patch = random.randint(0, 9)
        version = f"{major}.{minor}" if random.random() < 0.5 else f"{major}.{minor}.{patch}"
        
        # Construire le nom complet
        name = f"{company} {name_base} {version}"
        
        # Générer la description
        license_descriptors = {
            "Freeware": "gratuit et libre d'utilisation",
            "Shareware": "partageable mais avec des fonctionnalités limitées",
            "Trial": "en version d'essai limitée dans le temps",
            "Personal": "sous licence personnelle",
            "Commercial": "sous licence commerciale",
            "Enterprise": "destiné aux grandes entreprises",
            "Military": "de grade militaire, hautement sécurisé",
            "Black Market": "disponible uniquement sur le marché noir"
        }
        
        description = f"Un logiciel {license_descriptors.get(license_type, '')} développé par {company}. "
        
        if software_type == "OS":
            description += "Gère les ressources système et fournit une interface utilisateur."
        elif software_type == "SECURITY":
            description += "Protège votre système contre les intrusions et les menaces."
        elif software_type == "CRYPTOGRAPHY":
            description += "Permet de chiffrer et déchiffrer des données sensibles."
        elif software_type == "VIRUS":
            description += "Conçu pour infiltrer et perturber les systèmes cibles."
        elif software_type == "ANTIVIRUS":
            description += "Détecte et élimine les logiciels malveillants."
        elif software_type == "FIREWALL":
            description += "Filtre le trafic réseau pour bloquer les menaces."
        elif software_type == "EXPLOIT":
            description += "Exploite les vulnérabilités des systèmes pour y accéder."
        elif software_type == "UTILITY":
            description += "Un ensemble d'outils pour optimiser et maintenir votre système."
        elif software_type == "DATABASE":
            description += "Stocke et organise vos données de manière structurée."
        elif software_type == "AI":
            description += "Analyse les données et prend des décisions intelligentes."
        elif software_type == "VPN":
            description += "Sécurise vos connexions et masque votre identité en ligne."
        elif software_type == "CRACKING":
            description += "Conçu pour contourner les protections et accéder à des systèmes verrouillés."
        
        # Utilisation mémoire en fonction du type et du niveau
        memory_usage = 50 * level
        if software_type in ["OS", "DATABASE", "AI"]:
            memory_usage *= 2  # Plus gourmand en ressources
        elif software_type in ["VIRUS", "EXPLOIT"]:
            memory_usage //= 2  # Moins gourmand pour être discret
            
        # Déterminer si illégal
        is_illegal = SoftwareItem._determine_illegality(None, software_type, license_type)
        
        # Prix de base qui augmente avec le niveau
        base_price = 100 * level
        
        # Créer et retourner l'objet
        return SoftwareItem(
            name=name,
            description=description,
            software_type=software_type,
            version=version,
            license_type=license_type,
            level=level,
            memory_usage=memory_usage,
            is_illegal=is_illegal,
            price=base_price
        )
