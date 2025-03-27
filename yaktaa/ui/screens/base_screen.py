"""
Module contenant la classe de base pour tous les écrans du jeu YakTaa
"""

import logging
from typing import Optional, Any

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.BaseScreen")

class BaseScreen(QWidget):
    """Classe de base pour tous les écrans du jeu"""
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise un écran de base"""
        super().__init__(parent)
        
        # Référence au jeu
        self.game = game
        
        # Référence à la fenêtre principale (parent)
        self.main_window = parent
        
        # Mise en page principale
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Initialisation de l'interface utilisateur
        self._init_ui()
        
        logger.debug(f"Écran initialisé: {self.__class__.__name__}")
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur de l'écran (à surcharger)"""
        # Cette méthode doit être surchargée par les classes dérivées
        pass
    
    def on_show(self) -> None:
        """Appelé lorsque l'écran est affiché (à surcharger)"""
        # Cette méthode doit être surchargée par les classes dérivées
        logger.debug(f"Écran affiché: {self.__class__.__name__}")
    
    def on_hide(self) -> None:
        """Appelé lorsque l'écran est masqué (à surcharger)"""
        # Cette méthode doit être surchargée par les classes dérivées
        logger.debug(f"Écran masqué: {self.__class__.__name__}")
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur (à surcharger)"""
        # Cette méthode doit être surchargée par les classes dérivées
        pass
    
    def create_heading(self, text: str, level: int = 1) -> QLabel:
        """Crée un en-tête avec le style approprié"""
        heading = QLabel(text, self)
        heading.setProperty("heading", "true")
        
        # Taille de police en fonction du niveau d'en-tête
        font_sizes = {1: 28, 2: 24, 3: 20, 4: 16}
        font = heading.font()
        font.setPointSize(font_sizes.get(level, 16))
        font.setBold(True)
        heading.setFont(font)
        
        # Alignement
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return heading
    
    def show_screen(self, screen_name: str) -> bool:
        """Change l'écran affiché"""
        if self.main_window:
            self.on_hide()
            return self.main_window.show_screen(screen_name)
        return False
