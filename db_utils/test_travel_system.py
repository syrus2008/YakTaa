"""
Script de test pour le système de déplacement et la gestion des bâtiments dans YakTaa
Ce script permet de tester les fonctionnalités avancées de déplacement et d'exploration
urbaine dans le jeu YakTaa.
"""

import logging
import sys
import os
import time
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QComboBox, 
                           QTableWidget, QTableWidgetItem, QTabWidget, 
                           QTextEdit, QGridLayout, QScrollArea, QFrame,
                           QSplitter, QTreeWidget, QTreeWidgetItem, QGroupBox)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("YakTaa.TestTravelSystem")

# Importer les modules YakTaa
from yaktaa.game import Game
from yaktaa.world.world_manager import WorldManager
from yaktaa.world.travel import TravelSystem, CityManager, Building, BuildingType, TravelMethod, WeatherCondition
from yaktaa.world.building_generator import BuildingGenerator, populate_location_with_buildings

class TravelTestWindow(QMainWindow):
    """
    Fenêtre de test pour le système de déplacement et la gestion des bâtiments
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YakTaa - Test du système de déplacement")
        self.setGeometry(100, 100, 1280, 800)
        
        # Initialiser le jeu et le monde
        self.game = Game()
        self.world_manager = WorldManager(self.game)
        
        # Initialiser le système de déplacement et le gestionnaire de villes
        self.city_manager = CityManager(self.world_manager.world_map)
        self.travel_system = TravelSystem(self.world_manager.world_map)
        
        # Générer des bâtiments pour les lieux existants
        self._generate_buildings()
        
        # Créer l'interface utilisateur
        self._create_ui()
        
        # Mettre à jour l'interface avec les données initiales
        self._update_ui()
        
        # Timer pour les mises à jour périodiques (conditions météo, etc.)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(10000)  # Mise à jour toutes les 10 secondes
        
        logger.info("Fenêtre de test du système de déplacement initialisée")
    
    def _generate_buildings(self):
        """Génère des bâtiments pour les lieux existants"""
        # Générer des bâtiments pour les lieux principaux
        for location_id in self.world_manager.world_map.locations:
            location = self.world_manager.world_map.get_location(location_id)
            if not location.parent_location_id:  # Lieu principal (ville)
                # Générer entre 5 et 15 bâtiments
                num_buildings = random.randint(5, 15)
                populate_location_with_buildings(self.city_manager, location_id, num_buildings)
            elif location.parent_location_id:  # District
                # Générer entre 3 et 8 bâtiments
                num_buildings = random.randint(3, 8)
                populate_location_with_buildings(self.city_manager, location_id, num_buildings)
        
        logger.info(f"Bâtiments générés pour {len(self.city_manager.buildings)} lieux")
    
    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # En-tête
        header_layout = QHBoxLayout()
        title_label = QLabel("YakTaa - Système de déplacement avancé")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Splitter principal (carte à gauche, détails à droite)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter, 1)
        
        # Panneau de gauche (carte et navigation)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Informations sur le lieu actuel
        current_location_group = QGroupBox("Lieu actuel")
        current_location_layout = QVBoxLayout(current_location_group)
        self.current_location_name = QLabel("Nom: ")
        self.current_location_desc = QLabel("Description: ")
        self.current_location_desc.setWordWrap(True)
        self.current_location_info = QLabel("Informations: ")
        current_location_layout.addWidget(self.current_location_name)
        current_location_layout.addWidget(self.current_location_desc)
        current_location_layout.addWidget(self.current_location_info)
        left_layout.addWidget(current_location_group)
        
        # Destinations disponibles
        destinations_group = QGroupBox("Destinations disponibles")
        destinations_layout = QVBoxLayout(destinations_group)
        
        # Tableau des destinations
        self.destinations_table = QTableWidget()
        self.destinations_table.setColumnCount(5)
        self.destinations_table.setHorizontalHeaderLabels(["Destination", "Méthode", "Temps", "Coût", "Risque"])
        self.destinations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.destinations_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.destinations_table.cellClicked.connect(self._destination_selected)
        destinations_layout.addWidget(self.destinations_table)
        
        # Bouton de voyage
        travel_button = QPushButton("Voyager vers la destination sélectionnée")
        travel_button.clicked.connect(self._travel_to_selected)
        destinations_layout.addWidget(travel_button)
        
        left_layout.addWidget(destinations_group)
        
        # Panneau de droite (détails et bâtiments)
        right_panel = QTabWidget()
        
        # Onglet des bâtiments
        buildings_tab = QWidget()
        buildings_layout = QVBoxLayout(buildings_tab)
        
        # Liste des bâtiments
        buildings_group = QGroupBox("Bâtiments dans ce lieu")
        buildings_group_layout = QVBoxLayout(buildings_group)
        
        self.buildings_tree = QTreeWidget()
        self.buildings_tree.setHeaderLabels(["Nom", "Type", "Sécurité"])
        self.buildings_tree.setColumnWidth(0, 200)
        self.buildings_tree.itemClicked.connect(self._building_selected)
        buildings_group_layout.addWidget(self.buildings_tree)
        
        buildings_layout.addWidget(buildings_group)
        
        # Détails du bâtiment sélectionné
        self.building_details_group = QGroupBox("Détails du bâtiment")
        building_details_layout = QVBoxLayout(self.building_details_group)
        self.building_name = QLabel("Nom: ")
        self.building_desc = QLabel("Description: ")
        self.building_desc.setWordWrap(True)
        self.building_info = QLabel("Informations: ")
        building_details_layout.addWidget(self.building_name)
        building_details_layout.addWidget(self.building_desc)
        building_details_layout.addWidget(self.building_info)
        
        # Liste des pièces
        self.rooms_tree = QTreeWidget()
        self.rooms_tree.setHeaderLabels(["Pièce", "Étage", "Accès"])
        building_details_layout.addWidget(self.rooms_tree)
        
        buildings_layout.addWidget(self.building_details_group)
        
        # Onglet des conditions
        conditions_tab = QWidget()
        conditions_layout = QVBoxLayout(conditions_tab)
        
        # Conditions météorologiques
        weather_group = QGroupBox("Conditions météorologiques")
        weather_layout = QVBoxLayout(weather_group)
        self.weather_table = QTableWidget()
        self.weather_table.setColumnCount(3)
        self.weather_table.setHorizontalHeaderLabels(["Lieu", "Météo", "Congestion"])
        self.weather_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        weather_layout.addWidget(self.weather_table)
        conditions_layout.addWidget(weather_group)
        
        # Historique de voyage
        history_group = QGroupBox("Historique de voyage")
        history_layout = QVBoxLayout(history_group)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["De", "Vers", "Méthode", "Temps", "Coût"])
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        history_layout.addWidget(self.history_table)
        conditions_layout.addWidget(history_group)
        
        # Ajouter les onglets
        right_panel.addTab(buildings_tab, "Bâtiments")
        right_panel.addTab(conditions_tab, "Conditions & Historique")
        
        # Ajouter les panneaux au splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])
        
        # Barre de statut
        self.statusBar().showMessage("Prêt")
    
    def _update_ui(self):
        """Met à jour l'interface utilisateur avec les données actuelles"""
        # Mettre à jour les informations sur le lieu actuel
        current_location = self.world_manager.get_current_location()
        if current_location:
            self.current_location_name.setText(f"Nom: {current_location.name}")
            self.current_location_desc.setText(f"Description: {current_location.description}")
            self.current_location_info.setText(
                f"Sécurité: {current_location.security_level}/10 | "
                f"Population: {current_location.population:,} | "
                f"Services: {', '.join(current_location.services)}"
            )
            
            # Mettre à jour les destinations disponibles
            self._update_destinations()
            
            # Mettre à jour les bâtiments
            self._update_buildings()
        
        # Mettre à jour les conditions météorologiques
        self._update_weather_conditions()
        
        # Mettre à jour l'historique de voyage
        self._update_travel_history()
    
    def _update_destinations(self):
        """Met à jour la liste des destinations disponibles"""
        current_location_id = self.world_manager.current_location_id
        if not current_location_id:
            return
        
        # Récupérer les routes disponibles
        available_routes = self.travel_system.get_available_routes(current_location_id)
        
        # Effacer le tableau
        self.destinations_table.setRowCount(0)
        
        # Remplir le tableau avec les destinations
        row = 0
        for dest_id, routes in available_routes.items():
            for route in routes:
                dest_location = self.world_manager.world_map.get_location(dest_id)
                if not dest_location:
                    continue
                
                self.destinations_table.insertRow(row)
                
                # Nom de la destination
                self.destinations_table.setItem(row, 0, QTableWidgetItem(dest_location.name))
                
                # Méthode de voyage
                self.destinations_table.setItem(row, 1, QTableWidgetItem(route.method.name))
                
                # Temps de voyage
                actual_time = self.travel_system.calculate_actual_travel_time(route)
                self.destinations_table.setItem(row, 2, QTableWidgetItem(f"{actual_time:.1f} h"))
                
                # Coût du voyage
                actual_cost = self.travel_system.calculate_actual_travel_cost(route)
                self.destinations_table.setItem(row, 3, QTableWidgetItem(f"{actual_cost} ¥"))
                
                # Risque de sécurité
                self.destinations_table.setItem(row, 4, QTableWidgetItem(f"{route.security_risk}/10"))
                
                # Stocker l'ID de destination et l'index de route dans les données de l'élément
                self.destinations_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, (dest_id, routes.index(route)))
                
                row += 1
        
        # Ajuster les colonnes
        self.destinations_table.resizeColumnsToContents()
    
    def _update_buildings(self):
        """Met à jour la liste des bâtiments dans le lieu actuel"""
        current_location_id = self.world_manager.current_location_id
        if not current_location_id:
            return
        
        # Effacer l'arbre des bâtiments
        self.buildings_tree.clear()
        
        # Récupérer les bâtiments dans le lieu actuel
        buildings = self.city_manager.get_buildings_in_location(current_location_id)
        
        # Ajouter les bâtiments à l'arbre
        for building in buildings:
            item = QTreeWidgetItem(self.buildings_tree)
            item.setText(0, building.name)
            item.setText(1, building.building_type.name)
            item.setText(2, f"{building.security_level}/10")
            
            # Stocker l'ID du bâtiment dans les données de l'élément
            item.setData(0, Qt.ItemDataRole.UserRole, building.id)
            
            # Ajouter des informations supplémentaires
            services_item = QTreeWidgetItem(item)
            services_item.setText(0, f"Services: {', '.join(building.services)}")
            
            owner_item = QTreeWidgetItem(item)
            owner_item.setText(0, f"Propriétaire: {building.owner}")
            
            access_item = QTreeWidgetItem(item)
            access_status = "Accessible"
            if not building.is_accessible:
                access_status = "Accès restreint"
            if building.requires_special_access:
                access_status += " (Nécessite un accès spécial)"
            if building.requires_hacking:
                access_status += " (Nécessite du hacking)"
            access_item.setText(0, f"Accès: {access_status}")
        
        # Développer le premier niveau
        self.buildings_tree.expandToDepth(0)
    
    def _update_weather_conditions(self):
        """Met à jour l'affichage des conditions météorologiques"""
        # Effacer le tableau
        self.weather_table.setRowCount(0)
        
        # Remplir le tableau avec les conditions météorologiques
        row = 0
        for location_id, weather in self.travel_system.current_weather.items():
            location = self.world_manager.world_map.get_location(location_id)
            if not location:
                continue
            
            self.weather_table.insertRow(row)
            
            # Nom du lieu
            self.weather_table.setItem(row, 0, QTableWidgetItem(location.name))
            
            # Conditions météorologiques
            self.weather_table.setItem(row, 1, QTableWidgetItem(weather.name))
            
            # Niveau de congestion
            congestion = self.travel_system.congestion_levels.get(location_id, 0.0)
            congestion_text = f"{congestion:.2f}"
            if congestion < 0.3:
                congestion_text += " (Fluide)"
            elif congestion < 0.6:
                congestion_text += " (Modéré)"
            else:
                congestion_text += " (Congestionné)"
            self.weather_table.setItem(row, 2, QTableWidgetItem(congestion_text))
            
            row += 1
        
        # Ajuster les colonnes
        self.weather_table.resizeColumnsToContents()
    
    def _update_travel_history(self):
        """Met à jour l'affichage de l'historique de voyage"""
        # Récupérer l'historique de voyage
        history = self.travel_system.get_travel_history()
        
        # Effacer le tableau
        self.history_table.setRowCount(0)
        
        # Remplir le tableau avec l'historique
        for i, record in enumerate(history):
            self.history_table.insertRow(i)
            
            # Lieu de départ
            source_location = self.world_manager.world_map.get_location(record["source_id"])
            self.history_table.setItem(i, 0, QTableWidgetItem(source_location.name if source_location else record["source_id"]))
            
            # Lieu d'arrivée
            dest_location = self.world_manager.world_map.get_location(record["destination_id"])
            self.history_table.setItem(i, 1, QTableWidgetItem(dest_location.name if dest_location else record["destination_id"]))
            
            # Méthode de voyage
            self.history_table.setItem(i, 2, QTableWidgetItem(record["method"].name))
            
            # Temps de voyage
            self.history_table.setItem(i, 3, QTableWidgetItem(f"{record['time']:.1f} h"))
            
            # Coût du voyage
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{record['cost']} ¥"))
        
        # Ajuster les colonnes
        self.history_table.resizeColumnsToContents()
    
    def _destination_selected(self, row, column):
        """Gère la sélection d'une destination dans le tableau"""
        # Récupérer l'ID de destination et l'index de route
        item = self.destinations_table.item(row, 0)
        if not item:
            return
        
        dest_id, route_index = item.data(Qt.ItemDataRole.UserRole)
        dest_location = self.world_manager.world_map.get_location(dest_id)
        if not dest_location:
            return
        
        # Afficher des informations sur la destination dans la barre de statut
        self.statusBar().showMessage(f"Destination sélectionnée: {dest_location.name} - {dest_location.description}")
    
    def _travel_to_selected(self):
        """Effectue un voyage vers la destination sélectionnée"""
        # Récupérer la ligne sélectionnée
        selected_rows = self.destinations_table.selectionModel().selectedRows()
        if not selected_rows:
            self.statusBar().showMessage("Aucune destination sélectionnée")
            return
        
        row = selected_rows[0].row()
        item = self.destinations_table.item(row, 0)
        if not item:
            return
        
        # Récupérer l'ID de destination et l'index de route
        dest_id, route_index = item.data(Qt.ItemDataRole.UserRole)
        
        # Effectuer le voyage
        current_location_id = self.world_manager.current_location_id
        result = self.travel_system.travel(current_location_id, dest_id, route_index)
        
        if result["success"]:
            # Mettre à jour la position du joueur dans le gestionnaire de monde
            self.world_manager.travel_to(dest_id)
            
            # Mettre à jour l'interface
            self._update_ui()
            
            # Afficher un message de succès
            self.statusBar().showMessage(
                f"Voyage réussi vers {self.world_manager.world_map.get_location(dest_id).name} "
                f"en {result['actual_time']:.1f} heures pour {result['actual_cost']} crédits"
            )
        else:
            self.statusBar().showMessage(f"Échec du voyage: {result['message']}")
    
    def _building_selected(self, item, column):
        """Gère la sélection d'un bâtiment dans l'arbre"""
        # Vérifier si c'est un élément de premier niveau (bâtiment)
        if item.parent() is None:
            # Récupérer l'ID du bâtiment
            building_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not building_id:
                return
            
            # Récupérer le bâtiment
            building = self.city_manager.get_building(building_id)
            if not building:
                return
            
            # Mettre à jour les détails du bâtiment
            self.building_name.setText(f"Nom: {building.name}")
            self.building_desc.setText(f"Description: {building.description}")
            self.building_info.setText(
                f"Type: {building.building_type.name} | "
                f"Sécurité: {building.security_level}/10 | "
                f"Étages: {building.floors} | "
                f"Propriétaire: {building.owner}"
            )
            
            # Mettre à jour la liste des pièces
            self.rooms_tree.clear()
            
            # Organiser les pièces par étage
            rooms_by_floor = {}
            for room_id, room in building.rooms.items():
                floor = room["floor"]
                if floor not in rooms_by_floor:
                    rooms_by_floor[floor] = []
                rooms_by_floor[floor].append((room_id, room))
            
            # Ajouter les pièces à l'arbre, organisées par étage
            for floor in sorted(rooms_by_floor.keys()):
                floor_item = QTreeWidgetItem(self.rooms_tree)
                floor_item.setText(0, f"Étage {floor}")
                
                for room_id, room in rooms_by_floor[floor]:
                    room_item = QTreeWidgetItem(floor_item)
                    room_item.setText(0, room["name"])
                    room_item.setText(1, str(room["floor"]))
                    
                    access_status = "Accessible"
                    if not room["is_accessible"]:
                        access_status = "Restreint"
                    if room["requires_hacking"]:
                        access_status += " (Hacking)"
                    
                    room_item.setText(2, access_status)
            
            # Développer l'arbre des pièces
            self.rooms_tree.expandAll()
    
    def _periodic_update(self):
        """Effectue des mises à jour périodiques de l'interface"""
        # Mettre à jour les conditions météorologiques et de congestion
        self._update_weather_conditions()
        
        # Mettre à jour les temps et coûts de voyage
        self._update_destinations()
        
        # Afficher un message dans la barre de statut
        self.statusBar().showMessage("Conditions mises à jour", 3000)


def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    window = TravelTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
