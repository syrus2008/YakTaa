#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des armes dans l'u00e9diteur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.weapon_editor import WeaponEditor

logger = logging.getLogger(__name__)

class WeaponList(QWidget):
    """Widget de liste et gestion des armes"""
    
    weapon_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_weapons()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Armes")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Liste des armes
        self.weapon_list = QListWidget()
        self.weapon_list.itemClicked.connect(self.on_weapon_selected)
        main_layout.addWidget(self.weapon_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_weapon)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("u00c9diter")
        self.edit_button.clicked.connect(self.edit_weapon)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_weapon)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_weapons(self):
        """Charge la liste des armes"""
        try:
            self.weapon_list.clear()
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name, damage, damage_type, rarity FROM weapons WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            weapons = cursor.fetchall()
            
            for weapon in weapons:
                item = QListWidgetItem(f"{weapon['name']} ({weapon['damage']} du00e9gu00e2ts {weapon['damage_type']})")
                item.setData(Qt.ItemDataRole.UserRole, weapon['id'])
                # Ajouter une couleur selon la raretu00e9
                rarity = weapon.get('rarity', 'commun')
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
                
                self.weapon_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des armes: {str(e)}")
    
    def on_weapon_selected(self, item):
        """Gu00e8re la su00e9lection d'une arme"""
        weapon_id = item.data(Qt.ItemDataRole.UserRole)
        self.weapon_selected.emit(weapon_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_weapon(self):
        """Ajoute une nouvelle arme"""
        dialog = WeaponEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                weapon_data = dialog.get_weapon_data()
                weapon_id = f"weapon_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO weapons 
                       (id, world_id, name, description, damage, damage_type, weapon_range, 
                        accuracy, rate_of_fire, ammo_type, ammo_capacity, mod_slots, 
                        rarity, value, location_type, location_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (weapon_id, self.world_id, weapon_data["name"], weapon_data["description"],
                     weapon_data["damage"], weapon_data["damage_type"], weapon_data["weapon_range"],
                     weapon_data["accuracy"], weapon_data["rate_of_fire"], weapon_data["ammo_type"],
                     weapon_data["ammo_capacity"], weapon_data["mod_slots"], weapon_data["rarity"],
                     weapon_data["value"], weapon_data["location_type"], weapon_data["location_id"])
                )
                
                self.db.conn.commit()
                self.load_weapons()
                
                logger.info(f"Arme ajoutu00e9e: {weapon_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout de l'arme: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'arme: {str(e)}")
    
    def edit_weapon(self):
        """Modifie une arme existante"""
        selected_items = self.weapon_list.selectedItems()
        if not selected_items:
            return
            
        weapon_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = WeaponEditor(self.db, self.world_id, weapon_id, parent=self)
        if dialog.exec():
            try:
                weapon_data = dialog.get_weapon_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE weapons 
                       SET name = ?, description = ?, damage = ?, damage_type = ?, 
                           weapon_range = ?, accuracy = ?, rate_of_fire = ?, ammo_type = ?, 
                           ammo_capacity = ?, mod_slots = ?, rarity = ?, value = ?, 
                           location_type = ?, location_id = ?
                       WHERE id = ? AND world_id = ?""",
                    (weapon_data["name"], weapon_data["description"],
                     weapon_data["damage"], weapon_data["damage_type"],
                     weapon_data["weapon_range"], weapon_data["accuracy"],
                     weapon_data["rate_of_fire"], weapon_data["ammo_type"],
                     weapon_data["ammo_capacity"], weapon_data["mod_slots"],
                     weapon_data["rarity"], weapon_data["value"],
                     weapon_data["location_type"], weapon_data["location_id"],
                     weapon_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_weapons()
                
                logger.info(f"Arme modifiu00e9e: {weapon_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification de l'arme: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'arme: {str(e)}")
    
    def delete_weapon(self):
        """Supprime une arme"""
        selected_items = self.weapon_list.selectedItems()
        if not selected_items:
            return
            
        weapon_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        weapon_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer l'arme '{weapon_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM weapons WHERE id = ? AND world_id = ?",
                    (weapon_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_weapons()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Arme supprimu00e9e: {weapon_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de l'arme: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'arme: {str(e)}")
