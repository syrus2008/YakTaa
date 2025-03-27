"""
Gestionnaire d'interface utilisateur pour YakTaa
Ce module gère toutes les fenêtres et widgets de l'interface.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Union, Type, TYPE_CHECKING
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QMessageBox
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSize

# Import conditionnel pour éviter les imports circulaires
if TYPE_CHECKING:
    from yaktaa.core.game import Game
    from yaktaa.ui.widgets.terminal import TerminalWidget
    from yaktaa.ui.widgets.inventory import InventoryWidget
    from yaktaa.ui.widgets.hacking_minigames import HackingMinigameBase

logger = logging.getLogger("YakTaa.UI.UIManager")

class UIManager(QObject):
    """Gestionnaire des interfaces utilisateur du jeu"""
    
    # Signaux
    hacking_minigame_completed = pyqtSignal(bool, str)  # (success, target)
    
    def __init__(self, main_window=None, game=None):
        """
        Initialise le gestionnaire d'UI
        
        Args:
            main_window: Référence la fenêtre principale
            game: Instance du jeu (optionnel)
        """
        super().__init__()
        self.game = game
        
        # Fenêtres principales
        self.main_window = main_window
        self.windows = {}
        
        # Widgets
        self.widgets = {}
        
        # Mini-jeux actifs
        self.active_minigames = {}
        
        logger.info("Gestionnaire d'UI initialisé")
    
    def setup_main_window(self, window: QMainWindow) -> None:
        """
        Configure la fenêtre principale
        
        Args:
            window: Fenêtre principale du jeu
        """
        self.main_window = window
        logger.info("Fenêtre principale configurée")
    
    def register_widget(self, name: str, widget: QWidget) -> None:
        """
        Enregistre un widget dans le gestionnaire
        
        Args:
            name: Nom du widget
            widget: Instance du widget
        """
        self.widgets[name] = widget
        logger.debug(f"Widget '{name}' enregistré")
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """
        Récupère un widget par son nom
        
        Args:
            name: Nom du widget
            
        Returns:
            QWidget: Le widget demandé, ou None s'il n'existe pas
        """
        return self.widgets.get(name)
    
    def show_dialog(self, dialog_type: Type[QDialog], **kwargs) -> Optional[int]:
        """
        Affiche une boîte de dialogue
        
        Args:
            dialog_type: Type de dialogue à afficher
            **kwargs: Arguments à passer au constructeur du dialogue
            
        Returns:
            int: Code de retour du dialogue
        """
        dialog = dialog_type(parent=self.main_window, **kwargs)
        return dialog.exec()
    
    def show_message(self, title: str, message: str, detailed_text: str = None) -> None:
        """
        Affiche un message dans une boîte de dialogue
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message principal
            detailed_text: Texte détaillé (optionnel)
        """
        if not self.main_window:
            logger.warning(f"UIManager: Impossible d'afficher le message: {title} - {message}")
            return
            
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
            
        # Style cyberpunk
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #121212;
                color: #00CCFF;
            }
            QPushButton {
                background-color: #333333;
                color: #00CCFF;
                border: 1px solid #00CCFF;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
                border: 1px solid #00FFFF;
                color: #00FFFF;
            }
        """)
        
        msg_box.exec()
    
    def show_hacking_minigame(self, minigame: Any) -> None:
        """
        Affiche un mini-jeu de hacking
        
        Args:
            minigame: Instance du mini-jeu à afficher
        """
        if not minigame:
            logger.error("Tentative d'afficher un mini-jeu None")
            return
        
        # Vérifier que le mini-jeu a tous les attributs requis
        if not hasattr(minigame, 'target_name'):
            logger.error("Le mini-jeu n'a pas d'attribut target_name")
            return
            
        # Configurer le parent et les connexions
        minigame.setParent(self.main_window)
        
        # Connecter le signal de complétion du mini-jeu
        if hasattr(minigame, 'puzzle_completed'):
            minigame.puzzle_completed.connect(
                lambda success, time_used: self._on_minigame_completed(success, minigame.target_name, time_used)
            )
        else:
            logger.error("Le mini-jeu n'a pas de signal puzzle_completed")
            return
        
        # Stocker le mini-jeu actif
        target = minigame.target_name
        self.active_minigames[target] = minigame
        
        # Définir le style comme une fenêtre de dialogue
        minigame.setWindowFlags(Qt.WindowType.Dialog)
        minigame.setWindowTitle(f"Hack: {target}")
        
        # Ajuster la taille en fonction du type de mini-jeu
        preferred_size = getattr(minigame, 'preferred_size', None)
        if preferred_size:
            minigame.resize(preferred_size)
        else:
            minigame.resize(QSize(800, 600))
        
        # Centrer le mini-jeu par rapport à la fenêtre principale
        if self.main_window:
            geometry = self.main_window.geometry()
            x = (geometry.width() - minigame.width()) // 2 + geometry.x()
            y = (geometry.height() - minigame.height()) // 2 + geometry.y()
            minigame.move(x, y)
        
        # Afficher le mini-jeu
        minigame.show()
        minigame.activateWindow()
        logger.info(f"Mini-jeu de hacking affiché pour la cible: {target}")
    
    def _on_minigame_completed(self, success: bool, target: str, time_used: float = 0) -> None:
        """
        Appelé lorsqu'un mini-jeu est terminé
        
        Args:
            success: True si le hack a réussi, False sinon
            target: Cible du hack
            time_used: Temps utilisé pour compléter le mini-jeu (en secondes)
        """
        logger.info(f"Mini-jeu de hacking terminé pour {target} (réussite: {success}, temps: {time_used:.2f}s)")
        
        # Émettre le signal de complétion
        self.hacking_minigame_completed.emit(success, target)
        
        # Nettoyer le mini-jeu
        if target in self.active_minigames:
            minigame = self.active_minigames.pop(target)
            minigame.deleteLater()
    
    def close_hacking_minigame(self, target: str) -> None:
        """
        Ferme un mini-jeu de hacking
        
        Args:
            target: Cible du hack
        """
        if target in self.active_minigames:
            minigame = self.active_minigames.pop(target)
            minigame.close()
            minigame.deleteLater()
            logger.info(f"Mini-jeu de hacking fermé pour la cible: {target}")
    
    def close_all_hacking_minigames(self) -> None:
        """Ferme tous les mini-jeux de hacking actifs"""
        for target, minigame in list(self.active_minigames.items()):
            minigame.close()
            minigame.deleteLater()
        self.active_minigames.clear()
        logger.info("Tous les mini-jeux de hacking ont été fermés")
    
    def show_combat_interface(self, enemies, environment=None):
        """
        Affiche l'interface de combat avec les ennemis spécifiés
        
        Args:
            enemies: Liste des ennemis à combattre
            environment: Propriétés de l'environnement (optionnel)
            
        Returns:
            True si l'interface a été affichée, False sinon
        """
        if not self.game:
            logger.error("UIManager: Impossible d'afficher l'interface de combat, pas de référence au jeu")
            return False
            
        return self.game.start_combat(enemies, environment)
