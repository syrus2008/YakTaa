import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from yaktaa.ui.widgets.simple_shop_selector import SimpleShopSelector
from yaktaa.items.shop import Shop

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Shop Selector")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Créer le sélecteur de boutique
        self.shop_selector = SimpleShopSelector()
        layout.addWidget(self.shop_selector)
        
        # Créer quelques boutiques de test
        shops = [
            Shop('1', 'Boutique Test', 'TECH', 'Une boutique de test', {}),
            Shop('2', 'Autre Boutique', 'FOOD', 'Une autre boutique', {}),
            Shop('3', 'Magasin d\'armes', 'WEAPONS', 'Vente d\'armes', {})
        ]
        
        # Définir les boutiques dans le sélecteur
        logger.info("Définition des boutiques dans le sélecteur")
        self.shop_selector.set_shops(shops)
        
        # Vérifier les boutiques filtrées
        logger.info(f"Boutiques filtrées: {self.shop_selector.filtered_shops}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
