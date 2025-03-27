# Ce fichier est un alias pour food_item.py pour la compatibilité avec le code existant
import logging

# Configuration du logging
logger = logging.getLogger("YakTaa.Items.Food")
logger.debug("Module food.py chargé (alias pour food_item.py)")

# Réexporte tout le contenu du module food_item
from .food_item import FoodItem
