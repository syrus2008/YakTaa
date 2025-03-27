#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de sélection de boutique simplifié pour YakTaa.
Permet de sélectionner facilement une boutique parmi celles disponibles.
"""

import logging
import os
import traceback
from typing import List, Optional, Dict, Tuple, Callable
import uuid

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QFrame, QSplitter, QScrollArea,
                            QGridLayout, QSpacerItem, QSizePolicy, QLineEdit, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

from yaktaa.ui.utils import load_stylesheet, get_font
from yaktaa.items.shop import Shop, ShopType

# Configuration du logging
logger = logging.getLogger(__name__)

# Obtenir le répertoire de base du jeu
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class ShopCard(QFrame):
    """
    Carte représentant une boutique dans le sélecteur.
    
    Signals:
        clicked: Émis lorsque la carte est cliquée
    """
    
    clicked = pyqtSignal(str)  # ID de la boutique
    
    def __init__(self, shop: Shop, parent=None):
        super().__init__(parent)
        
        self.shop = shop
        
        # Gérer le cas où shop_id n'existe pas
        if hasattr(shop, 'shop_id') and shop.shop_id:
            self.shop_id = shop.shop_id
        elif hasattr(shop, 'id') and shop.id:
            self.shop_id = shop.id
        else:
            # Générer un identifiant unique si aucun n'est disponible
            self.shop_id = f"shop_{str(uuid.uuid4())[:8]}"
        
        # Style de base
        self.setObjectName(f"shop_card_{self.shop_id}")
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Configuration de l'interface
        self.setup_ui()
    
    def setup_ui(self):
        """
        Configure l'interface de la carte.
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Icône de la boutique
        icon_frame = QFrame()
        icon_frame.setObjectName("shop_icon_frame")
        icon_frame.setFixedSize(QSize(80, 80))
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(5, 5, 5, 5)
        
        # Obtenir le type de boutique (peut être une chaîne ou un objet)
        shop_type_str = ""
        if hasattr(self.shop, 'shop_type'):
            if isinstance(self.shop.shop_type, str):
                shop_type_str = self.shop.shop_type.lower()
            elif hasattr(self.shop.shop_type, 'name'):
                shop_type_str = self.shop.shop_type.name.lower()
            else:
                shop_type_str = "unknown"
        else:
            shop_type_str = "unknown"
        
        icon_label = QLabel()
        try:
            # Essayer de charger l'icône spécifique au type de boutique
            # Utiliser un chemin absolu pour les icônes
            icon_path = os.path.join(BASE_DIR, f"assets/icons/shop_type/{shop_type_str}.png")
            pixmap = QPixmap(icon_path)
            
            # Si le fichier existe mais est vide, utiliser l'icône par défaut
            if pixmap.isNull():
                # Essayer un chemin alternatif
                alt_path = os.path.join(BASE_DIR, f"assets/icons/shop_type/{shop_type_str}.png")
                pixmap = QPixmap(alt_path)
                if pixmap.isNull():
                    raise FileNotFoundError(f"Icône non trouvée ou invalide: {icon_path} ou {alt_path}")
                
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            # En cas d'erreur, utiliser une icône par défaut ou un texte
            logger.warning(f"Impossible de charger l'icône pour {self.shop.name}: {str(e)}")
            # Texte comme fallback
            icon_label.setText(shop_type_str[0].upper() if shop_type_str else "?")
            icon_label.setStyleSheet("font-size: 32px; font-weight: bold;")
            
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_frame)
        
        # Informations de la boutique
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nom de la boutique
        name_label = QLabel(self.shop.name)
        name_label.setFont(get_font("heading", 14, bold=True))
        name_label.setObjectName("title")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(name_label)
        
        # Description courte
        description = self.shop.description
        if isinstance(description, dict):
            # Si la description est un dictionnaire, convertir en chaîne
            description = str(description)
        if len(description) > 80:
            description = description[:77] + "..."
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        # Informations supplémentaires
        details_layout = QHBoxLayout()
        
        # Type de boutique
        if isinstance(self.shop.shop_type, str):
            shop_type_display = self.shop.shop_type.capitalize()
        elif hasattr(self.shop.shop_type, 'name'):
            shop_type_display = self.shop.shop_type.name.capitalize()
        else:
            shop_type_display = "Inconnu"
            
        type_label = QLabel(f"Type: {shop_type_display}")
        details_layout.addWidget(type_label)
        
        # Nombre d'articles
        if hasattr(self.shop, 'inventory') and self.shop.inventory is not None:
            items_count = len(self.shop.inventory)
        else:
            items_count = 0
            
        items_label = QLabel(f"Articles: {items_count}")
        details_layout.addWidget(items_label)
        
        # Statut légal
        is_legal = getattr(self.shop, 'is_legal', True)
        legal_status = "Légal" if is_legal else "Marché noir"
        legal_color = "#00FF99" if is_legal else "#FF5555"
        legal_label = QLabel(legal_status)
        legal_label.setStyleSheet(f"color: {legal_color};")
        details_layout.addWidget(legal_label)
        
        info_layout.addLayout(details_layout)
        layout.addLayout(info_layout, 1)  # 1 = stretch factor
        
        # Bouton pour entrer
        enter_button = QPushButton()
        enter_button.setIcon(QIcon(os.path.join(BASE_DIR, "assets/icons/enter.png")))
        enter_button.setIconSize(QSize(24, 24))
        enter_button.setFixedSize(QSize(40, 40))
        enter_button.setToolTip("Entrer dans la boutique")
        enter_button.clicked.connect(lambda: self.clicked.emit(self.shop_id))
        layout.addWidget(enter_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    def mousePressEvent(self, event):
        """
        Gère l'événement de clic sur la carte.
        """
        super().mousePressEvent(event)
        self.clicked.emit(self.shop_id)

class SimpleShopSelector(QWidget):
    """
    Widget simplifié pour sélectionner une boutique parmi celles disponibles.
    
    Signals:
        shop_selected(str): Émis lorsqu'une boutique est sélectionnée, avec l'ID de la boutique
        back_pressed(): Émis lorsque le bouton retour est pressé
    """
    
    shop_selected = pyqtSignal(str)  # ID de la boutique sélectionnée
    back_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.shops = []  # Liste des boutiques disponibles
        self.selected_shop_id = None
        self.current_filter = "all"
        self.search_text = ""
        self.group_by_type = True
        
        # Définir l'objectName pour le sélecteur de style CSS
        self.setObjectName("shop_selector")
        
        # Configuration de l'interface utilisateur
        self.setup_ui()
        
    def setup_ui(self):
        """
        Configure l'interface utilisateur de base.
        """
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        
        # En-tête avec style cyberpunk
        header_frame = QFrame()
        header_frame.setObjectName("shop_selector_header")
        header_layout = QVBoxLayout(header_frame)
        
        # Titre
        title_label = QLabel("Boutiques disponibles")
        title_label.setFont(get_font("heading", 16, bold=True))
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel("Sélectionnez une boutique pour voir ses articles")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        self.main_layout.addWidget(header_frame)
        
        # Barre d'outils: recherche et filtres
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("shop_selector_toolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Recherche
        search_layout = QHBoxLayout()
        search_label = QLabel("Recherche:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une boutique...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        toolbar_layout.addLayout(search_layout)
        
        # Filtre par type
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrer par type:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tous les types", "all")
        self.filter_combo.addItem("Armes", ShopType.WEAPONS.name)
        self.filter_combo.addItem("Technologie", ShopType.TECH.name)
        self.filter_combo.addItem("Médicaments", ShopType.DRUGS.name)
        self.filter_combo.addItem("Nourriture", ShopType.FOOD.name)
        self.filter_combo.addItem("Vêtements", ShopType.CLOTHING.name)
        self.filter_combo.addItem("Implants", ShopType.IMPLANTS.name)
        self.filter_combo.addItem("Hacking", ShopType.HACKING.name)
        self.filter_combo.addItem("Services", ShopType.SERVICES.name)
        self.filter_combo.addItem("Marché noir", ShopType.BLACK_MARKET.name)
        self.filter_combo.addItem("Général", ShopType.GENERAL.name)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        # Utiliser addLayout au lieu de créer un nouveau QHBoxLayout
        toolbar_layout.addLayout(filter_layout)
        
        self.main_layout.addWidget(toolbar_frame)
        
        # Conteneur pour la liste des boutiques avec défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget contenant la liste des boutiques
        shop_list_container = QWidget()
        shop_list_container.setStyleSheet("background-color: transparent;")
        self.shop_list_layout = QVBoxLayout(shop_list_container)
        self.shop_list_layout.setContentsMargins(5, 5, 5, 5)
        self.shop_list_layout.setSpacing(12)
        self.shop_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Message par défaut si aucune boutique n'est disponible
        self.no_shops_label = QLabel("Aucune boutique disponible dans cette zone.")
        self.no_shops_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_shops_label.setStyleSheet("color: #FF6666; font-size: 14px; margin: 20px;")
        self.shop_list_layout.addWidget(self.no_shops_label)
        
        # Définir le widget de contenu pour la zone de défilement
        scroll_area.setWidget(shop_list_container)
        
        # Ajouter la zone de défilement au layout principal
        self.main_layout.addWidget(scroll_area, 1)  # 1 = prend tout l'espace disponible
        
        # Boutons en bas
        footer_frame = QFrame()
        footer_frame.setObjectName("shop_selector_footer")
        footer_layout = QHBoxLayout(footer_frame)
        
        # Bouton Retour
        back_button = QPushButton("Retour")
        back_button.setObjectName("back_button")
        back_button.clicked.connect(self.back_pressed.emit)
        footer_layout.addWidget(back_button)
        
        # Spacer pour pousser le bouton d'aide à droite
        footer_layout.addStretch()
        
        # Bouton d'aide
        help_button = QPushButton("Aide")
        help_button.setObjectName("help_button")
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        self.main_layout.addWidget(footer_frame)
        
        # Appliquer la feuille de style
        self.setStyleSheet(load_stylesheet("shop_selector"))
    
    def set_shops(self, shops: List[Shop]):
        """
        Définit la liste des boutiques à afficher.
        
        Args:
            shops: Liste d'objets Shop à afficher
        """
        logger.debug(f"[DEBUG] set_shops appelé avec {len(shops)} boutiques")
        try:
            self.shops = shops
            logger.debug(f"[DEBUG] Liste des boutiques stockée, appel à refresh_shops")
            self.refresh_shops()
            logger.debug(f"[DEBUG] refresh_shops terminé avec succès")
        except Exception as e:
            logger.error(f"[DEBUG] Erreur dans set_shops: {str(e)}")
            logger.error(f"[DEBUG] Détails: {traceback.format_exc()}")
    
    def refresh_shops(self):
        """
        Rafraîchit la liste des boutiques affichées.
        """
        logger.debug(f"[DEBUG] refresh_shops démarré ({len(self.shops)} boutiques)")
        
        try:
            # Nettoyer la liste actuelle
            self._clear_shop_list()
            
            # Si aucune boutique, afficher le message approprié
            if not self.shops:
                self._show_no_shops_message()
                logger.debug("[DEBUG] refresh_shops terminé avec succès")
                return
            
            # Organiser les boutiques par type si activé
            if self.group_by_type:
                # Créer un dictionnaire des boutiques par type
                shops_by_type = {}
                
                for shop in self.filtered_shops:
                    # Gérer le cas où shop_type est un string ou un objet ShopType
                    if hasattr(shop.shop_type, 'name'):
                        # C'est un objet ShopType
                        shop_type = shop.shop_type.name
                    else:
                        # C'est une chaîne de caractères
                        shop_type = str(shop.shop_type).upper()
                    
                    if shop_type not in shops_by_type:
                        shops_by_type[shop_type] = []
                    shops_by_type[shop_type].append(shop)
                
                # Afficher les boutiques par type
                for shop_type, shops in shops_by_type.items():
                    # Créer un en-tête pour ce type
                    self._create_type_header(shop_type, len(shops))
                    
                    # Ajouter les boutiques de ce type
                    for i, shop in enumerate(shops, 1):
                        logger.debug(f"[DEBUG] Création de la carte pour la boutique {i}/{len(shops)}: {shop.name}")
                        try:
                            shop_card = ShopCard(shop)
                            shop_card.clicked.connect(self._select_shop)
                            self.shop_list_layout.addWidget(shop_card)
                            logger.debug(f"[DEBUG] Carte pour la boutique {shop.name} ajoutée avec succès")
                        except Exception as e:
                            logger.error(f"[DEBUG] Erreur lors de la création de la carte pour la boutique {shop.name}: {str(e)}")
                            logger.error(f"[DEBUG] Détails: {traceback.format_exc()}")
            else:
                # Afficher les boutiques sans regroupement
                for shop in self.filtered_shops:
                    try:
                        shop_card = ShopCard(shop)
                        shop_card.clicked.connect(self._select_shop)
                        self.shop_list_layout.addWidget(shop_card)
                    except Exception as e:
                        logger.error(f"[DEBUG] Erreur lors de la création de la carte pour la boutique {shop.name}: {str(e)}")
                        logger.error(f"[DEBUG] Détails: {traceback.format_exc()}")
            
            # Ajouter un espaceur final pour pousser les éléments vers le haut
            self.shop_list_layout.addStretch()
            
            logger.debug("[DEBUG] refresh_shops terminé avec succès")
        except Exception as e:
            logger.error(f"[DEBUG] Erreur dans refresh_shops: {str(e)}")
            logger.error(f"[DEBUG] Détails: {traceback.format_exc()}")
    
    def filter_shops(self, shops: List[Shop]) -> List[Shop]:
        """
        Filtre les boutiques selon les critères actuels.
        
        Args:
            shops: Liste des boutiques à filtrer
            
        Returns:
            Liste des boutiques filtrées
        """
        if self.current_filter == "all" and not self.search_text:
            return shops
        
        filtered = []
        for shop in shops:
            # Filtrer par type
            if self.current_filter != "all" and shop.shop_type.name != self.current_filter:
                continue
            
            # Filtrer par texte de recherche
            if self.search_text:
                search_lower = self.search_text.lower()
                name_match = search_lower in shop.name.lower()
                desc_match = hasattr(shop, 'description') and search_lower in shop.description.lower()
                type_match = search_lower in shop.shop_type.name.lower()
                
                if not (name_match or desc_match or type_match):
                    continue
            
            filtered.append(shop)
        
        return filtered
    
    def on_search_text_changed(self, text):
        """
        Gère le changement du texte de recherche.
        """
        self.search_text = text
        self.refresh_shops()
    
    def on_filter_changed(self, index):
        """
        Gère le changement de filtre.
        """
        self.current_filter = self.filter_combo.itemData(index)
        self.refresh_shops()
    
    def _clear_shop_list(self):
        """
        Vide la liste des boutiques.
        """
        logger.debug("[DEBUG] Nettoyage de la liste des boutiques")
        
        # Retirer temporairement le no_shops_label du layout s'il existe
        # mais NE PAS le détruire
        has_no_shops_label = False
        if hasattr(self, 'no_shops_label') and self.no_shops_label is not None:
            # Cacher le label plutôt que de le supprimer
            has_no_shops_label = True
            self.no_shops_label.setVisible(False)
            self.shop_list_layout.removeWidget(self.no_shops_label)
        
        # Supprimer tous les autres widgets
        while self.shop_list_layout.count():
            item = self.shop_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Réajouter le label si nécessaire
        if has_no_shops_label:
            self.no_shops_label.setVisible(True)
            self.shop_list_layout.addWidget(self.no_shops_label)
        
        logger.debug("[DEBUG] Nettoyage terminé")
    
    def _select_shop(self, shop_id: str):
        """
        Sélectionne une boutique et émet le signal shop_selected.
        
        Args:
            shop_id: ID de la boutique sélectionnée
        """
        logger.debug(f"Boutique sélectionnée: {shop_id}")
        self.selected_shop_id = shop_id
        self.shop_selected.emit(shop_id)
    
    def show_help(self):
        """
        Affiche une aide contextuelle pour le sélecteur de boutiques.
        """
        from PyQt6.QtWidgets import QMessageBox
        
        help_text = """
        <h3>Aide du sélecteur de boutiques</h3>
        <p>Bienvenue dans l'interface de sélection des boutiques de YakTaa.</p>
        <ul>
            <li><b>Recherche</b>: Filtrez les boutiques par nom, type ou description</li>
            <li><b>Filtre par type</b>: Sélectionnez un type spécifique de boutique</li>
            <li><b>Cartes de boutique</b>: Cliquez sur une boutique pour l'ouvrir</li>
        </ul>
        <p>Les boutiques sont organisées par type et affichent des informations importantes comme le nombre d'articles disponibles et leur statut légal.</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Aide - Sélecteur de boutiques")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    @property
    def filtered_shops(self):
        return self.filter_shops(self.shops)

    def _show_no_shops_message(self):
        self.no_shops_label.show()

    def _create_type_header(self, shop_type, shop_count):
        """
        Crée un en-tête pour un type de boutique.
        
        Args:
            shop_type (str): Le type de boutique
            shop_count (int): Le nombre de boutiques de ce type
        """
        logger.debug(f"[DEBUG] Création de l'en-tête pour le type {shop_type}")
        
        # Créer un frame pour l'en-tête
        header_frame = QFrame()
        header_frame.setObjectName("type_header_frame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 10, 5, 10)
        
        # Icône du type de boutique
        try:
            logger.debug(f"[DEBUG] Création de l'icône pour le type {shop_type}")
            icon_label = QLabel()
            
            # Normaliser le nom du type pour le chemin du fichier (en minuscules)
            icon_name = shop_type.lower()
            icon_path = os.path.join(BASE_DIR, f"assets/icons/shop_type/{icon_name}.png")
            
            logger.debug(f"[DEBUG] Recherche de l'icône: {icon_path}")
            
            if os.path.exists(icon_path):
                logger.debug(f"[DEBUG] Icône trouvée: {icon_path}")
                pixmap = QPixmap(icon_path)
                
                if not pixmap.isNull():
                    logger.debug("[DEBUG] Mise à l'échelle et application de l'icône")
                    pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(pixmap)
                    icon_label.setFixedSize(24, 24)
                    logger.debug("[DEBUG] Icône ajoutée avec succès")
                else:
                    logger.warning(f"[DEBUG] Icône invalide: {icon_path}")
                    icon_label.setText(shop_type[0])
            else:
                logger.warning(f"[DEBUG] Icône non trouvée: {icon_path}")
                icon_label.setText(shop_type[0])
                
            header_layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"[DEBUG] Erreur lors de la création de l'icône: {str(e)}")
        
        # Libellé du type
        logger.debug(f"[DEBUG] Création du label pour le type {shop_type}")
        type_label = QLabel(f"{shop_type.replace('_', ' ').title()} ({shop_count})")
        logger.debug("[DEBUG] Tentative d'obtention de la police 'heading'")
        type_label.setFont(get_font("heading", 14))
        header_layout.addWidget(type_label)
        logger.debug("[DEBUG] Label ajouté avec succès")
        
        # Espaceur pour pousser le texte vers la gauche
        header_layout.addStretch()
        logger.debug("[DEBUG] Ajout d'un espaceur")
        
        # Ajouter l'en-tête au layout principal
        self.shop_list_layout.addWidget(header_frame)
        logger.debug("[DEBUG] En-tête ajouté au layout principal")
    
    def clear_shops(self):
        """
        Vide la liste des boutiques.
        Cette méthode est appelée par ShopScreen.clear_shops().
        """
        logger.debug("[DEBUG] clear_shops appelé")
        self.shops = []
        self._clear_shop_list()
        self._show_no_shops_message()
    
    def set_location_name(self, location_name):
        """
        Définit le nom de l'emplacement actuel dans le sélecteur.
        Cette méthode est appelée par ShopScreen.set_location_name().
        
        Args:
            location_name: Nom de l'emplacement
        """
        logger.debug(f"[DEBUG] set_location_name appelé avec {location_name}")
        
        # Mettre à jour le sous-titre pour inclure le nom de l'emplacement
        if hasattr(self, 'subtitle_label') and self.subtitle_label is not None:
            self.subtitle_label.setText(f"Boutiques disponibles à {location_name}")
    
    def add_shop(self, shop):
        """
        Ajoute une boutique au sélecteur.
        Cette méthode est appelée par ShopScreen.add_shop().
        
        Args:
            shop: Objet boutique à ajouter
        """
        logger.debug(f"[DEBUG] add_shop appelé avec {shop.name if hasattr(shop, 'name') else shop}")
        
        # Ajouter la boutique à la liste des boutiques
        if shop not in self.shops:
            self.shops.append(shop)
            self.refresh_shops()
