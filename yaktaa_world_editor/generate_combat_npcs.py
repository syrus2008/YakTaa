#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer des PNJ avec des caractéristiques de combat avancées
"""

import logging
import sys
import random
import uuid
import argparse

from database import get_database, WorldDatabase

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.CombatNPCGenerator")

def generate_combat_npcs(db_path=None, world_id=None, num_npcs=10):
    """
    Génère des PNJ avec des caractéristiques de combat avancées
    
    Args:
        db_path: Chemin de la base de données (optionnel)
        world_id: ID du monde pour lequel générer les PNJ (optionnel)
        num_npcs: Nombre de PNJ à générer
        
    Returns:
        Liste d'IDs des PNJ générés
    """
    db = get_database(db_path)
    
    try:
        cursor = db.conn.cursor()
        
        # Trouver un monde si non spécifié
        if not world_id:
            cursor.execute("SELECT id FROM worlds WHERE is_active = 1 LIMIT 1")
            active_world = cursor.fetchone()
            
            if active_world:
                world_id = active_world["id"]
            else:
                cursor.execute("SELECT id FROM worlds LIMIT 1")
                world = cursor.fetchone()
                
                if world:
                    world_id = world["id"]
                else:
                    logger.error("Aucun monde trouvé dans la base de données")
                    return []
        
        # Récupérer les informations sur le monde
        cursor.execute("SELECT name FROM worlds WHERE id = ?", (world_id,))
        world_name = cursor.fetchone()["name"]
        logger.info(f"Génération de {num_npcs} PNJ de combat pour le monde: {world_name} ({world_id})")
        
        # Récupérer les lieux disponibles pour y placer les PNJ
        cursor.execute("""
        SELECT id, name, security_level 
        FROM locations 
        WHERE world_id = ? AND is_virtual = 0
        """, (world_id,))
        
        locations = cursor.fetchall()
        if not locations:
            logger.error(f"Aucun lieu trouvé pour le monde {world_id}")
            return []
            
        # Générer les PNJ
        generated_npcs = []
        
        # Types d'ennemis possibles
        enemy_types = ["HUMAN", "GUARD", "CYBORG", "DRONE", "ROBOT", "NETRUNNER", "MILITECH", "BEAST"]
        
        # Noms de base pour les personnages
        first_names_male = ["Alex", "Blake", "Chen", "Dante", "Elijah", "Finn", "Gabriel", "Hiro", 
                       "Ivan", "Jackson", "Kai", "Leon", "Marcus", "Neo", "Omar", "Pavel", 
                       "Quinn", "Ryder", "Silas", "Takeshi", "Ulysses", "Viktor", "Wren", 
                       "Xander", "Yusef", "Zephyr"]
                       
        first_names_female = ["Aria", "Bianca", "Cira", "Daria", "Echo", "Faye", "Gemma", "Harper", 
                         "Ivy", "Jade", "Kira", "Luna", "Maya", "Nova", "Orion", "Piper", 
                         "Quinn", "Raven", "Seren", "Trinity", "Uma", "Violet", "Winter", 
                         "Xena", "Yara", "Zoe"]
                         
        last_names = ["Anderson", "Blackwood", "Chen", "Decker", "Evans", "Flynn", "Garcia", 
                      "Hayashi", "Ivanov", "Jackson", "Kim", "Lynch", "Martinez", "Nakamura", 
                      "O'Malley", "Petrov", "Quinn", "Reyes", "Suzuki", "Tran", "Udinov", 
                      "Volkov", "Wong", "Xiong", "Yamamoto", "Zhang"]
        
        # Professions pouvant être hostiles
        hostile_professions = ["Mercenary", "Gang Member", "Smuggler", "Assassin", "Cyber-Criminal", "Rogue AI"]
        
        # Professions neutres ou amicales
        neutral_professions = ["Tech Specialist", "Information Broker", "Corporate Employee", "Street Vendor", 
                               "Medical Technician", "Engineer", "Netrunner", "Bartender", "Fixer"]
        
        # Factions
        factions = ["Corporate", "Street Gang", "Government", "Independent", "Criminal Syndicate", 
                    "Resistance", "Mercenary", "AI Collective"]
        
        for i in range(num_npcs):
            # Choisir les caractéristiques de base du PNJ
            npc_id = str(uuid.uuid4())
            is_hostile = random.choice([True, False])
            
            # Ajuster la probabilité d'être hostile en fonction du niveau de sécurité du lieu
            if is_hostile:
                # Placer les PNJ hostiles de préférence dans les lieux avec sécurité faible ou moyenne
                suitable_locations = [loc for loc in locations if loc["security_level"] <= 3]
                if not suitable_locations:
                    suitable_locations = locations
            else:
                # Les PNJ non-hostiles peuvent être n'importe où
                suitable_locations = locations
                
            location = random.choice(suitable_locations)
            
            # Genre et nom
            gender = random.choice(["M", "F"])
            if gender == "M":
                first_name = random.choice(first_names_male)
            else:
                first_name = random.choice(first_names_female)
                
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Profession et faction
            if is_hostile:
                profession = random.choice(hostile_professions)
                faction = random.choice(["Street Gang", "Criminal Syndicate", "Mercenary", "Independent"])
            else:
                profession = random.choice(neutral_professions)
                faction = random.choice(factions)
            
            # Niveau de base (1-10)
            base_level = random.randint(1, 10)
            
            # Type d'ennemi en fonction de la profession
            if profession in ["Mercenary", "Assassin"]:
                enemy_type = random.choice(["MILITECH", "CYBORG"])
            elif profession in ["Cyber-Criminal", "Netrunner"]:
                enemy_type = "NETRUNNER"
            elif profession == "Rogue AI":
                enemy_type = random.choice(["DRONE", "ROBOT"])
            elif profession == "Gang Member":
                enemy_type = random.choice(["HUMAN", "CYBORG"])
            else:
                enemy_type = random.choice(enemy_types)
            
            # Caractéristiques de combat en fonction du type
            if enemy_type == "HUMAN":
                health = 50 + (base_level * 5) + random.randint(0, 20)
                damage = 5 + (base_level // 2) + random.randint(0, 3)
                accuracy = 0.6 + (base_level * 0.02) + random.uniform(0, 0.1)
                initiative = 5 + (base_level // 3) + random.randint(0, 2)
                resistances = {
                    "physical": random.randint(0, 15),
                    "energy": random.randint(0, 10),
                    "emp": random.randint(0, 5),
                    "biohazard": random.randint(0, 15),
                    "cyber": random.randint(10, 25),
                    "viral": random.randint(0, 10),
                    "nanite": random.randint(0, 5)
                }
            elif enemy_type == "GUARD":
                health = 70 + (base_level * 7) + random.randint(0, 30)
                damage = 7 + (base_level // 2) + random.randint(0, 4)
                accuracy = 0.7 + (base_level * 0.02) + random.uniform(0, 0.1)
                initiative = 6 + (base_level // 3) + random.randint(0, 2)
                resistances = {
                    "physical": random.randint(15, 30),
                    "energy": random.randint(10, 20),
                    "emp": random.randint(5, 15),
                    "biohazard": random.randint(5, 15),
                    "cyber": random.randint(15, 30),
                    "viral": random.randint(5, 15),
                    "nanite": random.randint(5, 15)
                }
            elif enemy_type == "CYBORG":
                health = 90 + (base_level * 8) + random.randint(0, 40)
                damage = 9 + (base_level // 2) + random.randint(0, 5)
                accuracy = 0.75 + (base_level * 0.02) + random.uniform(0, 0.1)
                initiative = 7 + (base_level // 3) + random.randint(0, 3)
                resistances = {
                    "physical": random.randint(20, 40),
                    "energy": random.randint(15, 30),
                    "emp": random.randint(0, 10),  # Vulnérable aux EMP
                    "biohazard": random.randint(20, 40),
                    "cyber": random.randint(10, 25),
                    "viral": random.randint(20, 35),
                    "nanite": random.randint(10, 25)
                }
            elif enemy_type == "DRONE":
                health = 60 + (base_level * 6) + random.randint(0, 25)
                damage = 8 + (base_level // 2) + random.randint(0, 4)
                accuracy = 0.8 + (base_level * 0.01) + random.uniform(0, 0.1)
                initiative = 9 + (base_level // 3) + random.randint(0, 3)
                resistances = {
                    "physical": random.randint(15, 30),
                    "energy": random.randint(10, 25),
                    "emp": random.randint(0, 5),  # Très vulnérable aux EMP
                    "biohazard": random.randint(70, 80),  # Immune aux biohazards
                    "cyber": random.randint(15, 30),
                    "viral": random.randint(30, 50),
                    "nanite": random.randint(20, 35)
                }
            elif enemy_type == "ROBOT":
                health = 120 + (base_level * 10) + random.randint(0, 50)
                damage = 12 + (base_level // 2) + random.randint(0, 6)
                accuracy = 0.85 + (base_level * 0.01) + random.uniform(0, 0.05)
                initiative = 5 + (base_level // 4) + random.randint(0, 2)
                resistances = {
                    "physical": random.randint(30, 50),
                    "energy": random.randint(20, 40),
                    "emp": random.randint(0, 10),  # Très vulnérable aux EMP
                    "biohazard": random.randint(70, 80),  # Immune aux biohazards
                    "cyber": random.randint(20, 40),
                    "viral": random.randint(40, 60),
                    "nanite": random.randint(30, 50)
                }
            elif enemy_type == "NETRUNNER":
                health = 40 + (base_level * 4) + random.randint(0, 20)
                damage = 6 + (base_level // 2) + random.randint(0, 3)
                accuracy = 0.7 + (base_level * 0.02) + random.uniform(0, 0.1)
                initiative = 8 + (base_level // 3) + random.randint(0, 3)
                resistances = {
                    "physical": random.randint(0, 15),
                    "energy": random.randint(5, 20),
                    "emp": random.randint(15, 30),
                    "biohazard": random.randint(5, 15),
                    "cyber": random.randint(40, 60),  # Forte résistance cyber
                    "viral": random.randint(30, 50),
                    "nanite": random.randint(20, 35)
                }
            elif enemy_type == "MILITECH":
                health = 100 + (base_level * 9) + random.randint(0, 40)
                damage = 10 + (base_level // 2) + random.randint(0, 5)
                accuracy = 0.8 + (base_level * 0.015) + random.uniform(0, 0.1)
                initiative = 7 + (base_level // 3) + random.randint(0, 3)
                resistances = {
                    "physical": random.randint(30, 50),
                    "energy": random.randint(25, 45),
                    "emp": random.randint(15, 30),
                    "biohazard": random.randint(20, 40),
                    "cyber": random.randint(20, 40),
                    "viral": random.randint(15, 35),
                    "nanite": random.randint(15, 30)
                }
            elif enemy_type == "BEAST":
                health = 150 + (base_level * 12) + random.randint(0, 50)
                damage = 15 + (base_level // 2) + random.randint(0, 7)
                accuracy = 0.6 + (base_level * 0.015) + random.uniform(0, 0.1)
                initiative = 6 + (base_level // 3) + random.randint(0, 3)
                resistances = {
                    "physical": random.randint(25, 45),
                    "energy": random.randint(15, 35),
                    "emp": random.randint(50, 70),  # Très résistant aux EMP
                    "biohazard": random.randint(40, 60),
                    "cyber": random.randint(0, 15),  # Vulnérable aux attaques cyber
                    "viral": random.randint(30, 50),
                    "nanite": random.randint(30, 50)
                }
            else:  # Valeurs par défaut
                health = 50 + (base_level * 5)
                damage = 5 + (base_level // 2)
                accuracy = 0.7 + (base_level * 0.02)
                initiative = 5 + (base_level // 3)
                resistances = {
                    "physical": random.randint(0, 20),
                    "energy": random.randint(0, 20),
                    "emp": random.randint(0, 20),
                    "biohazard": random.randint(0, 20),
                    "cyber": random.randint(0, 20),
                    "viral": random.randint(0, 20),
                    "nanite": random.randint(0, 20)
                }
            
            # Niveau d'hostilité (0-100)
            if is_hostile:
                hostility = random.randint(60, 100)
            else:
                hostility = random.randint(0, 30)
            
            # Comportement IA
            if is_hostile:
                ai_behavior = random.choice(["offensive", "aggressive", "tactical"])
            else:
                ai_behavior = random.choice(["defensive", "cautious", "balanced"])
            
            # Style de combat
            if enemy_type == "NETRUNNER":
                combat_style = random.choice(["ranged", "stealth", "support"])
            elif enemy_type == "MILITECH" or enemy_type == "ROBOT":
                combat_style = random.choice(["tank", "ranged", "melee"])
            else:
                combat_style = random.choice(["balanced", "melee", "ranged", "stealth", "support", "tank"])
            
            # Capacités spéciales
            abilities = ["regeneration", "emp_burst", "stealth", "turret_hack", "adrenaline", 
                         "combat_drugs", "shield", "berserk", "teleport", "duplicate"]
            
            special_abilities = ""
            if random.random() < 0.3:  # 30% de chance d'avoir une capacité spéciale
                special_abilities = random.choice(abilities)
                
                # 10% de chance d'avoir une seconde capacité
                if random.random() < 0.1:
                    second_ability = random.choice([a for a in abilities if a != special_abilities])
                    special_abilities += f",{second_ability}"
            
            # Description
            descriptions = [
                f"Un {profession.lower()} {faction.lower()} équipé pour le combat.",
                f"Ce personnage est connu pour ses compétences en combat de type {combat_style}.",
                f"Un membre hostile de la faction {faction}." if is_hostile else f"Un membre de la faction {faction}.",
                f"Un {profession.lower()} avec des augmentations {enemy_type.lower()}.",
                f"Un combattant de niveau {base_level} spécialisé dans le style {combat_style}."
            ]
            description = random.choice(descriptions)
            
            # Déterminer s'il est donneur de quête ou marchand
            is_quest_giver = 1 if (not is_hostile and random.random() < 0.2) else 0  # 20% pour non-hostiles
            is_vendor = 1 if (not is_hostile and random.random() < 0.15) else 0      # 15% pour non-hostiles
            
            # Insérer dans la base de données
            cursor.execute("""
            INSERT INTO characters (
                id, world_id, name, description, location_id, faction, profession,
                gender, importance, hacking_level, combat_level, charisma, wealth,
                is_quest_giver, is_vendor, is_hostile,
                enemy_type, health, damage, accuracy, initiative, hostility,
                resistance_physical, resistance_energy, resistance_emp, resistance_biohazard,
                resistance_cyber, resistance_viral, resistance_nanite,
                ai_behavior, combat_style, special_abilities
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                npc_id, world_id, name, description, location["id"], faction, profession,
                gender, random.randint(1, 5), random.randint(0, 10), base_level, random.randint(1, 10), random.randint(1, 10),
                is_quest_giver, is_vendor, 1 if is_hostile else 0,
                enemy_type, health, damage, accuracy, initiative, hostility,
                resistances["physical"], resistances["energy"], resistances["emp"], resistances["biohazard"],
                resistances["cyber"], resistances["viral"], resistances["nanite"],
                ai_behavior, combat_style, special_abilities
            ))
            
            generated_npcs.append(npc_id)
            
            logger.info(f"PNJ généré: {name} ({enemy_type}, {'Hostile' if is_hostile else 'Non-hostile'})")
            logger.info(f"  - Localisation: {location['name']}")
            logger.info(f"  - Santé: {health}, Dégâts: {damage}, Précision: {accuracy:.2f}, Initiative: {initiative}")
            logger.info(f"  - Style: {combat_style}, IA: {ai_behavior}")
            if special_abilities:
                logger.info(f"  - Capacités spéciales: {special_abilities}")
            logger.info("")
        
        # Sauvegarder les modifications
        db.conn.commit()
        logger.info(f"{len(generated_npcs)} PNJ de combat générés avec succès pour le monde {world_name}")
        
        return generated_npcs
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des PNJ de combat: {e}")
        db.conn.rollback()
        return []
    finally:
        db.conn.close()

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Génération de PNJ de combat pour YakTaa")
    parser.add_argument("--db-path", help="Chemin vers la base de données")
    parser.add_argument("--world-id", help="ID du monde pour lequel générer les PNJ")
    parser.add_argument("--num-npcs", type=int, default=10, help="Nombre de PNJ à générer (défaut: 10)")
    
    args = parser.parse_args()
    
    generate_combat_npcs(args.db_path, args.world_id, args.num_npcs)

if __name__ == "__main__":
    main()
