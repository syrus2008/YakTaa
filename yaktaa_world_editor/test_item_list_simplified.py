#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simplifié pour le chargement et l'affichage des objets dans la classe ItemList
"""

import sys
import logging
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QTabWidget, QWidget
from PyQt6.QtCore import Qt

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ItemListTest')

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test d'affichage des objets")
        self.setGeometry(100, 100, 800, 600)
        self.world_id = "e456e121-333f-4395-8d1a-cf2c19e67a0b"  # ID du monde actuel
        
        # Créer un widget central et un layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Créer un widget à onglets
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Créer des onglets pour chaque type d'objet
        self.trees = {}
        
        # Hardware
        hardware_widget = QWidget()
        hardware_layout = QVBoxLayout(hardware_widget)
        self.hardware_tree = QTreeWidget()
        self.hardware_tree.setHeaderLabels(["Nom", "Type", "Qualité", "Niveau", "Légal", "Emplacement"])
        hardware_layout.addWidget(self.hardware_tree)
        tab_widget.addTab(hardware_widget, "Hardware")
        self.trees["hardware"] = self.hardware_tree
        
        # Weapons
        weapon_widget = QWidget()
        weapon_layout = QVBoxLayout(weapon_widget)
        self.weapon_tree = QTreeWidget()
        self.weapon_tree.setHeaderLabels(["Nom", "Type", "Dégâts", "Rareté", "Légal", "Prix"])
        weapon_layout.addWidget(self.weapon_tree)
        tab_widget.addTab(weapon_widget, "Armes")
        self.trees["weapon"] = self.weapon_tree
        
        # Implants
        implant_widget = QWidget()
        implant_layout = QVBoxLayout(implant_widget)
        self.implant_tree = QTreeWidget()
        self.implant_tree.setHeaderLabels(["Nom", "Type", "Emplacement", "Rareté", "Légal", "Localisation"])
        implant_layout.addWidget(self.implant_tree)
        tab_widget.addTab(implant_widget, "Implants")
        self.trees["implant"] = self.implant_tree
        
        # Armures
        armor_widget = QWidget()
        armor_layout = QVBoxLayout(armor_widget)
        self.armor_tree = QTreeWidget()
        self.armor_tree.setHeaderLabels(["Nom", "Type", "Défense", "Rareté", "Légal", "Localisation"])
        armor_layout.addWidget(self.armor_tree)
        tab_widget.addTab(armor_widget, "Armures")
        self.trees["armor"] = self.armor_tree
        
        # Chargement des données
        self.load_all_items()
    
    def load_all_items(self):
        """Charge tous les types d'objets"""
        logger.info("Chargement de tous les types d'objets")
        item_types = ["hardware", "weapon", "implant", "armor"]
        for item_type in item_types:
            self.load_items(item_type)
    
    def load_items(self, item_type):
        """Charge les objets du type spécifié"""
        logger.info(f"Chargement des objets de type {item_type}")
        
        # Récupérer l'arbre correspondant au type d'objet
        tree = self.trees.get(item_type)
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
        
        try:
            # Connexion à la base de données
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
            
            # Vérifier le nombre d'éléments dans la table sans filtre
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            logger.info(f"Nombre total d'éléments dans la table {table_name}: {total_count}")
            
            # Vérifier les world_ids disponibles
            cursor.execute(f"SELECT DISTINCT world_id FROM {table_name}")
            world_ids = cursor.fetchall()
            logger.info(f"World IDs disponibles: {[w[0] for w in world_ids]}")
            
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
                tree.expandAll()  # Développer tous les éléments
                
                # Vérifier le nombre d'éléments visibles
                logger.debug(f"Arbre {item_type} mis à jour avec {tree.topLevelItemCount()} éléments visibles")
            else:
                logger.warning(f"Aucun élément trouvé pour le type {item_type} avec world_id={self.world_id}")
            
            # Fermer la connexion
            conn.close()
            logger.debug("Connexion à la base de données fermée")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur SQL lors du chargement des {item_type}: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du chargement des {item_type}: {e}", exc_info=True)
        
        logger.info(f"--------- FIN DU CHARGEMENT DES OBJETS DE TYPE {item_type} ---------")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
