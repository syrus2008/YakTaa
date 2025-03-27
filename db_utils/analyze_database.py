import sqlite3
import json
import os
import sys
from typing import List, Dict, Any, Optional, Tuple

db_path = 'c:\\Users\\thibaut\\Desktop\\glata\\yaktaa_world_editor\\worlds.db'

print(f"Analyse approfondie de la base de données: {db_path}")
print(f"Le fichier existe: {os.path.exists(db_path)}")

def analyze_table_data(cursor, table_name: str, limit: int = 3):
    """Analyze and display sample data from a table"""
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  [!] Aucune donnée trouvée dans la table {table_name}")
            return
        
        # Obtenez les noms de colonnes
        column_names = [description[0] for description in cursor.description]
        
        print(f"  [*] Échantillon de données ({len(rows)} entrées):")
        for row in rows:
            print(f"   [ITEM] Entrée:")
            for idx, value in enumerate(row):
                col_name = column_names[idx]
                # Format JSON pour une meilleure lisibilité
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        json_value = json.loads(value)
                        value = f"{json.dumps(json_value, indent=2, ensure_ascii=False)}"
                    except:
                        pass
                print(f"     - {col_name}: {value}")
            print()
    except Exception as e:
        print(f"  [ERROR] Erreur lors de l'analyse des données de {table_name}: {str(e)}")

def check_expected_columns(cursor, table_name: str, expected_columns: List[str]) -> Tuple[bool, List[str]]:
    """Check if a table has all the expected columns"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    existing_columns = [col[1] for col in columns]
    
    missing_columns = [col for col in expected_columns if col not in existing_columns]
    return len(missing_columns) == 0, missing_columns

def analyze_specific_tables(cursor):
    """Analyze shop-related tables with more details"""
    # Tables spécifiques liées aux boutiques et aux objets
    shop_tables = {
        "shops": [
            "id", "name", "description", "shop_type", "is_legal", "world_id", 
            "building_id", "location_id"
        ],
        "shop_inventories": [
            "id", "shop_id", "item_id", "item_type", "quantity", "discount_percent",
            "is_special", "world_id"
        ],
        "hardware_items": [
            "id", "name", "description", "hardware_type", "quality", "level", 
            "price", "is_legal", "stats", "world_id", "building_id", "character_id", "device_id"
        ],
        "consumable_items": [
            "id", "name", "description", "item_type", "rarity", "duration", 
            "price", "is_legal", "effects", "world_id", "building_id", "character_id", "device_id"
        ],
        "software_items": [
            "id", "name", "description", "software_type", "version", "license_type", 
            "price", "is_legal", "capabilities", "world_id", "device_id", "file_id"
        ]
    }
    
    print("\n=== ANALYSE DÉTAILLÉE DES TABLES DE BOUTIQUES ET OBJETS ===")
    
    # Vérifiez si chaque table existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [table[0] for table in cursor.fetchall()]
    
    for table_name, expected_columns in shop_tables.items():
        if table_name in existing_tables:
            print(f"\n[OK] TABLE PRÉSENTE: {table_name}")
            
            # Vérifiez si toutes les colonnes attendues sont présentes
            all_columns_present, missing_columns = check_expected_columns(cursor, table_name, expected_columns)
            
            if all_columns_present:
                print(f"  [OK] Toutes les colonnes attendues sont présentes.")
            else:
                print(f"  [!] Colonnes manquantes: {', '.join(missing_columns)}")
            
            # Comptez les entrées
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  [*] Nombre d'entrées: {count}")
            
            # Obtenez un échantillon de données
            if count > 0:
                analyze_table_data(cursor, table_name)
        else:
            print(f"\n[MISSING] TABLE MANQUANTE: {table_name}")
            print(f"  Colonnes attendues: {', '.join(expected_columns)}")

def check_shop_integration(cursor):
    """Vérifier les liens entre boutiques et inventaires"""
    print("\n=== ANALYSE DE L'INTÉGRATION DES BOUTIQUES ET OBJETS ===")
    
    try:
        # Vérifier les liens entre boutiques et inventaires
        cursor.execute("""
            SELECT s.id, s.name, s.shop_type, COUNT(si.id)
            FROM shops s
            LEFT JOIN shop_inventories si ON s.id = si.shop_id
            GROUP BY s.id
        """)
        shop_inventory_counts = cursor.fetchall()
        
        if shop_inventory_counts:
            print("\n[*] Répartition des objets dans les boutiques:")
            for shop_id, shop_name, shop_type, item_count in shop_inventory_counts:
                print(f"  - {shop_name} ({shop_type}): {item_count} objets")
        else:
            print("[!] Aucune boutique avec inventaire trouvée")
        
        # Analyser les types d'objets dans les inventaires
        cursor.execute("""
            SELECT item_type, COUNT(*) as count
            FROM shop_inventories
            GROUP BY item_type
            ORDER BY count DESC
        """)
        item_type_counts = cursor.fetchall()
        
        if item_type_counts:
            print("\n[*] Répartition des types d'objets dans les inventaires:")
            for item_type, count in item_type_counts:
                print(f"  - {item_type}: {count} objets")
        else:
            print("[!] Aucun objet dans les inventaires")
            
        # Vérifier les objets illégaux vs légaux
        for table in ["consumable_items", "hardware_items", "software_items"]:
            try:
                cursor.execute(f"""
                    SELECT is_legal, COUNT(*) as count
                    FROM {table}
                    GROUP BY is_legal
                """)
                legal_counts = cursor.fetchall()
                
                if legal_counts:
                    print(f"\n[*] Distribution légal/illégal dans {table}:")
                    for is_legal, count in legal_counts:
                        status = "Légal" if is_legal else "Illégal"
                        print(f"  - {status}: {count} objets")
            except:
                print(f"[!] Impossible d'analyser la légalité pour {table}")
                
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'analyse de l'intégration: {str(e)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n=== TABLES EXISTANTES ===")
    for table in tables:
        table_name = table[0]
        print(f"\n[TABLE] {table_name}")
        
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
            print("  Clés étrangères:")
            for fk in foreign_keys:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"   - {from_col} -> {table}({to_col}) [ON DELETE {on_delete}]")
        
        # Nombre d'entrées
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Nombre d'entrées: {count}")
    
    # Analyse spécifique des tables de boutiques
    analyze_specific_tables(cursor)
    
    # Vérifier l'intégration des boutiques et objets
    check_shop_integration(cursor)
    
    # Tables potentiellement manquantes basées sur le concept du jeu
    print("\n=== ANALYSE DES TABLES MANQUANTES ===")
    
    tables_to_check = {
        # Système de joueur et progression
        "players": "Table pour stocker les informations des joueurs",
        "player_stats": "Table pour les statistiques des joueurs (compétences, attributs)",
        "player_inventory": "Table pour l'inventaire des joueurs (objets possédés)",
        "skills": "Table pour définir les différentes compétences disponibles",
        "achievements": "Table pour les succès et accomplissements",
        
        # Éléments supplémentaires du monde
        "factions": "Table pour les différentes factions du monde",
        "vendors": "Table pour les vendeurs et leurs inventaires",
        "shops": "Table pour les magasins et leurs produits",
        "shop_inventories": "Table pour les inventaires des magasins",
        
        # Types d'objets
        "hardware_items": "Table pour les objets matériels (CPU, RAM, etc.)",
        "consumable_items": "Table pour les objets consommables (stims, médikits, etc.)",
        "software_items": "Table pour les logiciels (OS, sécurité, hacking, etc.)",
        
        # Éléments de jeu avancés
        "crafting_recipes": "Table pour les recettes de fabrication d'objets",
        "quests": "Table pour les quêtes secondaires",
        "dialogue_trees": "Table pour les arbres de dialogue avec les PNJ",
        "events": "Table pour les événements scénarisés ou aléatoires",
        
        # Éléments de gameplay spécifiques
        "hacking_tools": "Table pour les outils de hacking disponibles",
        "software": "Table pour les logiciels que le joueur peut installer",
        "vehicles": "Table pour les véhicules que le joueur peut utiliser",
        "fast_travel_points": "Table pour les points de voyage rapide",
        
        # Système de réputation et relations
        "reputation": "Table pour la réputation du joueur auprès des factions",
        "relationships": "Table pour les relations entre personnages",
        
        # Système de communication
        "messages": "Table pour les messages reçus ou envoyés",
        "chat_logs": "Table pour l'historique des conversations",
        
        # Éléments liés au hacking
        "vulnerabilities": "Table pour les vulnérabilités des systèmes",
        "exploits": "Table pour les exploits disponibles"
    }
    
    existing_tables = [t[0] for t in tables]
    
    for table_name, description in tables_to_check.items():
        if table_name in existing_tables:
            print(f"[OK] {table_name} - Existe déjà")
        else:
            print(f"[MISSING] {table_name} - Manquant - {description}")
    
    conn.close()
    print("\nAnalyse terminée!")
    
except Exception as e:
    print(f"Erreur lors de l'analyse de la base de données: {str(e)}")
