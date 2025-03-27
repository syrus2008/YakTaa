#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur de fichiers pour l'éditeur de monde YakTaa
"""

import logging
import uuid
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QCheckBox, QTextEdit,
    QTabWidget, QWidget, QSlider, QMessageBox,
    QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

logger = logging.getLogger(__name__)

class FileEditor(QDialog):
    """Boîte de dialogue pour l'édition des fichiers sur un appareil"""
    
    def __init__(self, db, world_id, file_id=None, device_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.file_id = file_id
        self.device_id = device_id  # Appareil où se trouve le fichier (obligatoire pour un nouveau fichier)
        self.is_new = file_id is None
        
        self.init_ui()
        
        if not self.is_new:
            self.load_file_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Éditeur de fichier" if self.is_new else "Modifier le fichier")
        self.setMinimumSize(600, 500)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet des informations de base
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Nom du fichier
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("exemple.txt")
        basic_layout.addRow("Nom du fichier:", self.name_edit)
        
        # Type de fichier
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "text", "executable", "image", "audio", 
            "video", "database", "archive", "config",
            "log", "email", "document", "spreadsheet",
            "presentation", "source_code", "binary", "other"
        ])
        basic_layout.addRow("Type:", self.type_combo)
        
        # Taille du fichier
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(1)
        self.size_spin.setMaximum(1000000)
        self.size_spin.setValue(100)
        basic_layout.addRow("Taille (KB):", self.size_spin)
        
        # Appareil
        self.device_combo = QComboBox()
        self.load_devices()
        basic_layout.addRow("Appareil:", self.device_combo)
        
        # Chemin du fichier
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("/home/user/documents/")
        basic_layout.addRow("Chemin:", self.path_edit)
        
        # Fichier caché
        self.hidden_check = QCheckBox("Fichier caché")
        basic_layout.addRow(self.hidden_check)
        
        # Fichier chiffré
        self.encrypted_check = QCheckBox("Fichier chiffré")
        basic_layout.addRow(self.encrypted_check)
        
        # Niveau de sécurité
        self.security_spin = QSpinBox()
        self.security_spin.setMinimum(1)
        self.security_spin.setMaximum(5)
        self.security_spin.setValue(1)
        basic_layout.addRow("Niveau de sécurité:", self.security_spin)
        
        tabs.addTab(basic_tab, "Informations de base")
        
        # Onglet du contenu
        content_tab = QWidget()
        content_layout = QVBoxLayout(content_tab)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Entrez le contenu du fichier ici...")
        content_layout.addWidget(self.content_edit)
        
        # Boutons pour le contenu
        content_buttons_layout = QHBoxLayout()
        
        import_button = QPushButton("Importer depuis un fichier")
        import_button.clicked.connect(self.import_content)
        content_buttons_layout.addWidget(import_button)
        
        generate_button = QPushButton("Générer contenu aléatoire")
        generate_button.clicked.connect(self.generate_random_content)
        content_buttons_layout.addWidget(generate_button)
        
        content_layout.addLayout(content_buttons_layout)
        
        tabs.addTab(content_tab, "Contenu")
        
        # Onglet des métadonnées
        metadata_tab = QWidget()
        metadata_layout = QFormLayout(metadata_tab)
        
        # Propriétaire
        self.owner_edit = QLineEdit()
        metadata_layout.addRow("Propriétaire:", self.owner_edit)
        
        # Date de création
        self.creation_date_edit = QLineEdit()
        self.creation_date_edit.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        metadata_layout.addRow("Date de création:", self.creation_date_edit)
        
        # Date de modification
        self.modified_date_edit = QLineEdit()
        self.modified_date_edit.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        metadata_layout.addRow("Date de modification:", self.modified_date_edit)
        
        # Permissions
        permissions_group = QGroupBox("Permissions")
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.read_check = QCheckBox("Lecture")
        self.read_check.setChecked(True)
        permissions_layout.addWidget(self.read_check)
        
        self.write_check = QCheckBox("Écriture")
        self.write_check.setChecked(True)
        permissions_layout.addWidget(self.write_check)
        
        self.execute_check = QCheckBox("Exécution")
        permissions_layout.addWidget(self.execute_check)
        
        metadata_layout.addRow(permissions_group)
        
        tabs.addTab(metadata_tab, "Métadonnées")
        
        main_layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_devices(self):
        """Charge la liste des appareils depuis la base de données"""
        
        self.device_combo.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name
        FROM devices
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        devices = cursor.fetchall()
        
        for device in devices:
            self.device_combo.addItem(device["name"], device["id"])
        
        # Sélectionner l'appareil spécifié (si fourni)
        if self.device_id:
            for i in range(self.device_combo.count()):
                if self.device_combo.itemData(i) == self.device_id:
                    self.device_combo.setCurrentIndex(i)
                    break
    
    def import_content(self):
        """Importe le contenu depuis un fichier local"""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer depuis un fichier", "", "Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.content_edit.setText(content)
                    
                    # Mettre à jour le nom du fichier si vide
                    if not self.name_edit.text():
                        self.name_edit.setText(os.path.basename(file_path))
                    
                    # Mettre à jour la taille
                    file_size = os.path.getsize(file_path) // 1024  # Convertir en KB
                    self.size_spin.setValue(max(1, min(file_size, 1000000)))
                    
            except Exception as e:
                QMessageBox.warning(self, "Erreur d'importation", 
                                   f"Impossible d'importer le fichier: {str(e)}")
    
    def generate_random_content(self):
        """Génère un contenu aléatoire en fonction du type de fichier"""
        
        file_type = self.type_combo.currentText()
        
        if file_type == "text":
            content = "Ceci est un exemple de fichier texte généré automatiquement.\n\n"
            content += "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.\n"
            content += "Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor.\n"
            content += "Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi."
        
        elif file_type == "source_code":
            content = "#!/usr/bin/env python3\n\n"
            content += "def main():\n"
            content += "    print('Hello, YakTaa world!')\n"
            content += "    for i in range(10):\n"
            content += "        print(f'Count: {i}')\n\n"
            content += "if __name__ == '__main__':\n"
            content += "    main()\n"
        
        elif file_type == "log":
            content = "[2050-01-01 00:00:00] INFO: System initialized\n"
            content += "[2050-01-01 00:01:12] INFO: User login: admin\n"
            content += "[2050-01-01 00:02:45] WARNING: High memory usage detected\n"
            content += "[2050-01-01 00:03:30] ERROR: Connection timeout\n"
            content += "[2050-01-01 00:04:15] INFO: Backup started\n"
            content += "[2050-01-01 00:05:20] INFO: Backup completed\n"
        
        elif file_type == "config":
            content = "# Configuration file\n\n"
            content += "[General]\n"
            content += "Language = English\n"
            content += "Theme = Dark\n\n"
            content += "[Network]\n"
            content += "Host = 192.168.1.1\n"
            content += "Port = 8080\n"
            content += "Timeout = 30\n\n"
            content += "[Security]\n"
            content += "EnableFirewall = true\n"
            content += "AllowRemoteAccess = false\n"
        
        elif file_type == "email":
            content = "From: sender@example.com\n"
            content += "To: recipient@example.com\n"
            content += "Subject: Important information\n\n"
            content += "Dear User,\n\n"
            content += "This is an important message regarding your account security.\n"
            content += "Please update your password at your earliest convenience.\n\n"
            content += "Best regards,\n"
            content += "Security Team"
        
        else:
            content = f"[Contenu binaire simulé pour un fichier de type {file_type}]"
        
        self.content_edit.setText(content)
    
    def load_file_data(self):
        """Charge les données du fichier depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT name, file_type, size_kb, device_id, file_path,
               is_hidden, is_encrypted, security_level, content,
               owner, creation_date, modified_date, 
               permission_read, permission_write, permission_execute
        FROM files
        WHERE id = ? AND world_id = ?
        """, (self.file_id, self.world_id))
        
        file_data = cursor.fetchone()
        
        if not file_data:
            QMessageBox.critical(self, "Erreur", f"Impossible de trouver le fichier avec l'ID {self.file_id}")
            self.reject()
            return
        
        # Remplir les champs
        self.name_edit.setText(file_data["name"])
        
        # Trouver l'index du type de fichier
        type_index = self.type_combo.findText(file_data["file_type"])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        self.size_spin.setValue(file_data["size_kb"])
        
        # Trouver l'index de l'appareil
        if file_data["device_id"]:
            for i in range(self.device_combo.count()):
                if self.device_combo.itemData(i) == file_data["device_id"]:
                    self.device_combo.setCurrentIndex(i)
                    break
        
        if file_data["file_path"]:
            self.path_edit.setText(file_data["file_path"])
        
        self.hidden_check.setChecked(file_data["is_hidden"])
        self.encrypted_check.setChecked(file_data["is_encrypted"])
        self.security_spin.setValue(file_data["security_level"])
        
        if file_data["content"]:
            self.content_edit.setText(file_data["content"])
        
        if file_data["owner"]:
            self.owner_edit.setText(file_data["owner"])
        
        if file_data["creation_date"]:
            self.creation_date_edit.setText(file_data["creation_date"])
        
        if file_data["modified_date"]:
            self.modified_date_edit.setText(file_data["modified_date"])
        
        self.read_check.setChecked(file_data["permission_read"])
        self.write_check.setChecked(file_data["permission_write"])
        self.execute_check.setChecked(file_data["permission_execute"])
    
    def save_file(self):
        """Sauvegarde les données du fichier dans la base de données"""
        
        # Récupérer les valeurs
        name = self.name_edit.text()
        file_type = self.type_combo.currentText()
        size_kb = self.size_spin.value()
        
        device_id = None
        if self.device_combo.currentIndex() >= 0:
            device_id = self.device_combo.currentData()
        
        file_path = self.path_edit.text()
        is_hidden = self.hidden_check.isChecked()
        is_encrypted = self.encrypted_check.isChecked()
        security_level = self.security_spin.value()
        
        content = self.content_edit.toPlainText()
        
        owner = self.owner_edit.text()
        creation_date = self.creation_date_edit.text()
        modified_date = self.modified_date_edit.text()
        
        permission_read = self.read_check.isChecked()
        permission_write = self.write_check.isChecked()
        permission_execute = self.execute_check.isChecked()
        
        # Valider les données
        if not name:
            QMessageBox.warning(self, "Validation", "Le nom du fichier est obligatoire.")
            return
        
        if not device_id:
            QMessageBox.warning(self, "Validation", "L'appareil est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        if self.is_new:
            # Générer un nouvel ID
            self.file_id = str(uuid.uuid4())
            
            # Insérer le nouveau fichier
            cursor.execute("""
            INSERT INTO files (
                id, world_id, name, file_type, size_kb, device_id, file_path,
                is_hidden, is_encrypted, security_level, content,
                owner, creation_date, modified_date, 
                permission_read, permission_write, permission_execute
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.file_id, self.world_id, name, file_type, size_kb, device_id, file_path,
                is_hidden, is_encrypted, security_level, content,
                owner, creation_date, modified_date,
                permission_read, permission_write, permission_execute
            ))
        else:
            # Mettre à jour le fichier existant
            cursor.execute("""
            UPDATE files
            SET name = ?, file_type = ?, size_kb = ?, device_id = ?, file_path = ?,
                is_hidden = ?, is_encrypted = ?, security_level = ?, content = ?,
                owner = ?, creation_date = ?, modified_date = ?,
                permission_read = ?, permission_write = ?, permission_execute = ?
            WHERE id = ? AND world_id = ?
            """, (
                name, file_type, size_kb, device_id, file_path,
                is_hidden, is_encrypted, security_level, content,
                owner, creation_date, modified_date,
                permission_read, permission_write, permission_execute,
                self.file_id, self.world_id
            ))
        
        self.db.conn.commit()
        
        # Accepter la boîte de dialogue
        self.accept()
