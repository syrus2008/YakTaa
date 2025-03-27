#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur de bâtiments pour l'éditeur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QCheckBox, QTextEdit,
    QTabWidget, QWidget, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

logger = logging.getLogger(__name__)

class BuildingEditor(QDialog):
    """Boîte de dialogue pour l'édition des bâtiments"""
    
    def __init__(self, db, world_id, building_id=None, location_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.building_id = building_id
        self.location_id = location_id  # Lieu où se trouve le bâtiment (obligatoire pour un nouveau bâtiment)
        self.is_new = building_id is None
        
        self.init_ui()
        
        if not self.is_new:
            self.load_building_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Éditeur de bâtiment" if self.is_new else "Modifier le bâtiment")
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
        
        # Type de bâtiment
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "residential", "commercial", "government", "corporate", 
            "industrial", "educational", "medical", "entertainment", "special"
        ])
        basic_layout.addRow("Type:", self.type_combo)
        
        # Niveau de sécurité
        self.security_spin = QSpinBox()
        self.security_spin.setMinimum(1)
        self.security_spin.setMaximum(5)
        self.security_spin.setValue(2)
        basic_layout.addRow("Niveau de sécurité:", self.security_spin)
        
        # Nombre d'étages
        self.floors_spin = QSpinBox()
        self.floors_spin.setMinimum(1)
        self.floors_spin.setMaximum(200)
        self.floors_spin.setValue(1)
        basic_layout.addRow("Nombre d'étages:", self.floors_spin)
        
        # Lieu
        self.location_combo = QComboBox()
        self.load_locations()
        basic_layout.addRow("Lieu:", self.location_combo)
        
        # Bâtiment spécial
        self.is_special_check = QCheckBox("Bâtiment spécial")
        basic_layout.addRow(self.is_special_check)
        
        tabs.addTab(basic_tab, "Informations de base")
        
        # Onglet des attributs avancés
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Propriétaire
        self.owner_edit = QLineEdit()
        advanced_layout.addRow("Propriétaire:", self.owner_edit)
        
        # Accès public
        self.public_access_check = QCheckBox("Accès public")
        self.public_access_check.setChecked(True)
        advanced_layout.addRow(self.public_access_check)
        
        # Niveau de maintenance
        self.maintenance_spin = QSpinBox()
        self.maintenance_spin.setMinimum(1)
        self.maintenance_spin.setMaximum(5)
        self.maintenance_spin.setValue(3)
        advanced_layout.addRow("Niveau de maintenance:", self.maintenance_spin)
        
        # Année de construction
        self.year_built_spin = QSpinBox()
        self.year_built_spin.setMinimum(1900)
        self.year_built_spin.setMaximum(2100)
        self.year_built_spin.setValue(2050)
        advanced_layout.addRow("Année de construction:", self.year_built_spin)
        
        tabs.addTab(advanced_tab, "Attributs avancés")
        
        # Onglet de description
        description_tab = QWidget()
        description_layout = QVBoxLayout(description_tab)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez une description détaillée du bâtiment...")
        description_layout.addWidget(self.description_edit)
        
        tabs.addTab(description_tab, "Description")
        
        main_layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_building)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_locations(self):
        """Charge la liste des lieux depuis la base de données"""
        
        self.location_combo.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name
        FROM locations
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        locations = cursor.fetchall()
        
        for location in locations:
            self.location_combo.addItem(location["name"], location["id"])
        
        # Sélectionner le lieu spécifié (si fourni)
        if self.location_id:
            for i in range(self.location_combo.count()):
                if self.location_combo.itemData(i) == self.location_id:
                    self.location_combo.setCurrentIndex(i)
                    break
    
    def load_building_data(self):
        """Charge les données du bâtiment depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT name, building_type, security_level, floors, location_id,
               is_special, owner, public_access, maintenance_level, 
               year_built, description
        FROM buildings
        WHERE id = ? AND world_id = ?
        """, (self.building_id, self.world_id))
        
        building = cursor.fetchone()
        
        if not building:
            QMessageBox.critical(self, "Erreur", f"Impossible de trouver le bâtiment avec l'ID {self.building_id}")
            self.reject()
            return
        
        # Remplir les champs
        self.name_edit.setText(building["name"])
        
        # Trouver l'index du type de bâtiment
        type_index = self.type_combo.findText(building["building_type"])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.security_spin.setValue(building["security_level"])
        self.floors_spin.setValue(building["floors"])
        
        # Trouver l'index du lieu
        if building["location_id"]:
            for i in range(self.location_combo.count()):
                if self.location_combo.itemData(i) == building["location_id"]:
                    self.location_combo.setCurrentIndex(i)
                    break
        
        self.is_special_check.setChecked(building["is_special"])
        
        if building["owner"]:
            self.owner_edit.setText(building["owner"])
        
        self.public_access_check.setChecked(building["public_access"])
        
        if building["maintenance_level"]:
            self.maintenance_spin.setValue(building["maintenance_level"])
        
        if building["year_built"]:
            self.year_built_spin.setValue(building["year_built"])
        
        if building["description"]:
            self.description_edit.setText(building["description"])
    
    def save_building(self):
        """Sauvegarde les données du bâtiment dans la base de données"""
        
        # Récupérer les valeurs
        name = self.name_edit.text()
        building_type = self.type_combo.currentText()
        security_level = self.security_spin.value()
        floors = self.floors_spin.value()
        
        location_id = None
        if self.location_combo.currentIndex() >= 0:
            location_id = self.location_combo.currentData()
        
        is_special = self.is_special_check.isChecked()
        owner = self.owner_edit.text()
        public_access = self.public_access_check.isChecked()
        maintenance_level = self.maintenance_spin.value()
        year_built = self.year_built_spin.value()
        description = self.description_edit.toPlainText()
        
        # Valider les données
        if not name:
            QMessageBox.warning(self, "Validation", "Le nom du bâtiment est obligatoire.")
            return
        
        if not location_id:
            QMessageBox.warning(self, "Validation", "Le lieu du bâtiment est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        if self.is_new:
            # Générer un nouvel ID
            self.building_id = str(uuid.uuid4())
            
            # Insérer le nouveau bâtiment
            cursor.execute("""
            INSERT INTO buildings (
                id, world_id, name, building_type, security_level, floors,
                location_id, is_special, owner, public_access, 
                maintenance_level, year_built, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.building_id, self.world_id, name, building_type, security_level,
                floors, location_id, is_special, owner, public_access,
                maintenance_level, year_built, description
            ))
        else:
            # Mettre à jour le bâtiment existant
            cursor.execute("""
            UPDATE buildings
            SET name = ?, building_type = ?, security_level = ?, floors = ?,
                location_id = ?, is_special = ?, owner = ?, public_access = ?,
                maintenance_level = ?, year_built = ?, description = ?
            WHERE id = ? AND world_id = ?
            """, (
                name, building_type, security_level, floors,
                location_id, is_special, owner, public_access,
                maintenance_level, year_built, description,
                self.building_id, self.world_id
            ))
        
        self.db.conn.commit()
        
        # Accepter la boîte de dialogue
        self.accept()
