"""
Module pour le widget de tableau de missions du jeu YakTaa
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, 
    QSplitter, QFrame, QTabWidget, QGridLayout,
    QScrollArea, QToolBar, QMenu, QToolButton,
    QSizePolicy, QSpacerItem, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QDateTime
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QBrush, QAction

from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.MissionBoard")

class Mission:
    """Classe représentant une mission dans le jeu"""
    
    def __init__(self, 
                 id: str, 
                 title: str, 
                 description: str, 
                 difficulty: int = 1,
                 reward_money: int = 100,
                 reward_xp: int = 50,
                 reward_items: List[Dict[str, Any]] = None,
                 time_limit: Optional[int] = None,  # En minutes de jeu
                 prerequisites: List[str] = None,
                 location_id: Optional[str] = None,
                 faction_id: Optional[str] = None,
                 mission_type: str = "hack",
                 objectives: List[Dict[str, Any]] = None,
                 status: str = "available",
                 progress: int = 0):
        """Initialise une mission"""
        self.id = id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.reward_money = reward_money
        self.reward_xp = reward_xp
        self.reward_items = reward_items or []
        self.time_limit = time_limit
        self.prerequisites = prerequisites or []
        self.location_id = location_id
        self.faction_id = faction_id
        self.mission_type = mission_type
        self.objectives = objectives or []
        self.status = status
        
        # Dates de début et de fin
        self.start_time = None
        self.end_time = None
        
        # Progression
        self.progress = progress  # 0-100%
    
    def start(self) -> None:
        """Démarre la mission"""
        self.status = "active"
        self.start_time = datetime.now()
        
        if self.time_limit:
            self.end_time = self.start_time + timedelta(minutes=self.time_limit)
    
    def complete(self) -> None:
        """Marque la mission comme terminée"""
        self.status = "completed"
        self.progress = 100
    
    def fail(self) -> None:
        """Marque la mission comme échouée"""
        self.status = "failed"
    
    def update_progress(self, progress: int) -> None:
        """Met à jour la progression de la mission"""
        self.progress = max(0, min(100, progress))
        
        if self.progress >= 100:
            self.complete()
    
    def is_expired(self) -> bool:
        """Vérifie si la mission a expiré"""
        if not self.time_limit or not self.start_time or not self.end_time:
            return False
        
        return datetime.now() > self.end_time
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """Retourne le temps restant pour la mission"""
        if not self.time_limit or not self.end_time:
            return None
        
        remaining = self.end_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def get_objective_status(self) -> Tuple[int, int]:
        """Retourne le nombre d'objectifs complétés et le total"""
        if not self.objectives:
            return 0, 0
        
        completed = sum(1 for obj in self.objectives if obj.get("completed", False))
        return completed, len(self.objectives)


class MissionWidget(QFrame):
    """Widget représentant une mission dans l'interface"""
    
    # Signaux
    mission_clicked = pyqtSignal(Mission)
    mission_accepted = pyqtSignal(Mission)
    mission_abandoned = pyqtSignal(Mission)
    
    def __init__(self, mission: Mission, parent: Optional[QWidget] = None):
        """Initialise un widget de mission"""
        super().__init__(parent)
        
        # Référence à la mission
        self.mission = mission
        
        # Configuration du widget
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)
        
        # Style du widget selon le statut de la mission
        self._update_style()
        
        # Mise en page
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Indicateur de difficulté
        self.difficulty_widget = QWidget()
        self.difficulty_widget.setFixedWidth(30)
        self.difficulty_layout = QVBoxLayout(self.difficulty_widget)
        self.difficulty_layout.setContentsMargins(0, 0, 0, 0)
        self.difficulty_layout.setSpacing(2)
        
        # Étoiles de difficulté
        for i in range(5):
            star_label = QLabel("★" if i < mission.difficulty else "☆")
            star_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            star_label.setStyleSheet(f"""
                QLabel {{
                    color: {'#FFAA00' if i < mission.difficulty else '#666666'};
                    font-size: 14px;
                }}
            """)
            self.difficulty_layout.addWidget(star_label)
        
        self.difficulty_layout.addStretch()
        self.layout.addWidget(self.difficulty_widget)
        
        # Informations de la mission
        info_layout = QVBoxLayout()
        
        # Titre et type
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel(mission.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(self.title_label)
        
        self.type_label = QLabel(f"[{mission.mission_type.upper()}]")
        self.type_label.setStyleSheet("color: #AAAAAA;")
        title_layout.addWidget(self.type_label)
        
        title_layout.addStretch()
        
        # Statut ou temps restant
        self.status_label = QLabel()
        self._update_status_label()
        title_layout.addWidget(self.status_label)
        
        info_layout.addLayout(title_layout)
        
        # Description
        self.description_label = QLabel(mission.description)
        self.description_label.setWordWrap(True)
        info_layout.addWidget(self.description_label)
        
        # Barre de progression (uniquement pour les missions actives)
        if mission.status == "active":
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(mission.progress)
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat("%p%")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #333333;
                }
                
                QProgressBar::chunk {
                    background-color: #00AA00;
                    border-radius: 5px;
                }
            """)
            info_layout.addWidget(self.progress_bar)
        
        # Récompenses
        rewards_layout = QHBoxLayout()
        
        self.money_label = QLabel(f"💰 {mission.reward_money}")
        self.money_label.setToolTip(f"{mission.reward_money} crédits")
        rewards_layout.addWidget(self.money_label)
        
        self.xp_label = QLabel(f"⭐ {mission.reward_xp}")
        self.xp_label.setToolTip(f"{mission.reward_xp} points d'expérience")
        rewards_layout.addWidget(self.xp_label)
        
        if mission.reward_items:
            self.items_label = QLabel(f"📦 {len(mission.reward_items)}")
            self.items_label.setToolTip(f"{len(mission.reward_items)} objets")
            rewards_layout.addWidget(self.items_label)
        
        rewards_layout.addStretch()
        
        info_layout.addLayout(rewards_layout)
        
        self.layout.addLayout(info_layout, 1)
        
        # Boutons d'action
        action_layout = QVBoxLayout()
        
        if mission.status == "available":
            self.accept_button = QPushButton("Accepter")
            self.accept_button.clicked.connect(self._on_accept)
            action_layout.addWidget(self.accept_button)
        elif mission.status == "active":
            self.abandon_button = QPushButton("Abandonner")
            self.abandon_button.clicked.connect(self._on_abandon)
            action_layout.addWidget(self.abandon_button)
        
        action_layout.addStretch()
        
        self.layout.addLayout(action_layout)
        
        # Interactivité
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _update_style(self) -> None:
        """Met à jour le style du widget selon le statut de la mission"""
        base_style = """
            QFrame {
                border-radius: 5px;
            }
            
            QLabel {
                color: #FFFFFF;
            }
            
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            
            QPushButton:hover {
                background-color: #444444;
            }
            
            QPushButton:pressed {
                background-color: #555555;
            }
        """
        
        if self.mission.status == "available":
            self.setStyleSheet(base_style + """
                QFrame {
                    background-color: #222222;
                    border: 1px solid #444444;
                }
            """)
        elif self.mission.status == "active":
            self.setStyleSheet(base_style + """
                QFrame {
                    background-color: #223322;
                    border: 1px solid #00AA00;
                }
            """)
        elif self.mission.status == "completed":
            self.setStyleSheet(base_style + """
                QFrame {
                    background-color: #222244;
                    border: 1px solid #4444AA;
                }
            """)
        elif self.mission.status == "failed":
            self.setStyleSheet(base_style + """
                QFrame {
                    background-color: #442222;
                    border: 1px solid #AA4444;
                }
            """)
    
    def _update_status_label(self) -> None:
        """Met à jour l'étiquette de statut"""
        if self.mission.status == "available":
            self.status_label.setText("Disponible")
            self.status_label.setStyleSheet("color: #AAAAAA;")
        elif self.mission.status == "active":
            if self.mission.time_limit:
                remaining = self.mission.get_time_remaining()
                if remaining:
                    hours, remainder = divmod(remaining.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                    self.status_label.setText(f"Temps: {time_str}")
                    
                    # Changement de couleur si le temps est presque écoulé
                    if remaining.total_seconds() < 300:  # Moins de 5 minutes
                        self.status_label.setStyleSheet("color: #FF0000;")
                    else:
                        self.status_label.setStyleSheet("color: #FFAA00;")
                else:
                    self.status_label.setText("Temps écoulé!")
                    self.status_label.setStyleSheet("color: #FF0000;")
            else:
                self.status_label.setText("En cours")
                self.status_label.setStyleSheet("color: #00AA00;")
        elif self.mission.status == "completed":
            self.status_label.setText("Terminée")
            self.status_label.setStyleSheet("color: #4444FF;")
        elif self.mission.status == "failed":
            self.status_label.setText("Échouée")
            self.status_label.setStyleSheet("color: #FF4444;")
    
    def _on_accept(self) -> None:
        """Gère l'acceptation de la mission"""
        self.mission_accepted.emit(self.mission)
    
    def _on_abandon(self) -> None:
        """Gère l'abandon de la mission"""
        self.mission_abandoned.emit(self.mission)
    
    def mousePressEvent(self, event):
        """Gère l'appui sur un bouton de la souris"""
        self.mission_clicked.emit(self.mission)
        super().mousePressEvent(event)
    
    def update_mission(self, mission: Mission) -> None:
        """Met à jour la mission affichée"""
        self.mission = mission
        
        # Mise à jour des informations
        self.title_label.setText(mission.title)
        self.description_label.setText(mission.description)
        self.money_label.setText(f"💰 {mission.reward_money}")
        self.xp_label.setText(f"⭐ {mission.reward_xp}")
        
        # Mise à jour du statut
        self._update_status_label()
        
        # Mise à jour de la progression si applicable
        if hasattr(self, "progress_bar"):
            self.progress_bar.setValue(mission.progress)
        
        # Mise à jour du style
        self._update_style()


class MissionBoardWidget(QWidget):
    """Widget de tableau de missions pour YakTaa"""
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise le widget de tableau de missions"""
        super().__init__(parent)
        
        # Référence au jeu
        self.game = game
        
        # Mission sélectionnée
        self.selected_mission = None
        
        # Mise en page
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Barre d'outils
        self._create_toolbar()
        
        # Splitter principal
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.layout.addWidget(self.main_splitter)
        
        # Panneau supérieur avec les onglets de missions
        self.mission_tabs = QTabWidget()
        self.mission_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.mission_tabs.setDocumentMode(True)
        self.mission_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #222222;
            }
            
            QTabBar::tab {
                background-color: #333333;
                color: #CCCCCC;
                padding: 5px 10px;
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
        """)
        
        # Onglet Actives
        self.active_missions_widget = QWidget()
        self.active_missions_layout = QVBoxLayout(self.active_missions_widget)
        self.active_missions_layout.setContentsMargins(10, 10, 10, 10)
        self.active_missions_layout.setSpacing(10)
        
        self.active_missions_scroll = QScrollArea()
        self.active_missions_scroll.setWidgetResizable(True)
        self.active_missions_scroll.setWidget(self.active_missions_widget)
        self.active_missions_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #222222;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #333333;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.mission_tabs.addTab(self.active_missions_scroll, "Actives")
        
        # Onglet Disponibles
        self.available_missions_widget = QWidget()
        self.available_missions_layout = QVBoxLayout(self.available_missions_widget)
        self.available_missions_layout.setContentsMargins(10, 10, 10, 10)
        self.available_missions_layout.setSpacing(10)
        
        self.available_missions_scroll = QScrollArea()
        self.available_missions_scroll.setWidgetResizable(True)
        self.available_missions_scroll.setWidget(self.available_missions_widget)
        self.available_missions_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #222222;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #333333;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.mission_tabs.addTab(self.available_missions_scroll, "Disponibles")
        
        # Onglet Terminées
        self.completed_missions_widget = QWidget()
        self.completed_missions_layout = QVBoxLayout(self.completed_missions_widget)
        self.completed_missions_layout.setContentsMargins(10, 10, 10, 10)
        self.completed_missions_layout.setSpacing(10)
        
        self.completed_missions_scroll = QScrollArea()
        self.completed_missions_scroll.setWidgetResizable(True)
        self.completed_missions_scroll.setWidget(self.completed_missions_widget)
        self.completed_missions_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #222222;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #333333;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.mission_tabs.addTab(self.completed_missions_scroll, "Terminées")
        
        self.main_splitter.addWidget(self.mission_tabs)
        
        # Panneau de détails de mission
        self.mission_details = QFrame()
        self.mission_details.setFrameShape(QFrame.Shape.StyledPanel)
        self.mission_details.setMinimumHeight(200)
        self.mission_details.setStyleSheet("""
            QFrame {
                background-color: #222222;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            
            QLabel {
                color: #FFFFFF;
            }
            
            QTextEdit {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            
            QPushButton:hover {
                background-color: #444444;
            }
            
            QPushButton:pressed {
                background-color: #555555;
            }
            
            QPushButton:disabled {
                background-color: #222222;
                color: #666666;
            }
        """)
        
        details_layout = QVBoxLayout(self.mission_details)
        
        # Titre et difficulté
        title_layout = QHBoxLayout()
        
        self.details_title = QLabel("Sélectionnez une mission")
        self.details_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        title_layout.addWidget(self.details_title)
        
        self.details_difficulty = QLabel("")
        title_layout.addWidget(self.details_difficulty)
        
        title_layout.addStretch()
        
        details_layout.addLayout(title_layout)
        
        # Description
        self.details_description = QTextEdit()
        self.details_description.setReadOnly(True)
        self.details_description.setMaximumHeight(100)
        details_layout.addWidget(self.details_description)
        
        # Objectifs
        objectives_layout = QVBoxLayout()
        
        objectives_header = QLabel("Objectifs:")
        objectives_header.setStyleSheet("font-weight: bold;")
        objectives_layout.addWidget(objectives_header)
        
        self.objectives_tree = QTreeWidget()
        self.objectives_tree.setHeaderHidden(True)
        self.objectives_tree.setMaximumHeight(150)
        self.objectives_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            
            QTreeWidget::item {
                padding: 2px;
            }
            
            QTreeWidget::item:selected {
                background-color: #555555;
            }
        """)
        objectives_layout.addWidget(self.objectives_tree)
        
        details_layout.addLayout(objectives_layout)
        
        # Récompenses
        rewards_layout = QVBoxLayout()
        
        rewards_header = QLabel("Récompenses:")
        rewards_header.setStyleSheet("font-weight: bold;")
        rewards_layout.addWidget(rewards_header)
        
        rewards_grid = QGridLayout()
        
        self.reward_money_label = QLabel("Crédits: 0")
        rewards_grid.addWidget(self.reward_money_label, 0, 0)
        
        self.reward_xp_label = QLabel("XP: 0")
        rewards_grid.addWidget(self.reward_xp_label, 0, 1)
        
        self.reward_items_label = QLabel("Objets: 0")
        rewards_grid.addWidget(self.reward_items_label, 1, 0, 1, 2)
        
        rewards_layout.addLayout(rewards_grid)
        
        details_layout.addLayout(rewards_layout)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.track_button = QPushButton("Suivre")
        self.track_button.setEnabled(False)
        self.track_button.clicked.connect(self._track_mission)
        actions_layout.addWidget(self.track_button)
        
        self.abandon_button = QPushButton("Abandonner")
        self.abandon_button.setEnabled(False)
        self.abandon_button.clicked.connect(self._abandon_mission)
        actions_layout.addWidget(self.abandon_button)
        
        details_layout.addLayout(actions_layout)
        
        self.main_splitter.addWidget(self.mission_details)
        
        # Configuration du splitter
        self.main_splitter.setSizes([400, 200])
        
        # Chargement des missions
        self._load_missions()
        
        logger.info("Widget de tableau de missions initialisé")
    
    def _create_toolbar(self) -> None:
        """Crée la barre d'outils du tableau de missions"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #222222;
                border: none;
                border-bottom: 1px solid #444444;
                spacing: 2px;
                padding: 2px;
            }
            
            QToolButton {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                border-radius: 2px;
                padding: 2px;
            }
            
            QToolButton:hover {
                background-color: #444444;
            }
            
            QToolButton:pressed {
                background-color: #555555;
            }
        """)
        
        # Actions
        self.filter_button = QToolButton()
        self.filter_button.setText("Filtrer")
        self.filter_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Menu de filtrage
        self.filter_menu = QMenu(self.filter_button)
        
        self.filter_all_action = QAction("Toutes", self.filter_menu)
        self.filter_all_action.setCheckable(True)
        self.filter_all_action.setChecked(True)
        self.filter_all_action.triggered.connect(lambda: self._filter_missions("all"))
        self.filter_menu.addAction(self.filter_all_action)
        
        self.filter_menu.addSeparator()
        
        self.filter_hack_action = QAction("Hacking", self.filter_menu)
        self.filter_hack_action.setCheckable(True)
        self.filter_hack_action.triggered.connect(lambda: self._filter_missions("hack"))
        self.filter_menu.addAction(self.filter_hack_action)
        
        self.filter_retrieval_action = QAction("Récupération", self.filter_menu)
        self.filter_retrieval_action.setCheckable(True)
        self.filter_retrieval_action.triggered.connect(lambda: self._filter_missions("retrieval"))
        self.filter_menu.addAction(self.filter_retrieval_action)
        
        self.filter_escort_action = QAction("Escorte", self.filter_menu)
        self.filter_escort_action.setCheckable(True)
        self.filter_escort_action.triggered.connect(lambda: self._filter_missions("escort"))
        self.filter_menu.addAction(self.filter_escort_action)
        
        self.filter_button.setMenu(self.filter_menu)
        self.toolbar.addWidget(self.filter_button)
        
        # Bouton de tri
        self.sort_button = QToolButton()
        self.sort_button.setText("Trier")
        self.sort_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Menu de tri
        self.sort_menu = QMenu(self.sort_button)
        
        self.sort_difficulty_action = QAction("Par difficulté", self.sort_menu)
        self.sort_difficulty_action.triggered.connect(lambda: self._sort_missions("difficulty"))
        self.sort_menu.addAction(self.sort_difficulty_action)
        
        self.sort_reward_action = QAction("Par récompense", self.sort_menu)
        self.sort_reward_action.triggered.connect(lambda: self._sort_missions("reward"))
        self.sort_menu.addAction(self.sort_reward_action)
        
        self.sort_button.setMenu(self.sort_menu)
        self.toolbar.addWidget(self.sort_button)
        
        # Bouton de recherche
        self.search_action = QAction("Rechercher", self.toolbar)
        self.search_action.triggered.connect(self._search_missions)
        self.toolbar.addAction(self.search_action)
        
        # Espacement
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Statistiques
        self.stats_label = QLabel("Missions actives: 0 | Terminées: 0")
        self.toolbar.addWidget(self.stats_label)
        
        self.layout.addWidget(self.toolbar)
    
    def _load_missions(self) -> None:
        """Charge les missions depuis le jeu"""
        # Exemple de missions (dans une implémentation réelle, elles viendraient du jeu)
        missions = [
            Mission(
                "m1", 
                "Infiltration de MegaCorp", 
                "Infiltrez le réseau de MegaCorp et récupérez des données confidentielles sur leur nouveau produit.",
                difficulty=3,
                reward_money=1000,
                reward_xp=200,
                mission_type="hack",
                objectives=[
                    {"id": "obj1", "description": "Accéder au réseau de MegaCorp", "completed": False},
                    {"id": "obj2", "description": "Localiser les fichiers confidentiels", "completed": False},
                    {"id": "obj3", "description": "Télécharger les données", "completed": False},
                    {"id": "obj4", "description": "Effacer vos traces", "completed": False}
                ],
                status="available"
            ),
            Mission(
                "m2", 
                "Récupération de prototype", 
                "Un prototype de puce neurologique a été volé. Retrouvez-le et rapportez-le à son propriétaire légitime.",
                difficulty=2,
                reward_money=800,
                reward_xp=150,
                mission_type="retrieval",
                objectives=[
                    {"id": "obj1", "description": "Localiser le voleur", "completed": False},
                    {"id": "obj2", "description": "Récupérer le prototype", "completed": False},
                    {"id": "obj3", "description": "Retourner au point de rendez-vous", "completed": False}
                ],
                status="available"
            ),
            Mission(
                "m3", 
                "Protection de données", 
                "Un client important a besoin de protection pendant qu'il transfère des données sensibles. Assurez sa sécurité.",
                difficulty=4,
                reward_money=1500,
                reward_xp=300,
                mission_type="escort",
                objectives=[
                    {"id": "obj1", "description": "Rencontrer le client", "completed": True},
                    {"id": "obj2", "description": "Escorter le client jusqu'au point de transfert", "completed": False},
                    {"id": "obj3", "description": "Protéger le client pendant le transfert", "completed": False},
                    {"id": "obj4", "description": "Retourner à la base en sécurité", "completed": False}
                ],
                status="active",
                progress=25
            ),
            Mission(
                "m4", 
                "Piratage de drone", 
                "Prenez le contrôle d'un drone de surveillance et utilisez-le pour espionner une réunion secrète.",
                difficulty=2,
                reward_money=600,
                reward_xp=120,
                mission_type="hack",
                objectives=[
                    {"id": "obj1", "description": "Localiser le drone", "completed": True},
                    {"id": "obj2", "description": "Pirater le système de contrôle", "completed": True},
                    {"id": "obj3", "description": "Enregistrer la réunion", "completed": True},
                    {"id": "obj4", "description": "Transmettre les données", "completed": True}
                ],
                status="completed",
                progress=100
            )
        ]
        
        # Affichage des missions
        self._display_missions(missions)
        
        # Mise à jour des statistiques
        active_count = sum(1 for m in missions if m.status == "active")
        completed_count = sum(1 for m in missions if m.status == "completed")
        self.stats_label.setText(f"Missions actives: {active_count} | Terminées: {completed_count}")
    
    def _display_missions(self, missions: List[Mission]) -> None:
        """Affiche les missions dans l'interface"""
        # Effacement des missions existantes
        self._clear_missions()
        
        # Tri des missions par statut
        active_missions = [m for m in missions if m.status == "active"]
        available_missions = [m for m in missions if m.status == "available"]
        completed_missions = [m for m in missions if m.status in ["completed", "failed"]]
        
        # Affichage des missions actives
        for mission in active_missions:
            mission_widget = MissionWidget(mission)
            
            # Connexion des signaux
            mission_widget.mission_clicked.connect(self._on_mission_clicked)
            mission_widget.mission_abandoned.connect(self._on_mission_abandoned)
            
            self.active_missions_layout.addWidget(mission_widget)
        
        # Ajout d'un spacer pour les missions actives
        self.active_missions_layout.addStretch()
        
        # Affichage des missions disponibles
        for mission in available_missions:
            mission_widget = MissionWidget(mission)
            
            # Connexion des signaux
            mission_widget.mission_clicked.connect(self._on_mission_clicked)
            mission_widget.mission_accepted.connect(self._on_mission_accepted)
            
            self.available_missions_layout.addWidget(mission_widget)
        
        # Ajout d'un spacer pour les missions disponibles
        self.available_missions_layout.addStretch()
        
        # Affichage des missions terminées
        for mission in completed_missions:
            mission_widget = MissionWidget(mission)
            
            # Connexion des signaux
            mission_widget.mission_clicked.connect(self._on_mission_clicked)
            
            self.completed_missions_layout.addWidget(mission_widget)
        
        # Ajout d'un spacer pour les missions terminées
        self.completed_missions_layout.addStretch()
    
    def _clear_missions(self) -> None:
        """Efface toutes les missions de l'interface"""
        # Effacement des missions actives
        while self.active_missions_layout.count():
            item = self.active_missions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Effacement des missions disponibles
        while self.available_missions_layout.count():
            item = self.available_missions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Effacement des missions terminées
        while self.completed_missions_layout.count():
            item = self.completed_missions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _on_mission_clicked(self, mission: Mission) -> None:
        """Gère le clic sur une mission"""
        self.selected_mission = mission
        
        # Mise à jour du panneau de détails
        self.details_title.setText(mission.title)
        self.details_difficulty.setText("★" * mission.difficulty + "☆" * (5 - mission.difficulty))
        self.details_description.setText(mission.description)
        
        # Mise à jour des objectifs
        self.objectives_tree.clear()
        
        for objective in mission.objectives:
            item = QTreeWidgetItem([objective["description"]])
            
            # Style selon l'état de l'objectif
            if objective.get("completed", False):
                item.setForeground(0, QBrush(QColor("#00AA00")))
                item.setText(0, "✓ " + objective["description"])
            
            self.objectives_tree.addTopLevelItem(item)
        
        # Mise à jour des récompenses
        self.reward_money_label.setText(f"Crédits: {mission.reward_money}")
        self.reward_xp_label.setText(f"XP: {mission.reward_xp}")
        self.reward_items_label.setText(f"Objets: {len(mission.reward_items)}")
        
        # Activation des boutons selon le statut de la mission
        self.track_button.setEnabled(mission.status == "active")
        self.abandon_button.setEnabled(mission.status == "active")
    
    def _on_mission_accepted(self, mission: Mission) -> None:
        """Gère l'acceptation d'une mission"""
        # Dans une implémentation réelle, cette logique serait dans le gestionnaire de missions du jeu
        mission.start()
        
        # Mise à jour de l'interface
        self._refresh_missions()
        
        # Sélection de l'onglet des missions actives
        self.mission_tabs.setCurrentIndex(0)
    
    def _on_mission_abandoned(self, mission: Mission) -> None:
        """Gère l'abandon d'une mission"""
        # Dans une implémentation réelle, cette logique serait dans le gestionnaire de missions du jeu
        mission.fail()
        
        # Mise à jour de l'interface
        self._refresh_missions()
        
        # Sélection de l'onglet des missions terminées
        self.mission_tabs.setCurrentIndex(2)
    
    def _track_mission(self) -> None:
        """Suit la mission sélectionnée"""
        if not self.selected_mission or self.selected_mission.status != "active":
            return
        
        # TODO: Implémenter le suivi de mission (marquage comme mission principale, etc.)
        pass
    
    def _abandon_mission(self) -> None:
        """Abandonne la mission sélectionnée"""
        if not self.selected_mission or self.selected_mission.status != "active":
            return
        
        self._on_mission_abandoned(self.selected_mission)
    
    def _filter_missions(self, filter_type: str) -> None:
        """Filtre les missions selon un critère"""
        # TODO: Implémenter le filtrage des missions
        pass
    
    def _sort_missions(self, sort_by: str) -> None:
        """Trie les missions selon un critère"""
        # TODO: Implémenter le tri des missions
        pass
    
    def _search_missions(self) -> None:
        """Recherche des missions"""
        # TODO: Implémenter la recherche de missions
        pass
    
    def _refresh_missions(self) -> None:
        """Rafraîchit l'affichage des missions"""
        # Rechargement des missions
        self._load_missions()
        
        # Réinitialisation du panneau de détails si la mission sélectionnée n'est plus disponible
        if self.selected_mission:
            # TODO: Vérifier si la mission existe toujours et mettre à jour le panneau
            pass
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur du tableau de missions"""
        # Mise à jour des temps restants pour les missions avec limite de temps
        # TODO: Implémenter la mise à jour des temps restants
        pass
