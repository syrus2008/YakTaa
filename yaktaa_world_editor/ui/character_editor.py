#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur de personnages pour l'éditeur de monde YakTaa
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

from .combat_attributes_editor import CombatAttributesEditor

logger = logging.getLogger(__name__)

class CharacterEditor(QDialog):
    """Boîte de dialogue pour l'édition des personnages"""
    
    def __init__(self, db, world_id, character_id=None, location_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.character_id = character_id
        self.location_id = location_id  # Lieu où se trouve le personnage (optionnel)
        self.is_new = character_id is None
        
        self.init_ui()
        
        if not self.is_new:
            self.load_character_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Éditeur de personnage" if self.is_new else "Modifier le personnage")
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
        
        # Profession
        self.profession_combo = QComboBox()
        self.profession_combo.addItems([
            "Hacker", "Agent de sécurité", "Policier", "Corporatif", 
            "Technicien", "Médecin", "Journaliste", "Criminel", "Autre"
        ])
        self.profession_combo.setEditable(True)
        basic_layout.addRow("Profession:", self.profession_combo)
        
        # Faction
        self.faction_combo = QComboBox()
        self.faction_combo.addItems([
            "Gouvernement", "Corporation", "Syndicat", 
            "Hackers", "Criminels", "Indépendants", "Neutre"
        ])
        self.faction_combo.setEditable(True)
        basic_layout.addRow("Faction:", self.faction_combo)
        
        # Lieu
        self.location_combo = QComboBox()
        self.load_locations()
        basic_layout.addRow("Lieu:", self.location_combo)
        
        # Options du personnage
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.is_quest_giver_check = QCheckBox("Donneur de quêtes")
        options_layout.addWidget(self.is_quest_giver_check)
        
        self.is_vendor_check = QCheckBox("Marchand")
        options_layout.addWidget(self.is_vendor_check)
        
        self.is_hostile_check = QCheckBox("Hostile")
        options_layout.addWidget(self.is_hostile_check)
        
        basic_layout.addRow("", options_group)
        
        tabs.addTab(basic_tab, "Informations de base")
        
        # Onglet des compétences
        skills_tab = QWidget()
        skills_layout = QFormLayout(skills_tab)
        
        # Niveau de hacking
        self.hacking_spin = QSpinBox()
        self.hacking_spin.setMinimum(0)
        self.hacking_spin.setMaximum(10)
        self.hacking_spin.setValue(1)
        skills_layout.addRow("Niveau de hacking:", self.hacking_spin)
        
        # Niveau de combat
        self.combat_spin = QSpinBox()
        self.combat_spin.setMinimum(0)
        self.combat_spin.setMaximum(10)
        self.combat_spin.setValue(1)
        skills_layout.addRow("Niveau de combat:", self.combat_spin)
        
        # Charisme
        self.charisma_spin = QSpinBox()
        self.charisma_spin.setMinimum(0)
        self.charisma_spin.setMaximum(10)
        self.charisma_spin.setValue(1)
        skills_layout.addRow("Charisme:", self.charisma_spin)
        
        # Richesse
        self.wealth_spin = QSpinBox()
        self.wealth_spin.setMinimum(0)
        self.wealth_spin.setMaximum(10)
        self.wealth_spin.setValue(1)
        skills_layout.addRow("Richesse:", self.wealth_spin)
        
        tabs.addTab(skills_tab, "Compétences")
        
        # Onglet des attributs de combat
        combat_tab = QWidget()
        combat_layout = QVBoxLayout(combat_tab)
        
        # Ajouter l'éditeur d'attributs de combat
        self.combat_attributes_editor = CombatAttributesEditor()
        combat_layout.addWidget(self.combat_attributes_editor)
        
        tabs.addTab(combat_tab, "Combat")
        
        # Onglet de description
        description_tab = QWidget()
        description_layout = QVBoxLayout(description_tab)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez une description détaillée du personnage...")
        description_layout.addWidget(self.description_edit)
        
        tabs.addTab(description_tab, "Description")
        
        main_layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_character)
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
    
    def load_character_data(self):
        """Charge les données du personnage depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT name, profession, faction, location_id, hacking_level, combat_level,
               charisma, wealth, description, is_quest_giver, is_vendor, is_hostile,
               enemy_type, health, damage, accuracy, initiative, hostility,
               resistance_physical, resistance_energy, resistance_emp, resistance_biohazard,
               resistance_cyber, resistance_viral, resistance_nanite,
               ai_behavior, combat_style, special_abilities
        FROM characters
        WHERE id = ? AND world_id = ?
        """, (self.character_id, self.world_id))
        
        character = cursor.fetchone()
        
        if not character:
            QMessageBox.critical(self, "Erreur", f"Impossible de trouver le personnage avec l'ID {self.character_id}")
            self.reject()
            return
        
        # Remplir les champs
        self.name_edit.setText(character["name"])
        
        # Trouver l'index de la profession
        profession_index = self.profession_combo.findText(character["profession"])
        if profession_index >= 0:
            self.profession_combo.setCurrentIndex(profession_index)
        else:
            self.profession_combo.setEditText(character["profession"])
        
        # Trouver l'index de la faction
        faction_index = self.faction_combo.findText(character["faction"])
        if faction_index >= 0:
            self.faction_combo.setCurrentIndex(faction_index)
        else:
            self.faction_combo.setEditText(character["faction"])
        
        # Trouver l'index du lieu
        if character["location_id"]:
            for i in range(self.location_combo.count()):
                if self.location_combo.itemData(i) == character["location_id"]:
                    self.location_combo.setCurrentIndex(i)
                    break
        
        # Options
        self.is_quest_giver_check.setChecked(bool(character["is_quest_giver"]))
        self.is_vendor_check.setChecked(bool(character["is_vendor"]))
        self.is_hostile_check.setChecked(bool(character["is_hostile"]))
        
        # Compétences
        if character["hacking_level"] is not None:
            self.hacking_spin.setValue(character["hacking_level"])
        
        if character["combat_level"] is not None:
            self.combat_spin.setValue(character["combat_level"])
        
        if character["charisma"] is not None:
            self.charisma_spin.setValue(character["charisma"])
        
        if character["wealth"] is not None:
            self.wealth_spin.setValue(character["wealth"])
        
        # Description
        if character["description"]:
            self.description_edit.setText(character["description"])
            
        # Attributs de combat
        combat_attrs = {
            "enemy_type": character["enemy_type"] or "HUMAN",
            "health": character["health"] or 50,
            "damage": character["damage"] or 5,
            "accuracy": character["accuracy"] or 0.7,
            "initiative": character["initiative"] or 5,
            "hostility": character["hostility"] or 0,
            "resistance_physical": character["resistance_physical"] or 0,
            "resistance_energy": character["resistance_energy"] or 0,
            "resistance_emp": character["resistance_emp"] or 0,
            "resistance_biohazard": character["resistance_biohazard"] or 0,
            "resistance_cyber": character["resistance_cyber"] or 0,
            "resistance_viral": character["resistance_viral"] or 0,
            "resistance_nanite": character["resistance_nanite"] or 0,
            "ai_behavior": character["ai_behavior"] or "defensive",
            "combat_style": character["combat_style"] or "balanced",
            "special_abilities": character["special_abilities"] or ""
        }
        
        self.combat_attributes_editor.set_all_values(combat_attrs)
    
    def save_character(self):
        """Sauvegarde les données du personnage dans la base de données"""
        
        # Récupérer les valeurs
        name = self.name_edit.text()
        profession = self.profession_combo.currentText()
        faction = self.faction_combo.currentText()
        
        location_id = None
        if self.location_combo.currentIndex() >= 0:
            location_id = self.location_combo.currentData()
        
        is_quest_giver = 1 if self.is_quest_giver_check.isChecked() else 0
        is_vendor = 1 if self.is_vendor_check.isChecked() else 0
        is_hostile = 1 if self.is_hostile_check.isChecked() else 0
        
        hacking_level = self.hacking_spin.value()
        combat_level = self.combat_spin.value()
        charisma = self.charisma_spin.value()
        wealth = self.wealth_spin.value()
        description = self.description_edit.toPlainText()
        
        # Récupérer les attributs de combat
        combat_attrs = self.combat_attributes_editor.get_all_values()
        
        # Valider les données
        if not name:
            QMessageBox.warning(self, "Validation", "Le nom du personnage est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        if self.is_new:
            # Générer un nouvel ID
            self.character_id = str(uuid.uuid4())
            
            # Insérer le nouveau personnage
            cursor.execute("""
            INSERT INTO characters (
                id, world_id, name, profession, faction, location_id,
                hacking_level, combat_level, charisma, wealth, description,
                is_quest_giver, is_vendor, is_hostile,
                enemy_type, health, damage, accuracy, initiative, hostility,
                resistance_physical, resistance_energy, resistance_emp, resistance_biohazard,
                resistance_cyber, resistance_viral, resistance_nanite,
                ai_behavior, combat_style, special_abilities
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.character_id, self.world_id, name, profession, faction, location_id,
                hacking_level, combat_level, charisma, wealth, description,
                is_quest_giver, is_vendor, is_hostile,
                combat_attrs["enemy_type"], combat_attrs["health"], combat_attrs["damage"],
                combat_attrs["accuracy"], combat_attrs["initiative"], combat_attrs["hostility"],
                combat_attrs["resistance_physical"], combat_attrs["resistance_energy"],
                combat_attrs["resistance_emp"], combat_attrs["resistance_biohazard"],
                combat_attrs["resistance_cyber"], combat_attrs["resistance_viral"],
                combat_attrs["resistance_nanite"], combat_attrs["ai_behavior"],
                combat_attrs["combat_style"], combat_attrs["special_abilities"]
            ))
        else:
            # Mettre à jour le personnage existant
            cursor.execute("""
            UPDATE characters
            SET name = ?, profession = ?, faction = ?, location_id = ?,
                hacking_level = ?, combat_level = ?, charisma = ?, wealth = ?, description = ?,
                is_quest_giver = ?, is_vendor = ?, is_hostile = ?,
                enemy_type = ?, health = ?, damage = ?, accuracy = ?, initiative = ?, hostility = ?,
                resistance_physical = ?, resistance_energy = ?, resistance_emp = ?, resistance_biohazard = ?,
                resistance_cyber = ?, resistance_viral = ?, resistance_nanite = ?,
                ai_behavior = ?, combat_style = ?, special_abilities = ?
            WHERE id = ? AND world_id = ?
            """, (
                name, profession, faction, location_id,
                hacking_level, combat_level, charisma, wealth, description,
                is_quest_giver, is_vendor, is_hostile,
                combat_attrs["enemy_type"], combat_attrs["health"], combat_attrs["damage"],
                combat_attrs["accuracy"], combat_attrs["initiative"], combat_attrs["hostility"],
                combat_attrs["resistance_physical"], combat_attrs["resistance_energy"],
                combat_attrs["resistance_emp"], combat_attrs["resistance_biohazard"],
                combat_attrs["resistance_cyber"], combat_attrs["resistance_viral"],
                combat_attrs["resistance_nanite"], combat_attrs["ai_behavior"],
                combat_attrs["combat_style"], combat_attrs["special_abilities"],
                self.character_id, self.world_id
            ))
        
        self.db.conn.commit()
        
        # Accepter la boîte de dialogue
        self.accept()
