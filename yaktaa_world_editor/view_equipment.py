#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour visualiser les équipements dans la base de données
"""

import sqlite3
import os
from database import get_database

def view_equipment():
    """Affiche les équipements présents dans la base de données"""
    db = get_database()
    
    try:
        cursor = db.conn.cursor()
        
        # Récupérer les mondes
        cursor.execute("SELECT id, name FROM worlds")
        worlds = cursor.fetchall()
        
        for world in worlds:
            world_id = world["id"]
            world_name = world["name"]
            
            print(f"\n=== Équipements du monde: {world_name} ({world_id}) ===\n")
            
            # Récupérer les équipements par type
            for equipment_type in ["WEAPON", "ARMOR", "IMPLANT"]:
                cursor.execute("""
                SELECT id, name, equipment_type, subtype, rarity, price, damage, defense, 
                       special_abilities, is_cybernetic
                FROM equipment 
                WHERE world_id = ? AND equipment_type = ?
                """, (world_id, equipment_type))
                
                items = cursor.fetchall()
                
                if items:
                    print(f"-- {equipment_type}s ({len(items)}) --")
                    
                    for item in items:
                        print(f"• {item['name']}")
                        print(f"  Type: {item['subtype'] if item['subtype'] else 'N/A'}, Rareté: {item['rarity'] if item['rarity'] else 'N/A'}")
                        print(f"  Prix: {item['price']}")
                        
                        if equipment_type == "WEAPON":
                            print(f"  Dégâts: {item['damage']}")
                        elif equipment_type == "ARMOR":
                            print(f"  Défense: {item['defense']}")
                            
                        if item['special_abilities']:
                            print(f"  Capacités spéciales: {item['special_abilities']}")
                            
                        if item['is_cybernetic']:
                            print(f"  [Cybernétique]")
                            
                        print("")
                else:
                    print(f"-- Aucun {equipment_type} trouvé --\n")
    
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    finally:
        db.conn.close()

if __name__ == "__main__":
    view_equipment()
