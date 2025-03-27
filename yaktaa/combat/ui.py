# YakTaa - Interface utilisateur de combat (Wrapper de compatibilité)
import logging
from typing import Dict, List, Any, Optional, Callable
from .ui_pyqt import CombatUI as PyQtCombatUI
from .engine import CombatEngine, ActionType, CombatStatus

# Configurer le logger
logger = logging.getLogger(__name__)

class CombatUI(PyQtCombatUI):
    """
    Classe de compatibilité pour rediriger vers l'interface PyQt6
    Cette classe remplace l'ancienne implémentation Tkinter et
    assure la compatibilité avec le code existant.
    """
    
    def __init__(self, root, combat_engine: CombatEngine, end_callback: Callable = None):
        """
        Initialise l'interface utilisateur de combat
        
        Args:
            root: Fenêtre racine (ignorée pour PyQt6, utilisée avant pour Tkinter)
            combat_engine: Moteur de combat à utiliser
            end_callback: Fonction à appeler à la fin du combat
        """
        # Ignorer le root Tkinter, nous utilisons PyQt6 maintenant
        super().__init__(parent=None, combat_engine=combat_engine, end_callback=end_callback)
        logger.info("Interface de combat PyQt6 initialisée (remplace Tkinter)")
        
    # Toutes les autres méthodes sont héritées de PyQtCombatUI
