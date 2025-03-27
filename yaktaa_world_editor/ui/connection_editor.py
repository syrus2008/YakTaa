#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de l'éditeur de connexions pour l'éditeur de monde YakTaa
"""

import logging
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QComboBox, 
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

logger = logging.getLogger(__name__)

class ConnectionEditor(QWidget):
    """Widget d'édition des connexions entre lieux"""
    
    def __init__(self, db, world_id):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.source_location_id = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Groupe de sélection de lieu source
        source_group = QGroupBox("Lieu de départ")
        source_layout = QFormLayout(source_group)
        
        self.source_combo = QComboBox()
        self.source_combo.currentIndexChanged.connect(self.on_source_changed)
        source_layout.addRow("Lieu de départ:", self.source_combo)
        
        main_layout.addWidget(source_group)
        
        # Tableau des connexions
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(5)
        self.connections_table.setHorizontalHeaderLabels([
            "Destination", "Type de voyage", "Temps (h)", "Coût", "Actions"
        ])
        self.connections_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.connections_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.connections_table)
        
        # Groupe d'ajout de connexion
        add_group = QGroupBox("Ajouter une connexion")
        add_layout = QFormLayout(add_group)
        
        self.target_combo = QComboBox()
        add_layout.addRow("Destination:", self.target_combo)
        
        self.travel_type_combo = QComboBox()
        self.travel_type_combo.addItems([
            "standard", "fast", "hidden", "secure", "expensive"
        ])
        add_layout.addRow("Type de voyage:", self.travel_type_combo)
        
        self.travel_time_spin = QDoubleSpinBox()
        self.travel_time_spin.setMinimum(0.1)
        self.travel_time_spin.setMaximum(100.0)
        self.travel_time_spin.setValue(1.0)
        self.travel_time_spin.setSingleStep(0.1)
        add_layout.addRow("Temps de voyage (h):", self.travel_time_spin)
        
        self.travel_cost_spin = QSpinBox()
        self.travel_cost_spin.setMinimum(0)
        self.travel_cost_spin.setMaximum(10000)
        self.travel_cost_spin.setValue(0)
        add_layout.addRow("Coût du voyage:", self.travel_cost_spin)
        
        add_button = QPushButton("Ajouter la connexion")
        add_button.clicked.connect(self.add_connection)
        add_layout.addRow(add_button)
        
        main_layout.addWidget(add_group)
        
        # Charger les lieux
        self.load_locations()
    
    def load_locations(self):
        """Charge la liste des lieux depuis la base de données"""
        
        self.source_combo.clear()
        self.target_combo.clear()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name, location_type
        FROM locations
        WHERE world_id = ?
        ORDER BY name
        """, (self.world_id,))
        
        locations = cursor.fetchall()
        
        for location in locations:
            # Ajouter au combo source
            self.source_combo.addItem(location["name"], location["id"])
            
            # Ajouter au combo cible
            self.target_combo.addItem(location["name"], location["id"])
    
    def on_source_changed(self, index):
        """Gère le changement de lieu source"""
        
        if index < 0:
            self.source_location_id = None
            return
        
        self.source_location_id = self.source_combo.itemData(index)
        self.load_connections()
    
    def set_source_location(self, location_id):
        """Définit le lieu source par son ID"""
        
        # Trouver l'index du lieu dans le combo
        for i in range(self.source_combo.count()):
            if self.source_combo.itemData(i) == location_id:
                self.source_combo.setCurrentIndex(i)
                break
    
    def load_connections(self):
        """Charge les connexions pour le lieu source actuel"""
        
        if not self.source_location_id:
            return
        
        # Effacer le tableau
        self.connections_table.setRowCount(0)
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT c.id, c.destination_id, c.travel_type, c.travel_time, c.travel_cost, l.name
        FROM connections c
        JOIN locations l ON c.destination_id = l.id
        WHERE c.source_id = ? AND c.world_id = ?
        ORDER BY l.name
        """, (self.source_location_id, self.world_id))
        
        connections = cursor.fetchall()
        
        # Remplir le tableau
        for i, connection in enumerate(connections):
            self.connections_table.insertRow(i)
            
            # Destination
            self.connections_table.setItem(i, 0, QTableWidgetItem(connection["name"]))
            
            # Type de voyage
            self.connections_table.setItem(i, 1, QTableWidgetItem(connection["travel_type"]))
            
            # Temps
            self.connections_table.setItem(i, 2, QTableWidgetItem(str(connection["travel_time"])))
            
            # Coût
            self.connections_table.setItem(i, 3, QTableWidgetItem(str(connection["travel_cost"])))
            
            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Modifier")
            edit_button.clicked.connect(lambda checked, conn_id=connection["id"]: self.edit_connection(conn_id))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("Supprimer")
            delete_button.clicked.connect(lambda checked, conn_id=connection["id"]: self.delete_connection(conn_id))
            actions_layout.addWidget(delete_button)
            
            self.connections_table.setCellWidget(i, 4, actions_widget)
            
            # Colorer en fonction du type de voyage
            color = self.get_travel_type_color(connection["travel_type"])
            for j in range(4):
                self.connections_table.item(i, j).setBackground(QBrush(color))
    
    def get_travel_type_color(self, travel_type):
        """Retourne la couleur associée au type de voyage"""
        
        color_map = {
            "standard": QColor(255, 255, 255),  # Blanc
            "fast": QColor(255, 230, 230),      # Rouge clair
            "hidden": QColor(230, 255, 230),    # Vert clair
            "secure": QColor(230, 230, 255),    # Bleu clair
            "expensive": QColor(255, 230, 255)  # Violet clair
        }
        
        return color_map.get(travel_type, QColor(255, 255, 255))
    
    def add_connection(self):
        """Ajoute une nouvelle connexion"""
        
        if not self.source_location_id:
            QMessageBox.warning(self, "Aucun lieu source", 
                               "Veuillez sélectionner un lieu de départ.")
            return
        
        # Récupérer les valeurs
        target_index = self.target_combo.currentIndex()
        if target_index < 0:
            QMessageBox.warning(self, "Aucune destination", 
                               "Veuillez sélectionner un lieu de destination.")
            return
        
        target_id = self.target_combo.itemData(target_index)
        
        # Vérifier que la source et la cible sont différentes
        if self.source_location_id == target_id:
            QMessageBox.warning(self, "Connexion invalide", 
                               "Le lieu de départ et de destination ne peuvent pas être identiques.")
            return
        
        # Vérifier que la connexion n'existe pas déjà
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id FROM connections
        WHERE source_id = ? AND destination_id = ? AND world_id = ?
        """, (self.source_location_id, target_id, self.world_id))
        
        if cursor.fetchone():
            QMessageBox.warning(self, "Connexion existante", 
                               "Une connexion existe déjà entre ces deux lieux.")
            return
        
        # Récupérer les autres valeurs
        travel_type = self.travel_type_combo.currentText()
        travel_time = self.travel_time_spin.value()
        travel_cost = self.travel_cost_spin.value()
        
        # Générer un nouvel ID
        connection_id = str(uuid.uuid4())
        
        # Insérer la connexion
        cursor.execute("""
        INSERT INTO connections (
            id, world_id, source_id, destination_id, travel_type, travel_time, travel_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            connection_id, self.world_id, self.source_location_id, target_id,
            travel_type, travel_time, travel_cost
        ))
        
        # Créer également la connexion inverse si le type est standard
        if travel_type == "standard":
            reverse_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO connections (
                id, world_id, source_id, destination_id, travel_type, travel_time, travel_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reverse_id, self.world_id, target_id, self.source_location_id,
                travel_type, travel_time, travel_cost
            ))
        
        self.db.conn.commit()
        
        # Rafraîchir la liste des connexions
        self.load_connections()
    
    def edit_connection(self, connection_id):
        """Modifie une connexion existante"""
        
        # Récupérer les données de la connexion
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT destination_id, travel_type, travel_time, travel_cost
        FROM connections
        WHERE id = ? AND world_id = ?
        """, (connection_id, self.world_id))
        
        connection = cursor.fetchone()
        
        if not connection:
            QMessageBox.warning(self, "Connexion introuvable", 
                               "La connexion sélectionnée n'a pas été trouvée.")
            return
        
        # Ouvrir une boîte de dialogue d'édition (à implémenter)
        QMessageBox.information(self, "Fonctionnalité à venir", 
                               "L'édition de connexions sera disponible dans une prochaine version.")
    
    def delete_connection(self, connection_id):
        """Supprime une connexion existante"""
        
        # Demander confirmation
        reply = QMessageBox.question(self, "Confirmation de suppression", 
                                    "Êtes-vous sûr de vouloir supprimer cette connexion ?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Supprimer la connexion
        cursor = self.db.conn.cursor()
        cursor.execute("DELETE FROM connections WHERE id = ? AND world_id = ?", 
                      (connection_id, self.world_id))
        
        self.db.conn.commit()
        
        # Rafraîchir la liste des connexions
        self.load_connections()
    
    def refresh(self):
        """Rafraîchit les données"""
        
        self.load_locations()
        
        if self.source_location_id:
            self.load_connections()
    
    def save(self):
        """Sauvegarde les modifications (non utilisé ici)"""
        pass
