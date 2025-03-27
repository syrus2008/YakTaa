#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la liste des personnages pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QMenu, QMessageBox,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QBrush

from ui.character_editor import CharacterEditor

logger = logging.getLogger(__name__)

class CharacterList(QWidget):
    """Widget de liste des personnages pour l'éditeur de monde"""
    
    # Signaux
    character_selected = pyqtSignal(str)  # ID du personnage sélectionné
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_characters()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Liste des personnages
        self.character_tree = QTreeWidget()
        self.character_tree.setHeaderLabels(["Nom", "Profession", "Faction", "Niveau de hacking"])
        self.character_tree.setAlternatingRowColors(True)
        self.character_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.character_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.character_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.character_tree)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_character)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Modifier")
        edit_button.clicked.connect(self.edit_character)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_character)
        buttons_layout.addWidget(delete_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_characters(self):
        """Charge la liste des personnages depuis la base de données"""
        
        self.character_tree.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name, profession, faction, hacking_level, combat_level, charisma, wealth
        FROM characters
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        characters = cursor.fetchall()
        
        # Créer les items de l'arbre
        for character in characters:
            item = QTreeWidgetItem([
                character["name"],
                character["profession"],
                character["faction"],
                str(character["hacking_level"])
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, character["id"])
            
            # Colorer en fonction du niveau de hacking
            hacking_level = character["hacking_level"]
            if hacking_level >= 4:
                item.setForeground(0, QBrush(QColor(255, 0, 0)))  # Rouge pour les experts
            elif hacking_level >= 3:
                item.setForeground(0, QBrush(QColor(255, 128, 0)))  # Orange pour les avancés
            elif hacking_level >= 2:
                item.setForeground(0, QBrush(QColor(0, 128, 255)))  # Bleu pour les intermédiaires
            
            self.character_tree.addTopLevelItem(item)
        
        # Ajuster les colonnes
        for i in range(4):
            self.character_tree.resizeColumnToContents(i)
    
    def refresh(self):
        """Rafraîchit la liste des personnages"""
        
        # Sauvegarder l'ID du personnage sélectionné
        selected_id = None
        selected_items = self.character_tree.selectedItems()
        if selected_items:
            selected_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Recharger les personnages
        self.load_characters()
        
        # Restaurer la sélection
        if selected_id:
            self.select_character(selected_id)
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
    
    def on_selection_changed(self):
        """Gère le changement de sélection dans la liste"""
        
        selected_items = self.character_tree.selectedItems()
        if selected_items:
            character_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.character_selected.emit(character_id)
    
    def select_character(self, character_id):
        """Sélectionne un personnage dans la liste par son ID"""
        
        # Parcourir tous les items pour trouver celui avec l'ID correspondant
        for i in range(self.character_tree.topLevelItemCount()):
            item = self.character_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == character_id:
                self.character_tree.setCurrentItem(item)
                break
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        # Créer le menu
        menu = QMenu()
        
        add_action = QAction("Ajouter un personnage", self)
        add_action.triggered.connect(self.add_character)
        menu.addAction(add_action)
        
        # Actions supplémentaires si un item est sélectionné
        selected_items = self.character_tree.selectedItems()
        if selected_items:
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(self.edit_character)
            menu.addAction(edit_action)
            
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(self.delete_character)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            add_device_action = QAction("Ajouter un appareil", self)
            add_device_action.triggered.connect(self.add_device)
            menu.addAction(add_device_action)
        
        # Afficher le menu
        menu.exec(self.character_tree.mapToGlobal(position))
    
    def add_character(self):
        """Ajoute un nouveau personnage"""
        
        # Ouvrir l'éditeur de personnage
        editor = CharacterEditor(self.db, self.world_id)
        result = editor.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def edit_character(self):
        """Modifie le personnage sélectionné"""
        
        selected_items = self.character_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun personnage sélectionné", 
                               "Veuillez sélectionner un personnage à modifier.")
            return
        
        character_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur de personnage
        editor = CharacterEditor(self.db, self.world_id, character_id)
        result = editor.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def delete_character(self):
        """Supprime le personnage sélectionné"""
        
        selected_items = self.character_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun personnage sélectionné", 
                               "Veuillez sélectionner un personnage à supprimer.")
            return
        
        character_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        character_name = selected_items[0].text(0)
        
        # Demander confirmation
        reply = QMessageBox.question(self, "Confirmation de suppression", 
                                    f"Êtes-vous sûr de vouloir supprimer le personnage '{character_name}' ?\n"
                                    "Cette action supprimera également tous les appareils associés.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Supprimer le personnage et ses dépendances
        cursor = self.db.conn.cursor()
        
        # Supprimer les appareils
        cursor.execute("DELETE FROM devices WHERE character_id = ? AND world_id = ?", 
                      (character_id, self.world_id))
        
        # Supprimer le personnage lui-même
        cursor.execute("DELETE FROM characters WHERE id = ? AND world_id = ?", 
                      (character_id, self.world_id))
        
        self.db.conn.commit()
        
        # Rafraîchir la liste
        self.refresh()
    
    def add_device(self):
        """Ajoute un appareil au personnage sélectionné"""
        
        selected_items = self.character_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aucun personnage sélectionné", 
                               "Veuillez sélectionner un personnage pour ajouter un appareil.")
            return
        
        character_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir l'éditeur d'appareil (à implémenter)
        QMessageBox.information(self, "Fonctionnalité à venir", 
                               "L'ajout d'appareils sera disponible dans une prochaine version.")
