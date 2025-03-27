"""
Script de test pour vérifier que le jeu charge correctement la base de données
Ce script simule le comportement du jeu en chargeant un monde et ses objets
"""

import os
import sys
import json
import logging
import sqlite3
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestGameDBLoading")

# Ajouter le répertoire parent au path pour pouvoir importer les modules du jeu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les modules du jeu
try:
    from yaktaa.world.world_loader import WorldLoader
    from yaktaa.items.shop_manager import ShopManager
    logger.info("Modules du jeu importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules du jeu: {e}")
    sys.exit(1)

def test_db_loading():
    """
    Teste le chargement de la base de données par le jeu
    """
    logger.info("Démarrage du test de chargement de la base de données")
    
    # Initialiser le world loader
    try:
        world_loader = WorldLoader()
        db_path = world_loader.db_path
        logger.info(f"WorldLoader initialisé avec la base de données: {db_path}")
        logger.info(f"Le fichier existe: {db_path.exists()}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du WorldLoader: {e}")
        return False
    
    # Tester le chargement des mondes disponibles
    try:
        worlds = world_loader.get_available_worlds()
        if worlds:
            logger.info(f"Mondes disponibles: {len(worlds)}")
            for world in worlds:
                logger.info(f"Monde trouvé: {world['name']} (ID: {world['id']})")
        else:
            logger.warning("Aucun monde trouvé dans la base de données")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des mondes: {e}")
        return False
    
    # Initialiser le shop manager
    try:
        shop_manager = ShopManager(world_loader)
        logger.info("ShopManager initialisé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du ShopManager: {e}")
        return False
    
    # Tester le chargement des boutiques
    try:
        shop_manager.load_shops()
        shops = shop_manager.shops
        if shops:
            logger.info(f"Boutiques chargées: {len(shops)}")
            
            # Pour éviter trop de journalisation, nous allons limiter l'affichage à 5 boutiques
            count = 0
            for shop_id, shop in shops.items():
                count += 1
                if count > 5:
                    logger.info(f"... et {len(shops) - 5} autres boutiques")
                    break
                
                logger.info(f"Boutique: {shop.name} (Type: {shop.shop_type})")
                
                # Afficher les articles de la boutique (limités à 3 pour clarté)
                logger.info(f"Inventaire de la boutique {shop.name}: {len(shop.inventory)} articles")
                for i, item in enumerate(shop.inventory[:3]):
                    if hasattr(item, 'name') and hasattr(item, 'id'):
                        logger.info(f"  Article {i+1}: {item.name} (ID: {item.id}, Type: {type(item).__name__})")
                        
                        # Si c'est un vêtement, vérifier les attributs spécifiques que nous avons modifiés
                        if hasattr(item, 'clothing_type'):
                            logger.info(f"    Type de vêtement: {item.clothing_type}")
                            if hasattr(item, 'stats') and item.stats:
                                logger.info(f"    Stats: {item.stats}")
                            else:
                                logger.warning(f"    Vêtement sans stats: {item.id}")
                            
                            if hasattr(item, 'slots') and item.slots:
                                logger.info(f"    Slots: {item.slots}")
                            else:
                                logger.warning(f"    Vêtement sans slots: {item.id}")
                    else:
                        logger.warning(f"  Article {i+1}: Type non reconnu - {type(item)}")
                    
                    if i >= 2 and len(shop.inventory) > 3:
                        logger.info(f"    ... et {len(shop.inventory) - 3} autres articles")
                        break
        else:
            logger.warning("Aucune boutique chargée")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des boutiques: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Test direct de chargement d'articles depuis la base de données
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Vérifier les tables d'objets
        tables = ['weapon_items', 'clothing_items', 'hardware_items', 'consumable_items']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"Table {table} contient {count} objets")
            
            if count > 0:
                # Récupérer un exemple d'objet
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                columns = [col[0] for col in cursor.description]
                item_data = dict(zip(columns, cursor.fetchone()))
                
                # Vérifier la structure des métadonnées
                if 'metadata' in item_data and item_data['metadata']:
                    try:
                        metadata = json.loads(item_data['metadata'])
                        logger.info(f"Structure des métadonnées pour {table}: {list(metadata.keys())}")
                    except json.JSONDecodeError:
                        logger.warning(f"Métadonnées non valides dans {table}")
                
                # Si c'est un vêtement, vérifier les colonnes stats et slots
                if table == 'clothing_items':
                    if 'stats' in item_data:
                        logger.info(f"Colonne 'stats' présente dans {table}")
                    else:
                        logger.warning(f"Colonne 'stats' manquante dans {table}")
                    
                    if 'slots' in item_data:
                        logger.info(f"Colonne 'slots' présente dans {table}")
                    else:
                        logger.warning(f"Colonne 'slots' manquante dans {table}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de l'accès direct à la base de données: {e}")
        return False
    
    logger.info("Test de chargement de la base de données terminé avec succès")
    return True

if __name__ == "__main__":
    success = test_db_loading()
    if success:
        print("\n[SUCCES] La base de données a été chargée avec succès par le jeu")
    else:
        print("\n[ECHEC] Erreur lors du chargement de la base de données par le jeu")
