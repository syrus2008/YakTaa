"""
Module pour la génération des missions
Contient la fonction pour créer des missions et objectifs dans le monde
"""

import uuid
import json
import logging
import random
from typing import List

from database import get_database
from constants import MISSION_TYPES, MISSION_DIFFICULTIES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.Missions")

def generate_missions(db, world_id: str, location_ids: List[str], character_ids: List[str], num_missions: int, random) -> List[str]:
    """
    Génère des missions pour le monde

    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        character_ids: Liste des IDs des personnages
        num_missions: Nombre de missions à générer
        random: Instance de random pour la génération aléatoire

    Returns:
        Liste des IDs des missions générées
    """
    mission_ids = []

    # Obtenir une nouvelle connexion à la base de données
    db = get_database(db.db_path)

    cursor = db.conn.cursor()

    # Types de missions possibles
    mission_types = [
        'infiltration', 'récupération', 'hacking', 'protection', 'livraison',
        'élimination', 'sabotage', 'espionnage', 'escorte', 'investigation'
    ]

    # Niveaux de difficulté
    difficulty_levels = ['facile', 'moyen', 'difficile', 'très difficile', 'extrême']

    # Générer les missions
    for _ in range(num_missions):
        mission_id = str(uuid.uuid4())

        # Sélectionner un type de mission aléatoire
        mission_type = random.choice(mission_types)

        # Générer un titre pour la mission
        title_prefixes = {
            'infiltration': ['Infiltration', 'Accès', 'Pénétration'],
            'récupération': ['Récupération', 'Extraction', 'Sauvetage'],
            'hacking': ['Piratage', 'Intrusion', 'Bypass'],
            'protection': ['Protection', 'Défense', 'Sécurisation'],
            'livraison': ['Livraison', 'Transport', 'Transfert'],
            'élimination': ['Neutralisation', 'Élimination', 'Suppression'],
            'sabotage': ['Sabotage', 'Destruction', 'Dysfonctionnement'],
            'espionnage': ['Espionnage', 'Surveillance', 'Observation'],
            'escorte': ['Escorte', 'Accompagnement', 'Protection'],
            'investigation': ['Enquête', 'Investigation', 'Recherche']
        }

        title_objects = {
            'infiltration': ['du système', 'du bâtiment', 'de la zone sécurisée'],
            'récupération': ['des données', 'du prototype', 'de l\'otage'],
            'hacking': ['de la base de données', 'du réseau', 'du serveur'],
            'protection': ['du VIP', 'des données', 'du convoi'],
            'livraison': ['du colis', 'des informations', 'du prototype'],
            'élimination': ['de la cible', 'du témoin', 'de la menace'],
            'sabotage': ['de l\'infrastructure', 'du système', 'de la production'],
            'espionnage': ['de la réunion', 'des communications', 'des activités'],
            'escorte': ['du VIP', 'du convoi', 'du témoin'],
            'investigation': ['sur la disparition', 'sur le meurtre', 'sur le vol']
        }

        title_prefix = random.choice(title_prefixes[mission_type])
        title_object = random.choice(title_objects[mission_type])

        title = f"{title_prefix} {title_object}"

        # Générer une description pour la mission
        descriptions = []

        if mission_type == 'infiltration':
            descriptions.append("Infiltrez-vous dans un lieu hautement sécurisé pour accomplir un objectif.")
        elif mission_type == 'récupération':
            descriptions.append("Récupérez un objet ou des données importantes et ramenez-les à votre contact.")
        elif mission_type == 'hacking':
            descriptions.append("Piratez un système informatique pour extraire des informations ou modifier des données.")
        elif mission_type == 'protection':
            descriptions.append("Protégez une cible contre des menaces potentielles.")
        elif mission_type == 'livraison':
            descriptions.append("Livrez un colis ou des informations à un destinataire spécifique.")
        elif mission_type == 'élimination':
            descriptions.append("Éliminez une cible spécifique discrètement ou non.")
        elif mission_type == 'sabotage':
            descriptions.append("Sabotez un équipement ou une infrastructure pour perturber les opérations.")
        elif mission_type == 'espionnage':
            descriptions.append("Espionnez une cible pour recueillir des informations sensibles.")
        elif mission_type == 'escorte':
            descriptions.append("Escortez une personne ou un convoi jusqu'à sa destination en toute sécurité.")
        elif mission_type == 'investigation':
            descriptions.append("Enquêtez sur un événement mystérieux pour découvrir la vérité.")

        description = " ".join(descriptions)

        # Sélectionner un personnage aléatoire comme donneur de mission
        giver_id = random.choice(character_ids) if character_ids else None

        # Sélectionner un lieu aléatoire pour la mission
        location_id = random.choice(location_ids) if location_ids else None

        # Générer un niveau de difficulté aléatoire
        difficulty = random.choice(difficulty_levels)

        # Générer des récompenses aléatoires
        rewards = {
            'credits': random.randint(100, 10000),
            'items': random.randint(0, 3),
            'reputation': random.randint(1, 10)
        }

        # Déterminer si c'est une quête principale
        is_main_quest = 1 if random.random() < 0.2 else 0

        # Déterminer si la mission est répétable
        is_repeatable = 1 if random.random() < 0.1 else 0

        # Déterminer si la mission est cachée
        is_hidden = 1 if random.random() < 0.15 else 0

        # Métadonnées supplémentaires
        metadata = {
            'time_limit': random.randint(0, 72) if random.random() < 0.3 else None,  # Limite de temps en heures
            'failure_consequences': random.choice(['none', 'reputation_loss', 'item_loss', 'game_over']) if random.random() < 0.5 else None,
            'alternate_endings': random.randint(1, 3) if random.random() < 0.2 else 1
        }

        # Insérer la mission dans la base de données
        cursor.execute('''
        INSERT INTO missions (id, world_id, title, description, giver_id, location_id,
                           mission_type, difficulty, rewards, prerequisites,
                           is_main_quest, is_repeatable, is_hidden, story_elements, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mission_id, world_id, title, description, giver_id, location_id,
            mission_type, difficulty, json.dumps(rewards), None,
            is_main_quest, is_repeatable, is_hidden, None, json.dumps(metadata)
        ))

        # Générer des objectifs pour la mission
        num_objectives = random.randint(1, 5)

        for i in range(num_objectives):
            objective_id = str(uuid.uuid4())

            # Générer un titre pour l'objectif
            objective_titles = {
                'infiltration': ['Accéder à la zone', 'Trouver une entrée', 'Éviter les gardes'],
                'récupération': ['Localiser la cible', 'Récupérer l\'objet', 'S\'échapper avec l\'objet'],
                'hacking': ['Trouver un point d\'accès', 'Contourner le pare-feu', 'Extraire les données'],
                'protection': ['Éliminer les menaces', 'Sécuriser le périmètre', 'Escorter la cible'],
                'livraison': ['Récupérer le colis', 'Éviter les embuscades', 'Livrer le colis'],
                'élimination': ['Localiser la cible', 'Éliminer la cible', 'Effacer les traces'],
                'sabotage': ['Accéder au système', 'Planter le virus', 'S\'échapper discrètement'],
                'espionnage': ['Observer la cible', 'Enregistrer la conversation', 'Transmettre les informations'],
                'escorte': ['Rencontrer la cible', 'Protéger pendant le trajet', 'Arriver à destination'],
                'investigation': ['Interroger les témoins', 'Recueillir des preuves', 'Identifier le coupable']
            }

            objective_title = objective_titles[mission_type][i % len(objective_titles[mission_type])]

            # Générer une description pour l'objectif
            objective_description = f"Objectif {i+1} de la mission: {objective_title}"

            # Déterminer le type d'objectif
            objective_types = ['goto', 'interact', 'collect', 'hack', 'eliminate', 'protect', 'escape']
            objective_type = random.choice(objective_types)

            # Déterminer si l'objectif est optionnel
            is_optional = 1 if random.random() < 0.2 else 0

            # Insérer l'objectif dans la base de données
            cursor.execute('''
            INSERT INTO objectives (id, mission_id, title, description, objective_type,
                                 target_id, target_count, is_optional, order_index, completion_script, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                objective_id, mission_id, objective_title, objective_description, objective_type,
                None, random.randint(1, 5), is_optional, i, None, None
            ))

        mission_ids.append(mission_id)
        logger.debug(f"Mission générée: {title} (ID: {mission_id})")

    db.conn.commit()
    return mission_ids