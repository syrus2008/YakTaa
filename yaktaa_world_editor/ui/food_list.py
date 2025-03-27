#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste d'aliments pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QPushButton, QHBoxLayout, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from ui.food_editor import FoodEditor

logger = logging.getLogger(__name__)

class FoodList(QWidget):
    """Widget affichant la liste des aliments"""
    
    food_selected = pyqtSignal(str)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_food_items()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Liste des aliments
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID", "Nom", "Type", "Prix", "Restauration Santé"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 80)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_food)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_food)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_food)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
    
    def load_food_items(self):
        """Charge la liste des aliments"""
        
        self.tree.clear()
        
        try:
            cursor = self.db.conn.cursor()
            
            # Vérifier si la table food_items existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='food_items'")
            if not cursor.fetchone():
                # Créer la table si elle n'existe pas
                cursor.execute('''
                CREATE TABLE food_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    food_type TEXT,
                    price INTEGER,
                    health_restore INTEGER,
                    energy_restore INTEGER,
                    mental_restore INTEGER,
                    is_legal INTEGER DEFAULT 1,
                    rarity TEXT DEFAULT 'COMMON',
                    uses INTEGER DEFAULT 1
                )
                ''')
                logger.info("Table food_items créée avec succès")
            
            # Récupérer les aliments
            cursor.execute('''
            SELECT id, name, food_type, price, health_restore
            FROM food_items
            ORDER BY name
            ''')
            
            for row in cursor.fetchall():
                item = QTreeWidgetItem()
                item.setText(0, str(row['id']))
                item.setText(1, str(row['name']))
                item.setText(2, str(row['food_type']))
                item.setText(3, str(row['price']))
                item.setText(4, str(row['health_restore']))
                
                self.tree.addTopLevelItem(item)
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des aliments: {e}")
    
    def on_item_clicked(self, item, column):
        """Gère le clic sur un élément de la liste"""
        
        food_id = item.text(0)
        self.food_selected.emit(food_id)
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        
        item = self.tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        edit_action = QAction("Modifier", self)
        edit_action.triggered.connect(self.edit_food)
        menu.addAction(edit_action)
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(self.delete_food)
        menu.addAction(delete_action)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))
    
    def add_food(self):
        """Ajoute un nouvel aliment"""
        
        dialog = FoodEditor(self.db, self.world_id)
        if dialog.exec() == FoodEditor.Accepted:
            self.load_food_items()
    
    def edit_food(self):
        """Modifie un aliment existant"""
        
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Alerte", "Veuillez sélectionner un aliment à modifier.")
            return
        
        food_id = selected_items[0].text(0)
        
        dialog = FoodEditor(self.db, self.world_id, food_id)
        if dialog.exec() == FoodEditor.Accepted:
            self.load_food_items()
    
    def delete_food(self):
        """Supprime un aliment"""
        
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Alerte", "Veuillez sélectionner un aliment à supprimer.")
            return
        
        food_id = selected_items[0].text(0)
        food_name = selected_items[0].text(1)
        
        reply = QMessageBox.question(
            self, 
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'aliment {food_name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("DELETE FROM food_items WHERE id = ?", (food_id,))
                self.db.conn.commit()
                
                logger.info(f"Aliment {food_id} supprimé avec succès")
                self.load_food_items()
                
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'aliment: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'aliment: {e}")
