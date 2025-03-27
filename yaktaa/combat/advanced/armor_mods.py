"""
Modifications d'armure pour YakTaa
"""

import logging
from typing import Dict, List, Any
from enum import Enum

from .equipment_mods import EquipmentModSystem, ModType, ModRarity, ArmorModSlot

logger = logging.getLogger("YakTaa.Combat.Advanced.ArmorMods")

class ArmorModsInitializer:
    """
    Classe pour initialiser la base de données des modifications d'armure
    """
    
    @staticmethod
    def initialize_armor_mods(mod_system: EquipmentModSystem) -> None:
        """
        Initialise les modifications d'armure dans la base de données
        
        Args:
            mod_system: Le système de modifications d'équipement
        """
        # Blindage
        mod_system.mods_database["reinforced_plating"] = {
            "id": "reinforced_plating",
            "name": "Blindage renforcé",
            "description": "Augmente considérablement la protection contre les dégâts physiques",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PLATING,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "physical_resist_bonus": 0.15,  # +15% de résistance aux dégâts physiques
                "weight_multiplier": 1.2        # +20% de poids
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "SHIELD"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["reinforced_metal", "industrial_adhesive"]
        }
        
        mod_system.mods_database["lightweight_composite"] = {
            "id": "lightweight_composite",
            "name": "Composite léger",
            "description": "Offre une protection décente sans pénalité de poids",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PLATING,
            "rarity": ModRarity.RARE,
            "effects": {
                "physical_resist_bonus": 0.1,   # +10% de résistance aux dégâts physiques
                "weight_multiplier": 0.8        # -20% de poids
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 4,
            "crafting_materials": ["composite_material", "lightweight_alloy", "carbon_fiber"]
        }
        
        mod_system.mods_database["reactive_plating"] = {
            "id": "reactive_plating",
            "name": "Blindage réactif",
            "description": "Réduit les dégâts des armes explosives",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PLATING,
            "rarity": ModRarity.RARE,
            "effects": {
                "explosive_resist_bonus": 0.3,  # +30% de résistance aux explosifs
                "durability_multiplier": 0.9    # -10% de durabilité (s'use plus vite)
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "SHIELD"],
                "tech_level": 3
            },
            "installation_difficulty": 5,
            "crafting_materials": ["reactive_compound", "metal_plates", "electronic_parts"]
        }
        
        # Doublure
        mod_system.mods_database["thermal_lining"] = {
            "id": "thermal_lining",
            "name": "Doublure thermique",
            "description": "Protège contre les dégâts thermiques et les températures extrêmes",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.LINING,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "thermal_resist_bonus": 0.25,      # +25% de résistance thermique
                "environmental_protection": ["HEAT", "COLD"]
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["thermal_fabric", "insulation_material"]
        }
        
        mod_system.mods_database["energy_dispersing_lining"] = {
            "id": "energy_dispersing_lining",
            "name": "Doublure dispersante d'énergie",
            "description": "Dissipe l'énergie des armes laser et plasma",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.LINING,
            "rarity": ModRarity.RARE,
            "effects": {
                "energy_resist_bonus": 0.2,        # +20% de résistance énergétique
                "emp_resist_bonus": 0.15           # +15% de résistance aux EMP
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"],
                "tech_level": 2
            },
            "installation_difficulty": 4,
            "crafting_materials": ["conductive_mesh", "insulator", "microfiber"]
        }
        
        mod_system.mods_database["chemical_resistant_lining"] = {
            "id": "chemical_resistant_lining",
            "name": "Doublure résistante aux produits chimiques",
            "description": "Protège contre les dégâts chimiques et la contamination",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.LINING,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "chemical_resist_bonus": 0.25,     # +25% de résistance chimique
                "environmental_protection": ["TOXIN", "RADIATION", "CONTAMINATION"]
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["chemical_resistant_fabric", "sealant"]
        }
        
        # Rembourrage
        mod_system.mods_database["shock_absorbing_padding"] = {
            "id": "shock_absorbing_padding",
            "name": "Rembourrage absorbant les chocs",
            "description": "Réduit l'impact des coups et les dégâts contondants",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PADDING,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "blunt_resist_bonus": 0.2,       # +20% de résistance contondante
                "fall_damage_reduction": 0.3     # -30% de dégâts de chute
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 2,
            "crafting_materials": ["shock_absorbing_gel", "padding_material"]
        }
        
        mod_system.mods_database["ergonomic_padding"] = {
            "id": "ergonomic_padding",
            "name": "Rembourrage ergonomique",
            "description": "Améliore le confort et réduit la fatigue",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PADDING,
            "rarity": ModRarity.COMMON,
            "effects": {
                "stamina_drain_reduction": 0.15,   # -15% de consommation d'endurance
                "mobility_bonus": 0.1              # +10% de mobilité
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 1,
            "crafting_materials": ["comfort_padding", "flexible_material"]
        }
        
        mod_system.mods_database["medical_padding"] = {
            "id": "medical_padding",
            "name": "Rembourrage médical",
            "description": "Contient des agents médicaux qui aident à la guérison",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.PADDING,
            "rarity": ModRarity.RARE,
            "effects": {
                "passive_healing": 1,             # +1 PV récupéré par minute
                "bleeding_resist_bonus": 0.2      # +20% de résistance aux saignements
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"],
                "tech_level": 2
            },
            "installation_difficulty": 3,
            "crafting_materials": ["medical_compound", "absorbent_fabric", "biogel"]
        }
        
        # Tissage
        mod_system.mods_database["ballistic_weave"] = {
            "id": "ballistic_weave",
            "name": "Tissage balistique",
            "description": "Réduit les dégâts des armes à projectiles",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.WEAVE,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "ballistic_resist_bonus": 0.2,     # +20% de résistance balistique
                "piercing_resist_bonus": 0.1       # +10% de résistance perforante
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["ballistic_fiber", "reinforced_thread"]
        }
        
        mod_system.mods_database["nanomesh_weave"] = {
            "id": "nanomesh_weave",
            "name": "Tissage nanomesh",
            "description": "Tissage avancé qui s'adapte aux attaques",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.WEAVE,
            "rarity": ModRarity.EPIC,
            "effects": {
                "adaptive_defense": True,          # Adaptation aux types d'attaques
                "self_repair": 2                   # Répare 2 points de durabilité par heure
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"],
                "tech_level": 4
            },
            "installation_difficulty": 6,
            "crafting_materials": ["nanomaterial", "smart_fabric", "microprocessor", "rare_compound"]
        }
        
        mod_system.mods_database["stealth_weave"] = {
            "id": "stealth_weave",
            "name": "Tissage furtif",
            "description": "Réduit la signature visuelle, thermique et sonore",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.WEAVE,
            "rarity": ModRarity.RARE,
            "effects": {
                "stealth_bonus": 0.2,             # +20% de furtivité
                "noise_reduction": 0.15           # -15% de bruit
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"],
                "tech_level": 3
            },
            "installation_difficulty": 4,
            "crafting_materials": ["stealth_fiber", "sound_dampening_material", "thermal_regulator"]
        }
        
        # Revêtement
        mod_system.mods_database["reflective_coating"] = {
            "id": "reflective_coating",
            "name": "Revêtement réfléchissant",
            "description": "Réfléchit une partie des attaques laser",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.COATING,
            "rarity": ModRarity.RARE,
            "effects": {
                "laser_resist_bonus": 0.3,        # +30% de résistance laser
                "chance_to_reflect": 0.15         # 15% de chance de réfléchir les attaques laser
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT", "SHIELD"],
                "tech_level": 3
            },
            "installation_difficulty": 4,
            "crafting_materials": ["reflective_compound", "precision_applicator", "energy_crystal"]
        }
        
        mod_system.mods_database["chameleon_coating"] = {
            "id": "chameleon_coating",
            "name": "Revêtement caméléon",
            "description": "S'adapte à l'environnement pour améliorer la furtivité",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.COATING,
            "rarity": ModRarity.EPIC,
            "effects": {
                "stealth_bonus": 0.3,             # +30% de furtivité
                "adaptive_camouflage": True       # Camouflage adaptatif
            },
            "requirements": {
                "armor_types": ["MEDIUM", "LIGHT"],
                "tech_level": 4
            },
            "installation_difficulty": 5,
            "crafting_materials": ["chameleon_compound", "photoreactive_material", "microprocessor", "power_cell"]
        }
        
        mod_system.mods_database["hazard_coating"] = {
            "id": "hazard_coating",
            "name": "Revêtement anti-risques",
            "description": "Protège contre plusieurs types de dangers environnementaux",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.COATING,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "environmental_protection": ["ACID", "ELECTRICITY", "CORROSION"],
                "durability_multiplier": 1.2      # +20% de durabilité
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT", "SHIELD"]
            },
            "installation_difficulty": 3,
            "crafting_materials": ["hazard_resistant_compound", "sealant", "protective_resin"]
        }
        
        # Système
        mod_system.mods_database["auto_injector_system"] = {
            "id": "auto_injector_system",
            "name": "Système d'auto-injection",
            "description": "Injecte automatiquement des stimulants médicaux en cas de blessure",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.SYSTEM,
            "rarity": ModRarity.RARE,
            "effects": {
                "auto_healing": True,              # Soins automatiques
                "critical_response": 0.3           # 30% de chance d'activer des soins d'urgence
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"],
                "tech_level": 3
            },
            "installation_difficulty": 4,
            "crafting_materials": ["medical_injector", "microprocessor", "biogel", "tubing"]
        }
        
        mod_system.mods_database["power_assist_system"] = {
            "id": "power_assist_system",
            "name": "Système d'assistance énergétique",
            "description": "Augmente la force et réduit l'impact du poids de l'armure",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.SYSTEM,
            "rarity": ModRarity.RARE,
            "effects": {
                "strength_bonus": 2,              # +2 de force
                "weight_penalty_reduction": 0.5   # -50% de pénalité de poids
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM"],
                "tech_level": 3
            },
            "installation_difficulty": 5,
            "crafting_materials": ["servo_motor", "power_cell", "hydraulic_system", "microprocessor"]
        }
        
        mod_system.mods_database["environmental_control_system"] = {
            "id": "environmental_control_system",
            "name": "Système de contrôle environnemental",
            "description": "Régule la température et filtre l'air pour un confort optimal",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.SYSTEM,
            "rarity": ModRarity.UNCOMMON,
            "effects": {
                "environment_immunity": ["HEAT", "COLD", "TOXIN", "GAS"],
                "stamina_recovery_bonus": 0.2     # +20% de récupération d'endurance
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"],
                "tech_level": 2
            },
            "installation_difficulty": 3,
            "crafting_materials": ["air_filter", "temperature_regulator", "microprocessor", "power_cell"]
        }
        
        # Accessoire
        mod_system.mods_database["tactical_holster"] = {
            "id": "tactical_holster",
            "name": "Holster tactique",
            "description": "Permet de dégainer une arme plus rapidement",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.ACCESSORY,
            "rarity": ModRarity.COMMON,
            "effects": {
                "weapon_draw_time_multiplier": 0.7,  # -30% de temps de dégainage
                "weapon_switch_time_multiplier": 0.8  # -20% de temps de changement d'arme
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 1,
            "crafting_materials": ["leather", "quick_release_mechanism"]
        }
        
        mod_system.mods_database["utility_pouches"] = {
            "id": "utility_pouches",
            "name": "Poches utilitaires",
            "description": "Ajoute de l'espace de stockage pour les objets de petite taille",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.ACCESSORY,
            "rarity": ModRarity.COMMON,
            "effects": {
                "small_item_capacity_bonus": 5,    # +5 emplacements pour petits objets
                "consumable_use_time_multiplier": 0.8  # -20% de temps d'utilisation des consommables
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"]
            },
            "installation_difficulty": 1,
            "crafting_materials": ["fabric", "fastener"]
        }
        
        mod_system.mods_database["threat_detector"] = {
            "id": "threat_detector",
            "name": "Détecteur de menaces",
            "description": "Alerte le porteur des dangers à proximité",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.ACCESSORY,
            "rarity": ModRarity.RARE,
            "effects": {
                "detection_range_bonus": 10,      # +10m de portée de détection
                "surprise_chance_reduction": 0.5  # -50% de chance d'être surpris
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM", "LIGHT"],
                "tech_level": 3
            },
            "installation_difficulty": 3,
            "crafting_materials": ["sensor_array", "microprocessor", "power_cell", "display_unit"]
        }
        
        mod_system.mods_database["energy_shield_generator"] = {
            "id": "energy_shield_generator",
            "name": "Générateur de bouclier énergétique",
            "description": "Crée un bouclier d'énergie qui absorbe les dégâts",
            "type": ModType.ARMOR,
            "slot": ArmorModSlot.ACCESSORY,
            "rarity": ModRarity.EPIC,
            "effects": {
                "energy_shield": 50,              # Bouclier de 50 PV
                "shield_recharge_rate": 5,        # Recharge de 5 PV par minute
                "shield_recharge_delay": 30       # Délai de 30 secondes avant recharge
            },
            "requirements": {
                "armor_types": ["HEAVY", "MEDIUM"],
                "tech_level": 4
            },
            "installation_difficulty": 6,
            "crafting_materials": ["shield_emitter", "power_core", "energy_capacitor", "microprocessor", "rare_crystal"]
        }
        
        logger.debug("Modifications d'armure initialisées")
