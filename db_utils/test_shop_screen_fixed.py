import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from yaktaa.ui.screens.shop_screen import ShopScreen
from yaktaa.items.shop import Shop
from yaktaa.items.shop_manager import ShopManager
from yaktaa.world.world_loader import WorldLoader

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Shop Screen")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Créer un mock Game avec un ShopManager
        class MockGame:
            def __init__(self):
                self.world_loader = WorldLoader()
                self.shop_manager = ShopManager(self.world_loader)
                self.player = MockPlayer()
                
        class MockPlayer:
            def __init__(self):
                self.credits = 5000
                self.inventory = {}
        
        # Créer le jeu mock
        self.game = MockGame()
        
        # Créer quelques boutiques de test
        self.shops = [
            Shop('1', 'Boutique Test', 'TECH', 'Une boutique de test'),
            Shop('2', 'Autre Boutique', 'FOOD', 'Une autre boutique'),
            Shop('3', 'Magasin d\'armes', 'WEAPONS', 'Vente d\'armes')
        ]
        
        # Créer l'écran de boutique
        self.shop_screen = ShopScreen(self.game)
        layout.addWidget(self.shop_screen)
        
        # Afficher les boutiques directement
        self.shop_screen.display_shops(self.shops)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
