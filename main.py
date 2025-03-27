#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YakTaa - Un jeu de rôle cyberpunk avec terminal et exploration
"""

import sys
import os
import logging
from pathlib import Path

# Configuration des chemins et de l'environnement
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "yaktaa.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("YakTaa")

# Import des modules du jeu
from yaktaa.core.game import Game
from yaktaa.ui.app import Application


def main():
    """Point d'entrée principal du jeu YakTaa"""
    try:
        logger.info("Démarrage de YakTaa...")
        
        # Initialisation de l'application
        app = Application(sys.argv)
        
        # Initialisation du jeu
        game = Game()
        
        # Lancement de l'application
        exit_code = app.run(game)
        
        logger.info(f"YakTaa s'est terminé avec le code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Erreur critique: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
