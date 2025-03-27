"""
Module pour le widget de carte dans YakTaa
Ce module contient la classe MapWidget qui permet d'afficher et d'interagir
avec une carte du monde du jeu.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Set, Any
import random

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QGraphicsView, QGraphicsScene,
                           QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem,
                           QGraphicsTextItem, QGraphicsRectItem, QMenu, QToolTip)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QCursor, QTransform

from yaktaa.world.locations import Location, WorldMap
from yaktaa.world.travel import TravelMethod, WeatherCondition

logger = logging.getLogger("YakTaa.UI.MapWidget")

class LocationItem(QGraphicsEllipseItem):
    """Élément graphique représentant un lieu sur la carte"""
    
    def __init__(self, location: Location, parent=None):
        """Initialise un élément de lieu"""
        # Taille basée sur l'importance du lieu (population)
        size = 10
        if location.population > 0:
            size = min(30, max(10, 10 + math.log10(location.population) * 3))
        
        super().__init__(-size/2, -size/2, size, size, parent)
        
        self.location = location
        self.is_current = False
        self.is_discovered = True
        self.is_visited = False
        self.is_selected = False
        self.is_highlighted = False
        
        # Couleur basée sur le niveau de sécurité
        self._update_appearance()
        
        # Texte du nom du lieu
        self.label = QGraphicsTextItem(location.name, self)
        self.label.setPos(size/2 + 5, -10)
        font = QFont("Arial", 8)
        self.label.setFont(font)
        
        # Rendre l'élément interactif
        self.setAcceptHoverEvents(True)
        
        logger.debug(f"Élément de lieu créé pour {location.name}")
    
    def _update_appearance(self):
        """Met à jour l'apparence de l'élément en fonction de son état"""
        # Couleur de base selon le niveau de sécurité
        security_level = self.location.security_level
        
        # Palette de couleurs du plus sécurisé (bleu) au moins sécurisé (rouge)
        colors = [
            QColor(255, 0, 0),      # 1: Rouge vif (très dangereux)
            QColor(255, 60, 0),     # 2
            QColor(255, 120, 0),    # 3
            QColor(255, 180, 0),    # 4
            QColor(255, 240, 0),    # 5: Jaune (neutre)
            QColor(200, 255, 0),    # 6
            QColor(120, 255, 0),    # 7
            QColor(60, 255, 60),    # 8
            QColor(0, 200, 120),    # 9
            QColor(0, 120, 255)     # 10: Bleu (très sécurisé)
        ]
        
        base_color = colors[min(10, max(1, security_level)) - 1]
        
        # Modifier la couleur en fonction de l'état
        if self.is_current:
            # Lieu actuel: contour plus épais et plus lumineux
            pen = QPen(QColor(255, 255, 255), 2)
            brush = QBrush(base_color.lighter(150))
        elif self.is_selected:
            # Lieu sélectionné: contour jaune
            pen = QPen(QColor(255, 255, 0), 2)
            brush = QBrush(base_color)
        elif self.is_highlighted:
            # Lieu survolé: légèrement plus lumineux
            pen = QPen(Qt.PenStyle.SolidLine)
            brush = QBrush(base_color.lighter(130))
        elif not self.is_discovered:
            # Lieu non découvert: grisé
            pen = QPen(Qt.PenStyle.DotLine)
            brush = QBrush(QColor(100, 100, 100, 100))
        elif not self.is_visited:
            # Lieu découvert mais non visité: normal
            pen = QPen(Qt.PenStyle.SolidLine)
            brush = QBrush(base_color)
        else:
            # Lieu visité: normal
            pen = QPen(Qt.PenStyle.SolidLine)
            brush = QBrush(base_color)
        
        self.setPen(pen)
        self.setBrush(brush)
        
        # Ajuster la visibilité du label
        self.label.setVisible(self.is_discovered or self.is_current)
    
    def set_current(self, is_current: bool):
        """Définit si ce lieu est le lieu actuel du joueur"""
        self.is_current = is_current
        self._update_appearance()
    
    def set_discovered(self, is_discovered: bool):
        """Définit si ce lieu a été découvert par le joueur"""
        self.is_discovered = is_discovered
        self._update_appearance()
    
    def set_visited(self, is_visited: bool):
        """Définit si ce lieu a été visité par le joueur"""
        self.is_visited = is_visited
        self._update_appearance()
    
    def set_selected(self, is_selected: bool):
        """Définit si ce lieu est sélectionné"""
        self.is_selected = is_selected
        self._update_appearance()
    
    def hoverEnterEvent(self, event):
        """Gère l'événement d'entrée du curseur"""
        self.is_highlighted = True
        self._update_appearance()
        
        # Afficher une infobulle avec des informations sur le lieu
        tooltip_text = (
            f"<b>{self.location.name}</b><br>"
            f"Sécurité: {self.location.security_level}/10<br>"
            f"Population: {self.location.population:,}<br>"
            f"Services: {', '.join(self.location.services)}"
        )
        QToolTip.showText(event.screenPos(), tooltip_text)
        
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère l'événement de sortie du curseur"""
        self.is_highlighted = False
        self._update_appearance()
        super().hoverLeaveEvent(event)


class ConnectionItem(QGraphicsLineItem):
    """Élément graphique représentant une connexion entre deux lieux"""
    
    def __init__(self, source_pos: QPointF, dest_pos: QPointF, 
                 travel_method: TravelMethod, parent=None):
        """Initialise un élément de connexion"""
        super().__init__(source_pos.x(), source_pos.y(), dest_pos.x(), dest_pos.y(), parent)
        
        self.source_pos = source_pos
        self.dest_pos = dest_pos
        self.travel_method = travel_method
        self.is_highlighted = False
        self.is_active = True
        self.is_hidden = False
        self.requires_hacking = False
        self.requires_special_access = False
        
        # Style de ligne selon la méthode de transport
        self._update_appearance()
        
        logger.debug(f"Élément de connexion créé pour méthode {travel_method.name}")
    
    def _update_appearance(self):
        """Met à jour l'apparence de la connexion en fonction de son état"""
        pen = QPen()
        
        # Couleur et style selon la méthode de transport
        if self.travel_method == TravelMethod.WALK:
            pen.setColor(QColor(150, 150, 150))
            pen.setWidth(1)
        elif self.travel_method == TravelMethod.SUBWAY:
            pen.setColor(QColor(0, 150, 255))
            pen.setWidth(2)
        elif self.travel_method == TravelMethod.BUS:
            pen.setColor(QColor(0, 200, 0))
            pen.setWidth(2)
        elif self.travel_method == TravelMethod.TRAIN:
            pen.setColor(QColor(200, 0, 200))
            pen.setWidth(3)
        elif self.travel_method == TravelMethod.CAR:
            pen.setColor(QColor(200, 100, 0))
            pen.setWidth(2)
        elif self.travel_method == TravelMethod.PLANE:
            pen.setColor(QColor(0, 100, 200))
            pen.setWidth(3)
            pen.setStyle(Qt.PenStyle.DashLine)
        elif self.travel_method == TravelMethod.HYPERLOOP:
            pen.setColor(QColor(255, 50, 50))
            pen.setWidth(3)
            pen.setDashPattern([5, 2])
        elif self.travel_method == TravelMethod.TELEPORT:
            pen.setColor(QColor(0, 255, 255))
            pen.setWidth(2)
            pen.setDashPattern([2, 2])
        elif self.travel_method == TravelMethod.BOAT:
            pen.setColor(QColor(0, 0, 255))
            pen.setWidth(2)
            pen.setDashPattern([8, 2])
        elif self.travel_method == TravelMethod.DRONE:
            pen.setColor(QColor(255, 255, 0))
            pen.setWidth(1)
            pen.setDashPattern([1, 1])
        else:
            pen.setColor(QColor(100, 100, 100))
            pen.setWidth(1)
        
        # Modifier selon l'état
        if not self.is_active:
            pen.setColor(QColor(100, 100, 100, 100))
        elif self.is_highlighted:
            pen.setColor(pen.color().lighter(150))
            pen.setWidth(pen.width() + 1)
        
        if self.is_hidden:
            pen.setStyle(Qt.PenStyle.DotLine)
            pen.setColor(QColor(pen.color().red(), pen.color().green(), pen.color().blue(), 50))
        
        if self.requires_hacking:
            # Ajouter un motif spécial pour les connexions nécessitant du hacking
            pen.setDashPattern([1, 1])
        
        if self.requires_special_access:
            # Ajouter un motif spécial pour les connexions nécessitant un accès spécial
            pen.setDashPattern([5, 1, 1, 1])
        
        self.setPen(pen)
    
    def set_highlighted(self, is_highlighted: bool):
        """Définit si cette connexion est mise en évidence"""
        self.is_highlighted = is_highlighted
        self._update_appearance()
    
    def set_active(self, is_active: bool):
        """Définit si cette connexion est active"""
        self.is_active = is_active
        self._update_appearance()
    
    def set_hidden(self, is_hidden: bool):
        """Définit si cette connexion est cachée"""
        self.is_hidden = is_hidden
        self._update_appearance()
    
    def set_requires_hacking(self, requires_hacking: bool):
        """Définit si cette connexion nécessite du hacking"""
        self.requires_hacking = requires_hacking
        self._update_appearance()
    
    def set_requires_special_access(self, requires_special_access: bool):
        """Définit si cette connexion nécessite un accès spécial"""
        self.requires_special_access = requires_special_access
        self._update_appearance()


class MapWidget(QGraphicsView):
    """Widget d'affichage de la carte du monde"""
    
    # Signaux
    location_clicked = pyqtSignal(str)  # ID du lieu cliqué
    location_double_clicked = pyqtSignal(str)  # ID du lieu double-cliqué
    location_context_menu = pyqtSignal(str, QPoint)  # ID du lieu + position du clic
    
    def __init__(self, parent=None):
        """Initialise le widget de carte"""
        super().__init__(parent)
        
        # Créer la scène
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Configurer la vue
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumSize(400, 300)
        
        # Données de la carte
        self.world_map = None
        self.location_items: Dict[str, LocationItem] = {}
        self.connection_items: List[ConnectionItem] = []
        self.current_location_id = None
        self.visited_locations: Set[str] = set()
        self.discovered_locations: Set[str] = set()
        self.selected_location_id = None
        
        # Facteur de zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Animation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_active = False
        self.animation_step = 0
        self.animation_max_steps = 20
        self.animation_source_id = None
        self.animation_dest_id = None
        
        logger.info("Widget de carte initialisé")
    
    def set_world_map(self, world_map: WorldMap):
        """Définit la carte du monde à afficher"""
        self.world_map = world_map
        self._build_map()
        logger.info(f"Carte du monde définie avec {len(world_map.locations)} lieux")
    
    def set_current_location(self, location_id: str):
        """Définit le lieu actuel du joueur"""
        if location_id == self.current_location_id:
            return
        
        # Mettre à jour l'ancien lieu actuel
        if self.current_location_id in self.location_items:
            self.location_items[self.current_location_id].set_current(False)
        
        # Définir le nouveau lieu actuel
        self.current_location_id = location_id
        if location_id in self.location_items:
            self.location_items[location_id].set_current(True)
            self.location_items[location_id].set_visited(True)
            self.visited_locations.add(location_id)
            
            # Centrer la vue sur le lieu actuel
            self.center_on_location(location_id)
        
        logger.info(f"Lieu actuel défini: {location_id}")
    
    def set_visited_locations(self, location_ids: Set[str]):
        """Définit les lieux visités par le joueur"""
        self.visited_locations = set(location_ids)
        
        # Mettre à jour tous les éléments de lieu
        for location_id, item in self.location_items.items():
            item.set_visited(location_id in self.visited_locations)
        
        logger.info(f"Lieux visités définis: {len(self.visited_locations)} lieux")
    
    def set_discovered_locations(self, location_ids: Set[str]):
        """Définit les lieux découverts par le joueur"""
        self.discovered_locations = set(location_ids)
        
        # Mettre à jour tous les éléments de lieu
        for location_id, item in self.location_items.items():
            item.set_discovered(location_id in self.discovered_locations)
        
        logger.info(f"Lieux découverts définis: {len(self.discovered_locations)} lieux")
    
    def select_location(self, location_id: str):
        """Sélectionne un lieu sur la carte"""
        # Désélectionner l'ancien lieu
        if self.selected_location_id in self.location_items:
            self.location_items[self.selected_location_id].set_selected(False)
        
        # Sélectionner le nouveau lieu
        self.selected_location_id = location_id
        if location_id in self.location_items:
            self.location_items[location_id].set_selected(True)
        
        logger.info(f"Lieu sélectionné: {location_id}")
    
    def center_on_location(self, location_id: str):
        """Centre la vue sur un lieu spécifique"""
        if location_id not in self.location_items:
            return
        
        item = self.location_items[location_id]
        self.centerOn(item.pos())
        logger.debug(f"Vue centrée sur {location_id}")
    
    def animate_travel(self, source_id: str, dest_id: str):
        """Anime un déplacement entre deux lieux"""
        if source_id not in self.location_items or dest_id not in self.location_items:
            return False
        
        # Arrêter toute animation en cours
        if self.animation_active:
            self.animation_timer.stop()
        
        # Configurer la nouvelle animation
        self.animation_source_id = source_id
        self.animation_dest_id = dest_id
        self.animation_step = 0
        self.animation_active = True
        
        # Démarrer l'animation
        self.animation_timer.start(50)  # 50ms par étape
        
        logger.info(f"Animation de déplacement démarrée: {source_id} -> {dest_id}")
        return True
    
    def _update_animation(self):
        """Met à jour l'animation de déplacement"""
        if not self.animation_active:
            return
        
        self.animation_step += 1
        
        # Animation terminée
        if self.animation_step >= self.animation_max_steps:
            self.animation_timer.stop()
            self.animation_active = False
            
            # Mettre à jour le lieu actuel à la fin de l'animation
            self.set_current_location(self.animation_dest_id)
            
            logger.debug("Animation de déplacement terminée")
            return
        
        # Mettre à jour l'animation
        self.scene.update()
    
    def _build_map(self):
        """Construit la carte à partir des données du monde"""
        if not self.world_map:
            return
        
        # Effacer la scène
        self.scene.clear()
        self.location_items.clear()
        self.connection_items.clear()
        
        # Récupérer l'ID du monde actuel
        current_world_id = getattr(self.world_map, 'world_id', None)
        logger.debug(f"Construction de la carte pour le monde ID: {current_world_id}")
        
        # Dictionnaires pour stocker les villes principales et leurs coordonnées
        main_cities = {}  # {city_name: location}
        city_coords = {}  # {city_name: (x, y)}
        
        # Première passe: identifier les villes principales et leurs coordonnées
        for location_id, location in self.world_map.locations.items():
            # Vérifier si le lieu appartient au monde actuel
            location_world_id = getattr(location, 'world_id', None)
            if location_world_id is not None and current_world_id is not None and location_world_id != current_world_id:
                continue
            
            # Extraire le nom de base de la ville (avant le tiret s'il y en a un)
            location_name = getattr(location, 'name', '')
            base_city_name = location_name.split(' - ')[0].strip() if ' - ' in location_name else location_name
            
            # Vérifier si c'est une ville principale
            location_type = getattr(location, 'type', '').lower()
            if location_type in ('city', 'ville'):
                # C'est une ville explicitement marquée comme telle
                if base_city_name not in main_cities:
                    main_cities[base_city_name] = location
                    city_coords[base_city_name] = location.coordinates
            elif ' - ' not in location_name:
                # C'est peut-être une ville principale (pas de tiret dans le nom)
                if base_city_name not in main_cities:
                    main_cities[base_city_name] = location
                    city_coords[base_city_name] = location.coordinates
        
        # Si aucune ville principale n'a été trouvée, essayer avec une approche différente
        if not main_cities:
            # Regrouper les lieux par nom de base
            city_groups = {}
            for location_id, location in self.world_map.locations.items():
                location_name = getattr(location, 'name', '')
                base_city_name = location_name.split(' - ')[0].strip() if ' - ' in location_name else location_name
                
                if base_city_name not in city_groups:
                    city_groups[base_city_name] = []
                city_groups[base_city_name].append(location)
            
            # Prendre le premier lieu de chaque groupe comme ville principale
            for city_name, locations in city_groups.items():
                main_cities[city_name] = locations[0]
                city_coords[city_name] = locations[0].coordinates
        
        # Si toujours aucune ville, sortir
        if not main_cities:
            logger.warning("Aucune ville trouvée dans le monde actuel pour la carte")
            return
        
        # Calculer les limites de la carte
        coords = list(city_coords.values())
        min_x = min(x for x, y in coords)
        min_y = min(y for x, y in coords)
        max_x = max(x for x, y in coords)
        max_y = max(y for x, y in coords)
        
        # Ajouter une marge
        margin = 0.1
        width = max_x - min_x
        height = max_y - min_y
        min_x -= width * margin
        min_y -= height * margin
        max_x += width * margin
        max_y += height * margin
        
        # Définir les limites de la scène
        self.scene.setSceneRect(QRectF(min_x, min_y, max_x - min_x, max_y - min_y))
        
        # Créer un dictionnaire pour stocker les éléments de lieu
        city_items = {}
        
        # Ajouter les éléments de ville principale à la scène
        for city_name, location in main_cities.items():
            # Créer une copie de l'objet location pour ne pas modifier l'original
            city_location = type('Location', (), {})()
            for attr_name in dir(location):
                if not attr_name.startswith('__'):
                    setattr(city_location, attr_name, getattr(location, attr_name))
            
            # Définir le nom simplifié
            city_location.name = city_name
            
            # Créer l'élément graphique
            x, y = city_coords[city_name]
            item = LocationItem(city_location)
            item.setPos(x, y)
            self.scene.addItem(item)
            
            # Stocker l'élément avec son ID original
            self.location_items[location.id] = item
            city_items[city_name] = item
            
            # Configurer l'état initial
            item.set_current(location.id == self.current_location_id)
            item.set_visited(location.id in self.visited_locations)
            item.set_discovered(location.id in self.discovered_locations)
        
        # Créer les connexions entre villes principales
        added_connections = set()  # Pour éviter les doublons
        
        # Pour chaque ville, trouver les connexions vers d'autres villes principales
        for city1_name, location1 in main_cities.items():
            # Trouver toutes les villes connectées (directement ou via quartiers)
            connected_cities = set()
            
            # Fonction récursive pour explorer les connexions
            def explore_connections(loc_id, depth=0, max_depth=2):
                if depth > max_depth:
                    return
                
                loc = self.world_map.get_location(loc_id)
                if not loc or not hasattr(loc, 'connections'):
                    return
                
                for conn_id in loc.connections:
                    conn_loc = self.world_map.get_location(conn_id)
                    if not conn_loc:
                        continue
                    
                    # Extraire le nom de base
                    conn_name = getattr(conn_loc, 'name', '')
                    conn_base_name = conn_name.split(' - ')[0].strip() if ' - ' in conn_name else conn_name
                    
                    # Si c'est une ville principale différente, l'ajouter
                    if conn_base_name in main_cities and conn_base_name != city1_name:
                        connected_cities.add(conn_base_name)
                    else:
                        # Sinon, explorer récursivement
                        explore_connections(conn_id, depth + 1, max_depth)
            
            # Explorer les connexions à partir de cette ville
            explore_connections(location1.id)
            
            # Ajouter les connexions visuelles
            for city2_name in connected_cities:
                # Éviter les doublons
                connection_key = tuple(sorted([city1_name, city2_name]))
                if connection_key in added_connections:
                    continue
                
                added_connections.add(connection_key)
                
                # Créer l'élément de connexion
                source_pos = QPointF(*city_coords[city1_name])
                dest_pos = QPointF(*city_coords[city2_name])
                
                # Utiliser FAST_TRAVEL pour les connexions entre villes
                connection_item = ConnectionItem(source_pos, dest_pos, TravelMethod.FAST_TRAVEL)
                self.scene.addItem(connection_item)
                self.connection_items.append(connection_item)
        
        # Ajuster la vue pour afficher toute la carte
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom_factor = 1.0
        
        logger.info(f"Carte construite avec {len(city_items)} villes principales et {len(self.connection_items)} connexions")
    
    def wheelEvent(self, event):
        """Gère l'événement de la molette de la souris pour le zoom"""
        # Facteur de zoom
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Calculer le nouveau facteur de zoom
        if event.angleDelta().y() > 0:
            # Zoom in
            zoom_factor = zoom_in_factor
        else:
            # Zoom out
            zoom_factor = zoom_out_factor
        
        # Appliquer les limites de zoom
        new_zoom = self.zoom_factor * zoom_factor
        if new_zoom < self.min_zoom:
            zoom_factor = self.min_zoom / self.zoom_factor
        elif new_zoom > self.max_zoom:
            zoom_factor = self.max_zoom / self.zoom_factor
        
        # Mettre à jour le facteur de zoom
        self.zoom_factor *= zoom_factor
        
        # Appliquer le zoom
        self.scale(zoom_factor, zoom_factor)
        
        # Ne pas propager l'événement
        event.accept()
    
    def mousePressEvent(self, event):
        """Gère l'événement de clic de souris"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Vérifier si un lieu a été cliqué
            item = self.itemAt(event.pos())
            if isinstance(item, LocationItem):
                self.select_location(item.location.id)
                self.location_clicked.emit(item.location.id)
            elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), LocationItem):
                # Clic sur le label d'un lieu
                location_item = item.parentItem()
                self.select_location(location_item.location.id)
                self.location_clicked.emit(location_item.location.id)
        
        # Propager l'événement pour le déplacement de la vue
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Gère l'événement de double-clic de souris"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Vérifier si un lieu a été double-cliqué
            item = self.itemAt(event.pos())
            if isinstance(item, LocationItem):
                self.location_double_clicked.emit(item.location.id)
            elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), LocationItem):
                # Double-clic sur le label d'un lieu
                location_item = item.parentItem()
                self.location_double_clicked.emit(location_item.location.id)
        
        # Ne pas propager l'événement
        event.accept()
    
    def contextMenuEvent(self, event):
        """Gère l'événement de menu contextuel"""
        # Vérifier si un lieu a été cliqué
        item = self.itemAt(event.pos())
        if isinstance(item, LocationItem):
            self.location_context_menu.emit(item.location.id, event.globalPos())
        elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), LocationItem):
            # Clic droit sur le label d'un lieu
            location_item = item.parentItem()
            self.location_context_menu.emit(location_item.location.id, event.globalPos())
        else:
            # Menu contextuel général
            super().contextMenuEvent(event)
