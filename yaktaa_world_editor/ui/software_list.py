#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des logiciels dans l'éditeur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.software_editor import SoftwareEditor

logger = logging.getLogger(__name__)

class SoftwareList(QWidget):
    """Widget de liste et gestion des logiciels"""
    
    software_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_software()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Logiciels")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Liste des logiciels
        self.software_list = QListWidget()
        self.software_list.itemClicked.connect(self.on_software_selected)
        main_layout.addWidget(self.software_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_software)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_software)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_software)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_software(self):
        """Charge la liste des logiciels"""
        try:
            self.software_list.clear()
            
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name, software_type, version, rarity FROM software WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            softwares = cursor.fetchall()
            
            for software in softwares:
                item = QListWidgetItem(f"{software['name']} v{software['version']} ({software['software_type']})")
                item.setData(Qt.ItemDataRole.UserRole, software['id'])
                # Ajouter une couleur selon la rareté
                rarity = software['rarity'] if 'rarity' in software.keys() else 'commun'
                if rarity == 'commun':
                    item.setForeground(Qt.GlobalColor.white)
                elif rarity == 'peu commun':
                    item.setForeground(Qt.GlobalColor.green)
                elif rarity == 'rare':
                    item.setForeground(Qt.GlobalColor.blue)
                elif rarity == 'épique':
                    item.setForeground(Qt.GlobalColor.magenta)
                elif rarity == 'légendaire' or rarity == 'unique':
                    item.setForeground(Qt.GlobalColor.yellow)
                
                # Icone selon le type
                software_type = software['software_type'] if 'software_type' in software.keys() else 'utilitaire'
                if software_type == 'virus' or software_type == 'ransomware' or software_type == 'trojan':
                    # Rouge pour les malwares
                    item.setBackground(Qt.GlobalColor.darkRed)
                elif software_type == 'cracker' or software_type == 'exploit':
                    # Violet pour les outils de hacking
                    item.setBackground(Qt.GlobalColor.darkMagenta)
                elif software_type == 'antivirus' or software_type == 'firewall' or software_type == 'vpn':
                    # Vert pour les outils de protection
                    item.setBackground(Qt.GlobalColor.darkGreen)
                
                self.software_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des logiciels: {str(e)}")
    
    def on_software_selected(self, item):
        """Gère la sélection d'un logiciel"""
        software_id = item.data(Qt.ItemDataRole.UserRole)
        self.software_selected.emit(software_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_software(self):
        """Ajoute un nouveau logiciel"""
        dialog = SoftwareEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                software_data = dialog.get_software_data()
                software_id = f"software_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO software 
                       (id, world_id, name, description, software_type, 
                        version, license_type, system_requirements, capabilities, 
                        rarity, value, location_type, location_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (software_id, self.world_id, software_data["name"], software_data["description"],
                     software_data["software_type"], software_data["version"],
                     software_data["license_type"], software_data["system_requirements"],
                     software_data["capabilities"], software_data["rarity"],
                     software_data["value"], software_data["location_type"],
                     software_data["location_id"])
                )
                
                self.db.conn.commit()
                self.load_software()
                
                logger.info(f"Logiciel ajouté: {software_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout du logiciel: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter le logiciel: {str(e)}")
    
    def edit_software(self):
        """Modifie un logiciel existant"""
        selected_items = self.software_list.selectedItems()
        if not selected_items:
            return
            
        software_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = SoftwareEditor(self.db, self.world_id, software_id, parent=self)
        if dialog.exec():
            try:
                software_data = dialog.get_software_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE software 
                       SET name = ?, description = ?, software_type = ?, 
                           version = ?, license_type = ?, system_requirements = ?, 
                           capabilities = ?, rarity = ?, value = ?, 
                           location_type = ?, location_id = ?
                       WHERE id = ? AND world_id = ?""",
                    (software_data["name"], software_data["description"],
                     software_data["software_type"], software_data["version"],
                     software_data["license_type"], software_data["system_requirements"],
                     software_data["capabilities"], software_data["rarity"],
                     software_data["value"], software_data["location_type"],
                     software_data["location_id"], software_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_software()
                
                logger.info(f"Logiciel modifié: {software_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification du logiciel: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier le logiciel: {str(e)}")
    
    def delete_software(self):
        """Supprime un logiciel"""
        selected_items = self.software_list.selectedItems()
        if not selected_items:
            return
            
        software_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        software_name = selected_items[0].text().split(' v')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer le logiciel '{software_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM software WHERE id = ? AND world_id = ?",
                    (software_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_software()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Logiciel supprimé: {software_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression du logiciel: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le logiciel: {str(e)}")
