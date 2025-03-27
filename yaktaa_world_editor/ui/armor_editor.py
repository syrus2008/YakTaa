#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9dition des armures dans l'u00e9diteur de monde YakTaa
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

class ArmorEditor(QDialog):
    """Dialogue d'u00e9dition d'une armure"""
    
    def __init__(self, db, world_id, armor_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.armor_id = armor_id
        self.armor_data = None
        
        self.setWindowTitle("u00c9diteur d'armure")
        self.resize(600, 500)
        
        self.init_ui()
        
        if self.armor_id:
            self.load_armor_data()
        
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
        
        # Type de du00e9fense
        self.defense_type_combo = QComboBox()
        defense_types = ["physique", "u00e9nergie", "emp", "explosif", "chimique", "thermique"]
        self.defense_type_combo.addItems(defense_types)
        form_layout.addRow("Type de du00e9fense:", self.defense_type_combo)
        
        # Du00e9fense
        self.defense_spin = QSpinBox()
        self.defense_spin.setRange(1, 100)
        self.defense_spin.setValue(10)
        form_layout.addRow("Du00e9fense:", self.defense_spin)
        
        # Emplacements
        self.slots_edit = QLineEdit()
        self.slots_edit.setPlaceholderText("tu00eate,torse,bras,jambes,pieds")
        form_layout.addRow("Emplacements:", self.slots_edit)
        
        # Poids
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(1, 100)
        self.weight_spin.setValue(5)
        form_layout.addRow("Poids:", self.weight_spin)
        
        # Durabilitu00e9
        self.durability_spin = QSpinBox()
        self.durability_spin.setRange(1, 1000)
        self.durability_spin.setValue(100)
        form_layout.addRow("Durabilitu00e9:", self.durability_spin)
        
        # Emplacements de modification
        self.mod_slots_spin = QSpinBox()
        self.mod_slots_spin.setRange(0, 10)
        self.mod_slots_spin.setValue(2)
        form_layout.addRow("Emplacements de mods:", self.mod_slots_spin)
        
        # Raretu00e9
        self.rarity_combo = QComboBox()
        rarities = ["commun", "peu commun", "rare", "u00e9pique", "lu00e9gendaire", "unique"]
        self.rarity_combo.addItems(rarities)
        form_layout.addRow("Raretu00e9:", self.rarity_combo)
        
        # Valeur
        self.value_spin = QSpinBox()
        self.value_spin.setRange(1, 99999)
        self.value_spin.setValue(100)
        form_layout.addRow("Valeur (u00a5):", self.value_spin)
        
        # Emplacement initial
        self.location_type_combo = QComboBox()
        location_types = ["shop", "loot", "character", "quest"]
        self.location_type_combo.addItems(location_types)
        form_layout.addRow("Type d'emplacement:", self.location_type_combo)
        
        # ID d'emplacement (shop, character, etc.)
        self.location_id_edit = QLineEdit()
        form_layout.addRow("ID d'emplacement:", self.location_id_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_armor_data(self):
        """Charge les donnu00e9es de l'armure"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM armors WHERE id = ? AND world_id = ?",
                (self.armor_id, self.world_id)
            )
            armor = cursor.fetchone()
            if armor:
                self.armor_data = dict(armor)
                
                # Remplir les champs
                self.name_edit.setText(self.armor_data["name"])
                self.description_edit.setText(self.armor_data.get("description", ""))
                
                # Trouver l'index du type de du00e9fense dans la combobox
                defense_type = self.armor_data.get("defense_type", "physique")
                index = self.defense_type_combo.findText(defense_type)
                if index >= 0:
                    self.defense_type_combo.setCurrentIndex(index)
                
                self.defense_spin.setValue(self.armor_data.get("defense", 10))
                
                # Emplacements
                slots = self.armor_data.get("slots", "")
                try:
                    if slots:
                        slots_list = json.loads(slots)
                        self.slots_edit.setText(",".join(slots_list))
                except (json.JSONDecodeError, TypeError):
                    self.slots_edit.setText(slots)
                
                self.weight_spin.setValue(self.armor_data.get("weight", 5))
                self.durability_spin.setValue(self.armor_data.get("durability", 100))
                self.mod_slots_spin.setValue(self.armor_data.get("mod_slots", 2))
                
                # Trouver l'index de la raretu00e9 dans la combobox
                rarity = self.armor_data.get("rarity", "commun")
                index = self.rarity_combo.findText(rarity)
                if index >= 0:
                    self.rarity_combo.setCurrentIndex(index)
                
                self.value_spin.setValue(self.armor_data.get("value", 100))
                
                # Trouver l'index du type d'emplacement dans la combobox
                location_type = self.armor_data.get("location_type", "loot")
                index = self.location_type_combo.findText(location_type)
                if index >= 0:
                    self.location_type_combo.setCurrentIndex(index)
                
                self.location_id_edit.setText(self.armor_data.get("location_id", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des donnu00e9es de l'armure: {str(e)}")
    
    def get_armor_data(self):
        """Ru00e9cupu00e8re les donnu00e9es du formulaire"""
        data = {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "defense_type": self.defense_type_combo.currentText(),
            "defense": self.defense_spin.value(),
            "slots": json.dumps([s.strip() for s in self.slots_edit.text().split(',') if s.strip()]),
            "weight": self.weight_spin.value(),
            "durability": self.durability_spin.value(),
            "mod_slots": self.mod_slots_spin.value(),
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
            QMessageBox.warning(self, "Champ obligatoire", "Le nom de l'armure est obligatoire.")
            return
        
        super().accept()
