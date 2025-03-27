"""
Module pour l'écran de chargement du jeu YakTaa
"""

import logging
import random
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, 
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont

from yaktaa.ui.screens.base_screen import BaseScreen
from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.LoadingScreen")

class LoadingScreen(BaseScreen):
    """Écran de chargement du jeu"""
    
    # Liste de conseils à afficher pendant le chargement
    TIPS = [
        "Utilisez le terminal pour interagir avec les systèmes informatiques.",
        "Améliorez vos compétences en hacking pour accéder à des systèmes plus sécurisés.",
        "Explorez différentes villes pour découvrir de nouvelles missions et opportunités.",
        "Certains équipements peuvent être combinés pour créer des outils plus puissants.",
        "Les missions secondaires peuvent vous apporter des récompenses uniques.",
        "Gardez un œil sur votre réputation auprès des différentes factions.",
        "Les boutiques proposent des articles différents selon les villes.",
        "Utilisez la commande 'help' dans le terminal pour afficher les commandes disponibles.",
        "Les missions de haut niveau nécessitent une préparation adéquate.",
        "Sauvegardez régulièrement votre progression pour éviter de perdre vos données.",
        "Certains PNJ peuvent vous donner des informations précieuses si vous gagnez leur confiance.",
        "Les réseaux sécurisés peuvent contenir des données de grande valeur.",
        "Améliorez votre équipement pour augmenter vos chances de succès.",
        "Chaque ville a sa propre ambiance et ses propres défis.",
        "Certains lieux ne sont accessibles qu'avec un niveau de réputation suffisant.",
        "Les missions principales font avancer l'histoire du jeu.",
        "Certains systèmes informatiques peuvent être piratés de différentes manières.",
        "Votre style de jeu influence la façon dont les PNJ interagissent avec vous.",
        "Explorez les zones cachées pour découvrir des secrets.",
        "Utilisez la carte pour planifier vos déplacements efficacement."
    ]
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise l'écran de chargement"""
        super().__init__(game, parent)
        
        # Timer pour simuler le chargement
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.update_progress)
        
        # Progression du chargement
        self.progress = 0
        self.target_progress = 100
        self.progress_step = 1
        self.next_screen = None
        
        logger.info("Écran de chargement initialisé")
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur de l'écran de chargement"""
        # Mise en page principale
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Espacement
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Titre de chargement
        self.loading_label = QLabel("Chargement...", self)
        font = QFont("Cyberpunk", 36)
        self.loading_label.setFont(font)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {self.main_window.theme.get_color('primary')};")
        self.layout.addWidget(self.loading_label)
        
        # Barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumSize(QSize(400, 30))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.main_window.theme.get_color('primary')};
                border-radius: 5px;
                text-align: center;
                background-color: {self.main_window.theme.get_color('background_alt')};
            }}
            
            QProgressBar::chunk {{
                background-color: {self.main_window.theme.get_color('primary')};
            }}
        """)
        self.layout.addWidget(self.progress_bar)
        
        # Conseil
        self.tip_label = QLabel(self)
        tip_font = QFont("Segoe UI", 12)
        self.tip_label.setFont(tip_font)
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label.setStyleSheet(f"color: {self.main_window.theme.get_color('secondary')};")
        self.tip_label.setWordWrap(True)
        self.tip_label.setMinimumSize(QSize(600, 60))
        self.layout.addWidget(self.tip_label)
        
        # Espacement
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def on_show(self) -> None:
        """Appelé lorsque l'écran est affiché"""
        super().on_show()
        
        # Réinitialisation de la progression
        self.progress = 0
        self.progress_bar.setValue(0)
        
        # Affichage d'un conseil aléatoire
        self.tip_label.setText(f"Conseil: {random.choice(self.TIPS)}")
        
        # Démarrage du timer de chargement
        self.loading_timer.start(30)  # Mise à jour toutes les 30ms
    
    def on_hide(self) -> None:
        """Appelé lorsque l'écran est masqué"""
        super().on_hide()
        
        # Arrêt du timer de chargement
        self.loading_timer.stop()
    
    def update_progress(self) -> None:
        """Met à jour la progression du chargement"""
        # Incrémentation de la progression
        self.progress += self.progress_step
        
        # Mise à jour de la barre de progression
        self.progress_bar.setValue(self.progress)
        
        # Si le chargement est terminé
        if self.progress >= self.target_progress:
            # Arrêt du timer
            self.loading_timer.stop()
            
            # Passage à l'écran suivant
            if self.next_screen:
                self.show_screen(self.next_screen)
            else:
                # Par défaut, retour au menu principal
                self.show_screen("main_menu")
    
    def start_loading(self, next_screen: str, duration_ms: int = 3000) -> None:
        """Démarre le chargement vers l'écran spécifié"""
        # Configuration du chargement
        self.next_screen = next_screen
        self.progress = 0
        self.progress_bar.setValue(0)
        
        # Calcul du pas de progression en fonction de la durée
        update_interval = self.loading_timer.interval()
        num_updates = duration_ms / update_interval
        self.progress_step = self.target_progress / num_updates
        
        # Affichage d'un conseil aléatoire
        self.tip_label.setText(f"Conseil: {random.choice(self.TIPS)}")
        
        # Démarrage du timer
        self.loading_timer.start(update_interval)
        
        logger.info(f"Chargement démarré vers l'écran: {next_screen} (durée: {duration_ms}ms)")
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur"""
        # Animation du texte de chargement (à implémenter)
        pass
