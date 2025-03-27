"""
Module pour le widget de fiche de personnage du jeu YakTaa
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, 
    QSplitter, QFrame, QTabWidget, QGridLayout,
    QScrollArea, QToolBar, QMenu, QToolButton,
    QSizePolicy, QSpacerItem, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QTextEdit, QProgressBar, QGroupBox,
    QSlider, QDial
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QRect, QDateTime, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QBrush, QPainter, QPen, QRadialGradient, QLinearGradient, QAction

from yaktaa.ui.widgets.custom_widgets import QRadialBar
from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.CharacterSheet")

# Classe personnalisée pour les barres de progression circulaires
# Comme QRadialBar n'existe pas dans PyQt6, nous créons notre propre widget
class RadialProgressBar(QWidget):
    """Widget personnalisé pour afficher une barre de progression circulaire"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Valeurs par défaut
        self._min = 0
        self._max = 100
        self._value = 25
        
        # Apparence
        self._bg_color = QColor("#333333")
        self._progress_color = QColor("#00AA00")
        self._text_color = QColor("#FFFFFF")
        
        # Taille minimale
        self.setMinimumSize(80, 80)
    
    def setRange(self, min_val: int, max_val: int) -> None:
        """Définit la plage de valeurs"""
        self._min = min_val
        self._max = max_val
        self.update()
    
    def setValue(self, value: int) -> None:
        """Définit la valeur actuelle"""
        self._value = max(self._min, min(self._max, value))
        self.update()
    
    def setProgressColor(self, color: QColor) -> None:
        """Définit la couleur de la progression"""
        self._progress_color = color
        self.update()
    
    def paintEvent(self, event):
        """Dessine le widget"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calcul des dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Rectangle extérieur
        rect = QRect(int((width - size) / 2), int((height - size) / 2), size, size)
        
        # Calcul de l'angle
        start_angle = 90 * 16  # 90 degrés en unités QPainter (1 degré = 16 unités)
        span_angle = -int(360 * 16 * (self._value - self._min) / (self._max - self._min))
        
        # Dessin du fond
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg_color)
        painter.drawEllipse(rect.adjusted(5, 5, -5, -5))
        
        # Dessin de la progression
        painter.setBrush(self._progress_color)
        painter.drawPie(rect.adjusted(5, 5, -5, -5), start_angle, span_angle)
        
        # Dessin du cercle central
        painter.setBrush(QColor("#222222"))
        painter.drawEllipse(rect.adjusted(size // 4, size // 4, -size // 4, -size // 4))
        
        # Dessin du texte
        painter.setPen(self._text_color)
        painter.setFont(QFont("Arial", size // 8, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}")


class CharacterAttribute:
    """Classe représentant un attribut de personnage"""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 description: str, 
                 value: int = 1,
                 max_value: int = 10,
                 icon: Optional[str] = None):
        """Initialise un attribut de personnage"""
        self.id = id
        self.name = name
        self.description = description
        self.value = value
        self.max_value = max_value
        self.icon = icon


class CharacterSkill:
    """Classe représentant une compétence de personnage"""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 description: str, 
                 level: int = 0,
                 max_level: int = 5,
                 category: str = "general",
                 attributes: List[str] = None,
                 icon: Optional[str] = None,
                 unlocked: bool = True,
                 prerequisites: List[Dict[str, Any]] = None):
        """Initialise une compétence de personnage"""
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_level = max_level
        self.category = category
        self.attributes = attributes or []
        self.icon = icon
        self.unlocked = unlocked
        self.prerequisites = prerequisites or []


class CharacterPerk:
    """Classe représentant un avantage de personnage"""
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 description: str, 
                 active: bool = False,
                 category: str = "general",
                 icon: Optional[str] = None,
                 unlocked: bool = False,
                 prerequisites: List[Dict[str, Any]] = None,
                 effects: List[Dict[str, Any]] = None):
        """Initialise un avantage de personnage"""
        self.id = id
        self.name = name
        self.description = description
        self.active = active
        self.category = category
        self.icon = icon
        self.unlocked = unlocked
        self.prerequisites = prerequisites or []
        self.effects = effects or []


class Character:
    """Classe représentant un personnage joueur"""
    
    def __init__(self, 
                 name: str, 
                 level: int = 1,
                 experience: int = 0,
                 money: int = 100,
                 health: int = 100,
                 max_health: int = 100,
                 energy: int = 100,
                 max_energy: int = 100,
                 reputation: Dict[str, int] = None,
                 attributes: Dict[str, CharacterAttribute] = None,
                 skills: Dict[str, CharacterSkill] = None,
                 perks: Dict[str, CharacterPerk] = None,
                 biography: str = ""):
        """Initialise un personnage"""
        self.name = name
        self.level = level
        self.experience = experience
        self.money = money
        self.health = health
        self.max_health = max_health
        self.energy = energy
        self.max_energy = max_energy
        self.reputation = reputation or {}
        self.attributes = attributes or {}
        self.skills = skills or {}
        self.perks = perks or {}
        self.biography = biography
        
        # Points disponibles
        self.attribute_points = 0
        self.skill_points = 0
        self.perk_points = 0
    
    def get_experience_for_level(self, level: int) -> int:
        """Retourne l'expérience nécessaire pour atteindre un niveau"""
        # Formule simple: 100 * niveau^2
        return 100 * level * level
    
    def get_experience_for_next_level(self) -> int:
        """Retourne l'expérience nécessaire pour le prochain niveau"""
        return self.get_experience_for_level(self.level + 1)
    
    def get_experience_progress(self) -> float:
        """Retourne la progression vers le prochain niveau (0-1)"""
        current_level_exp = self.get_experience_for_level(self.level)
        next_level_exp = self.get_experience_for_level(self.level + 1)
        
        if next_level_exp == current_level_exp:
            return 1.0
        
        return (self.experience - current_level_exp) / (next_level_exp - current_level_exp)
    
    def add_experience(self, amount: int) -> bool:
        """Ajoute de l'expérience au personnage et gère la montée de niveau"""
        self.experience += amount
        
        # Vérification de la montée de niveau
        level_up = False
        while self.experience >= self.get_experience_for_next_level():
            self.level += 1
            
            # Attribution de points
            self.attribute_points += 1
            self.skill_points += 2
            
            # Tous les 5 niveaux, un point d'avantage
            if self.level % 5 == 0:
                self.perk_points += 1
            
            level_up = True
        
        return level_up
    
    def get_skill_level(self, skill_id: str) -> int:
        """Retourne le niveau d'une compétence"""
        if skill_id in self.skills:
            return self.skills[skill_id].level
        return 0
    
    def get_attribute_value(self, attribute_id: str) -> int:
        """Retourne la valeur d'un attribut"""
        if attribute_id in self.attributes:
            return self.attributes[attribute_id].value
        return 0
    
    def has_perk(self, perk_id: str) -> bool:
        """Vérifie si le personnage possède un avantage"""
        return perk_id in self.perks and self.perks[perk_id].active
    
    def can_upgrade_skill(self, skill_id: str) -> bool:
        """Vérifie si une compétence peut être améliorée"""
        if skill_id not in self.skills:
            return False
        
        skill = self.skills[skill_id]
        
        # Vérification du niveau maximum
        if skill.level >= skill.max_level:
            return False
        
        # Vérification des points disponibles
        if self.skill_points <= 0:
            return False
        
        # Vérification des prérequis
        for prereq in skill.prerequisites:
            prereq_id = prereq.get("id")
            prereq_level = prereq.get("level", 1)
            
            if prereq_id in self.skills:
                if self.skills[prereq_id].level < prereq_level:
                    return False
            else:
                return False
        
        return True
    
    def upgrade_skill(self, skill_id: str) -> bool:
        """Améliore une compétence"""
        if not self.can_upgrade_skill(skill_id):
            return False
        
        self.skills[skill_id].level += 1
        self.skill_points -= 1
        return True
    
    def can_upgrade_attribute(self, attribute_id: str) -> bool:
        """Vérifie si un attribut peut être amélioré"""
        if attribute_id not in self.attributes:
            return False
        
        attribute = self.attributes[attribute_id]
        
        # Vérification de la valeur maximale
        if attribute.value >= attribute.max_value:
            return False
        
        # Vérification des points disponibles
        if self.attribute_points <= 0:
            return False
        
        return True
    
    def upgrade_attribute(self, attribute_id: str) -> bool:
        """Améliore un attribut"""
        if not self.can_upgrade_attribute(attribute_id):
            return False
        
        self.attributes[attribute_id].value += 1
        self.attribute_points -= 1
        return True
    
    def can_unlock_perk(self, perk_id: str) -> bool:
        """Vérifie si un avantage peut être débloqué"""
        if perk_id not in self.perks:
            return False
        
        perk = self.perks[perk_id]
        
        # Vérification si déjà débloqué
        if perk.active:
            return False
        
        # Vérification des points disponibles
        if self.perk_points <= 0:
            return False
        
        # Vérification des prérequis
        for prereq in perk.prerequisites:
            prereq_type = prereq.get("type")
            prereq_id = prereq.get("id")
            prereq_value = prereq.get("value", 1)
            
            if prereq_type == "skill":
                if self.get_skill_level(prereq_id) < prereq_value:
                    return False
            elif prereq_type == "attribute":
                if self.get_attribute_value(prereq_id) < prereq_value:
                    return False
            elif prereq_type == "perk":
                if not self.has_perk(prereq_id):
                    return False
            elif prereq_type == "level":
                if self.level < prereq_value:
                    return False
        
        return True
    
    def unlock_perk(self, perk_id: str) -> bool:
        """Débloque un avantage"""
        if not self.can_unlock_perk(perk_id):
            return False
        
        self.perks[perk_id].active = True
        self.perk_points -= 1
        return True


class CharacterSheetWidget(QWidget):
    """Widget de fiche de personnage pour YakTaa"""
    
    # Signaux
    attribute_upgraded = pyqtSignal(str)
    skill_upgraded = pyqtSignal(str)
    perk_unlocked = pyqtSignal(str)
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise le widget de fiche de personnage"""
        super().__init__(parent)
        
        # Référence au jeu
        self.game = game
        
        # Personnage (exemple pour le développement)
        self._create_example_character()
        
        # Mise en page
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Panneau supérieur avec les informations générales
        self._create_header_panel()
        
        # Onglets pour les différentes sections
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #222222;
            }
            
            QTabBar::tab {
                background-color: #333333;
                color: #CCCCCC;
                padding: 5px 10px;
                border: 1px solid #444444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #222222;
                color: #FFFFFF;
            }
            
            QTabBar::tab:hover {
                background-color: #444444;
            }
        """)
        
        # Onglet Attributs
        self.attributes_tab = self._create_attributes_tab()
        self.tabs.addTab(self.attributes_tab, "Attributs")
        
        # Onglet Compétences
        self.skills_tab = self._create_skills_tab()
        self.tabs.addTab(self.skills_tab, "Compétences")
        
        # Onglet Avantages
        self.perks_tab = self._create_perks_tab()
        self.tabs.addTab(self.perks_tab, "Avantages")
        
        # Onglet Réputation
        self.reputation_tab = self._create_reputation_tab()
        self.tabs.addTab(self.reputation_tab, "Réputation")
        
        # Onglet Biographie
        self.biography_tab = self._create_biography_tab()
        self.tabs.addTab(self.biography_tab, "Biographie")
        
        self.layout.addWidget(self.tabs)
        
        logger.info("Widget de fiche de personnage initialisé")
    
    def _create_example_character(self) -> None:
        """Crée un personnage d'exemple pour le développement"""
        # Attributs
        attributes = {
            "str": CharacterAttribute("str", "Force", "Force physique et capacité à porter des objets lourds", 3),
            "dex": CharacterAttribute("dex", "Dextérité", "Agilité, réflexes et précision", 4),
            "con": CharacterAttribute("con", "Constitution", "Endurance, résistance aux dégâts et aux poisons", 3),
            "int": CharacterAttribute("int", "Intelligence", "Capacité d'apprentissage et de résolution de problèmes", 5),
            "wis": CharacterAttribute("wis", "Sagesse", "Intuition, perception et volonté", 2),
            "cha": CharacterAttribute("cha", "Charisme", "Capacité à influencer les autres", 3)
        }
        
        # Compétences
        skills = {
            "hacking": CharacterSkill("hacking", "Hacking", "Capacité à infiltrer des systèmes informatiques", 3, category="tech", attributes=["int"]),
            "electronics": CharacterSkill("electronics", "Électronique", "Connaissance des systèmes électroniques", 2, category="tech", attributes=["int", "dex"]),
            "stealth": CharacterSkill("stealth", "Discrétion", "Capacité à se déplacer sans être détecté", 1, category="physical", attributes=["dex"]),
            "persuasion": CharacterSkill("persuasion", "Persuasion", "Capacité à convaincre les autres", 2, category="social", attributes=["cha"]),
            "investigation": CharacterSkill("investigation", "Investigation", "Capacité à trouver des indices et des informations", 2, category="mental", attributes=["int", "wis"]),
            "combat": CharacterSkill("combat", "Combat", "Capacité au combat rapproché", 1, category="physical", attributes=["str", "dex"]),
            "firearms": CharacterSkill("firearms", "Armes à feu", "Maîtrise des armes à feu", 0, category="physical", attributes=["dex"]),
            "network": CharacterSkill("network", "Réseaux", "Connaissance des réseaux informatiques", 3, category="tech", attributes=["int"]),
            "cryptography": CharacterSkill("cryptography", "Cryptographie", "Capacité à coder et décoder des messages", 2, category="tech", attributes=["int"]),
            "security": CharacterSkill("security", "Sécurité", "Connaissance des systèmes de sécurité", 1, category="tech", attributes=["int", "wis"])
        }
        
        # Avantages
        perks = {
            "fast_hacker": CharacterPerk("fast_hacker", "Hacker rapide", "Réduit le temps nécessaire pour pirater un système", True, category="tech"),
            "ghost": CharacterPerk("ghost", "Fantôme", "Laisse moins de traces lors d'intrusions", False, category="tech"),
            "silver_tongue": CharacterPerk("silver_tongue", "Langue d'argent", "Bonus aux jets de persuasion", True, category="social"),
            "eagle_eye": CharacterPerk("eagle_eye", "Œil d'aigle", "Meilleure perception des détails", False, category="mental"),
            "tough": CharacterPerk("tough", "Robuste", "Augmente la résistance aux dégâts", False, category="physical"),
            "quick_reflexes": CharacterPerk("quick_reflexes", "Réflexes rapides", "Améliore la vitesse de réaction", False, category="physical"),
            "master_coder": CharacterPerk("master_coder", "Maître codeur", "Peut écrire des scripts plus complexes", False, category="tech"),
            "network_specialist": CharacterPerk("network_specialist", "Spécialiste réseau", "Bonus lors de l'analyse de réseaux", True, category="tech")
        }
        
        # Réputation
        reputation = {
            "hackers": 75,  # Amical
            "corps": 30,    # Neutre
            "police": 15,   # Hostile
            "underground": 60  # Amical
        }
        
        # Création du personnage
        self.character = Character(
            "NeoHacker",
            level=5,
            experience=2500,
            money=1500,
            health=85,
            max_health=100,
            energy=70,
            max_energy=100,
            reputation=reputation,
            attributes=attributes,
            skills=skills,
            perks=perks,
            biography="Un hacker talentueux qui a grandi dans les bas-fonds de Neo-Tokyo. Après avoir été impliqué dans plusieurs affaires de piratage de grandes corporations, il cherche maintenant à se faire un nom dans le monde souterrain de la cybersécurité."
        )
        
        # Points disponibles pour le développement
        self.character.attribute_points = 2
        self.character.skill_points = 3
        self.character.perk_points = 1
    
    def _create_header_panel(self) -> None:
        """Crée le panneau d'en-tête avec les informations générales du personnage"""
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(150)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #222222;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            
            QLabel {
                color: #FFFFFF;
            }
            
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #333333;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007700, stop:1 #00AA00);
                border-radius: 3px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Panneau de gauche (avatar et nom)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Avatar (placeholder)
        avatar_label = QLabel()
        avatar_label.setFixedSize(80, 80)
        avatar_label.setStyleSheet("""
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 5px;
        """)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setText("Avatar")
        left_layout.addWidget(avatar_label)
        
        # Nom et niveau
        name_label = QLabel(f"{self.character.name}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_layout.addWidget(name_label)
        
        level_label = QLabel(f"Niveau {self.character.level}")
        left_layout.addWidget(level_label)
        
        left_layout.addStretch()
        
        header_layout.addWidget(left_panel)
        
        # Panneau central (barres de santé, énergie, XP)
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Barre de santé
        health_layout = QHBoxLayout()
        health_label = QLabel("Santé:")
        health_layout.addWidget(health_label)
        
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, self.character.max_health)
        self.health_bar.setValue(self.character.health)
        self.health_bar.setFormat(f"{self.character.health}/{self.character.max_health}")
        self.health_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #770000, stop:1 #AA0000);
            }
        """)
        health_layout.addWidget(self.health_bar)
        
        center_layout.addLayout(health_layout)
        
        # Barre d'énergie
        energy_layout = QHBoxLayout()
        energy_label = QLabel("Énergie:")
        energy_layout.addWidget(energy_label)
        
        self.energy_bar = QProgressBar()
        self.energy_bar.setRange(0, self.character.max_energy)
        self.energy_bar.setValue(self.character.energy)
        self.energy_bar.setFormat(f"{self.character.energy}/{self.character.max_energy}")
        self.energy_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #000077, stop:1 #0000AA);
            }
        """)
        energy_layout.addWidget(self.energy_bar)
        
        center_layout.addLayout(energy_layout)
        
        # Barre d'expérience
        xp_layout = QHBoxLayout()
        xp_label = QLabel("XP:")
        xp_layout.addWidget(xp_label)
        
        self.xp_bar = QProgressBar()
        self.xp_bar.setRange(0, 100)
        self.xp_bar.setValue(int(self.character.get_experience_progress() * 100))
        
        next_level_xp = self.character.get_experience_for_next_level()
        current_level_xp = self.character.get_experience_for_level(self.character.level)
        xp_needed = next_level_xp - self.character.experience
        
        self.xp_bar.setFormat(f"{self.character.experience}/{next_level_xp} (Manque: {xp_needed})")
        self.xp_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #777700, stop:1 #AAAA00);
            }
        """)
        xp_layout.addWidget(self.xp_bar)
        
        center_layout.addLayout(xp_layout)
        
        header_layout.addWidget(center_panel, 1)
        
        # Panneau de droite (argent et points disponibles)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Argent
        money_label = QLabel(f"Crédits: {self.character.money}")
        money_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(money_label)
        
        # Points disponibles
        attr_points_label = QLabel(f"Points d'attribut: {self.character.attribute_points}")
        attr_points_label.setStyleSheet("color: #00AA00;" if self.character.attribute_points > 0 else "")
        right_layout.addWidget(attr_points_label)
        
        skill_points_label = QLabel(f"Points de compétence: {self.character.skill_points}")
        skill_points_label.setStyleSheet("color: #00AA00;" if self.character.skill_points > 0 else "")
        right_layout.addWidget(skill_points_label)
        
        perk_points_label = QLabel(f"Points d'avantage: {self.character.perk_points}")
        perk_points_label.setStyleSheet("color: #00AA00;" if self.character.perk_points > 0 else "")
        right_layout.addWidget(perk_points_label)
        
        right_layout.addStretch()
        
        header_layout.addWidget(right_panel)
        
        self.layout.addWidget(header_frame)
    
    def _create_attributes_tab(self) -> QWidget:
        """Crée l'onglet des attributs du personnage"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        tab_layout.setSpacing(10)
        
        # Titre et description
        title_label = QLabel("Attributs du personnage")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        tab_layout.addWidget(title_label)
        
        desc_label = QLabel("Les attributs définissent les capacités de base de votre personnage et influencent diverses compétences.")
        desc_label.setWordWrap(True)
        tab_layout.addWidget(desc_label)
        
        # Points disponibles
        points_label = QLabel(f"Points disponibles: {self.character.attribute_points}")
        points_label.setStyleSheet("color: #00AA00; font-weight: bold;" if self.character.attribute_points > 0 else "")
        tab_layout.addWidget(points_label)
        
        # Grille d'attributs
        attributes_grid = QGridLayout()
        attributes_grid.setSpacing(15)
        
        # En-têtes
        headers = ["Attribut", "Valeur", "Description", ""]
        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("font-weight: bold;")
            attributes_grid.addWidget(label, 0, i)
        
        # Attributs
        row = 1
        for attr_id, attr in self.character.attributes.items():
            # Nom
            name_label = QLabel(attr.name)
            attributes_grid.addWidget(name_label, row, 0)
            
            # Valeur avec barres
            value_widget = QWidget()
            value_layout = QHBoxLayout(value_widget)
            value_layout.setContentsMargins(0, 0, 0, 0)
            value_layout.setSpacing(2)
            
            for i in range(attr.max_value):
                bar = QFrame()
                bar.setFixedSize(15, 20)
                
                if i < attr.value:
                    bar.setStyleSheet("""
                        background-color: #00AA00;
                        border: 1px solid #008800;
                        border-radius: 2px;
                    """)
                else:
                    bar.setStyleSheet("""
                        background-color: #333333;
                        border: 1px solid #555555;
                        border-radius: 2px;
                    """)
                
                value_layout.addWidget(bar)
            
            value_layout.addStretch()
            attributes_grid.addWidget(value_widget, row, 1)
            
            # Description
            desc_label = QLabel(attr.description)
            desc_label.setWordWrap(True)
            attributes_grid.addWidget(desc_label, row, 2)
            
            # Bouton d'amélioration
            upgrade_button = QPushButton("+")
            upgrade_button.setFixedSize(30, 30)
            upgrade_button.setEnabled(self.character.can_upgrade_attribute(attr_id))
            
            # Connexion du signal
            upgrade_button.clicked.connect(lambda checked, a=attr_id: self._upgrade_attribute(a))
            
            attributes_grid.addWidget(upgrade_button, row, 3)
            
            row += 1
        
        # Ajout de la grille au layout
        tab_layout.addLayout(attributes_grid)
        
        # Espacement
        tab_layout.addStretch()
        
        return tab
    
    def _create_skills_tab(self) -> QWidget:
        """Crée l'onglet des compétences du personnage"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        tab_layout.setSpacing(10)
        
        # Titre et description
        title_label = QLabel("Compétences du personnage")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        tab_layout.addWidget(title_label)
        
        desc_label = QLabel("Les compétences représentent les connaissances et capacités spécifiques de votre personnage.")
        desc_label.setWordWrap(True)
        tab_layout.addWidget(desc_label)
        
        # Points disponibles
        points_label = QLabel(f"Points disponibles: {self.character.skill_points}")
        points_label.setStyleSheet("color: #00AA00; font-weight: bold;" if self.character.skill_points > 0 else "")
        tab_layout.addWidget(points_label)
        
        # Onglets de catégories
        categories_tabs = QTabWidget()
        categories_tabs.setTabPosition(QTabWidget.TabPosition.North)
        categories_tabs.setDocumentMode(True)
        
        # Regroupement des compétences par catégorie
        skills_by_category = {}
        for skill_id, skill in self.character.skills.items():
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            
            skills_by_category[skill.category].append((skill_id, skill))
        
        # Création des onglets pour chaque catégorie
        category_names = {
            "tech": "Technologie",
            "physical": "Physique",
            "social": "Social",
            "mental": "Mental",
            "general": "Général"
        }
        
        for category, skills in skills_by_category.items():
            category_tab = QWidget()
            category_layout = QVBoxLayout(category_tab)
            
            # Grille de compétences
            skills_grid = QGridLayout()
            skills_grid.setSpacing(10)
            
            # En-têtes
            headers = ["Compétence", "Niveau", "Description", ""]
            for i, header in enumerate(headers):
                label = QLabel(header)
                label.setStyleSheet("font-weight: bold;")
                skills_grid.addWidget(label, 0, i)
            
            # Compétences
            row = 1
            for skill_id, skill in sorted(skills, key=lambda x: x[1].name):
                # Nom
                name_label = QLabel(skill.name)
                skills_grid.addWidget(name_label, row, 0)
                
                # Niveau avec étoiles
                level_widget = QWidget()
                level_layout = QHBoxLayout(level_widget)
                level_layout.setContentsMargins(0, 0, 0, 0)
                level_layout.setSpacing(2)
                
                for i in range(skill.max_level):
                    star_label = QLabel("★" if i < skill.level else "☆")
                    star_label.setStyleSheet(f"""
                        color: {'#FFAA00' if i < skill.level else '#666666'};
                        font-size: 14px;
                    """)
                    level_layout.addWidget(star_label)
                
                level_layout.addStretch()
                skills_grid.addWidget(level_widget, row, 1)
                
                # Description
                desc_label = QLabel(skill.description)
                desc_label.setWordWrap(True)
                skills_grid.addWidget(desc_label, row, 2)
                
                # Bouton d'amélioration
                upgrade_button = QPushButton("+")
                upgrade_button.setFixedSize(30, 30)
                upgrade_button.setEnabled(self.character.can_upgrade_skill(skill_id))
                
                # Connexion du signal
                upgrade_button.clicked.connect(lambda checked, s=skill_id: self._upgrade_skill(s))
                
                skills_grid.addWidget(upgrade_button, row, 3)
                
                row += 1
            
            # Ajout de la grille au layout
            category_layout.addLayout(skills_grid)
            
            # Espacement
            category_layout.addStretch()
            
            # Ajout de l'onglet
            categories_tabs.addTab(category_tab, category_names.get(category, category.capitalize()))
        
        tab_layout.addWidget(categories_tabs)
        
        return tab
    
    def _upgrade_attribute(self, attribute_id: str) -> None:
        """Améliore un attribut du personnage"""
        if self.character.upgrade_attribute(attribute_id):
            # Mise à jour de l'interface
            self.tabs.setCurrentWidget(self.attributes_tab)
            
            # Recréation de l'onglet des attributs
            index = self.tabs.indexOf(self.attributes_tab)
            self.attributes_tab = self._create_attributes_tab()
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, self.attributes_tab, "Attributs")
            self.tabs.setCurrentIndex(index)
            
            # Émission du signal
            self.attribute_upgraded.emit(attribute_id)
            
            logger.info(f"Attribut amélioré: {attribute_id}")
    
    def _upgrade_skill(self, skill_id: str) -> None:
        """Améliore une compétence du personnage"""
        if self.character.upgrade_skill(skill_id):
            # Mise à jour de l'interface
            self.tabs.setCurrentWidget(self.skills_tab)
            
            # Recréation de l'onglet des compétences
            index = self.tabs.indexOf(self.skills_tab)
            self.skills_tab = self._create_skills_tab()
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, self.skills_tab, "Compétences")
            self.tabs.setCurrentIndex(index)
            
            # Émission du signal
            self.skill_upgraded.emit(skill_id)
            
            logger.info(f"Compétence améliorée: {skill_id}")
    
    def _create_perks_tab(self) -> QWidget:
        """Crée l'onglet des avantages du personnage"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        tab_layout.setSpacing(10)
        
        # Titre et description
        title_label = QLabel("Avantages du personnage")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        tab_layout.addWidget(title_label)
        
        desc_label = QLabel("Les avantages sont des capacités spéciales qui donnent à votre personnage des bonus uniques.")
        desc_label.setWordWrap(True)
        tab_layout.addWidget(desc_label)
        
        # Points disponibles
        points_label = QLabel(f"Points disponibles: {self.character.perk_points}")
        points_label.setStyleSheet("color: #00AA00; font-weight: bold;" if self.character.perk_points > 0 else "")
        tab_layout.addWidget(points_label)
        
        # Onglets de catégories
        categories_tabs = QTabWidget()
        categories_tabs.setTabPosition(QTabWidget.TabPosition.North)
        categories_tabs.setDocumentMode(True)
        
        # Regroupement des avantages par catégorie
        perks_by_category = {}
        for perk_id, perk in self.character.perks.items():
            if perk.category not in perks_by_category:
                perks_by_category[perk.category] = []
            
            perks_by_category[perk.category].append((perk_id, perk))
        
        # Création des onglets pour chaque catégorie
        category_names = {
            "tech": "Technologie",
            "physical": "Physique",
            "social": "Social",
            "mental": "Mental",
            "general": "Général"
        }
        
        for category, perks in perks_by_category.items():
            category_tab = QWidget()
            category_layout = QVBoxLayout(category_tab)
            
            # Grille d'avantages
            perks_grid = QGridLayout()
            perks_grid.setSpacing(10)
            
            # En-têtes
            headers = ["Avantage", "Statut", "Description", ""]
            for i, header in enumerate(headers):
                label = QLabel(header)
                label.setStyleSheet("font-weight: bold;")
                perks_grid.addWidget(label, 0, i)
            
            # Avantages
            row = 1
            for perk_id, perk in sorted(perks, key=lambda x: x[1].name):
                # Nom
                name_label = QLabel(perk.name)
                perks_grid.addWidget(name_label, row, 0)
                
                # Statut
                status_label = QLabel("Actif" if perk.active else "Inactif")
                status_label.setStyleSheet(f"color: {'#00AA00' if perk.active else '#AA0000'};")
                perks_grid.addWidget(status_label, row, 1)
                
                # Description
                desc_label = QLabel(perk.description)
                desc_label.setWordWrap(True)
                perks_grid.addWidget(desc_label, row, 2)
                
                # Bouton d'activation
                if perk.active:
                    # Si l'avantage est déjà actif, on affiche un indicateur
                    icon_label = QLabel("✓")
                    icon_label.setStyleSheet("color: #00AA00; font-weight: bold; font-size: 16px;")
                    perks_grid.addWidget(icon_label, row, 3, Qt.AlignmentFlag.AlignCenter)
                else:
                    # Sinon, on affiche un bouton pour l'activer
                    unlock_button = QPushButton("Débloquer")
                    unlock_button.setEnabled(self.character.perk_points > 0)
                    
                    # Connexion du signal
                    unlock_button.clicked.connect(lambda checked, p=perk_id: self._unlock_perk(p))
                    
                    perks_grid.addWidget(unlock_button, row, 3)
                
                row += 1
            
            # Ajout de la grille au layout
            category_layout.addLayout(perks_grid)
            
            # Espacement
            category_layout.addStretch()
            
            # Ajout de l'onglet
            categories_tabs.addTab(category_tab, category_names.get(category, category.capitalize()))
        
        tab_layout.addWidget(categories_tabs)
        
        return tab
    
    def _create_reputation_tab(self) -> QWidget:
        """Crée l'onglet de réputation du personnage"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        tab_layout.setSpacing(10)
        
        # Titre et description
        title_label = QLabel("Réputation du personnage")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        tab_layout.addWidget(title_label)
        
        desc_label = QLabel("Votre réputation auprès des différentes factions influence vos interactions et les missions disponibles.")
        desc_label.setWordWrap(True)
        tab_layout.addWidget(desc_label)
        
        # Grille de réputation
        reputation_grid = QGridLayout()
        reputation_grid.setSpacing(15)
        
        # En-têtes
        headers = ["Faction", "Réputation", "Statut"]
        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("font-weight: bold;")
            reputation_grid.addWidget(label, 0, i)
        
        # Définition des niveaux de réputation
        reputation_levels = {
            (0, 20): ("Hostile", "#AA0000"),
            (21, 40): ("Méfiant", "#AA5500"),
            (41, 60): ("Neutre", "#AAAA00"),
            (61, 80): ("Amical", "#55AA00"),
            (81, 100): ("Allié", "#00AA00")
        }
        
        # Noms des factions
        faction_names = {
            "hackers": "Communauté de hackers",
            "corps": "Corporations",
            "police": "Forces de l'ordre",
            "underground": "Marché noir"
        }
        
        # Réputation
        row = 1
        for faction_id, rep_value in self.character.reputation.items():
            # Nom de la faction
            faction_label = QLabel(faction_names.get(faction_id, faction_id.capitalize()))
            reputation_grid.addWidget(faction_label, row, 0)
            
            # Barre de réputation
            rep_bar = QProgressBar()
            rep_bar.setRange(0, 100)
            rep_bar.setValue(rep_value)
            rep_bar.setFormat(f"{rep_value}%")
            rep_bar.setFixedHeight(20)
            
            # Détermination du niveau de réputation
            status_text = "Inconnu"
            status_color = "#AAAAAA"
            for (min_val, max_val), (level_text, level_color) in reputation_levels.items():
                if min_val <= rep_value <= max_val:
                    status_text = level_text
                    status_color = level_color
                    
                    # Application du style à la barre de progression
                    rep_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: 1px solid #555555;
                            border-radius: 3px;
                            background-color: #333333;
                            text-align: center;
                        }}
                        
                        QProgressBar::chunk {{
                            background-color: {level_color};
                            border-radius: 2px;
                        }}
                    """)
                    break
            
            reputation_grid.addWidget(rep_bar, row, 1)
            
            # Statut
            status_label = QLabel(status_text)
            status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            reputation_grid.addWidget(status_label, row, 2)
            
            row += 1
        
        # Ajout de la grille au layout
        tab_layout.addLayout(reputation_grid)
        
        # Espacement
        tab_layout.addStretch()
        
        # Informations supplémentaires
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            
            QLabel {
                color: #CCCCCC;
            }
        """)
        
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Effets de la réputation")
        info_title.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "• <b>Hostile</b>: La faction vous attaquera à vue. Missions indisponibles.\n"
            "• <b>Méfiant</b>: Interactions limitées. Prix majorés. Missions basiques disponibles.\n"
            "• <b>Neutre</b>: Interactions standard. Prix normaux. Missions intermédiaires disponibles.\n"
            "• <b>Amical</b>: Interactions favorables. Remises sur les prix. Missions avancées disponibles.\n"
            "• <b>Allié</b>: Accès complet. Remises importantes. Missions spéciales disponibles."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        tab_layout.addWidget(info_frame)
        
        return tab
    
    def _create_biography_tab(self) -> QWidget:
        """Crée l'onglet de biographie du personnage"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)
        tab_layout.setSpacing(10)
        
        # Titre
        title_label = QLabel("Biographie du personnage")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        tab_layout.addWidget(title_label)
        
        # Biographie
        bio_frame = QFrame()
        bio_frame.setFrameShape(QFrame.Shape.StyledPanel)
        bio_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            
            QLabel {
                color: #CCCCCC;
            }
            
            QTextEdit {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
        
        bio_layout = QVBoxLayout(bio_frame)
        
        # Texte de biographie
        bio_text = QTextEdit()
        bio_text.setPlainText(self.character.biography)
        bio_text.setReadOnly(True)  # En lecture seule pour l'instant
        bio_layout.addWidget(bio_text)
        
        tab_layout.addWidget(bio_frame, 1)
        
        # Statistiques du personnage
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_frame.setMaximumHeight(200)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            
            QLabel {
                color: #CCCCCC;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("Statistiques")
        stats_title.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(stats_title)
        
        # Grille de statistiques
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # Statistiques fictives pour le développement
        stats = [
            ("Missions accomplies", "12"),
            ("Systèmes piratés", "27"),
            ("Ennemis neutralisés", "8"),
            ("Distance parcourue", "1245 km"),
            ("Temps de jeu", "14h 23m"),
            ("Argent gagné", "4500 crédits"),
            ("Objets trouvés", "34"),
            ("Compétences améliorées", "15")
        ]
        
        # Affichage des statistiques en deux colonnes
        for i, (stat_name, stat_value) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
            
            name_label = QLabel(stat_name + ":")
            stats_grid.addWidget(name_label, row, col)
            
            value_label = QLabel(stat_value)
            value_label.setStyleSheet("font-weight: bold;")
            stats_grid.addWidget(value_label, row, col + 1)
        
        stats_layout.addLayout(stats_grid)
        
        tab_layout.addWidget(stats_frame)
        
        return tab
    
    def _unlock_perk(self, perk_id: str) -> None:
        """Débloque un avantage pour le personnage"""
        if self.character.unlock_perk(perk_id):
            # Mise à jour de l'interface
            self.tabs.setCurrentWidget(self.perks_tab)
            
            # Recréation de l'onglet des avantages
            index = self.tabs.indexOf(self.perks_tab)
            self.perks_tab = self._create_perks_tab()
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, self.perks_tab, "Avantages")
            self.tabs.setCurrentIndex(index)
            
            # Émission du signal
            self.perk_unlocked.emit(perk_id)
            
            logger.info(f"Avantage débloqué: {perk_id}")
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur de la fiche de personnage"""
        # Mise à jour des barres de santé et d'énergie
        self.health_bar.setValue(self.character.health)
        self.health_bar.setFormat(f"{self.character.health}/{self.character.max_health}")
        
        self.energy_bar.setValue(self.character.energy)
        self.energy_bar.setFormat(f"{self.character.energy}/{self.character.max_energy}")
        
        # Mise à jour de la barre d'expérience
        self.xp_bar.setValue(int(self.character.get_experience_progress() * 100))
        
        next_level_xp = self.character.get_experience_for_next_level()
        xp_needed = next_level_xp - self.character.experience
        
        self.xp_bar.setFormat(f"{self.character.experience}/{next_level_xp} (Manque: {xp_needed})")
    
    def add_experience(self, amount: int) -> None:
        """Ajoute de l'expérience au personnage"""
        old_level = self.character.level
        self.character.experience += amount
        
        # Vérification du niveau
        if self.character.level > old_level:
            # Le personnage a gagné un niveau
            logger.info(f"Niveau gagné! Nouveau niveau: {self.character.level}")
            
            # Attribution des points
            self.character.attribute_points += 1
            self.character.skill_points += 2
            
            if self.character.level % 3 == 0:
                # Tous les 3 niveaux, on gagne un point d'avantage
                self.character.perk_points += 1
            
            # TODO: Afficher une animation ou un message de niveau gagné
        
        # Mise à jour de l'interface
        self.update_ui(0)
    
    def set_character(self, character: Character) -> None:
        """Définit le personnage à afficher"""
        self.character = character
        
        # Recréation des onglets
        index = self.tabs.indexOf(self.attributes_tab)
        self.attributes_tab = self._create_attributes_tab()
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, self.attributes_tab, "Attributs")
        
        index = self.tabs.indexOf(self.skills_tab)
        self.skills_tab = self._create_skills_tab()
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, self.skills_tab, "Compétences")
        
        index = self.tabs.indexOf(self.perks_tab)
        self.perks_tab = self._create_perks_tab()
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, self.perks_tab, "Avantages")
        
        index = self.tabs.indexOf(self.reputation_tab)
        self.reputation_tab = self._create_reputation_tab()
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, self.reputation_tab, "Réputation")
        
        index = self.tabs.indexOf(self.biography_tab)
        self.biography_tab = self._create_biography_tab()
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, self.biography_tab, "Biographie")
        
        # Mise à jour de l'interface
        self.update_ui(0)
        
        logger.info(f"Personnage défini: {character.name}")
