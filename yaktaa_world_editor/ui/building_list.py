#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la liste des bâtiments pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QBrush

from ui.building_editor import BuildingEditor

logger = logging.getLogger(__name__)

class BuildingList(QWidget):
    """Widget de liste des bâtiments pour l'éditeur de monde"""
    
    # Signaux
    building_selected = pyqtSignal(str)  # ID du bâtiment sélectionné
    
    def __init__(self, db, world_id, location_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.location_id = location_id  # Optionnel, pour filtrer par lieu
        
        self.init_ui()
        self.load_buildings()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Liste des bâtiments
        self.building_tree = QTreeWidget()
        self.building_tree.setHeaderLabels(["Nom", "Type", "Sécurité", "Étages", "Lieu"])
        self.building_tree.setAlternatingRowColors(True)
        self.building_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.building_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.building_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.building_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_building)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_building)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_building)
        buttons_layout.addWidget(delete_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_buildings(self):
        """Charge la liste des bâtiments depuis la base de données"""
        
        self.building_tree.clear()
        
        cursor = self.db.conn.cursor()
        
        # Requête SQL de base
        query = """
        SELECT b.id, b.name, b.building_type, b.security_level, b.floors, 
               l.name as location_name, b.location_id
        FROM buildings b
        LEFT JOIN locations l ON b.location_id = l.id
        WHERE b.world_id = ?
        """
        
        params = [self.world_id]
        
        # Ajouter un filtre par lieu si nécessaire
        if self.location_id:
            query += " AND b.location_id = ?"
            params.append(self.location_id)
        
        query += " ORDER BY b.name"
        
        cursor.execute(query, params)
        
        buildings = cursor.fetchall()
        
        # Créer les items de l'arbre
        for building in buildings:
            item = QTreeWidgetItem([
                building["name"],
                building["building_type"],
                str(building["security_level"]),
                str(building["floors"]),
                building["location_name"] or "N/A"
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, building["id"])
            item.setData(4, Qt.ItemDataRole.UserRole, building["location_id"])
            
            # Colorer en fonction du type de bâtiment
            if building["building_type"] == "residential":
                item.setForeground(0, QBrush(QColor(0, 128, 255)))  # Bleu pour résidentiel
            elif building["building_type"] == "commercial":
                item.setForeground(0, QBrush(QColor(0, 200, 0)))    # Vert pour commercial
            elif building["building_type"] == "government":
                item.setForeground(0, QBrush(QColor(128, 0, 128)))  # Violet pour gouvernement
            elif building["building_type"] == "corporate":
                item.setForeground(0, QBrush(QColor(200, 0, 0)))    # Rouge pour corporatif
            
            self.building_tree.addTopLevelItem(item)
        
        # Ajuster les colonnes
        for i in range(5):
            self.building_tree.resizeColumnToContents(i)
    
    def refresh(self):
        """Rafraîchit la liste des bâtiments"""
        
        # Sauvegarder l'ID du bâtiment sélectionné
        selected_id = None
        selected_items = self.building_tree.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Recharger les bâtiments
        self.load_buildings()
        
        # Restaurer la sélection
        if selected_id:
            self.select_building(selected_id)
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        
        selected_items = self.building_tree.selectedItems()
        if selected_items:
            building_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.building_selected.emit(building_id)
    
    def select_building(self, building_id):
        """Sélectionne un bâtiment dans la liste par son ID"""
        
        # Parcourir tous les items pour trouver celui avec l'ID correspondant
        for i in range(self.building_tree.topLevelItemCount()):
            item = self.building_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == building_id:
                self.building_tree.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        # Créer le menu
        menu = QMenu()
        
        add_action = QAction("Ajouter un bâtiment", self)
        add_action.triggered.connect(self.add_building)
        menu.addAction(add_action)
        
        # Actions supplémentaires si un item est sélectionné
        selected_items = self.building_tree.selectedItems()
        if selected_items:
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(self.edit_building)
            menu.addAction(edit_action)
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(self.delete_building)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            add_device_action = QAction("Ajouter un appareil", self)
            add_device_action.triggered.connect(self.add_device)
            menu.addAction(add_device_action)
        
        # Afficher le menu
        menu.exec(self.building_tree.mapToGlobal(position))
    
    def add_building(self):
        """Ajoute un nouveau bâtiment"""
        
        editor = BuildingEditor(self.db, self.world_id, location_id=self.location_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def edit_building(self):
        """Modifie le bâtiment sélectionné"""
        
        selected_items = self.building_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun bâtiment sélectionné", 
                               "Veuillez sélectionner un bâtiment à modifier.")
            return
        
        building_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        editor = BuildingEditor(self.db, self.world_id, building_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def delete_building(self):
        """Supprime le bâtiment sélectionné"""
        
        selected_items = self.building_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun bâtiment sélectionné", 
                               "Veuillez sélectionner un bâtiment à supprimer.")
            return
        
        building_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        building_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer le bâtiment '{building_name}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            
            # Supprimer les appareils associés
            cursor.execute("""
            DELETE FROM devices
            WHERE building_id = ? AND world_id = ?
            """, (building_id, self.world_id))
            
            # Supprimer le bâtiment
            cursor.execute("""
            DELETE FROM buildings
            WHERE id = ? AND world_id = ?
            """, (building_id, self.world_id))
            
            self.db.conn.commit()
            
            self.refresh()
    
    def add_device(self):
        """Ajoute un appareil au bâtiment sélectionné"""
        
        selected_items = self.building_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun bâtiment sélectionné", 
                               "Veuillez sélectionner un bâtiment pour ajouter un appareil.")
            return
        
        building_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur d'appareil avec le bâtiment pré-sélectionné
        from ui.device_editor import DeviceEditor
        editor = DeviceEditor(self.db, self.world_id, building_id=building_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            # Informer l'utilisateur que l'appareil a été ajouté
            QMessageBox.information(self, "Appareil ajouté", 
                                  "L'appareil a été ajouté avec succès au bâtiment sélectionné.")
