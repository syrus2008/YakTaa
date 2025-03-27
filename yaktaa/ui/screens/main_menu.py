"""
Module pour l'écran de menu principal du jeu YakTaa
"""

import logging
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy, QListWidget, 
    QListWidgetItem, QDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon

from yaktaa.ui.screens.base_screen import BaseScreen
from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.MainMenu")

class MainMenuScreen(BaseScreen):
    """Écran du menu principal du jeu"""
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise l'écran de menu principal"""
        super().__init__(game, parent)
        
        # État de l'écran
        self.save_games = []
        
        logger.info("Écran de menu principal initialisé")
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur du menu principal"""
        # Mise en page principale
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo du jeu
        self.logo_label = QLabel(self)
        # Ici, nous utiliserons un texte temporaire en attendant un logo
        self.logo_label.setText("YakTaa")
        font = QFont("Cyberpunk", 72)
        font.setBold(True)
        self.logo_label.setFont(font)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet(f"color: {self.main_window.theme.get_color('primary')};")
        self.layout.addWidget(self.logo_label)
        
        # Sous-titre
        subtitle = QLabel("Un jeu de rôle cyberpunk avec terminal et exploration", self)
        subtitle_font = QFont("NeonRetro", 18)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.main_window.theme.get_color('secondary')};")
        self.layout.addWidget(subtitle)
        
        # Espacement
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Conteneur pour les boutons
        button_container = QWidget(self)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Bouton Nouvelle Partie
        self.new_game_btn = QPushButton("Nouvelle Partie", self)
        self.new_game_btn.setMinimumSize(QSize(250, 50))
        self.new_game_btn.clicked.connect(self.on_new_game)
        button_layout.addWidget(self.new_game_btn)
        
        # Bouton Charger Partie
        self.load_game_btn = QPushButton("Charger Partie", self)
        self.load_game_btn.setMinimumSize(QSize(250, 50))
        self.load_game_btn.clicked.connect(self.on_load_game)
        button_layout.addWidget(self.load_game_btn)
        
        # Bouton Paramètres
        self.settings_btn = QPushButton("Paramètres", self)
        self.settings_btn.setMinimumSize(QSize(250, 50))
        self.settings_btn.clicked.connect(self.on_settings)
        button_layout.addWidget(self.settings_btn)
        
        # Bouton Quitter
        self.quit_btn = QPushButton("Quitter", self)
        self.quit_btn.setMinimumSize(QSize(250, 50))
        self.quit_btn.clicked.connect(self.on_quit)
        button_layout.addWidget(self.quit_btn)
        
        self.layout.addWidget(button_container)
        
        # Espacement
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Version du jeu
        version_label = QLabel(f"Version {self.game.config.get('version', '0.1.0')}", self)
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(version_label)
    
    def on_show(self) -> None:
        """Appelé lorsque l'écran est affiché"""
        super().on_show()
        
        # Mise à jour de la liste des sauvegardes
        self.save_games = self.game.save_manager.get_all_saves()
        
        # Mise à jour de l'état des boutons
        self.load_game_btn.setEnabled(len(self.save_games) > 0)
    
    def on_new_game(self) -> None:
        """Gère le clic sur le bouton Nouvelle Partie"""
        logger.info("Nouvelle partie demandée")
        
        # Boîte de dialogue pour le nom du joueur
        dialog = NewGameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player_name = dialog.get_player_name()
            
            if player_name:
                # Affichage de l'écran de chargement
                self.show_screen("loading")
                
                # Création d'une nouvelle partie
                success = self.game.new_game(player_name)
                
                if success:
                    # Passage à l'écran de jeu
                    self.show_screen("game")
                else:
                    # Affichage d'un message d'erreur
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        "Impossible de créer une nouvelle partie. Consultez les logs pour plus d'informations."
                    )
                    
                    # Retour au menu principal
                    self.show_screen("main_menu")
    
    def on_load_game(self) -> None:
        """Gère le clic sur le bouton Charger Partie"""
        logger.info("Chargement de partie demandé")
        
        # Si aucune sauvegarde n'est disponible
        if not self.save_games:
            QMessageBox.information(
                self,
                "Information",
                "Aucune sauvegarde disponible."
            )
            return
        
        # Boîte de dialogue pour sélectionner une sauvegarde
        dialog = LoadGameDialog(self.save_games, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            save_id = dialog.get_selected_save_id()
            
            if save_id:
                # Affichage de l'écran de chargement
                self.show_screen("loading")
                
                # Chargement de la partie
                success = self.game.load_game(save_id)
                
                if success:
                    # Passage à l'écran de jeu
                    self.show_screen("game")
                else:
                    # Affichage d'un message d'erreur
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        "Impossible de charger la partie. Consultez les logs pour plus d'informations."
                    )
                    
                    # Retour au menu principal
                    self.show_screen("main_menu")
    
    def on_settings(self) -> None:
        """Gère le clic sur le bouton Paramètres"""
        logger.info("Paramètres demandés")
        self.show_screen("settings")
    
    def on_quit(self) -> None:
        """Gère le clic sur le bouton Quitter"""
        logger.info("Quitter demandé")
        
        # Confirmation avant de quitter
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir quitter YakTaa ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Fermeture de l'application
            self.main_window.close()


class NewGameDialog(QDialog):
    """Boîte de dialogue pour créer une nouvelle partie"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialise la boîte de dialogue"""
        super().__init__(parent)
        
        self.setWindowTitle("Nouvelle Partie")
        self.setMinimumWidth(300)
        
        # Mise en page
        layout = QVBoxLayout(self)
        
        # Label
        layout.addWidget(QLabel("Entrez votre nom de hacker:"))
        
        # Champ de texte
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Nom du joueur")
        layout.addWidget(self.name_edit)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Annuler", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("Commencer", self)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def get_player_name(self) -> str:
        """Retourne le nom du joueur saisi"""
        return self.name_edit.text().strip()


class LoadGameDialog(QDialog):
    """Boîte de dialogue pour charger une partie"""
    
    def __init__(self, save_games: List[Dict], parent: Optional[QWidget] = None):
        """Initialise la boîte de dialogue"""
        super().__init__(parent)
        
        self.setWindowTitle("Charger Partie")
        self.setMinimumSize(QSize(400, 300))
        
        # Sauvegarde sélectionnée
        self.selected_save_id = None
        
        # Mise en page
        layout = QVBoxLayout(self)
        
        # Label
        layout.addWidget(QLabel("Sélectionnez une sauvegarde:"))
        
        # Liste des sauvegardes
        self.save_list = QListWidget(self)
        self.save_list.setAlternatingRowColors(True)
        self.save_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.save_list)
        
        # Remplissage de la liste
        for save in save_games:
            item = QListWidgetItem(f"{save['player_name']} - Niveau {save['level']} - {save['date']}")
            item.setData(Qt.ItemDataRole.UserRole, save['id'])
            self.save_list.addItem(item)
        
        # Sélection du premier élément
        if self.save_list.count() > 0:
            self.save_list.setCurrentRow(0)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("Supprimer", self)
        self.delete_btn.clicked.connect(self.on_delete)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.cancel_btn = QPushButton("Annuler", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.load_btn = QPushButton("Charger", self)
        self.load_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.load_btn)
        
        layout.addLayout(button_layout)
    
    def get_selected_save_id(self) -> str:
        """Retourne l'ID de la sauvegarde sélectionnée"""
        current_item = self.save_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def on_delete(self) -> None:
        """Gère le clic sur le bouton Supprimer"""
        current_item = self.save_list.currentItem()
        if not current_item:
            return
        
        save_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Confirmation avant de supprimer
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette sauvegarde ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Récupération du gestionnaire de sauvegardes depuis le parent
            parent = self.parent()
            if parent and hasattr(parent, 'game') and hasattr(parent.game, 'save_manager'):
                save_manager = parent.game.save_manager
                
                # Suppression de la sauvegarde
                if save_manager.delete_save(save_id):
                    # Suppression de l'élément de la liste
                    row = self.save_list.row(current_item)
                    self.save_list.takeItem(row)
                    
                    # Si la liste est vide, fermeture de la boîte de dialogue
                    if self.save_list.count() == 0:
                        QMessageBox.information(
                            self,
                            "Information",
                            "Aucune sauvegarde disponible."
                        )
                        self.reject()
                else:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        "Impossible de supprimer la sauvegarde."
                    )
