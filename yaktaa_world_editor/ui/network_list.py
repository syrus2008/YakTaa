#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste et gestion des réseaux informatiques dans l'éditeur de monde YakTaa
"""

import logging
import uuid
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QMessageBox, QListWidgetItem,
    QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ui.network_editor import NetworkEditor

logger = logging.getLogger(__name__)

class NetworkList(QWidget):
    """Widget de liste et gestion des réseaux informatiques"""
    
    network_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_networks()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Réseaux informatiques")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Filtres
        filter_layout = QHBoxLayout()
        
        # Filtre par bâtiment
        self.building_filter_label = QLabel("Bâtiment:")
        filter_layout.addWidget(self.building_filter_label)
        
        self.building_filter_combo = QComboBox()
        self.building_filter_combo.addItem("Tous", "")
        self.load_buildings()
        self.building_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.building_filter_combo, 1)
        
        # Filtre par type de réseau
        self.type_filter_label = QLabel("Type:")
        filter_layout.addWidget(self.type_filter_label)
        
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItem("Tous", "")
        self.type_filter_combo.addItems(["WiFi", "LAN", "WAN", "VPN", "IoT"])
        self.type_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter_combo, 1)
        
        # Recherche
        self.search_filter_label = QLabel("Recherche:")
        filter_layout.addWidget(self.search_filter_label)
        
        self.search_filter_edit = QLineEdit()
        self.search_filter_edit.setPlaceholderText("Filtrer par nom, SSID...")
        self.search_filter_edit.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_filter_edit, 2)
        
        main_layout.addLayout(filter_layout)
        
        # Liste des réseaux
        self.network_list = QListWidget()
        self.network_list.itemClicked.connect(self.on_network_selected)
        main_layout.addWidget(self.network_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_network)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_network)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_network)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
    
    def load_buildings(self):
        """Charge la liste des bâtiments pour le filtre"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, name FROM buildings WHERE world_id = ? ORDER BY name",
                (self.world_id,)
            )
            
            buildings = cursor.fetchall()
            for building in buildings:
                self.building_filter_combo.addItem(building['name'], building['id'])
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des bâtiments pour le filtre: {str(e)}")
    
    def load_networks(self, building_id=None, network_type=None, search_text=None):
        """Charge la liste des réseaux avec filtre optionnel"""
        try:
            self.network_list.clear()
            
            query = "SELECT n.id, n.name, n.ssid, n.network_type, n.security_level, n.security_type, "
            query += "n.is_hidden, n.building_id, b.name as building_name "
            query += "FROM networks n LEFT JOIN buildings b ON n.building_id = b.id "
            query += "WHERE n.world_id = ? "
            
            params = [self.world_id]
            
            if building_id:
                query += "AND n.building_id = ? "
                params.append(building_id)
            
            if network_type:
                query += "AND n.network_type = ? "
                params.append(network_type)
            
            if search_text:
                query += "AND (n.name LIKE ? OR n.ssid LIKE ?) "
                search_param = f"%{search_text}%"
                params.append(search_param)
                params.append(search_param)
            
            query += "ORDER BY n.name"
            
            cursor = self.db.conn.cursor()
            cursor.execute(query, params)
            
            networks = cursor.fetchall()
            
            for net in networks:
                # Formatage du texte
                display_text = f"{net['name']} "
                if 'ssid' in net and net['ssid']:
                    display_text += f"[{net['ssid']}] "
                display_text += f"({net['network_type']}) "
                if 'building_name' in net and net['building_name']:
                    display_text += f"- {net['building_name']}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, net['id'])
                
                # Colorier selon le type de réseau et sécurité
                if 'network_type' in net and net['network_type'] == 'WiFi':
                    item.setForeground(Qt.GlobalColor.cyan)
                elif 'network_type' in net and net['network_type'] == 'LAN':
                    item.setForeground(Qt.GlobalColor.green)
                elif 'network_type' in net and net['network_type'] == 'VPN':
                    item.setForeground(Qt.GlobalColor.yellow)
                elif 'network_type' in net and net['network_type'] == 'IoT':
                    item.setForeground(Qt.GlobalColor.magenta)
                
                # Marquer les réseaux masqués
                if 'is_hidden' in net and net['is_hidden']:
                    item.setForeground(Qt.GlobalColor.darkGray)
                
                # Colorier l'arrière-plan selon le niveau de sécurité
                if 'security_level' in net:
                    security_level = int(net['security_level'])
                    if security_level <= 3:  # Faible sécurité
                        item.setBackground(Qt.GlobalColor.darkGreen)
                    elif security_level <= 6:  # Sécurité moyenne
                        item.setBackground(Qt.GlobalColor.darkBlue)
                    else:  # Haute sécurité
                        item.setBackground(Qt.GlobalColor.darkRed)
                
                self.network_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des réseaux: {str(e)}")
    
    def apply_filters(self):
        """Applique les filtres sélectionnés"""
        building_id = self.building_filter_combo.currentData()
        
        network_type = None
        if self.type_filter_combo.currentIndex() > 0:
            network_type = self.type_filter_combo.currentText()
        
        search_text = self.search_filter_edit.text()
        if not search_text.strip():
            search_text = None
        
        self.load_networks(building_id, network_type, search_text)
    
    def on_network_selected(self, item):
        """Gère la sélection d'un réseau"""
        network_id = item.data(Qt.ItemDataRole.UserRole)
        self.network_selected.emit(network_id)
        
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_network(self):
        """Ajoute un nouveau réseau"""
        dialog = NetworkEditor(self.db, self.world_id, parent=self)
        if dialog.exec():
            try:
                network_data = dialog.get_network_data()
                network_id = f"net_{uuid.uuid4().hex[:8]}"
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """INSERT INTO networks 
                       (id, world_id, name, ssid, network_type, 
                        security_level, security_type, encryption, 
                        signal_strength, building_id, is_hidden, 
                        connected_devices, vulnerabilities, description)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (network_id, self.world_id, network_data["name"], 
                     network_data["ssid"], network_data["network_type"],
                     network_data["security_level"], network_data["security_type"],
                     network_data["encryption"], network_data["signal_strength"],
                     network_data["building_id"], network_data["is_hidden"],
                     network_data["connected_devices"], network_data["vulnerabilities"],
                     network_data["description"])
                )
                
                self.db.conn.commit()
                self.load_networks()
                
                logger.info(f"Réseau ajouté: {network_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de l'ajout du réseau: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter le réseau: {str(e)}")
    
    def edit_network(self):
        """Modifie un réseau existant"""
        selected_items = self.network_list.selectedItems()
        if not selected_items:
            return
            
        network_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        dialog = NetworkEditor(self.db, self.world_id, network_id, parent=self)
        if dialog.exec():
            try:
                network_data = dialog.get_network_data()
                
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """UPDATE networks 
                       SET name = ?, ssid = ?, network_type = ?, 
                           security_level = ?, security_type = ?, 
                           encryption = ?, signal_strength = ?, 
                           building_id = ?, is_hidden = ?, 
                           connected_devices = ?, vulnerabilities = ?, 
                           description = ?
                       WHERE id = ? AND world_id = ?""",
                    (network_data["name"], network_data["ssid"],
                     network_data["network_type"], network_data["security_level"],
                     network_data["security_type"], network_data["encryption"],
                     network_data["signal_strength"], network_data["building_id"],
                     network_data["is_hidden"], network_data["connected_devices"],
                     network_data["vulnerabilities"], network_data["description"],
                     network_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_networks()
                
                logger.info(f"Réseau modifié: {network_data['name']}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la modification du réseau: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier le réseau: {str(e)}")
    
    def delete_network(self):
        """Supprime un réseau"""
        selected_items = self.network_list.selectedItems()
        if not selected_items:
            return
            
        network_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        network_name = selected_items[0].text().split(' (')[0]
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer le réseau '{network_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "DELETE FROM networks WHERE id = ? AND world_id = ?",
                    (network_id, self.world_id)
                )
                
                self.db.conn.commit()
                self.load_networks()
                
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                
                logger.info(f"Réseau supprimé: {network_name}")
                
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression du réseau: {str(e)}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le réseau: {str(e)}")
