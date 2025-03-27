#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9dition des implants dans l'u00e9diteur de monde YakTaa
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

class ImplantEditor(QDialog):
    """Dialogue d'u00e9dition d'un implant cybernétique"""
    
    def __init__(self, db, world_id, implant_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.implant_id = implant_id
        self.implant_data = None
        
        self.setWindowTitle("u00c9diteur d'implant cybernétique")
        self.resize(600, 550)
        
        self.init_ui()
        
        if self.implant_id:
            self.load_implant_data()
        
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
        
        # Type d'implant
        self.implant_type_combo = QComboBox()
        implant_types = [
            "cortical", "occulaire", "auriculaire", "neural", "dermique", 
            "osseux", "musculaire", "respiratoire", "circulatoire", "digestif", 
            "squelettique", "immunologique", "interface"
        ]
        self.implant_type_combo.addItems(implant_types)
        form_layout.addRow("Type d'implant:", self.implant_type_combo)
        
        # Emplacement sur le corps
        self.body_location_combo = QComboBox()
        body_locations = [
            "tête", "yeux", "oreilles", "cerveau", "bras", "bras_gauche", "bras_droit", 
            "jambes", "jambe_gauche", "jambe_droite", "torse", "peau", "squelette", 
            "système_nerveux", "système_digestif", "système_respiratoire", "système_circulatoire"
        ]
        self.body_location_combo.addItems(body_locations)
        form_layout.addRow("Emplacement:", self.body_location_combo)
        
        # Difficulté d'installation
        self.surgery_difficulty_spin = QSpinBox()
        self.surgery_difficulty_spin.setRange(1, 10)
        self.surgery_difficulty_spin.setValue(3)
        form_layout.addRow("Difficulté d'installation:", self.surgery_difficulty_spin)
        
        # Effets secondaires
        self.side_effects_edit = QTextEdit()
        self.side_effects_edit.setPlaceholderText("Insomnies\nParanoïa\nRisque de rejet\netc.")
        form_layout.addRow("Effets secondaires:\n(un par ligne)", self.side_effects_edit)
        
        # Compatibilité
        self.compatibility_edit = QTextEdit()
        self.compatibility_edit.setPlaceholderText("neuromancer_os\nchronos_interface\netc.")
        form_layout.addRow("Compatibilité:\n(un par ligne)", self.compatibility_edit)
        
        # Bonus
        self.bonus_edit = QTextEdit()
        self.bonus_edit.setPlaceholderText("vision:+2\nfurtivité:+3\netc.")
        form_layout.addRow("Bonus:\n(un par ligne, format attribut:valeur)", self.bonus_edit)
        
        # Rareté
        self.rarity_combo = QComboBox()
        rarities = ["commun", "peu commun", "rare", "épique", "légendaire", "unique"]
        self.rarity_combo.addItems(rarities)
        form_layout.addRow("Rareté:", self.rarity_combo)
        
        # Valeur
        self.value_spin = QSpinBox()
        self.value_spin.setRange(100, 999999)
        self.value_spin.setValue(1000)
        form_layout.addRow("Valeur (¥):", self.value_spin)
        
        # Légalité
        self.legality_combo = QComboBox()
        legality_types = ["légal", "réglementé", "militaire", "illégal", "expérimental"]
        self.legality_combo.addItems(legality_types)
        form_layout.addRow("Légalité:", self.legality_combo)
        
        # Fabricant/Corporation
        self.manufacturer_edit = QLineEdit()
        form_layout.addRow("Fabricant:", self.manufacturer_edit)
        
        # Emplacement initial
        self.location_type_combo = QComboBox()
        location_types = ["shop", "loot", "character", "clinic", "quest"]
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
    
    def load_implant_data(self):
        """Charge les données de l'implant"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM implants WHERE id = ? AND world_id = ?",
                (self.implant_id, self.world_id)
            )
            implant = cursor.fetchone()
            if implant:
                self.implant_data = dict(implant)
                
                # Remplir les champs
                self.name_edit.setText(self.implant_data["name"])
                self.description_edit.setText(self.implant_data.get("description", ""))
                
                # Trouver l'index du type d'implant dans la combobox
                implant_type = self.implant_data.get("implant_type", "neural")
                index = self.implant_type_combo.findText(implant_type)
                if index >= 0:
                    self.implant_type_combo.setCurrentIndex(index)
                
                # Trouver l'index de l'emplacement sur le corps dans la combobox
                body_location = self.implant_data.get("body_location", "cerveau")
                index = self.body_location_combo.findText(body_location)
                if index >= 0:
                    self.body_location_combo.setCurrentIndex(index)
                
                self.surgery_difficulty_spin.setValue(self.implant_data.get("surgery_difficulty", 3))
                
                # Effets secondaires
                try:
                    side_effects = json.loads(self.implant_data.get("side_effects", "[]"))
                    self.side_effects_edit.setText("\n".join(side_effects))
                except (json.JSONDecodeError, TypeError):
                    self.side_effects_edit.setText("")
                
                # Compatibilité
                try:
                    compatibility = json.loads(self.implant_data.get("compatibility", "[]"))
                    self.compatibility_edit.setText("\n".join(compatibility))
                except (json.JSONDecodeError, TypeError):
                    self.compatibility_edit.setText("")
                
                # Bonus
                try:
                    bonus = json.loads(self.implant_data.get("bonus", "{}"))
                    bonus_lines = [f"{k}:{v}" for k, v in bonus.items()]
                    self.bonus_edit.setText("\n".join(bonus_lines))
                except (json.JSONDecodeError, TypeError):
                    self.bonus_edit.setText("")
                
                # Trouver l'index de la rareté dans la combobox
                rarity = self.implant_data.get("rarity", "commun")
                index = self.rarity_combo.findText(rarity)
                if index >= 0:
                    self.rarity_combo.setCurrentIndex(index)
                
                self.value_spin.setValue(self.implant_data.get("value", 1000))
                
                # Trouver l'index de la légalité dans la combobox
                legality = self.implant_data.get("legality", "légal")
                index = self.legality_combo.findText(legality)
                if index >= 0:
                    self.legality_combo.setCurrentIndex(index)
                
                self.manufacturer_edit.setText(self.implant_data.get("manufacturer", ""))
                
                # Trouver l'index du type d'emplacement dans la combobox
                location_type = self.implant_data.get("location_type", "shop")
                index = self.location_type_combo.findText(location_type)
                if index >= 0:
                    self.location_type_combo.setCurrentIndex(index)
                
                self.location_id_edit.setText(self.implant_data.get("location_id", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de l'implant: {str(e)}")
    
    def get_implant_data(self):
        """Récupère les données du formulaire"""
        
        # Traiter les bonus
        bonus_dict = {}
        for line in self.bonus_edit.toPlainText().split('\n'):
            if line.strip() and ':' in line:
                key, value = line.split(':', 1)
                try:
                    bonus_dict[key.strip()] = int(value.strip())
                except ValueError:
                    bonus_dict[key.strip()] = value.strip()
        
        data = {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "implant_type": self.implant_type_combo.currentText(),
            "body_location": self.body_location_combo.currentText(),
            "surgery_difficulty": self.surgery_difficulty_spin.value(),
            "side_effects": json.dumps([s.strip() for s in self.side_effects_edit.toPlainText().split('\n') if s.strip()]),
            "compatibility": json.dumps([c.strip() for c in self.compatibility_edit.toPlainText().split('\n') if c.strip()]),
            "bonus": json.dumps(bonus_dict),
            "rarity": self.rarity_combo.currentText(),
            "value": self.value_spin.value(),
            "legality": self.legality_combo.currentText(),
            "manufacturer": self.manufacturer_edit.text(),
            "location_type": self.location_type_combo.currentText(),
            "location_id": self.location_id_edit.text()
        }
        return data
    
    def accept(self):
        """Validation et sauvegarde"""
        if not self.name_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Champ obligatoire", "Le nom de l'implant est obligatoire.")
            return
        
        super().accept()
