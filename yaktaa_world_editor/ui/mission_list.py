#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion des missions pour l'éditeur de monde YakTaa
"""

import logging
import json
import uuid
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit,
                             QMenu, QMessageBox, QDialog, QFormLayout, QTextEdit, QCheckBox, QSpinBox,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCursor

from database import get_database

logger = logging.getLogger(__name__)

class MissionList(QWidget):
    """Widget de gestion des missions pour l'éditeur de monde YakTaa"""
    
    # Signaux
    mission_added = pyqtSignal(str)  # ID de la mission ajoutée
    mission_edited = pyqtSignal(str)  # ID de la mission modifiée
    mission_deleted = pyqtSignal(str)  # ID de la mission supprimée
    mission_updated = pyqtSignal(str)  # ID de la mission mise à jour
    
    def __init__(self, db, world_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.world_id = world_id
        self.setup_ui()
        
        # Initialisation des données
        self.missions = {}  # Dictionnaire des missions (clé: id, valeur: données de mission)
        
        # Si un world_id est fourni, charger les missions
        if self.world_id:
            self.load_missions()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        
        # En-tête avec titre et filtres
        header_layout = QHBoxLayout()
        
        header_label = QLabel("<h2>Missions</h2>")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Filtres
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", None)
        self.type_filter.addItems(["infiltration", "récupération", "hacking", "protection", 
                                  "livraison", "élimination", "sabotage", "espionnage", 
                                  "escorte", "investigation"])
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        header_layout.addWidget(QLabel("Type:"))
        header_layout.addWidget(self.type_filter)
        
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItem("Toutes les difficultés", None)
        self.difficulty_filter.addItems(["facile", "moyen", "difficile", "très difficile", "extrême"])
        self.difficulty_filter.currentIndexChanged.connect(self.apply_filters)
        header_layout.addWidget(QLabel("Difficulté:"))
        header_layout.addWidget(self.difficulty_filter)
        
        self.main_quest_filter = QComboBox()
        self.main_quest_filter.addItem("Toutes les missions", None)
        self.main_quest_filter.addItem("Quêtes principales", 1)
        self.main_quest_filter.addItem("Quêtes secondaires", 0)
        self.main_quest_filter.currentIndexChanged.connect(self.apply_filters)
        header_layout.addWidget(QLabel("Type:"))
        header_layout.addWidget(self.main_quest_filter)
        
        # Recherche
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher une mission...")
        self.search_edit.textChanged.connect(self.filter_missions)
        header_layout.addWidget(self.search_edit)
        
        main_layout.addLayout(header_layout)
        
        # Liste des missions (TreeWidget)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Titre", "Type", "Difficulté", "Quest", "Objectifs", "Donneur", "Lieu"])
        self.tree.setColumnWidth(0, 250)  # Titre
        self.tree.setColumnWidth(1, 100)  # Type
        self.tree.setColumnWidth(2, 100)  # Difficulté
        self.tree.setColumnWidth(3, 80)   # Quest
        self.tree.setColumnWidth(4, 80)   # Objectifs
        self.tree.setColumnWidth(5, 120)  # Donneur
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        main_layout.addWidget(self.tree)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Ajouter une mission")
        self.add_btn.clicked.connect(self.add_mission)
        button_layout.addWidget(self.add_btn)
        
        self.random_btn = QPushButton("Générer aléatoirement")
        self.random_btn.clicked.connect(self.add_random_mission)
        button_layout.addWidget(self.random_btn)
        
        self.edit_btn = QPushButton("Éditer")
        self.edit_btn.clicked.connect(self.edit_mission)
        button_layout.addWidget(self.edit_btn)
        
        self.objectives_btn = QPushButton("Gérer les objectifs")
        self.objectives_btn.clicked.connect(self.manage_objectives)
        button_layout.addWidget(self.objectives_btn)
        
        self.delete_btn = QPushButton("Supprimer")
        self.delete_btn.clicked.connect(self.delete_mission)
        button_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.load_missions)
        button_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_missions(self):
        """Charger les missions depuis la base de données"""
        try:
            # Effacer les éléments existants
            self.tree.clear()
            
            # Créer des groupes pour chaque type de mission
            types = {}
            difficulty_order = {
                "facile": 0,
                "moyen": 1,
                "difficile": 2,
                "très difficile": 3,
                "extrême": 4
            }
            
            # Obtenir les missions depuis la base de données
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
            SELECT m.id, m.title, m.description, m.mission_type, m.difficulty, 
                   m.is_main_quest, m.is_repeatable, m.is_hidden, m.rewards, m.metadata,
                   m.giver_id, m.location_id,
                   c.name as giver_name, l.name as location_name,
                   (SELECT COUNT(*) FROM objectives WHERE mission_id = m.id) as objective_count
            FROM missions m
            LEFT JOIN characters c ON m.giver_id = c.id
            LEFT JOIN locations l ON m.location_id = l.id
            WHERE m.world_id = ?
            ORDER BY m.is_main_quest DESC, m.mission_type, 
                     CASE 
                         WHEN m.difficulty = 'facile' THEN 1
                         WHEN m.difficulty = 'moyen' THEN 2
                         WHEN m.difficulty = 'difficile' THEN 3
                         WHEN m.difficulty = 'très difficile' THEN 4
                         WHEN m.difficulty = 'extrême' THEN 5
                         ELSE 6
                     END, 
                     m.title
            ''', (self.world_id,))
            
            missions = cursor.fetchall()
            
            # Regrouper les missions par type
            for mission in missions:
                mission_type = mission['mission_type']
                
                # Filtrage
                if self.type_filter.currentData() and mission_type != self.type_filter.currentData():
                    continue
                
                if self.difficulty_filter.currentData() and mission['difficulty'] != self.difficulty_filter.currentData():
                    continue
                
                if self.main_quest_filter.currentData() is not None and mission['is_main_quest'] != self.main_quest_filter.currentData():
                    continue
                
                # Créer le groupe s'il n'existe pas
                if mission_type not in types:
                    type_item = QTreeWidgetItem(self.tree)
                    type_item.setText(0, mission_type.capitalize())
                    type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    type_item.setExpanded(True)
                    types[mission_type] = {}
                
                # Sous-groupe par difficulté
                difficulty = mission['difficulty']
                if difficulty not in types[mission_type]:
                    diff_item = QTreeWidgetItem(types[mission_type].get('__item__', self.tree))
                    diff_item.setText(0, f"Difficulté: {difficulty}")
                    diff_item.setFlags(diff_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    diff_item.setExpanded(True)
                    types[mission_type][difficulty] = diff_item
                
                # Ajouter la mission
                mission_item = QTreeWidgetItem(types[mission_type][difficulty])
                mission_item.setText(0, mission['title'])
                mission_item.setText(1, mission_type)
                mission_item.setText(2, difficulty)
                mission_item.setText(3, "Principale" if mission['is_main_quest'] == 1 else "Secondaire")
                mission_item.setText(4, str(mission['objective_count']))
                mission_item.setText(5, mission['giver_name'] if mission['giver_name'] else "Aucun")
                mission_item.setText(6, mission['location_name'] if mission['location_name'] else "Aucun")
                
                # Stocker les données complètes de la mission avec l'élément pour référence
                mission_item.setData(0, Qt.ItemDataRole.UserRole, mission)
            
            logger.info(f"Chargé {len(missions)} missions pour le monde {self.world_id}")
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des missions: {e}")
    
    def apply_filters(self):
        """Appliquer les filtres de type, difficulté et quête principale"""
        self.type_filter = self.type_filter.currentData()
        self.difficulty_filter = self.difficulty_filter.currentData()
        self.main_quest_filter = self.main_quest_filter.currentData()
        
        # Recharger les missions avec les filtres appliqués
        self.load_missions()
    
    def filter_missions(self):
        """Filtrer les missions par texte de recherche"""
        search_text = self.search_edit.text().lower()
        
        def process_item(item):
            # Si c'est un élément de mission (pas un groupe)
            if item.data(0, Qt.ItemDataRole.UserRole):
                # Vérifier si le terme de recherche est dans le titre ou le type
                title = item.text(0).lower()
                mission_type = item.text(1).lower()
                show = search_text in title or search_text in mission_type
                item.setHidden(not show)
                return show
            
            # C'est un groupe ou un sous-groupe
            show_children = False
            for i in range(item.childCount()):
                if process_item(item.child(i)):
                    show_children = True
            
            # Ne montrer le groupe que s'il a des enfants visibles
            item.setHidden(not show_children)
            return show_children
        
        # Parcourir tous les éléments de premier niveau
        for i in range(self.tree.topLevelItemCount()):
            process_item(self.tree.topLevelItem(i))
    
    def show_context_menu(self, position):
        """Afficher le menu contextuel pour une mission"""
        item = self.tree.itemAt(position)
        if not item or not item.data(0, Qt.ItemDataRole.UserRole):
            return
        
        mission = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Créer le menu contextuel
        context_menu = QMenu(self)
        
        edit_action = QAction("Éditer la mission", self)
        edit_action.triggered.connect(lambda: self.edit_mission(mission))
        context_menu.addAction(edit_action)
        
        objectives_action = QAction("Gérer les objectifs", self)
        objectives_action.triggered.connect(lambda: self.manage_objectives(mission))
        context_menu.addAction(objectives_action)
        
        context_menu.addSeparator()
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_mission(mission))
        context_menu.addAction(delete_action)
        
        # Afficher le menu
        context_menu.exec(QCursor.pos())
    
    def on_item_double_clicked(self, item, column):
        """Gérer le double-clic sur un élément"""
        mission = item.data(0, Qt.ItemDataRole.UserRole)
        if mission:
            self.edit_mission(mission)
    
    def add_mission(self):
        """Ajouter une nouvelle mission"""
        dialog = MissionEditDialog(self, world_id=self.world_id)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mission_id = dialog.save_mission()
            if mission_id:
                self.load_missions()
                self.mission_added.emit(mission_id)
                logger.info(f"Mission ajoutée: {mission_id}")
    
    def add_random_mission(self):
        """Ajouter une mission générée aléatoirement"""
        dialog = RandomMissionDialog(self, world_id=self.world_id)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mission_id = dialog.generate_mission()
            if mission_id:
                self.load_missions()
                self.mission_added.emit(mission_id)
                QMessageBox.information(self, "Mission générée", "Une nouvelle mission a été générée avec succès.")
                logger.info(f"Mission aléatoire générée: {mission_id}")
    
    def edit_mission(self, mission=None):
        """Éditer une mission existante"""
        # Si aucune mission n'est spécifiée, utiliser la sélection actuelle
        if not mission:
            selected_items = self.tree.selectedItems()
            if not selected_items or not selected_items[0].data(0, Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une mission à éditer.")
                return
            mission = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir le dialogue d'édition
        dialog = MissionEditDialog(self, world_id=self.world_id, mission=mission)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mission_id = dialog.save_mission()
            if mission_id:
                self.load_missions()
                self.mission_edited.emit(mission_id)
                logger.info(f"Mission éditée: {mission_id}")
    
    def manage_objectives(self, mission=None):
        """Gérer les objectifs d'une mission"""
        # Si aucune mission n'est spécifiée, utiliser la sélection actuelle
        if not mission:
            selected_items = self.tree.selectedItems()
            if not selected_items or not selected_items[0].data(0, Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une mission pour gérer ses objectifs.")
                return
            mission = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Ouvrir le dialogue de gestion des objectifs
        dialog = ObjectiveManagerDialog(
            self, 
            world_id=self.world_id, 
            mission_id=mission['id'], 
            mission_title=mission['title']
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_missions()  # Recharger pour mettre à jour le nombre d'objectifs
            self.mission_updated.emit(mission['id'])
    
    def delete_mission(self, mission=None):
        """Supprimer une mission"""
        # Si aucune mission n'est spécifiée, utiliser la sélection actuelle
        if not mission:
            selected_items = self.tree.selectedItems()
            if not selected_items or not selected_items[0].data(0, Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une mission à supprimer.")
                return
            mission = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Demander confirmation
        response = QMessageBox.question(
            self, 
            "Confirmer la suppression", 
            f"Êtes-vous sûr de vouloir supprimer la mission '{mission['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.Yes:
            # Supprimer la mission
            try:
                cursor = self.db.conn.cursor()
                
                # Supprimer d'abord les objectifs associés
                cursor.execute("DELETE FROM objectives WHERE mission_id = ?", (mission['id'],))
                
                # Puis supprimer la mission
                cursor.execute("DELETE FROM missions WHERE id = ?", (mission['id'],))
                
                self.db.conn.commit()
                
                # Rafraîchir la liste
                self.load_missions()
                self.mission_deleted.emit(mission['id'])
                
                logger.info(f"Mission supprimée: {mission['id']}")
            except Exception as e:
                self.db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de la mission: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer la mission: {e}")
    
    def refresh(self):
        """Rafraîchir l'affichage"""
        self.load_missions()
    
    def save_changes(self):
        """Cette méthode est requise pour l'interface avec WorldTab
        Mais toutes les modifications sont enregistrées immédiatement"""
        pass


class MissionEditDialog(QDialog):
    """Dialogue pour ajouter ou éditer une mission"""
    
    def __init__(self, parent=None, world_id=None, mission=None):
        super().__init__(parent)
        self.world_id = world_id
        self.mission = mission  # None pour une nouvelle mission, sinon les données de la mission existante
        self.setup_ui()
        
        # Si on édite une mission existante, remplir les champs
        if self.mission:
            self.load_mission_data()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        self.setWindowTitle("Ajouter une mission" if not self.mission else "Éditer la mission")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_layout = QFormLayout()
        
        # Titre
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Entrez le titre de la mission")
        form_layout.addRow("Titre:", self.title_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez la description de la mission")
        self.description_edit.setMinimumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        # Type de mission
        self.mission_type_combo = QComboBox()
        self.mission_type_combo.addItems(["infiltration", "récupération", "hacking", "protection", 
                                       "livraison", "élimination", "sabotage", "espionnage", 
                                       "escorte", "investigation"])
        form_layout.addRow("Type de mission:", self.mission_type_combo)
        
        # Difficulté
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["facile", "moyen", "difficile", "très difficile", "extrême"])
        form_layout.addRow("Difficulté:", self.difficulty_combo)
        
        # Quête principale
        self.is_main_quest_check = QCheckBox("Cette mission fait partie de la quête principale")
        form_layout.addRow("", self.is_main_quest_check)
        
        # Options avancées
        self.is_repeatable_check = QCheckBox("Mission répétible")
        form_layout.addRow("", self.is_repeatable_check)
        
        self.is_hidden_check = QCheckBox("Mission cachée (découvrable uniquement via certaines actions)")
        form_layout.addRow("", self.is_hidden_check)
        
        # Localisation et donneur de mission
        self.location_combo = QComboBox()
        self.load_locations()
        form_layout.addRow("Lieu:", self.location_combo)
        
        self.giver_combo = QComboBox()
        self.load_characters()
        form_layout.addRow("Donneur de mission:", self.giver_combo)
        
        # Récompenses
        rewards_layout = QHBoxLayout()
        
        self.credits_spin = QSpinBox()
        self.credits_spin.setMinimum(0)
        self.credits_spin.setMaximum(100000)
        self.credits_spin.setSingleStep(100)
        self.credits_spin.setValue(1000)
        rewards_layout.addWidget(QLabel("Crédits:"))
        rewards_layout.addWidget(self.credits_spin)
        
        self.items_spin = QSpinBox()
        self.items_spin.setMinimum(0)
        self.items_spin.setMaximum(10)
        self.items_spin.setValue(1)
        rewards_layout.addWidget(QLabel("Objets:"))
        rewards_layout.addWidget(self.items_spin)
        
        self.reputation_spin = QSpinBox()
        self.reputation_spin.setMinimum(0)
        self.reputation_spin.setMaximum(100)
        self.reputation_spin.setValue(5)
        rewards_layout.addWidget(QLabel("Réputation:"))
        rewards_layout.addWidget(self.reputation_spin)
        
        form_layout.addRow("Récompenses:", rewards_layout)
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_locations(self):
        """Charger les lieux depuis la base de données"""
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            cursor.execute('''
            SELECT id, name FROM locations WHERE world_id = ? ORDER BY name
            ''', (self.world_id,))
            
            locations = cursor.fetchall()
            
            self.location_combo.clear()
            self.location_combo.addItem("Aucun", None)
            
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des lieux: {e}")
    
    def load_characters(self):
        """Charger les personnages depuis la base de données"""
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            cursor.execute('''
            SELECT id, name FROM characters WHERE world_id = ? ORDER BY name
            ''', (self.world_id,))
            
            characters = cursor.fetchall()
            
            self.giver_combo.clear()
            self.giver_combo.addItem("Aucun", None)
            
            for character in characters:
                self.giver_combo.addItem(character['name'], character['id'])
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des personnages: {e}")
    
    def load_mission_data(self):
        """Charger les données de la mission dans les champs du formulaire"""
        if not self.mission:
            return
        
        # Définir les valeurs de base
        self.title_edit.setText(self.mission['title'])
        self.description_edit.setText(self.mission['description'])
        
        # Sélectionner le type de mission
        index = self.mission_type_combo.findText(self.mission['mission_type'])
        if index >= 0:
            self.mission_type_combo.setCurrentIndex(index)
        
        # Sélectionner la difficulté
        index = self.difficulty_combo.findText(self.mission['difficulty'])
        if index >= 0:
            self.difficulty_combo.setCurrentIndex(index)
        
        # Options
        self.is_main_quest_check.setChecked(self.mission['is_main_quest'] == 1)
        self.is_repeatable_check.setChecked(self.mission['is_repeatable'] == 1)
        self.is_hidden_check.setChecked(self.mission['is_hidden'] == 1)
        
        # Lieu
        if self.mission['location_id']:
            index = self.location_combo.findData(self.mission['location_id'])
            if index >= 0:
                self.location_combo.setCurrentIndex(index)
        
        # Donneur de mission
        if self.mission['giver_id']:
            index = self.giver_combo.findData(self.mission['giver_id'])
            if index >= 0:
                self.giver_combo.setCurrentIndex(index)
        
        # Récompenses
        try:
            rewards = json.loads(self.mission['rewards'])
            self.credits_spin.setValue(rewards.get('credits', 0))
            self.items_spin.setValue(rewards.get('items', 0))
            self.reputation_spin.setValue(rewards.get('reputation', 0))
        except Exception as e:
            logger.error(f"Erreur lors du chargement des récompenses: {e}")
    
    def save_mission(self):
        """Sauvegarder la mission dans la base de données"""
        # Récupérer les données du formulaire
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        mission_type = self.mission_type_combo.currentText()
        difficulty = self.difficulty_combo.currentText()
        is_main_quest = 1 if self.is_main_quest_check.isChecked() else 0
        is_repeatable = 1 if self.is_repeatable_check.isChecked() else 0
        is_hidden = 1 if self.is_hidden_check.isChecked() else 0
        
        location_id = self.location_combo.currentData()
        giver_id = self.giver_combo.currentData()
        
        rewards = {
            'credits': self.credits_spin.value(),
            'items': self.items_spin.value(),
            'reputation': self.reputation_spin.value()
        }
        
        # Valider les données
        if not title:
            QMessageBox.warning(self, "Champs manquants", "Veuillez entrer un titre pour la mission.")
            return None
        
        if not description:
            QMessageBox.warning(self, "Champs manquants", "Veuillez entrer une description pour la mission.")
            return None
        
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            if self.mission:  # Modification d'une mission existante
                mission_id = self.mission['id']
                
                cursor.execute('''
                UPDATE missions
                SET title = ?, description = ?, mission_type = ?, difficulty = ?,
                    is_main_quest = ?, is_repeatable = ?, is_hidden = ?,
                    location_id = ?, giver_id = ?, rewards = ?
                WHERE id = ?
                ''', (
                    title, description, mission_type, difficulty,
                    is_main_quest, is_repeatable, is_hidden,
                    location_id, giver_id, json.dumps(rewards),
                    mission_id
                ))
                
                logger.info(f"Mission mise à jour: {mission_id}")
            
            else:  # Nouvelle mission
                mission_id = str(uuid.uuid4())
                
                cursor.execute('''
                INSERT INTO missions (id, world_id, title, description, mission_type, difficulty,
                                   is_main_quest, is_repeatable, is_hidden,
                                   location_id, giver_id, rewards)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mission_id, self.world_id, title, description, mission_type, difficulty,
                    is_main_quest, is_repeatable, is_hidden,
                    location_id, giver_id, json.dumps(rewards)
                ))
                
                logger.info(f"Nouvelle mission créée: {mission_id}")
            
            db.conn.commit()
            return mission_id
        
        except Exception as e:
            db.conn.rollback()
            logger.error(f"Erreur lors de l'enregistrement de la mission: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer la mission: {e}")
            return None


class ObjectiveManagerDialog(QDialog):
    """Dialogue pour gérer les objectifs d'une mission"""
    
    def __init__(self, parent=None, world_id=None, mission_id=None, mission_title=None):
        super().__init__(parent)
        self.world_id = world_id
        self.mission_id = mission_id
        self.mission_title = mission_title
        self.setup_ui()
        self.load_objectives()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        self.setWindowTitle(f"Objectifs de la mission: {self.mission_title}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Liste des objectifs
        self.objective_tree = QTreeWidget()
        self.objective_tree.setHeaderLabels(["Titre", "Type", "Obligatoire", "Cible", "Description"])
        self.objective_tree.setColumnWidth(0, 200)
        self.objective_tree.setColumnWidth(1, 100)
        self.objective_tree.setColumnWidth(2, 80)
        self.objective_tree.setColumnWidth(3, 150)
        self.objective_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.objective_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.objective_tree.itemDoubleClicked.connect(self.edit_objective)
        layout.addWidget(self.objective_tree)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ajouter un objectif")
        self.add_button.clicked.connect(self.add_objective)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Éditer")
        self.edit_button.clicked.connect(self.edit_objective)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_objective)
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.load_objectives)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # Boutons de dialogue
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def load_objectives(self):
        """Charger les objectifs de la mission depuis la base de données"""
        if not self.mission_id:
            return
        
        # Vider l'arbre
        self.objective_tree.clear()
        
        # Récupérer les objectifs depuis la base de données
        db = get_database()
        cursor = db.conn.cursor()
        
        try:
            cursor.execute('''
            SELECT o.id, o.title, o.description, o.objective_type, o.target_id, o.target_count,
                   o.is_optional, o.order_index, o.completion_script,
                   CASE 
                     WHEN o.target_id IS NOT NULL AND o.objective_type = 'goto' THEN (SELECT name FROM locations WHERE id = o.target_id)
                     WHEN o.target_id IS NOT NULL AND o.objective_type = 'interact' THEN (SELECT name FROM characters WHERE id = o.target_id)
                     WHEN o.target_id IS NOT NULL AND o.objective_type = 'collect' THEN (SELECT name FROM items WHERE id = o.target_id)
                     WHEN o.target_id IS NOT NULL AND o.objective_type = 'hack' THEN (SELECT name FROM devices WHERE id = o.target_id)
                     WHEN o.target_id IS NOT NULL AND o.objective_type = 'eliminate' THEN (SELECT name FROM characters WHERE id = o.target_id)
                     ELSE NULL
                   END as target_name
            FROM objectives o
            WHERE o.mission_id = ?
            ORDER BY o.order_index
            ''', (self.mission_id,))
            
            objectives = cursor.fetchall()
            
            for objective in objectives:
                item = QTreeWidgetItem(self.objective_tree)
                item.setText(0, objective['title'])
                item.setText(1, objective['objective_type'])
                item.setText(2, "Non" if objective['is_optional'] == 1 else "Oui")
                item.setText(3, objective['target_name'] if objective['target_name'] else "Aucune")
                item.setText(4, objective['description'])
                
                # Stocker l'ID de l'objectif dans l'élément pour référence
                item.setData(0, Qt.ItemDataRole.UserRole, objective['id'])
            
            logger.info(f"Chargé {len(objectives)} objectifs pour la mission {self.mission_id}")
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des objectifs: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les objectifs: {e}")
    
    def show_context_menu(self, position):
        """Afficher le menu contextuel pour un objectif"""
        item = self.objective_tree.itemAt(position)
        if not item:
            return
        
        # Créer le menu contextuel
        context_menu = QMenu(self)
        
        edit_action = QAction("Éditer l'objectif", self)
        edit_action.triggered.connect(lambda: self.edit_objective(item))
        context_menu.addAction(edit_action)
        
        context_menu.addSeparator()
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_objective(item.data(0, Qt.ItemDataRole.UserRole)))
        context_menu.addAction(delete_action)
        
        # Afficher le menu
        context_menu.exec(QCursor.pos())
    
    def add_objective(self):
        """Ajouter un nouvel objectif"""
        # Déterminer l'ordre du nouvel objectif (après le dernier)
        next_order = self.objective_tree.topLevelItemCount()
        
        # Ouvrir le dialogue d'édition d'objectif
        dialog = ObjectiveEditDialog(self, world_id=self.world_id, mission_id=self.mission_id, order_index=next_order)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Rafraîchir la liste des objectifs
            self.load_objectives()
    
    def edit_objective(self, item=None):
        """Éditer un objectif existant"""
        if isinstance(item, QTreeWidgetItem):
            objective_id = item.data(0, Qt.ItemDataRole.UserRole)
        else:
            # Utiliser l'élément sélectionné
            current_item = self.objective_tree.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un objectif à éditer.")
                return
            objective_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        if not objective_id:
            return
        
        # Récupérer les informations complètes de l'objectif
        db = get_database()
        cursor = db.conn.cursor()
        
        cursor.execute("SELECT * FROM objectives WHERE id = ?", (objective_id,))
        objective = cursor.fetchone()
        if not objective:
            QMessageBox.warning(self, "Erreur", "L'objectif n'a pas été trouvé dans la base de données.")
            return
        
        # Ouvrir le dialogue d'édition d'objectif
        dialog = ObjectiveEditDialog(self, world_id=self.world_id, mission_id=self.mission_id, objective=objective)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Rafraîchir la liste des objectifs
            self.load_objectives()
    
    def delete_objective(self, objective_id=None):
        """Supprimer un objectif"""
        if not objective_id:
            # Utiliser l'élément sélectionné
            current_item = self.objective_tree.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un objectif à supprimer.")
                return
            objective_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        if not objective_id:
            return
        
        # Demander confirmation
        response = QMessageBox.question(
            self, 
            "Confirmer la suppression", 
            "Êtes-vous sûr de vouloir supprimer cet objectif?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.Yes:
            # Supprimer l'objectif
            db = get_database()
            cursor = db.conn.cursor()
            
            try:
                cursor.execute("DELETE FROM objectives WHERE id = ?", (objective_id,))
                db.conn.commit()
                
                # Rafraîchir la liste
                self.load_objectives()
                
                logger.info(f"Objectif supprimé: {objective_id}")
            except Exception as e:
                db.conn.rollback()
                logger.error(f"Erreur lors de la suppression de l'objectif: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'objectif: {e}")


class ObjectiveEditDialog(QDialog):
    """Dialogue pour ajouter ou éditer un objectif de mission"""
    
    def __init__(self, parent=None, world_id=None, mission_id=None, objective=None, order_index=0):
        super().__init__(parent)
        self.world_id = world_id
        self.mission_id = mission_id
        self.objective = objective  # None pour un nouvel objectif, sinon les données de l'objectif existant
        self.order_index = order_index
        self.setup_ui()
        
        # Si on édite un objectif existant, remplir les champs
        if self.objective:
            self.load_objective_data()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        self.setWindowTitle("Ajouter un objectif" if not self.objective else "Éditer l'objectif")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_layout = QFormLayout()
        
        # Titre
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Entrez le titre de l'objectif")
        form_layout.addRow("Titre:", self.title_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Entrez la description de l'objectif")
        self.description_edit.setMinimumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        # Type d'objectif
        self.objective_type_combo = QComboBox()
        self.objective_type_combo.addItems(["goto", "interact", "collect", "hack", "eliminate", "protect", "escape"])
        self.objective_type_combo.currentIndexChanged.connect(self.update_target_options)
        form_layout.addRow("Type d'objectif:", self.objective_type_combo)
        
        # Cible
        self.target_layout = QHBoxLayout()
        
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(250)
        self.target_layout.addWidget(self.target_combo)
        
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(100)
        self.count_spin.setValue(1)
        self.target_layout.addWidget(QLabel("Quantité:"))
        self.target_layout.addWidget(self.count_spin)
        
        form_layout.addRow("Cible:", self.target_layout)
        
        # Options
        self.is_optional_check = QCheckBox("Cet objectif est optionnel")
        form_layout.addRow("", self.is_optional_check)
        
        # Ordre
        self.order_spin = QSpinBox()
        self.order_spin.setMinimum(0)
        self.order_spin.setMaximum(100)
        self.order_spin.setValue(self.order_index)
        form_layout.addRow("Ordre:", self.order_spin)
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Charger les cibles en fonction du type d'objectif sélectionné
        self.update_target_options()
    
    def update_target_options(self, index=None):
        """Mettre à jour les options de cible en fonction du type d'objectif"""
        objective_type = self.objective_type_combo.currentText()
        
        # Vider la liste actuelle
        self.target_combo.clear()
        self.target_combo.addItem("Aucune cible spécifique", None)
        
        # Déterminer la table de cibles en fonction du type d'objectif
        db = get_database()
        cursor = db.conn.cursor()
        
        try:
            if objective_type == "goto":
                # Les cibles sont des lieux
                cursor.execute('''
                SELECT id, name FROM locations WHERE world_id = ? ORDER BY name
                ''', (self.world_id,))
                targets = cursor.fetchall()
                for target in targets:
                    self.target_combo.addItem(target['name'], target['id'])
            
            elif objective_type == "interact" or objective_type == "eliminate" or objective_type == "protect":
                # Les cibles sont des personnages
                cursor.execute('''
                SELECT id, name FROM characters WHERE world_id = ? ORDER BY name
                ''', (self.world_id,))
                targets = cursor.fetchall()
                for target in targets:
                    self.target_combo.addItem(target['name'], target['id'])
            
            elif objective_type == "collect":
                # Les cibles sont des objets
                cursor.execute('''
                SELECT id, name FROM items WHERE world_id = ? 
                UNION 
                SELECT id, name FROM hardware_items WHERE world_id = ?
                UNION
                SELECT id, name FROM consumable_items WHERE world_id = ?
                ORDER BY name
                ''', (self.world_id, self.world_id, self.world_id))
                targets = cursor.fetchall()
                for target in targets:
                    self.target_combo.addItem(target['name'], target['id'])
            
            elif objective_type == "hack":
                # Les cibles sont des appareils
                cursor.execute('''
                SELECT id, name FROM devices WHERE world_id = ? ORDER BY name
                ''', (self.world_id,))
                targets = cursor.fetchall()
                for target in targets:
                    self.target_combo.addItem(target['name'], target['id'])
            
            # Pour "escape", pas de cible spécifique nécessaire
            
            # Afficher ou masquer la quantité en fonction du type
            need_count = objective_type in ["collect", "eliminate"]
            self.count_spin.setVisible(need_count)
            self.target_layout.itemAt(2).widget().setVisible(need_count)  # Le QLabel "Quantité:"
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des cibles: {e}")
    
    def load_objective_data(self):
        """Charger les données de l'objectif dans les champs du formulaire"""
        if not self.objective:
            return
        
        # Définir les valeurs de base
        self.title_edit.setText(self.objective['title'])
        self.description_edit.setText(self.objective['description'])
        
        # Sélectionner le type d'objectif
        index = self.objective_type_combo.findText(self.objective['objective_type'])
        if index >= 0:
            self.objective_type_combo.setCurrentIndex(index)
        
        # Mettre à jour les options de cible en fonction du type d'objectif
        self.update_target_options()
        
        # Sélectionner la cible si définie
        if self.objective['target_id']:
            index = self.target_combo.findData(self.objective['target_id'])
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
        
        # Définir la quantité
        self.count_spin.setValue(self.objective['target_count'])
        
        # Options
        self.is_optional_check.setChecked(self.objective['is_optional'] == 1)
        
        # Ordre
        self.order_spin.setValue(self.objective['order_index'])
    
    def accept(self):
        """Valider les données et sauvegarder l'objectif"""
        # Récupérer les données du formulaire
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        objective_type = self.objective_type_combo.currentText()
        target_id = self.target_combo.currentData()
        target_count = self.count_spin.value()
        is_optional = 1 if self.is_optional_check.isChecked() else 0
        order_index = self.order_spin.value()
        
        # Valider les données
        if not title:
            QMessageBox.warning(self, "Champs manquants", "Veuillez entrer un titre pour l'objectif.")
            return
        
        if not description:
            QMessageBox.warning(self, "Champs manquants", "Veuillez entrer une description pour l'objectif.")
            return
        
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            if self.objective:  # Modification d'un objectif existant
                objective_id = self.objective['id']
                
                cursor.execute('''
                UPDATE objectives
                SET title = ?, description = ?, objective_type = ?, target_id = ?, target_count = ?,
                    is_optional = ?, order_index = ?
                WHERE id = ?
                ''', (
                    title, description, objective_type, target_id, target_count,
                    is_optional, order_index, objective_id
                ))
                
                logger.info(f"Objectif mis à jour: {objective_id}")
            
            else:  # Nouvel objectif
                objective_id = str(uuid.uuid4())
                
                cursor.execute('''
                INSERT INTO objectives (id, mission_id, title, description, objective_type,
                                     target_id, target_count, is_optional, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    objective_id, self.mission_id, title, description, objective_type,
                    target_id, target_count, is_optional, order_index
                ))
                
                logger.info(f"Nouvel objectif créé: {objective_id}")
            
            db.conn.commit()
            
            # Fermer le dialogue
            super().accept()
        
        except Exception as e:
            db.conn.rollback()
            logger.error(f"Erreur lors de l'enregistrement de l'objectif: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer l'objectif: {e}")


class RandomMissionDialog(QDialog):
    """Dialogue pour générer une mission aléatoire"""
    
    def __init__(self, parent=None, world_id=None):
        super().__init__(parent)
        self.world_id = world_id
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        self.setWindowTitle("Générer une mission aléatoire")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Formulaire pour les paramètres de génération
        form_layout = QFormLayout()
        
        # Type de mission
        self.mission_type_combo = QComboBox()
        self.mission_type_combo.addItem("Aléatoire")
        self.mission_type_combo.addItems(["infiltration", "récupération", "hacking", "protection", 
                                       "livraison", "élimination", "sabotage", "espionnage", 
                                       "escorte", "investigation"])
        form_layout.addRow("Type de mission:", self.mission_type_combo)
        
        # Difficulté
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("Aléatoire")
        self.difficulty_combo.addItems(["facile", "moyen", "difficile", "très difficile", "extrême"])
        form_layout.addRow("Difficulté:", self.difficulty_combo)
        
        # Nombre d'objectifs
        self.objectives_spin = QSpinBox()
        self.objectives_spin.setMinimum(1)
        self.objectives_spin.setMaximum(10)
        self.objectives_spin.setValue(3)
        form_layout.addRow("Nombre d'objectifs:", self.objectives_spin)
        
        # Options
        self.main_quest_check = QCheckBox("Mission principale")
        form_layout.addRow("", self.main_quest_check)
        
        self.hidden_check = QCheckBox("Mission cachée")
        form_layout.addRow("", self.hidden_check)
        
        # Associer à un lieu
        self.location_combo = QComboBox()
        self.location_combo.addItem("Aléatoire", None)
        self.load_locations()
        form_layout.addRow("Lieu:", self.location_combo)
        
        # Associer à un donneur
        self.giver_combo = QComboBox()
        self.giver_combo.addItem("Aléatoire", None)
        self.load_characters()
        form_layout.addRow("Donneur de mission:", self.giver_combo)
        
        layout.addLayout(form_layout)
        
        # Message d'information
        info_label = QLabel("La mission générée aura des objectifs aléatoires basés sur les PNJ, lieux et objets existants dans le monde.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_locations(self):
        """Charger les lieux depuis la base de données"""
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            cursor.execute('''
            SELECT id, name FROM locations WHERE world_id = ? ORDER BY name
            ''', (self.world_id,))
            
            locations = cursor.fetchall()
            
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des lieux: {e}")
    
    def load_characters(self):
        """Charger les personnages depuis la base de données"""
        try:
            db = get_database()
            cursor = db.conn.cursor()
            
            cursor.execute('''
            SELECT id, name FROM characters WHERE world_id = ? ORDER BY name
            ''', (self.world_id,))
            
            characters = cursor.fetchall()
            
            for character in characters:
                self.giver_combo.addItem(character['name'], character['id'])
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des personnages: {e}")
    
    def generate_mission(self):
        """Générer une mission aléatoire avec les paramètres spécifiés"""
        try:
            # Récupérer un générateur de monde pour utiliser ses fonctions
            from world_generator import WorldGenerator
            generator = WorldGenerator()
            
            # Déterminer les paramètres
            mission_type = self.mission_type_combo.currentText()
            if mission_type == "Aléatoire":
                mission_type = None
            
            difficulty = self.difficulty_combo.currentText()
            if difficulty == "Aléatoire":
                difficulty = None
            
            num_objectives = self.objectives_spin.value()
            is_main_quest = self.main_quest_check.isChecked()
            is_hidden = self.hidden_check.isChecked()
            location_id = self.location_combo.currentData()
            giver_id = self.giver_combo.currentData()
            
            # Obtenir la connexion à la base de données
            db = get_database()
            
            # Récupérer les informations nécessaires pour générer la mission
            cursor = db.conn.cursor()
            
            # Récupérer les personnages
            cursor.execute("SELECT id FROM characters WHERE world_id = ?", (self.world_id,))
            character_ids = [row['id'] for row in cursor.fetchall()]
            
            # Récupérer les lieux
            cursor.execute("SELECT id FROM locations WHERE world_id = ?", (self.world_id,))
            location_ids = [row['id'] for row in cursor.fetchall()]
            
            # Générer une mission
            mission_ids = generator._generate_missions(
                db, self.world_id, location_ids, character_ids, 1,
                specific_type=mission_type,
                specific_difficulty=difficulty,
                force_main_quest=is_main_quest,
                force_hidden=is_hidden,
                force_location_id=location_id,
                force_giver_id=giver_id
            )
            
            if mission_ids and len(mission_ids) > 0:
                mission_id = mission_ids[0]
                
                # Générer des objectifs pour cette mission
                generator._generate_objectives_for_mission(db, mission_id, num_objectives)
                
                return mission_id
            
            return None
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la mission: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de générer la mission: {e}")
            return None
