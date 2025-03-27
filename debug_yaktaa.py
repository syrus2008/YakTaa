#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de débogage pour trouver la source de l'erreur "unhashable type: 'set'"
"""

import os
import sys
import traceback
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='debug_yaktaa.log',
    filemode='w'
)

logger = logging.getLogger("YakTaa.Debug")

def main():
    try:
        # Importation conditionnelle pour tester chaque module individuellement
        logger.info("Test d'importation des modules essentiels...")
        
        # Test 1: Import de la classe Game
        logger.info("Test 1: Import de la classe Game")
        from yaktaa.game import Game
        logger.info("Game importé avec succès")
        
        # Test 2: Import du gestionnaire de monde
        logger.info("Test 2: Import du gestionnaire de monde")
        from yaktaa.world.world_manager import WorldManager
        logger.info("WorldManager importé avec succès")
        
        # Test 3: Instanciation du gestionnaire de monde
        logger.info("Test 3: Instanciation du gestionnaire de monde")
        world_manager = WorldManager()
        logger.info("WorldManager instancié avec succès")
        
        # Test 4: Import de la boutique
        logger.info("Test 4: Import du module de boutique")
        from yaktaa.items.shop_manager import ShopManager
        logger.info("ShopManager importé avec succès")
        
        # Test 5: Import du chargeur de monde
        logger.info("Test 5: Import du chargeur de monde")
        from yaktaa.world.world_loader import WorldLoader
        logger.info("WorldLoader importé avec succès")
        
        # Test 6: Instanciation du jeu complet
        logger.info("Test 6: Instanciation du jeu complet")
        game = Game()
        logger.info("Game instancié avec succès")
        
        # Test 7: Test des structures de données
        logger.info("Test 7: Test des structures de données")
        # Vérifier si un ensemble est utilisé comme clé de dictionnaire quelque part
        test_dict = {}
        test_set = set([1, 2, 3])
        
        try:
            logger.info("Test d'utilisation d'un set comme clé")
            test_dict[test_set] = "Ceci va planter"
        except TypeError as e:
            logger.info(f"Erreur attendue: {str(e)}")
        
        logger.info("Tous les tests de base réussis !")
        logger.info("Démarrage de l'application principale...")
        
        # Import de l'application principale
        import yaktaa.main
        
    except Exception as e:
        logger.error(f"Erreur lors des tests: {str(e)}")
        logger.error(f"Traceback complet: {traceback.format_exc()}")
        print(f"ERREUR: {str(e)}")
        print(f"Consultez le fichier debug_yaktaa.log pour plus de détails.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
