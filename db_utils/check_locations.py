#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vu00e9rifier les emplacements dans la base de donnu00e9es YakTaa
"""

import sqlite3
import os
import json

# Chemin vers la base de donnu00e9es de l'u00e9diteur
DB_PATH = os.path.expanduser("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db")

def check_locations():
    print(f"\n=== Vu00e9rification des emplacements dans {DB_PATH} ===")
    
    try:
        # Se connecter u00e0 la base de donnu00e9es
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Pour avoir accu00e8s aux colonnes par leur nom
        cursor = conn.cursor()
        
        # Vu00e9rifier les tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables dans la base de donnu00e9es: {', '.join(tables)}")
        
        # Vu00e9rifier s'il y a une table 'locations'
        if 'locations' in tables:
            print("\n1. Table 'locations' trouvu00e9e")
            # Vu00e9rifier la structure
            cursor.execute("PRAGMA table_info(locations)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"   Colonnes: {', '.join(columns)}")
            
            # Ru00e9cupu00e9rer tous les emplacements
            cursor.execute("SELECT * FROM locations")
            locations = cursor.fetchall()
            print(f"   Nombre d'emplacements: {len(locations)}")
            print("   Emplacements:")
            for loc in locations:
                loc_dict = dict(loc)
                # Afficher les propriétés importantes
                print(f"     - {loc_dict.get('name', 'Inconnu')} (ID: {loc_dict.get('location_id', 'N/A')})")
                if 'properties' in loc_dict and loc_dict['properties']:
                    try:
                        props = json.loads(loc_dict['properties']) if isinstance(loc_dict['properties'], str) else loc_dict['properties']
                        print(f"       Type: {props.get('type', 'Inconnu')}, Sous-type: {props.get('subtype', 'Inconnu')}")
                    except json.JSONDecodeError:
                        print(f"       Propriétés (non-JSON): {loc_dict['properties']}")
        
        # Vérifier s'il y a une table 'world_locations'
        if 'world_locations' in tables:
            print("\n2. Table 'world_locations' trouvée")
            # Vérifier la structure
            cursor.execute("PRAGMA table_info(world_locations)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"   Colonnes: {', '.join(columns)}")
            
            # Récupérer les liens entre mondes et emplacements
            cursor.execute("SELECT * FROM world_locations LIMIT 10")
            world_locs = cursor.fetchall()
            print(f"   Nombre de liens monde-emplacement (limité à 10): {len(world_locs)}")
            for wl in world_locs:
                wl_dict = dict(wl)
                print(f"     - Monde: {wl_dict.get('world_id', 'N/A')}, Emplacement: {wl_dict.get('location_id', 'N/A')}")

        # Vérifier les mondes disponibles
        if 'worlds' in tables:
            print("\n3. Table 'worlds' trouvée")
            cursor.execute("SELECT id, name FROM worlds")
            worlds = cursor.fetchall()
            print(f"   Nombre de mondes: {len(worlds)}")
            for world in worlds:
                print(f"     - {world['name']} (ID: {world['id']})")
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la vu00e9rification des emplacements: {str(e)}")

# Exu00e9cuter la vu00e9rification
check_locations()
