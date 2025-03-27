#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la liste des fichiers pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QBrush

from ui.file_editor import FileEditor

logger = logging.getLogger(__name__)

class FileList(QWidget):
    """Widget de liste des fichiers pour l'éditeur de monde"""
    
    # Signaux
    file_selected = pyqtSignal(str)  # ID du fichier sélectionné
    
    def __init__(self, db, world_id, device_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.device_id = device_id  # Optionnel, pour filtrer par appareil
        
        self.init_ui()
        self.load_files()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Liste des fichiers
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Nom", "Type", "Taille (KB)", "Chemin", "Sécurité"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.file_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_file)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_file)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_file)
        buttons_layout.addWidget(delete_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_files(self):
        """Charge la liste des fichiers depuis la base de données"""
        
        self.file_tree.clear()
        
        cursor = self.db.conn.cursor()
        
        # Requête SQL de base
        query = """
        SELECT f.id, f.name, f.file_type, f.size_kb, f.file_path, 
               f.is_hidden, f.is_encrypted, f.security_level,
               d.name as device_name, f.device_id
        FROM files f
        LEFT JOIN devices d ON f.device_id = d.id
        WHERE f.world_id = ?
        """
        
        params = [self.world_id]
        
        # Ajouter un filtre par appareil si nécessaire
        if self.device_id:
            query += " AND f.device_id = ?"
            params.append(self.device_id)
        
        query += " ORDER BY f.name"
        
        cursor.execute(query, params)
        
        files = cursor.fetchall()
        
        # Créer les items de l'arbre
        for file in files:
            item = QTreeWidgetItem([
                file["name"],
                file["file_type"],
                str(file["size_kb"]),
                file["file_path"] or "",
                str(file["security_level"])
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, file["id"])
            item.setData(3, Qt.ItemDataRole.UserRole, file["device_id"])
            
            # Colorer en fonction du type de fichier et des attributs
            if file["is_encrypted"]:
                item.setForeground(0, QBrush(QColor(255, 0, 0)))  # Rouge pour les fichiers chiffrés
            elif file["is_hidden"]:
                item.setForeground(0, QBrush(QColor(128, 128, 128)))  # Gris pour les fichiers cachés
            elif file["file_type"] == "executable":
                item.setForeground(0, QBrush(QColor(0, 200, 0)))  # Vert pour les exécutables
            elif file["file_type"] == "text":
                item.setForeground(0, QBrush(QColor(0, 128, 255)))  # Bleu pour les fichiers texte
            elif file["file_type"] == "source_code":
                item.setForeground(0, QBrush(QColor(128, 0, 128)))  # Violet pour le code source
            
            self.file_tree.addTopLevelItem(item)
        
        # Ajuster les colonnes
        for i in range(5):
            self.file_tree.resizeColumnToContents(i)
    
    def refresh(self):
        """Rafraîchit la liste des fichiers"""
        
        # Sauvegarder l'ID du fichier sélectionné
        selected_id = None
        selected_items = self.file_tree.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Recharger les fichiers
        self.load_files()
        
        # Restaurer la sélection
        if selected_id:
            self.select_file(selected_id)
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        
        selected_items = self.file_tree.selectedItems()
        if selected_items:
            file_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.file_selected.emit(file_id)
    
    def select_file(self, file_id):
        """Sélectionne un fichier dans la liste par son ID"""
        
        # Parcourir tous les items pour trouver celui avec l'ID correspondant
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == file_id:
                self.file_tree.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        # Créer le menu
        menu = QMenu()
        
        add_action = QAction("Ajouter un fichier", self)
        add_action.triggered.connect(self.add_file)
        menu.addAction(add_action)
        
        # Actions supplémentaires si un item est sélectionné
        selected_items = self.file_tree.selectedItems()
        if selected_items:
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(self.edit_file)
            menu.addAction(edit_action)
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(self.delete_file)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            view_content_action = QAction("Voir le contenu", self)
            view_content_action.triggered.connect(self.view_file_content)
            menu.addAction(view_content_action)
        
        # Afficher le menu
        menu.exec(self.file_tree.mapToGlobal(position))
    
    def add_file(self):
        """Ajoute un nouveau fichier"""
        
        editor = FileEditor(self.db, self.world_id, device_id=self.device_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def edit_file(self):
        """Modifie le fichier sélectionné"""
        
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun fichier sélectionné", 
                               "Veuillez sélectionner un fichier à modifier.")
            return
        
        file_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        editor = FileEditor(self.db, self.world_id, file_id)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def delete_file(self):
        """Supprime le fichier sélectionné"""
        
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun fichier sélectionné", 
                               "Veuillez sélectionner un fichier à supprimer.")
            return
        
        file_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        file_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer le fichier '{file_name}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            
            # Supprimer le fichier
            cursor.execute("""
            DELETE FROM files
            WHERE id = ? AND world_id = ?
            """, (file_id, self.world_id))
            
            self.db.conn.commit()
            
            self.refresh()
    
    def view_file_content(self):
        """Affiche le contenu du fichier sélectionné"""
        
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            return
        
        file_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        file_name = selected_items[0].text(0)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT content, file_type, is_encrypted
        FROM files
        WHERE id = ? AND world_id = ?
        """, (file_id, self.world_id))
        
        file_data = cursor.fetchone()
        
        if not file_data:
            QMessageBox.warning(self, "Erreur", "Impossible de récupérer le contenu du fichier.")
            return
        
        # Si le fichier est chiffré, afficher un message spécial
        if file_data["is_encrypted"]:
            content = "[Ce fichier est chiffré et nécessite une clé de déchiffrement]"
        else:
            content = file_data["content"] or "[Aucun contenu]"
        
        # Créer une boîte de dialogue pour afficher le contenu
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Contenu de {file_name}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        content_edit.setText(content)
        
        # Définir une police à espacement fixe pour le code source
        if file_data["file_type"] in ["source_code", "text", "config", "log"]:
            font = content_edit.font()
            font.setFamily("Courier New")
            content_edit.setFont(font)
        
        layout.addWidget(content_edit)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
