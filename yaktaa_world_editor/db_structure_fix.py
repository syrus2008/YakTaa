#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction de structure de base de données pour YakTaa
Ce script ajoute spécifiquement les colonnes manquantes identifiées
dans les tables existantes.
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_structure_fix')

class DatabaseStructureFix:
    """Classe pour corriger la structure de la base de données YakTaa"""
    
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
        
        # Créer une sauvegarde avant modification
        self._backup_database()
        
        # Connecter à la base de données
        self._connect()
    
    def _backup_database(self):
        """Crée une sauvegarde de la base de données avant modification"""
        import shutil
        from datetime import datetime
        
        # Créer un nom de fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.db_path}.backup_fix_{timestamp}"
        
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
        Ajoute une colonne à une table
        
        Args:
            table_name: Nom de la table
            column_name: Nom de la colonne à ajouter
            column_type: Type de la colonne (TEXT, INTEGER, etc.)
            default_value: Valeur par défaut pour la colonne (optionnel)
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            cursor = self.conn.cursor()
            
            # Construire la requête SQL
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value is not None:
                sql += f" DEFAULT {default_value}"
            
            # Exécuter la requête
            cursor.execute(sql)
            
            logger.info(f"Colonne {column_name} ajoutée à la table {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout de la colonne {column_name} à {table_name}: {e}")
            return False
    
    def fix_locations_table(self) -> bool:
        """
        Corrige la structure de la table locations
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        table_name = "locations"
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas, impossible de la corriger")
            return False
        
        success = True
        
        # Ajouter les colonnes manquantes
        if not self.column_exists(table_name, "type"):
            success = success and self.add_column(table_name, "type", "TEXT")
        
        if not self.column_exists(table_name, "x_coord"):
            success = success and self.add_column(table_name, "x_coord", "REAL", "0.0")
        
        if not self.column_exists(table_name, "y_coord"):
            success = success and self.add_column(table_name, "y_coord", "REAL", "0.0")
        
        if not self.column_exists(table_name, "is_discoverable"):
            success = success and self.add_column(table_name, "is_discoverable", "INTEGER", "1")
        
        if not self.column_exists(table_name, "discovery_requirements"):
            success = success and self.add_column(table_name, "discovery_requirements", "TEXT")
        
        return success
    
    def fix_buildings_table(self) -> bool:
        """
        Corrige la structure de la table buildings
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        table_name = "buildings"
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas, impossible de la corriger")
            return False
        
        success = True
        
        # Ajouter les colonnes manquantes
        if not self.column_exists(table_name, "type"):
            success = success and self.add_column(table_name, "type", "TEXT")
        
        if not self.column_exists(table_name, "has_basement"):
            success = success and self.add_column(table_name, "has_basement", "INTEGER", "0")
        
        if not self.column_exists(table_name, "x_coord"):
            success = success and self.add_column(table_name, "x_coord", "REAL", "0.0")
        
        if not self.column_exists(table_name, "y_coord"):
            success = success and self.add_column(table_name, "y_coord", "REAL", "0.0")
        
        if not self.column_exists(table_name, "icon"):
            success = success and self.add_column(table_name, "icon", "TEXT")
        
        return success
    
    def fix_software_items_table(self) -> bool:
        """
        Corrige la structure de la table software_items
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        table_name = "software_items"
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas, impossible de la corriger")
            return False
        
        success = True
        
        # Ajouter les colonnes manquantes
        if not self.column_exists(table_name, "metadata"):
            success = success and self.add_column(table_name, "metadata", "TEXT")
        
        # S'assurer que les colonnes version et license_type existent
        if not self.column_exists(table_name, "version"):
            success = success and self.add_column(table_name, "version", "TEXT", "'N/A'")
        
        if not self.column_exists(table_name, "license_type"):
            success = success and self.add_column(table_name, "license_type", "TEXT", "'Standard'")
        
        if not self.column_exists(table_name, "capabilities"):
            success = success and self.add_column(table_name, "capabilities", "TEXT")
        
        return success
    
    def fix_consumable_items_table(self) -> bool:
        """
        Corrige la structure de la table consumable_items
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        table_name = "consumable_items"
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas, impossible de la corriger")
            return False
        
        success = True
        
        # Vérifier si item_type existe et consumable_type n'existe pas
        if self.column_exists(table_name, "item_type") and not self.column_exists(table_name, "consumable_type"):
            try:
                # Créer une table temporaire avec la bonne structure
                cursor = self.conn.cursor()
                cursor.execute(f"""
                CREATE TABLE temp_consumable_items AS 
                SELECT 
                    id, name, description, item_type AS consumable_type, 
                    rarity, uses, duration, price, is_legal, is_available, 
                    effects, world_id, building_id, character_id, device_id, 
                    location_type, location_id, metadata
                FROM {table_name}
                """)
                
                # Supprimer l'ancienne table
                cursor.execute(f"DROP TABLE {table_name}")
                
                # Renommer la table temporaire
                cursor.execute(f"ALTER TABLE temp_consumable_items RENAME TO {table_name}")
                
                logger.info(f"Colonne item_type renommée en consumable_type dans la table {table_name}")
                success = True
            except sqlite3.Error as e:
                logger.error(f"Erreur lors du renommage de item_type en consumable_type: {e}")
                success = False
        
        return success
    
    def fix_hardware_items_table(self) -> bool:
        """
        Corrige la structure de la table hardware_items
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        table_name = "hardware_items"
        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} n'existe pas, impossible de la corriger")
            return False
        
        success = True
        
        # Vérifier le type de la colonne quality
        columns = self.get_table_info(table_name)
        quality_col = next((col for col in columns if col['name'] == 'quality'), None)
        
        if quality_col and quality_col['type'].upper() == 'TEXT':
            try:
                # Vérifier d'abord si la conversion est possible
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT quality FROM {table_name}")
                rows = cursor.fetchall()
                
                # Vérifier si toutes les valeurs peuvent être converties en INTEGER
                can_convert = True
                for row in rows:
                    quality_value = row['quality']
                    if quality_value is not None and quality_value != '':
                        try:
                            # Si c'est déjà un nombre, pas de problème
                            int(quality_value)
                        except ValueError:
                            # Si ce n'est pas un nombre, vérifier si c'est une valeur textuelle connue
                            if quality_value not in ['Faible', 'Moyen', 'Bon', 'Excellent', 'Parfait']:
                                # Si ce n'est pas une valeur connue, on ne peut pas convertir
                                can_convert = False
                                logger.warning(f"Valeur non convertible dans quality: {quality_value}")
                                break
                
                if can_convert:
                    # Obtenir toutes les colonnes
                    cols = [col['name'] for col in columns]
                    cols_str = ', '.join(cols)
                    
                    # Créer une table temporaire avec la même structure
                    cursor.execute(f"CREATE TABLE temp_hardware_items AS SELECT * FROM {table_name} WHERE 0")
                    
                    # Modifier le type de la colonne quality dans la table temporaire
                    cursor.execute(f"ALTER TABLE temp_hardware_items DROP COLUMN quality")
                    cursor.execute(f"ALTER TABLE temp_hardware_items ADD COLUMN quality INTEGER")
                    
                    # Insérer les données avec conversion
                    for row in rows:
                        # Préparer les valeurs pour l'insertion
                        values = []
                        for col in columns:
                            if col['name'] == 'quality':
                                quality_value = row['quality']
                                if quality_value is None or quality_value == '':
                                    values.append(0)
                                elif quality_value == 'Faible':
                                    values.append(1)
                                elif quality_value == 'Moyen':
                                    values.append(2)
                                elif quality_value == 'Bon':
                                    values.append(3)
                                elif quality_value == 'Excellent':
                                    values.append(4)
                                elif quality_value == 'Parfait':
                                    values.append(5)
                                else:
                                    try:
                                        values.append(int(quality_value))
                                    except ValueError:
                                        values.append(0)
                            else:
                                values.append(row[col['name']])
                        
                        # Construire la requête d'insertion
                        placeholders = ', '.join(['?' for _ in values])
                        insert_cols = ', '.join([col['name'] for col in columns])
                        cursor.execute(f"INSERT INTO temp_hardware_items ({insert_cols}) VALUES ({placeholders})", values)
                    
                    # Supprimer l'ancienne table
                    cursor.execute(f"DROP TABLE {table_name}")
                    
                    # Renommer la table temporaire
                    cursor.execute(f"ALTER TABLE temp_hardware_items RENAME TO {table_name}")
                    
                    logger.info(f"Type de la colonne quality changé de TEXT à INTEGER dans la table {table_name}")
                    success = True
                else:
                    # Si on ne peut pas convertir toutes les valeurs, on laisse la colonne telle quelle
                    logger.warning(f"Impossible de convertir toutes les valeurs de quality en INTEGER, colonne laissée en TEXT")
                    success = True  # On considère que c'est un succès car on ne bloque pas la migration
            except sqlite3.Error as e:
                logger.error(f"Erreur lors du changement de type de quality: {e}")
                success = False
        
        return success
    
    def fix_database_structure(self) -> bool:
        """
        Corrige la structure complète de la base de données
        
        Returns:
            True si toutes les corrections ont réussi, False sinon
        """
        try:
            logger.info("Début de la correction de la structure de la base de données")
            
            # Commencer une transaction
            self.conn.execute("BEGIN TRANSACTION")
            
            # Corriger chaque table
            locations_success = self.fix_locations_table()
            buildings_success = self.fix_buildings_table()
            software_success = self.fix_software_items_table()
            consumable_success = self.fix_consumable_items_table()
            hardware_success = self.fix_hardware_items_table()
            
            # Vérifier si toutes les corrections ont réussi
            # Note: Nous considérons que c'est un succès même si certaines tables n'existent pas
            # ou si certaines conversions de type ne sont pas possibles
            all_success = True
            
            # Pour les tables qui existent, vérifier si les corrections ont réussi
            if not locations_success and self.table_exists("locations"):
                all_success = False
            if not buildings_success and self.table_exists("buildings"):
                all_success = False
            if not software_success and self.table_exists("software_items"):
                all_success = False
            if not consumable_success and self.table_exists("consumable_items"):
                all_success = False
            if not hardware_success and self.table_exists("hardware_items"):
                all_success = False
            
            if all_success:
                # Valider les modifications
                self.conn.execute("COMMIT")
                logger.info("Correction de la structure de la base de données terminée avec succès")
            else:
                # Annuler les modifications
                self.conn.execute("ROLLBACK")
                logger.error("Échec de la correction de la structure, modifications annulées")
            
            return all_success
            
        except Exception as e:
            # En cas d'erreur, annuler les modifications
            self.conn.execute("ROLLBACK")
            logger.error(f"Erreur lors de la correction de la structure: {e}")
            return False


def main():
    """Fonction principale"""
    try:
        # Récupérer le chemin de la base de données depuis les arguments
        db_path = None
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
        
        # Créer l'instance de correction
        fixer = DatabaseStructureFix(db_path)
        
        # Corriger la structure
        if fixer.fix_database_structure():
            print("[OK] Structure de la base de données corrigée avec succès")
            return 0
        else:
            print("[ERREUR] Échec de la correction de la structure")
            return 1
    
    except Exception as e:
        logger.error(f"Erreur non gérée: {e}")
        print(f"Erreur: {e}")
        return 1
    finally:
        # Fermer la connexion
        if 'fixer' in locals():
            fixer.close()


if __name__ == "__main__":
    sys.exit(main())
