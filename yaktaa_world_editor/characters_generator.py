"""
Module pour la génération des personnages
Contient la fonction pour créer des personnages dans le monde
"""

import uuid
import json
import logging
from typing import List
import random

from constants import CHARACTER_PROFESSIONS, FACTION_NAMES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Characters")

def generate_characters(db, world_id: str, location_ids: List[str], num_characters: int, random, 
                     enemy_types=None, hostile_percentage=30, combat_difficulty=3, 
                     ai_behavior="Équilibré", combat_styles=None, 
                     enable_status_effects=True) -> List[str]:
    """
    Génère des personnages pour le monde
    
    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        num_characters: Nombre de personnages à générer
        random: Instance de random pour la génération aléatoire
        enemy_types: Dictionnaire de distribution des types d'ennemis (pourcentages)
        hostile_percentage: Pourcentage de personnages hostiles
        combat_difficulty: Niveau de difficulté des combats (1-5)
        ai_behavior: Comportement AI par défaut
        combat_styles: Liste des styles de combat à inclure
        enable_status_effects: Activer les effets de statut
        
    Returns:
        Liste des IDs des personnages générés
    """
    character_ids = []
    cursor = db.conn.cursor()
    
    # Paramètres par défaut si non spécifiés
    if enemy_types is None:
        enemy_types = {
            "HUMAN": 40, 
            "GUARD": 20, 
            "CYBORG": 15, 
            "DRONE": 10, 
            "ROBOT": 5, 
            "NETRUNNER": 5, 
            "MILITECH": 3, 
            "BEAST": 2
        }
    
    if combat_styles is None:
        combat_styles = ["Équilibré", "Corps à corps", "Distance"]
    
    # Convertir les noms français des styles de combat en anglais pour la BD
    combat_style_map = {
        "Équilibré": "balanced",
        "Corps à corps": "melee",
        "Distance": "ranged",
        "Furtif": "stealth",
        "Support": "support",
        "Tank": "tank"
    }
    
    # Convertir les comportements AI du français vers l'anglais pour la BD
    ai_behavior_map = {
        "Équilibré": "balanced",
        "Agressif": "aggressive",
        "Défensif": "defensive",
        "Tactique": "tactical",
        "Prudent": "cautious",
        "Adaptatif": "adaptive"
    }
    
    available_combat_styles = [combat_style_map.get(style, "balanced") for style in combat_styles]
    default_ai = ai_behavior_map.get(ai_behavior, "balanced")
    
    # Récupérer les informations sur les lieux
    locations_by_id = {}
    for loc_id in location_ids:
        cursor.execute('''
        SELECT name, security_level, is_virtual, is_special, is_dangerous, tags
        FROM locations WHERE id = ?
        ''', (loc_id,))
        
        loc_data = cursor.fetchone()
        if loc_data:
            locations_by_id[loc_id] = loc_data
    
    # Générer les personnages
    for _ in range(num_characters):
        character_id = str(uuid.uuid4())
        
        # Sélectionner un lieu pour le personnage
        location_id = random.choice(location_ids)
        location_data = locations_by_id.get(location_id, {})
        
        # Générer un nom
        gender = random.choice(["M", "F"])
        
        if gender == "M":
            first_names = ["Adam", "Alex", "Benjamin", "Chen", "David", "Ethan", "Felix", "Gabriel", 
                          "Hiro", "Ian", "Jack", "Kenji", "Liam", "Miguel", "Noah", "Omar", 
                          "Paul", "Quentin", "Ryan", "Sanjay", "Thomas", "Umar", "Victor", "Wei", 
                          "Xavier", "Yuri", "Zack"]
            name = f"{random.choice(first_names)} {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'])}"
        else:
            first_names = ["Alice", "Bianca", "Claire", "Diana", "Emma", "Fiona", "Grace", "Hannah", 
                          "Iris", "Julia", "Kate", "Lily", "Maria", "Nina", "Olivia", "Penny", 
                          "Quinn", "Rose", "Sophia", "Tara", "Uma", "Victoria", "Wendy", "Xena", 
                          "Yasmine", "Zoe"]
            name = f"{random.choice(first_names)} {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'])}"
        
        # Sélectionner une profession
        profession = random.choice(CHARACTER_PROFESSIONS)
        
        # Déterminer la faction
        faction = random.choice(FACTION_NAMES)
        
        # Niveau d'importance (1-5)
        importance = random.randint(1, 5)
        
        # Niveau de hacking (0-10)
        if profession in ["Hacker", "Security Specialist", "Programmer", "Engineer"]:
            hacking_level = random.randint(5, 10)
        elif profession in ["Corporate Executive", "Government Agent", "Police Officer"]:
            hacking_level = random.randint(2, 5)
        else:
            hacking_level = random.randint(0, 3)
        
        # Niveau de combat (0-10) - Ajusté en fonction de la difficulté
        if profession in ["Mercenary", "Soldier", "Police Officer", "Assassin"]:
            combat_level = random.randint(5, 10) + (combat_difficulty - 3)
        elif profession in ["Security Specialist", "Smuggler", "Fixer"]:
            combat_level = random.randint(3, 7) + (combat_difficulty - 3)
        else:
            combat_level = random.randint(0, 3) + (combat_difficulty - 3)
        
        # Limiter le niveau de combat entre 0 et 10
        combat_level = max(0, min(10, combat_level))
        
        # Niveau de charisme (0-10)
        if profession in ["Fixer", "Corporate Executive", "Information Broker", "Journalist"]:
            charisma = random.randint(5, 10)
        else:
            charisma = random.randint(1, 8)
        
        # Niveau de richesse (0-10)
        if profession in ["Corporate Executive", "Information Broker", "Merchant"]:
            wealth = random.randint(5, 10)
        else:
            wealth = random.randint(0, 6)
            
        # Attributs spécifiques de combat
        
        # Déterminer le type d'ennemi en utilisant la distribution donnée
        enemy_type_choices = list(enemy_types.keys())
        enemy_type_weights = list(enemy_types.values())
        
        # S'assurer que le total des poids est 100
        total_weight = sum(enemy_type_weights)
        if total_weight > 0:
            enemy_type_weights = [w * 100 / total_weight for w in enemy_type_weights]
        else:
            # En cas de distribution incorrecte, utiliser une distribution par défaut
            enemy_type_weights = [40, 20, 15, 10, 5, 5, 3, 2]
        
        # Sélection pondérée du type d'ennemi
        selected_enemy_type = random.choices(enemy_type_choices, weights=enemy_type_weights, k=1)[0]
        
        # Ajuster le type en fonction de la profession (mais garder la distribution globale)
        if profession in ["Security Specialist", "Police Officer", "Government Agent"]:
            if random.random() < 0.7:  # 70% de chance d'être un garde quand c'est approprié
                enemy_type = "GUARD"
            else:
                enemy_type = selected_enemy_type
        elif profession in ["Mercenary", "Soldier", "Assassin"]:
            if random.random() < 0.7:
                enemy_type = "MILITECH"
            else:
                enemy_type = selected_enemy_type
        elif profession in ["Hacker", "Programmer", "Engineer"]:
            if random.random() < 0.7:
                enemy_type = "NETRUNNER"
            else:
                enemy_type = selected_enemy_type
        elif profession in ["Cybermodded", "Tech Specialist"]:
            if random.random() < 0.7:
                enemy_type = "CYBORG"
            else:
                enemy_type = selected_enemy_type
        else:
            enemy_type = selected_enemy_type
            
        # Santé (50-200) - Ajustée en fonction de la difficulté
        health_base = 50 + (combat_level * 10)
        health_multiplier = 0.8 + (combat_difficulty * 0.1)  # De 0.9 à 1.3 selon la difficulté
        health = int(health_base * health_multiplier) + random.randint(0, 50)
        
        # Dégâts (5-20) - Ajustés en fonction de la difficulté
        damage_base = 5 + (combat_level * 1)
        damage_multiplier = 0.8 + (combat_difficulty * 0.1)  # De 0.9 à 1.3 selon la difficulté
        damage = int(damage_base * damage_multiplier) + random.randint(0, 5)
        
        # Précision (0.5-0.9) - Ajustée en fonction de la difficulté
        accuracy_base = 0.5 + (combat_level * 0.03)
        accuracy_bonus = (combat_difficulty - 3) * 0.02  # De -0.04 à 0.04 selon la difficulté
        accuracy = accuracy_base + accuracy_bonus + random.uniform(0, 0.1)
        accuracy = min(0.9, max(0.5, accuracy))  # Limiter entre 0.5 et 0.9
        
        # Initiative (3-10) - Ajustée en fonction de la difficulté
        initiative_base = 3 + (combat_level // 2)
        initiative_bonus = (combat_difficulty - 3)  # De -2 à 2 selon la difficulté
        initiative = initiative_base + initiative_bonus + random.randint(0, 3)
        initiative = max(3, min(10, initiative))  # Limiter entre 3 et 10
        
        # Niveau d'hostilité (0-100) - Basé sur le paramètre hostile_percentage
        is_hostile = random.random() < (hostile_percentage / 100)
        if is_hostile:
            hostility = random.randint(60, 100)
        else:
            hostility = random.randint(0, 30)
            
        # Résistances
        resistance_physical = 0
        resistance_energy = 0
        resistance_emp = 0
        resistance_biohazard = 0
        resistance_cyber = 0
        resistance_viral = 0
        resistance_nanite = 0
        
        # Ajuster les résistances en fonction du type d'ennemi et de la difficulté
        difficulty_modifier = (combat_difficulty - 3) * 5  # De -10 à +10
        
        if enemy_type == "HUMAN":
            resistance_physical = random.randint(0, 10) + difficulty_modifier
            resistance_cyber = random.randint(5, 15) + difficulty_modifier
        elif enemy_type == "GUARD":
            resistance_physical = random.randint(10, 30) + difficulty_modifier
            resistance_energy = random.randint(5, 15) + difficulty_modifier
            resistance_emp = random.randint(0, 10) + difficulty_modifier
        elif enemy_type == "MILITECH":
            resistance_physical = random.randint(20, 50) + difficulty_modifier
            resistance_energy = random.randint(15, 40) + difficulty_modifier
            resistance_emp = random.randint(10, 20) + difficulty_modifier
        elif enemy_type == "NETRUNNER":
            resistance_physical = random.randint(0, 10) + difficulty_modifier
            resistance_cyber = random.randint(30, 60) + difficulty_modifier
            resistance_emp = random.randint(10, 30) + difficulty_modifier
        elif enemy_type == "CYBORG":
            resistance_physical = random.randint(15, 40) + difficulty_modifier
            resistance_energy = random.randint(10, 30) + difficulty_modifier
            resistance_cyber = random.randint(20, 40) + difficulty_modifier
            resistance_emp = max(0, 0 + difficulty_modifier)  # Vulnérable aux EMP, mais peut avoir une résistance en difficulté élevée
        elif enemy_type == "DRONE":
            resistance_physical = random.randint(10, 25) + difficulty_modifier
            resistance_energy = random.randint(5, 20) + difficulty_modifier
            resistance_cyber = random.randint(15, 35) + difficulty_modifier
            resistance_emp = max(0, 0 + difficulty_modifier)  # Vulnérable aux EMP
        elif enemy_type == "ROBOT":
            resistance_physical = random.randint(30, 60) + difficulty_modifier
            resistance_energy = random.randint(20, 45) + difficulty_modifier
            resistance_cyber = random.randint(10, 30) + difficulty_modifier
            resistance_emp = max(0, 0 + difficulty_modifier)  # Vulnérable aux EMP
        elif enemy_type == "BEAST":
            resistance_physical = random.randint(20, 40) + difficulty_modifier
            resistance_biohazard = random.randint(30, 70) + difficulty_modifier
            resistance_cyber = random.randint(0, 10) + difficulty_modifier
            
        # S'assurer que les résistances sont entre 0 et 100
        resistance_physical = max(0, min(100, resistance_physical))
        resistance_energy = max(0, min(100, resistance_energy))
        resistance_emp = max(0, min(100, resistance_emp))
        resistance_biohazard = max(0, min(100, resistance_biohazard))
        resistance_cyber = max(0, min(100, resistance_cyber))
        resistance_viral = max(0, min(100, resistance_viral))
        resistance_nanite = max(0, min(100, resistance_nanite))
            
        # Comportement IA et style de combat
        # Utiliser le comportement par défaut ou le choisir en fonction du type et de l'hostilité
        if is_hostile and default_ai == "balanced":
            ai_behaviors = ["offensive", "aggressive", "tactical"]
            weights = [0.4, 0.4, 0.2]
            selected_ai_behavior = random.choices(ai_behaviors, weights=weights, k=1)[0]
        elif not is_hostile and default_ai == "balanced":
            ai_behaviors = ["defensive", "cautious", "balanced"]
            weights = [0.4, 0.4, 0.2]
            selected_ai_behavior = random.choices(ai_behaviors, weights=weights, k=1)[0]
        else:
            selected_ai_behavior = default_ai
        
        # Style de combat selon le type et les styles disponibles
        enemy_type_styles = {
            "NETRUNNER": ["ranged", "stealth", "support"],
            "MILITECH": ["tank", "ranged", "melee"],
            "GUARD": ["balanced", "ranged", "tank"],
            "CYBORG": ["melee", "tank", "balanced"],
            "DRONE": ["ranged", "balanced"],
            "ROBOT": ["tank", "ranged"],
            "BEAST": ["melee", "tank"],
            "HUMAN": ["balanced", "melee", "ranged", "stealth", "support"]
        }
        
        # Filtrer les styles disponibles en fonction des styles activés
        available_type_styles = [style for style in enemy_type_styles.get(enemy_type, ["balanced"]) 
                                if style in available_combat_styles]
        
        # Si aucun style n'est disponible après filtrage, utiliser "balanced"
        if not available_type_styles:
            available_type_styles = ["balanced"]
            
        combat_style = random.choice(available_type_styles)
        
        # Capacités spéciales (vide pour la plupart des personnages)
        special_abilities = ""
        
        # Augmenter les chances de capacités spéciales en fonction de la difficulté
        special_ability_chance = 0.1 + (combat_difficulty * 0.05)  # De 0.15 à 0.35
        
        if random.random() < special_ability_chance and enable_status_effects:
            abilities = ["regeneration", "emp_burst", "stealth", "turret_hack", "adrenaline", "combat_drugs"]
            
            # Ajouter des capacités liées aux effets de statut si activés
            if enable_status_effects:
                abilities.extend(["poison_attack", "fire_attack", "shock_attack", "freeze_attack", "nanite_injection"])
                
            special_abilities = random.choice(abilities)
            
            # Chance d'avoir une seconde capacité augmentée avec la difficulté
            second_ability_chance = 0.05 + (combat_difficulty * 0.02)  # De 0.07 à 0.15
            if random.random() < second_ability_chance:
                second_ability = random.choice([a for a in abilities if a != special_abilities])
                special_abilities += f",{second_ability}"
                
        # Description par défaut (peut être remplacée par une génération IA plus tard)
        descriptions = []
        
        # Description de base
        descriptions.append(f"{name} est un(e) {profession.lower()} travaillant pour {faction}.")
        
        # Description basée sur les compétences
        if hacking_level >= 8:
            descriptions.append("Ses compétences en hacking sont légendaires.")
        elif hacking_level >= 5:
            descriptions.append("Possède de solides compétences en informatique et en hacking.")
        
        if combat_level >= 8:
            descriptions.append("C'est un combattant redoutable que peu osent défier.")
        elif combat_level >= 5:
            descriptions.append("Sait se défendre et n'hésite pas à utiliser la force si nécessaire.")
        
        if charisma >= 8:
            descriptions.append("Son charisme naturel lui ouvre de nombreuses portes.")
        
        if wealth >= 8:
            descriptions.append("Sa fortune considérable lui permet d'accéder aux cercles les plus exclusifs.")
        elif wealth <= 2:
            descriptions.append("Vit dans la précarité, cherchant constamment des moyens de survivre.")
        
        # Description basée sur l'importance
        if importance >= 4:
            descriptions.append("C'est une figure importante dans le monde de YakTaa.")
        
        # Description basée sur le lieu
        if location_data:
            descriptions.append(f"On peut généralement le trouver à {location_data['name']}.")
        
        description = " ".join(descriptions)
        
        # Métadonnées (pour stocker des informations supplémentaires)
        metadata = {
            "background": random.choice([
                "Ancien militaire reconverti dans le civil.",
                "A grandi dans les bas-fonds, s'est fait un nom par la force.",
                "Diplômé d'une prestigieuse université, a choisi une voie non conventionnelle.",
                "Ancien employé corporatif qui a changé de camp après avoir découvert la vérité.",
                "Autodidacte qui a appris sur le tas dans les rues de la ville.",
                "Issu d'une famille influente mais a renié son héritage."
            ]),
            "motivations": random.choice([
                "Recherche la richesse à tout prix.",
                "Veut changer le système de l'intérieur.",
                "Cherche à se venger d'une corporation.",
                "Protège les plus faibles contre les puissants.",
                "Poursuit le pouvoir et l'influence.",
                "Cherche simplement à survivre dans ce monde hostile."
            ]),
            "secrets": random.choice([
                "Cache une identité secrète.",
                "Travaille secrètement pour une faction rivale.",
                "Possède des informations compromettantes sur des personnalités importantes.",
                "A participé à un événement tragique dont personne ne connaît son implication.",
                "Est atteint d'une maladie rare et cherche désespérément un remède.",
                "Est en réalité un agent infiltré."
            ])
        }
        
        # Types additionnels
        is_quest_giver = 1 if random.random() < 0.2 else 0  # 20% de chance d'être donneur de quête
        is_vendor = 1 if random.random() < 0.15 else 0      # 15% de chance d'être marchand
        
        # Insérer le personnage dans la base de données
        cursor.execute("""
        INSERT INTO characters (
            id, world_id, name, description, location_id, faction, profession,
            gender, importance, hacking_level, combat_level, charisma, wealth,
            is_quest_giver, is_vendor, is_hostile,
            enemy_type, health, damage, accuracy, initiative, hostility,
            resistance_physical, resistance_energy, resistance_emp, resistance_biohazard,
            resistance_cyber, resistance_viral, resistance_nanite,
            ai_behavior, combat_style, special_abilities, equipment_slots
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, world_id, name, description, location_id, faction, profession,
            gender, importance, hacking_level, combat_level, charisma, wealth,
            is_quest_giver, is_vendor, int(is_hostile),
            enemy_type, health, damage, accuracy, initiative, hostility,
            resistance_physical, resistance_energy, resistance_emp, resistance_biohazard,
            resistance_cyber, resistance_viral, resistance_nanite,
            selected_ai_behavior, combat_style, special_abilities, "weapon,armor,accessory"
        ))
        
        character_ids.append(character_id)
        logger.debug(f"Personnage généré: {name} (ID: {character_id})")
    
    db.conn.commit()
    return character_ids