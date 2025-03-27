#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module principal de l'éditeur de monde YakTaa
Ce module lance l'interface graphique de l'éditeur
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings

from ui.main_window import MainWindow
from database import WorldDatabase, get_database

# Importer les modules de vérification et correction de la base de données
from db_structure_fix import DatabaseStructureFix

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("world_editor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def verify_and_fix_database(db_path):
    """
    Vérifie et corrige la structure de la base de données si nécessaire
    
    Args:
        db_path: Chemin vers le fichier de base de données
        
    Returns:
        True si la base de données est prête à être utilisée, False sinon
    """
    try:
        # Vérifier si le fichier existe
        db_exists = os.path.exists(db_path)
        
        if not db_exists:
            logger.info(f"Base de données non trouvée à {db_path}, elle sera créée automatiquement")
            return True
        
        # Si la base de données existe, vérifier et corriger sa structure
        logger.info(f"Vérification et correction de la structure de la base de données: {db_path}")
        fixer = DatabaseStructureFix(db_path)
        result = fixer.fix_database_structure()
        fixer.close()
        
        if result:
            logger.info("Structure de la base de données vérifiée et corrigée avec succès")
        else:
            logger.error("Échec de la vérification/correction de la structure de la base de données")
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/correction de la base de données: {e}")
        return False

def main():
    """Point d'entrée principal de l'application"""
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("YakTaa World Editor")
    app.setOrganizationName("YakTaa")
    
    # Charger les paramètres
    settings = QSettings()
    
    # Vérifier si c'est la première exécution
    first_run = settings.value("first_run", True, type=bool)
    
    # Initialiser la base de données
    db_path = settings.value("db_path", os.path.join(os.path.dirname(__file__), "worlds.db"))
    
    # Vérifier et corriger la structure de la base de données
    if not verify_and_fix_database(db_path):
        # Afficher un message d'erreur si la vérification/correction a échoué
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Erreur de base de données")
        error_dialog.setText("Impossible de vérifier ou corriger la structure de la base de données.")
        error_dialog.setInformativeText("L'application peut ne pas fonctionner correctement. Consultez le fichier de log pour plus de détails.")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()
    
    # Obtenir l'instance de la base de données
    db = get_database(db_path)
    
    # Créer et afficher la fenêtre principale
    main_window = MainWindow(db)
    main_window.show()
    
    # Si c'est la première exécution, afficher un message de bienvenue
    if first_run:
        main_window.show_welcome_dialog()
        settings.setValue("first_run", False)
    
    # Exécuter l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
