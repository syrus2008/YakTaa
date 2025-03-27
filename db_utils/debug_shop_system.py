import os
import sqlite3
import json
import logging
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shop_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ShopDebugger")

def inspect_shop_system():
    logger.info("===== DÉBUT DU DÉBOGAGE DU SYSTÈME DE BOUTIQUES =====")
    
    # 1. Vérification des chemins de la base de données
    check_database_paths()
    
    # 2. Analyse des bases de données disponibles
    db_paths = find_database_files()
    
    # 3. Inspection de chaque base de données
    for db_path in db_paths:
        inspect_database(db_path)

def check_database_paths():
    """Vérifie les chemins de base de données spécifiés dans le code"""
    logger.info("Vérification des chemins de bases de données configurés dans l'application")
    
    # Chemins possibles basés sur le code examiné
    db_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaktaa_data", "world.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaktaa_world_editor", "data", "world.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaktaa_world_editor", "worlds.db")
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            logger.info(f"✓ Base de données trouvée: {path}")
        else:
            logger.warning(f"✗ Base de données NON trouvée: {path}")

def find_database_files():
    """Recherche tous les fichiers .db dans le projet"""
    logger.info("Recherche de tous les fichiers de base de données (.db) dans le projet")
    db_files = []
    
    # Parcours récursif du répertoire du projet
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
        for file in files:
            if file.endswith(".db"):
                db_path = os.path.join(root, file)
                logger.info(f"Base de données trouvée: {db_path}")
                db_files.append(db_path)
    
    return db_files

def inspect_database(db_path):
    """Inspecte une base de données pour les tables et données relatives aux boutiques"""
    logger.info(f"\n===== INSPECTION DE LA BASE DE DONNÉES: {db_path} =====")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Vérifier les tables présentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Tables dans la base de données: {', '.join(tables)}")
        
        # 2. Vérifier si les tables nécessaires existent
        shop_related_tables = [
            "shops", "shop_inventory", "hardware_items", "software_items",
            "consumable_items", "weapon_items", "implant_items"
        ]
        
        for table in shop_related_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"✓ Table '{table}' existe avec {count} enregistrements")
            else:
                logger.warning(f"✗ Table '{table}' N'EXISTE PAS dans cette base de données")
        
        # 3. Si la table shops existe, examiner les boutiques
        if "shops" in tables:
            inspect_shops(conn, cursor)
            
            # 4. Examiner les relations entre boutiques et inventaires
            if "shop_inventory" in tables:
                inspect_shop_inventories(conn, cursor)
                
                # 5. Vérifier la cohérence entre les inventaires et les tables d'objets
                check_inventory_item_consistency(conn, cursor)
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'inspection de la base de données {db_path}: {str(e)}")

def inspect_shops(conn, cursor):
    """Examine les boutiques dans la base de données"""
    logger.info("\nExamen des boutiques:")
    
    # Vérifier la structure de la table shops
    cursor.execute("PRAGMA table_info(shops)")
    columns = [row[1] for row in cursor.fetchall()]
    logger.info(f"Colonnes de la table shops: {', '.join(columns)}")
    
    # Obtenir toutes les boutiques
    cursor.execute("SELECT * FROM shops LIMIT 20")
    shops = cursor.fetchall()
    
    # Afficher des informations sur chaque boutique
    for shop in shops:
        shop_dict = {column: shop[column] for column in shop.keys()}
        logger.info(f"\nDétails de la boutique:")
        logger.info(f"ID: {shop_dict.get('id')}")
        logger.info(f"Nom: {shop_dict.get('name')}")
        logger.info(f"Type: {shop_dict.get('shop_type')}")
        logger.info(f"Est légale: {bool(shop_dict.get('is_legal', 1))}")
        
        # Vérifier le nombre d'objets dans l'inventaire de cette boutique
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM shop_inventory WHERE shop_id = ?", 
                (shop_dict.get('id'),)
            )
            inventory_count = cursor.fetchone()[0]
            logger.info(f"Nombre d'objets dans l'inventaire: {inventory_count}")
            
            if inventory_count == 0:
                logger.warning(f"⚠️ La boutique '{shop_dict.get('name')}' a un inventaire VIDE!")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'inventaire: {str(e)}")

def inspect_shop_inventories(conn, cursor):
    """Examine les inventaires des boutiques"""
    logger.info("\nExamen des inventaires des boutiques:")
    
    # Vérifier la structure de la table shop_inventory
    cursor.execute("PRAGMA table_info(shop_inventory)")
    columns = [row[1] for row in cursor.fetchall()]
    logger.info(f"Colonnes de la table shop_inventory: {', '.join(columns)}")
    
    # Obtenir des statistiques sur les inventaires
    cursor.execute("""
        SELECT s.name, COUNT(si.id) as item_count 
        FROM shops s 
        LEFT JOIN shop_inventory si ON s.id = si.shop_id 
        GROUP BY s.id 
        ORDER BY item_count DESC 
        LIMIT 20
    """)
    
    inventory_stats = cursor.fetchall()
    logger.info("\nStatistiques d'inventaire par boutique:")
    for stat in inventory_stats:
        logger.info(f"Boutique '{stat['name']}': {stat['item_count']} objets")
    
    # Vérifier la distribution des types d'objets dans les inventaires
    try:
        cursor.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM shop_inventory 
            GROUP BY item_type
        """)
        
        type_distribution = cursor.fetchall()
        if type_distribution:
            logger.info("\nDistribution des types d'objets dans les inventaires:")
            for dist in type_distribution:
                logger.info(f"Type '{dist[0]}': {dist[1]} objets")
        else:
            logger.warning("⚠️ Aucune donnée trouvée dans la table shop_inventory!")
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des types d'objets: {str(e)}")

def check_inventory_item_consistency(conn, cursor):
    """Vérifie la cohérence entre les inventaires et les tables d'objets"""
    logger.info("\nVérification de la cohérence entre inventaires et objets:")
    
    # Obtenir quelques exemples d'objets d'inventaire
    cursor.execute("SELECT item_id, item_type FROM shop_inventory LIMIT 50")
    inventory_items = cursor.fetchall()
    
    if not inventory_items:
        logger.warning("⚠️ Aucun objet trouvé dans les inventaires pour vérifier la cohérence!")
        return
    
    # Vérifier l'existence de chaque objet dans sa table respective
    consistency_issues = 0
    for item in inventory_items:
        item_id = item['item_id']
        item_type = item['item_type']
        
        # Déterminer la table cible
        table_name = f"{item_type}_items" if not item_type.endswith('_items') else item_type
        
        # Vérifier si la table existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            logger.warning(f"⚠️ Table '{table_name}' pour l'objet de type '{item_type}' n'existe pas!")
            consistency_issues += 1
            continue
        
        # Vérifier si l'objet existe dans la table
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id = ?", (item_id,))
            item_exists = cursor.fetchone()[0] > 0
            
            if not item_exists:
                logger.warning(f"⚠️ L'objet {item_id} (type: {item_type}) n'existe pas dans la table {table_name}!")
                consistency_issues += 1
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'objet {item_id}: {str(e)}")
            consistency_issues += 1
    
    if consistency_issues > 0:
        logger.warning(f"⚠️ {consistency_issues} problèmes de cohérence détectés entre les inventaires et les objets!")
    else:
        logger.info("✓ Tous les objets d'inventaire vérifiés existent dans leurs tables respectives")

def analyze_shop_loading_code():
    """Analyse le code de chargement des boutiques"""
    logger.info("\n===== ANALYSE DU CODE DE CHARGEMENT DES BOUTIQUES =====")
    
    # Journaliser les fichiers importants à examiner
    shop_related_files = [
        "yaktaa/items/shop_manager.py",
        "yaktaa/ui/shop_window.py",
        "yaktaa_world_editor/world_generator.py",
        "yaktaa_world_editor/shop_item_generator.py"
    ]
    
    for file_path in shop_related_files:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        if os.path.exists(full_path):
            logger.info(f"✓ Fichier de code à examiner: {full_path}")
        else:
            logger.warning(f"✗ Fichier de code NON trouvé: {full_path}")

    # Points potentiels de défaillance à examiner manuellement
    logger.info("\nPoints potentiels de défaillance à examiner:")
    logger.info("1. ShopManager._load_shop_inventory: Peut échouer à charger des objets existants")
    logger.info("2. WorldGenerator._generate_shop_inventories: Peut échouer à générer des objets")
    logger.info("3. ShopWindow.display_items: Peut échouer à afficher des objets chargés")
    logger.info("4. Les méthodes _generate_random_*_item peuvent échouer silencieusement")
    logger.info("5. Connexion entre ID d'objets et ID de boutiques peut être incorrecte")
    logger.info("6. Il pourrait y avoir une incompatibilité entre l'ancien et le nouveau format de BD")

# Exécuter l'analyse
if __name__ == "__main__":
    logger.info("Démarrage de l'analyse du système de boutiques")
    inspect_shop_system()
    analyze_shop_loading_code()
    logger.info("\n===== FIN DE L'ANALYSE =====")
