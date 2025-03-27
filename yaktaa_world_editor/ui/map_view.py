#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la vue de carte pour visualiser les lieux et connexions
"""

import math
import logging
import json
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsRectItem, QMenu, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, 
    QContextMenuEvent, QTransform, QRadialGradient, QLinearGradient
)

logger = logging.getLogger(__name__)

class LocationItem(QGraphicsEllipseItem):
    """Item graphique représentant un lieu sur la carte"""
    
    def __init__(self, location_id, name, x, y, location_type, security_level):
        # Taille ajustée pour une meilleure visibilité
        size = 50
        super().__init__(0, 0, size, size)
        
        self.location_id = location_id
        self.name = name
        self.location_type = location_type
        self.security_level = security_level
        
        # Définir la position
        self.setPos(x - size/2, y - size/2)  # Centrer l'ellipse sur les coordonnées
        
        # Définir l'apparence en fonction du type et du niveau de sécurité
        self.set_appearance()
        
        # Permettre la sélection et le déplacement
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        # Ajouter le texte du nom avec un fond pour améliorer la lisibilité
        self.text_item = QGraphicsTextItem(self)
        
        # Utiliser une police plus lisible et légèrement plus grande
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.text_item.setFont(font)
        self.text_item.setPlainText(name)
        
        # Créer un rectangle de fond pour le texte
        text_rect = self.text_item.boundingRect()
        self.text_bg = QGraphicsRectItem(text_rect, self)
        self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))  # Fond blanc semi-transparent
        self.text_bg.setPen(QPen(Qt.PenStyle.NoPen))  # Pas de bordure
        
        # Positionner le texte sous le cercle
        text_width = text_rect.width()
        self.text_item.setPos(-text_width/2 + size/2, size + 5)
        self.text_bg.setPos(-text_width/2 + size/2, size + 5)
        
        # S'assurer que le texte est au-dessus du fond
        self.text_bg.setZValue(-1)
        self.text_item.setZValue(1)
        
        # Accepter les événements de survol
        self.setAcceptHoverEvents(True)
    
    def set_appearance(self):
        """Définit l'apparence de l'item en fonction de ses propriétés"""
        
        # Couleur en fonction du type de lieu avec des teintes cyberpunk
        color_map = {
            "city": QColor(0, 150, 255),       # Bleu
            "district": QColor(0, 220, 255),   # Bleu clair
            "special": QColor(255, 128, 0),    # Orange
            "rural": QColor(0, 200, 0),        # Vert
            "industrial": QColor(150, 150, 150), # Gris
            "government": QColor(255, 50, 50),   # Rouge
            "corporate": QColor(180, 0, 180)   # Violet
        }
        
        color = color_map.get(self.location_type, QColor(0, 0, 0))
        
        # Ajuster la luminosité en fonction du niveau de sécurité (1-5)
        # Plus le niveau est élevé, plus la couleur est foncée
        factor = max(0.5, 1.0 - (self.security_level - 1) * 0.1)
        color = QColor(
            min(255, int(color.red() * factor)),
            min(255, int(color.green() * factor)),
            min(255, int(color.blue() * factor))
        )
        
        # Définir le pinceau et le stylo avec un effet de brillance
        gradient = QRadialGradient(25, 25, 25)
        gradient.setColorAt(0, QColor(color.red() + 40, color.green() + 40, color.blue() + 40))
        gradient.setColorAt(1, color)
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
    
    def highlight(self, highlight=True):
        """Met en évidence l'item quand il est sélectionné"""
        
        if highlight:
            glow_pen = QPen(QColor(255, 255, 0, 200), 3)
            self.setPen(glow_pen)
            # Ajouter un effet de surbrillance au texte
            self.text_item.setDefaultTextColor(QColor(0, 0, 200))
        else:
            self.setPen(QPen(Qt.GlobalColor.black, 2))
            # Restaurer la couleur du texte
            self.text_item.setDefaultTextColor(QColor(0, 0, 0))
    
    def hoverEnterEvent(self, event):
        """Gère l'événement d'entrée du survol"""
        
        # Agrandir légèrement l'item et modifier l'opacité du fond du texte
        self.setScale(1.1)
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 230)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère l'événement de sortie du survol"""
        
        # Restaurer la taille normale et l'opacité du fond du texte
        self.setScale(1.0)
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))
        super().hoverLeaveEvent(event)

class ConnectionItem(QGraphicsLineItem):
    """Item graphique représentant une connexion entre deux lieux"""
    
    def __init__(self, connection_id, source_item, target_item, travel_type):
        # Créer la ligne entre les centres des deux items
        # Utiliser la taille mise à jour des LocationItem (50)
        source_center = source_item.pos() + QPointF(25, 25)
        target_center = target_item.pos() + QPointF(25, 25)
        super().__init__(source_center.x(), source_center.y(), 
                         target_center.x(), target_center.y())
        
        self.connection_id = connection_id
        self.source_item = source_item
        self.target_item = target_item
        self.travel_type = travel_type
        
        # Définir l'apparence en fonction du type de voyage
        self.set_appearance()
        
        # Ajouter le texte du type de voyage avec un fond pour améliorer la lisibilité
        self.text_item = QGraphicsTextItem(self)
        
        # Utiliser une police plus lisible
        font = QFont("Arial", 8)
        self.text_item.setFont(font)
        self.text_item.setPlainText(travel_type)
        
        # Créer un rectangle de fond pour le texte
        text_rect = self.text_item.boundingRect()
        self.text_bg = QGraphicsRectItem(text_rect, self)
        self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))  # Fond blanc semi-transparent
        self.text_bg.setPen(QPen(Qt.PenStyle.NoPen))  # Pas de bordure
        
        # Positionner le texte au milieu de la ligne
        line = self.line()
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2
        
        # Décaler légèrement le texte pour éviter qu'il soit exactement sur la ligne
        offset_y = -15
        
        self.text_item.setPos(mid_x - self.text_item.boundingRect().width() / 2,
                             mid_y - self.text_item.boundingRect().height() / 2 + offset_y)
        self.text_bg.setPos(mid_x - self.text_item.boundingRect().width() / 2,
                           mid_y - self.text_item.boundingRect().height() / 2 + offset_y)
        
        # S'assurer que le texte est au-dessus du fond
        self.text_bg.setZValue(-1)
        self.text_item.setZValue(1)
        
        # Accepter les événements de survol
        self.setAcceptHoverEvents(True)
    
    def set_appearance(self):
        """Définit l'apparence de l'item en fonction de ses propriétés"""
        
        # Couleur et style en fonction du type de voyage - style cyberpunk
        style_map = {
            "standard": (QColor(80, 80, 80), Qt.PenStyle.SolidLine, 2),      # Gris foncé, continu
            "fast": (QColor(255, 50, 50), Qt.PenStyle.SolidLine, 3),        # Rouge vif, continu, épais
            "hidden": (QColor(0, 180, 0), Qt.PenStyle.DashLine, 2),       # Vert vif, pointillé
            "secure": (QColor(0, 100, 255), Qt.PenStyle.DashDotLine, 2),    # Bleu électrique, mixte
            "expensive": (QColor(180, 0, 180), Qt.PenStyle.SolidLine, 2)  # Violet néon, continu
        }
        
        color, style, width = style_map.get(self.travel_type, 
                                           (QColor(80, 80, 80), Qt.PenStyle.SolidLine, 1))
        
        # Définir le stylo avec un effet de lueur pour un style cyberpunk
        pen = QPen(color, width, style)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.setPen(pen)
    
    def update_position(self):
        """Met à jour la position de la ligne en fonction des positions des lieux"""
        
        # Utiliser la taille mise à jour des LocationItem (50)
        source_center = self.source_item.pos() + QPointF(25, 25)
        target_center = self.target_item.pos() + QPointF(25, 25)
        
        self.setLine(source_center.x(), source_center.y(), 
                    target_center.x(), target_center.y())
        
        # Mettre à jour la position du texte
        line = self.line()
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2
        
        # Décaler légèrement le texte pour éviter qu'il soit exactement sur la ligne
        offset_y = -15
        
        self.text_item.setPos(mid_x - self.text_item.boundingRect().width() / 2,
                             mid_y - self.text_item.boundingRect().height() / 2 + offset_y)
        if hasattr(self, 'text_bg'):
            self.text_bg.setPos(mid_x - self.text_item.boundingRect().width() / 2,
                               mid_y - self.text_item.boundingRect().height() / 2 + offset_y)
        
        # S'assurer que le texte est au-dessus du fond
        self.text_bg.setZValue(-1)
        self.text_item.setZValue(1)
        
        # Accepter les événements de survol
        self.setAcceptHoverEvents(True)
    
    def hoverEnterEvent(self, event):
        """Gère l'événement d'entrée du survol"""
        
        # Mettre en évidence la connexion
        current_pen = self.pen()
        highlight_pen = QPen(current_pen)
        highlight_pen.setWidth(current_pen.width() + 1)
        highlight_pen.setColor(QColor(255, 255, 0))  # Jaune pour la surbrillance
        self.setPen(highlight_pen)
        
        # Rendre le texte plus visible
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 230)))
        
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère l'événement de sortie du survol"""
        
        # Restaurer l'apparence normale
        self.set_appearance()
        
        # Restaurer l'opacité du fond du texte
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))
        
        super().hoverLeaveEvent(event)

class BuildingItem(QGraphicsRectItem):
    """Item graphique représentant un bâtiment sur la carte"""
    
    def __init__(self, building_id, name, x, y, building_type, security_level, is_restricted=False):
        # Taille variable selon le type de bâtiment
        width = 40
        height = 40
        super().__init__(0, 0, width, height)
        
        self.building_id = building_id
        self.name = name
        self.building_type = building_type
        self.security_level = security_level
        self.is_restricted = is_restricted
        
        # Définir la position
        self.setPos(x - width/2, y - height/2)  # Centrer le rectangle sur les coordonnées
        
        # Définir l'apparence en fonction du type et du niveau de sécurité
        self.set_appearance()
        
        # Permettre la sélection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Ajouter le texte du nom avec un fond pour améliorer la lisibilité
        self.text_item = QGraphicsTextItem(self)
        
        # Utiliser une police plus lisible
        font = QFont("Arial", 8, QFont.Weight.Bold)
        self.text_item.setFont(font)
        self.text_item.setPlainText(name)
        
        # Créer un rectangle de fond pour le texte
        text_rect = self.text_item.boundingRect()
        self.text_bg = QGraphicsRectItem(text_rect, self)
        self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))  # Fond blanc semi-transparent
        self.text_bg.setPen(QPen(Qt.PenStyle.NoPen))  # Pas de bordure
        
        # Positionner le texte sous le rectangle
        text_width = text_rect.width()
        self.text_item.setPos(-text_width/2 + width/2, height + 5)
        self.text_bg.setPos(-text_width/2 + width/2, height + 5)
        
        # S'assurer que le texte est au-dessus du fond
        self.text_bg.setZValue(-1)
        self.text_item.setZValue(1)
        
        # Accepter les événements de survol
        self.setAcceptHoverEvents(True)
    
    def set_appearance(self):
        """Définit l'apparence de l'item en fonction de ses propriétés"""
        
        # Couleur en fonction du type de bâtiment avec des teintes cyberpunk
        color_map = {
            "residential": QColor(0, 180, 255),    # Bleu clair
            "commercial": QColor(255, 180, 0),     # Orange
            "industrial": QColor(150, 150, 150),   # Gris
            "government": QColor(255, 50, 50),     # Rouge
            "corporate": QColor(180, 0, 180),      # Violet
            "entertainment": QColor(0, 255, 180),  # Turquoise
            "security": QColor(255, 0, 0),         # Rouge vif
            "medical": QColor(0, 255, 0),          # Vert
            "education": QColor(255, 255, 0),      # Jaune
            "transport": QColor(0, 100, 255)       # Bleu
        }
        
        color = color_map.get(self.building_type, QColor(100, 100, 100))
        
        # Ajuster la luminosité en fonction du niveau de sécurité (1-5)
        # Plus le niveau est élevé, plus la couleur est foncée
        factor = max(0.5, 1.0 - (self.security_level - 1) * 0.1)
        color = QColor(
            min(255, int(color.red() * factor)),
            min(255, int(color.green() * factor)),
            min(255, int(color.blue() * factor))
        )
        
        # Définir le pinceau et le stylo avec un effet de brillance
        gradient = QLinearGradient(0, 0, 40, 40)
        gradient.setColorAt(0, QColor(color.red() + 40, color.green() + 40, color.blue() + 40))
        gradient.setColorAt(1, color)
        
        self.setBrush(QBrush(gradient))
        
        # Bordure spéciale pour les bâtiments à accès restreint
        if self.is_restricted:
            self.setPen(QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine))
        else:
            self.setPen(QPen(Qt.GlobalColor.black, 1))
    
    def highlight(self, highlight=True):
        """Met en évidence l'item quand il est sélectionné"""
        
        if highlight:
            glow_pen = QPen(QColor(255, 255, 0, 200), 2)
            self.setPen(glow_pen)
            # Ajouter un effet de surbrillance au texte
            self.text_item.setDefaultTextColor(QColor(0, 0, 200))
        else:
            # Restaurer l'apparence normale
            if self.is_restricted:
                self.setPen(QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine))
            else:
                self.setPen(QPen(Qt.GlobalColor.black, 1))
            # Restaurer la couleur du texte
            self.text_item.setDefaultTextColor(QColor(0, 0, 0))
    
    def hoverEnterEvent(self, event):
        """Gère l'événement d'entrée du survol"""
        
        # Agrandir légèrement l'item et modifier l'opacité du fond du texte
        self.setScale(1.1)
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 230)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère l'événement de sortie du survol"""
        
        # Restaurer la taille normale et l'opacité du fond du texte
        self.setScale(1.0)
        if hasattr(self, 'text_bg'):
            self.text_bg.setBrush(QBrush(QColor(255, 255, 255, 180)))
        super().hoverLeaveEvent(event)

class MapView(QWidget):
    """Widget de vue de carte pour visualiser les lieux et connexions"""
    
    # Signaux
    location_clicked = pyqtSignal(int)  # ID du lieu cliqué
    
    def __init__(self, db, world_id=None):
        super().__init__()
        
        self.db = db
        self.world_id = world_id
        self.location_items = {}  # Dictionnaire des items de lieu par ID
        self.connection_items = {}  # Dictionnaire des items de connexion par ID
        self.building_items = {}  # Dictionnaire des items de bâtiment par ID
        self.highlighted_location_id = None
        self.current_location_id = None  # ID du lieu actuellement sélectionné en mode détaillé
        self.view_mode = "global"  # Mode de visualisation: "global" ou "detailed"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Créer la disposition principale
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer la scène et la vue
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Ajouter la vue à la disposition
        layout.addWidget(self.view)
        
        # Créer la barre d'outils
        toolbar_layout = QHBoxLayout()
        
        # Ajouter le bouton de retour (initialement caché)
        self.back_button = QPushButton("Retour à la carte mondiale")
        self.back_button.clicked.connect(self.return_to_global_view)
        self.back_button.setVisible(False)
        toolbar_layout.addWidget(self.back_button)
        
        # Ajouter le label d'information
        self.info_label = QLabel("")
        toolbar_layout.addWidget(self.info_label)
        toolbar_layout.addStretch()
        
        # Ajouter le contrôle de zoom
        zoom_label = QLabel("Zoom:")
        toolbar_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        toolbar_layout.addWidget(self.zoom_slider)
        
        # Ajouter la barre d'outils à la disposition principale
        layout.addLayout(toolbar_layout)
        
        # Définir la disposition
        self.setLayout(layout)
        
        # Charger les données si un ID de monde est fourni
        if self.world_id:
            self.load_map_data()
    
    def load_map_data(self):
        """Charge les données de la carte à partir de la base de données"""
        
        if not self.world_id:
            return
        
        # Effacer la scène
        self.scene.clear()
        self.location_items.clear()
        self.connection_items.clear()
        self.building_items.clear()
        
        # Charger les lieux
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT id, name, coordinates, location_type, security_level
        FROM locations
        WHERE world_id = ?
        """, (self.world_id,))
        
        locations = cursor.fetchall()
        
        # Calculer l'échelle et l'offset pour un meilleur affichage
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        
        # Extraire les coordonnées et trouver les limites
        location_coords = []
        for location in locations:
            coordinates = json.loads(location["coordinates"])
            x_coord = coordinates[0]  # Latitude
            y_coord = coordinates[1]  # Longitude
            location_coords.append((location, x_coord, y_coord))
            
            min_x = min(min_x, x_coord)
            max_x = max(max_x, x_coord)
            min_y = min(min_y, y_coord)
            max_y = max(max_y, y_coord)
        
        # Calculer l'échelle pour un bon affichage
        width = max(800, max_x - min_x)
        height = max(600, max_y - min_y)
        
        # Ajouter une marge
        margin = 50
        scale_x = (width + 2 * margin) / (max_x - min_x) if max_x > min_x else 1
        scale_y = (height + 2 * margin) / (max_y - min_y) if max_y > min_y else 1
        
        # Utiliser une structure pour suivre les positions occupées
        occupied_positions = {}
        min_distance = 60  # Distance minimale entre les centres des lieux
        
        # Créer les items de lieu avec des positions ajustées
        for location, orig_x, orig_y in location_coords:
            # Normaliser les coordonnées
            x_coord = (orig_x - min_x) * scale_x + margin
            y_coord = (orig_y - min_y) * scale_y + margin
            
            # Trouver une position non superposée
            x_coord, y_coord = self.find_non_overlapping_position(
                x_coord, y_coord, occupied_positions, min_distance
            )
            
            # Marquer cette position comme occupée
            occupied_positions[(x_coord, y_coord)] = True
            
            item = LocationItem(
                location["id"],
                location["name"],
                x_coord,
                y_coord,
                location["location_type"],
                location["security_level"]
            )
            self.scene.addItem(item)
            self.location_items[location["id"]] = item
            
            # Connecter l'événement de clic
            item.mouseReleaseEvent = lambda event, item=item: self.on_location_clicked(event, item)
        
        # Charger les bâtiments
        cursor.execute("""
        SELECT id, name, building_type, security_level, location_id, 
               is_restricted, is_abandoned
        FROM buildings
        WHERE world_id = ?
        """, (self.world_id,))
        
        buildings = cursor.fetchall()
        
        # Créer les items de bâtiment (initialement cachés)
        for building in buildings:
            try:
                location_id = building["location_id"]
                
                # Vérifier que le lieu parent existe
                if location_id not in self.location_items:
                    continue
                    
                # Obtenir la position du lieu parent
                parent_item = self.location_items[location_id]
                parent_pos = parent_item.pos()
                parent_center_x = parent_pos.x() + parent_item.rect().width() / 2
                parent_center_y = parent_pos.y() + parent_item.rect().height() / 2
                
                # Positionner le bâtiment autour du lieu parent en spirale
                # pour éviter les superpositions
                angle = (hash(building["id"]) % 360) * (math.pi / 180)  # Angle aléatoire basé sur l'ID
                distance = 80 + (hash(building["id"]) % 100)  # Distance variable basée sur l'ID
                
                x_coord = parent_center_x + distance * math.cos(angle)
                y_coord = parent_center_y + distance * math.sin(angle)
                
                # Déterminer si le bâtiment est à accès restreint
                is_restricted = False
                try:
                    # Vérifier si le bâtiment est à accès restreint
                    is_restricted = building["is_restricted"] == 1
                except (KeyError, IndexError):
                    # Sinon, vérifier si le bâtiment est abandonné
                    try:
                        # Un bâtiment abandonné peut aussi être considéré comme restreint
                        is_restricted = building["is_abandoned"] == 1
                    except (KeyError, IndexError):
                        # Par défaut, non restreint
                        is_restricted = False
                
                item = BuildingItem(
                    building["id"],
                    building["name"],
                    x_coord,
                    y_coord,
                    building["building_type"],
                    building["security_level"],
                    is_restricted
                )
                
                # Stocker l'ID du lieu parent
                item.location_id = location_id
                
                # Cacher initialement les bâtiments
                item.setVisible(False)
                
                self.scene.addItem(item)
                self.building_items[building["id"]] = item
            except Exception as e:
                logger.error(f"Erreur lors du chargement du bâtiment {building['id']}: {str(e)}")
                continue
        
        # Charger les connexions
        cursor.execute("""
        SELECT id, source_id, destination_id, travel_type
        FROM connections
        WHERE world_id = ?
        """, (self.world_id,))
        
        connections = cursor.fetchall()
        
        # Créer les items de connexion
        for connection in connections:
            source_id = connection["source_id"]
            destination_id = connection["destination_id"]
            
            # Vérifier que les lieux source et destination existent
            if source_id in self.location_items and destination_id in self.location_items:
                source_item = self.location_items[source_id]
                destination_item = self.location_items[destination_id]
                
                item = ConnectionItem(
                    connection["id"],
                    source_item,
                    destination_item,
                    connection["travel_type"]
                )
                self.scene.addItem(item)
                self.connection_items[connection["id"]] = item
        
        # Ajuster la vue
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.view.centerOn(0, 0)
    
    def find_non_overlapping_position(self, x, y, occupied_positions, min_distance):
        """Trouve une position non superposée pour un lieu"""
        
        # Si la position n'est pas occupée, la retourner directement
        if not self.is_position_occupied(x, y, occupied_positions, min_distance):
            return x, y
        
        # Sinon, chercher en spirale une position libre
        for distance in range(5, 100, 5):  # Augmenter progressivement la distance
            for angle in range(0, 360, 30):  # Chercher dans différentes directions
                rad = math.radians(angle)
                new_x = x + distance * math.cos(rad)
                new_y = y + distance * math.sin(rad)
                
                if not self.is_position_occupied(new_x, new_y, occupied_positions, min_distance):
                    return new_x, new_y
        
        # Si aucune position n'est trouvée, retourner la position originale
        return x + 20, y + 20
    
    def is_position_occupied(self, x, y, occupied_positions, min_distance):
        """Vérifie si une position est déjà occupée"""
        
        for pos_x, pos_y in occupied_positions:
            distance = math.sqrt((x - pos_x) ** 2 + (y - pos_y) ** 2)
            if distance < min_distance:
                return True
        
        return False
    
    def refresh(self):
        """Rafraîchit la vue de la carte"""
        
        # Sauvegarder l'ID du lieu en surbrillance
        highlighted_id = self.highlighted_location_id
        
        # Recharger les données
        self.load_map_data()
        
        # Restaurer la surbrillance si nécessaire
        if highlighted_id and highlighted_id in self.location_items:
            self.highlight_location(highlighted_id)
    
    def highlight_location(self, location_id):
        """Met en évidence un lieu sur la carte"""
        
        # Désactiver la surbrillance précédente
        if self.highlighted_location_id and self.highlighted_location_id in self.location_items:
            self.location_items[self.highlighted_location_id].highlight(False)
        
        # Activer la nouvelle surbrillance
        if location_id in self.location_items:
            self.location_items[location_id].highlight(True)
            self.highlighted_location_id = location_id
            
            # Centrer la vue sur le lieu
            self.view.centerOn(self.location_items[location_id])
    
    def on_location_clicked(self, event, item):
        """Gère le clic sur un lieu"""
        
        # Gérer l'événement de base
        QGraphicsEllipseItem.mouseReleaseEvent(item, event)
        
        # Si on est en mode global, passer en mode détaillé
        if self.view_mode == "global":
            self.switch_to_detailed_view(item.location_id)
        
        # Émettre le signal avec l'ID du lieu
        self.location_clicked.emit(item.location_id)
    
    def switch_to_detailed_view(self, location_id):
        """Passe en mode de visualisation détaillée pour un lieu spécifique"""
        
        # Enregistrer l'ID du lieu actuel
        self.current_location_id = location_id
        
        # Changer le mode de visualisation
        self.view_mode = "detailed"
        
        # Mettre à jour le label d'information
        location_name = self.location_items[location_id].name
        self.info_label.setText(f"Bâtiments de {location_name}")
        
        # Afficher le bouton de retour
        self.back_button.setVisible(True)
        
        # Cacher tous les lieux et connexions
        for item in self.location_items.values():
            item.setVisible(False)
        
        for item in self.connection_items.values():
            item.setVisible(False)
        
        # Afficher uniquement le lieu sélectionné
        if location_id in self.location_items:
            self.location_items[location_id].setVisible(True)
            
            # Centrer la vue sur le lieu
            self.view.centerOn(self.location_items[location_id])
        
        # Afficher les bâtiments associés à ce lieu
        for building_id, building_item in self.building_items.items():
            if hasattr(building_item, 'location_id') and building_item.location_id == location_id:
                building_item.setVisible(True)
        
        # Ajuster la vue pour montrer tous les éléments visibles
        visible_items = [item for item in self.scene.items() if item.isVisible()]
        if visible_items:
            # Créer un rectangle englobant tous les éléments visibles
            rect = QRectF()
            for item in visible_items:
                rect = rect.united(item.sceneBoundingRect())
            
            # Ajouter une marge
            rect.adjust(-50, -50, 50, 50)
            
            # Ajuster la vue
            self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
    
    def return_to_global_view(self):
        """Revient à la vue globale de la carte"""
        
        # Changer le mode de visualisation
        self.view_mode = "global"
        
        # Réinitialiser le label d'information
        self.info_label.setText("")
        
        # Cacher le bouton de retour
        self.back_button.setVisible(False)
        
        # Afficher tous les lieux et connexions
        for item in self.location_items.values():
            item.setVisible(True)
        
        for item in self.connection_items.values():
            item.setVisible(True)
        
        # Cacher tous les bâtiments
        for item in self.building_items.values():
            item.setVisible(False)
        
        # Ajuster la vue pour montrer tous les lieux
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Restaurer la surbrillance si nécessaire
        if self.highlighted_location_id and self.highlighted_location_id in self.location_items:
            self.highlight_location(self.highlighted_location_id)
    
    def on_zoom_changed(self, value):
        """Gère le changement de zoom"""
        
        # Calculer le facteur de zoom
        factor = value / 100.0
        
        # Créer une transformation
        transform = QTransform()
        transform.scale(factor, factor)
        
        # Appliquer la transformation
        self.view.setTransform(transform)
