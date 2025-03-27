"""
Script pour corriger les avertissements liés aux boutiques dans YakTaa
Ce script corrige deux types de problèmes:
1. Types d'articles non reconnus (GENERAL, BLACK_MARKET)
2. Articles hardware manquants dans la table hardware_items
"""

import os
import sys
import json
import uuid
import sqlite3
import logging
import random
from pathlib import Path
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FixShopWarnings")

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                      "yaktaa_world_editor", "worlds.db")

def connect_to_db():
    """
    Établit une connexion à la base de données
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"Base de données non trouvée: {DB_PATH}")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info(f"Connecté à la base de données: {DB_PATH}")
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

def fix_shop_inventory_types():
    """
    Corrige les types d'articles non reconnus dans l'inventaire des boutiques
    """
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Rechercher les types d'articles dans l'inventaire des boutiques
        cursor.execute("SELECT DISTINCT item_type FROM shop_inventory")
        item_types = [row[0] for row in cursor.fetchall()]
        logger.info(f"Types d'articles trouvés dans l'inventaire: {item_types}")
        
        # Types d'articles problématiques
        problem_types = ["GENERAL", "BLACK_MARKET", "FOOD"]
        items_to_fix = []
        
        # Trouver les articles avec des types problématiques
        for item_type in problem_types:
            cursor.execute("SELECT id, item_id, shop_id, item_type FROM shop_inventory WHERE item_type = ?", (item_type,))
            items = cursor.fetchall()
            items_to_fix.extend(items)
        
        logger.info(f"Nombre d'articles à corriger: {len(items_to_fix)}")
        
        # Corriger les types d'articles
        updated_count = 0
        for item in items_to_fix:
            inventory_id, item_id, shop_id, item_type = item
            
            # Analyser le préfixe de l'item_id pour déterminer le type réel
            new_type = None
            if item_id.startswith("weapon_"):
                new_type = "weapon"
            elif item_id.startswith("clothing_"):
                new_type = "clothing"
            elif item_id.startswith("hardware_"):
                new_type = "hardware"
            elif item_id.startswith("software_"):
                new_type = "software"
            elif item_id.startswith("consumable_"):
                new_type = "consumable"
            elif item_id.startswith("implant_"):
                new_type = "implant"
            elif item_id.startswith("food_"):
                new_type = "food"
            else:
                # Si le préfixe n'est pas reconnu, assigner un type en fonction
                # du type de boutique
                cursor.execute("SELECT shop_type FROM shops WHERE id = ?", (shop_id,))
                shop_type = cursor.fetchone()[0]
                
                if shop_type == "WEAPON":
                    new_type = "weapon"
                elif shop_type == "CLOTHING":
                    new_type = "clothing"
                elif shop_type == "HARDWARE":
                    new_type = "hardware"
                elif shop_type == "SOFTWARE":
                    new_type = "software"
                elif shop_type == "FOOD":
                    new_type = "food"
                elif shop_type == "BLACK_MARKET":
                    # Pour les marchés noirs, assigner un type aléatoire parmi les plus communs
                    new_type = random.choice(["weapon", "hardware", "consumable"])
                else:
                    # Dernier recours: convertir en article générique le plus commun
                    new_type = "consumable"
            
            if new_type:
                # Mettre à jour le type d'article
                cursor.execute("UPDATE shop_inventory SET item_type = ? WHERE id = ?", (new_type, inventory_id))
                updated_count += 1
                logger.info(f"Article {item_id} mis à jour: {item_type} -> {new_type}")
                
                # Si le type est maintenant hardware, assurons-nous que l'article existe
                if new_type == "hardware" and item_id.startswith("hardware_"):
                    fix_hardware_item(conn, item_id)
        
        logger.info(f"{updated_count} articles mis à jour dans la table shop_inventory")
        conn.commit()
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction des types d'articles: {e}")
        import traceback
        logger.error(traceback.format_exc())
        conn.rollback()
        return False
    finally:
        conn.close()

def fix_missing_hardware_items():
    """
    Crée les articles hardware manquants dans la table hardware_items
    """
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Trouver les articles hardware dans l'inventaire qui n'existent pas dans la table hardware_items
        cursor.execute("""
            SELECT DISTINCT si.item_id 
            FROM shop_inventory si 
            LEFT JOIN hardware_items hi ON si.item_id = hi.id 
            WHERE si.item_type = 'hardware' AND si.item_id LIKE 'hardware_%' AND hi.id IS NULL
        """)
        
        missing_items = [row[0] for row in cursor.fetchall()]
        logger.info(f"Nombre d'articles hardware manquants: {len(missing_items)}")
        
        for item_id in missing_items:
            fix_hardware_item(conn, item_id)
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction des articles hardware manquants: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fix_hardware_item(conn, item_id):
    """
    Crée un article hardware manquant dans la table hardware_items
    """
    try:
        cursor = conn.cursor()
        
        # Vérifier si l'article existe déjà
        cursor.execute("SELECT COUNT(*) FROM hardware_items WHERE id = ?", (item_id,))
        if cursor.fetchone()[0] > 0:
            return
        
        # Types de matériel possibles
        hardware_types = ["CPU", "RAM", "SSD", "Cooling System", "Router", "Network Card"]
        
        # Fabricants possibles
        manufacturers = ["CyberIndustries", "NeuraTech", "DigiCore", "SynthCorp", "HyperSystems", "QuantumTech"]
        
        # Qualificateurs 
        qualifiers = ["Quantum", "Neural", "Cyber", "Tech", "Digital", "Synth", "Hyper"]
        
        # Modèles
        models = ["Alpha", "Pro", "Elite", "Max", "Omega", "Prime", "Plus"]
        
        # Générer un nom aléatoire
        manufacturer = random.choice(manufacturers)
        qualifier = random.choice(qualifiers)
        hardware_type = random.choice(hardware_types)
        model = random.choice(models)
        
        name = f"{manufacturer} {qualifier}{hardware_type.replace(' ', '')} {model}"
        description = f"Un {hardware_type.lower()} de haute qualité fabriqué par {manufacturer}"
        price = random.randint(100, 5000)
        
        # Générer des métadonnées
        metadata = {
            "stats": {
                "processing": random.randint(1, 10),
                "memory": random.randint(1, 10),
                "security": random.randint(1, 10)
            },
            "power_consumption": random.randint(1, 10),
            "compatibility": ["standard", "cyberdeck"],
            "heat_generation": random.randint(1, 5),
            "reliability": random.randint(60, 100),
            "hardware_type": hardware_type.upper().replace(" ", "_"),
            "performance": random.randint(1, 10)
        }
        
        # Insérer l'article dans la table hardware_items
        cursor.execute("""
            INSERT INTO hardware_items (id, name, description, price, hardware_type, manufacturer, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item_id, name, description, price, hardware_type.upper().replace(" ", "_"), 
              manufacturer, json.dumps(metadata)))
        
        logger.info(f"Article hardware créé: {name} (ID: {item_id})")
    
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'article hardware {item_id}: {e}")
        raise

def run_tests():
    """
    Exécute des tests après correction pour vérifier que les problèmes sont résolus
    """
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Vérifier les types d'articles dans l'inventaire des boutiques
        cursor.execute("SELECT DISTINCT item_type FROM shop_inventory")
        item_types = [row[0] for row in cursor.fetchall()]
        logger.info(f"Types d'articles dans l'inventaire après correction: {item_types}")
        problem_types = ["GENERAL", "BLACK_MARKET"]
        for problem_type in problem_types:
            if problem_type in item_types:
                logger.warning(f"Type d'article problématique toujours présent: {problem_type}")
            else:
                logger.info(f"Type d'article problématique corrigé: {problem_type}")
        
        # Vérifier les articles hardware manquants
        cursor.execute("""
            SELECT COUNT(*) FROM shop_inventory si 
            LEFT JOIN hardware_items hi ON si.item_id = hi.id 
            WHERE si.item_type = 'hardware' AND si.item_id LIKE 'hardware_%' AND hi.id IS NULL
        """)
        missing_count = cursor.fetchone()[0]
        if missing_count > 0:
            logger.warning(f"Il reste {missing_count} articles hardware manquants")
        else:
            logger.info("Tous les articles hardware référencés existent maintenant dans la table hardware_items")
        
        return missing_count == 0 and not any(pt in item_types for pt in problem_types)
    
    except Exception as e:
        logger.error(f"Erreur lors des tests: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Démarrage de la correction des avertissements liés aux boutiques")
    
    # Corriger les types d'articles
    logger.info("Correction des types d'articles non reconnus...")
    success_types = fix_shop_inventory_types()
    
    # Corriger les articles hardware manquants
    logger.info("Correction des articles hardware manquants...")
    success_hardware = fix_missing_hardware_items()
    
    # Exécuter des tests
    logger.info("Exécution des tests après correction...")
    success_tests = run_tests()
    
    if success_types and success_hardware and success_tests:
        logger.info("✅ Toutes les corrections ont été appliquées avec succès")
        print("\n[SUCCÈS] Tous les avertissements ont été corrigés")
    else:
        logger.warning("⚠️ Certaines corrections n'ont pas pu être appliquées")
        print("\n[ATTENTION] Certains avertissements n'ont pas pu être corrigés")
