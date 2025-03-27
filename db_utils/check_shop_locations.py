#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vu00e9rifier les emplacements des boutiques dans la base de donnu00e9es YakTaa
"""

import sqlite3
import os

# Chemin vers la base de donnu00e9es de l'u00e9diteur
DB_PATH = os.path.expanduser("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")

def check_shop_locations():
    print(f"\n=== Vu00e9rification des boutiques dans {DB_PATH} ===")
    
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vu00e9rifier la structure de la table shops
        cursor.execute("PRAGMA table_info(shops)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes de la table shops: {', '.join(columns)}")
        
        # Du00e9terminer le nom de la colonne ID (id ou shop_id)
        id_column = "shop_id" if "shop_id" in columns else "id"
        print(f"Colonne d'ID des boutiques: {id_column}")
        
        # Obtenir les boutiques et leurs emplacements
        cursor.execute(f"SELECT {id_column}, name, shop_type, location_id FROM shops ORDER BY location_id, name")
        shops = cursor.fetchall()
        
        if shops:
            print(f"\n{len(shops)} boutiques trouvu00e9es:")
            unique_locations = set()
            for shop in shops:
                shop_id, name, shop_type, location_id = shop
                unique_locations.add(location_id if location_id else "<aucun>")
                print(f"  - {name} (ID: {shop_id}, Type: {shop_type}, Emplacement: {location_id if location_id else '<aucun>'}")
            
            print(f"\nEmplacements uniques: {', '.join(unique_locations)}")
        else:
            print("Aucune boutique trouvu00e9e dans la base de donnu00e9es")
        
        # Vu00e9rifier si la table locations existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='locations'")
        if cursor.fetchone():
            # Obtenir les locations disponibles
            cursor.execute("SELECT location_id, name FROM locations")
            locations = cursor.fetchall()
            print(f"\n{len(locations)} emplacements disponibles:")
            for location in locations:
                location_id, name = location
                print(f"  - {name} (ID: {location_id})")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la vu00e9rification des boutiques: {str(e)}")

# Exu00e9cuter la vu00e9rification
check_shop_locations()
