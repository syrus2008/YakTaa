"""
Module pour le widget de carte du jeu YakTaa
"""

import logging
import math
import random
from typing import Optional, List, Dict, Any, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QPushButton, QComboBox, QScrollArea, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem,  # Ajout de QGraphicsPixmapItem
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem,
    QDialog, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QPixmap, QColor, QPen, QBrush, QFont, QPainter, QTransform, QPainterPath

from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.Map")

class MapLocation:
    """Classe représentant un lieu sur la carte"""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 x: float, 
                 y: float, 
                 type: str, 
                 description: str,
                 connections: List[str] = None):
        """Initialise un lieu sur la carte"""
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.type = type  # city, district, poi, etc.
        self.description = description
        self.connections = connections or []
        self.discovered = False
        self.visited = False
        self.current = False

class MapView(QGraphicsView):
    """Vue graphique pour la carte"""
    
    # Signal émis lorsqu'un lieu est sélectionné
    location_selected = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialise la vue de la carte"""
        super().__init__(parent)
        
        # Configuration de la vue
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Scène de la carte
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Facteur de zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        
        # Éléments de la carte
        self.background = None
        self.locations = {}
        self.connections = []
        self.current_location_id = None
        
        # Styles cyberpunk améliorés
        self.city_color = QColor(0, 170, 255)  # Bleu néon
        self.district_color = QColor(0, 255, 170)  # Vert néon
        self.poi_color = QColor(255, 170, 0)  # Orange néon
        self.server_color = QColor(255, 0, 255)  # Magenta néon
        self.hub_color = QColor(255, 255, 0)  # Jaune néon
        
        self.connection_color = QColor(100, 100, 150, 150)  # Connexions semi-transparentes
        self.secure_connection_color = QColor(255, 0, 0, 150)  # Connexions sécurisées
        
        self.current_color = QColor(255, 50, 50)  # Rouge vif
        self.visited_color = QColor(50, 255, 50)  # Vert vif
        self.discovered_color = QColor(255, 255, 50)  # Jaune vif
        self.undiscovered_color = QColor(80, 80, 80)  # Gris sombre
        
        # Effet de grille cyberpunk
        self._draw_grid()
    
    def _draw_grid(self):
        """Dessine une grille de style cyberpunk sur le fond"""
        if not self.background:
            return
            
        # Taille de la grille
        width = 800
        height = 600
        grid_size = 50
        
        # Créer les lignes de la grille
        for x in range(0, width + 1, grid_size):
            line = QGraphicsLineItem(x, 0, x, height)
            line.setPen(QPen(QColor(40, 40, 80, 100), 1, Qt.PenStyle.DotLine))
            line.setZValue(-0.5)
            self.scene.addItem(line)
            
        for y in range(0, height + 1, grid_size):
            line = QGraphicsLineItem(0, y, width, y)
            line.setPen(QPen(QColor(40, 40, 80, 100), 1, Qt.PenStyle.DotLine))
            line.setZValue(-0.5)
            self.scene.addItem(line)
    
    def wheelEvent(self, event):
        """Gère le zoom avec la molette de la souris"""
        factor = 1.2
        
        if event.angleDelta().y() < 0:
            # Zoom out
            factor = 1.0 / factor
            self.zoom_factor = max(self.min_zoom, self.zoom_factor * factor)
        else:
            # Zoom in
            self.zoom_factor = min(self.max_zoom, self.zoom_factor * factor)
        
        self.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))
    
    def set_background(self, pixmap: QPixmap):
        """Définit l'image de fond de la carte"""
        if self.background:
            self.scene.removeItem(self.background)
        
        self.background = self.scene.addPixmap(pixmap)
        self.background.setZValue(-1)
        self.scene.setSceneRect(self.background.boundingRect())
    
    def add_location(self, location: MapLocation, override_color: QColor = None):
        """Ajoute un lieu à la carte"""
        # Création de l'élément graphique pour le lieu
        if location.type == "city":
            size = 20
            color = self.city_color
        elif location.type == "district":
            size = 15
            color = self.district_color
        elif location.type == "server":
            size = 18
            color = self.server_color
        elif location.type == "hub":
            size = 22
            color = self.hub_color
        else:
            size = 12
            color = self.poi_color
        
        if override_color:
            color = override_color
        
        # Statut du lieu
        if location.current:
            outline_color = self.current_color
            outline_width = 3
        elif location.visited:
            outline_color = self.visited_color
            outline_width = 2
        elif location.discovered:
            outline_color = self.discovered_color
            outline_width = 2
        else:
            outline_color = self.undiscovered_color
            outline_width = 1
        
        # Texte du lieu - positionné à gauche du point
        font = QFont("Consolas", 8)
        if location.current:
            font.setBold(True)
            
        text = QGraphicsTextItem(location.name)
        text.setFont(font)
        
        # Créer d'abord le point (mais ne pas l'ajouter à la scène tout de suite)
        ellipse = QGraphicsEllipseItem(0, 0, size, size)
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(outline_color, outline_width))
        ellipse.setData(0, location.id)
        ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        ellipse.setZValue(1)
        
        # Positionner le point
        ellipse.setPos(location.x - size/2, location.y - size/2)  # Point centré à la position
        
        # Positionner le texte à côté du point avec un décalage pour la lisibilité
        text_width = text.boundingRect().width()
        min_margin = 70  # Marge minimale à respecter du bord gauche
        
        # Si le texte risque de dépasser à gauche, le placer à droite du point
        if location.x - text_width - 5 < min_margin:
            text.setPos(location.x + size/2 + 5, location.y - 6)  # Texte à droite du point
        else:
            text.setPos(location.x - text_width - size/2 - 5, location.y - 6)  # Texte à gauche du point
            
        text.setDefaultTextColor(Qt.GlobalColor.white)
        text.setZValue(1)
        
        # Effet de lueur (glow) pour les lieux découverts
        if location.discovered:
            glow_size = size + 10
            glow = QGraphicsEllipseItem(0, 0, glow_size, glow_size)
            glow.setPos(ellipse.pos().x() - (glow_size - size)/2, ellipse.pos().y() - (glow_size - size)/2)
            glow.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
            glow.setPen(QPen(Qt.PenStyle.NoPen))
            glow.setZValue(0.5)
            self.scene.addItem(glow)
        
        # Ajout à la scène
        self.scene.addItem(text)
        self.scene.addItem(ellipse)
        
        # Stockage des éléments
        self.locations[location.id] = {
            "location": location,
            "ellipse": ellipse,
            "text": text
        }
    
    def add_connection(self, from_id: str, to_id: str, secure: bool = False):
        """Ajoute une connexion entre deux lieux"""
        if from_id not in self.locations or to_id not in self.locations:
            return
        
        from_loc = self.locations[from_id]["location"]
        to_loc = self.locations[to_id]["location"]
        
        # Déterminer le style de la connexion
        if secure:
            pen = QPen(self.secure_connection_color, 2, Qt.PenStyle.DashLine)
        else:
            pen = QPen(self.connection_color, 1.5, Qt.PenStyle.DashLine)
        
        # Création de la ligne de connexion
        line = QGraphicsLineItem(from_loc.x, from_loc.y, to_loc.x, to_loc.y)
        line.setPen(pen)
        line.setZValue(0)
        
        # Ajout à la scène
        self.scene.addItem(line)
        self.connections.append(line)
    
    def clear_map(self):
        """Efface tous les éléments de la carte"""
        # Supprimer d'abord les connexions
        for connection in self.connections:
            self.scene.removeItem(connection)
        
        # Supprimer ensuite les lieux
        for loc_id, loc_data in self.locations.items():
            if "ellipse" in loc_data:
                self.scene.removeItem(loc_data["ellipse"])
            if "text" in loc_data:
                self.scene.removeItem(loc_data["text"])
        
        # Vider les collections
        self.locations = {}
        self.connections = []
        self.background = None
        
        # Effacer complètement la scène
        self.scene.clear()
        
        logger.info("Carte complètement effacée")
    
    def set_current_location(self, location_id: str):
        """Définit le lieu actuel du joueur"""
        # Réinitialisation du lieu précédent
        if self.current_location_id and self.current_location_id in self.locations:
            prev_loc = self.locations[self.current_location_id]
            prev_loc["location"].current = False
            
            if prev_loc["location"].visited:
                outline_color = self.visited_color
            elif prev_loc["location"].discovered:
                outline_color = self.discovered_color
            else:
                outline_color = self.undiscovered_color
            
            prev_loc["ellipse"].setPen(QPen(outline_color, 2))
        
        # Mise à jour du lieu actuel
        if location_id in self.locations:
            self.current_location_id = location_id
            curr_loc = self.locations[location_id]
            curr_loc["location"].current = True
            curr_loc["location"].visited = True
            curr_loc["ellipse"].setPen(QPen(self.current_color, 3))
            
            # Centrer la vue sur le lieu actuel
            self.centerOn(curr_loc["ellipse"])
    
    def mousePressEvent(self, event):
        """Gère les clics de souris sur la carte"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Récupération de l'élément cliqué
            item = self.itemAt(event.pos())
            
            if isinstance(item, QGraphicsEllipseItem):
                location_id = item.data(0)
                if location_id:
                    self.location_selected.emit(location_id)
        
        super().mousePressEvent(event)


class ExplorationDialog(QDialog):
    """Boîte de dialogue pour afficher les résultats de l'exploration"""
    
    def __init__(self, location_name: str, results: str, parent=None):
        """Initialise la boîte de dialogue d'exploration"""
        super().__init__(parent)
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle(f"Exploration de {location_name}")
        self.setMinimumSize(500, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #3a3a5a;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2a2a4a;
                color: #e0e0e0;
                border: 1px solid #3a3a5a;
                padding: 5px 15px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #3a3a6a;
            }
        """)
        
        # Mise en page
        layout = QVBoxLayout(self)
        
        # Zone de texte pour les résultats
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setHtml(results)
        layout.addWidget(self.results_text)
        
        # Bouton de fermeture
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class TravelDialog(QDialog):
    """Boîte de dialogue pour afficher les informations de voyage"""
    
    def __init__(self, from_location: str, to_location: str, travel_time: int, parent=None):
        """Initialise la boîte de dialogue de voyage"""
        super().__init__(parent)
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle(f"Voyage vers {to_location}")
        self.setMinimumSize(400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Consolas', monospace;
            }
            QProgressBar {
                border: 1px solid #3a3a5a;
                border-radius: 3px;
                background-color: #0f0f1a;
                text-align: center;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #00aaff;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Mise en page
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel(f"<h2>Voyage vers {to_location}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Informations
        info = QLabel(f"<p>Départ: <b>{from_location}</b></p><p>Destination: <b>{to_location}</b></p>")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Animation de voyage (simulée avec une barre de progression)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Message de voyage
        self.status = QLabel("Préparation du voyage...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        
        # Timer pour simuler le voyage
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(travel_time * 10)  # Plus le voyage est long, plus l'animation est lente
        
        # Variables pour l'animation
        self.progress_value = 0
        self.travel_messages = [
            "Préparation du voyage...",
            "En route...",
            "Navigation en cours...",
            "Traversée des zones urbaines...",
            "Contournement des points de contrôle...",
            "Arrivée imminente...",
            "Voyage terminé!"
        ]
        self.current_message = 0
    
    def _update_progress(self):
        """Met à jour la barre de progression et les messages"""
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        
        # Mettre à jour le message en fonction de la progression
        message_index = int(self.progress_value / 100 * (len(self.travel_messages) - 1))
        if message_index != self.current_message:
            self.current_message = message_index
            self.status.setText(self.travel_messages[message_index])
        
        # Fermer la boîte de dialogue lorsque le voyage est terminé
        if self.progress_value >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self.accept)  # Attendre un peu avant de fermer


class MapWidget(QWidget):
    """Widget complet de la carte"""
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise le widget de carte"""
        super().__init__(parent)
        
        # Référence au jeu
        self.game = game
        
        # Mise en page
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        
        # Barre d'outils
        self._create_toolbar()
        
        # Vue de la carte
        self.map_view = MapView(self)
        self.layout.addWidget(self.map_view)
        
        # Panneau d'informations
        self._create_info_panel()
        
        # Connexion des signaux
        self.map_view.location_selected.connect(self._on_location_selected)
        
        # Chargement des données de la carte
        self._load_map_data()
        
        # Timer pour les mises à jour
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # 10 FPS
        
        # Mode d'affichage (ville ou bâtiment)
        self.display_mode = "city"  # "city" ou "building"
        self.current_building_id = None
        self.current_building = None
        
        logger.info("Widget de carte initialisé")
    
    def _create_toolbar(self):
        """Crée la barre d'outils de la carte"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(10)
        
        # Sélecteur de carte
        self.map_selector = QComboBox()
        self.map_selector.addItem("Monde")
        self.map_selector.addItem("Ville actuelle")
        self.map_selector.currentIndexChanged.connect(self._on_map_changed)
        toolbar_layout.addWidget(QLabel("Carte:"))
        toolbar_layout.addWidget(self.map_selector)
        
        # Sélecteur de filtre
        self.filter_selector = QComboBox()
        self.filter_selector.addItem("Tous")
        self.filter_selector.addItem("Villes")
        self.filter_selector.addItem("Districts")
        self.filter_selector.addItem("Points d'intérêt")
        self.filter_selector.currentIndexChanged.connect(self._on_filter_changed)
        toolbar_layout.addWidget(QLabel("Filtre:"))
        toolbar_layout.addWidget(self.filter_selector)
        
        # Bouton de retour (pour revenir du mode bâtiment au mode ville)
        self.back_button = QPushButton("Retour à la ville")
        self.back_button.clicked.connect(self._on_back_to_city)
        self.back_button.setVisible(False)  # Caché par défaut
        toolbar_layout.addWidget(self.back_button)
        
        # Spacer
        toolbar_layout.addStretch()
        
        # Boutons de zoom
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(self._zoom_in)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(self._zoom_out)
        
        reset_view_btn = QPushButton("⟲")
        reset_view_btn.setFixedSize(30, 30)
        reset_view_btn.clicked.connect(self._reset_view)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(5)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(reset_view_btn)
        
        toolbar_layout.addLayout(zoom_layout)
        
        self.layout.addLayout(toolbar_layout)
    
    def _create_info_panel(self):
        """Crée le panneau d'informations sur le lieu sélectionné"""
        info_panel = QFrame()
        info_panel.setFrameShape(QFrame.Shape.StyledPanel)
        info_panel.setFrameShadow(QFrame.Shadow.Raised)
        info_panel.setMinimumHeight(150)
        info_panel.setMaximumHeight(200)
        
        info_layout = QVBoxLayout(info_panel)
        
        # Titre
        self.info_title = QLabel("Informations sur le lieu")
        self.info_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.info_title)
        
        # Description
        self.info_description = QLabel("Sélectionnez un lieu sur la carte pour afficher ses informations.")
        self.info_description.setWordWrap(True)
        self.info_description.setStyleSheet("color: #CCCCCC;")
        info_layout.addWidget(self.info_description)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        
        self.travel_btn = QPushButton("Voyager")
        self.travel_btn.setEnabled(False)
        self.travel_btn.clicked.connect(self._on_travel)
        action_layout.addWidget(self.travel_btn)
        
        self.explore_btn = QPushButton("Explorer")
        self.explore_btn.setEnabled(False)
        self.explore_btn.clicked.connect(self._on_explore)
        action_layout.addWidget(self.explore_btn)
        
        # Bouton pour entrer dans un bâtiment
        self.enter_building_btn = QPushButton("Entrer")
        self.enter_building_btn.setVisible(False)
        self.enter_building_btn.clicked.connect(self._on_enter_building)
        action_layout.addWidget(self.enter_building_btn)
        
        # Bouton pour entrer dans une pièce (visible uniquement en mode bâtiment)
        self.enter_room_btn = QPushButton("Entrer dans la pièce")
        self.enter_room_btn.setVisible(False)
        self.enter_room_btn.setEnabled(False)
        self.enter_room_btn.clicked.connect(self._on_enter_room)
        action_layout.addWidget(self.enter_room_btn)
        
        info_layout.addLayout(action_layout)
        
        self.layout.addWidget(info_panel)
    
    def _load_map_data(self):
        """Charge les données de la carte depuis le gestionnaire de monde"""
        # Effacer la carte actuelle
        self.map_view.clear_map()
        
        # Vérifier si le gestionnaire de monde est disponible
        if not self.game or not hasattr(self.game, 'world_manager'):
            logger.warning("Gestionnaire de monde non disponible, chargement des données de test")
            self._load_test_map_data()
            return
        
        # Charger l'image de fond avec un style cyberpunk
        background = QPixmap(800, 600)
        background.fill(QColor(20, 20, 40))
        self.map_view.set_background(background)
        
        # Récupérer les lieux depuis le gestionnaire de monde
        all_locations = self.game.world_manager.get_all_locations()
        
        if not all_locations:
            logger.warning("Aucun lieu trouvé dans le monde actif, chargement des données de test")
            self._load_test_map_data()
            return
        
        # Obtenir le filtre actuel
        current_filter = self.filter_selector.currentText().lower()
        logger.debug(f"Filtre actuel: {current_filter}")
        
        # Identifier les villes principales (pour n'importe quel filtre)
        main_cities = {}  # {nom_ville: premier_lieu_de_cette_ville}
        
        # Première étape : regrouper les lieux par nom de base de ville
        city_groups = {}
        for location in all_locations:
            # Extraire le nom de base (partie avant le tiret)
            location_name = location.name if hasattr(location, 'name') else "Inconnu"
            base_name = location_name.split(' - ')[0].strip() if ' - ' in location_name else location_name
            
            if base_name not in city_groups:
                city_groups[base_name] = []
            city_groups[base_name].append(location)
        
        # Deuxième étape : pour chaque groupe, identifier la ville principale
        for base_name, locations in city_groups.items():
            # Chercher un lieu de type 'city' ou 'ville'
            main_city = None
            for location in locations:
                location_type = location.type.lower() if hasattr(location, 'type') and location.type else ""
                if location_type in ('city', 'ville'):
                    main_city = location
                    break
            
            # Si aucun lieu n'est explicitement marqué comme ville, prendre le premier sans tiret
            if not main_city:
                for location in locations:
                    if ' - ' not in location.name:
                        main_city = location
                        break
            
            # En dernier recours, prendre le premier lieu du groupe
            if not main_city and locations:
                main_city = locations[0]
            
            if main_city:
                main_cities[base_name] = main_city
        
        # Filtrer les lieux selon le mode de filtre
        filtered_locations = []
        if current_filter == "tous":
            # Pour le filtre "Tous", n'inclure que les villes principales
            filtered_locations = list(main_cities.values())
        elif current_filter == "villes":
            # Inclure uniquement les lieux de type 'city' ou 'ville'
            for location in all_locations:
                location_type = location.type.lower() if hasattr(location, 'type') and location.type else ""
                if location_type in ('city', 'ville'):
                    filtered_locations.append(location)
            
            # Si aucune ville n'est trouvée, utiliser les villes principales
            if not filtered_locations:
                filtered_locations = list(main_cities.values())
        elif current_filter == "districts":
            # Inclure uniquement les districts (qui ont un tiret dans le nom)
            for location in all_locations:
                if ' - ' in location.name:
                    filtered_locations.append(location)
        elif current_filter == "points d'intérêt":
            # Points d'intérêt (à définir selon votre logique)
            for location in all_locations:
                location_type = location.type.lower() if hasattr(location, 'type') and location.type else ""
                if location_type in ('poi', 'landmark', 'special'):
                    filtered_locations.append(location)
        else:
            # Par défaut, n'afficher que les villes principales
            filtered_locations = list(main_cities.values())
        
        # Si aucun lieu n'est sélectionné après filtrage, revenir aux villes principales
        if not filtered_locations:
            filtered_locations = list(main_cities.values())
            logger.warning(f"Aucun lieu disponible avec le filtre '{current_filter}', affichage des villes principales")
        
        # Calculer les coordonnées pour l'affichage
        width, height = 700, 500
        margin = 50
        
        # Récupérer les coordonnées existantes ou en générer de nouvelles
        locations_with_coords = {}
        for location in filtered_locations:
            # Vérifier si le lieu a déjà des coordonnées définies
            if hasattr(location, 'x') and hasattr(location, 'y') and location.x and location.y:
                x, y = location.x, location.y
            else:
                # Générer des coordonnées aléatoires mais déterministes basées sur l'ID
                seed = sum(ord(c) for c in location.id)
                import random
                random.seed(seed)
                x = margin + random.random() * (width - 2 * margin)
                y = margin + random.random() * (height - 2 * margin)
            
            # Extraire le nom simplifié pour les villes principales
            display_name = location.name
            if current_filter in ("tous", "villes"):
                # Simplifier le nom pour l'affichage
                display_name = display_name.split(' - ')[0].strip() if ' - ' in display_name else display_name
            
            # Créer l'objet MapLocation
            map_location = MapLocation(
                id=location.id,
                name=display_name,  # Utiliser le nom simplifié
                x=x,
                y=y,
                type=location.type if hasattr(location, 'type') else "city",
                description=location.description if hasattr(location, 'description') else "",
                connections=location.connections if hasattr(location, 'connections') else []
            )
            
            # Définir le statut du lieu
            current_location_id = self.game.world_manager.current_location_id
            map_location.current = (location.id == current_location_id)
            map_location.visited = (location.id in self.game.world_manager.visited_locations)
            map_location.discovered = (location.id in self.game.world_manager.discovered_locations or 
                                      map_location.visited or map_location.current)
            
            locations_with_coords[location.id] = map_location
        
        # Ajouter les lieux filtrés à la carte
        for location_id, map_location in locations_with_coords.items():
            self.map_view.add_location(map_location)
        
        # Pour les connexions, créer des liens directs entre villes principales
        if current_filter in ("tous", "villes"):
            # Utiliser un set pour éviter les doublons de connexions
            added_connections = set()
            
            # Pour chaque lieu sur la carte
            for source_id, source_location in locations_with_coords.items():
                # Explorer les connexions jusqu'à 2 niveaux de profondeur
                connected_cities = set()
                
                def explore_connections(loc_id, depth=0, max_depth=2):
                    """Explore récursivement les connexions pour trouver les villes connectées"""
                    if depth > max_depth:
                        return
                    
                    # Obtenir le lieu et ses connexions
                    source_loc = None
                    for loc in all_locations:
                        if loc.id == loc_id:
                            source_loc = loc
                            break
                    
                    if not source_loc or not hasattr(source_loc, 'connections'):
                        return
                    
                    # Explorer chaque connexion
                    for conn_id in source_loc.connections:
                        # Si c'est une ville sur la carte, l'ajouter
                        if conn_id in locations_with_coords:
                            connected_cities.add(conn_id)
                        else:
                            # Sinon, explorer récursivement si nous n'avons pas atteint la profondeur max
                            explore_connections(conn_id, depth + 1, max_depth)
                
                # Explorer les connexions pour cette ville
                explore_connections(source_id)
                
                # Ajouter les connexions à la carte
                for target_id in connected_cities:
                    # Éviter les doublons et les connexions sur soi-même
                    connection_key = tuple(sorted([source_id, target_id]))
                    if source_id != target_id and connection_key not in added_connections:
                        added_connections.add(connection_key)
                        
                        # Toujours considérer les connexions entre villes principales comme sécurisées
                        self.map_view.add_connection(source_id, target_id, True)
        else:
            # Pour les autres modes de filtre, utiliser les connexions directes
            for location_id, map_location in locations_with_coords.items():
                for target_id in map_location.connections:
                    if target_id in locations_with_coords:
                        # Déterminer si la connexion est sécurisée
                        is_secure = (sum(ord(c) for c in location_id + target_id) % 5 == 0)
                        self.map_view.add_connection(location_id, target_id, is_secure)
        
        # Définir le lieu actuel
        if self.game.world_manager.current_location_id:
            self.map_view.set_current_location(self.game.world_manager.current_location_id)
            
            # Centrer la vue sur le lieu actuel
            if self.game.world_manager.current_location_id in self.map_view.locations:
                curr_loc = self.map_view.locations[self.game.world_manager.current_location_id]
                self.map_view.centerOn(curr_loc["ellipse"])
        
        logger.info(f"Carte chargée avec {len(locations_with_coords)} lieux filtrés")
    
    def _load_test_map_data(self):
        """Charge des données de test pour la carte"""
        # Chargement de l'image de fond
        background = QPixmap(800, 600)
        background.fill(QColor(20, 20, 40))
        self.map_view.set_background(background)
        
        # Création des lieux
        cities = [
            MapLocation("tokyo", "Neo-Tokyo", 200, 300, "city", 
                       "Mégalopole japonaise, centre technologique de l'Asie"),
            MapLocation("shanghai", "Shanghai-X", 350, 320, "city",
                       "Plaque tournante du commerce et de la cybernétique"),
            MapLocation("angeles", "New Angeles", 100, 200, "city",
                       "Anciennement Los Angeles, capitale du divertissement numérique"),
            MapLocation("berlin", "Neu-Berlin", 400, 150, "city",
                       "Centre européen de la cybersécurité et de l'IA"),
        ]
        
        # Ajout des lieux à la carte
        for city in cities:
            if city.id == "tokyo":
                city.discovered = True
                city.visited = True
                city.current = True
            elif city.id in ["shanghai", "angeles"]:
                city.discovered = True
            
            self.map_view.add_location(city)
        
        # Ajout des connexions
        self.map_view.add_connection("tokyo", "shanghai")
        self.map_view.add_connection("tokyo", "angeles")
        self.map_view.add_connection("shanghai", "berlin")
        
        # Définition du lieu actuel
        self.map_view.set_current_location("tokyo")
    
    def _on_back_to_city(self):
        """Retourne à l'affichage de la ville depuis l'affichage d'un bâtiment"""
        # Informer le CityManager de la sortie du bâtiment
        if self.game and hasattr(self.game, 'city_manager'):
            self.game.city_manager.exit_building()
            logger.info("CityManager informé de la sortie du bâtiment")
        
        # Changer le mode d'affichage
        self.display_mode = "city"
        
        # Réinitialiser les variables de bâtiment
        self.current_building_id = None
        self.current_building = None
        self.selected_room_id = None
        
        # Recharger les données de la carte de la ville
        self.map_view.clear_map()
        
        # Mettre à jour l'interface utilisateur selon le mode d'affichage
        self._update_ui_for_display_mode()
        
        # Changer l'index du combobox pour déclencher le chargement de la carte de la ville
        if hasattr(self, 'map_selector') and self.map_selector:
            current_index = self.map_selector.currentIndex()
            if current_index == 1:  # Si on est déjà sur l'index de la ville
                # Forcer le rechargement de la carte de la ville
                self._on_map_changed(1)
            else:
                # Changer l'index pour déclencher le chargement
                self.map_selector.setCurrentIndex(1)
        else:
            # Fallback si le sélecteur n'est pas disponible
            self._load_map_data()
        
        logger.info("Retour à la carte de la ville")
    
    def _on_location_selected(self, location_id: str):
        """Gère la sélection d'un lieu sur la carte"""
        if self.display_mode == "city":
            # Logique existante pour la sélection d'un lieu dans une ville
            location = None
            for loc in self.map_view.locations.values():
                if loc["location"].id == location_id:
                    location = loc["location"]
                    break
            
            if not location:
                return
            
            # Mise à jour du panneau d'informations
            self.info_title.setText(location.name)
            self.info_description.setText(location.description)
            
            # Vérifier si le lieu est accessible
            can_travel = location.discovered and location_id != self.map_view.current_location_id
            self.travel_btn.setEnabled(can_travel)
            
            # Vérifier si le lieu est explorable
            self.explore_btn.setEnabled(location.discovered)
            
            # Vérifier s'il s'agit d'un bâtiment
            if self.game and hasattr(self.game, 'city_manager'):
                building = self.game.city_manager.get_building(location_id)
                if building:
                    # Activer le bouton d'entrée dans le bâtiment
                    self.enter_building_btn.setVisible(True)
                    self.enter_building_btn.setEnabled(True)
                    self.current_building_id = location_id
                    self.current_building = building
                else:
                    self.enter_building_btn.setVisible(False)
            
            # Mettre à jour la sélection
            self.selected_location_id = location_id
        
        elif self.display_mode == "building":
            # Logique pour la sélection d'une pièce dans un bâtiment
            room_id = location_id
            if self.current_building and room_id in self.current_building.rooms:
                room = self.current_building.rooms[room_id]
                
                # Mise à jour du panneau d'informations
                self.info_title.setText(room["name"])
                self.info_description.setText(room["description"])
                
                # Activer le bouton d'entrée dans la pièce
                self.enter_room_btn.setEnabled(True)
                
                # Mettre à jour la sélection
                self.selected_room_id = room_id
    
    def _on_map_changed(self, index: int):
        """Gère le changement de carte"""
        logger.info(f"Changement de carte demandé : index={index}")
        
        # Effacer complètement la scène actuelle avant de changer de carte
        self.map_view.clear_map()
        
        # Définir le mode d'affichage en fonction de l'index
        if index == 0:  # Monde
            self.display_mode = "world"
        elif index == 1:  # Ville
            self.display_mode = "city"
        
        # Réinitialiser les variables de sélection
        self.selected_location_id = None
        self.selected_room_id = None
        
        # Si on quitte le mode bâtiment, réinitialiser les variables de bâtiment
        if self.display_mode != "building":
            self.current_building_id = None
            self.current_building = None
        
        # Mettre à jour l'interface utilisateur selon le mode d'affichage
        self._update_ui_for_display_mode()
        
        if index == 0:  # Monde
            # Charger la carte du monde
            self._load_map_data()
            logger.info("Changement vers la carte du monde")
        elif index == 1:  # Ville actuelle
            # Charger la carte de la ville actuelle
            if self.game and hasattr(self.game, 'world_manager') and self.game.world_manager.current_location_id:
                current_city = self.game.world_manager.get_current_location()
                logger.info(f"Ville actuelle : {current_city.name if current_city else 'Aucune'}")
                if current_city:
                    # Créer un fond amélioré pour la ville avec style cyberpunk
                    self._create_cyberpunk_city_background()
                    
                    # Récupérer les bâtiments de la ville
                    if hasattr(self.game, 'city_manager'):
                        logger.info(f"Récupération des bâtiments pour la ville {current_city.id}")
                        buildings = self.game.city_manager.get_buildings_in_city(current_city.id)
                        logger.info(f"Nombre de bâtiments récupérés : {len(buildings)}")
                        
                        if buildings:
                            # Organiser les bâtiments par type pour un affichage plus structuré
                            building_types = {}
                            for building_id, building in buildings.items():
                                btype = getattr(building, 'type', "UNKNOWN")
                                if btype not in building_types:
                                    building_types[btype] = []
                                building_types[btype].append((building_id, building))
                            
                            # Paramètres pour l'affichage
                            width, height = 800, 600
                            margin = 50
                            zone_height = (height - 2 * margin) / max(len(building_types), 1)
                            
                            # Couleurs spécifiques pour chaque type de bâtiment
                            building_colors = {
                                "CORPORATE": QColor(0, 180, 255, 200),    # Bleu corporatif
                                "RESIDENTIAL": QColor(0, 255, 180, 200),  # Vert résidentiel
                                "COMMERCIAL": QColor(255, 180, 0, 200),   # Orange commercial
                                "GOVERNMENT": QColor(255, 60, 60, 200),   # Rouge gouvernemental
                                "MEDICAL": QColor(60, 255, 130, 200),     # Vert médical
                                "ENTERTAINMENT": QColor(255, 60, 255, 200), # Rose divertissement
                                "UNKNOWN": QColor(150, 150, 150, 200)     # Gris par défaut
                            }
                            
                            # Ajouter une étiquette de district pour chaque type de bâtiment
                            zone_y = margin
                            type_labels = {
                                "CORPORATE": "District Corporatif",
                                "RESIDENTIAL": "Zone Résidentielle",
                                "COMMERCIAL": "Quartier Commercial", 
                                "GOVERNMENT": "Secteur Gouvernemental",
                                "MEDICAL": "Complexe Médical",
                                "ENTERTAINMENT": "District des Loisirs",
                                "UNKNOWN": "Zone Non-classifiée"
                            }
                            
                            # Ajouter les bâtiments à la carte par zone
                            for zone_index, (btype, buildings_of_type) in enumerate(building_types.items()):
                                # Ajouter le label de district avec taille de police plus petite
                                district_label = QGraphicsTextItem(type_labels.get(btype, f"District {btype}"))
                                district_label.setDefaultTextColor(QColor(200, 200, 220))
                                district_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                                
                                # Calculer la position pour centrer le texte dans la carte
                                label_width = district_label.boundingRect().width()
                                # S'assurer que le texte ne dépasse pas les limites de la carte
                                x_pos = max(margin, min(width/2 - label_width/2, width - margin - label_width))
                                district_label.setPos(x_pos, zone_y - 25)
                                self.map_view.scene.addItem(district_label)
                                
                                # Ligne de séparation des districts
                                if zone_index > 0:
                                    line = QGraphicsLineItem(margin - 20, zone_y - 10, width - margin + 20, zone_y - 10)
                                    line.setPen(QPen(QColor(100, 100, 150, 150), 1, Qt.PenStyle.DashLine))
                                    self.map_view.scene.addItem(line)
                                
                                # Paramètres pour l'affichage des bâtiments dans cette zone
                                num_buildings = len(buildings_of_type)
                                max_per_row = 4  # Maximum 4 bâtiments par ligne
                                spacing = min(120, (width - 2 * margin) / max_per_row)
                                
                                # Ajouter les bâtiments de ce type
                                for i, (building_id, building) in enumerate(buildings_of_type):
                                    row = i // max_per_row
                                    col = i % max_per_row
                                    
                                    # Calculer les coordonnées avec un léger décalage aléatoire pour un effet plus naturel
                                    offset_x = random.uniform(-10, 10)
                                    offset_y = random.uniform(-5, 5)
                                    x = margin + (col + 0.5) * spacing + offset_x
                                    y = zone_y + 20 + row * 90 + offset_y
                                    
                                    # Créer l'objet MapLocation pour le bâtiment
                                    building_location = MapLocation(
                                        id=building_id,
                                        name=building.name,
                                        x=x,
                                        y=y,
                                        type=btype if hasattr(building, 'type') else "building",
                                        description=building.description if hasattr(building, 'description') else "",
                                        connections=[]
                                    )
                                    
                                    # Tous les bâtiments sont découverts dans la ville actuelle
                                    building_location.discovered = True
                                    
                                    # Ajouter le bâtiment à la carte avec une couleur spécifique au type
                                    self.map_view.add_location(building_location, 
                                                            override_color=building_colors.get(btype, building_colors["UNKNOWN"]))
                                    logger.info(f"Bâtiment ajouté à la carte : {building.name}")
                                
                                # Passer à la zone suivante
                                zone_y += min(zone_height, (row + 1) * 90 + 50)
                            
                            logger.info(f"Changement vers la carte de la ville {current_city.name}")
                        else:
                            logger.warning(f"Aucun bâtiment trouvé dans la ville {current_city.name}")
                    else:
                        logger.warning("Gestionnaire de ville non disponible")
                else:
                    logger.warning("Ville actuelle non trouvée")
            else:
                logger.warning("Impossible de charger la carte de la ville : aucune ville actuelle")
        
        # Réinitialiser la sélection
        self.selected_location_id = None
        self.selected_room_id = None
        
        # Réinitialiser les informations
        if hasattr(self, 'info_description'):
            self.info_description.setText("")
    
    def _update_ui_for_display_mode(self):
        """Met à jour l'interface utilisateur en fonction du mode d'affichage actuel"""
        logger.info(f"Mise à jour de l'interface pour le mode: {self.display_mode}")
        
        # Réinitialiser tous les boutons d'abord
        self.travel_btn.setVisible(False)
        self.explore_btn.setVisible(False)
        self.enter_building_btn.setVisible(False)
        self.enter_room_btn.setVisible(False)
        self.back_button.setVisible(False)
        
        # Configurer les boutons selon le mode d'affichage
        if self.display_mode == "world" or self.display_mode == "city":
            # Boutons pour le monde et la ville
            self.travel_btn.setVisible(True)
            self.travel_btn.setEnabled(False)  # Désactivé par défaut jusqu'à sélection
            self.explore_btn.setVisible(True)
            self.explore_btn.setEnabled(False)  # Désactivé par défaut jusqu'à sélection
        elif self.display_mode == "building":
            # Boutons pour le bâtiment
            self.enter_room_btn.setVisible(True)
            self.enter_room_btn.setEnabled(False)  # Désactivé par défaut jusqu'à sélection
            self.back_button.setVisible(True)
        
        # Mettre à jour le titre du panneau d'informations
        if hasattr(self, 'info_title'):
            if self.display_mode == "world":
                self.info_title.setText("Informations sur le lieu")
            elif self.display_mode == "city":
                if self.game and hasattr(self.game, 'world_manager') and self.game.world_manager.current_location_id:
                    current_city = self.game.world_manager.get_current_location()
                    if current_city:
                        self.info_title.setText(f"Ville: {current_city.name}")
                    else:
                        self.info_title.setText("Ville")
                else:
                    self.info_title.setText("Ville")
            elif self.display_mode == "building" and self.current_building:
                self.info_title.setText(f"Bâtiment: {self.current_building.name}")
            else:
                self.info_title.setText("Informations")
        
        # Réinitialiser la description si aucun élément n'est sélectionné
        if not self.selected_location_id and not self.selected_room_id:
            if hasattr(self, 'info_description'):
                self.info_description.setText("")
    
    def _on_filter_changed(self, index: int):
        """Gère le changement de filtre"""
        logger.info(f"Changement de filtre : {self.filter_selector.currentText()}")
        # Recharger la carte avec le nouveau filtre
        self._load_map_data()
    
    def _zoom_in(self):
        """Zoom avant sur la carte"""
        self.map_view.zoom_factor = min(self.map_view.max_zoom, self.map_view.zoom_factor * 1.2)
        self.map_view.setTransform(QTransform().scale(self.map_view.zoom_factor, self.map_view.zoom_factor))
    
    def _zoom_out(self):
        """Zoom arrière sur la carte"""
        self.map_view.zoom_factor = max(self.map_view.min_zoom, self.map_view.zoom_factor / 1.2)
        self.map_view.setTransform(QTransform().scale(self.map_view.zoom_factor, self.map_view.zoom_factor))
    
    def _reset_view(self):
        """Réinitialise la vue de la carte"""
        self.map_view.zoom_factor = 1.0
        self.map_view.setTransform(QTransform())
        
        # Centrage sur le lieu actuel
        if self.map_view.current_location_id:
            curr_loc = self.map_view.locations[self.map_view.current_location_id]
            self.map_view.centerOn(curr_loc["ellipse"])
    
    def _on_travel(self):
        """Gère le voyage vers un lieu"""
        # Récupérer le lieu sélectionné
        selected_location_id = None
        for loc_id, loc_data in self.map_view.locations.items():
            if loc_data["ellipse"].isSelected():
                selected_location_id = loc_id
                break
        
        if not selected_location_id:
            logger.warning("Aucun lieu sélectionné pour le voyage")
            return
        
        # Récupérer les informations des lieux de départ et d'arrivée
        current_location = self.game.world_manager.get_current_location()
        destination = self.map_view.locations[selected_location_id]["location"]
        
        if not current_location:
            logger.warning("Aucun lieu de départ disponible")
            return
        
        # Calculer le temps de voyage (simulé pour l'instant)
        # Dans une vraie implémentation, cela serait basé sur la distance, le mode de transport, etc.
        travel_distance = math.sqrt(
            (destination.x - self.map_view.locations[self.map_view.current_location_id]["location"].x) ** 2 +
            (destination.y - self.map_view.locations[self.map_view.current_location_id]["location"].y) ** 2
        )
        travel_time = max(1, int(travel_distance / 20))  # En secondes
        
        # Afficher la boîte de dialogue de voyage
        travel_dialog = TravelDialog(
            current_location.name,
            destination.name,
            travel_time,
            self
        )
        
        # Animation de la ligne de voyage
        self._animate_travel_path(self.map_view.current_location_id, selected_location_id)
        
        # Exécuter la boîte de dialogue
        travel_dialog.exec()
        
        # Effectuer le voyage
        if not self.game.world_manager.travel_to(selected_location_id):
            logger.warning(f"Impossible de voyager vers {selected_location_id}")
            return
        
        # Mettre à jour la carte
        self.map_view.set_current_location(selected_location_id)
        
        # Mettre à jour l'interface
        self.info_title.setText(destination.name)
        self.info_description.setText(destination.description)
        
        # Désactiver le bouton de voyage et activer le bouton d'exploration
        self.travel_btn.setEnabled(False)
        self.explore_btn.setEnabled(True)
        
        logger.info(f"Voyage vers {destination.name} effectué")
    
    def _animate_travel_path(self, from_id: str, to_id: str):
        """Anime le chemin de voyage entre deux lieux"""
        if from_id not in self.map_view.locations or to_id not in self.map_view.locations:
            return
            
        # Récupérer les coordonnées des lieux
        from_loc = self.map_view.locations[from_id]["location"]
        to_loc = self.map_view.locations[to_id]["location"]
        
        # Créer une ligne animée
        line = QGraphicsLineItem(from_loc.x, from_loc.y, from_loc.x, from_loc.y)  # Commence au point de départ
        line.setPen(QPen(QColor(255, 215, 0, 200), 3, Qt.PenStyle.SolidLine))  # Ligne dorée
        line.setZValue(2)  # Au-dessus des autres éléments
        
        # Ajouter la ligne à la scène
        self.map_view.scene.addItem(line)
        
        # Animation de la ligne
        def update_line(progress):
            # Calculer les nouvelles coordonnées de la ligne
            end_x = from_loc.x + (to_loc.x - from_loc.x) * progress / 100
            end_y = from_loc.y + (to_loc.y - from_loc.y) * progress / 100
            line.setLine(from_loc.x, from_loc.y, end_x, end_y)
            
            # Supprimer la ligne à la fin de l'animation
            if progress >= 100:
                self.map_view.scene.removeItem(line)
        
        # Créer un timer pour l'animation
        animation_timer = QTimer(self)
        progress = 0
        
        def animate():
            nonlocal progress
            progress += 2
            update_line(progress)
            if progress >= 100:
                animation_timer.stop()
        
        animation_timer.timeout.connect(animate)
        animation_timer.start(20)  # 50 FPS
    
    def _on_explore(self):
        """Gère l'exploration d'un lieu"""
        # Récupérer le lieu sélectionné
        selected_location_id = None
        for loc_id, loc_data in self.map_view.locations.items():
            if loc_data["ellipse"].isSelected():
                selected_location_id = loc_id
                break
        
        if not selected_location_id:
            # Si aucun lieu n'est sélectionné, explorer le lieu actuel
            selected_location_id = self.map_view.current_location_id
            
        if not selected_location_id:
            logger.warning("Aucun lieu à explorer")
            return
        
        # Récupérer les informations du lieu
        location = self.map_view.locations[selected_location_id]["location"]
        
        # Marquer le lieu comme visité
        location.visited = True
        self.map_view.locations[selected_location_id]["location"].visited = True
        
        # Mettre à jour l'apparence du lieu
        if not location.current:
            self.map_view.locations[selected_location_id]["ellipse"].setPen(QPen(self.map_view.visited_color, 2))
        
        # Découvrir les lieux connectés
        connected_locations = []
        if selected_location_id == self.map_view.current_location_id:
            # Récupérer les lieux connectés
            connected_locations = self.game.world_manager.get_available_destinations()
            
            # Marquer les lieux connectés comme découverts
            for conn_loc in connected_locations:
                if conn_loc.id in self.map_view.locations:
                    self.map_view.locations[conn_loc.id]["location"].discovered = True
                    
                    # Mettre à jour l'apparence du lieu
                    if not self.map_view.locations[conn_loc.id]["location"].visited:
                        self.map_view.locations[conn_loc.id]["ellipse"].setPen(QPen(self.map_view.discovered_color, 2))
        
        # Générer les résultats de l'exploration
        results = self._generate_exploration_results(location, connected_locations)
        
        # Afficher les résultats dans une boîte de dialogue
        dialog = ExplorationDialog(location.name, results, self)
        dialog.exec()
        
        logger.info(f"Exploration de {location.name} effectuée")
    
    def _generate_exploration_results(self, location: MapLocation, connected_locations: List[Any]) -> str:
        """Génère les résultats de l'exploration d'un lieu"""
        results = f"""
        <h2 style='color: #00aaff;'>Exploration de {location.name}</h2>
        <p>{location.description}</p>
        <hr style='border: 1px solid #3a3a5a;'>
        """
        
        # Informations sur le lieu
        results += "<h3 style='color: #00ffaa;'>Informations</h3>"
        
        # Type de lieu
        results += f"<p><b>Type:</b> {location.type.capitalize()}</p>"
        
        # Sécurité (simulée pour l'instant)
        security_level = sum(ord(c) for c in location.id) % 5 + 1
        security_color = "#00ff00" if security_level < 3 else "#ffff00" if security_level < 5 else "#ff0000"
        results += f"<p><b>Niveau de sécurité:</b> <span style='color: {security_color};'>{security_level}/5</span></p>"
        
        # Population (simulée pour l'instant)
        population = sum(ord(c) for c in location.name) * 1000 % 10000000
        results += f"<p><b>Population:</b> {population:,}</p>"
        
        # Lieux connectés
        if connected_locations:
            results += "<h3 style='color: #00ffaa;'>Lieux connectés</h3><ul>"
            for conn_loc in connected_locations:
                results += f"<li>{conn_loc.name} ({conn_loc.type if hasattr(conn_loc, 'type') else 'lieu'})</li>"
            results += "</ul>"
        
        # Points d'intérêt (simulés pour l'instant)
        results += "<h3 style='color: #00ffaa;'>Points d'intérêt</h3><ul>"
        poi_count = (sum(ord(c) for c in location.id) % 5) + 1
        poi_types = ["Café", "Magasin", "Terminal", "Marché noir", "Centre commercial", "Clinique", "Bar"]
        
        for i in range(poi_count):
            poi_index = (sum(ord(c) for c in location.id) + i) % len(poi_types)
            poi_name = f"{location.name.split()[0]}-{poi_types[poi_index]}"
            results += f"<li>{poi_name}</li>"
        results += "</ul>"
        
        return results
    
    def _update_ui(self):
        """Met à jour l'interface utilisateur"""
        # Mettre à jour les boutons d'action en fonction du lieu sélectionné
        selected_location_id = None
        for loc_id, loc_data in self.map_view.locations.items():
            if loc_data["ellipse"].isSelected():
                selected_location_id = loc_id
                break
        
        if selected_location_id:
            location = self.map_view.locations[selected_location_id]["location"]
            
            # Activer/désactiver le bouton de voyage
            can_travel = (
                location.discovered and 
                not location.current and 
                self.map_view.current_location_id and
                selected_location_id in self.game.world_manager.get_current_location().connections
            )
            self.travel_btn.setEnabled(can_travel)
            
            # Activer/désactiver le bouton d'exploration
            self.explore_btn.setEnabled(location.discovered)

    def _on_enter_building(self):
        """Gère l'entrée dans un bâtiment"""
        logger.info(f"Tentative d'entrée dans le bâtiment : {self.current_building_id}")
        
        if not self.current_building_id or not self.current_building:
            logger.warning("Aucun bâtiment sélectionné pour entrer")
            return
        
        # Informer le CityManager de l'entrée dans le bâtiment
        if self.game and hasattr(self.game, 'city_manager'):
            self.game.city_manager.enter_building(self.current_building_id)
            logger.info(f"CityManager informé de l'entrée dans le bâtiment: {self.current_building_id}")
        
        # Mettre à jour l'interface utilisateur pour le mode bâtiment
        self.display_mode = "building"
        
        # S'assurer que la carte est complètement vide avant de charger la carte du bâtiment
        self.map_view.clear_map()
        
        self._update_ui_for_display_mode()
        
        # Charger la carte du bâtiment
        self._load_building_map()
        
        # Mise à jour des informations
        if hasattr(self, 'info_title'):
            self.info_title.setText(f"Bâtiment: {self.current_building.name}")
        
        # Informations détaillées sur le bâtiment
        building_type = getattr(self.current_building, 'type', "UNKNOWN")
        security_level = getattr(self.current_building, 'security_level', "?")
        num_floors = getattr(self.current_building, 'num_floors', 1)
        
        # Description avec détails du bâtiment en style HTML
        description = f"""
        <style>
            .building-info {{
                line-height: 1.4;
                margin-bottom: 8px;
            }}
            .label {{
                color: #00aaff;
                font-weight: bold;
            }}
            .security {{
                color: {'#ff5555' if security_level > 5 else '#ffaa55' if security_level > 3 else '#55ff55'};
            }}
        </style>
        <div class="building-info">
            <p><span class="label">Type:</span> {building_type}</p>
            <p><span class="label">Sécurité:</span> <span class="security">Niveau {security_level}</span></p>
            <p><span class="label">Étages:</span> {num_floors}</p>
            <p>{getattr(self.current_building, 'description', '')}</p>
        </div>
        """
        
        if hasattr(self, 'info_description'):
            self.info_description.setText(description)
        
        logger.info(f"Entrée réussie dans le bâtiment {self.current_building.name}")
    
    def _on_enter_room(self):
        """Gère l'entrée dans une pièce du bâtiment"""
        if not hasattr(self, 'selected_room_id') or not self.selected_room_id:
            return
        
        # Logique pour entrer dans une pièce
        room = self.current_building.rooms[self.selected_room_id]
        
        # Mettre à jour la position du joueur
        if self.game and hasattr(self.game, 'player'):
            self.game.player.current_room_id = self.selected_room_id
            self.game.player.current_room_name = room["name"]
            
            # Message de confirmation
            message = f"Vous êtes maintenant dans {room['name']}."
            if self.game and hasattr(self.game, 'terminal'):
                self.game.terminal.print_message(message)
            
            # Mettre à jour l'interface
            self._update_ui()
    
    def _load_building_map(self):
        """Charge la carte d'un bâtiment"""
        logger.info(f"Chargement de la carte du bâtiment {self.current_building_id}")
        
        # Effacer la carte actuelle
        self.map_view.clear_map()
        
        # Créer un fond pour la carte du bâtiment
        self._create_building_background()
        
        # Vérifier si le bâtiment a des pièces
        if not hasattr(self.current_building, 'rooms') or not self.current_building.rooms:
            logger.warning("Le bâtiment n'a pas de pièces définies")
            return
        
        # Organiser les pièces par étage
        rooms_by_floor = {}
        for room_id, room in self.current_building.rooms.items():
            floor = room.get('floor', 1)
            if floor not in rooms_by_floor:
                rooms_by_floor[floor] = []
            rooms_by_floor[floor].append((room_id, room))
        
        # Trier les étages (du plus haut au plus bas)
        sorted_floors = sorted(rooms_by_floor.keys(), reverse=True)
        
        # Définir les couleurs pour différents types de pièces
        room_colors = {
            "entrance": QColor(0, 255, 255, 200),    # Cyan pour entrée
            "corridor": QColor(150, 150, 150, 200),  # Gris pour couloir
            "office": QColor(0, 180, 255, 200),      # Bleu pour bureau
            "security": QColor(255, 50, 50, 200),    # Rouge pour sécurité
            "server": QColor(255, 150, 0, 200),      # Orange pour serveur
            "residential": QColor(0, 255, 150, 200), # Vert pour résidentiel
            "storage": QColor(150, 100, 200, 200),   # Violet pour stockage
            "meeting": QColor(255, 255, 100, 200),   # Jaune pour réunion
            "restricted": QColor(255, 0, 100, 200),  # Rose foncé pour zone restreinte
            "default": QColor(180, 180, 255, 200)    # Lavande par défaut
        }
        
        # Ajouter les étiquettes d'étage et les pièces
        width, height = 800, 600
        margin_x, margin_y = 80, 60
        
        # Hauteur disponible divisée entre les étages
        floor_section_height = (height - 2 * margin_y) / len(sorted_floors) if sorted_floors else height
        
        for i, floor in enumerate(sorted_floors):
            # Position Y de départ pour cet étage
            start_y = margin_y + i * floor_section_height
            
            # Ajouter l'étiquette d'étage
            floor_label = QGraphicsTextItem(f"Étage {floor}")
            floor_label.setDefaultTextColor(QColor(0, 200, 255))
            floor_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            floor_label.setPos(margin_x - 60, start_y + floor_section_height / 2 - 10)
            self.map_view.scene.addItem(floor_label)
            
            # Ligne de séparation des districts
            if i > 0:
                line = QGraphicsLineItem(margin_x - 70, start_y, width - margin_x + 70, start_y)
                line.setPen(QPen(QColor(100, 100, 150, 150), 1, Qt.PenStyle.DashLine))
                self.map_view.scene.addItem(line)
            
            # Nombre de pièces dans cet étage
            rooms_in_floor = rooms_by_floor[floor]
            num_rooms = len(rooms_in_floor)
            
            # Calculer la disposition des pièces (max 4 pièces par ligne)
            max_per_row = 4
            room_width = min(150, (width - 2 * margin_x) / max_per_row)
            room_height = min(60, (floor_section_height - 40) / ((num_rooms - 1) // max_per_row + 1))
            
            # Ajouter les pièces de cet étage
            for j, (room_id, room) in enumerate(rooms_in_floor):
                row = j // max_per_row
                col = j % max_per_row
                
                # Ajouter un léger décalage aléatoire pour un aspect moins rigide
                offset_x = random.uniform(-5, 5)
                offset_y = random.uniform(-3, 3)
                
                # Calculer les coordonnées
                x = margin_x + col * room_width + room_width / 2 + offset_x
                y = start_y + 20 + row * room_height + room_height / 2 + offset_y
                
                # Identifier le type de pièce pour la couleur
                room_type = room.get('type', 'default').lower()
                room_color = room_colors.get(room_type, room_colors['default'])
                
                # Créer l'objet MapLocation pour la pièce
                room_location = MapLocation(
                    id=room_id,
                    name=room.get('name', f"Pièce {room_id}"),
                    x=x,
                    y=y,
                    type=room_type,
                    description=room.get('description', ""),
                    connections=[]
                )
                
                # Toutes les pièces sont découvertes
                room_location.discovered = True
                
                # Ajouter la pièce à la carte
                self.map_view.add_location(room_location, override_color=room_color)
            
            # Ajouter des connexions entre les pièces
            for room_id, room in rooms_by_floor[floor]:
                if 'connections' in room:
                    for connected_room_id in room['connections']:
                        # Vérifier que la connexion est au même étage
                        if connected_room_id in self.current_building.rooms:
                            connected_room = self.current_building.rooms[connected_room_id]
                            if connected_room.get('floor', 1) == floor:
                                self.map_view.add_connection(room_id, connected_room_id)
        
        # Ajouter des connexions entre les étages (escaliers, ascenseurs)
        for room_id, room in self.current_building.rooms.items():
            if 'connections' in room:
                for connected_room_id in room['connections']:
                    if connected_room_id in self.current_building.rooms:
                        connected_room = self.current_building.rooms[connected_room_id]
                        if room.get('floor', 1) != connected_room.get('floor', 1):
                            # Connexion entre étages
                            self.map_view.add_connection(room_id, connected_room_id, secure=True)

    def _create_building_background(self):
        """Crée un fond pour la carte du bâtiment"""
        # Créer un fond pour le bâtiment avec un style cyberpunk
        pixmap = QPixmap(1000, 800)
        pixmap.fill(QColor(15, 15, 30))  # Fond très sombre
        
        # Obtenir un peintre pour dessiner
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner une grille technique pour effet blueprint cyberpunk
        pen = QPen(QColor(30, 50, 80, 120))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Grille principale
        grid_size = 40
        for x in range(0, pixmap.width(), grid_size):
            painter.setPen(QPen(QColor(30, 50, 80, 80), 1, Qt.PenStyle.DotLine))
            painter.drawLine(x, 0, x, pixmap.height())
        
        for y in range(0, pixmap.height(), grid_size):
            painter.setPen(QPen(QColor(30, 50, 80, 80), 1, Qt.PenStyle.DotLine))
            painter.drawLine(0, y, pixmap.width(), y)
        
        # Lignes principales plus visibles
        for x in range(0, pixmap.width(), grid_size * 5):
            painter.setPen(QPen(QColor(50, 100, 150, 120), 1, Qt.PenStyle.SolidLine))
            painter.drawLine(x, 0, x, pixmap.height())
        
        for y in range(0, pixmap.height(), grid_size * 5):
            painter.setPen(QPen(QColor(50, 100, 150, 120), 1, Qt.PenStyle.SolidLine))
            painter.drawLine(0, y, pixmap.width(), y)
        
        # Logo/Marqueurs du bâtiment
        building_type = getattr(self.current_building, 'type', "UNKNOWN")
        
        # Centre du dessin
        center_x, center_y = pixmap.width() / 2, pixmap.height() / 2
        
        # Dessiner un symbole central selon le type de bâtiment
        if building_type == "CORPORATE":
            # Cercle corporatif avec triangle interne
            painter.setPen(QPen(QColor(0, 150, 255, 60), 2))
            painter.setBrush(QBrush(QColor(0, 100, 200, 20)))
            painter.drawEllipse(QPointF(center_x, center_y), 150, 150)
            
            # Triangle interne
            points = []
            for i in range(3):
                angle = 2 * math.pi / 3 * i + math.pi/6  # Rotation pour esthétique
                px = center_x + 100 * math.cos(angle)
                py = center_y + 100 * math.sin(angle)
                points.append(QPointF(px, py))
            
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            painter.setPen(QPen(QColor(0, 180, 255, 40), 2))
            painter.setBrush(QBrush(QColor(0, 150, 255, 10)))
            painter.drawPath(path)
            
        elif building_type == "RESIDENTIAL":
            # Carré résidentiel
            painter.setPen(QPen(QColor(0, 200, 150, 60), 2))
            painter.setBrush(QBrush(QColor(0, 150, 100, 20)))
            painter.drawRect(int(center_x - 120), int(center_y - 120), 240, 240)
            
            # Croix centrale
            painter.setPen(QPen(QColor(0, 200, 150, 40), 2))
            painter.drawLine(int(center_x - 80), int(center_y), int(center_x + 80), int(center_y))
            painter.drawLine(int(center_x), int(center_y - 80), int(center_x), int(center_y + 80))
            
        elif building_type == "MEDICAL":
            # Cercle médical avec croix
            painter.setPen(QPen(QColor(60, 255, 130, 60), 2))
            painter.setBrush(QBrush(QColor(40, 200, 90, 20)))
            painter.drawEllipse(QPointF(center_x, center_y), 130, 130)
            
            # Croix médicale
            painter.setPen(QPen(QColor(60, 255, 130, 50), 6))
            painter.drawLine(int(center_x - 70), int(center_y), int(center_x + 70), int(center_y))
            painter.drawLine(int(center_x), int(center_y - 70), int(center_x), int(center_y + 70))
            
        elif building_type == "ENTERTAINMENT":
            # Hexagone pour divertissement
            hex_size = 130
            points = []
            for i in range(6):
                angle = 2 * math.pi / 6 * i
                px = center_x + hex_size * math.cos(angle)
                py = center_y + hex_size * math.sin(angle)
                points.append(QPointF(px, py))
            
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            
            painter.setPen(QPen(QColor(255, 60, 255, 60), 2))
            painter.setBrush(QBrush(QColor(200, 50, 200, 20)))
            painter.drawPath(path)
            
            # Étoile interne
            star_size = 80
            star_points = []
            for i in range(5):
                # Points externes
                angle_ext = 2 * math.pi / 5 * i + math.pi/2  # Rotation pour esthétique
                px_ext = center_x + star_size * math.cos(angle_ext)
                py_ext = center_y + star_size * math.sin(angle_ext)
                star_points.append(QPointF(px_ext, py_ext))
                
                # Points internes
                angle_int = 2 * math.pi / 5 * i + math.pi/5 - math.pi/2
                px_int = center_x + star_size * 0.4 * math.cos(angle_int)
                py_int = center_y + star_size * 0.4 * math.sin(angle_int)
                star_points.append(QPointF(px_int, py_int))
            
            star_path = QPainterPath()
            star_path.moveTo(star_points[0])
            for p in star_points[1:]:
                star_path.lineTo(p)
            star_path.closeSubpath()
            
            painter.setPen(QPen(QColor(255, 100, 255, 40), 2))
            painter.setBrush(QBrush(QColor(255, 100, 255, 10)))
            painter.drawPath(star_path)
            
        elif building_type == "GOVERNMENT":
            # Octogone gouvernemental
            octo_size = 130
            points = []
            for i in range(8):
                angle = 2 * math.pi / 8 * i
                px = center_x + octo_size * math.cos(angle)
                py = center_y + octo_size * math.sin(angle)
                points.append(QPointF(px, py))
            
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            
            painter.setPen(QPen(QColor(255, 60, 60, 60), 2))
            painter.setBrush(QBrush(QColor(200, 50, 50, 20)))
            painter.drawPath(path)
            
            # Cercle interne
            painter.setPen(QPen(QColor(255, 80, 80, 40), 2))
            painter.setBrush(QBrush(QColor(255, 80, 80, 10)))
            painter.drawEllipse(QPointF(center_x, center_y), 70, 70)
            
        elif building_type == "COMMERCIAL":
            # Diamond commercial
            painter.setPen(QPen(QColor(255, 180, 0, 60), 2))
            painter.setBrush(QBrush(QColor(200, 150, 0, 20)))
            
            diamond_size = 130
            points = []
            # 4 points du diamant
            points.append(QPointF(center_x, center_y - diamond_size))
            points.append(QPointF(center_x + diamond_size, center_y))
            points.append(QPointF(center_x, center_y + diamond_size))
            points.append(QPointF(center_x - diamond_size, center_y))
            
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            painter.drawPath(path)
            
            # Cercle interne
            painter.setPen(QPen(QColor(255, 200, 0, 40), 2))
            painter.setBrush(QBrush(QColor(255, 200, 0, 10)))
            painter.drawEllipse(QPointF(center_x, center_y), 70, 70)
        
        else:
            # Cercle générique avec croix interne
            painter.setPen(QPen(QColor(150, 150, 200, 60), 2))
            painter.setBrush(QBrush(QColor(120, 120, 160, 20)))
            painter.drawEllipse(QPointF(center_x, center_y), 130, 130)
            
            # Croix
            painter.setPen(QPen(QColor(150, 150, 200, 40), 2))
            painter.drawLine(int(center_x - 90), int(center_y - 90), int(center_x + 90), int(center_y + 90))
            painter.drawLine(int(center_x + 90), int(center_y - 90), int(center_x - 90), int(center_y + 90))
        
        painter.end()
        
        # Définir l'image de fond
        self.map_view.set_background(pixmap)

    def _create_cyberpunk_city_background(self):
        """Crée un fond de carte amélioré avec style cyberpunk pour la ville"""
        # Créer un fond pour la ville
        background = QPixmap(1000, 800)
        background.fill(QColor(20, 20, 35))  # Fond plus sombre
        
        # Obtenir un peintre pour dessiner
        painter = QPainter(background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner une grille hexagonale
        pen = QPen(QColor(40, 40, 70, 120))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Hexagones de grille pour effet cyberpunk
        hex_size = 50
        hex_width = hex_size * 2
        hex_height = hex_size * math.sqrt(3)
        
        for x in range(-hex_size, background.width() + hex_size, int(hex_width * 0.75)):
            for y in range(-hex_size, background.height() + hex_size, int(hex_height)):
                offset_y = 0 if (x // int(hex_width * 0.75)) % 2 == 0 else int(hex_height / 2)
                points = []
                for i in range(6):
                    angle = 2 * math.pi / 6 * i
                    px = x + hex_size * math.cos(angle)
                    py = y + offset_y + hex_size * math.sin(angle)
                    points.append(QPointF(px, py))
                
                path = QPainterPath()
                path.moveTo(points[0])
                for p in points[1:]:
                    path.lineTo(p)
                path.closeSubpath()
                painter.drawPath(path)
        
        # Cercles concentriques pour effet futuriste
        center_x, center_y = background.width() / 2, background.height() / 2
        for radius in range(100, 1000, 100):
            color = QColor(0, 100, 255, 15)  # Bleu très transparent
            painter.setPen(QPen(color, 1, Qt.PenStyle.DotLine))
            painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Lignes radiales
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            painter.setPen(QPen(QColor(0, 100, 255, 12), 1, Qt.PenStyle.DotLine))
            x1, y1 = center_x, center_y
            x2 = center_x + 1000 * math.cos(rad)
            y2 = center_y + 1000 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        painter.end()
        
        # Appliquer le fond à la vue de carte
        self.map_view.set_background(background)
