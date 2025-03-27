#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des factions dans l'u00e9diteur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.faction_editor import FactionEditor

logger = logging.getLogger(__name__)

class FactionList(QWidget):
    """Widget de liste et gestion des factions"""
    
    faction_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_factions()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Factions")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Liste des factions
        self.faction_list = QListWidget()
        self.faction_list.itemClicked.connect(self.on_faction_selected)
        main_layout.addWidget(self.faction_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_faction)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("u00c9diter")
        self.edit_button.clicked.connect(self.edit_faction)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_faction)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_factions(self):
        """Charge la liste des factions"""
        try:
            self.faction_list.clear()
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name, power_level FROM factions WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            factions = cursor.fetchall()
            
            for faction in factions:
                item = QListWidgetItem(f"{faction['name']} (Puissance: {faction['power_level']})")
                item.setData(Qt.ItemDataRole.UserRole, faction['id'])
                self.faction_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des factions: {str(e)}")
    
    def on_faction_selected(self, item):
        """Gu00e8re la su00e9lection d'une faction"""
        faction_id = item.data(Qt.ItemDataRole.UserRole)
        self.faction_selected.emit(faction_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_faction(self):
        """Ajoute une nouvelle faction"""
        dialog = FactionEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                faction_data = dialog.get_faction_data()
                faction_id = f"faction_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO factions 
                       (id, world_id, name, description, ideology, power_level, territory, notable_members, icon)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (faction_id, self.world_id, faction_data["name"], faction_data["description"],
                     faction_data["ideology"], faction_data["power_level"], faction_data["territory"],
                     faction_data["notable_members"], faction_data["icon"])
                )
                
                self.db.conn.commit()
                self.load_factions()
                
                logger.info(f"Faction ajoutu00e9e: {faction_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout de la faction: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la faction: {str(e)}")
    
    def edit_faction(self):
        """Modifie une faction existante"""
        selected_items = self.faction_list.selectedItems()
        if not selected_items:
            return
            
        faction_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = FactionEditor(self.db, self.world_id, faction_id, parent=self)
        if dialog.exec():
            try:
                faction_data = dialog.get_faction_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE factions 
                       SET name = ?, description = ?, ideology = ?, power_level = ?, 
                           territory = ?, notable_members = ?, icon = ?
                       WHERE id = ? AND world_id = ?""",
                    (faction_data["name"], faction_data["description"],
                     faction_data["ideology"], faction_data["power_level"],
                     faction_data["territory"], faction_data["notable_members"],
                     faction_data["icon"], faction_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_factions()
                
                logger.info(f"Faction modifiu00e9e: {faction_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification de la faction: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier la faction: {str(e)}")
    
    def delete_faction(self):
        """Supprime une faction"""
        selected_items = self.faction_list.selectedItems()
        if not selected_items:
            return
            
        faction_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        faction_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer la faction '{faction_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM factions WHERE id = ? AND world_id = ?",
                    (faction_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_factions()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Faction supprimu00e9e: {faction_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de la faction: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer la faction: {str(e)}")
