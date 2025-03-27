"""
Module pour l'écran de paramètres du jeu YakTaa
"""

import logging
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy, QComboBox,
    QSlider, QCheckBox, QTabWidget, QScrollArea,
    QGroupBox, QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from yaktaa.ui.screens.base_screen import BaseScreen
from yaktaa.core.game import Game

logger = logging.getLogger("YakTaa.UI.SettingsScreen")

class SettingsScreen(BaseScreen):
    """Écran de paramètres du jeu"""
    
    def __init__(self, game: Game, parent: Optional[QWidget] = None):
        """Initialise l'écran de paramètres"""
        super().__init__(game, parent)
        
        # Dictionnaire pour stocker les widgets de paramètres
        self.setting_widgets = {}
        
        # Configuration d'origine (pour annuler les modifications)
        self.original_config = {}
        
        logger.info("Écran de paramètres initialisé")
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur de l'écran de paramètres"""
        # Titre
        title = self.create_heading("Paramètres", 1)
        self.layout.addWidget(title)
        
        # Onglets de paramètres
        self.tabs = QTabWidget(self)
        self.layout.addWidget(self.tabs)
        
        # Création des onglets
        self._create_general_tab()
        self._create_graphics_tab()
        self._create_audio_tab()
        self._create_gameplay_tab()
        self._create_interface_tab()
        
        # Boutons de contrôle
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Bouton Retour
        self.back_btn = QPushButton("Retour", self)
        self.back_btn.clicked.connect(self.on_back)
        button_layout.addWidget(self.back_btn)
        
        # Espacement
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Bouton Réinitialiser
        self.reset_btn = QPushButton("Réinitialiser", self)
        self.reset_btn.clicked.connect(self.on_reset)
        button_layout.addWidget(self.reset_btn)
        
        # Bouton Appliquer
        self.apply_btn = QPushButton("Appliquer", self)
        self.apply_btn.clicked.connect(self.on_apply)
        button_layout.addWidget(self.apply_btn)
        
        self.layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> None:
        """Crée l'onglet des paramètres généraux"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe Langue
        language_group = QGroupBox("Langue", tab)
        language_layout = QFormLayout(language_group)
        
        # Sélection de la langue
        language_combo = QComboBox(language_group)
        language_combo.addItem("Français", "fr")
        language_combo.addItem("English", "en")
        
        # Sélection de la langue actuelle
        current_lang = self.game.config.get("language", "fr")
        index = language_combo.findData(current_lang)
        if index >= 0:
            language_combo.setCurrentIndex(index)
        
        language_layout.addRow("Langue du jeu:", language_combo)
        self.setting_widgets["language"] = language_combo
        
        layout.addWidget(language_group)
        
        # Groupe Sauvegarde
        save_group = QGroupBox("Sauvegarde", tab)
        save_layout = QFormLayout(save_group)
        
        # Sauvegarde automatique
        auto_save = QCheckBox(save_group)
        auto_save.setChecked(self.game.config.get("auto_save", True))
        save_layout.addRow("Sauvegarde automatique:", auto_save)
        self.setting_widgets["auto_save"] = auto_save
        
        # Intervalle de sauvegarde
        auto_save_interval = QSpinBox(save_group)
        auto_save_interval.setMinimum(5)
        auto_save_interval.setMaximum(60)
        auto_save_interval.setSingleStep(5)
        auto_save_interval.setValue(self.game.config.get("auto_save_interval", 15))
        auto_save_interval.setSuffix(" min")
        save_layout.addRow("Intervalle:", auto_save_interval)
        self.setting_widgets["auto_save_interval"] = auto_save_interval
        
        # Sauvegarde à la sortie
        auto_save_on_quit = QCheckBox(save_group)
        auto_save_on_quit.setChecked(self.game.config.get("auto_save_on_quit", True))
        save_layout.addRow("Sauvegarder en quittant:", auto_save_on_quit)
        self.setting_widgets["auto_save_on_quit"] = auto_save_on_quit
        
        layout.addWidget(save_group)
        
        # Espacement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.tabs.addTab(tab, "Général")
    
    def _create_graphics_tab(self) -> None:
        """Crée l'onglet des paramètres graphiques"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe Affichage
        display_group = QGroupBox("Affichage", tab)
        display_layout = QFormLayout(display_group)
        
        # Plein écran
        fullscreen = QCheckBox(display_group)
        fullscreen.setChecked(self.game.config.get("fullscreen", False))
        display_layout.addRow("Plein écran:", fullscreen)
        self.setting_widgets["fullscreen"] = fullscreen
        
        # Résolution
        resolution_combo = QComboBox(display_group)
        resolutions = [
            "1280x720", "1366x768", "1600x900", "1920x1080", 
            "2560x1440", "3840x2160"
        ]
        for res in resolutions:
            resolution_combo.addItem(res)
        
        # Sélection de la résolution actuelle
        current_res = self.game.config.get("resolution", (1280, 720))
        current_res_str = f"{current_res[0]}x{current_res[1]}"
        index = resolution_combo.findText(current_res_str)
        if index >= 0:
            resolution_combo.setCurrentIndex(index)
        
        display_layout.addRow("Résolution:", resolution_combo)
        self.setting_widgets["resolution"] = resolution_combo
        
        # VSync
        vsync = QCheckBox(display_group)
        vsync.setChecked(self.game.config.get("vsync", True))
        display_layout.addRow("VSync:", vsync)
        self.setting_widgets["vsync"] = vsync
        
        # Limite de FPS
        fps_limit = QSpinBox(display_group)
        fps_limit.setMinimum(30)
        fps_limit.setMaximum(240)
        fps_limit.setSingleStep(10)
        fps_limit.setValue(self.game.config.get("fps_limit", 60))
        fps_limit.setSuffix(" FPS")
        display_layout.addRow("Limite de FPS:", fps_limit)
        self.setting_widgets["fps_limit"] = fps_limit
        
        # Afficher les FPS
        show_fps = QCheckBox(display_group)
        show_fps.setChecked(self.game.config.get("show_fps", False))
        display_layout.addRow("Afficher les FPS:", show_fps)
        self.setting_widgets["show_fps"] = show_fps
        
        layout.addWidget(display_group)
        
        # Groupe Effets visuels
        effects_group = QGroupBox("Effets visuels", tab)
        effects_layout = QFormLayout(effects_group)
        
        # Vitesse d'animation
        animation_speed = QSlider(Qt.Orientation.Horizontal, effects_group)
        animation_speed.setMinimum(50)
        animation_speed.setMaximum(200)
        animation_speed.setSingleStep(10)
        animation_speed.setValue(int(self.game.config.get("animation_speed", 1.0) * 100))
        effects_layout.addRow("Vitesse d'animation:", animation_speed)
        self.setting_widgets["animation_speed"] = animation_speed
        
        layout.addWidget(effects_group)
        
        # Espacement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.tabs.addTab(tab, "Graphismes")
    
    def _create_audio_tab(self) -> None:
        """Crée l'onglet des paramètres audio"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe Volume
        volume_group = QGroupBox("Volume", tab)
        volume_layout = QFormLayout(volume_group)
        
        # Volume principal
        master_volume = QSlider(Qt.Orientation.Horizontal, volume_group)
        master_volume.setMinimum(0)
        master_volume.setMaximum(100)
        master_volume.setSingleStep(5)
        master_volume.setValue(int(self.game.config.get("master_volume", 0.8) * 100))
        volume_layout.addRow("Volume principal:", master_volume)
        self.setting_widgets["master_volume"] = master_volume
        
        # Volume de la musique
        music_volume = QSlider(Qt.Orientation.Horizontal, volume_group)
        music_volume.setMinimum(0)
        music_volume.setMaximum(100)
        music_volume.setSingleStep(5)
        music_volume.setValue(int(self.game.config.get("music_volume", 0.7) * 100))
        volume_layout.addRow("Musique:", music_volume)
        self.setting_widgets["music_volume"] = music_volume
        
        # Volume des effets sonores
        sfx_volume = QSlider(Qt.Orientation.Horizontal, volume_group)
        sfx_volume.setMinimum(0)
        sfx_volume.setMaximum(100)
        sfx_volume.setSingleStep(5)
        sfx_volume.setValue(int(self.game.config.get("sfx_volume", 0.9) * 100))
        volume_layout.addRow("Effets sonores:", sfx_volume)
        self.setting_widgets["sfx_volume"] = sfx_volume
        
        # Volume des voix
        voice_volume = QSlider(Qt.Orientation.Horizontal, volume_group)
        voice_volume.setMinimum(0)
        voice_volume.setMaximum(100)
        voice_volume.setSingleStep(5)
        voice_volume.setValue(int(self.game.config.get("voice_volume", 1.0) * 100))
        volume_layout.addRow("Voix:", voice_volume)
        self.setting_widgets["voice_volume"] = voice_volume
        
        # Muet
        mute = QCheckBox(volume_group)
        mute.setChecked(self.game.config.get("mute", False))
        volume_layout.addRow("Muet:", mute)
        self.setting_widgets["mute"] = mute
        
        layout.addWidget(volume_group)
        
        # Espacement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.tabs.addTab(tab, "Audio")
    
    def _create_gameplay_tab(self) -> None:
        """Crée l'onglet des paramètres de gameplay"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe Difficulté
        difficulty_group = QGroupBox("Difficulté", tab)
        difficulty_layout = QFormLayout(difficulty_group)
        
        # Niveau de difficulté
        difficulty_combo = QComboBox(difficulty_group)
        difficulty_combo.addItem("Facile", "easy")
        difficulty_combo.addItem("Normal", "normal")
        difficulty_combo.addItem("Difficile", "hard")
        difficulty_combo.addItem("Expert", "expert")
        
        # Sélection de la difficulté actuelle
        current_difficulty = self.game.config.get("difficulty", "normal")
        index = difficulty_combo.findData(current_difficulty)
        if index >= 0:
            difficulty_combo.setCurrentIndex(index)
        
        difficulty_layout.addRow("Niveau de difficulté:", difficulty_combo)
        self.setting_widgets["difficulty"] = difficulty_combo
        
        layout.addWidget(difficulty_group)
        
        # Espacement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.tabs.addTab(tab, "Gameplay")
    
    def _create_interface_tab(self) -> None:
        """Crée l'onglet des paramètres d'interface"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe Interface utilisateur
        ui_group = QGroupBox("Interface utilisateur", tab)
        ui_layout = QFormLayout(ui_group)
        
        # Échelle de l'interface
        ui_scale = QSlider(Qt.Orientation.Horizontal, ui_group)
        ui_scale.setMinimum(50)
        ui_scale.setMaximum(150)
        ui_scale.setSingleStep(10)
        ui_scale.setValue(int(self.game.config.get("ui_scale", 1.0) * 100))
        ui_layout.addRow("Échelle de l'interface:", ui_scale)
        self.setting_widgets["ui_scale"] = ui_scale
        
        # Thème de l'interface
        ui_theme = QComboBox(ui_group)
        themes = self.main_window.theme.get_all_themes()
        for theme_id, theme_name in themes.items():
            ui_theme.addItem(theme_name, theme_id)
        
        # Sélection du thème actuel
        current_theme = self.game.config.get("ui_theme", "cyberpunk_dark")
        index = ui_theme.findData(current_theme)
        if index >= 0:
            ui_theme.setCurrentIndex(index)
        
        ui_layout.addRow("Thème:", ui_theme)
        self.setting_widgets["ui_theme"] = ui_theme
        
        # Afficher les infobulles
        show_tooltips = QCheckBox(ui_group)
        show_tooltips.setChecked(self.game.config.get("show_tooltips", True))
        ui_layout.addRow("Afficher les infobulles:", show_tooltips)
        self.setting_widgets["show_tooltips"] = show_tooltips
        
        layout.addWidget(ui_group)
        
        # Groupe Terminal
        terminal_group = QGroupBox("Terminal", tab)
        terminal_layout = QFormLayout(terminal_group)
        
        # Taille de police du terminal
        terminal_font_size = QSpinBox(terminal_group)
        terminal_font_size.setMinimum(8)
        terminal_font_size.setMaximum(24)
        terminal_font_size.setSingleStep(1)
        terminal_font_size.setValue(self.game.config.get("terminal_font_size", 12))
        terminal_layout.addRow("Taille de police:", terminal_font_size)
        self.setting_widgets["terminal_font_size"] = terminal_font_size
        
        # Police du terminal
        terminal_font = QComboBox(terminal_group)
        terminal_font.addItem("Cascadia Code", "Cascadia Code")
        terminal_font.addItem("Consolas", "Consolas")
        terminal_font.addItem("Courier New", "Courier New")
        
        # Sélection de la police actuelle
        current_font = self.game.config.get("terminal_font", "Cascadia Code")
        index = terminal_font.findData(current_font)
        if index >= 0:
            terminal_font.setCurrentIndex(index)
        
        terminal_layout.addRow("Police:", terminal_font)
        self.setting_widgets["terminal_font"] = terminal_font
        
        # Opacité du terminal
        terminal_opacity = QSlider(Qt.Orientation.Horizontal, terminal_group)
        terminal_opacity.setMinimum(50)
        terminal_opacity.setMaximum(100)
        terminal_opacity.setSingleStep(5)
        terminal_opacity.setValue(int(self.game.config.get("terminal_opacity", 0.9) * 100))
        terminal_layout.addRow("Opacité:", terminal_opacity)
        self.setting_widgets["terminal_opacity"] = terminal_opacity
        
        layout.addWidget(terminal_group)
        
        # Espacement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.tabs.addTab(tab, "Interface")
    
    def on_show(self) -> None:
        """Appelé lorsque l'écran est affiché"""
        super().on_show()
        
        # Sauvegarde de la configuration d'origine
        self.original_config = self.game.config.get_all()
        
        # Mise à jour des widgets avec les valeurs actuelles
        self._update_widgets_from_config()
    
    def _update_widgets_from_config(self) -> None:
        """Met à jour les widgets avec les valeurs de la configuration"""
        config = self.game.config.get_all()
        
        for key, widget in self.setting_widgets.items():
            value = config.get(key)
            
            if isinstance(widget, QComboBox):
                index = widget.findData(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
            
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value)
            
            elif isinstance(widget, QSlider):
                # Pour les valeurs entre 0 et 1, on les multiplie par 100
                if isinstance(value, float) and 0 <= value <= 1:
                    widget.setValue(int(value * 100))
                else:
                    widget.setValue(value)
            
            elif isinstance(widget, QSpinBox):
                widget.setValue(value)
    
    def _update_config_from_widgets(self) -> None:
        """Met à jour la configuration avec les valeurs des widgets"""
        for key, widget in self.setting_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentData()
                self.game.config.set(key, value)
            
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
                self.game.config.set(key, value)
            
            elif isinstance(widget, QSlider):
                value = widget.value()
                
                # Pour les valeurs entre 0 et 1, on les divise par 100
                if key in ["master_volume", "music_volume", "sfx_volume", "voice_volume", "ui_scale", "terminal_opacity", "animation_speed"]:
                    value = value / 100.0
                
                self.game.config.set(key, value)
            
            elif isinstance(widget, QSpinBox):
                value = widget.value()
                self.game.config.set(key, value)
            
            # Cas particulier pour la résolution
            if key == "resolution" and isinstance(widget, QComboBox):
                res_str = widget.currentText()
                width, height = map(int, res_str.split("x"))
                self.game.config.set(key, (width, height))
    
    def on_apply(self) -> None:
        """Gère le clic sur le bouton Appliquer"""
        logger.info("Application des paramètres")
        
        # Mise à jour de la configuration
        self._update_config_from_widgets()
        
        # Sauvegarde de la configuration
        self.game.config.save()
        
        # Application des changements visuels
        self._apply_visual_changes()
    
    def on_reset(self) -> None:
        """Gère le clic sur le bouton Réinitialiser"""
        logger.info("Réinitialisation des paramètres")
        
        # Réinitialisation de la configuration
        self.game.config.reset()
        
        # Mise à jour des widgets
        self._update_widgets_from_config()
        
        # Application des changements visuels
        self._apply_visual_changes()
    
    def on_back(self) -> None:
        """Gère le clic sur le bouton Retour"""
        logger.info("Retour au menu principal")
        
        # Restauration de la configuration d'origine si les changements n'ont pas été appliqués
        for key, value in self.original_config.items():
            self.game.config.set(key, value)
        
        # Retour au menu principal
        self.show_screen("main_menu")
    
    def _apply_visual_changes(self) -> None:
        """Applique les changements visuels"""
        # Changement de thème
        theme_id = self.game.config.get("ui_theme")
        self.main_window.theme.change_theme(theme_id)
        self.main_window.theme.apply_to_application(self.main_window.parent())
