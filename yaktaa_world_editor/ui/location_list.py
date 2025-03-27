#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la liste des lieux pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QBrush

from ui.location_editor import LocationEditor
from ui.character_editor import CharacterEditor
from ui.building_editor import BuildingEditor

logger = logging.getLogger(__name__)

class LocationList(QWidget):
    """Widget de liste des lieux pour l'éditeur de monde"""
    
    # Signaux
    location_selected = pyqtSignal(str)  # ID du lieu sélectionné
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_locations()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Liste des lieux
        self.location_tree = QTreeWidget()
        self.location_tree.setHeaderLabels(["Nom", "Type", "Sécurité", "Population"])
        self.location_tree.setAlternatingRowColors(True)
        self.location_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.location_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.location_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.location_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_location)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_location)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_location)
        buttons_layout.addWidget(delete_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_locations(self):
        """Charge la liste des lieux depuis la base de données"""
        
        self.location_tree.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name, location_type, security_level, population, is_special
        FROM locations
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        locations = cursor.fetchall()
        
        # Créer les items de l'arbre
        for location in locations:
            item = QTreeWidgetItem([
                location["name"],
                location["location_type"],
                str(location["security_level"]),
                str(location["population"])
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, location["id"])
            
            # Colorer en fonction du type de lieu
            if location["is_special"]:
                item.setForeground(0, QBrush(QColor(255, 128, 0)))  # Orange pour les lieux spéciaux
            elif location["location_type"] == "city":
                item.setForeground(0, QBrush(QColor(0, 128, 255)))  # Bleu pour les villes
            elif location["location_type"] == "district":
                item.setForeground(0, QBrush(QColor(0, 200, 255)))  # Bleu clair pour les quartiers
            elif location["location_type"] == "rural":
                item.setForeground(0, QBrush(QColor(0, 180, 0)))    # Vert pour les zones rurales
            
            self.location_tree.addTopLevelItem(item)
        
        # Ajuster les colonnes
        for i in range(4):
            self.location_tree.resizeColumnToContents(i)
    
    def refresh(self):
        """Rafraîchit la liste des lieux"""
        
        # Sauvegarder l'ID du lieu sélectionné
        selected_id = None
        selected_items = self.location_tree.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Recharger les lieux
        self.load_locations()
        
        # Restaurer la sélection
        if selected_id:
            self.select_location(selected_id)
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        
        selected_items = self.location_tree.selectedItems()
        if selected_items:
            location_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.location_selected.emit(location_id)
    
    def select_location(self, location_id):
        """Sélectionne un lieu dans la liste par son ID"""
        
        # Parcourir tous les items pour trouver celui avec l'ID correspondant
        for i in range(self.location_tree.topLevelItemCount()):
            item = self.location_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == location_id:
                self.location_tree.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        # Créer le menu
        menu = QMenu()
        
        add_action = QAction("Ajouter un lieu", self)
        add_action.triggered.connect(self.add_location)
        menu.addAction(add_action)
        
        # Actions supplémentaires si un item est sélectionné
        selected_items = self.location_tree.selectedItems()
        if selected_items:
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(self.edit_location)
            menu.addAction(edit_action)
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(self.delete_location)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            add_building_action = QAction("Ajouter un bâtiment", self)
            add_building_action.triggered.connect(self.add_building)
            menu.addAction(add_building_action)
            
            add_character_action = QAction("Ajouter un personnage", self)
            add_character_action.triggered.connect(self.add_character)
            menu.addAction(add_character_action)
        
        # Afficher le menu
        menu.exec(self.location_tree.mapToGlobal(position))
    
    def add_location(self):
        """Ajoute un nouveau lieu"""
        
        editor = LocationEditor(self.db, self.world_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def edit_location(self):
        """Modifie le lieu sélectionné"""
        
        selected_items = self.location_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun lieu sélectionné", 
                               "Veuillez sélectionner un lieu à modifier.")
            return
        
        location_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        editor = LocationEditor(self.db, self.world_id, location_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def delete_location(self):
        """Supprime le lieu sélectionné"""
        
        selected_items = self.location_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun lieu sélectionné", 
                               "Veuillez sélectionner un lieu à supprimer.")
            return
        
        location_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        location_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(self, "Confirmation de suppression", 
                                    f"Êtes-vous sûr de vouloir supprimer le lieu '{location_name}' ?\n"
                                    "Cette action supprimera également tous les bâtiments, personnages et appareils associés.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Supprimer le lieu et ses dépendances
        cursor = self.db.conn.cursor()
        
        # Supprimer les connexions
        cursor.execute("""
        DELETE FROM connections 
        WHERE (source_id = ? OR destination_id = ?) AND world_id = ?
        """, (location_id, location_id, self.world_id))
        
        # Supprimer les bâtiments et leurs dépendances
        cursor.execute("SELECT id FROM buildings WHERE location_id = ? AND world_id = ?", 
                      (location_id, self.world_id))
        buildings = cursor.fetchall()
        
        for building in buildings:
            building_id = building["id"]
            
            # Supprimer les pièces
            cursor.execute("DELETE FROM rooms WHERE building_id = ? AND world_id = ?", 
                          (building_id, self.world_id))
            
            # Supprimer les appareils
            cursor.execute("DELETE FROM devices WHERE building_id = ? AND world_id = ?", 
                          (building_id, self.world_id))
        
        # Supprimer les bâtiments
        cursor.execute("DELETE FROM buildings WHERE location_id = ? AND world_id = ?", 
                      (location_id, self.world_id))
        
        # Supprimer les personnages
        cursor.execute("DELETE FROM characters WHERE location_id = ? AND world_id = ?", 
                      (location_id, self.world_id))
        
        # Supprimer le lieu lui-même
        cursor.execute("DELETE FROM locations WHERE id = ? AND world_id = ?", 
                      (location_id, self.world_id))
        
        self.db.conn.commit()
        
        # Rafraîchir la liste
        self.refresh()
    
    def add_building(self):
        """Ajoute un bâtiment au lieu sélectionné"""
        
        selected_items = self.location_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun lieu sélectionné", 
                               "Veuillez sélectionner un lieu pour ajouter un bâtiment.")
            return
        
        location_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur de bâtiment avec le lieu pré-sélectionné
        editor = BuildingEditor(self.db, self.world_id, location_id=location_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Informer l'utilisateur que le bâtiment a été ajouté
            QMessageBox.information(self, "Bâtiment ajouté", 
                                  "Le bâtiment a été ajouté avec succès au lieu sélectionné.")

    def add_character(self):
        """Ajoute un personnage au lieu sélectionné"""
        
        selected_items = self.location_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun lieu sélectionné", 
                               "Veuillez sélectionner un lieu pour ajouter un personnage.")
            return
        
        location_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur de personnage avec le lieu pré-sélectionné
        editor = CharacterEditor(self.db, self.world_id, location_id=location_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Informer l'utilisateur que le personnage a été ajouté
            QMessageBox.information(self, "Personnage ajouté", 
                                  "Le personnage a été ajouté avec succès au lieu sélectionné.")
