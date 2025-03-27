"""
Système de modifications d'équipement pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.EquipmentMods")

class ModRarity(Enum):
    """Rareté des modifications"""
    COMMON = 0      # Commun
    UNCOMMON = 1    # Peu commun
    RARE = 2        # Rare
    EPIC = 3        # Épique
    LEGENDARY = 4   # Légendaire

class ModType(Enum):
    """Types de modifications"""
    WEAPON = auto()     # Arme
    ARMOR = auto()      # Armure
    SHIELD = auto()     # Bouclier
    ACCESSORY = auto()  # Accessoire
    UNIVERSAL = auto()  # Universel

class WeaponModSlot(Enum):
    """Emplacements de modification d'arme"""
    BARREL = auto()     # Canon
    GRIP = auto()       # Poignée
    SIGHT = auto()      # Viseur
    MAGAZINE = auto()   # Chargeur
    STOCK = auto()      # Crosse
    MUZZLE = auto()     # Bouche
    ACCESSORY = auto()  # Accessoire
    FRAME = auto()      # Cadre
    CORE = auto()       # Cœur
    BLADE = auto()      # Lame

class ArmorModSlot(Enum):
    """Emplacements de modification d'armure"""
    PLATING = auto()    # Blindage
    LINING = auto()     # Doublure
    PADDING = auto()    # Rembourrage
    WEAVE = auto()      # Tissage
    COATING = auto()    # Revêtement
    SYSTEM = auto()     # Système
    ACCESSORY = auto()  # Accessoire

class EquipmentModSystem:
    """
    Système qui gère les modifications d'équipement
    """
    
    def __init__(self):
        """Initialise le système de modifications d'équipement"""
        self.mods_database = {}  # ID -> modification
        self.installed_mods = {}  # (equipment_id, slot) -> mod_id
        self.compatible_slots = {
            ModType.WEAPON: [slot for slot in WeaponModSlot],
            ModType.ARMOR: [slot for slot in ArmorModSlot],
            ModType.SHIELD: [ArmorModSlot.PLATING, ArmorModSlot.COATING, ArmorModSlot.ACCESSORY],
            ModType.ACCESSORY: [WeaponModSlot.ACCESSORY, ArmorModSlot.ACCESSORY],
            ModType.UNIVERSAL: []  # Défini lors de la création de la modification
        }
        self._init_mods_database()
        
        logger.debug("Système de modifications d'équipement initialisé")
    
    def _init_mods_database(self):
        """Initialise la base de données de modifications"""
        # Mods d'arme
        self._add_weapon_mods()
        
        # Mods d'armure
        self._add_armor_mods()
        
        # Mods de bouclier
        self._add_shield_mods()
        
        # Mods d'accessoire
        self._add_accessory_mods()
        
        # Mods universels
        self._add_universal_mods()
        
        logger.debug(f"Base de données de modifications initialisée avec {len(self.mods_database)} entrées")
    
    def _add_weapon_mods(self):
        """Ajoute les modifications d'arme"""
        # Canon
        self.mods_database["extended_barrel"] = {
            "id": "extended_barrel",
            "name": "Canon allongé",
            "description": "Augmente la portée et la précision",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.BARREL,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "range_multiplier": 1.25,  # +25% de portée
                "accuracy_bonus": 0.1      # +10% de précision
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["metal_parts", "precision_tools"]
        }
        
        self.mods_database["thermal_barrel"] = {
            "id": "thermal_barrel",
            "name": "Canon thermique",
            "description": "Ajoute des dégâts thermiques aux attaques",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.BARREL,
            "rarity": ModRarity.RARE,
            "effects": {
                "bonus_damage": 5,                  # +5 dégâts
                "damage_type_add": "THERMAL",       # Ajoute des dégâts thermiques
                "damage_type_split": [0.7, 0.3]     # 70% normaux, 30% thermiques
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "ENERGY_WEAPON"]
            },
            "installation_difficulty": 5,
            "crafting_materials": ["metal_parts", "thermal_cell", "coolant"]
        }
        
        # Poignée
        self.mods_database["ergonomic_grip"] = {
            "id": "ergonomic_grip",
            "name": "Poignée ergonomique",
            "description": "Améliore la prise en main et la précision",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.GRIP,
            "rarity": ModRarity.COMMON,
            "effects": {
                "accuracy_bonus": 0.05,    # +5% de précision
                "recoil_reduction": 0.1    # -10% de recul
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 1,
            "crafting_materials": ["polymer", "grip_tape"]
        }
        
        self.mods_database["stabilized_grip"] = {
            "id": "stabilized_grip",
            "name": "Poignée stabilisée",
            "description": "Réduit considérablement le recul",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.GRIP,
            "rarity": ModRarity.RARE,
            "effects": {
                "recoil_reduction": 0.3,   # -30% de recul
                "aim_time_reduction": 0.2  # -20% de temps de visée
            },
            "requirements": {
                "weapon_types": ["RIFLE", "SMG", "HEAVY_WEAPON"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["polymer", "carbon_fiber", "dampening_gel"]
        }
        
        # Viseur
        self.mods_database["reflex_sight"] = {
            "id": "reflex_sight",
            "name": "Viseur réflexe",
            "description": "Améliore la précision à courte et moyenne portée",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.SIGHT,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "accuracy_bonus": 0.15,         # +15% de précision
                "aim_time_reduction": 0.15      # -15% de temps de visée
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["lens", "electronic_parts"]
        }
        
        self.mods_database["thermal_scope"] = {
            "id": "thermal_scope",
            "name": "Lunette thermique",
            "description": "Permet de voir les ennemis à travers certains obstacles",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.SIGHT,
            "rarity": ModRarity.EPIC,
            "effects": {
                "accuracy_bonus": 0.2,             # +20% de précision
                "can_see_through": ["SMOKE", "THIN_WALLS"],
                "night_vision": True,
                "critical_chance_bonus": 0.1       # +10% de chance critique
            },
            "requirements": {
                "weapon_types": ["RIFLE", "SNIPER", "HEAVY_WEAPON"],
                "tech_level": 3
            },
            "installation_difficulty": 6,
            "crafting_materials": ["advanced_lens", "thermal_sensor", "microprocessor", "power_cell"]
        }
        
        # Chargeur
        self.mods_database["extended_magazine"] = {
            "id": "extended_magazine",
            "name": "Chargeur étendu",
            "description": "Augmente la capacité de munitions",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.MAGAZINE,
            "rarity": ModRarity.COMMON,
            "effects": {
                "ammo_capacity_multiplier": 1.5  # +50% de capacité
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 1,
            "crafting_materials": ["metal_parts", "spring"]
        }
        
        self.mods_database["quick_reload_mag"] = {
            "id": "quick_reload_mag",
            "name": "Chargeur à rechargement rapide",
            "description": "Réduit considérablement le temps de rechargement",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.MAGAZINE,
            "rarity": ModRarity.RARE,
            "effects": {
                "reload_time_multiplier": 0.6  # -40% de temps de rechargement
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["metal_parts", "spring", "lightweight_alloy"]
        }
        
        # Bouche
        self.mods_database["silencer"] = {
            "id": "silencer",
            "name": "Silencieux",
            "description": "Réduit considérablement le bruit des tirs",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.MUZZLE,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "noise_reduction": 0.85,     # -85% de bruit
                "stealth_attack_bonus": 0.25  # +25% de dégâts en attaque furtive
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["metal_parts", "sound_dampening_material"]
        }
        
        self.mods_database["compensator"] = {
            "id": "compensator",
            "name": "Compensateur",
            "description": "Réduit le recul et améliore la stabilité",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.MUZZLE,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "recoil_reduction": 0.25,     # -25% de recul
                "stability_bonus": 0.2        # +20% de stabilité
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "HEAVY_WEAPON"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["metal_parts", "precision_tools"]
        }
        
        # Crosse
        self.mods_database["tactical_stock"] = {
            "id": "tactical_stock",
            "name": "Crosse tactique",
            "description": "Améliore la stabilité et la précision",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.STOCK,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "stability_bonus": 0.15,      # +15% de stabilité
                "accuracy_bonus": 0.1         # +10% de précision
            },
            "requirements": {
                "weapon_types": ["RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["polymer", "metal_parts", "padding"]
        }
        
        self.mods_database["folding_stock"] = {
            "id": "folding_stock",
            "name": "Crosse pliable",
            "description": "Permet de ranger l'arme plus facilement et de la déployer rapidement",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.STOCK,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "draw_time_multiplier": 0.75,  # -25% de temps de dégainage
                "concealment_bonus": 0.2       # +20% de dissimulation
            },
            "requirements": {
                "weapon_types": ["RIFLE", "SMG", "SHOTGUN"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["metal_parts", "hinge", "polymer"]
        }
        
        # Cadre
        self.mods_database["lightweight_frame"] = {
            "id": "lightweight_frame",
            "name": "Cadre léger",
            "description": "Réduit le poids de l'arme pour une maniabilité accrue",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.FRAME,
            "rarity": ModRarity.RARE,
            "effects": {
                "weight_multiplier": 0.7,      # -30% de poids
                "aim_time_reduction": 0.15,    # -15% de temps de visée
                "movement_penalty_reduction": 0.25  # -25% de pénalité de mouvement
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN", "HEAVY_WEAPON"]
            },
            "installation_difficulty": 5,
            "crafting_materials": ["lightweight_alloy", "carbon_fiber", "precision_tools"]
        }
        
        self.mods_database["reinforced_frame"] = {
            "id": "reinforced_frame",
            "name": "Cadre renforcé",
            "description": "Augmente la durabilité de l'arme",
            "type": ModType.WEAPON,
            "slot": WeaponModSlot.FRAME,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "durability_multiplier": 2.0,   # +100% de durabilité
                "jam_chance_reduction": 0.5     # -50% de chance d'enrayement
            },
            "requirements": {
                "weapon_types": ["PISTOL", "RIFLE", "SMG", "SHOTGUN", "HEAVY_WEAPON"]
            },
            "installation_difficulty": 4,
            "crafting_materials": ["reinforced_metal", "industrial_adhesive", "precision_tools"]
        }
