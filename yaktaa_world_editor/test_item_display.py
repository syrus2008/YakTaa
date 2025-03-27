#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'affichage des objets dans l'éditeur YakTaa
"""

import sys
import sqlite3
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ItemDisplayTest')

class ItemDisplayTest(QMainWindow):
    """Fenêtre de test pour l'affichage des objets"""
    
    def __init__(self):
        super().__init__()
        
        # ID du monde à tester
        self.world_id = "e456e121-333f-4395-8d1a-cf2c19e67a0b"
        
        self.setWindowTitle("Test d'affichage des objets YakTaa")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Informations de diagnostic
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Initialisation...")
        info_layout.addWidget(self.info_label)
        main_layout.addLayout(info_layout)
        
        # Onglets
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Créer les onglets pour chaque type d'objet
        self.setup_tab("hardware", "Hardware", ["Nom", "Type", "Qualité", "Niveau", "Légal", "Emplacement"])
        self.setup_tab("consumable", "Consommables", ["Nom", "Type", "Rareté", "Durée", "Légal", "Emplacement"])
        self.setup_tab("software", "Software", ["Nom", "Type", "Version", "Licence", "Légal", "Emplacement"])
        self.setup_tab("weapon", "Armes", ["Nom", "Type", "Dégâts", "Rareté", "Légal", "Prix"])
        self.setup_tab("armor", "Armures", ["Nom", "Type", "Défense", "Rareté", "Légal", "Emplacement"])
        self.setup_tab("implant", "Implants", ["Nom", "Type", "Emplacement", "Rareté", "Légal", "Localisation"])
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Charger tous les objets")
        self.load_button.clicked.connect(self.load_all_items)
        button_layout.addWidget(self.load_button)
        
        self.count_button = QPushButton("Afficher les compteurs")
        self.count_button.clicked.connect(self.display_counts)
        button_layout.addWidget(self.count_button)
        
        main_layout.addLayout(button_layout)
        
        # Charger les données initiales
        self.load_all_items()
    
    def setup_tab(self, item_type, tab_name, headers):
        """Configure un onglet pour un type d'objet spécifique"""
        
        # Widget de l'onglet
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # Arbre pour afficher les objets
        tree = QTreeWidget()
        tree.setHeaderLabels(headers)
        tree.setColumnWidth(0, 200)
        tree.setColumnWidth(1, 100)
        
        # Stocker l'arbre dans un attribut dynamique de l'instance
        setattr(self, f"{item_type}_tree", tree)
        
        tab_layout.addWidget(tree)
        
        # Ajouter l'onglet
        self.tab_widget.addTab(tab_widget, tab_name)
    
    def get_tree(self, item_type):
        """Retourne l'arbre correspondant au type d'objet"""
        return getattr(self, f"{item_type}_tree", None)
    
    def load_all_items(self):
        """Charge tous les types d'objets"""
        
        total_items = 0
        for item_type in ["hardware", "consumable", "software", "weapon", "armor", "implant"]:
            count = self.load_items(item_type)
            total_items += count
        
        self.info_label.setText(f"Chargement terminé. Total: {total_items} objets.")
    
    def display_counts(self):
        """Affiche le nombre d'éléments chargés dans chaque arbre"""
        
        counts = []
        for item_type in ["hardware", "consumable", "software", "weapon", "armor", "implant"]:
            tree = self.get_tree(item_type)
            if tree:
                count = tree.topLevelItemCount()
                counts.append(f"{item_type}: {count}")
        
        self.info_label.setText(" | ".join(counts))
    
    def load_items(self, item_type):
        """Charge les objets d'un type spécifique"""
        
        logger.info(f"Chargement des objets de type {item_type}...")
        
        tree = self.get_tree(item_type)
        if not tree:
            logger.error(f"Arbre non trouvé pour le type {item_type}")
            return 0
        
        # Vider l'arbre
        tree.clear()
        
        # Table correspondant au type d'objet
        table_name = {
            "hardware": "hardware_items",
            "consumable": "consumable_items",
            "software": "software_items",
            "weapon": "weapon_items",
            "armor": "armors",
            "implant": "implant_items"
        }.get(item_type)
        
        try:
            # Connexion à la base de données
            conn = sqlite3.connect('worlds.db')
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                logger.error(f"La table {table_name} n'existe pas")
                conn.close()
                return 0
            
            # Vérifier les colonnes disponibles
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            logger.debug(f"Colonnes disponibles: {columns}")
            
            # Construire la requête SQL en fonction du type d'objet
            if item_type == "hardware":
                query = f"""
                SELECT id, name, hardware_type as hw_type, quality, level, is_legal,
                CASE 
                    WHEN building_id IS NOT NULL THEN 'Bâtiment'
                    WHEN character_id IS NOT NULL THEN 'Personnage'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            elif item_type == "consumable":
                query = f"""
                SELECT id, name, consumable_type as c_type, rarity, duration, is_legal,
                CASE 
                    WHEN building_id IS NOT NULL THEN 'Bâtiment'
                    WHEN character_id IS NOT NULL THEN 'Personnage'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            elif item_type == "software":
                query = f"""
                SELECT id, name, software_type as sw_type, version, license_type, is_legal,
                CASE 
                    WHEN building_id IS NOT NULL THEN 'Bâtiment'
                    WHEN character_id IS NOT NULL THEN 'Personnage'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            elif item_type == "weapon":
                query = f"""
                SELECT id, name, weapon_type as w_type, damage, rarity, is_legal, price
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            elif item_type == "armor":
                query = f"""
                SELECT id, name, 'Armure' as ar_type, defense, rarity, is_legal,
                CASE 
                    WHEN building_id IS NOT NULL THEN 'Bâtiment'
                    WHEN character_id IS NOT NULL THEN 'Personnage'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            elif item_type == "implant":
                query = f"""
                SELECT id, name, implant_type as imp_type, body_location, rarity, is_legal,
                CASE 
                    WHEN building_id IS NOT NULL THEN 'Bâtiment'
                    WHEN character_id IS NOT NULL THEN 'Personnage'
                    ELSE 'Monde'
                END as location
                FROM {table_name}
                WHERE world_id = ?
                ORDER BY name
                """
            
            # Exécuter la requête
            cursor.execute(query, (self.world_id,))
            items = cursor.fetchall()
            
            logger.info(f"Nombre d'éléments récupérés: {len(items)}")
            
            # Ajouter les éléments à l'arbre
            for item in items:
                item_id = item[0]
                name = item[1]
                
                list_item = QTreeWidgetItem([name])
                
                # Ajouter les colonnes supplémentaires
                for i in range(2, len(item)):
                    value = item[i]
                    if value is None:
                        value = ""
                    elif isinstance(value, bool) or value == 0 or value == 1:
                        value = "Oui" if value else "Non"
                    list_item.setText(i-1, str(value))
                
                list_item.setData(0, Qt.ItemDataRole.UserRole, item_id)
                tree.addTopLevelItem(list_item)
            
            conn.close()
            
            # Mettre à jour l'interface
            tree.update()
            
            return len(items)
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des {item_type}: {e}", exc_info=True)
            return 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ItemDisplayTest()
    window.show()
    sys.exit(app.exec())
