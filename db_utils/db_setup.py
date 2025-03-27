#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour analyser et configurer la base de donnu00e9es YakTaa

Ce script analyse la structure de la base de donnu00e9es YakTaa,
affiche les tables existantes et cru00e9e celles qui sont manquantes.
"""

import sqlite3
import os
import logging
import sys

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("YakTaa.DBSetup")

# Chemin vers la base de donnu00e9es
DB_PATH = os.path.expanduser("~/yaktaa_worlds.db")

# Liste des tables nu00e9cessaires avec leurs schu00e9mas
REQUIRED_TABLES = {
    # Table des mondes
    "worlds": """CREATE TABLE IF NOT EXISTS worlds (
        world_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""",
    
    # Table des lieux
    "locations": """CREATE TABLE IF NOT EXISTS locations (
        location_id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        type TEXT,
        description TEXT,
        x REAL,
        y REAL,
        population INTEGER DEFAULT 0,
        security_level INTEGER DEFAULT 1,
        FOREIGN KEY (world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
    );""",
    
    # Table des relations entre lieux (connections)
    "location_connections": """CREATE TABLE IF NOT EXISTS location_connections (
        connection_id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        location1_id TEXT NOT NULL,
        location2_id TEXT NOT NULL,
        travel_time INTEGER DEFAULT 0,
        type TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(world_id) ON DELETE CASCADE,
        FOREIGN KEY (location1_id) REFERENCES locations(location_id) ON DELETE CASCADE,
        FOREIGN KEY (location2_id) REFERENCES locations(location_id) ON DELETE CASCADE
    );""",
    
    # Table des bu00e2timents
    "buildings": """CREATE TABLE IF NOT EXISTS buildings (
        building_id TEXT PRIMARY KEY,
        location_id TEXT NOT NULL,
        name TEXT NOT NULL,
        type TEXT,
        description TEXT,
        floor_count INTEGER DEFAULT 1,
        security_level INTEGER DEFAULT 1,
        FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
    );""",
    
    # Table des PNJ
    "npcs": """CREATE TABLE IF NOT EXISTS npcs (
        npc_id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        type TEXT,
        description TEXT,
        location_id TEXT,
        building_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(world_id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
        FOREIGN KEY (building_id) REFERENCES buildings(building_id) ON DELETE SET NULL
    );""",
    
    # Table des missions
    "missions": """CREATE TABLE IF NOT EXISTS missions (
        mission_id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        reward TEXT,
        prerequisite_mission_id TEXT,
        status TEXT DEFAULT 'available',
        FOREIGN KEY (world_id) REFERENCES worlds(world_id) ON DELETE CASCADE,
        FOREIGN KEY (prerequisite_mission_id) REFERENCES missions(mission_id) ON DELETE SET NULL
    );""",
    
    # Table des objectifs de mission
    "mission_objectives": """CREATE TABLE IF NOT EXISTS mission_objectives (
        objective_id TEXT PRIMARY KEY,
        mission_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        order_num INTEGER,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (mission_id) REFERENCES missions(mission_id) ON DELETE CASCADE
    );""",
    
    # Table des boutiques
    "shops": """CREATE TABLE IF NOT EXISTS shops (
        shop_id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        shop_type TEXT,
        city_id TEXT NOT NULL,
        description TEXT,
        owner TEXT,
        markup_factor REAL DEFAULT 1.0,
        discount_factor REAL DEFAULT 0.5,
        FOREIGN KEY (world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
    );""",
    
    # Table des articles (items)
    "items": """CREATE TABLE IF NOT EXISTS items (
        item_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        value INTEGER DEFAULT 0,
        properties TEXT,  -- Stockage JSON des propriu00e9tu00e9s
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""",
    
    # Table des inventaires de boutique
    "shop_inventory": """CREATE TABLE IF NOT EXISTS shop_inventory (
        inventory_id TEXT PRIMARY KEY,
        shop_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
    );""",
    
    # Table des ru00e9seaux informatiques
    "networks": """CREATE TABLE IF NOT EXISTS networks (
        network_id TEXT PRIMARY KEY,
        building_id TEXT NOT NULL,
        name TEXT NOT NULL,
        ssid TEXT,
        type TEXT,  -- WiFi, LAN, WAN, VPN, IoT
        security_level TEXT,  -- WEP, WPA, WPA2, WPA3, ENTERPRISE
        encryption_type TEXT,
        FOREIGN KEY (building_id) REFERENCES buildings(building_id) ON DELETE CASCADE
    );"""
}


def analyze_database():
    """Analyse la base de donnu00e9es et affiche les tables existantes"""
    try:
        # Vu00e9rifier si la base de donnu00e9es existe
        if not os.path.exists(DB_PATH):
            logger.warning(f"La base de donnu00e9es n'existe pas u00e0 l'emplacement: {DB_PATH}")
            return False
        
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtenir la liste des tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Tables existantes dans la base de donnu00e9es: {', '.join(existing_tables) if existing_tables else 'Aucune'}")
        
        # Vu00e9rifier les tables manquantes
        missing_tables = [table for table in REQUIRED_TABLES.keys() if table not in existing_tables]
        
        if missing_tables:
            logger.warning(f"Tables manquantes: {', '.join(missing_tables)}")
        else:
            logger.info("Toutes les tables requises sont pru00e9sentes.")
        
        conn.close()
        return missing_tables
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la base de donnu00e9es: {str(e)}")
        return None


def create_missing_tables(missing_tables):
    """Cru00e9e les tables manquantes dans la base de donnu00e9es"""
    if not missing_tables:
        return True
    
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Cru00e9er chaque table manquante
        for table in missing_tables:
            if table in REQUIRED_TABLES:
                logger.info(f"Cru00e9ation de la table: {table}")
                cursor.execute(REQUIRED_TABLES[table])
        
        # Valider les changements
        conn.commit()
        logger.info(f"Tables cru00e9u00e9es avec succu00e8s: {', '.join(missing_tables)}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la cru00e9ation des tables: {str(e)}")
        return False


def add_test_items():
    """Ajoute des articles de test u00e0 la base de donnu00e9es"""
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vu00e9rifier si des articles existent du00e9ju00e0
        cursor.execute("SELECT COUNT(*) FROM items;")
        item_count = cursor.fetchone()[0]
        
        if item_count > 0:
            logger.info(f"Il y a du00e9ju00e0 {item_count} articles dans la base de donnu00e9es. Aucun article de test n'a u00e9tu00e9 ajoutu00e9.")
            conn.close()
            return True
        
        # Articles de test u00e0 ajouter
        test_items = [
            ("item_a1b2c3d4", "Pistolet Smart-Lock", "Arme intelligente avec systu00e8me de verrouillage biomu00e9trique.", "WEAPON", 500, '{"damage": 20, "accuracy": 85, "durability": 100, "range": 50}'),
            ("item_e5f6g7h8", "Nu00e9o-Veste Tactique", "Veste renforcu00e9e avec protection balistique avancu00e9e.", "ARMOR", 350, '{"defense": 15, "durability": 100, "mobility": 80, "tech_resist": 10}'),
            ("item_i9j0k1l2", "CyberDeck MK3", "Appareil de hacking avancu00e9 avec capacitu00e9s d'intrusion amu00e9lioru00e9es.", "HARDWARE", 1200, '{"performance": 80, "reliability": 90, "power_usage": 40, "heat": 30}'),
            ("item_m3n4o5p6", "Bio-Scanner", "Scanner portable pour analyser les signatures biologiques.", "TOOL", 250, '{"accuracy": 90, "range": 30, "battery": 100}'),
            ("item_q7r8s9t0", "Stimpack Plus", "Injection mu00e9dicale avancu00e9e pour ru00e9gu00e9nu00e9ration rapide.", "CONSUMABLE", 75, '{"healing": 50, "duration": 30, "side_effects": 10}'),
            ("item_u1v2w3x4", "Implant Optique", "Amu00e9lioration oculaire avec vision nocturne et zoom optique.", "IMPLANT", 800, '{"effectiveness": 75, "integration": 85, "side_effects": 15, "maintenance": 20}'),
            ("item_y5z6a7b8", "Du00e9crypteur NexGen", "Logiciel de du00e9cryptage de derniu00e8re gu00e9nu00e9ration.", "SOFTWARE", 650, '{"power": 70, "stealth": 85, "compatibility": 75, "complexity": 3}'),
            ("item_c9d0e1f2", "ComboKit de Crochetage", "Ensemble d'outils pour crocheter des serrures physiques et numu00e9riques.", "TOOL", 180, '{"effectiveness": 60, "durability": 90, "versatility": 80}'),
            ("item_g3h4i5j6", "Bombes IEM", "Dispositifs gu00e9nu00e9rant des impulsions u00e9lectromagnu00e9tiques.", "CONSUMABLE", 120, '{"radius": 15, "duration": 20, "power": 40}'),
            ("item_k7l8m9n0", "Implant Nu00e9uro-Ru00e9flexe", "Amu00e9lioration neuronale pour des ru00e9flexes surhumains.", "IMPLANT", 950, '{"effectiveness": 85, "integration": 70, "side_effects": 25, "maintenance": 30}')
        ]
        
        # Insu00e9rer les articles de test
        cursor.executemany("INSERT INTO items (item_id, name, description, category, value, properties) VALUES (?, ?, ?, ?, ?, ?)", test_items)
        
        # Valider les changements
        conn.commit()
        logger.info(f"{len(test_items)} articles de test ajoutu00e9s avec succu00e8s.")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des articles de test: {str(e)}")
        return False


def link_items_to_shops():
    """Associe des articles aux boutiques existantes"""
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vu00e9rifier si des associations existent du00e9ju00e0
        cursor.execute("SELECT COUNT(*) FROM shop_inventory;")
        inventory_count = cursor.fetchone()[0]
        
        if inventory_count > 0:
            logger.info(f"Il y a du00e9ju00e0 {inventory_count} associations article-boutique. Aucune association de test n'a u00e9tu00e9 ajoutu00e9e.")
            conn.close()
            return True
        
        # Ru00e9cupu00e9rer les boutiques existantes
        cursor.execute("SELECT shop_id, shop_type FROM shops;")
        shops = cursor.fetchall()
        
        if not shops:
            logger.warning("Aucune boutique trouvu00e9e dans la base de donnu00e9es.")
            conn.close()
            return False
        
        # Ru00e9cupu00e9rer les articles existants
        cursor.execute("SELECT item_id, category FROM items;")
        items = cursor.fetchall()
        
        if not items:
            logger.warning("Aucun article trouvu00e9 dans la base de donnu00e9es.")
            conn.close()
            return False
        
        # Cru00e9er des associations articles-boutiques en fonction du type
        inventory_entries = []
        import uuid
        
        for shop_id, shop_type in shops:
            # Su00e9lectionner les articles appropriu00e9s pour ce type de boutique
            suitable_items = []
            
            if shop_type == "TECH" or shop_type == "GENERAL":
                suitable_items.extend([item for item in items if item[1] in ("HARDWARE", "SOFTWARE", "TOOL")])
            
            if shop_type == "WEAPONS" or shop_type == "BLACK_MARKET":
                suitable_items.extend([item for item in items if item[1] in ("WEAPON", "ARMOR")])
            
            if shop_type == "CLOTHING":
                suitable_items.extend([item for item in items if item[1] in ("CLOTHING", "ARMOR")])
            
            if shop_type == "IMPLANTS" or shop_type == "SERVICES":
                suitable_items.extend([item for item in items if item[1] in ("IMPLANT", "CONSUMABLE")])
            
            if shop_type == "DRUGS" or shop_type == "FOOD":
                suitable_items.extend([item for item in items if item[1] in ("CONSUMABLE")])
            
            if shop_type == "HACKING":
                suitable_items.extend([item for item in items if item[1] in ("SOFTWARE", "HARDWARE")])
            
            # Si aucun article appropriu00e9 n'a u00e9tu00e9 trouvu00e9, ajouter quelques articles gu00e9nu00e9riques
            if not suitable_items and items:
                suitable_items = items[:min(5, len(items))]
            
            # Ajouter entre 3 et 8 articles u00e0 l'inventaire de cette boutique
            import random
            num_items = min(len(suitable_items), random.randint(3, 8))
            selected_items = random.sample(suitable_items, num_items) if num_items > 0 else []
            
            for item_id, _ in selected_items:
                inventory_id = f"inv_{uuid.uuid4().hex[:8]}"
                quantity = random.randint(1, 10)
                inventory_entries.append((inventory_id, shop_id, item_id, quantity))
        
        # Insu00e9rer les associations dans la table d'inventaire
        if inventory_entries:
            cursor.executemany("INSERT INTO shop_inventory (inventory_id, shop_id, item_id, quantity) VALUES (?, ?, ?, ?)", inventory_entries)
            conn.commit()
            logger.info(f"{len(inventory_entries)} associations article-boutique ajoutu00e9es avec succu00e8s.")
        else:
            logger.warning("Aucune association article-boutique n'a pu u00eatre cru00e9u00e9e.")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'association des articles aux boutiques: {str(e)}")
        return False


def main():
    """Fonction principale du script"""
    logger.info("=== Analyse et configuration de la base de donnu00e9es YakTaa ===")
    
    # Analyser la base de donnu00e9es
    missing_tables = analyze_database()
    
    if missing_tables is None:
        logger.error("Impossible d'analyser la base de donnu00e9es. Arru00eat du script.")
        return 1
    
    # Cru00e9er les tables manquantes
    if missing_tables:
        logger.info("Cru00e9ation des tables manquantes...")
        if not create_missing_tables(missing_tables):
            logger.error("Impossible de cru00e9er les tables manquantes. Arru00eat du script.")
            return 1
        logger.info("Tables manquantes cru00e9u00e9es avec succu00e8s.")
    
    # Ajouter des articles de test si la table 'items' vient d'u00eatre cru00e9u00e9e
    if "items" in missing_tables:
        logger.info("Ajout d'articles de test...")
        if not add_test_items():
            logger.warning("Impossible d'ajouter des articles de test.")
    
    # Associer des articles aux boutiques si la table 'shop_inventory' vient d'u00eatre cru00e9u00e9e
    if "shop_inventory" in missing_tables:
        logger.info("Association des articles aux boutiques...")
        if not link_items_to_shops():
            logger.warning("Impossible d'associer des articles aux boutiques.")
    
    logger.info("=== Configuration de la base de donnu00e9es terminu00e9e ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
