"""
Module pour l'affichage et l'interaction avec les PNJ dans YakTaa
"""

import logging
from typing import Optional, Dict, Any, List, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QDialog, QGraphicsItem,
    QGraphicsPixmapItem, QGraphicsEllipseItem, QToolTip
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor, QIcon, QFont

from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.NPCWidget")

class NPCNode(QGraphicsEllipseItem):
    """
    Représentation graphique d'un PNJ sur la carte
    """
    
    def __init__(self, npc_id: str, npc_data: Dict[str, Any], parent=None):
        """
        Initialise un nœud de PNJ
        
        Args:
            npc_id: Identifiant unique du PNJ
            npc_data: Données du PNJ
            parent: Élément parent
        """
        size = 15  # Taille du nœud
        super().__init__(-size/2, -size/2, size, size, parent)
        
        self.npc_id = npc_id
        self.npc_data = npc_data
        self.setPos(npc_data.get("position", (0, 0)))
        
        # Déterminer la couleur en fonction du type de PNJ
        npc_type = npc_data.get("type", "neutral")
        if npc_type == "hostile":
            color = QColor("#FF3333")  # Rouge pour hostile
        elif npc_type == "friendly":
            color = QColor("#33FF33")  # Vert pour amical
        elif npc_type == "vendor":
            color = QColor("#FFCC33")  # Orange pour vendeur
        elif npc_type == "quest_giver":
            color = QColor("#3399FF")  # Bleu pour donneur de quête
        else:
            color = QColor("#CCCCCC")  # Gris pour neutre
        
        # Style du nœud
        self.setPen(QPen(Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(color))
        
        # Étiquette avec le nom du PNJ
        self.label = QGraphicsTextItem(npc_data.get("name", "PNJ inconnu"), self)
        self.label.setPos(-self.label.boundingRect().width()/2, size/2 + 5)
        self.label.setDefaultTextColor(QColor("#FFFFFF"))
        
        # Rendre l'élément interactif
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        # Variable pour stocker la fonction de callback
        self.on_click_callback = None
    
    def hoverEnterEvent(self, event):
        """Gère l'entrée du curseur sur le nœud"""
        # Effet de survol
        self.setPen(QPen(Qt.PenStyle.SolidLine))
        self.setScale(1.2)
        
        # Afficher une infobulle avec les détails du PNJ
        tooltip_text = f"<b>{self.npc_data.get('name', 'PNJ inconnu')}</b><br>"
        tooltip_text += f"Type: {self.npc_data.get('type', 'inconnu').capitalize()}<br>"
        
        if "description" in self.npc_data:
            tooltip_text += f"{self.npc_data['description']}<br>"
        
        QToolTip.showText(event.screenPos(), tooltip_text)
        
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Gère la sortie du curseur du nœud"""
        self.setPen(QPen(Qt.PenStyle.SolidLine))
        self.setScale(1.0)
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Gère le clic sur le nœud"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.on_click_callback:
                self.on_click_callback(self.npc_id)
        super().mousePressEvent(event)
    
    def set_click_callback(self, callback: Callable[[str], None]):
        """Définit la fonction à appeler lors d'un clic sur le PNJ"""
        self.on_click_callback = callback


class NPCDetailsDialog(QDialog):
    """
    Fenêtre de dialogue affichant les détails d'un PNJ et permettant d'interagir avec lui
    """
    
    def __init__(self, game: Game, npc_id: str, npc_data: Dict[str, Any], parent=None):
        """
        Initialise la fenêtre de détails du PNJ
        
        Args:
            game: Instance du jeu
            npc_id: Identifiant du PNJ
            npc_data: Données du PNJ
            parent: Widget parent
        """
        super().__init__(parent)
        self.game = game
        self.npc_id = npc_id
        self.npc_data = npc_data
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"PNJ - {npc_data.get('name', 'Inconnu')}")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #CCCCCC;
            }
            QLabel {
                color: #CCCCCC;
            }
            QLabel#npc_name {
                color: #00CCFF;
                font-size: 16pt;
                font-weight: bold;
            }
            QFrame {
                background-color: #1A1A1A;
                border-radius: 4px;
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
            QPushButton#attack_button {
                background-color: #500000;
                color: #FF3333;
                border: 1px solid #FF3333;
            }
            QPushButton#attack_button:hover {
                background-color: #700000;
                color: #FF5555;
                border: 1px solid #FF5555;
            }
        """)
        
        # Créer l'interface
        self._create_ui()
    
    def _create_ui(self):
        """Crée l'interface utilisateur de la fenêtre"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # En-tête avec nom et type
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        npc_avatar = QLabel()
        # Essayer de charger l'avatar du PNJ, ou utiliser une image par défaut
        avatar_path = self.npc_data.get("avatar_path", ":/assets/images/default_npc.png")
        try:
            pixmap = QPixmap(avatar_path)
            if pixmap.isNull():
                pixmap = QPixmap(":/assets/images/default_npc.png")
        except:
            pixmap = QPixmap(":/assets/images/default_npc.png")
        
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        npc_avatar.setPixmap(pixmap)
        
        npc_name = QLabel(self.npc_data.get("name", "PNJ inconnu"))
        npc_name.setObjectName("npc_name")
        
        npc_type = self.npc_data.get("type", "neutral")
        npc_type_label = QLabel(f"Type: {npc_type.capitalize()}")
        
        header_info = QVBoxLayout()
        header_info.addWidget(npc_name)
        header_info.addWidget(npc_type_label)
        
        header_layout.addWidget(npc_avatar)
        header_layout.addLayout(header_info, 1)
        
        # Description
        description_frame = QFrame()
        description_layout = QVBoxLayout(description_frame)
        
        description_title = QLabel("Description")
        description_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        description_text = self.npc_data.get("description", "Aucune information disponible.")
        description_content = QLabel(description_text)
        description_content.setWordWrap(True)
        
        description_layout.addWidget(description_title)
        description_layout.addWidget(description_content)
        
        # Boutons d'action
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        
        # Bouton d'attaque
        attack_button = QPushButton("Attaquer")
        attack_button.setObjectName("attack_button")
        attack_button.setIcon(QIcon(":/assets/icons/attack.png"))
        attack_button.clicked.connect(self._on_attack)
        
        # Bouton de dialogue
        talk_button = QPushButton("Parler")
        talk_button.setIcon(QIcon(":/assets/icons/talk.png"))
        talk_button.clicked.connect(self._on_talk)
        
        # Bouton de commerce (pour les vendeurs)
        trade_button = QPushButton("Commercer")
        trade_button.setIcon(QIcon(":/assets/icons/trade.png"))
        trade_button.clicked.connect(self._on_trade)
        
        # N'afficher le bouton de commerce que pour les vendeurs
        if npc_type != "vendor":
            trade_button.setVisible(False)
        
        # Bouton pour missions (pour les donneurs de quête)
        quest_button = QPushButton("Missions")
        quest_button.setIcon(QIcon(":/assets/icons/quest.png"))
        quest_button.clicked.connect(self._on_quest)
        
        # N'afficher le bouton de mission que pour les donneurs de quête
        if npc_type != "quest_giver":
            quest_button.setVisible(False)
        
        # Ajouter les boutons au layout
        actions_layout.addWidget(attack_button)
        actions_layout.addWidget(talk_button)
        actions_layout.addWidget(trade_button)
        actions_layout.addWidget(quest_button)
        
        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        
        # Ajouter toutes les sections au layout principal
        main_layout.addWidget(header_frame)
        main_layout.addWidget(description_frame, 1)  # Stretch factor
        main_layout.addWidget(actions_frame)
        main_layout.addWidget(close_button)
    
    def _on_attack(self):
        """Gère l'action d'attaque du PNJ"""
        logger.info(f"Attaque du PNJ {self.npc_id}")
        
        if self.game:
            # Lancer le combat
            success = self.game.player_attack_npc(self.npc_id)
            
            if success:
                # Fermer la fenêtre de dialogue
                self.accept()
            else:
                logger.warning(f"Échec du démarrage du combat avec le PNJ {self.npc_id}")
        else:
            logger.error("Impossible d'attaquer le PNJ: pas d'instance de jeu disponible")
    
    def _on_talk(self):
        """Gère l'action de dialogue avec le PNJ"""
        logger.info(f"Dialogue avec le PNJ {self.npc_id}")
        # TODO: Implémenter le système de dialogue
    
    def _on_trade(self):
        """Gère l'action de commerce avec le PNJ"""
        logger.info(f"Commerce avec le PNJ {self.npc_id}")
        # TODO: Ouvrir la boutique du PNJ
    
    def _on_quest(self):
        """Gère l'action de prise de quête avec le PNJ"""
        logger.info(f"Interaction de quête avec le PNJ {self.npc_id}")
        # TODO: Afficher les quêtes disponibles


class NPCManager:
    """
    Gestionnaire des PNJ dans le jeu
    """
    
    def __init__(self, game: Game):
        """
        Initialise le gestionnaire de PNJ
        
        Args:
            game: Instance du jeu
        """
        self.game = game
        self.npcs = {}  # Dictionnaire des PNJ chargés (id -> données)
        self.npc_nodes = {}  # Nœuds de PNJ pour l'affichage sur la carte
        
        logger.info("Gestionnaire de PNJ initialisé")
    
    def load_npcs_for_location(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Charge les PNJ pour un lieu spécifique
        
        Args:
            location_id: Identifiant du lieu
            
        Returns:
            Liste des PNJ chargés
        """
        # Réinitialiser les PNJ
        self.npcs = {}
        
        # TODO: Charger les PNJ depuis la base de données
        # Pour l'instant, on génère des PNJ de test
        self._generate_test_npcs(location_id)
        
        logger.info(f"{len(self.npcs)} PNJ chargés pour le lieu {location_id}")
        
        return list(self.npcs.values())
    
    def _generate_test_npcs(self, location_id: str):
        """
        Génère des PNJ de test pour un lieu
        
        Args:
            location_id: Identifiant du lieu
        """
        import random
        
        # Types de PNJ possibles
        npc_types = ["neutral", "hostile", "friendly", "vendor", "quest_giver"]
        
        # Noms aléatoires
        first_names = ["Alex", "Kim", "Jordan", "Casey", "Riley", "Taylor", "Morgan", "Jamie", "Sam", "Avery"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        
        # Générer entre 3 et 7 PNJ
        num_npcs = random.randint(3, 7)
        
        for i in range(num_npcs):
            npc_id = f"npc_{location_id}_{i}"
            
            # Type aléatoire avec une préférence pour les neutres et amicaux
            npc_type = random.choices(
                npc_types, 
                weights=[0.4, 0.2, 0.2, 0.1, 0.1], 
                k=1
            )[0]
            
            # Nom aléatoire
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Position aléatoire dans un rayon raisonnable
            x = random.randint(-200, 200)
            y = random.randint(-200, 200)
            
            # Données du PNJ
            npc_data = {
                "id": npc_id,
                "name": name,
                "type": npc_type,
                "position": (x, y),
                "location_id": location_id,
                "description": f"Un{'' if npc_type == 'hostile' else 'e'} {npc_type} habitant{'' if npc_type == 'hostile' else 'e'} de la région."
            }
            
            # Ajouter des données spécifiques selon le type
            if npc_type == "hostile":
                npc_data["hostility"] = random.randint(50, 100)
                npc_data["description"] = "Une personne à l'air menaçant. Semble prêt à attaquer au moindre prétexte."
            elif npc_type == "vendor":
                npc_data["shop_type"] = random.choice(["weapons", "implants", "electronics", "general"])
                npc_data["description"] = f"Un marchand spécialisé dans les {npc_data['shop_type']}."
            elif npc_type == "quest_giver":
                npc_data["quest_ids"] = [f"quest_{random.randint(1000, 9999)}" for _ in range(random.randint(1, 3))]
                npc_data["description"] = "Cette personne semble avoir des opportunités de travail à offrir."
            
            # Ajouter le PNJ à la liste
            self.npcs[npc_id] = npc_data
    
    def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'un PNJ par son identifiant
        
        Args:
            npc_id: Identifiant du PNJ
            
        Returns:
            Données du PNJ ou None si non trouvé
        """
        return self.npcs.get(npc_id)
    
    def on_npc_clicked(self, npc_id: str, parent_widget: QWidget = None):
        """
        Gère le clic sur un PNJ
        
        Args:
            npc_id: Identifiant du PNJ
            parent_widget: Widget parent pour le dialogue
        """
        npc_data = self.get_npc(npc_id)
        if not npc_data:
            logger.warning(f"PNJ {npc_id} non trouvé")
            return
            
        logger.info(f"Clic sur le PNJ {npc_id} ({npc_data.get('name', 'Inconnu')})")
        
        # Afficher la fenêtre de détails du PNJ
        dialog = NPCDetailsDialog(self.game, npc_id, npc_data, parent_widget)
        dialog.exec()
        
    def create_npc_nodes(self, scene):
        """
        Crée les nœuds graphiques pour tous les PNJ
        
        Args:
            scene: Scène graphique où ajouter les nœuds
        """
        # Supprimer les anciens nœuds s'il y en a
        for node in self.npc_nodes.values():
            scene.removeItem(node)
        self.npc_nodes = {}
        
        # Créer les nouveaux nœuds
        for npc_id, npc_data in self.npcs.items():
            node = NPCNode(npc_id, npc_data)
            node.set_click_callback(self.on_npc_clicked)
            scene.addItem(node)
            self.npc_nodes[npc_id] = node
        
        logger.info(f"{len(self.npc_nodes)} nœuds de PNJ créés")
