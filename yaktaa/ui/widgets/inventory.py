"""
Module pour l'interface d'inventaire du joueur dans YakTaa
Ce module définit les widgets d'interface utilisateur pour l'inventaire.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QSplitter, QFrame, QTabWidget, QGridLayout,
    QScrollArea, QToolBar, QMenu, QToolButton,
    QSizePolicy, QSpacerItem, QGroupBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QLineEdit, QAbstractItemView, QLayout
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QIcon, QFont, QPixmap, QDrag, QDragEnterEvent, QDropEvent, QMouseEvent, QAction

from yaktaa.items.inventory_manager import InventoryManager, InventoryItem
from yaktaa.items.hardware import Hardware, HardwareType, HardwareRarity

class ItemWidget(QFrame):
    """Widget pour afficher un objet dans l'inventaire"""
    
    # Signal émis lorsqu'un objet est cliqué
    clicked = pyqtSignal(object)
    
    # Signal émis lorsqu'un objet est double-cliqué
    double_clicked = pyqtSignal(object)
    
    # Couleurs pour les différents types d'objets
    TYPE_COLORS = {
        "armes": "#FF5555",       # Rouge
        "armures": "#5555FF",     # Bleu
        "consommables": "#55FF55", # Vert
        "outils": "#FFFF55",      # Jaune
        "divers": "#AAAAAA"       # Gris
    }
    
    # Icônes pour les différents types d'objets
    TYPE_ICONS = {
        "armes": "",
        "armures": "",
        "consommables": "",
        "outils": "",
        "divers": ""
    }
    
    def __init__(self, item: 'Item', parent: Optional[QWidget] = None):
        """Initialise le widget d'objet"""
        super().__init__(parent)
        
        # Référence à l'objet
        self.item = item
        
        # Configuration du cadre
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumSize(100, 100)
        self.setMaximumSize(150, 150)
        
        # Appliquer le style en fonction du type
        item_type = item.type.lower()
        type_color = self.TYPE_COLORS.get(item_type, "#AAAAAA")
        self.setStyleSheet(f"""
            ItemWidget {{
                background-color: #333333;
                border: 2px solid {type_color};
                border-radius: 5px;
            }}
            
            ItemWidget:hover {{
                background-color: #444444;
                border: 2px solid #FFFFFF;
            }}
        """)
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)
        
        # Icône et type
        self.type_layout = QHBoxLayout()
        
        # Icône
        self.icon_label = QLabel(self.TYPE_ICONS.get(item_type, ""))
        self.icon_label.setStyleSheet(f"color: {type_color}; font-size: 16px;")
        self.type_layout.addWidget(self.icon_label)
        
        # Type
        self.type_label = QLabel(item_type.capitalize())
        self.type_label.setStyleSheet(f"color: {type_color}; font-weight: bold;")
        self.type_layout.addWidget(self.type_label)
        
        self.layout.addLayout(self.type_layout)
        
        # Nom
        self.name_label = QLabel(item.name)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.layout.addWidget(self.name_label)
        
        # Quantité
        if hasattr(item, 'quantity') and item.quantity > 1:
            self.quantity_label = QLabel(f"x{item.quantity}")
            self.quantity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.quantity_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            self.layout.addWidget(self.quantity_label)
        
        # Prix
        self.price_label = QLabel(f"{item.value} ¥")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.price_label.setStyleSheet("color: #55AA55;")
        self.layout.addWidget(self.price_label)
        
        # Rendre le widget cliquable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Gère l'événement de clic sur le widget"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.item)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Gère l'événement de double-clic sur le widget"""
        super().mouseDoubleClickEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.item)


class HardwareWidget(QFrame):
    """Widget pour afficher un composant matériel dans l'inventaire"""
    
    # Signal émis lorsqu'un composant est cliqué
    clicked = pyqtSignal(object)
    
    # Signal émis lorsqu'un composant est double-cliqué
    double_clicked = pyqtSignal(object)
    
    # Couleurs pour les différentes raretés
    RARITY_COLORS = {
        "common": "#AAAAAA",
        "uncommon": "#55AA55",
        "rare": "#5555FF",
        "epic": "#AA55AA",
        "legendary": "#FFAA00"
    }
    
    # Icônes pour les différents types de matériel
    TYPE_ICONS = {
        "cpu": "",
        "memory": "",
        "storage": "",
        "network": "",
        "security": "",
        "tool": ""
    }
    
    def __init__(self, hardware: 'Hardware', parent: Optional[QWidget] = None):
        """Initialise le widget de composant matériel"""
        super().__init__(parent)
        
        # Référence au composant
        self.hardware = hardware
        
        # Configuration du cadre
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumSize(100, 100)
        self.setMaximumSize(150, 150)
        
        # Appliquer le style en fonction de la rareté
        rarity_color = self.RARITY_COLORS.get(hardware.rarity, "#AAAAAA")
        self.setStyleSheet(f"""
            HardwareWidget {{
                background-color: #333333;
                border: 2px solid {rarity_color};
                border-radius: 5px;
            }}
            
            HardwareWidget:hover {{
                background-color: #444444;
                border: 2px solid #FFFFFF;
            }}
        """)
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)
        
        # Icône et type
        self.type_layout = QHBoxLayout()
        
        # Icône
        self.icon_label = QLabel(self.TYPE_ICONS.get(hardware.type, ""))
        self.icon_label.setStyleSheet(f"color: {rarity_color}; font-size: 16px;")
        self.type_layout.addWidget(self.icon_label)
        
        # Type
        self.type_label = QLabel(hardware.type.capitalize())
        self.type_label.setStyleSheet(f"color: {rarity_color}; font-weight: bold;")
        self.type_layout.addWidget(self.type_label)
        
        self.layout.addLayout(self.type_layout)
        
        # Nom
        self.name_label = QLabel(hardware.name)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.layout.addWidget(self.name_label)
        
        # Niveau
        self.level_label = QLabel(f"Niv. {hardware.level}")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet("color: #AAAAAA;")
        self.layout.addWidget(self.level_label)
        
        # Statistique principale
        main_stat = self._get_main_stat()
        if main_stat:
            self.stat_label = QLabel(main_stat)
            self.stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stat_label.setStyleSheet("color: #CCCCCC;")
            self.layout.addWidget(self.stat_label)
        
        # Prix
        self.price_label = QLabel(f"{hardware.price} ¥")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.price_label.setStyleSheet("color: #55AA55;")
        self.layout.addWidget(self.price_label)
        
        # Rendre le widget cliquable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def _get_main_stat(self) -> str:
        """Récupère la statistique principale du composant en fonction de son type"""
        if self.hardware.type == "cpu":
            return f"+{self.hardware.processing_power} Proc."
        elif self.hardware.type == "memory":
            return f"+{self.hardware.multitasking} Multi."
        elif self.hardware.type == "storage":
            return f"+{self.hardware.capacity} Go"
        elif self.hardware.type == "network":
            return f"+{self.hardware.bandwidth} Mbps"
        elif self.hardware.type == "security":
            return f"+{self.hardware.encryption} Crypt."
        elif self.hardware.type == "tool":
            return f"+{self.hardware.hack_speed_bonus}% Vitesse"
        return ""
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Gère l'événement de clic sur le widget"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.hardware)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Gère l'événement de double-clic sur le widget"""
        super().mouseDoubleClickEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.hardware)


class InventoryWidget(QWidget):
    """Widget d'inventaire principal avec onglets pour objets et matériel"""
    
    # Signaux pour les actions d'inventaire
    item_used = pyqtSignal(object)  # Objet utilisé
    item_dropped = pyqtSignal(object)  # Objet jeté
    hardware_equipped = pyqtSignal(object)  # Matériel équipé
    hardware_unequipped = pyqtSignal(object)  # Matériel déséquipé
    
    def __init__(self, parent=None):
        """Initialise le widget d'inventaire"""
        super().__init__(parent)
        
        # Initialiser les variables
        self.inventory_manager = None
        self.selected_item = None
        self.selected_hardware = None
        self.equipment_slots = {}
        self.stats = {}
        self.stat_labels = {}
        
        # Initialiser l'interface utilisateur
        self._init_ui()
        
        # Connecter les boutons d'action
        self.use_button.clicked.connect(self._use_item)
        self.drop_button.clicked.connect(self._on_drop_button_clicked)
        self.equip_button.clicked.connect(self._equip_item)
        self.unequip_button.clicked.connect(self._unequip_item)
    
    # Ajout d'une méthode pour gérer le clic sur le bouton de suppression
    def _on_drop_button_clicked(self):
        """Gère le clic sur le bouton de suppression en fonction de la sélection"""
        if self.selected_item:
            self._drop_item()
        elif self.selected_hardware:
            self._drop_hardware()
    
    def set_inventory_manager(self, inventory_manager: InventoryManager):
        """Définit le gestionnaire d'inventaire pour ce widget"""
        self.inventory_manager = inventory_manager
        self.load_inventory()
    
    def load_inventory(self):
        """Charge l'inventaire depuis le gestionnaire d'inventaire"""
        if not self.inventory_manager:
            return
        
        # Effacer les conteneurs d'objets et de matériel
        self._clear_items_container()
        self._clear_hardware_container()
        self._clear_equipment_containers()
        
        # Charger les objets
        self.load_items()
        
        # Charger le matériel
        self.load_hardware()
        
        # Charger l'équipement (armes, armures, implants)
        self.load_equipment()
        
        # Mettre à jour les slots équipés
        self._update_equipped_slots()
        self._update_equipped_gear()
        
        # Mettre à jour les statistiques
        self._update_stats()
    
    def load_items(self):
        """Charge les objets depuis le gestionnaire d'inventaire"""
        if not self.inventory_manager:
            return
        
        # Effacer les objets actuels
        self._clear_items_container()
        
        # Récupérer les objets de l'inventaire
        items = self.inventory_manager.get_items()
        
        # Ajouter chaque objet au conteneur
        layout = self.items_container.layout()
        for item_id, item in items.items():
            item_widget = ItemWidget(item, self.items_container)
            item_widget.item_id = item_id
            item_widget.clicked.connect(self._on_item_clicked)
            item_widget.double_clicked.connect(self._on_item_double_clicked)
            layout.addWidget(item_widget)
    
    def load_hardware(self):
        """Charge le matériel depuis le gestionnaire d'inventaire"""
        if not self.inventory_manager:
            return
        
        # Effacer le matériel actuel
        self._clear_hardware_container()
        
        # Récupérer le matériel de l'inventaire
        hardware_items = self.inventory_manager.get_hardware()
        
        # Ajouter chaque matériel au conteneur
        layout = self.hardware_container.layout()
        for hw_id, hardware in hardware_items.items():
            # Ignorer le matériel équipé (affiché séparément)
            is_equipped = False
            if hasattr(self.inventory_manager, "player") and hasattr(self.inventory_manager.player, "equipment"):
                for slot, equipped_id in self.inventory_manager.player.equipment.items():
                    if equipped_id == hw_id:
                        is_equipped = True
                        break
            
            # Si le matériel n'est pas équipé, l'ajouter à la liste
            if not is_equipped:
                hardware_widget = HardwareWidget(hardware, self.hardware_container)
                hardware_widget.hardware_id = hw_id
                hardware_widget.clicked.connect(self._on_hardware_clicked)
                hardware_widget.double_clicked.connect(self._equip_hardware)
                layout.addWidget(hardware_widget)
    
    def _init_ui(self):
        # Mise en page principale
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Onglets pour les différentes catégories
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Onglet "Objets"
        self.items_tab = QWidget()
        self.tabs.addTab(self.items_tab, "Objets")
        
        # Mise en page de l'onglet "Objets"
        self.items_layout = QVBoxLayout(self.items_tab)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(5)
        
        # Conteneur d'objets
        self.items_scroll = QScrollArea()
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.items_container = QWidget()
        self.items_flow_layout = FlowLayout(self.items_container)
        self.items_scroll.setWidget(self.items_container)
        
        self.items_layout.addWidget(self.items_scroll)
        
        # Onglet "Matériel"
        self.hardware_tab = QWidget()
        self.tabs.addTab(self.hardware_tab, "Matériel")
        
        # Mise en page de l'onglet "Matériel"
        self.hardware_layout = QVBoxLayout(self.hardware_tab)
        self.hardware_layout.setContentsMargins(0, 0, 0, 0)
        self.hardware_layout.setSpacing(10)
        
        # Équipement actif
        self.active_equipment_group = QGroupBox("Équipement actif")
        self.active_equipment_layout = QGridLayout(self.active_equipment_group)
        
        # Emplacements d'équipement (CPU, RAM, stockage, réseau, sécurité)
        self.equipment_slots = {
            "cpu": {"label": QLabel("CPU:"), "widget": QLabel("Aucun"), "equipped": None},
            "memory": {"label": QLabel("Mémoire:"), "widget": QLabel("Aucun"), "equipped": None},
            "storage": {"label": QLabel("Stockage:"), "widget": QLabel("Aucun"), "equipped": None},
            "network": {"label": QLabel("Réseau:"), "widget": QLabel("Aucun"), "equipped": None},
            "security": {"label": QLabel("Sécurité:"), "widget": QLabel("Aucun"), "equipped": None}
        }
        
        # Ajouter les emplacements d'équipement
        row = 0
        for slot_type, slot_data in self.equipment_slots.items():
            self.active_equipment_layout.addWidget(slot_data["label"], row, 0)
            self.active_equipment_layout.addWidget(slot_data["widget"], row, 1)
            row += 1
        
        self.hardware_layout.addWidget(self.active_equipment_group)
        
        # Statistiques de l'équipement
        self.stats_group = QGroupBox("Statistiques")
        self.stats_layout = QGridLayout(self.stats_group)
        
        # Statistiques (puissance de calcul, mémoire, stockage, bande passante, sécurité)
        self.stats = {
            "processing": {"label": QLabel("Puissance de calcul:"), "value": QLabel("0")},
            "memory": {"label": QLabel("Mémoire:"), "value": QLabel("0")},
            "storage": {"label": QLabel("Stockage:"), "value": QLabel("0")},
            "bandwidth": {"label": QLabel("Bande passante:"), "value": QLabel("0")},
            "security": {"label": QLabel("Sécurité:"), "value": QLabel("0")}
        }
        
        # Ajouter les statistiques
        row = 0
        for stat_type, stat_data in self.stats.items():
            self.stats_layout.addWidget(stat_data["label"], row, 0)
            self.stats_layout.addWidget(stat_data["value"], row, 1)
            row += 1
        
        self.hardware_layout.addWidget(self.stats_group)
        
        # Conteneur de matériel
        self.hardware_scroll = QScrollArea()
        self.hardware_scroll.setWidgetResizable(True)
        self.hardware_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hardware_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.hardware_container = QWidget()
        self.hardware_flow_layout = FlowLayout(self.hardware_container)
        self.hardware_scroll.setWidget(self.hardware_container)
        
        self.hardware_layout.addWidget(self.hardware_scroll)
        
        # Nouvel onglet "Équipement" pour les implants, armes et armures
        self.equipment_tab = QWidget()
        self.tabs.addTab(self.equipment_tab, "Équipement")
        
        # Mise en page de l'onglet "Équipement"
        self.equipment_layout = QVBoxLayout(self.equipment_tab)
        self.equipment_layout.setContentsMargins(0, 0, 0, 0)
        self.equipment_layout.setSpacing(10)
        
        # Splitter pour diviser l'écran entre équipement actif et disponible
        self.equipment_splitter = QSplitter(Qt.Orientation.Vertical)
        self.equipment_layout.addWidget(self.equipment_splitter)
        
        # Partie supérieure : Équipement actif (implants, armes, armures équipés)
        self.active_gear_widget = QWidget()
        self.active_gear_layout = QVBoxLayout(self.active_gear_widget)
        
        # Section des armes équipées
        self.weapons_group = QGroupBox("Armes équipées")
        self.weapons_layout = QGridLayout(self.weapons_group)
        
        # Emplacements d'armes (principale, secondaire)
        self.weapon_slots = {
            "primary": {"label": QLabel("Principale:"), "widget": QLabel("Aucune"), "equipped": None},
            "secondary": {"label": QLabel("Secondaire:"), "widget": QLabel("Aucune"), "equipped": None}
        }
        
        # Ajouter les emplacements d'armes
        row = 0
        for slot_type, slot_data in self.weapon_slots.items():
            self.weapons_layout.addWidget(slot_data["label"], row, 0)
            slot_data["widget"].setCursor(Qt.CursorShape.PointingHandCursor)
            slot_data["widget"].mousePressEvent = lambda event, slot=slot_type: self._on_equipped_weapon_clicked(slot)
            self.weapons_layout.addWidget(slot_data["widget"], row, 1)
            row += 1
        
        self.active_gear_layout.addWidget(self.weapons_group)
        
        # Section des armures équipées
        self.armor_group = QGroupBox("Armures équipées")
        self.armor_layout = QGridLayout(self.armor_group)
        
        # Emplacements d'armures (tête, torse, bras, jambes)
        self.armor_slots = {
            "head": {"label": QLabel("Tête:"), "widget": QLabel("Aucune"), "equipped": None},
            "torso": {"label": QLabel("Torse:"), "widget": QLabel("Aucune"), "equipped": None},
            "arms": {"label": QLabel("Bras:"), "widget": QLabel("Aucune"), "equipped": None},
            "legs": {"label": QLabel("Jambes:"), "widget": QLabel("Aucune"), "equipped": None}
        }
        
        # Ajouter les emplacements d'armures
        row = 0
        for slot_type, slot_data in self.armor_slots.items():
            self.armor_layout.addWidget(slot_data["label"], row, 0)
            slot_data["widget"].setCursor(Qt.CursorShape.PointingHandCursor)
            slot_data["widget"].mousePressEvent = lambda event, slot=slot_type: self._on_equipped_armor_clicked(slot)
            self.armor_layout.addWidget(slot_data["widget"], row, 1)
            row += 1
        
        self.active_gear_layout.addWidget(self.armor_group)
        
        # Section des implants équipés
        self.implants_group = QGroupBox("Implants installés")
        self.implants_layout = QGridLayout(self.implants_group)
        
        # Emplacements d'implants (cerveau, yeux, oreilles, bras, jambes, peau)
        self.implant_slots = {
            "brain": {"label": QLabel("Cerveau:"), "widget": QLabel("Aucun"), "equipped": None},
            "eyes": {"label": QLabel("Yeux:"), "widget": QLabel("Aucun"), "equipped": None},
            "ears": {"label": QLabel("Oreilles:"), "widget": QLabel("Aucun"), "equipped": None},
            "arms": {"label": QLabel("Bras:"), "widget": QLabel("Aucun"), "equipped": None},
            "legs": {"label": QLabel("Jambes:"), "widget": QLabel("Aucun"), "equipped": None},
            "skin": {"label": QLabel("Peau:"), "widget": QLabel("Aucun"), "equipped": None}
        }
        
        # Ajouter les emplacements d'implants
        row = 0
        for slot_type, slot_data in self.implant_slots.items():
            self.implants_layout.addWidget(slot_data["label"], row, 0)
            slot_data["widget"].setCursor(Qt.CursorShape.PointingHandCursor)
            slot_data["widget"].mousePressEvent = lambda event, slot=slot_type: self._on_equipped_implant_clicked(slot)
            self.implants_layout.addWidget(slot_data["widget"], row, 1)
            row += 1
        
        self.active_gear_layout.addWidget(self.implants_group)
        
        # Ajouter le widget d'équipement actif au splitter
        self.equipment_splitter.addWidget(self.active_gear_widget)
        
        # Partie inférieure : Équipement disponible dans l'inventaire
        self.available_gear_widget = QWidget()
        self.available_gear_layout = QVBoxLayout(self.available_gear_widget)
        
        # Onglets pour les différents types d'équipement disponible
        self.gear_tabs = QTabWidget()
        self.available_gear_layout.addWidget(self.gear_tabs)
        
        # Onglet pour les armes disponibles
        self.available_weapons_tab = QWidget()
        self.gear_tabs.addTab(self.available_weapons_tab, "Armes")
        
        self.available_weapons_layout = QVBoxLayout(self.available_weapons_tab)
        self.available_weapons_scroll = QScrollArea()
        self.available_weapons_scroll.setWidgetResizable(True)
        self.available_weapons_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.available_weapons_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.available_weapons_container = QWidget()
        self.available_weapons_flow_layout = FlowLayout(self.available_weapons_container)
        self.available_weapons_scroll.setWidget(self.available_weapons_container)
        
        self.available_weapons_layout.addWidget(self.available_weapons_scroll)
        
        # Onglet pour les armures disponibles
        self.available_armor_tab = QWidget()
        self.gear_tabs.addTab(self.available_armor_tab, "Armures")
        
        self.available_armor_layout = QVBoxLayout(self.available_armor_tab)
        self.available_armor_scroll = QScrollArea()
        self.available_armor_scroll.setWidgetResizable(True)
        self.available_armor_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.available_armor_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.available_armor_container = QWidget()
        self.available_armor_flow_layout = FlowLayout(self.available_armor_container)
        self.available_armor_scroll.setWidget(self.available_armor_container)
        
        self.available_armor_layout.addWidget(self.available_armor_scroll)
        
        # Onglet pour les implants disponibles
        self.available_implants_tab = QWidget()
        self.gear_tabs.addTab(self.available_implants_tab, "Implants")
        
        self.available_implants_layout = QVBoxLayout(self.available_implants_tab)
        self.available_implants_scroll = QScrollArea()
        self.available_implants_scroll.setWidgetResizable(True)
        self.available_implants_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.available_implants_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.available_implants_container = QWidget()
        self.available_implants_flow_layout = FlowLayout(self.available_implants_container)
        self.available_implants_scroll.setWidget(self.available_implants_container)
        
        self.available_implants_layout.addWidget(self.available_implants_scroll)
        
        # Ajouter le widget d'équipement disponible au splitter
        self.equipment_splitter.addWidget(self.available_gear_widget)
        
        # Définir les tailles initiales du splitter (40% pour l'équipement actif, 60% pour l'équipement disponible)
        self.equipment_splitter.setSizes([400, 600])
        
        # Panneau d'information
        self.info_panel = QGroupBox("Information")
        self.info_panel.setMinimumHeight(150)
        self.info_layout = QVBoxLayout(self.info_panel)
        
        # Titre de l'objet/matériel
        self.info_title = QLabel("Sélectionnez un objet pour voir ses détails")
        self.info_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.info_layout.addWidget(self.info_title)
        
        # Description de l'objet/matériel
        self.info_description = QLabel()
        self.info_description.setWordWrap(True)
        self.info_layout.addWidget(self.info_description)
        
        # Statistiques de l'objet/matériel
        self.info_stats = QLabel()
        self.info_layout.addWidget(self.info_stats)
        
        # Actions possibles (utiliser, équiper, jeter)
        self.actions_layout = QHBoxLayout()
        
        self.use_button = QPushButton("Utiliser")
        self.actions_layout.addWidget(self.use_button)
        
        self.equip_button = QPushButton("Équiper")
        self.actions_layout.addWidget(self.equip_button)
        
        self.unequip_button = QPushButton("Déséquiper")
        self.actions_layout.addWidget(self.unequip_button)
        
        self.drop_button = QPushButton("Jeter")
        self.actions_layout.addWidget(self.drop_button)
        
        self.info_layout.addLayout(self.actions_layout)
        
        self.main_layout.addWidget(self.info_panel)
        
        # Initialiser les boutons d'action (désactivés par défaut)
        self._update_action_buttons()
    
    def _clear_items_container(self):
        """Efface tous les widgets d'objets"""
        layout = self.items_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _clear_hardware_container(self):
        """Efface tous les widgets de matériel"""
        layout = self.hardware_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _clear_equipment_containers(self):
        """Efface tous les widgets d'équipement (armes, armures, implants)"""
        # Effacer les armes disponibles
        layout = self.available_weapons_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Effacer les armures disponibles
        layout = self.available_armor_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Effacer les implants disponibles
        layout = self.available_implants_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def load_equipment(self):
        """Charge l'équipement (armes, armures, implants) depuis le gestionnaire d'inventaire"""
        if not self.inventory_manager:
            return
        
        # Effacer les conteneurs d'équipement
        self._clear_equipment_containers()
        
        # Récupérer les objets de l'inventaire
        items = self.inventory_manager.get_items()
        
        # Trier les objets par type
        weapons = []
        armors = []
        implants = []
        
        for item_id, item in items.items():
            item_type = item.type.lower() if hasattr(item, 'type') else "unknown"
            
            # Vérifier si l'objet est déjà équipé
            is_equipped = self._is_item_equipped(item)
            
            if item_type == "weapon" and not is_equipped:
                weapons.append(item)
            elif item_type == "armor" and not is_equipped:
                armors.append(item)
            elif item_type == "implant" and not is_equipped:
                implants.append(item)
        
        # Ajouter les armes disponibles
        for weapon in weapons:
            item_widget = QLabel(weapon.name)
            item_widget.setStyleSheet("border: 1px solid #333; padding: 3px; background-color: #222;")
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            item_widget.mousePressEvent = lambda event, item=weapon: self._on_equipment_item_clicked(item)
            item_widget.mouseDoubleClickEvent = lambda event, item=weapon: self._on_equipment_item_double_clicked(item)
            self.available_weapons_container.layout().addWidget(item_widget)
        
        # Ajouter les armures disponibles
        for armor in armors:
            item_widget = QLabel(armor.name)
            item_widget.setStyleSheet("border: 1px solid #333; padding: 3px; background-color: #222;")
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            item_widget.mousePressEvent = lambda event, item=armor: self._on_equipment_item_clicked(item)
            item_widget.mouseDoubleClickEvent = lambda event, item=armor: self._on_equipment_item_double_clicked(item)
            self.available_armor_container.layout().addWidget(item_widget)
        
        # Ajouter les implants disponibles
        for implant in implants:
            item_widget = QLabel(implant.name)
            item_widget.setStyleSheet("border: 1px solid #333; padding: 3px; background-color: #222;")
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            item_widget.mousePressEvent = lambda event, item=implant: self._on_equipment_item_clicked(item)
            item_widget.mouseDoubleClickEvent = lambda event, item=implant: self._on_equipment_item_double_clicked(item)
            self.available_implants_container.layout().addWidget(item_widget)
    
    def _update_equipped_slots(self):
        """Met à jour l'affichage des slots équipés"""
        if not self.inventory_manager or not hasattr(self.inventory_manager, "player"):
            return
        
        # Effacer tous les widgets des slots
        for slot_name, slot_frame in self.equipment_slots.items():
            layout = slot_frame.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
        
        # Ajouter les composants équipés aux slots correspondants
        player = self.inventory_manager.player
        if hasattr(player, "equipment"):
            for slot_name, hardware_id in player.equipment.items():
                if hardware_id and slot_name in self.equipment_slots:
                    hardware = self.inventory_manager.hardware.get(hardware_id)
                    if hardware:
                        slot_frame = self.equipment_slots[slot_name]
                        hardware_widget = HardwareWidget(hardware, slot_frame)
                        hardware_widget.setFixedSize(45, 45)
                        hardware_widget.clicked.connect(self._on_equipped_hardware_clicked)
                        slot_frame.layout().addWidget(hardware_widget)
    
    def _update_stats(self):
        """Met à jour l'affichage des statistiques"""
        if not self.inventory_manager:
            return
        
        # Récupérer les statistiques du matériel équipé
        stats = self.inventory_manager.get_hardware_stats()
        
        # Mettre à jour les labels de statistiques
        for stat_name, value in stats.items():
            if stat_name in self.stats:
                self.stats[stat_name]["value"].setText(f"{value}")
    
    def _on_item_clicked(self, item):
        """Gère le clic sur un objet"""
        self.selected_item = item
        self.selected_hardware = None
        self._update_action_buttons()
        self._update_item_info(item)
    
    def _on_hardware_clicked(self, hardware):
        """Gère le clic sur un matériel"""
        self.selected_hardware = hardware
        self.selected_item = None
        self._update_action_buttons()
        self._update_hardware_info(hardware)
    
    def _on_equipped_hardware_clicked(self, hardware):
        """Gère le clic sur un matériel équipé"""
        self.selected_hardware = hardware
        self.selected_item = None
        self._update_action_buttons()
        self._update_hardware_info(hardware)
        # Ajouter un bouton pour déséquiper
        self.unequip_button.setVisible(True)
    
    def _on_item_double_clicked(self, item):
        """Gère le double-clic sur un objet (utilisation)"""
        if self.inventory_manager:
            # Récupérer l'ID de l'objet
            item_id = item.id if hasattr(item, 'id') else None
            
            if not item_id:
                return
                
            # Vérifier si l'inventory_manager a la méthode use_item
            if hasattr(self.inventory_manager, 'use_item'):
                result = self.inventory_manager.use_item(item_id)
                # Émettre le signal d'utilisation d'objet
                self.item_used.emit(item_id, result)
                # Rafraîchir l'interface
                self.load_items()
                self.load_equipment()
                self._update_equipped_gear()
                self._clear_selection()
            else:
                # Afficher un message d'erreur
                QMessageBox.warning(
                    self, 
                    "Opération non supportée", 
                    "L'utilisation d'objets n'est pas supportée dans ce contexte."
                )
    
    def _update_action_buttons(self):
        """Met à jour l'état des boutons d'action en fonction de la sélection actuelle"""
        # Aucun objet/matériel sélectionné
        if not self.selected_item and not self.selected_hardware:
            self.use_button.setEnabled(False)
            self.equip_button.setEnabled(False)
            self.unequip_button.setEnabled(False)
            self.drop_button.setEnabled(False)
            return
        
        # Un objet est sélectionné
        if self.selected_item:
            item_type = self.selected_item.type.lower() if hasattr(self.selected_item, 'type') else "unknown"
            
            # Activer/désactiver les boutons en fonction du type d'objet
            if item_type in ["weapon", "armor", "implant"]:
                # Vérifier si l'objet est équipé
                is_equipped = self._is_item_equipped(self.selected_item)
                
                self.use_button.setEnabled(not is_equipped)  # "Utiliser" pour équiper
                self.equip_button.setEnabled(not is_equipped)  # Équiper
                self.unequip_button.setEnabled(is_equipped)  # Déséquiper
                self.drop_button.setEnabled(not is_equipped)  # Ne peut pas jeter si équipé
            else:
                # Objets normaux
                self.use_button.setEnabled(True)
                self.equip_button.setEnabled(False)
                self.unequip_button.setEnabled(False)
                self.drop_button.setEnabled(True)
        
        # Un matériel est sélectionné
        if self.selected_hardware:
            self.use_button.setEnabled(False)
            
            # Vérifier si le matériel est équipé
            is_equipped = False
            for slot in self.equipment_slots.values():
                if slot["equipped"] == self.selected_hardware:
                    is_equipped = True
                    break
            
            # Activer/désactiver les boutons en fonction de l'état
            self.equip_button.setEnabled(not is_equipped)
            self.unequip_button.setEnabled(is_equipped)
            self.drop_button.setEnabled(not is_equipped)
    
    def _is_item_equipped(self, item):
        """Vérifie si un objet est équipé"""
        if not hasattr(self.inventory_manager, "player"):
            return False
        
        item_type = item.type.lower() if hasattr(item, 'type') else "unknown"
        item_id = item.id if hasattr(item, 'id') else None
        
        if not item_id:
            return False
        
        # Vérifier si c'est une arme équipée
        if item_type == "weapon" and hasattr(self.inventory_manager.player, "equipment"):
            # Trouver dans quel slot l'arme est équipée
            for slot in ["primary", "secondary"]:
                if hasattr(self.inventory_manager.player.equipment, slot):
                    equipped_id = getattr(self.inventory_manager.player.equipment, slot)
                    if equipped_id == item_id:
                        return True
        
        # Vérifier si c'est une armure équipée
        elif item_type == "armor" and hasattr(self.inventory_manager.player, "equipment"):
            # Trouver dans quel slot l'armure est équipée
            for slot in ["head", "torso", "arms", "legs"]:
                if hasattr(self.inventory_manager.player.equipment, slot):
                    equipped_id = getattr(self.inventory_manager.player.equipment, slot)
                    if equipped_id == item_id:
                        return True
        
        # Vérifier si c'est un implant installé
        elif item_type == "implant" and hasattr(self.inventory_manager.player, "implants"):
            # Trouver dans quel slot l'implant est installé
            for slot, equipped_id in self.inventory_manager.player.implants.items():
                if equipped_id == item_id:
                    return True
        
        return False
    
    def _unequip_weapon(self, slot):
        """Déséquipe une arme"""
        if not self.inventory_manager or not hasattr(self.inventory_manager, "player") or not hasattr(self.inventory_manager.player, "equipment"):
            return
        
        # Vérifier si une arme est équipée dans cet emplacement
        if hasattr(self.inventory_manager.player.equipment, slot):
            weapon_id = getattr(self.inventory_manager.player.equipment, slot)
            if weapon_id:
                # Réinitialiser l'emplacement
                setattr(self.inventory_manager.player.equipment, slot, None)
                
                # Mettre à jour l'interface
                self.load_equipment()
                self._update_equipped_gear()
                self._clear_selection()
    
    def _unequip_armor(self, slot):
        """Déséquipe une armure"""
        if not self.inventory_manager or not hasattr(self.inventory_manager, "player") or not hasattr(self.inventory_manager.player, "equipment"):
            return
        
        # Vérifier si une armure est équipée dans cet emplacement
        if hasattr(self.inventory_manager.player.equipment, slot):
            armor_id = getattr(self.inventory_manager.player.equipment, slot)
            if armor_id:
                # Réinitialiser l'emplacement
                setattr(self.inventory_manager.player.equipment, slot, None)
                
                # Mettre à jour l'interface
                self.load_equipment()
                self._update_equipped_gear()
                self._clear_selection()
    
    def _unequip_implant(self, slot):
        """Déséquipe un implant"""
        if not self.inventory_manager or not hasattr(self.inventory_manager, "player") or not hasattr(self.inventory_manager.player, "implants"):
            return
        
        # Vérifier si un implant est installé dans cet emplacement
        if slot in self.inventory_manager.player.implants:
            # Retirer l'implant
            del self.inventory_manager.player.implants[slot]
            
            # Mettre à jour l'interface
            self.load_equipment()
            self._update_equipped_gear()
            self._clear_selection()
    
    def _use_item(self):
        """Utilise l'objet sélectionné"""
        if not self.selected_item or not self.inventory_manager:
            return
        
        # Vérifier si l'inventory_manager a la méthode use_item
        if hasattr(self.inventory_manager, 'use_item'):
            # Récupérer l'ID de l'objet
            item_id = self.selected_item.id if hasattr(self.selected_item, 'id') else None
            
            if item_id:
                result = self.inventory_manager.use_item(item_id)
                # Émettre le signal d'utilisation d'objet
                self.item_used.emit(item_id, result)
                # Rafraîchir l'interface
                self.load_items()
                self.load_equipment()
                self._update_equipped_gear()
                self._clear_selection()
        else:
            # Afficher un message d'erreur
            QMessageBox.warning(
                self, 
                "Opération non supportée", 
                "L'utilisation d'objets n'est pas supportée dans ce contexte."
            )
    
    def _drop_item(self):
        """Jette l'objet sélectionné"""
        if not self.selected_item or not self.inventory_manager:
            return
            
        # Récupérer le nom et l'ID de l'objet
        item_name = self.selected_item.name if hasattr(self.selected_item, 'name') else "Objet inconnu"
        item_id = self.selected_item.id if hasattr(self.selected_item, 'id') else None
        
        if not item_id:
            return
            
        # Confirmer l'action
        confirm = QMessageBox.question(
            self, 
            "Confirmer", 
            f"Êtes-vous sûr de vouloir jeter {item_name} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Vérifier si l'objet est équipé
            if self._is_item_equipped(self.selected_item):
                QMessageBox.warning(
                    self,
                    "Impossible de jeter",
                    "Vous ne pouvez pas jeter un objet équipé. Déséquipez-le d'abord."
                )
                return
                
            if hasattr(self.inventory_manager, 'remove_item'):
                self.inventory_manager.remove_item(item_id)
                # Émettre le signal d'objet jeté
                self.item_dropped.emit(item_id)
                # Rafraîchir l'interface
                self.load_items()
                self.load_equipment()
                self._clear_selection()
            else:
                # Afficher un message d'erreur
                QMessageBox.warning(
                    self, 
                    "Opération non supportée", 
                    "La suppression d'objets n'est pas supportée dans ce contexte."
                )
    
    def _drop_hardware(self):
        """Jette le matériel sélectionné"""
        if not self.selected_hardware or not self.inventory_manager:
            return
            
        # Confirmer l'action
        confirm = QMessageBox.question(
            self, 
            "Confirmer", 
            f"Êtes-vous sûr de vouloir jeter {self.selected_hardware.name} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.inventory_manager.remove_hardware(self.selected_hardware.hardware_id)
            # Émettre le signal de matériel jeté
            self.hardware_dropped.emit(self.selected_hardware.hardware_id)
            # Rafraîchir l'interface
            self.load_hardware()
            self._update_equipped_slots()
            self._update_stats()
            self._clear_selection()
    
    def _equip_hardware(self):
        """Équipe le matériel sélectionné"""
        if not self.selected_hardware or not self.inventory_manager:
            return
            
        if hasattr(self.selected_hardware, "slot") and self.selected_hardware.slot:
            success = self.inventory_manager.equip_hardware(self.selected_hardware.hardware_id)
            
            if success:
                # Émettre le signal de matériel équipé
                self.hardware_equipped.emit(self.selected_hardware.hardware_id, self.selected_hardware.slot)
                # Rafraîchir l'interface
                self._update_equipped_slots()
                self._update_stats()
                self._update_action_buttons()
            else:
                QMessageBox.warning(
                    self, 
                    "Impossible d'équiper", 
                    f"Impossible d'équiper {self.selected_hardware.name}. Vérifiez les conditions requises."
                )
    
    def _unequip_item(self):
        """Déséquipe l'objet sélectionné"""
        if not self.selected_item or not self.inventory_manager or not hasattr(self.inventory_manager.player, 'active_equipment'):
            return
        
        # Trouver dans quel slot l'objet est équipé
        item_id = self.selected_item.id if hasattr(self.selected_item, 'id') else None
        if not item_id:
            return
            
        # Parcourir l'équipement actif pour trouver l'objet
        found_slot = None
        for slot, equipped_item in self.inventory_manager.player.active_equipment.items():
            if hasattr(equipped_item, 'id') and equipped_item.id == item_id:
                found_slot = slot
                break
                
        if not found_slot:
            QMessageBox.warning(
                self, 
                "Impossible de déséquiper", 
                f"{self.selected_item.name} n'est pas équipé actuellement."
            )
            return
            
        # Déséquiper l'objet
        success = self.inventory_manager.player.unequip_item(found_slot)
        if success:
            # Émettre le signal de déséquipement
            self.item_used.emit(item_id, {"action": "unequip", "slot": found_slot})
            # Rafraîchir l'interface
            self.load_equipment()
            self._update_equipped_gear()
            self._update_action_buttons()
        else:
            QMessageBox.warning(
                self, 
                "Impossible de déséquiper", 
                f"Impossible de déséquiper {self.selected_item.name}."
            )
    
    def _equip_item(self):
        """Équipe l'objet sélectionné"""
        if not self.selected_item or not self.inventory_manager:
            return
        
        item_type = self.selected_item.type.lower() if hasattr(self.selected_item, 'type') else "unknown"
        item_id = self.selected_item.id if hasattr(self.selected_item, 'id') else None
        
        if not item_id:
            return
            
        # Vérifier si l'inventory_manager a la méthode equip_item
        if hasattr(self.inventory_manager, 'equip_item'):
            # Déterminer le slot selon le type d'objet
            slot = None
            
            # Pour les armes et armures, on peut utiliser des slots spécifiques
            if item_type == "weapon":
                slot = "primary"  # Par défaut pour les armes
            elif item_type == "armor":
                # Utiliser les propriétés de l'objet pour déterminer le slot si disponible
                if hasattr(self.selected_item, 'properties') and 'slot' in self.selected_item.properties:
                    slot = self.selected_item.properties['slot']
                else:
                    slot = "torso"  # Par défaut pour les armures
            
            # Équiper l'objet avec le slot déterminé
            result = self.inventory_manager.equip_item(item_id, slot)
            
            if result:
                # Émettre le signal d'équipement
                self.item_used.emit(item_id, {"action": "equip", "slot": slot or "default"})
                # Rafraîchir l'interface
                self.load_equipment()
                self._update_equipped_gear()
                self._update_action_buttons()
            else:
                QMessageBox.warning(
                    self, 
                    "Impossible d'équiper", 
                    f"Impossible d'équiper {self.selected_item.name}. Vérifiez les conditions requises."
                )
        else:
            # Afficher un message d'erreur
            QMessageBox.warning(
                self, 
                "Opération non supportée", 
                "L'équipement d'objets n'est pas supporté dans ce contexte."
            )
    
    def _update_item_info(self, item):
        """Affiche les informations d'un objet dans le panneau d'information"""
        if not item:
            self.info_panel.setVisible(False)
            return
            
        self.info_panel.setVisible(True)
        self.info_title.setText(item.name)
        self.info_description.setText(item.description)
        
        # Afficher les statistiques de l'objet
        stats_text = f"Type: {item.type.capitalize()}\n"
        stats_text += f"Valeur: {item.value} ¥\n"
        
        if hasattr(item, 'quantity') and item.quantity > 1:
            stats_text += f"Quantité: {item.quantity}\n"
        
        # Ajouter d'autres statistiques si disponibles
        if hasattr(item, 'stats') and item.stats:
            for stat_name, stat_value in item.stats.items():
                stats_text += f"{stat_name.capitalize()}: {stat_value}\n"
        
        self.info_stats.setText(stats_text)
    
    def _update_hardware_info(self, hardware):
        """Affiche les informations d'un matériel dans le panneau d'information"""
        if not hardware:
            self.info_panel.setVisible(False)
            return
            
        self.info_panel.setVisible(True)
        self.info_title.setText(hardware.name)
        self.info_description.setText(hardware.description)
        
        # Afficher les statistiques du matériel
        stats_text = f"Type: {hardware.type.capitalize()}\n"
        stats_text += f"Slot: {hardware.slot.capitalize()}\n"
        stats_text += f"Rareté: {hardware.rarity.capitalize()}\n"
        stats_text += f"Valeur: {hardware.value} ¥\n"
        
        # Ajouter les bonus de statistiques
        for stat_name, stat_value in hardware.stats.items():
            if stat_value != 0:
                stats_text += f"{stat_name.capitalize()}: +{stat_value}\n"
        
        self.info_stats.setText(stats_text)
    
    def _update_action_buttons(self):
        """Met à jour l'état des boutons d'action en fonction de la sélection actuelle"""
        # Masquer tous les boutons par défaut
        self.use_button.setVisible(False)
        self.drop_button.setVisible(False)
        self.equip_button.setVisible(False)
        self.unequip_button.setVisible(False)
        
        # Si un objet est sélectionné
        if self.selected_item:
            item_type = self.selected_item.type.lower() if hasattr(self.selected_item, 'type') else "unknown"
            
            # Activer/désactiver les boutons en fonction du type d'objet
            if item_type in ["weapon", "armor", "implant"]:
                # Vérifier si l'objet est équipé
                is_equipped = self._is_item_equipped(self.selected_item)
                
                self.use_button.setVisible(not is_equipped)  # "Utiliser" pour équiper
                self.equip_button.setVisible(not is_equipped)  # Équiper
                self.unequip_button.setVisible(is_equipped)  # Déséquiper
                self.drop_button.setVisible(not is_equipped)  # Ne peut pas jeter si équipé
            else:
                # Objets normaux
                self.use_button.setVisible(True)
                self.equip_button.setVisible(False)
                self.unequip_button.setVisible(False)
                self.drop_button.setVisible(True)
        
        # Si un matériel est sélectionné
        elif self.selected_hardware:
            self.drop_button.setVisible(True)
            
            # Vérifier si le matériel est équipé
            is_equipped = False
            for slot in self.equipment_slots.values():
                if slot["equipped"] == self.selected_hardware:
                    is_equipped = True
                    break
            
            # Afficher le bouton approprié (équiper ou déséquiper)
            if is_equipped:
                self.unequip_button.setVisible(True)
            else:
                self.equip_button.setVisible(True)
    
    def _clear_selection(self):
        """Efface la sélection actuelle"""
        self.selected_item = None
        self.selected_hardware = None
        self.info_panel.setVisible(False)
        self._update_action_buttons()
    
    def _update_equipped_gear(self):
        """Met à jour l'affichage des équipements (armes, armures, implants) équipés"""
        if not self.inventory_manager or not hasattr(self.inventory_manager, "player"):
            return
        
        # Mettre à jour les armes équipées
        if hasattr(self.inventory_manager.player, "equipment"):
            # Réinitialiser les slots d'armes
            for slot_name, slot_data in self.weapon_slots.items():
                slot_data["widget"].setText("Aucune")
                slot_data["equipped"] = None
            
            # Parcourir l'équipement du joueur
            equipment = self.inventory_manager.player.equipment
            
            # Arme principale
            if hasattr(equipment, "primary") and equipment.primary:
                weapon_id = equipment.primary
                weapon = self.inventory_manager.get_item(weapon_id)
                if weapon:
                    self.weapon_slots["primary"]["widget"].setText(weapon.name)
                    self.weapon_slots["primary"]["equipped"] = weapon
            
            # Arme secondaire
            if hasattr(equipment, "secondary") and equipment.secondary:
                weapon_id = equipment.secondary
                weapon = self.inventory_manager.get_item(weapon_id)
                if weapon:
                    self.weapon_slots["secondary"]["widget"].setText(weapon.name)
                    self.weapon_slots["secondary"]["equipped"] = weapon
        
        # Mettre à jour les armures équipées
        if hasattr(self.inventory_manager.player, "equipment"):
            # Réinitialiser les slots d'armures
            for slot_name, slot_data in self.armor_slots.items():
                slot_data["widget"].setText("Aucune")
                slot_data["equipped"] = None
            
            # Parcourir l'équipement du joueur
            equipment = self.inventory_manager.player.equipment
            
            # Armure de tête
            if hasattr(equipment, "head") and equipment.head:
                armor_id = equipment.head
                armor = self.inventory_manager.get_item(armor_id)
                if armor:
                    self.armor_slots["head"]["widget"].setText(armor.name)
                    self.armor_slots["head"]["equipped"] = armor
            
            # Armure de torse
            if hasattr(equipment, "torso") and equipment.torso:
                armor_id = equipment.torso
                armor = self.inventory_manager.get_item(armor_id)
                if armor:
                    self.armor_slots["torso"]["widget"].setText(armor.name)
                    self.armor_slots["torso"]["equipped"] = armor
            
            # Armure de bras
            if hasattr(equipment, "arms") and equipment.arms:
                armor_id = equipment.arms
                armor = self.inventory_manager.get_item(armor_id)
                if armor:
                    self.armor_slots["arms"]["widget"].setText(armor.name)
                    self.armor_slots["arms"]["equipped"] = armor
            
            # Armure de jambes
            if hasattr(equipment, "legs") and equipment.legs:
                armor_id = equipment.legs
                armor = self.inventory_manager.get_item(armor_id)
                if armor:
                    self.armor_slots["legs"]["widget"].setText(armor.name)
                    self.armor_slots["legs"]["equipped"] = armor
        
        # Mettre à jour les implants équipés
        if hasattr(self.inventory_manager.player, "implants"):
            # Réinitialiser les slots d'implants
            for slot_name, slot_data in self.implant_slots.items():
                slot_data["widget"].setText("Aucun")
                slot_data["equipped"] = None
            
            # Parcourir les implants du joueur
            implants = self.inventory_manager.player.implants
            
            # Mettre à jour chaque emplacement d'implant
            for slot_name, implant_id in implants.items():
                if slot_name in self.implant_slots:
                    implant = self.inventory_manager.get_item(implant_id)
                    if implant:
                        self.implant_slots[slot_name]["widget"].setText(implant.name)
                        self.implant_slots[slot_name]["equipped"] = implant
    
    def _on_equipped_weapon_clicked(self, slot):
        """Gère le clic sur une arme équipée"""
        if slot in self.weapon_slots:
            equipped_weapon = self.weapon_slots[slot]["equipped"]
            if equipped_weapon:
                self.selected_item = equipped_weapon
                self.selected_hardware = None
                self._update_item_info(equipped_weapon)
                self._update_action_buttons()
                
                # Déséquiper l'arme si clic droit
                if hasattr(QApplication.instance(), 'mouseButtons') and QApplication.instance().mouseButtons() == Qt.MouseButton.RightButton:
                    self._unequip_weapon(slot)
    
    def _on_equipped_armor_clicked(self, slot):
        """Gère le clic sur une armure équipée"""
        if slot in self.armor_slots:
            equipped_armor = self.armor_slots[slot]["equipped"]
            if equipped_armor:
                self.selected_item = equipped_armor
                self.selected_hardware = None
                self._update_item_info(equipped_armor)
                self._update_action_buttons()
                
                # Déséquiper l'armure si clic droit
                if hasattr(QApplication.instance(), 'mouseButtons') and QApplication.instance().mouseButtons() == Qt.MouseButton.RightButton:
                    self._unequip_armor(slot)
    
    def _on_equipped_implant_clicked(self, slot):
        """Gère le clic sur un implant équipé"""
        if slot in self.implant_slots:
            equipped_implant = self.implant_slots[slot]["equipped"]
            if equipped_implant:
                self.selected_item = equipped_implant
                self.selected_hardware = None
                self._update_item_info(equipped_implant)
                self._update_action_buttons()
                
                # Déséquiper l'implant si clic droit
                if hasattr(QApplication.instance(), 'mouseButtons') and QApplication.instance().mouseButtons() == Qt.MouseButton.RightButton:
                    self._unequip_implant(slot)
    
    def _on_equipment_item_clicked(self, item):
        """Gère le clic sur un équipement disponible"""
        self.selected_item = item
        self.selected_hardware = None
        self._update_item_info(item)
        self._update_action_buttons()
    
    def _on_equipment_item_double_clicked(self, item):
        """Gère le double-clic sur un équipement disponible (équipe automatiquement)"""
        self.selected_item = item
        self.selected_hardware = None
        self._update_item_info(item)
        self._update_action_buttons()
        
        # Équiper automatiquement l'objet
        self._use_item()


class InventoryScreen(QWidget):
    """Écran d'inventaire pour le jeu YakTaa, incluant les objets et le matériel"""
    
    # Signaux
    inventory_closed = pyqtSignal()
    item_used = pyqtSignal(str, dict)  # ID de l'objet et résultat de l'utilisation
    item_dropped = pyqtSignal(str)     # ID de l'objet jeté
    hardware_equipped = pyqtSignal(str, str)  # ID du matériel et type de slot
    hardware_unequipped = pyqtSignal(str)     # ID du matériel déséquipé
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_manager = None
        self.initUI()
    
    def initUI(self):
        """Initialise l'interface utilisateur de l'écran d'inventaire"""
        # Configuration de base
        self.setWindowTitle("Inventaire")
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Toolbar en haut
        toolbar = QToolBar()
        close_action = QAction("Fermer", self)
        close_action.triggered.connect(self._on_close)
        toolbar.addAction(close_action)
        
        # Ajouter des séparateurs et des labels pour améliorer l'apparence
        toolbar.addSeparator()
        title_label = QLabel("INVENTAIRE")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        toolbar.addWidget(title_label)
        
        main_layout.addWidget(toolbar)
        
        # Créer le widget d'inventaire
        self.inventory_widget = InventoryWidget(self)
        main_layout.addWidget(self.inventory_widget)
        
        # Connecter les signaux
        self.inventory_widget.item_used.connect(self._on_item_used)
        self.inventory_widget.item_dropped.connect(self._on_item_dropped)
        self.inventory_widget.hardware_equipped.connect(self._on_hardware_equipped)
        self.inventory_widget.hardware_unequipped.connect(self._on_hardware_unequipped)
        
        # Appliquer des styles CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QToolBar {
                background-color: #333333;
                border: none;
                padding: 5px;
            }
            QToolButton, QAction {
                color: #E0E0E0;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
            }
            QTabBar::tab {
                background-color: #333333;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                border-bottom: 2px solid #00A0E4;
            }
            QTabBar::tab:!selected {
                background-color: #2D2D2D;
                border-bottom: none;
            }
        """)
    
    def set_inventory_manager(self, inventory_manager):
        """Définit le gestionnaire d'inventaire à utiliser"""
        self.inventory_manager = inventory_manager
        self.inventory_widget.set_inventory_manager(inventory_manager)
    
    def _on_close(self):
        """Gère la fermeture de l'écran d'inventaire"""
        self.inventory_closed.emit()
        self.hide()
    
    def _on_item_used(self, item_id, result):
        """Relaye le signal d'utilisation d'objet"""
        self.item_used.emit(item_id, result)
    
    def _on_item_dropped(self, item_id):
        """Relaye le signal d'objet jeté"""
        self.item_dropped.emit(item_id)
    
    def _on_hardware_equipped(self, hardware_id, slot):
        """Relaye le signal de matériel équipé"""
        self.hardware_equipped.emit(hardware_id, slot)
    
    def _on_hardware_unequipped(self, hardware_id):
        """Relaye le signal de matériel déséquipé"""
        self.hardware_unequipped.emit(hardware_id)


class FlowLayout(QLayout):
    """Layout qui arrange les widgets de gauche à droite et de haut en bas"""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
        
        self.items = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.items.append(item)
    
    def count(self):
        return len(self.items)
    
    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
            
        size += QSize(2 * self.contentsMargins().left(), 2 * self.contentsMargins().top())
        return size
    
    def _doLayout(self, rect, testOnly):
        x = rect.x() + self.contentsMargins().left()
        y = rect.y() + self.contentsMargins().top()
        lineHeight = 0
        
        for item in self.items:
            widget = item.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            spaceY = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical
            )
            
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x() + self.contentsMargins().left()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
                
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
            
        return y + lineHeight - rect.y() + self.contentsMargins().bottom()
