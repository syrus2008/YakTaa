"""
Module de définition des schémas de métadonnées standardisés pour tous les types d'objets.
Ce module assure la cohérence entre l'éditeur de monde et le jeu principal.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class MetadataSchema:
    """Classe de base pour tous les schémas de métadonnées"""
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide un dictionnaire de métadonnées selon le schéma défini
        
        Args:
            metadata: Dictionnaire de métadonnées à valider
            
        Returns:
            Tuple contenant (est_valide, liste_erreurs)
        """
        return True, []
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        """
        Retourne un dictionnaire de métadonnées par défaut conforme au schéma
        
        Returns:
            Dictionnaire de métadonnées par défaut
        """
        return {}
    
    @staticmethod
    def parse_json(metadata_str: Optional[str]) -> Dict[str, Any]:
        """
        Parse une chaîne JSON en dictionnaire de métadonnées
        
        Args:
            metadata_str: Chaîne JSON à parser
            
        Returns:
            Dictionnaire de métadonnées, ou dictionnaire vide en cas d'erreur
        """
        if not metadata_str:
            return {}
            
        try:
            if isinstance(metadata_str, dict):
                return metadata_str
            return json.loads(metadata_str)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}")
            return {}
    
    @staticmethod
    def to_json(metadata: Dict[str, Any]) -> str:
        """
        Convertit un dictionnaire de métadonnées en chaîne JSON
        
        Args:
            metadata: Dictionnaire de métadonnées à convertir
            
        Returns:
            Chaîne JSON
        """
        try:
            return json.dumps(metadata, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur de conversion en JSON: {e}")
            return "{}"


class WeaponMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les armes"""
    
    REQUIRED_FIELDS = ["damage_type", "damage", "accuracy", "range"]
    OPTIONAL_FIELDS = ["critical_chance", "critical_multiplier", "ammo_type", 
                       "fire_modes", "attachments", "durability", "condition"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "damage" in metadata and not isinstance(metadata["damage"], (int, float)):
            errors.append("Le champ 'damage' doit être un nombre")
            
        if "accuracy" in metadata and not isinstance(metadata["accuracy"], (int, float)):
            errors.append("Le champ 'accuracy' doit être un nombre")
            
        if "range" in metadata and not isinstance(metadata["range"], (int, float)):
            errors.append("Le champ 'range' doit être un nombre")
            
        if "damage_type" in metadata and not isinstance(metadata["damage_type"], str):
            errors.append("Le champ 'damage_type' doit être une chaîne de caractères")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "damage_type": "PHYSICAL",
            "damage": 10,
            "accuracy": 70,
            "range": 10,
            "critical_chance": 5,
            "critical_multiplier": 1.5
        }


class ArmorMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les armures"""
    
    REQUIRED_FIELDS = ["defense_type", "defense", "durability"]
    OPTIONAL_FIELDS = ["resistance", "mobility_penalty", "slots", "condition"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "defense" in metadata and not isinstance(metadata["defense"], (int, float)):
            errors.append("Le champ 'defense' doit être un nombre")
            
        if "durability" in metadata and not isinstance(metadata["durability"], (int, float)):
            errors.append("Le champ 'durability' doit être un nombre")
            
        if "defense_type" in metadata and not isinstance(metadata["defense_type"], str):
            errors.append("Le champ 'defense_type' doit être une chaîne de caractères")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "defense_type": "PHYSICAL",
            "defense": 5,
            "durability": 100,
            "resistance": {
                "PHYSICAL": 0,
                "ENERGY": 0,
                "THERMAL": 0,
                "CHEMICAL": 0,
                "EMP": 0
            },
            "mobility_penalty": 0
        }


class ImplantMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les implants"""
    
    REQUIRED_FIELDS = ["stats_bonus", "humanity_cost", "surgery_difficulty"]
    OPTIONAL_FIELDS = ["side_effects", "compatibility", "special_abilities", "power_consumption"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "stats_bonus" in metadata and not isinstance(metadata["stats_bonus"], dict):
            errors.append("Le champ 'stats_bonus' doit être un dictionnaire")
            
        if "humanity_cost" in metadata and not isinstance(metadata["humanity_cost"], (int, float)):
            errors.append("Le champ 'humanity_cost' doit être un nombre")
            
        if "surgery_difficulty" in metadata and not isinstance(metadata["surgery_difficulty"], (int, float)):
            errors.append("Le champ 'surgery_difficulty' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "stats_bonus": {
                "STRENGTH": 0,
                "AGILITY": 0,
                "INTELLIGENCE": 0,
                "PERCEPTION": 0,
                "CHARISMA": 0
            },
            "humanity_cost": 5,
            "surgery_difficulty": 3,
            "side_effects": [],
            "compatibility": ["ALL"],
            "special_abilities": []
        }


class ConsumableMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les consommables"""
    
    REQUIRED_FIELDS = ["effects", "duration"]
    OPTIONAL_FIELDS = ["addiction_chance", "side_effects", "taste", "quality", "nutrition_value"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "effects" in metadata and not isinstance(metadata["effects"], list):
            errors.append("Le champ 'effects' doit être une liste")
            
        if "duration" in metadata and not isinstance(metadata["duration"], (int, float)):
            errors.append("Le champ 'duration' doit être un nombre")
            
        if "addiction_chance" in metadata and not isinstance(metadata["addiction_chance"], (int, float)):
            errors.append("Le champ 'addiction_chance' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "effects": [
                {"stat": "HEALTH", "value": 10, "type": "INSTANT"}
            ],
            "duration": 0,
            "addiction_chance": 0,
            "side_effects": [],
            "taste": "Neutre",
            "quality": 1
        }


class FoodMetadataSchema(ConsumableMetadataSchema):
    """Schéma de métadonnées spécifique pour la nourriture"""
    
    REQUIRED_FIELDS = ConsumableMetadataSchema.REQUIRED_FIELDS + ["nutrition_value"]
    OPTIONAL_FIELDS = ["calories", "ingredients", "cuisine_type", "freshness", "expiration_date"]
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        default = super().get_default()
        default.update({
            "nutrition_value": 5,
            "calories": 200,
            "ingredients": [],
            "cuisine_type": "Standard",
            "freshness": 100
        })
        return default


class HardwareMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour le matériel informatique"""
    
    REQUIRED_FIELDS = ["stats", "power_consumption"]
    OPTIONAL_FIELDS = ["compatibility", "heat_generation", "noise_level", "reliability"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "stats" in metadata and not isinstance(metadata["stats"], dict):
            errors.append("Le champ 'stats' doit être un dictionnaire")
            
        if "power_consumption" in metadata and not isinstance(metadata["power_consumption"], (int, float)):
            errors.append("Le champ 'power_consumption' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "stats": {
                "processing_power": 10,
                "memory": 8,
                "storage": 256
            },
            "power_consumption": 5,
            "compatibility": ["STANDARD"],
            "heat_generation": 2,
            "reliability": 90
        }


class SoftwareMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les logiciels"""
    
    REQUIRED_FIELDS = ["features", "system_requirements"]
    OPTIONAL_FIELDS = ["compatibility", "install_size", "encryption_level", "license_type"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "features" in metadata and not isinstance(metadata["features"], list):
            errors.append("Le champ 'features' doit être une liste")
            
        if "system_requirements" in metadata and not isinstance(metadata["system_requirements"], dict):
            errors.append("Le champ 'system_requirements' doit être un dictionnaire")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "features": ["Basic functionality"],
            "system_requirements": {
                "min_processing_power": 5,
                "min_memory": 4,
                "min_storage": 50
            },
            "compatibility": ["STANDARD"],
            "install_size": 100,
            "encryption_level": 1
        }


class DeviceMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les appareils électroniques"""
    
    REQUIRED_FIELDS = ["specs", "security_level", "connected_networks"]
    OPTIONAL_FIELDS = ["installed_software", "vulnerabilities", "access_level", "encryption"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "specs" in metadata and not isinstance(metadata["specs"], dict):
            errors.append("Le champ 'specs' doit être un dictionnaire")
            
        if "security_level" in metadata and not isinstance(metadata["security_level"], (int, float)):
            errors.append("Le champ 'security_level' doit être un nombre")
            
        if "connected_networks" in metadata and not isinstance(metadata["connected_networks"], list):
            errors.append("Le champ 'connected_networks' doit être une liste")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "specs": {
                "processing_power": 10,
                "memory": 8,
                "storage": 256
            },
            "security_level": 3,
            "connected_networks": [],
            "installed_software": [],
            "vulnerabilities": [],
            "access_level": "PUBLIC"
        }


class NetworkMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les réseaux informatiques"""
    
    REQUIRED_FIELDS = ["security_type", "encryption", "connected_devices"]
    OPTIONAL_FIELDS = ["bandwidth", "latency", "firewall_level", "monitored", "access_points"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "security_type" in metadata and not isinstance(metadata["security_type"], str):
            errors.append("Le champ 'security_type' doit être une chaîne de caractères")
            
        if "encryption" in metadata and not isinstance(metadata["encryption"], str):
            errors.append("Le champ 'encryption' doit être une chaîne de caractères")
            
        if "connected_devices" in metadata and not isinstance(metadata["connected_devices"], list):
            errors.append("Le champ 'connected_devices' doit être une liste")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "security_type": "WPA2",
            "encryption": "AES",
            "connected_devices": [],
            "bandwidth": 100,
            "latency": 10,
            "firewall_level": 2,
            "monitored": False,
            "access_points": 1
        }


class CharacterMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les personnages"""
    
    REQUIRED_FIELDS = ["stats", "skills", "inventory"]
    OPTIONAL_FIELDS = ["dialog_options", "daily_routine", "relationships", "faction_standing"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "stats" in metadata and not isinstance(metadata["stats"], dict):
            errors.append("Le champ 'stats' doit être un dictionnaire")
            
        if "skills" in metadata and not isinstance(metadata["skills"], dict):
            errors.append("Le champ 'skills' doit être un dictionnaire")
            
        if "inventory" in metadata and not isinstance(metadata["inventory"], list):
            errors.append("Le champ 'inventory' doit être une liste")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "stats": {
                "STRENGTH": 5,
                "AGILITY": 5,
                "INTELLIGENCE": 5,
                "PERCEPTION": 5,
                "CHARISMA": 5
            },
            "skills": {
                "HACKING": 1,
                "COMBAT": 1,
                "STEALTH": 1,
                "PERSUASION": 1,
                "TECH": 1
            },
            "inventory": [],
            "dialog_options": [],
            "daily_routine": [],
            "relationships": {},
            "faction_standing": {}
        }


class ShopMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les magasins"""
    
    REQUIRED_FIELDS = ["shop_type", "restock_time", "price_modifier"]
    OPTIONAL_FIELDS = ["special_items", "reputation_requirement", "opening_hours", "services"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "shop_type" in metadata and not isinstance(metadata["shop_type"], str):
            errors.append("Le champ 'shop_type' doit être une chaîne de caractères")
            
        if "restock_time" in metadata and not isinstance(metadata["restock_time"], (int, float)):
            errors.append("Le champ 'restock_time' doit être un nombre")
            
        if "price_modifier" in metadata and not isinstance(metadata["price_modifier"], (int, float)):
            errors.append("Le champ 'price_modifier' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "shop_type": "GENERAL",
            "restock_time": 24,
            "price_modifier": 1.0,
            "special_items": [],
            "reputation_requirement": 0,
            "opening_hours": {"start": 8, "end": 20},
            "services": []
        }


class MissionMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les missions"""
    
    REQUIRED_FIELDS = ["objectives", "rewards", "difficulty"]
    OPTIONAL_FIELDS = ["time_limit", "consequences", "prerequisites", "failure_conditions", "story_impact"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "objectives" in metadata and not isinstance(metadata["objectives"], list):
            errors.append("Le champ 'objectives' doit être une liste")
            
        if "rewards" in metadata and not isinstance(metadata["rewards"], dict):
            errors.append("Le champ 'rewards' doit être un dictionnaire")
            
        if "difficulty" in metadata and not isinstance(metadata["difficulty"], (int, float)):
            errors.append("Le champ 'difficulty' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "objectives": [
                {"type": "TALK", "target": "", "description": "Parler à quelqu'un"}
            ],
            "rewards": {
                "xp": 100,
                "money": 500,
                "items": [],
                "reputation": {}
            },
            "difficulty": 1,
            "time_limit": 0,  # 0 = pas de limite
            "consequences": {
                "success": [],
                "failure": []
            },
            "prerequisites": {
                "level": 1,
                "missions": [],
                "reputation": {}
            }
        }


class LocationMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les lieux"""
    
    REQUIRED_FIELDS = ["environment_type", "population_density", "security_level"]
    OPTIONAL_FIELDS = ["weather", "ambient_sounds", "points_of_interest", "hazards", "accessibility"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "environment_type" in metadata and not isinstance(metadata["environment_type"], str):
            errors.append("Le champ 'environment_type' doit être une chaîne de caractères")
            
        if "population_density" in metadata and not isinstance(metadata["population_density"], (int, float)):
            errors.append("Le champ 'population_density' doit être un nombre")
            
        if "security_level" in metadata and not isinstance(metadata["security_level"], (int, float)):
            errors.append("Le champ 'security_level' doit être un nombre")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "environment_type": "URBAN",
            "population_density": 5,
            "security_level": 3,
            "weather": "NORMAL",
            "ambient_sounds": ["city_background"],
            "points_of_interest": [],
            "hazards": [],
            "accessibility": "ALL"
        }


class BuildingMetadataSchema(MetadataSchema):
    """Schéma de métadonnées pour les bâtiments"""
    
    REQUIRED_FIELDS = ["building_type", "security_level", "floors"]
    OPTIONAL_FIELDS = ["access_points", "security_systems", "interior_layout", "owner", "condition"]
    
    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        if "building_type" in metadata and not isinstance(metadata["building_type"], str):
            errors.append("Le champ 'building_type' doit être une chaîne de caractères")
            
        if "security_level" in metadata and not isinstance(metadata["security_level"], (int, float)):
            errors.append("Le champ 'security_level' doit être un nombre")
            
        if "floors" in metadata and not isinstance(metadata["floors"], int):
            errors.append("Le champ 'floors' doit être un entier")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_default(cls) -> Dict[str, Any]:
        return {
            "building_type": "RESIDENTIAL",
            "security_level": 2,
            "floors": 1,
            "access_points": ["MAIN_ENTRANCE"],
            "security_systems": [],
            "interior_layout": {},
            "owner": "",
            "condition": 100
        }


# Dictionnaire associant les types d'objets à leurs schémas de métadonnées
METADATA_SCHEMAS = {
    "weapon": WeaponMetadataSchema,
    "armor": ArmorMetadataSchema,
    "implant": ImplantMetadataSchema,
    "consumable": ConsumableMetadataSchema,
    "food": FoodMetadataSchema,
    "hardware": HardwareMetadataSchema,
    "software": SoftwareMetadataSchema,
    "device": DeviceMetadataSchema,
    "network": NetworkMetadataSchema,
    "character": CharacterMetadataSchema,
    "shop": ShopMetadataSchema,
    "mission": MissionMetadataSchema,
    "location": LocationMetadataSchema,
    "building": BuildingMetadataSchema
}


def get_schema_for_item_type(item_type: str) -> MetadataSchema:
    """
    Récupère le schéma de métadonnées approprié pour un type d'objet
    
    Args:
        item_type: Type d'objet (weapon, armor, implant, etc.)
        
    Returns:
        Classe de schéma de métadonnées appropriée
    """
    item_type = item_type.lower()
    
    # Gérer les sous-types spécifiques
    if item_type in ["pistol", "rifle", "melee", "shotgun", "smg", "sniper"]:
        return METADATA_SCHEMAS["weapon"]
    elif item_type in ["helmet", "chest", "legs", "boots", "gloves"]:
        return METADATA_SCHEMAS["armor"]
    elif item_type in ["neural", "optical", "skeletal", "dermal", "circulatory"]:
        return METADATA_SCHEMAS["implant"]
    elif item_type in ["stimulant", "medicine", "drug"]:
        return METADATA_SCHEMAS["consumable"]
    elif item_type in ["food", "drink"]:
        return METADATA_SCHEMAS["food"]
    elif item_type in ["cpu", "ram", "ssd", "tool", "peripheral"]:
        return METADATA_SCHEMAS["hardware"]
    elif item_type in ["os", "firewall", "antivirus", "utility", "hacking_tool"]:
        return METADATA_SCHEMAS["software"]
    
    # Essayer de trouver une correspondance directe
    for schema_type, schema_class in METADATA_SCHEMAS.items():
        if item_type.startswith(schema_type):
            return schema_class
    
    # Schéma par défaut
    return MetadataSchema
