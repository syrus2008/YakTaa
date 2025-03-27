"""
Module pour la génération des éléments d'histoire
Contient la fonction pour créer des éléments narratifs dans le monde
"""

import uuid
import json
import logging
import random
from typing import List

from database import get_database
from constants import STORY_ELEMENT_TYPES

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.StoryElements")

def generate_story_elements(db, world_id: str, location_ids: List[str], character_ids: List[str], mission_ids: List[str], num_elements: int, random) -> List[str]:
    """
    Génère des éléments d'histoire pour le monde

    Args:
        db: Base de données
        world_id: ID du monde
        location_ids: Liste des IDs des lieux
        character_ids: Liste des IDs des personnages
        mission_ids: Liste des IDs des missions
        num_elements: Nombre d'éléments à générer
        random: Instance de random pour la génération aléatoire

    Returns:
        Liste des IDs des éléments d'histoire générés
    """
    story_element_ids = []
    
    # Obtenir une nouvelle connexion à la base de données
    db = get_database(db.db_path)
    
    cursor = db.conn.cursor()
    
    # Types d'éléments d'histoire
    element_types = [
        'background', 'event', 'lore', 'character_story', 'location_history',
        'faction_info', 'technology', 'mystery', 'rumor', 'legend'
    ]
    
    # Générer les éléments d'histoire
    for i in range(num_elements):
        element_id = str(uuid.uuid4())
        
        # Sélectionner un type d'élément aléatoire
        element_type = random.choice(element_types)
        
        # Générer un titre pour l'élément d'histoire
        title_prefixes = {
            'background': ['Histoire de', 'Origines de', 'Passé de'],
            'event': ['Incident de', 'Événement de', 'Catastrophe de'],
            'lore': ['Mythes de', 'Légendes de', 'Traditions de'],
            'character_story': ['Histoire de', 'Passé de', 'Secrets de'],
            'location_history': ['Histoire de', 'Fondation de', 'Évolution de'],
            'faction_info': ['Idéologie de', 'Structure de', 'Objectifs de'],
            'technology': ['Développement de', 'Innovation de', 'Avancées en'],
            'mystery': ['Mystère de', 'Énigme de', 'Secret de'],
            'rumor': ['Rumeurs sur', 'On dit que', 'Il paraît que'],
            'legend': ['Légende de', 'Mythe de', 'Conte de']
        }
        
        # Sélectionner des éléments liés aléatoires
        related_location_id = random.choice(location_ids) if location_ids and random.random() < 0.7 else None
        related_character_id = random.choice(character_ids) if character_ids and random.random() < 0.5 else None
        related_mission_id = random.choice(mission_ids) if mission_ids and random.random() < 0.3 else None
        
        # Récupérer les noms des éléments liés pour générer un titre pertinent
        location_name = "un lieu inconnu"
        character_name = "quelqu'un"
        mission_title = "une mission"
        
        if related_location_id:
            cursor.execute("SELECT name FROM locations WHERE id = ?", (related_location_id,))
            result = cursor.fetchone()
            if result:
                location_name = result[0]
        
        if related_character_id:
            cursor.execute("SELECT name FROM characters WHERE id = ?", (related_character_id,))
            result = cursor.fetchone()
            if result:
                character_name = result[0]
        
        if related_mission_id:
            cursor.execute("SELECT title FROM missions WHERE id = ?", (related_mission_id,))
            result = cursor.fetchone()
            if result:
                mission_title = result[0]
        
        # Générer le titre en fonction du type et des éléments liés
        if element_type == 'character_story' and related_character_id:
            title = f"{random.choice(title_prefixes[element_type])} {character_name}"
        elif element_type == 'location_history' and related_location_id:
            title = f"{random.choice(title_prefixes[element_type])} {location_name}"
        elif related_mission_id:
            title = f"{random.choice(title_prefixes[element_type])} {mission_title}"
        elif related_location_id:
            title = f"{random.choice(title_prefixes[element_type])} {location_name}"
        elif related_character_id:
            title = f"{random.choice(title_prefixes[element_type])} {character_name}"
        else:
            # Définir les options en dehors de la f-string pour éviter les problèmes d'échappement
            location_options = ['la ville', 'la région', 'l\'époque', 'la technologie', 'la corporation']
            selected_location = random.choice(location_options)
            title = f"{random.choice(title_prefixes[element_type])} {selected_location}"
        
        # Générer le contenu de l'élément d'histoire
        content_templates = {
            'background': [
                "Il y a longtemps, cette région était connue pour ses ressources naturelles abondantes.",
                "Avant la grande catastrophe, cet endroit était un centre technologique florissant.",
                "Les origines de cette zone remontent à l'époque des premières colonies spatiales."
            ],
            'event': [
                "Un incident majeur s'est produit ici il y a quelques années, changeant à jamais la dynamique locale.",
                "La grande panne de 2077 a paralysé les systèmes pendant des semaines.",
                "L'attaque du réseau central a révélé des vulnérabilités critiques dans l'infrastructure."
            ],
            'lore': [
                "Les anciens racontent que des créatures mystérieuses habitaient autrefois ces lieux.",
                "Selon la tradition locale, celui qui contrôle l'information contrôle le monde.",
                "Les légendes parlent d'un trésor de données caché quelque part dans les profondeurs du réseau."
            ],
            'character_story': [
                "Né dans les bas-fonds, ce personnage a gravi les échelons grâce à son intelligence exceptionnelle.",
                "Ancien agent de sécurité, cette personne a changé de camp après avoir découvert la vérité.",
                "Mystérieux et solitaire, peu de gens connaissent le véritable passé de cet individu."
            ],
            'location_history': [
                "Autrefois un simple avant-poste, cet endroit s'est transformé en centre névralgique.",
                "Construit sur les ruines d'une ancienne mégalopole, ce lieu conserve des secrets enfouis.",
                "Ce quartier a changé de mains de nombreuses fois au cours des guerres corporatives."
            ],
            'faction_info': [
                "Cette organisation opère dans l'ombre, manipulant l'économie mondiale à son avantage.",
                "Fondée par d'anciens militaires, cette faction prône un retour à l'ordre traditionnel.",
                "Collectif de hackers idéalistes, ce groupe lutte pour la liberté de l'information."
            ],
            'technology': [
                "Cette innovation révolutionnaire a changé la façon dont les gens interagissent avec le réseau.",
                "Développée initialement à des fins militaires, cette technologie s'est répandue dans la société civile.",
                "Les implants neuraux de dernière génération permettent une connexion instantanée au cyberespace."
            ],
            'mystery': [
                "Personne ne sait ce qui est arrivé aux habitants originels de cette zone.",
                "Les disparitions mystérieuses continuent d'intriguer les autorités locales.",
                "Le code source original n'a jamais été retrouvé, alimentant de nombreuses théories."
            ],
            'rumor': [
                "On raconte que certains hackers peuvent accéder à des niveaux de réseau dont l'existence est niée.",
                "Des témoins affirment avoir vu des agents gouvernementaux tester des technologies inconnues.",
                "Selon les rumeurs, une IA autonome se cacherait quelque part dans le réseau mondial."
            ],
            'legend': [
                "La légende du Fantôme du Réseau continue de fasciner les jeunes hackers.",
                "L'histoire du Gardien des Codes est transmise de génération en génération.",
                "Le mythe de la Clé Universelle inspire encore aujourd'hui de nombreux technophiles."
            ]
        }
        
        content = random.choice(content_templates[element_type])
        
        # Déterminer si l'élément est révélé dès le début
        is_revealed = 1 if random.random() < 0.6 else 0
        
        # Conditions de révélation pour les éléments cachés
        reveal_condition = None
        if not is_revealed:
            conditions = [
                "complete_mission:{}".format(related_mission_id) if related_mission_id else None,
                "visit_location:{}".format(related_location_id) if related_location_id else None,
                "meet_character:{}".format(related_character_id) if related_character_id else None,
                "player_level:{}".format(random.randint(5, 20)),
                "hacking_skill:{}".format(random.randint(3, 10))
            ]
            reveal_condition = next((c for c in conditions if c is not None), "player_level:5")
        
        # Insérer l'élément d'histoire dans la base de données
        cursor.execute('''
        INSERT INTO story_elements (id, world_id, title, content, element_type,
                                 related_location_id, related_character_id, related_mission_id,
                                 order_index, is_revealed, reveal_condition, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            element_id, world_id, title, content, element_type,
            related_location_id, related_character_id, related_mission_id,
            i, is_revealed, reveal_condition, None
        ))
        
        story_element_ids.append(element_id)
        logger.debug(f"Élément d'histoire généré: {title} (ID: {element_id})")
    
    db.conn.commit()
    return story_element_ids