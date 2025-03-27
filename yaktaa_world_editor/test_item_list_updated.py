import sys
import logging
import sqlite3
from PyQt6.QtWidgets import QApplication
from ui.item_list import ItemList

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Monde de test - utilisez l'ID du monde existant avec des armures
    test_world_id = "10ac4af3-21bc-437d-b34f-11b4af004f8f"  # Monde actuel
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    # Connecter à la base de données
    db_conn = sqlite3.connect('worlds.db')
    
    # Créer et afficher le widget ItemList
    logger.info(f"Création de l'ItemList pour le monde {test_world_id}")
    item_list = ItemList(db_conn, test_world_id)
    item_list.show()
    
    # Charger tous les types d'objets
    for item_type in ["hardware", "consumable", "software", "weapon", "armor", "implant"]:
        logger.info(f"Chargement des objets de type {item_type}")
        item_list.load_items(item_type)
    
    # Exécuter l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
