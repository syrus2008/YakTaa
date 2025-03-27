#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module pour l'onglet des options de combat dans le générateur de monde
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QSpinBox, QComboBox, QSlider, QGroupBox, 
    QCheckBox, QPushButton, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

class CombatOptionsTab(QWidget):
    """
    Onglet des options de combat pour le générateur de monde
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialiser l'interface utilisateur
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Groupe des types d'ennemis
        enemy_types_group = QGroupBox("Distribution des types d'ennemis")
        enemy_types_layout = QVBoxLayout(enemy_types_group)
        
        # Formulaire pour les sliders des types d'ennemis
        form_layout = QFormLayout()
        
        # Créer les sliders pour chaque type d'ennemi
        self.enemy_type_sliders = {}
        
        enemy_types = {
            "HUMAN": "Humains",
            "GUARD": "Gardes",
            "CYBORG": "Cyborgs",
            "DRONE": "Drones",
            "ROBOT": "Robots",
            "NETRUNNER": "Netrunners",
            "MILITECH": "Militech",
            "BEAST": "Bêtes"
        }
        
        default_values = {
            "HUMAN": 40,
            "GUARD": 20,
            "CYBORG": 15,
            "DRONE": 10,
            "ROBOT": 5,
            "NETRUNNER": 5,
            "MILITECH": 3,
            "BEAST": 2
        }
        
        for enemy_type, label in enemy_types.items():
            # Créer un layout horizontal pour le slider et la valeur
            slider_layout = QHBoxLayout()
            
            # Créer le slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(default_values.get(enemy_type, 10))
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)
            
            # Créer le label pour afficher la valeur
            value_label = QLabel(f"{slider.value()}%")
            
            # Connecter le changement de valeur du slider
            slider.valueChanged.connect(lambda val, lbl=value_label: lbl.setText(f"{val}%"))
            
            # Ajouter le slider et le label à leur layout
            slider_layout.addWidget(slider)
            slider_layout.addWidget(value_label)
            
            # Ajouter au formulaire
            form_layout.addRow(f"{label}:", slider_layout)
            
            # Stocker le slider dans le dictionnaire
            self.enemy_type_sliders[enemy_type] = slider
        
        enemy_types_layout.addLayout(form_layout)
        
        # Bouton pour équilibrer automatiquement
        balance_button = QPushButton("Équilibrer automatiquement")
        balance_button.clicked.connect(self.balance_enemy_types)
        enemy_types_layout.addWidget(balance_button)
        
        main_layout.addWidget(enemy_types_group)
        
        # Groupe des paramètres de combat généraux
        combat_params_group = QGroupBox("Paramètres de combat généraux")
        combat_params_layout = QFormLayout(combat_params_group)
        
        # Pourcentage de personnages hostiles
        self.hostile_percentage_slider = QSlider(Qt.Orientation.Horizontal)
        self.hostile_percentage_slider.setMinimum(0)
        self.hostile_percentage_slider.setMaximum(100)
        self.hostile_percentage_slider.setValue(30)
        self.hostile_percentage_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hostile_percentage_slider.setTickInterval(10)
        
        hostile_slider_layout = QHBoxLayout()
        hostile_slider_layout.addWidget(self.hostile_percentage_slider)
        
        self.hostile_percentage_label = QLabel(f"{self.hostile_percentage_slider.value()}%")
        hostile_slider_layout.addWidget(self.hostile_percentage_label)
        
        self.hostile_percentage_slider.valueChanged.connect(
            lambda val: self.hostile_percentage_label.setText(f"{val}%")
        )
        
        combat_params_layout.addRow("Personnages hostiles:", hostile_slider_layout)
        
        # Difficulté des combats
        self.combat_difficulty_spin = QSpinBox()
        self.combat_difficulty_spin.setMinimum(1)
        self.combat_difficulty_spin.setMaximum(5)
        self.combat_difficulty_spin.setValue(3)
        self.combat_difficulty_spin.setToolTip("Niveau de difficulté des combats (1-5)")
        
        combat_params_layout.addRow("Difficulté des combats:", self.combat_difficulty_spin)
        
        # Comportement AI par défaut
        self.default_ai_behavior_combo = QComboBox()
        self.default_ai_behavior_combo.addItems([
            "Équilibré",
            "Agressif",
            "Défensif",
            "Tactique",
            "Prudent",
            "Adaptatif"
        ])
        self.default_ai_behavior_combo.setCurrentIndex(0)
        
        combat_params_layout.addRow("Comportement AI par défaut:", self.default_ai_behavior_combo)
        
        main_layout.addWidget(combat_params_group)
        
        # Groupe des styles de combat
        combat_styles_group = QGroupBox("Styles de combat")
        combat_styles_layout = QVBoxLayout(combat_styles_group)
        
        self.combat_styles_list = QListWidget()
        self.combat_styles_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        styles = [
            ("Équilibré", True),
            ("Corps à corps", True),
            ("Distance", True),
            ("Furtif", False),
            ("Support", False),
            ("Tank", False)
        ]
        
        for style, selected in styles:
            item = QListWidgetItem(style)
            if selected:
                item.setSelected(True)
            self.combat_styles_list.addItem(item)
        
        combat_styles_layout.addWidget(self.combat_styles_list)
        
        main_layout.addWidget(combat_styles_group)
        
        # Groupe des effets de statut
        status_effects_group = QGroupBox("Effets de statut")
        status_effects_layout = QFormLayout(status_effects_group)
        
        self.enable_status_effects_check = QCheckBox("Activer les effets de statut")
        self.enable_status_effects_check.setChecked(True)
        status_effects_layout.addRow("", self.enable_status_effects_check)
        
        self.dot_effects_check = QCheckBox("Inclure les effets de dégâts sur la durée")
        self.dot_effects_check.setChecked(True)
        status_effects_layout.addRow("", self.dot_effects_check)
        
        self.cc_effects_check = QCheckBox("Inclure les effets de contrôle")
        self.cc_effects_check.setChecked(True)
        status_effects_layout.addRow("", self.cc_effects_check)
        
        self.buff_effects_check = QCheckBox("Inclure les effets de renforcement")
        self.buff_effects_check.setChecked(True)
        status_effects_layout.addRow("", self.buff_effects_check)
        
        self.status_effects_complexity_spin = QSpinBox()
        self.status_effects_complexity_spin.setMinimum(1)
        self.status_effects_complexity_spin.setMaximum(5)
        self.status_effects_complexity_spin.setValue(3)
        self.status_effects_complexity_spin.setToolTip("Complexité des effets de statut (1-5)")
        status_effects_layout.addRow("Complexité des effets:", self.status_effects_complexity_spin)
        
        main_layout.addWidget(status_effects_group)
    
    def balance_enemy_types(self):
        """Équilibre automatiquement les types d'ennemis"""
        # Calculer la somme actuelle de tous les sliders
        total = sum(slider.value() for slider in self.enemy_type_sliders.values())
        
        if total == 0:
            # Si tous les sliders sont à 0, définir des valeurs équilibrées par défaut
            default_values = {
                "HUMAN": 40,
                "GUARD": 20,
                "CYBORG": 15,
                "DRONE": 10,
                "ROBOT": 5,
                "NETRUNNER": 5,
                "MILITECH": 3,
                "BEAST": 2
            }
            
            for enemy_type, slider in self.enemy_type_sliders.items():
                slider.setValue(default_values.get(enemy_type, 10))
        else:
            # Normaliser les valeurs actuelles pour qu'elles totalisent 100%
            scale_factor = 100.0 / total
            
            for slider in self.enemy_type_sliders.values():
                new_value = int(slider.value() * scale_factor)
                slider.setValue(new_value)
            
            # Ajuster pour s'assurer que le total est exactement 100%
            remaining = 100 - sum(slider.value() for slider in self.enemy_type_sliders.values())
            
            if remaining != 0:
                # Ajouter le reste à la première valeur non nulle, ou à la première valeur si toutes sont nulles
                for slider in self.enemy_type_sliders.values():
                    if slider.value() > 0 or remaining > 0:
                        slider.setValue(slider.value() + remaining)
                        break
    
    def get_values(self):
        """
        Récupère toutes les valeurs configurées dans cet onglet
        
        Returns:
            dict: Dictionnaire contenant toutes les valeurs configurées
        """
        # Récupérer les distributions d'ennemis
        enemy_type_distribution = {
            enemy_type: slider.value() 
            for enemy_type, slider in self.enemy_type_sliders.items()
        }
        
        # Récupérer les styles de combat sélectionnés
        selected_combat_styles = [
            item.text() 
            for i in range(self.combat_styles_list.count()) 
            if self.combat_styles_list.item(i).isSelected()
        ]
        
        # Récupérer les autres paramètres
        return {
            "enemy_type_distribution": enemy_type_distribution,
            "hostile_character_percentage": self.hostile_percentage_slider.value(),
            "combat_difficulty": self.combat_difficulty_spin.value(),
            "default_ai_behavior": self.default_ai_behavior_combo.currentText(),
            "combat_styles": selected_combat_styles,
            "enable_status_effects": self.enable_status_effects_check.isChecked(),
            "dot_effects_enabled": self.dot_effects_check.isChecked(),
            "cc_effects_enabled": self.cc_effects_check.isChecked(),
            "buff_effects_enabled": self.buff_effects_check.isChecked(),
            "status_effects_complexity": self.status_effects_complexity_spin.value()
        }
