"""
Module de vérification de compatibilité entre l'éditeur de monde YakTaa et le jeu principal.
Ce module permet de vérifier que toutes les structures de données sont compatibles
et que les métadonnées sont correctement formatées.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Any, List, Tuple, Optional, Set
from pathlib import Path

from metadata_schema import METADATA_SCHEMAS, get_schema_for_item_type, MetadataSchema

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompatibilityChecker:
    """
    Classe pour vérifier la compatibilité entre l'éditeur de monde et le jeu principal.
    """
    
    def __init__(self, editor_db_path: str, game_db_path: Optional[str] = None):
        """
        Initialise le vérificateur de compatibilité.
        
        Args:
            editor_db_path: Chemin vers la base de données de l'éditeur de monde
            game_db_path: Chemin vers la base de données du jeu principal (optionnel)
        """
        self.editor_db_path = Path(editor_db_path)
        self.game_db_path = Path(game_db_path) if game_db_path else None
        
        # Tables et colonnes attendues pour chaque type d'objet
        self.expected_tables = {
            "worlds": ["id", "name", "description", "creation_date"],
            "locations": ["id", "world_id", "name", "type", "description", "x_coord", "y_coord"],
            "buildings": ["id", "location_id", "name", "type", "description", "security_level"],
            "characters": ["id", "world_id", "name", "description", "faction_id", "location_id"],
            "devices": ["id", "network_id", "name", "device_type", "os", "security_level"],
            "networks": ["id", "building_id", "name", "network_type", "security_level"],
            "shops": ["id", "location_id", "building_id", "name", "type", "description"],
            "shop_inventory": ["id", "shop_id", "item_type", "item_id", "quantity", "price_modifier"],
            "hardware_items": ["id", "name", "description", "hardware_type", "price", "world_id", "metadata"],
            "software_items": ["id", "name", "description", "software_type", "price", "world_id", "metadata"],
            "consumable_items": ["id", "name", "description", "consumable_type", "price", "world_id", "metadata"],
            "implant_items": ["id", "name", "description", "implant_type", "price", "world_id", "metadata"],
            "weapon_items": ["id", "name", "description", "weapon_type", "price", "world_id", "metadata"],
            "armor_items": ["id", "name", "description", "armor_type", "price", "world_id", "metadata"],
            "missions": ["id", "world_id", "name", "description", "type", "difficulty", "metadata"]
        }
        
        # Correspondance entre les tables et les types d'objets pour les schémas de métadonnées
        self.table_to_schema_type = {
            "hardware_items": "hardware",
            "software_items": "software",
            "consumable_items": "consumable",
            "implant_items": "implant",
            "weapon_items": "weapon",
            "armor_items": "armor",
            "devices": "device",
            "networks": "network",
            "characters": "character",
            "shops": "shop",
            "missions": "mission",
            "locations": "location",
            "buildings": "building"
        }
    
    def check_database_existence(self) -> bool:
        """
        Vérifie si les bases de données existent.
        
        Returns:
            True si les bases de données existent, False sinon
        """
        editor_exists = self.editor_db_path.exists()
        
        if not editor_exists:
            logger.error(f"Base de données de l'éditeur non trouvée: {self.editor_db_path}")
            return False
        
        if self.game_db_path:
            game_exists = self.game_db_path.exists()
            if not game_exists:
                logger.error(f"Base de données du jeu non trouvée: {self.game_db_path}")
                return False
        
        return True
    
    def get_tables(self, db_path: Path) -> List[str]:
        """
        Récupère la liste des tables dans une base de données.
        
        Args:
            db_path: Chemin vers la base de données
            
        Returns:
            Liste des noms de tables
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return tables
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des tables: {e}")
            return []
    
    def get_columns(self, db_path: Path, table_name: str) -> List[str]:
        """
        Récupère la liste des colonnes d'une table.
        
        Args:
            db_path: Chemin vers la base de données
            table_name: Nom de la table
            
        Returns:
            Liste des noms de colonnes
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            conn.close()
            return columns
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des colonnes de {table_name}: {e}")
            return []
    
    def check_table_structure(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie la structure des tables dans la base de données de l'éditeur.
        
        Returns:
            Dictionnaire contenant les résultats de la vérification pour chaque table
        """
        if not self.check_database_existence():
            return {}
        
        results = {}
        tables = self.get_tables(self.editor_db_path)
        
        for expected_table, expected_columns in self.expected_tables.items():
            if expected_table not in tables:
                results[expected_table] = {
                    "exists": False,
                    "missing_columns": [],
                    "extra_columns": [],
                    "status": "MISSING"
                }
                continue
            
            actual_columns = self.get_columns(self.editor_db_path, expected_table)
            missing_columns = [col for col in expected_columns if col not in actual_columns]
            extra_columns = [col for col in actual_columns if col not in expected_columns]
            
            status = "OK"
            if missing_columns:
                status = "INCOMPLETE"
            
            results[expected_table] = {
                "exists": True,
                "missing_columns": missing_columns,
                "extra_columns": extra_columns,
                "status": status
            }
        
        return results
    
    def check_metadata_format(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie le format des métadonnées pour tous les objets dans la base de données.
        
        Returns:
            Dictionnaire contenant les résultats de la vérification pour chaque type d'objet
        """
        if not self.check_database_existence():
            return {}
        
        results = {}
        
        try:
            conn = sqlite3.connect(str(self.editor_db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for table_name, schema_type in self.table_to_schema_type.items():
                # Vérifier si la table existe
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    results[table_name] = {
                        "exists": False,
                        "items_checked": 0,
                        "items_with_errors": 0,
                        "error_details": [],
                        "status": "MISSING"
                    }
                    continue
                
                # Vérifier si la table a une colonne metadata
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                if "metadata" not in columns:
                    results[table_name] = {
                        "exists": True,
                        "items_checked": 0,
                        "items_with_errors": 0,
                        "error_details": ["Colonne 'metadata' manquante"],
                        "status": "INCOMPLETE"
                    }
                    continue
                
                # Récupérer tous les objets de la table
                type_column = None
                if f"{schema_type}_type" in columns:
                    type_column = f"{schema_type}_type"
                elif "type" in columns:
                    type_column = "type"
                
                cursor.execute(f"SELECT id, name, {type_column if type_column else 'NULL as type'}, metadata FROM {table_name}")
                rows = cursor.fetchall()
                
                items_checked = len(rows)
                items_with_errors = 0
                error_details = []
                
                for row in rows:
                    item_id = row["id"]
                    item_name = row["name"]
                    item_type = row["type"] if type_column else schema_type
                    metadata_str = row["metadata"]
                    
                    if not metadata_str:
                        continue
                    
                    try:
                        # Obtenir le schéma approprié
                        schema_class = get_schema_for_item_type(item_type if item_type else schema_type)
                        
                        # Parser les métadonnées
                        metadata = schema_class.parse_json(metadata_str)
                        
                        # Valider les métadonnées
                        is_valid, errors = schema_class.validate(metadata)
                        
                        if not is_valid:
                            items_with_errors += 1
                            error_details.append({
                                "id": item_id,
                                "name": item_name,
                                "type": item_type,
                                "errors": errors
                            })
                    except Exception as e:
                        items_with_errors += 1
                        error_details.append({
                            "id": item_id,
                            "name": item_name,
                            "type": item_type,
                            "errors": [str(e)]
                        })
                
                status = "OK"
                if items_with_errors > 0:
                    status = "ERRORS" if items_with_errors == items_checked else "PARTIAL"
                
                results[table_name] = {
                    "exists": True,
                    "items_checked": items_checked,
                    "items_with_errors": items_with_errors,
                    "error_details": error_details,
                    "status": status
                }
            
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la vérification des métadonnées: {e}")
        
        return results
    
    def fix_metadata_format(self) -> Dict[str, Dict[str, Any]]:
        """
        Corrige le format des métadonnées pour tous les objets dans la base de données.
        
        Returns:
            Dictionnaire contenant les résultats de la correction pour chaque type d'objet
        """
        if not self.check_database_existence():
            return {}
        
        results = {}
        
        try:
            conn = sqlite3.connect(str(self.editor_db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for table_name, schema_type in self.table_to_schema_type.items():
                # Vérifier si la table existe
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    results[table_name] = {
                        "exists": False,
                        "items_checked": 0,
                        "items_fixed": 0,
                        "status": "MISSING"
                    }
                    continue
                
                # Vérifier si la table a une colonne metadata
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                if "metadata" not in columns:
                    # Ajouter la colonne metadata si elle n'existe pas
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN metadata TEXT")
                        conn.commit()
                        logger.info(f"Colonne 'metadata' ajoutée à la table {table_name}")
                    except sqlite3.Error as e:
                        logger.error(f"Erreur lors de l'ajout de la colonne 'metadata' à {table_name}: {e}")
                        results[table_name] = {
                            "exists": True,
                            "items_checked": 0,
                            "items_fixed": 0,
                            "status": "ERROR"
                        }
                        continue
                
                # Récupérer tous les objets de la table
                type_column = None
                if f"{schema_type}_type" in columns:
                    type_column = f"{schema_type}_type"
                elif "type" in columns:
                    type_column = "type"
                
                cursor.execute(f"SELECT id, name, {type_column if type_column else 'NULL as type'}, metadata FROM {table_name}")
                rows = cursor.fetchall()
                
                items_checked = len(rows)
                items_fixed = 0
                
                for row in rows:
                    item_id = row["id"]
                    item_type = row["type"] if type_column else schema_type
                    metadata_str = row["metadata"]
                    
                    # Obtenir le schéma approprié
                    schema_class = get_schema_for_item_type(item_type if item_type else schema_type)
                    
                    # Parser les métadonnées existantes ou créer un dictionnaire vide
                    metadata = schema_class.parse_json(metadata_str) if metadata_str else {}
                    
                    # Valider les métadonnées
                    is_valid, errors = schema_class.validate(metadata)
                    
                    if not is_valid or not metadata:
                        # Récupérer les métadonnées par défaut
                        default_metadata = schema_class.get_default()
                        
                        # Fusionner avec les métadonnées existantes
                        for key, value in default_metadata.items():
                            if key not in metadata:
                                metadata[key] = value
                        
                        # Convertir en JSON et mettre à jour la base de données
                        new_metadata_str = schema_class.to_json(metadata)
                        cursor.execute(f"UPDATE {table_name} SET metadata = ? WHERE id = ?", 
                                      (new_metadata_str, item_id))
                        items_fixed += 1
                
                conn.commit()
                
                status = "OK"
                if items_fixed > 0:
                    status = "FIXED"
                
                results[table_name] = {
                    "exists": True,
                    "items_checked": items_checked,
                    "items_fixed": items_fixed,
                    "status": status
                }
            
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la correction des métadonnées: {e}")
        
        return results
    
    def check_cross_compatibility(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie la compatibilité croisée entre l'éditeur de monde et le jeu principal.
        
        Returns:
            Dictionnaire contenant les résultats de la vérification
        """
        if not self.check_database_existence() or not self.game_db_path:
            return {}
        
        results = {}
        
        # Vérifier les tables communes
        editor_tables = self.get_tables(self.editor_db_path)
        game_tables = self.get_tables(self.game_db_path)
        
        common_tables = set(editor_tables) & set(game_tables)
        missing_in_game = set(editor_tables) - set(game_tables)
        missing_in_editor = set(game_tables) - set(editor_tables)
        
        results["tables"] = {
            "common": list(common_tables),
            "missing_in_game": list(missing_in_game),
            "missing_in_editor": list(missing_in_editor)
        }
        
        # Vérifier les colonnes des tables communes
        column_compatibility = {}
        
        for table in common_tables:
            editor_columns = set(self.get_columns(self.editor_db_path, table))
            game_columns = set(self.get_columns(self.game_db_path, table))
            
            common_columns = editor_columns & game_columns
            missing_in_game = editor_columns - game_columns
            missing_in_editor = game_columns - editor_columns
            
            column_compatibility[table] = {
                "common": list(common_columns),
                "missing_in_game": list(missing_in_game),
                "missing_in_editor": list(missing_in_editor),
                "status": "OK" if not missing_in_game else "INCOMPLETE"
            }
        
        results["columns"] = column_compatibility
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Génère un rapport complet de compatibilité.
        
        Returns:
            Dictionnaire contenant le rapport complet
        """
        report = {
            "database_existence": self.check_database_existence(),
            "table_structure": self.check_table_structure(),
            "metadata_format": self.check_metadata_format()
        }
        
        if self.game_db_path:
            report["cross_compatibility"] = self.check_cross_compatibility()
        
        return report
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """
        Affiche un rapport de compatibilité de manière lisible.
        
        Args:
            report: Rapport généré par generate_report()
        """
        print("\n===== RAPPORT DE COMPATIBILITÉ YAKTAA =====\n")
        
        # Vérification de l'existence des bases de données
        print("1. EXISTENCE DES BASES DE DONNÉES")
        print(f"   Base de données de l'éditeur: {'✅ Trouvée' if report['database_existence'] else '❌ Non trouvée'}")
        if self.game_db_path:
            print(f"   Base de données du jeu: {'✅ Trouvée' if report['database_existence'] else '❌ Non trouvée'}")
        print()
        
        # Structure des tables
        print("2. STRUCTURE DES TABLES")
        for table, result in report["table_structure"].items():
            status_icon = "✅" if result["status"] == "OK" else "⚠️" if result["status"] == "INCOMPLETE" else "❌"
            print(f"   {status_icon} {table}: {result['status']}")
            
            if result["missing_columns"]:
                print(f"      Colonnes manquantes: {', '.join(result['missing_columns'])}")
        print()
        
        # Format des métadonnées
        print("3. FORMAT DES MÉTADONNÉES")
        for table, result in report["metadata_format"].items():
            if not result["exists"]:
                print(f"   ❌ {table}: Table manquante")
                continue
                
            status_icon = "✅" if result["status"] == "OK" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"   {status_icon} {table}: {result['items_with_errors']}/{result['items_checked']} objets avec erreurs")
            
            if result["items_with_errors"] > 0:
                print(f"      Exemples d'erreurs:")
                for i, error in enumerate(result["error_details"][:3]):  # Afficher seulement les 3 premières erreurs
                    print(f"      - {error['name']} ({error['id']}): {', '.join(error['errors'])}")
                
                if len(result["error_details"]) > 3:
                    print(f"      ... et {len(result['error_details']) - 3} autres erreurs")
        print()
        
        # Compatibilité croisée
        if "cross_compatibility" in report:
            print("4. COMPATIBILITÉ CROISÉE")
            
            # Tables
            print("   Tables:")
            print(f"      ✅ Communes: {len(report['cross_compatibility']['tables']['common'])}")
            print(f"      ⚠️ Manquantes dans le jeu: {len(report['cross_compatibility']['tables']['missing_in_game'])}")
            if report['cross_compatibility']['tables']['missing_in_game']:
                print(f"         {', '.join(report['cross_compatibility']['tables']['missing_in_game'][:5])}")
                if len(report['cross_compatibility']['tables']['missing_in_game']) > 5:
                    print(f"         ... et {len(report['cross_compatibility']['tables']['missing_in_game']) - 5} autres")
            
            # Colonnes
            print("   Colonnes:")
            incomplete_tables = [table for table, result in report["cross_compatibility"]["columns"].items() 
                               if result["status"] != "OK"]
            
            if incomplete_tables:
                print(f"      ⚠️ Tables avec colonnes incompatibles: {len(incomplete_tables)}")
                for table in incomplete_tables[:3]:  # Afficher seulement les 3 premières tables
                    result = report["cross_compatibility"]["columns"][table]
                    print(f"         - {table}: {len(result['missing_in_game'])} colonnes manquantes dans le jeu")
                    print(f"           {', '.join(result['missing_in_game'][:3])}")
                    if len(result['missing_in_game']) > 3:
                        print(f"           ... et {len(result['missing_in_game']) - 3} autres")
                
                if len(incomplete_tables) > 3:
                    print(f"         ... et {len(incomplete_tables) - 3} autres tables")
            else:
                print("      ✅ Toutes les colonnes sont compatibles")
        
        print("\n===========================================\n")
    
    def fix_all_issues(self) -> Dict[str, Any]:
        """
        Corrige tous les problèmes de compatibilité identifiés.
        
        Returns:
            Dictionnaire contenant les résultats des corrections
        """
        results = {
            "metadata_fixed": self.fix_metadata_format()
        }
        
        # Ajouter ici d'autres corrections si nécessaire
        
        return results


def main():
    """Fonction principale pour exécuter le vérificateur de compatibilité"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vérificateur de compatibilité YakTaa")
    parser.add_argument("--editor-db", required=True, help="Chemin vers la base de données de l'éditeur de monde")
    parser.add_argument("--game-db", help="Chemin vers la base de données du jeu principal (optionnel)")
    parser.add_argument("--fix", action="store_true", help="Corriger automatiquement les problèmes identifiés")
    parser.add_argument("--report", action="store_true", help="Générer un rapport détaillé")
    
    args = parser.parse_args()
    
    checker = CompatibilityChecker(args.editor_db, args.game_db)
    
    if args.fix:
        print("Correction des problèmes de compatibilité...")
        results = checker.fix_all_issues()
        print(f"Métadonnées corrigées pour {sum(r['items_fixed'] for r in results['metadata_fixed'].values() if 'items_fixed' in r)} objets")
    
    if args.report or not args.fix:
        report = checker.generate_report()
        checker.print_report(report)
    
    return 0


if __name__ == "__main__":
    main()
