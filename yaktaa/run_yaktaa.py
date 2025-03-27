#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YakTaa - Lanceur du jeu
Ce script permet de lancer le jeu YakTaa sans avoir à installer le package
"""

import sys
import os
import logging
from pathlib import Path

# Ajout du répertoire parent au chemin de recherche Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / 'yaktaa.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    # Importation de PyQt6
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    
    # Importation du fichier principal
    from yaktaa.main import MainWindow
    
    def main():
        """Point d'entrée principal de l'application"""
        app = QApplication(sys.argv)
        
        # Application de la police par défaut
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    logger.error(f"Erreur d'importation: {e}")
    print(f"Erreur: {e}")
    print("Assurez-vous d'avoir installé les dépendances requises:")
    print("pip install PyQt6")
    sys.exit(1)
except Exception as e:
    logger.error(f"Erreur lors du lancement du jeu: {e}", exc_info=True)
    print(f"Erreur: {e}")
    sys.exit(1)
