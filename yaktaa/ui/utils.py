#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module d'utilitaires UI pour YakTaa

Contient des fonctions et classes d'aide pour l'interface utilisateur,
particulièrement pour les éléments de style cyberpunk.
"""

import logging
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union, Any

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QRect, QPoint
from PyQt6.QtGui import QColor, QPalette, QFont, QLinearGradient, QGradient, QPainter, QPen, QBrush, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect

# Configuration du logger
logger = logging.getLogger(__name__)

# Couleurs principales du thème cyberpunk
CYBERPUNK_COLORS = {
    'primary': QColor(0, 230, 255),       # Cyan néon
    'secondary': QColor(240, 60, 170),    # Rose néon
    'tertiary': QColor(127, 0, 255),      # Violet néon
    'accent': QColor(255, 240, 30),       # Jaune néon
    'background_dark': QColor(10, 12, 20), # Noir bleuté profond
    'background_mid': QColor(20, 25, 40),  # Bleu foncé
    'text_primary': QColor(220, 220, 220), # Blanc cassé
    'text_secondary': QColor(150, 150, 160), # Gris clair
    'success': QColor(0, 255, 136),       # Vert néon
    'warning': QColor(255, 165, 0),       # Orange néon
    'error': QColor(255, 55, 55),         # Rouge néon
    'black': QColor(5, 5, 10),            # Noir profond
    'terminal_green': QColor(40, 255, 40), # Vert terminal
}

# Polices
CYBERPUNK_FONTS = {
    'title': QFont("Orbitron", 14, QFont.Weight.Bold),
    'subtitle': QFont("Rajdhani", 12, QFont.Weight.DemiBold),
    'body': QFont("Share Tech Mono", 10),
    'code': QFont("Courier New", 10),
    'small': QFont("Share Tech Mono", 8),
    'large': QFont("Orbitron", 16, QFont.Weight.Bold),
    'button': QFont("Rajdhani", 11, QFont.Weight.Bold),
    'heading': QFont("Orbitron", 14, QFont.Weight.Bold),  # Ajout du style 'heading'
}

# Essayer de fallback sur des polices système si les polices cyberpunk ne sont pas disponibles
def setup_fonts():
    """Configure les polices avec des alternatives système si nécessaire"""
    global CYBERPUNK_FONTS
    
    # Vérifier si chaque police est disponible
    system_fonts = QFont().families()
    
    # Fallbacks pour chaque style
    fallbacks = {
        'title': ["Impact", "Arial Black", "Arial"],
        'subtitle': ["Segoe UI", "Arial", "Tahoma"],
        'body': ["Consolas", "Courier New", "Monospace"],
        'code': ["Consolas", "Courier New", "Monospace"],
        'small': ["Consolas", "Courier New", "Monospace"],
        'large': ["Impact", "Arial Black", "Arial"],
        'button': ["Segoe UI", "Arial", "Tahoma"],
        'heading': ["Impact", "Arial Black", "Arial"],
    }
    
    # Appliquer les fallbacks si nécessaire
    for style, font in CYBERPUNK_FONTS.items():
        font_family = font.family()
        if font_family not in system_fonts:
            for fallback in fallbacks[style]:
                if fallback in system_fonts:
                    new_font = QFont(fallback, font.pointSize(), font.weight())
                    CYBERPUNK_FONTS[style] = new_font
                    logger.debug(f"Police {font_family} non disponible, utilisation de {fallback}")
                    break

# Appeler au chargement du module
setup_fonts()

# Fonction pour obtenir une police selon le style
def get_font(style="body", size=None, bold=False, italic=False):
    """
    Retourne une police QFont selon le style spécifié
    
    Args:
        style: Le style de police à utiliser (default: 'body')
        size: Taille de la police en points (défaut: None, utilise la taille par défaut du style)
        bold: Si True, la police sera en gras (défaut: False)
        italic: Si True, la police sera en italique (défaut: False)
    
    Returns:
        QFont: La police configurée selon le style demandé
    """
    logger.debug(f"Chargement de la police pour le style '{style}' (taille: {size}, gras: {bold}, italique: {italic})")
    
    if style in CYBERPUNK_FONTS:
        font = CYBERPUNK_FONTS[style]
        if size is not None:
            font.setPointSize(size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        if italic:
            font.setItalic(True)
        return font
    else:
        logger.warning(f"Style de police non reconnu: {style}, utilisation du style 'body'")
        font = CYBERPUNK_FONTS['body']
        if size is not None:
            font.setPointSize(size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        if italic:
            font.setItalic(True)
        return font

def apply_cyberpunk_style(widget: QWidget, style_type: str = 'default') -> None:
    """
    Applique un style cyberpunk à un widget QT
    
    Args:
        widget: Le widget à styler
        style_type: Type de style à appliquer (default, button, panel, terminal, etc.)
    """
    logger.debug(f"Application du style cyberpunk '{style_type}' au widget {widget.__class__.__name__}")
    
    if style_type == 'default':
        # Style par défaut
        widget.setStyleSheet(
            f"background-color: {CYBERPUNK_COLORS['background_mid'].name()}; "
            f"color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"border: 1px solid {CYBERPUNK_COLORS['primary'].name()}; "
            f"border-radius: 4px;"
        )
    
    elif style_type == 'button':
        # Style de bouton cyberpunk
        widget.setFont(CYBERPUNK_FONTS['button'])
        widget.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
            f"  color: {CYBERPUNK_COLORS['primary'].name()}; "
            f"  border: 1px solid {CYBERPUNK_COLORS['primary'].name()}; "
            f"  border-radius: 4px; "
            f"  padding: 5px 15px; "
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {CYBERPUNK_COLORS['primary'].name()}; "
            f"  color: {CYBERPUNK_COLORS['black'].name()}; "
            f"}}"
            f"QPushButton:pressed {{"
            f"  background-color: {CYBERPUNK_COLORS['tertiary'].name()}; "
            f"  color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"}}"
            f"QPushButton:disabled {{"
            f"  background-color: {CYBERPUNK_COLORS['background_mid'].name()}; "
            f"  color: {CYBERPUNK_COLORS['text_secondary'].name()}; "
            f"  border: 1px solid {CYBERPUNK_COLORS['text_secondary'].name()}; "
            f"}}"
        )
        
        # Ajouter un effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(CYBERPUNK_COLORS['primary'])
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)
    
    elif style_type == 'panel':
        # Style de panneau/cadre
        widget.setStyleSheet(
            f"QFrame {{"
            f"  background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
            f"  color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"  border: 1px solid {CYBERPUNK_COLORS['primary'].name()}; "
            f"  border-radius: 6px; "
            f"}}"
        )
        
        # Ajouter un effet d'ombre subtil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(3, 3)
        widget.setGraphicsEffect(shadow)
    
    elif style_type == 'terminal':
        # Style de terminal
        widget.setFont(CYBERPUNK_FONTS['code'])
        widget.setStyleSheet(
            f"background-color: {CYBERPUNK_COLORS['black'].name()}; "
            f"color: {CYBERPUNK_COLORS['terminal_green'].name()}; "
            f"border: 1px solid {CYBERPUNK_COLORS['primary'].name()}; "
            f"border-radius: 4px; "
            f"padding: 5px;"
        )
    
    elif style_type == 'shop_item':
        # Style spécifique pour les items de boutique
        widget.setStyleSheet(
            f"QFrame {{"
            f"  background-color: {CYBERPUNK_COLORS['background_mid'].name()}; "
            f"  color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"  border: 1px solid {CYBERPUNK_COLORS['secondary'].name()}; "
            f"  border-radius: 5px; "
            f"  margin: 3px; "
            f"  padding: 5px; "
            f"}}"
            f"QFrame:hover {{"
            f"  background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
            f"  border: 1.5px solid {CYBERPUNK_COLORS['accent'].name()}; "
            f"}}"
        )
        
        # Effet de brillance au survol
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(CYBERPUNK_COLORS['secondary'])
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

# Fonction pour obtenir une feuille de style commune
def get_stylesheet(theme="cyberpunk", component="default"):
    """
    Retourne une feuille de style CSS selon le thème et le composant spécifiés
    
    Args:
        theme: Le thème à utiliser (default: 'cyberpunk')
        component: Le type de composant ('default', 'button', 'panel', etc.)
    
    Returns:
        str: La feuille de style CSS à appliquer
    """
    logger.debug(f"Chargement de la feuille de style pour le thème '{theme}' et le composant '{component}'")

    if theme == "cyberpunk":
        if component == "default":
            return f"""
                background-color: {CYBERPUNK_COLORS['background_mid'].name()};
                color: {CYBERPUNK_COLORS['text_primary'].name()};
                border: 1px solid {CYBERPUNK_COLORS['primary'].name()};
                border-radius: 4px;
            """
        elif component == "button":
            return f"""
                QPushButton {{
                    background-color: {CYBERPUNK_COLORS['background_dark'].name()};
                    color: {CYBERPUNK_COLORS['primary'].name()};
                    border: 1px solid {CYBERPUNK_COLORS['primary'].name()};
                    border-radius: 4px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: {CYBERPUNK_COLORS['primary'].name()};
                    color: {CYBERPUNK_COLORS['black'].name()};
                }}
                QPushButton:pressed {{
                    background-color: {CYBERPUNK_COLORS['tertiary'].name()};
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                }}
                QPushButton:disabled {{
                    background-color: {CYBERPUNK_COLORS['background_mid'].name()};
                    color: {CYBERPUNK_COLORS['text_secondary'].name()};
                    border: 1px solid {CYBERPUNK_COLORS['text_secondary'].name()};
                }}
            """
        elif component == "shop_item":
            return f"""
                QFrame {{
                    background-color: {CYBERPUNK_COLORS['background_mid'].name()};
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: 1px solid {CYBERPUNK_COLORS['secondary'].name()};
                    border-radius: 5px;
                    margin: 3px;
                    padding: 5px;
                }}
                QFrame:hover {{
                    background-color: {CYBERPUNK_COLORS['background_dark'].name()};
                    border: 1.5px solid {CYBERPUNK_COLORS['accent'].name()};
                }}
                QLabel {{
                    background-color: transparent;
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: none;
                }}
                QLabel[class="item_name"] {{
                    color: {CYBERPUNK_COLORS['primary'].name()};
                    font-weight: bold;
                }}
                QLabel[class="item_price"] {{
                    color: {CYBERPUNK_COLORS['accent'].name()};
                }}
                QLabel[class="item_description"] {{
                    color: {CYBERPUNK_COLORS['text_secondary'].name()};
                    font-style: italic;
                }}
            """
        elif component == "shop_panel":
            return f"""
                QFrame {{
                    background-color: {CYBERPUNK_COLORS['background_dark'].name()};
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: 1.5px solid {CYBERPUNK_COLORS['primary'].name()};
                    border-radius: 6px;
                }}
                QLabel {{
                    background-color: transparent;
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: none;
                }}
                QLabel[class="shop_title"] {{
                    color: {CYBERPUNK_COLORS['primary'].name()};
                    font-weight: bold;
                    font-size: 14px;
                }}
                QLabel[class="credits"] {{
                    color: {CYBERPUNK_COLORS['accent'].name()};
                    font-weight: bold;
                }}
                QPushButton {{
                    background-color: {CYBERPUNK_COLORS['background_dark'].name()};
                    color: {CYBERPUNK_COLORS['primary'].name()};
                    border: 1px solid {CYBERPUNK_COLORS['primary'].name()};
                    border-radius: 4px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: {CYBERPUNK_COLORS['primary'].name()};
                    color: {CYBERPUNK_COLORS['black'].name()};
                }}
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    background-color: {CYBERPUNK_COLORS['background_mid'].name()};
                    width: 12px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {CYBERPUNK_COLORS['primary'].name()};
                    min-height: 20px;
                    border-radius: 4px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """
        elif component == "inventory_panel":
            return f"""
                QFrame {{
                    background-color: {CYBERPUNK_COLORS['background_dark'].name()};
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: 1.5px solid {CYBERPUNK_COLORS['tertiary'].name()};
                    border-radius: 6px;
                }}
                QLabel {{
                    background-color: transparent;
                    color: {CYBERPUNK_COLORS['text_primary'].name()};
                    border: none;
                }}
                QLabel[class="inventory_title"] {{
                    color: {CYBERPUNK_COLORS['tertiary'].name()};
                    font-weight: bold;
                    font-size: 14px;
                }}
            """
        else:
            logger.warning(f"Composant non reconnu: {component}, utilisation du style par défaut")

            return f"""
                background-color: {CYBERPUNK_COLORS['background_mid'].name()};
                color: {CYBERPUNK_COLORS['text_primary'].name()};
            """
    else:
        logger.warning(f"Thème non reconnu: {theme}, utilisation du thème par défaut")

        return f"""
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #555;
            border-radius: 4px;
        """

# Fonction pour charger une feuille de style depuis un fichier
def load_stylesheet(name):
    """
    Charge une feuille de style depuis le répertoire stylesheets
    
    Args:
        name: Nom de la feuille de style (sans extension)
    
    Returns:
        Contenu de la feuille de style ou chaîne vide si non trouvée
    """
    import os
    
    # Définir le chemin vers le répertoire des feuilles de style
    stylesheet_dir = os.path.join(os.path.dirname(__file__), "stylesheets")
    stylesheet_path = os.path.join(stylesheet_dir, f"{name}.qss")
    
    try:
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r', encoding='utf-8') as file:
                stylesheet = file.read()
                logger.debug(f"Feuille de style chargée: {name}")
                return stylesheet
        else:
            logger.warning(f"Feuille de style non trouvée: {name}")
            return ""
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la feuille de style {name}: {str(e)}")
        return ""

# Classe pour créer un label avec effet de texte cyberpunk (clignotant, glitch, etc.)
class CyberpunkLabel(QLabel):
    """Label avec effets visuels cyberpunk"""
    
    def __init__(self, text="", parent=None, effect_type="glow"):
        super().__init__(text, parent)
        self.effect_type = effect_type
        self.glow_color = CYBERPUNK_COLORS['primary']
        self.blink_interval = 300  # ms
        self.setup_style()
        
    def setup_style(self):
        """Configure le style initial du label"""
        self.setFont(CYBERPUNK_FONTS['subtitle'])
        
        if self.effect_type == "glow":
            self.setup_glow_effect()
        elif self.effect_type == "blink":
            self.setup_blink_effect()
        elif self.effect_type == "glitch":
            self.setup_glitch_effect()
    
    def setup_glow_effect(self):
        """Configure un effet de brillance"""
        self.setStyleSheet(
            f"color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"background: transparent;"
        )
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(self.glow_color)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    def setup_blink_effect(self):
        """Configure un effet de clignotement"""
        self.setStyleSheet(
            f"color: {CYBERPUNK_COLORS['primary'].name()}; "
            f"background: transparent;"
        )
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blink)
        self.timer.start(self.blink_interval)
        self.blink_state = True
    
    def setup_glitch_effect(self):
        """Configure un effet de glitch"""
        self.setStyleSheet(
            f"color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"background: transparent;"
        )
        
        self.original_text = self.text()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.glitch)
        self.timer.start(150)  # ms
    
    def blink(self):
        """Alterne la visibilité pour l'effet de clignotement"""
        if self.blink_state:
            self.setStyleSheet(
                f"color: transparent; "
                f"background: transparent;"
            )
        else:
            self.setStyleSheet(
                f"color: {CYBERPUNK_COLORS['primary'].name()}; "
                f"background: transparent;"
            )
        self.blink_state = not self.blink_state
    
    def glitch(self):
        """Crée un effet de texte glitché"""
        # 1 chance sur 10 d'appliquer un glitch
        if random.random() < 0.1:
            text = list(self.original_text)
            for i in range(min(2, len(text))):
                idx = random.randint(0, len(text) - 1)
                text[idx] = random.choice('!@#$%^&*01')
            self.setText(''.join(text))
            
            # Rétablir le texte original après un court délai
            QTimer.singleShot(100, lambda: self.setText(self.original_text))

# Classe de bouton cyberpunk amélioré
class CyberpunkButton(QPushButton):
    """Bouton avec style et animations cyberpunk"""
    
    def __init__(self, text="", parent=None, color="primary"):
        super().__init__(text, parent)
        self.color_key = color
        self.color = CYBERPUNK_COLORS.get(color, CYBERPUNK_COLORS['primary'])
        self.setup_style()
    
    def setup_style(self):
        """Configure le style du bouton"""
        self.setFont(CYBERPUNK_FONTS['button'])
        
        # Style de base
        self.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
            f"  color: {self.color.name()}; "
            f"  border: 1.5px solid {self.color.name()}; "
            f"  border-radius: 4px; "
            f"  padding: 8px 15px; "
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {self.color.name()}; "
            f"  color: {CYBERPUNK_COLORS['black'].name()}; "
            f"}}"
            f"QPushButton:pressed {{"
            f"  background-color: {CYBERPUNK_COLORS['tertiary'].name()}; "
            f"  color: {CYBERPUNK_COLORS['text_primary'].name()}; "
            f"}}"
        )
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(self.color)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """Animation au survol"""
        self.enlarge_animation()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animation à la sortie du survol"""
        self.shrink_animation()
        super().leaveEvent(event)
    
    def enlarge_animation(self):
        """Animation d'agrandissement"""
        animation = QPropertyAnimation(self, b"minimumSize")
        current_size = self.minimumSize()
        animation.setStartValue(current_size)
        animation.setEndValue(QSize(int(current_size.width() * 1.05), int(current_size.height() * 1.05)))
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    
    def shrink_animation(self):
        """Animation de rétrécissement"""
        animation = QPropertyAnimation(self, b"minimumSize")
        current_size = self.minimumSize()
        animation.setStartValue(current_size)
        animation.setEndValue(QSize(int(current_size.width() / 1.05), int(current_size.height() / 1.05)))
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

# Classe pour les panneaux avec bords illuminés
class CyberpunkPanel(QFrame):
    """Panneau avec bords illuminés et effet de pulsation cyberpunk"""
    
    def __init__(self, parent=None, border_color="primary", pulse=True):
        super().__init__(parent)
        self.border_color_key = border_color
        self.border_color = CYBERPUNK_COLORS.get(border_color, CYBERPUNK_COLORS['primary'])
        self.pulse_enabled = pulse
        self.pulse_intensity = 0
        self.pulse_direction = 1
        self.setup_style()
    
    def setup_style(self):
        """Configure le style initial du panneau"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
            f"border: 1.5px solid {self.border_color.name()}; "
            f"border-radius: 6px; "
            f"padding: 5px;"
        )
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(self.border_color)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        # Timer pour l'effet de pulsation
        if self.pulse_enabled:
            self.pulse_timer = QTimer(self)
            self.pulse_timer.timeout.connect(self.pulse_effect)
            self.pulse_timer.start(50)  # ms
    
    def pulse_effect(self):
        """Crée un effet de pulsation sur la bordure"""
        # Modifier l'intensité de la pulsation
        self.pulse_intensity += 0.02 * self.pulse_direction
        if self.pulse_intensity >= 1.0:
            self.pulse_intensity = 1.0
            self.pulse_direction = -1
        elif self.pulse_intensity <= 0.3:
            self.pulse_intensity = 0.3
            self.pulse_direction = 1
        
        # Appliquer l'effet de pulsation
        shadow = self.graphicsEffect()
        if shadow:
            color = QColor(self.border_color)
            color.setAlpha(int(255 * self.pulse_intensity))
            shadow.setColor(color)

# Fonction pour du timestamp formatté façon cyberpunk
def get_cyberpunk_timestamp(include_ms=False) -> str:
    """Retourne un timestamp formatté dans un style cyberpunk"""
    now = datetime.now()
    if include_ms:
        return now.strftime("%Y.%m.%d-%H:%M:%S.%f")[:-3]
    return now.strftime("%Y.%m.%d-%H:%M:%S")

# Fonction pour du texte animé façon "terminal typing"
def terminal_typing_effect(target_widget, text, delay=30, callback=None):
    """Crée un effet de frappe de texte style terminal"""
    target_widget.setText("")
    chars = list(text)
    
    def add_char(i):
        if i < len(chars):
            current_text = target_widget.text() + chars[i]
            target_widget.setText(current_text)
            QTimer.singleShot(delay, lambda: add_char(i+1))
        elif callback:
            callback()
    
    add_char(0)

# Fonction pour afficher une notification cyberpunk
def show_cyberpunk_notification(parent, title, message, timeout=3000, type="info"):
    """Affiche une notification dans le style cyberpunk"""
    # Couleur selon le type
    color_map = {
        "info": "primary",
        "success": "success",
        "warning": "warning",
        "error": "error"
    }
    color_key = color_map.get(type, "primary")
    color = CYBERPUNK_COLORS[color_key]
    
    # Créer le widget de notification
    notif = QFrame(parent)
    notif.setObjectName("cyberpunk_notification")
    notif.setFrameShape(QFrame.Shape.StyledPanel)
    notif.setStyleSheet(
        f"background-color: {CYBERPUNK_COLORS['background_dark'].name()}; "
        f"border: 1.5px solid {color.name()}; "
        f"border-radius: 6px; "
        f"color: {CYBERPUNK_COLORS['text_primary'].name()};"
    )
    
    # Layout
    layout = QVBoxLayout(notif)
    
    # Titre
    title_label = QLabel(title)
    title_label.setFont(CYBERPUNK_FONTS['subtitle'])
    title_label.setStyleSheet(f"color: {color.name()};")
    layout.addWidget(title_label)
    
    # Message
    message_label = QLabel(message)
    message_label.setFont(CYBERPUNK_FONTS['body'])
    layout.addWidget(message_label)
    
    # Timestamp
    timestamp = QLabel(get_cyberpunk_timestamp())
    timestamp.setFont(CYBERPUNK_FONTS['small'])
    timestamp.setStyleSheet(f"color: {CYBERPUNK_COLORS['text_secondary'].name()};")
    layout.addWidget(timestamp)
    
    # Effet d'ombre
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(color)
    shadow.setOffset(0, 0)
    notif.setGraphicsEffect(shadow)
    
    # Positionner la notification
    notif.setGeometry(parent.width() - 350, parent.height() - 120, 300, 100)
    notif.show()
    
    # Animation d'apparition
    anim = QPropertyAnimation(notif, b"geometry")
    start_pos = QRect(parent.width(), parent.height() - 120, 300, 100)
    end_pos = QRect(parent.width() - 350, parent.height() - 120, 300, 100)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setDuration(300)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    
    # Disparition après un délai
    def hide_notification():
        hide_anim = QPropertyAnimation(notif, b"geometry")
        hide_anim.setStartValue(end_pos)
        hide_anim.setEndValue(QRect(parent.width(), parent.height() - 120, 300, 100))
        hide_anim.setDuration(300)
        hide_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        hide_anim.start()
        hide_anim.finished.connect(notif.deleteLater)
    
    QTimer.singleShot(timeout, hide_notification)
    
    return notif
