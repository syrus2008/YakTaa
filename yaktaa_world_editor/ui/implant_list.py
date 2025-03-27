#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des implants dans l'u00e9diteur de monde YakTaa
"""

import logging
import uuid
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.implant_editor import ImplantEditor

logger = logging.getLogger(__name__)

class ImplantList(QWidget):
    """Widget de liste et gestion des implants cyberu00e9tiques"""
    
    implant_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_implants()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Implants Cyberu00e9tiques")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Liste des implants
        self.implant_list = QListWidget()
        self.implant_list.itemClicked.connect(self.on_implant_selected)
        main_layout.addWidget(self.implant_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_implant)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("u00c9diter")
        self.edit_button.clicked.connect(self.edit_implant)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_implant)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_implants(self):
        """Charge la liste des implants"""
        try:
            self.implant_list.clear()
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name, implant_type, body_location, rarity, legality, manufacturer FROM implants WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            implants = cursor.fetchall()
            
            for implant in implants:
                # Formatage du texte selon les caractéristiques
                manufacturer_text = f" [{implant['manufacturer']}]" if 'manufacturer' in implant and implant['manufacturer'] else ""
                display_text = f"{implant['name']} ({implant['implant_type']}/{implant['body_location']}){manufacturer_text}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, implant['id'])
                
                # Ajouter une couleur selon la raretu00e9
                rarity = implant['rarity'] if 'rarity' in implant else 'commun'
                if rarity == 'commun':
                    item.setForeground(Qt.GlobalColor.white)
                elif rarity == 'peu commun':
                    item.setForeground(Qt.GlobalColor.green)
                elif rarity == 'rare':
                    item.setForeground(Qt.GlobalColor.blue)
                elif rarity == 'u00e9pique':
                    item.setForeground(Qt.GlobalColor.magenta)
                elif rarity == 'lu00e9gendaire' or rarity == 'unique':
                    item.setForeground(Qt.GlobalColor.yellow)
                
                # Couleur de fond selon la légalité
                legality = implant['legality'] if 'legality' in implant else 'légal'
                if legality == 'illu00e9gal':
                    item.setBackground(Qt.GlobalColor.darkRed)
                elif legality == 'militaire':
                    item.setBackground(Qt.GlobalColor.darkBlue)
                elif legality == 'expu00e9rimental':
                    item.setBackground(Qt.GlobalColor.darkMagenta)
                
                self.implant_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des implants: {str(e)}")
    
    def on_implant_selected(self, item):
        """Gu00e8re la su00e9lection d'un implant"""
        implant_id = item.data(Qt.ItemDataRole.UserRole)
        self.implant_selected.emit(implant_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_implant(self):
        """Ajoute un nouvel implant"""
        dialog = ImplantEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                implant_data = dialog.get_implant_data()
                implant_id = f"implant_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO implants 
                       (id, world_id, name, description, implant_type, 
                        body_location, surgery_difficulty, side_effects, 
                        compatibility, bonus, rarity, value, legality,
                        manufacturer, location_type, location_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (implant_id, self.world_id, implant_data["name"], implant_data["description"],
                     implant_data["implant_type"], implant_data["body_location"],
                     implant_data["surgery_difficulty"], implant_data["side_effects"],
                     implant_data["compatibility"], implant_data["bonus"],
                     implant_data["rarity"], implant_data["value"],
                     implant_data["legality"], implant_data["manufacturer"],
                     implant_data["location_type"], implant_data["location_id"])
                )
                
                self.db.conn.commit()
                self.load_implants()
                
                logger.info(f"Implant ajoutu00e9: {implant_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout de l'implant: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'implant: {str(e)}")
    
    def edit_implant(self):
        """Modifie un implant existant"""
        selected_items = self.implant_list.selectedItems()
        if not selected_items:
            return
            
        implant_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = ImplantEditor(self.db, self.world_id, implant_id, parent=self)
        if dialog.exec():
            try:
                implant_data = dialog.get_implant_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE implants 
                       SET name = ?, description = ?, implant_type = ?, 
                           body_location = ?, surgery_difficulty = ?, 
                           side_effects = ?, compatibility = ?, 
                           bonus = ?, rarity = ?, value = ?, 
                           legality = ?, manufacturer = ?,
                           location_type = ?, location_id = ?
                       WHERE id = ? AND world_id = ?""",
                    (implant_data["name"], implant_data["description"],
                     implant_data["implant_type"], implant_data["body_location"],
                     implant_data["surgery_difficulty"], implant_data["side_effects"],
                     implant_data["compatibility"], implant_data["bonus"],
                     implant_data["rarity"], implant_data["value"],
                     implant_data["legality"], implant_data["manufacturer"],
                     implant_data["location_type"], implant_data["location_id"],
                     implant_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_implants()
                
                logger.info(f"Implant modifiu00e9: {implant_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification de l'implant: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'implant: {str(e)}")
    
    def delete_implant(self):
        """Supprime un implant"""
        selected_items = self.implant_list.selectedItems()
        if not selected_items:
            return
            
        implant_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        implant_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer l'implant '{implant_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM implants WHERE id = ? AND world_id = ?",
                    (implant_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_implants()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Implant supprimu00e9: {implant_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de l'implant: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'implant: {str(e)}")
