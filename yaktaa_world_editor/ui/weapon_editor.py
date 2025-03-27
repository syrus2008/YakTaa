#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9dition des armes dans l'u00e9diteur de monde YakTaa
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

class WeaponEditor(QDialog):
    """Dialogue d'u00e9dition d'une arme"""
    
    def __init__(self, db, world_id, weapon_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.weapon_id = weapon_id
        self.weapon_data = None
        
        self.setWindowTitle("u00c9diteur d'arme")
        self.resize(600, 500)
        
        self.init_ui()
        
        if self.weapon_id:
            self.load_weapon_data()
        
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
        
        # Type de du00e9gu00e2ts
        self.damage_type_combo = QComboBox()
        damage_types = ["physique", "u00e9nergie", "emp", "explosif", "chimique", "thermique"]
        self.damage_type_combo.addItems(damage_types)
        form_layout.addRow("Type de du00e9gu00e2ts:", self.damage_type_combo)
        
        # Du00e9gu00e2ts
        self.damage_spin = QSpinBox()
        self.damage_spin.setRange(1, 100)
        self.damage_spin.setValue(10)
        form_layout.addRow("Du00e9gu00e2ts:", self.damage_spin)
        
        # Portu00e9e
        self.range_spin = QSpinBox()
        self.range_spin.setRange(1, 500)
        self.range_spin.setValue(10)
        form_layout.addRow("Portu00e9e:", self.range_spin)
        
        # Pru00e9cision
        self.accuracy_spin = QSpinBox()
        self.accuracy_spin.setRange(1, 100)
        self.accuracy_spin.setValue(70)
        form_layout.addRow("Pru00e9cision (%):", self.accuracy_spin)
        
        # Cadence de tir
        self.rate_of_fire_spin = QSpinBox()
        self.rate_of_fire_spin.setRange(1, 100)
        self.rate_of_fire_spin.setValue(1)
        form_layout.addRow("Cadence de tir:", self.rate_of_fire_spin)
        
        # Type de munitions
        self.ammo_type_edit = QLineEdit()
        form_layout.addRow("Type de munitions:", self.ammo_type_edit)
        
        # Capacitu00e9 du chargeur
        self.ammo_capacity_spin = QSpinBox()
        self.ammo_capacity_spin.setRange(1, 200)
        self.ammo_capacity_spin.setValue(10)
        form_layout.addRow("Capacitu00e9 du chargeur:", self.ammo_capacity_spin)
        
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
    
    def load_weapon_data(self):
        """Charge les donnu00e9es de l'arme"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM weapons WHERE id = ? AND world_id = ?",
                (self.weapon_id, self.world_id)
            )
            weapon = cursor.fetchone()
            if weapon:
                self.weapon_data = dict(weapon)
                
                # Remplir les champs
                self.name_edit.setText(self.weapon_data["name"])
                self.description_edit.setText(self.weapon_data.get("description", ""))
                
                # Trouver l'index du type de du00e9gu00e2ts dans la combobox
                damage_type = self.weapon_data.get("damage_type", "physique")
                index = self.damage_type_combo.findText(damage_type)
                if index >= 0:
                    self.damage_type_combo.setCurrentIndex(index)
                
                self.damage_spin.setValue(self.weapon_data.get("damage", 10))
                self.range_spin.setValue(self.weapon_data.get("weapon_range", 10))
                self.accuracy_spin.setValue(self.weapon_data.get("accuracy", 70))
                self.rate_of_fire_spin.setValue(self.weapon_data.get("rate_of_fire", 1))
                self.ammo_type_edit.setText(self.weapon_data.get("ammo_type", ""))
                self.ammo_capacity_spin.setValue(self.weapon_data.get("ammo_capacity", 10))
                self.mod_slots_spin.setValue(self.weapon_data.get("mod_slots", 2))
                
                # Trouver l'index de la raretu00e9 dans la combobox
                rarity = self.weapon_data.get("rarity", "commun")
                index = self.rarity_combo.findText(rarity)
                if index >= 0:
                    self.rarity_combo.setCurrentIndex(index)
                
                self.value_spin.setValue(self.weapon_data.get("value", 100))
                
                # Trouver l'index du type d'emplacement dans la combobox
                location_type = self.weapon_data.get("location_type", "loot")
                index = self.location_type_combo.findText(location_type)
                if index >= 0:
                    self.location_type_combo.setCurrentIndex(index)
                
                self.location_id_edit.setText(self.weapon_data.get("location_id", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des donnu00e9es de l'arme: {str(e)}")
    
    def get_weapon_data(self):
        """Ru00e9cupu00e8re les donnu00e9es du formulaire"""
        data = {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "damage_type": self.damage_type_combo.currentText(),
            "damage": self.damage_spin.value(),
            "weapon_range": self.range_spin.value(),
            "accuracy": self.accuracy_spin.value(),
            "rate_of_fire": self.rate_of_fire_spin.value(),
            "ammo_type": self.ammo_type_edit.text(),
            "ammo_capacity": self.ammo_capacity_spin.value(),
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
            QMessageBox.warning(self, "Champ obligatoire", "Le nom de l'arme est obligatoire.")
            return
        
        super().accept()
