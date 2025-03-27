"""
Module pour le widget de carte du jeu YakTaa
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
import math
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QFrame, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QToolBar, QAction, QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor, QPainter, QFont, QIcon

from yaktaa.core.game import Game
from yaktaa.ui.widgets.npc_widget import NPCManager

logger = logging.getLogger("YakTaa.UI.MapView")

class Location:
    """Classe représentant un lieu sur la carte"""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 position: Tuple[float, float], 
                 type: str = "city", 
                 security_level: int = 1,
                 discovered: bool = False,
                 accessible: bool = False,
                 description: str = ""):
        """Initialise un lieu"""
        self.id = id
        self.name = name
        self.position = position
        self.type = type
        self.security_level = security_level
        self.discovered = discovered
        self.accessible = accessible
        self.description = description
        
        # Connexions à d'autres lieux
        self.connections = []


class BuildingNode(QGraphicsEllipseItem):
    """Classe représentant un bâtiment sur la carte"""
    
    def __init__(self, building_id: str, name: str, position: Tuple[float, float], 
                 building_type: str, security_level: int, is_restricted: bool = False, parent=None):
        """Initialise un nœud de bâtiment"""
        size = 15  # Taille plus petite que les villes
        super().__init__(-size/2, -size/2, size, size, parent)
        
        self.building_id = building_id
        self.name = name
        self.building_type = building_type
        self.security_level = security_level
        self.is_restricted = is_restricted
        
        self.setPos(position[0], position[1])
        
        # Apparence du nœud
        color = QColor("#00AAFF")  # Bleu par défaut
        
        if security_level >= 4:
            color = QColor("#FF0000")  # Rouge pour haute sécurité
        elif security_level >= 2:
            color = QColor("#FFAA00")  # Orange pour sécurité moyenne
            
        if is_restricted:
            # Contour rouge pour les bâtiments à accès restreint
            self.setPen(QPen(QColor("#FF0000"), 2, Qt.PenStyle.DashLine))
        else:
            self.setPen(QPen(Qt.PenStyle.SolidLine))
            
        self.setBrush(QBrush(color))
        
        # Forme spécifique selon le type
        if building_type == "corporate":
            # Forme carrée pour les bâtiments corporatifs
            self.setRect(-size/2, -size/2, size, size)
        elif building_type == "government":
            # Forme triangulaire pour les bâtiments gouvernementaux
            # Simulé avec un cercle pour l'instant
            pass
            
        # Étiquette du nœud
        self.label = QGraphicsTextItem(name, self)
        self.label.setPos(-self.label.boundingRect().width()/2, size/2 + 5)
        
        # Interactivité
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
    
    def hoverEnterEvent(self, event):
        """Gère l'entrée du curseur sur le nœud"""
        self.setPen(QPen(Qt.PenStyle.SolidLine, 2, Qt.PenStyle.SolidLine))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère la sortie du curseur du nœud"""
        if self.is_restricted:
            self.setPen(QPen(QColor("#FF0000"), 2, Qt.PenStyle.DashLine))
        else:
            self.setPen(QPen(Qt.PenStyle.SolidLine, 1, Qt.PenStyle.SolidLine))
        super().hoverLeaveEvent(event)


class MapNode(QGraphicsEllipseItem):
    """Classe représentant un nœud sur la carte"""
    
    def __init__(self, location: Location, parent=None):
        """Initialise un nœud de carte"""
        size = 20 if location.type == "city" else 10
        super().__init__(-size/2, -size/2, size, size, parent)
        
        self.location = location
        self.setPos(location.position[0], location.position[1])
        
        # Apparence du nœud
        color = QColor("#00FF00")  # Vert par défaut
        
        if location.type == "city":
            if location.security_level >= 4:
                color = QColor("#FF0000")  # Rouge pour haute sécurité
            elif location.security_level >= 2:
                color = QColor("#FFAA00")  # Orange pour sécurité moyenne
        elif location.type == "server":
            color = QColor("#00FFFF")  # Cyan pour les serveurs
        elif location.type == "hub":
            color = QColor("#FF00FF")  # Magenta pour les hubs
        
        # Style du nœud
        self.setPen(QPen(Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(color))
        
        # Étiquette du nœud
        self.label = QGraphicsTextItem(location.name, self)
        self.label.setPos(-self.label.boundingRect().width()/2, size/2 + 5)
        
        # Interactivité
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
    
    def hoverEnterEvent(self, event):
        """Gère l'entrée du curseur sur le nœud"""
        self.setPen(QPen(Qt.PenStyle.SolidLine, 2, Qt.PenStyle.SolidLine))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère la sortie du curseur du nœud"""
        self.setPen(QPen(Qt.PenStyle.SolidLine, 1, Qt.PenStyle.SolidLine))
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Gère le clic sur le nœud"""
        # Propager l'événement à la scène
        scene = self.scene()
        if scene:
            # Trouver le widget de carte parent
            view_items = scene.views()
            if view_items:
                view = view_items[0]
                if view and view.parent():
                    map_view = view.parent()
                    if hasattr(map_view, 'on_location_clicked'):
                        map_view.on_location_clicked(self.location.id)
        
        super().mousePressEvent(event)


class MapView(QWidget):
    """Widget de visualisation de carte pour YakTaa"""
    
    # Signal émis lorsqu'un lieu est sélectionné
    location_selected = pyqtSignal(str)
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise la vue de carte"""
        super().__init__(parent)
        
        self.game = game
        
        # Création de la scène et de la vue
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Lieux et nœuds
        self.locations = {}
        self.nodes = {}
        self.buildings = {}
        self.building_nodes = {}  # Pour stocker les nœuds de bâtiments par lieu
        
        # Lieu actuel
        self.current_location_id = None
        self.selected_location_id = None
        
        # Gestionnaire de PNJ
        self.npc_manager = NPCManager(game)
        
        # Interface utilisateur
        self._setup_ui()
        
        # Chargement des données
        self._load_map_data()
        
        # Timer pour les animations
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animations)
        self.animation_timer.start(50)  # 20 FPS
        
        logger.info("Widget de carte initialisé")
    
    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur de la carte"""
        # Mise en page
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Barre d'outils
        self._create_toolbar()
        
        # Vue graphique
        self.layout.addWidget(self.view)
        
        # Barre d'information
        self._create_info_bar()
    
    def _create_toolbar(self) -> None:
        """Crée la barre d'outils de la carte"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(Qt.QSize(16, 16))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #000000;
                border: none;
                border-bottom: 1px solid #333333;
                spacing: 2px;
                padding: 2px;
            }
            
            QToolButton {
                background-color: #333333;
                color: #00FF00;
                border: none;
                border-radius: 2px;
                padding: 2px;
            }
            
            QToolButton:hover {
                background-color: #444444;
            }
            
            QToolButton:pressed {
                background-color: #555555;
            }
            
            QComboBox {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 2px;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #00FF00;
                selection-background-color: #555555;
            }
        """)
        
        # Actions
        self.zoom_in_action = QAction("Zoom +", self.toolbar)
        self.zoom_in_action.triggered.connect(self._zoom_in)
        self.toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("Zoom -", self.toolbar)
        self.zoom_out_action.triggered.connect(self._zoom_out)
        self.toolbar.addAction(self.zoom_out_action)
        
        self.toolbar.addSeparator()
        
        self.reset_view_action = QAction("Réinitialiser", self.toolbar)
        self.reset_view_action.triggered.connect(self._reset_view)
        self.toolbar.addAction(self.reset_view_action)
        
        self.toolbar.addSeparator()
        
        # Sélecteur de type de carte
        self.map_type_label = QLabel("Type de carte:")
        self.toolbar.addWidget(self.map_type_label)
        
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItem("Réseau")
        self.map_type_combo.addItem("Géographique")
        self.map_type_combo.addItem("Sécurité")
        self.map_type_combo.currentIndexChanged.connect(self._change_map_type)
        self.toolbar.addWidget(self.map_type_combo)
        
        # Espacement
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Recherche
        self.search_button = QAction("Rechercher", self.toolbar)
        self.search_button.triggered.connect(self._search_location)
        self.toolbar.addAction(self.search_button)
        
        self.layout.addWidget(self.toolbar)
    
    def _create_info_bar(self) -> None:
        """Crée la barre d'information de la carte"""
        self.info_bar = QFrame()
        self.info_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.info_bar.setMaximumHeight(50)
        self.info_bar.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: none;
                border-top: 1px solid #333333;
            }
            
            QLabel {
                color: #00FF00;
            }
            
            QPushButton {
                background-color: #333333;
                color: #00FF00;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 5px;
            }
            
            QPushButton:hover {
                background-color: #444444;
            }
            
            QPushButton:pressed {
                background-color: #555555;
            }
            
            QPushButton:disabled {
                background-color: #222222;
                color: #555555;
            }
        """)
        
        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(5, 0, 5, 0)
        
        # Informations sur le lieu sélectionné
        self.location_name_label = QLabel("Aucun lieu sélectionné")
        info_layout.addWidget(self.location_name_label)
        
        # Espacement
        info_layout.addStretch()
        
        # Bouton de voyage
        self.travel_button = QPushButton("Voyager")
        self.travel_button.setEnabled(False)
        self.travel_button.clicked.connect(self._travel_to_selected)
        info_layout.addWidget(self.travel_button)
        
        self.layout.addWidget(self.info_bar)
    
    def _load_map_data(self) -> None:
        """Charge les données de la carte depuis le gestionnaire de monde"""
        # Vider la scène
        self.scene.clear()
        self.locations = {}
        self.nodes = {}
        self.buildings = {}
        self.building_nodes = {}
        
        # Vérifier que le jeu et le gestionnaire de monde sont disponibles
        if not self.game or not hasattr(self.game, 'world_manager'):
            logger.warning("Gestionnaire de monde non disponible, utilisation de données de test")
            self._load_test_map_data()
            return
        
        world_manager = self.game.world_manager
        
        # Récupérer les lieux du monde
        for location_id, location_data in world_manager.world_map.locations.items():
            # Convertir les coordonnées du monde en coordonnées de la scène
            # Les coordonnées sont normalisées entre -200 et 200 pour l'affichage
            x = location_data.coordinates[0] * 2  # Latitude
            y = location_data.coordinates[1] * 2  # Longitude
            
            # Déterminer le type de lieu
            location_type = "city"  # Type par défaut
            if hasattr(location_data, 'is_virtual') and location_data.is_virtual:
                location_type = "server"
            elif hasattr(location_data, 'is_special') and location_data.is_special:
                location_type = "hub"
            
            # Créer l'objet Location pour l'affichage
            location = Location(
                id=location_id,
                name=location_data.name,
                position=(x, y),
                type=location_type,
                security_level=location_data.security_level,
                discovered=location_id in world_manager.discovered_locations,
                accessible=location_id in world_manager.visited_locations,
                description=location_data.description
            )
            
            self.locations[location_id] = location
            
            # Création du nœud graphique
            node = MapNode(location)
            self.scene.addItem(node)
            self.nodes[location_id] = node
            
            # Connexion du signal de clic
            node.setAcceptHoverEvents(True)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Création des connexions entre les lieux
        for location_id, location_data in world_manager.world_map.locations.items():
            source = self.locations.get(location_id)
            if not source:
                continue
                
            for connection in world_manager.world_map.get_connections(location_id):
                target_id = connection.target_id
                if target_id not in self.locations:
                    continue
                
                target = self.locations[target_id]
                
                # Vérifier si la connexion existe déjà dans l'autre sens
                if target_id in source.connections:
                    continue
                
                # Ajout de la connexion aux lieux
                source.connections.append(target_id)
                target.connections.append(location_id)
                
                # Création de la ligne graphique
                source_pos = QPointF(source.position[0], source.position[1])
                target_pos = QPointF(target.position[0], target.position[1])
                
                line = QGraphicsLineItem(source_pos.x(), source_pos.y(), target_pos.x(), target_pos.y())
                
                # Style de la ligne en fonction du type de connexion
                pen_color = QColor("#333333")  # Couleur par défaut
                pen_width = 2
                pen_style = Qt.PenStyle.SolidLine
                
                if hasattr(connection, 'travel_type'):
                    if connection.travel_type == "fast":
                        pen_color = QColor("#00FF00")  # Vert pour les connexions rapides
                        pen_width = 3
                    elif connection.travel_type == "secure":
                        pen_color = QColor("#FF0000")  # Rouge pour les connexions sécurisées
                        pen_style = Qt.PenStyle.DashLine
                
                line.setPen(QPen(pen_color, pen_width, pen_style))
                self.scene.addItem(line)
        
        # Création des bâtiments
        for location_id, location_data in world_manager.world_map.locations.items():
            location = self.locations.get(location_id)
            if not location:
                continue
            
            for building_data in location_data.buildings:
                building_id = building_data.id
                building_name = building_data.name
                building_type = building_data.type
                security_level = building_data.security_level
                is_restricted = building_data.is_restricted
                
                # Positionner le bâtiment à côté de la ville
                building_x = location.position[0] + random.uniform(-20, 20)
                building_y = location.position[1] + random.uniform(-20, 20)
                
                building = BuildingNode(building_id, building_name, (building_x, building_y), building_type, security_level, is_restricted)
                self.scene.addItem(building)
                self.buildings[building_id] = building
                if location_id not in self.building_nodes:
                    self.building_nodes[location_id] = []
                self.building_nodes[location_id].append(building)
        
        # Définition du lieu actuel
        self.current_location_id = world_manager.current_location_id
        self._highlight_current_location()
        
        # Ajustement de la vue
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _load_test_map_data(self) -> None:
        """Charge des données de test pour la carte"""
        # Création de quelques lieux
        locations = [
            Location("home", "Base", (0, 0), "hub", 1, True, True, "Votre base d'opérations"),
            Location("server1", "Serveur Alpha", (100, -50), "server", 2, True, True, "Un serveur de données standard"),
            Location("server2", "Serveur Beta", (-100, -50), "server", 3, True, False, "Un serveur sécurisé"),
            Location("megacorp", "MegaCorp HQ", (0, -150), "city", 4, True, False, "Le siège social de MegaCorp"),
            Location("darknet", "DarkNet Hub", (150, 100), "hub", 1, True, True, "Un hub du darknet"),
            Location("govnet", "GovNet", (-150, 100), "hub", 5, False, False, "Réseau gouvernemental hautement sécurisé")
        ]
        
        # Ajout des lieux à la carte
        for location in locations:
            self.locations[location.id] = location
            
            # Création du nœud graphique
            node = MapNode(location)
            self.scene.addItem(node)
            self.nodes[location.id] = node
            
            # Connexion du signal de clic
            node.setAcceptHoverEvents(True)
            node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Création des connexions entre les lieux
        connections = [
            ("home", "server1"),
            ("home", "server2"),
            ("server1", "megacorp"),
            ("server2", "megacorp"),
            ("home", "darknet"),
            ("darknet", "govnet")
        ]
        
        for source_id, target_id in connections:
            source = self.locations[source_id]
            target = self.locations[target_id]
            
            # Ajout de la connexion aux lieux
            source.connections.append(target_id)
            target.connections.append(source_id)
            
            # Création de la ligne graphique
            source_pos = QPointF(source.position[0], source.position[1])
            target_pos = QPointF(target.position[0], target.position[1])
            
            line = QGraphicsLineItem(source_pos.x(), source_pos.y(), target_pos.x(), target_pos.y())
            line.setPen(QPen(QColor("#333333"), 2, Qt.PenStyle.SolidLine))
            
            self.scene.addItem(line)
        
        # Création des bâtiments
        buildings = [
            ("megacorp", "MegaCorp HQ", "corporate", 4, False),
            ("megacorp", "MegaCorp Lab", "corporate", 3, True),
            ("darknet", "DarkNet Market", "blackmarket", 1, False),
            ("govnet", "GovNet HQ", "government", 5, False)
        ]
        
        for location_id, building_name, building_type, security_level, is_restricted in buildings:
            location = self.locations.get(location_id)
            if not location:
                continue
            
            # Positionner le bâtiment à côté de la ville
            building_x = location.position[0] + random.uniform(-20, 20)
            building_y = location.position[1] + random.uniform(-20, 20)
            
            building = BuildingNode(f"{location_id}_{building_name}", building_name, (building_x, building_y), building_type, security_level, is_restricted)
            self.scene.addItem(building)
            self.buildings[f"{location_id}_{building_name}"] = building
            if location_id not in self.building_nodes:
                self.building_nodes[location_id] = []
            self.building_nodes[location_id].append(building)
        
        # Définition du lieu actuel
        self.current_location_id = "home"
        self._highlight_current_location()
        
        # Ajustement de la vue
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _zoom_in(self) -> None:
        """Zoom avant sur la carte"""
        self.view.scale(1.2, 1.2)
    
    def _zoom_out(self) -> None:
        """Zoom arrière sur la carte"""
        self.view.scale(1/1.2, 1/1.2)
    
    def _reset_view(self) -> None:
        """Réinitialise la vue de la carte"""
        self.view.resetTransform()
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def _highlight_current_location(self) -> None:
        """Met en évidence le lieu actuel"""
        # Réinitialisation de tous les nœuds
        for node_id, node in self.nodes.items():
            node.setPen(QPen(Qt.PenStyle.SolidLine, 1, Qt.PenStyle.SolidLine))
            node.setSelected(False)
        
        # Mise en évidence du lieu actuel
        if self.current_location_id in self.nodes:
            current_node = self.nodes[self.current_location_id]
            current_node.setPen(QPen(QColor("#FFFFFF"), 3, Qt.PenStyle.SolidLine))
            current_node.setSelected(True)
            
            # Mise à jour des informations
            location = self.locations[self.current_location_id]
            self.location_name_label.setText(f"{location.name} - {location.description}")
    
    def _change_map_type(self, index: int) -> None:
        """Change le type de carte affiché"""
        map_type = self.map_type_combo.currentText()
        
        # Mise à jour de l'apparence des nœuds en fonction du type de carte
        for node_id, node in self.nodes.items():
            location = self.locations[node_id]
            
            if map_type == "Réseau":
                # Coloration par type
                if location.type == "city":
                    node.setBrush(QBrush(QColor("#00FF00")))
                elif location.type == "server":
                    node.setBrush(QBrush(QColor("#00FFFF")))
                elif location.type == "hub":
                    node.setBrush(QBrush(QColor("#FF00FF")))
            
            elif map_type == "Géographique":
                # Coloration par accessibilité
                if location.accessible:
                    node.setBrush(QBrush(QColor("#00FF00")))
                elif location.discovered:
                    node.setBrush(QBrush(QColor("#FFFF00")))
                else:
                    node.setBrush(QBrush(QColor("#FF0000")))
            
            elif map_type == "Sécurité":
                # Coloration par niveau de sécurité
                if location.security_level >= 4:
                    node.setBrush(QBrush(QColor("#FF0000")))
                elif location.security_level >= 2:
                    node.setBrush(QBrush(QColor("#FFAA00")))
                else:
                    node.setBrush(QBrush(QColor("#00FF00")))
    
    def _search_location(self) -> None:
        """Recherche un lieu sur la carte"""
        # TODO: Implémenter une boîte de dialogue de recherche
        pass
    
    def _travel_to_selected(self) -> None:
        """Voyage vers le lieu sélectionné"""
        # TODO: Implémenter le voyage entre les lieux
        pass
    
    def _update_animations(self) -> None:
        """Met à jour les animations de la carte"""
        # TODO: Implémenter des animations pour la carte
        pass
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur de la carte"""
        # Mise à jour des animations, effets visuels, etc.
        pass
    
    def resizeEvent(self, event) -> None:
        """Gère le redimensionnement du widget"""
        super().resizeEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def set_current_location(self, location_id: str) -> None:
        """
        Définit le lieu actuel
        
        Args:
            location_id: Identifiant du lieu
        """
        if location_id not in self.locations:
            logger.error(f"Lieu introuvable: {location_id}")
            return
            
        # Définir le lieu actuel
        self.current_location_id = location_id
        
        # Mettre à jour l'interface
        self._highlight_current_location()
        
        # Charger les bâtiments du lieu
        if location_id in self.locations:
            self._load_buildings_for_location(location_id)
            
            # Charger les PNJ du lieu
            self.npc_manager.load_npcs_for_location(location_id)
            self.npc_manager.create_npc_nodes(self.scene)
        
        # Mettre à jour l'info-bulle
        self.info_label.setText(f"Lieu actuel: {self.locations[location_id].name}")
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Récupère un lieu par son identifiant"""
        return self.locations.get(location_id)
    
    def on_location_clicked(self, location_id: str) -> None:
        """Gère le clic sur un lieu"""
        # Afficher les bâtiments du lieu
        location = self.get_location(location_id)
        if location:
            print(f"Lieu sélectionné : {location.name}")
            
            # Afficher les bâtiments associés à la ville
            if location_id in self.building_nodes:
                for building in self.building_nodes[location_id]:
                    building_name, building_type, security_level, is_restricted = building.name, building.building_type, building.security_level, building.is_restricted
                    
                    # Afficher les informations du bâtiment
                    print(f"  - {building_name} ({building_type}) - Sécurité : {security_level}, Accès restreint : {is_restricted}")
            
            # Mettre à jour l'interface utilisateur
            self.selected_location_id = location_id
            self.location_name_label.setText(f"{location.name} - {location.description}")
            self.travel_button.setEnabled(True)
