"""
Script pour mettre à jour le schéma de la base de données YakTaa
et ajouter les tables et colonnes nécessaires pour les boutiques, consommables et implants
"""

import sqlite3
import uuid
import json
import random
import os
from datetime import datetime

# Chemin vers la base de données
DB_PATH = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

def update_schema(conn):
    """Mettre à jour le schéma de la base de données"""
    cursor = conn.cursor()
    
    print("Mise à jour du schéma de la base de données...")
    
    # 1. Ajouter les colonnes manquantes aux tables existantes
    
    # 1.1 Table consumable_items
    missing_columns_consumables = [
        ("consumable_type", "TEXT", "NOT NULL DEFAULT 'HEALTH'"),
        ("addiction_risk", "REAL", "DEFAULT 0.0"),
        ("side_effects", "TEXT", "DEFAULT NULL"),
        ("is_legal", "INTEGER", "DEFAULT 1"),
        ("item_type", "TEXT", "NOT NULL DEFAULT 'CONSUMABLE'"),
        ("location_type", "TEXT", "NOT NULL DEFAULT 'SHOP'"),
        ("location_id", "TEXT", "DEFAULT NULL"),
        ("uses", "INTEGER", "DEFAULT 1"),
        ("is_available", "INTEGER", "DEFAULT 1")
    ]
    
    for col_name, col_type, col_constraint in missing_columns_consumables:
        try:
            cursor.execute(f"ALTER TABLE consumable_items ADD COLUMN {col_name} {col_type} {col_constraint}")
            print(f"Ajout de la colonne {col_name} à la table consumable_items")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"La colonne {col_name} existe déjà dans consumable_items")
            else:
                print(f"Erreur lors de l'ajout de la colonne {col_name} à consumable_items: {e}")
    
    # 1.2 Table hardware_items
    missing_columns_hardware = [
        ("type", "TEXT", "NOT NULL DEFAULT 'CPU'"),
        ("is_legal", "INTEGER", "DEFAULT 1"),
        ("location_type", "TEXT", "NOT NULL DEFAULT 'SHOP'"),
        ("location_id", "TEXT", "DEFAULT NULL"),
        ("rarity", "TEXT", "DEFAULT 'Common'"),
        ("is_installed", "INTEGER", "DEFAULT 0"),
        ("is_available", "INTEGER", "DEFAULT 1")
    ]
    
    for col_name, col_type, col_constraint in missing_columns_hardware:
        try:
            # Vérifier si la colonne existe déjà
            cursor.execute("PRAGMA table_info(hardware_items)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE hardware_items ADD COLUMN {col_name} {col_type} {col_constraint}")
                print(f"Ajout de la colonne {col_name} à la table hardware_items")
            else:
                print(f"La colonne {col_name} existe déjà dans hardware_items")
        except sqlite3.OperationalError as e:
            print(f"Erreur lors de l'ajout de la colonne {col_name} à hardware_items: {e}")
    
    # 1.3 Table shops
    missing_columns_shops = [
        ("building_id", "TEXT", "DEFAULT NULL"),
        ("created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for col_name, col_type, col_constraint in missing_columns_shops:
        try:
            cursor.execute(f"ALTER TABLE shops ADD COLUMN {col_name} {col_type} {col_constraint}")
            print(f"Ajout de la colonne {col_name} à la table shops")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"La colonne {col_name} existe déjà dans shops")
            else:
                print(f"Erreur lors de l'ajout de la colonne {col_name} à shops: {e}")
    
    # 1.4 Table shop_inventory
    missing_columns_shop_inventory = [
        ("added_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP"),
        ("price", "INTEGER", "DEFAULT 100")
    ]
    
    for col_name, col_type, col_constraint in missing_columns_shop_inventory:
        try:
            cursor.execute(f"ALTER TABLE shop_inventory ADD COLUMN {col_name} {col_type} {col_constraint}")
            print(f"Ajout de la colonne {col_name} à la table shop_inventory")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"La colonne {col_name} existe déjà dans shop_inventory")
            else:
                print(f"Erreur lors de l'ajout de la colonne {col_name} à shop_inventory: {e}")
    
    # 2. Créer les tables manquantes
    
    # 2.1 Table implant_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS implant_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            implant_type TEXT NOT NULL,
            grade TEXT DEFAULT 'Standard',
            level INTEGER DEFAULT 1,
            stats TEXT,
            price INTEGER DEFAULT 0,
            world_id TEXT NOT NULL,
            is_legal INTEGER DEFAULT 1,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
    ''')
    print("Table implant_items créée ou existante")
    
    # 2.2 Table weapon_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapon_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            weapon_type TEXT NOT NULL,
            rarity TEXT DEFAULT 'Common',
            level INTEGER DEFAULT 1,
            stats TEXT,
            price INTEGER DEFAULT 0,
            world_id TEXT NOT NULL,
            is_legal INTEGER DEFAULT 1,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
    ''')
    print("Table weapon_items créée ou existante")
    
    # 2.3 Table software_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS software_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            software_type TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            features TEXT,
            price INTEGER DEFAULT 0,
            world_id TEXT NOT NULL,
            is_legal INTEGER DEFAULT 1,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE
        )
    ''')
    print("Table software_items créée ou existante")
    
    conn.commit()
    print("Schéma de la base de données mis à jour avec succès")

def get_first_world_id(conn):
    """Récupère l'ID du premier monde disponible"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM worlds LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def get_random_locations(conn, world_id, limit=5):
    """Récupère des lieux aléatoires dans le monde"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM locations WHERE world_id = ? ORDER BY RANDOM() LIMIT ?", (world_id, limit))
    return [row[0] for row in cursor.fetchall()]

def create_test_shops(conn, world_id, location_ids):
    """Crée des boutiques de test"""
    cursor = conn.cursor()
    
    # Types de boutiques
    shop_types = [
        "general", "weapons", "electronics", "medical", 
        "clothing", "food", "cybernetics", "digital_services", "black_market", "datachips"
    ]
    
    # Noms de boutiques par type
    shop_names = {
        "general": ["YakMart", "NeoGoods", "CyberBazaar", "StreetCorner", "Night Market"],
        "weapons": ["BoomSticks", "FirePower", "Iron Arsenal", "Shadow Armory", "Ballistic Dreams"],
        "electronics": ["CircuitCity", "ByteWorks", "TechHub", "WiredUp", "ElectroCore"],
        "medical": ["MediLife", "ChromaHealth", "BioFix", "SynthetiCare", "New You"],
        "clothing": ["StreetWear", "ChromaThreads", "NeoStyle", "UrbanGear", "Fashionista"],
        "food": ["NoodleHouse", "SynthFood", "UrbanEats", "ByteBites", "ProteinPlace"],
        "cybernetics": ["Chrome Clinic", "NeuroTech", "Body Mods", "Cyberdyne", "Augment Nation"],
        "digital_services": ["DataFlow", "NetConnect", "VirtualSuite", "CodeSpace", "InfoStream"],
        "black_market": ["BackAlley", "Shadow Deals", "The Underground", "Black Box", "Off Grid"],
        "datachips": ["ChipWorks", "DataBank", "MemStick", "InfoCore", "BitByte"]
    }
    
    shops_created = 0
    shop_ids = []
    
    print("Création de boutiques de test...")
    
    for location_id in location_ids:
        # Créer 1-3 boutiques par lieu
        num_shops = random.randint(1, 3)
        
        for _ in range(num_shops):
            shop_id = f"shop_{str(uuid.uuid4())}"
            shop_type = random.choice(shop_types)
            shop_name = random.choice(shop_names.get(shop_type, ["Generic Shop"]))
            is_legal = 1 if shop_type != "black_market" else 0
            
            description = f"Boutique de type {shop_type} vendant divers articles."
            
            try:
                cursor.execute('''
                    INSERT INTO shops (id, name, description, shop_type, location_id, is_legal, world_id, building_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL, datetime('now'))
                ''', (shop_id, shop_name, description, shop_type, location_id, is_legal, world_id))
                
                shops_created += 1
                shop_ids.append(shop_id)
                print(f"Boutique créée: {shop_name} ({shop_type})")
            except sqlite3.IntegrityError as e:
                print(f"Erreur lors de la création de la boutique: {e}")
    
    conn.commit()
    print(f"{shops_created} boutiques créées avec succès")
    return shop_ids

def create_test_items(conn, world_id, location_ids):
    """Crée des objets de test dans les tables d'objets"""
    cursor = conn.cursor()
    items_created = {
        "consumable": 0,
        "implant": 0,
        "hardware": 0,
        "weapon": 0,
        "software": 0
    }
    item_ids = {
        "consumable": [],
        "implant": [],
        "hardware": [],
        "weapon": [],
        "software": []
    }
    
    print("Création d'objets de test...")
    
    # 1. Créer des consommables
    consumable_types = ["HEALTH", "ENERGY", "FOCUS", "MEMORY", "ANTIVIRUS", "STIMPACK"]
    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    
    for i in range(20):
        item_id = f"consumable_{str(uuid.uuid4())}"
        name = f"{random.choice(['Boost', 'Ultra', 'Mega', 'Hyper', 'Quantum'])} {random.choice(consumable_types)} {random.choice(['Pill', 'Shot', 'Spray', 'Patch', 'Chip'])}"
        description = f"Un consommable qui augmente temporairement vos performances."
        cons_type = random.choice(consumable_types)
        rarity = random.choices(rarities, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]
        
        effects = {
            "duration": random.randint(10, 60),
            "strength": random.randint(1, 10),
            "stat_affected": cons_type.lower()
        }
        
        addiction_risk = random.uniform(0.0, 0.5) if cons_type in ["FOCUS", "STIMPACK"] else 0.0
        side_effects = json.dumps(["dizziness", "nausea"]) if random.random() > 0.7 else None
        price = random.randint(10, 200) * (1 + rarities.index(rarity))
        is_legal = 1 if random.random() > 0.3 else 0
        
        # Colonnes requises supplémentaires
        item_type = "CONSUMABLE"
        location_type = "SHOP"
        location_id = random.choice(location_ids)
        uses = random.randint(1, 5)
        is_available = 1
        
        try:
            cursor.execute('''
                INSERT INTO consumable_items 
                (id, name, description, consumable_type, rarity, effects, addiction_risk, side_effects, price, world_id, is_legal,
                item_type, location_type, location_id, uses, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, name, description, cons_type, rarity, json.dumps(effects), addiction_risk, side_effects, price, world_id, is_legal,
                 item_type, location_type, location_id, uses, is_available))
            
            items_created["consumable"] += 1
            item_ids["consumable"].append(item_id)
        except sqlite3.IntegrityError as e:
            print(f"Erreur lors de la création du consommable: {e}")
    
    # 2. Créer des implants
    implant_types = ["NEURAL", "OCULAR", "AUDIO", "DERMAL", "MUSCULAR", "SKELETAL", "CARDIAC", "RESPIRATORY", "IMMUNE", "INTERFACE"]
    grades = ["Standard", "Enhanced", "Premium", "Elite", "Prototype"]
    
    for i in range(20):
        item_id = f"implant_{str(uuid.uuid4())}"
        implant_type = random.choice(implant_types)
        grade = random.choices(grades, weights=[0.4, 0.3, 0.15, 0.1, 0.05], k=1)[0]
        level = random.randint(1, 10)
        
        name = f"{random.choice(['NeuraTech', 'CyberFlex', 'BioSync', 'ChromaSys'])} {implant_type.title()} MK-{level} [{grade}]"
        description = f"Un implant cybernétique qui améliore vos capacités {implant_type.lower()}."
        
        stats = {
            "durability": random.randint(1, 10),
            "effectiveness": random.randint(1, 10) * (1 + grades.index(grade) * 0.5),
            "energy_cost": random.randint(1, 5)
        }
        
        price = random.randint(500, 5000) * (1 + grades.index(grade))
        is_legal = 1 if random.random() > 0.3 else 0
        
        try:
            cursor.execute('''
                INSERT INTO implant_items 
                (id, name, description, implant_type, grade, level, stats, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, name, description, implant_type, grade, level, json.dumps(stats), price, world_id, is_legal))
            
            items_created["implant"] += 1
            item_ids["implant"].append(item_id)
        except sqlite3.IntegrityError as e:
            print(f"Erreur lors de la création de l'implant: {e}")
    
    # 3. Créer du hardware
    hardware_types = ["CPU", "RAM", "GPU", "Motherboard", "HDD", "SSD", "Network Card", "Cooling System", "Power Supply"]
    qualities = ["Normal", "Good", "Excellent", "Superior", "Legendary"]
    
    for i in range(15):
        item_id = f"hardware_{str(uuid.uuid4())}"
        hw_type = random.choice(hardware_types)
        quality = random.choices(qualities, weights=[0.4, 0.3, 0.15, 0.1, 0.05], k=1)[0]
        level = random.randint(1, 10)
        
        name = f"{random.choice(['Quantum', 'Cyber', 'Neuro', 'Hyper', 'Nano'])} {hw_type} {random.choice(['XL', 'Pro', 'Elite', 'Max'])}"
        description = f"Un composant matériel de qualité pour améliorer vos systèmes."
        
        stats = {
            "performance": random.randint(1, 10) * (1 + qualities.index(quality) * 0.3),
            "reliability": random.randint(1, 10),
            "power_consumption": random.randint(1, 10)
        }
        
        price = random.randint(100, 1000) * (1 + qualities.index(quality) * 0.5)
        is_legal = 1 if random.random() > 0.2 else 0
        
        # Colonnes requises supplémentaires
        location_type = "SHOP"
        location_id = random.choice(location_ids)
        rarity = random.choice(["Common", "Uncommon", "Rare", "Epic"])
        is_installed = 0
        is_available = 1
        
        try:
            cursor.execute('''
                INSERT INTO hardware_items 
                (id, name, description, hardware_type, type, quality, rarity, level, stats, price, world_id, is_legal,
                location_type, location_id, is_installed, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, name, description, hw_type, hw_type, quality, rarity, level, json.dumps(stats), price, world_id, is_legal,
                 location_type, location_id, is_installed, is_available))
            
            items_created["hardware"] += 1
            item_ids["hardware"].append(item_id)
        except sqlite3.IntegrityError as e:
            print(f"Erreur lors de la création du hardware: {e}")
    
    # 4. Créer des armes
    weapon_types = ["MELEE", "PISTOL", "RIFLE", "SMG", "SHOTGUN", "SNIPER", "LAUNCHER", "EXOTIC"]
    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    
    for i in range(15):
        item_id = f"weapon_{str(uuid.uuid4())}"
        weapon_type = random.choice(weapon_types)
        rarity = random.choices(rarities, weights=[0.4, 0.3, 0.15, 0.1, 0.05], k=1)[0]
        level = random.randint(1, 10)
        
        name = f"{random.choice(['Shadow', 'Cyber', 'Thunder', 'Viper'])} {random.choice(['AresArms', 'NeoForge', 'IronWolf'])} {weapon_type.title()} {random.choice(['Mark II', 'X-9', 'Delta'])}"
        description = f"Une arme puissante et précise pour vos combats urbains."
        
        stats = {
            "damage": random.randint(10, 50) * (1 + rarities.index(rarity) * 0.3),
            "accuracy": random.randint(40, 90),
            "rate_of_fire": random.randint(1, 10)
        }
        
        price = random.randint(200, 2000) * (1 + rarities.index(rarity))
        is_legal = 1 if weapon_type in ["PISTOL", "MELEE"] and random.random() > 0.5 else 0
        
        try:
            cursor.execute('''
                INSERT INTO weapon_items 
                (id, name, description, weapon_type, rarity, level, stats, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, name, description, weapon_type, rarity, level, json.dumps(stats), price, world_id, is_legal))
            
            items_created["weapon"] += 1
            item_ids["weapon"].append(item_id)
        except sqlite3.IntegrityError as e:
            print(f"Erreur lors de la création de l'arme: {e}")
    
    # 5. Créer des logiciels
    software_types = ["OS", "FIREWALL", "ANTIVIRUS", "UTILITY", "SECURITY", "CRYPTO", "VPN", "HACKING"]
    
    for i in range(15):
        item_id = f"software_{str(uuid.uuid4())}"
        sw_type = random.choice(software_types)
        level = random.randint(1, 10)
        
        name = f"{random.choice(['NeoSoft', 'ByteCorp', 'DataFlex', 'CyberTech'])} {sw_type.title()} {random.choice(['Standard', 'Pro', 'Enterprise'])} {random.choice(['1.0', '2.0', 'X'])}"
        description = f"Un logiciel puissant pour vos besoins informatiques."
        
        features = [
            random.choice(["Multi-threading", "Cloud integration", "Advanced algorithms"]),
            random.choice(["Secure encryption", "AI-powered", "Low resource usage"])
        ]
        
        price = random.randint(50, 500) * (1 + (level / 10))
        is_legal = 1 if sw_type not in ["HACKING", "CRYPTO"] or random.random() > 0.7 else 0
        
        try:
            cursor.execute('''
                INSERT INTO software_items 
                (id, name, description, software_type, level, features, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, name, description, sw_type, level, json.dumps(features), price, world_id, is_legal))
            
            items_created["software"] += 1
            item_ids["software"].append(item_id)
        except sqlite3.IntegrityError as e:
            print(f"Erreur lors de la création du logiciel: {e}")
    
    conn.commit()
    print("Objets créés:")
    for item_type, count in items_created.items():
        print(f"- {item_type}: {count}")
    
    return item_ids

def populate_shop_inventories(conn, shop_ids, item_ids):
    """Remplit les inventaires des boutiques avec les objets créés"""
    cursor = conn.cursor()
    
    inventory_items_added = 0
    print("Remplissage des inventaires des boutiques...")
    
    # Définir les types d'objets préférés pour chaque type de boutique
    shop_type_preferences = {
        "general": ["consumable", "hardware", "software"],
        "weapons": ["weapon"],
        "electronics": ["hardware", "software"],
        "medical": ["consumable", "implant"],
        "cybernetics": ["implant", "hardware"],
        "digital_services": ["software"],
        "black_market": ["weapon", "implant", "software", "consumable", "hardware"],
        "datachips": ["software", "hardware"],
        "clothing": ["consumable"],
        "food": ["consumable"]
    }
    
    # Pour chaque boutique
    for shop_id in shop_ids:
        # Récupérer le type de boutique
        cursor.execute("SELECT shop_type, is_legal FROM shops WHERE id = ?", (shop_id,))
        result = cursor.fetchone()
        if not result:
            continue
            
        shop_type, is_shop_legal = result
        
        # Déterminer le nombre d'articles à ajouter (entre 5 et 15)
        num_items = random.randint(5, 15)
        
        # Déterminer quels types d'objets cette boutique vend principalement
        preferred_item_types = shop_type_preferences.get(shop_type, ["consumable", "hardware", "software"])
        
        # Pour chaque article à ajouter
        for _ in range(num_items):
            # Déterminer le type d'article (préférence pour les types privilégiés)
            if random.random() < 0.8:  # 80% de chance de choisir un type préféré
                item_type = random.choice(preferred_item_types)
            else:
                item_type = random.choice(list(item_ids.keys()))
            
            # S'assurer qu'il y a des objets de ce type
            if not item_ids[item_type]:
                continue
                
            # Choisir un objet aléatoire de ce type
            item_id = random.choice(item_ids[item_type])
            
            # Vérifier que l'objet est légal si la boutique est légale
            if is_shop_legal:
                # Pour les boutiques légales, vérifier la légalité de l'objet
                table_name = f"{item_type}_items"
                cursor.execute(f"SELECT is_legal FROM {table_name} WHERE id = ?", (item_id,))
                result = cursor.fetchone()
                if result and result[0] == 0:  # Si l'objet est illégal
                    # 80% de chance de passer à un autre objet pour une boutique légale
                    if random.random() < 0.8:
                        continue
            
            # Déterminer la quantité (généralement 1 pour les objets rares, plus pour les consommables)
            quantity = 1
            if item_type == "consumable":
                quantity = random.randint(1, 10)
            elif item_type == "software":
                quantity = random.randint(1, 3)
                
            # Déterminer un modificateur de prix (variation entre 0.8 et 1.2)
            price_modifier = round(random.uniform(0.8, 1.2), 2)
            
            # Créer l'entrée d'inventaire
            inventory_id = f"inv_{str(uuid.uuid4())}"
            
            try:
                cursor.execute('''
                    INSERT INTO shop_inventory (id, shop_id, item_id, item_type, quantity, price_modifier, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (inventory_id, shop_id, item_id, item_type, quantity, price_modifier))
                
                inventory_items_added += 1
            except sqlite3.IntegrityError as e:
                print(f"Erreur lors de l'ajout à l'inventaire: {e}")
    
    conn.commit()
    print(f"{inventory_items_added} articles ajoutés aux inventaires des boutiques")

def main():
    print(f"Mise à jour de la base de données: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"Erreur: Le fichier de base de données {DB_PATH} n'existe pas!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Mettre à jour le schéma
        update_schema(conn)
        
        # Récupérer l'ID du premier monde
        world_id = get_first_world_id(conn)
        if not world_id:
            print("Aucun monde trouvé dans la base de données!")
            conn.close()
            return
            
        print(f"Utilisation du monde ID: {world_id}")
        
        # Récupérer des lieux aléatoires
        location_ids = get_random_locations(conn, world_id, 10)
        if not location_ids:
            print("Aucun lieu trouvé dans le monde!")
            conn.close()
            return
            
        print(f"Lieux sélectionnés: {len(location_ids)}")
        
        # Créer des boutiques de test
        shop_ids = create_test_shops(conn, world_id, location_ids)
        
        # Créer des objets de test
        item_ids = create_test_items(conn, world_id, location_ids)
        
        # Remplir les inventaires des boutiques
        populate_shop_inventories(conn, shop_ids, item_ids)
        
        conn.close()
        print("Mise à jour de la base de données terminée avec succès!")
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
