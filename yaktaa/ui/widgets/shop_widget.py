"""
Widget d'interface de boutique pour YakTaa.
Permet aux joueurs d'acheter et de vendre des objets dans les boutiques du jeu.
"""

import logging
from typing import Dict, List, Optional, Tuple, Callable
import os

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QTabWidget, QSplitter, 
                            QTextEdit, QScrollArea, QFrame, QDialog, QMessageBox,
                            QGridLayout, QSpacerItem, QSizePolicy, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor

from ...items.shop_manager import Shop
from ...items.item import Item
from ...items.inventory_manager import InventoryManager
from ..theme import get_stylesheet, get_font

# Obtenir le répertoire de base du jeu
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Configuration du logging
logger = logging.getLogger(__name__)

class ItemDetailWidget(QWidget):
    """Widget affichant les détails d'un objet sélectionné."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre de l'objet avec style cyberpunk
        self.title_frame = QFrame()
        self.title_frame.setObjectName("item-title-frame")
        self.title_frame.setStyleSheet("#item-title-frame { background-color: rgba(0, 0, 0, 0.3); border-radius: 8px; }")
        title_layout = QVBoxLayout(self.title_frame)
        
        self.title_label = QLabel("Sélectionnez un objet")
        self.title_label.setFont(get_font("heading", 16, bold=True))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.title_label)
        
        layout.addWidget(self.title_frame)
        
        # Image et informations de base
        info_layout = QHBoxLayout()
        
        # Image de l'objet avec cadre stylisé
        image_frame = QFrame()
        image_frame.setObjectName("item-image-frame")
        image_frame.setStyleSheet("#item-image-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        image_frame.setFixedSize(QSize(150, 150))
        image_layout = QVBoxLayout(image_frame)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(QSize(128, 128))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.3); border-radius: 5px;")
        image_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(image_frame)
        
        # Informations de base
        basic_info_layout = QVBoxLayout()
        
        # Type et rareté
        self.type_frame = QFrame()
        self.type_frame.setObjectName("item-type-frame")
        self.type_frame.setStyleSheet("#item-type-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 5px; }")
        type_layout = QVBoxLayout(self.type_frame)
        type_layout.setContentsMargins(10, 5, 10, 5)
        
        self.type_label = QLabel("Type: N/A")
        self.type_label.setFont(get_font("body", 12))
        type_layout.addWidget(self.type_label)
        
        self.rarity_label = QLabel("Rareté: N/A")
        self.rarity_label.setFont(get_font("body", 12))
        type_layout.addWidget(self.rarity_label)
        
        basic_info_layout.addWidget(self.type_frame)
        
        # Prix
        self.price_frame = QFrame()
        self.price_frame.setObjectName("item-price-frame")
        self.price_frame.setStyleSheet("#item-price-frame { background-color: rgba(0, 120, 215, 0.2); border-radius: 5px; }")
        price_layout = QHBoxLayout(self.price_frame)
        price_layout.setContentsMargins(10, 5, 10, 5)
        
        price_icon = QLabel()
        price_icon.setPixmap(QPixmap("assets/icons/credit.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        price_layout.addWidget(price_icon)
        
        self.price_label = QLabel("Prix: N/A")
        self.price_label.setFont(get_font("body", 14, bold=True))
        price_layout.addWidget(self.price_label)
        
        basic_info_layout.addWidget(self.price_frame)
        
        # Espaceur
        basic_info_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        info_layout.addLayout(basic_info_layout)
        layout.addLayout(info_layout)
        
        # Description avec cadre stylisé
        desc_frame = QFrame()
        desc_frame.setObjectName("item-desc-frame")
        desc_frame.setStyleSheet("#item-desc-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        desc_layout = QVBoxLayout(desc_frame)
        
        desc_title = QLabel("Description")
        desc_title.setFont(get_font("heading", 14))
        desc_layout.addWidget(desc_title)
        
        self.description_label = QTextEdit()
        self.description_label.setReadOnly(True)
        self.description_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); border: none; color: rgba(255, 255, 255, 0.8);")
        self.description_label.setMinimumHeight(100)
        desc_layout.addWidget(self.description_label)
        
        layout.addWidget(desc_frame)
        
        # Statistiques avec cadre stylisé
        stats_frame = QFrame()
        stats_frame.setObjectName("item-stats-frame")
        stats_frame.setStyleSheet("#item-stats-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("Statistiques")
        stats_title.setFont(get_font("heading", 14))
        stats_layout.addWidget(stats_title)
        
        self.stats_widget = QWidget()
        self.stats_layout = QGridLayout(self.stats_widget)
        self.stats_layout.setColumnStretch(1, 1)  # La colonne de valeur s'étire
        stats_layout.addWidget(self.stats_widget)
        
        layout.addWidget(stats_frame)
        
        # Bouton d'action avec style
        self.action_frame = QFrame()
        self.action_frame.setObjectName("item-action-frame")
        self.action_frame.setStyleSheet("#item-action-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        action_layout = QVBoxLayout(self.action_frame)
        
        self.action_button = QPushButton("Sélectionnez un objet")
        self.action_button.setEnabled(False)
        self.action_button.setMinimumHeight(40)
        self.action_button.setFont(get_font("body", 14, bold=True))
        action_layout.addWidget(self.action_button)
        
        layout.addWidget(self.action_frame)
    
    def display_item(self, item: Item, price: int, action_text: str, 
                     action_callback: Callable, can_afford: bool = True):
        """
        Affiche les détails d'un objet.
        
        Args:
            item: L'objet à afficher
            price: Le prix de l'objet
            action_text: Le texte du bouton d'action
            action_callback: Fonction appelée lorsque le bouton est cliqué
            can_afford: Si le joueur peut se permettre l'objet
        """
        # Titre
        self.title_label.setText(f"{item.name}")
        
        # Image (à implémenter avec les vraies images)
        icon_path = self._get_item_icon(item)
        self.image_label.setPixmap(QPixmap(icon_path).scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Type et rareté
        item_type = self._get_item_type(item)
        self.type_label.setText(f"Type: {item_type}")
        
        rarity = "Standard"
        if hasattr(item, 'rarity') and item.rarity:
            rarity = item.rarity
        self.rarity_label.setText(f"Rareté: {rarity}")
        
        # Prix
        self.price_label.setText(f"{price}")
        
        # Description
        description = item.description if hasattr(item, 'description') and item.description else "Aucune description disponible."
        self.description_label.setHtml(f"<p>{description}</p>")
        
        # Nettoyer les anciennes statistiques
        self._clear_stats_layout()
        
        # Ajouter les nouvelles statistiques selon le type d'objet
        row = 0
        
        # Statistiques spécifiques au hardware
        if hasattr(item, 'hardware_type'):
            self._add_stat("Performance", getattr(item, 'performance', 'N/A'), row)
            row += 1
            self._add_stat("Consommation", getattr(item, 'power_consumption', 'N/A'), row)
            row += 1
        
        # Statistiques spécifiques aux implants
        elif hasattr(item, 'implant_type'):
            self._add_stat("Emplacement", getattr(item, 'body_location', 'N/A'), row)
            row += 1
            self._add_stat("Difficulté d'installation", getattr(item, 'surgery_difficulty', 'N/A'), row)
            row += 1
            if hasattr(item, 'side_effects') and item.side_effects:
                self._add_stat("Effets secondaires", item.side_effects, row)
                row += 1
        
        # Statistiques spécifiques aux consommables
        elif hasattr(item, 'item_type') and hasattr(item, 'uses'):
            self._add_stat("Utilisations", getattr(item, 'uses', 'N/A'), row)
            row += 1
            self._add_stat("Effet", getattr(item, 'effect_type', 'N/A'), row)
            row += 1
            self._add_stat("Puissance", getattr(item, 'effect_power', 'N/A'), row)
            row += 1
            if hasattr(item, 'duration') and item.duration:
                self._add_stat("Durée", f"{item.duration} sec", row)
                row += 1
        
        # Statistiques spécifiques aux software
        elif hasattr(item, 'software_type'):
            self._add_stat("Version", getattr(item, 'version', 'N/A'), row)
            row += 1
            self._add_stat("Licence", getattr(item, 'license_type', 'N/A'), row)
            row += 1
        
        # Statistiques spécifiques aux armes
        elif hasattr(item, 'weapon_type'):
            self._add_stat("Dégâts", getattr(item, 'damage', 'N/A'), row)
            row += 1
            self._add_stat("Type de dégâts", getattr(item, 'damage_type', 'N/A'), row)
            row += 1
            self._add_stat("Portée", getattr(item, 'range', 'N/A'), row)
            row += 1
            if hasattr(item, 'rate_of_fire') and item.rate_of_fire:
                self._add_stat("Cadence de tir", item.rate_of_fire, row)
                row += 1
        
        # Bouton d'action
        self.action_button.setText(action_text)
        self.action_button.setEnabled(can_afford)
        
        # Style du bouton selon si on peut se le permettre
        if can_afford:
            self.action_button.setStyleSheet("background-color: rgba(0, 150, 0, 0.3); color: white;")
        else:
            self.action_button.setStyleSheet("background-color: rgba(150, 0, 0, 0.3); color: rgba(255, 255, 255, 0.5);")
        
        # Connecter le callback
        try:
            self.action_button.clicked.disconnect()
        except:
            pass  # Ignorer si aucun callback n'était connecté
        
        self.action_button.clicked.connect(action_callback)
    
    def _get_item_icon(self, item: Item) -> str:
        """Retourne le chemin de l'icône en fonction du type d'objet."""
        # Utilisation d'un cache statique pour les chemins d'icônes
        if not hasattr(self.__class__, '_icon_cache'):
            self.__class__._icon_cache = {}
            
        # Calculer une clé de cache unique pour cet item
        cache_key = f"{type(item).__name__}_{item.name}_icon"
        
        # Vérifier si l'icône est déjà en cache
        if cache_key in self.__class__._icon_cache:
            return self.__class__._icon_cache[cache_key]
        
        # Par défaut, utiliser une icône générique
        icon_path = os.path.join(BASE_DIR, "assets/icons/items/generic.png")
        
        try:
            # Déterminer le type d'objet
            if hasattr(item, 'hardware_type'):
                icon_path = os.path.join(BASE_DIR, f"assets/icons/items/hardware_{item.hardware_type.lower()}.png")
            elif hasattr(item, 'item_type') and hasattr(item, 'uses'):
                icon_path = os.path.join(BASE_DIR, f"assets/icons/items/consumable_{item.item_type.lower()}.png")
            elif hasattr(item, 'software_type'):
                icon_path = os.path.join(BASE_DIR, f"assets/icons/items/software_{item.software_type.lower()}.png")
            elif hasattr(item, 'implant_type'):
                icon_path = os.path.join(BASE_DIR, f"assets/icons/items/implant_{item.implant_type.lower()}.png")
            elif hasattr(item, 'weapon_type'):
                icon_path = os.path.join(BASE_DIR, f"assets/icons/items/weapon_{item.weapon_type.lower()}.png")
            
            # Vérifier si le fichier existe, sinon utiliser l'icône générique
            if not os.path.exists(icon_path):
                logger.warning(f"Icône introuvable: {icon_path}, utilisation de l'icône générique")
                icon_path = os.path.join(BASE_DIR, "assets/icons/items/generic.png")
            
            # Mettre en cache le chemin d'icône
            self.__class__._icon_cache[cache_key] = icon_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'icône pour {item.name}: {str(e)}")
            # Utiliser l'icône générique en cas d'erreur
            icon_path = os.path.join(BASE_DIR, "assets/icons/items/generic.png")
            
        return icon_path
    
    def _get_item_type(self, item: Item) -> str:
        """Retourne le type d'objet sous forme de chaîne."""
        if hasattr(item, 'hardware_type'):
            return f"Hardware - {item.hardware_type}"
        elif hasattr(item, 'item_type') and hasattr(item, 'uses'):
            return f"Consommable - {item.item_type}"
        elif hasattr(item, 'software_type'):
            return f"Software - {item.software_type}"
        elif hasattr(item, 'implant_type'):
            return f"Implant - {item.implant_type}"
        elif hasattr(item, 'weapon_type'):
            return f"Arme - {item.weapon_type}"
        return "Objet générique"
    
    def _add_stat(self, name: str, value, row: int):
        """Ajoute une statistique à la grille."""
        # Nom de la statistique
        name_label = QLabel(f"{name}:")
        name_label.setFont(get_font("body", 12, bold=True))
        self.stats_layout.addWidget(name_label, row, 0)
        
        # Valeur de la statistique
        value_label = QLabel(str(value))
        value_label.setFont(get_font("body", 12))
        self.stats_layout.addWidget(value_label, row, 1)
    
    def _clear_stats_layout(self):
        """Nettoie la grille de statistiques."""
        # Supprimer tous les widgets de la grille
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def clear(self):
        """Réinitialise l'affichage."""
        self.title_label.setText("Sélectionnez un objet")
        self.image_label.clear()
        self.type_label.setText("Type: N/A")
        self.rarity_label.setText("Rareté: N/A")
        self.price_label.setText("N/A")
        self.description_label.clear()
        self._clear_stats_layout()
        self.action_button.setText("Sélectionnez un objet")
        self.action_button.setEnabled(False)
        self.action_button.setStyleSheet("")
        
        try:
            self.action_button.clicked.disconnect()
        except:
            pass  # Ignorer si aucun callback n'était connecté

class ShopWidget(QWidget):
    """Widget principal pour l'interface de boutique."""
    
    # Signaux
    transaction_completed = pyqtSignal(str, int)  # Message, nouveaux crédits
    exit_shop = pyqtSignal()
    
    def __init__(self, shop: Shop, player_inventory: InventoryManager, player_credits: int, 
                 player_reputation: int = 0, player_location_id: int = 0, parent=None):
        """
        Initialise le widget de la boutique.
        
        Args:
            shop: Instance de la boutique
            player_inventory: Gestionnaire d'inventaire du joueur
            player_credits: Crédits du joueur
            player_reputation: Réputation du joueur auprès de la faction de la boutique
            player_location_id: ID de la localisation du joueur
            parent: Widget parent
        """
        super().__init__(parent)
        
        self.shop = shop
        self.player_inventory = player_inventory
        self.player_credits = player_credits
        self.player_reputation = player_reputation
        self.player_location_id = player_location_id
        self.current_filter = "all"
        self.current_sort = "name_asc"
        self.search_text = ""
        
        # Cache des données pour éviter les rechargements inutiles
        self._shop_inventory_cache = []
        self._player_inventory_cache = []
        self._filtered_shop_cache = []
        self._filtered_player_cache = []
        self._displayed_shop_items = []
        self._displayed_player_items = []
        
        # Configuration pour le chargement par lots
        self.batch_size = 20  # Nombre d'articles à charger à la fois
        self.is_loading = False
        
        # Interface
        self.setup_ui()
        
        # Chargement initial des données
        logger.debug("Initialisation du chargement des données de la boutique")
        self.load_shop_data()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # En-tête avec style cyberpunk
        header_frame = QFrame()
        header_frame.setObjectName("shop-header")
        header_frame.setStyleSheet("#shop-header { background-color: rgba(0, 0, 0, 0.3); border-radius: 8px; }")
        header_layout = QVBoxLayout(header_frame)
        
        # Ligne supérieure: Titre et crédits
        top_header = QHBoxLayout()
        
        # Titre de la boutique avec icône
        title_layout = QHBoxLayout()
        shop_icon = QLabel()
        shop_icon.setPixmap(QPixmap(os.path.join(BASE_DIR, f"assets/icons/shop_type/{self.shop.shop_type.lower()}.png")).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        title_layout.addWidget(shop_icon)
        
        self.shop_title = QLabel(self.shop.name)
        self.shop_title.setFont(get_font("heading", 18, bold=True))
        title_layout.addWidget(self.shop_title)
        top_header.addLayout(title_layout)
        
        # Espaceur
        top_header.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Crédits du joueur avec style
        credits_frame = QFrame()
        credits_frame.setObjectName("credits-display")
        credits_frame.setStyleSheet("#credits-display { background-color: rgba(0, 120, 215, 0.2); border-radius: 5px; padding: 5px; }")
        credits_layout = QHBoxLayout(credits_frame)
        credits_layout.setContentsMargins(10, 5, 10, 5)
        
        credits_icon = QLabel()
        credits_icon.setPixmap(QPixmap(os.path.join(BASE_DIR, "assets/icons/credit.png")).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        credits_layout.addWidget(credits_icon)
        
        self.credits_label = QLabel(f"{self.player_credits}")
        self.credits_label.setFont(get_font("body", 14, bold=True))
        credits_layout.addWidget(self.credits_label)
        
        top_header.addWidget(credits_frame)
        header_layout.addLayout(top_header)
        
        # Description de la boutique
        self.shop_description = QLabel(self.shop.description)
        self.shop_description.setWordWrap(True)
        self.shop_description.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        header_layout.addWidget(self.shop_description)
        
        layout.addWidget(header_frame)
        
        # Barre d'outils: recherche, filtres, tri
        toolbar_layout = QHBoxLayout()
        
        # Recherche
        search_layout = QHBoxLayout()
        search_label = QLabel("Recherche:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un item...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        toolbar_layout.addLayout(search_layout)
        
        # Filtre par type
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrer:")
        filter_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tous les items", "all")
        self.filter_combo.addItem("Hardware", "hardware")
        self.filter_combo.addItem("Software", "software")
        self.filter_combo.addItem("Implants", "implant")
        self.filter_combo.addItem("Consommables", "consumable")
        self.filter_combo.addItem("Armes", "weapon")
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        toolbar_layout.addLayout(filter_layout)
        
        # Tri
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Trier par:")
        sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Nom (A-Z)", "name_asc")
        self.sort_combo.addItem("Nom (Z-A)", "name_desc")
        self.sort_combo.addItem("Prix (croissant)", "price_asc")
        self.sort_combo.addItem("Prix (décroissant)", "price_desc")
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        sort_layout.addWidget(self.sort_combo)
        
        toolbar_layout.addLayout(sort_layout)
        
        layout.addLayout(toolbar_layout)
        
        # Contenu principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Onglets (Acheter/Vendre)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 5px; }")
        
        # Tab Acheter
        self.buy_tab = QWidget()
        buy_layout = QVBoxLayout(self.buy_tab)
        
        # Liste des objets à acheter améliorée
        self.buy_list = QListWidget()
        self.buy_list.setMinimumWidth(350)
        self.buy_list.setIconSize(QSize(32, 32))
        self.buy_list.setSpacing(2)
        self.buy_list.currentRowChanged.connect(self.on_buy_item_selected)
        buy_layout.addWidget(self.buy_list)
        
        self.tab_widget.addTab(self.buy_tab, "Acheter")
        
        # Tab Vendre
        self.sell_tab = QWidget()
        sell_layout = QVBoxLayout(self.sell_tab)
        
        # Liste des objets à vendre améliorée
        self.sell_list = QListWidget()
        self.sell_list.setMinimumWidth(350)
        self.sell_list.setIconSize(QSize(32, 32))
        self.sell_list.setSpacing(2)
        self.sell_list.currentRowChanged.connect(self.on_sell_item_selected)
        sell_layout.addWidget(self.sell_list)
        
        self.tab_widget.addTab(self.sell_tab, "Vendre")
        
        # Ajouter les onglets au splitter
        main_splitter.addWidget(self.tab_widget)
        
        # Panneau de détails amélioré
        detail_frame = QFrame()
        detail_frame.setObjectName("detail-frame")
        detail_frame.setStyleSheet("#detail-frame { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        detail_layout = QVBoxLayout(detail_frame)
        
        self.detail_widget = ItemDetailWidget()
        detail_layout.addWidget(self.detail_widget)
        
        main_splitter.addWidget(detail_frame)
        
        # Définir les tailles relatives des widgets dans le splitter
        main_splitter.setSizes([350, 450])
        
        layout.addWidget(main_splitter)
        
        # Pied de page
        footer_frame = QFrame()
        footer_frame.setObjectName("shop-footer")
        footer_frame.setStyleSheet("#shop-footer { background-color: rgba(0, 0, 0, 0.2); border-radius: 8px; }")
        footer_layout = QHBoxLayout(footer_frame)
        
        # Bouton de retour
        self.back_button = QPushButton("Quitter la boutique")
        self.back_button.setIcon(QIcon(os.path.join(BASE_DIR, "assets/icons/exit.png")))
        self.back_button.clicked.connect(self.exit_shop.emit)
        footer_layout.addWidget(self.back_button)
        
        # Ajouter des boutons d'aide
        help_button = QPushButton("Aide")
        help_button.setIcon(QIcon(os.path.join(BASE_DIR, "assets/icons/help.png")))
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        layout.addWidget(footer_frame)
        
        # Appliquer le style
        self.setStyleSheet(get_stylesheet("shop"))
    
    def load_shop_data(self):
        """Charge les données initiales de la boutique sans les afficher."""
        logger.debug(f"Chargement des données de la boutique {self.shop.name}")
        try:
            # Stockage des données brutes
            self._shop_inventory_cache = list(self.shop.inventory)
            if hasattr(self.player_inventory, 'items'):
                self._player_inventory_cache = list(self.player_inventory.items)
            else:
                self._player_inventory_cache = []
                
            # Premier filtrage et tri
            self._apply_filters_and_sort()
            
            # Rafraîchir l'interface avec les données filtrées
            self.refresh_shop_data()
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de la boutique: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les données de la boutique: {str(e)}")
    
    def _apply_filters_and_sort(self):
        """Applique les filtres et le tri aux données brutes."""
        try:
            # Filtrer et trier l'inventaire de la boutique
            self._filtered_shop_cache = self.filter_inventory(self._shop_inventory_cache)
            self._filtered_shop_cache = self.sort_inventory(self._filtered_shop_cache)
            
            # Filtrer et trier l'inventaire du joueur
            self._filtered_player_cache = self.filter_player_inventory(self._player_inventory_cache)
            self._filtered_player_cache = self.sort_player_inventory(self._filtered_player_cache)
        except Exception as e:
            logger.error(f"Erreur lors de l'application des filtres: {str(e)}", exc_info=True)
    
    def refresh_shop_data(self):
        """Rafraîchit l'affichage des données de la boutique."""
        if self.is_loading:
            return
            
        self.is_loading = True
        logger.debug("Rafraîchissement de l'interface de la boutique")
        
        try:
            # Mise à jour des crédits
            self.credits_label.setText(f"{self.player_credits}")
            
            # Vider les listes d'affichage
            self.buy_list.clear()
            self.sell_list.clear()
            
            # Réappliquer les filtres et le tri si nécessaire
            self._apply_filters_and_sort()
            
            # Afficher les articles par lots
            self._display_shop_items()
            self._display_player_items()
            
            # Réinitialiser les détails
            self.detail_widget.clear()
            
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des données: {str(e)}", exc_info=True)
        finally:
            self.is_loading = False
    
    def _display_shop_items(self):
        """Affiche les articles de la boutique par lots."""
        try:
            # Limiter le nombre d'articles à afficher
            display_items = self._filtered_shop_cache[:self.batch_size]
            self._displayed_shop_items = display_items
            
            for i, (item, price) in enumerate(display_items):
                # Réutiliser _create_item_widget pour créer l'affichage de l'article
                item_widget, list_item = self._create_item_widget(
                    item, 
                    price, 
                    self.player_credits >= price
                )
                self.buy_list.addItem(list_item)
                self.buy_list.setItemWidget(list_item, item_widget)
            
            # Ajouter un message si aucun article ne correspond aux critères
            if not display_items:
                empty_item = QListWidgetItem("Aucun article ne correspond aux critères")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.buy_list.addItem(empty_item)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des articles de la boutique: {str(e)}", exc_info=True)
    
    def _display_player_items(self):
        """Affiche les articles du joueur par lots."""
        try:
            # Limiter le nombre d'articles à afficher
            display_items = self._filtered_player_cache[:self.batch_size]
            self._displayed_player_items = display_items
            
            for i, item in enumerate(display_items):
                # Calculer le prix de vente (50% du prix original)
                sell_price = int(item.price * 0.5)
                
                # Réutiliser _create_item_widget pour créer l'affichage de l'article
                item_widget, list_item = self._create_item_widget(
                    item, 
                    sell_price, 
                    True,
                    is_selling=True
                )
                self.sell_list.addItem(list_item)
                self.sell_list.setItemWidget(list_item, item_widget)
            
            # Ajouter un message si aucun article ne correspond aux critères
            if not display_items:
                empty_item = QListWidgetItem("Aucun article ne correspond aux critères")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sell_list.addItem(empty_item)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des articles du joueur: {str(e)}", exc_info=True)
    
    def _create_item_widget(self, item, price, can_afford=True, is_selling=False):
        """Crée un widget pour un article (factorisation du code)."""
        # Créer un widget personnalisé pour chaque item
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        try:
            # Icône
            icon_label = QLabel()
            icon_path = self.detail_widget._get_item_icon(item)
            icon_label.setPixmap(QPixmap(icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
            item_layout.addWidget(icon_label)
            
            # Informations sur l'item
            info_layout = QVBoxLayout()
            name_label = QLabel(item.name)
            name_label.setFont(get_font("body", 12, bold=True))
            info_layout.addWidget(name_label)
            
            # Type et rareté
            type_rarity = self.get_item_type_display(item)
            type_label = QLabel(type_rarity)
            type_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            info_layout.addWidget(type_label)
            
            item_layout.addLayout(info_layout)
            
            # Espaceur
            item_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            
            # Prix
            frame_id = f"{'sell' if is_selling else 'price'}-frame-{id(item)}"
            price_frame = QFrame()
            price_frame.setObjectName(frame_id)
            
            if not is_selling:
                price_style = "background-color: rgba(0, 150, 0, 0.2);" if can_afford else "background-color: rgba(150, 0, 0, 0.2);"
            else:
                price_style = "background-color: rgba(0, 150, 0, 0.2);"
                
            price_frame.setStyleSheet(f"#{frame_id} {{ {price_style} border-radius: 5px; padding: 2px; }}")
            
            price_layout = QHBoxLayout(price_frame)
            price_layout.setContentsMargins(5, 2, 5, 2)
            
            price_label = QLabel(f"{price}")
            price_label.setFont(get_font("body", 12, bold=True))
            price_layout.addWidget(price_label)
            
            item_layout.addWidget(price_frame)
            
            # Griser les objets trop chers
            if not is_selling and not can_afford:
                name_label.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
            
            # Créer l'élément de liste
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            return item_widget, list_item
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du widget d'article: {str(e)}", exc_info=True)
            # En cas d'erreur, retourner un widget vide
            return QWidget(), QListWidgetItem()
    
    def get_item_type_display(self, item: Item) -> str:
        """Retourne une chaîne formatée avec le type et la rareté de l'item."""
        item_type = ""
        rarity = ""
        
        # Déterminer le type
        if hasattr(item, 'hardware_type'):
            item_type = f"Hardware - {item.hardware_type}"
        elif hasattr(item, 'item_type') and hasattr(item, 'uses'):
            item_type = f"Consommable - {item.item_type}"
        elif hasattr(item, 'software_type'):
            item_type = f"Software - {item.software_type}"
        elif hasattr(item, 'implant_type'):
            item_type = f"Implant - {item.implant_type}"
        elif hasattr(item, 'weapon_type'):
            item_type = f"Arme - {item.weapon_type}"
        
        # Déterminer la rareté
        if hasattr(item, 'rarity'):
            rarity = item.rarity
        
        if rarity:
            return f"{item_type} | {rarity}"
        return item_type
    
    def filter_inventory(self, inventory):
        """Filtre l'inventaire de la boutique selon les critères actuels."""
        if not inventory:
            return []
            
        if self.current_filter == "all" and not self.search_text:
            return inventory
        
        try:
            filtered = []
            for item_data in inventory:
                item, price = item_data
                
                # Filtrer par type
                if self.current_filter != "all":
                    if self.current_filter == "hardware" and not hasattr(item, 'hardware_type'):
                        continue
                    elif self.current_filter == "software" and not hasattr(item, 'software_type'):
                        continue
                    elif self.current_filter == "implant" and not hasattr(item, 'implant_type'):
                        continue
                    elif self.current_filter == "consumable" and not (hasattr(item, 'item_type') and hasattr(item, 'uses')):
                        continue
                    elif self.current_filter == "weapon" and not hasattr(item, 'weapon_type'):
                        continue
                
                # Filtrer par texte de recherche
                if self.search_text:
                    search_lower = self.search_text.lower()
                    name_match = item.name.lower().find(search_lower) != -1
                    desc_match = False
                    if hasattr(item, 'description'):
                        desc_match = item.description.lower().find(search_lower) != -1
                    
                    if not (name_match or desc_match):
                        continue
                
                filtered.append(item_data)
            
            return filtered
        except Exception as e:
            logger.error(f"Erreur lors du filtrage de l'inventaire: {str(e)}", exc_info=True)
            return []
    
    def filter_player_inventory(self, inventory):
        """Filtre l'inventaire du joueur selon les critères actuels."""
        if not inventory:
            return []
            
        if self.current_filter == "all" and not self.search_text:
            return inventory
        
        try:
            filtered = []
            for item in inventory:
                # Filtrer par type
                if self.current_filter != "all":
                    if self.current_filter == "hardware" and not hasattr(item, 'hardware_type'):
                        continue
                    elif self.current_filter == "software" and not hasattr(item, 'software_type'):
                        continue
                    elif self.current_filter == "implant" and not hasattr(item, 'implant_type'):
                        continue
                    elif self.current_filter == "consumable" and not (hasattr(item, 'item_type') and hasattr(item, 'uses')):
                        continue
                    elif self.current_filter == "weapon" and not hasattr(item, 'weapon_type'):
                        continue
                
                # Filtrer par texte de recherche
                if self.search_text:
                    search_lower = self.search_text.lower()
                    name_match = item.name.lower().find(search_lower) != -1
                    desc_match = False
                    if hasattr(item, 'description'):
                        desc_match = item.description.lower().find(search_lower) != -1
                    
                    if not (name_match or desc_match):
                        continue
                
                filtered.append(item)
            
            return filtered
        except Exception as e:
            logger.error(f"Erreur lors du filtrage de l'inventaire du joueur: {str(e)}", exc_info=True)
            return []
    
    def sort_inventory(self, inventory):
        """Trie l'inventaire selon le critère de tri actuel."""
        if not inventory:
            return []
            
        try:
            if self.current_sort == "name_asc":
                return sorted(inventory, key=lambda x: x[0].name.lower())
            elif self.current_sort == "name_desc":
                return sorted(inventory, key=lambda x: x[0].name.lower(), reverse=True)
            elif self.current_sort == "price_asc":
                return sorted(inventory, key=lambda x: x[1])
            elif self.current_sort == "price_desc":
                return sorted(inventory, key=lambda x: x[1], reverse=True)
            return inventory
        except Exception as e:
            logger.error(f"Erreur lors du tri de l'inventaire: {str(e)}", exc_info=True)
            return inventory
    
    def sort_player_inventory(self, inventory):
        """Trie l'inventaire du joueur selon le critère de tri actuel."""
        if not inventory:
            return []
            
        try:
            if self.current_sort == "name_asc":
                return sorted(inventory, key=lambda x: x.name.lower())
            elif self.current_sort == "name_desc":
                return sorted(inventory, key=lambda x: x.name.lower(), reverse=True)
            elif self.current_sort == "price_asc":
                return sorted(inventory, key=lambda x: x.price)
            elif self.current_sort == "price_desc":
                return sorted(inventory, key=lambda x: x.price, reverse=True)
            return inventory
        except Exception as e:
            logger.error(f"Erreur lors du tri de l'inventaire du joueur: {str(e)}", exc_info=True)
            return inventory
    
    def on_search_changed(self, text):
        """Gère le changement du texte de recherche."""
        if self.search_text == text:
            return  # Éviter les rechargements inutiles
        self.search_text = text
        self.refresh_shop_data()
    
    def on_filter_changed(self, index):
        """Gère le changement de filtre."""
        new_filter = self.filter_combo.itemData(index)
        if self.current_filter == new_filter:
            return  # Éviter les rechargements inutiles
        self.current_filter = new_filter
        self.refresh_shop_data()
    
    def on_sort_changed(self, index):
        """Gère le changement de tri."""
        new_sort = self.sort_combo.itemData(index)
        if self.current_sort == new_sort:
            return  # Éviter les rechargements inutiles
        self.current_sort = new_sort
        self.refresh_shop_data()
    
    def on_buy_item_selected(self, row: int):
        """Gère la sélection d'un objet à acheter."""
        if row < 0 or row >= len(self._displayed_shop_items):
            self.detail_widget.clear()
            return
        
        item, price = self._displayed_shop_items[row]
        can_afford = self.player_credits >= price
        
        self.detail_widget.display_item(
            item=item,
            price=price,
            action_text=f"Acheter pour {price} crédits",
            action_callback=lambda: self.buy_item(row),
            can_afford=can_afford
        )
    
    def on_sell_item_selected(self, row: int):
        """Gère la sélection d'un objet à vendre."""
        if row < 0 or row >= len(self._displayed_player_items):
            self.detail_widget.clear()
            return
        
        item = self._displayed_player_items[row]
        sell_price = int(item.price * 0.5)
        
        self.detail_widget.display_item(
            item=item,
            price=sell_price,
            action_text=f"Vendre pour {sell_price} crédits",
            action_callback=lambda: self.sell_item(row),
            can_afford=True  # Toujours vrai pour la vente
        )
    
    def buy_item(self, item_index: int):
        """Achète un objet de la boutique."""
        if item_index < 0 or item_index >= len(self._displayed_shop_items):
            return
        
        # Acheter l'objet
        success, message, item, remaining_credits = self.shop.buy_item(
            item_index, self.player_inventory, self.player_credits, self.player_location_id
        )
        
        # Mettre à jour les crédits
        if success:
            self.player_credits = remaining_credits
            self.transaction_completed.emit(message, remaining_credits)
            self.refresh_shop_data()
        else:
            # Afficher un message d'erreur
            QMessageBox.warning(self, "Erreur d'achat", message)
    
    def sell_item(self, item_index: int):
        """Vend un objet à la boutique."""
        if item_index < 0 or item_index >= len(self._displayed_player_items):
            return
        
        # Vendre l'objet
        success, message, new_credits = self.shop.sell_item(
            item_index, self.player_inventory, self.player_credits, self.player_location_id
        )
        
        # Mettre à jour les crédits
        if success:
            self.player_credits = new_credits
            self.transaction_completed.emit(message, new_credits)
            self.refresh_shop_data()
        else:
            # Afficher un message d'erreur
            QMessageBox.warning(self, "Erreur de vente", message)
    
    def update_credits(self, credits: int):
        """Met à jour l'affichage des crédits."""
        self.player_credits = credits
        self.credits_label.setText(f"{self.player_credits}")
        
        # Rafraîchir les indicateurs visuels d'accessibilité
        for i, (item, price) in enumerate(self._displayed_shop_items):
            list_item = self.buy_list.item(i)
            if price > self.player_credits:
                list_item.setForeground(QColor(150, 150, 150))
            else:
                list_item.setForeground(QColor(255, 255, 255))
            
        # Mettre à jour le bouton d'action si un objet est sélectionné
        current_row = self.buy_list.currentRow()
        if current_row >= 0 and current_row < len(self._displayed_shop_items):
            self.on_buy_item_selected(current_row)
    
    def show_help(self):
        """Affiche l'aide."""
        help_text = "Aide de la boutique:\n\n"
        help_text += "  * Utilisez les filtres pour afficher uniquement les objets qui vous intéressent.\n"
        help_text += "  * Triez les objets par nom ou prix pour les trouver plus facilement.\n"
        help_text += "  * Sélectionnez un objet pour afficher ses détails et acheter ou vendre.\n"
        help_text += "  * Utilisez le bouton 'Acheter' pour acheter un objet ou 'Vendre' pour vendre un objet.\n"
        
        QMessageBox.information(self, "Aide", help_text)
