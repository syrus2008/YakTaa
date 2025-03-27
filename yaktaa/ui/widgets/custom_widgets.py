"""
Module contenant des widgets personnalisés pour l'interface utilisateur de YakTaa
"""

import math
from typing import Optional, Union

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QSize, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QRadialGradient, QConicalGradient

class QRadialBar(QWidget):
    """
    Widget personnalisé pour afficher une barre de progression circulaire
    Inspiré des designs cyberpunk pour l'affichage des statistiques
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Propriétés par défaut
        self._min = 0
        self._max = 100
        self._value = 25
        
        # Apparence
        self._foreground_color = QColor(0, 200, 255)  # Bleu cyberpunk
        self._background_color = QColor(20, 20, 30)   # Fond sombre
        self._text_color = QColor(220, 220, 220)      # Texte clair
        
        self._suffix = "%"
        self._precision = 0
        self._dial_width = 25
        self._show_text = True
        self._text_font = QFont("Orbitron", 12)
        
        # Taille minimale
        self.setMinimumSize(80, 80)
    
    def paintEvent(self, event):
        """Dessine le widget"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculer le rectangle
        rect = self.rect()
        size = min(rect.width(), rect.height())
        
        # Ajuster le rectangle pour le centrer
        rect.setWidth(size)
        rect.setHeight(size)
        rect.moveCenter(self.rect().center())
        
        # Calculer la valeur en pourcentage
        progress = (self._value - self._min) / (self._max - self._min)
        angle = progress * 360
        
        # Dessiner le fond
        center = rect.center()
        radius = size / 2 - self._dial_width / 2
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Fond avec dégradé radial
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, self._background_color.darker(150))
        gradient.setColorAt(1, self._background_color)
        painter.setBrush(gradient)
        
        # Dessiner le cercle de fond
        painter.drawEllipse(center, radius, radius)
        
        # Dessiner l'arc de progression
        pen = QPen(self._foreground_color)
        pen.setWidth(self._dial_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Dessiner l'arc de progression avec un dégradé conique
        rect_arc = QRectF(
            self._dial_width / 2,
            self._dial_width / 2,
            size - self._dial_width,
            size - self._dial_width
        )
        
        # Dessiner l'arc de progression
        start_angle = 90 * 16  # 90 degrés en unités QPainter (1 degré = 16 unités)
        span_angle = -angle * 16  # Angle négatif pour aller dans le sens horaire
        painter.drawArc(rect_arc, start_angle, span_angle)
        
        # Dessiner le texte si nécessaire
        if self._show_text:
            painter.setPen(self._text_color)
            painter.setFont(self._text_font)
            
            # Formater le texte avec la précision demandée
            text = f"{self._value:.{self._precision}f}{self._suffix}"
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def sizeHint(self):
        """Taille suggérée pour le widget"""
        return QSize(120, 120)
    
    def minimumSizeHint(self):
        """Taille minimale pour le widget"""
        return QSize(80, 80)
    
    # Propriétés
    @pyqtProperty(int)
    def minimum(self):
        return self._min
    
    @minimum.setter
    def minimum(self, value):
        self._min = value
        self.update()
    
    @pyqtProperty(int)
    def maximum(self):
        return self._max
    
    @maximum.setter
    def maximum(self, value):
        self._max = value
        self.update()
    
    @pyqtProperty(int)
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = max(self._min, min(self._max, value))
            self.valueChanged.emit(self._value)
            self.update()
    
    @pyqtProperty(QColor)
    def foregroundColor(self):
        return self._foreground_color
    
    @foregroundColor.setter
    def foregroundColor(self, color):
        self._foreground_color = color
        self.update()
    
    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._background_color
    
    @backgroundColor.setter
    def backgroundColor(self, color):
        self._background_color = color
        self.update()
    
    @pyqtProperty(QColor)
    def textColor(self):
        return self._text_color
    
    @textColor.setter
    def textColor(self, color):
        self._text_color = color
        self.update()
    
    @pyqtProperty(str)
    def suffix(self):
        return self._suffix
    
    @suffix.setter
    def suffix(self, text):
        self._suffix = text
        self.update()
    
    @pyqtProperty(int)
    def dialWidth(self):
        return self._dial_width
    
    @dialWidth.setter
    def dialWidth(self, width):
        self._dial_width = width
        self.update()
    
    @pyqtProperty(bool)
    def showText(self):
        return self._show_text
    
    @showText.setter
    def showText(self, show):
        self._show_text = show
        self.update()
    
    @pyqtProperty(QFont)
    def textFont(self):
        return self._text_font
    
    @textFont.setter
    def textFont(self, font):
        self._text_font = font
        self.update()
    
    @pyqtProperty(int)
    def precision(self):
        return self._precision
    
    @precision.setter
    def precision(self, precision):
        self._precision = precision
        self.update()
