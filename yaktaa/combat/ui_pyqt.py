#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'interface utilisateur de combat pour YakTaa (Version PyQt6)
Remplace la version Tkinter précédente pour assurer la compatibilité avec l'éditeur de monde
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QPushButton, 
    QProgressBar, QListWidget, QListWidgetItem, QGroupBox, QTextEdit, QSplitter,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QTextCursor, QFont, QPalette

from .engine import CombatEngine, ActionType, CombatStatus

# Configurer le logger
logger = logging.getLogger(__name__)

class CombatUI(QWidget):
    """Interface utilisateur pour les combats (version PyQt6)"""
    
    def __init__(self, parent=None, combat_engine: CombatEngine = None, end_callback: Callable = None):
        """Initialise l'interface utilisateur de combat
        
        Args:
            parent: Widget parent PyQt6 (peut être None)
            combat_engine: Moteur de combat à utiliser
            end_callback: Fonction à appeler à la fin du combat
        """
        super().__init__(parent)
        self.combat_engine = combat_engine
        self.end_callback = end_callback
        
        # Variables d'état pour la sélection d'action/cible
        self.current_action = None
        self.current_item = None
        
        # Configuration pour l'intégration dans l'UI principale
        self.setObjectName("combat_ui")
        
        # Setup UI
        self.setup_ui()
        
        # Style cyberpunk
        self.apply_cyberpunk_style()
        
        # Si un moteur de combat est fourni, démarrer le combat
        if self.combat_engine:
            self.combat_engine.start_combat()
            self.update_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.setWindowTitle("Combat YakTaa")
        self.resize(800, 600)
        
        # Création des différentes sections
        self.create_info_section()
        self.create_log_section()
        self.create_action_section()
        self.create_target_selection()
    
    def create_info_section(self):
        """Crée la section d'information sur le combat (santé, statut)"""
        info_frame = QGroupBox("Statut du combat")
        info_layout = QVBoxLayout(info_frame)
        
        # Section joueur
        player_frame = QFrame()
        player_layout = QGridLayout(player_frame)
        
        player_layout.addWidget(QLabel("Joueur:"), 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.player_name_label = QLabel(self.combat_engine.player.name if self.combat_engine else "Joueur")
        player_layout.addWidget(self.player_name_label, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        player_layout.addWidget(QLabel("Santé:"), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.player_health_bar = QProgressBar()
        self.player_health_bar.setRange(0, 100)
        self.player_health_bar.setValue(100)
        self.player_health_bar.setTextVisible(False)
        player_layout.addWidget(self.player_health_bar, 1, 1)
        
        self.player_health_text = QLabel("100/100")
        player_layout.addWidget(self.player_health_text, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        
        player_layout.addWidget(QLabel("Effets actifs:"), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.player_effects_label = QLabel("Aucun")
        player_layout.addWidget(self.player_effects_label, 2, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        
        info_layout.addWidget(player_frame)
        
        # Section ennemis
        enemies_frame = QGroupBox("Ennemis")
        enemies_layout = QVBoxLayout(enemies_frame)
        
        self.enemy_frames = []
        
        if self.combat_engine:
            for enemy in self.combat_engine.enemies:
                enemy_frame = QFrame()
                enemy_layout = QGridLayout(enemy_frame)
                
                enemy_name_label = QLabel(enemy.name)
                enemy_layout.addWidget(enemy_name_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
                
                enemy_health_bar = QProgressBar()
                enemy_health_bar.setRange(0, 100)
                enemy_health_bar.setValue(100)
                enemy_health_bar.setTextVisible(False)
                enemy_layout.addWidget(enemy_health_bar, 0, 1)
                
                enemy_health_text = QLabel("100/100")
                enemy_layout.addWidget(enemy_health_text, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
                
                enemy_effects_label = QLabel("")
                enemy_layout.addWidget(enemy_effects_label, 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
                
                enemies_layout.addWidget(enemy_frame)
                
                self.enemy_frames.append({
                    "frame": enemy_frame,
                    "name": enemy_name_label,
                    "health_bar": enemy_health_bar,
                    "health_text": enemy_health_text,
                    "effects": enemy_effects_label,
                    "enemy": enemy
                })
        
        info_layout.addWidget(enemies_frame)
        
        # Information sur le tour actuel
        turn_frame = QFrame()
        turn_layout = QGridLayout(turn_frame)
        
        turn_layout.addWidget(QLabel("Tour:"), 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.turn_label = QLabel("1")
        turn_layout.addWidget(self.turn_label, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        turn_layout.addWidget(QLabel("Tour de:"), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.current_actor_label = QLabel("")
        turn_layout.addWidget(self.current_actor_label, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        info_layout.addWidget(turn_frame)
        
        self.main_layout.addWidget(info_frame)
    
    def create_log_section(self):
        """Crée la section de logs du combat"""
        log_frame = QGroupBox("Journal de combat")
        log_layout = QVBoxLayout(log_frame)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        self.main_layout.addWidget(log_frame)
    
    def create_action_section(self):
        """Crée la section des actions de combat"""
        action_frame = QGroupBox("Actions")
        action_layout = QGridLayout(action_frame)
        
        # Boutons d'action - première ligne
        self.attack_btn = QPushButton("Attaquer")
        self.attack_btn.clicked.connect(lambda: self.on_action_selected(ActionType.ATTACK))
        action_layout.addWidget(self.attack_btn, 0, 0)
        
        self.hack_btn = QPushButton("Hacker")
        self.hack_btn.clicked.connect(lambda: self.on_action_selected(ActionType.HACK))
        action_layout.addWidget(self.hack_btn, 0, 1)
        
        self.use_item_btn = QPushButton("Utiliser Objet")
        self.use_item_btn.clicked.connect(lambda: self.on_action_selected(ActionType.USE_ITEM))
        action_layout.addWidget(self.use_item_btn, 0, 2)
        
        self.activate_implant_btn = QPushButton("Activer Implant")
        self.activate_implant_btn.clicked.connect(lambda: self.on_action_selected(ActionType.ACTIVATE_IMPLANT))
        action_layout.addWidget(self.activate_implant_btn, 0, 3)
        
        # Boutons d'action - deuxième ligne
        self.defend_btn = QPushButton("Défendre")
        self.defend_btn.clicked.connect(lambda: self.execute_action(ActionType.DEFEND))
        action_layout.addWidget(self.defend_btn, 1, 0)
        
        self.scan_btn = QPushButton("Scanner")
        self.scan_btn.clicked.connect(lambda: self.on_action_selected(ActionType.SCAN))
        action_layout.addWidget(self.scan_btn, 1, 1)
        
        self.escape_btn = QPushButton("Fuir")
        self.escape_btn.clicked.connect(lambda: self.execute_action(ActionType.ESCAPE))
        action_layout.addWidget(self.escape_btn, 1, 2)
        
        self.main_layout.addWidget(action_frame)
    
    def create_target_selection(self):
        """Crée la section de sélection de cible"""
        self.target_frame = QGroupBox("Sélection de cible")
        target_layout = QVBoxLayout(self.target_frame)
        
        # Liste de sélection des cibles
        self.target_listbox = QListWidget()
        target_layout.addWidget(self.target_listbox)
        
        # Boutons de confirmation/annulation
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        
        self.confirm_btn = QPushButton("Confirmer")
        self.confirm_btn.clicked.connect(self.on_target_confirmed)
        btn_layout.addWidget(self.confirm_btn)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.on_target_cancelled)
        btn_layout.addWidget(self.cancel_btn)
        
        target_layout.addWidget(btn_frame)
        
        # Caché par défaut
        self.target_frame.hide()
        self.main_layout.addWidget(self.target_frame)
    
    def apply_cyberpunk_style(self):
        """Applique un style cyberpunk à l'interface"""
        # Police avec une apparence monospace/techno
        font = QFont("Consolas", 10)
        self.setFont(font)
        
        # Couleurs cyberpunk
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a12;
                color: #00ffcc;
            }
            QGroupBox {
                border: 1px solid #00ffcc;
                border-radius: 3px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #121225;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1a1a40;
            }
            QPushButton:pressed {
                background-color: #00ffcc;
                color: #121225;
            }
            QProgressBar {
                border: 1px solid #00ffcc;
                border-radius: 3px;
                background-color: #121225;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ffcc;
            }
            QTextEdit {
                background-color: #0a0a12;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                font-family: 'Consolas';
            }
            QListWidget {
                background-color: #121225;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #1a1a40;
                color: #00ffff;
            }
        """)
        
        # Changer la couleur des barres de santé en fonction du niveau
        for enemy_frame in self.enemy_frames:
            enemy_frame["health_bar"].setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ff3366;
                    border-radius: 3px;
                    background-color: #121225;
                }
                QProgressBar::chunk {
                    background-color: #ff3366;
                }
            """)
    
    def update_ui(self):
        """Met à jour l'interface utilisateur en fonction de l'état du combat"""
        if not self.combat_engine:
            return
            
        # Mise à jour des infos du joueur
        player = self.combat_engine.player
        max_health = player.max_health if hasattr(player, 'max_health') else 100
        current_health = player.health
        health_percent = int((current_health / max_health) * 100) if max_health > 0 else 0
        
        self.player_health_bar.setRange(0, max_health)
        self.player_health_bar.setValue(current_health)
        self.player_health_text.setText(f"{current_health}/{max_health}")
        
        # Mise à jour des effets du joueur
        if hasattr(player, 'active_effects') and player.active_effects:
            effects_text = ", ".join(player.active_effects)
            self.player_effects_label.setText(effects_text)
        else:
            self.player_effects_label.setText("Aucun")
        
        # Mise à jour des infos des ennemis
        for i, enemy_data in enumerate(self.enemy_frames):
            enemy = enemy_data["enemy"]
            max_health = enemy.max_health if hasattr(enemy, 'max_health') else 100
            current_health = enemy.health
            
            enemy_data["health_bar"].setRange(0, max_health)
            enemy_data["health_bar"].setValue(current_health)
            enemy_data["health_text"].setText(f"{current_health}/{max_health}")
            
            # Mise à jour des effets de l'ennemi
            if hasattr(enemy, 'active_effects') and enemy.active_effects:
                effects_text = ", ".join(enemy.active_effects)
                enemy_data["effects"].setText(effects_text)
            else:
                enemy_data["effects"].setText("")
        
        # Mise à jour des infos de tour
        self.turn_label.setText(str(self.combat_engine.turn_count))
        if self.combat_engine.current_actor:
            self.current_actor_label.setText(self.combat_engine.current_actor.name)
        
        # Mise à jour des boutons d'action
        is_player_turn = self.combat_engine.is_player_turn()
        combat_ended = self.combat_engine.status != CombatStatus.IN_PROGRESS
        
        self.attack_btn.setEnabled(is_player_turn and not combat_ended)
        self.hack_btn.setEnabled(is_player_turn and not combat_ended)
        self.use_item_btn.setEnabled(is_player_turn and not combat_ended)
        self.activate_implant_btn.setEnabled(is_player_turn and not combat_ended)
        self.defend_btn.setEnabled(is_player_turn and not combat_ended)
        self.scan_btn.setEnabled(is_player_turn and not combat_ended)
        self.escape_btn.setEnabled(is_player_turn and not combat_ended)
    
    def add_log_message(self, message, color="#00ffcc"):
        """Ajoute un message au journal de combat"""
        self.log_text.setTextColor(QColor(color))
        self.log_text.append(message)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def on_action_selected(self, action_type):
        """Gère la sélection d'une action par le joueur"""
        self.current_action = action_type
        
        # Selon le type d'action, affiche la sélection de cible ou exécute directement
        if action_type in [ActionType.ATTACK, ActionType.HACK, ActionType.SCAN]:
            self.show_enemy_targets()
        elif action_type == ActionType.USE_ITEM:
            self.show_item_selection()
        elif action_type == ActionType.ACTIVATE_IMPLANT:
            self.show_implant_selection()
        else:
            self.execute_action(action_type)
    
    def show_enemy_targets(self):
        """Affiche la liste des ennemis comme cibles potentielles"""
        self.target_listbox.clear()
        for enemy in self.combat_engine.enemies:
            if enemy.health > 0:  # Seulement les ennemis vivants
                item = QListWidgetItem(enemy.name)
                item.setData(Qt.ItemDataRole.UserRole, enemy)
                self.target_listbox.addItem(item)
        
        if self.target_listbox.count() > 0:
            self.target_listbox.setCurrentRow(0)
            self.target_frame.show()
        else:
            self.add_log_message("Aucune cible disponible.", "#ff3366")
    
    def show_item_selection(self):
        """Affiche la liste des objets utilisables"""
        self.target_listbox.clear()
        
        # Supposons que le joueur a un inventaire avec des objets
        if hasattr(self.combat_engine.player, 'inventory') and self.combat_engine.player.inventory:
            for item in self.combat_engine.player.inventory:
                item_text = f"{item.name} - {item.description}" if hasattr(item, 'description') else item.name
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.target_listbox.addItem(list_item)
            
            if self.target_listbox.count() > 0:
                self.target_listbox.setCurrentRow(0)
                self.target_frame.show()
            else:
                self.add_log_message("Vous n'avez aucun objet utilisable.", "#ff3366")
        else:
            self.add_log_message("Vous n'avez aucun objet dans votre inventaire.", "#ff3366")
    
    def show_implant_selection(self):
        """Affiche la liste des implants activables"""
        self.target_listbox.clear()
        
        # Supposons que le joueur a des implants
        if hasattr(self.combat_engine.player, 'implants') and self.combat_engine.player.implants:
            for implant in self.combat_engine.player.implants:
                if hasattr(implant, 'is_active') and not implant.is_active:  # Seulement les implants non actifs
                    implant_text = f"{implant.name} - {implant.description}" if hasattr(implant, 'description') else implant.name
                    list_item = QListWidgetItem(implant_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, implant)
                    self.target_listbox.addItem(list_item)
            
            if self.target_listbox.count() > 0:
                self.target_listbox.setCurrentRow(0)
                self.target_frame.show()
            else:
                self.add_log_message("Vous n'avez aucun implant activable.", "#ff3366")
        else:
            self.add_log_message("Vous n'avez aucun implant.", "#ff3366")
    
    def on_target_confirmed(self):
        """Gère la confirmation d'une cible"""
        if self.target_listbox.currentItem():
            target = self.target_listbox.currentItem().data(Qt.ItemDataRole.UserRole)
            
            if self.current_action == ActionType.USE_ITEM:
                self.current_item = target
                # Pour les objets, on doit ensuite sélectionner une cible (soi-même ou un ennemi)
                self.show_item_targets()
            elif self.current_action == ActionType.ACTIVATE_IMPLANT:
                self.current_item = target
                self.execute_action(self.current_action, target=None, item=target)
            else:
                self.execute_action(self.current_action, target=target)
        
        self.target_frame.hide()
    
    def show_item_targets(self):
        """Affiche les cibles possibles pour un objet"""
        self.target_listbox.clear()
        
        # Ajouter le joueur comme cible possible
        item = QListWidgetItem("Vous-même")
        item.setData(Qt.ItemDataRole.UserRole, self.combat_engine.player)
        self.target_listbox.addItem(item)
        
        # Ajouter les ennemis comme cibles possibles
        for enemy in self.combat_engine.enemies:
            if enemy.health > 0:  # Seulement les ennemis vivants
                item = QListWidgetItem(enemy.name)
                item.setData(Qt.ItemDataRole.UserRole, enemy)
                self.target_listbox.addItem(item)
        
        if self.target_listbox.count() > 0:
            self.target_listbox.setCurrentRow(0)
            self.target_frame.show()
    
    def on_target_cancelled(self):
        """Gère l'annulation d'une sélection de cible"""
        self.current_action = None
        self.current_item = None
        self.target_frame.hide()
    
    def execute_action(self, action_type, target=None, item=None):
        """Exécute l'action sélectionnée"""
        if not self.combat_engine:
            return
            
        result = self.combat_engine.execute_action(
            action_type=action_type,
            target=target,
            item=item or self.current_item
        )
        
        # Afficher le résultat de l'action
        if result and 'message' in result:
            self.add_log_message(result['message'])
        
        # Réinitialiser les variables d'état
        self.current_action = None
        self.current_item = None
        
        # Mettre à jour l'interface
        self.update_ui()
        
        # Vérifier si le combat est terminé
        self.check_combat_status()
        
        # Si c'est au tour d'un ennemi, exécuter son tour après un court délai
        if not self.combat_engine.is_player_turn() and self.combat_engine.status == CombatStatus.IN_PROGRESS:
            QTimer.singleShot(1000, self.execute_enemy_turn)
    
    def execute_enemy_turn(self):
        """Exécute le tour d'un ennemi"""
        if not self.combat_engine or self.combat_engine.status != CombatStatus.IN_PROGRESS:
            return
            
        if not self.combat_engine.is_player_turn():
            result = self.combat_engine.execute_enemy_turn()
            
            # Afficher le résultat de l'action
            if result and 'message' in result:
                self.add_log_message(result['message'], "#ff3366")
            
            # Mettre à jour l'interface
            self.update_ui()
            
            # Vérifier si le combat est terminé
            self.check_combat_status()
            
            # Si c'est encore au tour d'un ennemi, continuer
            if not self.combat_engine.is_player_turn() and self.combat_engine.status == CombatStatus.IN_PROGRESS:
                QTimer.singleShot(1000, self.execute_enemy_turn)
    
    def check_combat_status(self):
        """Vérifie si le combat est terminé et agit en conséquence"""
        if not self.combat_engine:
            return
            
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            message = ""
            color = "#00ffcc"
            
            if self.combat_engine.status == CombatStatus.PLAYER_VICTORY:
                message = "Victoire ! Vous avez vaincu tous les ennemis."
                color = "#00ff00"
            elif self.combat_engine.status == CombatStatus.ENEMY_VICTORY:
                message = "Défaite ! Vous avez été vaincu."
                color = "#ff3366"
            elif self.combat_engine.status == CombatStatus.ESCAPED:
                message = "Vous avez réussi à fuir le combat."
                color = "#ffff00"
            elif self.combat_engine.status == CombatStatus.ABORTED:
                message = "Le combat a été interrompu."
                color = "#ffff00"
            
            self.add_log_message(message, color)
            
            # Désactiver les boutons d'action
            self.attack_btn.setEnabled(False)
            self.hack_btn.setEnabled(False)
            self.use_item_btn.setEnabled(False)
            self.activate_implant_btn.setEnabled(False)
            self.defend_btn.setEnabled(False)
            self.scan_btn.setEnabled(False)
            self.escape_btn.setEnabled(False)
            
            # Ajouter un bouton pour terminer le combat
            end_btn = QPushButton("Terminer le combat")
            end_btn.clicked.connect(self.end_combat)
            self.main_layout.addWidget(end_btn)
    
    def end_combat(self):
        """Termine le combat et appelle le callback de fin"""
        if self.end_callback:
            self.end_callback(self.combat_engine.status)

    def set_parent_widget(self, parent):
        """
        Configure le widget parent pour intégration dans l'interface principale
        
        Args:
            parent: QWidget parent dans lequel intégrer cette interface
        """
        if parent:
            # Détacher du parent actuel si nécessaire
            if self.parent():
                self.setParent(None)
            
            # Attacher au nouveau parent
            self.setParent(parent)
            
            # Adapter la taille au parent
            parent_size = parent.size()
            self.resize(parent_size)
            
            # S'assurer que les mises à jour d'affichage sont propagées
            self.show()
            
            logger.info("Interface de combat intégrée dans le widget parent")

    def update_style(self, main_color="#00ffcc", accent_color="#ff3366", bg_color="#0a0a12"):
        """
        Met à jour les couleurs du style cyberpunk pour correspondre au style global
        
        Args:
            main_color: Couleur principale pour le texte et les bordures
            accent_color: Couleur d'accentuation pour les éléments importants
            bg_color: Couleur d'arrière-plan
        """
        # Police avec une apparence monospace/techno
        font = QFont("Consolas", 10)
        self.setFont(font)
        
        # Appliquer les styles avec les couleurs personnalisées
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {main_color};
            }}
            QGroupBox {{
                border: 1px solid {main_color};
                border-radius: 3px;
                margin-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {bg_color};
                color: {main_color};
                border: 1px solid {main_color};
                border-radius: 3px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #1a1a40;
            }}
            QPushButton:pressed {{
                background-color: {main_color};
                color: {bg_color};
            }}
            QProgressBar {{
                border: 1px solid {main_color};
                border-radius: 3px;
                background-color: {bg_color};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {main_color};
            }}
            QTextEdit {{
                background-color: {bg_color};
                color: {main_color};
                border: 1px solid {main_color};
                font-family: 'Consolas';
            }}
            QListWidget {{
                background-color: {bg_color};
                color: {main_color};
                border: 1px solid {main_color};
                outline: none;
            }}
            QListWidget::item:selected {{
                background-color: #1a1a40;
                color: {main_color};
            }}
        """)
        
        # Changer la couleur des barres de santé en fonction du niveau
        for enemy_frame in self.enemy_frames:
            enemy_frame["health_bar"].setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {accent_color};
                    border-radius: 3px;
                    background-color: {bg_color};
                }}
                QProgressBar::chunk {{
                    background-color: {accent_color};
                }}
            """)
            
        logger.info(f"Style de l'interface de combat mis à jour avec les couleurs personnalisées")

    def resizeEvent(self, event):
        """
        Gère l'événement de redimensionnement pour adapter l'interface
        
        Args:
            event: QResizeEvent contenant les informations de redimensionnement
        """
        super().resizeEvent(event)
        
        # Adapter la disposition des éléments à la nouvelle taille
        new_size = event.size()
        logger.debug(f"Interface de combat redimensionnée à {new_size.width()}x{new_size.height()}")
        
        # Si le parent existe et que c'est un conteneur, s'adapter à sa taille
        if self.parent():
            parent_size = self.parent().size()
            if parent_size.width() > 0 and parent_size.height() > 0:
                self.resize(parent_size)
                
        # Mettre à jour l'interface après le redimensionnement
        self.update()
