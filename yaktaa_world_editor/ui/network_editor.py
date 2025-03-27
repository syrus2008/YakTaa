#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'u00e9dition des ru00e9seaux informatiques dans l'u00e9diteur de monde YakTaa
"""

import logging
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QPushButton, QLabel, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class NetworkEditor(QDialog):
    """Dialogue d'u00e9dition d'un ru00e9seau informatique"""
    
    def __init__(self, db, world_id, network_id=None, building_id=None, parent=None):
        super().__init__(parent)
        
        self.db = db
        self.world_id = world_id
        self.network_id = network_id
        self.building_id = building_id
        self.network_data = None
        
        self.setWindowTitle("u00c9diteur de Ru00e9seau Informatique")
        self.resize(600, 500)
        
        self.init_ui()
        
        if self.network_id:
            self.load_network_data()
        else:
            # Si on crée un nouveau réseau et qu'on a un bâtiment associé
            if self.building_id:
                self.building_id_edit.setText(self.building_id)
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom du réseau
        self.name_edit = QLineEdit()
        form_layout.addRow("Nom du ru00e9seau:", self.name_edit)
        
        # SSID (identifiant du réseau)
        self.ssid_edit = QLineEdit()
        form_layout.addRow("SSID:", self.ssid_edit)
        
        # Type de réseau
        self.network_type_combo = QComboBox()
        network_types = ["WiFi", "LAN", "WAN", "VPN", "IoT"]
        self.network_type_combo.addItems(network_types)
        form_layout.addRow("Type de ru00e9seau:", self.network_type_combo)
        
        # Niveau de sécurité (1-10)
        self.security_level_spin = QSpinBox()
        self.security_level_spin.setRange(1, 10)
        self.security_level_spin.setValue(5)
        form_layout.addRow("Niveau de su00e9curitu00e9 (1-10):", self.security_level_spin)
        
        # Type de sécurité
        self.security_type_combo = QComboBox()
        security_types = ["Ouvert", "WEP", "WPA", "WPA2", "WPA3", "Enterprise"]
        self.security_type_combo.addItems(security_types)
        form_layout.addRow("Type de su00e9curitu00e9:", self.security_type_combo)
        
        # Type de chiffrement
        self.encryption_combo = QComboBox()
        encryption_types = ["Aucun", "TKIP", "AES", "CCMP", "Militaire", "Quantique"]
        self.encryption_combo.addItems(encryption_types)
        form_layout.addRow("Type de chiffrement:", self.encryption_combo)
        
        # Force du signal
        self.signal_strength_spin = QSpinBox()
        self.signal_strength_spin.setRange(1, 100)
        self.signal_strength_spin.setValue(80)
        form_layout.addRow("Force du signal (%):", self.signal_strength_spin)
        
        # ID du bâtiment associé
        self.building_id_edit = QLineEdit()
        form_layout.addRow("ID du bu00e2timent associu00e9:", self.building_id_edit)
        
        # Visibilité du réseau
        self.is_hidden_check = QCheckBox("Ru00e9seau masquu00e9")
        form_layout.addRow("", self.is_hidden_check)
        
        # Appareils connectés (JSON)
        self.connected_devices_edit = QTextEdit()
        self.connected_devices_edit.setPlaceholderText("Format JSON: [{\"id\": \"device_123\", \"name\": \"Serveur principal\"}]")
        form_layout.addRow("Appareils connectu00e9s (JSON):", self.connected_devices_edit)
        
        # Vulnérabilités associées
        self.vulnerabilities_edit = QTextEdit()
        self.vulnerabilities_edit.setPlaceholderText("IDs des vulnu00e9rabilitu00e9s, un par ligne")
        form_layout.addRow("Vulnu00e9rabilitu00e9s associu00e9es:\n(un ID par ligne)", self.vulnerabilities_edit)
        
        # Description
        self.description_edit = QTextEdit()
        form_layout.addRow("Description:", self.description_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_network_data(self):
        """Charge les donnu00e9es du ru00e9seau"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT * FROM networks WHERE id = ? AND world_id = ?",
                (self.network_id, self.world_id)
            )
            network = cursor.fetchone()
            if network:
                self.network_data = dict(network)
                
                # Remplir les champs
                self.name_edit.setText(self.network_data["name"])
                self.ssid_edit.setText(self.network_data.get("ssid", ""))
                
                # Type de réseau
                network_type = self.network_data.get("network_type", "WiFi")
                index = self.network_type_combo.findText(network_type)
                if index >= 0:
                    self.network_type_combo.setCurrentIndex(index)
                
                self.security_level_spin.setValue(self.network_data.get("security_level", 5))
                
                # Type de sécurité
                security_type = self.network_data.get("security_type", "WPA2")
                index = self.security_type_combo.findText(security_type)
                if index >= 0:
                    self.security_type_combo.setCurrentIndex(index)
                
                # Type de chiffrement
                encryption = self.network_data.get("encryption", "AES")
                index = self.encryption_combo.findText(encryption)
                if index >= 0:
                    self.encryption_combo.setCurrentIndex(index)
                
                self.signal_strength_spin.setValue(self.network_data.get("signal_strength", 80))
                self.building_id_edit.setText(self.network_data.get("building_id", ""))
                self.is_hidden_check.setChecked(bool(self.network_data.get("is_hidden", 0)))
                
                # Convertir les appareils connectés en JSON formaté pour l'affichage
                try:
                    connected_devices = json.loads(self.network_data.get("connected_devices", "[]"))
                    self.connected_devices_edit.setText(json.dumps(connected_devices, indent=2))
                except (json.JSONDecodeError, TypeError):
                    self.connected_devices_edit.setText("[]")
                
                # Vulnérabilités
                try:
                    vulnerabilities = json.loads(self.network_data.get("vulnerabilities", "[]"))
                    self.vulnerabilities_edit.setText("\n".join(vulnerabilities))
                except (json.JSONDecodeError, TypeError):
                    self.vulnerabilities_edit.setText("")
                
                self.description_edit.setText(self.network_data.get("description", ""))
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des donnu00e9es du ru00e9seau: {str(e)}")
    
    def get_network_data(self):
        """Ru00e9cupu00e8re les donnu00e9es du formulaire"""
        # Validation des appareils connectés JSON
        try:
            connected_devices_text = self.connected_devices_edit.toPlainText().strip()
            if connected_devices_text:
                connected_devices = json.loads(connected_devices_text)
            else:
                connected_devices = []
            connected_devices_json = json.dumps(connected_devices)
        except json.JSONDecodeError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "JSON invalide", "Le format JSON des appareils connectu00e9s est invalide.")
            return None
        
        # Traitement des vulnérabilités
        vulnerabilities = [v.strip() for v in self.vulnerabilities_edit.toPlainText().split('\n') if v.strip()]
        vulnerabilities_json = json.dumps(vulnerabilities)
        
        data = {
            "name": self.name_edit.text(),
            "ssid": self.ssid_edit.text(),
            "network_type": self.network_type_combo.currentText(),
            "security_level": self.security_level_spin.value(),
            "security_type": self.security_type_combo.currentText(),
            "encryption": self.encryption_combo.currentText(),
            "signal_strength": self.signal_strength_spin.value(),
            "building_id": self.building_id_edit.text(),
            "is_hidden": 1 if self.is_hidden_check.isChecked() else 0,
            "connected_devices": connected_devices_json,
            "vulnerabilities": vulnerabilities_json,
            "description": self.description_edit.toPlainText()
        }
        return data
    
    def accept(self):
        """Validation et sauvegarde"""
        if not self.name_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Champ obligatoire", "Le nom du ru00e9seau est obligatoire.")
            return
        
        data = self.get_network_data()
        if data is None:
            return
        
        super().accept()
