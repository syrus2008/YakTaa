#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'éditeur d'aliments pour l'éditeur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QPushButton, QDialogButtonBox,
    QTextEdit, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class FoodEditor(QDialog):
    """Dialogue d'édition d'aliments"""
    
    FOOD_TYPES = [
        "SNACK", "MEAL", "DRINK", "FRUIT", "VEGETABLE", 
        "MEAT", "DESSERT", "ENERGY_BAR", "MEDICINE", "SPECIAL"
    ]
    
    RARITY_LEVELS = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    
    def __init__(self, db, world_id, item_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.item_id = item_id
        self.editing_mode = item_id is not None
        
        self.item_data = {}
        if self.editing_mode:
            self.load_item_data()
        
        self.init_ui()
        
        # Configuration du titre de la fenêtre
        self.setWindowTitle("Modifier Aliment" if self.editing_mode else "Nouvel Aliment")
        self.resize(600, 500)
    
    def load_item_data(self):
        """Charge les données de l'aliment depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT *
        FROM food_items
        WHERE id = ?
        ''', (self.item_id,))
        
        item = cursor.fetchone()
        if item:
            self.item_data = dict(item)
        else:
            logger.error(f"Aliment {self.item_id} non trouvé")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Informations de base
        basic_group = QGroupBox("Informations de base")
        basic_layout = QFormLayout()
        
        # Champ ID
        self.id_edit = QLineEdit(self.item_data.get('id', f"food_{str(uuid.uuid4())}"))
        self.id_edit.setReadOnly(self.editing_mode)  # ID en lecture seule en mode édition
        basic_layout.addRow("ID:", self.id_edit)
        
        # Champ Nom
        self.name_edit = QLineEdit(self.item_data.get('name', ''))
        basic_layout.addRow("Nom:", self.name_edit)
        
        # Champ Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(self.item_data.get('description', ''))
        self.description_edit.setFixedHeight(100)
        basic_layout.addRow("Description:", self.description_edit)
        
        # Type d'aliment
        self.food_type_combo = QComboBox()
        for food_type in self.FOOD_TYPES:
            self.food_type_combo.addItem(food_type)
        
        current_type = self.item_data.get('food_type', 'SNACK')
        if current_type in self.FOOD_TYPES:
            self.food_type_combo.setCurrentText(current_type)
        basic_layout.addRow("Type d'aliment:", self.food_type_combo)
        
        # Prix
        self.price_spin = QSpinBox()
        self.price_spin.setRange(1, 10000000)
        self.price_spin.setValue(int(self.item_data.get('price', 10)))
        basic_layout.addRow("Prix:", self.price_spin)
        
        # Rareté
        self.rarity_combo = QComboBox()
        for rarity in self.RARITY_LEVELS:
            self.rarity_combo.addItem(rarity)
        
        current_rarity = self.item_data.get('rarity', 'COMMON')
        if current_rarity in self.RARITY_LEVELS:
            self.rarity_combo.setCurrentText(current_rarity)
        basic_layout.addRow("Rareté:", self.rarity_combo)
        
        basic_group.setLayout(basic_layout)
        main_layout.addWidget(basic_group)
        
        # Propriétés de restauration
        restore_group = QGroupBox("Propriétés de restauration")
        restore_layout = QFormLayout()
        
        # Restauration de santé
        self.health_restore_spin = QSpinBox()
        self.health_restore_spin.setRange(0, 100)
        self.health_restore_spin.setValue(int(self.item_data.get('health_restore', 5)))
        restore_layout.addRow("Restauration de santé:", self.health_restore_spin)
        
        # Restauration d'énergie
        self.energy_restore_spin = QSpinBox()
        self.energy_restore_spin.setRange(0, 100)
        self.energy_restore_spin.setValue(int(self.item_data.get('energy_restore', 5)))
        restore_layout.addRow("Restauration d'énergie:", self.energy_restore_spin)
        
        # Restauration mentale
        self.mental_restore_spin = QSpinBox()
        self.mental_restore_spin.setRange(0, 100)
        self.mental_restore_spin.setValue(int(self.item_data.get('mental_restore', 0)))
        restore_layout.addRow("Restauration mentale:", self.mental_restore_spin)
        
        restore_group.setLayout(restore_layout)
        main_layout.addWidget(restore_group)
        
        # Autres propriétés
        other_group = QGroupBox("Autres propriétés")
        other_layout = QFormLayout()
        
        # Est légal
        self.is_legal_check = QCheckBox()
        self.is_legal_check.setChecked(bool(int(self.item_data.get('is_legal', 1))))
        other_layout.addRow("Est légal:", self.is_legal_check)
        
        # Utilisations
        self.uses_spin = QSpinBox()
        self.uses_spin.setRange(1, 100)
        self.uses_spin.setValue(int(self.item_data.get('uses', 1)))
        other_layout.addRow("Utilisations:", self.uses_spin)
        
        other_group.setLayout(other_layout)
        main_layout.addWidget(other_group)
        
        # Boutons d'action
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def accept(self):
        """Valide et sauvegarde les données"""
        
        # Vérification des champs obligatoires
        if not self.name_edit.text().strip():
            logger.error("Le nom de l'aliment est obligatoire")
            return
        
        # Récupération des données
        data = {
            'id': self.id_edit.text(),
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'food_type': self.food_type_combo.currentText(),
            'price': self.price_spin.value(),
            'health_restore': self.health_restore_spin.value(),
            'energy_restore': self.energy_restore_spin.value(),
            'mental_restore': self.mental_restore_spin.value(),
            'is_legal': 1 if self.is_legal_check.isChecked() else 0,
            'rarity': self.rarity_combo.currentText(),
            'uses': self.uses_spin.value()
        }
        
        # Sauvegarde en base de données
        try:
            cursor = self.db.conn.cursor()
            
            # Vérifier si la table food_items existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='food_items'")
            if not cursor.fetchone():
                # Créer la table si elle n'existe pas
                cursor.execute('''
                CREATE TABLE food_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    food_type TEXT,
                    price INTEGER,
                    health_restore INTEGER,
                    energy_restore INTEGER,
                    mental_restore INTEGER,
                    is_legal INTEGER DEFAULT 1,
                    rarity TEXT DEFAULT 'COMMON',
                    uses INTEGER DEFAULT 1
                )
                ''')
                logger.info("Table food_items créée avec succès")
            
            if self.editing_mode:
                # Mise à jour d'un aliment existant
                placeholders = ', '.join([f"{k} = ?" for k in data.keys() if k != 'id'])
                values = [data[k] for k in data.keys() if k != 'id']
                values.append(data['id'])
                
                query = f"UPDATE food_items SET {placeholders} WHERE id = ?"
                cursor.execute(query, values)
                logger.info(f"Aliment {data['id']} mis à jour")
            else:
                # Création d'un nouvel aliment
                placeholders = ', '.join(['?'] * len(data))
                columns = ', '.join(data.keys())
                values = list(data.values())
                
                query = f"INSERT INTO food_items ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)
                logger.info(f"Nouvel aliment {data['id']} créé")
            
            self.db.conn.commit()
            super().accept()
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'aliment: {e}")
