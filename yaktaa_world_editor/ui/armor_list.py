#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des armures dans l'u00e9diteur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.armor_editor import ArmorEditor

logger = logging.getLogger(__name__)

class ArmorList(QWidget):
    """Widget de liste et gestion des armures"""
    
    armor_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_armors()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Armures")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Liste des armures
        self.armor_list = QListWidget()
        self.armor_list.itemClicked.connect(self.on_armor_selected)
        main_layout.addWidget(self.armor_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_armor)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("u00c9diter")
        self.edit_button.clicked.connect(self.edit_armor)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_armor)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_armors(self):
        """Charge la liste des armures"""
        try:
            self.armor_list.clear()
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name, defense, defense_type, rarity FROM armors WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            armors = cursor.fetchall()
            
            for armor in armors:
                item = QListWidgetItem(f"{armor['name']} ({armor['defense']} du00e9fense {armor['defense_type']})")
                item.setData(Qt.ItemDataRole.UserRole, armor['id'])
                # Ajouter une couleur selon la raretu00e9
                rarity = armor.get('rarity', 'commun')
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
                
                self.armor_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des armures: {str(e)}")
    
    def on_armor_selected(self, item):
        """Gu00e8re la su00e9lection d'une armure"""
        armor_id = item.data(Qt.ItemDataRole.UserRole)
        self.armor_selected.emit(armor_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_armor(self):
        """Ajoute une nouvelle armure"""
        dialog = ArmorEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                armor_data = dialog.get_armor_data()
                armor_id = f"armor_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO armors 
                       (id, world_id, name, description, defense, defense_type, 
                        slots, weight, durability, mod_slots, rarity, value, 
                        location_type, location_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (armor_id, self.world_id, armor_data["name"], armor_data["description"],
                     armor_data["defense"], armor_data["defense_type"], armor_data["slots"],
                     armor_data["weight"], armor_data["durability"], armor_data["mod_slots"],
                     armor_data["rarity"], armor_data["value"], armor_data["location_type"],
                     armor_data["location_id"])
                )
                
                self.db.conn.commit()
                self.load_armors()
                
                logger.info(f"Armure ajoutu00e9e: {armor_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout de l'armure: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'armure: {str(e)}")
    
    def edit_armor(self):
        """Modifie une armure existante"""
        selected_items = self.armor_list.selectedItems()
        if not selected_items:
            return
            
        armor_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = ArmorEditor(self.db, self.world_id, armor_id, parent=self)
        if dialog.exec():
            try:
                armor_data = dialog.get_armor_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE armors 
                       SET name = ?, description = ?, defense = ?, defense_type = ?, 
                           slots = ?, weight = ?, durability = ?, mod_slots = ?, 
                           rarity = ?, value = ?, location_type = ?, location_id = ?
                       WHERE id = ? AND world_id = ?""",
                    (armor_data["name"], armor_data["description"],
                     armor_data["defense"], armor_data["defense_type"],
                     armor_data["slots"], armor_data["weight"], 
                     armor_data["durability"], armor_data["mod_slots"],
                     armor_data["rarity"], armor_data["value"],
                     armor_data["location_type"], armor_data["location_id"],
                     armor_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_armors()
                
                logger.info(f"Armure modifiu00e9e: {armor_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification de l'armure: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'armure: {str(e)}")
    
    def delete_armor(self):
        """Supprime une armure"""
        selected_items = self.armor_list.selectedItems()
        if not selected_items:
            return
            
        armor_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        armor_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer l'armure '{armor_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM armors WHERE id = ? AND world_id = ?",
                    (armor_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_armors()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Armure supprimu00e9e: {armor_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de l'armure: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'armure: {str(e)}")
