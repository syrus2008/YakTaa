#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de débogage pour l'interface des boutiques
Ce script teste l'affichage des boutiques sans lancer l'application complète
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ShopUIDebugger")

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt

try:
    # Essayer d'importer les modules nécessaires
    logger.info("[DEBUG_SHOP_UI] Importation des modules...")
    
    from yaktaa.world.world_loader import WorldLoader
    from yaktaa.items.shop_manager import ShopManager, Shop
    from yaktaa.items.item_factory import ItemFactory
    from yaktaa.ui.widgets.simple_shop_selector import SimpleShopSelector
    from yaktaa.ui.widgets.shop_widget import ShopWidget
    
    logger.info("[DEBUG_SHOP_UI] Modules importés avec succès")
    
    class SimpleItemFactory:
        """Implémentation simplifiée de ItemFactory pour le débogage"""
        def create_item(self, item_type, item_id, **kwargs):
            return {
                "id": item_id,
                "type": item_type,
                "name": f"Item {item_id}",
                "description": "Item de test",
                "price": 100,
                **kwargs
            }
    
    class DebugShopWindow(QMainWindow):
        """Fenêtre de débogage pour les boutiques"""
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Débogage des boutiques")
            self.resize(800, 600)
            
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Étape 1: Initialiser le WorldLoader
            logger.info("[DEBUG_SHOP_UI] Initialisation du WorldLoader...")
            self.world_loader = WorldLoader()
            logger.info("[DEBUG_SHOP_UI] WorldLoader initialisé avec succès")
            
            # Étape 2: Initialiser le ShopManager
            logger.info("[DEBUG_SHOP_UI] Initialisation du ShopManager...")
            self.shop_manager = ShopManager(self.world_loader)
            logger.info("[DEBUG_SHOP_UI] ShopManager initialisé avec succès")
            
            # Étape 3: Créer et affecter un ItemFactory
            logger.info("[DEBUG_SHOP_UI] Création du SimpleItemFactory...")
            self.item_factory = SimpleItemFactory()
            self.shop_manager.item_factory = self.item_factory
            logger.info("[DEBUG_SHOP_UI] ItemFactory créé et affecté au ShopManager")
            
            # Étape 4: Charger les boutiques
            logger.info("[DEBUG_SHOP_UI] Tentative de chargement des boutiques...")
            try:
                shops = self.shop_manager.load_shops()
                logger.info(f"[DEBUG_SHOP_UI] Chargement des boutiques réussi. {len(shops)} boutiques chargées.")
                
                for shop in shops:
                    logger.info(f"[DEBUG_SHOP_UI] Boutique ID: {shop.id}, Nom: {shop.name}, Type: {shop.shop_type}")
            except Exception as e:
                logger.error(f"[DEBUG_SHOP_UI] Erreur lors du chargement des boutiques: {str(e)}")
                import traceback
                logger.error(f"[DEBUG_SHOP_UI] Détails: {traceback.format_exc()}")
                shops = []
            
            # Étape 5: Tester l'affichage des boutiques avec le SimpleShopSelector
            logger.info("[DEBUG_SHOP_UI] Création du SimpleShopSelector...")
            try:
                self.shop_selector = SimpleShopSelector()
                layout.addWidget(self.shop_selector)
                logger.info("[DEBUG_SHOP_UI] SimpleShopSelector créé avec succès")
                
                # Afficher les boutiques
                logger.info("[DEBUG_SHOP_UI] Tentative d'affichage des boutiques...")
                try:
                    self.shop_selector.set_shops(shops)
                    logger.info("[DEBUG_SHOP_UI] Affichage des boutiques réussi")
                except Exception as e:
                    logger.error(f"[DEBUG_SHOP_UI] Erreur lors de l'affichage des boutiques: {str(e)}")
                    logger.error(f"[DEBUG_SHOP_UI] Détails: {traceback.format_exc()}")
            except Exception as e:
                logger.error(f"[DEBUG_SHOP_UI] Erreur lors de la création du SimpleShopSelector: {str(e)}")
                logger.error(f"[DEBUG_SHOP_UI] Détails: {traceback.format_exc()}")
                
                # Afficher un message d'erreur
                error_label = QLabel(f"Erreur: {str(e)}")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(error_label)

    # Fonction principale
    def main():
        app = QApplication(sys.argv)
        window = DebugShopWindow()
        window.show()
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()
        
except Exception as e:
    logger.error(f"[DEBUG_SHOP_UI] Erreur critique: {str(e)}")
    logger.error(f"[DEBUG_SHOP_UI] Détails: {traceback.format_exc()}")
