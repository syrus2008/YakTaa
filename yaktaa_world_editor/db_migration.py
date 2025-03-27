#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration de base de données pour YakTaa
Ce script standardise la structure des tables de la base de données
en ajoutant les colonnes manquantes et en corrigeant les incohérences.
"""

import os
import sys
import sqlite3
import logging
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_migration')

class DatabaseMigration:
    """Classe pour gérer la migration de la base de données YakTaa"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données. Si None, utilise le chemin par défaut.
        """
        if db_path is None:
            # Chemin par défaut dans le dossier utilisateur
            db_path = os.path.join(Path.home(), "yaktaa_worlds.db")
        
        self.db_path = db_path
        self.conn = None
        
        # Vérifier si le fichier existe
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            raise FileNotFoundError(f"Base de données non trouvée: {db_path}")
        
        # Créer une sauvegarde avant migration
        self._backup_database()
        
        # Connecter à la base de données
        self._connect()
        
    def _backup_database(self):
        """Crée une sauvegarde de la base de données avant la migration"""
        import shutil
        from datetime import datetime
        
        # Créer un nom de fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.db_path}.backup_{timestamp}"
        
        # Copier le fichier
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Sauvegarde créée: {backup_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            raise
    
    def _connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Activer les clés étrangères
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Définir le niveau d'isolation pour permettre des transactions explicites
            self.conn.isolation_level = "DEFERRED"
            
            logger.info(f"Connecté à la base de données: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            raise
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.info("Connexion à la base de données fermée")
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Récupère les informations sur les colonnes d'une table
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des informations de colonnes
        """
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [dict(row) for row in cursor.fetchall()]
        return columns
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifie si une table existe dans la base de données
        
        Args:
            table_name: Nom de la table à vérifier
            
        Returns:
            True si la table existe, False sinon
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Vérifie si une colonne existe dans une table
        
        Args:
            table_name: Nom de la table
            column_name: Nom de la colonne
            
        Returns:
            True si la colonne existe, False sinon
        """
        if not self.table_exists(table_name):
            return False
        
        columns = self.get_table_info(table_name)
        return any(col['name'] == column_name for col in columns)
    
    def add_column(self, table_name: str, column_name: str, column_type: str, default_value: Optional[str] = None) -> bool:
        """
        Ajoute une colonne à une table existante
        
        Args:
            table_name: Nom de la table
            column_name: Nom de la colonne à ajouter
            column_type: Type de la colonne (TEXT, INTEGER, etc.)
            default_value: Valeur par défaut pour la colonne
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas")
            return False
        
        if self.column_exists(table_name, column_name):
            logger.info(f"Colonne {column_name} existe déjà dans {table_name}")
            return True
        
        try:
            cursor = self.conn.cursor()
            
            # Construire la requête SQL
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value is not None:
                sql += f" DEFAULT {default_value}"
            
            # Exécuter la requête
            cursor.execute(sql)
            
            logger.info(f"Colonne {column_name} ajoutée à {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout de la colonne {column_name} à {table_name}: {e}")
            return False
    
    def rename_column(self, table_name: str, old_column: str, new_column: str, column_type: str) -> bool:
        """
        Renomme une colonne dans une table (SQLite ne supporte pas directement ALTER TABLE RENAME COLUMN)
        Cette méthode crée une nouvelle table avec la colonne renommée et copie les données
        
        Args:
            table_name: Nom de la table
            old_column: Nom actuel de la colonne
            new_column: Nouveau nom de la colonne
            column_type: Type de la colonne
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas")
            return False
        
        if not self.column_exists(table_name, old_column):
            logger.warning(f"Colonne {old_column} n'existe pas dans {table_name}")
            return False
        
        if self.column_exists(table_name, new_column):
            logger.info(f"Colonne {new_column} existe déjà dans {table_name}")
            return True
        
        try:
            cursor = self.conn.cursor()
            
            # 1. Obtenir la structure de la table
            columns = self.get_table_info(table_name)
            
            # 2. Créer une nouvelle table avec la colonne renommée
            create_stmt = f"CREATE TABLE {table_name}_new ("
            column_defs = []
            
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                col_notnull = "NOT NULL" if col['notnull'] else ""
                col_pk = "PRIMARY KEY" if col['pk'] else ""
                col_default = f"DEFAULT {col['dflt_value']}" if col['dflt_value'] is not None else ""
                
                if col_name == old_column:
                    # Renommer la colonne
                    column_defs.append(f"{new_column} {column_type} {col_notnull} {col_pk} {col_default}")
                else:
                    column_defs.append(f"{col_name} {col_type} {col_notnull} {col_pk} {col_default}")
            
            create_stmt += ", ".join(column_defs) + ")"
            cursor.execute(create_stmt)
            
            # 3. Copier les données
            old_cols = [col['name'] for col in columns]
            new_cols = [new_column if col == old_column else col for col in old_cols]
            
            # Construire la requête d'insertion
            insert_stmt = f"INSERT INTO {table_name}_new ({', '.join(new_cols)}) SELECT {', '.join(old_cols)} FROM {table_name}"
            cursor.execute(insert_stmt)
            
            # 4. Supprimer l'ancienne table
            cursor.execute(f"DROP TABLE {table_name}")
            
            # 5. Renommer la nouvelle table
            cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            logger.info(f"Colonne {old_column} renommée en {new_column} dans {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du renommage de la colonne {old_column} en {new_column} dans {table_name}: {e}")
            return False
    
    def change_column_type(self, table_name: str, column_name: str, new_type: str) -> bool:
        """
        Change le type d'une colonne (SQLite ne supporte pas directement ALTER TABLE ALTER COLUMN)
        Cette méthode crée une nouvelle table avec le type modifié et copie les données
        
        Args:
            table_name: Nom de la table
            column_name: Nom de la colonne
            new_type: Nouveau type de la colonne
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas")
            return False
        
        if not self.column_exists(table_name, column_name):
            logger.warning(f"Colonne {column_name} n'existe pas dans {table_name}")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # 1. Obtenir la structure de la table
            columns = self.get_table_info(table_name)
            
            # 2. Créer une nouvelle table avec le type modifié
            create_stmt = f"CREATE TABLE {table_name}_new ("
            column_defs = []
            
            for col in columns:
                col_name = col['name']
                col_type = new_type if col_name == column_name else col['type']
                col_notnull = "NOT NULL" if col['notnull'] else ""
                col_pk = "PRIMARY KEY" if col['pk'] else ""
                col_default = f"DEFAULT {col['dflt_value']}" if col['dflt_value'] is not None else ""
                
                column_defs.append(f"{col_name} {col_type} {col_notnull} {col_pk} {col_default}")
            
            create_stmt += ", ".join(column_defs) + ")"
            cursor.execute(create_stmt)
            
            # 3. Copier les données
            cols = [col['name'] for col in columns]
            
            # Construire la requête d'insertion
            insert_stmt = f"INSERT INTO {table_name}_new SELECT {', '.join(cols)} FROM {table_name}"
            cursor.execute(insert_stmt)
            
            # 4. Supprimer l'ancienne table
            cursor.execute(f"DROP TABLE {table_name}")
            
            # 5. Renommer la nouvelle table
            cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            logger.info(f"Type de la colonne {column_name} dans {table_name} changé en {new_type}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du changement de type de la colonne {column_name} dans {table_name}: {e}")
            return False
    
    def create_table_if_not_exists(self, table_name: str, columns: List[Dict[str, str]]) -> bool:
        """
        Crée une table si elle n'existe pas
        
        Args:
            table_name: Nom de la table à créer
            columns: Liste des définitions de colonnes
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        if self.table_exists(table_name):
            logger.info(f"Table {table_name} existe déjà")
            return True
        
        try:
            cursor = self.conn.cursor()
            
            # Construire la requête SQL
            create_stmt = f"CREATE TABLE {table_name} ("
            column_defs = []
            
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get('not_null', False):
                    col_def += " NOT NULL"
                if col.get('primary_key', False):
                    col_def += " PRIMARY KEY"
                if 'default' in col:
                    col_def += f" DEFAULT {col['default']}"
                if 'foreign_key' in col:
                    fk = col['foreign_key']
                    col_def += f", FOREIGN KEY ({col['name']}) REFERENCES {fk['table']} ({fk['column']})"
                    if fk.get('on_delete'):
                        col_def += f" ON DELETE {fk['on_delete']}"
                
                column_defs.append(col_def)
            
            create_stmt += ", ".join(column_defs) + ")"
            cursor.execute(create_stmt)
            
            logger.info(f"Table {table_name} créée")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création de la table {table_name}: {e}")
            return False
    
    def migrate_software_items(self) -> bool:
        """
        Migre la table software_items pour assurer la compatibilité
        
        Returns:
            True si la migration a réussi, False sinon
        """
        table_name = "software_items"
        
        # Vérifier si la table existe
        if not self.table_exists(table_name):
            # Créer la table avec la structure standardisée
            columns = [
                {"name": "id", "type": "TEXT", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "description", "type": "TEXT"},
                {"name": "software_type", "type": "TEXT", "not_null": True},
                {"name": "version", "type": "TEXT", "default": "'N/A'"},
                {"name": "license_type", "type": "TEXT", "default": "'Standard'"},
                {"name": "price", "type": "INTEGER", "default": "0"},
                {"name": "is_legal", "type": "BOOLEAN", "default": "1"},
                {"name": "capabilities", "type": "TEXT"},
                {"name": "world_id", "type": "TEXT", "not_null": True, 
                 "foreign_key": {"table": "worlds", "column": "id", "on_delete": "CASCADE"}},
                {"name": "device_id", "type": "TEXT", 
                 "foreign_key": {"table": "devices", "column": "id", "on_delete": "SET NULL"}},
                {"name": "file_id", "type": "TEXT", 
                 "foreign_key": {"table": "files", "column": "id", "on_delete": "SET NULL"}}
            ]
            return self.create_table_if_not_exists(table_name, columns)
        
        # Ajouter les colonnes manquantes
        success = True
        
        # Vérifier et ajouter la colonne version
        if not self.column_exists(table_name, "version"):
            success = success and self.add_column(table_name, "version", "TEXT", "'N/A'")
        
        # Vérifier et ajouter la colonne license_type
        if not self.column_exists(table_name, "license_type"):
            success = success and self.add_column(table_name, "license_type", "TEXT", "'Standard'")
        
        # Vérifier et ajouter d'autres colonnes importantes
        if not self.column_exists(table_name, "price"):
            success = success and self.add_column(table_name, "price", "INTEGER", "0")
        
        if not self.column_exists(table_name, "is_legal"):
            success = success and self.add_column(table_name, "is_legal", "BOOLEAN", "1")
        
        if not self.column_exists(table_name, "capabilities"):
            success = success and self.add_column(table_name, "capabilities", "TEXT", "NULL")
        
        return success
    
    def migrate_consumable_items(self) -> bool:
        """
        Migre la table consumable_items pour assurer la compatibilité
        
        Returns:
            True si la migration a réussi, False sinon
        """
        table_name = "consumable_items"
        
        # Vérifier si la table existe
        if not self.table_exists(table_name):
            # Créer la table avec la structure standardisée
            columns = [
                {"name": "id", "type": "TEXT", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "description", "type": "TEXT"},
                {"name": "consumable_type", "type": "TEXT", "not_null": True},
                {"name": "rarity", "type": "TEXT", "default": "'Commun'"},
                {"name": "uses", "type": "INTEGER", "default": "1"},
                {"name": "duration", "type": "INTEGER", "default": "15"},
                {"name": "price", "type": "INTEGER", "default": "0"},
                {"name": "is_legal", "type": "BOOLEAN", "default": "1"},
                {"name": "is_available", "type": "INTEGER", "default": "1"},
                {"name": "effects", "type": "TEXT"},
                {"name": "world_id", "type": "TEXT", "not_null": True, 
                 "foreign_key": {"table": "worlds", "column": "id", "on_delete": "CASCADE"}},
                {"name": "building_id", "type": "TEXT", 
                 "foreign_key": {"table": "buildings", "column": "id", "on_delete": "SET NULL"}},
                {"name": "character_id", "type": "TEXT", 
                 "foreign_key": {"table": "characters", "column": "id", "on_delete": "SET NULL"}},
                {"name": "device_id", "type": "TEXT", 
                 "foreign_key": {"table": "devices", "column": "id", "on_delete": "SET NULL"}},
                {"name": "location_type", "type": "TEXT"},
                {"name": "location_id", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ]
            return self.create_table_if_not_exists(table_name, columns)
        
        success = True
        
        # Vérifier si la colonne item_type existe et doit être renommée
        if self.column_exists(table_name, "item_type") and not self.column_exists(table_name, "consumable_type"):
            success = success and self.rename_column(table_name, "item_type", "consumable_type", "TEXT")
        
        # Ajouter les colonnes manquantes
        if not self.column_exists(table_name, "rarity"):
            success = success and self.add_column(table_name, "rarity", "TEXT", "'Commun'")
        
        if not self.column_exists(table_name, "duration"):
            success = success and self.add_column(table_name, "duration", "INTEGER", "15")
        
        if not self.column_exists(table_name, "is_legal"):
            success = success and self.add_column(table_name, "is_legal", "BOOLEAN", "1")
        
        return success
    
    def migrate_hardware_items(self) -> bool:
        """
        Migre la table hardware_items pour assurer la compatibilité
        
        Returns:
            True si la migration a réussi, False sinon
        """
        table_name = "hardware_items"
        
        # Vérifier si la table existe
        if not self.table_exists(table_name):
            # Créer la table avec la structure standardisée
            columns = [
                {"name": "id", "type": "TEXT", "primary_key": True},
                {"name": "name", "type": "TEXT", "not_null": True},
                {"name": "description", "type": "TEXT"},
                {"name": "hardware_type", "type": "TEXT", "not_null": True},
                {"name": "quality", "type": "INTEGER", "default": "0"},
                {"name": "rarity", "type": "TEXT", "default": "'Commun'"},
                {"name": "level", "type": "INTEGER", "default": "1"},
                {"name": "price", "type": "INTEGER", "default": "0"},
                {"name": "is_legal", "type": "BOOLEAN", "default": "1"},
                {"name": "is_installed", "type": "INTEGER", "default": "0"},
                {"name": "is_available", "type": "INTEGER", "default": "1"},
                {"name": "stats", "type": "TEXT"},
                {"name": "world_id", "type": "TEXT", "not_null": True, 
                 "foreign_key": {"table": "worlds", "column": "id", "on_delete": "CASCADE"}},
                {"name": "building_id", "type": "TEXT", 
                 "foreign_key": {"table": "buildings", "column": "id", "on_delete": "SET NULL"}},
                {"name": "character_id", "type": "TEXT", 
                 "foreign_key": {"table": "characters", "column": "id", "on_delete": "SET NULL"}},
                {"name": "device_id", "type": "TEXT", 
                 "foreign_key": {"table": "devices", "column": "id", "on_delete": "SET NULL"}},
                {"name": "location_type", "type": "TEXT"},
                {"name": "location_id", "type": "TEXT"},
                {"name": "metadata", "type": "TEXT"}
            ]
            return self.create_table_if_not_exists(table_name, columns)
        
        success = True
        
        # Vérifier si la colonne quality est de type TEXT et doit être changée en INTEGER
        columns = self.get_table_info(table_name)
        quality_col = next((col for col in columns if col['name'] == 'quality'), None)
        
        if quality_col and quality_col['type'].upper() == 'TEXT':
            success = success and self.change_column_type(table_name, "quality", "INTEGER")
        
        # Ajouter les colonnes manquantes
        if not self.column_exists(table_name, "quality"):
            success = success and self.add_column(table_name, "quality", "INTEGER", "0")
        
        if not self.column_exists(table_name, "level"):
            success = success and self.add_column(table_name, "level", "INTEGER", "1")
        
        if not self.column_exists(table_name, "is_legal"):
            success = success and self.add_column(table_name, "is_legal", "BOOLEAN", "1")
        
        return success
    
    def run_migration(self) -> bool:
        """
        Exécute toutes les migrations nécessaires
        
        Returns:
            True si toutes les migrations ont réussi, False sinon
        """
        try:
            logger.info("Début de la migration de la base de données")
            
            # Utiliser une transaction unique pour toutes les opérations
            with self.conn:
                # Migrer les tables principales
                success = True
                success = success and self.migrate_software_items()
                success = success and self.migrate_consumable_items()
                success = success and self.migrate_hardware_items()
                
                if not success:
                    logger.error("Échec de la migration")
                    return False
                
            logger.info("Migration terminée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {e}")
            return False
        finally:
            # Fermer la connexion
            self.close()


def main():
    """Fonction principale"""
    try:
        # Récupérer le chemin de la base de données depuis les arguments
        db_path = None
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
        
        # Créer l'instance de migration
        migration = DatabaseMigration(db_path)
        
        # Exécuter la migration
        success = migration.run_migration()
        
        # Afficher le résultat
        if success:
            print("Migration terminée avec succès")
            return 0
        else:
            print("Échec de la migration")
            return 1
    except Exception as e:
        logger.error(f"Erreur non gérée: {e}")
        print(f"Erreur: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
