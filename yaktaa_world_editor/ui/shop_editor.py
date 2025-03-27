#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'édition de boutiques pour l'éditeur de monde YakTaa
"""

import logging
import uuid
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QDialogButtonBox,
    QTabWidget, QTextEdit, QGroupBox, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCursor, QColor

logger = logging.getLogger(__name__)

class ShopEditor(QDialog):
    """Dialogue d'édition de boutique"""
    
    def __init__(self, db, world_id, shop_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.shop_id = shop_id
        self.editing_mode = shop_id is not None
        
        self.shop_data = {}
        if self.editing_mode:
            self.load_shop_data()
        
        self.init_ui()
        self.setWindowTitle("Modifier la boutique" if self.editing_mode else "Nouvelle boutique")
        self.resize(600, 500)
    
    def load_shop_data(self):
        """Charge les données de la boutique depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, description, shop_type, location_id, building_id, 
               is_legal, price_modifier, inventory_refresh_rate, owner_id
        FROM shops WHERE id = ?
        ''', (self.shop_id,))
        
        shop = cursor.fetchone()
        if shop:
            self.shop_data = dict(shop)
        else:
            logger.error(f"Boutique {self.shop_id} non trouvée")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Onglets
        tab_widget = QTabWidget()
        
        # Onglet des informations générales
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Nom
        self.name_edit = QLineEdit()
        if self.editing_mode:
            self.name_edit.setText(self.shop_data.get("name", ""))
        general_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        if self.editing_mode:
            self.description_edit.setText(self.shop_data.get("description", ""))
        general_layout.addRow("Description:", self.description_edit)
        
        # Type de boutique
        self.type_combo = QComboBox()
        shop_types = ["hardware", "software", "consumable", "cybernetic", "weapon", "armor", "general", "black_market"]
        self.type_combo.addItems(shop_types)
        if self.editing_mode and "shop_type" in self.shop_data:
            index = self.type_combo.findText(self.shop_data["shop_type"])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        general_layout.addRow("Type:", self.type_combo)
        
        # Emplacement
        self.location_combo = QComboBox()
        self.load_locations()
        general_layout.addRow("Lieu:", self.location_combo)
        
        # Bâtiment
        self.building_combo = QComboBox()
        self.building_combo.addItem("Aucun", None)
        self.load_buildings()
        general_layout.addRow("Bâtiment:", self.building_combo)
        
        # Propriétaire
        self.owner_combo = QComboBox()
        self.owner_combo.addItem("Aucun", None)
        self.load_characters()
        general_layout.addRow("Propriétaire:", self.owner_combo)
        
        # Légalité
        self.legal_check = QCheckBox("Boutique légale")
        if self.editing_mode:
            self.legal_check.setChecked(self.shop_data.get("is_legal", True))
        else:
            self.legal_check.setChecked(True)
        general_layout.addRow("", self.legal_check)
        
        # Modificateur de prix
        self.price_modifier_spin = QDoubleSpinBox()
        self.price_modifier_spin.setRange(0.1, 5.0)
        self.price_modifier_spin.setSingleStep(0.1)
        self.price_modifier_spin.setValue(self.shop_data.get("price_modifier", 1.0) if self.editing_mode else 1.0)
        general_layout.addRow("Mod. prix:", self.price_modifier_spin)
        
        # Taux de rafraîchissement de l'inventaire
        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setRange(0, 100)
        self.refresh_rate_spin.setSuffix("%")
        self.refresh_rate_spin.setValue(self.shop_data.get("inventory_refresh_rate", 10) if self.editing_mode else 10)
        general_layout.addRow("Taux rafr.:", self.refresh_rate_spin)
        
        tab_widget.addTab(general_tab, "Général")
        
        # Onglet d'inventaire
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        
        if not self.editing_mode:
            inventory_info = QLabel("L'inventaire peut être édité une fois la boutique créée.")
            inventory_layout.addWidget(inventory_info)
        else:
            # Statistiques d'inventaire
            inventory_stats = self.get_inventory_stats()
            inventory_stats_label = QLabel(inventory_stats)
            inventory_stats_label.setObjectName("inventory_stats_label")
            inventory_layout.addWidget(inventory_stats_label)
            
            # Tableau d'inventaire
            self.inventory_table = QTableWidget()
            self.inventory_table.setColumnCount(5)
            self.inventory_table.setHorizontalHeaderLabels(["Type", "Nom", "Quantité", "Prix", "ID"])
            self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.inventory_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.inventory_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.inventory_table.customContextMenuRequested.connect(self.show_inventory_context_menu)
            inventory_layout.addWidget(self.inventory_table)
            
            # Boutons de gestion d'inventaire
            inventory_buttons_layout = QHBoxLayout()
            
            # Bouton pour ajouter un article
            add_item_button = QPushButton("Ajouter un article")
            add_item_button.clicked.connect(self.add_inventory_item)
            inventory_buttons_layout.addWidget(add_item_button)
            
            # Bouton pour modifier un article
            edit_item_button = QPushButton("Modifier l'article sélectionné")
            edit_item_button.clicked.connect(self.edit_inventory_item)
            inventory_buttons_layout.addWidget(edit_item_button)
            
            # Bouton pour supprimer un article
            delete_item_button = QPushButton("Supprimer l'article sélectionné")
            delete_item_button.clicked.connect(self.delete_inventory_item)
            inventory_buttons_layout.addWidget(delete_item_button)
            
            inventory_layout.addLayout(inventory_buttons_layout)
            
            # Bouton de génération aléatoire d'inventaire
            random_inventory_button = QPushButton("Générer un inventaire aléatoire")
            random_inventory_button.clicked.connect(self.generate_random_inventory)
            inventory_layout.addWidget(random_inventory_button)
            
            # Charger l'inventaire actuel
            self.load_inventory()
        
        tab_widget.addTab(inventory_tab, "Inventaire")
        
        main_layout.addWidget(tab_widget)
        
        # Boutons d'action
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def load_locations(self):
        """Charge la liste des lieux depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, location_type
        FROM locations
        WHERE world_id = ?
        ORDER BY name
        ''', (self.world_id,))
        
        locations = cursor.fetchall()
        
        self.location_combo.clear()
        for location in locations:
            display_text = f"{location['name']} ({location['location_type']})"
            self.location_combo.addItem(display_text, location["id"])
        
        if self.editing_mode and "location_id" in self.shop_data:
            for i in range(self.location_combo.count()):
                if self.location_combo.itemData(i) == self.shop_data["location_id"]:
                    self.location_combo.setCurrentIndex(i)
                    break
    
    def load_buildings(self):
        """Charge la liste des bâtiments depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT b.id, b.name, l.name as location_name, b.building_type
        FROM buildings b
        LEFT JOIN locations l ON b.location_id = l.id
        WHERE b.world_id = ?
        ORDER BY l.name, b.name
        ''', (self.world_id,))
        
        buildings = cursor.fetchall()
        
        self.building_combo.clear()
        self.building_combo.addItem("Aucun", None)
        
        for building in buildings:
            display_text = f"{building['name']} ({building['building_type']}) - {building['location_name']}"
            self.building_combo.addItem(display_text, building["id"])
        
        if self.editing_mode and "building_id" in self.shop_data and self.shop_data["building_id"]:
            for i in range(self.building_combo.count()):
                if self.building_combo.itemData(i) == self.shop_data["building_id"]:
                    self.building_combo.setCurrentIndex(i)
                    break
    
    def load_characters(self):
        """Charge la liste des personnages depuis la base de données"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT id, name, profession
        FROM characters
        WHERE world_id = ?
        ORDER BY name
        ''', (self.world_id,))
        
        characters = cursor.fetchall()
        
        self.owner_combo.clear()
        self.owner_combo.addItem("Aucun", None)
        
        for character in characters:
            display_text = f"{character['name']} ({character['profession']})"
            self.owner_combo.addItem(display_text, character["id"])
        
        if self.editing_mode and "owner_id" in self.shop_data and self.shop_data["owner_id"]:
            for i in range(self.owner_combo.count()):
                if self.owner_combo.itemData(i) == self.shop_data["owner_id"]:
                    self.owner_combo.setCurrentIndex(i)
                    break
    
    def get_inventory_stats(self):
        """Récupère les statistiques d'inventaire de la boutique"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN item_type = 'hardware' THEN 1 ELSE 0 END) as hardware,
               SUM(CASE WHEN item_type = 'consumable' THEN 1 ELSE 0 END) as consumable,
               SUM(CASE WHEN item_type = 'software' THEN 1 ELSE 0 END) as software,
               AVG(price) as avg_price
        FROM shop_inventory
        WHERE shop_id = ?
        ''', (self.shop_id,))
        
        stats = cursor.fetchone()
        
        if not stats or stats["total"] == 0:
            return "Aucun article dans l'inventaire."
        
        return f"Inventaire: {stats['total']} articles au total\n" + \
               f"- Hardware: {stats['hardware']}\n" + \
               f"- Consommables: {stats['consumable']}\n" + \
               f"- Software: {stats['software']}\n" + \
               f"Prix moyen: {stats['avg_price']:.2f} crédits"
    
    def generate_random_inventory(self):
        """Génère un inventaire aléatoire pour la boutique"""
        
        # Cette fonctionnalité appelle le générateur de monde pour créer un inventaire
        # Cette implémentation simple est un exemple, à développer davantage
        
        # Importation adaptative pour fonctionner dans différents contextes
        try:
            # Essayer d'abord l'importation relative
            from ..shop_inventory_generator import generate_shop_inventory
        except ImportError:
            # Si échec, essayer l'importation directe (si le fichier est dans le même dossier ou dans le PYTHONPATH)
            import sys
            import os
            # Ajouter le répertoire parent au chemin pour trouver le module
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from shop_inventory_generator import generate_shop_inventory
        
        # Supprimer l'inventaire existant
        cursor = self.db.conn.cursor()
        cursor.execute("DELETE FROM shop_inventory WHERE shop_id = ?", (self.shop_id,))
        
        # Générer un nouvel inventaire
        num_items = generate_shop_inventory(self.db, self.world_id, self.shop_id)
        
        self.db.conn.commit()
        
        # Mettre à jour les stats d'inventaire
        inventory_stats = self.get_inventory_stats()
        # Ici, on pourrait mettre à jour l'interface pour afficher les nouvelles stats
        
        logger.info(f"Inventaire généré pour la boutique {self.shop_id}: {num_items} articles")
    
    def load_inventory(self):
        """Charge l'inventaire du magasin"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT 
            si.id, 
            si.item_type, 
            si.item_id, 
            si.quantity, 
            si.price, 
            si.price_modifier,
            si.is_featured, 
            si.is_limited_time, 
            si.expiry_date,
            si.metadata
        FROM shop_inventory si
        WHERE si.shop_id = ?
        ORDER BY si.is_featured DESC, si.item_type, si.price DESC
        ''', (self.shop_id,))
        
        inventory = cursor.fetchall()
        
        # Effacer le tableau d'inventaire
        self.inventory_table.setRowCount(0)
        
        # Remplir le tableau avec les données
        for i, item in enumerate(inventory):
            self.inventory_table.insertRow(i)
            
            # Extraire le nom de l'article des métadonnées si disponible
            item_name = item["item_id"]
            try:
                metadata = json.loads(item["metadata"])
                if "name" in metadata:
                    item_name = metadata["name"]
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Définir les colonnes
            self.inventory_table.setItem(i, 0, QTableWidgetItem(item["item_type"]))
            self.inventory_table.setItem(i, 1, QTableWidgetItem(item_name))
            self.inventory_table.setItem(i, 2, QTableWidgetItem(str(item["quantity"])))
            self.inventory_table.setItem(i, 3, QTableWidgetItem(f"{item['price']:.2f} ¥"))
            
            # Stocker l'ID de l'article dans les données de la ligne
            self.inventory_table.setItem(i, 4, QTableWidgetItem(item["id"]))
            
            # Marquer les articles mis en avant
            if item["is_featured"]:
                for col in range(self.inventory_table.columnCount()):
                    cell_item = self.inventory_table.item(i, col)
                    if cell_item:
                        cell_item.setBackground(QColor(255, 255, 200))  # Jaune clair
            
            # Marquer les articles à durée limitée
            if item["is_limited_time"]:
                for col in range(self.inventory_table.columnCount()):
                    cell_item = self.inventory_table.item(i, col)
                    if cell_item:
                        cell_item.setForeground(QColor(200, 0, 0))  # Rouge
        
        # Ajuster la taille des colonnes
        self.inventory_table.resizeColumnsToContents()
        
        # Mettre à jour les statistiques
        self.update_inventory_stats()
    
    def add_inventory_item(self):
        """Ajoute un article à l'inventaire"""
        
        from .inventory_item_editor import InventoryItemEditor
        
        # Vérifier que la boutique a été enregistrée
        if not self.shop_id:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord enregistrer la boutique avant d'ajouter des articles.")
            return
        
        dialog = InventoryItemEditor(self.db, self.shop_id)
        if dialog.exec():
            self.load_inventory()
            self.update_inventory_stats()
    
    def edit_inventory_item(self):
        """Modifie l'article sélectionné dans l'inventaire"""
        
        from .inventory_item_editor import InventoryItemEditor
        
        # Vérifier qu'un article est sélectionné
        selected_rows = self.inventory_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à modifier.")
            return
        
        # Récupérer l'ID de l'article sélectionné (sous forme de chaîne, pas d'entier)
        item_id = self.inventory_table.item(selected_rows[0].row(), 4).text()
        
        dialog = InventoryItemEditor(self.db, self.shop_id, item_id)
        if dialog.exec():
            # Recharger l'inventaire pour afficher les modifications
            self.load_inventory()
            # Mettre à jour les statistiques
            self.update_inventory_stats()
    
    def delete_inventory_item(self):
        """Supprime l'article sélectionné dans l'inventaire"""
        
        # Vérifier qu'un article est sélectionné
        selected_rows = self.inventory_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à supprimer.")
            return
        
        # Demander confirmation
        reply = QMessageBox.question(
            self, 
            "Confirmation", 
            "Êtes-vous sûr de vouloir supprimer cet article de l'inventaire ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Récupérer l'ID de l'article sélectionné (sous forme de chaîne, pas d'entier)
            item_id = self.inventory_table.item(selected_rows[0].row(), 4).text()
            
            # Supprimer l'article de la base de données
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM shop_inventory WHERE id = ?", (item_id,))
            self.db.conn.commit()
            
            # Recharger l'inventaire
            self.load_inventory()
            
            # Mettre à jour les statistiques
            self.update_inventory_stats()
    
    def show_inventory_context_menu(self, pos):
        """Affiche le menu contextuel pour l'inventaire"""
        
        # Vérifier qu'un article est sélectionné
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            return
        
        # Créer le menu contextuel
        context_menu = QMenu(self)
        
        # Actions
        edit_action = QAction("Modifier", self)
        edit_action.triggered.connect(self.edit_inventory_item)
        context_menu.addAction(edit_action)
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(self.delete_inventory_item)
        context_menu.addAction(delete_action)
        
        # Afficher le menu
        context_menu.exec(QCursor.pos())
    
    def update_inventory_stats(self):
        """Met à jour les statistiques d'inventaire affichées"""
        if not self.editing_mode:
            return  # Ne rien faire si on n'est pas en mode édition
            
        inventory_stats = self.get_inventory_stats()
        stats_label = self.findChild(QLabel, "inventory_stats_label")
        if stats_label:
            stats_label.setText(inventory_stats)
    
    def accept(self):
        """Enregistre les modifications"""
        
        # Validation des données
        if not self.name_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation", "Le nom de la boutique est obligatoire.")
            return
        
        cursor = self.db.conn.cursor()
        
        # Préparer les données
        shop_data = {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "shop_type": self.type_combo.currentText(),
            "location_id": self.location_combo.currentData(),
            "building_id": self.building_combo.currentData(),
            "owner_id": self.owner_combo.currentData(),
            "is_legal": self.legal_check.isChecked(),
            "price_modifier": self.price_modifier_spin.value(),
            "inventory_refresh_rate": self.refresh_rate_spin.value(),
            "world_id": self.world_id
        }
        
        if self.editing_mode:
            # Mettre à jour une boutique existante
            placeholders = ', '.join([f"{key} = ?" for key in shop_data.keys()])
            values = list(shop_data.values()) + [self.shop_id]
            
            cursor.execute(f'''
            UPDATE shops
            SET {placeholders}
            WHERE id = ?
            ''', values)
            
            logger.info(f"Boutique {self.shop_id} mise à jour")
        else:
            # Créer une nouvelle boutique
            shop_id = str(uuid.uuid4())
            shop_data["id"] = shop_id
            
            placeholders = ', '.join(['?'] * len(shop_data))
            columns = ', '.join(shop_data.keys())
            values = list(shop_data.values())
            
            cursor.execute(f'''
            INSERT INTO shops ({columns})
            VALUES ({placeholders})
            ''', values)
            
            self.shop_id = shop_id
            logger.info(f"Boutique {shop_id} créée")
        
        self.db.conn.commit()
        super().accept()
