import sqlite3
import json
import os

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Ajout des tables essentielles à la base de données: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Table des factions (importantes pour l'ambiance cyberpunk et les relations)
    print("Création de la table 'factions'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS factions (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        faction_type TEXT NOT NULL,  -- corporation, gang, gouvernement, hackers, etc.
        headquarters_location_id TEXT,
        influence_level INTEGER DEFAULT 5,  -- de 1 à 10
        specialties TEXT,  -- domaines d'expertise de la faction (JSON)
        relations TEXT,  -- relations avec d'autres factions (JSON)
        notable_members TEXT,  -- personnages importants (JSON)
        resources TEXT,  -- ressources de la faction (JSON)
        is_hostile_to_player INTEGER DEFAULT 0,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (headquarters_location_id) REFERENCES locations(id) ON DELETE SET NULL
    )
    ''')
    
    # 2. Table des logiciels (essentiels pour l'aspect hacking)
    print("Création de la table 'software'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS software (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        software_type TEXT NOT NULL,  -- OS, malware, utilitaire, cryptage, etc.
        version TEXT,
        size INTEGER,  -- en Mo
        memory_usage INTEGER,  -- en Mo
        cpu_usage INTEGER,  -- en %
        compatibility TEXT,  -- systèmes compatibles (JSON)
        features TEXT,  -- fonctionnalités (JSON)
        license_type TEXT,  -- libre, commercial, militaire, illégal
        price INTEGER DEFAULT 0,
        rarity TEXT,  -- common, uncommon, rare, epic, legendary
        effects TEXT,  -- effets sur les systèmes (JSON)
        location_type TEXT,  -- device, building, character, shop, loot
        location_id TEXT,
        is_malicious INTEGER DEFAULT 0,
        is_available INTEGER DEFAULT 1,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    # 3. Table des vulnérabilités (essentielles pour les systèmes de hacking)
    print("Création de la table 'vulnerabilities'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        vuln_type TEXT NOT NULL,  -- buffer overflow, SQL injection, XSS, etc.
        affected_systems TEXT,  -- types de systèmes affectés (JSON)
        difficulty INTEGER,  -- difficulté d'exploitation (1-10)
        discovery_date TEXT,
        is_zero_day INTEGER DEFAULT 0,
        exploit_available INTEGER DEFAULT 1,
        patch_available INTEGER DEFAULT 0,
        cve_id TEXT,  -- identifiant fictif de vulnérabilité
        target_type TEXT,  -- device, network
        target_id TEXT,
        exploit_effect TEXT,  -- effets de l'exploitation (JSON)
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    # 4. Table des exploits (outils pour exploiter les vulnérabilités)
    print("Création de la table 'exploits'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exploits (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        exploit_type TEXT NOT NULL,
        target_vulnerability TEXT,  -- id de la vulnérabilité ciblée
        code_quality INTEGER,  -- qualité du code (1-10)
        success_rate INTEGER,  -- en %
        detection_risk INTEGER,  -- risque de détection (1-10)
        origin_faction_id TEXT,  -- faction qui a créé l'exploit
        price INTEGER DEFAULT 0,
        rarity TEXT,  -- common, uncommon, rare, epic, legendary
        effects TEXT,  -- effets de l'exploitation (JSON)
        location_type TEXT,  -- device, building, character, shop, loot
        location_id TEXT,
        is_available INTEGER DEFAULT 1,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (target_vulnerability) REFERENCES vulnerabilities(id) ON DELETE SET NULL,
        FOREIGN KEY (origin_faction_id) REFERENCES factions(id) ON DELETE SET NULL
    )
    ''')
    
    # 5. Table des magasins/vendeurs
    print("Création de la table 'shops'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shops (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        location_id TEXT,
        owner_id TEXT,  -- personnage propriétaire
        faction_id TEXT,  -- faction propriétaire
        shop_type TEXT NOT NULL,  -- hardware, software, black market, etc.
        reputation INTEGER DEFAULT 5,  -- réputation (1-10)
        price_modifier REAL DEFAULT 1.0,  -- modificateur de prix
        special_items TEXT,  -- objets spéciaux disponibles (JSON)
        services TEXT,  -- services proposés (JSON)
        inventory_refresh_rate INTEGER DEFAULT 24,  -- en heures
        is_legal INTEGER DEFAULT 1,
        requires_reputation INTEGER DEFAULT 0,
        required_reputation_level INTEGER DEFAULT 0,
        open_hours TEXT,  -- heures d'ouverture (JSON)
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
        FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL,
        FOREIGN KEY (faction_id) REFERENCES factions(id) ON DELETE SET NULL
    )
    ''')
    
    # 6. Table des inventaires de magasins
    print("Création de la table 'shop_inventory'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shop_inventory (
        id TEXT PRIMARY KEY,
        shop_id TEXT NOT NULL,
        item_type TEXT NOT NULL,  -- hardware, software, consumable
        item_id TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        price_modifier REAL DEFAULT 1.0,
        is_featured INTEGER DEFAULT 0,
        is_limited_time INTEGER DEFAULT 0,
        expiry_date TEXT,
        metadata TEXT,
        FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
    )
    ''')
    
    # 7. Table des joueurs (pour sauvegarder les informations de partie)
    print("Création de la table 'players'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        character_name TEXT NOT NULL,
        current_world_id TEXT,
        current_location_id TEXT,
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        hacking_skill INTEGER DEFAULT 1,
        engineering_skill INTEGER DEFAULT 1,
        charisma_skill INTEGER DEFAULT 1,
        stealth_skill INTEGER DEFAULT 1,
        combat_skill INTEGER DEFAULT 1,
        credits INTEGER DEFAULT 1000,
        reputation TEXT,  -- réputation auprès des factions (JSON)
        completed_missions TEXT,  -- missions terminées (JSON)
        known_locations TEXT,  -- lieux découverts (JSON)
        inventory TEXT,  -- inventaire (JSON)
        equipped_items TEXT,  -- objets équipés (JSON)
        active_effects TEXT,  -- effets actifs (JSON)
        game_time TEXT,  -- temps de jeu
        last_saved TEXT,  -- dernière sauvegarde
        metadata TEXT,
        FOREIGN KEY (current_world_id) REFERENCES worlds(id) ON DELETE SET NULL,
        FOREIGN KEY (current_location_id) REFERENCES locations(id) ON DELETE SET NULL
    )
    ''')
    
    # 8. Table des hacking tools (outils spécifiques pour le hacking)
    print("Création de la table 'hacking_tools'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hacking_tools (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        tool_type TEXT NOT NULL,  -- Scanner, Déchiffreur, Injecteur, etc.
        quality TEXT NOT NULL,  -- Broken, Poor, Standard, High-End, Military-Grade, Prototype
        rarity TEXT NOT NULL,  -- Common, Uncommon, Rare, Epic, Legendary
        level INTEGER NOT NULL,
        capabilities TEXT,  -- capacités de l'outil (JSON)
        effectiveness INTEGER,  -- efficacité (1-10)
        detection_risk INTEGER,  -- risque de détection (1-10)
        cooldown INTEGER,  -- temps de recharge en secondes
        power_consumption INTEGER,  -- consommation d'énergie
        target_systems TEXT,  -- systèmes ciblés (JSON)
        compatible_software TEXT,  -- logiciels compatibles (JSON)
        price INTEGER DEFAULT 0,
        location_type TEXT,  -- device, building, character, shop, loot
        location_id TEXT,
        is_available INTEGER DEFAULT 1,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    print("Tables essentielles ajoutées avec succès!")
    
    # Vérifier que les tables ont bien été créées
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nTables dans la base de données après ajout:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"Erreur lors de l'ajout des tables: {str(e)}")
