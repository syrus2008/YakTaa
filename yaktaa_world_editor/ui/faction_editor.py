#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'édition des factions dans l'éditeur de monde YakTaa
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

class FactionEditor(QDialog):
    """Dialogue d'édition d'une faction"""
    
    def __init__(self, db, world_id, faction_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.faction_id = faction_id
        self.faction_data = None
        
        self.setWindowTitle("Éditeur de faction")
        self.resize(600, 500)
        
        self.init_ui()
        
        if self.faction_id:
            self.load_faction_data()
        
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
        
        # Idéologie
        self.ideology_edit = QLineEdit()
        form_layout.addRow("Idéologie:", self.ideology_edit)
        
        # Niveau de puissance
        self.power_level_spin = QSpinBox()
        self.power_level_spin.setRange(1, 10)
        self.power_level_spin.setValue(5)
        form_layout.addRow("Niveau de puissance:", self.power_level_spin)
        
        # Territoire
        self.territory_edit = QTextEdit()
        form_layout.addRow("Territoire:", self.territory_edit)
        
        # Membres notables
        self.notable_members_edit = QTextEdit()
        form_layout.addRow("Membres notables:\n(un par ligne)", self.notable_members_edit)
        
        # Icône
        self.icon_edit = QLineEdit()
        form_layout.addRow("Icône:", self.icon_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_faction_data(self):
        """Charge les données de la faction"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM factions WHERE id = ? AND world_id = ?",
                (self.faction_id, self.world_id)
            )
            faction = cursor.fetchone()
            if faction:
                self.faction_data = dict(faction)
                
                # Remplir les champs
                self.name_edit.setText(self.faction_data["name"])
                self.description_edit.setText(self.faction_data.get("description", ""))
                self.ideology_edit.setText(self.faction_data.get("ideology", ""))
                self.power_level_spin.setValue(self.faction_data.get("power_level", 5))
                
                # Champs JSON
                try:
                    territory = json.loads(self.faction_data.get("territory", "[]"))
                    self.territory_edit.setText("\n".join(territory))
                except (json.JSONDecodeError, TypeError):
                    self.territory_edit.setText("")
                
                try:
                    members = json.loads(self.faction_data.get("notable_members", "[]"))
                    self.notable_members_edit.setText("\n".join(members))
                except (json.JSONDecodeError, TypeError):
                    self.notable_members_edit.setText("")
                
                self.icon_edit.setText(self.faction_data.get("icon", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de faction: {str(e)}")
    
    def get_faction_data(self):
        """Récupère les données du formulaire"""
        data = {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "ideology": self.ideology_edit.text(),
            "power_level": self.power_level_spin.value(),
            "territory": json.dumps([t for t in self.territory_edit.toPlainText().split('\n') if t.strip()]),
            "notable_members": json.dumps([m for m in self.notable_members_edit.toPlainText().split('\n') if m.strip()]),
            "icon": self.icon_edit.text()
        }
        return data
    
    def accept(self):
        """Validation et sauvegarde"""
        if not self.name_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Champ obligatoire", "Le nom de la faction est obligatoire.")
            return
        
        super().accept()
