# Ce fichier est un alias pour consumable_item.py pour la compatibilitu00e9 avec le code existant
import logging

# Configuration du logging
logger = logging.getLogger("YakTaa.Items.Consumable")
logger.debug("Module consumable.py chargu00e9 (alias pour consumable_item.py)")

# Ru00e9exporte tout le contenu du module consumable_item
from .consumable_item import ConsumableItem
