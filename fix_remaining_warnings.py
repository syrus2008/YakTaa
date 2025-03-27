"""
Script pour corriger les avertissements restants dans YakTaa
Ce script corrige deux types de problèmes:
1. Les avertissements sur les types d'articles en minuscules (weapon, clothing, etc.)
2. Les articles hardware et software manquants dans leurs tables respectives
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
logger = logging.getLogger("FixRemainingWarnings")

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

def fix_shop_manager_classes():
    """
    Crée une version mise à jour du shop_manager.py pour gérer les types en minuscules
    """
    shop_manager_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     "yaktaa", "items", "shop_manager.py")
    
    if not os.path.exists(shop_manager_path):
        logger.error(f"Fichier shop_manager.py non trouvé: {shop_manager_path}")
        return False
    
    try:
        with open(shop_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher la section qui vérifie les types d'articles
        if "if item_type.lower().startswith('software')" in content:
            # Remplacer la vérification des types d'articles pour accepter les minuscules
            original = "if item_type.lower().startswith('software')"
            replacement = """
        # Normaliser le type d'article en minuscules
        item_type_lower = item_type.lower()
        
        if item_type_lower.startswith('software')"""
            content = content.replace(original, replacement)
            
            # Mettre à jour les autres conditions avec la nouvelle variable item_type_lower
            content = content.replace("elif item_type.lower() in ['weapon', 'pistol', 'rifle', 'melee']",
                                     "elif item_type_lower in ['weapon', 'pistol', 'rifle', 'melee']")
            
            content = content.replace("elif item_type.lower() in ['clothing', 'armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']",
                                     "elif item_type_lower in ['clothing', 'armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']")
            
            content = content.replace("elif item_type.lower() in ['implant', 'cyberware', 'cybernetic']",
                                     "elif item_type_lower in ['implant', 'cyberware', 'cybernetic']")
            
            content = content.replace("elif item_type.lower() in ['hardware', 'device', 'gadget']",
                                     "elif item_type_lower in ['hardware', 'device', 'gadget']")
            
            content = content.replace("elif item_type.lower() in ['consumable', 'item', 'usable']",
                                     "elif item_type_lower in ['consumable', 'item', 'usable']")
            
            content = content.replace("elif item_type.lower() in ['food', 'drink', 'drug']",
                                     "elif item_type_lower in ['food', 'drink', 'drug']")
            
            # Pour éviter les avertissements pour les types inconnus, ajouter une gestion plus flexible
            if "logger.warning(f\"[SHOP_MANAGER] Type d'article non reconnu: {item_type}\")" in content:
                original = "logger.warning(f\"[SHOP_MANAGER] Type d'article non reconnu: {item_type}\")"
                replacement = """# Tenter de déterminer le type réel à partir du préfixe de l'ID
            if item_id.startswith('weapon_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> weapon")
                item_type_lower = 'weapon'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'weapon', item_id)
            elif item_id.startswith('clothing_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> clothing")
                item_type_lower = 'clothing'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'clothing', item_id)
            elif item_id.startswith('hardware_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> hardware")
                item_type_lower = 'hardware'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'hardware', item_id)
            elif item_id.startswith('software_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> software")
                item_type_lower = 'software'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'software', item_id)
            elif item_id.startswith('consumable_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> consumable")
                item_type_lower = 'consumable'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'consumable', item_id)
            elif item_id.startswith('implant_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> implant")
                item_type_lower = 'implant'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'implant', item_id)
            elif item_id.startswith('food_'):
                logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> food")
                item_type_lower = 'food'
                # Rappeler récursivement la méthode avec le type corrigé
                return self._load_item_details(conn, 'food', item_id)
            else:
                logger.warning(f"[SHOP_MANAGER] Type d'article non reconnu: {item_type}")"""
                content = content.replace(original, replacement)
        
        # Sauvegarder le fichier modifié
        backup_path = shop_manager_path + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Renommer le fichier de sauvegarde vers le fichier original
        os.replace(backup_path, shop_manager_path)
        
        logger.info(f"Fichier shop_manager.py mis à jour avec succès: {shop_manager_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du fichier shop_manager.py: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

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
            create_hardware_item(conn, item_id)
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction des articles hardware manquants: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fix_missing_software_items():
    """
    Crée les articles software manquants dans la table software_items
    """
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Trouver les articles software dans l'inventaire qui n'existent pas dans la table software_items
        cursor.execute("""
            SELECT DISTINCT si.item_id 
            FROM shop_inventory si 
            LEFT JOIN software_items soi ON si.item_id = soi.id 
            WHERE si.item_type = 'software' AND si.item_id LIKE 'software_%' AND soi.id IS NULL
        """)
        
        missing_items = [row[0] for row in cursor.fetchall()]
        logger.info(f"Nombre d'articles software manquants: {len(missing_items)}")
        
        for item_id in missing_items:
            create_software_item(conn, item_id)
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction des articles software manquants: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_hardware_item(conn, item_id):
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

def create_software_item(conn, item_id):
    """
    Crée un article software manquant dans la table software_items
    """
    try:
        cursor = conn.cursor()
        
        # Vérifier si l'article existe déjà
        cursor.execute("SELECT COUNT(*) FROM software_items WHERE id = ?", (item_id,))
        if cursor.fetchone()[0] > 0:
            return
        
        # Types de logiciels possibles
        software_types = ["Security", "Hacking", "Utility", "AI", "Virus", "Firewall", "Analysis"]
        
        # Développeurs possibles
        developers = ["NetSecure", "ByteForge", "QuantumSoft", "CyberLogic", "SynthWave", "NeuraSoft"]
        
        # Qualificateurs 
        qualifiers = ["Cyber", "Quantum", "Neural", "Digital", "Synth", "Crypto", "Data"]
        
        # Versions
        versions = ["v1.0", "v2.5", "v3.2", "v4.7", "v5.0", "v6.3", "v7.1"]
        
        # Générer un nom aléatoire
        developer = random.choice(developers)
        qualifier = random.choice(qualifiers)
        software_type = random.choice(software_types)
        version = random.choice(versions)
        
        name = f"{developer} {qualifier}{software_type} {version}"
        description = f"Un logiciel de {software_type.lower()} développé par {developer}"
        price = random.randint(50, 2000)
        
        # Générer des métadonnées
        metadata = {
            "software_type": software_type.upper(),
            "version": version,
            "developer": developer,
            "requirements": {
                "cpu": random.randint(1, 5),
                "ram": random.randint(1, 5),
                "storage": random.randint(1, 10)
            },
            "capabilities": [
                random.choice(["decrypt", "encrypt", "analyze", "bypass", "defend", "attack", "monitor", "optimize"])
                for _ in range(random.randint(1, 3))
            ],
            "license_type": random.choice(["FREE", "TRIAL", "PREMIUM", "ENTERPRISE", "BLACK_MARKET"]),
            "rating": random.randint(1, 5)
        }
        
        # Insérer l'article dans la table software_items
        cursor.execute("""
            INSERT INTO software_items (id, name, description, price, software_type, developer, version, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, name, description, price, software_type.upper(), 
              developer, version, json.dumps(metadata)))
        
        logger.info(f"Article software créé: {name} (ID: {item_id})")
    
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'article software {item_id}: {e}")
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
        
        # Vérifier les articles hardware manquants
        cursor.execute("""
            SELECT COUNT(*) FROM shop_inventory si 
            LEFT JOIN hardware_items hi ON si.item_id = hi.id 
            WHERE si.item_type = 'hardware' AND si.item_id LIKE 'hardware_%' AND hi.id IS NULL
        """)
        missing_hardware_count = cursor.fetchone()[0]
        
        # Vérifier les articles software manquants
        cursor.execute("""
            SELECT COUNT(*) FROM shop_inventory si 
            LEFT JOIN software_items soi ON si.item_id = soi.id 
            WHERE si.item_type = 'software' AND si.item_id LIKE 'software_%' AND soi.id IS NULL
        """)
        missing_software_count = cursor.fetchone()[0]
        
        if missing_hardware_count > 0:
            logger.warning(f"Il reste {missing_hardware_count} articles hardware manquants")
        else:
            logger.info("Tous les articles hardware référencés existent maintenant dans la table hardware_items")
            
        if missing_software_count > 0:
            logger.warning(f"Il reste {missing_software_count} articles software manquants")
        else:
            logger.info("Tous les articles software référencés existent maintenant dans la table software_items")
        
        return missing_hardware_count == 0 and missing_software_count == 0
    
    except Exception as e:
        logger.error(f"Erreur lors des tests: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Démarrage de la correction des avertissements restants")
    
    # Mettre à jour le fichier shop_manager.py pour mieux gérer les types en minuscules
    logger.info("Mise à jour du fichier shop_manager.py...")
    fix_shop_manager_classes()
    
    # Corriger les articles hardware manquants
    logger.info("Correction des articles hardware manquants...")
    success_hardware = fix_missing_hardware_items()
    
    # Corriger les articles software manquants
    logger.info("Correction des articles software manquants...")
    success_software = fix_missing_software_items()
    
    # Exécuter des tests
    logger.info("Exécution des tests après correction...")
    success_tests = run_tests()
    
    if success_hardware and success_software and success_tests:
        logger.info("✅ Toutes les corrections ont été appliquées avec succès")
        print("\n[SUCCÈS] Tous les avertissements restants ont été corrigés")
    else:
        logger.warning("⚠️ Certaines corrections n'ont pas pu être appliquées")
        print("\n[ATTENTION] Certains avertissements n'ont pas pu être corrigés")
