#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la boîte de dialogue pour la génération de mondes
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QSlider, QGroupBox, 
    QCheckBox, QPushButton, QTabWidget, QComboBox, 
    QProgressBar, QMessageBox, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ui.combat_options_tab import CombatOptionsTab  # Importer le nouvel onglet

logger = logging.getLogger(__name__)

class WorldGeneratorThread(QThread):
    """Thread pour la génération de monde en arrière-plan"""
    
    # Signaux
    progress_updated = pyqtSignal(int, str)  # Pourcentage, message
    generation_complete = pyqtSignal(str)  # ID du monde généré
    generation_error = pyqtSignal(str)  # Message d'erreur
    
    def __init__(self, generator, params):
        super().__init__()
        
        self.generator = generator
        self.params = params
    
    def run(self):
        """Exécute la génération de monde"""
        
        try:
            # Mettre à jour le générateur avec les paramètres
            self.generator.name = self.params["name"]
            self.generator.author = self.params["author"]
            self.generator.complexity = self.params["complexity"]
            self.generator.city_count = self.params["city_count"]
            self.generator.special_location_count = self.params["special_location_count"]
            self.generator.character_count = self.params["character_count"]
            self.generator.device_count = self.params["device_count"]
            
            # Ajouter les nouveaux paramètres
            self.generator.implant_count = self.params.get("implant_count", 10)
            self.generator.vulnerability_count = self.params.get("vulnerability_count", 15)
            self.generator.network_count = self.params.get("network_count", 20)
            self.generator.implant_complexity = self.params.get("implant_complexity", 3)
            self.generator.vulnerability_complexity = self.params.get("vulnerability_complexity", 3)
            self.generator.network_complexity = self.params.get("network_complexity", 3)
            self.generator.shop_count = self.params.get("shop_count", 10)
            self.generator.shop_complexity = self.params.get("shop_complexity", 3)
            self.generator.shop_types = self.params.get("shop_types", {})
            self.generator.items_per_shop = self.params.get("items_per_shop", 20)
            self.generator.rare_items_percentage = self.params.get("rare_items_percentage", 20)
            self.generator.include_illegal_items = self.params.get("include_illegal_items", True)
            self.generator.include_featured_items = self.params.get("include_featured_items", True)
            self.generator.include_limited_time_items = self.params.get("include_limited_time_items", True)
            
            # Configurer les callbacks de progression
            def progress_callback(percent, message):
                self.progress_updated.emit(percent, message)
            
            self.generator.progress_callback = progress_callback
            
            # Générer le monde
            world_id = self.generator.generate_world()
            
            # Signaler la fin de la génération
            self.generation_complete.emit(world_id)
        
        except Exception as e:
            logger.exception("Erreur lors de la génération du monde")
            self.generation_error.emit(str(e))

class WorldGeneratorDialog(QDialog):
    """Boîte de dialogue pour la génération de mondes"""
    
    def __init__(self, generator):
        super().__init__()
        
        self.generator = generator
        self.generated_world_id = None
        self.generation_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet des paramètres de base
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Groupe des informations générales
        general_group = QGroupBox("Informations générales")
        general_form = QFormLayout(general_group)
        
        self.name_edit = QLineEdit("Nouveau Monde")
        general_form.addRow("Nom du monde:", self.name_edit)
        
        self.author_edit = QLineEdit("YakTaa Editor")
        general_form.addRow("Auteur:", self.author_edit)
        
        self.complexity_spin = QSpinBox()
        self.complexity_spin.setMinimum(1)
        self.complexity_spin.setMaximum(5)
        self.complexity_spin.setValue(3)
        self.complexity_spin.setToolTip("Niveau de complexité du monde (1-5)")
        general_form.addRow("Complexité:", self.complexity_spin)
        
        basic_layout.addWidget(general_group)
        
        # Groupe des paramètres de génération
        generation_group = QGroupBox("Paramètres de génération")
        generation_form = QFormLayout(generation_group)
        
        self.city_count_spin = QSpinBox()
        self.city_count_spin.setMinimum(1)
        self.city_count_spin.setMaximum(20)
        self.city_count_spin.setValue(5)
        generation_form.addRow("Nombre de villes:", self.city_count_spin)
        
        self.special_location_count_spin = QSpinBox()
        self.special_location_count_spin.setMinimum(0)
        self.special_location_count_spin.setMaximum(10)
        self.special_location_count_spin.setValue(3)
        generation_form.addRow("Lieux spéciaux:", self.special_location_count_spin)
        
        self.character_count_spin = QSpinBox()
        self.character_count_spin.setMinimum(5)
        self.character_count_spin.setMaximum(100)
        self.character_count_spin.setValue(20)
        generation_form.addRow("Personnages:", self.character_count_spin)
        
        self.device_count_spin = QSpinBox()
        self.device_count_spin.setMinimum(5)
        self.device_count_spin.setMaximum(200)
        self.device_count_spin.setValue(30)
        generation_form.addRow("Appareils:", self.device_count_spin)
        
        basic_layout.addWidget(generation_group)
        
        # Ajouter l'onglet de base
        tabs.addTab(basic_tab, "Paramètres de base")
        
        # Onglet des paramètres avancés
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Groupe des paramètres de sécurité
        security_group = QGroupBox("Paramètres de sécurité")
        security_layout = QVBoxLayout(security_group)
        
        security_label = QLabel("Niveau de sécurité moyen:")
        security_layout.addWidget(security_label)
        
        self.security_slider = QSlider(Qt.Orientation.Horizontal)
        self.security_slider.setMinimum(1)
        self.security_slider.setMaximum(5)
        self.security_slider.setValue(3)
        self.security_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.security_slider.setTickInterval(1)
        security_layout.addWidget(self.security_slider)
        
        security_value_layout = QHBoxLayout()
        security_value_layout.addWidget(QLabel("Faible (1)"))
        security_value_layout.addStretch()
        security_value_layout.addWidget(QLabel("Moyen (3)"))
        security_value_layout.addStretch()
        security_value_layout.addWidget(QLabel("Élevé (5)"))
        security_layout.addLayout(security_value_layout)
        
        advanced_layout.addWidget(security_group)
        
        # Groupe des options de génération
        options_group = QGroupBox("Options de génération")
        options_layout = QVBoxLayout(options_group)
        
        self.generate_missions_check = QCheckBox("Générer des missions")
        self.generate_missions_check.setChecked(True)
        options_layout.addWidget(self.generate_missions_check)
        
        self.generate_story_check = QCheckBox("Générer des éléments d'histoire")
        self.generate_story_check.setChecked(True)
        options_layout.addWidget(self.generate_story_check)
        
        self.balanced_world_check = QCheckBox("Équilibrer le monde automatiquement")
        self.balanced_world_check.setChecked(True)
        options_layout.addWidget(self.balanced_world_check)
        
        advanced_layout.addWidget(options_group)
        
        # Ajouter l'onglet avancé
        tabs.addTab(advanced_tab, "Paramètres avancés")
        
        # Nouvel onglet pour les nouvelles fonctionnalités
        new_features_tab = QWidget()
        new_features_layout = QVBoxLayout(new_features_tab)
        
        # Groupe des implants
        implants_group = QGroupBox("Implants")
        implants_layout = QFormLayout(implants_group)
        
        self.implant_count_spin = QSpinBox()
        self.implant_count_spin.setMinimum(0)
        self.implant_count_spin.setMaximum(50)
        self.implant_count_spin.setValue(10)
        self.implant_count_spin.setToolTip("Nombre d'implants à générer")
        implants_layout.addRow("Nombre d'implants:", self.implant_count_spin)
        
        self.implant_complexity_spin = QSpinBox()
        self.implant_complexity_spin.setMinimum(1)
        self.implant_complexity_spin.setMaximum(5)
        self.implant_complexity_spin.setValue(3)
        self.implant_complexity_spin.setToolTip("Niveau de complexité des implants (1-5)")
        implants_layout.addRow("Complexité des implants:", self.implant_complexity_spin)
        
        self.generate_rare_implants_check = QCheckBox("Générer des implants rares")
        self.generate_rare_implants_check.setChecked(True)
        self.generate_rare_implants_check.setToolTip("Inclure des implants rares et uniques")
        implants_layout.addRow("", self.generate_rare_implants_check)
        
        new_features_layout.addWidget(implants_group)
        
        # Groupe des vulnérabilités
        vulnerabilities_group = QGroupBox("Vulnérabilités")
        vulnerabilities_layout = QFormLayout(vulnerabilities_group)
        
        self.vulnerability_count_spin = QSpinBox()
        self.vulnerability_count_spin.setMinimum(0)
        self.vulnerability_count_spin.setMaximum(50)
        self.vulnerability_count_spin.setValue(15)
        self.vulnerability_count_spin.setToolTip("Nombre de vulnérabilités à générer")
        vulnerabilities_layout.addRow("Nombre de vulnérabilités:", self.vulnerability_count_spin)
        
        self.vulnerability_complexity_spin = QSpinBox()
        self.vulnerability_complexity_spin.setMinimum(1)
        self.vulnerability_complexity_spin.setMaximum(5)
        self.vulnerability_complexity_spin.setValue(3)
        self.vulnerability_complexity_spin.setToolTip("Niveau de complexité des vulnérabilités (1-5)")
        vulnerabilities_layout.addRow("Complexité des vulnérabilités:", self.vulnerability_complexity_spin)
        
        self.zero_day_vuln_check = QCheckBox("Inclure des vulnérabilités zero-day")
        self.zero_day_vuln_check.setChecked(False)
        self.zero_day_vuln_check.setToolTip("Inclure des vulnérabilités zero-day (très rares)")
        vulnerabilities_layout.addRow("", self.zero_day_vuln_check)
        
        new_features_layout.addWidget(vulnerabilities_group)
        
        # Groupe des réseaux
        networks_group = QGroupBox("Réseaux")
        networks_layout = QFormLayout(networks_group)
        
        self.network_count_spin = QSpinBox()
        self.network_count_spin.setMinimum(1)
        self.network_count_spin.setMaximum(50)
        self.network_count_spin.setValue(20)
        self.network_count_spin.setToolTip("Nombre de réseaux à générer")
        networks_layout.addRow("Nombre de réseaux:", self.network_count_spin)
        
        self.network_complexity_spin = QSpinBox()
        self.network_complexity_spin.setMinimum(1)
        self.network_complexity_spin.setMaximum(5)
        self.network_complexity_spin.setValue(3)
        self.network_complexity_spin.setToolTip("Niveau de complexité des réseaux (1-5)")
        networks_layout.addRow("Complexité des réseaux:", self.network_complexity_spin)
        
        self.network_type_combo = QComboBox()
        self.network_type_combo.addItems(["Tous", "WiFi", "LAN", "WAN", "VPN", "IoT"])
        self.network_type_combo.setCurrentIndex(0)
        networks_layout.addRow("Type de réseaux prioritaire:", self.network_type_combo)
        
        new_features_layout.addWidget(networks_group)
        
        # Ajouter l'onglet des nouvelles fonctionnalités
        tabs.addTab(new_features_tab, "Nouvelles fonctionnalités")
        
        # Onglet des magasins et articles
        shops_tab = QWidget()
        shops_layout = QVBoxLayout(shops_tab)
        
        # Groupe des magasins
        shops_group = QGroupBox("Magasins")
        shops_form = QFormLayout(shops_group)
        
        self.shop_count_spin = QSpinBox()
        self.shop_count_spin.setMinimum(0)
        self.shop_count_spin.setMaximum(50)
        self.shop_count_spin.setValue(10)
        self.shop_count_spin.setToolTip("Nombre de magasins à générer")
        shops_form.addRow("Nombre de magasins:", self.shop_count_spin)
        
        self.shop_complexity_spin = QSpinBox()
        self.shop_complexity_spin.setMinimum(1)
        self.shop_complexity_spin.setMaximum(5)
        self.shop_complexity_spin.setValue(3)
        self.shop_complexity_spin.setToolTip("Niveau de complexité des magasins (1-5)")
        shops_form.addRow("Complexité des magasins:", self.shop_complexity_spin)
        
        self.shop_types_group = QGroupBox("Types de magasins à inclure")
        shop_types_layout = QVBoxLayout(self.shop_types_group)
        
        self.shop_types = {
            "WEAPON": QCheckBox("Magasins d'armes"),
            "IMPLANT": QCheckBox("Cliniques d'implants"),
            "HARDWARE": QCheckBox("Magasins de matériel"),
            "SOFTWARE": QCheckBox("Magasins de logiciels"),
            "CLOTHING": QCheckBox("Magasins de vêtements"),
            "FOOD": QCheckBox("Magasins alimentaires"),
            "GENERAL": QCheckBox("Magasins généraux"),
            "BLACK_MARKET": QCheckBox("Marchés noirs")
        }
        
        # Cocher toutes les cases par défaut
        for shop_type, checkbox in self.shop_types.items():
            checkbox.setChecked(True)
            shop_types_layout.addWidget(checkbox)
        
        shops_form.addRow(self.shop_types_group)
        
        shops_layout.addWidget(shops_group)
        
        # Groupe des articles
        items_group = QGroupBox("Articles")
        items_form = QFormLayout(items_group)
        
        self.items_per_shop_spin = QSpinBox()
        self.items_per_shop_spin.setMinimum(5)
        self.items_per_shop_spin.setMaximum(100)
        self.items_per_shop_spin.setValue(20)
        self.items_per_shop_spin.setToolTip("Nombre moyen d'articles par magasin")
        items_form.addRow("Articles par magasin:", self.items_per_shop_spin)
        
        self.rare_items_slider = QSlider(Qt.Orientation.Horizontal)
        self.rare_items_slider.setMinimum(0)
        self.rare_items_slider.setMaximum(100)
        self.rare_items_slider.setValue(20)
        self.rare_items_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rare_items_slider.setTickInterval(10)
        self.rare_items_slider.setToolTip("Pourcentage d'articles rares")
        
        rare_items_layout = QVBoxLayout()
        rare_items_layout.addWidget(self.rare_items_slider)
        
        rare_items_value_layout = QHBoxLayout()
        rare_items_value_layout.addWidget(QLabel("0%"))
        rare_items_value_layout.addStretch()
        rare_items_value_layout.addWidget(QLabel("50%"))
        rare_items_value_layout.addStretch()
        rare_items_value_layout.addWidget(QLabel("100%"))
        rare_items_layout.addLayout(rare_items_value_layout)
        
        items_form.addRow("Articles rares:", rare_items_layout)
        
        self.illegal_items_check = QCheckBox("Inclure des articles illégaux")
        self.illegal_items_check.setChecked(True)
        self.illegal_items_check.setToolTip("Inclure des articles illégaux dans les magasins appropriés")
        items_form.addRow("", self.illegal_items_check)
        
        self.featured_items_check = QCheckBox("Inclure des articles mis en avant")
        self.featured_items_check.setChecked(True)
        self.featured_items_check.setToolTip("Certains articles seront mis en avant dans les magasins")
        items_form.addRow("", self.featured_items_check)
        
        self.limited_time_items_check = QCheckBox("Inclure des articles à durée limitée")
        self.limited_time_items_check.setChecked(True)
        self.limited_time_items_check.setToolTip("Certains articles seront disponibles pour une durée limitée")
        items_form.addRow("", self.limited_time_items_check)
        
        shops_layout.addWidget(items_group)
        
        # Ajouter l'onglet des magasins
        tabs.addTab(shops_tab, "Magasins et Articles")
        
        # Onglet des options de combat
        combat_tab = CombatOptionsTab()
        tabs.addTab(combat_tab, "Combat")
        
        main_layout.addWidget(tabs)
        
        # Barre de progression
        self.progress_group = QGroupBox("Progression")
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Prêt à générer")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(self.progress_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Générer")
        self.generate_button.clicked.connect(self.start_generation)
        buttons_layout.addWidget(self.generate_button)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Référence à l'onglet de combat pour récupérer les valeurs
        self.combat_options_tab = combat_tab

    def start_generation(self):
        """Démarre la génération du monde"""
        
        # Désactiver les contrôles
        self.generate_button.setEnabled(False)
        self.cancel_button.setText("Annuler la génération")
        
        # Préparer les paramètres
        params = {
            "name": self.name_edit.text(),
            "author": self.author_edit.text(),
            "complexity": self.complexity_spin.value(),
            "city_count": self.city_count_spin.value(),
            "special_location_count": self.special_location_count_spin.value(),
            "character_count": self.character_count_spin.value(),
            "device_count": self.device_count_spin.value(),
            "security_level": self.security_slider.value(),
            "generate_missions": self.generate_missions_check.isChecked(),
            "generate_story": self.generate_story_check.isChecked(),
            "balanced_world": self.balanced_world_check.isChecked(),
            # Nouveaux paramètres
            "implant_count": self.implant_count_spin.value(),
            "implant_complexity": self.implant_complexity_spin.value(),
            "generate_rare_implants": self.generate_rare_implants_check.isChecked(),
            "vulnerability_count": self.vulnerability_count_spin.value(),
            "vulnerability_complexity": self.vulnerability_complexity_spin.value(),
            "include_zero_day": self.zero_day_vuln_check.isChecked(),
            "network_count": self.network_count_spin.value(),
            "network_complexity": self.network_complexity_spin.value(),
            "network_type_priority": self.network_type_combo.currentText(),
            # Paramètres des magasins et articles
            "shop_count": self.shop_count_spin.value(),
            "shop_complexity": self.shop_complexity_spin.value(),
            "shop_types": {shop_type: checkbox.isChecked() for shop_type, checkbox in self.shop_types.items()},
            "items_per_shop": self.items_per_shop_spin.value(),
            "rare_items_percentage": self.rare_items_slider.value(),
            "include_illegal_items": self.illegal_items_check.isChecked(),
            "include_featured_items": self.featured_items_check.isChecked(),
            "include_limited_time_items": self.limited_time_items_check.isChecked(),
        }
        
        # Ajout sécurisé des paramètres de combat
        try:
            combat_params = self.combat_options_tab.get_values()
            params.update(combat_params)
        except Exception as e:
            import logging
            logging.warning(f"Impossible de charger les paramètres de combat: {str(e)}")
            # Valeurs par défaut pour les paramètres de combat
            params.update({
                "enemy_types_distribution": {"HUMAN": 30, "GUARD": 20, "CYBORG": 15, 
                                            "DRONE": 10, "ROBOT": 10, "NETRUNNER": 5,
                                            "MILITECH": 5, "BEAST": 5},
                "combat_difficulty": 3,
                "include_boss_enemies": False
            })
        
        # Créer et démarrer le thread de génération
        self.generation_thread = WorldGeneratorThread(self.generator, params)
        self.generation_thread.progress_updated.connect(self.update_progress)
        self.generation_thread.generation_complete.connect(self.on_generation_complete)
        self.generation_thread.generation_error.connect(self.on_generation_error)
        
        self.generation_thread.start()
    
    def update_progress(self, percent, message):
        """Met à jour la barre de progression"""
        
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
    
    def on_generation_complete(self, world_id):
        """Gère la fin de la génération"""
        
        self.generated_world_id = world_id
        self.status_label.setText("Génération terminée avec succès!")
        self.progress_bar.setValue(100)
        
        # Réactiver les contrôles
        self.generate_button.setEnabled(True)
        self.cancel_button.setText("Fermer")
        self.cancel_button.clicked.disconnect()  # Déconnecter le signal précédent
        self.cancel_button.clicked.connect(self.accept)  # Connecter à accept() au lieu de reject()
        
        # Afficher un message de succès
        QMessageBox.information(self, "Génération terminée", 
                               f"Le monde '{self.name_edit.text()}' a été généré avec succès!")
        
        # Accepter la boîte de dialogue
        self.accept()
    
    def on_generation_error(self, error_message):
        """Gère les erreurs de génération"""
        
        self.status_label.setText(f"Erreur: {error_message}")
        
        # Réactiver les contrôles
        self.generate_button.setEnabled(True)
        self.cancel_button.setText("Fermer")
        
        # Afficher un message d'erreur
        QMessageBox.critical(self, "Erreur de génération", 
                            f"Une erreur est survenue lors de la génération du monde:\n{error_message}")
    
    def reject(self):
        """Gère l'annulation de la boîte de dialogue"""
        
        # Si la génération est en cours, demander confirmation
        if self.generation_thread and self.generation_thread.isRunning():
            reply = QMessageBox.question(self, "Annuler la génération", 
                                        "La génération est en cours. Êtes-vous sûr de vouloir l'annuler?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Arrêter le thread
                self.generation_thread.terminate()
                self.generation_thread.wait()
                super().reject()
        else:
            super().reject()
