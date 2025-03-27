#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour le SimpleShopSelector.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from yaktaa.ui.widgets.simple_shop_selector import SimpleShopSelector
from yaktaa.items.shop import Shop, ShopType

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test SimpleShopSelector")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Créer le sélecteur de boutiques
        self.shop_selector = SimpleShopSelector()
        main_layout.addWidget(self.shop_selector)
        
        # Créer quelques boutiques de test
        test_shops = [
            Shop(
                shop_id="shop1",
                name="Armurerie CyberTech",
                shop_type=ShopType.WEAPONS,
                description="Armes de haute technologie"
            ),
            Shop(
                shop_id="shop2",
                name="Pharmacie NeuroChem",
                shop_type=ShopType.DRUGS,
                description="Médicaments et stimulants"
            ),
            Shop(
                shop_id="shop3",
                name="Marché Noir du Quartier Est",
                shop_type=ShopType.BLACK_MARKET,
                description="Tout ce qui est illégal"
            ),
            Shop(
                shop_id="shop4",
                name="Boutique d'implants CyberMod",
                shop_type=ShopType.IMPLANTS,
                description="Améliorations cybernétiques"
            )
        ]
        
        # Ajouter la propriété is_legal manuellement
        test_shops[0].is_legal = True
        test_shops[1].is_legal = True
        test_shops[2].is_legal = False
        test_shops[3].is_legal = True
        
        # Définir les boutiques dans le sélecteur
        self.shop_selector.set_shops(test_shops)
        
        # Connecter le signal de sélection de boutique
        self.shop_selector.shop_selected.connect(self.on_shop_selected)
    
    def on_shop_selected(self, shop_id):
        print(f"Boutique sélectionnée: {shop_id}")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
