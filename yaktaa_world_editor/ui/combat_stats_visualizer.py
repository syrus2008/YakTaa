#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de visualisation des statistiques de combat avec des graphiques radar
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QApplication)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QPen, QBrush, QPolygon, QColor, QPainterPath, QFont
from PyQt6.QtCore import QPoint


class RadarChartWidget(QWidget):
    """Widget de graphique radar pour visualiser les statistiques de combat"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Données par défaut
        self.labels = ["Santé", "Dégâts", "Précision", "Initiative", "Résistance"]
        self.values = [0.5, 0.5, 0.5, 0.5, 0.5]  # Valeurs normalisées (0-1)
        self.colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"]
        self.bg_color = QColor(30, 30, 40)
        self.grid_color = QColor(60, 60, 70)
        self.text_color = QColor(200, 200, 210)
        self.highlight_color = QColor(80, 80, 100)
        
        self.show_values = True
        self.title = "Statistiques de Combat"
        
        # Style du graphique
        self.line_width = 2
        self.num_levels = 5  # Nombre de niveaux dans la grille
        
    def set_data(self, labels, values, normalize=True):
        """
        Définit les données du graphique radar
        
        Args:
            labels: Liste d'étiquettes pour chaque axe
            values: Liste de valeurs correspondantes
            normalize: Si True, normalise les valeurs entre 0 et 1
        """
        if len(labels) != len(values):
            raise ValueError("Les listes d'étiquettes et de valeurs doivent avoir la même longueur")
            
        self.labels = labels
        
        if normalize:
            # Normalisation des valeurs entre 0 et 1
            max_value = max(values) if max(values) > 0 else 1
            self.values = [v / max_value for v in values]
        else:
            # Assurez-vous que les valeurs sont entre 0 et 1
            self.values = [max(0, min(v, 1)) for v in values]
            
        self.update()
        
    def set_title(self, title):
        """Définit le titre du graphique"""
        self.title = title
        self.update()
        
    def set_colors(self, fill_color, grid_color=None, text_color=None, bg_color=None):
        """
        Définit les couleurs du graphique
        
        Args:
            fill_color: Couleur de remplissage du polygone (peut être une liste de couleurs)
            grid_color: Couleur de la grille
            text_color: Couleur du texte
            bg_color: Couleur d'arrière-plan
        """
        if isinstance(fill_color, list):
            self.colors = fill_color
        else:
            self.colors = [fill_color] * len(self.labels)
            
        if grid_color:
            self.grid_color = QColor(grid_color)
        if text_color:
            self.text_color = QColor(text_color)
        if bg_color:
            self.bg_color = QColor(bg_color)
            
        self.update()
    
    def show_numeric_values(self, show=True):
        """Active/désactive l'affichage des valeurs numériques"""
        self.show_values = show
        self.update()
        
    def paintEvent(self, event):
        """Gestionnaire d'événement de dessin"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner l'arrière-plan
        painter.fillRect(self.rect(), self.bg_color)
        
        # Calculer le centre et le rayon
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 50  # Marge pour le texte
        
        # Dessiner le titre
        painter.setPen(self.text_color)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        painter.setFont(title_font)
        painter.drawText(0, 10, width, 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Dessiner la grille de fond
        self._draw_grid(painter, center_x, center_y, radius)
        
        # Dessiner les axes et les étiquettes
        self._draw_axes(painter, center_x, center_y, radius)
        
        # Dessiner le polygone des données
        self._draw_data_polygon(painter, center_x, center_y, radius)
        
    def _draw_grid(self, painter, cx, cy, radius):
        """Dessine la grille de fond"""
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DashLine))
        
        # Dessiner les cercles concentriques
        for i in range(1, self.num_levels + 1):
            level_radius = radius * i / self.num_levels
            painter.drawEllipse(cx - level_radius, cy - level_radius, 
                               level_radius * 2, level_radius * 2)
        
    def _draw_axes(self, painter, cx, cy, radius):
        """Dessine les axes et les étiquettes"""
        n = len(self.labels)
        
        # Police pour les étiquettes
        label_font = QFont()
        label_font.setPointSize(9)
        painter.setFont(label_font)
        
        for i in range(n):
            angle = 2 * np.pi * i / n - np.pi / 2  # Commencer à midi, sens horaire
            
            # Coordonnées de l'extrémité de l'axe
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)
            
            # Dessiner l'axe
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.SolidLine))
            painter.drawLine(cx, cy, int(x), int(y))
            
            # Position de l'étiquette (un peu à l'extérieur du cercle)
            label_radius = radius * 1.15
            lx = cx + label_radius * np.cos(angle)
            ly = cy + label_radius * np.sin(angle)
            
            # Alignement du texte en fonction de la position
            flags = Qt.AlignmentFlag.AlignCenter
            
            # Dessiner l'étiquette avec une zone plus large
            text_width = 80
            text_height = 30
            text_x = int(lx - text_width // 2)
            text_y = int(ly - text_height // 2)
            
            painter.setPen(self.text_color)
            painter.drawText(text_x, text_y, text_width, text_height, flags, self.labels[i])
            
            # Dessiner les valeurs numériques si activé
            if self.show_values:
                value_radius = radius * 0.6  # Plus proche du centre
                value_angle = angle  # Même angle que l'étiquette
                
                # Calculer la position de la valeur (sur l'axe)
                vx = cx + value_radius * np.cos(angle) * self.values[i]
                vy = cy + value_radius * np.sin(angle) * self.values[i]
                
                # Dessiner un cercle de fond pour la valeur
                painter.setBrush(QBrush(self.highlight_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(vx) - 15, int(vy) - 10, 30, 20)
                
                # Dessiner la valeur
                painter.setPen(self.text_color)
                
                # Formatage de la valeur (pourcentage)
                display_value = f"{int(self.values[i] * 100)}%"
                painter.drawText(int(vx) - 15, int(vy) - 10, 30, 20, 
                                Qt.AlignmentFlag.AlignCenter, display_value)
    
    def _draw_data_polygon(self, painter, cx, cy, radius):
        """Dessine le polygone des données"""
        n = len(self.values)
        
        # Créer un chemin pour le polygone
        path = QPainterPath()
        
        # Ajouter les points au polygone
        for i in range(n):
            angle = 2 * np.pi * i / n - np.pi / 2  # Commencer à midi, sens horaire
            
            # Calculer la position du point (normalisée par la valeur)
            x = cx + radius * np.cos(angle) * self.values[i]
            y = cy + radius * np.sin(angle) * self.values[i]
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        # Fermer le chemin
        path.closeSubpath()
        
        # Dessiner le polygone avec transparence
        fill_color = QColor(self.colors[0])
        fill_color.setAlpha(150)  # Semi-transparent
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(QColor(self.colors[0]), self.line_width))
        painter.drawPath(path)
        
        # Dessiner les points aux sommets
        for i in range(n):
            angle = 2 * np.pi * i / n - np.pi / 2
            x = cx + radius * np.cos(angle) * self.values[i]
            y = cy + radius * np.sin(angle) * self.values[i]
            
            # Dessiner un cercle à chaque sommet
            point_color = QColor(self.colors[i % len(self.colors)])
            painter.setBrush(QBrush(point_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)


class ResistancesRadarChart(RadarChartWidget):
    """Widget spécialisé pour visualiser les résistances aux dommages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialiser avec les types de résistances
        self.labels = ["Physique", "Énergie", "EMP", "Biohazard", "Cyber", "Viral", "Nanite"]
        self.values = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
        self.title = "Résistances aux Dommages"
        
        # Couleurs pour chaque type de résistance
        self.colors = ["#e74c3c", "#3498db", "#f39c12", "#2ecc71", 
                       "#9b59b6", "#1abc9c", "#d35400"]
    
    def set_resistances(self, resistances_dict):
        """
        Définit les résistances à partir d'un dictionnaire
        
        Args:
            resistances_dict: Dictionnaire avec les clés correspondant aux types de résistance
                             et les valeurs correspondant aux pourcentages (0-100)
        """
        values = []
        for label in self.labels:
            key = label.lower()
            if key in resistances_dict:
                values.append(resistances_dict[key] / 100)  # Normaliser à 0-1
            else:
                values.append(0)
                
        self.values = values
        self.update()


class CombatStatsVisualizer(QWidget):
    """Widget principal pour visualiser les statistiques de combat"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Créer la disposition principale
        main_layout = QHBoxLayout(self)
        
        # Graphique radar pour les stats principales
        self.stats_chart = RadarChartWidget(self)
        self.stats_chart.set_title("Statistiques de Combat")
        
        # Graphique radar pour les résistances
        self.resistances_chart = ResistancesRadarChart(self)
        
        # Ajouter les graphiques à la disposition
        main_layout.addWidget(self.stats_chart)
        main_layout.addWidget(self.resistances_chart)
        
        # Initialiser les données
        self._init_demo_data()
        
    def _init_demo_data(self):
        """Initialise des données de démonstration"""
        # Stats de combat
        self.stats_chart.set_data(
            ["Santé", "Dégâts", "Précision", "Initiative", "Hostilité"],
            [100, 15, 75, 8, 50],
            normalize=True
        )
        
        # Résistances
        self.resistances_chart.set_resistances({
            "physique": 40,
            "énergie": 30,
            "emp": 20,
            "biohazard": 60,
            "cyber": 45,
            "viral": 35,
            "nanite": 25
        })
        
    def set_character_stats(self, character_data):
        """
        Définit les données du personnage à visualiser
        
        Args:
            character_data: Dictionnaire contenant les statistiques du personnage
        """
        # Stats principales
        stats_values = [
            character_data.get("health", 0),
            character_data.get("damage", 0),
            character_data.get("accuracy", 0) * 100,  # Convertir en pourcentage
            character_data.get("initiative", 0),
            character_data.get("hostility", 0)
        ]
        
        self.stats_chart.set_data(
            ["Santé", "Dégâts", "Précision", "Initiative", "Hostilité"],
            stats_values,
            normalize=True
        )
        
        # Résistances
        resistances = {
            "physique": character_data.get("resistance_physical", 0),
            "énergie": character_data.get("resistance_energy", 0),
            "emp": character_data.get("resistance_emp", 0),
            "biohazard": character_data.get("resistance_biohazard", 0),
            "cyber": character_data.get("resistance_cyber", 0),
            "viral": character_data.get("resistance_viral", 0),
            "nanite": character_data.get("resistance_nanite", 0)
        }
        
        self.resistances_chart.set_resistances(resistances)


# Test du module
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CombatStatsVisualizer()
    window.setWindowTitle("Test de Visualisation des Statistiques de Combat")
    window.resize(800, 400)
    window.show()
    sys.exit(app.exec())
