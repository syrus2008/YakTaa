#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de chargement des boutiques
Ce script teste le chargement des boutiques pour différentes localisations
"""

import os
import sys
import logging
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_shop_loading')

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules nécessaires
try:
    from yaktaa.world.world_loader import WorldLoader
    from yaktaa.items.shop_manager import ShopManager, Shop
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

def test_shop_loading():
    """
    Teste le chargement des boutiques pour différentes localisations.
    """
    try:
        # Créer le WorldLoader et le ShopManager
        logger.info("Initialisation du WorldLoader...")
        world_loader = WorldLoader()
        
        logger.info("Initialisation du ShopManager...")
        shop_manager = ShopManager(world_loader)
        
        # Tester différentes localisations
        test_locations = [
            'tokyo',
            'neo-tokyo',
            'default',
            'lagos',
            '2256d4e4-5635-47f1-87ed-61ea4ae79f1f'  # ID direct que nous avons utilisé comme alias pour Tokyo
        ]
        
        # Tester le chargement des boutiques pour chaque localisation
        for location in test_locations:
            logger.info(f"\n=== Test pour la localisation: {location} ===")
            
            # Obtenir l'ID de la ville
            city_id = shop_manager.get_city_id_from_location(location)
            logger.info(f"ID de ville obtenu: {city_id}")
            
            # Récupérer les boutiques
            shops = shop_manager.get_shops_by_location(location)
            logger.info(f"Nombre de boutiques trouvées: {len(shops)}")
            
            # Afficher les détails des boutiques trouvées
            for i, shop in enumerate(shops):
                logger.info(f"  Boutique {i+1}: ID={shop.id}, Nom={shop.name}, Type={shop.shop_type}")
                
            logger.info(f"=== Fin du test pour {location} ===\n")
            
        # Analyser la base de données
        logger.info("\n=== Analyse de la structure de la base de données ===")
        conn = world_loader.get_connection()
        cursor = conn.cursor()
        
        # Vérifier les tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"Tables trouvées: {[table[0] for table in tables]}")
        
        # Vérifier la structure de la table shops
        if any(table[0] == 'shops' for table in tables):
            cursor.execute("PRAGMA table_info(shops)")
            columns = cursor.fetchall()
            logger.info(f"Structure de la table shops: {[col[1] for col in columns]}")
            
            # Compter le nombre de boutiques
            cursor.execute("SELECT COUNT(*) FROM shops")
            count = cursor.fetchone()[0]
            logger.info(f"Nombre total de boutiques dans la base: {count}")
            
            # Obtenir quelques exemples
            cursor.execute("SELECT * FROM shops LIMIT 5")
            samples = cursor.fetchall()
            logger.info(f"Exemples de boutiques:")
            for shop in samples:
                shop_dict = {columns[i][1]: shop[i] for i in range(len(columns))}
                logger.info(f"  {shop_dict}")
        
        # Vérifier la structure de la table locations
        if any(table[0] == 'locations' for table in tables):
            cursor.execute("PRAGMA table_info(locations)")
            columns = cursor.fetchall()
            logger.info(f"Structure de la table locations: {[col[1] for col in columns]}")
            
            # Compter le nombre de localisations
            cursor.execute("SELECT COUNT(*) FROM locations")
            count = cursor.fetchone()[0]
            logger.info(f"Nombre total de localisations dans la base: {count}")
            
            # Rechercher tokyo et les emplacements similaires
            cursor.execute("SELECT * FROM locations WHERE name LIKE '%tokyo%' OR name LIKE '%Tokyo%'")
            tokyo_locations = cursor.fetchall()
            logger.info(f"Emplacements contenant 'tokyo': {len(tokyo_locations)}")
            for loc in tokyo_locations:
                loc_dict = {columns[i][1]: loc[i] for i in range(len(columns))}
                logger.info(f"  {loc_dict}")
                
            # Rechercher 'lagos' qui est utilisé comme fallback
            cursor.execute("SELECT * FROM locations WHERE id = '2256d4e4-5635-47f1-87ed-61ea4ae79f1f' OR name LIKE '%lagos%'")
            lagos_locations = cursor.fetchall()
            logger.info(f"Emplacements Lagos: {len(lagos_locations)}")
            for loc in lagos_locations:
                loc_dict = {columns[i][1]: loc[i] for i in range(len(columns))}
                logger.info(f"  {loc_dict}")
        
        conn.close()
        logger.info("=== Fin de l'analyse de la base de données ===\n")
        
        logger.info("Tests terminés avec succès")
    except Exception as e:
        logger.error(f"Erreur lors des tests: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Démarrage des tests de chargement des boutiques")
    test_shop_loading()
