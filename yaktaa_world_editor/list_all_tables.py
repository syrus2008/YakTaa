#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour lister toutes les tables dans la base de données
"""

import sqlite3

def list_all_tables(db_path):
    """
    Liste toutes les tables dans la base de données SQLite
    
    Args:
        db_path: Chemin vers le fichier de base de données
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les noms de toutes les tables
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        
        print(f"Tables trouvées dans la base de données {db_path}:")
        print("-" * 50)
        
        for i, table in enumerate(tables):
            print(f"{i+1}. {table[0]}")
        
        print(f"\nNombre total de tables: {len(tables)}")
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "worlds.db"
    list_all_tables(db_path)
