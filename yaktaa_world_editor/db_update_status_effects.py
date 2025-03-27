#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour la base de données avec les tables d'effets de statut
"""

import os
import logging
import sqlite3
from database import get_database, WorldDatabase

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.DBUpdateStatusEffects")

def update_status_effects_schema():
    """
    Met à jour le schéma de la base de données pour inclure les tables d'effets de statut
    
    Returns:
        bool: True si la mise à jour est réussie, False sinon
    """
    # Chemin explicite vers la base de données de l'application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        logger.error(f"La base de données n'existe pas: {db_path}")
        return False
    
    # Ouvrir la connexion à la base de données
    db = get_database(db_path)
    
    try:
        cursor = db.conn.cursor()
        
        # 1. Table d'effets de statut
        logger.info("Création de la table 'status_effects'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_effects (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            duration INTEGER DEFAULT 3,
            effect_value INTEGER,
            effect_type TEXT NOT NULL,
            is_debuff BOOLEAN DEFAULT 0,
            visual_effect TEXT,
            tick_frequency INTEGER DEFAULT 1,
            stackable BOOLEAN DEFAULT 0,
            max_stacks INTEGER DEFAULT 1,
            icon_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
        )
        """)
        
        # 2. Table d'association entre personnages et effets de statut
        logger.info("Création de la table 'character_status_effects'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS character_status_effects (
            id TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            status_effect_id TEXT NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_remaining INTEGER,
            current_stacks INTEGER DEFAULT 1,
            source_character_id TEXT,
            source_equipment_id TEXT,
            source_ability_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            last_tick TIMESTAMP,
            custom_properties TEXT,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY (status_effect_id) REFERENCES status_effects(id) ON DELETE CASCADE,
            FOREIGN KEY (source_character_id) REFERENCES characters(id) ON DELETE SET NULL,
            FOREIGN KEY (source_equipment_id) REFERENCES equipment(id) ON DELETE SET NULL
        )
        """)
        
        # 3. Index pour améliorer les performances
        logger.info("Création des index pour les tables d'effets de statut")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_world_id ON status_effects(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_type ON status_effects(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_effects_is_debuff ON status_effects(is_debuff)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_status_char_id ON character_status_effects(character_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_status_is_active ON character_status_effects(is_active)")
        
        # Enregistrer les modifications
        db.conn.commit()
        logger.info("Mise à jour du schéma d'effets de statut terminée avec succès")
        
        return True, db
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du schéma d'effets de statut: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False, None

def insert_default_status_effects(world_id=None, db=None):
    """
    Insère des effets de statut par défaut dans la base de données
    
    Args:
        world_id: ID du monde pour lequel créer les effets (optionnel)
                Si None, utilise le monde actif
        db: Objet de connexion à la base de données
                
    Returns:
        bool: True si l'insertion est réussie, False sinon
    """
    if not db:
        # Chemin explicite vers la base de données de l'application
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
        db = get_database(db_path)
    
    try:
        cursor = db.conn.cursor()
        
        # Trouver un monde valide si non spécifié
        if not world_id:
            cursor.execute("SELECT id FROM worlds LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                world_id = result["id"]
            else:
                logger.error("Aucun monde trouvé dans la base de données")
                return False
        
        # Vérifier si des effets de statut existent déjà
        cursor.execute("SELECT COUNT(*) as count FROM status_effects WHERE world_id = ?", (world_id,))
        count = cursor.fetchone()["count"]
        
        if count > 0:
            logger.info(f"{count} effets de statut existent déjà pour ce monde")
            return True
        
        # Liste des effets de statut par défaut
        default_status_effects = [
            # Effets positifs (buffs)
            {
                "id": "buff_regen",
                "name": "Régénération",
                "description": "Restaure progressivement les points de vie",
                "type": "heal",
                "duration": 5,
                "effect_value": 5,
                "effect_type": "heal_over_time",
                "is_debuff": 0,
                "visual_effect": "green_sparkles",
                "tick_frequency": 1
            },
            {
                "id": "buff_focus",
                "name": "Concentration",
                "description": "Augmente la précision des attaques",
                "type": "accuracy",
                "duration": 3,
                "effect_value": 15,
                "effect_type": "accuracy_percent",
                "is_debuff": 0,
                "visual_effect": "blue_glow"
            },
            {
                "id": "buff_shield",
                "name": "Bouclier d'énergie",
                "description": "Absorbe les dégâts entrants",
                "type": "defense",
                "duration": 3,
                "effect_value": 30,
                "effect_type": "damage_absorb",
                "is_debuff": 0,
                "visual_effect": "energy_barrier"
            },
            {
                "id": "buff_berserk",
                "name": "Rage",
                "description": "Augmente les dégâts mais réduit la défense",
                "type": "damage",
                "duration": 3,
                "effect_value": 25,
                "effect_type": "damage_percent",
                "is_debuff": 0,
                "visual_effect": "red_aura"
            },
            {
                "id": "buff_stealth",
                "name": "Camouflage",
                "description": "Réduit les chances d'être détecté",
                "type": "stealth",
                "duration": 5,
                "effect_value": 50,
                "effect_type": "detection_reduce",
                "is_debuff": 0,
                "visual_effect": "transparency"
            },
            
            # Effets négatifs (debuffs)
            {
                "id": "debuff_poison",
                "name": "Poison",
                "description": "Inflige des dégâts au fil du temps",
                "type": "damage",
                "duration": 4,
                "effect_value": 8,
                "effect_type": "damage_over_time",
                "is_debuff": 1,
                "visual_effect": "green_particles",
                "tick_frequency": 1,
                "stackable": 1,
                "max_stacks": 3
            },
            {
                "id": "debuff_bleeding",
                "name": "Saignement",
                "description": "Inflige des dégâts au fil du temps et augmente avec les mouvements",
                "type": "damage",
                "duration": 3,
                "effect_value": 10,
                "effect_type": "damage_over_time",
                "is_debuff": 1,
                "visual_effect": "blood_droplets",
                "tick_frequency": 1,
                "stackable": 1,
                "max_stacks": 5
            },
            {
                "id": "debuff_stun",
                "name": "Étourdissement",
                "description": "Empêche d'agir pendant un certain temps",
                "type": "control",
                "duration": 2,
                "effect_value": 100,
                "effect_type": "action_prevent",
                "is_debuff": 1,
                "visual_effect": "stars_around_head"
            },
            {
                "id": "debuff_weaken",
                "name": "Affaiblissement",
                "description": "Réduit les dégâts infligés",
                "type": "damage",
                "duration": 3,
                "effect_value": -30,
                "effect_type": "damage_percent",
                "is_debuff": 1,
                "visual_effect": "purple_aura"
            },
            {
                "id": "debuff_blind",
                "name": "Aveuglement",
                "description": "Réduit considérablement la précision",
                "type": "accuracy",
                "duration": 2,
                "effect_value": -70,
                "effect_type": "accuracy_percent",
                "is_debuff": 1,
                "visual_effect": "dark_haze"
            },
            {
                "id": "debuff_hack",
                "name": "Piratage",
                "description": "Les attaques subies ont une chance de devenir critiques",
                "type": "vulnerability",
                "duration": 3,
                "effect_value": 30,
                "effect_type": "critical_vulnerability",
                "is_debuff": 1,
                "visual_effect": "code_particles"
            },
            {
                "id": "debuff_burn",
                "name": "Brûlure",
                "description": "Inflige des dégâts au fil du temps et réduit la défense",
                "type": "damage",
                "duration": 3,
                "effect_value": 12,
                "effect_type": "damage_over_time",
                "is_debuff": 1,
                "visual_effect": "fire_particles",
                "tick_frequency": 1
            }
        ]
        
        # Insérer les effets de statut par défaut
        for effect in default_status_effects:
            effect["world_id"] = world_id
            
            placeholders = ", ".join(["?"] * len(effect))
            columns = ", ".join(effect.keys())
            
            cursor.execute(f"""
            INSERT INTO status_effects ({columns})
            VALUES ({placeholders})
            """, tuple(effect.values()))
        
        # Enregistrer les modifications
        db.conn.commit()
        logger.info(f"{len(default_status_effects)} effets de statut par défaut ont été insérés dans la base de données")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des effets de statut par défaut: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False
    finally:
        if db and db.conn:
            db.conn.close()

def main():
    """
    Fonction principale
    """
    logger.info("Début de la mise à jour du schéma d'effets de statut")
    
    # Mettre à jour le schéma
    schema_updated, db = update_status_effects_schema()
    
    if schema_updated:
        # Insérer les données
        logger.info("Insertion des effets de statut par défaut")
        data_inserted = insert_default_status_effects(db=db)
        
        if data_inserted:
            logger.info("Mise à jour des effets de statut terminée avec succès")
            # Fermer la connexion à la fin
            if db and db.conn:
                db.conn.close()
            return True
        else:
            logger.error("Échec de l'insertion des effets de statut par défaut")
            # Fermer la connexion à la fin
            if db and db.conn:
                db.conn.close()
            return False
    else:
        logger.error("Échec de la mise à jour du schéma d'effets de statut")
        # Fermer la connexion à la fin
        if db and db.conn:
            db.conn.close()
        return False

if __name__ == "__main__":
    main()
