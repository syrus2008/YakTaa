#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de la boîte de dialogue de bienvenue
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWizard, QWizardPage, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

logger = logging.getLogger(__name__)

class WelcomeDialog(QDialog):
    """Boîte de dialogue de bienvenue affichée au premier lancement"""
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de la boîte de dialogue
        self.setWindowTitle("Bienvenue dans YakTaa World Editor")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("Bienvenue dans YakTaa World Editor")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        description_label = QLabel(
            "Cet éditeur vous permet de créer et de modifier des mondes pour le jeu YakTaa.\n\n"
            "Vous pouvez générer des mondes aléatoires ou créer vos propres mondes en ajoutant "
            "des lieux, des personnages, des appareils et des connexions.\n\n"
            "Pour commencer, vous pouvez :\n"
            "- Créer un nouveau monde en utilisant le générateur\n"
            "- Ouvrir un monde existant\n"
            "- Importer un monde depuis un fichier JSON"
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description_label)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        start_button = QPushButton("Commencer")
        start_button.clicked.connect(self.accept)
        buttons_layout.addWidget(start_button)
        
        tutorial_button = QPushButton("Voir le tutoriel")
        tutorial_button.clicked.connect(self.show_tutorial)
        buttons_layout.addWidget(tutorial_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Case à cocher pour ne plus afficher
        self.dont_show_check = QCheckBox("Ne plus afficher ce message")
        main_layout.addWidget(self.dont_show_check)
    
    def show_tutorial(self):
        """Affiche le tutoriel"""
        
        tutorial = TutorialWizard()
        tutorial.exec()

class TutorialWizard(QWizard):
    """Assistant de tutoriel"""
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        
        # Configuration de l'assistant
        self.setWindowTitle("Tutoriel YakTaa World Editor")
        self.setMinimumSize(700, 500)
        
        # Page 1 : Introduction
        intro_page = QWizardPage()
        intro_page.setTitle("Introduction")
        
        intro_layout = QVBoxLayout(intro_page)
        
        intro_label = QLabel(
            "Bienvenue dans ce tutoriel qui vous guidera à travers les fonctionnalités "
            "de l'éditeur de monde YakTaa.\n\n"
            "Cet éditeur vous permet de créer des mondes riches et complexes pour le jeu YakTaa, "
            "avec des lieux, des personnages, des appareils et des connexions entre eux."
        )
        intro_label.setWordWrap(True)
        intro_layout.addWidget(intro_label)
        
        self.addPage(intro_page)
        
        # Page 2 : Création d'un monde
        create_page = QWizardPage()
        create_page.setTitle("Création d'un monde")
        
        create_layout = QVBoxLayout(create_page)
        
        create_label = QLabel(
            "Pour créer un nouveau monde, vous pouvez utiliser le générateur de monde.\n\n"
            "1. Cliquez sur 'Fichier > Nouveau monde' ou sur le bouton 'Nouveau' dans la barre d'outils.\n"
            "2. Remplissez les informations de base du monde (nom, auteur, complexité).\n"
            "3. Définissez les paramètres de génération (nombre de villes, de lieux spéciaux, etc.).\n"
            "4. Cliquez sur 'Générer' pour créer le monde."
        )
        create_label.setWordWrap(True)
        create_layout.addWidget(create_label)
        
        self.addPage(create_page)
        
        # Page 3 : Édition d'un monde
        edit_page = QWizardPage()
        edit_page.setTitle("Édition d'un monde")
        
        edit_layout = QVBoxLayout(edit_page)
        
        edit_label = QLabel(
            "Une fois votre monde créé, vous pouvez l'éditer :\n\n"
            "1. Utilisez la vue de carte pour visualiser les lieux et les connexions.\n"
            "2. Ajoutez de nouveaux lieux, personnages et appareils via les menus ou les boutons.\n"
            "3. Modifiez les propriétés des éléments existants en les sélectionnant dans les listes.\n"
            "4. Créez des connexions entre les lieux dans l'onglet 'Connexions'.\n"
            "5. N'oubliez pas de sauvegarder régulièrement votre travail."
        )
        edit_label.setWordWrap(True)
        edit_layout.addWidget(edit_label)
        
        self.addPage(edit_page)
        
        # Page 4 : Exportation et importation
        export_page = QWizardPage()
        export_page.setTitle("Exportation et importation")
        
        export_layout = QVBoxLayout(export_page)
        
        export_label = QLabel(
            "Vous pouvez exporter vos mondes pour les partager ou les sauvegarder :\n\n"
            "1. Ouvrez le monde que vous souhaitez exporter.\n"
            "2. Cliquez sur 'Fichier > Exporter monde'.\n"
            "3. Choisissez l'emplacement et le nom du fichier JSON.\n\n"
            "Pour importer un monde :\n"
            "1. Cliquez sur 'Fichier > Importer monde'.\n"
            "2. Sélectionnez le fichier JSON contenant le monde à importer."
        )
        export_label.setWordWrap(True)
        export_layout.addWidget(export_label)
        
        self.addPage(export_page)
        
        # Page 5 : Conclusion
        conclusion_page = QWizardPage()
        conclusion_page.setTitle("Conclusion")
        
        conclusion_layout = QVBoxLayout(conclusion_page)
        
        conclusion_label = QLabel(
            "Vous êtes maintenant prêt à utiliser l'éditeur de monde YakTaa !\n\n"
            "N'hésitez pas à explorer toutes les fonctionnalités et à créer des mondes riches et détaillés "
            "pour votre jeu YakTaa.\n\n"
            "Bon jeu !"
        )
        conclusion_label.setWordWrap(True)
        conclusion_layout.addWidget(conclusion_label)
        
        self.addPage(conclusion_page)
