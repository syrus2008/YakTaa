#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9diteur d'objets pour l'u00e9diteur de monde YakTaa
"""

import logging
import uuid
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QDialogButtonBox,
    QTabWidget, QTextEdit, QGroupBox, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class ItemEditor(QDialog):
    """Dialogue d'u00e9dition d'objet (hardware, consumable, software)"""
    
    def __init__(self, db, world_id, item_id=None, item_type="hardware"):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.item_id = item_id
        self.item_type = item_type
        self.editing_mode = item_id is not None
        
        self.item_data = {}
        if self.editing_mode:
            self.load_item_data()
        
        self.init_ui()
        
        # Configuration du titre de la fenu00eatre
        type_names = {
            "hardware": "Hardware",
            "consumable": "Consommable",
            "software": "Software"
        }
        
        type_display = type_names.get(self.item_type, self.item_type.capitalize())
        self.setWindowTitle(f"Modifier {type_display}" if self.editing_mode else f"Nouveau {type_display}")
        self.resize(600, 500)
    
    def load_item_data(self):
        """Charge les donnu00e9es de l'objet depuis la base de donnu00e9es"""
        
        cursor = self.db.conn.cursor()
        
        if self.item_type == "hardware":
            cursor.execute('''
            SELECT *
            FROM hardware_items
            WHERE id = ?
            ''', (self.item_id,))
        elif self.item_type == "consumable":
            cursor.execute('''
            SELECT *
            FROM consumable_items
            WHERE id = ?
            ''', (self.item_id,))
        elif self.item_type == "software":
            cursor.execute('''
            SELECT *
            FROM software_items
            WHERE id = ?
            ''', (self.item_id,))
        
        item = cursor.fetchone()
        if item:
            self.item_data = dict(item)
        else:
            logger.error(f"Objet {self.item_id} de type {self.item_type} non trouvu00e9")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Contenu spu00e9cifique au type d'objet
        if self.item_type == "hardware":
            self.init_hardware_ui(main_layout)
        elif self.item_type == "consumable":
            self.init_consumable_ui(main_layout)
        elif self.item_type == "software":
            self.init_software_ui(main_layout)
        else:
            # Type d'objet non pris en charge
            main_layout.addWidget(QLabel(f"Type d'objet '{self.item_type}' non pris en charge"))
        
        # Boutons d'action
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def init_hardware_ui(self, main_layout):
        """Initialise l'interface pour les objets hardware"""
        
        # Onglets
        tab_widget = QTabWidget()
        
        # Onglet des informations gu00e9nu00e9rales
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Nom
        self.name_edit = QLineEdit()
        if self.editing_mode:
            self.name_edit.setText(self.item_data.get("name", ""))
        general_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        if self.editing_mode:
            self.description_edit.setText(self.item_data.get("description", ""))
        general_layout.addRow("Description:", self.description_edit)
        
        # Type de hardware
        self.hw_type_combo = QComboBox()
        hw_types = ["CPU", "GPU", "RAM", "Storage", "Network", "Input", "Output", 
                   "Security", "Power", "Cooling", "Cybernetic", "Specialist"]
        self.hw_type_combo.addItems(hw_types)
        if self.editing_mode and "hardware_type" in self.item_data:
            index = self.hw_type_combo.findText(self.item_data["hardware_type"])
            if index >= 0:
                self.hw_type_combo.setCurrentIndex(index)
        general_layout.addRow("Type:", self.hw_type_combo)
        
        # Qualitu00e9
        self.quality_combo = QComboBox()
        qualities = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Prototype"]
        self.quality_combo.addItems(qualities)
        if self.editing_mode and "quality" in self.item_data:
            index = self.quality_combo.findText(self.item_data["quality"])
            if index >= 0:
                self.quality_combo.setCurrentIndex(index)
        general_layout.addRow("Qualitu00e9:", self.quality_combo)
        
        # Niveau
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        if self.editing_mode:
            self.level_spin.setValue(self.item_data.get("level", 1))
        general_layout.addRow("Niveau:", self.level_spin)
        
        # Prix
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 1000000)
        self.price_spin.setSuffix(" cru00e9dits")
        if self.editing_mode:
            self.price_spin.setValue(self.item_data.get("price", 100))
        general_layout.addRow("Prix:", self.price_spin)
        
        # Lu00e9galitu00e9
        self.legal_check = QCheckBox("Objet lu00e9gal")
        if self.editing_mode:
            self.legal_check.setChecked(self.item_data.get("is_legal", True))
        else:
            self.legal_check.setChecked(True)
        general_layout.addRow("", self.legal_check)
        
        # Emplacement
        location_group = QGroupBox("Emplacement")
        location_layout = QFormLayout(location_group)
        
        self.location_type_combo = QComboBox()
        self.location_type_combo.addItems(["Monde", "Bu00e2timent", "Personnage", "Appareil"])
        self.location_type_combo.currentIndexChanged.connect(self.on_location_type_changed)
        location_layout.addRow("Type:", self.location_type_combo)
        
        self.location_combo = QComboBox()
        location_layout.addRow("Valeur:", self.location_combo)
        
        general_layout.addRow("", location_group)
        
        tab_widget.addTab(general_tab, "Gu00e9nu00e9ral")
        
        # Onglet des statistiques
        stats_tab = QWidget()
        stats_layout = QFormLayout(stats_tab)
        
        # Statistiques en JSON
        self.stats_edit = QTextEdit()
        if self.editing_mode and "stats" in self.item_data:
            try:
                stats = json.loads(self.item_data["stats"])
                self.stats_edit.setText(json.dumps(stats, indent=2))
            except Exception as e:
                logger.error(f"Erreur lors du chargement des statistiques: {e}")
                self.stats_edit.setText(self.item_data.get("stats", "{}"))
        else:
            # Statistiques par du00e9faut
            default_stats = {}
            self.stats_edit.setText(json.dumps(default_stats, indent=2))
        
        stats_layout.addWidget(QLabel("Statistiques (format JSON):"))
        stats_layout.addWidget(self.stats_edit)
        
        # Boutons pour la gu00e9nu00e9ration alu00e9atoire des statistiques
        random_stats_button = QPushButton("Gu00e9nu00e9rer des statistiques alu00e9atoires")
        random_stats_button.clicked.connect(self.generate_random_hw_stats)
        stats_layout.addWidget(random_stats_button)
        
        tab_widget.addTab(stats_tab, "Statistiques")
        
        main_layout.addWidget(tab_widget)
        
        # Initialiser l'emplacement en fonction des donnu00e9es existantes
        if self.editing_mode:
            self.init_location_from_data()
        
        # Remplir le combo d'emplacement par du00e9faut
        self.on_location_type_changed(0)
        
    def init_consumable_ui(self, main_layout):
        """Initialise l'interface pour les objets consommables"""
        
        # Onglets
        tab_widget = QTabWidget()
        
        # Onglet des informations gu00e9nu00e9rales
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Nom
        self.name_edit = QLineEdit()
        if self.editing_mode:
            self.name_edit.setText(self.item_data.get("name", ""))
        general_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        if self.editing_mode:
            self.description_edit.setText(self.item_data.get("description", ""))
        general_layout.addRow("Description:", self.description_edit)
        
        # Type de consommable
        self.con_type_combo = QComboBox()
        con_types = ["Stim", "Medkit", "Drug", "Food", "Drink", "Repair", "Hack", "Boost"]
        self.con_type_combo.addItems(con_types)
        if self.editing_mode and "item_type" in self.item_data:
            index = self.con_type_combo.findText(self.item_data["item_type"])
            if index >= 0:
                self.con_type_combo.setCurrentIndex(index)
        general_layout.addRow("Type:", self.con_type_combo)
        
        # Raretu00e9
        self.rarity_combo = QComboBox()
        rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        self.rarity_combo.addItems(rarities)
        if self.editing_mode and "rarity" in self.item_data:
            index = self.rarity_combo.findText(self.item_data["rarity"])
            if index >= 0:
                self.rarity_combo.setCurrentIndex(index)
        general_layout.addRow("Raretu00e9:", self.rarity_combo)
        
        # Duru00e9e d'effet
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)  # 1 min u00e0 24h
        self.duration_spin.setSuffix(" min")
        if self.editing_mode:
            self.duration_spin.setValue(self.item_data.get("duration", 15))
        general_layout.addRow("Duru00e9e:", self.duration_spin)
        
        # Prix
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 100000)
        self.price_spin.setSuffix(" cru00e9dits")
        if self.editing_mode:
            self.price_spin.setValue(self.item_data.get("price", 50))
        general_layout.addRow("Prix:", self.price_spin)
        
        # Lu00e9galitu00e9
        self.legal_check = QCheckBox("Objet lu00e9gal")
        if self.editing_mode:
            self.legal_check.setChecked(self.item_data.get("is_legal", True))
        else:
            self.legal_check.setChecked(True)
        general_layout.addRow("", self.legal_check)
        
        # Emplacement
        location_group = QGroupBox("Emplacement")
        location_layout = QFormLayout(location_group)
        
        self.location_type_combo = QComboBox()
        self.location_type_combo.addItems(["Monde", "Bu00e2timent", "Personnage", "Appareil"])
        self.location_type_combo.currentIndexChanged.connect(self.on_location_type_changed)
        location_layout.addRow("Type:", self.location_type_combo)
        
        self.location_combo = QComboBox()
        location_layout.addRow("Valeur:", self.location_combo)
        
        general_layout.addRow("", location_group)
        
        tab_widget.addTab(general_tab, "Gu00e9nu00e9ral")
        
        # Onglet des effets
        effects_tab = QWidget()
        effects_layout = QFormLayout(effects_tab)
        
        # Effets en JSON
        self.effects_edit = QTextEdit()
        if self.editing_mode and "effects" in self.item_data:
            try:
                effects = json.loads(self.item_data["effects"])
                self.effects_edit.setText(json.dumps(effects, indent=2))
            except Exception as e:
                logger.error(f"Erreur lors du chargement des effets: {e}")
                self.effects_edit.setText(self.item_data.get("effects", "{}"))
        else:
            # Effets par du00e9faut
            default_effects = {}
            self.effects_edit.setText(json.dumps(default_effects, indent=2))
        
        effects_layout.addWidget(QLabel("Effets (format JSON):"))
        effects_layout.addWidget(self.effects_edit)
        
        # Boutons pour la gu00e9nu00e9ration alu00e9atoire des effets
        random_effects_button = QPushButton("Gu00e9nu00e9rer des effets alu00e9atoires")
        random_effects_button.clicked.connect(self.generate_random_effects)
        effects_layout.addWidget(random_effects_button)
        
        tab_widget.addTab(effects_tab, "Effets")
        
        main_layout.addWidget(tab_widget)
        
        # Initialiser l'emplacement en fonction des donnu00e9es existantes
        if self.editing_mode:
            self.init_location_from_data()
        
        # Remplir le combo d'emplacement par du00e9faut
        self.on_location_type_changed(0)
    
    def init_software_ui(self, main_layout):
        """Initialise l'interface pour les objets software"""
        
        # Onglets
        tab_widget = QTabWidget()
        
        # Onglet des informations gu00e9nu00e9rales
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Nom
        self.name_edit = QLineEdit()
        if self.editing_mode:
            self.name_edit.setText(self.item_data.get("name", ""))
        general_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        if self.editing_mode:
            self.description_edit.setText(self.item_data.get("description", ""))
        general_layout.addRow("Description:", self.description_edit)
        
        # Type de software
        self.sw_type_combo = QComboBox()
        sw_types = ["OS", "Security", "Hacking", "Analysis", "Communication", 
                    "Database", "Mining", "Virus", "Utility", "Game"]
        self.sw_type_combo.addItems(sw_types)
        if self.editing_mode and "software_type" in self.item_data:
            index = self.sw_type_combo.findText(self.item_data["software_type"])
            if index >= 0:
                self.sw_type_combo.setCurrentIndex(index)
        general_layout.addRow("Type:", self.sw_type_combo)
        
        # Version
        self.version_edit = QLineEdit()
        if self.editing_mode:
            self.version_edit.setText(self.item_data.get("version", "1.0"))
        else:
            self.version_edit.setText("1.0")
        general_layout.addRow("Version:", self.version_edit)
        
        # Licence
        self.license_combo = QComboBox()
        license_types = ["Commercial", "Trial", "Shareware", "Freeware", "Open Source", "Cracked"]
        self.license_combo.addItems(license_types)
        if self.editing_mode and "license_type" in self.item_data:
            index = self.license_combo.findText(self.item_data["license_type"])
            if index >= 0:
                self.license_combo.setCurrentIndex(index)
        general_layout.addRow("Licence:", self.license_combo)
        
        # Prix
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 100000)
        self.price_spin.setSuffix(" cru00e9dits")
        if self.editing_mode:
            self.price_spin.setValue(self.item_data.get("price", 200))
        general_layout.addRow("Prix:", self.price_spin)
        
        # Lu00e9galitu00e9
        self.legal_check = QCheckBox("Objet lu00e9gal")
        if self.editing_mode:
            self.legal_check.setChecked(self.item_data.get("is_legal", True))
        else:
            self.legal_check.setChecked(True)
        general_layout.addRow("", self.legal_check)
        
        # Emplacement
        location_group = QGroupBox("Emplacement")
        location_layout = QFormLayout(location_group)
        
        self.location_type_combo = QComboBox()
        self.location_type_combo.addItems(["Monde", "Appareil", "Fichier"])
        self.location_type_combo.currentIndexChanged.connect(self.on_location_type_changed)
        location_layout.addRow("Type:", self.location_type_combo)
        
        self.location_combo = QComboBox()
        location_layout.addRow("Valeur:", self.location_combo)
        
        general_layout.addRow("", location_group)
        
        tab_widget.addTab(general_tab, "Gu00e9nu00e9ral")
        
        # Onglet des capacitu00e9s
        capabilities_tab = QWidget()
        capabilities_layout = QFormLayout(capabilities_tab)
        
        # Capacitu00e9s en JSON
        self.capabilities_edit = QTextEdit()
        if self.editing_mode and "capabilities" in self.item_data:
            try:
                capabilities = json.loads(self.item_data["capabilities"])
                self.capabilities_edit.setText(json.dumps(capabilities, indent=2))
            except Exception as e:
                logger.error(f"Erreur lors du chargement des capacitu00e9s: {e}")
                self.capabilities_edit.setText(self.item_data.get("capabilities", "{}"))
        else:
            # Capacitu00e9s par du00e9faut
            default_capabilities = {}
            self.capabilities_edit.setText(json.dumps(default_capabilities, indent=2))
        
        capabilities_layout.addWidget(QLabel("Capacitu00e9s (format JSON):"))
        capabilities_layout.addWidget(self.capabilities_edit)
        
        # Boutons pour la gu00e9nu00e9ration alu00e9atoire des capacitu00e9s
        random_capabilities_button = QPushButton("Gu00e9nu00e9rer des capacitu00e9s alu00e9atoires")
        random_capabilities_button.clicked.connect(self.generate_random_capabilities)
        capabilities_layout.addWidget(random_capabilities_button)
        
        tab_widget.addTab(capabilities_tab, "Capacitu00e9s")
        
        main_layout.addWidget(tab_widget)
        
        # Initialiser l'emplacement en fonction des donnu00e9es existantes
        if self.editing_mode:
            self.init_location_from_data()
        
        # Remplir le combo d'emplacement par du00e9faut
        self.on_location_type_changed(0)

    def init_location_from_data(self):
        """Initialise les contrôles d'emplacement en fonction des données existantes"""
        
        if self.item_type == "hardware":
            if "device_id" in self.item_data and self.item_data["device_id"]:
                self.location_type_combo.setCurrentIndex(3)  # Appareil
            elif "character_id" in self.item_data and self.item_data["character_id"]:
                self.location_type_combo.setCurrentIndex(2)  # Personnage
            elif "building_id" in self.item_data and self.item_data["building_id"]:
                self.location_type_combo.setCurrentIndex(1)  # Bâtiment
            else:
                self.location_type_combo.setCurrentIndex(0)  # Monde
                
        elif self.item_type == "consumable":
            if "device_id" in self.item_data and self.item_data["device_id"]:
                self.location_type_combo.setCurrentIndex(3)  # Appareil
            elif "character_id" in self.item_data and self.item_data["character_id"]:
                self.location_type_combo.setCurrentIndex(2)  # Personnage
            elif "building_id" in self.item_data and self.item_data["building_id"]:
                self.location_type_combo.setCurrentIndex(1)  # Bâtiment
            else:
                self.location_type_combo.setCurrentIndex(0)  # Monde
                
        elif self.item_type == "software":
            if "device_id" in self.item_data and self.item_data["device_id"]:
                self.location_type_combo.setCurrentIndex(1)  # Appareil
            elif "file_id" in self.item_data and self.item_data["file_id"]:
                self.location_type_combo.setCurrentIndex(2)  # Fichier
            else:
                self.location_type_combo.setCurrentIndex(0)  # Monde
    
    def on_location_type_changed(self, index):
        """Gère le changement de type d'emplacement"""
        
        self.location_combo.clear()
        
        if self.item_type in ("hardware", "consumable"):
            locations = {
                0: lambda: self.load_world(),         # Monde
                1: lambda: self.load_buildings(),     # Bâtiment
                2: lambda: self.load_characters(),    # Personnage
                3: lambda: self.load_devices()        # Appareil
            }
        elif self.item_type == "software":
            locations = {
                0: lambda: self.load_world(),         # Monde
                1: lambda: self.load_devices(),       # Appareil
                2: lambda: self.load_files()          # Fichier
            }
        else:
            return
        
        if index in locations:
            locations[index]()
            
    def load_world(self):
        """Charge l'option Monde"""
        self.location_combo.addItem("Monde", None)
        
    def load_buildings(self):
        """Charge la liste des bâtiments"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT b.id, b.name, l.name as location_name
        FROM buildings b
        LEFT JOIN locations l ON b.location_id = l.id
        WHERE b.world_id = ?
        ORDER BY b.name
        ''', (self.world_id,))
        
        buildings = cursor.fetchall()
        
        for building in buildings:
            display = f"{building['name']} ({building['location_name']})"
            self.location_combo.addItem(display, building["id"])
            
        # Sélectionner l'élément actuel si en mode édition
        if self.editing_mode and "building_id" in self.item_data and self.item_data["building_id"]:
            self.select_combo_item(self.location_combo, self.item_data["building_id"])
            
    def load_characters(self):
        """Charge la liste des personnages"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, profession
        FROM characters
        WHERE world_id = ?
        ORDER BY name
        ''', (self.world_id,))
        
        characters = cursor.fetchall()
        
        for character in characters:
            display = f"{character['name']} ({character['profession']})"
            self.location_combo.addItem(display, character["id"])
            
        # Sélectionner l'élément actuel si en mode édition
        if self.editing_mode and "character_id" in self.item_data and self.item_data["character_id"]:
            self.select_combo_item(self.location_combo, self.item_data["character_id"])
            
    def load_devices(self):
        """Charge la liste des appareils"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, device_type, os_type
        FROM devices
        WHERE world_id = ?
        ORDER BY name
        ''', (self.world_id,))
        
        devices = cursor.fetchall()
        
        for device in devices:
            display = f"{device['name']} ({device['device_type']}, {device['os_type']})"
            self.location_combo.addItem(display, device["id"])
            
        # Sélectionner l'élément actuel si en mode édition
        if self.editing_mode and "device_id" in self.item_data and self.item_data["device_id"]:
            self.select_combo_item(self.location_combo, self.item_data["device_id"])
            
    def load_files(self):
        """Charge la liste des fichiers"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT f.id, f.name, f.file_type, d.name as device_name
        FROM files f
        LEFT JOIN devices d ON f.device_id = d.id
        WHERE f.world_id = ?
        ORDER BY f.name
        ''', (self.world_id,))
        
        files = cursor.fetchall()
        
        for file in files:
            display = f"{file['name']} ({file['file_type']}) sur {file['device_name'] or 'inconnu'}"
            self.location_combo.addItem(display, file["id"])
            
        # Sélectionner l'élément actuel si en mode édition
        if self.editing_mode and "file_id" in self.item_data and self.item_data["file_id"]:
            self.select_combo_item(self.location_combo, self.item_data["file_id"])
            
    def select_combo_item(self, combo, item_id):
        """Sélectionne un élément dans un QComboBox par son ID"""
        for i in range(combo.count()):
            if combo.itemData(i) == item_id:
                combo.setCurrentIndex(i)
                break
                
    def generate_random_hw_stats(self):
        """Génère des statistiques aléatoires pour un objet hardware"""
        import random
        
        hw_type = self.hw_type_combo.currentText()
        quality = self.quality_combo.currentText()
        level = self.level_spin.value()
        
        # Facteurs de qualité
        quality_factors = {
            "Common": 1.0,
            "Uncommon": 1.5,
            "Rare": 2.0,
            "Epic": 3.0,
            "Legendary": 4.0,
            "Prototype": 5.0
        }
        
        # Stats de base par type
        base_stats = {
            "CPU": {
                "processing_power": 10 * level * quality_factors.get(quality, 1.0),
                "cores": min(32, max(1, int(level / 5) + random.randint(1, 4))),
                "clock_speed": (1.0 + level * 0.1) * quality_factors.get(quality, 1.0),
                "heat_generation": random.randint(5, 15) / quality_factors.get(quality, 1.0)
            },
            "GPU": {
                "rendering_power": 15 * level * quality_factors.get(quality, 1.0),
                "memory": min(32, max(1, int(level / 3) * 2)) * quality_factors.get(quality, 1.0),
                "hash_rate": level * 5 * quality_factors.get(quality, 1.0),
                "power_consumption": random.randint(10, 20) / quality_factors.get(quality, 1.0)
            },
            "RAM": {
                "capacity": min(256, max(4, level * 4)) * quality_factors.get(quality, 1.0),
                "speed": (1600 + level * 50) * quality_factors.get(quality, 1.0),
                "channels": min(8, max(1, int(level / 10) + 1)),
                "latency": random.randint(5, 15) / quality_factors.get(quality, 1.0)
            }
            # Autres types ajoutés selon le même principe
        }
        
        # Si le type n'est pas prédéfini, générer des stats génériques
        if hw_type not in base_stats:
            base_stats[hw_type] = {
                "level": level,
                "quality_factor": quality_factors.get(quality, 1.0),
                "efficiency": random.randint(70, 95) * quality_factors.get(quality, 1.0) / 100,
                "durability": level * quality_factors.get(quality, 1.0) * 10
            }
        
        # Ajout d'une variation aléatoire
        stats = base_stats[hw_type].copy()
        for key in stats:
            if isinstance(stats[key], (int, float)):
                variation = random.uniform(0.9, 1.1)  # +/- 10%
                stats[key] = round(stats[key] * variation, 2)
        
        # Afficher les stats générées
        self.stats_edit.setText(json.dumps(stats, indent=2))
        
    def generate_random_effects(self):
        """Génère des effets aléatoires pour un objet consommable"""
        import random
        
        con_type = self.con_type_combo.currentText()
        rarity = self.rarity_combo.currentText()
        
        # Facteurs de rareté
        rarity_factors = {
            "Common": 1.0,
            "Uncommon": 1.5,
            "Rare": 2.0,
            "Epic": 3.0,
            "Legendary": 4.0
        }
        
        # Effets de base par type
        base_effects = {
            "Stim": {
                "energy": 20 * rarity_factors.get(rarity, 1.0),
                "focus": 15 * rarity_factors.get(rarity, 1.0),
                "speed": 10 * rarity_factors.get(rarity, 1.0),
                "side_effects": random.randint(0, 3) if rarity != "Legendary" else 0
            },
            "Medkit": {
                "healing": 30 * rarity_factors.get(rarity, 1.0),
                "pain_relief": 25 * rarity_factors.get(rarity, 1.0),
                "infection_prevention": random.choice([True, False])
            },
            "Hack": {
                "bypass_bonus": 15 * rarity_factors.get(rarity, 1.0),
                "stealth_bonus": 10 * rarity_factors.get(rarity, 1.0),
                "duration_bonus": 5 * rarity_factors.get(rarity, 1.0)
            }
            # Autres types ajoutés selon le même principe
        }
        
        # Si le type n'est pas prédéfini, générer des effets génériques
        if con_type not in base_effects:
            base_effects[con_type] = {
                "potency": 25 * rarity_factors.get(rarity, 1.0),
                "duration_factor": rarity_factors.get(rarity, 1.0),
                "quality": random.randint(1, 5)
            }
        
        # Ajout d'une variation aléatoire
        effects = base_effects[con_type].copy()
        for key in effects:
            if isinstance(effects[key], (int, float)):
                variation = random.uniform(0.9, 1.1)  # +/- 10%
                effects[key] = round(effects[key] * variation, 2)
        
        # Afficher les effets générés
        self.effects_edit.setText(json.dumps(effects, indent=2))
        
    def generate_random_capabilities(self):
        """Génère des capacités aléatoires pour un objet software"""
        import random
        
        sw_type = self.sw_type_combo.currentText()
        license_type = self.license_combo.currentText()
        
        # Facteurs de licence
        license_factors = {
            "Cracked": 0.8,  # Moins stable
            "Trial": 0.6,   # Limité
            "Shareware": 0.7,
            "Freeware": 0.9,
            "Open Source": 1.0,
            "Commercial": 1.2  # Premium
        }
        
        # Capacités de base par type
        base_capabilities = {
            "Hacking": {
                "decryption_speed": 20 * license_factors.get(license_type, 1.0),
                "trace_avoidance": 15 * license_factors.get(license_type, 1.0),
                "backdoor_capability": random.choice([True, False]),
                "max_target_level": min(10, max(1, int(10 * license_factors.get(license_type, 1.0))))
            },
            "Security": {
                "firewall_strength": 25 * license_factors.get(license_type, 1.0),
                "intrusion_detection": 20 * license_factors.get(license_type, 1.0),
                "encryption_level": min(5, max(1, int(5 * license_factors.get(license_type, 1.0))))
            },
            "OS": {
                "stability": 90 * license_factors.get(license_type, 1.0),
                "multitasking": 15 * license_factors.get(license_type, 1.0),
                "compatibility": 80 * license_factors.get(license_type, 1.0),
                "security_patches": license_type != "Cracked"  # Les versions crackées n'ont pas de patches
            }
            # Autres types ajoutés selon le même principe
        }
        
        # Si le type n'est pas prédéfini, générer des capacités génériques
        if sw_type not in base_capabilities:
            base_capabilities[sw_type] = {
                "performance": 70 * license_factors.get(license_type, 1.0),
                "reliability": 80 * license_factors.get(license_type, 1.0),
                "resource_usage": 50 / license_factors.get(license_type, 1.0)  # Plus bas = meilleur
            }
        
        # Ajout d'une variation aléatoire
        capabilities = base_capabilities[sw_type].copy()
        for key in capabilities:
            if isinstance(capabilities[key], (int, float)):
                variation = random.uniform(0.9, 1.1)  # +/- 10%
                capabilities[key] = round(capabilities[key] * variation, 2)
        
        # Afficher les capacités générées
        self.capabilities_edit.setText(json.dumps(capabilities, indent=2))
    
    def get_location_data(self):
        """Récupère les données de localisation en fonction de l'emplacement sélectionné"""
        location_type_index = self.location_type_combo.currentIndex()
        location_id = self.location_combo.currentData()
        
        result = {
            "device_id": None,
            "character_id": None,
            "building_id": None,
            "file_id": None
        }
        
        if self.item_type in ("hardware", "consumable"):
            if location_type_index == 1:  # Bâtiment
                result["building_id"] = location_id
            elif location_type_index == 2:  # Personnage
                result["character_id"] = location_id
            elif location_type_index == 3:  # Appareil
                result["device_id"] = location_id
        elif self.item_type == "software":
            if location_type_index == 1:  # Appareil
                result["device_id"] = location_id
            elif location_type_index == 2:  # Fichier
                result["file_id"] = location_id
                
        return result
    
    def accept(self):
        """Enregistre les modifications à l'objet"""
        
        # Validation des données
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom de l'objet est obligatoire.")
            return
        
        try:
            # Récupérer les données JSON
            if self.item_type == "hardware" and hasattr(self, 'stats_edit'):
                stats_json = self.stats_edit.toPlainText()
                json.loads(stats_json)  # Vérifie que c'est un JSON valide
            elif self.item_type == "consumable" and hasattr(self, 'effects_edit'):
                effects_json = self.effects_edit.toPlainText()
                json.loads(effects_json)  # Vérifie que c'est un JSON valide
            elif self.item_type == "software" and hasattr(self, 'capabilities_edit'):
                capabilities_json = self.capabilities_edit.toPlainText()
                json.loads(capabilities_json)  # Vérifie que c'est un JSON valide
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Validation", "Format JSON invalide.")
            return
        
        cursor = self.db.conn.cursor()
        
        # Préparer les données communes
        common_data = {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "is_legal": self.legal_check.isChecked(),
            "price": self.price_spin.value(),
            "world_id": self.world_id
        }
        
        # Fusionner avec les données de localisation
        common_data.update(self.get_location_data())
        
        # Données spécifiques par type
        if self.item_type == "hardware":
            item_data = {
                "hardware_type": self.hw_type_combo.currentText(),
                "quality": self.quality_combo.currentText(),
                "level": self.level_spin.value(),
                "stats": self.stats_edit.toPlainText()
            }
        elif self.item_type == "consumable":
            item_data = {
                "item_type": self.con_type_combo.currentText(),
                "rarity": self.rarity_combo.currentText(),
                "duration": self.duration_spin.value(),
                "effects": self.effects_edit.toPlainText()
            }
        elif self.item_type == "software":
            item_data = {
                "software_type": self.sw_type_combo.currentText(),
                "version": self.version_edit.text(),
                "license_type": self.license_combo.currentText(),
                "capabilities": self.capabilities_edit.toPlainText()
            }
        else:
            item_data = {}
        
        # Fusionner toutes les données
        all_data = {**common_data, **item_data}
        
        # Déterminer la table en fonction du type d'objet
        table_name = {
            "hardware": "hardware_items",
            "consumable": "consumable_items",
            "software": "software_items"
        }.get(self.item_type)
        
        if self.editing_mode:
            # Mettre à jour un objet existant
            placeholders = ', '.join([f"{key} = ?" for key in all_data.keys()])
            values = list(all_data.values()) + [self.item_id]
            
            cursor.execute(f'''
            UPDATE {table_name}
            SET {placeholders}
            WHERE id = ?
            ''', values)
            
            logger.info(f"Objet {self.item_id} de type {self.item_type} mis à jour")
        else:
            # Créer un nouvel objet
            item_id = str(uuid.uuid4())
            all_data["id"] = item_id
            
            placeholders = ', '.join(['?'] * len(all_data))
            columns = ', '.join(all_data.keys())
            values = list(all_data.values())
            
            cursor.execute(f'''
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ''', values)
            
            self.item_id = item_id
            logger.info(f"Objet {item_id} de type {self.item_type} créé")
        
        self.db.conn.commit()
        super().accept()
