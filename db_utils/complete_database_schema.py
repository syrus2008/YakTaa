import sqlite3
import os
import json
import random
import uuid
from datetime import datetime, timedelta

# Chemin vers la base de données
DB_PATH = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

def get_first_world_id(conn):
    """Récupère l'ID du premier monde dans la base de données"""
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM worlds LIMIT 1')
    result = cursor.fetchone()
    return result[0] if result else None

def get_random_locations(conn, world_id, count=10):
    """Récupère des lieux aléatoires du monde"""
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM locations WHERE world_id = ? ORDER BY RANDOM() LIMIT ?', (world_id, count))
    return [row[0] for row in cursor.fetchall()]

def get_random_characters(conn, world_id, count=10):
    """Récupère des personnages aléatoires du monde"""
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM characters WHERE world_id = ? ORDER BY RANDOM() LIMIT ?', (world_id, count))
    return [row[0] for row in cursor.fetchall()]

def add_missing_tables(conn):
    """Ajoute les tables manquantes à la base de données"""
    cursor = conn.cursor()
    
    # 1. Table player_stats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_stats (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL,
        world_id TEXT NOT NULL,
        strength INTEGER DEFAULT 5,
        agility INTEGER DEFAULT 5,
        intelligence INTEGER DEFAULT 5, 
        charisma INTEGER DEFAULT 5,
        hacking_skill INTEGER DEFAULT 1,
        combat_skill INTEGER DEFAULT 1,
        stealth_skill INTEGER DEFAULT 1,
        persuasion_skill INTEGER DEFAULT 1,
        engineering_skill INTEGER DEFAULT 1,
        medical_skill INTEGER DEFAULT 1,
        cybernetics_skill INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        skill_points INTEGER DEFAULT 0,
        attribute_points INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    print("Table player_stats créée ou existante")

    # 2. Table player_inventory
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_inventory (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL, 
        world_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        item_type TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        is_equipped INTEGER DEFAULT 0,
        slot TEXT,
        acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        custom_name TEXT,
        custom_description TEXT,
        is_favorite INTEGER DEFAULT 0,
        is_quest_item INTEGER DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    print("Table player_inventory créée ou existante")

    # 3. Table vendors
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendors (
        id TEXT PRIMARY KEY,
        character_id TEXT NOT NULL,
        world_id TEXT NOT NULL,
        shop_id TEXT,
        vendor_type TEXT NOT NULL,
        specialization TEXT,
        reputation_threshold INTEGER DEFAULT 0,
        price_modifier REAL DEFAULT 1.0,
        inventory_refresh_time INTEGER DEFAULT 86400,
        last_refresh TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        haggle_difficulty INTEGER DEFAULT 5,
        buy_modifier REAL DEFAULT 0.5,
        sell_modifier REAL DEFAULT 1.5,
        special_offers TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE SET NULL
    )
    ''')
    print("Table vendors créée ou existante")

    # 4. Table quests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quests (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        quest_type TEXT NOT NULL,
        level_requirement INTEGER DEFAULT 1,
        reputation_requirement INTEGER DEFAULT 0,
        faction_id TEXT,
        giver_id TEXT,
        rewards TEXT,
        is_repeatable INTEGER DEFAULT 0,
        cooldown_hours INTEGER DEFAULT 0,
        prerequisites TEXT,
        next_quest_id TEXT,
        is_active INTEGER DEFAULT 1,
        is_hidden INTEGER DEFAULT 0,
        time_limit INTEGER,
        start_location_id TEXT,
        end_location_id TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (faction_id) REFERENCES factions(id) ON DELETE SET NULL,
        FOREIGN KEY (giver_id) REFERENCES characters(id) ON DELETE SET NULL,
        FOREIGN KEY (next_quest_id) REFERENCES quests(id) ON DELETE SET NULL,
        FOREIGN KEY (start_location_id) REFERENCES locations(id) ON DELETE SET NULL,
        FOREIGN KEY (end_location_id) REFERENCES locations(id) ON DELETE SET NULL
    )
    ''')
    print("Table quests créée ou existante")

    # 5. Table relationships
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS relationships (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        character1_id TEXT NOT NULL,
        character2_id TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        strength INTEGER DEFAULT 0,
        description TEXT,
        is_hidden INTEGER DEFAULT 0,
        last_interaction TIMESTAMP,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (character1_id) REFERENCES characters(id) ON DELETE CASCADE,
        FOREIGN KEY (character2_id) REFERENCES characters(id) ON DELETE CASCADE,
        UNIQUE(character1_id, character2_id)
    )
    ''')
    print("Table relationships créée ou existante")

    # 6. Table chat_logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        player_id TEXT NOT NULL,
        character_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        message TEXT NOT NULL,
        is_player INTEGER DEFAULT 1,
        message_type TEXT DEFAULT 'text',
        is_encrypted INTEGER DEFAULT 0,
        encryption_level INTEGER DEFAULT 0,
        is_mission_related INTEGER DEFAULT 0,
        mission_id TEXT,
        location_id TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE SET NULL,
        FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE SET NULL,
        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
    )
    ''')
    print("Table chat_logs créée ou existante")
    
    # 7. Table player_quests (pour suivre la progression)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_quests (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL,
        quest_id TEXT NOT NULL,
        world_id TEXT NOT NULL,
        status TEXT DEFAULT 'not_started',
        progress INTEGER DEFAULT 0,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completion_time TIMESTAMP,
        current_objective_id TEXT,
        failed INTEGER DEFAULT 0,
        fail_reason TEXT,
        rewards_claimed INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        UNIQUE(player_id, quest_id)
    )
    ''')
    print("Table player_quests créée ou existante")

    conn.commit()

def create_test_player_stats(conn, world_id):
    """Crée des statistiques de joueur de test"""
    cursor = conn.cursor()
    
    # Vérifier si la table players existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
    if not cursor.fetchone():
        print("La table players n'existe pas, création de la table")
        # Créer la table players si elle n'existe pas - structure adaptée au jeu YakTaa
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
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
            reputation INTEGER DEFAULT 0,
            completed_missions TEXT,
            known_locations TEXT,
            inventory TEXT,
            equipped_items TEXT,
            active_effects TEXT,
            game_time INTEGER DEFAULT 0,
            last_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        ''')
        print("Table players créée")
    
    # Vérifier la structure de la table players existante
    cursor.execute("PRAGMA table_info(players)")
    columns_info = cursor.fetchall()
    columns = [column[1] for column in columns_info]
    not_null_columns = [column[1] for column in columns_info if column[3] == 1]  # Colonnes avec contrainte NOT NULL
    
    print(f"Colonnes existantes dans la table players: {columns}")
    print(f"Colonnes avec contrainte NOT NULL: {not_null_columns}")
    
    # Créer un joueur de test s'il n'en existe pas
    cursor.execute("SELECT id FROM players LIMIT 1")
    player = cursor.fetchone()
    
    if not player:
        player_id = str(uuid.uuid4())
        
        # Construire la requête d'insertion en fonction des colonnes existantes
        insert_columns = []
        insert_values = []
        insert_placeholders = []
        
        # Ajouter les champs requis dans l'ordre approprié
        column_values = {
            "id": player_id,
            "username": "testplayer",
            "character_name": "NeoHacker",
            "current_world_id": world_id,
            "current_location_id": None,  # Sera défini plus tard si nécessaire
            "level": 1,
            "experience": 0,
            "hacking_skill": 3,
            "engineering_skill": 2,
            "charisma_skill": 2,
            "stealth_skill": 2,
            "combat_skill": 1,
            "credits": 2000,
            "reputation": 0,
            "completed_missions": "[]",
            "known_locations": "[]",
            "inventory": "[]",
            "equipped_items": "{}",
            "active_effects": "[]",
            "game_time": 0,
            "metadata": "{}"
        }
        
        # S'assurer que toutes les colonnes NOT NULL sont incluses
        for col in not_null_columns:
            if col not in column_values and col in columns:
                print(f"ATTENTION: Colonne NOT NULL '{col}' manquante dans les valeurs")
                # Assigner une valeur par défaut selon le type
                column_values[col] = ""  # Chaîne vide par défaut
        
        # Générer la requête d'insertion
        for col in columns:
            if col in column_values:
                insert_columns.append(col)
                insert_values.append(column_values[col])
                insert_placeholders.append("?")
        
        # Vérifier si des colonnes obligatoires manquent
        for col in not_null_columns:
            if col not in insert_columns:
                print(f"ERREUR: Impossible d'insérer - colonne obligatoire '{col}' manquante")
                return None
                
        # Construire et exécuter la requête dynamiquement
        if insert_columns:
            query = f'''
            INSERT INTO players ({', '.join(insert_columns)})
            VALUES ({', '.join(insert_placeholders)})
            '''
            try:
                cursor.execute(query, insert_values)
                print("Joueur de test créé")
            except sqlite3.Error as e:
                print(f"Erreur lors de la création du joueur: {e}")
                print(f"Colonnes: {insert_columns}")
                print(f"Valeurs: {insert_values}")
                return None
        else:
            print("Impossible de créer un joueur avec la structure de table actuelle")
            return None
    else:
        player_id = player[0]
    
    # Créer des statistiques pour le joueur
    cursor.execute("SELECT id FROM player_stats WHERE player_id = ?", (player_id,))
    if not cursor.fetchone():
        stats_id = str(uuid.uuid4())
        cursor.execute('''
        INSERT INTO player_stats (
            id, player_id, world_id, strength, agility, intelligence, charisma,
            hacking_skill, combat_skill, stealth_skill, persuasion_skill,
            engineering_skill, medical_skill, cybernetics_skill, experience, level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats_id, player_id, world_id, 
            random.randint(3, 8), random.randint(3, 8), random.randint(3, 8), random.randint(3, 8),
            random.randint(1, 5), random.randint(1, 5), random.randint(1, 5), random.randint(1, 5),
            random.randint(1, 5), random.randint(1, 5), random.randint(1, 5),
            random.randint(0, 1000), random.randint(1, 5)
        ))
        print("Statistiques du joueur créées")
    
    return player_id

def create_test_player_inventory(conn, player_id, world_id):
    """Crée des objets d'inventaire pour le joueur de test"""
    cursor = conn.cursor()
    items_added = 0
    
    # Récupérer des objets de différents types
    item_types = ["consumable_items", "hardware_items", "implant_items", "weapon_items", "software_items"]
    item_count = 0
    
    for item_type in item_types:
        type_name = item_type[:-6]  # Enlever "_items"
        cursor.execute(f"SELECT id FROM {item_type} WHERE world_id = ? LIMIT 5", (world_id,))
        items = cursor.fetchall()
        
        for item in items:
            item_id = item[0]
            inventory_id = str(uuid.uuid4())
            quantity = random.randint(1, 3)
            is_equipped = 1 if random.random() > 0.7 and type_name != "consumable" else 0
            slot = None
            if is_equipped:
                if type_name == "hardware":
                    slot = random.choice(["CPU", "RAM", "GPU", "HDD"])
                elif type_name == "implant":
                    slot = random.choice(["HEAD", "EYES", "ARMS", "LEGS", "TORSO"])
                elif type_name == "weapon":
                    slot = "WEAPON"
            
            is_favorite = 1 if random.random() > 0.8 else 0
            
            cursor.execute('''
            INSERT INTO player_inventory 
            (id, player_id, world_id, item_id, item_type, quantity, is_equipped, slot, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (inventory_id, player_id, world_id, item_id, type_name, quantity, is_equipped, slot, is_favorite))
            
            items_added += 1
            
    print(f"{items_added} objets ajoutés à l'inventaire du joueur")
    return items_added

def create_test_vendors(conn, world_id):
    """Crée des vendeurs de test liés aux personnages et aux boutiques"""
    cursor = conn.cursor()
    vendors_created = 0
    
    # Récupérer des personnages qui pourraient être des vendeurs
    cursor.execute('''
    SELECT c.id, s.id 
    FROM characters c
    LEFT JOIN shops s ON s.location_id = c.location_id
    WHERE c.world_id = ? AND c.is_vendor = 1
    LIMIT 15
    ''', (world_id,))
    characters = cursor.fetchall()
    
    if not characters:
        # Si aucun personnage n'est déjà marqué comme vendeur, on en choisit aléatoirement
        cursor.execute('''
        SELECT c.id, s.id 
        FROM characters c
        LEFT JOIN shops s ON s.location_id = c.location_id
        WHERE c.world_id = ?
        ORDER BY RANDOM()
        LIMIT 15
        ''', (world_id,))
        characters = cursor.fetchall()
        
        # Marquer ces personnages comme vendeurs
        for char_id, _ in characters:
            cursor.execute('''
            UPDATE characters SET is_vendor = 1 WHERE id = ?
            ''', (char_id,))
    
    vendor_types = ["GENERAL", "WEAPONS", "IMPLANTS", "ELECTRONICS", "FOOD", "BLACK_MARKET", "CLOTHING", "MEDICAL"]
    specializations = ["Discount", "Premium", "Rare", "Exclusive", "Illegal", "Custom", "Used", "New"]
    
    for char_id, shop_id in characters:
        vendor_id = str(uuid.uuid4())
        vendor_type = random.choice(vendor_types)
        specialization = random.choice(specializations)
        reputation_threshold = random.randint(0, 30)
        price_modifier = round(random.uniform(0.8, 1.5), 2)
        haggle_difficulty = random.randint(1, 10)
        buy_modifier = round(random.uniform(0.3, 0.7), 2)
        sell_modifier = round(random.uniform(1.2, 2.0), 2)
        
        special_offers = json.dumps({
            "discount_day": random.choice(["Monday", "Wednesday", "Friday", "Sunday"]),
            "discount_amount": random.randint(10, 30),
            "special_item_chance": random.randint(5, 20)
        })
        
        cursor.execute('''
        INSERT INTO vendors 
        (id, character_id, world_id, shop_id, vendor_type, specialization, 
         reputation_threshold, price_modifier, haggle_difficulty, buy_modifier, sell_modifier, special_offers)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vendor_id, char_id, world_id, shop_id, vendor_type, specialization,
            reputation_threshold, price_modifier, haggle_difficulty, buy_modifier, sell_modifier, special_offers
        ))
        
        vendors_created += 1
    
    print(f"{vendors_created} vendeurs créés")
    return vendors_created

def create_test_quests(conn, world_id):
    """Crée des quêtes secondaires de test"""
    cursor = conn.cursor()
    quests_created = 0
    
    # Récupérer des personnages pour être donneurs de quêtes
    cursor.execute('''
    SELECT id FROM characters 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 10
    ''', (world_id,))
    characters = [row[0] for row in cursor.fetchall()]
    
    # Récupérer des lieux pour les quêtes
    cursor.execute('''
    SELECT id FROM locations 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 20
    ''', (world_id,))
    locations = [row[0] for row in cursor.fetchall()]
    
    # Récupérer des factions
    cursor.execute('''
    SELECT id FROM factions 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 5
    ''', (world_id,))
    factions_result = cursor.fetchall()
    factions = [row[0] for row in factions_result] if factions_result else []
    
    quest_types = ["FETCH", "DELIVERY", "ASSASSINATION", "ESCORT", "HACK", "PROTECT", "RESCUE", "SABOTAGE", "STEAL", "INVESTIGATE"]
    
    # Créer des quêtes
    for i in range(15):
        quest_id = str(uuid.uuid4())
        title = f"{random.choice(['La', 'Une', 'Mission:', 'Opération'])} {random.choice(['mystérieuse', 'dangereuse', 'secrète', 'lucrative', 'impossible', 'urgente'])} {random.choice(['livraison', 'rencontre', 'récupération', 'infiltration', 'évasion', 'extraction'])}"
        description = f"Une quête secondaire qui implique diverses actions dans l'univers cyberpunk."
        quest_type = random.choice(quest_types)
        level_requirement = random.randint(1, 10)
        reputation_requirement = random.randint(0, 50)
        
        faction_id = random.choice(factions) if factions and random.random() > 0.5 else None
        giver_id = random.choice(characters)
        
        rewards = json.dumps({
            "credits": random.randint(100, 2000),
            "experience": random.randint(50, 500),
            "items": random.randint(0, 3),
            "reputation": random.randint(5, 25)
        })
        
        is_repeatable = 1 if random.random() > 0.7 else 0
        cooldown_hours = random.randint(12, 72) if is_repeatable else 0
        
        prerequisites = json.dumps({
            "quests_completed": [],
            "min_level": level_requirement,
            "min_reputation": reputation_requirement,
            "skills_required": {
                random.choice(["hacking", "combat", "stealth", "persuasion"]): random.randint(1, 5)
            }
        })
        
        is_hidden = 1 if random.random() > 0.8 else 0
        time_limit = random.randint(1, 24) * 3600 if random.random() > 0.7 else None
        
        start_location_id = random.choice(locations)
        end_location_id = random.choice(locations)
        
        cursor.execute('''
        INSERT INTO quests 
        (id, world_id, title, description, quest_type, level_requirement, reputation_requirement,
         faction_id, giver_id, rewards, is_repeatable, cooldown_hours, prerequisites,
         is_hidden, time_limit, start_location_id, end_location_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quest_id, world_id, title, description, quest_type, level_requirement, reputation_requirement,
            faction_id, giver_id, rewards, is_repeatable, cooldown_hours, prerequisites,
            is_hidden, time_limit, start_location_id, end_location_id
        ))
        
        quests_created += 1
    
    print(f"{quests_created} quêtes secondaires créées")
    return quests_created

def create_test_relationships(conn, world_id):
    """Crée des relations entre personnages"""
    cursor = conn.cursor()
    relationships_created = 0
    
    # Récupérer des personnages
    cursor.execute('''
    SELECT id FROM characters 
    WHERE world_id = ? 
    LIMIT 30
    ''', (world_id,))
    characters = [row[0] for row in cursor.fetchall()]
    
    if len(characters) < 5:
        print("Pas assez de personnages pour créer des relations significatives")
        return 0
    
    relationship_types = ["FRIEND", "ENEMY", "ALLY", "RIVAL", "FAMILY", "LOVER", "BUSINESS", "MENTOR", "SUBORDINATE"]
    
    # Créer des relations entre personnages
    for i in range(min(40, len(characters) * 2)):
        # Sélectionner deux personnages différents
        char1, char2 = random.sample(characters, 2)
        
        # Vérifier si une relation existe déjà
        cursor.execute('''
        SELECT id FROM relationships 
        WHERE (character1_id = ? AND character2_id = ?) OR (character1_id = ? AND character2_id = ?)
        ''', (char1, char2, char2, char1))
        
        if cursor.fetchone():
            continue
        
        relationship_id = str(uuid.uuid4())
        relationship_type = random.choice(relationship_types)
        strength = random.randint(-100, 100)
        
        description = f"Une relation de type {relationship_type.lower()} avec une force de {strength}"
        is_hidden = 1 if random.random() > 0.8 else 0
        
        # Date aléatoire dans les 30 derniers jours
        last_interaction = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO relationships 
        (id, world_id, character1_id, character2_id, relationship_type, strength, 
         description, is_hidden, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            relationship_id, world_id, char1, char2, relationship_type, strength, 
            description, is_hidden, last_interaction
        ))
        
        relationships_created += 1
    
    print(f"{relationships_created} relations entre personnages créées")
    return relationships_created

def create_test_chat_logs(conn, player_id, world_id):
    """Crée des logs de conversation de test"""
    cursor = conn.cursor()
    logs_created = 0
    
    # Récupérer des personnages pour les conversations
    cursor.execute('''
    SELECT id FROM characters 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 10
    ''', (world_id,))
    characters = [row[0] for row in cursor.fetchall()]
    
    # Récupérer des missions
    cursor.execute('''
    SELECT id FROM missions 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 5
    ''', (world_id,))
    missions = [row[0] for row in cursor.fetchall()]
    
    # Récupérer des lieux
    cursor.execute('''
    SELECT id FROM locations 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 5
    ''', (world_id,))
    locations = [row[0] for row in cursor.fetchall()]
    
    message_types = ["text", "audio", "video", "data"]
    
    # Créer des discussions pour chaque personnage
    for character_id in characters:
        # Nombre aléatoire de messages dans la conversation
        for i in range(random.randint(3, 10)):
            log_id = str(uuid.uuid4())
            
            # 50% chance que ce soit un message du joueur ou du PNJ
            is_player = 1 if random.random() > 0.5 else 0
            
            if is_player:
                message = random.choice([
                    "Qu'est-ce que tu sais sur cette mission?",
                    "J'ai besoin d'informations sur ce secteur.",
                    "Combien me coûterait cet équipement?",
                    "Tu as entendu des rumeurs récemment?",
                    "Je cherche un travail bien payé.",
                    "Parle-moi de toi.",
                    "Tu connais quelqu'un qui pourrait m'aider?",
                    "As-tu des contacts dans le milieu?",
                    "Je peux te faire confiance?",
                    "J'ai quelque chose qui pourrait t'intéresser."
                ])
            else:
                message = random.choice([
                    "Je ne parle pas aux étrangers, dégage.",
                    "Peut-être que je sais quelque chose... pour le bon prix.",
                    "Tu ferais mieux de faire attention dans ce quartier.",
                    "J'ai des informations qui pourraient t'intéresser.",
                    "Je connais quelqu'un qui cherche un hacker de talent.",
                    "Les corporations ont renforcé la sécurité récemment.",
                    "Il y a une opportunité dans le secteur sud, si tu es intéressé.",
                    "Tu n'as pas l'air d'être flic, alors je vais te faire confiance.",
                    "J'ai des implants de qualité à vendre, pas trop chers.",
                    "Les gangs sont en guerre, c'est pas le moment de traîner ici."
                ])
            
            message_type = random.choice(message_types)
            is_encrypted = 1 if random.random() > 0.8 else 0
            encryption_level = random.randint(1, 5) if is_encrypted else 0
            
            is_mission_related = 1 if missions and random.random() > 0.7 else 0
            mission_id = random.choice(missions) if is_mission_related and missions else None
            
            location_id = random.choice(locations) if locations else None
            
            # Date aléatoire dans les 7 derniers jours
            timestamp = (datetime.now() - timedelta(days=random.randint(0, 7), 
                                                  hours=random.randint(0, 23), 
                                                  minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO chat_logs 
            (id, world_id, player_id, character_id, timestamp, message, is_player, 
             message_type, is_encrypted, encryption_level, is_mission_related, mission_id, location_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_id, world_id, player_id, character_id, timestamp, message, is_player, 
                message_type, is_encrypted, encryption_level, is_mission_related, mission_id, location_id
            ))
            
            logs_created += 1
    
    print(f"{logs_created} logs de conversation créés")
    return logs_created

def create_test_player_quests(conn, player_id, world_id):
    """Crée des associations entre le joueur et des quêtes"""
    cursor = conn.cursor()
    player_quests_created = 0
    
    # Récupérer des quêtes
    cursor.execute('''
    SELECT id FROM quests 
    WHERE world_id = ? 
    ORDER BY RANDOM() 
    LIMIT 10
    ''', (world_id,))
    quests_result = cursor.fetchall()
    
    if not quests_result:
        # Récupérer des missions si pas de quêtes
        cursor.execute('''
        SELECT id FROM missions 
        WHERE world_id = ? 
        ORDER BY RANDOM() 
        LIMIT 10
        ''', (world_id,))
        quests_result = cursor.fetchall()
    
    quests = [row[0] for row in quests_result]
    
    if not quests:
        print("Aucune quête ou mission disponible")
        return 0
    
    statuses = ["not_started", "in_progress", "completed", "failed", "abandoned"]
    
    for quest_id in quests:
        player_quest_id = str(uuid.uuid4())
        
        # Distribuer les statuts de manière réaliste
        status_weights = [0.2, 0.4, 0.25, 0.1, 0.05]  # Pondérations pour chaque statut
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        
        progress = 0
        if status == "in_progress":
            progress = random.randint(10, 90)
        elif status == "completed":
            progress = 100
        
        start_time = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        
        completion_time = None
        if status in ["completed", "failed", "abandoned"]:
            # Complétion entre la date de début et maintenant
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            days_since_start = (datetime.now() - start_dt).days
            completion_time = (start_dt + timedelta(days=random.randint(1, max(1, days_since_start)))).strftime('%Y-%m-%d %H:%M:%S')
        
        failed = 1 if status == "failed" else 0
        fail_reason = random.choice([
            "Temps écoulé", 
            "Cible éliminée", 
            "Mission compromise", 
            "Objectif inaccessible"
        ]) if failed else None
        
        rewards_claimed = 1 if status == "completed" else 0
        
        cursor.execute('''
        INSERT INTO player_quests 
        (id, player_id, quest_id, world_id, status, progress, start_time, 
         completion_time, failed, fail_reason, rewards_claimed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_quest_id, player_id, quest_id, world_id, status, progress, start_time, 
            completion_time, failed, fail_reason, rewards_claimed
        ))
        
        player_quests_created += 1
    
    print(f"{player_quests_created} associations joueur-quêtes créées")
    return player_quests_created

def main():
    print(f"Complétion de la base de données: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"Erreur: Le fichier de base de données {DB_PATH} n'existe pas!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Récupérer l'ID du premier monde
        world_id = get_first_world_id(conn)
        if not world_id:
            print("Aucun monde trouvé dans la base de données!")
            conn.close()
            return
            
        print(f"Utilisation du monde ID: {world_id}")
        
        # Ajouter les tables manquantes
        add_missing_tables(conn)
        
        # Créer des données de test pour chaque table
        print("\nCréation de données de test pour les nouvelles tables...")
        
        # Création du joueur et de ses statistiques
        player_id = create_test_player_stats(conn, world_id)
        
        # Création de l'inventaire du joueur
        create_test_player_inventory(conn, player_id, world_id)
        
        # Création des vendeurs
        create_test_vendors(conn, world_id)
        
        # Création des quêtes secondaires
        create_test_quests(conn, world_id)
        
        # Création des relations entre personnages
        create_test_relationships(conn, world_id)
        
        # Création des logs de conversation
        create_test_chat_logs(conn, player_id, world_id)
        
        # Création des associations joueur-quêtes
        create_test_player_quests(conn, player_id, world_id)
        
        conn.commit()
        print("\nSchéma de base de données complété avec succès!")
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
