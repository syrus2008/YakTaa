"""
Interface utilisateur PyQt6 pour le système de combat YakTaa
Ce module remplace l'ancienne interface Tkinter par une interface PyQt6 compatible
avec le reste de l'application.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QListWidget, QListWidgetItem, QComboBox, QDialog,
    QScrollArea, QGridLayout, QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QPalette

from .engine import CombatEngine, ActionType, CombatStatus

# Configurer le logger
logger = logging.getLogger(__name__)

class CombatUI(QDialog):
    """Interface utilisateur PyQt6 pour les combats"""
    
    # Signal émis à la fin du combat
    combat_ended = pyqtSignal(CombatStatus)
    
    def __init__(self, parent=None, combat_engine: CombatEngine = None, end_callback: Callable = None):
        """Initialise l'interface utilisateur de combat
        
        Args:
            parent: Widget parent
            combat_engine: Moteur de combat à utiliser
            end_callback: Fonction à appeler à la fin du combat
        """
        super().__init__(parent)
        self.combat_engine = combat_engine
        self.end_callback = end_callback
        
        # Configuration de la fenêtre
        self.setWindowTitle("Combat - YakTaa")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # Connexion du signal
        self.combat_ended.connect(self._on_combat_end)
        
        # Création de l'interface
        self._create_ui()
        
        # Application du style cyberpunk
        self._apply_cyberpunk_style()
        
        # Démarrer le combat
        if self.combat_engine:
            self.combat_engine.start_combat()
            self._update_ui()
            
            # Timer pour les mises à jour régulières
            self.update_timer = QTimer(self)
            self.update_timer.timeout.connect(self._update_ui)
            self.update_timer.start(100)  # Mise à jour à 10 FPS
    
    def _create_ui(self):
        """Crée l'interface utilisateur du combat"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Création des différentes sections
        self._create_info_section(main_layout)
        self._create_combat_area(main_layout)
        self._create_log_section(main_layout)
        self._create_action_section(main_layout)
    
    def _create_info_section(self, parent_layout):
        """Crée la section d'information sur le combat (santé, statut)"""
        info_frame = QGroupBox("Statut du combat")
        info_layout = QHBoxLayout(info_frame)
        
        # Info sur le joueur
        player_frame = QFrame()
        player_layout = QGridLayout(player_frame)
        
        player = self.combat_engine.player
        self.player_name_label = QLabel(f"<b>{player.name}</b>")
        self.player_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.player_health_bar = QProgressBar()
        self.player_health_bar.setMinimum(0)
        self.player_health_bar.setMaximum(player.max_health)
        self.player_health_bar.setValue(player.health)
        self.player_health_bar.setFormat("%v / %m PV")
        self.player_health_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #555; border-radius: 3px; text-align: center; }"
            "QProgressBar::chunk { background-color: #0F0; }"
        )
        
        player_layout.addWidget(self.player_name_label, 0, 0)
        player_layout.addWidget(self.player_health_bar, 1, 0)
        
        # Info sur les ennemis
        enemy_frame = QFrame()
        enemy_layout = QVBoxLayout(enemy_frame)
        
        self.enemy_info = {}
        for i, enemy in enumerate(self.combat_engine.enemies):
            enemy_row = QFrame()
            enemy_row_layout = QHBoxLayout(enemy_row)
            enemy_row_layout.setContentsMargins(0, 0, 0, 0)
            
            enemy_name = QLabel(f"<b>{enemy.name}</b>")
            enemy_health_bar = QProgressBar()
            enemy_health_bar.setMinimum(0)
            enemy_health_bar.setMaximum(enemy.max_health)
            enemy_health_bar.setValue(enemy.health)
            enemy_health_bar.setFormat("%v / %m PV")
            enemy_health_bar.setStyleSheet(
                "QProgressBar { border: 1px solid #555; border-radius: 3px; text-align: center; }"
                "QProgressBar::chunk { background-color: #F00; }"
            )
            
            enemy_row_layout.addWidget(enemy_name)
            enemy_row_layout.addWidget(enemy_health_bar)
            
            enemy_layout.addWidget(enemy_row)
            
            # Stocker les références pour les mises à jour
            self.enemy_info[enemy] = {
                "name_label": enemy_name,
                "health_bar": enemy_health_bar
            }
        
        # Ajouter les frames au layout principal
        info_layout.addWidget(player_frame, 1)
        info_layout.addWidget(enemy_frame, 2)
        
        # Indicateur de tour
        turn_frame = QFrame()
        turn_layout = QVBoxLayout(turn_frame)
        
        self.turn_indicator = QLabel("Tour: 1")
        self.turn_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_actor_label = QLabel("En attente...")
        self.current_actor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        turn_layout.addWidget(self.turn_indicator)
        turn_layout.addWidget(self.current_actor_label)
        
        info_layout.addWidget(turn_frame)
        
        # Ajouter la section d'info au layout parent
        parent_layout.addWidget(info_frame)
    
    def _create_combat_area(self, parent_layout):
        """Crée la zone centrale d'affichage du combat"""
        combat_frame = QFrame()
        combat_frame.setMinimumHeight(200)
        combat_frame.setStyleSheet("background-color: #1a1a1a; border-radius: 5px;")
        
        # Ici, on pourrait ajouter des visualisations des personnages, des effets, etc.
        # Pour l'instant, on le laisse simple
        
        parent_layout.addWidget(combat_frame, 1)  # Stretch factor de 1
    
    def _create_log_section(self, parent_layout):
        """Crée la section des logs de combat"""
        log_frame = QGroupBox("Journal de combat")
        log_layout = QVBoxLayout(log_frame)
        
        self.log_list = QListWidget()
        self.log_list.setAlternatingRowColors(True)
        self.log_list.setStyleSheet(
            "QListWidget { background-color: #0a0a0a; color: #ddd; border: 1px solid #444; }"
            "QListWidget::item:alternate { background-color: #1a1a1a; }"
        )
        
        log_layout.addWidget(self.log_list)
        
        parent_layout.addWidget(log_frame)
    
    def _create_action_section(self, parent_layout):
        """Crée la section des actions du joueur"""
        action_frame = QGroupBox("Actions")
        action_layout = QHBoxLayout(action_frame)
        
        # Sélection de la cible
        target_frame = QFrame()
        target_layout = QVBoxLayout(target_frame)
        
        target_label = QLabel("Cible :")
        self.target_selector = QComboBox()
        
        # Remplir les options de cible
        for enemy in self.combat_engine.enemies:
            self.target_selector.addItem(enemy.name)
        
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_selector)
        
        # Boutons d'action
        action_buttons_frame = QFrame()
        action_buttons_layout = QGridLayout(action_buttons_frame)
        
        # Créer les boutons d'action
        self.attack_button = QPushButton("Attaquer")
        self.attack_button.clicked.connect(self._on_attack)
        
        self.defend_button = QPushButton("Défendre")
        self.defend_button.clicked.connect(self._on_defend)
        
        self.special_button = QPushButton("Action spéciale")
        self.special_button.clicked.connect(self._on_special)
        
        self.use_item_button = QPushButton("Utiliser objet")
        self.use_item_button.clicked.connect(self._on_use_item)
        
        self.flee_button = QPushButton("Fuir")
        self.flee_button.clicked.connect(self._on_flee)
        
        # Ajouter les boutons à la grille
        action_buttons_layout.addWidget(self.attack_button, 0, 0)
        action_buttons_layout.addWidget(self.defend_button, 0, 1)
        action_buttons_layout.addWidget(self.special_button, 1, 0)
        action_buttons_layout.addWidget(self.use_item_button, 1, 1)
        action_buttons_layout.addWidget(self.flee_button, 2, 0, 1, 2)
        
        # Ajouter les frames au layout principal de la section
        action_layout.addWidget(target_frame, 1)
        action_layout.addWidget(action_buttons_frame, 2)
        
        parent_layout.addWidget(action_frame)
    
    def _update_ui(self):
        """Met à jour l'interface utilisateur avec les données actuelles du combat"""
        if not self.combat_engine:
            return
            
        # Vérifier si le combat est terminé
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            self._handle_combat_end()
            return
            
        # Mettre à jour les informations du joueur
        player = self.combat_engine.player
        self.player_health_bar.setValue(player.health)
        
        # Mettre à jour les informations des ennemis
        for enemy in self.combat_engine.enemies[:]:  # Copie de la liste pour éviter les problèmes de modification pendant l'itération
            if enemy in self.enemy_info:
                if enemy.health <= 0:
                    # Mettre à jour l'affichage pour les ennemis vaincus
                    self.enemy_info[enemy]["name_label"].setText(f"<s>{enemy.name}</s> (Vaincu)")
                    self.enemy_info[enemy]["health_bar"].setValue(0)
                else:
                    self.enemy_info[enemy]["health_bar"].setValue(enemy.health)
        
        # Mettre à jour les indicateurs de tour
        self.turn_indicator.setText(f"Tour: {self.combat_engine.current_turn}")
        
        # Mettre à jour l'indicateur de joueur actif
        current_actor = self.combat_engine.current_actor
        if current_actor:
            self.current_actor_label.setText(f"Tour de: {current_actor.name}")
            
            # Activer/désactiver les boutons selon le tour
            is_player_turn = (current_actor == player)
            self.attack_button.setEnabled(is_player_turn)
            self.defend_button.setEnabled(is_player_turn)
            self.special_button.setEnabled(is_player_turn)
            self.use_item_button.setEnabled(is_player_turn)
            self.flee_button.setEnabled(is_player_turn)
        
        # Mettre à jour la liste des logs
        self._update_log_list()
        
        # Si c'est le tour d'un ennemi, faire jouer l'IA après un court délai
        if current_actor and current_actor != player:
            QTimer.singleShot(1000, self._enemy_turn)
    
    def _update_log_list(self):
        """Met à jour la liste des logs de combat"""
        # Récupérer les nouveaux messages
        current_count = self.log_list.count()
        new_messages = self.combat_engine.log_messages[current_count:]
        
        # Ajouter les nouveaux messages
        for message in new_messages:
            self.log_list.addItem(message)
            
        # Scroller jusqu'au dernier message
        if new_messages:
            self.log_list.scrollToBottom()
    
    def _enemy_turn(self):
        """Exécute le tour de l'ennemi actif"""
        if not self.combat_engine or self.combat_engine.status != CombatStatus.IN_PROGRESS:
            return
            
        current_actor = self.combat_engine.current_actor
        if current_actor and current_actor != self.combat_engine.player:
            # Action simple pour l'ennemi: attaque du joueur
            action_result = self.combat_engine.perform_action(
                ActionType.ATTACK,
                target=self.combat_engine.player
            )
            
            # Mettre à jour l'interface après l'action
            self._update_ui()
    
    def _on_attack(self):
        """Gère l'action d'attaque du joueur"""
        if not self._check_player_turn():
            return
            
        # Récupérer la cible sélectionnée
        target_index = self.target_selector.currentIndex()
        if target_index >= 0 and target_index < len(self.combat_engine.enemies):
            target = self.combat_engine.enemies[target_index]
            
            # Exécuter l'action d'attaque
            action_result = self.combat_engine.perform_action(
                ActionType.ATTACK,
                target=target
            )
            
            # Mettre à jour l'interface après l'action
            self._update_ui()
    
    def _on_defend(self):
        """Gère l'action de défense du joueur"""
        if not self._check_player_turn():
            return
            
        # Exécuter l'action de défense
        action_result = self.combat_engine.perform_action(ActionType.DEFEND)
        
        # Mettre à jour l'interface après l'action
        self._update_ui()
    
    def _on_special(self):
        """Gère l'action spéciale du joueur"""
        if not self._check_player_turn():
            return
            
        # Récupérer la cible sélectionnée
        target_index = self.target_selector.currentIndex()
        if target_index >= 0 and target_index < len(self.combat_engine.enemies):
            target = self.combat_engine.enemies[target_index]
            
            # Exécuter l'action spéciale
            action_result = self.combat_engine.perform_action(
                ActionType.SPECIAL,
                target=target
            )
            
            # Mettre à jour l'interface après l'action
            self._update_ui()
    
    def _on_use_item(self):
        """Gère l'utilisation d'un objet par le joueur"""
        if not self._check_player_turn():
            return
            
        # TODO: Implémenter la sélection et l'utilisation d'objets
        # Pour l'instant, juste un message dans les logs
        self.combat_engine.log_message("Fonctionnalité d'utilisation d'objets non implémentée")
        self._update_log_list()
    
    def _on_flee(self):
        """Gère la tentative de fuite du joueur"""
        if not self._check_player_turn():
            return
            
        # Exécuter l'action de fuite
        action_result = self.combat_engine.perform_action(ActionType.ESCAPE)
        
        # Mettre à jour l'interface après l'action
        self._update_ui()
    
    def _check_player_turn(self) -> bool:
        """Vérifie si c'est bien le tour du joueur"""
        if not self.combat_engine:
            return False
            
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            return False
            
        if self.combat_engine.current_actor != self.combat_engine.player:
            self.combat_engine.log_message("Ce n'est pas votre tour !")
            self._update_log_list()
            return False
            
        return True
    
    def _handle_combat_end(self):
        """Gère la fin du combat"""
        # Arrêter le timer de mise à jour
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
            
        # Mettre à jour l'interface une dernière fois
        self._update_log_list()
        
        # Désactiver tous les boutons d'action
        self.attack_button.setEnabled(False)
        self.defend_button.setEnabled(False)
        self.special_button.setEnabled(False)
        self.use_item_button.setEnabled(False)
        self.flee_button.setEnabled(False)
        
        # Afficher un message selon le résultat
        result_message = ""
        if self.combat_engine.status == CombatStatus.PLAYER_VICTORY:
            result_message = "Victoire ! Tous les ennemis sont vaincus."
        elif self.combat_engine.status == CombatStatus.ENEMY_VICTORY:
            result_message = "Défaite ! Vous avez été vaincu."
        elif self.combat_engine.status == CombatStatus.ESCAPED:
            result_message = "Vous avez fui le combat."
        else:
            result_message = "Combat terminé."
            
        # Ajouter le message aux logs
        self.combat_engine.log_message(result_message)
        self._update_log_list()
        
        # Créer un bouton pour fermer la fenêtre
        close_button = QPushButton("Terminer", self)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("font-weight: bold; padding: 8px 16px;")
        
        # Ajouter le bouton en bas de l'interface
        self.layout().addWidget(close_button)
        
        # Émettre le signal de fin de combat
        self.combat_ended.emit(self.combat_engine.status)
    
    def _on_combat_end(self, status: CombatStatus):
        """Appelé lorsque le combat se termine"""
        logger.info(f"Combat terminé avec statut: {status}")
        
        # Si un callback a été fourni, l'appeler
        if self.end_callback:
            self.end_callback(status)
    
    def _apply_cyberpunk_style(self):
        """Applique un style cyberpunk à l'interface"""
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #CCCCCC;
            }
            
            QGroupBox {
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
                color: #00CCFF;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QLabel {
                color: #CCCCCC;
            }
            
            QPushButton {
                background-color: #333333;
                color: #00CCFF;
                border: 1px solid #00CCFF;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #444444;
                border: 1px solid #00FFFF;
                color: #00FFFF;
            }
            
            QPushButton:pressed {
                background-color: #222222;
                border: 1px solid #0088AA;
            }
            
            QPushButton:disabled {
                background-color: #222222;
                border: 1px solid #555555;
                color: #555555;
            }
            
            QComboBox {
                background-color: #333333;
                border: 1px solid #00CCFF;
                border-radius: 4px;
                padding: 4px;
                color: #CCCCCC;
            }
            
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #00CCFF;
            }
            
            QComboBox QAbstractItemView {
                background-color: #333333;
                border: 1px solid #00CCFF;
                selection-background-color: #00CCFF;
                selection-color: #121212;
            }
            
            QProgressBar {
                border: 1px solid #00CCFF;
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #222222;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00CCFF, stop:1 #0088AA);
            }
            
            QFrame {
                background-color: #1A1A1A;
                border-radius: 4px;
            }
        """)

# Fonction pour créer une interface de combat facilement depuis d'autres modules
def create_combat_ui(parent, player, enemies, end_callback=None):
    """
    Crée et affiche une interface de combat
    
    Args:
        parent: Widget parent pour la fenêtre
        player: Le joueur participant au combat
        enemies: Liste des ennemis à combattre
        end_callback: Fonction à appeler à la fin du combat
        
    Returns:
        La fenêtre de combat créée
    """
    from .engine import CombatEngine
    
    # Créer le moteur de combat
    combat_engine = CombatEngine(player, enemies)
    
    # Créer l'interface de combat
    combat_ui = CombatUI(parent, combat_engine, end_callback)
    combat_ui.show()
    
    return combat_ui
