#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'onglet principal pour l'affichage et l'édition d'un monde
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QSplitter, QTreeWidget, 
    QTreeWidgetItem, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent

from ui.map_view import MapView
from ui.location_list import LocationList
from ui.character_list import CharacterList
from ui.device_list import DeviceList
from ui.building_list import BuildingList
from ui.file_list import FileList
from ui.shop_list import ShopList
from ui.item_list import ItemList
from ui.connection_editor import ConnectionEditor
from ui.mission_list import MissionList
from ui.faction_list import FactionList
from ui.weapon_list import WeaponList
from ui.armor_list import ArmorList
from ui.software_list import SoftwareList
from ui.implant_list import ImplantList
from ui.vulnerability_list import VulnerabilityList
from ui.network_list import NetworkList
from ui.food_list import FoodList

logger = logging.getLogger(__name__)

class WorldTab(QWidget):
    """Onglet principal pour l'affichage et l'édition d'un monde"""
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        
        self.init_ui()
        self.load_world_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Splitter principal
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Partie gauche : liste des éléments
        self.elements_widget = QTabWidget()
        
        # Onglet des lieux
        self.location_list = LocationList(self.db, self.world_id)
        self.location_list.location_selected.connect(self.on_location_selected)
        self.elements_widget.addTab(self.location_list, "Lieux")
        
        # Onglet des bâtiments
        self.building_list = BuildingList(self.db, self.world_id)
        self.elements_widget.addTab(self.building_list, "Bâtiments")
        
        # Onglet des personnages
        self.character_list = CharacterList(self.db, self.world_id)
        self.elements_widget.addTab(self.character_list, "Personnages")
        
        # Onglet des factions
        self.faction_list = FactionList(self.db, self.world_id)
        self.elements_widget.addTab(self.faction_list, "Factions")
        
        # Onglet des appareils
        self.device_list = DeviceList(self.db, self.world_id)
        self.elements_widget.addTab(self.device_list, "Appareils")
        
        # Onglet des fichiers
        self.file_list = FileList(self.db, self.world_id)
        self.elements_widget.addTab(self.file_list, "Fichiers")
        
        # Onglet des magasins
        self.shop_list = ShopList(self.db, self.world_id)
        self.elements_widget.addTab(self.shop_list, "Magasins")
        
        # Onglet des objets
        self.item_list = ItemList(self.db, self.world_id)
        self.elements_widget.addTab(self.item_list, "Objets")
        
        # Onglet des armes
        self.weapon_list = WeaponList(self.db, self.world_id)
        self.elements_widget.addTab(self.weapon_list, "Armes")
        
        # Onglet des armures
        self.armor_list = ArmorList(self.db, self.world_id)
        self.elements_widget.addTab(self.armor_list, "Armures")
        
        # Onglet des aliments
        self.food_list = FoodList(self.db, self.world_id)
        self.elements_widget.addTab(self.food_list, "Aliments")
        
        # Onglet des logiciels
        self.software_list = SoftwareList(self.db, self.world_id)
        self.elements_widget.addTab(self.software_list, "Logiciels")
        
        # Onglet des implants
        self.implant_list = ImplantList(self.db, self.world_id)
        self.elements_widget.addTab(self.implant_list, "Implants")
        
        # Onglet des vulnérabilités
        self.vulnerability_list = VulnerabilityList(self.db, self.world_id)
        self.elements_widget.addTab(self.vulnerability_list, "Vulnérabilités")
        
        # Onglet des réseaux informatiques
        self.network_list = NetworkList(self.db, self.world_id)
        self.elements_widget.addTab(self.network_list, "Réseaux")
        
        # Onglet des missions
        self.mission_list = MissionList(self.db, self.world_id)
        self.elements_widget.addTab(self.mission_list, "Missions")
        
        self.main_splitter.addWidget(self.elements_widget)
        
        # Partie droite : vue de la carte et détails
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        
        # Vue de la carte
        self.map_view = MapView(self.db, self.world_id)
        self.map_view.location_clicked.connect(self.on_map_location_clicked)
        right_layout.addWidget(self.map_view)
        
        # Onglets de détails
        self.details_tabs = QTabWidget()
        
        # Onglet des connexions
        self.connection_editor = ConnectionEditor(self.db, self.world_id)
        self.details_tabs.addTab(self.connection_editor, "Connexions")
        
        right_layout.addWidget(self.details_tabs)
        
        self.main_splitter.addWidget(self.right_widget)
        
        # Définir les tailles initiales du splitter
        self.main_splitter.setSizes([300, 700])
        
        main_layout.addWidget(self.main_splitter)
        
        # Barre d'actions en bas
        actions_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.refresh)
        actions_layout.addWidget(refresh_button)
        
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save)
        actions_layout.addWidget(save_button)
        
        actions_layout.addStretch()
        
        main_layout.addLayout(actions_layout)
    
    def load_world_data(self):
        """Charge les données du monde"""
        
        # Charger les informations de base du monde
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM worlds WHERE id = ?", (self.world_id,))
        self.world_data = cursor.fetchone()
        
        if not self.world_data:
            logger.error(f"Impossible de trouver le monde avec l'ID {self.world_id}")
            return
        
        # Mettre à jour les composants
        self.refresh()
    
    def refresh(self):
        """Rafraîchit tous les composants de l'onglet"""
        
        # Liste des composants à rafraîchir avec gestion d'erreur
        components = [
            self.location_list,
            self.building_list,
            self.character_list,
            self.faction_list,
            self.device_list,
            self.file_list,
            self.shop_list,
            self.item_list,
            self.weapon_list,
            self.map_view,
            self.connection_editor,
            self.mission_list,
            self.armor_list,
            self.software_list,
            self.implant_list,
            self.vulnerability_list,
            self.network_list,
            self.food_list
        ]
        
        # Rafraîchir tous les composants avec un mécanisme de sécurité
        for component in components:
            try:
                # Vérifier si le composant a une méthode refresh
                if hasattr(component, 'refresh'):
                    component.refresh()
                # Sinon, essayer les alternatives connues
                elif hasattr(component, 'load_shops'):  # Pour ShopList
                    component.load_shops()
                elif hasattr(component, 'load_items'):  # Pour ItemList
                    component.load_items()
            except Exception as e:
                # Log d'erreur sans faire échouer l'application
                logger.error(f"Erreur lors du rafraîchissement du composant {component.__class__.__name__}: {e}")
    
    def save(self):
        """Sauvegarde les modifications apportées au monde"""
        
        # Liste des composants à sauvegarder avec gestion d'erreur
        components = [
            self.location_list,
            self.building_list,
            self.character_list,
            self.faction_list,
            self.device_list,
            self.file_list,
            self.shop_list,
            self.item_list,
            self.weapon_list,
            self.connection_editor,
            self.mission_list,
            self.armor_list,
            self.software_list,
            self.implant_list,
            self.vulnerability_list,
            self.network_list,
            self.food_list
        ]
        
        # Sauvegarder tous les composants avec un mécanisme de sécurité
        for component in components:
            try:
                # Vérifier si le composant a une méthode save
                if hasattr(component, 'save'):
                    component.save()
                # Sinon, essayer les alternatives connues
                elif hasattr(component, 'db') and hasattr(component.db, 'conn'):
                    # Commit direct sur la base de données
                    component.db.conn.commit()
            except Exception as e:
                # Log d'erreur sans faire échouer l'application
                logger.error(f"Erreur lors de la sauvegarde du composant {component.__class__.__name__}: {e}")
        
        # Mettre à jour la carte
        try:
            self.map_view.refresh()
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de la carte: {e}")
    
    def on_location_selected(self, location_id):
        """Gère la sélection d'un lieu dans la liste"""
        
        # Mettre à jour la carte pour mettre en évidence le lieu sélectionné
        self.map_view.highlight_location(location_id)
        
        # Mettre à jour l'éditeur de connexions pour afficher les connexions du lieu sélectionné
        self.connection_editor.set_source_location(location_id)
        
        # Mettre à jour la liste des bâtiments pour afficher uniquement ceux du lieu sélectionné
        self.building_list.location_id = location_id
        self.building_list.refresh()
        
        # Changer l'onglet pour afficher les bâtiments
        if self.elements_widget.currentIndex() == 0:  # Si on est sur l'onglet des lieux
            self.elements_widget.setCurrentIndex(1)   # Passer à l'onglet des bâtiments

    def on_map_location_clicked(self, location_id):
        """Gère le clic sur un lieu dans la carte"""
        
        # Sélectionner le lieu dans la liste
        self.location_list.select_location(location_id)
        
        # Mettre à jour l'éditeur de connexions
        self.connection_editor.set_source_location(location_id)
