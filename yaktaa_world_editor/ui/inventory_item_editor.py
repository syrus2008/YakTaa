#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'édition d'articles d'inventaire pour l'éditeur de monde YakTaa
"""

import logging
import datetime
import json
import uuid
import random
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QDialogButtonBox,
    QDateEdit, QGroupBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QDate

logger = logging.getLogger(__name__)

class InventoryItemEditor(QDialog):
    """Dialogue d'édition d'article d'inventaire"""
    
    def __init__(self, db, shop_id, item_id=None):
        super().__init__()
        
        self.db = db
        self.shop_id = shop_id
        self.item_id = item_id
        self.editing_mode = item_id is not None
        self.shop_data = self.get_shop_data()
        
        self.item_data = {}
        if self.editing_mode:
            self.load_item_data()
        
        self.init_ui()
        self.setWindowTitle("Modifier l'article" if self.editing_mode else "Nouvel article")
        self.resize(500, 400)
    
    def get_shop_data(self):
        """Récupère les données du magasin"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, shop_type, is_legal FROM shops WHERE id = ?
        ''', (self.shop_id,))
        
        shop_data = cursor.fetchone()
        if not shop_data:
            logger.error(f"Magasin {self.shop_id} non trouvé")
            return {"id": self.shop_id, "name": "Inconnu", "shop_type": "general", "is_legal": 1}
        
        return shop_data
    
    def load_item_data(self):
        """Charge les données de l'article depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT * FROM shop_inventory WHERE id = ?
        ''', (self.item_id,))
        
        self.item_data = cursor.fetchone()
        
        if not self.item_data:
            logger.error(f"Article {self.item_id} non trouvé")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        main_layout = QVBoxLayout(self)
        
        # Afficher le type de magasin
        shop_info = QLabel(f"Magasin: {self.shop_data['name']} (Type: {self.shop_data['shop_type']})")
        main_layout.addWidget(shop_info)
        
        form_layout = QFormLayout()
        
        # Type d'article
        self.type_combo = QComboBox()
        self.populate_item_types()
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        if self.editing_mode and "item_type" in self.item_data:
            self.type_combo.setCurrentText(self.item_data["item_type"])
        form_layout.addRow("Type:", self.type_combo)
        
        # Sélection de l'item
        self.item_selector_layout = QHBoxLayout()
        self.item_id_edit = QLineEdit()
        if self.editing_mode and "item_id" in self.item_data:
            self.item_id_edit.setText(self.item_data["item_id"])
        self.item_selector_layout.addWidget(self.item_id_edit)
        
        self.select_item_btn = QPushButton("Générer...")
        self.select_item_btn.clicked.connect(self.generate_item_id)
        self.item_selector_layout.addWidget(self.select_item_btn)
        form_layout.addRow("ID de l'item:", self.item_selector_layout)
        
        # Quantité
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        if self.editing_mode and "quantity" in self.item_data:
            self.quantity_spin.setValue(self.item_data["quantity"])
        form_layout.addRow("Quantité:", self.quantity_spin)
        
        # Prix
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" ¥")
        if self.editing_mode and "price" in self.item_data:
            self.price_spin.setValue(self.item_data["price"])
        else:
            # Prix par défaut en fonction du type de magasin
            self.price_spin.setValue(self.get_default_price())
        form_layout.addRow("Prix:", self.price_spin)
        
        # Modificateur de prix
        self.price_mod_spin = QDoubleSpinBox()
        self.price_mod_spin.setRange(0.1, 10.0)
        self.price_mod_spin.setDecimals(2)
        self.price_mod_spin.setSingleStep(0.1)
        self.price_mod_spin.setValue(1.0)
        if self.editing_mode and "price_modifier" in self.item_data:
            self.price_mod_spin.setValue(self.item_data["price_modifier"])
        form_layout.addRow("Modificateur de prix:", self.price_mod_spin)
        
        # Mis en avant
        self.featured_check = QCheckBox()
        if self.editing_mode and "is_featured" in self.item_data:
            self.featured_check.setChecked(bool(self.item_data["is_featured"]))
        form_layout.addRow("Mis en avant:", self.featured_check)
        
        # Durée limitée
        self.limited_time_check = QCheckBox()
        self.limited_time_check.stateChanged.connect(self.toggle_expiry_date)
        if self.editing_mode and "is_limited_time" in self.item_data:
            self.limited_time_check.setChecked(bool(self.item_data["is_limited_time"]))
        form_layout.addRow("Durée limitée:", self.limited_time_check)
        
        # Date d'expiration
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addDays(30))  # Par défaut, 30 jours
        if self.editing_mode and "expiry_date" in self.item_data and self.item_data["expiry_date"]:
            try:
                expiry_date = datetime.datetime.fromisoformat(self.item_data["expiry_date"])
                self.expiry_date_edit.setDate(QDate(expiry_date.year, expiry_date.month, expiry_date.day))
            except (ValueError, TypeError):
                pass
        self.expiry_date_edit.setEnabled(self.limited_time_check.isChecked())
        form_layout.addRow("Date d'expiration:", self.expiry_date_edit)
        
        # Métadonnées
        self.metadata_edit = QLineEdit()
        if self.editing_mode and "metadata" in self.item_data:
            self.metadata_edit.setText(self.item_data["metadata"])
        else:
            self.metadata_edit.setText("{}")
        form_layout.addRow("Métadonnées:", self.metadata_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons d'action
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def populate_item_types(self):
        """Remplit la liste des types d'articles en fonction du type de magasin"""
        self.type_combo.clear()
        
        shop_type = self.shop_data["shop_type"].upper() if self.shop_data and "shop_type" in self.shop_data else "GENERAL"
        
        # Définir les types d'articles disponibles en fonction du type de magasin
        if shop_type == "HARDWARE":
            self.type_combo.addItems(["HARDWARE"])
        elif shop_type == "SOFTWARE" or shop_type == "DIGITAL_SERVICES":
            self.type_combo.addItems(["SOFTWARE"])
        elif shop_type == "WEAPONS":
            self.type_combo.addItems(["WEAPON"])
        elif shop_type == "IMPLANTS":
            self.type_combo.addItems(["IMPLANT"])
        elif shop_type == "CONSUMABLES":
            self.type_combo.addItems(["CONSUMABLE"])
        elif shop_type == "BLACK_MARKET":
            self.type_combo.addItems(["SOFTWARE", "WEAPON", "IMPLANT", "CONSUMABLE"])
        else:
            # Type de magasin général ou inconnu
            self.type_combo.addItems(["WEAPON", "ARMOR", "CONSUMABLE", "SOFTWARE", "HARDWARE", "IMPLANT", "MISC"])
    
    def on_type_changed(self, item_type):
        """Réagit au changement de type d'article"""
        # Mettre à jour le prix par défaut
        self.price_spin.setValue(self.get_default_price())
    
    def get_default_price(self):
        """Retourne un prix par défaut en fonction du type d'article et du magasin"""
        item_type = self.type_combo.currentText()
        is_legal = bool(self.shop_data["is_legal"]) if self.shop_data and "is_legal" in self.shop_data else True
        
        # Prix de base par type d'article
        base_prices = {
            "WEAPON": random.randint(500, 2000),
            "ARMOR": random.randint(300, 1500),
            "CONSUMABLE": random.randint(50, 300),
            "SOFTWARE": random.randint(200, 1000),
            "HARDWARE": random.randint(300, 1500),
            "IMPLANT": random.randint(1000, 5000),
            "MISC": random.randint(50, 500)
        }
        
        # Ajuster le prix en fonction de la légalité
        price = base_prices.get(item_type, 100)
        if not is_legal:
            # Les articles illégaux sont généralement plus chers
            price = int(price * 1.5)
        
        return price
    
    def generate_item_id(self):
        """Génère un ID d'article en fonction du type sélectionné"""
        item_type = self.type_combo.currentText()
        
        # Générer un ID unique pour le type d'article
        prefix = item_type.lower()[:3]  # Utiliser les 3 premières lettres du type
        unique_id = f"{prefix}_{uuid.uuid4().hex[:8]}"
        
        # Définir l'ID généré
        self.item_id_edit.setText(unique_id)
        
        # Générer des métadonnées de base
        metadata = self.generate_metadata(item_type)
        self.metadata_edit.setText(json.dumps(metadata))
        
        # Afficher un message de confirmation
        QMessageBox.information(self, "ID Généré", f"ID généré pour {item_type}: {unique_id}")
    
    def generate_metadata(self, item_type):
        """Génère des métadonnées pour l'article en fonction de son type"""
        metadata = {}
        
        if item_type == "WEAPON":
            weapon_types = ["Pistol", "Rifle", "Shotgun", "SMG", "Sniper", "Melee"]
            metadata = {
                "name": f"{random.choice(['Cyber', 'Quantum', 'Pulse', 'Nexus', 'Shadow'])} {random.choice(weapon_types)}",
                "damage": random.randint(10, 50),
                "accuracy": random.randint(60, 95),
                "range": random.randint(5, 100),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        elif item_type == "ARMOR":
            armor_types = ["Helmet", "Chest", "Gloves", "Boots", "Shield"]
            metadata = {
                "name": f"{random.choice(['Reinforced', 'Quantum', 'Nano', 'Cybernetic', 'Tactical'])} {random.choice(armor_types)}",
                "defense": random.randint(5, 30),
                "durability": random.randint(50, 200),
                "weight": random.randint(1, 10),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        elif item_type == "CONSUMABLE":
            consumable_types = ["Medkit", "Stimpack", "Antidote", "Energy Drink", "Food"]
            metadata = {
                "name": f"{random.choice(['Advanced', 'Quantum', 'Nano', 'Synthetic', 'Military'])} {random.choice(consumable_types)}",
                "effect": random.choice(["Healing", "Stamina", "Focus", "Strength", "Resistance"]),
                "potency": random.randint(10, 100),
                "duration": random.randint(30, 300),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        elif item_type == "SOFTWARE":
            software_types = ["Firewall", "Antivirus", "Hacking Tool", "Encryption", "OS"]
            metadata = {
                "name": f"{random.choice(['Quantum', 'Cyber', 'Neural', 'Nexus', 'Shadow'])} {random.choice(software_types)}",
                "version": f"{random.randint(1, 10)}.{random.randint(0, 9)}",
                "security_level": random.randint(1, 10),
                "compatibility": random.choice(["All", "Windows", "Linux", "Mac", "Custom"]),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        elif item_type == "HARDWARE":
            hardware_types = ["CPU", "RAM", "GPU", "HDD", "SSD", "Network Card"]
            metadata = {
                "name": f"{random.choice(['Quantum', 'Cyber', 'Neural', 'Nexus', 'Fusion'])} {random.choice(hardware_types)}",
                "performance": random.randint(1, 10),
                "power_consumption": random.randint(5, 100),
                "compatibility": random.choice(["All", "Gaming", "Server", "Mobile", "Custom"]),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        elif item_type == "IMPLANT":
            implant_types = ["Neural", "Ocular", "Skeletal", "Dermal", "Cardiac"]
            metadata = {
                "name": f"{random.choice(['Quantum', 'Cyber', 'Neural', 'Nexus', 'Bio'])} {random.choice(implant_types)} Implant",
                "effect": random.choice(["Strength", "Intelligence", "Perception", "Agility", "Endurance"]),
                "potency": random.randint(1, 10),
                "surgery_difficulty": random.randint(1, 10),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        else:  # MISC
            misc_types = ["Tool", "Gadget", "Component", "Collectible", "Key"]
            metadata = {
                "name": f"{random.choice(['Quantum', 'Cyber', 'Neural', 'Nexus', 'Tech'])} {random.choice(misc_types)}",
                "use": random.choice(["Utility", "Quest", "Crafting", "Trading", "Unknown"]),
                "rarity": random.choice(["Common", "Uncommon", "Rare", "Epic", "Legendary"])
            }
        
        return metadata
    
    def toggle_expiry_date(self, state):
        """Active ou désactive la date d'expiration en fonction de l'état de la case à cocher"""
        self.expiry_date_edit.setEnabled(state == Qt.CheckState.Checked)
    
    def get_item_data(self):
        """Récupère les données de l'article à partir des champs du formulaire"""
        
        data = {
            "shop_id": self.shop_id,
            "item_type": self.type_combo.currentText(),
            "item_id": self.item_id_edit.text(),
            "quantity": self.quantity_spin.value(),
            "price": self.price_spin.value(),
            "price_modifier": self.price_mod_spin.value(),
            "is_featured": self.featured_check.isChecked(),
            "is_limited_time": self.limited_time_check.isChecked()
        }
        
        if self.limited_time_check.isChecked():
            expiry_date = self.expiry_date_edit.date()
            data["expiry_date"] = datetime.date(expiry_date.year(), expiry_date.month(), expiry_date.day()).isoformat()
        else:
            data["expiry_date"] = None
        
        # Ajouter la date actuelle si c'est un nouvel article
        if not self.editing_mode:
            data["added_at"] = datetime.datetime.now().isoformat()
        
        # Ajouter les métadonnées
        data["metadata"] = self.metadata_edit.text()
        
        return data
    
    def accept(self):
        """Enregistre les modifications"""
        
        # Vérifier que l'ID de l'article est renseigné
        if not self.item_id_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Veuillez générer ou saisir un ID d'article.")
            return
        
        item_data = self.get_item_data()
        
        cursor = self.db.conn.cursor()
        
        if self.editing_mode:
            # Mise à jour d'un article existant
            cursor.execute('''
            UPDATE shop_inventory
            SET item_type = ?, item_id = ?, quantity = ?, price = ?, 
                price_modifier = ?, is_featured = ?, is_limited_time = ?, expiry_date = ?, metadata = ?
            WHERE id = ?
            ''', (
                item_data["item_type"], item_data["item_id"], 
                item_data["quantity"], item_data["price"], item_data["price_modifier"],
                item_data["is_featured"], item_data["is_limited_time"], 
                item_data["expiry_date"], item_data["metadata"], self.item_id
            ))
        else:
            # Création d'un nouvel article
            new_id = str(uuid.uuid4())
            
            cursor.execute('''
            INSERT INTO shop_inventory 
            (id, shop_id, item_type, item_id, quantity, price, price_modifier, 
             is_featured, is_limited_time, expiry_date, added_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_id, self.shop_id, item_data["item_type"], item_data["item_id"], 
                item_data["quantity"], item_data["price"], item_data["price_modifier"],
                item_data["is_featured"], item_data["is_limited_time"], 
                item_data["expiry_date"], item_data["added_at"], item_data["metadata"]
            ))
        
        self.db.conn.commit()
        
        super().accept()
