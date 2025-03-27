"""
Module pour l'écran de jeu principal de YakTaa
"""

import logging
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy, QTabWidget,
    QSplitter, QFrame, QStackedWidget, QToolBar,
    QToolButton, QMenu, QAction
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap

from yaktaa.ui.screens.base_screen import BaseScreen
from yaktaa.ui.widgets.terminal import TerminalWidget
from yaktaa.ui.widgets.map_view import MapView
from yaktaa.ui.widgets.inventory import InventoryWidget
from yaktaa.ui.widgets.mission_board import MissionBoardWidget
from yaktaa.ui.widgets.character_sheet import CharacterSheetWidget
from yaktaa.ui.widgets.messaging import MessagingWidget
from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.GameScreen")

class GameScreen(BaseScreen):
    """Écran principal du jeu"""
    
    # Signal émis lorsque le joueur veut quitter la partie
    quit_game_signal = pyqtSignal()
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise l'écran de jeu principal"""
        super().__init__(game, parent)
        
        # Widgets principaux
        self.terminal = None
        self.map_view = None
        self.mission_board = None
        self.inventory = None
        self.character_sheet = None
        self.messaging = None
        
        # État du jeu
        self.paused = False
        
        logger.info("Écran de jeu principal initialisé")
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur de l'écran de jeu"""
        # Suppression des marges par défaut
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Barre d'outils principale
        self._create_toolbar()
        
        # Conteneur principal avec splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.main_splitter)
        
        # Panneau gauche (terminal et carte)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        
        # Splitter vertical pour le panneau gauche
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.left_layout.addWidget(self.left_splitter)
        
        # Terminal
        self.terminal = TerminalWidget(self.game, self)
        self.left_splitter.addWidget(self.terminal)
        
        # Carte
        self.map_view = MapView(self.game, self)
        self.left_splitter.addWidget(self.map_view)
        
        # Configuration du splitter gauche
        self.left_splitter.setSizes([300, 400])  # Tailles initiales
        
        # Ajout du panneau gauche au splitter principal
        self.main_splitter.addWidget(self.left_panel)
        
        # Panneau droit (onglets avec différentes fonctionnalités)
        self.right_panel = QTabWidget()
        self.right_panel.setTabPosition(QTabWidget.TabPosition.North)
        self.right_panel.setDocumentMode(True)
        
        # Onglet Missions
        self.mission_board = MissionBoardWidget(self.game, self)
        self.right_panel.addTab(self.mission_board, "Missions")
        
        # Onglet Inventaire
        self.inventory = InventoryWidget(self.game, self)
        self.right_panel.addTab(self.inventory, "Inventaire")
        
        # Onglet Personnage
        self.character_sheet = CharacterSheetWidget(self.game, self)
        self.right_panel.addTab(self.character_sheet, "Personnage")
        
        # Onglet Messagerie
        self.messaging = MessagingWidget(self.game, self)
        self.right_panel.addTab(self.messaging, "Messages")
        
        # Ajout du panneau droit au splitter principal
        self.main_splitter.addWidget(self.right_panel)
        
        # Configuration du splitter principal
        self.main_splitter.setSizes([600, 400])  # Tailles initiales
        
        # Barre d'état
        self._create_status_bar()
        
        # Connexion des signaux
        self.quit_game_signal.connect(self._on_quit_game)
    
    def _create_toolbar(self) -> None:
        """Crée la barre d'outils principale"""
        self.toolbar = QToolBar("Barre d'outils principale")
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.layout.addWidget(self.toolbar)
        
        # Bouton Menu
        self.menu_button = QToolButton()
        self.menu_button.setText("Menu")
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Menu déroulant
        self.menu = QMenu(self.menu_button)
        
        # Actions du menu
        self.save_action = QAction("Sauvegarder", self.menu)
        self.save_action.triggered.connect(self._on_save_game)
        self.menu.addAction(self.save_action)
        
        self.load_action = QAction("Charger", self.menu)
        self.load_action.triggered.connect(self._on_load_game)
        self.menu.addAction(self.load_action)
        
        self.menu.addSeparator()
        
        self.settings_action = QAction("Paramètres", self.menu)
        self.settings_action.triggered.connect(self._on_settings)
        self.menu.addAction(self.settings_action)
        
        self.menu.addSeparator()
        
        self.quit_action = QAction("Quitter", self.menu)
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        
        self.menu_button.setMenu(self.menu)
        self.toolbar.addWidget(self.menu_button)
        
        # Séparateur
        self.toolbar.addSeparator()
        
        # Boutons d'action rapide
        self.terminal_button = QAction("Terminal", self.toolbar)
        self.terminal_button.setCheckable(True)
        self.terminal_button.setChecked(True)
        self.terminal_button.triggered.connect(self._toggle_terminal)
        self.toolbar.addAction(self.terminal_button)
        
        self.map_button = QAction("Carte", self.toolbar)
        self.map_button.setCheckable(True)
        self.map_button.setChecked(True)
        self.map_button.triggered.connect(self._toggle_map)
        self.toolbar.addAction(self.map_button)
        
        # Séparateur
        self.toolbar.addSeparator()
        
        # Bouton de pause
        self.pause_button = QAction("Pause", self.toolbar)
        self.pause_button.setCheckable(True)
        self.pause_button.triggered.connect(self._toggle_pause)
        self.toolbar.addAction(self.pause_button)
        
        # Espacement flexible
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        
        # Affichage du temps de jeu
        self.game_time_label = QLabel("Temps de jeu: 00:00:00")
        self.toolbar.addWidget(self.game_time_label)
    
    def _create_status_bar(self) -> None:
        """Crée la barre d'état"""
        self.status_bar = QFrame()
        self.status_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.status_bar.setMaximumHeight(30)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        # Emplacement actuel
        self.location_label = QLabel("Emplacement: Non défini")
        status_layout.addWidget(self.location_label)
        
        # Espacement
        status_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Argent
        self.money_label = QLabel("Credits: 0")
        status_layout.addWidget(self.money_label)
        
        # Niveau et XP
        self.level_label = QLabel("Niveau: 1 | XP: 0/100")
        status_layout.addWidget(self.level_label)
        
        self.layout.addWidget(self.status_bar)
    
    def on_show(self) -> None:
        """Appelé lorsque l'écran est affiché"""
        super().on_show()
        
        # Mise à jour de l'interface avec les données du jeu
        self._update_ui_from_game()
        
        # Activation du terminal
        if self.terminal:
            self.terminal.setFocus()
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur"""
        # Mise à jour du temps de jeu
        if self.game and self.game.running:
            self.game_time_label.setText(f"Temps de jeu: {self.game.format_game_time()}")
        
        # Mise à jour des widgets
        if self.terminal:
            self.terminal.update_ui(delta_time)
        
        if self.map_view:
            self.map_view.update_ui(delta_time)
        
        if self.mission_board:
            self.mission_board.update_ui(delta_time)
        
        if self.character_sheet:
            self.character_sheet.update_ui(delta_time)
        
        if self.messaging:
            self.messaging.update_ui(delta_time)
    
    def _update_ui_from_game(self) -> None:
        """Met à jour l'interface avec les données du jeu"""
        if not self.game or not self.game.player or not self.game.world_manager:
            return
        
        # Mise à jour de l'emplacement
        current_location = self.game.world_manager.get_current_location()
        if current_location:
            self.location_label.setText(f"Emplacement: {current_location.name}")
        
        # Mise à jour de l'argent
        self.money_label.setText(f"Credits: {self.game.player.money}")
        
        # Mise à jour du niveau et de l'XP
        xp_next = self.game.player.xp_for_next_level()
        self.level_label.setText(f"Niveau: {self.game.player.level} | XP: {self.game.player.xp}/{xp_next}")
    
    def _toggle_terminal(self, checked: bool) -> None:
        """Active ou désactive l'affichage du terminal"""
        if self.terminal:
            self.terminal.setVisible(checked)
    
    def _toggle_map(self, checked: bool) -> None:
        """Active ou désactive l'affichage de la carte"""
        if self.map_view:
            self.map_view.setVisible(checked)
    
    def _toggle_pause(self, checked: bool) -> None:
        """Met le jeu en pause ou le reprend"""
        self.paused = checked
        
        if self.game:
            if self.paused:
                self.game.pause()
                self.pause_button.setText("Reprendre")
            else:
                self.game.resume()
                self.pause_button.setText("Pause")
    
    def _on_save_game(self) -> None:
        """Gère la sauvegarde du jeu"""
        if self.game:
            # Sauvegarde automatique
            success = self.game.save_game("quick_save")
            
            if success:
                # Affichage d'un message dans le terminal
                if self.terminal:
                    self.terminal.add_system_message("Partie sauvegardée avec succès.")
            else:
                # Affichage d'un message d'erreur dans le terminal
                if self.terminal:
                    self.terminal.add_system_message("Erreur lors de la sauvegarde de la partie.", error=True)
    
    def _on_load_game(self) -> None:
        """Gère le chargement d'une sauvegarde"""
        # Retour au menu principal pour charger une partie
        self.show_screen("main_menu")
    
    def _on_settings(self) -> None:
        """Ouvre l'écran des paramètres"""
        # Mise en pause du jeu
        if self.game and not self.paused:
            self.game.pause()
        
        # Affichage de l'écran des paramètres
        self.show_screen("settings")
    
    def _on_quit(self) -> None:
        """Gère la demande de quitter le jeu"""
        # Émission du signal de quitter le jeu
        self.quit_game_signal.emit()
    
    def _on_quit_game(self) -> None:
        """Quitte la partie en cours"""
        if self.game:
            # Sauvegarde automatique si configurée
            if self.game.config.get("auto_save_on_quit", True):
                self.game.save_game("auto_save")
            
            # Arrêt du jeu
            self.game.quit()
        
        # Retour au menu principal
        self.show_screen("main_menu")
