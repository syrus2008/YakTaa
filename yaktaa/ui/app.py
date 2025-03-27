"""
Module principal de l'interface utilisateur du jeu YakTaa basé sur PyQt6
"""

import sys
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QFontDatabase

from yaktaa.core.game import Game
from yaktaa.ui.screens.main_menu import MainMenuScreen
from yaktaa.ui.screens.game_screen import GameScreen
from yaktaa.ui.screens.loading_screen import LoadingScreen
from yaktaa.ui.screens.settings_screen import SettingsScreen
from yaktaa.ui.theme import Theme

logger = logging.getLogger("YakTaa.UI.App")

class Application(QApplication):
    """Classe principale de l'application PyQt6 pour YakTaa"""
    
    def __init__(self, argv):
        """Initialise l'application PyQt6"""
        super().__init__(argv)
        
        # Configuration de l'application
        self.setApplicationName("YakTaa")
        self.setApplicationVersion("0.1.0")
        self.setOrganizationName("YakTaa Team")
        
        # Chargement des polices
        self._load_fonts()
        
        # Chargement du thème
        self.theme = Theme()
        self.theme.apply_to_application(self)
        
        # Fenêtre principale
        self.main_window = MainWindow()
        
        logger.info("Application PyQt6 initialisée")
    
    def _load_fonts(self) -> None:
        """Charge les polices personnalisées"""
        try:
            # Liste des polices à charger
            fonts = [
                "assets/fonts/CascadiaCode.ttf",
                "assets/fonts/Cyberpunk.ttf",
                "assets/fonts/NeonRetro.ttf"
            ]
            
            # Chargement des polices
            for font_path in fonts:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    logger.warning(f"Impossible de charger la police: {font_path}")
                else:
                    logger.debug(f"Police chargée: {font_path}")
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des polices: {str(e)}", exc_info=True)
    
    def run(self, game: Game) -> int:
        """Lance l'application et retourne le code de sortie"""
        try:
            # Initialisation de la fenêtre principale avec le jeu
            self.main_window.initialize(game)
            self.main_window.show()
            
            # Lancement de la boucle d'événements
            return self.exec()
            
        except Exception as e:
            logger.error(f"Erreur critique lors de l'exécution de l'application: {str(e)}", exc_info=True)
            return 1


class MainWindow(QMainWindow):
    """Fenêtre principale du jeu YakTaa"""
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        super().__init__()
        
        # Configuration de la fenêtre
        self.setWindowTitle("YakTaa")
        self.setWindowIcon(QIcon("assets/images/icon.png"))
        self.setMinimumSize(QSize(1024, 768))
        
        # Gestionnaire d'écrans
        self.screen_stack = QStackedWidget(self)
        self.setCentralWidget(self.screen_stack)
        
        # Référence au jeu
        self.game = None
        
        # Timer de mise à jour
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update)
        
        # Écrans du jeu
        self.screens = {}
        
        logger.info("Fenêtre principale initialisée")
    
    def initialize(self, game: Game) -> None:
        """Initialise la fenêtre avec le jeu"""
        self.game = game
        
        # Création des écrans
        self._create_screens()
        
        # Affichage de l'écran de menu principal
        self.show_screen("main_menu")
        
        # Démarrage du timer de mise à jour
        self.update_timer.start(16)  # ~60 FPS
        
        logger.info("Fenêtre principale initialisée avec le jeu")
    
    def _create_screens(self) -> None:
        """Crée les différents écrans du jeu"""
        try:
            # Écran de menu principal
            main_menu = MainMenuScreen(self.game, self)
            self.screens["main_menu"] = main_menu
            self.screen_stack.addWidget(main_menu)
            
            # Écran de chargement
            loading = LoadingScreen(self.game, self)
            self.screens["loading"] = loading
            self.screen_stack.addWidget(loading)
            
            # Écran de jeu principal
            game_screen = GameScreen(self.game, self)
            self.screens["game"] = game_screen
            self.screen_stack.addWidget(game_screen)
            
            # Écran de paramètres
            settings = SettingsScreen(self.game, self)
            self.screens["settings"] = settings
            self.screen_stack.addWidget(settings)
            
            logger.info("Écrans du jeu créés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des écrans: {str(e)}", exc_info=True)
    
    def show_screen(self, screen_name: str) -> bool:
        """Affiche un écran spécifique"""
        if screen_name in self.screens:
            screen = self.screens[screen_name]
            screen.on_show()
            self.screen_stack.setCurrentWidget(screen)
            logger.info(f"Écran affiché: {screen_name}")
            return True
        else:
            logger.error(f"Écran inconnu: {screen_name}")
            return False
    
    def _update(self) -> None:
        """Met à jour le jeu et l'interface utilisateur"""
        if self.game:
            # Calcul du delta time (temps écoulé depuis la dernière mise à jour)
            delta_time = 1.0 / self.update_timer.interval() * 1000
            
            # Mise à jour du jeu
            self.game.update(delta_time)
            
            # Mise à jour de l'écran actuel
            current_screen = self.screen_stack.currentWidget()
            if hasattr(current_screen, "update_ui"):
                current_screen.update_ui(delta_time)
    
    def closeEvent(self, event):
        """Gère l'événement de fermeture de la fenêtre"""
        if self.game:
            # Arrêt propre du jeu
            self.game.quit()
        
        # Arrêt du timer de mise à jour
        self.update_timer.stop()
        
        # Acceptation de l'événement de fermeture
        event.accept()
        
        logger.info("Fermeture de la fenêtre principale")
