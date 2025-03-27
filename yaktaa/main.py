#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YakTaa - Jeu de rôle cyberpunk immersif
Point d'entrée principal de l'application
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSplitter, QFrame, QLabel, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont
import traceback

# Importation des modules du jeu avec gestion des erreurs
try:
    from .core.game import Game
    from .core.config import Config
    from .ui.ui_manager import UIManager
except ImportError:
    # Fallback pour les importations directes (sans package)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from yaktaa.core.game import Game
        from yaktaa.core.config import Config
        from yaktaa.ui.ui_manager import UIManager
    except ImportError:
        # Classes minimales de remplacement
        class Game:
            def __init__(self):
                self.running = False
                self.player = None
                
            def set_ui_manager(self, ui_manager):
                self.ui_manager = ui_manager
                
        class Config:
            def __init__(self):
                self.config_data = {}
                
            def get(self, key, default=None):
                return self.config_data.get(key, default)
                
        class UIManager:
            def __init__(self, main_window, game):
                self.main_window = main_window
                self.game = game
                
            def show_message(self, title, message):
                print(f"{title}: {message}")
                
            def show_hacking_minigame(self, minigame_type, params):
                print(f"Mini-jeu de hacking de type {minigame_type}")
                return False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / 'yaktaa.log')
    ]
)

logger = logging.getLogger(__name__)

# Importation du widget de mission
mission_widget_available = False
try:
    logger.info("Tentative d'importation du widget de mission")
    from yaktaa.ui.widgets.mission_board import MissionBoardWidget
    mission_widget_available = True
    logger.info("Widget de mission importé avec succès")
except ImportError as e:
    logger.warning(f"Impossible d'importer le module mission_board: {str(e)}")

# Importation du widget de personnage
character_widget_available = False
try:
    logger.info("Tentative d'importation du widget de personnage")
    from yaktaa.ui.widgets.character_sheet import CharacterSheetWidget
    character_widget_available = True
    logger.info("Widget de personnage importé avec succès")
except ImportError as e:
    logger.warning(f"Impossible d'importer le module character_sheet: {str(e)}")

# Importation du widget de terminal
terminal_widget_available = False
try:
    logger.info("Tentative d'importation du widget de terminal")
    from yaktaa.ui.widgets.terminal import TerminalWidget
    terminal_widget_available = True
    logger.info("Widget de terminal importé avec succès")
except ImportError as e:
    logger.warning(f"Impossible d'importer le module terminal: {str(e)}")

# Importation du widget de carte
map_widget_available = False
try:
    logger.info("Tentative d'importation du widget de carte")
    from yaktaa.ui.widgets.map import MapWidget
    map_widget_available = True
    logger.info("Widget de carte importé avec succès")
except ImportError as e:
    logger.warning(f"Impossible d'importer le module map: {str(e)}")

# Importation du widget d'inventaire
try:
    logger.info("Tentative d'importation de l'écran d'inventaire")
    # Import direct sans tentative relative/absolue
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from yaktaa.ui.widgets.inventory import InventoryScreen
    inventory_available = True
    logger.info("Écran d'inventaire importé avec succès")
except ImportError as e:
    logger.error(f"Échec de l'import de l'inventaire: {str(e)}")
    logger.error(f"Détails de l'erreur d'importation: {str(e)}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    inventory_available = False
    
    # Définissons une implémentation minimale de secours pour InventoryScreen
    class InventoryScreen(QWidget):
        """Version simplifiée de l'écran d'inventaire pour le cas où l'importation échoue"""
        inventory_closed = pyqtSignal()
        item_used = pyqtSignal(str, dict)
        item_dropped = pyqtSignal(str)
        hardware_equipped = pyqtSignal(str, str)
        hardware_unequipped = pyqtSignal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.inventory_manager = None
            self.initUI()
            
        def initUI(self):
            layout = QVBoxLayout(self)
            
            # Message indiquant que c'est une version de secours
            label = QLabel("Version de secours de l'écran d'inventaire")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            # Bouton pour fermer l'écran
            close_button = QPushButton("Fermer")
            close_button.clicked.connect(self.inventory_closed.emit)
            layout.addWidget(close_button)
        
        def set_inventory_manager(self, inventory_manager):
            self.inventory_manager = inventory_manager

# Importation du widget de boutique
shop_screen_available = False  # Initialisation explicite avant la tentative d'import
try:
    logger.info("Tentative d'importation de l'écran de boutique")
    from yaktaa.ui.screens.shop_screen import ShopScreen
    shop_screen_available = True
    logger.info("Écran de boutique importé avec succès")
except ImportError as e:
    logger.warning(f"Impossible d'importer le module shop_screen: {str(e)}")

# Définition d'un adaptateur pour convertir une liste d'objets en interface d'inventaire
class InventoryAdapter:
    def __init__(self, items_list):
        self.items = items_list if isinstance(items_list, list) else []
    
    def add_item(self, item):
        self.items.append(item)
        return True
    
    def remove_item(self, item_index):
        if 0 <= item_index < len(self.items):
            self.items.pop(item_index)
            return True
        return False
    
    def get_items(self):
        """Retourne un dictionnaire d'objets avec leurs ID comme clés"""
        items_dict = {}
        for i, item in enumerate(self.items):
            # Si l'objet a déjà un ID, l'utiliser, sinon générer un ID basé sur l'index
            if hasattr(item, 'id'):
                item_id = item.id
            elif isinstance(item, dict) and 'id' in item:
                item_id = item['id']
            else:
                item_id = f"item_{i}"
            
            items_dict[item_id] = item
        return items_dict
    
    def get_hardware(self):
        """Retourne un dictionnaire de matériel avec leurs ID comme clés"""
        # Par défaut, on suppose qu'aucun objet n'est du matériel
        return {}
    
    def get_equipped_hardware(self):
        """Retourne un dictionnaire de matériel équipé par slot"""
        # Par défaut, on suppose qu'aucun matériel n'est équipé
        return {}
    
    def get_hardware_stats(self):
        """Retourne un dictionnaire des statistiques du matériel équipé"""
        # Valeurs par défaut des statistiques pour éviter les erreurs
        return {
            "cpu": 0,
            "memory": 0,
            "storage": 0,
            "network": 0,
            "cooling": 0,
            "power": 0,
            "security": 0
        }

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application YakTaa"""
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        super().__init__()
        
        # Configuration de la fenêtre
        self.setWindowTitle("YakTaa - Cyberpunk RPG")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            
            QSplitter::handle {
                background-color: #333333;
            }
            
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #222222;
            }
            
            QTabBar::tab {
                background-color: #333333;
                color: #CCCCCC;
                padding: 8px 12px;
                border: 1px solid #444444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #222222;
                color: #FFFFFF;
            }
            
            QTabBar::tab:hover {
                background-color: #444444;
            }
            
            QLabel {
                color: #FFFFFF;
            }
            
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 10px;
            }
            
            QPushButton:hover {
                background-color: #444444;
                border: 1px solid #666666;
            }
            
            QPushButton:pressed {
                background-color: #222222;
            }
            
            QFrame {
                background-color: #222222;
                border: 1px solid #444444;
                border-radius: 5px;
            }
        """)
        
        # Initialisation du jeu
        self.game = Game()
        self.config = Config()
        
        # Création de l'interface
        self._create_ui()
        
        # Initialisation du gestionnaire d'interface utilisateur
        self.ui_manager = UIManager(self, self.game)
        self.game.set_ui_manager(self.ui_manager)
        
        # Timer pour les mises à jour
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # 10 FPS
        
        logger.info("Application YakTaa démarrée")
    
    def _create_ui(self):
        """
        Crée l'interface utilisateur principale de l'application.
        Met en place toute la structure de l'interface, dont le panneau de navigation,
        le contenu central et le panneau d'informations.
        """
        global shop_screen_available
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre de titre personnalisée
        self._create_title_bar(main_layout)
        
        # Contenu principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Splitter principal (gauche/droite)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panneau de gauche (navigation)
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Panneau central (contenu principal)
        self.content_stack = QStackedWidget()
        
        # Écran d'accueil
        home_screen = self._create_home_screen()
        self.content_stack.addWidget(home_screen)
        
        # Import dynamique des widgets au moment de leur instanciation
        # Écran de missions
        if mission_widget_available:
            try:
                # Import uniquement au moment où on en a besoin
                from yaktaa.ui.widgets.mission_board import MissionBoardWidget
                self.mission_board = MissionBoardWidget(self.game)
                self.content_stack.addWidget(self.mission_board)
            except ImportError as e:
                logger.error(f"Erreur lors de l'import dynamique de MissionBoardWidget: {str(e)}")
                # Placeholder pour le tableau de missions
                mission_placeholder = QWidget()
                mission_layout = QVBoxLayout(mission_placeholder)
                mission_label = QLabel("Tableau de missions (module non disponible)")
                mission_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                mission_layout.addWidget(mission_label)
                self.content_stack.addWidget(mission_placeholder)
        else:
            # Placeholder pour le tableau de missions
            mission_placeholder = QWidget()
            mission_layout = QVBoxLayout(mission_placeholder)
            mission_label = QLabel("Tableau de missions (module non disponible)")
            mission_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mission_layout.addWidget(mission_label)
            self.content_stack.addWidget(mission_placeholder)
        
        # Écran de personnage
        if character_widget_available:
            try:
                # Import uniquement au moment où on en a besoin
                from yaktaa.ui.widgets.character_sheet import CharacterSheetWidget
                self.character_sheet = CharacterSheetWidget(self.game)
                self.content_stack.addWidget(self.character_sheet)
            except ImportError as e:
                logger.error(f"Erreur lors de l'import dynamique de CharacterSheetWidget: {str(e)}")
                # Placeholder pour la fiche de personnage
                character_placeholder = QWidget()
                character_layout = QVBoxLayout(character_placeholder)
                character_label = QLabel("Fiche de personnage (module non disponible)")
                character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                character_layout.addWidget(character_label)
                self.content_stack.addWidget(character_placeholder)
        else:
            # Placeholder pour la fiche de personnage
            character_placeholder = QWidget()
            character_layout = QVBoxLayout(character_placeholder)
            character_label = QLabel("Fiche de personnage (module non disponible)")
            character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            character_layout.addWidget(character_label)
            self.content_stack.addWidget(character_placeholder)
        
        # Écran de terminal
        if terminal_widget_available:
            try:
                # Import uniquement au moment où on en a besoin
                from yaktaa.ui.widgets.terminal import TerminalWidget
                self.terminal = TerminalWidget(self.game)
                self.content_stack.addWidget(self.terminal)
            except ImportError as e:
                logger.error(f"Erreur lors de l'import dynamique de TerminalWidget: {str(e)}")
                # Placeholder pour le terminal
                terminal_placeholder = QWidget()
                terminal_layout = QVBoxLayout(terminal_placeholder)
                terminal_label = QLabel("Terminal (module non disponible)")
                terminal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                terminal_layout.addWidget(terminal_label)
                self.content_stack.addWidget(terminal_placeholder)
        else:
            # Placeholder pour le terminal
            terminal_placeholder = QWidget()
            terminal_layout = QVBoxLayout(terminal_placeholder)
            terminal_label = QLabel("Terminal (module non disponible)")
            terminal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            terminal_layout.addWidget(terminal_label)
            self.content_stack.addWidget(terminal_placeholder)
        
        # Écran de carte
        if map_widget_available:
            try:
                # Import uniquement au moment où on en a besoin
                from yaktaa.ui.widgets.map import MapWidget
                self.map_widget = MapWidget(self.game)
                self.content_stack.addWidget(self.map_widget)
            except ImportError as e:
                logger.error(f"Erreur lors de l'import dynamique de MapWidget: {str(e)}")
                # Placeholder pour la carte
                map_placeholder = QWidget()
                map_layout = QVBoxLayout(map_placeholder)
                map_label = QLabel("Carte (module non disponible)")
                map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                map_layout.addWidget(map_label)
                self.content_stack.addWidget(map_placeholder)
        else:
            # Placeholder pour la carte
            map_placeholder = QWidget()
            map_layout = QVBoxLayout(map_placeholder)
            map_label = QLabel("Carte (module non disponible)")
            map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            map_layout.addWidget(map_label)
            self.content_stack.addWidget(map_placeholder)
        
        # Écran d'inventaire
        if inventory_available:
            try:
                # Import uniquement au moment où on en a besoin
                from yaktaa.ui.widgets.inventory import InventoryScreen
                self.inventory_screen = InventoryScreen()
                # Connecter les signaux
                self.inventory_screen.inventory_closed.connect(lambda: self.content_stack.setCurrentIndex(0))
                self.inventory_screen.item_used.connect(self._on_item_used)
                self.inventory_screen.item_dropped.connect(self._on_item_dropped)
                self.inventory_screen.hardware_equipped.connect(self._on_hardware_equipped)
                self.inventory_screen.hardware_unequipped.connect(self._on_hardware_unequipped)
                self.content_stack.addWidget(self.inventory_screen)
            except ImportError as e:
                logger.error(f"Erreur lors de l'import dynamique de InventoryScreen: {str(e)}")
                # Placeholder pour l'inventaire
                inventory_placeholder = QWidget()
                inventory_layout = QVBoxLayout(inventory_placeholder)
                inventory_label = QLabel("Inventaire (module non disponible)")
                inventory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                inventory_layout.addWidget(inventory_label)
                self.content_stack.addWidget(inventory_placeholder)
        else:
            # Placeholder pour l'inventaire
            inventory_placeholder = QWidget()
            inventory_layout = QVBoxLayout(inventory_placeholder)
            inventory_label = QLabel("Inventaire (module non disponible)")
            inventory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inventory_layout.addWidget(inventory_label)
            self.content_stack.addWidget(inventory_placeholder)
        
        # Écran de boutique
        if shop_screen_available:
            try:
                logger.debug("Tentative d'initialisation de ShopScreen")
                from yaktaa.ui.screens.shop_screen import ShopScreen
                
                # Vérifier les pré-requis
                if not hasattr(self, 'game') or self.game is None:
                    logger.error("Impossible d'initialiser ShopScreen: instance de jeu non disponible")
                    raise ImportError("Game instance requise pour ShopScreen")
                
                # Réinitialiser le shop_manager si nécessaire
                if not hasattr(self.game, 'shop_manager') or self.game.shop_manager is None:
                    try:
                        logger.warning("ShopManager non disponible lors de l'initialisation - tentative de réinitialisation")
                        from yaktaa.items.shop_manager import ShopManager
                        from yaktaa.world.world_loader import WorldLoader
                        
                        # Créer une nouvelle instance
                        world_loader = WorldLoader()
                        self.game.shop_manager = ShopManager(world_loader)
                        
                        # Charger les boutiques pour le monde actuel
                        world_id = "default"
                        if hasattr(self.game, 'world_manager') and self.game.world_manager:
                            current_world = getattr(self.game.world_manager, 'current_world_id', None)
                            if current_world:
                                world_id = current_world
                        
                        self.game.shop_manager.load_shops_for_world(world_id)
                        logger.info(f"ShopManager réinitialisé avec succès pour le monde {world_id}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la réinitialisation de ShopManager: {str(e)}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        raise ImportError(f"Erreur de réinitialisation du ShopManager: {str(e)}")
                
                # Créer l'instance avec gestion d'erreurs détaillée
                try:
                    logger.debug("Création de l'instance ShopScreen")
                    self.shop_screen = ShopScreen(self.game)
                    logger.debug("Instance ShopScreen créée avec succès")
                except Exception as init_err:
                    logger.error(f"Erreur lors de l'initialisation de ShopScreen: {str(init_err)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise ImportError(f"Erreur d'initialisation: {str(init_err)}")
                
                # Connecter les signaux avec gestion d'erreurs
                try:
                    logger.debug("Connexion des signaux de ShopScreen")
                    self.shop_screen.shop_closed.connect(lambda: self.content_stack.setCurrentIndex(0))
                    self.shop_screen.item_purchased.connect(self._on_item_purchased)
                    self.shop_screen.item_sold.connect(self._on_item_sold)
                    logger.debug("Signaux de ShopScreen connectés avec succès")
                except Exception as signal_err:
                    logger.error(f"Erreur lors de la connexion des signaux de ShopScreen: {str(signal_err)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise ImportError(f"Erreur de connexion des signaux: {str(signal_err)}")
                
                # Tout s'est bien passé, ajouter le widget au stack
                self.content_stack.addWidget(self.shop_screen)
                logger.info("ShopScreen initialisé et ajouté avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'import dynamique de ShopScreen: {str(e)}")
                import traceback
                logger.error(f"Traceback complet: {traceback.format_exc()}")
                
                # Placeholder pour la boutique avec message d'erreur détaillé
                shop_placeholder = QWidget()
                shop_layout = QVBoxLayout(shop_placeholder)
                
                # Style visuel cyberpunk pour le message d'erreur
                error_frame = QFrame()
                error_frame.setObjectName("error_frame")
                error_frame.setStyleSheet("""
                    QFrame#error_frame {
                        background-color: #1a1a2e;
                        border: 1px solid #00a8cc;
                        border-radius: 5px;
                    }
                    QLabel {
                        color: #e94560;
                        font-weight: bold;
                    }
                    QLabel#error_details {
                        color: #00a8cc;
                        font-family: monospace;
                    }
                """)
                
                error_layout = QVBoxLayout(error_frame)
                
                title_label = QLabel("Erreur de boutique")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title_label.setStyleSheet("font-size: 18px;")
                error_layout.addWidget(title_label)
                
                message_label = QLabel(f"Impossible de charger l'écran de boutique: {str(e)}")
                message_label.setWordWrap(True)
                message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_layout.addWidget(message_label)
                
                error_details = QLabel("Consultez les logs pour plus de détails.")
                error_details.setObjectName("error_details")
                
                error_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_layout.addWidget(error_details)
                
                # Bouton pour revenir à l'écran principal
                retry_button = QPushButton("Revenir à l'écran principal")
                retry_button.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
                error_layout.addWidget(retry_button)
                
                shop_layout.addWidget(error_frame)
                self.content_stack.addWidget(shop_placeholder)
                
                # Marquer comme non disponible pour les appels ultérieurs
                shop_screen_available = False
        else:
            # Placeholder pour la boutique
            shop_placeholder = QWidget()
            shop_layout = QVBoxLayout(shop_placeholder)
            shop_label = QLabel("Boutique (module non disponible)")
            shop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            shop_layout.addWidget(shop_label)
            self.content_stack.addWidget(shop_placeholder)
        
        main_splitter.addWidget(self.content_stack)
        
        # Panneau de droite (informations contextuelles)
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Configuration des tailles relatives des panneaux
        main_splitter.setStretchFactor(0, 1)  # Panneau de gauche
        main_splitter.setStretchFactor(1, 4)  # Contenu principal
        main_splitter.setStretchFactor(2, 1)  # Panneau de droite
        
        content_layout.addWidget(main_splitter)
        
        # Barre d'état
        self._create_status_bar(content_layout)
        
        main_layout.addWidget(content_widget)
    
    def _create_title_bar(self, layout):
        """Crée la barre de titre personnalisée"""
        title_bar = QFrame()
        title_bar.setMaximumHeight(60)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-bottom: 1px solid #444444;
                border-radius: 0px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo et titre
        logo_label = QLabel("YakTaa")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00AAFF;")
        title_layout.addWidget(logo_label)
        
        # Sous-titre
        subtitle_label = QLabel("Cyberpunk RPG")
        subtitle_label.setStyleSheet("font-size: 14px; color: #888888;")
        title_layout.addWidget(subtitle_label)
        
        title_layout.addStretch()
        
        # Boutons de la barre de titre
        for name, icon in [
            ("Paramètres", "⚙️"),
            ("Aide", "❓"),
            ("À propos", "ℹ️")
        ]:
            button = QPushButton(f"{icon} {name}")
            button.setFlat(True)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #CCCCCC;
                    border: none;
                    padding: 5px 10px;
                }
                
                QPushButton:hover {
                    background-color: #333333;
                    border-radius: 4px;
                }
                
                QPushButton:pressed {
                    background-color: #222222;
                }
            """)
            title_layout.addWidget(button)
        
        layout.addWidget(title_bar)
    
    def _create_left_panel(self):
        """Crée le panneau de navigation à gauche"""
        panel = QFrame()
        panel.setMinimumWidth(150)
        panel.setMaximumWidth(200)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(5, 10, 5, 10)
        panel_layout.setSpacing(10)
        
        # Boutons de navigation
        nav_buttons = [
            ("🏠 Accueil", 0),
            ("📋 Missions", 1),
            ("👤 Personnage", 2),
            ("💻 Terminal", 3),
            ("🗺️ Carte", 4),
            ("🎒 Inventaire", 5),
            ("🛒 Boutique", 6)
        ]
        
        for text, index in nav_buttons:
            button = QPushButton(text)
            button.setMinimumHeight(40)
            # Utiliser des fonctions spécifiques pour certains boutons qui nécessitent une initialisation
            if text == "🛒 Boutique":
                button.clicked.connect(self._show_shop_screen)
            elif text == "🎒 Inventaire":
                button.clicked.connect(self._show_inventory_screen)
            else:
                button.clicked.connect(lambda checked, idx=index: self.content_stack.setCurrentIndex(idx))
            panel_layout.addWidget(button)
        
        panel_layout.addStretch()
        
        # Bouton de sauvegarde
        save_button = QPushButton("💾 Sauvegarder")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self._save_game)
        panel_layout.addWidget(save_button)
        
        # Bouton de chargement
        load_button = QPushButton("📂 Charger")
        load_button.setMinimumHeight(40)
        load_button.clicked.connect(self._load_game)
        panel_layout.addWidget(load_button)
        
        # Bouton de quitter
        quit_button = QPushButton("🚪 Quitter")
        quit_button.setMinimumHeight(40)
        quit_button.clicked.connect(self.close)
        panel_layout.addWidget(quit_button)
        
        return panel
    
    def _create_right_panel(self):
        """Crée le panneau d'informations à droite"""
        panel = QFrame()
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(5, 10, 5, 10)
        panel_layout.setSpacing(10)
        
        # Titre du panneau
        panel_title = QLabel("Informations")
        panel_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        panel_layout.addWidget(panel_title)
        
        # Onglets d'informations
        info_tabs = QTabWidget()
        info_tabs.setTabPosition(QTabWidget.TabPosition.North)
        info_tabs.setDocumentMode(True)
        
        # Onglet des notifications
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        notifications_layout.addWidget(QLabel("Aucune notification"))
        info_tabs.addTab(notifications_tab, "📢 Notifications")
        
        # Onglet des objectifs
        objectives_tab = QWidget()
        objectives_layout = QVBoxLayout(objectives_tab)
        objectives_layout.addWidget(QLabel("Aucun objectif actif"))
        info_tabs.addTab(objectives_tab, "🎯 Objectifs")
        
        # Onglet des contacts
        contacts_tab = QWidget()
        contacts_layout = QVBoxLayout(contacts_tab)
        contacts_layout.addWidget(QLabel("Aucun contact"))
        info_tabs.addTab(contacts_tab, "👥 Contacts")
        
        panel_layout.addWidget(info_tabs)
        
        # Horloge du jeu
        clock_frame = QFrame()
        clock_layout = QVBoxLayout(clock_frame)
        
        clock_title = QLabel("Horloge du jeu")
        clock_title.setStyleSheet("font-weight: bold;")
        clock_layout.addWidget(clock_title)
        
        self.clock_label = QLabel("Jour 1 - 08:00")
        self.clock_label.setStyleSheet("font-size: 14px;")
        clock_layout.addWidget(self.clock_label)
        
        panel_layout.addWidget(clock_frame)
        
        # Informations sur la localisation
        location_frame = QFrame()
        location_layout = QVBoxLayout(location_frame)
        
        location_title = QLabel("Localisation")
        location_title.setStyleSheet("font-weight: bold;")
        location_layout.addWidget(location_title)
        
        self.location_label = QLabel("Neo-Tokyo, District 7")
        self.location_label.setStyleSheet("font-size: 14px;")
        location_layout.addWidget(self.location_label)
        
        panel_layout.addWidget(location_frame)
        
        panel_layout.addStretch()
        
        return panel
    
    def _create_status_bar(self, layout):
        """Crée la barre d'état en bas de l'interface"""
        status_bar = QFrame()
        status_bar.setMaximumHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-top: 1px solid #444444;
                border-radius: 0px;
            }
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 0, 10, 0)
        
        # Statut du jeu
        self.status_label = QLabel("Prêt")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Version du jeu
        version_label = QLabel("YakTaa v0.1.0")
        version_label.setStyleSheet("color: #888888;")
        status_layout.addWidget(version_label)
        
        layout.addWidget(status_bar)
    
    def _create_home_screen(self):
        """Crée l'écran d'accueil"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(20)
        
        # Titre de bienvenue
        welcome_label = QLabel("Bienvenue dans YakTaa")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00AAFF;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(welcome_label)
        
        # Description du jeu
        desc_label = QLabel(
            "YakTaa est un jeu de rôle cyberpunk immersif où vous incarnez un hacker dans un monde "
            "futuriste. Explorez des villes, accomplissez des missions, améliorez vos compétences "
            "et interagissez avec divers systèmes informatiques via un terminal."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px;")
        home_layout.addWidget(desc_label)
        
        # Grille de raccourcis
        shortcuts_frame = QFrame()
        shortcuts_layout = QHBoxLayout(shortcuts_frame)
        
        shortcuts = [
            ("📋 Missions", "Consultez et acceptez\ndes missions", 1),
            ("👤 Personnage", "Gérez votre personnage\net ses compétences", 2),
            ("💻 Terminal", "Accédez au terminal\nde hacking", 3),
            ("🗺️ Carte", "Explorez le monde\net voyagez", 4)
        ]
        
        for icon_text, desc, index in shortcuts:
            shortcut_frame = QFrame()
            shortcut_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            shortcut_frame.mousePressEvent = lambda event, idx=index: self.content_stack.setCurrentIndex(idx)
            
            shortcut_layout = QVBoxLayout(shortcut_frame)
            
            icon_label = QLabel(icon_text.split()[0])
            icon_label.setStyleSheet("font-size: 32px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            shortcut_layout.addWidget(icon_label)
            
            title_label = QLabel(icon_text.split()[1])
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            shortcut_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            shortcut_layout.addWidget(desc_label)
            
            shortcuts_layout.addWidget(shortcut_frame)
        
        home_layout.addWidget(shortcuts_frame)
        
        # Dernières nouvelles
        news_frame = QFrame()
        news_layout = QVBoxLayout(news_frame)
        
        news_title = QLabel("Dernières nouvelles")
        news_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        news_layout.addWidget(news_title)
        
        news_items = [
            "Mise à jour v0.1.0 - Première version jouable",
            "Ajout du tableau de missions et de la fiche de personnage",
            "Ajout du terminal de hacking avec commandes interactives",
            "Prochainement : système de carte et d'inventaire"
        ]
        
        for item in news_items:
            item_label = QLabel(f"• {item}")
            news_layout.addWidget(item_label)
        
        home_layout.addWidget(news_frame)
        
        home_layout.addStretch()
        
        return home_widget
    
    def _update_ui(self):
        """Met à jour l'interface utilisateur"""
        # Mise à jour de l'horloge du jeu
        # Dans une version complète, cela serait lié au temps du jeu
        
        # Définition d'un adaptateur pour convertir la liste en interface compatible
        # class InventoryAdapter:
        #     def __init__(self, items_list):
        #         self.items = items_list if isinstance(items_list, list) else []
        #     
        #     def add_item(self, item):
        #         self.items.append(item)
        #         return True
        #     
        #     def remove_item(self, item_index):
        #         if 0 <= item_index < len(self.items):
        #             self.items.pop(item_index)
        #             return True
        #         return False
        
        # Si l'écran d'inventaire est disponible et que le joueur est initialisé,
        # assurez-vous que l'écran d'inventaire a accès à l'InventoryManager
        if inventory_available and hasattr(self, 'inventory_screen'):
            if hasattr(self.game, 'player') and self.game.player and hasattr(self.game.player, 'inventory'):
                player_inventory = self.game.player.inventory
                
                # Vérifier si l'inventaire est une liste et l'adapter si nécessaire
                if isinstance(player_inventory, list):
                    # Utiliser l'adaptateur pour convertir la liste en interface compatible
                    player_inventory = InventoryAdapter(player_inventory)
                
                if self.inventory_screen.inventory_manager != player_inventory:
                    self.inventory_screen.set_inventory_manager(player_inventory)
        
        pass
    
    def _on_item_used(self, item_id, result):
        """Gère l'utilisation d'un objet depuis l'inventaire"""
        logger.info(f"Objet utilisé: {item_id}, résultat: {result}")
        # Implémenter les effets spécifiques au jeu ici
        # Par exemple, restaurer la santé, appliquer des effets, etc.
        
        # Mettre à jour l'interface si nécessaire
        self._update_ui()
    
    def _on_item_dropped(self, item_id):
        """Gère la suppression d'un objet de l'inventaire"""
        logger.info(f"Objet jeté: {item_id}")
        # Implémenter des fonctionnalités supplémentaires si nécessaire
        # Par exemple, créer l'objet dans le monde du jeu
        
        # Mettre à jour l'interface si nécessaire
        self._update_ui()
    
    def _on_hardware_equipped(self, hardware_id, slot):
        """Gère l'équipement d'un matériel"""
        logger.info(f"Matériel équipé: {hardware_id} dans le slot {slot}")
        # Implémenter des fonctionnalités supplémentaires si nécessaire
        # Par exemple, mettre à jour les statistiques du joueur
        
        # Mettre à jour l'interface si nécessaire
        self._update_ui()
    
    def _on_hardware_unequipped(self, hardware_id):
        """Gère le déséquipement d'un matériel"""
        logger.debug(f"Matériel déséquipé : {hardware_id}")
        
    def _on_item_purchased(self, item_id, shop_id, price):
        """
        Gère l'achat d'un objet dans une boutique
        """
        logger.info(f"[SHOP] === Début du processus d'achat d'item ===")
        logger.debug(f"[SHOP] Achat de l'item {item_id} détecté (boutique {shop_id}, prix {price})")
        
        try:
            # Mise à jour des crédits du joueur
            if hasattr(self.game, 'player') and self.game.player:
                # Déduction du prix
                old_credits = self.game.player.credits
                self.game.player.credits -= price
                logger.debug(f"[SHOP] Crédits du joueur mis à jour: {old_credits} -> {self.game.player.credits}")
                
                # Mise à jour de l'affichage des crédits dans toutes les interfaces
                if hasattr(self, 'shop_screen'):
                    logger.debug(f"[SHOP] Envoi du signal de mise à jour des crédits: {self.game.player.credits}")
                    self.shop_screen.update_player_credits.emit(self.game.player.credits)
                
                # Mise à jour de l'inventaire du joueur
                if hasattr(self.game, 'shop_manager'):
                    # Récupérer la boutique
                    shop = self.game.shop_manager.get_shop(shop_id)
                    if shop:
                        logger.debug(f"[SHOP] Boutique {shop_id} ({shop.name}) trouvée pour le traitement de l'achat")
                        
                        # Trouver l'item à ajouter
                        for item, item_price in shop.inventory:
                            if item.id == item_id:
                                logger.debug(f"[SHOP] Item trouvé dans l'inventaire de la boutique: {item.name}")
                                
                                # Ajouter à l'inventaire du joueur
                                self.game.player.inventory.add_item(item)
                                logger.info(f"[SHOP] Item {item.name} ajouté à l'inventaire du joueur")
                                
                                # Afficher un message de confirmation
                                self.status_label.setText(f"Achat réussi: {item.name} pour {price} crédits")
                                break
                        else:
                            logger.warning(f"[SHOP] Item {item_id} non trouvé dans l'inventaire de la boutique {shop_id}")
                    else:
                        logger.warning(f"[SHOP] Boutique {shop_id} non trouvée pour la finalisation de l'achat")
                else:
                    logger.error("[SHOP] Shop manager non disponible pour finaliser l'achat")
            else:
                logger.error("[SHOP] Joueur non disponible pour finaliser l'achat")
                self.status_label.setText("Erreur lors de l'achat: joueur non disponible")
        except Exception as e:
            logger.error(f"[SHOP] Erreur lors du traitement de l'achat: {str(e)}")
            import traceback
            logger.error(f"[SHOP] Traceback: {traceback.format_exc()}")
            self.status_label.setText(f"Erreur lors de l'achat: {str(e)}")
        
        logger.info("[SHOP] === Fin du processus d'achat d'item ===")
    
    def _on_item_sold(self, item_id, shop_id, price):
        """
        Gère la vente d'un objet à une boutique
        """
        logger.info(f"[SHOP] === Début du processus de vente d'item ===")
        logger.debug(f"[SHOP] Vente de l'item {item_id} détectée (boutique {shop_id}, prix {price})")
        
        try:
            # Mise à jour des crédits du joueur
            if hasattr(self.game, 'player') and self.game.player:
                # Ajout du prix de vente
                old_credits = self.game.player.credits
                self.game.player.credits += price
                logger.debug(f"[SHOP] Crédits du joueur mis à jour: {old_credits} -> {self.game.player.credits}")
                
                # Mise à jour de l'affichage des crédits
                if hasattr(self, 'shop_screen'):
                    logger.debug(f"[SHOP] Envoi du signal de mise à jour des crédits: {self.game.player.credits}")
                    self.shop_screen.update_player_credits.emit(self.game.player.credits)
                
                # Mise à jour de l'inventaire du joueur
                if hasattr(self.game.player, 'inventory'):
                    # Vérifier si l'inventaire est un InventoryManager ou une liste
                    inventory = self.game.player.inventory
                    
                    # Si c'est un InventoryManager, utiliser ses méthodes
                    if hasattr(inventory, 'get_item'):
                        # Récupérer l'item à retirer
                        item = inventory.get_item(item_id)
                        if item:
                            logger.debug(f"[SHOP] Item {item_id} ({item.name}) trouvé dans l'inventaire du joueur")
                            
                            # Retirer de l'inventaire
                            inventory.remove_item(item_id)
                            logger.info(f"[SHOP] Item {item.name} retiré de l'inventaire du joueur")
                            
                            # Ajouter à la boutique si shop_manager disponible
                            if hasattr(self.game, 'shop_manager'):
                                self.game.shop_manager.add_item_to_shop(shop_id, item)
                                logger.debug(f"[SHOP] Item {item.name} ajouté à l'inventaire de la boutique {shop_id}")
                            
                            # Afficher un message de confirmation
                            self.status_label.setText(f"Vente réussie: {item.name} pour {price} crédits")
                        else:
                            logger.warning(f"[SHOP] Item {item_id} non trouvé dans l'inventaire du joueur")
                    # Si c'est une liste, chercher l'item par son ID
                    else:
                        # Chercher l'item dans la liste par son ID
                        item = None
                        item_index = -1
                        
                        for i, inv_item in enumerate(inventory):
                            if hasattr(inv_item, 'id') and inv_item.id == item_id:
                                item = inv_item
                                item_index = i
                                break
                        
                        if item:
                            logger.debug(f"[SHOP] Item {item_id} ({item.name}) trouvé dans l'inventaire du joueur (index {item_index})")
                            
                            # Retirer de l'inventaire
                            inventory.pop(item_index)
                            logger.info(f"[SHOP] Item {item.name} retiré de l'inventaire du joueur")
                            
                            # Ajouter à la boutique si shop_manager disponible
                            if hasattr(self.game, 'shop_manager'):
                                self.game.shop_manager.add_item_to_shop(shop_id, item)
                                logger.debug(f"[SHOP] Item {item.name} ajouté à l'inventaire de la boutique {shop_id}")
                            
                            # Afficher un message de confirmation
                            self.status_label.setText(f"Vente réussie: {item.name} pour {price} crédits")
                        else:
                            logger.warning(f"[SHOP] Item {item_id} non trouvé dans l'inventaire du joueur")
                else:
                    logger.error("[SHOP] Inventaire du joueur non disponible pour finaliser la vente")
            else:
                logger.error("[SHOP] Joueur non disponible pour finaliser la vente")
                self.status_label.setText("Erreur lors de la vente: joueur non disponible")
        except Exception as e:
            logger.error(f"[SHOP] Erreur lors du traitement de la vente: {str(e)}")
            import traceback
            logger.error(f"[SHOP] Traceback: {traceback.format_exc()}")
            self.status_label.setText(f"Erreur lors de la vente: {str(e)}")
        
        logger.info("[SHOP] === Fin du processus de vente d'item ===")
    
    def _save_game(self):
        """Sauvegarde l'état du jeu"""
        # TODO: Implémenter la sauvegarde
        self.status_label.setText("Jeu sauvegardé")
        logger.info("Jeu sauvegardé")
    
    def _load_game(self):
        """Charge un état de jeu sauvegardé"""
        # TODO: Implémenter le chargement
        self.status_label.setText("Jeu chargé")
        logger.info("Jeu chargé")
    
    def closeEvent(self, event):
        """Gère l'événement de fermeture de la fenêtre"""
        # TODO: Demander confirmation et sauvegarder si nécessaire
        logger.info("Application YakTaa fermée")
        event.accept()
    
    def _show_inventory_screen(self):
        """Affiche l'écran d'inventaire et initialise les données"""
        # Passer à l'écran d'inventaire
        self.content_stack.setCurrentIndex(5)
        
        # Mettre à jour l'inventaire si le joueur existe
        if hasattr(self.game, 'player') and self.game.player and hasattr(self.game.player, 'inventory'):
            # Mettre à jour le widget d'inventaire
            if inventory_available and hasattr(self, 'inventory_screen'):
                # Vérifier si l'inventaire est une liste et l'adapter si nécessaire
                inventory = self.game.player.inventory
                if isinstance(inventory, list):
                    # Créer un adaptateur d'inventaire pour la liste
                    inventory_adapter = InventoryAdapter(inventory)
                    self.inventory_screen.set_inventory_manager(inventory_adapter)
                else:
                    # Utiliser l'inventaire directement s'il s'agit déjà d'un InventoryManager
                    self.inventory_screen.set_inventory_manager(inventory)
    
    def _show_shop_screen(self):
        """Affiche l'écran de boutique"""
        logger.info("[SHOP] === Début du chargement de l'écran de boutique ===")
        
        try:
            # Récupérer l'ID d'emplacement actuel depuis le gestionnaire de monde
            current_location = self.game.world_manager.current_location_id
            logger.debug(f"[SHOP] Emplacement actuel: {current_location}")
            
            # Obtenir l'ID de la ville, que le joueur soit dans un bâtiment ou directement dans la ville
            logger.debug(f"[SHOP] Conversion de l'emplacement {current_location} en ID de ville")
            city_id = self.game.shop_manager.get_city_id_from_location(current_location)
            logger.debug(f"[SHOP] ID de ville obtenu: {city_id}")
            
            # Vérifier si l'ID de ville existe dans la base de données
            city_exists = False
            city_name = "inconnue"
            
            try:
                conn = self.game.shop_manager.world_loader.get_connection()
                if conn:
                    cursor = conn.cursor()
                    # Vérifier si la ville existe par son ID
                    cursor.execute("SELECT name FROM locations WHERE id = ?", (city_id,))
                    city_info = cursor.fetchone()
                    if city_info:
                        city_exists = True
                        city_name = city_info[0]
                        logger.info(f"[SHOP] Ville trouvée: {city_name} (ID: {city_id})")
            except Exception as e:
                logger.warning(f"[SHOP] Impossible de vérifier l'existence de la ville: {str(e)}")
            
            # Si l'ID de ville n'est pas trouvé, chercher une ville valide disponible
            if not city_exists:
                logger.warning(f"[SHOP] L'ID de ville {city_id} n'existe pas dans la base de données")
                # Afficher un message d'information à l'utilisateur
                self.status_label.setText(f"Recherche d'une connexion alternative...")
                
                # Stocker l'ID de ville problématique pour référence ultérieure
                invalid_city_id = city_id
                
                try:
                    conn = self.game.shop_manager.world_loader.get_connection()
                    if conn:
                        cursor = conn.cursor()
                        # Récupérer toutes les villes disponibles, sans filtre de type pour plus de flexibilité
                        cursor.execute("SELECT id, name FROM locations ORDER BY name")
                        all_locations = cursor.fetchall()
                        
                        if all_locations:
                            # Créer une liste de toutes les locations disponibles
                            available_locations = [(loc[0], loc[1]) for loc in all_locations]
                            
                            # Trouver une location avec des boutiques
                            location_with_shops = None
                            for location_candidate in available_locations:
                                candidate_id = location_candidate[0]
                                candidate_shops = self.game.shop_manager.get_shops_by_location(candidate_id)
                                if candidate_shops:
                                    city_id = candidate_id
                                    city_name = location_candidate[1]
                                    location_with_shops = (city_id, city_name, len(candidate_shops))
                                    break
                            
                            if location_with_shops:
                                # Location avec boutiques trouvée
                                logger.info(f"[SHOP] Location alternative trouvée: {location_with_shops[1]} (ID: {location_with_shops[0]}) avec {location_with_shops[2]} boutiques")
                                
                                # Informer l'utilisateur du changement de location
                                msg = f"Connexion à {invalid_city_id} impossible. Redirection vers {city_name}..."
                                self.status_label.setText(msg)
                                
                                # Montrer une notification cyberpunk
                                notification = QFrame(self)
                                notification.setStyleSheet("""
                                    QFrame {
                                        background-color: rgba(0, 0, 0, 0.8);
                                        border: 1px solid #00FFFF;
                                        border-radius: 5px;
                                    }
                                    QLabel {
                                        color: #00FFFF;
                                        font-family: 'Courier New';
                                        font-size: 13px;
                                    }
                                """)
                                notification_layout = QVBoxLayout(notification)
                                notification_title = QLabel("⚠ Alerte Réseau ⚠")
                                notification_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF00FF;")
                                notification_msg = QLabel(f"Connexion perdue vers {invalid_city_id}.\nRéacheminement vers {city_name}...")
                                notification_layout.addWidget(notification_title)
                                notification_layout.addWidget(notification_msg)
                                
                                # Ajouter la notification à l'interface
                                notification.setGeometry(self.width() - 350, 80, 300, 100)
                                notification.show()
                                
                                # Timer pour cacher la notification
                                QTimer.singleShot(5000, notification.hide)
                                
                                # Mettre à jour le gestionnaire de monde avec la nouvelle location
                                self.game.world_manager.set_current_location(city_id)
                                logger.info(f"[SHOP] Location actuelle mise à jour: {city_id}")
                            else:
                                # Aucune location avec boutiques trouvée
                                logger.warning("[SHOP] Aucune location avec boutiques trouvée dans la base de données")
                                self.status_label.setText("Aucune boutique disponible dans ce monde.")
                                
                                # Notification plus sévère
                                notification = QFrame(self)
                                notification.setStyleSheet("""
                                    QFrame {
                                        background-color: rgba(0, 0, 0, 0.8);
                                        border: 1px solid #FF0000;
                                        border-radius: 5px;
                                    }
                                    QLabel {
                                        color: #FF0000;
                                        font-family: 'Courier New';
                                        font-size: 13px;
                                    }
                                """)
                                notification_layout = QVBoxLayout(notification)
                                notification_title = QLabel("❌ ERREUR CRITIQUE ❌")
                                notification_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF0000;")
                                notification_msg = QLabel("Aucune boutique disponible dans ce monde.\nCréez des boutiques dans l'éditeur de monde.")
                                notification_layout.addWidget(notification_title)
                                notification_layout.addWidget(notification_msg)
                                
                                # Ajouter la notification à l'interface
                                notification.setGeometry(self.width() - 350, 80, 300, 120)
                                notification.show()
                                
                                # Timer pour cacher la notification
                                QTimer.singleShot(8000, notification.hide)
                                
                                # Retourner à l'écran principal après un délai
                                QTimer.singleShot(3000, self.show_main_screen)
                                logger.info("[SHOP] Retour à l'écran principal car aucune boutique n'est disponible")
                                return
                        else:
                            # Aucune location trouvée dans la base de données
                            logger.warning("[SHOP] Aucune location trouvée dans la base de données")
                            self.status_label.setText("Aucune location disponible dans ce monde.")
                            # Retourner à l'écran principal après un délai
                            QTimer.singleShot(3000, self.show_main_screen)
                            return
                except Exception as e:
                    logger.error(f"[SHOP] Erreur lors de la recherche d'une location alternative: {str(e)}")
                    self.status_label.setText("Erreur lors de la connexion à la base de données.")
                    # Retourner à l'écran principal après un délai
                    QTimer.singleShot(3000, self.show_main_screen)
                    return
            
            # Récupérer les boutiques pour la ville sélectionnée
            shops = self.game.shop_manager.get_shops_by_location(city_id)
            logger.info(f"[SHOP] {len(shops)} boutiques trouvées à {city_name} (ID: {city_id})")
            
            # Afficher les boutiques dans l'interface
            self.shop_screen.clear_shops()
            self.shop_screen.set_location_name(city_name)
            
            for shop in shops:
                self.shop_screen.add_shop(shop)
            
            # Passer à l'écran de boutique
            if self.content_stack.currentWidget() != self.shop_screen:
                self.content_stack.setCurrentWidget(self.shop_screen)
            
            logger.info(f"[SHOP] Écran de boutique chargé avec {len(shops)} boutiques à {city_name}")
            logger.info("[SHOP] === Fin du chargement de l'écran de boutique ===")
            
        except Exception as e:
            logger.error(f"[SHOP] Erreur lors du chargement de l'écran de boutique: {str(e)}")
            self.status_label.setText("Erreur lors du chargement des boutiques.")
    
def main():
    """Point d'entrée principal de l'application"""
    try:
        app = QApplication(sys.argv)
        
        # Application de la police par défaut
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        window = MainWindow()
        window.show()
        
        return app.exec()
    except Exception as e:
        logger.error(f"Erreur critique dans l'application: {str(e)}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
