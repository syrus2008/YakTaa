"""
Écran de boutique pour YakTaa.
Permet d'afficher l'interface des boutiques dans le jeu.
"""

import logging
from typing import Dict, List, Optional, Tuple, Callable

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QStackedWidget, QSplitter, QFrame, QGraphicsOpacityEffect, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QBrush, QLinearGradient

from yaktaa.ui.utils import load_stylesheet, get_font
from yaktaa.items.item import Item
from yaktaa.items.shop import Shop
from yaktaa.ui.widgets.shop_widget import ShopWidget  
from yaktaa.ui.widgets.simple_shop_selector import SimpleShopSelector

from yaktaa.items.shop_manager import ShopManager
from .base_screen import BaseScreen

# Configuration du logging
logger = logging.getLogger(__name__)

class ShopScreen(BaseScreen):
    """Écran principal pour l'interface des boutiques."""
    
    # Signaux
    back_to_game = pyqtSignal()
    shop_closed = pyqtSignal()  # Signal émis lorsque l'écran de boutique est fermé
    item_purchased = pyqtSignal(str, str, int)  # item_id, shop_id, price
    item_sold = pyqtSignal(str, str, int)  # item_id, shop_id, price
    update_player_credits = pyqtSignal(int)
    
    def __init__(self, game=None, parent=None):
        """
        Initialise l'écran de boutique.
        
        Args:
            game: Instance du jeu principal (contient shop_manager, player, etc.)
            parent: Widget parent
        """
        # Appel du constructeur parent avec les bons paramètres
        # Utiliser None comme premier argument si game est None pour éviter les erreurs
        super().__init__(game if game is not None else None, parent)
        
        # Si game n'était pas None mais a été passé au constructeur parent,
        # ne pas le réassigner ici pour éviter la duplication
        if not hasattr(self, 'game') or self.game is None:
            self.game = game
            
        self.shop_manager = getattr(game, 'shop_manager', None)
        self.player_data = {'credits': 1000}  # Valeurs par défaut
        
        if hasattr(game, 'player') and game.player:
            self.player_data = {
                'credits': getattr(game.player, 'credits', 1000),
                'inventory': getattr(game.player, 'inventory', None)
            }
        
        self.current_shop_id = None
        
        # Interface - Ne pas appeler setup_ui() ici, utiliser _init_ui() à la place
        # qui est appelé par le constructeur parent
        
        # Connecter les signaux internes
        self.back_to_game.connect(self.shop_closed.emit)
        self.update_player_credits.connect(self.update_credits_display)
    
    def _init_ui(self):
        """Surcharge de la méthode _init_ui de BaseScreen."""
        # Utiliser le layout déjà créé par BaseScreen
        self.main_layout = self.layout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Widget principal empilé (pour les transitions)
        self.stacked_widget = QStackedWidget()
        
        # Écran de sélection de boutique - Utilisation du nouveau SimpleShopSelector
        self.shop_selector = SimpleShopSelector()
        self.shop_selector.shop_selected.connect(self.open_shop)
        self.shop_selector.back_pressed.connect(self.back_to_game.emit)
        self.stacked_widget.addWidget(self.shop_selector)
        
        # Écran de boutique (sera ajouté dynamiquement)
        self.shop_screen_container = QWidget()
        # Créer le layout pour le conteneur sans l'assigner directement
        self.shop_screen_layout = QVBoxLayout()
        self.shop_screen_container.setLayout(self.shop_screen_layout)
        self.stacked_widget.addWidget(self.shop_screen_container)
        
        # Ajouter le widget empilé au layout principal
        self.main_layout.addWidget(self.stacked_widget)
        
        # Appliquer le style
        self.setStyleSheet(load_stylesheet("shop_screen"))
    
    def display_shops(self, shops: List[Shop]):
        """
        Affiche la liste des boutiques disponibles.
        
        Args:
            shops: Liste des boutiques à afficher
        """
        logger.debug(f"display_shops appelé avec {len(shops)} boutiques")
        
        # Mettre à jour les crédits du joueur dans l'interface
        credits = self.player_data.get('credits', 0)
        
        # Définir les boutiques dans le sélecteur
        self.shop_selector.set_shops(shops)
        
        # Retourner à l'écran de sélection de boutique
        self.stacked_widget.setCurrentIndex(0)
        
        logger.debug("Liste des boutiques mise à jour")
    
    def open_shop(self, shop_id: str):
        """
        Ouvre une boutique spécifique.
        
        Args:
            shop_id: Identifiant de la boutique à ouvrir
        """
        try:
            if not self.shop_manager:
                logger.error("ShopManager non disponible")
                return
            
            # Récupérer la boutique
            shop = self.shop_manager.get_shop(shop_id)
            if not shop:
                logger.error(f"Boutique non trouvée: {shop_id}")
                return
            
            # Stocker l'ID de la boutique actuelle au lieu de l'objet boutique
            self.current_shop_id = shop_id
            self._clear_shop_screen()
            
            # Extraire les informations dont ShopWidget a besoin
            player_credits = self.player_data.get('credits', 0)
            player_inventory = None
            player_location_id = None
            
            if hasattr(self.game, 'player') and self.game.player:
                # Vérifier si l'inventaire est un objet InventoryManager ou une liste
                player_inventory_obj = getattr(self.game.player, 'inventory', None)
                player_credits = getattr(self.game.player, 'credits', 0)
                
                # S'assurer que player_inventory est un InventoryManager et non une liste
                if player_inventory_obj is not None:
                    from yaktaa.items.inventory_manager import InventoryManager
                    
                    # Si c'est déjà un InventoryManager, l'utiliser tel quel
                    if isinstance(player_inventory_obj, InventoryManager):
                        player_inventory = player_inventory_obj
                        logger.debug("Utilisé directement l'objet InventoryManager existant")
                    else:
                        # Si c'est une liste, créer un InventoryAdapter qui simule un InventoryManager
                        logger.warning("L'inventaire du joueur est une liste et non un InventoryManager")
                        
                        # Créer un adaptateur simple pour l'inventaire
                        class InventoryAdapter:
                            def __init__(self, items_list):
                                self.items = items_list if isinstance(items_list, list) else []
                            
                            def add_item(self, item):
                                self.items.append(item)
                                return True
                            
                            def remove_item(self, item_index):
                                if 0 <= item_index < len(self.items):
                                    self.items.pop(item_index)
                                    return True
                                return False
                        
                        player_inventory = InventoryAdapter(player_inventory_obj)
                        logger.debug(f"Créé un adaptateur pour {len(player_inventory.items)} objets d'inventaire")
            
            # Obtenir l'emplacement actuel du joueur
            if hasattr(self.game, 'world_manager') and self.game.world_manager:
                player_location_id = getattr(self.game.world_manager, 'current_location_id', None)
                logger.debug(f"Location ID du joueur récupéré: {player_location_id}")
            
            # Créer un widget de boutique avec les bons paramètres
            logger.debug(f"Création du widget de boutique pour {shop.name} avec {player_credits} crédits, location: {player_location_id}")
            shop_widget = ShopWidget(shop, player_inventory, player_credits, player_reputation=0, player_location_id=player_location_id)
            
            # Connecter les signaux du widget
            shop_widget.exit_shop.connect(self._return_to_shop_selection)
            
            # Stocker l'ID de façon sûre pour la lambda
            current_shop_id = shop_id  # Copie locale stable pour la lambda
            shop_widget.transaction_completed.connect(
                lambda item_id, amount: self._handle_transaction(item_id, amount, current_shop_id)
            )
            
            # Ajouter le widget au layout
            self.shop_screen_layout.addWidget(shop_widget)
            
            # Passer à l'écran de boutique
            self.stacked_widget.setCurrentIndex(1)
            logger.info(f"Boutique ouverte: {shop.name} (ID: {shop_id})")
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de la boutique {shop_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _clear_shop_screen(self):
        """Nettoie l'écran de boutique."""
        # Supprimer tous les widgets du layout de l'écran de boutique
        while self.shop_screen_layout.count():
            item = self.shop_screen_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                # Récursion pour nettoyer les sous-layouts
                self._clear_layout(item.layout())
    
    def _clear_layout(self, layout):
        """Nettoie récursivement un layout et tous ses enfants."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self._clear_layout(item.layout())
    
    def clear_shops(self):
        """
        Nettoie la liste des boutiques dans le sélecteur.
        Cette méthode est appelée par MainWindow._show_shop_screen().
        """
        logger.debug("clear_shops appelé")
        self.shop_selector.clear_shops()
    
    def set_location_name(self, location_name):
        """
        Définit le nom de l'emplacement actuel dans le sélecteur.
        Cette méthode est appelée par MainWindow._show_shop_screen().
        
        Args:
            location_name: Nom de l'emplacement
        """
        logger.debug(f"set_location_name appelé avec {location_name}")
        self.shop_selector.set_location_name(location_name)
    
    def add_shop(self, shop):
        """
        Ajoute une boutique au sélecteur.
        Cette méthode est appelée par MainWindow._show_shop_screen().
        
        Args:
            shop: Objet boutique à ajouter
        """
        logger.debug(f"add_shop appelé avec {shop.name if hasattr(shop, 'name') else shop}")
        self.shop_selector.add_shop(shop)
    
    def _return_to_shop_selection(self):
        """
        Retourne à l'écran de sélection de boutique.
        """
        self.stacked_widget.setCurrentIndex(0)
        logger.debug("Retour à l'écran de sélection de boutique")
        
        # Si le joueur existe, mettre à jour les crédits dans l'interface
        if hasattr(self.game, 'player') and self.game.player:
            self.player_data['credits'] = self.game.player.credits
    
    def _handle_transaction(self, item_id, amount, shop_id):
        """
        Gère une transaction (achat ou vente).
        
        Args:
            item_id: Identifiant de l'objet
            amount: Prix de la transaction
            shop_id: Identifiant de la boutique
        """
        # Pour détecter l'achat vs vente: 
        # - Achat  = montant négatif (dépense)
        # - Vente = montant positif (gain)
        if amount < 0:
            # C'est un achat
            logger.debug(f"[SHOP] Transaction détectée: ACHAT item {item_id} pour {abs(amount)} crédits")
            self.item_purchased.emit(item_id, shop_id, abs(amount))
        else:
            # C'est une vente
            logger.debug(f"[SHOP] Transaction détectée: VENTE item {item_id} pour {amount} crédits")
            self.item_sold.emit(item_id, shop_id, amount)
        
        # Mettre à jour l'affichage des crédits
        if hasattr(self.game, 'player') and self.game.player:
            self.update_player_credits.emit(self.game.player.credits)
    
    def update_credits_display(self, credits: int):
        """
        Met à jour l'affichage des crédits du joueur.
        
        Args:
            credits: Nouveau montant de crédits
        """
        logger.debug(f"[SHOP] Mise à jour des crédits affichés: {credits}")
        
        # Enregistrer la nouvelle valeur
        self.player_data['credits'] = credits
        
        # Si un ShopWidget est actif, mettre à jour ses crédits
        shop_widget = None
        for i in range(self.shop_screen_layout.count()):
            widget = self.shop_screen_layout.itemAt(i).widget()
            if isinstance(widget, ShopWidget):
                shop_widget = widget
                break
        
        if shop_widget:
            logger.debug("[SHOP] Mise à jour des crédits dans le widget de boutique")
            shop_widget.update_credits(credits)
    
    def refresh_shops(self):
        """Rafraîchit la liste des boutiques disponibles."""
        if not self.shop_manager:
            logger.warning("Impossible de rafraîchir les boutiques : ShopManager non disponible")
            return
        
        # Obtenir l'emplacement actuel du joueur
        current_location = None
        if hasattr(self.game, 'world_manager'):
            current_location = self.game.world_manager.current_location_id
        
        if not current_location:
            logger.warning("Impossible de déterminer l'emplacement actuel du joueur")
            current_location = 'default'
        
        # Obtenir l'ID de la ville correspondant à l'emplacement
        city_id = self.shop_manager.get_city_id_from_location(current_location)
        
        # Récupérer les boutiques disponibles dans cette ville
        shops = self.shop_manager.get_shops_by_location(city_id)
        logger.info(f"{len(shops)} boutiques trouvées à {city_id}")
        
        # Afficher les boutiques
        self.display_shops(shops)
    
    def paintEvent(self, event):
        """Personnalisation de l'arrière-plan avec effet cyberpunk."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Créer un dégradé de fond
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(20, 20, 30))
        gradient.setColorAt(1, QColor(10, 10, 20))
        
        # Appliquer le dégradé
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Dessiner une grille de lignes horizontales bleutées
        painter.setPen(QColor(0, 100, 200, 40))
        line_spacing = 20
        for y in range(0, self.height(), line_spacing):
            painter.drawLine(0, y, self.width(), y)
        
        # Dessiner quelques lignes verticales plus claires
        painter.setPen(QColor(0, 150, 255, 15))
        for x in range(0, self.width(), 100):
            painter.drawLine(x, 0, x, self.height())
        
        # Ajouter de petits points brillants aléatoires (fixes pour une session)
        painter.setPen(QColor(0, 200, 255, 100))
        for i in range(50):
            x = (i * 23) % self.width()
            y = (i * 29) % self.height()
            painter.drawPoint(x, y)
