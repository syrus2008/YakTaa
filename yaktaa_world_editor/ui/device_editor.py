#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur d'appareils pour l'éditeur de monde YakTaa
"""

import logging
import uuid
import random
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QCheckBox, QTextEdit,
    QTabWidget, QWidget, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

logger = logging.getLogger(__name__)

class DeviceEditor(QDialog):
    """Boîte de dialogue pour l'édition des appareils"""
    
    def __init__(self, db, world_id, device_id=None, character_id=None, building_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.device_id = device_id
        self.character_id = character_id  # Propriétaire de l'appareil (optionnel)
        self.building_id = building_id    # Bâtiment où se trouve l'appareil (optionnel)
        self.is_new = device_id is None
        
        self.init_ui()
        
        if not self.is_new:
            self.load_device_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Éditeur d'appareil" if self.is_new else "Modifier l'appareil")
        self.setMinimumSize(600, 500)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet des informations de base
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Nom
        self.name_edit = QLineEdit()
        basic_layout.addRow("Nom:", self.name_edit)
        
        # Type d'appareil
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "computer", "server", "smartphone", "tablet", 
            "iot_device", "security_system", "atm", "special"
        ])
        basic_layout.addRow("Type:", self.type_combo)
        
        # Type d'OS
        self.os_combo = QComboBox()
        self.os_combo.addItems([
            "Windows", "Linux", "macOS", "Android", 
            "iOS", "Custom", "Embedded"
        ])
        basic_layout.addRow("Système d'exploitation:", self.os_combo)
        
        # Niveau de sécurité
        self.security_spin = QSpinBox()
        self.security_spin.setMinimum(1)
        self.security_spin.setMaximum(5)
        self.security_spin.setValue(2)
        basic_layout.addRow("Niveau de sécurité:", self.security_spin)
        
        # Adresse IP
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.1")
        basic_layout.addRow("Adresse IP:", self.ip_edit)
        
        # Bouton pour générer une IP aléatoire
        generate_ip_button = QPushButton("Générer IP aléatoire")
        generate_ip_button.clicked.connect(self.generate_random_ip)
        basic_layout.addRow(generate_ip_button)
        
        # Propriétaire
        owner_group = QGroupBox("Propriétaire")
        owner_layout = QVBoxLayout(owner_group)
        
        self.owner_type_combo = QComboBox()
        self.owner_type_combo.addItems(["Aucun", "Personnage", "Bâtiment"])
        self.owner_type_combo.currentIndexChanged.connect(self.on_owner_type_changed)
        owner_layout.addWidget(self.owner_type_combo)
        
        self.character_combo = QComboBox()
        self.character_combo.setVisible(False)
        owner_layout.addWidget(self.character_combo)
        
        self.building_combo = QComboBox()
        self.building_combo.setVisible(False)
        owner_layout.addWidget(self.building_combo)
        
        basic_layout.addRow(owner_group)
        
        # Charger les listes de personnages et de bâtiments
        self.load_characters()
        self.load_buildings()
        
        # Définir le propriétaire initial
        if self.character_id:
            self.owner_type_combo.setCurrentIndex(1)  # Personnage
            self.on_owner_type_changed(1)
            for i in range(self.character_combo.count()):
                if self.character_combo.itemData(i) == self.character_id:
                    self.character_combo.setCurrentIndex(i)
                    break
        elif self.building_id:
            self.owner_type_combo.setCurrentIndex(2)  # Bâtiment
            self.on_owner_type_changed(2)
            for i in range(self.building_combo.count()):
                if self.building_combo.itemData(i) == self.building_id:
                    self.building_combo.setCurrentIndex(i)
                    break
        
        tabs.addTab(basic_tab, "Informations de base")
        
        # Onglet des caractéristiques techniques
        tech_tab = QWidget()
        tech_layout = QFormLayout(tech_tab)
        
        # Puissance de calcul
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setMinimum(1)
        self.cpu_spin.setMaximum(10)
        self.cpu_spin.setValue(3)
        tech_layout.addRow("Puissance de calcul:", self.cpu_spin)
        
        # Mémoire
        self.memory_spin = QSpinBox()
        self.memory_spin.setMinimum(1)
        self.memory_spin.setMaximum(64)
        self.memory_spin.setValue(4)
        tech_layout.addRow("Mémoire (GB):", self.memory_spin)
        
        # Stockage
        self.storage_spin = QSpinBox()
        self.storage_spin.setMinimum(1)
        self.storage_spin.setMaximum(10000)
        self.storage_spin.setValue(500)
        tech_layout.addRow("Stockage (GB):", self.storage_spin)
        
        # Connectivité
        self.connectivity_combo = QComboBox()
        self.connectivity_combo.addItems([
            "Ethernet", "WiFi", "Bluetooth", "Cellular", 
            "Satellite", "Isolé"
        ])
        tech_layout.addRow("Connectivité:", self.connectivity_combo)
        
        tabs.addTab(tech_tab, "Caractéristiques techniques")
        
        # Onglet de description
        description_tab = QWidget()
        description_layout = QVBoxLayout(description_tab)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez une description détaillée de l'appareil...")
        description_layout.addWidget(self.description_edit)
        
        tabs.addTab(description_tab, "Description")
        
        main_layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_device)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_characters(self):
        """Charge la liste des personnages depuis la base de données"""
        
        self.character_combo.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name
        FROM characters
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        characters = cursor.fetchall()
        
        for character in characters:
            self.character_combo.addItem(character["name"], character["id"])
    
    def load_buildings(self):
        """Charge la liste des bâtiments depuis la base de données"""
        
        self.building_combo.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name
        FROM buildings
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        buildings = cursor.fetchall()
        
        for building in buildings:
            self.building_combo.addItem(building["name"], building["id"])
    
    def on_owner_type_changed(self, index):
        """Gère le changement de type de propriétaire"""
        
        self.character_combo.setVisible(index == 1)  # Personnage
        self.building_combo.setVisible(index == 2)   # Bâtiment
    
    def generate_random_ip(self):
        """Génère une adresse IP aléatoire"""
        
        # Générer une adresse IP aléatoire
        ip_parts = [str(random.randint(1, 254)) for _ in range(4)]
        ip_address = ".".join(ip_parts)
        
        self.ip_edit.setText(ip_address)
    
    def load_device_data(self):
        """Charge les données de l'appareil depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT name, device_type, os_type, security_level, ip_address,
               character_id, building_id, cpu_power, memory, storage,
               connectivity, description
        FROM devices
        WHERE id = ? AND world_id = ?
        """, (self.device_id, self.world_id))
        
        device = cursor.fetchone()
        
        if not device:
            QMessageBox.critical(self, "Erreur", f"Impossible de trouver l'appareil avec l'ID {self.device_id}")
            self.reject()
            return
        
        # Remplir les champs
        self.name_edit.setText(device["name"])
        
        # Trouver l'index du type d'appareil
        type_index = self.type_combo.findText(device["device_type"])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        # Trouver l'index du type d'OS
        os_index = self.os_combo.findText(device["os_type"])
        if os_index >= 0:
            self.os_combo.setCurrentIndex(os_index)
        
        self.security_spin.setValue(device["security_level"])
        
        if device["ip_address"]:
            self.ip_edit.setText(device["ip_address"])
        
        # Propriétaire
        if device["character_id"]:
            self.owner_type_combo.setCurrentIndex(1)  # Personnage
            self.on_owner_type_changed(1)
            for i in range(self.character_combo.count()):
                if self.character_combo.itemData(i) == device["character_id"]:
                    self.character_combo.setCurrentIndex(i)
                    break
        elif device["building_id"]:
            self.owner_type_combo.setCurrentIndex(2)  # Bâtiment
            self.on_owner_type_changed(2)
            for i in range(self.building_combo.count()):
                if self.building_combo.itemData(i) == device["building_id"]:
                    self.building_combo.setCurrentIndex(i)
                    break
        
        # Caractéristiques techniques
        if device["cpu_power"]:
            self.cpu_spin.setValue(device["cpu_power"])
        
        if device["memory"]:
            self.memory_spin.setValue(device["memory"])
        
        if device["storage"]:
            self.storage_spin.setValue(device["storage"])
        
        if device["connectivity"]:
            connectivity_index = self.connectivity_combo.findText(device["connectivity"])
            if connectivity_index >= 0:
                self.connectivity_combo.setCurrentIndex(connectivity_index)
        
        # Description
        if device["description"]:
            self.description_edit.setText(device["description"])
    
    def save_device(self):
        """Sauvegarde les données de l'appareil dans la base de données"""
        
        # Récupérer les valeurs
        name = self.name_edit.text()
        device_type = self.type_combo.currentText()
        os_type = self.os_combo.currentText()
        security_level = self.security_spin.value()
        ip_address = self.ip_edit.text()
        
        # Propriétaire
        owner_type = self.owner_type_combo.currentIndex()
        character_id = None
        building_id = None
        
        if owner_type == 1 and self.character_combo.currentIndex() >= 0:  # Personnage
            character_id = self.character_combo.currentData()
        elif owner_type == 2 and self.building_combo.currentIndex() >= 0:  # Bâtiment
            building_id = self.building_combo.currentData()
        
        # Caractéristiques techniques
        cpu_power = self.cpu_spin.value()
        memory = self.memory_spin.value()
        storage = self.storage_spin.value()
        connectivity = self.connectivity_combo.currentText()
        
        description = self.description_edit.toPlainText()
        
        # Valider les données
        if not name:
            QMessageBox.warning(self, "Validation", "Le nom de l'appareil est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        if self.is_new:
            # Générer un nouvel ID
            self.device_id = str(uuid.uuid4())
            
            # Insérer le nouvel appareil
            cursor.execute("""
            INSERT INTO devices (
                id, world_id, name, device_type, os_type, security_level,
                ip_address, character_id, building_id, cpu_power, memory,
                storage, connectivity, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.device_id, self.world_id, name, device_type, os_type,
                security_level, ip_address, character_id, building_id,
                cpu_power, memory, storage, connectivity, description
            ))
        else:
            # Mettre à jour l'appareil existant
            cursor.execute("""
            UPDATE devices
            SET name = ?, device_type = ?, os_type = ?, security_level = ?,
                ip_address = ?, character_id = ?, building_id = ?,
                cpu_power = ?, memory = ?, storage = ?, connectivity = ?,
                description = ?
            WHERE id = ? AND world_id = ?
            """, (
                name, device_type, os_type, security_level,
                ip_address, character_id, building_id,
                cpu_power, memory, storage, connectivity, description,
                self.device_id, self.world_id
            ))
        
        self.db.conn.commit()
        
        # Accepter la boîte de dialogue
        self.accept()
