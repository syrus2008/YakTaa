#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ShopDebugger")

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    logger.info("Importation des modules...")
    from yaktaa.items.shop import Shop, ShopType
    # Nous n'avons pas besoin du ShopManager pour ce test, on le commente
    # from yaktaa.items.shop_manager import ShopManager
    from yaktaa.ui.widgets.simple_shop_selector import SimpleShopSelector
    from yaktaa.ui.theme import Theme
    
    class ShopDebugWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Débogueur d'animation de boutiques")
            self.resize(800, 600)
            
            # Configuration de l'interface
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Initialiser le Theme s'il existe
            try:
                self.theme = Theme("cyberpunk_dark")
                logger.info("Theme initialisé avec succès")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser Theme: {str(e)}")
                logger.warning("Poursuite sans thème...")
            
            # Créer un bouton pour déclencher l'affichage des boutiques
            self.load_button = QPushButton("Charger les boutiques")
            self.load_button.clicked.connect(self.load_shops)
            layout.addWidget(self.load_button)
            
            # Créer le widget de sélection de boutiques
            self.shop_selector = SimpleShopSelector()
            layout.addWidget(self.shop_selector)
            
            # Nous n'avons pas besoin du ShopManager pour ce test
            # self.shop_manager = ShopManager()
            
            logger.info("Fenêtre d'interface initialisée")
            
        def load_shops(self):
            """Charge toutes les boutiques disponibles et les affiche"""
            try:
                logger.info("Début du chargement des boutiques")
                
                # Créons quelques boutiques de test
                shops = []
                
                # Boutique 1
                shop1 = Shop(
                    shop_id="shop1",
                    name="Tech Store",
                    shop_type=ShopType.TECH,
                    description="Une boutique d'électronique high-tech",
                    city_id="loc1"
                )
                shops.append(shop1)
                
                # Boutique 2
                shop2 = Shop(
                    shop_id="shop2",
                    name="Weapons Dealer",
                    shop_type=ShopType.WEAPONS,
                    description="Vente d'armes et de munitions",
                    city_id="loc1"
                )
                shops.append(shop2)
                
                # Boutique 3
                shop3 = Shop(
                    shop_id="shop3",
                    name="Med Clinic",
                    shop_type=ShopType.DRUGS,
                    description="Fournitures médicales et implants",
                    city_id="loc1"
                )
                shops.append(shop3)
                
                # Boutique 4
                shop4 = Shop(
                    shop_id="shop4",
                    name="Black Market",
                    shop_type=ShopType.BLACK_MARKET,
                    description="Marchandises illégales et rares",
                    city_id="loc1"
                )
                shops.append(shop4)
                
                # Boutique 5
                shop5 = Shop(
                    shop_id="shop5",
                    name="Implant Clinic",
                    shop_type=ShopType.IMPLANTS,
                    description="Clinique spécialisée dans les implants cybernétiques",
                    city_id="loc1"
                )
                shops.append(shop5)
                
                logger.info(f"Essai d'affichage de {len(shops)} boutiques de test")
                
                # Utiliser un timer pour débugger l'affichage étape par étape
                def step1():
                    logger.info("ÉTAPE 1: Nettoyage de l'affichage")
                    self.shop_selector._clear_shop_list()
                    QTimer.singleShot(500, step2)
                
                def step2():
                    logger.info("ÉTAPE 2: Définition des boutiques")
                    self.shop_selector.shops = shops
                    QTimer.singleShot(500, step3)
                
                def step3():
                    logger.info("ÉTAPE 3: Filtrage des boutiques")
                    filtered_shops = self.shop_selector.filter_shops(shops)
                    logger.info(f"Filtrage terminé, {len(filtered_shops)} boutiques après filtrage")
                    QTimer.singleShot(500, step4)
                
                def step4():
                    logger.info("ÉTAPE 4: Organisation des boutiques par type")
                    shops_by_type = {}
                    for shop in shops:
                        shop_type = shop.shop_type.name.capitalize()
                        if shop_type not in shops_by_type:
                            shops_by_type[shop_type] = []
                        shops_by_type[shop_type].append(shop)
                    logger.info(f"{len(shops_by_type)} types de boutiques trouvés: {', '.join(shops_by_type.keys())}")
                    QTimer.singleShot(500, step5)
                
                def step5():
                    logger.info("ÉTAPE 5: Démarrage de refresh_shops")
                    try:
                        self.shop_selector.refresh_shops()
                        logger.info("refresh_shops terminé avec succès")
                    except Exception as e:
                        logger.error(f"Erreur lors du rafraîchissement des boutiques: {str(e)}")
                        logger.error(traceback.format_exc())
                
                # Démarrer la séquence
                logger.info("Démarrage de la séquence de test")
                QTimer.singleShot(500, step1)
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement des boutiques: {str(e)}")
                logger.error(traceback.format_exc())
    
    def main():
        app = QApplication(sys.argv)
        window = ShopDebugWindow()
        window.show()
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    logger.error(f"Erreur critique: {str(e)}")
    logger.error(f"Détails: {traceback.format_exc()}")
