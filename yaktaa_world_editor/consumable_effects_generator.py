"""
Module pour la génération des effets des consommables
Contient la fonction pour créer les effets des objets consommables
"""

import logging
from typing import Dict

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ConsumableEffects")

def _generate_consumable_effects(self, item_type: str, rarity: str) -> Dict:
    """
    Génère des effets pour un objet consommable en fonction de son type et de sa rareté
    
    Args:
        item_type: Type de consommable
        rarity: Rareté du consommable
        
    Returns:
        Dictionnaire d'effets
    """
    effects = {}
    rarity_multiplier = {
        "Common": 1.0, "Uncommon": 1.3, "Rare": 1.8, 
        "Epic": 2.5, "Legendary": 4.0
    }.get(rarity, 1.0)
    
    # Modifier légèrement le multiplicateur pour chaque item
    rarity_multiplier *= 0.9 + self.random.random() * 0.2
    
    if item_type == "Data Chip":
        effects["knowledge_boost"] = int(10 * rarity_multiplier)
        effects["skill_xp"] = int(50 * rarity_multiplier)
        effects["target_skill"] = self.random.choice(["Hacking", "Cryptography", "Programming", "Networks", "Security"])
        
    elif item_type == "Neural Booster":
        effects["mental_boost"] = int(15 * rarity_multiplier)
        effects["focus_duration"] = int(30 * rarity_multiplier)  # en minutes
        effects["cooldown"] = int(240 - 30 * rarity_multiplier)  # en minutes
        
    elif item_type == "Code Fragment":
        effects["unlock_level"] = int(1 + 1 * rarity_multiplier)
        effects["code_quality"] = int(10 * rarity_multiplier)
        effects["bypass_chance"] = min(90, int(30 * rarity_multiplier))  # en %
        
    elif item_type == "Crypto Key":
        effects["encryption_level"] = int(2 * rarity_multiplier)
        effects["unlock_time"] = int(30 - 5 * rarity_multiplier)  # en secondes
        effects["detection_reduction"] = min(90, int(20 * rarity_multiplier))  # en %
        
    elif item_type == "Access Card":
        effects["access_level"] = int(1 + 1 * rarity_multiplier)
        effects["building_types"] = self.random.sample(["Corporate", "Government", "Military", "Research", "Commercial"], 
                                                    k=min(5, max(1, int(1 + rarity_multiplier))))
        effects["duration"] = int(60 * rarity_multiplier)  # en minutes
        
    elif item_type == "Security Token":
        effects["security_level"] = int(2 * rarity_multiplier)
        effects["valid_duration"] = int(30 * rarity_multiplier)  # en minutes
        effects["traceback_protection"] = min(95, int(30 * rarity_multiplier))  # en %
        
    elif item_type == "Firewall Bypass":
        effects["bypass_strength"] = int(15 * rarity_multiplier)
        effects["firewall_levels"] = int(1 + 1 * rarity_multiplier)
        effects["stealth_bonus"] = min(75, int(15 * rarity_multiplier))  # en %
        
    elif item_type == "Signal Jammer":
        effects["jamming_radius"] = int(10 * rarity_multiplier)  # en mètres
        effects["duration"] = int(30 * rarity_multiplier)  # en secondes
        effects["effectiveness"] = min(95, int(50 * rarity_multiplier))  # en %
        
    elif item_type == "Decryption Tool":
        effects["decryption_power"] = int(10 * rarity_multiplier)
        effects["compatible_encryptions"] = min(5, max(1, int(1 + rarity_multiplier)))
        effects["time_reduction"] = min(90, int(20 * rarity_multiplier))  # en %
        
    elif item_type == "Memory Cleaner":
        effects["trace_removal"] = min(100, int(60 * rarity_multiplier))  # en %
        effects["system_optimization"] = int(10 * rarity_multiplier)
        effects["cooldown_reduction"] = min(50, int(10 * rarity_multiplier))  # en %
        
    elif item_type == "Battery Pack":
        effects["energy_boost"] = int(20 * rarity_multiplier)
        effects["duration"] = int(60 * rarity_multiplier)  # en minutes
        effects["device_types"] = min(5, max(1, int(1 + rarity_multiplier)))
        
    else:  # Types génériques ou non listés
        effects["general_boost"] = int(10 * rarity_multiplier)
        effects["duration"] = int(30 * rarity_multiplier)  # en minutes
        
    # Ajouter des bonus/malus aléatoires
    if self.random.random() < 0.3:  # 30% de chance d'avoir un bonus
        if "duration" in effects:
            effects["duration"] = int(effects["duration"] * (1.1 + self.random.random() * 0.3))
        elif list(effects.keys()):
            bonus_stat = self.random.choice(list(effects.keys()))
            if isinstance(effects[bonus_stat], int):
                bonus_value = effects[bonus_stat] * (0.1 + self.random.random() * 0.2)
                effects[bonus_stat] = int(effects[bonus_stat] + bonus_value)
                
    # Ajouter des effets spéciaux pour les objets légendaires et épiques
    if rarity in ["Legendary", "Epic"]:
        if self.random.random() < 0.7:  # 70% de chance d'avoir un effet spécial
            special_effects = {
                "Data Chip": "Débloque une compétence cachée",
                "Neural Booster": "Permet de visualiser les flux de données en réalité augmentée",
                "Code Fragment": "Contourne automatiquement certaines sécurités",
                "Crypto Key": "Auto-adaptation aux systèmes de sécurité",
                "Access Card": "Permet d'accéder à des zones restreintes",
                "Security Token": "Usurpe l'identité d'un admin système",
                "Firewall Bypass": "Invisibilité temporaire aux systèmes de surveillance",
                "Signal Jammer": "Peut désactiver temporairement des caméras de sécurité",
                "Decryption Tool": "Révèle des informations cachées dans les fichiers",
                "Memory Cleaner": "Efface complètement les traces de votre passage",
                "Battery Pack": "Surcharge temporaire des systèmes électroniques"
            }
            
            effects["special_effect"] = special_effects.get(item_type, "Effet spécial personnalisé")
                
    return effects