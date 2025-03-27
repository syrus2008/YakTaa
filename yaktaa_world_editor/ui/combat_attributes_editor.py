#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module pour l'édition des attributs de combat d'un personnage
"""

import logging
from enum import Enum, auto
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QDoubleSpinBox, QSlider,
    QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

logger = logging.getLogger(__name__)

# Définition des types d'ennemis, correspondant à ceux définis dans combat/enemy.py
class EnemyType(Enum):
    """Types d'ennemis disponibles dans le jeu"""
    HUMAN = auto()       # Humain non augmenté
    GUARD = auto()       # Garde de sécurité légèrement augmenté
    CYBORG = auto()      # Humain fortement augmenté
    DRONE = auto()       # Drone autonome
    ROBOT = auto()       # Robot militaire ou de sécurité
    NETRUNNER = auto()   # Hacker spécialisé dans la cyberguerre
    MILITECH = auto()    # Soldat équipé de technologie militaire avancée
    BEAST = auto()       # Créature mutante ou biomodifiée

class CombatAttributesEditor(QWidget):
    """Widget pour l'édition des attributs de combat d'un personnage"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Valeurs par défaut
        self.enemy_type = "HUMAN"
        self.health = 50
        self.damage = 5
        self.accuracy = 0.7
        self.initiative = 5
        
        # Résistances
        self.resistance_physical = 0
        self.resistance_energy = 0
        self.resistance_emp = 0
        self.resistance_biohazard = 0
        self.resistance_cyber = 0
        self.resistance_viral = 0
        self.resistance_nanite = 0
        
        # Comportement
        self.hostility = 0
        self.ai_behavior = "defensive"
        self.combat_style = "balanced"
        self.special_abilities = ""
        
        # Initialiser l'interface
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Secteur 1: Type d'ennemi et attributs de base
        base_group = QGroupBox("Caractéristiques de base")
        base_layout = QFormLayout(base_group)
        
        # Type d'ennemi
        self.enemy_type_combo = QComboBox()
        for enemy_type in EnemyType:
            self.enemy_type_combo.addItem(enemy_type.name, enemy_type.name)
        self.enemy_type_combo.currentIndexChanged.connect(self._on_enemy_type_changed)
        base_layout.addRow("Type d'ennemi:", self.enemy_type_combo)
        
        # Points de vie
        self.health_spin = QSpinBox()
        self.health_spin.setMinimum(10)
        self.health_spin.setMaximum(2000)
        self.health_spin.setValue(self.health)
        self.health_spin.setSingleStep(10)
        base_layout.addRow("Points de vie:", self.health_spin)
        
        # Dégâts
        self.damage_spin = QSpinBox()
        self.damage_spin.setMinimum(1)
        self.damage_spin.setMaximum(100)
        self.damage_spin.setValue(self.damage)
        base_layout.addRow("Dégâts de base:", self.damage_spin)
        
        # Précision
        self.accuracy_spin = QDoubleSpinBox()
        self.accuracy_spin.setMinimum(0.1)
        self.accuracy_spin.setMaximum(1.0)
        self.accuracy_spin.setValue(self.accuracy)
        self.accuracy_spin.setSingleStep(0.05)
        self.accuracy_spin.setDecimals(2)
        base_layout.addRow("Précision (0.1-1.0):", self.accuracy_spin)
        
        # Initiative
        self.initiative_spin = QSpinBox()
        self.initiative_spin.setMinimum(1)
        self.initiative_spin.setMaximum(20)
        self.initiative_spin.setValue(self.initiative)
        base_layout.addRow("Initiative:", self.initiative_spin)
        
        # Niveau d'hostilité
        self.hostility_spin = QSpinBox()
        self.hostility_spin.setMinimum(0)
        self.hostility_spin.setMaximum(100)
        self.hostility_spin.setValue(self.hostility)
        base_layout.addRow("Hostilité (0-100):", self.hostility_spin)
        
        main_layout.addWidget(base_group)
        
        # Secteur 2: Résistances
        resistances_group = QGroupBox("Résistances aux dégâts")
        resistances_layout = QFormLayout(resistances_group)
        
        # Résistance physique
        self.resistance_physical_spin = QSpinBox()
        self.resistance_physical_spin.setMinimum(0)
        self.resistance_physical_spin.setMaximum(80)  # Max 80% de résistance
        self.resistance_physical_spin.setValue(self.resistance_physical)
        self.resistance_physical_spin.setSuffix("%")
        resistances_layout.addRow("Résistance physique:", self.resistance_physical_spin)
        
        # Résistance énergétique
        self.resistance_energy_spin = QSpinBox()
        self.resistance_energy_spin.setMinimum(0)
        self.resistance_energy_spin.setMaximum(80)
        self.resistance_energy_spin.setValue(self.resistance_energy)
        self.resistance_energy_spin.setSuffix("%")
        resistances_layout.addRow("Résistance énergétique:", self.resistance_energy_spin)
        
        # Résistance EMP
        self.resistance_emp_spin = QSpinBox()
        self.resistance_emp_spin.setMinimum(0)
        self.resistance_emp_spin.setMaximum(80)
        self.resistance_emp_spin.setValue(self.resistance_emp)
        self.resistance_emp_spin.setSuffix("%")
        resistances_layout.addRow("Résistance EMP:", self.resistance_emp_spin)
        
        # Résistance biohazard
        self.resistance_biohazard_spin = QSpinBox()
        self.resistance_biohazard_spin.setMinimum(0)
        self.resistance_biohazard_spin.setMaximum(80)
        self.resistance_biohazard_spin.setValue(self.resistance_biohazard)
        self.resistance_biohazard_spin.setSuffix("%")
        resistances_layout.addRow("Résistance biohazard:", self.resistance_biohazard_spin)
        
        # Résistance cyber
        self.resistance_cyber_spin = QSpinBox()
        self.resistance_cyber_spin.setMinimum(0)
        self.resistance_cyber_spin.setMaximum(80)
        self.resistance_cyber_spin.setValue(self.resistance_cyber)
        self.resistance_cyber_spin.setSuffix("%")
        resistances_layout.addRow("Résistance cyber:", self.resistance_cyber_spin)
        
        # Résistance virale
        self.resistance_viral_spin = QSpinBox()
        self.resistance_viral_spin.setMinimum(0)
        self.resistance_viral_spin.setMaximum(80)
        self.resistance_viral_spin.setValue(self.resistance_viral)
        self.resistance_viral_spin.setSuffix("%")
        resistances_layout.addRow("Résistance virale:", self.resistance_viral_spin)
        
        # Résistance nanite
        self.resistance_nanite_spin = QSpinBox()
        self.resistance_nanite_spin.setMinimum(0)
        self.resistance_nanite_spin.setMaximum(80)
        self.resistance_nanite_spin.setValue(self.resistance_nanite)
        self.resistance_nanite_spin.setSuffix("%")
        resistances_layout.addRow("Résistance nanite:", self.resistance_nanite_spin)
        
        main_layout.addWidget(resistances_group)
        
        # Secteur 3: Comportement de combat
        behavior_group = QGroupBox("Comportement de combat")
        behavior_layout = QFormLayout(behavior_group)
        
        # Comportement IA
        self.ai_behavior_combo = QComboBox()
        self.ai_behavior_combo.addItems([
            "defensive", "offensive", "cautious", "aggressive", "tactical", "random"
        ])
        self.ai_behavior_combo.setCurrentText(self.ai_behavior)
        behavior_layout.addRow("Comportement IA:", self.ai_behavior_combo)
        
        # Style de combat
        self.combat_style_combo = QComboBox()
        self.combat_style_combo.addItems([
            "balanced", "ranged", "melee", "stealth", "tank", "support"
        ])
        self.combat_style_combo.setCurrentText(self.combat_style)
        behavior_layout.addRow("Style de combat:", self.combat_style_combo)
        
        # Capacités spéciales
        self.special_abilities_edit = QLineEdit()
        self.special_abilities_edit.setText(self.special_abilities)
        self.special_abilities_edit.setPlaceholderText("Ex: regeneration,emp_burst,stealth (séparées par des virgules)")
        behavior_layout.addRow("Capacités spéciales:", self.special_abilities_edit)
        
        main_layout.addWidget(behavior_group)
        
        # Prérégler en fonction du type d'ennemi
        self._on_enemy_type_changed(0)
    
    def _on_enemy_type_changed(self, index):
        """Met à jour les valeurs par défaut en fonction du type d'ennemi sélectionné"""
        enemy_type = self.enemy_type_combo.currentData()
        
        # Préréglages par type d'ennemi
        if enemy_type == "HUMAN":
            self.health_spin.setValue(50)
            self.damage_spin.setValue(5)
            self.accuracy_spin.setValue(0.7)
            self.initiative_spin.setValue(5)
            self.resistance_physical_spin.setValue(0)
            self.resistance_energy_spin.setValue(0)
            self.resistance_emp_spin.setValue(0)
            self.resistance_cyber_spin.setValue(10)
            
        elif enemy_type == "GUARD":
            self.health_spin.setValue(80)
            self.damage_spin.setValue(8)
            self.accuracy_spin.setValue(0.75)
            self.initiative_spin.setValue(7)
            self.resistance_physical_spin.setValue(20)
            self.resistance_energy_spin.setValue(10)
            self.resistance_emp_spin.setValue(10)
            self.resistance_cyber_spin.setValue(20)
            
        elif enemy_type == "CYBORG":
            self.health_spin.setValue(120)
            self.damage_spin.setValue(12)
            self.accuracy_spin.setValue(0.8)
            self.initiative_spin.setValue(8)
            self.resistance_physical_spin.setValue(30)
            self.resistance_energy_spin.setValue(20)
            self.resistance_emp_spin.setValue(0)  # Vulnérable aux EMP
            self.resistance_cyber_spin.setValue(40)
            
        elif enemy_type == "DRONE":
            self.health_spin.setValue(60)
            self.damage_spin.setValue(10)
            self.accuracy_spin.setValue(0.85)
            self.initiative_spin.setValue(10)
            self.resistance_physical_spin.setValue(20)
            self.resistance_energy_spin.setValue(10)
            self.resistance_emp_spin.setValue(0)  # Très vulnérable aux EMP
            self.resistance_cyber_spin.setValue(30)
            
        elif enemy_type == "ROBOT":
            self.health_spin.setValue(150)
            self.damage_spin.setValue(15)
            self.accuracy_spin.setValue(0.9)
            self.initiative_spin.setValue(6)
            self.resistance_physical_spin.setValue(40)
            self.resistance_energy_spin.setValue(30)
            self.resistance_emp_spin.setValue(0)  # Très vulnérable aux EMP
            self.resistance_cyber_spin.setValue(40)
            
        elif enemy_type == "NETRUNNER":
            self.health_spin.setValue(40)
            self.damage_spin.setValue(6)
            self.accuracy_spin.setValue(0.75)
            self.initiative_spin.setValue(8)
            self.resistance_physical_spin.setValue(0)
            self.resistance_energy_spin.setValue(10)
            self.resistance_emp_spin.setValue(20)
            self.resistance_cyber_spin.setValue(60)  # Forte résistance cyber
            
        elif enemy_type == "MILITECH":
            self.health_spin.setValue(140)
            self.damage_spin.setValue(16)
            self.accuracy_spin.setValue(0.85)
            self.initiative_spin.setValue(9)
            self.resistance_physical_spin.setValue(50)
            self.resistance_energy_spin.setValue(40)
            self.resistance_emp_spin.setValue(20)
            self.resistance_cyber_spin.setValue(30)
            
        elif enemy_type == "BEAST":
            self.health_spin.setValue(180)
            self.damage_spin.setValue(20)
            self.accuracy_spin.setValue(0.65)  # Moins précis
            self.initiative_spin.setValue(7)
            self.resistance_physical_spin.setValue(30)
            self.resistance_energy_spin.setValue(20)
            self.resistance_emp_spin.setValue(60)  # Résistant aux EMP
            self.resistance_cyber_spin.setValue(0)  # Vulnérable aux attaques cyber
    
    def get_all_values(self):
        """Récupère toutes les valeurs du widget"""
        return {
            "enemy_type": self.enemy_type_combo.currentData(),
            "health": self.health_spin.value(),
            "damage": self.damage_spin.value(),
            "accuracy": self.accuracy_spin.value(),
            "initiative": self.initiative_spin.value(),
            "hostility": self.hostility_spin.value(),
            "resistance_physical": self.resistance_physical_spin.value(),
            "resistance_energy": self.resistance_energy_spin.value(),
            "resistance_emp": self.resistance_emp_spin.value(),
            "resistance_biohazard": self.resistance_biohazard_spin.value(),
            "resistance_cyber": self.resistance_cyber_spin.value(),
            "resistance_viral": self.resistance_viral_spin.value(),
            "resistance_nanite": self.resistance_nanite_spin.value(),
            "ai_behavior": self.ai_behavior_combo.currentText(),
            "combat_style": self.combat_style_combo.currentText(),
            "special_abilities": self.special_abilities_edit.text()
        }
    
    def set_all_values(self, values):
        """Définit toutes les valeurs du widget"""
        if "enemy_type" in values:
            index = self.enemy_type_combo.findData(values["enemy_type"])
            if index >= 0:
                self.enemy_type_combo.setCurrentIndex(index)
        
        if "health" in values:
            self.health_spin.setValue(values["health"])
            
        if "damage" in values:
            self.damage_spin.setValue(values["damage"])
            
        if "accuracy" in values:
            self.accuracy_spin.setValue(values["accuracy"])
            
        if "initiative" in values:
            self.initiative_spin.setValue(values["initiative"])
            
        if "hostility" in values:
            self.hostility_spin.setValue(values["hostility"])
            
        if "resistance_physical" in values:
            self.resistance_physical_spin.setValue(values["resistance_physical"])
            
        if "resistance_energy" in values:
            self.resistance_energy_spin.setValue(values["resistance_energy"])
            
        if "resistance_emp" in values:
            self.resistance_emp_spin.setValue(values["resistance_emp"])
            
        if "resistance_biohazard" in values:
            self.resistance_biohazard_spin.setValue(values["resistance_biohazard"])
            
        if "resistance_cyber" in values:
            self.resistance_cyber_spin.setValue(values["resistance_cyber"])
            
        if "resistance_viral" in values:
            self.resistance_viral_spin.setValue(values["resistance_viral"])
            
        if "resistance_nanite" in values:
            self.resistance_nanite_spin.setValue(values["resistance_nanite"])
            
        if "ai_behavior" in values:
            index = self.ai_behavior_combo.findText(values["ai_behavior"])
            if index >= 0:
                self.ai_behavior_combo.setCurrentIndex(index)
            
        if "combat_style" in values:
            index = self.combat_style_combo.findText(values["combat_style"])
            if index >= 0:
                self.combat_style_combo.setCurrentIndex(index)
            
        if "special_abilities" in values:
            self.special_abilities_edit.setText(values["special_abilities"])
