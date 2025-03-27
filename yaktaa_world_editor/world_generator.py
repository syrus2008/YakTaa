"""
Module de génération aléatoire de mondes pour YakTaa
Ce module permet de créer des mondes complets avec lieux, connexions, personnages, etc.
"""

import random
import string
import uuid
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import ipaddress

from database import get_database
# Import des générateurs spécifiques
import city_generator
import buildings_generator
import characters_generator
import connections_generator
import devices_generator
import networks_generator
import special_locations_generator
import hacking_puzzles_generator
import files_generator
import missions_generator
import story_elements_generator
import hardware_items_generator
import consumable_items_generator
import shops_generator
from shop_item_generator import ShopItemGenerator  # Import pour la génération d'objets de boutique
from constants import *  # Importer toutes les constantes
from init_database import init_database  # Import pour l'initialisation de la base de données

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator")

class WorldGenerator:
    """
    Classe pour générer aléatoirement des mondes complets pour YakTaa
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialise le générateur de monde
        
        Args:
            db_path: Chemin vers la base de données (optionnel)
        """
        self.db_path = db_path
        self.random = random.Random()  # Pour permettre de définir une seed
        
        # S'assurer que la base de données est correctement initialisée
        logger.info("Vérification de la structure de la base de données")
        init_database(self.db_path or "worlds.db")
        
        # Initialiser les attributs pour les paramètres de génération
        self.name = None
        self.author = "YakTaa Generator"
        self.complexity = 3
        self.city_count = 3
        self.special_location_count = 2
        self.character_count = 20
        self.device_count = 30
        self.implant_count = 10
        self.vulnerability_count = 15
        self.network_count = 20
        self.implant_complexity = 3
        self.vulnerability_complexity = 3
        self.network_complexity = 3
        
        # Paramètres pour les magasins et articles
        self.shop_count = 10
        self.shop_complexity = 3
        self.shop_types = {shop_type: True for shop_type in SHOP_TYPES}
        self.items_per_shop = 20
        self.rare_items_percentage = 20
        self.include_illegal_items = True
        self.include_featured_items = True
        self.include_limited_time_items = True
        
        # Nouveaux paramètres pour le combat
        self.enemy_type_distribution = {
            "HUMAN": 40, 
            "GUARD": 20, 
            "CYBORG": 15, 
            "DRONE": 10, 
            "ROBOT": 5, 
            "NETRUNNER": 5, 
            "MILITECH": 3, 
            "BEAST": 2
        }
        self.hostile_character_percentage = 30
        self.combat_difficulty = 3  # De 1 à 5
        self.default_ai_behavior = "Équilibré"
        self.combat_styles = ["Équilibré", "Corps à corps", "Distance"]
        self.enable_status_effects = True
        self.dot_effects_enabled = True
        self.cc_effects_enabled = True
        self.buff_effects_enabled = True
        self.status_effects_complexity = 3
        
        self.progress_callback = None
        
        logger.info("Générateur de monde initialisé")
    
    def set_seed(self, seed: Optional[int] = None) -> int:
        """
        Définit une seed pour la génération aléatoire
        
        Args:
            seed: Seed à utiliser (si None, utilise une seed aléatoire)
            
        Returns:
            La seed utilisée
        """
        if seed is None:
            seed = random.randint(1, 1000000)
        
        self.random.seed(seed)
        logger.info(f"Seed définie: {seed}")
        return seed
    
    def generate_world_name(self) -> str:
        """Génère un nom aléatoire pour le monde"""
        adjectives = ["Cyber", "Digital", "Neon", "Shadow", "Chrome", "Quantum", "Synthetic", "Virtual"]
        nouns = ["Realm", "Nexus", "Matrix", "Grid", "Domain", "Sphere", "Network", "Pulse"]
        
        return f"{self.random.choice(adjectives)} {self.random.choice(nouns)}"
    
    def generate_cities(self, db, world_id, num_cities):
        """Génère les villes du monde"""
        return city_generator.generate_cities(db, world_id, num_cities, self.random)
    
    def generate_districts(self, db, world_id, city_ids, num_districts_per_city):
        """Génère les districts des villes"""
        return city_generator.generate_districts(db, world_id, city_ids, num_districts_per_city, self.random)
    
    def generate_special_locations(self, db, world_id, num_special_locations):
        """Génère les lieux spéciaux"""
        return special_locations_generator.generate_special_locations(db, world_id, num_special_locations, self.random)
    
    def generate_connections(self, db, world_id, location_ids):
        """Génère les connexions entre lieux"""
        return connections_generator.generate_connections(db, world_id, location_ids, self.random)
    
    def generate_buildings(self, db, world_id, location_ids):
        """Génère les bâtiments"""
        return buildings_generator.generate_buildings(db, world_id, location_ids, self.random)
    
    def generate_characters(self, db, world_id, location_ids, num_characters, random_instance=None,
                         enemy_types=None, hostile_percentage=None, combat_difficulty=None,
                         ai_behavior=None, combat_styles=None, enable_status_effects=None):
        """Génère les personnages"""
        
        # Utiliser les paramètres par défaut de l'instance si non spécifiés
        if random_instance is None:
            random_instance = self.random
            
        if enemy_types is None:
            enemy_types = self.enemy_type_distribution
            
        if hostile_percentage is None:
            hostile_percentage = self.hostile_character_percentage
            
        if combat_difficulty is None:
            combat_difficulty = self.combat_difficulty
            
        if ai_behavior is None:
            ai_behavior = self.default_ai_behavior
            
        if combat_styles is None:
            combat_styles = self.combat_styles
            
        if enable_status_effects is None:
            enable_status_effects = self.enable_status_effects
        
        return characters_generator.generate_characters(
            db, 
            world_id, 
            location_ids, 
            num_characters, 
            random_instance,
            enemy_types=enemy_types,
            hostile_percentage=hostile_percentage,
            combat_difficulty=combat_difficulty,
            ai_behavior=ai_behavior,
            combat_styles=combat_styles,
            enable_status_effects=enable_status_effects
        )
    
    def generate_devices(self, db, world_id, location_ids, character_ids, num_devices):
        """Génère les appareils électroniques"""
        return devices_generator.generate_devices(db, world_id, location_ids, character_ids, num_devices, self.random)
    
    def generate_networks(self, db, world_id, building_ids):
        """Génère les réseaux"""
        return networks_generator.generate_networks(db, world_id, building_ids, self.random)
    
    def generate_hacking_puzzles(self, db, world_id, device_ids, network_ids):
        """Génère les puzzles de hacking"""
        return hacking_puzzles_generator.generate_hacking_puzzles(db, world_id, device_ids, network_ids, self.random)
    
    def generate_files(self, db, world_id, device_ids):
        """Génère les fichiers"""
        return files_generator.generate_files(db, world_id, device_ids, self.random)
    
    def generate_missions(self, db, world_id, location_ids, character_ids, num_missions):
        """Génère les missions"""
        return missions_generator.generate_missions(db, world_id, location_ids, character_ids, num_missions, self.random)
    
    def generate_story_elements(self, db, world_id, location_ids, character_ids, mission_ids, num_story_elements):
        """Génère les éléments d'histoire"""
        return story_elements_generator.generate_story_elements(db, world_id, location_ids, character_ids, mission_ids, num_story_elements, self.random)
    
    def generate_hardware_items(self, db, world_id, device_ids, building_ids, character_ids, num_hardware_items):
        """Génère les objets hardware"""
        return hardware_items_generator.generate_hardware_items(db, world_id, device_ids, building_ids, character_ids, num_hardware_items, self.random)
    
    def generate_consumable_items(self, db, world_id, device_ids, building_ids, character_ids, num_consumable_items):
        """Génère les objets consommables"""
        return consumable_items_generator.generate_consumable_items(db, world_id, device_ids, building_ids, character_ids, num_consumable_items, self.random)
    
    def generate_shops(self, db, world_id, location_ids, building_ids, num_shops):
        """Génère les boutiques"""
        # Filtrer les types de magasins activés
        enabled_shop_types = [shop_type for shop_type, enabled in self.shop_types.items() if enabled]
        if not enabled_shop_types:
            enabled_shop_types = list(SHOP_TYPES)  # Utiliser tous les types si aucun n'est sélectionné
            
        return shops_generator.generate_shops(
            db, 
            world_id, 
            location_ids, 
            building_ids, 
            num_shops, 
            self.random,
            shop_types=enabled_shop_types,
            shop_complexity=self.shop_complexity
        )
    
    def generate_shop_inventory(self, db, world_id, shop_ids):
        """Génère l'inventaire des boutiques"""
        # Créer une instance du générateur d'articles
        item_generator = ShopItemGenerator(self.random)
        
        for shop_id in shop_ids:
            # Récupérer les informations du magasin
            cursor = db.conn.cursor()
            cursor.execute("SELECT shop_type, is_legal FROM shops WHERE id = ?", (shop_id,))
            shop_data = cursor.fetchone()
            
            if not shop_data:
                continue
                
            shop_type = shop_data["shop_type"]
            is_legal = bool(shop_data["is_legal"])
            
            # Déterminer le nombre d'articles pour ce magasin
            # Ajouter une variation aléatoire autour de la moyenne
            variation = int(self.items_per_shop * 0.3)  # 30% de variation
            num_items = max(5, self.items_per_shop + self.random.randint(-variation, variation))
            
            # Générer les articles
            for _ in range(num_items):
                # Déterminer si l'article est rare
                is_rare = self.random.randint(1, 100) <= self.rare_items_percentage
                
                # Déterminer si l'article est illégal (uniquement si autorisé et pour certains types de magasins)
                is_item_illegal = False
                if self.include_illegal_items and shop_type in ["WEAPON", "SOFTWARE", "BLACK_MARKET", "IMPLANT"]:
                    is_item_illegal = self.random.random() < 0.3  # 30% de chance d'être illégal
                
                # Si le magasin est légal, ne pas inclure d'articles illégaux
                if is_legal and is_item_illegal:
                    is_item_illegal = False
                
                # Déterminer si l'article est mis en avant
                is_featured = False
                if self.include_featured_items:
                    is_featured = self.random.random() < 0.1  # 10% de chance d'être mis en avant
                
                # Déterminer si l'article est à durée limitée
                is_limited_time = False
                expiry_date = None
                if self.include_limited_time_items:
                    is_limited_time = self.random.random() < 0.15  # 15% de chance d'être à durée limitée
                    if is_limited_time:
                        # Date d'expiration entre 1 et 30 jours
                        days = self.random.randint(1, 30)
                        expiry_date = (datetime.now() + timedelta(days=days)).isoformat()
                
                # Générer l'article en fonction du type de magasin
                item_id = None
                if shop_type == "WEAPON":
                    item_id = item_generator.generate_random_weapon(db, world_id, is_item_illegal)
                elif shop_type == "IMPLANT":
                    item_id = item_generator.generate_random_implant(db, world_id, is_item_illegal)
                elif shop_type == "HARDWARE":
                    item_id = item_generator.generate_random_hardware_item(db, world_id, is_item_illegal)
                elif shop_type == "SOFTWARE":
                    item_id = item_generator.generate_random_software_item(db, world_id, is_item_illegal)
                elif shop_type == "CLOTHING":
                    item_id = item_generator.generate_random_clothing_item(db, world_id, is_item_illegal)
                elif shop_type == "FOOD":
                    item_id = item_generator.generate_random_food_item(db, world_id, is_item_illegal)
                elif shop_type == "GENERAL":
                    # Pour les magasins généraux, choisir un type d'article aléatoire
                    item_types = ["WEAPON", "HARDWARE", "SOFTWARE", "CLOTHING", "FOOD"]
                    random_type = self.random.choice(item_types)
                    if random_type == "WEAPON":
                        item_id = item_generator.generate_random_weapon(db, world_id, is_item_illegal)
                    elif random_type == "HARDWARE":
                        item_id = item_generator.generate_random_hardware_item(db, world_id, is_item_illegal)
                    elif random_type == "SOFTWARE":
                        item_id = item_generator.generate_random_software_item(db, world_id, is_item_illegal)
                    elif random_type == "CLOTHING":
                        item_id = item_generator.generate_random_clothing_item(db, world_id, is_item_illegal)
                    elif random_type == "FOOD":
                        item_id = item_generator.generate_random_food_item(db, world_id, is_item_illegal)
                elif shop_type == "BLACK_MARKET":
                    # Pour le marché noir, choisir un type d'article aléatoire, mais toujours illégal
                    item_types = ["WEAPON", "IMPLANT", "SOFTWARE"]
                    random_type = self.random.choice(item_types)
                    if random_type == "WEAPON":
                        item_id = item_generator.generate_random_weapon(db, world_id, True)
                    elif random_type == "IMPLANT":
                        item_id = item_generator.generate_random_implant(db, world_id, True)
                    elif random_type == "SOFTWARE":
                        item_id = item_generator.generate_random_software_item(db, world_id, True)
                
                if item_id:
                    # Au lieu d'essayer de récupérer les métadonnées des tables qui pourraient ne pas exister,
                    # ou des colonnes qui pourraient ne pas exister, utilisons une approche plus robuste.
                    
                    # Déterminer la rareté et le prix en fonction de l'ID de l'article
                    item_type_prefix = item_id.split('_')[0]
                    
                    # Déterminer le prix de base en fonction du type d'article 
                    # (Ces valeurs sont des estimations; les générateurs spécifiques définissent les prix réels)
                    base_prices = {
                        "weapon": 500,
                        "hardware": 400,
                        "consumable": 50,
                        "clothing": 150,
                        "software": 300,
                        "implant": 1000
                    }
                    
                    base_price = base_prices.get(item_type_prefix, 100)
                    
                    # Appliquer les modificateurs de prix
                    if is_rare:
                        base_price *= self.random.uniform(2.0, 5.0)  # Les articles rares sont 2 à 5 fois plus chers
                    
                    # Variation aléatoire du prix
                    price_variation = self.random.uniform(0.8, 1.2)  # ±20%
                    price = int(base_price * price_variation)
                    
                    # Déterminer la quantité
                    if is_rare:
                        quantity = self.random.randint(1, 3)  # Les articles rares sont en quantité limitée
                    else:
                        quantity = self.random.randint(5, 20)  # Les articles communs sont plus abondants
                    
                    # Créer des métadonnées simplifiées pour l'inventaire
                    metadata = {
                        "item_id": item_id,
                        "item_type": item_type_prefix.upper(),
                        "added_date": datetime.now().isoformat(),
                        "is_rare": is_rare,
                        "is_featured": is_featured,
                        "shop_specific_description": f"Article vendu par {shop_id}"
                    }
                    
                    # Ajouter l'article à l'inventaire du magasin
                    cursor.execute('''
                    INSERT INTO shop_inventory (
                        id, shop_id, item_type, item_id, quantity, price, price_modifier,
                        is_featured, is_limited_time, expiry_date, metadata, added_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        shop_id,
                        shop_type,
                        item_id,
                        quantity,
                        price,
                        1.0,  # price_modifier par défaut
                        1 if is_featured else 0,
                        1 if is_limited_time else 0,
                        expiry_date,
                        json.dumps(metadata),
                        datetime.now().isoformat()
                    ))
    
    def generate_world(self, name: Optional[str] = None, complexity: int = 3, 
                       author: str = "YakTaa Generator", seed: Optional[int] = None) -> str:
        """
        Génère un monde complet avec lieux, connexions, personnages, etc.
        
        Args:
            name: Nom du monde (si None, génère un nom aléatoire)
            complexity: Niveau de complexité du monde (1-5)
            author: Auteur du monde
            seed: Seed pour la génération aléatoire
            
        Returns:
            ID du monde généré
        """
        seed = self.set_seed(seed)
        logger.info(f"Génération d'un nouveau monde (seed: {seed}, complexité: {complexity})")
        
        # Obtenir la base de données
        db = get_database(self.db_path)
        
        # Générer un nom si non fourni
        if name is None:
            name = self.generate_world_name()
        
        # Insérer le monde dans la base de données
        world_id = str(uuid.uuid4())
        cursor = db.conn.cursor()
        cursor.execute('''
        INSERT INTO worlds (id, name, description, author, version, is_active, metadata, complexity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            world_id, name, f"Un monde généré automatiquement avec complexité {complexity}",
            author, "1.0", 1, json.dumps({"seed": seed}), complexity
        ))
        db.conn.commit()
        
        # Générer les différents éléments du monde
        try:
            # Définir les quantités en fonction de la complexité
            num_cities = max(1, min(8, complexity + 1))
            num_districts_per_city = max(1, min(6, complexity + 1))
            num_special_locations = max(0, min(5, complexity - 1))
            num_devices = max(10, min(100, complexity * 25))
            num_characters = max(5, min(50, complexity * 15))
            num_missions = max(3, min(20, complexity * 5))
            num_story_elements = max(1, min(10, complexity * 3))
            
            num_hardware_items = max(10, min(50, complexity * 10))
            num_consumable_items = max(10, min(50, complexity * 10))
            
            # Mettre à jour la progression
            if self.progress_callback:
                self.progress_callback(5, "Initialisation du monde...")
            
            # Générer les villes
            logger.info("Génération des villes...")
            city_ids = self.generate_cities(db, world_id, num_cities)
            if self.progress_callback:
                self.progress_callback(10, "Génération des villes...")
            
            # Générer les districts
            logger.info("Génération des districts...")
            district_ids = self.generate_districts(db, world_id, city_ids, num_districts_per_city)
            if self.progress_callback:
                self.progress_callback(15, "Génération des districts...")
            
            # Générer les lieux spéciaux
            special_location_ids = []
            if num_special_locations > 0:
                logger.info("Génération des lieux spéciaux...")
                special_location_ids = self.generate_special_locations(db, world_id, num_special_locations)
                if self.progress_callback:
                    self.progress_callback(20, "Génération des lieux spéciaux...")
            
            # Combiner tous les lieux
            all_location_ids = city_ids + district_ids + special_location_ids
            
            # Générer les connexions entre lieux
            logger.info("Génération des connexions...")
            self.generate_connections(db, world_id, all_location_ids)
            if self.progress_callback:
                self.progress_callback(25, "Génération des connexions...")
            
            # Générer les bâtiments
            logger.info("Génération des bâtiments...")
            building_ids = self.generate_buildings(db, world_id, all_location_ids)
            if self.progress_callback:
                self.progress_callback(30, "Génération des bâtiments...")
            
            # Générer les personnages
            logger.info("Génération des personnages...")
            character_ids = self.generate_characters(
                db, 
                world_id, 
                all_location_ids, 
                num_characters
            )
            if self.progress_callback:
                self.progress_callback(40, "Génération des personnages...")
            
            # Générer les appareils électroniques
            logger.info("Génération des appareils...")
            device_ids = self.generate_devices(db, world_id, all_location_ids, character_ids, num_devices)
            if self.progress_callback:
                self.progress_callback(50, "Génération des appareils...")
            
            # Générer les réseaux
            logger.info("Génération des réseaux...")
            network_ids = self.generate_networks(db, world_id, building_ids)
            if self.progress_callback:
                self.progress_callback(60, "Génération des réseaux...")
            
            # Générer les puzzles de hacking
            logger.info("Génération des puzzles de hacking...")
            puzzle_ids = self.generate_hacking_puzzles(db, world_id, device_ids, network_ids)
            if self.progress_callback:
                self.progress_callback(65, "Génération des puzzles de hacking...")
            
            # Générer les fichiers
            logger.info("Génération des fichiers...")
            file_ids = self.generate_files(db, world_id, device_ids)
            if self.progress_callback:
                self.progress_callback(70, "Génération des fichiers...")
            
            # Générer les missions
            logger.info("Génération des missions...")
            mission_ids = self.generate_missions(db, world_id, all_location_ids, character_ids, num_missions)
            if self.progress_callback:
                self.progress_callback(75, "Génération des missions...")
            
            # Générer les éléments d'histoire
            logger.info("Génération des éléments d'histoire...")
            story_element_ids = []  # Liste vide puisque nous sautons cette étape
            logger.info("Étape de génération des éléments d'histoire ignorée (table non présente dans le schéma)")
            if self.progress_callback:
                self.progress_callback(80, "Génération des éléments d'histoire...")
            
            # Générer les objets hardware (armes, armures, etc.)
            logger.info("Génération des équipements...")
            hardware_item_ids = self.generate_hardware_items(db, world_id, device_ids, building_ids, character_ids, num_hardware_items)
            if self.progress_callback:
                self.progress_callback(85, "Génération des équipements...")
            
            # Générer les objets consommables
            logger.info("Génération des consommables...")
            consumable_item_ids = self.generate_consumable_items(db, world_id, device_ids, building_ids, character_ids, num_consumable_items)
            if self.progress_callback:
                self.progress_callback(87, "Génération des consommables...")
            
            # Générer les implants
            logger.info("Génération des implants...")
            implant_ids = self.generate_implants(db, world_id, character_ids, self.implant_count)
            if self.progress_callback:
                self.progress_callback(90, "Génération des implants...")
            
            # Générer les vulnérabilités
            logger.info("Génération des vulnérabilités...")
            vulnerability_ids = self.generate_vulnerabilities(db, world_id, device_ids, network_ids, self.vulnerability_count)
            if self.progress_callback:
                self.progress_callback(92, "Génération des vulnérabilités...")
            
            # Générer les logiciels
            logger.info("Génération des logiciels...")
            software_ids = self.generate_software(db, world_id, device_ids, self.device_count // 2)
            if self.progress_callback:
                self.progress_callback(95, "Génération des logiciels...")
            
            # Générer les boutiques
            logger.info("Génération des boutiques...")
            shop_ids = self.generate_shops(db, world_id, all_location_ids, building_ids, self.shop_count)
            if self.progress_callback:
                self.progress_callback(97, "Génération des boutiques...")
            
            # Générer l'inventaire des boutiques
            logger.info("Génération de l'inventaire des boutiques...")
            self.generate_shop_inventory(db, world_id, shop_ids)
            if self.progress_callback:
                self.progress_callback(98, "Génération de l'inventaire des boutiques...")
            
            db.conn.commit()
            logger.info(f"Monde '{name}' (ID: {world_id}) généré avec succès")
            
            if self.progress_callback:
                self.progress_callback(100, "Génération terminée!")
            
            return world_id
            
        except Exception as e:
            db.conn.rollback()
            logger.error(f"Erreur lors de la génération du monde: {str(e)}")
            raise

    def generate_implants(self, db, world_id: str, character_ids: List[str], num_implants: int) -> List[str]:
        """
        Génère des implants cybernétiques pour le monde
        
        Args:
            db: Base de données
            world_id: ID du monde
            character_ids: Liste des IDs des personnages
            num_implants: Nombre d'implants à générer
            
        Returns:
            Liste des IDs des implants générés
        """
        logger.info(f"Génération de {num_implants} implants")
        
        # Importer le générateur d'implants
        try:
            import implant_items_generator
            
            # Utiliser le générateur d'implants
            device_ids = []  # Pas besoin d'appareils pour les implants
            building_ids = []  # Récupérer les bâtiments si nécessaire
            
            # Récupérer les bâtiments médicaux pour y placer les implants
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT id FROM buildings 
                WHERE building_type IN ('Hospital', 'Research Lab', 'Medical Center')
                AND world_id = ?
            """, (world_id,))
            
            medical_buildings = cursor.fetchall()
            if medical_buildings:
                building_ids = [b[0] for b in medical_buildings]
            
            # Appeler le générateur d'implants
            implant_ids = implant_items_generator.generate_implant_items(
                db, world_id, device_ids, building_ids, character_ids, num_implants, self.random
            )
            
            logger.info(f"{len(implant_ids)} implants générés avec succès")
            return implant_ids
            
        except ImportError as e:
            logger.error(f"Impossible d'importer le générateur d'implants: {e}")
            logger.warning("Utilisation de la méthode de secours pour générer des implants")
            
            # Méthode de secours (ancienne implémentation)
            cursor = db.conn.cursor()
            implant_ids = []
            
            # Types d'implants possibles
            implant_types = [
                "NEURAL", "OPTICAL", "SKELETAL", "DERMAL", "CIRCULATORY"
            ]
            
            # Fabricants d'implants
            manufacturers = [
                "Arasaka", "Militech", "Kiroshi", "Zetatech", "Raven", 
                "Biotechnica", "Dynalar", "Cybertech", "Kang Tao", "IEC"
            ]
            
            for _ in range(num_implants):
                implant_id = f"implant_{uuid.uuid4()}"
                implant_type = self.random.choice(implant_types)
                
                # Générer un nom basé sur le type
                prefix = self.random.choice(["Cyber", "Net", "Data", "Code", "Bit", "Byte", "Quantum", "Synth", "Digi", "Tech"])
                suffix = self.random.choice(["Link", "Core", "Ware", "Tech", "Soft", "Hard", "Net", "Web", "Mesh", "Grid"])
                manufacturer = self.random.choice(manufacturers)
                
                name = f"{manufacturer} {prefix}{suffix} {implant_type}"
                description = f"Un implant cybernétique de type {implant_type} fabriqué par {manufacturer}."
                
                # Déterminer la rareté
                rarity = self.random.choices(
                    ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"],
                    weights=[40, 30, 20, 8, 2],
                    k=1
                )[0]
                
                # Niveau requis basé sur la rareté
                level_map = {
                    "COMMON": self.random.randint(1, 3),
                    "UNCOMMON": self.random.randint(2, 5),
                    "RARE": self.random.randint(4, 8),
                    "EPIC": self.random.randint(7, 12),
                    "LEGENDARY": self.random.randint(10, 15)
                }
                level = level_map.get(rarity, 1)
                
                # Prix basé sur la rareté et le niveau
                price_base = {
                    "COMMON": 100,
                    "UNCOMMON": 500,
                    "RARE": 2000,
                    "EPIC": 8000,
                    "LEGENDARY": 25000
                }
                price_multiplier = 1 + (level * 0.2)
                price = int(price_base.get(rarity, 100) * price_multiplier)
                
                # Vérifier si la table implant_items existe
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='implant_items'
                """)
                
                if not cursor.fetchone():
                    # Créer la table implant_items si elle n'existe pas
                    cursor.execute("""
                        CREATE TABLE implant_items (
                            id TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            implant_type TEXT NOT NULL,
                            level INTEGER DEFAULT 1,
                            price INTEGER DEFAULT 100,
                            stats_bonus TEXT,  -- JSON
                            humanity_cost INTEGER DEFAULT 5,
                            installation_difficulty INTEGER DEFAULT 1,
                            special_effects TEXT,  -- JSON
                            combat_bonus TEXT,  -- JSON
                            icon TEXT DEFAULT 'implant',
                            is_illegal INTEGER DEFAULT 0,
                            rarity TEXT DEFAULT 'COMMON',
                            world_id TEXT,
                            location_type TEXT,
                            location_id TEXT,
                            FOREIGN KEY (world_id) REFERENCES worlds (id)
                        )
                    """)
                    db.conn.commit()
                    logger.info("Table implant_items créée")
                
                # Insérer l'implant dans la base de données
                cursor.execute("""
                    INSERT INTO implant_items (
                        id, name, description, implant_type, level, price, 
                        stats_bonus, humanity_cost, installation_difficulty, 
                        special_effects, combat_bonus, icon, is_illegal, 
                        rarity, world_id, location_type, location_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    implant_id, name, description, implant_type, level, price,
                    json.dumps({}), 5, 1,
                    json.dumps([]), json.dumps({}), f"implant_{implant_type.lower()}", 0,
                    rarity, world_id, "loot", "world"
                ))
                
                implant_ids.append(implant_id)
            
            db.conn.commit()
            logger.info(f"{len(implant_ids)} implants générés avec la méthode de secours")
            return implant_ids

    def generate_vulnerabilities(self, db, world_id: str, device_ids: List[str], network_ids: List[str], num_vulnerabilities: int) -> List[str]:
        """
        Génère des vulnérabilités pour les appareils et réseaux
        
        Args:
            db: Base de données
            world_id: ID du monde
            device_ids: Liste des IDs des appareils
            network_ids: Liste des IDs des réseaux
            num_vulnerabilities: Nombre de vulnérabilités à générer
            
        Returns:
            Liste des IDs des vulnérabilités générées
        """
        logger.info(f"Génération de {num_vulnerabilities} vulnérabilités")
        cursor = db.conn.cursor()
        vulnerability_ids = []
        
        # Types de vulnérabilités
        vulnerability_types = [
            "Buffer Overflow", "SQL Injection", "Cross-Site Scripting", 
            "Authentication Bypass", "Command Execution", "Privilege Escalation",
            "Memory Corruption", "Race Condition", "Default Credentials",
            "Insecure Encryption", "Firmware Downgrade", "Side-Channel Attack"
        ]
        
        # Noms de code pour les vulnérabilités
        code_names = [
            "BlueScreen", "RedFlag", "DarkHole", "SilentBreak", "GhostAccess",
            "PhantomGate", "ShadowKey", "IceBreak", "FireWall", "StormFront",
            "NightCrawler", "DayWalker", "QuickSilver", "DeadZone", "LiveWire"
        ]
        
        for _ in range(num_vulnerabilities):
            vulnerability_id = str(uuid.uuid4())
            
            # Sélectionner un type de vulnérabilité
            vuln_type = self.random.choice(vulnerability_types)
            code_name = self.random.choice(code_names)
            
            # Générer la difficulté et l'impact
            difficulty = self.random.randint(1, 10)
            impact = self.random.randint(1, 10)
            
            # La rareté est inversement proportionnelle à la difficulté
            rarity_map = {
                (1, 3): "commun",
                (4, 6): "peu_commun",
                (7, 8): "rare",
                (9, 10): "très_rare"
            }
            
            rarity = None
            for range_tuple, rarity_value in rarity_map.items():
                if difficulty >= range_tuple[0] and difficulty <= range_tuple[1]:
                    rarity = rarity_value
                    break
            
            if not rarity:
                rarity = "commun"
            
            # Décrire la vulnérabilité
            descriptions = {
                "Buffer Overflow": "Permet d'injecter du code en dépassant les limites d'un tampon mémoire.",
                "SQL Injection": "Exécute des commandes SQL non autorisées en manipulant les entrées.",
                "Cross-Site Scripting": "Injecte du code malveillant qui s'exécute dans le navigateur de la victime.",
                "Authentication Bypass": "Contourne les mécanismes d'authentification pour obtenir un accès non autorisé.",
                "Command Execution": "Exécute des commandes système arbitraires sur l'appareil cible.",
                "Privilege Escalation": "Élève les privilèges pour obtenir un accès administrateur.",
                "Memory Corruption": "Manipule la mémoire pour obtenir un comportement inattendu du système.",
                "Race Condition": "Exploite le timing entre les opérations pour manipuler le comportement du système.",
                "Default Credentials": "Utilise des identifiants par défaut non modifiés pour accéder au système.",
                "Insecure Encryption": "Exploite des faiblesses dans l'implémentation du chiffrement.",
                "Firmware Downgrade": "Rétrograde le firmware pour exploiter d'anciennes vulnérabilités corrigées.",
                "Side-Channel Attack": "Exploite les fuites d'informations via des canaux secondaires comme la consommation d'énergie."
            }
            
            description = descriptions.get(vuln_type, "Une vulnérabilité de sécurité exploitable.")
            
            # Déterminer si la vulnérabilité est liée à un appareil ou à un réseau
            target_type = self.random.choice(["device", "network"])
            target_id = None
            
            if target_type == "device" and device_ids:
                target_id = self.random.choice(device_ids)
            elif target_type == "network" and network_ids:
                target_id = self.random.choice(network_ids)
            
            # Générer les exploits possibles
            exploits = []
            exploit_count = self.random.randint(1, 3)
            
            exploit_types = [
                "volDonnées", "contrôleAccès", "déniService", "élévationPrivilèges",
                "executionCode", "contournementAuthentification", "modificationDonnées"
            ]
            
            for _ in range(exploit_count):
                exploit_type = self.random.choice(exploit_types)
                exploit_difficulty = self.random.randint(1, 10)
                exploit_impact = self.random.randint(1, 10)
                
                exploits.append({
                    "type": exploit_type,
                    "difficulté": exploit_difficulty,
                    "impact": exploit_impact
                })
            
            # Insérer la vulnérabilité dans la base de données
            cursor.execute('''
            INSERT INTO vulnerabilities (
                id, world_id, name, description, vuln_type, difficulty, target_id,
                target_type, discovery_date, is_public, is_patched, exploits, code_name,
                impact, rarity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vulnerability_id, world_id, f"Vulnérabilité {vuln_type}", description,
                vuln_type, difficulty, target_id, target_type,
                datetime.now().isoformat(), self.random.choice([0, 1]),
                self.random.choice([0, 1]), json.dumps(exploits), code_name,
                impact, rarity
            ))
            
            vulnerability_ids.append(vulnerability_id)
        
        db.conn.commit()
        return vulnerability_ids

    def generate_software(self, db, world_id: str, device_ids: List[str], num_software: int) -> List[str]:
        """
        Génère des logiciels pour les appareils
        
        Args:
            db: Base de données
            world_id: ID du monde
            device_ids: Liste des IDs des appareils
            num_software: Nombre de logiciels à générer
            
        Returns:
            Liste des IDs des logiciels générés
        """
        logger.info(f"Génération de {num_software} logiciels")
        cursor = db.conn.cursor()
        software_ids = []
        
        # Types de logiciels
        software_types = [
            "Système d'exploitation", "Antivirus", "Firewall", "Cryptage",
            "Décodeur", "Base de données", "Suite bureautique", "Jeu",
            "Outil de développement", "Utilitaire système", "Navigateur",
            "Analyseur réseau", "Scanner de vulnérabilités", "Outil de hacking"
        ]
        
        # Sociétés de développement
        developers = [
            "Netsoft", "Microtech", "ByteSec", "CodeCorp", "Tenkei",
            "Futureworks", "OpenSense", "Darkcode", "Cryotech", "Bluelight"
        ]
        
        for _ in range(num_software):
            software_id = str(uuid.uuid4())
            
            # Sélectionner un type de logiciel
            software_type = self.random.choice(software_types)
            
            # Générer un nom basé sur le type
            prefixes = ["Cyber", "Net", "Data", "Code", "Bit", "Byte", "Quantum", "Synth", "Digi", "Tech"]
            suffixes = ["Guardian", "Shield", "Master", "Pro", "Suite", "Elite", "Prime", "Ultimate", "Core", "Advanced"]
            
            name = f"{self.random.choice(prefixes)}{software_type.split()[0][:4]} {self.random.choice(suffixes)}"
            
            # Déterminer les caractéristiques du logiciel
            version = f"{self.random.randint(1, 9)}.{self.random.randint(0, 9)}.{self.random.randint(0, 9)}"
            developer = self.random.choice(developers)
            license_type = self.random.choice(["gratuit", "essai", "open_source", "commercial", "cracked"])
            is_malware = 1 if self.random.random() < 0.15 else 0  # 15% de chance d'être un malware
            
            # Calculer le niveau et le prix
            level = self.random.randint(1, 10)
            price = 0 if license_type in ["gratuit", "open_source", "cracked"] else self.random.randint(50, 5000)
            
            # Générer des capacités pour le logiciel
            capabilities = []
            capability_count = self.random.randint(1, 5)
            
            capability_types = [
                "protection", "analyse", "optimisation", "déchiffrement",
                "anonymisation", "détection", "virtualisation", "automatisation"
            ]
            
            for _ in range(capability_count):
                capability_type = self.random.choice(capability_types)
                capability_level = self.random.randint(1, 10)
                
                capabilities.append({
                    "type": capability_type,
                    "niveau": capability_level
                })
            
            # Description du logiciel
            description = f"{name} v{version} est un logiciel de type {software_type.lower()} développé par {developer}. "
            
            if license_type == "gratuit":
                description += "Il est disponible gratuitement. "
            elif license_type == "essai":
                description += "Une version d'essai limitée est disponible. "
            elif license_type == "open_source":
                description += "Il est open-source et librement modifiable. "
            elif license_type == "commercial":
                description += f"C'est un logiciel commercial au prix de {price} crédits. "
            elif license_type == "cracked":
                description += "C'est une version piratée d'un logiciel commercial. "
            
            if is_malware:
                description += "ATTENTION: Ce logiciel contient du code malveillant! "
            
            # Générer des métadonnées
            metadata = {
                "capabilities": capabilities,
                "requirements": {
                    "cpu": self.random.randint(1, 8),
                    "ram": self.random.randint(1, 16),
                    "storage": self.random.randint(1, 100)
                },
                "compatibility": self.random.sample(["Windows", "Linux", "MacOS", "Android", "iOS"], self.random.randint(1, 5)),
                "install_time": self.random.randint(10, 300),
                "has_updates": self.random.choice([True, False])
            }
            
            # Insérer le logiciel dans la base de données
            cursor.execute('''
            INSERT INTO software (
                id, world_id, name, description, software_type, version, developer,
                license_type, level, price, is_malware, metadata, release_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                software_id, world_id, name, description, software_type,
                version, developer, license_type, level, price, is_malware,
                json.dumps(metadata), datetime.now().isoformat()
            ))
            
            # Installer le logiciel sur certains appareils
            if device_ids and self.random.random() < 0.4:  # 40% de chance
                device_id = self.random.choice(device_ids)
                cursor.execute('''
                INSERT INTO device_software (
                    id, device_id, software_id, installation_date, is_active, is_running
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()), device_id, software_id,
                    datetime.now().isoformat(), 1, self.random.choice([0, 1])
                ))
            
            software_ids.append(software_id)
        
        db.conn.commit()
        return software_ids