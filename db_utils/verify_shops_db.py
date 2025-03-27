#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de vérification des boutiques et des emplacements dans la base de données YakTaa.
Ce script analyse la structure des tables shops et locations pour identifier les problèmes
de chargement des boutiques dans les villes.
"""

import sqlite3
import os
import logging
import sys
from pathlib import Path
import json

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("YakTaa.ShopValidator")


def find_database():
    """Recherche la base de données dans différents emplacements possibles"""
    possible_paths = [
        # Chemin absolu vers la base de données de l'éditeur (PRIORITAIRE)
        Path("C:/Users/thibaut/Desktop/glata/yaktaa_world_editor/worlds.db"),
        
        # Chemin relatif dans le dossier de l'éditeur
        Path("../yaktaa_world_editor/worlds.db"),
        Path("../yaktaa_world_editor/yaktaa_worlds.db"),
        
        # Chemin par défaut dans le dossier utilisateur
        Path.home() / "yaktaa_worlds.db",
        Path.home() / "worlds.db",
        
        # Chemin relatif dans le dossier courant
        Path("yaktaa_worlds.db"),
        Path("worlds.db"),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Base de données trouvée à: {path}")
            return path
    
    logger.error("Aucune base de données trouvée!")
    return None


def check_table_structure(conn, table_name):
    """Vérifie la structure d'une table spécifique"""
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table existe
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not cursor.fetchone():
            logger.warning(f"Table '{table_name}' introuvable dans la base de données")
            return None
        
        # Récupérer la structure de la table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        logger.info(f"Structure de la table '{table_name}':")
        for col in columns:
            logger.info(f"  - Colonne {col[0]}: {col[1]} (Type: {col[2]}, NotNull: {col[3]}, DefaultValue: {col[4]}, PK: {col[5]})")
        
        return {col[1]: (col[2], col[3], col[4], col[5]) for col in columns}
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la structure de la table '{table_name}': {str(e)}")
        return None


def analyze_shops_data(conn):
    """Analyse les données des boutiques et leur lien avec les emplacements"""
    cursor = conn.cursor()
    
    try:
        # Vérifier la structure des tables
        shops_columns = check_table_structure(conn, "shops")
        locations_columns = check_table_structure(conn, "locations")
        
        if not shops_columns or not locations_columns:
            return
        
        # Identifier les colonnes critiques pour la connexion shop-location
        shop_id_column = "shop_id" if "shop_id" in shops_columns else "id"
        shop_type_column = "shop_type" if "shop_type" in shops_columns else "type"
        location_id_column = "location_id" if "location_id" in shops_columns else "city_id"
        
        location_id_col = "location_id" if "location_id" in locations_columns else "id"
        
        logger.info(f"\nColonnes critiques identifiées:")
        logger.info(f"  - ID de boutique: {shop_id_column}")
        logger.info(f"  - Type de boutique: {shop_type_column}")
        logger.info(f"  - ID d'emplacement dans boutiques: {location_id_column}")
        logger.info(f"  - ID d'emplacement dans locations: {location_id_col}")
        
        # Récupérer les mondes disponibles
        cursor.execute("SELECT DISTINCT world_id FROM shops")
        worlds = cursor.fetchall()
        logger.info(f"\nMondes contenant des boutiques: {[w[0] for w in worlds]}")
        
        # Récupérer des exemples de boutiques
        cursor.execute(f"SELECT * FROM shops LIMIT 5")
        shops = cursor.fetchall()
        
        logger.info(f"\nExemples de boutiques:")
        for shop in shops:
            logger.info(f"  - {shop}")
        
        # Vérifier l'intégrité des relations
        cursor.execute(f"""
            SELECT s.{shop_id_column}, s.name, s.{location_id_column}, 
                   l.name as location_name 
            FROM shops s 
            LEFT JOIN locations l ON s.{location_id_column} = l.{location_id_col} 
            LIMIT 10
        """)
        relations = cursor.fetchall()
        
        logger.info(f"\nRelations boutiques-emplacements:")
        for rel in relations:
            shop_id, shop_name, loc_id, loc_name = rel
            status = "✓ OK" if loc_name else "✗ ERREUR - Emplacement non trouvé"
            logger.info(f"  - {shop_name} ({shop_id}) → {loc_id}: {loc_name if loc_name else 'N/A'} {status}")
        
        # Vérifier si 'tokyo' existe comme emplacement
        cursor.execute(f"SELECT * FROM locations WHERE LOWER(name) = 'tokyo' OR {location_id_col} = 'tokyo'")
        tokyo = cursor.fetchone()
        
        if tokyo:
            logger.info(f"\nEmplacement 'tokyo' trouvé: {tokyo}")
        else:
            logger.warning(f"\nEmplacement 'tokyo' non trouvé dans la base de données")
            
            # Chercher des emplacements similaires
            cursor.execute(f"SELECT {location_id_col}, name FROM locations WHERE name LIKE '%tok%' OR name LIKE '%yo%'")
            similar = cursor.fetchall()
            if similar:
                logger.info("Emplacements similaires:")
                for loc in similar:
                    logger.info(f"  - {loc}")
        
        # Vérifier les boutiques sans emplacement valide
        cursor.execute(f"""
            SELECT COUNT(*) FROM shops s 
            LEFT JOIN locations l ON s.{location_id_column} = l.{location_id_col} 
            WHERE l.{location_id_col} IS NULL
        """)
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count > 0:
            logger.warning(f"\n{orphaned_count} boutiques n'ont pas d'emplacement valide!")
            
            # Montrer quelques exemples
            cursor.execute(f"""
                SELECT s.{shop_id_column}, s.name, s.{location_id_column} 
                FROM shops s 
                LEFT JOIN locations l ON s.{location_id_column} = l.{location_id_col} 
                WHERE l.{location_id_col} IS NULL 
                LIMIT 5
            """)
            orphaned = cursor.fetchall()
            logger.info("Exemples de boutiques sans emplacement valide:")
            for shop in orphaned:
                logger.info(f"  - {shop}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des données: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def generate_fix_script(conn):
    """Génère un script SQL pour corriger les problèmes identifiés"""
    cursor = conn.cursor()
    
    try:
        # Vérifier la structure des tables
        shops_columns = check_table_structure(conn, "shops")
        
        if not shops_columns:
            return
        
        # Identifier les colonnes qui pourraient nécessiter une correction
        fixes = []
        
        # 1. Vérifier si la colonne shop_type existe, sinon proposer de renommer type en shop_type
        if "type" in shops_columns and "shop_type" not in shops_columns:
            fixes.append(("ALTER TABLE shops RENAME COLUMN type TO shop_type;", 
                         "Renommer la colonne 'type' en 'shop_type'"))
        
        # 2. Vérifier si la colonne location_id existe, sinon proposer de renommer city_id en location_id
        if "city_id" in shops_columns and "location_id" not in shops_columns:
            fixes.append(("ALTER TABLE shops RENAME COLUMN city_id TO location_id;", 
                         "Renommer la colonne 'city_id' en 'location_id'"))
        
        # 3. Vérifier si les ID de boutiques sont standardisés
        if "id" in shops_columns and "shop_id" not in shops_columns:
            fixes.append(("ALTER TABLE shops RENAME COLUMN id TO shop_id;", 
                         "Renommer la colonne 'id' en 'shop_id'"))
        
        # Générer le script SQL
        if fixes:
            logger.info("\nScript SQL pour corriger les problèmes identifiés:")
            logger.info("```sql")
            for sql, desc in fixes:
                logger.info(f"-- {desc}")
                logger.info(sql)
            logger.info("```")
            
            # Créer un fichier SQL avec les corrections
            with open("fix_shops_db.sql", "w") as f:
                f.write("-- Script de correction pour la base de données YakTaa\n\n")
                for sql, desc in fixes:
                    f.write(f"-- {desc}\n")
                    f.write(f"{sql}\n\n")
            
            logger.info(f"Script de correction enregistré dans 'fix_shops_db.sql'")
        else:
            logger.info("\nAucune correction nécessaire pour la structure des tables.")
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du script de correction: {str(e)}")


def main():
    """Fonction principale du script"""
    logger.info("=== Vérification de la base de données YakTaa pour les boutiques ===\n")
    
    # Rechercher la base de données
    db_path = find_database()
    if not db_path:
        return 1
    
    try:
        # Se connecter à la base de données
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Analyser la structure et les données
        analyze_shops_data(conn)
        
        # Générer un script de correction
        generate_fix_script(conn)
        
        conn.close()
        logger.info("\n=== Vérification terminée ===")
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la base de données: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
