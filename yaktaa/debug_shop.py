#!/usr/bin/env python
"""
Script de débogage spécifique pour les fonctionnalités de boutique dans YakTaa.
Ce script permet d'isoler et diagnostiquer les problèmes qui surviennent lors du chargement des boutiques.
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime

# Ajout du répertoire parent au chemin de recherche Python (comme dans run_yaktaa.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logger pour un débogage détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [DEBUG_SHOP] %(message)s',
    handlers=[
        logging.FileHandler("shop_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ShopDebugger")
logger.info("=== Démarrage du script de débogage de boutique ===")

try:
    # Import des modules nécessaires avec le chemin correct
    logger.info("Importation des modules...")
    # Import direct des modules du projet
    from yaktaa.world.world_loader import WorldLoader
    from yaktaa.items.shop_manager import ShopManager
    from yaktaa.items.inventory_manager import InventoryManager
    from yaktaa.items.item import Item
    # Import directs des modules items sans importer les classes spécifiques
    # Nous les utiliserons directement dans le code
    import yaktaa.items.weapon as weapon_module
    import yaktaa.items.consumable as consumable_module
    import yaktaa.items.software as software_module
    import yaktaa.items.hardware as hardware_module
    import yaktaa.items.implant as implant_module
    logger.info("Modules importés avec succès")
except Exception as e:
    logger.critical(f"Erreur lors de l'importation des modules: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Création d'une classe de remplacement pour ItemFactory
class SimpleItemFactory:
    """Classe simplifiée pour remplacer ItemFactory dans le contexte de débogage"""
    
    def __init__(self):
        logger.info("Initialisation de SimpleItemFactory pour le débogage")
        
    def create_item(self, item_data):
        """Crée un item basé sur les données fournies"""
        item_type = item_data.get('type', 'misc')
        
        logger.debug(f"Tentative de création d'item de type {item_type} avec ID {item_data.get('id', 'inconnu')}")
        
        try:
            if item_type == 'weapon':
                # Utiliser la classe WeaponItem au lieu de Weapon
                return weapon_module.WeaponItem(**item_data)
            elif item_type == 'consumable':
                # Pour consumable, vérifier si ConsumableItem existe
                if hasattr(consumable_module, 'ConsumableItem'):
                    return consumable_module.ConsumableItem(**item_data)
                else:
                    # Fallback à la classe par défaut ou une autre classe disponible
                    return consumable_module.Consumable(**item_data)
            elif item_type == 'software':
                # Pour software, vérifier si SoftwareItem existe
                if hasattr(software_module, 'SoftwareItem'):
                    return software_module.SoftwareItem(**item_data)
                else:
                    return software_module.Software(**item_data)
            elif item_type == 'hardware':
                # Pour hardware, vérifier si HardwareItem existe
                if hasattr(hardware_module, 'HardwareItem'):
                    return hardware_module.HardwareItem(**item_data)
                else:
                    return hardware_module.Hardware(**item_data)
            elif item_type == 'implant':
                # Pour implant, vérifier si ImplantItem existe
                if hasattr(implant_module, 'ImplantItem'):
                    return implant_module.ImplantItem(**item_data)
                else:
                    return implant_module.Implant(**item_data)
            else:
                return Item(**item_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'item {item_data.get('id')}: {e}")
            logger.error(traceback.format_exc())
            return Item(name="Item Error", description=f"Erreur: {str(e)}")

# Fonction principale pour le débogage de la boutique
def debug_shop():
    logger.info("Début du processus de débogage de la boutique")
    
    try:
        # 1. Initialisation du WorldLoader
        logger.info("Initialisation du WorldLoader...")
        # Essayer d'abord sans spécifier de monde spécifique
        try:
            world_loader = WorldLoader()
            logger.info("WorldLoader initialisé avec succès (sans monde spécifique)")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser WorldLoader sans monde spécifique: {e}")
            # Essayer avec un nom de monde par défaut
            world_loader = WorldLoader("default")
            logger.info("WorldLoader initialisé avec succès (avec monde 'default')")
        
        # 2. Initialisation du ShopManager
        logger.info("Initialisation du ShopManager...")
        shop_manager = ShopManager(world_loader)
        logger.info("ShopManager initialisé avec succès")
        
        # 3. Création et affectation du SimpleItemFactory
        logger.info("Création du SimpleItemFactory...")
        item_factory = SimpleItemFactory()
        shop_manager.set_item_factory(item_factory)
        logger.info("ItemFactory créé et affecté au ShopManager")
        
        # 4. Tentative de chargement des boutiques
        logger.info("Tentative de chargement des boutiques...")
        try:
            # Vérifier l'état de la base de données avant le chargement
            logger.info("Vérification des tables de boutique dans la base de données...")
            # Vérification de la connexion à la base de données
            conn = world_loader.get_connection()
            if conn:
                logger.info("Connexion à la base de données établie avec succès")
                cursor = conn.cursor()
                
                # Vérifier si la table shops existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
                if cursor.fetchone():
                    logger.info("Table 'shops' trouvée dans la base de données")
                    
                    # Compter le nombre de boutiques
                    cursor.execute("SELECT COUNT(*) FROM shops")
                    shop_count = cursor.fetchone()[0]
                    logger.info(f"Nombre de boutiques dans la base de données: {shop_count}")
                else:
                    logger.warning("Table 'shops' non trouvée dans la base de données!")
            else:
                logger.error("Impossible d'établir une connexion à la base de données")
            
            # Chargement des boutiques
            shop_manager.load_shops()
            logger.info(f"Chargement des boutiques réussi. {len(shop_manager.shops)} boutiques chargées.")
            
            # Affichage des informations des boutiques
            for shop_id, shop in shop_manager.shops.items():
                logger.info(f"Boutique ID: {shop_id}, Nom: {shop.name}, Nombre d'items: {len(shop.inventory) if hasattr(shop, 'inventory') and shop.inventory is not None else 'N/A'}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des boutiques: {e}")
            logger.error(traceback.format_exc())
            
        # 5. Test d'accès à une boutique spécifique
        logger.info("Test d'accès à une boutique spécifique...")
        try:
            # Tentative d'accès à la première boutique (si disponible)
            if shop_manager.shops:
                first_shop_id = next(iter(shop_manager.shops))
                shop = shop_manager.shops[first_shop_id]
                logger.info(f"Accès réussi à la boutique {shop.name}")
                
                # Affichage des items de la boutique
                logger.info(f"Items dans la boutique {shop.name}:")
                
                # Vérification du type d'inventaire (peut être dict ou list selon l'implémentation)
                if hasattr(shop, 'inventory'):
                    if shop.inventory is None:
                        logger.warning("L'inventaire de la boutique est None!")
                    elif isinstance(shop.inventory, dict):
                        for item_id, item_info in shop.inventory.items():
                            logger.info(f"  - Item ID: {item_id}, Nom: {item_info.get('name', 'Inconnu')}, Type: {item_info.get('type', 'Inconnu')}")
                    elif isinstance(shop.inventory, list):
                        for i, item_entry in enumerate(shop.inventory):
                            # L'entrée peut être un tuple (item, price) ou autre chose
                            if isinstance(item_entry, tuple) and len(item_entry) >= 2:
                                item, price = item_entry[0], item_entry[1]
                                item_name = getattr(item, 'name', 'Inconnu')
                                item_id = getattr(item, 'id', 'Inconnu')
                                logger.info(f"  - Item {i+1}: {item_name} (ID: {item_id}), Prix: {price}")
                            else:
                                logger.info(f"  - Item {i+1}: {item_entry}")
                    else:
                        logger.warning(f"L'inventaire de la boutique est d'un type inattendu: {type(shop.inventory)}")
                else:
                    logger.warning("La boutique n'a pas d'attribut 'inventory'")
            else:
                logger.warning("Aucune boutique n'a été chargée pour les tests")
        except Exception as e:
            logger.error(f"Erreur lors du test d'accès à une boutique: {e}")
            logger.error(traceback.format_exc())
            
    except Exception as e:
        logger.critical(f"Erreur critique dans le processus de débogage: {e}")
        logger.critical(traceback.format_exc())
    
    logger.info("Fin du processus de débogage de la boutique")

# Exécution du script de débogage
if __name__ == "__main__":
    debug_shop()
