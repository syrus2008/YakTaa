"""
Module de gestion des thèmes de l'interface utilisateur pour YakTaa
"""

import logging
import json
import os
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

logger = logging.getLogger("YakTaa.UI.Theme")

# Définir le chemin vers le répertoire des feuilles de style
STYLESHEET_DIR = os.path.join(os.path.dirname(__file__), "stylesheets")

# Définir les polices par défaut
DEFAULT_FONTS = {
    "main": "Segoe UI",
    "terminal": "Cascadia Code",
    "headers": "Segoe UI Semibold",
    "text": "Segoe UI",
    "button": "Segoe UI",
    "code": "Cascadia Code"
}

def get_font(font_type: str = "main", size: int = 10, bold: bool = False, italic: bool = False) -> QFont:
    """
    Obtient une police QFont selon le type et les propriétés demandées
    
    Args:
        font_type: Type de police (main, terminal, headers, text, button, code)
        size: Taille de la police en points
        bold: Si la police doit être en gras
        italic: Si la police doit être en italique
        
    Returns:
        Une instance de QFont configurée selon les paramètres
    """
    # Obtenir le nom de la police depuis les polices par défaut
    font_name = DEFAULT_FONTS.get(font_type, DEFAULT_FONTS["main"])
    
    # Créer la police
    font = QFont(font_name, size)
    font.setBold(bold)
    font.setItalic(italic)
    
    # Configurations spécifiques selon le type
    if font_type == "terminal" or font_type == "code":
        font.setFixedPitch(True)  # Police à espacement fixe
    
    if font_type == "headers":
        font.setWeight(QFont.Weight.DemiBold)
    
    return font

class Theme:
    """Classe qui gère les thèmes de l'interface utilisateur"""
    
    # Thèmes prédéfinis
    THEMES = {
        "cyberpunk_dark": {
            "name": "Cyberpunk Dark",
            "colors": {
                "primary": "#00FFFF",          # Cyan néon
                "secondary": "#FF00FF",        # Magenta néon
                "accent": "#FFFF00",           # Jaune néon
                "background": "#121212",       # Noir profond
                "background_alt": "#1E1E1E",   # Noir légèrement plus clair
                "foreground": "#FFFFFF",       # Blanc
                "foreground_alt": "#CCCCCC",   # Gris clair
                "success": "#00FF00",          # Vert néon
                "warning": "#FF9900",          # Orange
                "error": "#FF0000",            # Rouge néon
                "info": "#0099FF",             # Bleu clair
                "terminal_bg": "#000000",      # Noir pour le terminal
                "terminal_text": "#00FF00"     # Vert pour le texte du terminal
            },
            "fonts": {
                "main": "Cyberpunk",
                "terminal": "Cascadia Code",
                "headers": "NeonRetro",
                "text": "Segoe UI"
            },
            "styles": {
                "border_radius": "4px",
                "border_width": "1px",
                "shadow": "0px 4px 8px rgba(0, 255, 255, 0.3)",
                "gradient": "linear-gradient(135deg, #121212, #1E1E1E)"
            }
        },
        "neon_city": {
            "name": "Neon City",
            "colors": {
                "primary": "#FF00FF",          # Magenta néon
                "secondary": "#00FFFF",        # Cyan néon
                "accent": "#FFFF00",           # Jaune néon
                "background": "#0A0A1E",       # Bleu très foncé
                "background_alt": "#151530",   # Bleu foncé
                "foreground": "#FFFFFF",       # Blanc
                "foreground_alt": "#CCCCCC",   # Gris clair
                "success": "#00FF00",          # Vert néon
                "warning": "#FF9900",          # Orange
                "error": "#FF0000",            # Rouge néon
                "info": "#0099FF",             # Bleu clair
                "terminal_bg": "#000000",      # Noir pour le terminal
                "terminal_text": "#00FFFF"     # Cyan pour le texte du terminal
            },
            "fonts": {
                "main": "NeonRetro",
                "terminal": "Cascadia Code",
                "headers": "Cyberpunk",
                "text": "Segoe UI"
            },
            "styles": {
                "border_radius": "6px",
                "border_width": "1px",
                "shadow": "0px 4px 8px rgba(255, 0, 255, 0.3)",
                "gradient": "linear-gradient(135deg, #0A0A1E, #151530)"
            }
        },
        "hacker_green": {
            "name": "Hacker Green",
            "colors": {
                "primary": "#00FF00",          # Vert néon
                "secondary": "#CCFF00",        # Vert-jaune
                "accent": "#FFFFFF",           # Blanc
                "background": "#000000",       # Noir
                "background_alt": "#0A1A0A",   # Vert très foncé
                "foreground": "#00FF00",       # Vert néon
                "foreground_alt": "#AAFFAA",   # Vert clair
                "success": "#00FF00",          # Vert néon
                "warning": "#FFFF00",          # Jaune
                "error": "#FF0000",            # Rouge
                "info": "#00FFFF",             # Cyan
                "terminal_bg": "#000000",      # Noir pour le terminal
                "terminal_text": "#00FF00"     # Vert pour le texte du terminal
            },
            "fonts": {
                "main": "Cascadia Code",
                "terminal": "Cascadia Code",
                "headers": "Cascadia Code",
                "text": "Cascadia Code"
            },
            "styles": {
                "border_radius": "0px",
                "border_width": "1px",
                "shadow": "0px 4px 8px rgba(0, 255, 0, 0.3)",
                "gradient": "none"
            }
        }
    }
    
    def __init__(self, theme_name: str = "cyberpunk_dark"):
        """Initialise le thème avec le nom spécifié"""
        self.current_theme_name = theme_name
        self.current_theme = self.THEMES.get(theme_name, self.THEMES["cyberpunk_dark"])
        
        logger.info(f"Thème initialisé: {self.current_theme['name']}")
    
    def get_color(self, color_name: str) -> str:
        """Récupère une couleur du thème actuel"""
        return self.current_theme["colors"].get(color_name, "#FFFFFF")
    
    def get_font(self, font_name: str) -> str:
        """Récupère une police du thème actuel"""
        return self.current_theme["fonts"].get(font_name, "Segoe UI")
    
    def get_style(self, style_name: str) -> str:
        """Récupère un style du thème actuel"""
        return self.current_theme["styles"].get(style_name, "")
    
    def change_theme(self, theme_name: str) -> bool:
        """Change le thème actuel"""
        if theme_name in self.THEMES:
            self.current_theme_name = theme_name
            self.current_theme = self.THEMES[theme_name]
            logger.info(f"Thème changé: {self.current_theme['name']}")
            return True
        else:
            logger.warning(f"Thème inconnu: {theme_name}")
            return False
    
    def apply_to_application(self, app: QApplication) -> None:
        """Applique le thème à l'application PyQt6"""
        try:
            # Création d'une palette de couleurs
            palette = QPalette()
            
            # Couleurs de base
            palette.setColor(QPalette.ColorRole.Window, QColor(self.get_color("background")))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.ColorRole.Base, QColor(self.get_color("background_alt")))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(self.get_color("background")))
            palette.setColor(QPalette.ColorRole.Text, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.ColorRole.Button, QColor(self.get_color("background_alt")))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(self.get_color("accent")))
            
            # Couleurs des liens
            palette.setColor(QPalette.ColorRole.Link, QColor(self.get_color("primary")))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor(self.get_color("secondary")))
            
            # Couleurs de surbrillance
            palette.setColor(QPalette.ColorRole.Highlight, QColor(self.get_color("primary")))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(self.get_color("background")))
            
            # Application de la palette
            app.setPalette(palette)
            
            # Police par défaut
            default_font = QFont(self.get_font("text"), 10)
            app.setFont(default_font)
            
            # Feuille de style CSS globale
            app.setStyleSheet(self._generate_stylesheet())
            
            logger.info(f"Thème appliqué à l'application: {self.current_theme['name']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application du thème: {str(e)}", exc_info=True)
    
    def _generate_stylesheet(self) -> str:
        """Génère la feuille de style CSS pour le thème actuel"""
        css = f"""
        /* Styles globaux */
        QWidget {{
            background-color: {self.get_color("background")};
            color: {self.get_color("foreground")};
            font-family: {self.get_font("text")};
        }}
        
        /* En-têtes */
        QLabel[heading="true"] {{
            font-family: {self.get_font("headers")};
            color: {self.get_color("primary")};
            font-weight: bold;
        }}
        
        /* Boutons */
        QPushButton {{
            background-color: {self.get_color("background_alt")};
            color: {self.get_color("primary")};
            border: {self.get_style("border_width")} solid {self.get_color("primary")};
            border-radius: {self.get_style("border_radius")};
            padding: 8px 16px;
            font-family: {self.get_font("main")};
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {self.get_color("primary")};
            color: {self.get_color("background")};
        }}
        
        QPushButton:pressed {{
            background-color: {self.get_color("secondary")};
        }}
        
        /* Champs de texte */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.get_color("background_alt")};
            color: {self.get_color("foreground")};
            border: {self.get_style("border_width")} solid {self.get_color("primary")};
            border-radius: {self.get_style("border_radius")};
            padding: 4px;
        }}
        
        /* Terminal */
        QPlainTextEdit[terminal="true"] {{
            background-color: {self.get_color("terminal_bg")};
            color: {self.get_color("terminal_text")};
            font-family: {self.get_font("terminal")};
            border: none;
        }}
        
        /* Menus */
        QMenuBar {{
            background-color: {self.get_color("background")};
            color: {self.get_color("foreground")};
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.get_color("primary")};
            color: {self.get_color("background")};
        }}
        
        QMenu {{
            background-color: {self.get_color("background_alt")};
            color: {self.get_color("foreground")};
            border: {self.get_style("border_width")} solid {self.get_color("primary")};
        }}
        
        QMenu::item:selected {{
            background-color: {self.get_color("primary")};
            color: {self.get_color("background")};
        }}
        """
        
        return css
    
    def get_all_themes(self) -> Dict[str, str]:
        """Retourne la liste de tous les thèmes disponibles"""
        return {theme_id: theme_data["name"] for theme_id, theme_data in self.THEMES.items()}
    
    def export_theme(self, file_path: str) -> bool:
        """Exporte le thème actuel dans un fichier JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_theme, f, indent=4)
            
            logger.info(f"Thème exporté vers: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation du thème: {str(e)}", exc_info=True)
            return False
    
    def import_theme(self, file_path: str, theme_id: str) -> bool:
        """Importe un thème depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Validation minimale du thème
            required_keys = ["name", "colors", "fonts", "styles"]
            if not all(key in theme_data for key in required_keys):
                logger.error(f"Format de thème invalide: {file_path}")
                return False
            
            # Ajout du thème à la liste des thèmes disponibles
            self.THEMES[theme_id] = theme_data
            
            logger.info(f"Thème importé: {theme_data['name']} (ID: {theme_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'importation du thème: {str(e)}", exc_info=True)
            return False

# Clé unique pour l'objet Theme dans l'application
_THEME_INSTANCE = None

def get_theme() -> Theme:
    """
    Récupère l'instance unique du thème
    
    Returns:
        L'instance unique du thème
    """
    global _THEME_INSTANCE
    
    if _THEME_INSTANCE is None:
        _THEME_INSTANCE = Theme()
    
    return _THEME_INSTANCE

def apply_theme(widget, theme_name: str = None) -> None:
    """
    Applique le thème actuel à un widget spécifique
    
    Args:
        widget: Le widget auquel appliquer le thème
        theme_name: Le nom du thème à appliquer (optionnel, utilise le thème actuel par défaut)
    """
    theme = get_theme()
    
    if theme_name:
        theme.change_theme(theme_name)
    
    # Appliquer les styles au widget
    stylesheet = f"""
    /* Styles de base */
    QWidget {{
        background-color: {theme.get_color("background")};
        color: {theme.get_color("foreground")};
        font-family: {theme.get_font("main")};
    }}
    
    QPushButton {{
        background-color: {theme.get_color("background_alt")};
        color: {theme.get_color("primary")};
        border: 1px solid {theme.get_color("primary")};
        border-radius: {theme.get_style("border_radius")};
        padding: 5px 10px;
        font-family: {theme.get_font("button")};
    }}
    
    QPushButton:hover {{
        background-color: {theme.get_color("primary")};
        color: {theme.get_color("background")};
    }}
    
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {theme.get_color("background_alt")};
        color: {theme.get_color("foreground")};
        border: 1px solid {theme.get_color("primary")};
        border-radius: {theme.get_style("border_radius")};
        padding: 2px;
    }}
    
    QLabel {{
        color: {theme.get_color("foreground")};
    }}
    
    QTabWidget::pane {{
        border: 1px solid {theme.get_color("primary")};
        background-color: {theme.get_color("background")};
    }}
    
    QTabBar::tab {{
        background-color: {theme.get_color("background_alt")};
        color: {theme.get_color("foreground")};
        border: 1px solid {theme.get_color("primary")};
        padding: 5px 10px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme.get_color("primary")};
        color: {theme.get_color("background")};
    }}
    
    /* Styles pour le terminal */
    #terminalWidget, #console {{
        background-color: {theme.get_color("terminal_bg")};
        color: {theme.get_color("terminal_text")};
        font-family: {theme.get_font("terminal")};
        border: 1px solid {theme.get_color("primary")};
    }}
    """
    
    # Appliquer la feuille de style
    widget.setStyleSheet(stylesheet)
    
    # Appliquer récursivement aux enfants si c'est un conteneur
    try:
        for child in widget.findChildren(object):
            # Éviter de réappliquer aux widgets qui ont déjà un style personnalisé
            if hasattr(child, 'objectName') and child.objectName():
                continue
            # Appliquer le style aux autres widgets enfants
            child.setStyleSheet(stylesheet)
    except Exception as e:
        logger.warning(f"Erreur lors de l'application du thème aux widgets enfants: {str(e)}")

def get_stylesheet(name: str) -> str:
    """
    Charge une feuille de style depuis le répertoire stylesheets
    
    Args:
        name: Nom de la feuille de style (sans extension)
    
    Returns:
        Contenu de la feuille de style ou chaîne vide si non trouvée
    """
    stylesheet_path = os.path.join(STYLESHEET_DIR, f"{name}.qss")
    
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

def available_themes() -> list:
    """
    Renvoie la liste des thèmes disponibles
    
    Returns:
        Liste des noms de thèmes disponibles
    """
    return list(Theme.THEMES.keys())
