#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9dition des logiciels dans l'u00e9diteur de monde YakTaa
"""

import logging
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QPushButton, QLabel, QDialogButtonBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class SoftwareEditor(QDialog):
    """Dialogue d'u00e9dition d'un logiciel"""
    
    def __init__(self, db, world_id, software_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.software_id = software_id
        self.software_data = None
        
        self.setWindowTitle("u00c9diteur de logiciel")
        self.resize(600, 500)
        
        self.init_ui()
        
        if self.software_id:
            self.load_software_data()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom
        self.name_edit = QLineEdit()
        form_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        form_layout.addRow("Description:", self.description_edit)
        
        # Type de logiciel
        self.software_type_combo = QComboBox()
        software_types = [
            "os", "navigateur", "messagerie", "antivirus", "firewall", 
            "cracker", "keylogger", "exploit", "virus", "trojan", 
            "ransomware", "spyware", "crypteur", "vpn", "utilitaire"
        ]
        self.software_type_combo.addItems(software_types)
        form_layout.addRow("Type de logiciel:", self.software_type_combo)
        
        # Version
        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0")
        form_layout.addRow("Version:", self.version_edit)
        
        # Type de licence
        self.license_type_combo = QComboBox()
        license_types = [
            "gratuit", "shareware", "commercial", "libre", "pirateu00e9", 
            "mallware", "personnalisu00e9", "gouvernemental", "militaire"
        ]
        self.license_type_combo.addItems(license_types)
        form_layout.addRow("Type de licence:", self.license_type_combo)
        
        # Configuration requise
        self.system_requirements_edit = QTextEdit()
        form_layout.addRow("Configuration requise:", self.system_requirements_edit)
        
        # Capacitu00e9s
        self.capabilities_edit = QTextEdit()
        form_layout.addRow("Capacitu00e9s:\n(une par ligne)", self.capabilities_edit)
        
        # Raretu00e9
        self.rarity_combo = QComboBox()
        rarities = ["commun", "peu commun", "rare", "u00e9pique", "lu00e9gendaire", "unique"]
        self.rarity_combo.addItems(rarities)
        form_layout.addRow("Raretu00e9:", self.rarity_combo)
        
        # Valeur
        self.value_spin = QSpinBox()
        self.value_spin.setRange(0, 99999)
        self.value_spin.setValue(50)
        form_layout.addRow("Valeur (u00a5):", self.value_spin)
        
        # Emplacement initial
        self.location_type_combo = QComboBox()
        location_types = ["device", "shop", "network", "file", "quest"]
        self.location_type_combo.addItems(location_types)
        form_layout.addRow("Type d'emplacement:", self.location_type_combo)
        
        # ID d'emplacement
        self.location_id_edit = QLineEdit()
        form_layout.addRow("ID d'emplacement:", self.location_id_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_software_data(self):
        """Charge les donnu00e9es du logiciel"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM software WHERE id = ? AND world_id = ?",
                (self.software_id, self.world_id)
            )
            software = cursor.fetchone()
            if software:
                self.software_data = dict(software)
                
                # Remplir les champs
                self.name_edit.setText(self.software_data["name"])
                self.description_edit.setText(self.software_data.get("description", ""))
                
                # Trouver l'index du type de logiciel dans la combobox
                software_type = self.software_data.get("software_type", "utilitaire")
                index = self.software_type_combo.findText(software_type)
                if index >= 0:
                    self.software_type_combo.setCurrentIndex(index)
                
                self.version_edit.setText(self.software_data.get("version", "1.0"))
                
                # Trouver l'index du type de licence dans la combobox
                license_type = self.software_data.get("license_type", "commercial")
                index = self.license_type_combo.findText(license_type)
                if index >= 0:
                    self.license_type_combo.setCurrentIndex(index)
                
                self.system_requirements_edit.setText(self.software_data.get("system_requirements", ""))
                
                # Capacitu00e9s
                try:
                    capabilities = json.loads(self.software_data.get("capabilities", "[]"))
                    self.capabilities_edit.setText("\n".join(capabilities))
                except (json.JSONDecodeError, TypeError):
                    self.capabilities_edit.setText("")
                
                # Trouver l'index de la raretu00e9 dans la combobox
                rarity = self.software_data.get("rarity", "commun")
                index = self.rarity_combo.findText(rarity)
                if index >= 0:
                    self.rarity_combo.setCurrentIndex(index)
                
                self.value_spin.setValue(self.software_data.get("value", 50))
                
                # Trouver l'index du type d'emplacement dans la combobox
                location_type = self.software_data.get("location_type", "device")
                index = self.location_type_combo.findText(location_type)
                if index >= 0:
                    self.location_type_combo.setCurrentIndex(index)
                
                self.location_id_edit.setText(self.software_data.get("location_id", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des donnu00e9es du logiciel: {str(e)}")
    
    def get_software_data(self):
        """Ru00e9cupu00e8re les donnu00e9es du formulaire"""
        data = {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "software_type": self.software_type_combo.currentText(),
            "version": self.version_edit.text(),
            "license_type": self.license_type_combo.currentText(),
            "system_requirements": self.system_requirements_edit.toPlainText(),
            "capabilities": json.dumps([c for c in self.capabilities_edit.toPlainText().split('\n') if c.strip()]),
            "rarity": self.rarity_combo.currentText(),
            "value": self.value_spin.value(),
            "location_type": self.location_type_combo.currentText(),
            "location_id": self.location_id_edit.text()
        }
        return data
    
    def accept(self):
        """Validation et sauvegarde"""
        if not self.name_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Champ obligatoire", "Le nom du logiciel est obligatoire.")
            return
        
        super().accept()
