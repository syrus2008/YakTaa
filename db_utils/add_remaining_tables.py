import sqlite3
import json
import os

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Ajout des tables restantes à la base de données: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Table des compétences (skills) plus détaillée
    print("Création de la table 'skills'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        skill_type TEXT NOT NULL,  -- hacking, combat, social, technique, etc.
        base_cost INTEGER,  -- coût en points de compétence
        prerequisites TEXT,  -- prérequis (JSON)
        effects TEXT,  -- effets (JSON)
        max_level INTEGER DEFAULT 5,
        unlocks TEXT,  -- éléments débloqués (JSON)
        icon_path TEXT,
        skill_tree_position TEXT,  -- position dans l'arbre de compétences (JSON)
        metadata TEXT
    )
    ''')
    
    # 2. Table des véhicules
    print("Création de la table 'vehicles'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        vehicle_type TEXT NOT NULL,  -- car, bike, drone, aircraft, etc.
        brand TEXT,
        model TEXT,
        year INTEGER,
        speed INTEGER,
        acceleration INTEGER,
        handling INTEGER,
        durability INTEGER,
        fuel_capacity INTEGER,
        fuel_consumption REAL,
        features TEXT,  -- fonctionnalités (JSON)
        modifications TEXT,  -- modifications (JSON)
        security_systems TEXT,  -- systèmes de sécurité (JSON)
        price INTEGER DEFAULT 0,
        location_id TEXT,
        owner_id TEXT,
        is_available INTEGER DEFAULT 1,
        requires_license INTEGER DEFAULT 1,
        license_type TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
        FOREIGN KEY (owner_id) REFERENCES characters(id) ON DELETE SET NULL
    )
    ''')
    
    # 3. Table des messages (communication dans le jeu)
    print("Création de la table 'messages'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        sender_id TEXT,  -- peut être NULL pour les messages système
        receiver_id TEXT NOT NULL,
        subject TEXT,
        content TEXT NOT NULL,
        attachment TEXT,  -- pièces jointes (JSON)
        is_encrypted INTEGER DEFAULT 0,
        encryption_type TEXT,
        encryption_key TEXT,
        is_read INTEGER DEFAULT 0,
        is_marked_important INTEGER DEFAULT 0,
        timestamp TEXT,
        expiry_date TEXT,  -- date d'expiration
        thread_id TEXT,  -- pour les conversations
        contains_mission INTEGER DEFAULT 0,
        related_mission_id TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES characters(id) ON DELETE SET NULL,
        FOREIGN KEY (receiver_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (related_mission_id) REFERENCES missions(id) ON DELETE SET NULL
    )
    ''')
    
    # 4. Table des arbres de dialogue
    print("Création de la table 'dialogue_trees'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dialogue_trees (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        character_id TEXT NOT NULL,
        name TEXT NOT NULL,
        context TEXT,  -- situation contextuelle
        nodes TEXT NOT NULL,  -- nœuds de dialogue (JSON)
        options TEXT NOT NULL,  -- options de réponse (JSON)
        conditions TEXT,  -- conditions d'accès aux dialogues (JSON)
        consequences TEXT,  -- conséquences des choix (JSON)
        triggers TEXT,  -- déclencheurs d'événements (JSON)
        is_mission_related INTEGER DEFAULT 0,
        related_mission_id TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
        FOREIGN KEY (related_mission_id) REFERENCES missions(id) ON DELETE SET NULL
    )
    ''')
    
    # 5. Table des événements (pour les événements dynamiques du monde)
    print("Création de la table 'events'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        event_type TEXT NOT NULL,  -- ambiant, scénarisé, aléatoire, etc.
        location_id TEXT,  -- peut être NULL pour les événements globaux
        trigger_condition TEXT,  -- condition de déclenchement
        trigger_chance INTEGER,  -- probabilité de déclenchement (0-100)
        duration INTEGER,  -- durée en secondes, 0 pour instantané
        cooldown INTEGER,  -- temps de recharge en secondes
        effects TEXT,  -- effets sur le monde (JSON)
        involved_factions TEXT,  -- factions impliquées (JSON)
        rewards TEXT,  -- récompenses (JSON)
        is_repeatable INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        start_date TEXT,
        end_date TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
    )
    ''')
    
    # 6. Table des recettes de fabrication
    print("Création de la table 'crafting_recipes'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crafting_recipes (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        recipe_type TEXT NOT NULL,  -- hardware, software, consumable, etc.
        ingredients TEXT NOT NULL,  -- ingrédients nécessaires (JSON)
        tools_required TEXT,  -- outils nécessaires (JSON)
        skills_required TEXT,  -- compétences nécessaires (JSON)
        result_item_type TEXT NOT NULL,  -- type d'objet produit
        result_item_properties TEXT NOT NULL,  -- propriétés de l'objet produit (JSON)
        crafting_time INTEGER,  -- temps de fabrication en secondes
        crafting_difficulty INTEGER,  -- difficulté (1-10)
        success_chance INTEGER DEFAULT 100,  -- probabilité de succès (0-100)
        failure_effects TEXT,  -- effets en cas d'échec (JSON)
        is_learnable INTEGER DEFAULT 1,
        learning_source TEXT,  -- source d'apprentissage (vendeur, mission, etc.)
        price INTEGER DEFAULT 0,  -- prix d'achat de la recette
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
    ''')
    
    # 7. Table des points de réputation
    print("Création de la table 'reputation'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reputation (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL,
        faction_id TEXT NOT NULL,
        level INTEGER DEFAULT 0,  -- de -100 à 100
        title TEXT,  -- titre obtenu auprès de la faction
        benefits TEXT,  -- avantages débloqués (JSON)
        penalties TEXT,  -- pénalités (JSON)
        earned_through TEXT,  -- comment la réputation a été gagnée
        last_updated TEXT,
        metadata TEXT,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (faction_id) REFERENCES factions(id) ON DELETE CASCADE
    )
    ''')
    
    # 8. Table des succès/achievements
    print("Création de la table 'achievements'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        requirements TEXT NOT NULL,  -- conditions d'obtention (JSON)
        reward_type TEXT,  -- type de récompense
        reward_value TEXT,  -- valeur de la récompense
        category TEXT,  -- catégorie (exploration, combat, hacking, etc.)
        difficulty TEXT,  -- difficulté (easy, medium, hard, etc.)
        icon_path TEXT,
        is_hidden INTEGER DEFAULT 0,
        is_special INTEGER DEFAULT 0,
        metadata TEXT
    )
    ''')
    
    # 9. Table des points de voyage rapide
    print("Création de la table 'fast_travel_points'...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fast_travel_points (
        id TEXT PRIMARY KEY,
        world_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        location_id TEXT NOT NULL,
        travel_type TEXT NOT NULL,  -- subway, train, airport, etc.
        destinations TEXT,  -- destinations possibles (JSON)
        unlock_condition TEXT,  -- condition de déverrouillage
        is_unlocked INTEGER DEFAULT 0,
        cost_modifier REAL DEFAULT 1.0,
        travel_time_modifier REAL DEFAULT 1.0,
        icon_path TEXT,
        metadata TEXT,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    print("Tables restantes ajoutées avec succès!")
    
    # Vérifier que les tables ont bien été créées
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\nListe complète des tables dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
    
    print("\nBase de données complète et prête pour le jeu YakTaa!")
    
except Exception as e:
    print(f"Erreur lors de l'ajout des tables: {str(e)}")
