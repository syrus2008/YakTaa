"""
Module pour la génération des articles de boutique
Permet de peupler les boutiques avec des articles standardisés
"""

import uuid
import random
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# Import du standardiseur de métadonnées
from metadata_standardizer import MetadataStandardizer, get_standardized_metadata

# Configuration du logging
logger = logging.getLogger("YakTaa.WorldEditor.Generator.ShopItems")

class ShopItemGenerator:
    """
    Classe pour la génération des articles de boutique
    """
    def __init__(self, db):
        """
        Initialise le générateur d'articles de boutique
        
        Args:
            db: Base de données
        """
        self.db = db
        
    def generate_shop_inventory(self, world_id: str, shop_ids: List[str], 
                               item_types: List[str], random_seed: Optional[int] = None) -> None:
        """
        Génère l'inventaire des boutiques avec des articles standardisés
        
        Args:
            world_id: ID du monde
            shop_ids: Liste des IDs des boutiques
            item_types: Types d'articles à générer ("weapons", "armors", "consumables", "implants", "hardware", "software")
            random_seed: Graine pour la génération aléatoire
        """
        logger.info(f"Génération de l'inventaire pour {len(shop_ids)} boutiques")
        
        if not shop_ids:
            logger.warning("Aucune boutique trouvée pour générer l'inventaire")
            return
        
        # Initialiser le générateur aléatoire
        random_gen = random.Random(random_seed)
        
        cursor = self.db.conn.cursor()
        
        # Vérifier si la table shop_inventory existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='shop_inventory'
        """)
        
        if not cursor.fetchone():
            # Créer la table shop_inventory si elle n'existe pas
            cursor.execute("""
                CREATE TABLE shop_inventory (
                    id TEXT PRIMARY KEY,
                    shop_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    price_modifier REAL DEFAULT 1.0,
                    is_featured INTEGER DEFAULT 0,
                    is_limited_time INTEGER DEFAULT 0,
                    expiry_date TEXT,
                    added_at TEXT,
                    metadata TEXT,
                    price INTEGER DEFAULT 0,
                    FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE CASCADE
                )
            """)
            self.db.conn.commit()
            logger.info("Table shop_inventory créée")
        
        # Pour chaque boutique
        for shop_id in shop_ids:
            # Récupérer les informations de la boutique
            cursor.execute("""
                SELECT type, name FROM shops WHERE id = ?
            """, (shop_id,))
            
            shop_data = cursor.fetchone()
            if not shop_data:
                logger.warning(f"Boutique {shop_id} non trouvée, ignorée.")
                continue
                
            shop_type, shop_name = shop_data
            
            # Déterminer le nombre d'articles
            base_num_items = random_gen.randint(5, 20)
            
            # Types d'articles adaptés à cette boutique
            shop_item_types = self._get_shop_item_types(shop_type, item_types)
            
            # Pour chaque type d'article
            for item_type in shop_item_types:
                # Nombre d'articles de ce type
                num_items = random_gen.randint(1, max(2, base_num_items // len(shop_item_types)))
                
                # Table correspondant au type d'article
                table_name = self._get_table_for_type(item_type)
                if not table_name:
                    logger.warning(f"Type d'article {item_type} non reconnu, ignoré.")
                    continue
                
                # Vérifier si la table existe
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{table_name}'
                """)
                
                if not cursor.fetchone():
                    logger.warning(f"Table {table_name} non trouvée, ignorée.")
                    continue
                
                # Récupérer les articles disponibles de ce type
                cursor.execute(f"""
                    SELECT id, name, price, rarity, metadata FROM {table_name}
                    WHERE world_id = ? 
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (world_id, num_items * 3))  # Plus d'articles que nécessaire pour avoir du choix
                
                available_items = cursor.fetchall()
                
                if not available_items:
                    logger.warning(f"Aucun article de type {item_type} trouvé pour la boutique {shop_id}.")
                    continue
                
                # Sélectionner des articles aléatoirement
                selected_items = random_gen.sample(available_items, min(num_items, len(available_items)))
                
                # Ajouter les articles à l'inventaire de la boutique
                for item_id, item_name, item_price, item_rarity, item_metadata in selected_items:
                    # Extraire les métadonnées si c'est une chaîne JSON
                    if isinstance(item_metadata, str):
                        try:
                            item_metadata = json.loads(item_metadata)
                        except json.JSONDecodeError:
                            item_metadata = {}
                    
                    # Paramètres de l'article dans la boutique
                    quantity = random_gen.randint(1, 10)
                    price_modifier = self._determine_price_modifier(shop_type, item_type, item_rarity, random_gen)
                    is_featured = 1 if random_gen.random() < 0.1 else 0
                    is_limited_time = 1 if random_gen.random() < 0.2 else 0
                    
                    # Date d'ajout et d'expiration
                    added_at = datetime.now().isoformat()
                    expiry_date = None
                    if is_limited_time:
                        days_until_expiry = random_gen.randint(1, 30)
                        expiry_date = (datetime.now() + timedelta(days=days_until_expiry)).isoformat()
                    
                    # Calculer le prix final
                    final_price = max(1, int(item_price * price_modifier))
                    
                    # ID unique pour l'entrée d'inventaire
                    inventory_id = f"shop_item_{uuid.uuid4()}"
                    
                    # Standardiser les métadonnées
                    metadata = MetadataStandardizer.standardize_shop_item_metadata(
                        item_type=item_type,
                        base_price=item_price,
                        final_price=final_price,
                        quantity=quantity,
                        price_modifier=price_modifier,
                        is_featured=bool(is_featured),
                        is_limited_time=bool(is_limited_time),
                        expiry_date=expiry_date,
                        added_at=added_at,
                        item_metadata=item_metadata,
                        shop_type=shop_type
                    )
                    
                    # Insérer dans la base de données
                    cursor.execute("""
                        INSERT INTO shop_inventory (
                            id, shop_id, item_type, item_id, quantity, price_modifier,
                            is_featured, is_limited_time, expiry_date, added_at, 
                            metadata, price
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        inventory_id, shop_id, item_type, item_id, quantity, price_modifier,
                        is_featured, is_limited_time, expiry_date, added_at,
                        json.dumps(metadata), final_price
                    ))
            
            # Valider les changements
            self.db.conn.commit()
            logger.info(f"Inventaire généré pour la boutique {shop_name} (ID: {shop_id})")
        
        logger.info(f"Génération de l'inventaire terminée pour {len(shop_ids)} boutiques")
                
    def generate_random_food_item(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère un article alimentaire aléatoire pour une boutique
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_illegal: Si l'article est illégal
            
        Returns:
            ID de l'article généré
        """
        logger.info("Génération d'un article alimentaire aléatoire")
        
        cursor = db.conn.cursor()
        
        # Vérifier si la table consumable_items existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='consumable_items'
        """)
        
        if not cursor.fetchone():
            # Créer la table consumable_items si elle n'existe pas
            cursor.execute("""
                CREATE TABLE consumable_items (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    consumable_type TEXT NOT NULL,
                    price INTEGER DEFAULT 0,
                    rarity TEXT DEFAULT 'COMMON',
                    uses INTEGER DEFAULT 1,
                    duration INTEGER DEFAULT 15,
                    is_legal INTEGER DEFAULT 1,
                    effects TEXT,
                    metadata TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                )
            """)
            db.conn.commit()
            logger.info("Table consumable_items créée")
        
        # Générer les détails de l'article alimentaire
        item_id = f"food_{uuid.uuid4()}"
        
        # Générer un type alimentaire aléatoire
        food_types = ["MEAL", "SNACK", "DRINK", "SUPPLEMENT"]
        food_type = random.choice(food_types)
        
        # Générer un nom d'article selon le type
        food_names = {
            "MEAL": ["Soupe instantanée", "Ration de survie", "Burrito synthétique", "NutriPack", "Dîner préparé",
                    "Bol protéiné", "Pizza comprimée", "Curry en poudre", "Ramen énergisant"],
            "SNACK": ["Chips protéinées", "Barre énergétique", "Crackers de soja", "Friandise synthétique", 
                    "Cubes de nutriments", "Bonbons fortifiés", "Jerky cultive", "Snack d'algues"],
            "DRINK": ["BoostJuice", "Hydratant électrolytique", "Smoothie synthétique", "Café en poudre", 
                    "Thé énergétique", "Soda nootropique", "Eau purifiée", "Boisson protéinée"],
            "SUPPLEMENT": ["Vitamines", "Minéraux", "Fortifiant immunitaire", "Boost d'énergie", 
                        "Concentré nutritionnel", "Poudre protéinée", "Stimulant métabolique"]
        }
        
        item_name = random.choice(food_names.get(food_type, food_names["SNACK"]))
        
        # Générer une description
        descriptions = {
            "MEAL": [
                "Un repas complet avec tous les nutriments essentiels.",
                "Fournit un apport calorique et nutritionnel complet.",
                "Une solution de repas rapide et nutritive."
            ],
            "SNACK": [
                "Une collation énergétique pour tenir entre les repas.",
                "Petit mais nourrissant, idéal pour les déplacements.",
                "Satisfait les petites faims avec un boost d'énergie."
            ],
            "DRINK": [
                "Hydrate et fournit des nutriments essentiels.",
                "Une boisson revitalisante avec électrolytes et vitamines.",
                "Étanche la soif tout en boostant l'énergie."
            ],
            "SUPPLEMENT": [
                "Complément nutritionnel pour combler les carences.",
                "Concentré de vitamines et minéraux essentiels.",
                "Formule avancée pour soutenir les performances physiques."
            ]
        }
        
        item_description = random.choice(descriptions.get(food_type, descriptions["SNACK"]))
        
        # Générer le prix de base selon la rareté
        rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
        rarity_weights = [70, 20, 7, 2, 1]
        rarity = random.choices(rarities, weights=rarity_weights)[0]
        
        # Prix de base selon la rareté
        base_prices = {
            "COMMON": random.randint(5, 20),
            "UNCOMMON": random.randint(15, 40),
            "RARE": random.randint(30, 80),
            "EPIC": random.randint(70, 150),
            "LEGENDARY": random.randint(120, 300),
        }
        price = base_prices.get(rarity, random.randint(10, 50))
        
        # Générer les caractéristiques alimentaires
        calories = random.randint(50, 500)
        nutrition_value = random.randint(1, 10)
        taste = random.choice(["SWEET", "SALTY", "SOUR", "BITTER", "UMAMI", "NEUTRAL"])
        shelf_life = random.randint(7, 365)  # en jours
        weight = random.randint(10, 500) / 100.0  # en kg
        
        # Effets possibles
        possible_effects = [
            {"type": "HEALTH", "value": random.randint(1, 10)},
            {"type": "ENERGY", "value": random.randint(1, 10)},
            {"type": "STAMINA", "value": random.randint(1, 10)},
            {"type": "FOCUS", "value": random.randint(1, 5)},
            {"type": "STRENGTH", "value": random.randint(1, 3)},
            {"type": "INTELLIGENCE", "value": random.randint(1, 3)}
        ]
        
        # Effets secondaires possibles
        possible_side_effects = [
            "NAUSEA", "DROWSINESS", "HEADACHE", "DIZZINESS", "JITTERS",
            "DEHYDRATION", "HUNGER", "FATIGUE", "WEAKNESS"
        ]
        
        # Sélectionner des effets aléatoires
        num_effects = random.randint(1, 3)
        effects = random.sample(possible_effects, k=num_effects)
        
        # Sélectionner des effets secondaires aléatoires (rares)
        side_effects = []
        if random.random() < 0.3:  # 30% de chance d'avoir des effets secondaires
            num_side_effects = random.randint(1, 2)
            side_effects = random.sample(possible_side_effects, k=num_side_effects)
        
        # Fabricants possibles
        manufacturers = [
            "NutriCorp", "FoodTech", "VitaBlend", "SynthMeal", "EcoNutrients",
            "UrbanEats", "CoreNutrition", "FutureFoods", "BioHarvest", "NeoNutrition"
        ]
        manufacturer = random.choice(manufacturers)
        
        # Générer les métadonnées standardisées
        metadata = MetadataStandardizer.standardize_food_metadata(
            food_type=food_type,
            calories=calories,
            nutrition_value=nutrition_value,
            taste=taste,
            shelf_life=shelf_life,
            effects=effects,
            side_effects=side_effects,
            manufacturer=manufacturer,
            weight=weight
        )
        
        # Qualité de l'article
        qualities = ["Poor", "Average", "Good", "Excellent", "Perfect"]
        quality_weights = [10, 40, 30, 15, 5]
        quality = random.choices(qualities, weights=quality_weights)[0]
        
        # Légalité (1 = légal, 0 = illégal)
        legality = 0 if is_illegal else 1
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO consumable_items (
                id, world_id, name, description, consumable_type, price, rarity, uses, duration, is_legal, effects, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, world_id, item_name, item_description, "FOOD",
            price, rarity, 1, 15, legality, json.dumps(effects), json.dumps(metadata)
        ))
        
        db.conn.commit()
        logger.info(f"Article alimentaire généré: {item_name} (ID: {item_id})")
        
        return item_id
            
    def generate_random_hardware_item(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère un article de matériel informatique aléatoire pour une boutique
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_illegal: Si l'article est illégal
            
        Returns:
            ID de l'article généré
        """
        logger.info("Génération d'un article matériel aléatoire")
        
        cursor = db.conn.cursor()
        
        # Vérifier si la table hardware_items existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='hardware_items'
        """)
        
        if not cursor.fetchone():
            # Créer la table hardware_items si elle n'existe pas
            cursor.execute("""
                CREATE TABLE hardware_items (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    hardware_type TEXT NOT NULL,
                    quality TEXT DEFAULT 'Normal',
                    rarity TEXT DEFAULT 'COMMON',
                    level INTEGER DEFAULT 1,
                    price INTEGER DEFAULT 0,
                    is_legal INTEGER DEFAULT 1,
                    stats TEXT,
                    metadata TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                )
            """)
            db.conn.commit()
            logger.info("Table hardware_items créée")
        
        # Générer les détails de l'article matériel
        item_id = f"hardware_{uuid.uuid4()}"
        
        # Générer un type matériel aléatoire
        hardware_types = ["CPU", "RAM", "STORAGE", "GPU", "NETWORK", "PERIPHERAL", "TOOL"]
        hardware_type = random.choice(hardware_types)
        
        # Générer un nom d'article selon le type
        hardware_names = {
            "CPU": ["Quantum Core", "NeuroPro", "SyntheCore", "BitMaster", "ProcessorX", 
                   "CyberCPU", "QuantumChip", "NanoProcessor", "SiliconBrain"],
            "RAM": ["MemoryX", "QuickRAM", "NeuraMem", "HyperStick", "QuantumRAM", 
                   "FlashMem", "BioMemory", "CyberRAM", "QuantumStick"],
            "STORAGE": ["DataCube", "QuantumDrive", "NeuraDisk", "StorageX", "HyperDrive", 
                       "FlashDrive", "BioStorage", "CyberDrive", "QuantumVault"],
            "GPU": ["VisualCore", "RenderX", "GraphicsMaster", "PixelEngine", "QuantumGPU", 
                   "HoloChip", "NeuraCast", "VisionPro", "RealityRenderer"],
            "NETWORK": ["NetLink", "WaveConnect", "DataStream", "CyberNet", "QuantumRouter", 
                       "MeshHub", "SignalBoost", "NetMaster", "CommCore"],
            "PERIPHERAL": ["CyberGlove", "NeuraMouse", "VoiceBox", "RetinaScan", "TouchPad", 
                          "GestureTrack", "BioConnector", "SenseHub", "ControlPad"],
            "TOOL": ["HackTool", "CrackerPro", "BypassKit", "FirewallDrill", "PortScanner", 
                    "CodeBreaker", "SecurityProbe", "CipherTool", "NetAnalyzer"]
        }
        
        item_name = random.choice(hardware_names.get(hardware_type, hardware_names["PERIPHERAL"]))
        
        # Générer une description
        descriptions = {
            "CPU": [
                "Processeur avancé offrant des performances de calcul exceptionnelles.",
                "Cœur de traitement neuromorphique avec capacités d'IA intégrées.",
                "Unité centrale quantique avec architecture parallèle massive."
            ],
            "RAM": [
                "Mémoire ultra-rapide avec temps de latence minimal.",
                "Stockage temporaire de données avec connexion neurale.",
                "Module mémoire avec circuits quantiques intégrés."
            ],
            "STORAGE": [
                "Stockage permanent avec chiffrement intégré.",
                "Disque quantique avec capacité de compression avancée.",
                "Unité de stockage moléculaire à haute densité."
            ],
            "GPU": [
                "Processeur graphique capable de rendu holographique en temps réel.",
                "Unité de calcul parallèle spécialisée dans la visualisation.",
                "Moteur de rendu pour réalité virtuelle et augmentée."
            ],
            "NETWORK": [
                "Interface réseau avec capacités de cryptage avancées.",
                "Routeur quantique capable de communications sécurisées.",
                "Hub de connexion avec analyse de trafic intégrée."
            ],
            "PERIPHERAL": [
                "Périphérique d'interface humain-machine avec retour haptique.",
                "Dispositif d'entrée avancé avec reconnaissance gestuelle.",
                "Interface multimodale pour contrôle système intuitif."
            ],
            "TOOL": [
                "Outil spécialisé pour analyse et modification de systèmes.",
                "Kit de diagnostic pour réseaux et systèmes informatiques.",
                "Dispositif d'accès et d'analyse pour sécurité informatique."
            ]
        }
        
        item_description = random.choice(descriptions.get(hardware_type, descriptions["PERIPHERAL"]))
        
        # Générer le prix de base selon la rareté
        rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
        rarity_weights = [60, 25, 10, 4, 1]
        rarity = random.choices(rarities, weights=rarity_weights)[0]
        
        # Prix de base selon la rareté et le type
        base_prices = {
            "COMMON": {
                "CPU": random.randint(50, 200),
                "RAM": random.randint(30, 150),
                "STORAGE": random.randint(40, 180),
                "GPU": random.randint(80, 250),
                "NETWORK": random.randint(40, 160),
                "PERIPHERAL": random.randint(20, 100),
                "TOOL": random.randint(30, 120)
            },
            "UNCOMMON": {
                "CPU": random.randint(180, 400),
                "RAM": random.randint(120, 300),
                "STORAGE": random.randint(150, 350),
                "GPU": random.randint(200, 500),
                "NETWORK": random.randint(140, 320),
                "PERIPHERAL": random.randint(80, 200),
                "TOOL": random.randint(100, 250)
            },
            "RARE": {
                "CPU": random.randint(350, 800),
                "RAM": random.randint(250, 600),
                "STORAGE": random.randint(300, 700),
                "GPU": random.randint(450, 1000),
                "NETWORK": random.randint(280, 650),
                "PERIPHERAL": random.randint(180, 400),
                "TOOL": random.randint(220, 500)
            },
            "EPIC": {
                "CPU": random.randint(750, 1500),
                "RAM": random.randint(550, 1200),
                "STORAGE": random.randint(650, 1400),
                "GPU": random.randint(900, 2000),
                "NETWORK": random.randint(600, 1300),
                "PERIPHERAL": random.randint(350, 800),
                "TOOL": random.randint(450, 1000)
            },
            "LEGENDARY": {
                "CPU": random.randint(1400, 3000),
                "RAM": random.randint(1100, 2500),
                "STORAGE": random.randint(1300, 2800),
                "GPU": random.randint(1800, 4000),
                "NETWORK": random.randint(1200, 2600),
                "PERIPHERAL": random.randint(700, 1600),
                "TOOL": random.randint(900, 2000)
            }
        }
        
        price = base_prices.get(rarity, {}).get(hardware_type, random.randint(100, 500))
        
        # Générer des statistiques basées sur la rareté
        stats_multiplier = {
            "COMMON": 1,
            "UNCOMMON": 1.5,
            "RARE": 2,
            "EPIC": 3,
            "LEGENDARY": 5
        }.get(rarity, 1)
        
        # Statistiques de base selon le type
        base_stats = {
            "CPU": {
                "processing_power": int(random.randint(5, 15) * stats_multiplier),
                "threads": int(random.randint(2, 8) * stats_multiplier),
                "frequency": round(random.uniform(1.5, 4.5) * stats_multiplier, 1),
                "thermal_efficiency": random.randint(3, 10)
            },
            "RAM": {
                "capacity": int(random.randint(4, 32) * stats_multiplier),
                "speed": int(random.randint(1600, 3600) * stats_multiplier),
                "latency": round(random.uniform(1.0, 5.0) / stats_multiplier, 1),
                "power_consumption": random.randint(1, 8)
            },
            "STORAGE": {
                "capacity": int(random.randint(100, 1000) * stats_multiplier),
                "read_speed": int(random.randint(500, 3000) * stats_multiplier),
                "write_speed": int(random.randint(400, 2500) * stats_multiplier),
                "encryption_level": random.randint(1, 10)
            },
            "GPU": {
                "cores": int(random.randint(500, 2000) * stats_multiplier),
                "memory": int(random.randint(2, 16) * stats_multiplier),
                "render_power": int(random.randint(5, 20) * stats_multiplier),
                "power_consumption": random.randint(5, 15)
            },
            "NETWORK": {
                "bandwidth": int(random.randint(100, 1000) * stats_multiplier),
                "encryption": random.randint(1, 10),
                "range": int(random.randint(10, 100) * stats_multiplier),
                "power_consumption": random.randint(1, 5)
            },
            "PERIPHERAL": {
                "response_time": round(random.uniform(0.5, 5.0) / stats_multiplier, 1),
                "precision": random.randint(1, 10),
                "comfort": random.randint(1, 10),
                "power_consumption": random.randint(1, 3)
            },
            "TOOL": {
                "effectiveness": random.randint(1, 10),
                "versatility": random.randint(1, 10),
                "stealth": random.randint(1, 10),
                "power_consumption": random.randint(1, 8)
            }
        }
        
        stats = base_stats.get(hardware_type, {"power": random.randint(1, 10), "utility": random.randint(1, 10)})
        
        # Paramètres de compatibilité
        compatibility = ["STANDARD", "PROPRIETARY", "MILITARY", "CUSTOM", "CORPORATE", "LEGACY"]
        compat_type = random.choice(compatibility)
        
        # Configuration requise
        system_requirements = {
            "power_supply": random.randint(1, 10),
            "space_required": random.randint(1, 5),
            "cooling_needed": random.randint(1, 5)
        }
        
        # Fabricants possibles
        manufacturers = [
            "NeuraTech", "QuantumSys", "CyberCore", "SiliconDreams", "DataForge",
            "NexusWave", "SyntheticaInc", "CoreTech", "FutureHardware", "BitStream"
        ]
        manufacturer = random.choice(manufacturers)
        
        # Générer les métadonnées standardisées
        metadata = MetadataStandardizer.standardize_hardware_metadata(
            hardware_type=hardware_type,
            stats=stats,
            power_consumption=stats.get("power_consumption", random.randint(1, 10)),
            compatibility=compat_type,
            manufacturer=manufacturer,
            system_requirements=system_requirements,
            version=f"{random.randint(1, 9)}.{random.randint(0, 9)}"
        )
        
        # Qualité de l'article
        qualities = ["Poor", "Average", "Good", "Excellent", "Perfect"]
        quality_weights = [10, 40, 30, 15, 5]
        quality = random.choices(qualities, weights=quality_weights)[0]
        
        # Légalité (1 = légal, 0 = illégal)
        legality = 0 if is_illegal else 1
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO hardware_items (
                id, world_id, name, description, hardware_type, quality, rarity, level, price, is_legal, stats, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, world_id, item_name, item_description, hardware_type,
            quality, rarity, 1, price, legality, json.dumps(stats), json.dumps(metadata)
        ))
        
        db.conn.commit()
        logger.info(f"Article matériel généré: {item_name} (ID: {item_id})")
        
        return item_id
            
    def generate_random_implant(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère un implant cybernétique aléatoire pour une boutique
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_illegal: Si l'article est illégal
            
        Returns:
            ID de l'article généré
        """
        logger.info("Génération d'un implant aléatoire")
        
        cursor = db.conn.cursor()
        
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
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    implant_type TEXT NOT NULL,
                    body_location TEXT,
                    surgery_difficulty INTEGER,
                    side_effects TEXT,
                    compatibility TEXT,
                    rarity TEXT DEFAULT 'COMMON',
                    price INTEGER DEFAULT 0,
                    is_legal INTEGER DEFAULT 1,
                    metadata TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                )
            """)
            db.conn.commit()
            logger.info("Table implant_items créée")
        
        # Générer les détails de l'implant
        item_id = f"implant_{uuid.uuid4()}"
        
        # Générer un type d'implant aléatoire
        implant_types = ["NEURAL", "OPTICAL", "SKELETAL", "DERMAL", "CIRCULATORY", "RESPIRATORY", "IMMUNE", "MUSCULAR"]
        implant_type = random.choice(implant_types)
        
        # Générer un nom d'article selon le type
        implant_names = {
            "NEURAL": ["NeuroLink", "SynapseBoost", "CortexEnhancer", "BrainWave", "NeuroMatrix", 
                      "MindTech", "CerebralCore", "NeuroPulse", "SynapticNode"],
            "OPTICAL": ["EyeTech", "VisualCore", "OpticPro", "RetinaScan", "NightVision", 
                       "ZoomLens", "ChromaSight", "EagleEye", "HoloVision"],
            "SKELETAL": ["BoneWeave", "EndoFrame", "SkeleCore", "OsseousReinforcement", "JointTech", 
                        "SpinalLink", "FrameBoost", "BoneMatrix", "TitanSkeleton"],
            "DERMAL": ["SkinShield", "DermaPlate", "TactileMesh", "ArmorSkin", "SensoryDerm", 
                      "ThermoLayer", "ChromaSkin", "ReflexDerm", "SynthSkin"],
            "CIRCULATORY": ["BloodBoost", "CardioCore", "VeinTech", "PulseWave", "OxygenMax", 
                           "HemoFilter", "CircuitVein", "FlowControl", "HeartTech"],
            "RESPIRATORY": ["LungTech", "OxygenCore", "BreatheEasy", "FilterLung", "AirMatrix", 
                           "RespiControl", "PureBreathe", "PneumaCore", "VentTech"],
            "IMMUNE": ["ImmunoBoost", "PathogenShield", "NanoDefense", "BioCleanse", "ImmuneMatrix", 
                      "ToxFilter", "HealthCore", "CellGuard", "ViruScan"],
            "MUSCULAR": ["MuscleWeave", "FiberTech", "StrengthCore", "FlexMatrix", "PowerMuscle", 
                        "MotorBoost", "ReflexEnhance", "TendoLink", "ForceCore"]
        }
        
        item_name = random.choice(implant_names.get(implant_type, implant_names["NEURAL"]))
        
        # Générer une description
        descriptions = {
            "NEURAL": [
                "Implant neural offrant une amélioration cognitive significative.",
                "Interface neurale pour une connexion plus rapide aux réseaux.",
                "Processeur neural intégré avec capacités d'IA autonomes."
            ],
            "OPTICAL": [
                "Implant oculaire avancé avec vision nocturne et zoom intégré.",
                "Remplacement rétinien complet avec réalité augmentée.",
                "Interface visuelle avec analyse en temps réel et filtres personnalisables."
            ],
            "SKELETAL": [
                "Renforcement osseux offrant une résistance accrue aux impacts.",
                "Structure squelettique composite avec alliages légers avancés.",
                "Implants articulaires permettant des mouvements surhumains."
            ],
            "DERMAL": [
                "Armure sous-cutanée offrant une protection contre les projectiles.",
                "Maille dermique thermosensible avec capteurs intégrés.",
                "Revêtement synthétique avec régulation thermique avancée."
            ],
            "CIRCULATORY": [
                "Système circulatoire amélioré pour une endurance exceptionnelle.",
                "Filtre sanguin automatisé éliminant toxines et pathogènes.",
                "Régulateur cardiaque avec modes de performances ajustables."
            ],
            "RESPIRATORY": [
                "Système respiratoire augmenté avec filtration avancée.",
                "Bioréacteur pulmonaire maximisant l'absorption d'oxygène.",
                "Implant permettant de respirer dans des environnements hostiles."
            ],
            "IMMUNE": [
                "Système immunitaire renforcé contre agents pathogènes et toxines.",
                "Nanobots médicaux en circulation permanente dans le corps.",
                "Défense biologique adaptative avec mémoire immunitaire avancée."
            ],
            "MUSCULAR": [
                "Fibre musculaire synthétique offrant une force surhumaine.",
                "Système myoélectrique avec réponse réflexe amplifiée.",
                "Implants de tendons et ligaments pour performances athlétiques exceptionnelles."
            ]
        }
        
        item_description = random.choice(descriptions.get(implant_type, descriptions["NEURAL"]))
        
        # Générer le prix de base selon la rareté
        rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
        rarity_weights = [50, 30, 15, 4, 1]
        rarity = random.choices(rarities, weights=rarity_weights)[0]
        
        # Prix de base selon la rareté et le type
        base_prices = {
            "COMMON": {
                "NEURAL": random.randint(500, 1500),
                "OPTICAL": random.randint(400, 1200),
                "SKELETAL": random.randint(600, 1800),
                "DERMAL": random.randint(300, 1000),
                "CIRCULATORY": random.randint(700, 2000),
                "RESPIRATORY": random.randint(600, 1800),
                "IMMUNE": random.randint(800, 2500),
                "MUSCULAR": random.randint(500, 1500)
            },
            "UNCOMMON": {
                "NEURAL": random.randint(1400, 3000),
                "OPTICAL": random.randint(1100, 2500),
                "SKELETAL": random.randint(1600, 3500),
                "DERMAL": random.randint(900, 2000),
                "CIRCULATORY": random.randint(1800, 4000),
                "RESPIRATORY": random.randint(1500, 3500),
                "IMMUNE": random.randint(2300, 5000),
                "MUSCULAR": random.randint(1400, 3000)
            },
            "RARE": {
                "NEURAL": random.randint(2800, 6000),
                "OPTICAL": random.randint(2400, 5000),
                "SKELETAL": random.randint(3300, 7000),
                "DERMAL": random.randint(1800, 4000),
                "CIRCULATORY": random.randint(3800, 8000),
                "RESPIRATORY": random.randint(3300, 7000),
                "IMMUNE": random.randint(4800, 10000),
                "MUSCULAR": random.randint(2800, 6000)
            },
            "EPIC": {
                "NEURAL": random.randint(5800, 12000),
                "OPTICAL": random.randint(4800, 10000),
                "SKELETAL": random.randint(6500, 15000),
                "DERMAL": random.randint(3800, 8000),
                "CIRCULATORY": random.randint(7500, 18000),
                "RESPIRATORY": random.randint(6500, 15000),
                "IMMUNE": random.randint(9500, 20000),
                "MUSCULAR": random.randint(5800, 12000)
            },
            "LEGENDARY": {
                "NEURAL": random.randint(11500, 25000),
                "OPTICAL": random.randint(9500, 20000),
                "SKELETAL": random.randint(14000, 30000),
                "DERMAL": random.randint(7500, 16000),
                "CIRCULATORY": random.randint(17000, 35000),
                "RESPIRATORY": random.randint(14000, 30000),
                "IMMUNE": random.randint(19000, 40000),
                "MUSCULAR": random.randint(11500, 25000)
            }
        }
        
        price = base_prices.get(rarity, {}).get(implant_type, random.randint(1000, 5000))
        
        # Générer des statistiques basées sur la rareté
        stats_multiplier = {
            "COMMON": 1,
            "UNCOMMON": 1.5,
            "RARE": 2.5,
            "EPIC": 4,
            "LEGENDARY": 7
        }.get(rarity, 1)
        
        # Effets de l'implant
        effects = []
        
        # Effets communs à tous les implants
        base_effects = [
            {"type": "HEALTH_MAX", "value": int(random.randint(5, 15) * stats_multiplier)},
            {"type": "STAMINA_MAX", "value": int(random.randint(5, 15) * stats_multiplier)},
            {"type": "RESISTANCE", "value": int(random.randint(1, 5) * stats_multiplier)}
        ]
        
        # Effets spécifiques selon le type d'implant
        type_effects = {
            "NEURAL": [
                {"type": "INTELLIGENCE", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "HACKING", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "REACTION_TIME", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "OPTICAL": [
                {"type": "PERCEPTION", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "ACCURACY", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "NIGHT_VISION", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "SKELETAL": [
                {"type": "STRENGTH", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "DURABILITY", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "CARRY_WEIGHT", "value": int(random.randint(10, 30) * stats_multiplier)}
            ],
            "DERMAL": [
                {"type": "ARMOR", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "THERMAL_RESISTANCE", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "TOXIN_RESISTANCE", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "CIRCULATORY": [
                {"type": "STAMINA_REGEN", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "OXYGEN_EFFICIENCY", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "BLEEDING_RESISTANCE", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "RESPIRATORY": [
                {"type": "ENDURANCE", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "TOXIN_FILTERING", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "OXYGEN_STORAGE", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "IMMUNE": [
                {"type": "DISEASE_RESISTANCE", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "HEALING_RATE", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "TOXIN_RESISTANCE", "value": int(random.randint(5, 15) * stats_multiplier)}
            ],
            "MUSCULAR": [
                {"type": "STRENGTH", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "AGILITY", "value": int(random.randint(5, 15) * stats_multiplier)},
                {"type": "SPEED", "value": int(random.randint(5, 15) * stats_multiplier)}
            ]
        }
        
        # Sélectionner des effets
        effects.extend(random.sample(base_effects, k=1))  # Un effet de base
        type_specific_effects = type_effects.get(implant_type, type_effects["NEURAL"])
        effects.extend(random.sample(type_specific_effects, k=min(2, len(type_specific_effects))))  # Deux effets spécifiques
        
        # Effets secondaires possibles
        side_effects = []
        if random.random() < 0.4:  # 40% de chance d'avoir des effets secondaires
            possible_side_effects = [
                {"type": "HEALTH_MAX", "value": -int(random.randint(1, 5))},
                {"type": "STAMINA_MAX", "value": -int(random.randint(1, 5))},
                {"type": "INTELLIGENCE", "value": -int(random.randint(1, 3))},
                {"type": "IMMUNE_RESPONSE", "value": -int(random.randint(1, 3))},
                {"type": "SOCIAL", "value": -int(random.randint(1, 3))},
                {"type": "ADDICTION_CHANCE", "value": int(random.randint(1, 5))},
                {"type": "GLITCH_CHANCE", "value": int(random.randint(1, 5))}
            ]
            
            side_effects = random.sample(possible_side_effects, k=random.randint(1, 2))
        
        # Paramètres d'installation
        surgery_difficulty = random.randint(1, 10)
        
        # Paramètres de compatibilité
        compatibility = {
            "required_tech_level": random.randint(1, 7),
            "compatible_systems": random.sample(["STANDARD", "MILITARY", "CORPORATE", "BLACK_MARKET", "EXPERIMENTAL"], k=random.randint(1, 3)),
            "incompatible_implants": [] if random.random() < 0.7 else random.sample(implant_types, k=random.randint(1, 2))
        }
        
        # Fabricants possibles
        manufacturers = [
            "CyberMed", "BioTechnica", "NeuroSoft", "ImplantX", "SynthTech",
            "BodyWare", "EnhanceTech", "CyberLife", "BioForge", "ImplantSolutions"
        ]
        manufacturer = random.choice(manufacturers)
        
        # Emplacement corporel
        body_locations = {
            "NEURAL": ["BRAIN", "SPINE", "CORTEX"],
            "OPTICAL": ["EYES", "OPTIC_NERVE", "VISUAL_CORTEX"],
            "SKELETAL": ["SPINE", "JOINTS", "FULL_SKELETON", "RIBS"],
            "DERMAL": ["TORSO", "FULL_BODY", "ARMS", "FACE"],
            "CIRCULATORY": ["HEART", "VEINS", "BLOOD"],
            "RESPIRATORY": ["LUNGS", "THROAT", "DIAPHRAGM"],
            "IMMUNE": ["LYMPHATIC", "BLOODSTREAM", "BONE_MARROW"],
            "MUSCULAR": ["ARMS", "LEGS", "TORSO", "FULL_BODY"]
        }
        body_location = random.choice(body_locations.get(implant_type, ["TORSO"]))
        
        # Niveau d'intégration
        integration_levels = ["BASIC", "STANDARD", "ADVANCED", "EXPERIMENTAL", "PROTOTYPE"]
        integration_level = random.choices(
            integration_levels,
            weights=[0.3, 0.4, 0.2, 0.07, 0.03],
            k=1
        )[0]
        
        # Générer les métadonnées standardisées pour l'implant
        metadata = {
            "implant_type": implant_type,
            "body_location": body_location,
            "surgery_difficulty": surgery_difficulty,
            "effects": effects,
            "side_effects": side_effects,
            "compatibility": compatibility,
            "manufacturer": manufacturer,
            "integration_level": integration_level,
            "power_consumption": random.randint(1, 10),
            "requires_maintenance": random.random() < 0.3
        }
        
        # Qualité de l'article
        qualities = ["Poor", "Average", "Good", "Excellent", "Perfect"]
        quality_weights = [10, 40, 30, 15, 5]
        quality = random.choices(qualities, weights=quality_weights)[0]
        
        # Légalité (1 = légal, 0 = illégal)
        legality = 0 if is_illegal or random.random() < 0.2 else 1
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO implant_items (
                id, world_id, name, description, implant_type, body_location, surgery_difficulty, 
                side_effects, compatibility, rarity, price, is_legal, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, world_id, item_name, item_description, implant_type, body_location,
            surgery_difficulty, json.dumps(side_effects), json.dumps(compatibility),
            rarity, price, legality, json.dumps(metadata)
        ))
        
        db.conn.commit()
        logger.info(f"Implant généré: {item_name} (ID: {item_id})")
        
        return item_id
            
    def generate_random_clothing_item(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère un vêtement aléatoire pour une boutique
        
        Args:
            db: Base de données
            world_id: ID du monde
            is_illegal: Si l'article est illégal
            
        Returns:
            ID de l'article généré
        """
        logger.info("Génération d'un vêtement aléatoire")
        
        cursor = db.conn.cursor()
        
        # Vérifier si la table clothing_items existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='clothing_items'
        """)
        
        if not cursor.fetchone():
            # Créer la table clothing_items si elle n'existe pas
            cursor.execute("""
                CREATE TABLE clothing_items (
                    id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    subtype TEXT,
                    price INTEGER DEFAULT 0,
                    rarity TEXT DEFAULT 'COMMON',
                    quality TEXT DEFAULT 'Normal',
                    legality INTEGER DEFAULT 1,
                    metadata TEXT,
                    slots TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
                )
            """)
            db.conn.commit()
            logger.info("Table clothing_items créée")
        
        # Générer les détails du vêtement
        item_id = f"clothing_{uuid.uuid4()}"
        
        # Types de vêtements
        clothing_types = ["HEAD", "FACE", "TORSO", "ARMS", "HANDS", "LEGS", "FEET", "FULL_BODY", "ACCESSORY"]
        clothing_type = random.choice(clothing_types)
        
        # Sous-types selon le type de vêtement
        subtypes = {
            "HEAD": ["HELMET", "HAT", "CAP", "BEANIE", "HOOD", "HEADBAND"],
            "FACE": ["MASK", "GLASSES", "VISOR", "RESPIRATOR", "FACE_SHIELD"],
            "TORSO": ["SHIRT", "JACKET", "COAT", "VEST", "ARMOR", "SWEATER", "HOODIE"],
            "ARMS": ["SLEEVES", "ARM_PADS", "TATTOO_SLEEVES", "CYBER_SLEEVES"],
            "HANDS": ["GLOVES", "GAUNTLETS", "CYBER_GLOVES", "TACTICAL_GLOVES"],
            "LEGS": ["PANTS", "SHORTS", "SKIRT", "LEG_ARMOR", "JEANS", "LEGGINGS"],
            "FEET": ["BOOTS", "SHOES", "SNEAKERS", "CYBER_BOOTS", "TACTICAL_BOOTS"],
            "FULL_BODY": ["SUIT", "OUTFIT", "JUMPSUIT", "EXOSUIT", "STEALTH_SUIT"],
            "ACCESSORY": ["BELT", "WATCH", "NECKLACE", "BRACELET", "EARRINGS", "BACKPACK", "BAG"]
        }
        
        clothing_subtype = random.choice(subtypes.get(clothing_type, ["STANDARD"]))
        
        # Styles disponibles
        styles = ["CASUAL", "FORMAL", "MILITARY", "CORPORATE", "STREETWEAR", "CYBER", "RETRO", "PUNK", "TECH", "GANG"]
        
        # Générer un nom en fonction du type et du style
        style = random.choice(styles)
        
        # Préfixes basés sur le style
        style_prefixes = {
            "CASUAL": ["Comfy", "Relaxed", "Everyday", "Basic", "Simple"],
            "FORMAL": ["Elegant", "Professional", "Business", "Refined", "Sophisticated"],
            "MILITARY": ["Tactical", "Combat", "Armored", "Camo", "Battle"],
            "CORPORATE": ["Corporate", "Executive", "Office", "Business", "Professional"],
            "STREETWEAR": ["Urban", "Street", "Graffiti", "Metro", "City"],
            "CYBER": ["Cyber", "Neon", "Digital", "Tech", "Futuristic"],
            "RETRO": ["Vintage", "Classic", "Retro", "Old-School", "Throwback"],
            "PUNK": ["Rebel", "Anarchy", "Spike", "Chain", "Distressed"],
            "TECH": ["Smart", "Connected", "HUD", "AR", "Sensor"],
            "GANG": ["Gang", "Crew", "Faction", "Turf", "Street"]
        }
        
        # Noms de base selon le type
        base_names = {
            "HEAD": ["Helmet", "Hat", "Cap", "Headgear", "Hood"],
            "FACE": ["Mask", "Visor", "Glasses", "Respirator", "Face Cover"],
            "TORSO": ["Jacket", "Vest", "Shirt", "Coat", "Top", "Armor"],
            "ARMS": ["Sleeves", "Arm Guards", "Arm Pads", "Arm Wraps"],
            "HANDS": ["Gloves", "Gauntlets", "Hand Protectors", "Grip Enhancers"],
            "LEGS": ["Pants", "Trousers", "Jeans", "Leggings", "Shorts"],
            "FEET": ["Boots", "Shoes", "Sneakers", "Footwear"],
            "FULL_BODY": ["Suit", "Outfit", "Jumpsuit", "Bodysuit", "Armor"],
            "ACCESSORY": ["Belt", "Watch", "Necklace", "Bracelet", "Bag", "Backpack"]
        }
        
        # Qualificatifs selon le style et la rareté
        rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
        rarity_weights = [60, 25, 10, 4, 1]
        rarity = random.choices(rarities, weights=rarity_weights)[0]
        
        rarity_qualifiers = {
            "COMMON": ["Standard", "Basic", "Regular", "Common", "Simple"],
            "UNCOMMON": ["Quality", "Enhanced", "Reinforced", "Improved", "Custom"],
            "RARE": ["Premium", "Advanced", "Superior", "Elite", "Specialized"],
            "EPIC": ["Exceptional", "Mastercraft", "Professional", "Cutting-Edge", "Legendary"],
            "LEGENDARY": ["Ultimate", "Mythical", "Unprecedented", "Revolutionary", "Godlike"]
        }
        
        # Construire le nom complet
        prefix = random.choice(style_prefixes.get(style, ["Standard"]))
        base_name = random.choice(base_names.get(clothing_type, ["Clothing"]))
        qualifier = random.choice(rarity_qualifiers.get(rarity, ["Standard"]))
        
        name_patterns = [
            f"{prefix} {base_name}",
            f"{qualifier} {base_name}",
            f"{prefix} {qualifier} {base_name}",
            f"{style} {base_name}",
            f"{base_name} of {qualifier} {style}"
        ]
        
        item_name = random.choice(name_patterns)
        
        # Générer une description
        description_templates = [
            f"Un {base_name.lower()} de style {style.lower()}, offrant {random.choice(['confort', 'protection', 'style', 'durabilité'])} et {random.choice(['fonctionnalité', 'élégance', 'résistance'])}.",
            f"Ce {base_name.lower()} {style.lower()} se distingue par son {random.choice(['design unique', 'style remarquable', 'confort exceptionnel', 'aspect intimidant'])}.",
            f"Vêtement {style.lower()} conçu pour les environnements {random.choice(['urbains', 'hostiles', 'professionnels', 'sociaux', 'dangereux'])}.",
            f"Un {qualifier.lower()} {base_name.lower()} qui {random.choice(['protège', 'améliore', 'complète', 'transforme'])} votre apparence."
        ]
        
        item_description = random.choice(description_templates)
        
        # Générer le prix selon le type, le style et la rareté
        base_prices = {
            "HEAD": random.randint(20, 100),
            "FACE": random.randint(30, 150),
            "TORSO": random.randint(50, 200),
            "ARMS": random.randint(30, 120),
            "HANDS": random.randint(20, 100),
            "LEGS": random.randint(40, 180),
            "FEET": random.randint(40, 150),
            "FULL_BODY": random.randint(100, 400),
            "ACCESSORY": random.randint(10, 80)
        }
        
        style_price_multipliers = {
            "CASUAL": 0.8,
            "FORMAL": 1.2,
            "MILITARY": 1.5,
            "CORPORATE": 1.3,
            "STREETWEAR": 1.0,
            "CYBER": 1.6,
            "RETRO": 1.1,
            "PUNK": 1.0,
            "TECH": 1.7,
            "GANG": 0.9
        }
        
        rarity_price_multipliers = {
            "COMMON": 1,
            "UNCOMMON": 2,
            "RARE": 4,
            "EPIC": 8,
            "LEGENDARY": 20
        }
        
        base_price = base_prices.get(clothing_type, 50)
        style_multiplier = style_price_multipliers.get(style, 1.0)
        rarity_multiplier = rarity_price_multipliers.get(rarity, 1)
        
        price = int(base_price * style_multiplier * rarity_multiplier)
        
        # Qualité
        qualities = ["Poor", "Average", "Good", "Excellent", "Perfect"]
        quality_weights = [10, 40, 30, 15, 5]
        quality = random.choices(qualities, weights=quality_weights)[0]
        
        # Caractéristiques et attributs
        attributes = []
        
        # Attributs potentiels selon le type
        potential_attributes = {
            "HEAD": ["ARMOR", "PERCEPTION", "COMMS", "STYLE", "TEMPERATURE_CONTROL", "NVG"],
            "FACE": ["ARMOR", "PERCEPTION", "STEALTH", "FILTER", "ID_PROTECTION", "AR_DISPLAY"],
            "TORSO": ["ARMOR", "STORAGE", "TEMPERATURE_CONTROL", "STEALTH", "STYLE"],
            "ARMS": ["ARMOR", "MOBILITY", "STYLE", "STORAGE", "STRENGTH_BOOST"],
            "HANDS": ["ARMOR", "GRIP", "DEXTERITY", "HACKING_BOOST", "WEAPON_HANDLING"],
            "LEGS": ["ARMOR", "MOBILITY", "STORAGE", "STYLE", "JUMP_BOOST"],
            "FEET": ["ARMOR", "MOBILITY", "GRIP", "SILENT", "TEMPERATURE_CONTROL"],
            "FULL_BODY": ["ARMOR", "STEALTH", "TEMPERATURE_CONTROL", "STORAGE", "STRENGTH_BOOST", "STYLE"],
            "ACCESSORY": ["STORAGE", "STYLE", "UTILITY", "COMMS", "HACKING_BOOST"]
        }
        
        # Sélectionner des attributs aléatoirement
        type_attributes = potential_attributes.get(clothing_type, ["STYLE"])
        num_attributes = min(random.randint(1, 3), len(type_attributes))
        selected_attributes = random.sample(type_attributes, k=num_attributes)
        
        for attr in selected_attributes:
            attr_value = random.randint(1, 10) * (1 + rarities.index(rarity) * 0.5)
            attributes.append({"type": attr, "value": int(attr_value)})
        
        # Possibilités d'amélioration
        mod_slots = random.randint(0, 3) * (1 + rarities.index(rarity) * 0.2)
        
        # Restrictions d'utilisation (si applicable)
        requirements = {}
        if random.random() < 0.3:  # 30% de chance d'avoir des restrictions
            requirements = {
                "level": random.randint(1, 10) * (1 + rarities.index(rarity) * 0.3),
                "attributes": {}
            }
            
            possible_req_attributes = ["STRENGTH", "AGILITY", "REPUTATION", "INTELLIGENCE"]
            req_attr = random.choice(possible_req_attributes)
            requirements["attributes"][req_attr] = random.randint(1, 5)
        
        # Protection aux éléments (si applicable)
        element_protection = {}
        if random.random() < 0.5:  # 50% de chance d'avoir des protections élémentaires
            elements = ["PHYSICAL", "THERMAL", "ELECTRICAL", "CHEMICAL", "RADIATION"]
            num_elements = random.randint(1, min(3, len(elements)))
            
            for element in random.sample(elements, k=num_elements):
                protection_value = random.randint(1, 10) * (1 + rarities.index(rarity) * 0.4)
                element_protection[element] = int(protection_value)
        
        # Déterminer l'emplacement (slot) en fonction du type de vêtement
        if clothing_type.lower() in ["hat", "helmet", "cap"]:
            slots = "HEAD"
        elif clothing_type.lower() in ["jacket", "coat", "vest", "armor", "shirt"]:
            slots = "BODY"
        elif clothing_type.lower() in ["pants", "shorts", "skirt"]:
            slots = "LEGS"
        elif clothing_type.lower() in ["boots", "shoes"]:
            slots = "FEET"
        elif clothing_type.lower() in ["gloves"]:
            slots = "HANDS"
        else:
            slots = "ACCESSORY"
            
        # Générer les métadonnées standardisées
        metadata = {
            "clothing_type": clothing_type,
            "style": style,
            "attributes": attributes,
            "mod_slots": int(mod_slots),
            "requirements": requirements,
            "element_protection": element_protection,
            "weight": random.randint(1, 10),
            "durability": random.randint(1, 100) + (rarities.index(rarity) * 20),
            "slots": slots
        }
        
        # Légalité (1 = légal, 0 = illégal)
        # Certains styles ou types de vêtements peuvent être illégaux
        legality = 0 if is_illegal or (style in ["MILITARY", "GANG"] and random.random() < 0.3) else 1
        
        # Construire les statistiques complètes
        stats = {
            "style": style,
            "comfort": random.randint(1, 10),
            "protection": random.randint(1, 10),
            "charisma": random.randint(1, 10),
            "status": random.randint(1, 10)
        }
        
        # Métadonnées complètes pour la compatibilité avec le jeu
        metadata = {
            "clothing_type": clothing_type,
            "style": style,
            "comfort": stats["comfort"],
            "protection": stats["protection"],
            "charisma": stats["charisma"],
            "status": stats["status"],
            "level": random.randint(1, 10),
            "rarity": rarity,
            "is_legal": legality,
            "armor_type": "body" if clothing_type in ["jacket", "coat", "vest", "armor"] else 
                         "head" if clothing_type in ["hat", "helmet", "cap"] else
                         "legs" if clothing_type in ["pants", "shorts", "skirt"] else
                         "feet" if clothing_type in ["shoes", "boots"] else
                         "hands" if clothing_type in ["gloves"] else "accessory",
            "slots": slots
        }
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO clothing_items (
                id, name, description, clothing_type, rarity, level, stats, price, world_id, is_legal, metadata, slots
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, item_name, item_description, clothing_type, rarity, random.randint(1, 10), 
            json.dumps(stats), price, world_id, legality, json.dumps(metadata), slots
        ))
        
        db.conn.commit()
        logger.info(f"Vêtement généré: {item_name} (ID: {item_id})")
        
        return item_id
            
    def generate_random_software_item(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère un logiciel aléatoire pour une boutique.
        
        Args:
            db: Connexion à la base de données
            world_id: ID du monde
            is_illegal: Indique si l'objet doit être illégal

        Returns:
            L'ID de l'objet généré
        """
        cursor = db.conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS software_items (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                software_type TEXT,
                level INTEGER,
                features TEXT,
                price INTEGER,
                world_id TEXT,
                is_legal INTEGER DEFAULT 1,
                metadata TEXT,
                version TEXT DEFAULT 'N/A',
                license_type TEXT DEFAULT 'Standard',
                capabilities TEXT,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
        """)

        # Générer un ID unique pour l'objet
        item_id = f"software_{uuid.uuid4()}"
        
        # Types de logiciels
        software_types = [
            "SECURITY", "HACKING", "ANTIVIRUS", "FIREWALL", "ENCRYPTION", 
            "DECRYPTION", "BYPASS", "TRACKER", "SPYWARE", "UTILITY",
            "DATABASE", "AI", "VPN", "OPERATING_SYSTEM", "GAME"
        ]
        
        # Versions de logiciels
        software_versions = [
            "1.0", "2.0", "3.5", "4.2", "5.0", "6.1", "7.0", "8.3", "9.0", "10.5",
            "2023", "2024", "2025", "Alpha", "Beta", "RC", "Pro", "Enterprise", "Ultimate", "Lite"
        ]
        
        # Types de licences
        license_types = [
            "Standard", "Pro", "Enterprise", "Personal", "Educational", "Free", "Trial",
            "Open Source", "Black Market", "Military", "Government", "Corporate"
        ]
        
        # Fabricants de logiciels
        manufacturers = [
            "ByteCorp", "CyberSys", "NetMatrix", "CodeFlow", "DigitalNexus", 
            "TechWave", "SynthCorp", "VirtualEdge", "InfoStream", "DataForge",
            "AlgoBit", "QuantumSoft", "NeuraTech", "CryptoLogic", "MegaByte"
        ]
        
        # Fonctionnalités
        possible_features = [
            "Encryption avancée", "Analyse temps réel", "Interface intuitive", "Outil de diagnostic", 
            "Protection multi-couches", "IA adaptative", "Module antivirus",
            "Analyse forensique", "Détection proactive", "Bypass firewall", "Accès distant",
            "Craquage de mots de passe", "Masquage d'IP", "Anonymisation", "Data shredder", 
            "VPN intégré", "Anti-traçage", "Brouillage réseau", "Scan de vulnérabilités"
        ]
        
        # Niveaux de rareté avec leurs probabilités
        rarities = [
            ("Common", 0.50),
            ("Uncommon", 0.30),
            ("Rare", 0.15),
            ("Epic", 0.04),
            ("Legendary", 0.01)
        ]
        
        # Sélectionner un type de logiciel aléatoire
        software_type = random.choice(software_types)
        
        # Sélectionner un fabricant aléatoire
        manufacturer = random.choice(manufacturers)
        
        # Sélectionner une version aléatoire
        version = random.choice(software_versions)
        
        # Sélectionner un type de licence aléatoire
        license_type = random.choice(license_types)
        
        if is_illegal:
            # Augmenter la probabilité de types illégaux pour les articles illégaux
            if random.random() < 0.8:
                software_type = random.choice(["HACKING", "BYPASS", "SPYWARE", "DECRYPTION"])
                license_type = random.choice(["Black Market", "Military", "Corporate"])
                
        # Déterminer la légalité en fonction du type et de l'attribut is_illegal
        legality = 0 if is_illegal or software_type in ["HACKING", "BYPASS", "SPYWARE"] and random.random() < 0.7 else 1
        
        # Sélectionner un niveau de rareté basé sur les probabilités
        rarity = random.choices([r[0] for r in rarities], weights=[r[1] for r in rarities])[0]
        
        # Déterminer le niveau de l'objet (1-10)
        level = random.randint(1, 10)
        
        # Construire le nom de l'objet
        item_name = f"{manufacturer} {software_type.title()} {version}"
        
        # Construire la description en fonction de la rareté
        if rarity == "Common":
            item_description = f"Logiciel standard d'entrée de gamme."
        elif rarity == "Uncommon":
            item_description = f"Bonne logiciel avec composants améliorés."
        elif rarity == "Rare":
            item_description = f"Logiciel supérieur avec finition personnalisée."
        elif rarity == "Epic":
            item_description = f"Puissance de traitement considérable de qualité supérieure avec composants exclusifs."
        else:  # Legendary
            item_description = f"Logiciel mythique d'exception, rare et extrêmement puissant."
        
        # Déterminer les fonctionnalités de l'objet en fonction de la rareté
        num_features = min(len(possible_features), random.randint(1, 4))
        features = random.sample(possible_features, k=num_features)
        
        # Déterminer le prix en fonction de la rareté et du niveau
        base_price = 50
        
        if rarity == "Common":
            price_multiplier = 1
        elif rarity == "Uncommon":
            price_multiplier = 2
        elif rarity == "Rare":
            price_multiplier = 4
        elif rarity == "Epic":
            price_multiplier = 8
        else:  # Legendary
            price_multiplier = 16
        
        price = base_price * price_multiplier * level
        price = round(price * random.uniform(0.8, 1.2))  # Variation aléatoire de ±20%
        
        # Construire le dictionnaire de métadonnées
        metadata = {
            "manufacturer": manufacturer,
            "creation_date": (datetime.now() + timedelta(days=random.randint(365, 1095))).isoformat(),
            "installation_size": f"{random.randint(1, 500)} MB",
            "system_requirements": [
                f"RAM: {random.choice([2, 4, 8, 16, 32])} GB",
                f"Processor: {random.choice(['Basic', 'Standard', 'Advanced', 'High-end'])}"
            ],
            "compatible_os": random.sample(["Windows", "Linux", "MacOS", "Android", "iOS"], random.randint(1, 5))
        }
        
        # Créer un dictionnaire de capabilities
        capabilities = {
            "processing_power": random.randint(1, 10) * level,
            "encryption_level": random.randint(1, 10) * (1 if software_type != "ENCRYPTION" else 2),
            "stealth_factor": random.randint(1, 10) * (1 if software_type != "SPYWARE" else 2),
            "detection_rating": random.randint(1, 10) * (1 if software_type != "ANTIVIRUS" else 2)
        }
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO software_items (
                id, name, description, software_type, level, features, price, world_id, is_legal,
                metadata, version, license_type, capabilities
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, item_name, item_description, software_type, level, json.dumps(features),
            price, world_id, legality, json.dumps(metadata), version, license_type, json.dumps(capabilities)
        ))
        
        db.conn.commit()
        
        logger = logging.getLogger("YakTaa.WorldEditor.Generator.ShopItems")
        logger.info(f"Logiciel généré: {item_name} (ID: {item_id})")
        
        return item_id
            
    def generate_random_weapon(self, db, world_id: str, is_illegal: bool = False):
        """
        Génère une arme aléatoire pour une boutique.
        
        Args:
            db: Connexion à la base de données
            world_id: ID du monde
            is_illegal: Indique si l'objet doit être illégal

        Returns:
            L'ID de l'objet généré
        """
        cursor = db.conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weapon_items (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                weapon_type TEXT,
                rarity TEXT,
                level INTEGER,
                stats TEXT,
                price INTEGER,
                world_id TEXT,
                is_legal INTEGER DEFAULT 1,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
            )
        """)

        # Générer un ID unique pour l'objet
        item_id = f"weapon_{uuid.uuid4()}"
        
        # Types d'armes
        weapon_types = [
            "PISTOL", "RIFLE", "SHOTGUN", "SMG", "SNIPER", "MELEE", "EXPLOSIVE", 
            "ENERGY", "LASER", "PLASMA", "STUN", "GADGET", "BOW", "BLADE"
        ]
        
        # Fabricants d'armes
        manufacturers = [
            "TechArms", "BlastTech", "SynthFire", "NeoCorp", "PulseCraft", 
            "VortexDefense", "CyberStrike", "NexusGun", "QuantumForge", "HyperCannon",
            "Stealth Industries", "BlackOps", "Securitech", "Enforcer", "Shadow"
        ]
        
        # Préfixes et suffixes pour les noms
        prefixes = [
            "Advanced", "Enhanced", "Tactical", "Military", "Urban", "Stealth", 
            "Precision", "Reinforced", "Compact", "Augmented", "Prototype", 
            "Elite", "Custom", "Industrial", "Black Market"
        ]
        
        suffixes = [
            "Mk I", "Mk II", "Mk III", "X1", "X2", "Alpha", "Beta", "Prototype",
            "Standard", "Special", "Elite", "Pro", "Nexus", "Prime", "V2.0"
        ]
        
        # Niveaux de rareté avec leurs probabilités
        rarities = [
            ("Common", 0.50),
            ("Uncommon", 0.30),
            ("Rare", 0.15),
            ("Epic", 0.04),
            ("Legendary", 0.01)
        ]
        
        # Effets spéciaux possibles
        special_effects = [
            "silencer", "extended_mag", "laser_sight", "armor_piercing", "scope",
            "quick_reload", "explosive_rounds", "incendiary_ammo", "dual_wield",
            "stabilizer", "shock_rounds", "bio_targeting", "holographic_sight"
        ]
        
        # Sélectionner un type d'arme aléatoire
        weapon_type = random.choice(weapon_types)
        
        # Sélectionner un fabricant aléatoire
        manufacturer = random.choice(manufacturers)
        
        # Sélectionner un préfixe aléatoire
        prefix = random.choice(prefixes)
        
        # Sélectionner un suffixe aléatoire
        suffix = random.choice(suffixes)
        
        if is_illegal:
            # Augmenter la probabilité de certains types d'armes pour les articles illégaux
            if random.random() < 0.7:
                weapon_type = random.choice(["SNIPER", "ENERGY", "PLASMA", "EXPLOSIVE"])
                prefix = random.choice(["Black Market", "Military", "Stealth", "Elite"])
                
        # Déterminer la légalité en fonction du type et de l'attribut is_illegal
        legality = 0 if is_illegal or weapon_type in ["PLASMA", "EXPLOSIVE"] and random.random() < 0.7 else 1
        
        # Sélectionner un niveau de rareté basé sur les probabilités
        rarity = random.choices([r[0] for r in rarities], weights=[r[1] for r in rarities])[0]
        
        # Déterminer le niveau de l'objet (1-10)
        level = random.randint(1, 10)
        
        # Construire le nom de l'objet
        item_name = f"{prefix} {manufacturer} {weapon_type.title()} {suffix} [{rarity}]"
        
        # Construire la description en fonction de la rareté
        if rarity == "Common":
            item_description = f"Arme standard d'entrée de gamme."
        elif rarity == "Uncommon":
            item_description = f"Bonne arme avec composants améliorés."
        elif rarity == "Rare":
            item_description = f"Arme supérieure avec finition personnalisée."
        elif rarity == "Epic":
            item_description = f"Puissance de feu considérable de qualité supérieure avec composants exclusifs."
        else:  # Legendary
            item_description = f"Arme mythique d'exception, rare et extrêmement puissante."
        
        # Déterminer les statistiques de l'arme en fonction du type et de la rareté
        base_damage = random.randint(10, 30)
        base_accuracy = random.randint(10, 30)
        base_range = random.randint(10, 30)
        base_rate = random.randint(10, 30)
        base_stability = random.randint(10, 30)
        
        # Modificateurs par type d'arme
        if weapon_type == "PISTOL":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 0.8, 1.2, 0.7, 1.0, 1.2
        elif weapon_type == "RIFLE":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.1, 1.1, 1.2, 0.9, 1.0
        elif weapon_type == "SHOTGUN":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.5, 0.7, 0.6, 0.6, 0.8
        elif weapon_type == "SMG":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 0.7, 0.8, 0.6, 1.5, 0.7
        elif weapon_type == "SNIPER":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.4, 1.5, 1.5, 0.5, 0.9
        elif weapon_type == "MELEE":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.3, 1.0, 0.3, 1.2, 1.3
        elif weapon_type == "EXPLOSIVE":
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.8, 0.6, 1.0, 0.4, 0.5
        elif weapon_type in ["ENERGY", "LASER", "PLASMA"]:
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.2, 1.3, 1.1, 1.0, 1.1
        else:  # Other types
            damage_mod, accuracy_mod, range_mod, rate_mod, stability_mod = 1.0, 1.0, 1.0, 1.0, 1.0
        
        # Modificateurs par rareté
        if rarity == "Common":
            rarity_mod = 1.0
        elif rarity == "Uncommon":
            rarity_mod = 1.3
        elif rarity == "Rare":
            rarity_mod = 1.6
        elif rarity == "Epic":
            rarity_mod = 2.0
        else:  # Legendary
            rarity_mod = 2.5
        
        # Calcul des statistiques finales
        damage = int(base_damage * damage_mod * rarity_mod * (0.9 + 0.2 * level / 10))
        accuracy = int(base_accuracy * accuracy_mod * rarity_mod * (0.9 + 0.2 * level / 10))
        range_stat = int(base_range * range_mod * rarity_mod * (0.9 + 0.2 * level / 10))
        rate_of_fire = int(base_rate * rate_mod * rarity_mod * (0.9 + 0.2 * level / 10))
        stability = int(base_stability * stability_mod * rarity_mod * (0.9 + 0.2 * level / 10))
        
        # Calcul du temps de rechargement (plus bas = meilleur)
        reload_time = round(5.0 - (rarity_mod * 0.5) - (level * 0.1), 2)
        reload_time = max(0.5, reload_time)  # Minimum 0.5 secondes
        
        # Sélectionner des effets spéciaux en fonction de la rareté
        num_effects = 0
        if rarity == "Uncommon":
            num_effects = random.randint(0, 1)
        elif rarity == "Rare":
            num_effects = random.randint(1, 2)
        elif rarity == "Epic":
            num_effects = random.randint(2, 3)
        elif rarity == "Legendary":
            num_effects = random.randint(3, 5)
        
        selected_effects = random.sample(special_effects, min(len(special_effects), num_effects))
        
        # Créer un dictionnaire de statistiques
        stats = {
            "damage": damage,
            "accuracy": accuracy,
            "range": range_stat,
            "rate_of_fire": rate_of_fire,
            "stability": stability,
            "reload_time": reload_time
        }
        
        if selected_effects:
            stats["special_effects"] = selected_effects
        
        # Déterminer le prix en fonction de la rareté et du niveau
        base_price = 100
        
        if rarity == "Common":
            price_multiplier = 1
        elif rarity == "Uncommon":
            price_multiplier = 3
        elif rarity == "Rare":
            price_multiplier = 6
        elif rarity == "Epic":
            price_multiplier = 12
        else:  # Legendary
            price_multiplier = 25
        
        price = base_price * price_multiplier * level
        price = round(price * random.uniform(0.8, 1.2))  # Variation aléatoire de ±20%
        
        # Stocker les propriétés importantes dans la colonne metadata
        metadata = {
            "damage": damage,
            "accuracy": accuracy,
            "range": range_stat,
            "rate_of_fire": rate_of_fire,
            "stability": stability,
            "reload_time": reload_time,
            "weapon_type": weapon_type,
            "level": level,
            "rarity": rarity,
            "is_legal": legality
        }
        
        # Insérer dans la base de données
        cursor.execute("""
            INSERT INTO weapon_items (
                id, name, description, weapon_type, rarity, level, stats, price, world_id, is_legal, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, item_name, item_description, weapon_type, rarity, level,
            json.dumps(stats), price, world_id, legality, json.dumps(metadata)
        ))
        
        db.conn.commit()
        
        logger = logging.getLogger("YakTaa.WorldEditor.Generator.ShopItems")
        logger.info(f"Arme générée: {item_name} (ID: {item_id})")
        
        return item_id
            
    def _get_shop_item_types(self, shop_type: str, available_types: List[str]) -> List[str]:
        """
        Détermine les types d'articles adaptés à une boutique
        
        Args:
            shop_type: Type de boutique
            available_types: Types d'articles disponibles
            
        Returns:
            Liste des types d'articles adaptés
        """
        shop_type = shop_type.upper()
        
        # Mapping des types de boutiques aux types d'articles adaptés
        shop_types_mapping = {
            "WEAPONS": ["weapons"],
            "ARMORY": ["weapons", "armors"],
            "GENERAL": ["weapons", "armors", "consumables", "hardware"],
            "ELECTRONICS": ["hardware", "software"],
            "MEDICAL": ["consumables", "implants"],
            "CYBER": ["implants", "hardware"],
            "GROCERY": ["consumables"],
            "CLOTHING": ["armors"],
            "BLACK_MARKET": ["weapons", "armors", "consumables", "implants", "hardware", "software"],
        }
        
        # Types d'articles adaptés à cette boutique
        shop_item_types = shop_types_mapping.get(shop_type, ["weapons", "armors", "consumables"])
        
        # Filtrer pour n'inclure que les types disponibles
        return [item_type for item_type in shop_item_types if item_type in available_types]
    
    def _get_table_for_type(self, item_type: str) -> str:
        """
        Retourne le nom de la table correspondant au type d'article
        
        Args:
            item_type: Type d'article
            
        Returns:
            Nom de la table
        """
        type_to_table = {
            "weapons": "weapon_items",
            "armors": "armor_items",
            "consumables": "consumable_items",
            "implants": "implant_items",
            "hardware": "hardware_items",
            "software": "software_items",
        }
        
        return type_to_table.get(item_type, "")
        
    def _determine_price_modifier(self, shop_type: str, item_type: str, 
                                 item_rarity: str, random_gen: random.Random) -> float:
        """
        Détermine le modificateur de prix pour un article
        
        Args:
            shop_type: Type de boutique
            item_type: Type d'article
            item_rarity: Rareté de l'article
            random_gen: Générateur aléatoire
            
        Returns:
            Modificateur de prix
        """
        # Base par défaut
        base_modifier = 1.0
        
        # Ajustement selon le type de boutique
        shop_type_modifiers = {
            "BLACK_MARKET": 1.5,  # Marché noir plus cher
            "GENERAL": 1.2,       # Magasins généraux un peu plus chers
            "ELECTRONICS": 1.1,   # Électronique un peu plus cher
            "WEAPONS": 1.3,       # Armes plus chères
            "ARMORY": 1.2,        # Armurerie un peu plus chère
            "MEDICAL": 1.4,       # Médical plus cher
            "CYBER": 1.5,         # Cyber très cher
            "GROCERY": 0.9,       # Épicerie moins chère
            "CLOTHING": 1.1       # Vêtements un peu plus chers
        }
        
        # Ajustement selon la rareté
        rarity_modifiers = {
            "COMMON": 1.0,
            "UNCOMMON": 1.1,
            "RARE": 1.2,
            "EPIC": 1.3,
            "LEGENDARY": 1.5
        }
        
        # Calcul du modificateur de base
        base_modifier *= shop_type_modifiers.get(shop_type.upper(), 1.0)
        base_modifier *= rarity_modifiers.get(item_rarity.upper(), 1.0)
        
        # Ajout d'une variance aléatoire (±15%)
        variance = random_gen.uniform(0.85, 1.15)
        
        return base_modifier * variance

# Fonction autonome pour la compatibilité avec le code existant
def generate_shop_inventory(db, world_id: str, shop_ids: List[str], 
                           item_types: List[str], random_seed: Optional[int] = None) -> None:
    """
    Version autonome de la fonction pour compatibilité avec le code existant
    """
    generator = ShopItemGenerator(db)
    return generator.generate_shop_inventory(world_id, shop_ids, item_types, random_seed)