"""
Script pour corriger le fichier shop_manager.py
Ce script corrige l'erreur de syntaxe dans le fichier shop_manager.py
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FixShopManager")

def fix_shop_manager():
    """
    Crée une version corrigée du shop_manager.py
    """
    shop_manager_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     "yaktaa", "items", "shop_manager.py")
    
    if not os.path.exists(shop_manager_path):
        logger.error(f"Fichier shop_manager.py non trouvé: {shop_manager_path}")
        return False
    
    try:
        with open(shop_manager_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Trouver la section à corriger
        start_line = None
        end_line = None
        
        for i, line in enumerate(lines):
            if "def _load_item_details(self, conn, item_type: str, item_id: str):" in line:
                start_line = i
            if start_line is not None and "return item" in line:
                end_line = i
                break
        
        if start_line is None or end_line is None:
            logger.error("Section à corriger non trouvée dans shop_manager.py")
            return False
        
        # Reconstruire la méthode _load_item_details correctement
        corrected_method = """    def _load_item_details(self, conn, item_type: str, item_id: str):
        \"\"\"
        Charge les détails d'un article à partir de la base de données
        
        Args:
            conn: Connexion à la base de données
            item_type: Type d'article (software, weapon, clothing, etc.)
            item_id: ID de l'article
            
        Returns:
            Instance de l'article ou None si non trouvé
        \"\"\"
        try:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            
            # Extraire l'ID réel sans le préfixe du type
            real_item_id = item_id
            if '_' in item_id and item_id.split('_')[0].lower() in ['software', 'hardware', 'consumable']:
                real_item_id = item_id.split('_', 1)[1]
            
            # Normaliser le type d'article en minuscules
            item_type_lower = item_type.lower()
            
            # Déterminer la table appropriée en fonction du type d'article
            table_name = None
            
            if item_type_lower.startswith('software') or item_type_lower in ['os', 'firewall', 'data_broker', 'vpn', 'crypto', 'cloud_storage']:
                table_name = 'software_items'
            elif item_type_lower.startswith('hardware') or item_type_lower in ['cpu', 'ram', 'ssd', 'tool']:
                table_name = 'hardware_items'
            elif item_type_lower.startswith('consumable') or item_type_lower in ['drink', 'stimulant', 'food']:
                table_name = 'consumable_items'
            elif item_type_lower in ['weapon', 'pistol', 'rifle', 'melee']:
                table_name = 'weapon_items'
            elif item_type_lower in ['clothing', 'armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']:
                table_name = 'clothing_items'
            elif item_type_lower in ['implant', 'cyberware', 'cybernetic']:
                table_name = 'implant_items'
                # Vérifier si la table implant_items existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implant_items'")
                if not cursor.fetchone():
                    # Si la table n'existe pas, créer un item générique
                    logger.info(f"[SHOP_MANAGER] Table implant_items non trouvée, création d'un implant générique pour {item_id}")
                    return self._create_generic_item(item_id, item_type)
            elif item_type_lower in ['food', 'drink', 'drug']:
                table_name = 'consumable_items'
            else:
                # Tenter de déterminer le type réel à partir du préfixe de l'ID
                if item_id.startswith('weapon_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> weapon")
                    return self._load_item_details(conn, 'weapon', item_id)
                elif item_id.startswith('clothing_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> clothing")
                    return self._load_item_details(conn, 'clothing', item_id)
                elif item_id.startswith('hardware_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> hardware")
                    return self._load_item_details(conn, 'hardware', item_id)
                elif item_id.startswith('software_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> software")
                    return self._load_item_details(conn, 'software', item_id)
                elif item_id.startswith('consumable_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> consumable")
                    return self._load_item_details(conn, 'consumable', item_id)
                elif item_id.startswith('implant_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> implant")
                    return self._load_item_details(conn, 'implant', item_id)
                elif item_id.startswith('food_'):
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> food")
                    return self._load_item_details(conn, 'food', item_id)
                else:
                    logger.warning(f"[SHOP_MANAGER] Type d'article non reconnu: {item_type}")
                    return self._create_generic_item(item_id, item_type)
            
            # Si c'est une arme et que la table n'existe pas encore, utiliser items
            if table_name == 'weapon_items':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weapon_items'")
                if not cursor.fetchone():
                    table_name = 'items'
                    
            if table_name:
                # Faire la requête avec le bon ID (préfixé ou non selon la table)
                query_id = item_id if table_name != 'items' else real_item_id
                cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (query_id,))
                item_data = cursor.fetchone()
                
                if item_data:
                    # Créer l'article selon son type
                    if table_name == 'software_items' or item_type_lower.startswith('software'):
                        from yaktaa.items.software import SoftwareItem
                        item = SoftwareItem(item_data)
                    elif table_name == 'weapon_items' or item_type_lower.startswith('weapon'):
                        from yaktaa.items.weapon import WeaponItem
                        item = WeaponItem(item_data)
                    elif table_name == 'clothing_items' or item_type_lower.startswith('clothing'):
                        from yaktaa.items.clothing import ClothingItem
                        item = ClothingItem(item_data)
                    elif table_name == 'hardware_items' or item_type_lower.startswith('hardware'):
                        from yaktaa.items.hardware import HardwareItem
                        item = HardwareItem(item_data)
                    elif table_name == 'consumable_items' or item_type_lower in ['consumable', 'food', 'drink', 'drug']:
                        from yaktaa.items.consumable import ConsumableItem
                        item = ConsumableItem(item_data)
                    elif table_name == 'implant_items' or item_type_lower.startswith('implant'):
                        from yaktaa.items.implant import ImplantItem
                        item = ImplantItem(item_data)
                    else:
                        from yaktaa.items.item import Item
                        item = Item(item_data)
                    
                    return item
                else:
                    # Si l'article n'est pas trouvé dans la table appropriée, vérifier s'il existe dans la table générique
                    if table_name != 'items':
                        logger.warning(f"[SHOP_MANAGER] Article {item_id} non trouvé dans la table {table_name}")
                        if item_type_lower.startswith('hardware'):
                            logger.warning(f"[SHOP_MANAGER] Article {item_id} non trouvé dans la table {table_name}")
                    # Créer un article générique
                    return self._create_generic_item(item_id, item_type)
            else:
                # Si aucune table appropriée n'est trouvée, créer un article générique
                return self._create_generic_item(item_id, item_type)
                
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors du chargement de l'article {item_id}: {e}")
            return self._create_generic_item(item_id, item_type)
"""
        
        # Remplacer la méthode dans le fichier
        new_lines = lines[:start_line] + [corrected_method] + lines[end_line+1:]
        
        # Sauvegarder le fichier corrigé
        with open(shop_manager_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        logger.info(f"Fichier shop_manager.py corrigé avec succès: {shop_manager_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction du fichier shop_manager.py: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Démarrage de la correction du fichier shop_manager.py")
    
    if fix_shop_manager():
        logger.info("✅ Fichier shop_manager.py corrigé avec succès")
        print("\n[SUCCÈS] Fichier shop_manager.py corrigé avec succès")
    else:
        logger.warning("⚠️ Erreur lors de la correction du fichier shop_manager.py")
        print("\n[ERREUR] Échec de la correction du fichier shop_manager.py")
