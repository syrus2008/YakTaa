"""
Module pour le widget de terminal du jeu YakTaa
"""

import logging
import re
import time
from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit,
    QHBoxLayout, QLabel, QFrame, QSplitter, QMenu,
    QToolBar, QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QKeyEvent, QSyntaxHighlighter, QTextDocument, QAction

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Import conditionnel pour éviter les imports circulaires
if TYPE_CHECKING:
    from yaktaa.core.game import Game
    from yaktaa.terminal.command_processor import CommandProcessor

logger = logging.getLogger("YakTaa.UI.Terminal")

class SyntaxHighlighter(QSyntaxHighlighter):
    """Classe pour la coloration syntaxique du terminal"""
    
    def __init__(self, document: QTextDocument, theme: Dict[str, str]):
        """Initialise le surligneur de syntaxe"""
        super().__init__(document)
        self.theme = theme
        
        # Règles de coloration
        self.rules = []
        
        # Commandes
        command_format = QTextCharFormat()
        command_format.setForeground(QColor(self.theme.get("command", "#00FF00")))
        command_format.setFontWeight(700)
        self.rules.append((r'^\$\s+([a-zA-Z0-9_\-]+)', command_format))
        
        # Chemins de fichiers
        path_format = QTextCharFormat()
        path_format.setForeground(QColor(self.theme.get("path", "#FFFF00")))
        self.rules.append((r'(/[a-zA-Z0-9_\-\.]+)+', path_format))
        
        # Adresses IP
        ip_format = QTextCharFormat()
        ip_format.setForeground(QColor(self.theme.get("ip", "#00FFFF")))
        self.rules.append((r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip_format))
        
        # Nombres
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme.get("number", "#FF00FF")))
        self.rules.append((r'\b\d+\b', number_format))
        
        # Messages d'erreur
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(self.theme.get("error", "#FF0000")))
        self.rules.append((r'(Error|ERROR|Failed|FAILED|Exception|EXCEPTION).*$', error_format))
        
        # Messages de succès
        success_format = QTextCharFormat()
        success_format.setForeground(QColor(self.theme.get("success", "#00FF00")))
        self.rules.append((r'(Success|SUCCESS|Completed|COMPLETED|OK).*$', success_format))
        
        # Mots-clés
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme.get("keyword", "#FF9900")))
        keyword_format.setFontWeight(700)
        keywords = [
            r'\bconnect\b', r'\bdisconnect\b', r'\bscan\b', r'\bhack\b', r'\bcrack\b',
            r'\bexploit\b', r'\binstall\b', r'\bupload\b', r'\bdownload\b', r'\bexecute\b',
            r'\bcd\b', r'\bls\b', r'\bdir\b', r'\bcat\b', r'\bhelp\b', r'\bexit\b'
        ]
        for keyword in keywords:
            self.rules.append((keyword, keyword_format))
    
    def highlightBlock(self, text: str) -> None:
        """Surligne un bloc de texte"""
        for pattern, format in self.rules:
            regex = re.compile(pattern)
            for match in regex.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class TerminalOutput(QPlainTextEdit):
    """Widget d'affichage du terminal"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialise le widget d'affichage du terminal"""
        super().__init__(parent)
        
        # Configuration du widget
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setProperty("terminal", "true")
        
        # Police
        font = QFont("Cascadia Code", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Couleurs par défaut
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: none;
            }
        """)
        
        # Historique
        self.history = []
        self.max_history_lines = 1000
        
        # Thème de coloration
        self.theme = {
            "text": "#00FF00",
            "command": "#00FFFF",
            "path": "#FFFF00",
            "ip": "#00FFFF",
            "number": "#FF00FF",
            "error": "#FF0000",
            "success": "#00FF00",
            "keyword": "#FF9900",
            "system": "#AAAAAA"
        }
        
        # Surligneur de syntaxe
        self.highlighter = SyntaxHighlighter(self.document(), self.theme)
    
    def add_text(self, text: str, color: Optional[str] = None) -> None:
        """Ajoute du texte au terminal"""
        # Création du format
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Application de la couleur si spécifiée
        if color:
            format = QTextCharFormat()
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
        
        # Insertion du texte
        cursor.insertText(text)
        
        # Défilement automatique
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
        # Ajout à l'historique
        self.history.append(text)
        
        # Limitation de l'historique
        if len(self.history) > self.max_history_lines:
            self.history = self.history[-self.max_history_lines:]
    
    def add_html(self, html: str) -> None:
        """Ajoute du HTML au terminal"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        
        # Défilement automatique
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def clear_terminal(self) -> None:
        """Efface le contenu du terminal"""
        self.clear()
        self.history = []


class TerminalInput(QLineEdit):
    """Widget de saisie du terminal"""
    
    # Signal émis lorsqu'une commande est saisie
    command_entered = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialise le widget de saisie du terminal"""
        super().__init__(parent)
        
        # Configuration du widget
        self.setPlaceholderText("Entrez une commande...")
        
        # Police
        font = QFont("Cascadia Code", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Couleurs
        self.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: #00FF00;
                border: none;
                border-top: 1px solid #333333;
                padding: 5px;
            }
        """)
        
        # Historique des commandes
        self.command_history = []
        self.history_index = -1
        
        # Connexion du signal
        self.returnPressed.connect(self.on_return_pressed)
    
    def on_return_pressed(self) -> None:
        """Gère l'appui sur la touche Entrée"""
        command = self.text().strip()
        
        if command:
            # Émission du signal
            self.command_entered.emit(command)
            
            # Ajout à l'historique
            self.command_history.append(command)
            self.history_index = -1
            
            # Effacement du champ de saisie
            self.clear()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Gère les événements clavier"""
        # Touche flèche haut pour naviguer dans l'historique
        if event.key() == Qt.Key.Key_Up:
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.setText(self.command_history[-(self.history_index + 1)])
                self.setCursorPosition(len(self.text()))
        
        # Touche flèche bas pour naviguer dans l'historique
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index >= 0:
                self.history_index -= 1
                if self.history_index >= 0:
                    self.setText(self.command_history[-(self.history_index + 1)])
                else:
                    self.clear()
                self.setCursorPosition(len(self.text()))
        
        # Touche Tab pour l'autocomplétion (à implémenter)
        elif event.key() == Qt.Key.Key_Tab:
            # TODO: Implémenter l'autocomplétion
            pass
        
        # Autres touches
        else:
            super().keyPressEvent(event)


class TerminalWidget(QWidget):
    """Widget complet du terminal"""
    
    def __init__(self, game: 'Any', parent: Optional[QWidget] = None):
        """Initialise le widget de terminal"""
        super().__init__(parent)
        
        # Référence au jeu
        self.game = game
        
        # Processeur de commandes
        from yaktaa.terminal.command_processor import CommandProcessor
        self.command_processor = CommandProcessor(game)
        
        # Mise en page
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Affichage du terminal
        self.output = TerminalOutput(self)
        self.layout.addWidget(self.output)
        
        # Barre d'outils
        self._create_toolbar()
        
        # Saisie du terminal
        self.input = TerminalInput(self)
        self.layout.addWidget(self.input)
        
        # Connexion des signaux
        self.input.command_entered.connect(self.process_command)
        
        # Affichage du message de bienvenue
        self._show_welcome_message()
        
        # Timer pour les effets visuels
        self.fx_timer = QTimer(self)
        self.fx_timer.timeout.connect(self._update_fx)
        self.fx_timer.start(100)  # 10 FPS
        
        logger.info("Widget de terminal initialisé")
    
    def _create_toolbar(self) -> None:
        """Crée la barre d'outils du terminal"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #000000;
                border: none;
                border-bottom: 1px solid #333333;
                spacing: 2px;
                padding: 2px;
            }
            
            QToolButton {
                background-color: #333333;
                color: #00FF00;
                border: none;
                border-radius: 2px;
                padding: 2px;
            }
            
            QToolButton:hover {
                background-color: #444444;
            }
            
            QToolButton:pressed {
                background-color: #555555;
            }
        """)
        
        # Actions
        self.clear_action = QAction("Effacer", self.toolbar)
        self.clear_action.triggered.connect(self.output.clear_terminal)
        self.toolbar.addAction(self.clear_action)
        
        self.toolbar.addSeparator()
        
        # Titre du terminal
        self.title_label = QLabel("Terminal YakTaa")
        self.title_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.toolbar.addWidget(self.title_label)
        
        # Espacement
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Statut de connexion
        self.status_label = QLabel("Déconnecté")
        self.status_label.setStyleSheet("color: #FF0000;")
        self.toolbar.addWidget(self.status_label)
        
        self.layout.addWidget(self.toolbar)
    
    def _show_welcome_message(self) -> None:
        """Affiche le message de bienvenue du terminal"""
        welcome_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                   TERMINAL YAKTAA v0.1.0                         ║
║                                                                  ║
║  Bienvenue dans le système de terminal YakTaa.                   ║
║  Tapez 'help' pour afficher la liste des commandes disponibles.  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Système: YakTaa OS v1.0

"""
        self.output.add_text(welcome_text, self.output.theme["text"])
    
    def process_command(self, command: str) -> None:
        """Traite une commande saisie par l'utilisateur"""
        # Affichage de la commande
        prompt = "$ "
        self.output.add_text(f"\n{prompt}{command}\n", self.output.theme["command"])
        
        # Traitement de la commande
        try:
            # Commandes spéciales du terminal
            if command.lower() == "clear":
                self.output.clear_terminal()
                return
            elif command.lower() == "exit":
                self.add_system_message("Utilisez la commande 'quit' pour quitter le jeu.")
                return
            
            # Traitement par le processeur de commandes
            result = self.command_processor.process(command)
            
            # Affichage du résultat
            if result:
                # Détection du type de résultat
                if isinstance(result, dict) and "type" in result:
                    if result["type"] == "error":
                        self.add_system_message(result.get("message", "Erreur inconnue"), error=True)
                    elif result["type"] == "success":
                        self.add_system_message(result.get("message", "Opération réussie"), success=True)
                    elif result["type"] == "code":
                        self._display_code(result.get("code", ""), result.get("language", "text"))
                    elif result["type"] == "table":
                        self._display_table(result.get("headers", []), result.get("rows", []))
                    elif result["type"] == "complex":
                        # Afficher d'abord le message
                        if "message" in result:
                            self.output.add_text(result["message"] + "\n")
                        # Puis afficher le tableau si présent
                        if "table" in result and isinstance(result["table"], dict):
                            self._display_table(result["table"].get("headers", []), result["table"].get("rows", []))
                        # Enfin, afficher le footer si présent
                        if "footer" in result:
                            self.output.add_text("\n" + result["footer"] + "\n")
                    else:
                        self.output.add_text(str(result.get("message", "")))
                else:
                    self.output.add_text(str(result))
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la commande: {str(e)}", exc_info=True)
            self.add_system_message(f"Erreur: {str(e)}", error=True)
    
    def add_system_message(self, message: str, error: bool = False, success: bool = False) -> None:
        """Ajoute un message système au terminal"""
        color = self.output.theme["system"]
        if error:
            color = self.output.theme["error"]
        elif success:
            color = self.output.theme["success"]
        
        self.output.add_text(f"{message}\n", color)
    
    def _display_code(self, code: str, language: str) -> None:
        """Affiche du code avec coloration syntaxique"""
        try:
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(style="monokai")
            highlighted = highlight(code, lexer, formatter)
            
            # Ajout du CSS de base
            css = formatter.get_style_defs()
            html = f"<style>{css}</style>{highlighted}"
            
            self.output.add_html(html)
            
        except Exception as e:
            logger.error(f"Erreur lors de la coloration syntaxique: {str(e)}", exc_info=True)
            self.output.add_text(code)
    
    def _display_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        """Affiche un tableau dans le terminal"""
        if not headers or not rows:
            return
        
        # Calcul de la largeur des colonnes
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Ligne de séparation
        separator = "+"
        for width in col_widths:
            separator += "-" * (width + 2) + "+"
        
        # En-tête
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header.ljust(col_widths[i])} |"
        
        # Affichage
        table = f"\n{separator}\n{header_line}\n{separator}\n"
        
        # Lignes de données
        for row in rows:
            row_line = "|"
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f" {str(cell).ljust(col_widths[i])} |"
            table += f"{row_line}\n"
        
        table += f"{separator}\n"
        
        self.output.add_text(table)
    
    def set_connected(self, connected: bool, target: Optional[str] = None) -> None:
        """Met à jour l'état de connexion du terminal"""
        if connected:
            self.status_label.setText(f"Connecté: {target or 'Système local'}")
            self.status_label.setStyleSheet("color: #00FF00;")
        else:
            self.status_label.setText("Déconnecté")
            self.status_label.setStyleSheet("color: #FF0000;")
    
    def _update_fx(self) -> None:
        """Met à jour les effets visuels du terminal"""
        # À implémenter: effets visuels comme des glitches, des animations, etc.
        pass
    
    def update_ui(self, delta_time: float) -> None:
        """Met à jour l'interface utilisateur du terminal"""
        # Mise à jour des effets visuels, animations, etc.
        pass
