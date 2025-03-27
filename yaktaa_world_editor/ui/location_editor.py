#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur de lieux pour l'éditeur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QCheckBox, QTextEdit,
    QTabWidget, QWidget, QSlider, QMessageBox,
    QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

logger = logging.getLogger(__name__)

class LocationEditor(QDialog):
    """Boîte de dialogue pour l'édition des lieux"""
    
    def __init__(self, db, world_id, location_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.location_id = location_id
        self.is_new = location_id is None
        
        self.init_ui()
        
        if not self.is_new:
            self.load_location_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Éditeur de lieu" if self.is_new else "Modifier le lieu")
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
        
        # Type de lieu
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "city", "district", "rural", "industrial", 
            "government", "corporate", "special"
        ])
        basic_layout.addRow("Type:", self.type_combo)
        
        # Niveau de sécurité
        self.security_spin = QSpinBox()
        self.security_spin.setMinimum(1)
        self.security_spin.setMaximum(5)
        self.security_spin.setValue(3)
        basic_layout.addRow("Niveau de sécurité:", self.security_spin)
        
        # Population
        self.population_spin = QSpinBox()
        self.population_spin.setMinimum(0)
        self.population_spin.setMaximum(10000000)
        self.population_spin.setSingleStep(1000)
        self.population_spin.setValue(10000)
        basic_layout.addRow("Population:", self.population_spin)
        
        # Coordonnées
        coordinates_group = QGroupBox("Coordonnées sur la carte")
        coordinates_layout = QFormLayout(coordinates_group)
        
        self.x_coord_spin = QSpinBox()
        self.x_coord_spin.setMinimum(0)
        self.x_coord_spin.setMaximum(1000)
        self.x_coord_spin.setValue(500)
        coordinates_layout.addRow("X:", self.x_coord_spin)
        
        self.y_coord_spin = QSpinBox()
        self.y_coord_spin.setMinimum(0)
        self.y_coord_spin.setMaximum(1000)
        self.y_coord_spin.setValue(500)
        coordinates_layout.addRow("Y:", self.y_coord_spin)
        
        basic_layout.addRow(coordinates_group)
        
        # Lieu spécial
        self.is_special_check = QCheckBox("Lieu spécial")
        basic_layout.addRow(self.is_special_check)
        
        tabs.addTab(basic_tab, "Informations de base")
        
        # Onglet de description
        description_tab = QWidget()
        description_layout = QVBoxLayout(description_tab)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez une description détaillée du lieu...")
        description_layout.addWidget(self.description_edit)
        
        tabs.addTab(description_tab, "Description")
        
        # Onglet des attributs avancés
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Niveau de criminalité
        self.crime_rate_spin = QSpinBox()
        self.crime_rate_spin.setMinimum(1)
        self.crime_rate_spin.setMaximum(5)
        self.crime_rate_spin.setValue(3)
        advanced_layout.addRow("Niveau de criminalité:", self.crime_rate_spin)
        
        # Niveau de richesse
        self.wealth_spin = QSpinBox()
        self.wealth_spin.setMinimum(1)
        self.wealth_spin.setMaximum(5)
        self.wealth_spin.setValue(3)
        advanced_layout.addRow("Niveau de richesse:", self.wealth_spin)
        
        # Niveau technologique
        self.tech_level_spin = QSpinBox()
        self.tech_level_spin.setMinimum(1)
        self.tech_level_spin.setMaximum(5)
        self.tech_level_spin.setValue(3)
        advanced_layout.addRow("Niveau technologique:", self.tech_level_spin)
        
        # Faction dominante
        self.faction_combo = QComboBox()
        self.faction_combo.addItems([
            "Gouvernement", "Corporation", "Syndicat", 
            "Hackers", "Criminels", "Indépendants", "Neutre"
        ])
        advanced_layout.addRow("Faction dominante:", self.faction_combo)
        
        tabs.addTab(advanced_tab, "Attributs avancés")
        
        main_layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_location)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_location_data(self):
        """Charge les données du lieu depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT name, location_type, security_level, population, x_coord, y_coord,
               is_special, description, crime_rate, wealth_level, tech_level, faction
        FROM locations
        WHERE id = ? AND world_id = ?
        """, (self.location_id, self.world_id))
        
        location = cursor.fetchone()
        
        if not location:
            QMessageBox.critical(self, "Erreur", f"Impossible de trouver le lieu avec l'ID {self.location_id}")
            self.reject()
            return
        
        # Remplir les champs
        self.name_edit.setText(location["name"])
        
        # Trouver l'index du type de lieu
        type_index = self.type_combo.findText(location["location_type"])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.security_spin.setValue(location["security_level"])
        self.population_spin.setValue(location["population"])
        self.x_coord_spin.setValue(location["x_coord"])
        self.y_coord_spin.setValue(location["y_coord"])
        self.is_special_check.setChecked(location["is_special"])
        
        if location["description"]:
            self.description_edit.setText(location["description"])
        
        if location["crime_rate"]:
            self.crime_rate_spin.setValue(location["crime_rate"])
        
        if location["wealth_level"]:
            self.wealth_spin.setValue(location["wealth_level"])
        
        if location["tech_level"]:
            self.tech_level_spin.setValue(location["tech_level"])
        
        if location["faction"]:
            faction_index = self.faction_combo.findText(location["faction"])
            if faction_index >= 0:
                self.faction_combo.setCurrentIndex(faction_index)
    
    def save_location(self):
        """Sauvegarde les données du lieu dans la base de données"""
        
        # Récupérer les valeurs
        name = self.name_edit.text()
        location_type = self.type_combo.currentText()
        security_level = self.security_spin.value()
        population = self.population_spin.value()
        x_coord = self.x_coord_spin.value()
        y_coord = self.y_coord_spin.value()
        is_special = self.is_special_check.isChecked()
        description = self.description_edit.toPlainText()
        crime_rate = self.crime_rate_spin.value()
        wealth_level = self.wealth_spin.value()
        tech_level = self.tech_level_spin.value()
        faction = self.faction_combo.currentText()
        
        # Valider les données
        if not name:
            QMessageBox.warning(self, "Validation", "Le nom du lieu est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        if self.is_new:
            # Générer un nouvel ID
            self.location_id = str(uuid.uuid4())
            
            # Insérer le nouveau lieu
            cursor.execute("""
            INSERT INTO locations (
                id, world_id, name, location_type, security_level, population,
                x_coord, y_coord, is_special, description, crime_rate,
                wealth_level, tech_level, faction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.location_id, self.world_id, name, location_type, security_level,
                population, x_coord, y_coord, is_special, description, crime_rate,
                wealth_level, tech_level, faction
            ))
        else:
            # Mettre à jour le lieu existant
            cursor.execute("""
            UPDATE locations
            SET name = ?, location_type = ?, security_level = ?, population = ?,
                x_coord = ?, y_coord = ?, is_special = ?, description = ?,
                crime_rate = ?, wealth_level = ?, tech_level = ?, faction = ?
            WHERE id = ? AND world_id = ?
            """, (
                name, location_type, security_level, population,
                x_coord, y_coord, is_special, description,
                crime_rate, wealth_level, tech_level, faction,
                self.location_id, self.world_id
            ))
        
        self.db.conn.commit()
        
        # Accepter la boîte de dialogue
        self.accept()
