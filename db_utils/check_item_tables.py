#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vu00e9rifier les tables d'objets dans la base de donnu00e9es YakTaa
"""

import sqlite3
import os
import json

# Chemin vers la base de donnu00e9es de l'u00e9diteur
DB_PATH = os.path.expanduser("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")

def check_item_tables():
    print(f"\n=== Vu00e9rification des tables d'objets dans {DB_PATH} ===")
    
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Pour avoir accu00e8s aux colonnes par leur nom
        cursor = conn.cursor()
        
        # 1. Vu00e9rifions les tables d'objets existantes
        item_tables = [
            "hardware_items", "software_items", "consumable_items", 
            "weapon_items", "implant_items", "items"
        ]
        
        # Vu00e9rifier les tables qui existent effectivement
        print("\n1. Tables d'objets existantes:")
        for table in item_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                # Afficher la structure de la table
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"\n   Table '{table}' trouvue, avec colonnes:")
                for col in columns:
                    print(f"     - {col['name']} ({col['type']})")
                
                # Afficher quelques exemples d'objets
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                items = cursor.fetchall()
                if items:
                    print(f"   Exemples d'objets dans '{table}' ({len(items)} monru00e9s):")
                    for item in items:
                        item_dict = dict(item)
                        if 'id' in item_dict:
                            print(f"     - {item_dict.get('name', 'Sans nom')} (ID: {item_dict['id']})")
                        elif 'item_id' in item_dict:
                            print(f"     - {item_dict.get('name', 'Sans nom')} (ID: {item_dict['item_id']})")
                        else:
                            print(f"     - {item_dict}")
            else:
                print(f"   Table '{table}' non trouvue dans la base de donnu00e9es")
        
        # 2. Vu00e9rifions la table shop_inventory
        print("\n2. Examen de la table d'inventaire des boutiques:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='shop_inventory' OR name='shop_inventories')")
        inventory_table = cursor.fetchone()
        if inventory_table:
            inventory_table_name = inventory_table[0]
            print(f"   Table d'inventaire trouvue: '{inventory_table_name}'")
            
            # Afficher la structure
            cursor.execute(f"PRAGMA table_info({inventory_table_name})")
            columns = cursor.fetchall()
            print(f"   Structure de '{inventory_table_name}':")
            for col in columns:
                print(f"     - {col['name']} ({col['type']})")
            
            # Afficher quelques exemples
            cursor.execute(f"SELECT * FROM {inventory_table_name} LIMIT 5")
            inventories = cursor.fetchall()
            if inventories:
                print(f"   Exemples d'inventaires dans '{inventory_table_name}' ({len(inventories)} monru00e9s):")
                for inv in inventories:
                    inv_dict = dict(inv)
                    print(f"     - Shop ID: {inv_dict.get('shop_id', 'N/A')}, Item ID: {inv_dict.get('item_id', 'N/A')}, Prix: {inv_dict.get('price', 'N/A')}")
            
            # Essayer de joindre avec les tables d'objets pour voir comment ils sont liés
            for item_table in [t for t in item_tables if t != "items"]:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (item_table,))
                if cursor.fetchone():
                    try:
                        cursor.execute(f"""
                            SELECT si.shop_id, si.item_id, i.name, si.price 
                            FROM {inventory_table_name} si 
                            JOIN {item_table} i ON si.item_id = i.id 
                            LIMIT 2
                        """)
                        joined_items = cursor.fetchall()
                        if joined_items:
                            print(f"   Jointure ru00e9ussie entre {inventory_table_name} et {item_table}:")
                            for ji in joined_items:
                                ji_dict = dict(ji)
                                print(f"     - {ji_dict.get('name', 'Sans nom')} (Shop: {ji_dict['shop_id']}, Prix: {ji_dict['price']})")
                    except sqlite3.Error as e:
                        print(f"   Erreur lors de la jointure entre {inventory_table_name} et {item_table}: {str(e)}")
        else:
            print("   Aucune table d'inventaire de boutique trouvu00e9e")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la vu00e9rification des tables d'objets: {str(e)}")

# Exu00e9cuter la vu00e9rification
check_item_tables()
