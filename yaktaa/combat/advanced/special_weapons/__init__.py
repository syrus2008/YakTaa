"""
Système d'armes spéciales pour YakTaa

Ce module contient les classes et fonctions pour gérer les armes spéciales
avec des capacités uniques qui vont au-delà des armes standard.
"""

from .core import SpecialWeaponSystem, SpecialWeaponType, SpecialWeaponRarity
from .effects import SpecialWeaponEffect, EffectTriggerType
from .weapons import initialize_special_weapons
from .evolution import WeaponEvolutionSystem, EvolutionTrigger
from .crafting import WeaponCraftingSystem, WeaponComponentType

__all__ = [
    'SpecialWeaponSystem',
    'SpecialWeaponType',
    'SpecialWeaponRarity',
    'SpecialWeaponEffect',
    'EffectTriggerType',
    'initialize_special_weapons',
    'WeaponEvolutionSystem',
    'EvolutionTrigger',
    'WeaponCraftingSystem',
    'WeaponComponentType'
]
