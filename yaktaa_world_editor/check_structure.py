#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier la structure de la table consumable_items
"""

import sqlite3
import json

def check_table_structure(db_path, table_name):
    """
    Vérifie et affiche la structure d'une table dans la base de données
    
    Args:
        db_path: Chemin vers le fichier de base de données
        table_name: Nom de la table à vérifier
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        
        if not cursor.fetchone():
            print(f"La table {table_name} n'existe pas dans la base de données.")
            return
        
        # Obtenir les informations sur les colonnes
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"Structure de la table {table_name}:")
        print("-" * 50)
        print("| {:3} | {:20} | {:10} | {:8} | {:8} | {:8} |".format(
            "CID", "Nom", "Type", "Not Null", "Def Val", "PK"
        ))
        print("-" * 50)
        
        for col in columns:
            cid, name, type_, notnull, dflt_value, pk = col
            print("| {:3} | {:20} | {:10} | {:8} | {:8} | {:8} |".format(
                cid, name, type_, notnull, str(dflt_value or ""), pk
            ))
        
        print("-" * 50)
        
        # Afficher le nombre d'enregistrements
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements dans la table: {count}")
        
        # Afficher un exemple d'enregistrement si la table n'est pas vide
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            record = cursor.fetchone()
            column_names = [description[0] for description in cursor.description]
            
            print("\nExemple d'enregistrement:")
            print("-" * 50)
            for i, col_name in enumerate(column_names):
                value = record[i]
                # Si la valeur semble être du JSON, tenter de l'afficher joliment
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    try:
                        value = json.dumps(json.loads(value), indent=2)
                    except:
                        pass
                print(f"{col_name}: {value}")
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "worlds.db"
    check_table_structure(db_path, "consumable_items")
