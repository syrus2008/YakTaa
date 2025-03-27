"""
Gestionnaire de modifications d'équipement pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from .equipment_mods import EquipmentModSystem, ModType, ModRarity, WeaponModSlot, ArmorModSlot

logger = logging.getLogger("YakTaa.Combat.Advanced.EquipmentModsManager")

class ModificationResult(Enum):
    """Résultats possibles d'une opération de modification"""
    SUCCESS = 0
    INCOMPATIBLE_SLOT = 1
    INCOMPATIBLE_EQUIPMENT = 2
    SLOT_ALREADY_USED = 3
    MOD_NOT_FOUND = 4
    EQUIPMENT_NOT_FOUND = 5
    INSUFFICIENT_SKILLS = 6
    MISSING_MATERIALS = 7
    INSTALLATION_FAILED = 8
    REMOVAL_FAILED = 9
    NOT_INSTALLED = 10

class EquipmentModManager:
    """
    Gestionnaire qui permet d'installer et de gérer les modifications d'équipement
    """
    
    def __init__(self, mod_system: EquipmentModSystem):
        """
        Initialise le gestionnaire de modifications
        
        Args:
            mod_system: Le système de modifications d'équipement
        """
        self.mod_system = mod_system
        logger.debug("Gestionnaire de modifications d'équipement initialisé")
    
    def get_compatible_mods(self, equipment: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère toutes les modifications compatibles avec un équipement
        
        Args:
            equipment: L'équipement
            
        Returns:
            Dictionnaire des modifications compatibles par emplacement
        """
        if not equipment:
            return {}
            
        # Déterminer le type d'équipement
        equipment_type = self._get_equipment_type(equipment)
        if not equipment_type:
            return {}
            
        # Récupérer les emplacements compatibles
        compatible_slots = self.mod_system.compatible_slots.get(equipment_type, [])
        
        # Récupérer les restrictions d'équipement
        equipment_subtype = equipment.get("subtype", "UNKNOWN")
        tech_level = equipment.get("tech_level", 1)
        
        # Initialiser le résultat
        result = {}
        
        # Parcourir tous les emplacements compatibles
        for slot in compatible_slots:
            # Récupérer les modifications pour cet emplacement
            slot_mods = []
            
            for mod_id, mod in self.mod_system.mods_database.items():
                # Vérifier la compatibilité du type
                if mod["type"] != equipment_type and mod["type"] != ModType.UNIVERSAL:
                    continue
                    
                # Vérifier la compatibilité de l'emplacement
                if mod["slot"] != slot:
                    continue
                    
                # Vérifier la compatibilité avec le sous-type d'équipement
                requirements = mod.get("requirements", {})
                weapon_types = requirements.get("weapon_types", [])
                armor_types = requirements.get("armor_types", [])
                
                if equipment_type == ModType.WEAPON and weapon_types and equipment_subtype not in weapon_types:
                    continue
                    
                if equipment_type == ModType.ARMOR and armor_types and equipment_subtype not in armor_types:
                    continue
                    
                # Vérifier le niveau technologique requis
                if requirements.get("tech_level", 1) > tech_level:
                    continue
                    
                # La modification est compatible
                slot_mods.append(mod)
            
            # Ajouter les modifications trouvées au résultat
            if slot_mods:
                result[slot.name] = slot_mods
        
        return result
    
    def _get_equipment_type(self, equipment: Dict[str, Any]) -> Optional[ModType]:
        """Détermine le type de modification correspondant à un équipement"""
        equipment_type = equipment.get("type", "").upper()
        
        if equipment_type in ["PISTOL", "RIFLE", "SMG", "SHOTGUN", "ENERGY_WEAPON", "MELEE_WEAPON", "HEAVY_WEAPON"]:
            return ModType.WEAPON
        elif equipment_type in ["ARMOR", "HELMET", "CHEST", "LEGS", "ARMS"]:
            return ModType.ARMOR
        elif equipment_type == "SHIELD":
            return ModType.SHIELD
        elif equipment_type in ["ACCESSORY", "TRINKET", "DEVICE"]:
            return ModType.ACCESSORY
        
        return None
    
    def install_mod(self, equipment_id: str, equipment: Dict[str, Any], mod_id: str, 
                   installer_skills: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Installe une modification sur un équipement
        
        Args:
            equipment_id: Identifiant de l'équipement
            equipment: L'équipement
            mod_id: Identifiant de la modification
            installer_skills: Compétences de l'installateur
            
        Returns:
            Résultat de l'installation
        """
        # Vérifier que l'équipement existe
        if not equipment:
            return {
                "success": False,
                "result": ModificationResult.EQUIPMENT_NOT_FOUND,
                "message": "Équipement non trouvé"
            }
            
        # Vérifier que la modification existe
        if mod_id not in self.mod_system.mods_database:
            return {
                "success": False,
                "result": ModificationResult.MOD_NOT_FOUND,
                "message": f"Modification {mod_id} introuvable"
            }
            
        mod = self.mod_system.mods_database[mod_id]
        
        # Vérifier la compatibilité
        equipment_type = self._get_equipment_type(equipment)
        if not equipment_type:
            return {
                "success": False,
                "result": ModificationResult.INCOMPATIBLE_EQUIPMENT,
                "message": "Type d'équipement incompatible"
            }
            
        # Vérifier la compatibilité de l'emplacement
        slot = mod["slot"]
        compatible_slots = self.mod_system.compatible_slots.get(equipment_type, [])
        
        if slot not in compatible_slots:
            return {
                "success": False,
                "result": ModificationResult.INCOMPATIBLE_SLOT,
                "message": f"Emplacement {slot.name} incompatible avec l'équipement"
            }
            
        # Vérifier les restrictions d'équipement
        equipment_subtype = equipment.get("subtype", "UNKNOWN")
        tech_level = equipment.get("tech_level", 1)
        
        requirements = mod.get("requirements", {})
        weapon_types = requirements.get("weapon_types", [])
        armor_types = requirements.get("armor_types", [])
        
        if equipment_type == ModType.WEAPON and weapon_types and equipment_subtype not in weapon_types:
            return {
                "success": False,
                "result": ModificationResult.INCOMPATIBLE_EQUIPMENT,
                "message": f"Type d'arme {equipment_subtype} incompatible avec la modification"
            }
            
        if equipment_type == ModType.ARMOR and armor_types and equipment_subtype not in armor_types:
            return {
                "success": False,
                "result": ModificationResult.INCOMPATIBLE_EQUIPMENT,
                "message": f"Type d'armure {equipment_subtype} incompatible avec la modification"
            }
            
        # Vérifier le niveau technologique requis
        if requirements.get("tech_level", 1) > tech_level:
            return {
                "success": False,
                "result": ModificationResult.INCOMPATIBLE_EQUIPMENT,
                "message": f"Niveau technologique {tech_level} insuffisant (requis: {requirements.get('tech_level', 1)})"
            }
            
        # Vérifier si l'emplacement est déjà utilisé
        slot_key = (equipment_id, slot.name)
        if slot_key in self.mod_system.installed_mods:
            return {
                "success": False,
                "result": ModificationResult.SLOT_ALREADY_USED,
                "message": f"Emplacement {slot.name} déjà utilisé par une autre modification"
            }
            
        # Vérifier les compétences requises pour l'installation
        installation_difficulty = mod.get("installation_difficulty", 1)
        if installer_skills:
            # Déterminer la compétence applicable
            applicable_skill = None
            skill_value = 0
            
            if equipment_type == ModType.WEAPON:
                applicable_skill = "weapons_tech"
            elif equipment_type == ModType.ARMOR or equipment_type == ModType.SHIELD:
                applicable_skill = "armor_tech"
            else:
                applicable_skill = "electronics"
                
            skill_value = installer_skills.get(applicable_skill, 0)
            
            # Vérifier si les compétences sont suffisantes
            if skill_value < installation_difficulty - 2:
                return {
                    "success": False,
                    "result": ModificationResult.INSUFFICIENT_SKILLS,
                    "message": f"Compétence {applicable_skill} insuffisante (valeur: {skill_value}, requis: {installation_difficulty - 2})"
                }
                
            # Calculer la chance de réussite
            success_chance = min(0.95, 0.5 + (skill_value - installation_difficulty) * 0.1)
            
            # Vérifier la réussite de l'installation
            if random.random() > success_chance:
                return {
                    "success": False,
                    "result": ModificationResult.INSTALLATION_FAILED,
                    "message": "L'installation a échoué",
                    "chance_was": success_chance
                }
        
        # Installer la modification
        self.mod_system.installed_mods[slot_key] = mod_id
        
        logger.debug(f"Modification {mod_id} installée sur l'équipement {equipment_id} (emplacement {slot.name})")
        
        return {
            "success": True,
            "result": ModificationResult.SUCCESS,
            "message": f"Modification {mod['name']} installée avec succès",
            "mod": mod,
            "equipment_id": equipment_id,
            "slot": slot.name
        }
    
    def remove_mod(self, equipment_id: str, slot: Any, installer_skills: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Retire une modification d'un équipement
        
        Args:
            equipment_id: Identifiant de l'équipement
            slot: Emplacement de la modification
            installer_skills: Compétences de l'installateur
            
        Returns:
            Résultat du retrait
        """
        # Convertir l'emplacement en chaîne si nécessaire
        if isinstance(slot, (WeaponModSlot, ArmorModSlot)):
            slot_name = slot.name
        else:
            slot_name = str(slot)
            
        # Vérifier si une modification est installée à cet emplacement
        slot_key = (equipment_id, slot_name)
        if slot_key not in self.mod_system.installed_mods:
            return {
                "success": False,
                "result": ModificationResult.NOT_INSTALLED,
                "message": f"Aucune modification installée à l'emplacement {slot_name}"
            }
            
        # Récupérer la modification
        mod_id = self.mod_system.installed_mods[slot_key]
        mod = self.mod_system.mods_database.get(mod_id)
        
        if not mod:
            # La modification n'existe plus, la retirer quand même
            del self.mod_system.installed_mods[slot_key]
            return {
                "success": True,
                "result": ModificationResult.SUCCESS,
                "message": "Modification retirée",
                "mod_id": mod_id,
                "equipment_id": equipment_id,
                "slot": slot_name
            }
            
        # Vérifier les compétences requises pour le retrait
        removal_difficulty = mod.get("installation_difficulty", 1) - 1  # Le retrait est généralement plus facile
        removal_difficulty = max(1, removal_difficulty)  # Minimum 1
        
        if installer_skills:
            # Déterminer la compétence applicable
            applicable_skill = None
            skill_value = 0
            
            if mod["type"] == ModType.WEAPON:
                applicable_skill = "weapons_tech"
            elif mod["type"] == ModType.ARMOR or mod["type"] == ModType.SHIELD:
                applicable_skill = "armor_tech"
            else:
                applicable_skill = "electronics"
                
            skill_value = installer_skills.get(applicable_skill, 0)
            
            # Vérifier si les compétences sont suffisantes
            if skill_value < removal_difficulty - 2:
                return {
                    "success": False,
                    "result": ModificationResult.INSUFFICIENT_SKILLS,
                    "message": f"Compétence {applicable_skill} insuffisante (valeur: {skill_value}, requis: {removal_difficulty - 2})"
                }
                
            # Calculer la chance de réussite
            success_chance = min(0.98, 0.6 + (skill_value - removal_difficulty) * 0.15)
            
            # Vérifier la réussite du retrait
            if random.random() > success_chance:
                return {
                    "success": False,
                    "result": ModificationResult.REMOVAL_FAILED,
                    "message": "Le retrait a échoué",
                    "chance_was": success_chance
                }
        
        # Retirer la modification
        del self.mod_system.installed_mods[slot_key]
        
        logger.debug(f"Modification {mod_id} retirée de l'équipement {equipment_id} (emplacement {slot_name})")
        
        return {
            "success": True,
            "result": ModificationResult.SUCCESS,
            "message": f"Modification {mod['name']} retirée avec succès",
            "mod": mod,
            "equipment_id": equipment_id,
            "slot": slot_name
        }
    
    def get_installed_mods(self, equipment_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Récupère toutes les modifications installées sur un équipement
        
        Args:
            equipment_id: Identifiant de l'équipement
            
        Returns:
            Dictionnaire des modifications installées par emplacement
        """
        result = {}
        
        # Parcourir toutes les modifications installées
        for (eq_id, slot_name), mod_id in self.mod_system.installed_mods.items():
            if eq_id == equipment_id:
                # Récupérer la modification
                mod = self.mod_system.mods_database.get(mod_id)
                if mod:
                    result[slot_name] = mod
        
        return result
    
    def calculate_mod_effects(self, equipment_id: str, equipment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les effets cumulés de toutes les modifications installées sur un équipement
        
        Args:
            equipment_id: Identifiant de l'équipement
            equipment: L'équipement
            
        Returns:
            Effets cumulés des modifications
        """
        # Récupérer toutes les modifications installées
        installed_mods = self.get_installed_mods(equipment_id)
        
        # Initialiser les effets cumulés
        cumulative_effects = {}
        
        # Parcourir toutes les modifications installées
        for slot_name, mod in installed_mods.items():
            # Récupérer les effets de la modification
            effects = mod.get("effects", {})
            
            # Ajouter les effets au cumul
            for effect_key, effect_value in effects.items():
                # Gérer les différents types d'effets
                if effect_key.endswith("_multiplier"):
                    # Les multiplicateurs se multiplient entre eux
                    current_value = cumulative_effects.get(effect_key, 1.0)
                    cumulative_effects[effect_key] = current_value * effect_value
                elif effect_key.endswith("_bonus") or effect_key.endswith("_reduction"):
                    # Les bonus et réductions s'additionnent
                    current_value = cumulative_effects.get(effect_key, 0.0)
                    cumulative_effects[effect_key] = current_value + effect_value
                elif effect_key.endswith("_add"):
                    # Les ajouts sont stockés dans une liste
                    current_value = cumulative_effects.get(effect_key, [])
                    if effect_value not in current_value:
                        current_value.append(effect_value)
                    cumulative_effects[effect_key] = current_value
                elif isinstance(effect_value, bool):
                    # Les effets booléens (true/false) sont conservés comme true si au moins une modification les active
                    current_value = cumulative_effects.get(effect_key, False)
                    cumulative_effects[effect_key] = current_value or effect_value
                elif isinstance(effect_value, list):
                    # Les listes sont simplement concaténées
                    current_value = cumulative_effects.get(effect_key, [])
                    for item in effect_value:
                        if item not in current_value:
                            current_value.append(item)
                    cumulative_effects[effect_key] = current_value
                else:
                    # Les autres valeurs sont remplacées par la valeur la plus élevée
                    current_value = cumulative_effects.get(effect_key, 0)
                    cumulative_effects[effect_key] = max(current_value, effect_value)
        
        return {
            "success": True,
            "equipment_id": equipment_id,
            "installed_mods_count": len(installed_mods),
            "effects": cumulative_effects
        }
    
    def generate_random_mod(self, equipment_type: ModType, rarity: ModRarity = None) -> Dict[str, Any]:
        """
        Génère une modification aléatoire
        
        Args:
            equipment_type: Type d'équipement cible
            rarity: Rareté souhaitée (optionnel)
            
        Returns:
            Modification aléatoire
        """
        # Filtrer les modifications par type d'équipement
        compatible_mods = []
        
        for mod_id, mod in self.mod_system.mods_database.items():
            if mod["type"] == equipment_type or mod["type"] == ModType.UNIVERSAL:
                # Si une rareté est spécifiée, filtrer également par rareté
                if rarity is None or mod["rarity"] == rarity:
                    compatible_mods.append(mod)
        
        # Si aucune modification n'est trouvée, retourner None
        if not compatible_mods:
            return None
            
        # Sélectionner une modification aléatoire
        return random.choice(compatible_mods)
    
    def craft_mod(self, mod_id: str, crafter_skills: Dict[str, int], 
                 available_materials: Dict[str, int]) -> Dict[str, Any]:
        """
        Tente de fabriquer une modification
        
        Args:
            mod_id: Identifiant de la modification à fabriquer
            crafter_skills: Compétences du fabricant
            available_materials: Matériaux disponibles
            
        Returns:
            Résultat de la fabrication
        """
        # Vérifier que la modification existe
        if mod_id not in self.mod_system.mods_database:
            return {
                "success": False,
                "message": f"Modification {mod_id} introuvable"
            }
            
        mod = self.mod_system.mods_database[mod_id]
        
        # Vérifier les matériaux requis
        crafting_materials = mod.get("crafting_materials", [])
        missing_materials = []
        
        for material in crafting_materials:
            if material not in available_materials or available_materials[material] < 1:
                missing_materials.append(material)
        
        if missing_materials:
            return {
                "success": False,
                "result": ModificationResult.MISSING_MATERIALS,
                "message": "Matériaux manquants",
                "missing_materials": missing_materials
            }
            
        # Déterminer la compétence applicable
        applicable_skill = None
        skill_value = 0
        
        if mod["type"] == ModType.WEAPON:
            applicable_skill = "weapons_tech"
        elif mod["type"] == ModType.ARMOR or mod["type"] == ModType.SHIELD:
            applicable_skill = "armor_tech"
        else:
            applicable_skill = "electronics"
            
        skill_value = crafter_skills.get(applicable_skill, 0)
        
        # Calculer la difficulté de fabrication
        crafting_difficulty = mod.get("installation_difficulty", 1) + mod["rarity"].value
        
        # Vérifier si les compétences sont suffisantes
        if skill_value < crafting_difficulty - 1:
            return {
                "success": False,
                "result": ModificationResult.INSUFFICIENT_SKILLS,
                "message": f"Compétence {applicable_skill} insuffisante (valeur: {skill_value}, requis: {crafting_difficulty - 1})"
            }
            
        # Calculer la chance de réussite
        success_chance = min(0.95, 0.4 + (skill_value - crafting_difficulty) * 0.1)
        
        # Vérifier la réussite de la fabrication
        crafting_success = random.random() <= success_chance
        
        # Consommer les matériaux (même en cas d'échec)
        for material in crafting_materials:
            available_materials[material] -= 1
            
        if not crafting_success:
            # Chance de récupérer certains matériaux en cas d'échec
            recovery_chance = 0.3 + skill_value * 0.05  # 30% + 5% par niveau de compétence
            recovered_materials = []
            
            for material in crafting_materials:
                if random.random() <= recovery_chance:
                    available_materials[material] += 1
                    recovered_materials.append(material)
            
            return {
                "success": False,
                "result": ModificationResult.INSTALLATION_FAILED,
                "message": "La fabrication a échoué",
                "chance_was": success_chance,
                "recovered_materials": recovered_materials
            }
            
        # Fabrication réussie
        return {
            "success": True,
            "result": ModificationResult.SUCCESS,
            "message": f"Modification {mod['name']} fabriquée avec succès",
            "mod": mod,
            "used_materials": crafting_materials
        }
