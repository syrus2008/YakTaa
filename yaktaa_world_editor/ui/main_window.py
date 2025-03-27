#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la fenêtre principale de l'éditeur de monde YakTaa
"""

import os
import logging
import sqlite3
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QFileDialog, 
    QDockWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
    QFormLayout, QGroupBox, QSplitter, QTreeWidget, QTreeWidgetItem,
    QMenu, QToolBar, QStatusBar, QDialog
)
from PyQt6.QtCore import Qt, QSize, QSettings, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap

from ui.world_tab import WorldTab
from ui.location_editor import LocationEditor
from ui.character_editor import CharacterEditor
from ui.device_editor import DeviceEditor
from ui.welcome_dialog import WelcomeDialog
from ui.world_generator_dialog import WorldGeneratorDialog
from world_generator import WorldGenerator

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Fenêtre principale de l'éditeur de monde YakTaa"""
    
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        self.current_world_id = None
        # Utiliser le même chemin de base de données que l'éditeur principal
        self.world_generator = WorldGenerator(db_path=db.db_path)
        
        self.init_ui()
        self.load_settings()
        self.load_worlds_list()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la fenêtre
        self.setWindowTitle("YakTaa World Editor")
        self.setMinimumSize(1200, 800)
        
        # Barre d'outils
        self.create_toolbar()
        
        # Barre de statut
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")
        
        # Widget central avec onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Dock pour la liste des mondes
        self.create_worlds_dock()
        
        # Dock pour les propriétés
        self.create_properties_dock()
        
        # Créer les menus
        self.create_menus()
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        
        self.toolbar = QToolBar("Barre d'outils principale")
        self.toolbar.setObjectName("main_toolbar")  
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        
        # Actions
        new_world_action = QAction("Nouveau monde", self)
        new_world_action.triggered.connect(self.show_world_generator_dialog)
        self.toolbar.addAction(new_world_action)
        
        open_world_action = QAction("Ouvrir monde", self)
        open_world_action.triggered.connect(self.open_world)
        self.toolbar.addAction(open_world_action)
        
        save_action = QAction("Sauvegarder", self)
        save_action.triggered.connect(self.save_current_world)
        self.toolbar.addAction(save_action)
        
        self.toolbar.addSeparator()
        
        export_action = QAction("Exporter", self)
        export_action.triggered.connect(self.export_world)
        self.toolbar.addAction(export_action)
        
        import_action = QAction("Importer", self)
        import_action.triggered.connect(self.import_world)
        self.toolbar.addAction(import_action)
    
    def create_worlds_dock(self):
        """Crée le dock pour la liste des mondes"""
        
        self.worlds_dock = QDockWidget("Mondes disponibles", self)
        self.worlds_dock.setObjectName("worlds_dock")  
        self.worlds_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                         Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Widget pour le contenu du dock
        worlds_widget = QWidget()
        layout = QVBoxLayout(worlds_widget)
        
        # Liste des mondes
        self.worlds_tree = QTreeWidget()
        self.worlds_tree.setHeaderLabels(["Nom", "Auteur", "Complexité"])
        self.worlds_tree.itemDoubleClicked.connect(self.on_world_double_clicked)
        layout.addWidget(self.worlds_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        new_button = QPushButton("Nouveau")
        new_button.clicked.connect(self.show_world_generator_dialog)
        buttons_layout.addWidget(new_button)
        
        open_button = QPushButton("Ouvrir")
        open_button.clicked.connect(self.open_world)
        buttons_layout.addWidget(open_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_world)
        buttons_layout.addWidget(delete_button)
        
        layout.addLayout(buttons_layout)
        
        self.worlds_dock.setWidget(worlds_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.worlds_dock)
    
    def create_properties_dock(self):
        """Crée le dock pour les propriétés"""
        
        self.properties_dock = QDockWidget("Propriétés", self)
        self.properties_dock.setObjectName("properties_dock")  
        self.properties_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Widget pour le contenu du dock
        properties_widget = QWidget()
        layout = QVBoxLayout(properties_widget)
        
        # Formulaire pour les propriétés
        self.properties_form = QFormLayout()
        
        # Propriétés du monde
        self.world_properties_group = QGroupBox("Propriétés du monde")
        world_form = QFormLayout(self.world_properties_group)
        
        self.world_name_edit = QLineEdit()
        world_form.addRow("Nom:", self.world_name_edit)
        
        self.world_author_edit = QLineEdit()
        world_form.addRow("Auteur:", self.world_author_edit)
        
        self.world_complexity_spin = QSpinBox()
        self.world_complexity_spin.setMinimum(1)
        self.world_complexity_spin.setMaximum(5)
        world_form.addRow("Complexité:", self.world_complexity_spin)
        
        layout.addWidget(self.world_properties_group)
        
        # Bouton de sauvegarde
        save_button = QPushButton("Appliquer les modifications")
        save_button.clicked.connect(self.save_properties)
        layout.addWidget(save_button)
        
        # Espacement
        layout.addStretch()
        
        self.properties_dock.setWidget(properties_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
    
    def create_menus(self):
        """Crée les menus de l'application"""
        
        # Menu Fichier
        file_menu = self.menuBar().addMenu("&Fichier")
        
        new_action = QAction("&Nouveau monde", self)
        new_action.triggered.connect(self.show_world_generator_dialog)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Ouvrir monde", self)
        open_action.triggered.connect(self.open_world)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Sauvegarder", self)
        save_action.triggered.connect(self.save_current_world)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exporter monde", self)
        export_action.triggered.connect(self.export_world)
        file_menu.addAction(export_action)
        
        import_action = QAction("&Importer monde", self)
        import_action.triggered.connect(self.import_world)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Édition
        edit_menu = self.menuBar().addMenu("&Édition")
        
        add_location_action = QAction("Ajouter un &lieu", self)
        add_location_action.triggered.connect(self.add_location)
        edit_menu.addAction(add_location_action)
        
        add_character_action = QAction("Ajouter un &personnage", self)
        add_character_action.triggered.connect(self.add_character)
        edit_menu.addAction(add_character_action)
        
        add_device_action = QAction("Ajouter un &appareil", self)
        add_device_action.triggered.connect(self.add_device)
        edit_menu.addAction(add_device_action)
        
        # Menu Outils
        tools_menu = self.menuBar().addMenu("&Outils")
        
        generate_action = QAction("&Générer un monde", self)
        generate_action.triggered.connect(self.show_world_generator_dialog)
        tools_menu.addAction(generate_action)
        
        validate_action = QAction("&Valider le monde", self)
        validate_action.triggered.connect(self.validate_world)
        tools_menu.addAction(validate_action)
        
        # Menu Aide
        help_menu = self.menuBar().addMenu("&Aide")
        
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        help_action = QAction("&Aide", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def load_settings(self):
        """Charge les paramètres de l'application"""
        
        settings = QSettings()
        
        # Restaurer la géométrie de la fenêtre
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restaurer l'état des docks et barres d'outils
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def save_settings(self):
        """Sauvegarde les paramètres de l'application"""
        
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Sauvegarder le monde actuel si nécessaire
        if self.current_world_id:
            settings.setValue("last_world_id", self.current_world_id)
    
    def load_worlds_list(self):
        """Charge la liste des mondes disponibles"""
        
        self.worlds_tree.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, name, author, complexity FROM worlds ORDER BY name")
        
        worlds = cursor.fetchall()
        
        for world in worlds:
            item = QTreeWidgetItem([world["name"], world["author"], str(world["complexity"])])
            item.setData(0, Qt.ItemDataRole.UserRole, world["id"])
            self.worlds_tree.addTopLevelItem(item)
        
        self.worlds_tree.resizeColumnToContents(0)
        self.worlds_tree.resizeColumnToContents(1)
    
    def on_world_double_clicked(self, item, column):
        """Gère le double-clic sur un monde dans la liste"""
        
        world_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.open_world_by_id(world_id)
    
    def open_world(self):
        """Ouvre le monde sélectionné dans la liste"""
        
        selected_items = self.worlds_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun monde sélectionné", 
                               "Veuillez sélectionner un monde à ouvrir.")
            return
        
        world_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        self.open_world_by_id(world_id)
    
    def open_world_by_id(self, world_id):
        """Ouvre un monde par son ID"""
        
        # Fermer l'onglet actuel s'il existe
        if self.current_world_id:
            self.tab_widget.clear()
        
        # Charger les données du monde
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM worlds WHERE id = ?", (world_id,))
        world_data = cursor.fetchone()
        
        if not world_data:
            response = QMessageBox.question(
                self, 
                "Monde non trouvé", 
                f"Le monde avec l'ID {world_id} n'existe plus dans la base de données.\n\nSouhaitez-vous créer un nouveau monde ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self.show_world_generator_dialog()
            return
        
        # Mettre à jour l'ID du monde actuel
        self.current_world_id = world_id
        
        # Mettre à jour les propriétés
        self.world_name_edit.setText(world_data["name"])
        self.world_author_edit.setText(world_data["author"])
        self.world_complexity_spin.setValue(world_data["complexity"])
        
        # Créer un nouvel onglet pour le monde
        world_tab = WorldTab(self.db, world_id)
        self.tab_widget.addTab(world_tab, world_data["name"])
        
        # Mettre à jour la barre de statut
        self.statusBar.showMessage(f"Monde '{world_data['name']}' ouvert")
    
    def save_current_world(self):
        """Sauvegarde le monde actuel"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Sauvegarder les propriétés
        self.save_properties()
        
        # Sauvegarder les données de l'onglet actuel
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'save'):
            current_tab.save()
        
        self.statusBar.showMessage("Monde sauvegardé avec succès", 3000)
    
    def save_properties(self):
        """Sauvegarde les propriétés du monde actuel"""
        
        if not self.current_world_id:
            return
        
        name = self.world_name_edit.text()
        author = self.world_author_edit.text()
        complexity = self.world_complexity_spin.value()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        UPDATE worlds 
        SET name = ?, author = ?, complexity = ?
        WHERE id = ?
        """, (name, author, complexity, self.current_world_id))
        
        self.db.conn.commit()
        
        # Mettre à jour le titre de l'onglet
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), name)
        
        # Mettre à jour la liste des mondes
        self.load_worlds_list()
    
    def delete_world(self):
        """Supprime le monde sélectionné"""
        
        selected_items = self.worlds_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun monde sélectionné", 
                               "Veuillez sélectionner un monde à supprimer.")
            return
        
        world_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        world_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(self, "Confirmation de suppression", 
                                    f"Êtes-vous sûr de vouloir supprimer le monde '{world_name}' ?\n"
                                    "Cette action est irréversible.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Supprimer le monde
        try:
            # Utiliser la méthode delete_world de la classe Database
            # qui gère correctement la suppression des données liées
            success = self.db.delete_world(world_id)
            
            if not success:
                QMessageBox.warning(self, "Suppression impossible", 
                                   f"Le monde '{world_name}' n'a pas pu être supprimé.")
                return
            
            # Si c'était le monde actuel, fermer l'onglet
            if self.current_world_id == world_id:
                self.tab_widget.clear()
                self.current_world_id = None
            
            # Mettre à jour la liste des mondes
            self.load_worlds_list()
            
            self.statusBar.showMessage(f"Monde '{world_name}' supprimé", 3000)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la suppression du monde: {str(e)}")
            logger.error(f"Erreur lors de la suppression du monde: {str(e)}")
    
    def export_world(self):
        """Exporte le monde actuel vers un fichier JSON"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Demander le chemin du fichier
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter le monde", 
                                                 "", "Fichiers JSON (*.json)")
        
        if not file_path:
            return
        
        # Exporter le monde
        try:
            self.db.export_world(self.current_world_id, file_path)
            self.statusBar.showMessage(f"Monde exporté avec succès vers {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exportation", 
                                f"Une erreur est survenue lors de l'exportation du monde: {str(e)}")
    
    def import_world(self):
        """Importe un monde depuis un fichier JSON"""
        
        # Demander le chemin du fichier
        file_path, _ = QFileDialog.getOpenFileName(self, "Importer un monde", 
                                                 "", "Fichiers JSON (*.json)")
        
        if not file_path:
            return
        
        # Importer le monde
        try:
            world_id = self.db.import_world(file_path)
            self.load_worlds_list()
            self.open_world_by_id(world_id)
            self.statusBar.showMessage(f"Monde importé avec succès", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'importation", 
                                f"Une erreur est survenue lors de l'importation du monde: {str(e)}")
    
    def add_location(self):
        """Ajoute un nouveau lieu au monde actuel"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Ouvrir l'éditeur de lieu
        editor = LocationEditor(self.db, self.current_world_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour l'onglet actuel
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
    
    def add_character(self):
        """Ajoute un nouveau personnage au monde actuel"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Ouvrir l'éditeur de personnage
        editor = CharacterEditor(self.db, self.current_world_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour l'onglet actuel
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
    
    def add_device(self):
        """Ajoute un nouvel appareil au monde actuel"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Ouvrir l'éditeur d'appareil
        editor = DeviceEditor(self.db, self.current_world_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour l'onglet actuel
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
    
    def validate_world(self):
        """Valide le monde actuel"""
        
        if not self.current_world_id:
            QMessageBox.warning(self, "Aucun monde ouvert", 
                               "Aucun monde n'est actuellement ouvert.")
            return
        
        # Effectuer des vérifications sur le monde
        cursor = self.db.conn.cursor()
        
        # Vérifier qu'il y a au moins un lieu
        cursor.execute("SELECT COUNT(*) as count FROM locations WHERE world_id = ?", 
                      (self.current_world_id,))
        location_count = cursor.fetchone()["count"]
        
        if location_count == 0:
            QMessageBox.warning(self, "Validation échouée", 
                               "Le monde doit contenir au moins un lieu.")
            return
        
        # Vérifier qu'il y a au moins une connexion si plus d'un lieu
        if location_count > 1:
            cursor.execute("SELECT COUNT(*) as count FROM connections WHERE world_id = ?", 
                          (self.current_world_id,))
            connection_count = cursor.fetchone()["count"]
            
            if connection_count == 0:
                QMessageBox.warning(self, "Validation échouée", 
                                   "Le monde doit contenir au moins une connexion entre les lieux.")
                return
        
        # Autres vérifications possibles...
        
        # Si tout est valide
        QMessageBox.information(self, "Validation réussie", 
                               "Le monde est valide et prêt à être utilisé dans YakTaa.")
    
    def show_world_generator_dialog(self):
        """Affiche la boîte de dialogue de génération de monde"""
        
        dialog = WorldGeneratorDialog(self.world_generator)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Recharger la connexion à la base de données pour s'assurer que les changements sont visibles
            self.db.conn.commit()  # Commit any pending transactions
            
            # Mettre à jour la liste des mondes
            self.load_worlds_list()
            
            # Ouvrir le monde généré
            if dialog.generated_world_id:
                self.open_world_by_id(dialog.generated_world_id)
    
    def show_welcome_dialog(self):
        """Affiche la boîte de dialogue de bienvenue"""
        
        dialog = WelcomeDialog()
        dialog.exec()
    
    def show_about_dialog(self):
        """Affiche la boîte de dialogue À propos"""
        
        QMessageBox.about(self, "À propos de YakTaa World Editor",
                         "YakTaa World Editor\n"
                         "Version 1.0\n\n"
                         "Un éditeur de monde pour le jeu YakTaa.\n"
                         " 2023 YakTaa Team")
    
    def show_help(self):
        """Affiche l'aide"""
        
        QMessageBox.information(self, "Aide",
                               "Pour obtenir de l'aide sur l'utilisation de l'éditeur de monde, "
                               "consultez la documentation en ligne.")
    
    def closeEvent(self, event):
        """Gère l'événement de fermeture de la fenêtre"""
        
        # Sauvegarder les paramètres
        self.save_settings()
        
        # Sauvegarder le monde actuel si nécessaire
        if self.current_world_id:
            reply = QMessageBox.question(self, "Sauvegarder les modifications", 
                                        "Voulez-vous sauvegarder les modifications avant de quitter ?",
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No | 
                                        QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_current_world()
        
        # Fermer la base de données
        self.db.close()
        
        event.accept()
