#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste des boutiques pour l'éditeur de monde YakTaa
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QMenu, QMessageBox, QDialog, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ui.shop_editor import ShopEditor

logger = logging.getLogger(__name__)

class ShopList(QWidget):
    """Widget d'affichage et de gestion des boutiques d'un monde"""
    
    shop_selected = pyqtSignal(str)  # Signal émis lors de la sélection d'une boutique (ID)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_shops()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Header avec boutons d'action
        header_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_shop)
        header_layout.addWidget(self.add_button)
        
        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.load_shops)
        header_layout.addWidget(self.refresh_button)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Liste des boutiques
        self.shop_tree = QTreeWidget()
        self.shop_tree.setHeaderLabels(["Nom", "Type", "Lieu", "Légal", "Nb objets"])
        self.shop_tree.setColumnWidth(0, 200)
        self.shop_tree.setColumnWidth(1, 100)
        self.shop_tree.setColumnWidth(2, 150)
        self.shop_tree.setColumnWidth(3, 60)
        self.shop_tree.itemClicked.connect(self.on_item_clicked)
        self.shop_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.shop_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.shop_tree)
    
    def load_shops(self):
        """Charge la liste des boutiques depuis la base de données"""
        
        self.shop_tree.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT s.id, s.name, s.shop_type, l.name as location_name, s.is_legal, 
               (SELECT COUNT(*) FROM shop_inventory WHERE shop_id = s.id) as item_count
        FROM shops s
        LEFT JOIN locations l ON s.location_id = l.id
        WHERE s.world_id = ?
        ORDER BY s.name
        ''', (self.world_id,))
        
        shops = cursor.fetchall()
        
        for shop in shops:
            item = QTreeWidgetItem(self.shop_tree)
            item.setText(0, shop["name"])
            item.setText(1, shop["shop_type"])
            item.setText(2, shop["location_name"] or "N/A")
            item.setText(3, "Oui" if shop["is_legal"] else "Non")
            item.setText(4, str(shop["item_count"]))
            item.setData(0, Qt.ItemDataRole.UserRole, shop["id"])  # Stocker l'ID de la boutique
    
    def on_item_clicked(self, item, column):
        """Gérer le clic sur un élément de la liste"""
        
        shop_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.shop_selected.emit(shop_id)
    
    def show_context_menu(self, position):
        """Afficher le menu contextuel pour la liste des boutiques"""
        
        item = self.shop_tree.itemAt(position)
        if not item:
            return
        
        shop_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        context_menu = QMenu(self)
        
        edit_action = QAction("Modifier", self)
        edit_action.triggered.connect(lambda: self.edit_shop(shop_id))
        context_menu.addAction(edit_action)
        
        view_inventory_action = QAction("Voir l'inventaire", self)
        view_inventory_action.triggered.connect(lambda: self.view_inventory(shop_id))
        context_menu.addAction(view_inventory_action)
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_shop(shop_id))
        context_menu.addAction(delete_action)
        
        context_menu.exec(self.shop_tree.mapToGlobal(position))
    
    def add_shop(self):
        """Ajouter une nouvelle boutique"""
        
        dialog = ShopEditor(self.db, self.world_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_shops()
    
    def edit_shop(self, shop_id):
        """Modifier une boutique existante"""
        
        dialog = ShopEditor(self.db, self.world_id, shop_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_shops()
    
    def view_inventory(self, shop_id):
        """Afficher l'inventaire d'une boutique"""
        
        from .shop_editor import ShopEditor
        
        # Ouvrir l'éditeur de boutique avec l'onglet d'inventaire sélectionné
        dialog = ShopEditor(self.db, self.world_id, shop_id)
        
        # Sélectionner l'onglet d'inventaire (index 1)
        tab_widget = dialog.findChild(QTabWidget)
        if tab_widget:
            tab_widget.setCurrentIndex(1)  # L'onglet d'inventaire est généralement le deuxième (index 1)
        
        dialog.exec()
    
    def delete_shop(self, shop_id):
        """Supprimer une boutique"""
        
        confirm = QMessageBox.question(
            self, "Confirmation", 
            "Êtes-vous sûr de vouloir supprimer cette boutique et tout son inventaire?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            
            # Supprimer l'inventaire d'abord (contrainte de clé étrangère)
            cursor.execute("DELETE FROM shop_inventory WHERE shop_id = ?", (shop_id,))
            
            # Supprimer la boutique
            cursor.execute("DELETE FROM shops WHERE id = ?", (shop_id,))
            
            self.db.conn.commit()
            self.load_shops()
            
            logger.info(f"Boutique {shop_id} supprimée")
    
    def refresh(self):
        """Rafraîchir la liste des boutiques"""
        self.load_shops()
    
    def save(self):
        """Sauvegarder les modifications (pas d'opération spécifique ici car tout est sauvegardé immédiatement)"""
        self.db.conn.commit()
