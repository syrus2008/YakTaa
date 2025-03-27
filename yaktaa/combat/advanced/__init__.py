"""
Module de combat avancé pour YakTaa
Ce module étend le système de combat existant avec des fonctionnalités avancées
"""

from .initiative import InitiativeSystem
from .tactical import TacticalCombatSystem
from .status_effects import StatusEffectSystem
from .special_actions import SpecialActionSystem
from .defense import DefenseSystem
from .ai import EnemyAISystem
from .environment import CombatEnvironmentSystem
from .group import GroupCombatSystem
from .progression import CombatProgressionSystem
from .progression_bonuses import CombatProgressionBonuses
from .equipment_mods import EquipmentModSystem
from .equipment_mods_manager import EquipmentModManager
from .armor_mods import ArmorModifications
from .special_weapons import (
    SpecialWeaponSystem, 
    WeaponEvolutionSystem, 
    WeaponCraftingSystem,
    initialize_special_weapons
)

__all__ = [
    'InitiativeSystem',
    'TacticalCombatSystem',
    'StatusEffectSystem',
    'SpecialActionSystem',
    'DefenseSystem',
    'EnemyAISystem',
    'CombatEnvironmentSystem',
    'GroupCombatSystem',
    'CombatProgressionSystem',
    'CombatProgressionBonuses',
    'EquipmentModSystem',
    'EquipmentModManager',
    'ArmorModifications',
    'SpecialWeaponSystem',
    'WeaponEvolutionSystem',
    'WeaponCraftingSystem',
    'initialize_special_weapons'
]
