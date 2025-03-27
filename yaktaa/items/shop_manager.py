"""
Module de gestion des boutiques pour YakTaa.
Permet de charger, gérer et interagir avec les boutiques dans le monde du jeu.
Utilise les tables 'shops' et 'shop_inventory' de la base de données.
"""

import json
import random
import uuid
import logging
import sqlite3
from typing import Dict, List, Optional, Union, Tuple, Any

# Importation des classes nécessaires du jeu
from .item import Item
from .hardware import HardwareItem
from .software_item import SoftwareItem
from .consumable import ConsumableItem
from .food import FoodItem
from .weapon import WeaponItem
from .implant import ImplantItem
from .clothing import ClothingItem
from .inventory_manager import InventoryManager
from ..world.world_loader import WorldLoader

# Configuration du logging
logger = logging.getLogger(__name__)

class Shop:
    """Représente une boutique dans le monde YakTaa."""
    
    def __init__(self, shop_id: str, name: str, description: str, shop_type: str,
                 location_id: str = None, owner_id: str = None, faction_id: str = None,
                 reputation: int = 5, price_modifier: float = 1.0, 
                 is_legal: bool = True, data: Dict = None):
        """
        Initialise une boutique.
        
        Args:
            shop_id: Identifiant unique de la boutique
            name: Nom de la boutique
            description: Description de la boutique
            shop_type: Type de boutique (hardware, software, black market, etc.)
            location_id: ID de l'emplacement de la boutique
            owner_id: ID du propriétaire (personnage)
            faction_id: ID de la faction propriétaire
            reputation: Niveau de réputation (1-10)
            price_modifier: Modificateur de prix (1.0 = prix normal)
            is_legal: Si la boutique est légale ou non
            data: Données brutes de la boutique depuis la base de données
        """
        self.id = shop_id
        self.name = name
        self.description = description
        self.shop_type = shop_type
        self.location_id = location_id
        self.owner_id = owner_id
        self.faction_id = faction_id
        self.reputation = reputation
        self.price_modifier = price_modifier
        self.is_legal = is_legal
        
        # Données supplémentaires
        self.special_items = {}
        self.services = {}
        self.open_hours = {"open": "08:00", "close": "20:00"}
        self.inventory_refresh_rate = 24  # en heures
        self.requires_reputation = False
        self.required_reputation_level = 0
        self.metadata = {}
        
        # Chargement des données supplémentaires si fournies
        if data:
            self._load_from_data(data)
        
        # Inventaire de la boutique
        self.inventory = []
    
    def _load_from_data(self, data: Dict) -> None:
        """Charge les données supplémentaires depuis un dictionnaire."""
        if 'special_items' in data and data['special_items']:
            self.special_items = json.loads(data['special_items'])
        
        if 'services' in data and data['services']:
            self.services = json.loads(data['services'])
        
        if 'open_hours' in data and data['open_hours']:
            self.open_hours = json.loads(data['open_hours'])
        
        if 'inventory_refresh_rate' in data:
            self.inventory_refresh_rate = data['inventory_refresh_rate']
        
        if 'requires_reputation' in data:
            self.requires_reputation = bool(data['requires_reputation'])
        
        if 'required_reputation_level' in data:
            self.required_reputation_level = data['required_reputation_level']
        
        if 'metadata' in data and data['metadata']:
            self.metadata = json.loads(data['metadata'])
    
    def calculate_price(self, base_price: int, player_reputation: int = 0) -> int:
        """
        Calcule le prix final d'un article en fonction du modificateur de la boutique
        et de la réputation du joueur.
        
        Args:
            base_price: Prix de base de l'article
            player_reputation: Niveau de réputation du joueur (optionnel)
            
        Returns:
            Prix final calculé
        """
        # Facteur de base (prix de vente)
        price = base_price * self.price_modifier
        
        # Ajustement selon la réputation du joueur (réduction jusqu'à 20%)
        if player_reputation > 0:
            rep_discount = min(player_reputation * 0.02, 0.2)
            price = price * (1 - rep_discount)
        
        return max(1, int(price))
    
    def buy_item(self, item_index: int, player_inventory: Union[InventoryManager, List], 
                 player_credits: int, player_location_id: str) -> Tuple[bool, str, Optional[Item], int]:
        """
        Achète un article de la boutique.
        
        Args:
            item_index: Index de l'article dans l'inventaire de la boutique
            player_inventory: Gestionnaire d'inventaire du joueur ou liste d'objets
            player_credits: Crédits disponibles du joueur
            player_location_id: ID de la ville ou du joueur se trouve (extrait avec get_city_id_from_location)
            
        Returns:
            Tuple (succès, message, item acheté, crédits restants)
        """
        # Vérifier que le joueur est dans la même ville que la boutique
        # On doit d'abord extraire l'ID de la ville du joueur si c'est un bâtiment
        player_city_id = player_location_id
        if player_location_id and player_location_id.startswith("building_") and "_" in player_location_id:
            parts = player_location_id.split("_", 2)
            if len(parts) >= 3:
                player_city_id = parts[1]
                
        shop_city_id = self.location_id
        # Si la boutique est dans un bâtiment, extraire l'ID de la ville
        if self.location_id and self.location_id.startswith("building_") and "_" in self.location_id:
            parts = self.location_id.split("_", 2)
            if len(parts) >= 3:
                shop_city_id = parts[1]
                
        if player_city_id != shop_city_id:
            return False, "Vous devez être dans la même ville que la boutique pour effectuer un achat.", None, player_credits
        
        if item_index < 0 or item_index >= len(self.inventory):
            return False, "Article introuvable.", None, player_credits
        
        item, price = self.inventory[item_index]
        
        if player_credits < price:
            return False, "Crédits insuffisants.", None, player_credits
        
        # Mise à jour des crédits du joueur
        remaining_credits = player_credits - price
        
        # Ajout de l'article à l'inventaire du joueur
        if isinstance(player_inventory, list):
            # Si l'inventaire est une liste, ajouter directement l'objet
            player_inventory.append(item)
        else:
            # Si c'est un InventoryManager, utiliser sa méthode add_item
            player_inventory.add_item(item)
        
        # Suppression de l'article de l'inventaire de la boutique
        self.inventory.pop(item_index)
        
        return True, f"{item.name} acheté pour {price} crédits.", item, remaining_credits
    
    def sell_item(self, item_index: int, player_inventory: Union[InventoryManager, List], 
                  player_credits: int, player_location_id: str = None) -> Tuple[bool, str, int]:
        """
        Vend un article du joueur à la boutique.
        
        Args:
            item_index: Index de l'article dans l'inventaire du joueur
            player_inventory: Gestionnaire d'inventaire du joueur ou liste d'objets
            player_credits: Crédits actuels du joueur
            player_location_id: ID de la localisation du joueur (optionnel)
            
        Returns:
            Tuple (succès, message, nouveaux crédits)
        """
        # Vérifier que le joueur est dans la même ville que la boutique (si player_location_id est fourni)
        if player_location_id:
            # On doit d'abord extraire l'ID de la ville du joueur si c'est un bâtiment
            player_city_id = player_location_id
            if player_location_id.startswith("building_") and "_" in player_location_id:
                parts = player_location_id.split("_", 2)
                if len(parts) >= 3:
                    player_city_id = parts[1]
                    
            shop_city_id = self.location_id
            # Si la boutique est dans un bâtiment, extraire l'ID de la ville
            if self.location_id and self.location_id.startswith("building_") and "_" in self.location_id:
                parts = self.location_id.split("_", 2)
                if len(parts) >= 3:
                    shop_city_id = parts[1]
                    
            if player_city_id != shop_city_id:
                return False, "Vous devez être dans la même ville que la boutique pour vendre des objets.", player_credits
        
        # Déterminer si l'inventaire est une liste ou un InventoryManager
        if isinstance(player_inventory, list):
            # Cas où l'inventaire est une liste
            if item_index < 0 or item_index >= len(player_inventory):
                return False, "Article introuvable dans votre inventaire.", player_credits
            
            item = player_inventory[item_index]
            
            # Calcul du prix de rachat (généralement 50% du prix de vente)
            sell_price = int(item.price * 0.5) if hasattr(item, 'price') else 10
            
            # Suppression de l'article de l'inventaire du joueur
            removed_item = player_inventory.pop(item_index)
            
            # Mise à jour des crédits du joueur
            new_credits = player_credits + sell_price
            
            return True, f"{item.name} vendu pour {sell_price} crédits.", new_credits
        else:
            # Cas où l'inventaire est un InventoryManager
            if item_index < 0 or item_index >= len(player_inventory.items):
                return False, "Article introuvable dans votre inventaire.", player_credits
            
            item = player_inventory.items[item_index]
            
            # Calcul du prix de rachat (généralement 50% du prix de vente)
            sell_price = int(item.price * 0.5)
            
            # Suppression de l'article de l'inventaire du joueur
            player_inventory.remove_item(item_index)
            
            # Mise à jour des crédits du joueur
            new_credits = player_credits + sell_price
            
            return True, f"{item.name} vendu pour {sell_price} crédits.", new_credits
    
    def to_dict(self) -> Dict:
        """Convertit la boutique en dictionnaire pour l'affichage ou la sauvegarde."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'shop_type': self.shop_type,
            'reputation': self.reputation,
            'price_modifier': self.price_modifier,
            'is_legal': self.is_legal,
            'requires_reputation': self.requires_reputation,
            'required_reputation_level': self.required_reputation_level,
            'open_hours': self.open_hours,
            'special_items': self.special_items,
            'services': self.services,
            'inventory_size': len(self.inventory)
        }
    
class ShopManager:
    """Gestionnaire des boutiques dans le monde YakTaa."""
    
    def __init__(self, world_loader: WorldLoader):
        """
        Initialise le gestionnaire de boutiques.
        
        Args:
            world_loader: Chargeur de monde pour accéder à la base de données
        """
        self.world_loader = world_loader
        self.shops = {}  # Dictionnaire des boutiques par ID
        self.location_shops = {}  # Dictionnaire des boutiques par emplacement
        self.item_factory = None  # Sera défini après
        
        # Initialiser les tables de boutiques si elles n'existent pas
        self._initialize_shop_tables()
    
    def set_item_factory(self, item_factory):
        """Définit la factory d'items pour créer les objets vendus."""
        self.item_factory = item_factory
    
    def load_shops(self):
        """
        Charge tous les magasins depuis la base de données
        """
        try:
            # Réinitialiser les dictionnaires de boutiques pour éviter les doublons
            self.shops = {}
            self.location_shops = {}
            
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Vérifier la structure de la table shops
            cursor.execute("PRAGMA table_info(shops)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Déterminer le nom des colonnes
            id_column = "id"
            type_column = "shop_type" if "shop_type" in columns else "type"
            
            # Récupérer tous les magasins
            cursor.execute(f"SELECT {id_column}, name, description, {type_column}, location_id FROM shops")
            
            all_shops = []
            for row in cursor.fetchall():
                shop_id, name, description, shop_type, location_id = row
                shop = Shop(shop_id, name, description, shop_type, location_id)
                self._load_shop_inventory(shop)
                all_shops.append(shop)
                
                # Stocker la boutique dans le dictionnaire principal
                self.shops[shop_id] = shop
                
                # Stocker la boutique par emplacement
                if location_id:
                    if location_id not in self.location_shops:
                        self.location_shops[location_id] = []
                    self.location_shops[location_id].append(shop)
            
            logger.info(f"[SHOP_MANAGER] {len(all_shops)} boutiques chargées avec succès")
            return all_shops
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des magasins: {e}")
            return []
    
    def _create_shop_from_data(self, data: Dict) -> Shop:
        """Crée une instance de boutique à partir des données de la base de données."""
        return Shop(
            shop_id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            shop_type=data['shop_type'],
            location_id=data.get('location_id'),
            owner_id=data.get('owner_id'),
            faction_id=data.get('faction_id'),
            reputation=data.get('reputation', 5),
            price_modifier=data.get('price_modifier', 1.0),
            is_legal=bool(data.get('is_legal', 1)),
            data=data
        )
    
    def _load_shop_inventories(self, conn, world_id: str) -> None:
        """Charge les inventaires pour toutes les boutiques chargées."""
        cursor = conn.cursor()
        
        for shop_id, shop in self.shops.items():
            cursor.execute("""
                SELECT * FROM shop_inventory
                WHERE shop_id = ?
            """, (shop_id,))
            
            # Récupérer les noms de colonnes
            column_names = [description[0] for description in cursor.description]
            
            inventory_items = cursor.fetchall()
            shop.inventory = []
            
            for inv_item in inventory_items:
                # Créer un dictionnaire en associant les noms de colonnes aux valeurs
                item_data = {column_names[i]: inv_item[i] for i in range(len(column_names))}
                
                item_type = item_data['item_type']
                item_id = item_data['item_id']
                
                # Chargement des détails de l'article selon son type
                item = self._load_item_details(conn, item_type, item_id)
                
                if item:
                    # Calcul du prix avec le modificateur spécifique à cet article dans l'inventaire
                    price_modifier = item_data.get('price_modifier', 1.0)
                    price = int(item.price * price_modifier) if hasattr(item, 'price') else int(100 * price_modifier)
                    
                    # Ajout à l'inventaire de la boutique
                    shop.inventory.append((item, price))
    
    def _load_item_details(self, conn, item_type: str, item_id: str):
        """
        Charge les détails d'un article spécifique selon son type.
        
        Args:
            conn: Connexion à la base de données
            item_type: Type d'article (hardware, software, consumable)
            item_id: ID de l'article
            
        Returns:
            Instance de l'article ou None si non trouvé
        """
        try:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            
            # Normaliser le type d'article en minuscules
            item_type_lower = item_type.lower()
            
            # Extraire l'ID réel
            real_item_id = item_id
            
            # Si l'item_id contient déjà le préfixe correspondant à son type, l'utiliser tel quel
            # C'est souvent le cas des items provenant directement de la base de données
            if (item_id.startswith('hardware_') and item_type_lower in ['hardware', 'cpu', 'ram', 'ssd', 'tool']) or \
               (item_id.startswith('software_') and item_type_lower in ['software', 'os', 'firewall', 'vpn']) or \
               (item_id.startswith('weapon_') and item_type_lower in ['weapon', 'knife', 'pistol', 'rifle']) or \
               (item_id.startswith('implant_') and item_type_lower in ['implant', 'neural', 'optical']) or \
               (item_id.startswith('clothing_') and item_type_lower in ['clothing', 'armor', 'jacket']):
                # L'ID est déjà préfixé correctement, pas besoin de modifier
                pass
            else:
                # Si on a un préfixe de type mais pas le bon, extraire l'ID sans préfixe
                if '_' in item_id:
                    prefix, id_part = item_id.split('_', 1)
                    recognized_prefixes = ['hardware', 'software', 'weapon', 'implant', 'clothing', 'consumable']
                    if prefix.lower() in recognized_prefixes:
                        real_item_id = id_part
                        logger.debug(f"[SHOP_MANAGER] ID extrait du préfixe: {item_id} -> {real_item_id}")
            
            # Déterminer la table appropriée en fonction du type d'article
            table_name = None
            
            if item_type_lower.startswith('software') or item_type_lower in ['os', 'firewall', 'data_broker', 'vpn', 'crypto', 'cloud_storage']:
                table_name = 'software_items'
            elif item_type_lower.startswith('hardware') or item_type_lower in ['cpu', 'ram', 'ssd', 'tool']:
                table_name = 'hardware_items'
            elif item_type_lower.startswith('consumable') or item_type_lower in ['drink', 'stimulant', 'food']:
                table_name = 'consumable_items'
            elif item_type_lower.startswith('implant') or item_type_lower in ['neural', 'optical', 'skeletal', 'dermal', 'circulatory']:
                table_name = 'implant_items'
                # Vérifier si la table implant_items existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implant_items'")
                if not cursor.fetchone():
                    # Si la table n'existe pas, créer un item générique
                    logger.info(f"[SHOP_MANAGER] Table implant_items non trouvée, création d'un implant générique pour {item_id}")
                    return self._create_generic_item(item_id, item_type)
            elif item_type_lower.startswith('clothing') or item_type_lower in ['armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']:
                table_name = 'clothing_items'
            elif item_type_lower == 'weapon' or item_type_lower in ['knife', 'pistol', 'rifle', 'shotgun', 'smg', 'sniper']:
                table_name = 'weapon_items'
            else:
                # Tenter de déterminer le type réel à partir du préfixe de l'ID
                if item_id.startswith('weapon_') and item_type_lower != 'weapon':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> weapon")
                    item_type_lower = 'weapon'
                    table_name = 'weapon_items'
                elif item_id.startswith('clothing_') and item_type_lower != 'clothing':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> clothing")
                    item_type_lower = 'clothing'
                    table_name = 'clothing_items'
                elif item_id.startswith('hardware_') and item_type_lower != 'hardware':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> hardware")
                    item_type_lower = 'hardware'
                    table_name = 'hardware_items'
                elif item_id.startswith('software_') and item_type_lower != 'software':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> software")
                    item_type_lower = 'software'
                    table_name = 'software_items'
                elif item_id.startswith('consumable_') and item_type_lower != 'consumable':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> consumable")
                    item_type_lower = 'consumable'
                    table_name = 'consumable_items'
                elif item_id.startswith('implant_') and item_type_lower != 'implant':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> implant")
                    item_type_lower = 'implant'
                    table_name = 'implant_items'
                elif item_id.startswith('food_') and item_type_lower != 'food':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> food")
                    item_type_lower = 'food'
                    table_name = 'food_items'
                else:
                    logger.info(f"[SHOP_MANAGER] Type d'article non reconnu: {item_type}, création d'un article générique")
                    return self._create_generic_item(item_id, item_type)
            
            # Vérifier si la table existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                logger.info(f"[SHOP_MANAGER] Table {table_name} non trouvée dans la base de données, création d'un article générique")
                return self._create_generic_item(item_id, item_type)
            
            # Essayer avec l'ID original complet
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (item_id,))
            data = cursor.fetchone()
            
            # Si rien trouvé, essayer avec l'ID extrait
            if not data and item_id != real_item_id:
                cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (real_item_id,))
                data = cursor.fetchone()
            
            # Essayer avec préfixe + ID réel
            if not data:
                # Ajouter le préfixe correct basé sur le type de table
                prefixed_id = None
                if table_name == 'hardware_items':
                    prefixed_id = f"hardware_{real_item_id}"
                elif table_name == 'software_items':
                    prefixed_id = f"software_{real_item_id}"
                elif table_name == 'weapon_items':
                    prefixed_id = f"weapon_{real_item_id}"
                elif table_name == 'implant_items':
                    prefixed_id = f"implant_{real_item_id}"
                elif table_name == 'clothing_items':
                    prefixed_id = f"clothing_{real_item_id}"
                elif table_name == 'food_items':
                    prefixed_id = f"food_{real_item_id}"
                
                if prefixed_id:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (prefixed_id,))
                    data = cursor.fetchone()
            
            if not data:
                logger.info(f"[SHOP_MANAGER] Article {item_id} non trouvé dans la table {table_name}, création d'un article générique")
                return self._create_generic_item(item_id, item_type)
            
            # Récupérer les noms de colonnes
            column_names = [description[0] for description in cursor.description]
            # Créer un dictionnaire des données
            item_data = {column_names[i]: data[i] for i in range(len(column_names))}
            
            # Créer l'instance d'article appropriée selon le type
            if item_type_lower in ['hardware', 'cpu', 'ram', 'ssd', 'tool']:
                try:
                    # Convertir la chaîne 'type' en énumération HardwareType si possible
                    from .hardware import HardwareType
                    hw_type = item_data.get('hardware_type') or item_type
                    if isinstance(hw_type, str):
                        try:
                            for t in HardwareType:
                                if t.value == hw_type.lower():
                                    hw_type = t
                                    break
                            if isinstance(hw_type, str):
                                hw_type = HardwareType.TOOL  # Type par défaut
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors de la conversion du type hardware: {e}")
                            hw_type = HardwareType.TOOL
                    
                    # Convertir la chaîne 'rarity' en énumération HardwareRarity si possible
                    from .hardware import HardwareRarity
                    hw_rarity = item_data.get('rarity', 'common')
                    if isinstance(hw_rarity, str):
                        try:
                            for r in HardwareRarity:
                                if r.value == hw_rarity.lower():
                                    hw_rarity = r
                                    break
                            if isinstance(hw_rarity, str):
                                hw_rarity = HardwareRarity.COMMON  # Rareté par défaut
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors de la conversion de la rareté hardware: {e}")
                            hw_rarity = HardwareRarity.COMMON
                    
                    hardware_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Hardware {item_type.capitalize()}",
                        'type': hw_type,
                        'description': item_data.get('description') or f"Un équipement de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'rarity': hw_rarity,
                        'price': item_data.get('price', 100)
                    }
                    
                    # Ajouter stats si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats' in metadata:
                                    hardware_params['stats'] = metadata['stats']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats hardware: {e}")
                    
                    return HardwareItem(**hardware_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article hardware {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
                    
            elif item_type_lower in ['software', 'os', 'firewall', 'data_broker', 'vpn', 'crypto', 'cloud_storage']:
                try:
                    software_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Logiciel {item_type.capitalize()}",
                        'software_type': item_data.get('software_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un logiciel de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'version': item_data.get('version', '1.0'),
                        'price': item_data.get('price', 100)
                    }
                    
                    # Ajouter features si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'features' in metadata:
                                    software_params['features'] = metadata['features']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des features software: {e}")
                    
                    return SoftwareItem(**software_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article software {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['consumable', 'drink', 'stimulant', 'food']:
                try:
                    consumable_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Consommable {item_type.capitalize()}",
                        'item_type': item_data.get('consumable_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un consommable de type {item_type}",
                        'price': item_data.get('price', 50),
                        'uses': item_data.get('uses', 1),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    # Ajouter effects si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'effects' in metadata:
                                    consumable_params['effects'] = metadata['effects']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des effects consumable: {e}")
                    
                    return ConsumableItem(**consumable_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article consumable {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
                    
            elif item_type_lower in ['implant', 'neural', 'optical', 'skeletal', 'dermal', 'circulatory']:
                try:
                    implant_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Implant {item_type.capitalize()}",
                        'implant_type': item_data.get('implant_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un implant de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'price': item_data.get('price', 100),
                        'rarity': item_data.get('rarity', 'COMMON')
                    }
                    
                    # Ajouter stats_bonus si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats_bonus' in metadata:
                                    implant_params['stats_bonus'] = metadata['stats_bonus']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats_bonus implant: {e}")
                    
                    return ImplantItem(**implant_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article implant {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['weapon', 'pistol', 'rifle', 'melee']:
                try:
                    # Extraire les données d'arme de metadata si disponible
                    weapon_metadata = {}
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                weapon_metadata = json.loads(item_data['metadata'])
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des metadata d'arme: {e}")
                    
                    return WeaponItem(
                        id=item_data.get('id') or item_id,
                        name=item_data.get('name') or f"Arme {item_type.capitalize()}",
                        weapon_type=item_type,
                        description=item_data.get('description') or f"Une arme de type {item_type}",
                        damage=weapon_metadata.get('damage', 10),
                        damage_type=weapon_metadata.get('damage_type', 'PHYSICAL'),
                        range=weapon_metadata.get('range', 10),
                        accuracy=weapon_metadata.get('accuracy', 70),
                        price=item_data.get('price', 200)
                    )
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article weapon {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type)
            
            elif item_type_lower in ['clothing', 'armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']:
                try:
                    clothing_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Vêtement {item_type.capitalize()}",
                        'clothing_type': item_data.get('clothing_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un vêtement de type {item_type}",
                        'price': item_data.get('price', 50),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    # Ajouter stats si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats' in metadata:
                                    clothing_params['stats'] = metadata['stats']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats clothing: {e}")
                    
                    return ClothingItem(**clothing_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article clothing {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['food']:
                try:
                    food_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Nourriture {item_type.capitalize()}",
                        'food_type': item_data.get('food_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un aliment de type {item_type}",
                        'price': item_data.get('price', 50),
                        'health_restore': item_data.get('health_restore', 10),
                        'energy_restore': item_data.get('energy_restore', 10),
                        'mental_restore': item_data.get('mental_restore', 5),
                        'uses': item_data.get('uses', 1),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    return FoodItem(**food_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article food {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            else:
                # Article générique pour les autres types
                return self._create_generic_item(item_id, item_type)
                
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors du chargement de l'article {item_id}: {e}")
            return self._create_generic_item(item_id, item_type)
    
    def _create_generic_item(self, item_id, item_type, item_data=None):
        """Crée un article générique lorsque les détails spécifiques ne sont pas disponibles"""
        if item_data is None:
            item_data = {}
        
        # Si c'est une arme, créer une instance de WeaponItem au lieu d'un Item générique
        if item_type.lower() in ['weapon', 'pistol', 'rifle', 'melee']:
            try:
                from .weapon import WeaponItem
                # Générer un nom aléatoire basé sur le type d'arme
                weapon_types = {
                    'pistol': ['Pistolet', 'Revolver', 'Derringer'],
                    'rifle': ['Fusil', 'Carabine', 'Fusil d\'assaut'],
                    'melee': ['Couteau', 'Épée', 'Matraque'],
                    'weapon': ['Arme', 'Blaster', 'Fusil à plasma']
                }
                
                import random
                prefix = random.choice(weapon_types.get(item_type.lower(), ['Arme']))
                suffix = random.choice(['de base', 'standard', 'commun', 'générique'])
                
                logger.info(f"[SHOP_MANAGER] Création d'une arme générique {prefix} {suffix} (ID: {item_id})")
                
                # Extraire l'ID unique de l'arme pour générer des stats cohérentes
                import hashlib
                hash_id = hashlib.md5(item_id.encode()).hexdigest()
                damage = 5 + int(hash_id[0:2], 16) % 15  # Dégâts entre 5 et 20
                accuracy = 50 + int(hash_id[2:4], 16) % 40  # Précision entre 50 et 90
                
                logger.info(f"[SHOP_MANAGER] Création d'une arme générique {prefix} {suffix} (ID: {item_id})")
                
                # Déterminer le type d'arme pour WeaponItem
                weapon_type_map = {
                    'pistol': 'RANGED',
                    'rifle': 'RANGED',
                    'melee': 'MELEE',
                    'weapon': 'RANGED'
                }
                weapon_type = weapon_type_map.get(item_type.lower(), 'RANGED')
                
                # Créer l'arme avec les bons paramètres
                return WeaponItem(
                    id=item_id,
                    name=f"{prefix} {suffix}",
                    description=f"Une arme de type {item_type} générique.",
                    weapon_type=weapon_type,  # Utiliser le type d'arme mappé
                    damage=damage,
                    damage_type="PHYSICAL",
                    range=10,
                    accuracy=accuracy,
                    price=item_data.get('price', 100)
                )
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'arme générique: {e}")
                # En cas d'échec, revenir à la création d'un Item générique
        
        # Si c'est un implant, créer une instance de ImplantItem
        elif item_type.lower() in ['implant', 'neural', 'optical', 'skeletal', 'dermal', 'circulatory']:
            try:
                from .implant import ImplantItem
                
                # Générer un nom aléatoire basé sur le type d'implant
                implant_types = {
                    'neural': ['Implant neural', 'Interface neurale', 'Processeur neural'],
                    'optical': ['Implant optique', 'Scanner rétinien', 'Vision améliorée'],
                    'skeletal': ['Renforcement squelettique', 'Exosquelette interne', 'Articulations améliorées'],
                    'dermal': ['Armure dermique', 'Protection cutanée', 'Peau synthétique'],
                    'circulatory': ['Système circulatoire amélioré', 'Filtre sanguin', 'Régulateur cardiaque'],
                    'implant': ['Implant générique', 'Augmentation cybernétique', 'Module d\'amélioration']
                }
                
                import random
                prefix = random.choice(implant_types.get(item_type.lower(), ['Implant']))
                suffix = random.choice(['de base', 'standard', 'commun', 'générique'])
                
                logger.info(f"[SHOP_MANAGER] Création d'un implant générique {prefix} {suffix} (ID: {item_id})")
                
                # Créer l'implant avec des paramètres par défaut
                return ImplantItem(
                    id=item_id,
                    name=f"{prefix} {suffix}",
                    description=f"Un implant de type {item_type} générique.",
                    implant_type=item_type.upper(),
                    level=1,
                    price=item_data.get('price', 150),
                    rarity="COMMON",
                    stats_bonus={"INTELLIGENCE": 1}  # Bonus minimal par défaut
                )
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'implant générique: {e}")
                # En cas d'échec, revenir à la création d'un Item générique
        
        # Si c'est un consommable de type FOOD, créer une instance de FoodItem
        elif item_type.lower() == 'food':
            try:
                from .food import FoodItem
                
                # Générer un nom aléatoire pour la nourriture
                food_types = ['Ration', 'Nourriture', 'Repas', 'Snack', 'Plat']
                
                import random
                prefix = random.choice(food_types)
                suffix = random.choice(['de base', 'standard', 'commun', 'générique'])
                
                logger.info(f"[SHOP_MANAGER] Création d'un item de nourriture {prefix} {suffix} (ID: {item_id})")
                
                # Générer des valeurs de restauration basées sur l'ID pour être cohérent
                import hashlib
                hash_id = hashlib.md5(item_id.encode()).hexdigest()
                health_restore = 5 + int(hash_id[0:2], 16) % 15  # Entre 5 et 20
                energy_restore = 10 + int(hash_id[2:4], 16) % 15  # Entre 10 et 25
                mental_restore = 5 + int(hash_id[4:6], 16) % 10  # Entre 5 et 15
                
                # Créer l'item de nourriture avec des paramètres appropriés
                return FoodItem(
                    id=item_id,
                    name=f"{prefix} {suffix}",
                    description=f"Un article alimentaire basique.",
                    food_type="STANDARD",
                    health_restore=health_restore,
                    energy_restore=energy_restore,
                    mental_restore=mental_restore,
                    uses=1,
                    price=item_data.get('price', 50),
                    rarity="Common"
                )
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'item de nourriture: {e}")
                # En cas d'échec, revenir à la création d'un Item générique
        
        # Si c'est un autre type de consommable (drink, stimulant), créer une instance de ConsumableItem
        elif item_type.lower() in ['drink', 'stimulant']:
            try:
                from .consumable import ConsumableItem
                
                # Générer un nom aléatoire basé sur le type de consommable
                consumable_types = {
                    'drink': ['Boisson', 'Breuvage', 'Liquide'],
                    'stimulant': ['Stimulant', 'Booster', 'Énergisant']
                }
                
                import random
                prefix = random.choice(consumable_types.get(item_type.lower(), ['Consommable']))
                suffix = random.choice(['de base', 'standard', 'commun', 'générique'])
                
                logger.info(f"[SHOP_MANAGER] Création d'un consommable générique {prefix} {suffix} (ID: {item_id})")
                
                # Créer le consommable avec des paramètres par défaut
                return ConsumableItem(
                    id=item_id,
                    name=f"{prefix} {suffix}",
                    description=f"Un consommable de type {item_type} générique.",
                    item_type=item_type.upper(),
                    price=item_data.get('price', 50),
                    uses=1,
                    rarity="Common",
                    effects={"ENERGY": 10}  # Effet minimal par défaut
                )
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la création du consommable générique: {e}")
                # En cas d'échec, revenir à la création d'un Item générique
        
        # Pour tous les autres types d'articles, créer un Item générique
        return Item(
            id=item_id,
            name=item_data.get('name') or f"Article {item_type.capitalize()}",
            type=item_type.lower(),  
            description=item_data.get('description') or f"Un article de type {item_type}",
            value=item_data.get('price', 100)
        )
    
    def get_shops_by_location(self, location_id: str) -> List[Shop]:
        """
        Récupère toutes les boutiques pour un emplacement spécifique.
        
        Args:
            location_id: ID de l'emplacement
            
        Returns:
            Liste des boutiques
        """
        logger.info(f"[SHOP_MANAGER] === Recherche des boutiques pour l'emplacement: {location_id} ===")
        
        # Si l'ID de localisation est vide, retourner une liste vide
        if not location_id:
            logger.warning("[SHOP_MANAGER] ID de localisation vide, aucune boutique retournée")
            return []
        
        shops = []
        conn = None
        try:
            # Obtenir une connexion à la base de données
            conn = self.world_loader.get_connection()
            if not conn:
                logger.error("[SHOP_MANAGER] Impossible d'obtenir une connexion à la base de données")
                return []
            
            cursor = conn.cursor()
            
            # Vérifier si la table shops existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
            if not cursor.fetchone():
                logger.error("[SHOP_MANAGER] Table 'shops' non trouvée dans la base de données")
                return []
            
            # APPROCHE SIMPLIFIÉE: Récupérer le nom de la ville actuelle
            city_name = None
            try:
                # Rechercher le nom de la location à partir de son ID
                cursor.execute("SELECT name FROM locations WHERE id = ?", (location_id,))
                result = cursor.fetchone()
                if result:
                    city_name = result[0]
                    logger.info(f"[SHOP_MANAGER] Nom de la ville trouvé: {city_name}")
            except Exception as e:
                logger.warning(f"[SHOP_MANAGER] Erreur en cherchant le nom de la ville: {e}")

            # Obtenir les boutiques correspondant à cet emplacement
            # MÉTHODE 1: Par ID de location
            try:
                # Récupération via location_id (le plus simple et direct)
                cursor.execute("""
                    SELECT id, name, description, shop_type, world_id 
                    FROM shops 
                    WHERE location_id = ?
                """, (location_id,))
                
                shops_data = cursor.fetchall()
                if shops_data:
                    logger.info(f"[SHOP_MANAGER] {len(shops_data)} boutiques trouvées pour location_id={location_id}")
                    
                    for shop_data in shops_data:
                        shop_id, name, description, shop_type, world_id = shop_data
                        shop = Shop(
                            shop_id=shop_id,
                            name=name if name else f"Boutique {shop_id[:8]}",
                            description=description if description else "Une boutique mystérieuse",
                            shop_type=shop_type if shop_type else "general",
                            location_id=location_id
                        )
                        shop.inventory = self._load_shop_inventory(shop)
                        shops.append(shop)
                    
                    # Si des boutiques sont trouvées, retourner immédiatement
                    if shops:
                        return shops
            except Exception as e:
                logger.warning(f"[SHOP_MANAGER] Erreur lors de la recherche par location_id: {e}")
            
            # MÉTHODE 2: Si le nom de la ville est connu, rechercher par nom
            if city_name:
                try:
                    # Recherche par jointure avec la table locations
                    cursor.execute("""
                        SELECT s.id, s.name, s.description, s.shop_type, l.name
                        FROM shops s
                        JOIN locations l ON s.location_id = l.id
                        WHERE l.name LIKE ?
                    """, (f"%{city_name}%",))
                    
                    shops_data = cursor.fetchall()
                    if shops_data:
                        logger.info(f"[SHOP_MANAGER] {len(shops_data)} boutiques trouvées pour la ville {city_name} via jointure")
                        
                        for shop_data in shops_data:
                            shop_id, name, description, shop_type, shop_location_name = shop_data
                            shop = Shop(
                                shop_id=shop_id,
                                name=name if name else f"Boutique {shop_id[:8]}",
                                description=description if description else "Une boutique mystérieuse",
                                shop_type=shop_type if shop_type else "general",
                                location_id=location_id
                            )
                            shop.inventory = self._load_shop_inventory(shop)
                            shops.append(shop)
                        
                        # Si des boutiques sont trouvées, retourner immédiatement
                        if shops:
                            return shops
                except Exception as e:
                    logger.warning(f"[SHOP_MANAGER] Erreur lors de la recherche par jointure: {e}")

            # MÉTHODE 3: Recherche par world_id et location_name dans les métadonnées
            if city_name:
                try:
                    # Identifier le monde actif
                    world_id = self.get_first_world_id()
                    if world_id:
                        cursor.execute("""
                            SELECT id, name, description, shop_type, metadata
                            FROM shops
                            WHERE world_id = ?
                        """, (world_id,))
                        
                        shops_data = cursor.fetchall()
                        if shops_data:
                            logger.info(f"[SHOP_MANAGER] {len(shops_data)} boutiques potentielles trouvées pour world_id={world_id}")
                            
                            # Filtrer les boutiques par nom de ville dans les métadonnées ou la description
                            for shop_data in shops_data:
                                shop_id, name, description, shop_type, metadata = shop_data
                                
                                # Vérifier si la ville est mentionnée dans la description ou les métadonnées
                                if (description and city_name.lower() in description.lower()) or \
                                   (metadata and city_name.lower() in metadata.lower()):
                                    shop = Shop(
                                        shop_id=shop_id,
                                        name=name if name else f"Boutique {shop_id[:8]}",
                                        description=description if description else "Une boutique mystérieuse",
                                        shop_type=shop_type if shop_type else "general",
                                        location_id=location_id
                                    )
                                    shop.inventory = self._load_shop_inventory(shop)
                                    shops.append(shop)
                except Exception as e:
                    logger.warning(f"[SHOP_MANAGER] Erreur lors de la recherche par world_id: {e}")

            # MÉTHODE 4: FALLBACK - Recherche de toutes les boutiques du monde actif
            try:
                # Si aucune boutique n'est trouvée et que nous sommes dans le monde actif,
                # chercher toutes les boutiques sans filtre d'emplacement
                if not shops:
                    world_id = self.get_first_world_id()
                    if world_id:
                        cursor.execute("""
                            SELECT s.id, s.name, s.description, s.shop_type, l.name
                            FROM shops s
                            LEFT JOIN locations l ON s.location_id = l.id
                            WHERE s.world_id = ?
                            LIMIT 50
                        """, (world_id,))
                        
                        shops_data = cursor.fetchall()
                        if shops_data:
                            logger.info(f"[SHOP_MANAGER] FALLBACK: {len(shops_data)} boutiques trouvées pour le monde {world_id}")
                            
                            # Associer temporairement ces boutiques à l'emplacement actuel
                            for shop_data in shops_data:
                                shop_id, name, description, shop_type, shop_location_name = shop_data
                                shop = Shop(
                                    shop_id=shop_id,
                                    name=name if name else f"Boutique {shop_id[:8]}",
                                    description=description if description else "Une boutique mystérieuse",
                                    shop_type=shop_type if shop_type else "general",
                                    location_id=location_id
                                )
                                shop.inventory = self._load_shop_inventory(shop)
                                shops.append(shop)
                            
                            # Ajouter un log pour indiquer que ce sont des boutiques temporairement relocalisées
                            if shops:
                                logger.warning(f"[SHOP_MANAGER] {len(shops)} boutiques d'autres villes temporairement affichées à {city_name or location_id}")
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la recherche de toutes les boutiques: {e}")

            logger.info(f"[SHOP_MANAGER] {len(shops)} boutiques trouvées pour l'emplacement: {location_id}")
            return shops
            
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors de la récupération des boutiques: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_shop(self, shop_id):
        """
        Récupère une boutique par son ID
        
        Args:
            shop_id (str): ID de la boutique à récupérer
            
        Returns:
            Shop: L'objet boutique correspondant, ou None si non trouvé
        """
        if not shop_id:
            logger.warning("[SHOP_MANAGER] ID de boutique non spécifié")
            return None
            
        # Si déjà en cache, retourner directement
        if shop_id in self.shops:
            logger.debug(f"[SHOP_MANAGER] Boutique {shop_id} récupérée depuis le cache")
            return self.shops[shop_id]
        
        try:
            cursor = self.world_loader.get_connection().cursor()
            
            # D'abord, vérifions la structure de la table shops
            cursor.execute("PRAGMA table_info(shops)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Déterminer le nom des colonnes
            id_column = "id"
            type_column = "shop_type" if "shop_type" in columns else "type"
            
            # Vérifier si la table shops existe et a les bonnes colonnes
            query = f"SELECT {id_column}, name, description, {type_column}, location_id FROM shops WHERE {id_column} = ?"
            
            cursor.execute(query, (shop_id,))
            
            shop_data = cursor.fetchone()
            if shop_data:
                shop_id, name, description, shop_type, city_id = shop_data
                logger.debug(f"[SHOP_MANAGER] Boutique trouvée: {shop_id} - {name} (type: {shop_type})")
                
                # Créer l'objet Shop avec le bon ordre des paramètres
                shop = Shop(shop_id, name, description, shop_type, city_id)
                # Initialiser l'inventaire comme une liste vide avant de le charger
                shop.inventory = []
                
                # Charger l'inventaire de la boutique
                self._load_shop_inventory(shop)
                # Protection contre les cas où l'inventaire pourrait être None
                if shop.inventory is None:
                    shop.inventory = []
                logger.debug(f"[SHOP_MANAGER] Inventaire chargé pour {name}: {len(shop.inventory)} items")
                
                return shop
            else:
                # Essayons une recherche plus large en cas de problème d'ID
                logger.warning(f"[SHOP_MANAGER] Aucune boutique trouvée avec l'ID exact {shop_id}, recherche alternative")
                
                # Rechercher par nom si l'ID n'est pas trouvé exactement
                cursor.execute(f"SELECT {id_column}, name, description, {type_column}, location_id FROM shops WHERE name LIKE ? LIMIT 1", (f"%{shop_id}%",))
                
                shop_data = cursor.fetchone()
                if shop_data:
                    shop_id, name, description, shop_type, city_id = shop_data
                    logger.info(f"[SHOP_MANAGER] Boutique trouvée par recherche alternative: {shop_id} - {name}")
                    
                    # Créer l'objet Shop avec le bon ordre des paramètres
                    shop = Shop(shop_id, name, description, shop_type, city_id)
                    # Initialiser l'inventaire comme une liste vide avant de le charger
                    shop.inventory = []
                    
                    # Charger l'inventaire de la boutique
                    self._load_shop_inventory(shop)
                    # Protection contre les cas où l'inventaire pourrait être None
                    if shop.inventory is None:
                        shop.inventory = []
                    logger.debug(f"[SHOP_MANAGER] Inventaire chargé pour {name}: {len(shop.inventory)} items")
                    
                    return shop
                
                logger.warning(f"[SHOP_MANAGER] Aucune boutique trouvée avec l'ID ou le nom contenant {shop_id}")
                return None
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors de la récupération de la boutique {shop_id}: {str(e)}")
            import traceback
            logger.error(f"[SHOP_MANAGER] Traceback: {traceback.format_exc()}")
            return None
            
    def _load_shop_inventory(self, shop):
        """Charge l'inventaire d'un magasin depuis la base de données"""
        logger.debug(f"Chargement de l'inventaire pour {shop.name}")
        
        if not shop:
            return []
            
        # S'assurer que l'inventaire est initialisé comme une liste vide
        if not hasattr(shop, 'inventory') or shop.inventory is None:
            shop.inventory = []
            
        try:
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Vérifier la structure de la table shops
            cursor.execute("PRAGMA table_info(shops)")
            columns_shops = [col[1] for col in cursor.fetchall()]
            
            # Vérifier la structure de la table shop_inventory
            cursor.execute("PRAGMA table_info(shop_inventory)")
            columns_inventory = [col[1] for col in cursor.fetchall()]
            
            # Déterminer le nom des colonnes
            shop_id_column = "shop_id" if "shop_id" in columns_inventory else "id"
            
            # Déterminer les colonnes disponibles pour la requête
            available_columns = ["item_id", "item_type", "quantity", "price_modifier"]
            if "is_special" in columns_inventory:
                available_columns.append("is_special")
            if "metadata" in columns_inventory:
                available_columns.append("metadata")
                
            # Construire la requête dynamiquement
            columns_str = ", ".join(available_columns)
            
            # Charger l'inventaire depuis la base de données
            query = f"""
                SELECT {columns_str} 
                FROM shop_inventory 
                WHERE {shop_id_column} = ?
            """
            
            logger.debug(f"Requête d'inventaire: {query} avec paramètre: {shop.id}")
            cursor.execute(query, (shop.id,))
            
            # Récupérer les noms de colonnes
            column_names = [description[0] for description in cursor.description]
            
            inventory_items = cursor.fetchall()
            
            # Assurons-nous que nous avons bien une liste pour l'inventaire
            if shop.inventory is None:
                shop.inventory = []
            
            for inv_item in inventory_items:
                try:
                    # Créer un dictionnaire en associant les noms de colonnes aux valeurs
                    item_data = {column_names[i]: inv_item[i] for i in range(len(column_names))}
                    
                    item_type = item_data['item_type']
                    item_id = item_data['item_id']
                    
                    # Chargement des détails de l'article selon son type
                    item = self._load_item_details(conn, item_type, item_id)
                    
                    if item:
                        # Calcul du prix avec le modificateur spécifique à cet article dans l'inventaire
                        price_modifier = item_data.get('price_modifier', 1.0)
                        price = int(item.price * price_modifier) if hasattr(item, 'price') else int(100 * price_modifier)
                        
                        # Ajout à l'inventaire de la boutique
                        shop.inventory.append((item, price))
                except Exception as item_error:
                    logger.error(f"Erreur lors du traitement d'un item de l'inventaire: {item_error}")
                    continue
                    
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors du chargement de l'inventaire de la boutique {shop.name}: {e}")
            import traceback
            logger.error(f"[SHOP_MANAGER] Traceback: {traceback.format_exc()}")
            # Générer un inventaire par défaut en cas d'erreur, mais ne pas écraser un inventaire existant
            if not shop.inventory or len(shop.inventory) == 0:
                shop.inventory = self._generate_default_inventory(shop)
        
        # Retourner l'inventaire chargé ou généré
        return shop.inventory
    
    def _generate_default_inventory(self, shop):
        """Génère un inventaire par défaut pour un magasin sans objets"""
        logger.info(f"Génération d'un inventaire par défaut pour {shop.name} (type: {shop.shop_type})")
        inventory = []
        
        # Déterminer quels types d'objets générer en fonction du type de magasin
        if shop.shop_type in ["hardware", "electronics", "general"]:
            # Matériel informatique
            inventory.extend([
                (HardwareItem(f"default_cpu_{i}", f"Processeur de base {i}00MHz", "cpu", 
                            "Un processeur de base pour tout ordinateur.", price=100 + i*50), 100 + i*50)
                for i in range(1, 4)
            ])
            inventory.extend([
                (HardwareItem(f"default_ram_{i}", f"Mémoire RAM {i}Go", "ram", 
                            "Module de mémoire vive standard.", price=80 + i*40), 80 + i*40)
                for i in range(1, 5)
            ])
            inventory.extend([
                (HardwareItem(f"default_ssd_{i}", f"SSD {i*250}Go", "ssd", 
                            "Disque SSD pour un stockage rapide.", price=120 + i*60), 120 + i*60)
                for i in range(1, 3)
            ])
        
        if shop.shop_type in ["software", "digital_services", "general"]:
            # Logiciels
            inventory.extend([
                (SoftwareItem(f"default_os_{i}", f"Système d'exploitation v{i}.0", "os", 
                            "Système d'exploitation de base.", price=150 + i*75, version=f"{i}.0"), 150 + i*75)
                for i in range(1, 4)
            ])
            inventory.extend([
                (SoftwareItem(f"default_security_{i}", f"Parefeu Niveau {i}", "firewall", 
                            "Protection de base contre les intrusions.", price=120 + i*80, version=f"{i}.5"), 120 + i*80)
                for i in range(1, 3)
            ])
        
        if shop.shop_type in ["consumables", "general", "black_market"]:
            # Consommables
            inventory.extend([
                (ConsumableItem(f"default_energy_{i}", f"Boisson énergisante +{i*10}", "drink", 
                               f"Restaure {i*10}% d'énergie.", price=10 + i*5, 
                               effects={"energy": i*10}), 10 + i*5)
                for i in range(1, 5)
            ])
            inventory.extend([
                (ConsumableItem(f"default_focus_{i}", f"Stimulant de concentration x{i}", "stimulant", 
                               f"Augmente la concentration de {i*5}% pendant 10 minutes.", price=25 + i*15, 
                               effects={"focus": i*5, "duration": 600}), 25 + i*15)
                for i in range(1, 3)
            ])
        
        if shop.shop_type in ["weapons", "black_market"]:
            # Armes
            inventory.extend([
                (WeaponItem(f"default_weapon_{i}", f"Pistolet de défense MK{i}", "pistol", 
                          f"Arme de poing standard pour la défense personnelle.", 
                          damage=10 + i*5, damage_type='PHYSICAL', range=10 + i*2, accuracy=70 + i*5, price=200 + i*100), 200 + i*100)
                for i in range(1, 3)
            ])
        
        if shop.shop_type in ["implants", "cybernetics", "black_market"]:
            # Implants
            inventory.extend([
                (ImplantItem(f"default_implant_{i}", f"Implant neural de base v{i}", "neural", 
                           f"Améliore légèrement les capacités cognitives.", 
                           level=i, price=300 + i*150,
                           stats_bonus={"intelligence": i*3, "memory": i*2},
                           humanity_cost=5, installation_difficulty=i), 300 + i*150)
                for i in range(1, 3)
            ])
        
        # Si toujours vide, ajouter quelques objets génériques
        if not inventory:
            inventory.extend([
                (Item(id=f"default_item_{i}", 
                     name=f"Objet générique {i}", 
                     type="misc", 
                     description="Un objet quelconque.", 
                     value=50 + i*10), 50 + i*10)
                for i in range(1, 6)
            ])
        
        logger.info(f"Inventaire par défaut généré pour {shop.name}: {len(inventory)} objets")
        return inventory
    
    def add_item_to_shop(self, shop_id, item, price=None):
        """
        Ajoute un item à l'inventaire d'une boutique
        
        Args:
            shop_id (str): ID de la boutique
            item (Item): L'objet item à ajouter
            price (int, optional): Prix de vente (si non spécifié, calculé automatiquement)
            
        Returns:
            bool: True si succès, False sinon
        """
        logger.info(f"[SHOP_MANAGER] === Ajout d'item à la boutique {shop_id} ===" )
        logger.debug(f"[SHOP_MANAGER] Ajout de l'item {item.id} ({item.name}) à la boutique {shop_id}")
        
        # Récupérer la boutique
        shop = self.get_shop(shop_id)
        if not shop:
            logger.warning(f"[SHOP_MANAGER] Boutique {shop_id} non trouvée pour l'ajout d'item")
            return False
        
        # Calculer le prix si non spécifié
        if price is None:
            # Prix de base selon la rareté
            base_price = {
                'common': 50,
                'uncommon': 100,
                'rare': 250,
                'epic': 500,
                'legendary': 1000
            }.get(getattr(item, 'rarity', 'common'), 50)
            
            # Modifier selon le type d'item
            type_multiplier = {
                'weapon': 1.5,
                'armor': 1.3,
                'hardware': 1.2,
                'software': 1.1,
                'consumable': 0.8
            }.get(getattr(item, 'item_type', 'consumable'), 1.0)
            
            # Formule finale
            price = int(base_price * type_multiplier)
            logger.debug(f"[SHOP_MANAGER] Prix calculé pour {item.name}: {price} crédits (base: {base_price}, mult: {type_multiplier})")
        
        try:
            # Vérifier si l'item existe déjà dans la base de données
            cursor = self.world_loader.get_connection().cursor()
            cursor.execute("SELECT id FROM items WHERE id = ?", (item.id,))
            if not cursor.fetchone():
                # Sauvegarder l'item dans la base de données
                logger.debug(f"[SHOP_MANAGER] Ajout de l'item {item.id} à la table des items")
                
                # Préparer les propriétés au format JSON
                properties = {}
                for attr in dir(item):
                    if not attr.startswith('_') and attr not in ['id', 'name', 'description', 'item_type', 'rarity']:
                        properties[attr] = getattr(item, attr)
                
                properties_json = json.dumps(properties)
                
                cursor.execute(
                    """INSERT INTO items (id, name, item_type, description, properties, rarity) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (item.id, item.name, getattr(item, 'item_type', 'misc'), 
                     getattr(item, 'description', ''), properties_json, getattr(item, 'rarity', 'common'))
                )
            
            # Ajouter à l'inventaire de la boutique
            logger.debug(f"[SHOP_MANAGER] Ajout de l'item {item.id} à l'inventaire de la boutique {shop_id} (prix: {price})")
            cursor.execute(
                """INSERT OR REPLACE INTO shop_inventory (shop_id, item_id, price) 
                VALUES (?, ?, ?)""",
                (shop_id, item.id, price)
            )
            
            self.world_loader.get_connection().commit()
            logger.info(f"[SHOP_MANAGER] Item {item.name} ajouté à la boutique {shop.name} avec succès")
            
            # Mettre à jour l'objet boutique en mémoire
            shop.add_to_inventory(item, price)
            
            return True
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors de l'ajout de l'item à la boutique: {str(e)}")
            import traceback
            logger.error(f"[SHOP_MANAGER] Traceback: {traceback.format_exc()}")
            return False
    
    def remove_item_from_shop(self, shop_id: str, item_index: int) -> bool:
        """
        Supprime un article de l'inventaire d'une boutique.
        
        Args:
            shop_id: ID de la boutique
            item_index: Index de l'article dans l'inventaire
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        shop = self.shops.get(shop_id)
        if not shop or item_index < 0 or item_index >= len(shop.inventory):
            return False
        
        # Récupération de l'article à supprimer
        item, _ = shop.inventory[item_index]
        
        # Suppression de l'inventaire
        shop.inventory.pop(item_index)
        
        # Synchronisation avec la base de données
        try:
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Suppression de l'entrée d'inventaire
            cursor.execute("""
                DELETE FROM shop_inventory
                WHERE shop_id = ? AND item_id = ?
            """, (shop_id, item.id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression d'un article de la boutique: {e}")
            return False
    
    def is_player_in_compatible_location(self, player_location_id: str, shop_location_id: str) -> bool:
        """
        Détermine si le joueur est dans un emplacement compatible avec la boutique.
        Prend en compte la hiérarchie des emplacements (ex: un bâtiment dans une ville).
        
        Args:
            player_location_id: ID de l'emplacement actuel du joueur
            shop_location_id: ID de l'emplacement de la boutique
            
        Returns:
            True si l'emplacement est compatible, False sinon
        """
        # Correspondance directe
        if player_location_id == shop_location_id:
            return True
            
        # Vérifier si le joueur est dans un bâtiment de la ville de la boutique
        # Format conventionnel des IDs de bâtiment: "building_{city_id}_{unique_suffix}"
        if player_location_id.startswith("building_") and "_" in player_location_id:
            # Extraire l'ID de la ville depuis l'ID du bâtiment
            parts = player_location_id.split("_", 2)
            if len(parts) >= 3:
                city_id = parts[1]
                # Si la boutique est dans cette ville, le joueur peut y accéder
                if city_id == shop_location_id:
                    return True
                    
        return False
    
    def get_city_id_from_location(self, location_id: str) -> str:
        """
        Extrait l'ID de la ville à partir d'un ID de localisation.
        Si le joueur est dans un bâtiment, on extrait l'ID de la ville du bâtiment.
        Sinon, on suppose que le joueur est directement dans une ville.
        
        Args:
            location_id: ID de la localisation (ville ou bâtiment)
            
        Returns:
            ID de la ville correspondante ou l'ID original si ce n'est pas un bâtiment
        """
        logger.debug(f"[SHOP_MANAGER] Extraction de l'ID de ville à partir de: {location_id}")
        
        # Si l'ID de localisation est vide, retourner 'default'
        if not location_id:
            logger.warning("[SHOP_MANAGER] ID de localisation vide, utilisation de 'default'")
            return 'default'
        
        # Format attendu des IDs de bâtiment: "building_{city_id}_{unique_suffix}"
        if location_id.startswith("building_") and "_" in location_id:
            parts = location_id.split("_", 2)
            if len(parts) >= 3:
                city_id = parts[1]
                logger.debug(f"[SHOP_MANAGER] ID de ville extrait du bâtiment: {city_id}")
                return city_id
        
        # Si ce n'est pas un bâtiment ou si le format est invalide,
        # on suppose que c'est directement une ville
        # Essayons de voir si nous pouvons trouver l'ID de la ville dans la base de données
        try:
            conn = self.world_loader.get_connection()
            if conn:
                cursor = conn.cursor()
                
                # Vérifier si la table locations existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='locations'")
                if cursor.fetchone():
                    # Vérifier si l'ID correspond à une localisation existante
                    cursor.execute("PRAGMA table_info(locations)")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Déterminer le nom de la colonne ID (id ou location_id)
                    id_column = "location_id" if "location_id" in columns else "id"
                    
                    # Déterminer le nom de la colonne type (location_type ou type)
                    type_column = "location_type" if "location_type" in columns else "type"
                    
                    # Chercher par ID
                    query = f"SELECT {id_column}, name, {type_column} FROM locations WHERE {id_column} = ?"
                    cursor.execute(query, (location_id,))
                    location_data = cursor.fetchone()
                    
                    if location_data:
                        # Si c'est une ville, utiliser son ID
                        loc_type = location_data[2] if location_data[2] else ""
                        if loc_type.lower() in ['city', 'town', 'village', 'metropolis']:
                            logger.debug(f"[SHOP_MANAGER] Localisation '{location_id}' identifiée comme une ville")
                            return location_id
                        # Si c'est un bâtiment, chercher sa ville
                        else:
                            # Chercher la ville de ce bâtiment s'il y a une relation
                            if 'parent_id' in columns or 'parent_location_id' in columns:
                                parent_column = "parent_location_id" if "parent_location_id" in columns else "parent_id"
                                # Exécuter une nouvelle requête pour récupérer le parent_id
                                parent_query = f"SELECT {parent_column} FROM locations WHERE {id_column} = ?"
                                cursor.execute(parent_query, (location_id,))
                                parent_row = cursor.fetchone()
                                if parent_row and parent_row[0]:
                                    parent_id = parent_row[0]
                                    logger.debug(f"[SHOP_MANAGER] Bâtiment trouvé avec parent_id: {parent_id}")
                                    return parent_id
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors de la recherche dans la base de données: {str(e)}")
    
        # Par défaut, retourner l'ID original
        logger.debug(f"[SHOP_MANAGER] Utilisation de l'ID non modifié comme ID de ville: {location_id}")
        return location_id
    
    def get_first_world_id(self):
        """
        Récupère l'ID du premier monde disponible dans la base de données.
        
        Returns:
            str: ID du premier monde trouvé, ou "default" si aucun monde n'est trouvé
        """
        try:
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Vérifier si la table worlds existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worlds';")
            if not cursor.fetchone():
                logger.warning("La table worlds n'existe pas dans la base de données.")
                return "default"
            
            # Récupérer le premier monde
            cursor.execute("SELECT id FROM worlds LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                world_id = result[0]
                logger.info(f"Premier monde trouvé dans la base de données: {world_id}")
                return world_id
            else:
                # Si aucun monde n'est trouvé, essayer de récupérer l'ID de monde à partir des magasins
                cursor.execute("SELECT DISTINCT world_id FROM shops LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    world_id = result[0]
                    logger.info(f"Monde trouvé à partir des magasins: {world_id}")
                    return world_id
                
                logger.warning("Aucun monde trouvé dans la base de données.")
                return "default"
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du premier monde: {e}")
            return "default"
    
    def _initialize_shop_tables(self):
        """
        Initialise les tables de boutiques dans la base de données si elles n'existent pas.
        """
        try:
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Création de la table des boutiques
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shops (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    shop_type TEXT NOT NULL,
                    location_id TEXT,
                    owner_id TEXT,
                    faction_id TEXT,
                    reputation INTEGER DEFAULT 5,
                    price_modifier REAL DEFAULT 1.0,
                    is_legal INTEGER DEFAULT 1,
                    special_items TEXT,
                    services TEXT,
                    open_hours TEXT,
                    inventory_refresh_rate INTEGER DEFAULT 24,
                    requires_reputation INTEGER DEFAULT 0,
                    required_reputation_level INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)
            
            # Création de la table d'inventaire des boutiques
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shop_inventory (
                    id TEXT PRIMARY KEY,
                    shop_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    price_modifier REAL DEFAULT 1.0,
                    is_special INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Tables de boutiques initialisées avec succès")
            
            # Créer des boutiques de démonstration pour le monde par défaut
            self._create_demo_shops()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des tables de boutiques: {e}")

    def _create_demo_shops(self):
        """
        Crée des boutiques de démonstration pour le mode test.
        Cette fonction est appelée uniquement si les tables viennent d'être créées.
        """
        try:
            # Vérifier si des boutiques existent déjà
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Vérifier la structure de la table shops
            cursor.execute("PRAGMA table_info(shops)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Déterminer le nom des colonnes
            id_column = "id"
            type_column = "shop_type" if "shop_type" in columns else "type"
            
            # Vérifier si des boutiques existent déjà
            cursor.execute("SELECT COUNT(*) FROM shops")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Créer des boutiques de démonstration pour Tokyo (location_id: tokyo)
                shop_id = str(uuid.uuid4())[:8]
                cursor.execute("""
                    INSERT INTO shops (id, world_id, name, description, """ + type_column + """, location_id, price_modifier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"shop_{shop_id}", "default", "CyberTech Tokyo", 
                    "Boutique de matériel informatique haut de gamme", "hardware", 
                    "tokyo", 1.2
                ))
                
                # Boutique de logiciels à Tokyo
                shop_id = str(uuid.uuid4())[:8]
                cursor.execute("""
                    INSERT INTO shops (id, world_id, name, description, """ + type_column + """, location_id, price_modifier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"shop_{shop_id}", "default", "Digital Dreams", 
                    "Boutique spécialisée dans les logiciels de sécurité", "software", 
                    "tokyo", 1.0
                ))
                
                # Marché noir à Tokyo
                shop_id = str(uuid.uuid4())[:8]
                cursor.execute("""
                    INSERT INTO shops (id, world_id, name, description, """ + type_column + """, location_id, price_modifier, is_legal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"shop_{shop_id}", "default", "Back Alley Tech", 
                    "Marché noir pour équipement de hacking", "black_market", 
                    "tokyo", 1.5, 0
                ))
                
                # Boutique à New York (location_id: new_york)
                shop_id = str(uuid.uuid4())[:8]
                cursor.execute("""
                    INSERT INTO shops (id, world_id, name, description, """ + type_column + """, location_id, price_modifier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"shop_{shop_id}", "default", "Manhattan Tech", 
                    "Grande surface de matériel informatique", "hardware", 
                    "new_york", 0.9
                ))
                
                conn.commit()
                logger.info("Boutiques de démonstration créées avec succès")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des boutiques de démonstration: {e}")

    def load_shops_for_world(self, world_id: str) -> bool:
        """
        Charge toutes les boutiques pour un monde spu00e9cifique.
        
        Args:
            world_id: Identifiant du monde
        
        Returns:
            True si le chargement est ru00e9ussi, False sinon
        """
        logger.info(f"[SHOP_MANAGER] Chargement des boutiques pour le monde: {world_id}")
        
        try:
            # Ru00e9initialiser la liste des boutiques
            self.shops = {}
            self.location_shops = {}
            
            # Obtenir une connexion u00e0 la base de donnu00e9es
            conn = self.world_loader.get_connection()
            if not conn:
                logger.error("[SHOP_MANAGER] Impossible d'obtenir une connexion u00e0 la base de donnu00e9es")
                return False
            
            cursor = conn.cursor()
            
            # Ru00e9cupu00e9rer toutes les villes de ce monde
            logger.debug(f"[SHOP_MANAGER] Ru00e9cupu00e9ration des villes du monde {world_id}")
            cursor.execute("PRAGMA table_info(locations)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Du00e9terminer les noms de colonnes corrects
            id_column = "location_id" if "location_id" in columns else "id"
            world_column = "world_id" if "world_id" in columns else "world"
            type_column = "location_type" if "location_type" in columns else "type"
            
            # Si la colonne de type n'existe pas, utiliser une autre mu00e9thode pour identifier les villes
            city_query = ""
            if type_column in columns:
                city_query = f"SELECT {id_column}, name FROM locations WHERE {world_column} = ? AND {type_column} = 'city'"
            else:
                # Si pas de colonne de type, chercher par d'autres moyens (parent_id NULL ou tags contenant 'ville')
                if 'parent_id' in columns or 'parent_location_id' in columns:
                    parent_column = "parent_location_id" if "parent_location_id" in columns else "parent_id"
                    city_query = f"SELECT {id_column}, name FROM locations WHERE {world_column} = ? AND {parent_column} IS NULL"
                elif 'tags' in columns:
                    city_query = f"SELECT {id_column}, name FROM locations WHERE {world_column} = ? AND tags LIKE '%ville%' OR tags LIKE '%city%'"
                else:
                    # Si aucun moyen de du00e9terminer les villes, utiliser toutes les locations
                    city_query = f"SELECT {id_column}, name FROM locations WHERE {world_column} = ?"
                    logger.warning("[SHOP_MANAGER] Impossible de du00e9terminer quelles locations sont des villes - utilisation de toutes les locations")
        
            # Exu00e9cuter la requu00eate pour ru00e9cupu00e9rer les villes
            try:
                cursor.execute(city_query, (world_id,))
                cities = cursor.fetchall()
                logger.info(f"[SHOP_MANAGER] {len(cities)} villes trouvu00e9es dans le monde {world_id}")
            except Exception as e:
                logger.error(f"[SHOP_MANAGER] Erreur lors de la ru00e9cupu00e9ration des villes: {str(e)}")
                # Si la requu00e9te u00e9choue, essayer une requu00e9te plus simple sans filtrage par type
                cursor.execute(f"SELECT {id_column}, name FROM locations WHERE {world_column} = ?", (world_id,))
                cities = cursor.fetchall()
                logger.info(f"[SHOP_MANAGER] {len(cities)} locations trouvu00e9es dans le monde {world_id} (sans filtrage par type)")
        
            # Ru00e9cupu00e9rer les boutiques pour chaque ville
            total_shops = 0
            for city_id, city_name in cities:
                logger.debug(f"[SHOP_MANAGER] Chargement des boutiques pour la ville: {city_name} (ID: {city_id})")
                shops = self.get_shops_by_location(city_id)
                
                # Enregistrer les boutiques par ville
                if shops:
                    self.location_shops[city_id] = shops
                    logger.info(f"[SHOP_MANAGER] {len(shops)} boutiques trouvu00e9es pour {city_name} (ID: {city_id})")
                    total_shops += len(shops)
                    
                    # Ajouter u00e9galement les boutiques au dictionnaire principal
                    for shop in shops:
                        self.shops[shop.id] = shop
        
            logger.info(f"[SHOP_MANAGER] Total: {total_shops} boutiques chargu00e9es pour le monde {world_id}")
        
            # Chargement des inventaires pour chaque boutique
            logger.debug("[SHOP_MANAGER] Chargement des inventaires des boutiques")
            for shop_id, shop in self.shops.items():
                try:
                    shop.inventory = self._load_shop_inventory(shop)
                    logger.debug(f"[SHOP_MANAGER] Inventaire chargu00e9 pour la boutique {shop.name}: {len(shop.inventory)} objets")
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors du chargement de l'inventaire de la boutique {shop.name}: {str(e)}")
        
            return True
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors du chargement des boutiques: {str(e)}")
            import traceback
            logger.error(f"[SHOP_MANAGER] Traceback: {traceback.format_exc()}")
            return False
    
    def get_shops_by_type(self, shop_type: str) -> List[Shop]:
        """
        Récupère les magasins par type
        
        Args:
            shop_type: Type de magasin à rechercher
            
        Returns:
            Liste des magasins du type spécifié
        """
        try:
            conn = self.world_loader.get_connection()
            cursor = conn.cursor()
            
            # Vérifier la structure de la table shops
            cursor.execute("PRAGMA table_info(shops)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Déterminer le nom des colonnes
            id_column = "id"
            type_column = "shop_type" if "shop_type" in columns else "type"
            
            # Récupérer les magasins par type
            cursor.execute(f"""
                SELECT {id_column}, name, description, {type_column}, location_id 
                FROM shops 
                WHERE {type_column} = ?
            """, (shop_type,))
            
            shops = []
            for row in cursor.fetchall():
                shop_id, name, description, shop_type, location_id = row
                shop = Shop(shop_id, name, description, shop_type, location_id)
                self._load_shop_inventory(shop)
                shops.append(shop)
                
            return shops
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des magasins par type: {e}")
            return []

    def _load_item_details(self, conn, item_type: str, item_id: str):
        """
        Charge les détails d'un article spécifique selon son type.
        
        Args:
            conn: Connexion à la base de données
            item_type: Type d'article (hardware, software, consumable)
            item_id: ID de l'article
            
        Returns:
            Instance de l'article ou None si non trouvé
        """
        try:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            
            # Normaliser le type d'article en minuscules
            item_type_lower = item_type.lower()
            
            # Extraire l'ID réel
            real_item_id = item_id
            
            # Si l'item_id contient déjà le préfixe correspondant à son type, l'utiliser tel quel
            # C'est souvent le cas des items provenant directement de la base de données
            if (item_id.startswith('hardware_') and item_type_lower in ['hardware', 'cpu', 'ram', 'ssd', 'tool']) or \
               (item_id.startswith('software_') and item_type_lower in ['software', 'os', 'firewall', 'vpn']) or \
               (item_id.startswith('weapon_') and item_type_lower in ['weapon', 'knife', 'pistol', 'rifle']) or \
               (item_id.startswith('implant_') and item_type_lower in ['implant', 'neural', 'optical']) or \
               (item_id.startswith('clothing_') and item_type_lower in ['clothing', 'armor', 'jacket']):
                # L'ID est déjà préfixé correctement, pas besoin de modifier
                pass
            else:
                # Si on a un préfixe de type mais pas le bon, extraire l'ID sans préfixe
                if '_' in item_id:
                    prefix, id_part = item_id.split('_', 1)
                    recognized_prefixes = ['hardware', 'software', 'weapon', 'implant', 'clothing', 'consumable']
                    if prefix.lower() in recognized_prefixes:
                        real_item_id = id_part
                        logger.debug(f"[SHOP_MANAGER] ID extrait du préfixe: {item_id} -> {real_item_id}")
            
            # Déterminer la table appropriée en fonction du type d'article
            table_name = None
            
            if item_type_lower.startswith('software') or item_type_lower in ['os', 'firewall', 'data_broker', 'vpn', 'crypto', 'cloud_storage']:
                table_name = 'software_items'
            elif item_type_lower.startswith('hardware') or item_type_lower in ['cpu', 'ram', 'ssd', 'tool']:
                table_name = 'hardware_items'
            elif item_type_lower.startswith('consumable') or item_type_lower in ['drink', 'stimulant', 'food']:
                table_name = 'consumable_items'
            elif item_type_lower.startswith('implant') or item_type_lower in ['neural', 'optical', 'skeletal', 'dermal', 'circulatory']:
                table_name = 'implant_items'
                # Vérifier si la table implant_items existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='implant_items'")
                if not cursor.fetchone():
                    # Si la table n'existe pas, créer un item générique
                    logger.info(f"[SHOP_MANAGER] Table implant_items non trouvée, création d'un implant générique pour {item_id}")
                    return self._create_generic_item(item_id, item_type)
            elif item_type_lower.startswith('clothing') or item_type_lower in ['armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']:
                table_name = 'clothing_items'
            elif item_type_lower == 'weapon' or item_type_lower in ['knife', 'pistol', 'rifle', 'shotgun', 'smg', 'sniper']:
                table_name = 'weapon_items'
            else:
                # Tenter de déterminer le type réel à partir du préfixe de l'ID
                if item_id.startswith('weapon_') and item_type_lower != 'weapon':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> weapon")
                    item_type_lower = 'weapon'
                    table_name = 'weapon_items'
                elif item_id.startswith('clothing_') and item_type_lower != 'clothing':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> clothing")
                    item_type_lower = 'clothing'
                    table_name = 'clothing_items'
                elif item_id.startswith('hardware_') and item_type_lower != 'hardware':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> hardware")
                    item_type_lower = 'hardware'
                    table_name = 'hardware_items'
                elif item_id.startswith('software_') and item_type_lower != 'software':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> software")
                    item_type_lower = 'software'
                    table_name = 'software_items'
                elif item_id.startswith('consumable_') and item_type_lower != 'consumable':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> consumable")
                    item_type_lower = 'consumable'
                    table_name = 'consumable_items'
                elif item_id.startswith('implant_') and item_type_lower != 'implant':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> implant")
                    item_type_lower = 'implant'
                    table_name = 'implant_items'
                elif item_id.startswith('food_') and item_type_lower != 'food':
                    logger.info(f"[SHOP_MANAGER] Type d'article corrigé: {item_type} -> food")
                    item_type_lower = 'food'
                    table_name = 'food_items'
                else:
                    logger.info(f"[SHOP_MANAGER] Type d'article non reconnu: {item_type}, création d'un article générique")
                    return self._create_generic_item(item_id, item_type)
            
            # Vérifier si la table existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                logger.info(f"[SHOP_MANAGER] Table {table_name} non trouvée dans la base de données, création d'un article générique")
                return self._create_generic_item(item_id, item_type)
            
            # Essayer avec l'ID original complet
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (item_id,))
            data = cursor.fetchone()
            
            # Si rien trouvé, essayer avec l'ID extrait
            if not data and item_id != real_item_id:
                cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (real_item_id,))
                data = cursor.fetchone()
            
            # Essayer avec préfixe + ID réel
            if not data:
                # Ajouter le préfixe correct basé sur le type de table
                prefixed_id = None
                if table_name == 'hardware_items':
                    prefixed_id = f"hardware_{real_item_id}"
                elif table_name == 'software_items':
                    prefixed_id = f"software_{real_item_id}"
                elif table_name == 'weapon_items':
                    prefixed_id = f"weapon_{real_item_id}"
                elif table_name == 'implant_items':
                    prefixed_id = f"implant_{real_item_id}"
                elif table_name == 'clothing_items':
                    prefixed_id = f"clothing_{real_item_id}"
                elif table_name == 'food_items':
                    prefixed_id = f"food_{real_item_id}"
                
                if prefixed_id:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (prefixed_id,))
                    data = cursor.fetchone()
            
            if not data:
                logger.info(f"[SHOP_MANAGER] Article {item_id} non trouvé dans la table {table_name}, création d'un article générique")
                return self._create_generic_item(item_id, item_type)
            
            # Récupérer les noms de colonnes
            column_names = [description[0] for description in cursor.description]
            # Créer un dictionnaire des données
            item_data = {column_names[i]: data[i] for i in range(len(column_names))}
            
            # Créer l'instance d'article appropriée selon le type
            if item_type_lower in ['hardware', 'cpu', 'ram', 'ssd', 'tool']:
                try:
                    # Convertir la chaîne 'type' en énumération HardwareType si possible
                    from .hardware import HardwareType
                    hw_type = item_data.get('hardware_type') or item_type
                    if isinstance(hw_type, str):
                        try:
                            for t in HardwareType:
                                if t.value == hw_type.lower():
                                    hw_type = t
                                    break
                            if isinstance(hw_type, str):
                                hw_type = HardwareType.TOOL  # Type par défaut
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors de la conversion du type hardware: {e}")
                            hw_type = HardwareType.TOOL
                    
                    # Convertir la chaîne 'rarity' en énumération HardwareRarity si possible
                    from .hardware import HardwareRarity
                    hw_rarity = item_data.get('rarity', 'common')
                    if isinstance(hw_rarity, str):
                        try:
                            for r in HardwareRarity:
                                if r.value == hw_rarity.lower():
                                    hw_rarity = r
                                    break
                            if isinstance(hw_rarity, str):
                                hw_rarity = HardwareRarity.COMMON  # Rareté par défaut
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors de la conversion de la rareté hardware: {e}")
                            hw_rarity = HardwareRarity.COMMON
                    
                    hardware_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Hardware {item_type.capitalize()}",
                        'type': hw_type,
                        'description': item_data.get('description') or f"Un équipement de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'rarity': hw_rarity,
                        'price': item_data.get('price', 100)
                    }
                    
                    # Ajouter stats si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats' in metadata:
                                    hardware_params['stats'] = metadata['stats']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats hardware: {e}")
                    
                    return HardwareItem(**hardware_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article hardware {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
                    
            elif item_type_lower in ['software', 'os', 'firewall', 'data_broker', 'vpn', 'crypto', 'cloud_storage']:
                try:
                    software_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Logiciel {item_type.capitalize()}",
                        'software_type': item_data.get('software_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un logiciel de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'version': item_data.get('version', '1.0'),
                        'price': item_data.get('price', 100)
                    }
                    
                    # Ajouter features si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'features' in metadata:
                                    software_params['features'] = metadata['features']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des features software: {e}")
                    
                    return SoftwareItem(**software_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article software {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['consumable', 'drink', 'stimulant', 'food']:
                try:
                    consumable_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Consommable {item_type.capitalize()}",
                        'item_type': item_data.get('consumable_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un consommable de type {item_type}",
                        'price': item_data.get('price', 50),
                        'uses': item_data.get('uses', 1),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    # Ajouter effects si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'effects' in metadata:
                                    consumable_params['effects'] = metadata['effects']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des effects consumable: {e}")
                    
                    return ConsumableItem(**consumable_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article consumable {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
                    
            elif item_type_lower in ['implant', 'neural', 'optical', 'skeletal', 'dermal', 'circulatory']:
                try:
                    implant_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Implant {item_type.capitalize()}",
                        'implant_type': item_data.get('implant_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un implant de type {item_type}",
                        'level': 1,  # Valeur par défaut
                        'price': item_data.get('price', 100),
                        'rarity': item_data.get('rarity', 'COMMON')
                    }
                    
                    # Ajouter stats_bonus si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats_bonus' in metadata:
                                    implant_params['stats_bonus'] = metadata['stats_bonus']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats_bonus implant: {e}")
                    
                    return ImplantItem(**implant_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article implant {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['weapon', 'pistol', 'rifle', 'melee']:
                try:
                    # Extraire les données d'arme de metadata si disponible
                    weapon_metadata = {}
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                weapon_metadata = json.loads(item_data['metadata'])
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des metadata d'arme: {e}")
                    
                    return WeaponItem(
                        id=item_data.get('id') or item_id,
                        name=item_data.get('name') or f"Arme {item_type.capitalize()}",
                        weapon_type=item_type,
                        description=item_data.get('description') or f"Une arme de type {item_type}",
                        damage=weapon_metadata.get('damage', 10),
                        damage_type=weapon_metadata.get('damage_type', 'PHYSICAL'),
                        range=weapon_metadata.get('range', 10),
                        accuracy=weapon_metadata.get('accuracy', 70),
                        price=item_data.get('price', 200)
                    )
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article weapon {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type)
            
            elif item_type_lower in ['clothing', 'armor', 'jacket', 'pants', 'shirt', 'boots', 'hat', 'gloves']:
                try:
                    clothing_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Vêtement {item_type.capitalize()}",
                        'clothing_type': item_data.get('clothing_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un vêtement de type {item_type}",
                        'price': item_data.get('price', 50),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    # Ajouter stats si présent dans metadata
                    if 'metadata' in item_data and item_data['metadata']:
                        try:
                            if isinstance(item_data['metadata'], str):
                                metadata = json.loads(item_data['metadata'])
                                if 'stats' in metadata:
                                    clothing_params['stats'] = metadata['stats']
                        except Exception as e:
                            logger.error(f"[SHOP_MANAGER] Erreur lors du parsing des stats clothing: {e}")
                    
                    return ClothingItem(**clothing_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article clothing {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            elif item_type_lower in ['food']:
                try:
                    food_params = {
                        'id': item_data.get('id') or item_id,
                        'name': item_data.get('name') or f"Nourriture {item_type.capitalize()}",
                        'food_type': item_data.get('food_type') or item_type.upper(),
                        'description': item_data.get('description') or f"Un aliment de type {item_type}",
                        'price': item_data.get('price', 50),
                        'health_restore': item_data.get('health_restore', 10),
                        'energy_restore': item_data.get('energy_restore', 10),
                        'mental_restore': item_data.get('mental_restore', 5),
                        'uses': item_data.get('uses', 1),
                        'rarity': item_data.get('rarity', 'Common')
                    }
                    
                    return FoodItem(**food_params)
                except Exception as e:
                    logger.error(f"[SHOP_MANAGER] Erreur lors de la création de l'article food {item_id}: {e}")
                    return self._create_generic_item(item_id, item_type, item_data)
            
            else:
                # Article générique pour les autres types
                return self._create_generic_item(item_id, item_type)
                
        except Exception as e:
            logger.error(f"[SHOP_MANAGER] Erreur lors du chargement de l'article {item_id}: {e}")
            return self._create_generic_item(item_id, item_type)
