"""
Module pour les mini-jeux de hacking visuels dans YakTaa
"""

import logging
import random
import time
import math
from typing import Dict, List, Any, Optional, Callable, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSplitter, QGridLayout, QLineEdit, QProgressBar,
    QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsRectItem, QGraphicsLineItem, QGraphicsPathItem,
    QStackedWidget, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QRect, QPoint, QPointF
from PyQt6.QtGui import QFont, QColor, QPen, QBrush, QPainterPath, QPixmap

from yaktaa.terminal.hacking_system import (
    HackingPuzzle, HackingPuzzleType, HackingTool, SecurityLevel,
    PasswordBruteforcePuzzle, BufferOverflowPuzzle, SequenceMatchingPuzzle,
    NetworkReroutingPuzzle
)

logger = logging.getLogger("YakTaa.UI.HackingMinigames")

class HackingMinigameBase(QDialog):
    """Classe de base pour tous les mini-jeux de hacking"""
    
    # Signaux
    puzzle_completed = pyqtSignal(bool, float)  # Succès, temps utilisé
    
    def __init__(self, puzzle: HackingPuzzle, parent=None):
        """Initialise le mini-jeu de base"""
        super().__init__(parent)
        self.puzzle = puzzle
        self.time_left = puzzle.time_limit
        self.completed = False
        self.success = False
        
        # Configuration de base
        self.setWindowTitle(f"Hacking: {puzzle.puzzle_type.name}")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # Mise en page principale
        self.layout = QVBoxLayout(self)
        
        # En-tête avec description et temps
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        
        self.description_label = QLabel(puzzle.description)
        self.description_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.header_layout.addWidget(self.description_label)
        
        self.time_label = QLabel(f"Temps: {self.time_left}s")
        self.time_label.setStyleSheet("color: #FF9900; font-weight: bold;")
        self.header_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.layout.addWidget(self.header)
        
        # Barre de progression du temps
        self.time_progress = QProgressBar()
        self.time_progress.setRange(0, puzzle.time_limit)
        self.time_progress.setValue(puzzle.time_limit)
        self.time_progress.setTextVisible(False)
        self.time_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                background-color: #111;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #FF9900;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.time_progress)
        
        # Zone de jeu principale (à implémenter dans les sous-classes)
        self.game_area = QWidget()
        self.game_layout = QVBoxLayout(self.game_area)
        self.layout.addWidget(self.game_area)
        
        # Zone de boutons
        self.button_area = QWidget()
        self.button_layout = QHBoxLayout(self.button_area)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.on_cancel)
        self.button_layout.addWidget(self.cancel_button)
        
        self.submit_button = QPushButton("Soumettre")
        self.submit_button.clicked.connect(self.on_submit)
        self.button_layout.addWidget(self.submit_button)
        
        self.layout.addWidget(self.button_area)
        
        # Timer pour mettre à jour le temps restant
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1 seconde
        
        # Démarrage du puzzle
        self.puzzle.start()
        
        logger.info(f"Mini-jeu de hacking initialisé pour puzzle: {puzzle.puzzle_type.name}")
    
    def update_time(self):
        """Met à jour l'affichage du temps restant"""
        self.time_left = max(0, self.puzzle.get_remaining_time())
        self.time_label.setText(f"Temps: {self.time_left:.1f}s")
        self.time_progress.setValue(self.time_left)
        
        # Changer la couleur au fur et à mesure que le temps diminue
        if self.time_left < self.puzzle.time_limit * 0.25:
            self.time_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #333;
                    border-radius: 5px;
                    background-color: #111;
                    height: 10px;
                }
                QProgressBar::chunk {
                    background-color: #FF0000;
                    border-radius: 5px;
                }
            """)
        elif self.time_left < self.puzzle.time_limit * 0.5:
            self.time_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #333;
                    border-radius: 5px;
                    background-color: #111;
                    height: 10px;
                }
                QProgressBar::chunk {
                    background-color: #FFFF00;
                    border-radius: 5px;
                }
            """)
        
        # Vérifier si le temps est écoulé
        if self.time_left <= 0 and not self.completed:
            self.complete_puzzle(False)
    
    def on_submit(self):
        """Gère la soumission de la solution (à implémenter dans les sous-classes)"""
        pass
    
    def on_cancel(self):
        """Annule le mini-jeu"""
        self.complete_puzzle(False)
    
    def complete_puzzle(self, success: bool):
        """Termine le mini-jeu"""
        if not self.completed:
            self.completed = True
            self.success = success
            self.timer.stop()
            
            # Temps utilisé
            elapsed_time = self.puzzle.time_limit - self.time_left
            
            # Terminer le puzzle
            self.puzzle.end(success)
            
            # Émettre le signal
            self.puzzle_completed.emit(success, elapsed_time)
            
            # Fermer le dialogue après un délai
            QTimer.singleShot(1000, self.close)
            
            logger.info(f"Mini-jeu terminé: {success=}, temps: {elapsed_time:.1f}s")


class PasswordBruteforceMinigame(HackingMinigameBase):
    """Mini-jeu de bruteforce de mot de passe"""
    
    def __init__(self, puzzle: PasswordBruteforcePuzzle, parent=None):
        """Initialise le mini-jeu de bruteforce"""
        super().__init__(puzzle, parent)
        
        # Configuration spécifique
        self.setWindowTitle("Bruteforce de mot de passe")
        
        # Mise en page du jeu
        self.passwords_grid = QGridLayout()
        self.game_layout.addLayout(self.passwords_grid)
        
        # Indice sur la longueur
        hint_label = QLabel(f"Longueur: {len(puzzle.data['correct_password'])}")
        hint_label.setStyleSheet("color: #AAAAAA;")
        self.game_layout.addWidget(hint_label)
        
        # Afficher les options de mot de passe
        self.password_buttons = []
        
        for i, password in enumerate(puzzle.data['password_options']):
            row, col = divmod(i, 4)
            
            password_frame = QFrame()
            password_frame.setFrameShape(QFrame.Shape.StyledPanel)
            password_frame.setStyleSheet("""
                QFrame {
                    background-color: #001122;
                    border: 1px solid #333;
                    border-radius: 5px;
                }
            """)
            
            password_layout = QVBoxLayout(password_frame)
            
            # Texte du mot de passe
            password_label = QLabel(password)
            password_label.setFont(QFont("Cascadia Code", 12))
            password_label.setStyleSheet("color: #00FF00;")
            password_layout.addWidget(password_label, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Bouton de sélection
            select_button = QPushButton("Sélectionner")
            select_button.setProperty("password", password)
            select_button.clicked.connect(self.select_password)
            password_layout.addWidget(select_button)
            
            self.passwords_grid.addWidget(password_frame, row, col)
            self.password_buttons.append(select_button)
    
    def select_password(self):
        """Sélectionne un mot de passe"""
        sender = self.sender()
        if sender:
            selected_password = sender.property("password")
            correct_password = self.puzzle.data['correct_password']
            
            success = selected_password == correct_password
            self.complete_puzzle(success)


class BufferOverflowMinigame(HackingMinigameBase):
    """Mini-jeu d'exploitation de buffer overflow"""
    
    def __init__(self, puzzle: BufferOverflowPuzzle, parent=None):
        """Initialise le mini-jeu de buffer overflow"""
        super().__init__(puzzle, parent)
        
        # Configuration spécifique
        self.setWindowTitle("Exploitation de buffer overflow")
        
        # Zone de code vulnérable
        code_label = QLabel("Code vulnérable:")
        code_label.setStyleSheet("color: #00FFFF;")
        self.game_layout.addWidget(code_label)
        
        code_frame = QFrame()
        code_frame.setFrameShape(QFrame.Shape.StyledPanel)
        code_frame.setStyleSheet("""
            QFrame {
                background-color: #001133;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        code_layout = QVBoxLayout(code_frame)
        
        # Affichage du code vulnérable
        vulnerable_code = QLabel(puzzle.data['vulnerable_code'])
        vulnerable_code.setFont(QFont("Cascadia Code", 10))
        vulnerable_code.setStyleSheet("color: #00FF00;")
        vulnerable_code.setWordWrap(True)
        code_layout.addWidget(vulnerable_code)
        
        self.game_layout.addWidget(code_frame)
        
        # Zone d'entrée pour l'exploitation
        input_label = QLabel("Entrez la charge utile d'exploitation:")
        input_label.setStyleSheet("color: #00FFFF;")
        self.game_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Cascadia Code", 10))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #000011;
                color: #FF00FF;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.input_field.setPlaceholderText("Entrez votre payload d'exploitation...")
        self.game_layout.addWidget(self.input_field)
        
        # Indice
        hint_label = QLabel(f"Indice: {puzzle.data['hint']}")
        hint_label.setStyleSheet("color: #AAAAAA; font-style: italic;")
        self.game_layout.addWidget(hint_label)
    
    def on_submit(self):
        """Vérifie la solution soumise"""
        payload = self.input_field.text()
        pattern = self.puzzle.data['exploit_pattern']
        
        # Vérification simple basée sur un motif
        success = pattern in payload
        self.complete_puzzle(success)


class SequenceMatchingMinigame(HackingMinigameBase):
    """Mini-jeu de correspondance de séquences"""
    
    def __init__(self, puzzle: SequenceMatchingPuzzle, parent=None):
        """Initialise le mini-jeu de correspondance de séquences"""
        super().__init__(puzzle, parent)
        
        # Configuration spécifique
        self.setWindowTitle("Correspondance de séquences")
        
        # Séquence correcte (caché)
        self.correct_sequence = puzzle.data['correct_sequence']
        
        # Fragments disponibles
        fragments_label = QLabel("Fragments disponibles:")
        fragments_label.setStyleSheet("color: #00FFFF;")
        self.game_layout.addWidget(fragments_label)
        
        # Grille pour les fragments
        fragments_grid = QGridLayout()
        
        self.selected_fragments = []
        self.fragment_buttons = []
        
        for i, fragment in enumerate(puzzle.data['fragments']):
            row, col = divmod(i, 5)
            
            fragment_button = QPushButton(fragment)
            fragment_button.setFont(QFont("Cascadia Code", 10))
            fragment_button.setProperty("fragment", fragment)
            fragment_button.setStyleSheet("""
                QPushButton {
                    background-color: #001122;
                    color: #00FFFF;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #002244;
                }
                QPushButton:pressed {
                    background-color: #003366;
                }
            """)
            fragment_button.clicked.connect(self.toggle_fragment)
            
            fragments_grid.addWidget(fragment_button, row, col)
            self.fragment_buttons.append(fragment_button)
        
        self.game_layout.addLayout(fragments_grid)
        
        # Séquence actuelle
        current_seq_label = QLabel("Séquence actuelle:")
        current_seq_label.setStyleSheet("color: #00FFFF;")
        self.game_layout.addWidget(current_seq_label)
        
        self.current_sequence = QLabel("")
        self.current_sequence.setFont(QFont("Cascadia Code", 12))
        self.current_sequence.setStyleSheet("""
            QLabel {
                background-color: #000022;
                color: #00FF00;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.current_sequence.setWordWrap(True)
        self.game_layout.addWidget(self.current_sequence)
        
        # Bouton pour réinitialiser
        reset_button = QPushButton("Réinitialiser la séquence")
        reset_button.clicked.connect(self.reset_sequence)
        self.game_layout.addWidget(reset_button)
    
    def toggle_fragment(self):
        """Ajoute ou retire un fragment de la séquence"""
        sender = self.sender()
        if sender:
            fragment = sender.property("fragment")
            
            if fragment in self.selected_fragments:
                self.selected_fragments.remove(fragment)
                sender.setStyleSheet("""
                    QPushButton {
                        background-color: #001122;
                        color: #00FFFF;
                        border: 1px solid #333;
                        border-radius: 5px;
                        padding: 10px;
                    }
                """)
            else:
                self.selected_fragments.append(fragment)
                sender.setStyleSheet("""
                    QPushButton {
                        background-color: #003366;
                        color: #00FFFF;
                        border: 1px solid #333;
                        border-radius: 5px;
                        padding: 10px;
                    }
                """)
            
            # Mettre à jour l'affichage de la séquence
            self.current_sequence.setText("".join(self.selected_fragments))
    
    def reset_sequence(self):
        """Réinitialise la séquence sélectionnée"""
        self.selected_fragments = []
        self.current_sequence.setText("")
        
        # Réinitialiser tous les boutons
        for button in self.fragment_buttons:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #001122;
                    color: #00FFFF;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
    
    def on_submit(self):
        """Vérifie la solution soumise"""
        current = "".join(self.selected_fragments)
        success = current == self.correct_sequence
        self.complete_puzzle(success)


class NetworkReroutingMinigame(HackingMinigameBase):
    """Mini-jeu de réacheminement de réseau"""
    
    def __init__(self, puzzle: NetworkReroutingPuzzle, parent=None):
        """Initialise le mini-jeu de réacheminement de réseau"""
        super().__init__(puzzle, parent)
        
        # Configuration spécifique
        self.setWindowTitle("Réacheminement de réseau")
        
        # Définir les nœuds et connexions
        self.nodes = puzzle.data['nodes']
        self.connections = puzzle.data['connections']
        self.target_path = puzzle.data['target_path']
        self.current_path = []
        
        # Vue graphique du réseau
        network_view = QGraphicsView()
        network_view.setRenderHint(network_view.RenderHint.Antialiasing)
        network_view.setMinimumHeight(300)
        
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#001133")))
        network_view.setScene(self.scene)
        
        self.game_layout.addWidget(network_view)
        
        # Créer et positionner les nœuds graphiquement
        self.node_items = {}
        self.connection_items = {}
        self.create_network_visualization()
        
        # Info sur le chemin actuel
        path_label = QLabel("Chemin actuel:")
        path_label.setStyleSheet("color: #00FFFF;")
        self.game_layout.addWidget(path_label)
        
        self.path_display = QLabel("")
        self.path_display.setFont(QFont("Cascadia Code", 10))
        self.path_display.setStyleSheet("color: #00FF00;")
        self.path_display.setWordWrap(True)
        self.game_layout.addWidget(self.path_display)
        
        # Bouton de réinitialisation
        reset_button = QPushButton("Réinitialiser le chemin")
        reset_button.clicked.connect(self.reset_path)
        self.game_layout.addWidget(reset_button)
    
    def create_network_visualization(self):
        """Crée la visualisation du réseau"""
        # Position des nœuds
        positions = {}
        rows = max(3, math.ceil(math.sqrt(len(self.nodes))))
        cols = math.ceil(len(self.nodes) / rows)
        
        width, height = 700, 250
        margin = 50
        
        # Calculer les positions des nœuds
        for i, node_id in enumerate(self.nodes):
            row, col = divmod(i, cols)
            x = margin + col * ((width - 2 * margin) / (cols - 1 if cols > 1 else 1))
            y = margin + row * ((height - 2 * margin) / (rows - 1 if rows > 1 else 1))
            positions[node_id] = (x, y)
        
        # Créer les connexions
        for source, target in self.connections:
            source_pos = positions[source]
            target_pos = positions[target]
            
            line = QGraphicsLineItem(source_pos[0], source_pos[1], target_pos[0], target_pos[1])
            line.setPen(QPen(QColor("#333333"), 2))
            self.scene.addItem(line)
            
            self.connection_items[(source, target)] = line
        
        # Créer les nœuds
        for node_id, (x, y) in positions.items():
            # Rectangle pour le nœud
            rect = QGraphicsRectItem(x - 25, y - 15, 50, 30)
            rect.setPen(QPen(QColor("#00FFFF"), 2))
            rect.setBrush(QBrush(QColor("#002244")))
            
            # Texte du nœud
            text = self.scene.addText(node_id)
            text.setPos(x - 20, y - 10)
            text.setDefaultTextColor(QColor("#FFFFFF"))
            
            # Rendre le nœud cliquable
            proxy = self.scene.addRect(x - 25, y - 15, 50, 30)
            proxy.setPen(QPen(Qt.PenStyle.NoPen))
            proxy.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            proxy.setData(0, node_id)
            proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            
            self.node_items[node_id] = (rect, text, proxy)
    
    def mousePressEvent(self, event):
        """Gère les clics sur les nœuds"""
        super().mousePressEvent(event)
        
        # Vérifier si un nœud a été cliqué
        item = self.scene.itemAt(self.mapToScene(event.pos()), self.view.transform())
        
        if item and item.data(0):
            node_id = item.data(0)
            self.select_node(node_id)
    
    def select_node(self, node_id):
        """Sélectionne un nœud pour le chemin"""
        # Vérifier si ce nœud peut être ajouté au chemin
        if len(self.current_path) == 0 or (
            self.current_path[-1] != node_id and
            (self.current_path[-1], node_id) in self.connections
        ):
            # Ajouter au chemin
            self.current_path.append(node_id)
            
            # Mettre à jour l'affichage du chemin
            self.path_display.setText(" -> ".join(self.current_path))
            
            # Mettre en évidence le nœud
            rect, _, _ = self.node_items[node_id]
            rect.setBrush(QBrush(QColor("#00AAFF")))
            
            # Mettre en évidence la connexion si ce n'est pas le premier nœud
            if len(self.current_path) > 1:
                source = self.current_path[-2]
                target = node_id
                
                if (source, target) in self.connection_items:
                    conn = self.connection_items[(source, target)]
                    conn.setPen(QPen(QColor("#00FFFF"), 3))
    
    def reset_path(self):
        """Réinitialise le chemin actuel"""
        self.current_path = []
        self.path_display.setText("")
        
        # Réinitialiser les couleurs
        for node_id, (rect, _, _) in self.node_items.items():
            rect.setBrush(QBrush(QColor("#002244")))
        
        for conn in self.connection_items.values():
            conn.setPen(QPen(QColor("#333333"), 2))
    
    def on_submit(self):
        """Vérifie la solution soumise"""
        success = self.current_path == self.target_path
        self.complete_puzzle(success)


class HackingMinigameFactory:
    """Fabrique de mini-jeux de hacking"""
    
    @staticmethod
    def create_minigame(puzzle: HackingPuzzle, parent=None) -> HackingMinigameBase:
        """Crée un mini-jeu de hacking en fonction du type de puzzle"""
        if puzzle.puzzle_type == HackingPuzzleType.PASSWORD_BRUTEFORCE:
            return PasswordBruteforceMinigame(puzzle, parent)
        elif puzzle.puzzle_type == HackingPuzzleType.BUFFER_OVERFLOW:
            return BufferOverflowMinigame(puzzle, parent)
        elif puzzle.puzzle_type == HackingPuzzleType.SEQUENCE_MATCHING:
            return SequenceMatchingMinigame(puzzle, parent)
        elif puzzle.puzzle_type == HackingPuzzleType.NETWORK_REROUTING:
            return NetworkReroutingMinigame(puzzle, parent)
        else:
            logger.warning(f"Type de puzzle non pris en charge: {puzzle.puzzle_type}")
            return None
