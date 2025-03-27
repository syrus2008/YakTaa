"""
Module pour la gestion des items hardware dans YakTaa.
Définit les différents types de matériel informatique que le joueur peut acquérir.
"""

import logging
import random
from typing import Dict, List, Optional, Any

from .item import Item

logger = logging.getLogger("YakTaa.Items.HardwareItem")

class HardwareItem(Item):
    """
    Classe représentant un élément matériel (hardware) dans le jeu
    """
    
    HARDWARE_TYPES = [
        "CPU", "GPU", "RAM", "SSD", "HDD", "MOBO", "PSU", "COOLING", 
        "CASE", "NETWORK", "PERIPHERAL", "IMPLANT"
    ]
    
    QUALITY_LEVELS = ["Standard", "Amélioré", "Avancé", "Prototype", "Militaire", "Alien"]
    
    def __init__(self, 
                 id: str = None,
                 name: str = "Hardware inconnu", 
                 description: str = "Un composant matériel mystérieux.",
                 hardware_type: str = "CPU",
                 quality: str = "Standard",
                 level: int = 1,
                 stats: Dict[str, Any] = None,
                 price: int = 100,
                 icon: str = "hardware",
                 properties: Dict[str, Any] = None):
        """
        Initialise un item hardware
        
        Args:
            id: Identifiant unique de l'item
            name: Nom de l'item
            description: Description de l'item
            hardware_type: Type de matériel (CPU, GPU, etc.)
            quality: Niveau de qualité du matériel
            level: Niveau/tier de l'item (1-10)
            stats: Statistiques spécifiques au type de matériel
            price: Prix de base en crédits
            icon: Icône représentant l'item
            properties: Propriétés supplémentaires
        """
        # Normaliser le type de hardware
        if hardware_type.upper() in [t.upper() for t in self.HARDWARE_TYPES]:
            for t in self.HARDWARE_TYPES:
                if hardware_type.upper() == t.upper():
                    hardware_type = t
                    break
        else:
            hardware_type = "CPU"  # Type par défaut
            
        # Normaliser la qualité
        if quality not in self.QUALITY_LEVELS:
            quality = "Standard"  # Qualité par défaut
            
        # Initialiser les statistiques par défaut selon le type
        if stats is None:
            stats = self._generate_default_stats(hardware_type, quality, level)
        
        # Calculer le prix en fonction de la qualité et du niveau
        price = self._calculate_price(hardware_type, quality, level, price)
        
        # Initialiser la classe parente
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="hardware",
            quantity=1,  # Les items hardware sont généralement uniques
            value=price,
            icon=f"hardware_{hardware_type.lower()}",
            properties=properties or {}
        )
        
        # Attributs spécifiques au hardware
        self.hardware_type = hardware_type
        self.quality = quality
        self.level = level
        self.stats = stats
        self.price = price
        
        logger.debug(f"Nouvel item hardware créé : {name} (Type: {hardware_type}, Qualité: {quality}, Niveau: {level})")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Retourne les informations à afficher dans l'interface"""
        base_info = super().get_display_info()
        
        # Ajouter les informations spécifiques au hardware
        hardware_info = {
            "type": f"Hardware - {self.hardware_type}",
            "quality": self.quality,
            "level": f"Niveau {self.level}",
            "stats": self.stats
        }
        
        return {**base_info, **hardware_info}
    
    def _generate_default_stats(self, hardware_type: str, quality: str, level: int) -> Dict[str, Any]:
        """
        Génère des statistiques par défaut selon le type de hardware
        
        Args:
            hardware_type: Type de matériel
            quality: Qualité du matériel
            level: Niveau de l'item
            
        Returns:
            Dictionnaire de statistiques
        """
        # Facteur de qualité
        quality_factor = self.QUALITY_LEVELS.index(quality) + 1
        
        # Statistiques de base
        base_stats = {
            "CPU": {
                "fréquence": f"{(1.5 + level * 0.5 + quality_factor * 0.3):.1f} GHz",
                "cores": min(32, 2 + level + quality_factor),
                "puissance_calcul": level * quality_factor * 10,
                "consommation": min(100, 10 + level * 5 - quality_factor)
            },
            "GPU": {
                "VRAM": f"{min(32, 1 + level + quality_factor)} GB",
                "performance": level * quality_factor * 15,
                "passthrough": quality_factor > 3,
                "consommation": min(250, 20 + level * 10 - quality_factor * 2)
            },
            "RAM": {
                "capacité": f"{min(128, 4 * (level + quality_factor))} GB",
                "fréquence": f"{(1600 + level * 200 + quality_factor * 300)} MHz",
                "latence": max(1, 10 - level * 0.5 - quality_factor * 0.5)
            },
            "SSD": {
                "capacité": f"{min(4096, 128 * (level + quality_factor))} GB",
                "vitesse_lecture": f"{(500 + level * 200 + quality_factor * 300)} MB/s",
                "vitesse_écriture": f"{(400 + level * 150 + quality_factor * 250)} MB/s"
            },
            "HDD": {
                "capacité": f"{min(16384, 512 * (level + quality_factor))} GB",
                "vitesse_lecture": f"{(100 + level * 20 + quality_factor * 30)} MB/s",
                "vitesse_écriture": f"{(80 + level * 15 + quality_factor * 25)} MB/s"
            },
            "MOBO": {
                "slots_RAM": min(8, 2 + level//2 + quality_factor//2),
                "slots_extension": min(6, 1 + level//2 + quality_factor//2),
                "sécurité": level * quality_factor,
                "stabilité": min(100, 50 + level * 3 + quality_factor * 5)
            },
            "PSU": {
                "puissance": f"{min(1200, 300 + level * 50 + quality_factor * 75)} W",
                "efficacité": f"{min(95, 70 + level * 1 + quality_factor * 3)}%",
                "stabilité": min(100, 60 + level * 2 + quality_factor * 4)
            },
            "COOLING": {
                "puissance": min(100, 30 + level * 5 + quality_factor * 7),
                "bruit": max(0, 30 - level * 2 - quality_factor * 3),
                "efficacité": min(100, 60 + level * 2 + quality_factor * 4)
            },
            "CASE": {
                "slots": min(10, 3 + level//2 + quality_factor//2),
                "ventilation": min(100, 50 + level * 3 + quality_factor * 5),
                "sécurité": level * quality_factor,
                "esthétique": min(100, 50 + quality_factor * 8)
            },
            "NETWORK": {
                "vitesse": f"{min(10, level//2 + quality_factor//2)} Gbps",
                "portée": f"{min(100, 10 + level * 5 + quality_factor * 8)} m",
                "sécurité": level * quality_factor,
                "furtivité": min(100, quality_factor * 15)
            },
            "PERIPHERAL": {
                "précision": min(100, 60 + level * 2 + quality_factor * 4),
                "confort": min(100, 50 + level * 3 + quality_factor * 5),
                "avantage": level * quality_factor
            },
            "IMPLANT": {
                "compatibilité": min(100, 70 + level + quality_factor * 3),
                "risque_rejet": max(1, 20 - level - quality_factor * 2),
                "puissance": level * quality_factor,
                "discrétion": min(100, 60 + quality_factor * 6)
            }
        }
        
        return base_stats.get(hardware_type, {"qualité": quality_factor * 10})
    
    def _calculate_price(self, hardware_type: str, quality: str, level: int, base_price: int) -> int:
        """
        Calcule le prix en fonction des caractéristiques
        
        Args:
            hardware_type: Type de matériel
            quality: Qualité du matériel
            level: Niveau de l'item
            base_price: Prix de base
            
        Returns:
            Prix calculé
        """
        # Facteurs de prix selon le type
        type_factors = {
            "CPU": 1.2,
            "GPU": 1.4,
            "RAM": 0.8,
            "SSD": 0.9,
            "HDD": 0.6,
            "MOBO": 1.1,
            "PSU": 0.7,
            "COOLING": 0.5,
            "CASE": 0.4,
            "NETWORK": 0.8,
            "PERIPHERAL": 0.6,
            "IMPLANT": 1.5
        }
        
        # Facteur de qualité
        quality_factor = self.QUALITY_LEVELS.index(quality) + 1
        
        # Calcul du prix
        calculated_price = base_price * type_factors.get(hardware_type, 1.0) * (level ** 1.5) * (quality_factor ** 1.8)
        
        # Ajouter une variation aléatoire de +/- 10%
        variation = random.uniform(0.9, 1.1)
        
        return max(1, int(calculated_price * variation))
    
    @staticmethod
    def generate_random(level: int = 1, hardware_type: Optional[str] = None, quality: Optional[str] = None) -> 'HardwareItem':
        """
        Génère un item hardware aléatoire
        
        Args:
            level: Niveau de l'item (1-10)
            hardware_type: Type spécifique de hardware (optionnel)
            quality: Qualité spécifique (optionnel)
            
        Returns:
            Instance de HardwareItem
        """
        # Limiter le niveau
        level = max(1, min(10, level))
        
        # Sélectionner un type aléatoire si non spécifié
        if hardware_type is None:
            hardware_type = random.choice(HardwareItem.HARDWARE_TYPES)
        
        # Sélectionner une qualité en fonction du niveau si non spécifiée
        if quality is None:
            # Plus le niveau est élevé, plus la chance d'avoir une qualité élevée est grande
            max_quality_index = min(len(HardwareItem.QUALITY_LEVELS) - 1, 
                                   (level - 1) // 2)  # Niveau 1-2: Standard, 3-4: Amélioré, etc.
            quality_weights = [max(1, 10 - i*2) for i in range(max_quality_index + 1)]
            quality = random.choices(
                HardwareItem.QUALITY_LEVELS[:max_quality_index + 1],
                weights=quality_weights
            )[0]
        
        # Noms possibles selon le type
        type_names = {
            "CPU": ["Processeur", "CPU", "Unité de calcul", "Puce de traitement"],
            "GPU": ["Carte graphique", "GPU", "Accélérateur graphique", "Processeur visuel"],
            "RAM": ["Mémoire vive", "RAM", "Barrette mémoire", "Module DIMM"],
            "SSD": ["Disque SSD", "Stockage rapide", "Mémoire flash", "Disque solide"],
            "HDD": ["Disque dur", "HDD", "Stockage magnétique", "Disque mécanique"],
            "MOBO": ["Carte mère", "Plaque système", "Mainboard", "Circuit principal"],
            "PSU": ["Alimentation", "Bloc d'alimentation", "Convertisseur", "Module électrique"],
            "COOLING": ["Système de refroidissement", "Radiateur", "Ventilateur avancé", "Dissipateur"],
            "CASE": ["Boîtier", "Châssis", "Tour", "Coque renforcée"],
            "NETWORK": ["Interface réseau", "Adaptateur WiFi", "Module de connexion", "Antenne"],
            "PERIPHERAL": ["Périphérique", "Interface", "Contrôleur", "Accessoire"],
            "IMPLANT": ["Implant", "Augmentation", "Prothèse", "Bio-connecteur"]
        }
        
        # Marques fictives
        brands = ["NeuraTech", "QuantumByte", "SynapseCore", "VoidSystems", "ByteForge", 
                 "NexGen", "CyberDyne", "AlphaWare", "OmniTech", "RadianTech"]
        
        # Sélectionner un nom de base et une marque
        name_base = random.choice(type_names.get(hardware_type, ["Composant"]))
        brand = random.choice(brands)
        
        # Générer un identifiant de modèle
        model_id = f"{random.choice('ABCDEFGHX')}-{random.randint(100, 999)}"
        
        # Construire le nom complet
        name = f"{brand} {name_base} {model_id}"
        
        # Générer la description
        quality_descriptors = {
            "Standard": "de qualité standard",
            "Amélioré": "de qualité supérieure",
            "Avancé": "à la pointe de la technologie",
            "Prototype": "en phase expérimentale avancée",
            "Militaire": "de grade militaire",
            "Alien": "d'origine inconnue, aux capacités extraordinaires"
        }
        
        description = f"Un {name_base.lower()} {quality_descriptors.get(quality, '')} fabriqué par {brand}. "
        
        if hardware_type == "CPU":
            description += "Optimisé pour les calculs intensifs et le multitâche."
        elif hardware_type == "GPU":
            description += "Conçu pour le rendu graphique et les calculs parallèles."
        elif hardware_type == "RAM":
            description += "Offre une mémoire vive rapide pour les applications exigeantes."
        elif hardware_type == "SSD":
            description += "Stockage ultra-rapide avec temps d'accès minimal."
        elif hardware_type == "HDD":
            description += "Grande capacité de stockage à un prix abordable."
        elif hardware_type == "MOBO":
            description += "Le cœur de votre système, compatible avec les derniers composants."
        elif hardware_type == "PSU":
            description += "Fournit une alimentation stable et fiable à votre équipement."
        elif hardware_type == "COOLING":
            description += "Maintient votre système à température optimale même sous charge intense."
        elif hardware_type == "CASE":
            description += "Protège vos composants tout en optimisant la circulation d'air."
        elif hardware_type == "NETWORK":
            description += "Assure des connexions réseau rapides et sécurisées."
        elif hardware_type == "PERIPHERAL":
            description += "Améliore votre interface avec les systèmes numériques."
        elif hardware_type == "IMPLANT":
            description += "Augmentation cybernétique offrant des capacités supérieures."
        
        # Prix de base qui augmente avec le niveau
        base_price = 100 * level
        
        # Créer et retourner l'objet
        return HardwareItem(
            name=name,
            description=description,
            hardware_type=hardware_type,
            quality=quality,
            level=level,
            price=base_price
        )
