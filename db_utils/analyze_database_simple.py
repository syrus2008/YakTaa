import sqlite3
import json
import os

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Analyse approfondie de la base de donnees: {db_path}")
print(f"Le fichier existe: {os.path.exists(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n=== TABLES EXISTANTES ===")
    for table in tables:
        table_name = table[0]
        print(f"\nTABLE: {table_name}")
        
        # Structure de la table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("  Colonnes:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_value, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if not_null:
                constraints.append("NOT NULL")
            if default_value is not None:
                constraints.append(f"DEFAULT {default_value}")
                
            constraints_str = ", ".join(constraints)
            print(f"   - {col_name} ({col_type}) {constraints_str}")
        
        # Clés étrangères
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print("  Cles etrangeres:")
            for fk in foreign_keys:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"   - {from_col} -> {table}({to_col}) [ON DELETE {on_delete}]")
        
        # Nombre d'entrées
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Nombre d'entrees: {count}")
    
    # Tables potentiellement manquantes basées sur le concept du jeu
    print("\n=== ANALYSE DES TABLES MANQUANTES ===")
    
    tables_to_check = {
        # Système de joueur et progression
        "players": "Table pour stocker les informations des joueurs",
        "player_stats": "Table pour les statistiques des joueurs (competences, attributs)",
        "player_inventory": "Table pour l'inventaire des joueurs (objets possedes)",
        "skills": "Table pour definir les differentes competences disponibles",
        "achievements": "Table pour les succes et accomplissements",
        
        # Éléments supplémentaires du monde
        "factions": "Table pour les differentes factions du monde",
        "vendors": "Table pour les vendeurs et leurs inventaires",
        "shops": "Table pour les magasins et leurs produits",
        
        # Éléments de jeu avancés
        "crafting_recipes": "Table pour les recettes de fabrication d'objets",
        "quests": "Table pour les quetes secondaires",
        "dialogue_trees": "Table pour les arbres de dialogue avec les PNJ",
        "events": "Table pour les evenements scenarises ou aleatoires",
        
        # Éléments de gameplay spécifiques
        "hacking_tools": "Table pour les outils de hacking disponibles",
        "software": "Table pour les logiciels que le joueur peut installer",
        "vehicles": "Table pour les vehicules que le joueur peut utiliser",
        "fast_travel_points": "Table pour les points de voyage rapide",
        
        # Système de réputation et relations
        "reputation": "Table pour la reputation du joueur aupres des factions",
        "relationships": "Table pour les relations entre personnages",
        
        # Système de communication
        "messages": "Table pour les messages recus ou envoyes",
        "chat_logs": "Table pour l'historique des conversations",
        
        # Éléments liés au hacking
        "vulnerabilities": "Table pour les vulnerabilites des systemes",
        "exploits": "Table pour les exploits disponibles"
    }
    
    existing_tables = [t[0] for t in tables]
    
    for table_name, description in tables_to_check.items():
        if table_name in existing_tables:
            print(f"[OK] {table_name} - Existe deja")
        else:
            print(f"[MISSING] {table_name} - Manquant - {description}")
    
    conn.close()
    print("\nAnalyse terminee!")
    
except Exception as e:
    print(f"Erreur lors de l'analyse de la base de donnees: {str(e)}")
