#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de liste des objets pour l'éditeur de monde YakTaa
"""

import logging
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QMenu, QMessageBox, QDialog, QTabWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ui.item_editor import ItemEditor

# Configurer le logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ItemList")

class ItemList(QWidget):
    """Widget d'affichage et de gestion des objets d'un monde"""
    
    item_selected = pyqtSignal(str, str)  # Signal émis lors de la sélection d'un objet (ID, type)
    
    def __init__(self, db, world_id):
        super().__init__()
        
        logger.debug(f"Initialisation de ItemList avec world_id: {world_id}")
        self.world_id = world_id
        self.db = db
        logger.debug(f"Database instance: {self.db}")
        
        self.init_ui()
        
        # Charger les données initiales, un type à la fois
        for item_type in ["hardware", "consumable", "software", "weapon", "armor", "implant"]:
            logger.info(f"Chargement initial des objets de type {item_type}")
            self.load_items(item_type)
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Onglets pour différents types d'objets
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(True)  # Assurer que le widget à onglets est visible
        
        # Tab Hardware
        self.hardware_tab = QWidget()
        hardware_layout = QVBoxLayout(self.hardware_tab)
        self.hardware_tree = QTreeWidget()
        self.hardware_tree.setHeaderLabels(["Nom", "Type", "Qualité", "Niveau", "Légal", "Emplacement"])
        hardware_layout.addWidget(self.hardware_tree)
        self.tab_widget.addTab(self.hardware_tab, "Hardware")
        
        # Tab Consommables
        self.consumable_tab = QWidget()
        consumable_layout = QVBoxLayout(self.consumable_tab)
        self.consumable_tree = QTreeWidget()
        self.consumable_tree.setHeaderLabels(["Nom", "Type", "Rareté", "Durée", "Légal", "Emplacement"])
        consumable_layout.addWidget(self.consumable_tree)
        self.tab_widget.addTab(self.consumable_tab, "Consommables")
        
        # Tab Software
        self.software_tab = QWidget()
        software_layout = QVBoxLayout(self.software_tab)
        self.software_tree = QTreeWidget()
        self.software_tree.setHeaderLabels(["Nom", "Type", "Version", "Licence", "Légal", "Emplacement"])
        software_layout.addWidget(self.software_tree)
        self.tab_widget.addTab(self.software_tab, "Software")
        
        # Tab Armes
        self.weapon_tab = QWidget()
        weapon_layout = QVBoxLayout(self.weapon_tab)
        self.weapon_tree = QTreeWidget()
        self.weapon_tree.setHeaderLabels(["Nom", "Type", "Dégâts", "Rareté", "Légal", "Prix"])
        weapon_layout.addWidget(self.weapon_tree)
        self.tab_widget.addTab(self.weapon_tab, "Armes")
        
        # Tab Armures
        self.armor_tab = QWidget()
        armor_layout = QVBoxLayout(self.armor_tab)
        self.armor_tree = QTreeWidget()
        self.armor_tree.setHeaderLabels(["Nom", "Type", "Défense", "Rareté", "Légal", "Emplacement"])
        armor_layout.addWidget(self.armor_tree)
        self.tab_widget.addTab(self.armor_tab, "Armures")
        
        # Tab Implants
        self.implant_tab = QWidget()
        implant_layout = QVBoxLayout(self.implant_tab)
        self.implant_tree = QTreeWidget()
        self.implant_tree.setHeaderLabels(["Nom", "Type", "Emplacement", "Rareté", "Légal", "Localisation"])
        implant_layout.addWidget(self.implant_tree)
        self.tab_widget.addTab(self.implant_tab, "Implants")
        
        # Assurer que tous les arbres sont visibles
        for tree in [self.hardware_tree, self.consumable_tree, self.software_tree, 
                    self.weapon_tree, self.armor_tree, self.implant_tree]:
            tree.setVisible(True)
            tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            tree.setMinimumHeight(200)  # Définir une hauteur minimale
        
        # Assurer que tous les onglets sont visibles
        for tab in [self.hardware_tab, self.consumable_tab, self.software_tab,
                   self.weapon_tab, self.armor_tab, self.implant_tab]:
            tab.setVisible(True)
        
        # Ajouter le widget à onglets au layout principal
        main_layout.addWidget(self.tab_widget)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        # Bouton Ajouter
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.on_add_item)
        button_layout.addWidget(self.add_button)
        
        # Bouton Supprimer
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.on_delete_item)
        button_layout.addWidget(self.delete_button)
        
        # Bouton Éditer
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.on_edit_item)
        button_layout.addWidget(self.edit_button)
        
        # Ajouter le layout de boutons au layout principal
        main_layout.addLayout(button_layout)
        
        # Connexion des signaux
        self.hardware_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("hardware"))
        self.consumable_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("consumable"))
        self.software_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("software"))
        self.weapon_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("weapon"))
        self.armor_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("armor"))
        self.implant_tree.itemSelectionChanged.connect(lambda: self.on_item_selected("implant"))
        
        # Menu contextuel pour les arbres
        for tree in [self.hardware_tree, self.consumable_tree, self.software_tree, 
                    self.weapon_tree, self.armor_tree, self.implant_tree]:
            tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Définir le layout
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Sélectionner le premier onglet par défaut
        self.tab_widget.setCurrentIndex(0)
        
        # Forcer une mise à jour pour garantir l'affichage
        self.update()
        self.show()
    
    def on_tab_changed(self, index):
        """Gérer le changement d'onglet"""
        logger.debug(f"Changement d'onglet vers l'index {index}")
        tab_map = {
            0: "hardware",
            1: "consumable",
            2: "software",
            3: "weapon",
            4: "armor",
            5: "implant"
        }
        
        if index in tab_map:
            logger.debug(f"Chargement des objets pour l'onglet {tab_map[index]}")
            self.load_items(tab_map[index])
    
    def get_tree(self, item_type):
        """Retourne l'arbre correspondant au type d'objet"""
        tree = {
            "hardware": self.hardware_tree,
            "consumable": self.consumable_tree,
            "software": self.software_tree,
            "weapon": self.weapon_tree,
            "armor": self.armor_tree,
            "implant": self.implant_tree
        }.get(item_type)
        logger.debug(f"get_tree pour {item_type}: {'Trouvé' if tree else 'Non trouvé'}")
        return tree

    def load_items(self, item_type=None):
        """Charge la liste des objets depuis la base de données"""
        
        logger.info(f"--------- DÉBUT DU CHARGEMENT DES OBJETS DE TYPE {item_type} ---------")
        
        if item_type is None:
            item_type = self.get_current_item_type()
            logger.debug(f"Type d'objet non spécifié, utilisation du type courant: {item_type}")
        
        # Récupérer l'arbre correspondant au type d'objet
        tree = self.get_tree(item_type)
        if not tree:
            logger.error(f"Arbre non trouvé pour le type {item_type}")
            return
        
        # Vider l'arbre
        tree.clear()
        logger.debug(f"Arbre vidé pour le type {item_type}")
        
        # Table correspondant au type d'objet
        table_name = {
            "hardware": "hardware_items",
            "consumable": "consumable_items",
            "software": "software_items",
            "weapon": "weapon_items",
            "armor": "armors",
            "implant": "implant_items"
        }.get(item_type)
        
        logger.info(f"Chargement des objets depuis la table {table_name}")
        
        # Création d'une connexion directe à la base de données (pour éviter les problèmes avec self.db)
        logger.debug("Création d'une connexion directe à la base de données")
        conn = sqlite3.connect('worlds.db')
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            logger.error(f"La table {table_name} n'existe pas dans la base de données")
            conn.close()
            return
        
        # Vérifier les colonnes disponibles dans la table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"Colonnes disponibles dans {table_name}: {columns}")
        
        # Vérifier la présence de la colonne world_id
        if 'world_id' not in columns:
            logger.warning(f"La colonne world_id n'existe pas dans la table {table_name}")
        
        try:
            # Construire des requêtes adaptées à la structure réelle des tables
            if item_type == "hardware":
                query = f"""
                SELECT id, name, hardware_type, quality, level, is_legal,
                CASE 
                    WHEN location_type = 'device' THEN 'Appareil'
                    WHEN location_type = 'character' THEN 'Personnage'
                    WHEN location_type = 'building' THEN 'Bâtiment'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            elif item_type == "consumable":
                query = f"""
                SELECT id, name, 
                COALESCE(consumable_type, 'Inconnu') as c_type, 
                COALESCE(rarity, 'COMMON') as rarity,
                COALESCE(duration, 0) as duration,
                COALESCE(is_legal, 1) as is_legal,
                'Monde' as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            elif item_type == "software":
                query = f"""
                SELECT id, name, 
                COALESCE(software_type, 'Inconnu') as sw_type, 
                COALESCE(version, '1.0') as version,
                COALESCE(license_type, 'Standard') as license_type,
                COALESCE(is_legal, 1) as is_legal,
                'Monde' as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            elif item_type == "weapon":
                query = f"""
                SELECT id, name, 
                COALESCE(weapon_type, 'Inconnu') as w_type, 
                'Voir stats' as damage,
                COALESCE(rarity, 'COMMON') as rarity,
                COALESCE(is_legal, 1) as is_legal,
                COALESCE(price, 0) as price
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            elif item_type == "armor":
                query = f"""
                SELECT id, name, 
                'Armure' as ar_type, 
                COALESCE(defense, 0) as defense,
                COALESCE(rarity, 'COMMON') as rarity,
                1 as is_legal,
                COALESCE(location_type, 'Monde') as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            elif item_type == "implant":
                query = f"""
                SELECT id, name, 
                implant_type as imp_type, 
                body_location,
                rarity,
                is_legal,
                CASE 
                    WHEN location_type = 'character' THEN 'Personnage'
                    WHEN location_type = 'building' THEN 'Bâtiment'
                    WHEN location_type = 'shop' THEN 'Boutique'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            # Exécuter la requête avec les paramètres
            params = (self.world_id,)
            logger.debug(f"Requête SQL: {query}")
            logger.debug(f"Paramètres: {params}")
            
            cursor.execute(query, params)
            items = cursor.fetchall()
            logger.info(f"Nombre d'éléments récupérés: {len(items)}")
        
            if len(items) > 0:
                for i, item in enumerate(items[:5]):  # Limiter le logging aux 5 premiers items
                    logger.debug(f"Item {i}: {item}")
                
                for item in items:
                    item_id = item[0]
                    name = item[1]
                    
                    # Vérifier que le nom n'est pas vide
                    if not name:
                        logger.warning(f"L'item {item_id} a un nom vide, il sera ignoré")
                        continue
                    
                    list_item = QTreeWidgetItem([name])
                    
                    # Ajouter les colonnes supplémentaires en fonction du type d'objet
                    for i in range(2, len(item)):
                        value = item[i]
                        if value is None:
                            value = ""
                        elif isinstance(value, bool) or value == 0 or value == 1:
                            value = "Oui" if value else "Non"
                        list_item.setText(i-1, str(value))
                    
                    list_item.setData(0, Qt.ItemDataRole.UserRole, item_id)
                    tree.addTopLevelItem(list_item)
                
                logger.info(f"Chargé {len(items)} {item_type}")
                
                # Forcer l'affichage des éléments
                tree.update()
                tree.setVisible(True)
                if tree.parent():
                    tree.parent().setVisible(True)
                tree.expandAll()  # Développer tous les éléments
                
                # Vérifier le nombre d'éléments visibles
                logger.debug(f"Arbre {item_type} mis à jour avec {tree.topLevelItemCount()} éléments visibles")
                
                # Vérifier l'état de visibilité
                is_visible = tree.isVisible()
                parent_visible = True
                if isinstance(tree.parent(), QWidget):
                    parent_visible = tree.parent().isVisible()
                logger.debug(f"État de visibilité de l'arbre {item_type}: widget={is_visible}, parent={parent_visible}")
            else:
                logger.warning(f"Aucun élément trouvé pour le type {item_type}")
                
                # Essayons de vérifier s'il y a des éléments dans la table sans filtre
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"Nombre total d'éléments dans la table {table_name} (sans filtre): {count}")
                
                if count > 0 and 'world_id' in columns and self.world_id:
                    # Il y a des éléments mais ils n'ont peut-être pas le bon world_id
                    cursor.execute(f"SELECT DISTINCT world_id FROM {table_name}")
                    distinct_worlds = cursor.fetchall()
                    logger.info(f"World IDs existants dans la table {table_name}: {distinct_worlds}")
            
            # Fermer la connexion
            conn.close()
            logger.debug("Connexion à la base de données fermée")
        
        except sqlite3.Error as e:
            logger.error(f"Erreur SQL lors du chargement des {item_type}: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les {item_type}: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du chargement des {item_type}: {e}", exc_info=True)
            QMessageBox.warning(self, "Erreur", f"Erreur inattendue: {e}")
        
        logger.info(f"--------- FIN DU CHARGEMENT DES OBJETS DE TYPE {item_type} ---------")
    
    def get_current_item_type(self):
        """Retourne le type d'objet actuellement affiché"""
        
        current_index = self.tab_widget.currentIndex()
        return {
            0: "hardware",
            1: "consumable",
            2: "software",
            3: "weapon",
            4: "armor",
            5: "implant"
        }.get(current_index, "hardware")
    
    def on_item_clicked(self, item, column, item_type):
        """Gérer le clic sur un élément de la liste"""
        
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.item_selected.emit(item_id, item_type)
    
    def show_context_menu(self, pos):
        """Afficher le menu contextuel pour la liste des objets"""
        
        # Déterminer l'arbre qui a déclenché l'événement
        sending_widget = self.sender()
        
        # Déterminer le type d'élément en fonction de l'arbre
        item_type = None
        if sending_widget == self.hardware_tree:
            item_type = "hardware"
        elif sending_widget == self.consumable_tree:
            item_type = "consumable"
        elif sending_widget == self.software_tree:
            item_type = "software"
        elif sending_widget == self.weapon_tree:
            item_type = "weapon"
        elif sending_widget == self.armor_tree:
            item_type = "armor"
        elif sending_widget == self.implant_tree:
            item_type = "implant"
        
        if item_type:
            tree = sending_widget
            
            # Vérifier s'il y a un élément sous la position du clic
            item = tree.itemAt(pos)
            
            if item:
                # Menu pour un élément spécifique
                item_id = item.data(0, Qt.ItemDataRole.UserRole)
                item_name = item.text(0)
                
                menu = QMenu(self)
                
                edit_action = QAction("Éditer", self)
                edit_action.triggered.connect(lambda: self.edit_item(item_type, item_id))
                menu.addAction(edit_action)
                
                delete_action = QAction("Supprimer", self)
                delete_action.triggered.connect(lambda: self.delete_item(item_type, item_id, item_name))
                menu.addAction(delete_action)
                
                duplicate_action = QAction("Dupliquer", self)
                duplicate_action.triggered.connect(lambda: self.duplicate_item(item_type, item_id))
                menu.addAction(duplicate_action)
            else:
                # Menu général (aucun élément sélectionné)
                menu = QMenu(self)
                
                add_action = QAction("Ajouter", self)
                add_action.triggered.connect(lambda: self.add_item(item_type))
                menu.addAction(add_action)
                
                refresh_action = QAction("Actualiser", self)
                refresh_action.triggered.connect(lambda: self.load_items(item_type))
                menu.addAction(refresh_action)
            
            # Afficher le menu à la position du clic
            menu.exec(tree.mapToGlobal(pos))
    
    def on_add_item(self):
        """Ajouter un nouvel élément du type actuellement sélectionné"""
        current_index = self.tab_widget.currentIndex()
        item_types = ["hardware", "consumable", "software", "weapon", "armor", "implant"]
        if 0 <= current_index < len(item_types):
            item_type = item_types[current_index]
            logger.info(f"Ajout d'un élément de type {item_type}")
            
            # Ouvrir l'éditeur d'élément avec un nouvel élément vide
            editor = ItemEditor(self, self.db, item_type, None, self.world_id)
            if editor.exec() == QDialog.DialogCode.Accepted:
                # Actualiser la liste après l'ajout
                self.load_items(item_type)
    
    def on_delete_item(self):
        """Supprimer l'élément sélectionné"""
        current_index = self.tab_widget.currentIndex()
        item_types = ["hardware", "consumable", "software", "weapon", "armor", "implant"]
        if 0 <= current_index < len(item_types):
            item_type = item_types[current_index]
            tree = self.get_tree(item_type)
            
            if tree and tree.selectedItems():
                selected_item = tree.selectedItems()[0]
                item_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
                item_name = selected_item.text(0)
                
                # Demander confirmation
                reply = QMessageBox.question(
                    self, 
                    "Confirmation de suppression",
                    f"Êtes-vous sûr de vouloir supprimer {item_name} ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    logger.info(f"Suppression de l'élément {item_id} ({item_name}) de type {item_type}")
                    try:
                        # Déterminer la table en fonction du type
                        table_name = {
                            "hardware": "hardware_items",
                            "consumable": "consumable_items",
                            "software": "software_items",
                            "weapon": "weapon_items",
                            "armor": "armors",
                            "implant": "implant_items"
                        }.get(item_type)
                        
                        # Exécuter la requête de suppression
                        conn = sqlite3.connect('worlds.db')
                        cursor = conn.cursor()
                        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
                        conn.commit()
                        conn.close()
                        
                        # Actualiser la liste
                        self.load_items(item_type)
                        
                        QMessageBox.information(self, "Suppression réussie", f"{item_name} a été supprimé avec succès.")
                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression de l'élément: {e}")
                        QMessageBox.critical(self, "Erreur de suppression", f"Impossible de supprimer l'élément: {e}")
    
    def on_edit_item(self):
        """Éditer l'élément sélectionné"""
        current_index = self.tab_widget.currentIndex()
        item_types = ["hardware", "consumable", "software", "weapon", "armor", "implant"]
        if 0 <= current_index < len(item_types):
            item_type = item_types[current_index]
            tree = self.get_tree(item_type)
            
            if tree and tree.selectedItems():
                selected_item = tree.selectedItems()[0]
                item_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
                
                logger.info(f"Édition de l'élément {item_id} de type {item_type}")
                
                # Ouvrir l'éditeur d'élément avec l'élément sélectionné
                editor = ItemEditor(self, self.db, item_type, item_id, self.world_id)
                if editor.exec() == QDialog.DialogCode.Accepted:
                    # Actualiser la liste après l'édition
                    self.load_items(item_type)
    
    def on_item_selected(self, item_type):
        """Gérer la sélection d'un élément dans un arbre"""
        tree = self.get_tree(item_type)
        if tree and tree.selectedItems():
            selected_item = tree.selectedItems()[0]
            item_id = selected_item.data(0, Qt.ItemDataRole.UserRole)
            item_name = selected_item.text(0)
            
            logger.info(f"Élément sélectionné: {item_name} ({item_id}) de type {item_type}")
            
            # Émettre le signal avec l'ID de l'élément et son type
            self.item_selected.emit(item_id, item_type)
    
    def add_item(self, item_type):
        """Ajouter un nouvel objet"""
        
        dialog = ItemEditor(self.db, self.world_id, item_type=item_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_items(item_type)
    
    def edit_item(self, item_type, item_id):
        """Modifier un objet existant"""
        
        dialog = ItemEditor(self.db, self.world_id, item_id=item_id, item_type=item_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_items(item_type)
    
    def clone_item(self, item_type, item_id):
        """Dupliquer un objet existant"""
        
        confirm = QMessageBox.question(
            self, "Confirmation", 
            f"Êtes-vous sûr de vouloir dupliquer cet objet?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Implémentation de la duplication
            import uuid
            new_id = str(uuid.uuid4())
            cursor = self.db.conn.cursor()
            
            table_name = {
                "hardware": "hardware_items",
                "consumable": "consumable_items",
                "software": "software_items",
                "weapon": "weapon_items",
                "armor": "armors",
                "implant": "implant_items"
            }.get(item_type)
            
            # Récupérer les données de l'objet original
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (item_id,))
            original_item = cursor.fetchone()
            
            if original_item:
                # Créer un dictionnaire avec les colonnes et valeurs, en excluant l'ID
                columns = [column for column in original_item.keys() if column != "id"]
                values = [original_item[column] for column in columns]
                
                # Ajouter la colonne ID et sa valeur
                columns.append("id")
                values.append(new_id)
                
                # Modifier le nom pour indiquer qu'il s'agit d'une copie
                name_index = columns.index("name")
                values[name_index] = f"{values[name_index]} (copie)"
                
                # Construire la requête INSERT
                placeholders = ", ".join(["?" for _ in columns])
                columns_str = ", ".join(columns)
                
                cursor.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", values)
                self.db.conn.commit()
                
                # Recharger la liste
                self.load_items(item_type)
                logger.info(f"Objet {item_id} dupliqué vers {new_id}")
    
    def delete_item(self, item_type, item_id, item_name):
        """Supprimer un objet"""
        
        confirm = QMessageBox.question(
            self, "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer cet objet?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            
            # Déterminer la table en fonction du type
            table_name = {
                "hardware": "hardware_items",
                "consumable": "consumable_items",
                "software": "software_items",
                "weapon": "weapon_items",
                "armor": "armors",
                "implant": "implant_items"
            }.get(item_type)
            
            # Supprimer l'objet de la base de données
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
            self.db.conn.commit()
            
            # Recharger la liste
            self.load_items(item_type)
            logger.info(f"Objet {item_id} supprimé")
    
    def refresh(self):
        """Rafraîchir la liste des objets"""
        current_tab = self.tab_widget.currentIndex()
        item_types = ["hardware", "consumable", "software", "weapon", "armor", "implant"]
        
        # Rafraîchir tous les types d'objets
        for item_type in item_types:
            self.load_items(item_type)
    
    def save(self):
        """Sauvegarder les modifications (pas d'opération spécifique ici car tout est sauvegardé immédiatement)"""
        self.db.conn.commit()
