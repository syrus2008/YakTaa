# Ce fichier est un alias pour software_item.py pour la compatibilité avec le code existant
import logging

# Configuration du logging
logger = logging.getLogger("YakTaa.Items.Software")
logger.debug("Module software.py chargé (alias pour software_item.py)")

# Réexporte tout le contenu du module software_item
from .software_item import SoftwareItem
