# YakTaa - Démonstration du système de combat
import sys
import os
import logging
import random
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any

# Ajouter le répertoire parent au path pour l'importation
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Importer les modules nécessaires
from combat.engine import CombatEngine, ActionType, CombatStatus, DamageType
from combat.ui import CombatUI
from combat.enemy import Enemy, EnemyType, generate_random_enemy
from characters.player import Player
from items.weapon import WeaponItem
from items.implant import ImplantItem

# Configurer le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_player() -> Player:
    """Crée un joueur de test avec des armes et implants"""
    # Créer un joueur de test
    player = Player("Neo")
    
    # Définir des attributs de base
    player.health = 100
    player.max_health = 100
    player.attributes = {
        "strength": 6,
        "reflexes": 8,
        "technical": 9,
        "intelligence": 10,
        "body": 5
    }
    
    # Définir les slots d'équipement
    player.active_equipment = {
        "weapon": None,
        "implant_head": None,
        "implant_eyes": None,
        "implant_arms": None,
        "implant_legs": None,
        "implant_chest": None
    }
    
    # Créer et équiper une arme avancée
    weapon = create_test_weapon()
    player.active_equipment["weapon"] = weapon
    
    # Créer et équiper des implants
    implants = create_test_implants()
    for i, (slot, implant) in enumerate(zip(
        ["implant_head", "implant_eyes", "implant_arms"],
        implants
    )):
        player.active_equipment[slot] = implant
    
    return player

def create_test_weapon() -> WeaponItem:
    """Crée une arme de test avec des fonctionnalités avancées"""
    # Créer une arme de test
    weapon = WeaponItem(
        name="Mantis Blade 2.0",
        description="Lame rétractable cybernétique améliorée avec traitement nano-edge",
        price=1500,
        rarity="RARE",  # Rare
        weapon_type="MELEE",
        damage=25,
        damage_type="PHYSICAL",  # Type de dégâts
        accuracy=85  # 85% de précision
    )
    
    # Ajouter des effets spéciaux
    weapon.special_effects = ["BLEEDING", "ARMOR_PIERCING"]
    
    # Ajouter des bonus de combat
    weapon.combat_bonuses = {
        "critical_chance": 0.15,  # +15% de chance de coup critique
        "critical_damage_multiplier": 1.7,  # Les coups critiques font x1.7 dégâts
        "damage_multiplier": 1.2  # Multiplicateur de dégâts de base
    }
    
    return weapon

def create_test_implants() -> List[ImplantItem]:
    """Crée plusieurs implants de test avec diverses fonctionnalités"""
    implants = []
    
    # Implant 1: Synapt Pro (Implant Neural)
    neural_implant = ImplantItem(
        name="Synapt Pro",
        description="Accélérateur synaptique haute performance améliorant les réflexes et la vitesse de traitement mental",
        implant_type="NEURAL",
        price=5000,
        rarity="RARE",
        humanity_cost=12,
        installation_difficulty=7,
        stats_bonus={"intelligence": 2, "reflexes": 2}
    )
    
    # Ajouter des effets spéciaux
    neural_implant.special_effects = ["INITIATIVE_BOOST", "REACTION_TIME"]
    
    # Bénéfices au combat
    neural_implant.combat_bonuses = {
        "dodge_chance": 0.2,       # +20% d'esquive
        "initiative": 25,         # +25 à l'initiative
        "action_points": 1        # +1 point d'action par tour
    }
    
    implants.append(neural_implant)
    
    # Implant 2: OculEx MK3 (Implant Oculaire)
    ocular_implant = ImplantItem(
        name="OculEx MK3",
        description="Implant oculaire tactique avec vision nocturne, zoom et analyse de cibles",
        implant_type="OPTICAL",
        price=4000,
        rarity="RARE",
        humanity_cost=8,
        installation_difficulty=6,
        stats_bonus={"perception": 3}
    )
    
    # Ajouter des effets spéciaux
    ocular_implant.special_effects = ["NIGHT_VISION", "TARGET_ANALYSIS"]
    
    # Bénéfices au combat
    ocular_implant.combat_bonuses = {
        "accuracy": 0.15,          # +15% de précision
        "critical_chance": 0.1,    # +10% chance de critique
        "target_weak_spot": 0.25  # 25% de chance de cibler un point faible
    }
    
    implants.append(ocular_implant)
    
    # Implant 3: TitaniumFrame (Implant Squelettique)
    skeletal_implant = ImplantItem(
        name="TitaniumFrame",
        description="Renforcement squelettique en nano-titane, offrant résistance aux dégâts et force améliorée",
        implant_type="SKELETAL",
        price=6000,
        rarity="RARE",
        humanity_cost=15,
        installation_difficulty=8,
        stats_bonus={"strength": 3, "body": 2}
    )
    
    # Ajouter des effets spéciaux
    skeletal_implant.special_effects = ["DAMAGE_REDUCTION", "ENHANCED_STRENGTH"]
    
    # Bénéfices au combat
    skeletal_implant.combat_bonuses = {
        "damage_resistance": 0.25,  # 25% de résistance aux dégâts
        "melee_damage": 0.2,       # +20% aux dégâts de mêlée
        "knockback_resist": 0.5    # 50% de résistance aux knockbacks
    }
    
    implants.append(skeletal_implant)
    
    return implants

def create_test_enemies(difficulty: int, count: int = 2) -> List[Enemy]:
    """Crée des ennemis de test pour le combat
    
    Args:
        difficulty: Niveau de difficulté des ennemis
        count: Nombre d'ennemis à créer
        
    Returns:
        Liste d'ennemis générés
    """
    enemies = []
    
    # Générer le nombre demandé d'ennemis
    for i in range(count):
        # Varier légèrement la difficulté
        enemy_difficulty = difficulty + random.randint(-1, 1)
        enemy_difficulty = max(1, enemy_difficulty)  # Minimum 1
        
        # Générer un ennemi aléatoire
        enemy = generate_random_enemy(enemy_difficulty, "CORPORATE")
        enemies.append(enemy)
    
    return enemies

def run_combat_demo():
    """Lance une démonstration du système de combat"""
    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("YakTaa - Démonstration du système de combat")
    root.geometry("800x600")
    
    # Créer un style cyberpunk pour l'application
    style = ttk.Style()
    style.theme_use('clam')  # Utiliser un thème de base propre
    
    # Configurer les couleurs de base
    root.configure(background='#0a0a0a')
    
    # Créer un joueur de test
    player = create_test_player()
    
    # Créer des ennemis de test
    enemies = create_test_enemies(difficulty=2, count=2)
    
    # Afficher les détails du joueur
    logger.info(f"Joueur créé: {player.name}")
    logger.info(f"Arme équipée: {player.active_equipment['weapon'].name}")
    for slot, implant in player.active_equipment.items():
        if slot.startswith("implant_") and implant is not None:
            logger.info(f"Implant équipé ({slot}): {implant.name}")
    
    # Afficher les détails des ennemis
    for enemy in enemies:
        logger.info(f"Ennemi créé: {enemy.name} (Type: {enemy.enemy_type.name}, Niveau: {enemy.level})")
    
    # Créer un moteur de combat
    combat_engine = CombatEngine(player, enemies)
    
    # Fonction de callback pour la fin du combat
    def on_combat_end(status):
        logger.info(f"Combat terminé avec statut: {status}")
        root.after(2000, root.destroy)  # Fermer l'application après 2 secondes
    
    # Créer l'interface de combat
    combat_ui = CombatUI(root, combat_engine, on_combat_end)
    
    # Lancer la boucle principale
    root.mainloop()

if __name__ == "__main__":
    run_combat_demo()
