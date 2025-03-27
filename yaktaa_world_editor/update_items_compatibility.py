#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migration pour mettre à jour la base de données et assurer
la compatibilité entre l'éditeur de monde et le jeu.
"""

import os
import sys
import json
import logging
import sqlite3
import random
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ItemsCompatibilityUpdate")

# Chemin vers la base de données
DB_PATH = Path("worlds.db")

def connect_to_db():
    """
    Se connecte à la base de données.
    
    Returns:
        Tuple (conn, cursor) si connexion réussie, sinon (None, None)
    """
    try:
        logger.info(f"Connexion à la base de données: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        return None, None

def update_table_schema(conn, cursor):
    """
    Met à jour le schéma de la base de données pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        True si les mises à jour ont réussi, False sinon
    """
    try:
        logger.info("Vérification du schéma des tables...")
        
        # 1. Vérifier si la colonne stats existe dans clothing_items
        cursor.execute("PRAGMA table_info(clothing_items)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "stats" not in columns:
            logger.info("Ajout de la colonne 'stats' à la table clothing_items")
            cursor.execute("ALTER TABLE clothing_items ADD COLUMN stats TEXT")
        else:
            logger.info("La colonne 'stats' existe déjà dans la table clothing_items")
        
        # 2. Vérifier si la colonne slots existe dans clothing_items
        if "slots" not in columns:
            logger.info("Ajout de la colonne 'slots' à la table clothing_items")
            cursor.execute("ALTER TABLE clothing_items ADD COLUMN slots TEXT NOT NULL DEFAULT 'BODY'")
        else:
            logger.info("La colonne 'slots' existe déjà dans la table clothing_items")
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour du schéma: {e}")
        conn.rollback()
        return False

def update_weapon_metadata(conn, cursor):
    """
    Met à jour les métadonnées des armes pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées des armes...")
        
        # Récupérer toutes les armes
        cursor.execute("""
            SELECT id, name, weapon_type, damage, damage_type, accuracy, range, metadata
            FROM weapon_items
        """)
        weapons = cursor.fetchall()
        
        updated_count = 0
        for weapon_id, name, weapon_type, damage, damage_type, accuracy, range_val, metadata_str in weapons:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "damage" not in metadata:
                    metadata["damage"] = damage or random.randint(5, 20)
                if "damage_type" not in metadata:
                    metadata["damage_type"] = damage_type or "physical"
                if "accuracy" not in metadata:
                    metadata["accuracy"] = accuracy or random.uniform(0.6, 0.9)
                if "range" not in metadata:
                    metadata["range"] = range_val or random.randint(1, 10)
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE weapon_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), weapon_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(weapons)} armes mises à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées de l'arme {weapon_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour de l'arme {weapon_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(weapons)} armes mises à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des armes: {e}")
        conn.rollback()
        return 0

def update_clothing_metadata(conn, cursor):
    """
    Met à jour les métadonnées des vêtements pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées des vêtements...")
        
        # Récupérer tous les vêtements
        cursor.execute("""
            SELECT id, name, clothing_type, metadata, slots
            FROM clothing_items
        """)
        clothing_items = cursor.fetchall()
        
        updated_count = 0
        for item_id, name, clothing_type, metadata_str, slots in clothing_items:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Déterminer le type d'armure en fonction du type de vêtement
                if clothing_type.lower() in ["hat", "helmet", "cap"]:
                    armor_type = "head"
                    item_slots = "HEAD"
                elif clothing_type.lower() in ["jacket", "coat", "vest", "armor", "shirt"]:
                    armor_type = "body"
                    item_slots = "BODY"
                elif clothing_type.lower() in ["pants", "shorts", "skirt"]:
                    armor_type = "legs"
                    item_slots = "LEGS"
                elif clothing_type.lower() in ["boots", "shoes"]:
                    armor_type = "feet"
                    item_slots = "FEET"
                elif clothing_type.lower() in ["gloves"]:
                    armor_type = "hands"
                    item_slots = "HANDS"
                else:
                    armor_type = "accessory"
                    item_slots = "ACCESSORY"
                
                # Ajouter ou mettre à jour les champs requis
                if "protection" not in metadata:
                    metadata["protection"] = random.randint(1, 10)
                if "armor_type" not in metadata:
                    metadata["armor_type"] = armor_type
                if "slots" not in metadata:
                    metadata["slots"] = item_slots
                
                # Mettre à jour la base de données avec les nouvelles métadonnées et slots
                cursor.execute("""
                    UPDATE clothing_items
                    SET metadata = ?, slots = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_slots, item_id))
                
                # Générer et mettre à jour le champ 'stats' si nécessaire
                stats = {
                    "defense": random.randint(1, 10),
                    "comfort": random.randint(1, 10),
                    "style": random.randint(1, 10),
                    "charisma": random.randint(1, 5),
                    "status": random.randint(1, 5)
                }
                
                cursor.execute("""
                    UPDATE clothing_items
                    SET stats = ?
                    WHERE id = ?
                """, (json.dumps(stats), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(clothing_items)} vêtements mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du vêtement {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du vêtement {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(clothing_items)} vêtements mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des vêtements: {e}")
        conn.rollback()
        return 0

def update_implant_metadata(conn, cursor):
    """
    Met à jour les métadonnées des implants pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées des implants...")
        
        # Récupérer tous les implants
        cursor.execute("""
            SELECT id, name, implant_type, metadata
            FROM implant_items
        """)
        implant_items = cursor.fetchall()
        
        updated_count = 0
        for item_id, name, implant_type, metadata_str in implant_items:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Déterminer l'emplacement sur le corps en fonction du type d'implant
                if implant_type.lower() in ["neural", "brain", "cortical"]:
                    body_location = "BRAIN"
                elif implant_type.lower() in ["ocular", "eye", "retinal"]:
                    body_location = "EYES"
                elif implant_type.lower() in ["dermal", "skin"]:
                    body_location = "SKIN"
                elif implant_type.lower() in ["skeletal", "bone"]:
                    body_location = "SKELETON"
                elif implant_type.lower() in ["muscular", "muscle"]:
                    body_location = "MUSCLES"
                else:
                    body_location = "INTERNAL"
                
                # Ajouter ou mettre à jour les champs requis
                if "implant_type" not in metadata:
                    metadata["implant_type"] = implant_type
                if "body_location" not in metadata:
                    metadata["body_location"] = body_location
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE implant_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(implant_items)} implants mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées de l'implant {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour de l'implant {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(implant_items)} implants mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des implants: {e}")
        conn.rollback()
        return 0

def update_hardware_metadata(conn, cursor):
    """
    Met à jour les métadonnées du matériel informatique pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées du matériel informatique...")
        
        # Récupérer tout le matériel informatique
        cursor.execute("""
            SELECT id, name, hardware_type, performance, metadata
            FROM hardware_items
        """)
        hardware_items = cursor.fetchall()
        
        updated_count = 0
        for item_id, name, hardware_type, performance, metadata_str in hardware_items:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "hardware_type" not in metadata:
                    metadata["hardware_type"] = hardware_type
                if "performance" not in metadata:
                    metadata["performance"] = performance or random.randint(1, 10)
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE hardware_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(hardware_items)} matériels informatiques mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du matériel {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du matériel {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(hardware_items)} matériels informatiques mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées du matériel informatique: {e}")
        conn.rollback()
        return 0

def update_software_metadata(conn, cursor):
    """
    Met à jour les métadonnées des logiciels pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées des logiciels...")
        
        # Récupérer tous les logiciels
        cursor.execute("""
            SELECT id, name, software_type, version, metadata
            FROM software_items
        """)
        software_items = cursor.fetchall()
        
        updated_count = 0
        for item_id, name, software_type, version, metadata_str in software_items:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "software_type" not in metadata:
                    metadata["software_type"] = software_type
                if "version" not in metadata:
                    metadata["version"] = version or f"{random.randint(1, 9)}.{random.randint(0, 9)}"
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE software_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(software_items)} logiciels mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du logiciel {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du logiciel {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(software_items)} logiciels mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des logiciels: {e}")
        conn.rollback()
        return 0

def update_consumable_metadata(conn, cursor):
    """
    Met à jour les métadonnées des consommables pour assurer la compatibilité.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la connexion
    
    Returns:
        Nombre d'objets mis à jour
    """
    try:
        logger.info("Mise à jour des métadonnées des consommables...")
        
        # Récupérer tous les consommables
        cursor.execute("""
            SELECT id, name, consumable_type, effect_type, effect_power, metadata
            FROM consumable_items
        """)
        consumable_items = cursor.fetchall()
        
        updated_count = 0
        for item_id, name, consumable_type, effect_type, effect_power, metadata_str in consumable_items:
            try:
                # Analyser les métadonnées existantes
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Ajouter ou mettre à jour les champs requis
                if "effect_type" not in metadata:
                    metadata["effect_type"] = effect_type or "health"
                if "effect_power" not in metadata:
                    metadata["effect_power"] = effect_power or random.randint(5, 30)
                
                # Mettre à jour la base de données
                cursor.execute("""
                    UPDATE consumable_items
                    SET metadata = ?
                    WHERE id = ?
                """, (json.dumps(metadata), item_id))
                
                updated_count += 1
                if updated_count % 10 == 0:
                    logger.info(f"Progression: {updated_count}/{len(consumable_items)} consommables mis à jour")
            
            except json.JSONDecodeError:
                logger.error(f"Erreur lors du décodage des métadonnées du consommable {item_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du consommable {item_id}: {e}")
        
        conn.commit()
        logger.info(f"Terminé: {updated_count}/{len(consumable_items)} consommables mis à jour")
        return updated_count
    
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées des consommables: {e}")
        conn.rollback()
        return 0

def run_all_updates():
    """
    Exécute toutes les mises à jour pour assurer la compatibilité
    entre l'éditeur et le jeu.
    
    Returns:
        True si les mises à jour ont réussi, False sinon
    """
    conn, cursor = connect_to_db()
    if not conn or not cursor:
        return False
    
    try:
        # 1. Mettre à jour le schéma de la base de données
        if not update_table_schema(conn, cursor):
            logger.error("Échec de la mise à jour du schéma")
            return False
        
        # 2. Mettre à jour les métadonnées des objets
        update_weapon_metadata(conn, cursor)
        update_clothing_metadata(conn, cursor)
        update_implant_metadata(conn, cursor)
        update_hardware_metadata(conn, cursor)
        update_software_metadata(conn, cursor)
        update_consumable_metadata(conn, cursor)
        
        logger.info("Toutes les mises à jour ont été effectuées avec succès")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors des mises à jour: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("=== Début de la mise à jour des objets pour la compatibilité ===")
    
    if not DB_PATH.exists():
        logger.error(f"Base de données non trouvée: {DB_PATH}")
        sys.exit(1)
    
    success = run_all_updates()
    
    if success:
        logger.info("=== Mise à jour terminée avec succès ===")
        sys.exit(0)
    else:
        logger.error("=== Échec de la mise à jour ===")
        sys.exit(1)
