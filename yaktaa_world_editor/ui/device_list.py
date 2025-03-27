#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la liste des appareils pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QBrush

from ui.device_editor import DeviceEditor
from ui.file_list import FileList

logger = logging.getLogger(__name__)

class DeviceList(QWidget):
    """Widget de liste des appareils pour l'éditeur de monde"""
    
    # Signaux
    device_selected = pyqtSignal(str)  # ID de l'appareil sélectionné
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_devices()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Liste des appareils
        self.device_tree = QTreeWidget()
        self.device_tree.setHeaderLabels(["Nom", "Type", "OS", "Sécurité", "Adresse IP"])
        self.device_tree.setAlternatingRowColors(True)
        self.device_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.device_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.device_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.device_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_device)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_device)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_device)
        buttons_layout.addWidget(delete_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_devices(self):
        """Charge la liste des appareils depuis la base de données"""
        
        self.device_tree.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name, device_type, os_type, security_level, ip_address, 
               location_id, owner_id
        FROM devices
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        devices = cursor.fetchall()
        
        # Créer les items de l'arbre
        for device in devices:
            item = QTreeWidgetItem([
                device["name"],
                device["device_type"],
                device["os_type"],
                str(device["security_level"]),
                device["ip_address"]
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, device["id"])
            
            # Colorer en fonction du niveau de sécurité
            security_level = device["security_level"]
            if security_level >= 4:
                item.setForeground(0, QBrush(QColor(255, 0, 0)))  # Rouge pour haute sécurité
            elif security_level >= 3:
                item.setForeground(0, QBrush(QColor(255, 128, 0)))  # Orange pour sécurité moyenne
            elif security_level <= 1:
                item.setForeground(0, QBrush(QColor(0, 180, 0)))    # Vert pour faible sécurité
            
            # Ajouter des informations sur le propriétaire
            if device["location_id"]:
                # Obtenir le nom du bâtiment
                cursor.execute("SELECT name FROM locations WHERE id = ?", (device["location_id"],))
                location = cursor.fetchone()
                if location:
                    item.setText(5, f"Location: {location['name']}")
            
            if device["owner_id"]:
                # Obtenir le nom du personnage
                cursor.execute("SELECT name FROM characters WHERE id = ?", (device["owner_id"],))
                character = cursor.fetchone()
                if character:
                    item.setText(5, f"Propriétaire: {character['name']}")
            
            self.device_tree.addTopLevelItem(item)
        
        # Ajuster les colonnes
        for i in range(5):
            self.device_tree.resizeColumnToContents(i)
    
    def refresh(self):
        """Rafraîchit la liste des appareils"""
        
        # Sauvegarder l'ID de l'appareil sélectionné
        selected_id = None
        selected_items = self.device_tree.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Recharger les appareils
        self.load_devices()
        
        # Restaurer la sélection
        if selected_id:
            self.select_device(selected_id)
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        
        selected_items = self.device_tree.selectedItems()
        if selected_items:
            device_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.device_selected.emit(device_id)
    
    def select_device(self, device_id):
        """Sélectionne un appareil dans la liste par son ID"""
        
        # Parcourir tous les items pour trouver celui avec l'ID correspondant
        for i in range(self.device_tree.topLevelItemCount()):
            item = self.device_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == device_id:
                self.device_tree.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        # Créer le menu
        menu = QMenu()
        
        add_action = QAction("Ajouter un appareil", self)
        add_action.triggered.connect(self.add_device)
        menu.addAction(add_action)
        
        # Actions supplémentaires si un item est sélectionné
        selected_items = self.device_tree.selectedItems()
        if selected_items:
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(self.edit_device)
            menu.addAction(edit_action)
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(self.delete_device)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            files_action = QAction("Gérer les fichiers", self)
            files_action.triggered.connect(self.manage_files)
            menu.addAction(files_action)
        
        # Afficher le menu
        menu.exec(self.device_tree.mapToGlobal(position))
    
    def add_device(self):
        """Ajoute un nouvel appareil"""
        
        # Récupérer l'ID du personnage sélectionné (si applicable)
        character_id = None
        if hasattr(self, 'character_id') and self.character_id:
            character_id = self.character_id
        
        # Ouvrir l'éditeur d'appareil
        editor = DeviceEditor(self.db, self.world_id, character_id=character_id)
        result = editor.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def edit_device(self):
        """Modifie l'appareil sélectionné"""
        
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun appareil sélectionné", 
                               "Veuillez sélectionner un appareil à modifier.")
            return
        
        device_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur d'appareil
        editor = DeviceEditor(self.db, self.world_id, device_id)
        result = editor.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_device(self):
        """Supprime l'appareil sélectionné"""
        
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun appareil sélectionné", 
                               "Veuillez sélectionner un appareil à supprimer.")
            return
        
        device_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        device_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer l'appareil '{device_name}' ?\n\n"
            "Cette action est irréversible et supprimera également tous les fichiers associés.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            
            # Supprimer les fichiers associés
            cursor.execute("""
            DELETE FROM files
            WHERE device_id = ? AND world_id = ?
            """, (device_id, self.world_id))
            
            # Supprimer l'appareil
            cursor.execute("""
            DELETE FROM devices
            WHERE id = ? AND world_id = ?
            """, (device_id, self.world_id))
            
            self.db.conn.commit()
            
            self.refresh()
    
    def manage_files(self):
        """Ouvre la liste des fichiers pour l'appareil sélectionné"""
        
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun appareil sélectionné", 
                               "Veuillez sélectionner un appareil pour gérer ses fichiers.")
            return
        
        device_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        device_name = selected_items[0].text(0)
        
        # Ouvrir la liste des fichiers
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Fichiers de l'appareil: {device_name}")
        dialog.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        file_list = FileList(self.db, self.world_id, device_id)
        layout.addWidget(file_list)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
