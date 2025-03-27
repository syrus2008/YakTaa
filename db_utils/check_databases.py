#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour comparer les bases de données YakTaa
"""

import sqlite3
import os

# Chemins vers les bases de données
GAME_DB_PATH = os.path.expanduser("~/yaktaa_worlds.db")
EDITOR_DB_PATH = os.path.expanduser("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")

def check_db_tables(db_path, db_name):
    """Vérifie les tables et leurs données dans une base de données"""
    print(f"\n=== Vérification de la base de données {db_name} à {db_path} ===")
    
    try:
        # Vérifier si la base de données existe
        if not os.path.exists(db_path):
            print(f"La base de données {db_name} n'existe pas à l'emplacement: {db_path}")
            return
        
        # Se connecter à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtenir la liste des tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tables dans {db_name}: {', '.join(existing_tables) if existing_tables else 'Aucune'}")
        
        # Vérifier le contenu de certaines tables importantes
        if 'shops' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM shops;")
            shop_count = cursor.fetchone()[0]
            cursor.execute("SELECT shop_id, name, shop_type FROM shops LIMIT 5;")
            shops = cursor.fetchall()
            print(f"\nBoutiques dans {db_name}: {shop_count} au total")
            print("Exemples de boutiques:")
            for shop in shops:
                print(f"  - {shop[1]} (ID: {shop[0]}, Type: {shop[2]})")
        
        if 'items' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM items;")
            item_count = cursor.fetchone()[0]
            cursor.execute("SELECT item_id, name, category FROM items LIMIT 5;")
            items = cursor.fetchall()
            print(f"\nArticles dans {db_name}: {item_count} au total")
            print("Exemples d'articles:")
            for item in items:
                print(f"  - {item[1]} (ID: {item[0]}, Catégorie: {item[2]})")
        
        if 'shop_inventory' in existing_tables:
            # Vérifier si la colonne 'price' existe
            cursor.execute("PRAGMA table_info(shop_inventory)")
            columns = [col[1] for col in cursor.fetchall()]
            has_price = 'price' in columns
            
            cursor.execute("SELECT COUNT(*) FROM shop_inventory;")
            inventory_count = cursor.fetchone()[0]
            
            print(f"\nInventaire des boutiques dans {db_name}: {inventory_count} articles au total")
            print(f"La colonne 'price' existe: {'Oui' if has_price else 'Non'}")
            
            if inventory_count > 0 and has_price:
                cursor.execute("""
                    SELECT s.name, i.name, si.quantity, si.price
                    FROM shop_inventory si
                    JOIN shops s ON si.shop_id = s.shop_id
                    JOIN items i ON si.item_id = i.item_id
                    LIMIT 5
                """)
                inventory = cursor.fetchall()
                print("Exemples d'articles en boutique:")
                for inv in inventory:
                    print(f"  - {inv[0]} vend {inv[1]} (Qté: {inv[2]}, Prix: {inv[3]})")
            elif inventory_count > 0:
                cursor.execute("""
                    SELECT s.name, i.name, si.quantity
                    FROM shop_inventory si
                    JOIN shops s ON si.shop_id = s.shop_id
                    JOIN items i ON si.item_id = i.item_id
                    LIMIT 5
                """)
                inventory = cursor.fetchall()
                print("Exemples d'articles en boutique:")
                for inv in inventory:
                    print(f"  - {inv[0]} vend {inv[1]} (Qté: {inv[2]})")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la vérification de {db_name}: {str(e)}")

# Vérifier les deux bases de données
check_db_tables(GAME_DB_PATH, "YakTaa Game")
check_db_tables(EDITOR_DB_PATH, "YakTaa World Editor")

print("\n=== Résumé ===")
print("Si les deux bases de données contiennent des données différentes, ")
print("cela confirme qu'elles sont bien distinctes.")
print("La base de données GAME est celle utilisée par le jeu principal.")
print("La base de données EDITOR est celle utilisée par l'éditeur de monde.")
print("\nPour un fonctionnement optimal, il faudrait synchroniser les données entre les deux,")
print("ou configurer l'application YakTaa pour utiliser la base de données de l'éditeur.")
