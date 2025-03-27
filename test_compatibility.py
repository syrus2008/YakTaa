#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la compatibilité entre l'éditeur de monde et le jeu.
Ce script vérifie que les objets créés dans l'éditeur peuvent être correctement chargés par le jeu.
"""

import os
import sys
import json
import logging
import sqlite3
import pathlib
from typing import Dict, Any, List, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CompatibilityTest")

# Chemins vers les modules du jeu et de l'éditeur
GAME_PATH = pathlib.Path("./yaktaa")
EDITOR_PATH = pathlib.Path("./yaktaa_world_editor")
DB_PATH = EDITOR_PATH / "worlds.db"

# Ajouter les chemins au sys.path pour pouvoir importer les modules
sys.path.append(str(pathlib.Path.cwd()))

class CompatibilityTester:
    """Classe pour tester la compatibilité entre l'éditeur et le jeu"""
    
    def __init__(self, db_path: pathlib.Path):
        """
        Initialise le testeur de compatibilité.
        
        Args:
            db_path: Chemin vers la base de données de l'éditeur
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.test_world_id = None
        
        logger.info(f"Testeur de compatibilité initialisé avec la base de données: {db_path}")
    
    def connect_to_db(self) -> bool:
        """
        Se connecte à la base de données.
        
        Returns:
            True si la connexion a réussi, False sinon
        """
        try:
            logger.info(f"Tentative de connexion à la base de données: {self.db_path}")
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Vérifier si la connexion fonctionne
            self.cursor.execute("SELECT sqlite_version()")
            version = self.cursor.fetchone()
            logger.info(f"Connecté à la base de données SQLite version: {version[0]}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {e}")
            return False
    
    def verify_table_structure(self) -> Dict[str, bool]:
        """
        Vérifie la structure des tables importantes.
        
        Returns:
            Dictionnaire avec les résultats de la vérification pour chaque table
        """
        logger.info("Vérification de la structure des tables...")
        results = {}
        
        # Tables à vérifier
        tables = ["weapon_items", "clothing_items", "implant_items", "hardware_items", "software_items", "consumable_items"]
        
        for table in tables:
            try:
                # Vérifier si la table existe
                self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not self.cursor.fetchone():
                    logger.warning(f"Table '{table}' inexistante")
                    results[table] = False
                    continue
                
                # Vérifier les colonnes
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = {row[1]: row for row in self.cursor.fetchall()}
                
                # Colonnes requises pour chaque table
                required_columns = {
                    "weapon_items": ["id", "name", "description", "weapon_type", "stats", "metadata"],
                    "clothing_items": ["id", "name", "description", "clothing_type", "slots", "stats", "metadata"],
                    "implant_items": ["id", "name", "description", "implant_type", "metadata"],
                    "hardware_items": ["id", "name", "description", "hardware_type", "metadata"],
                    "software_items": ["id", "name", "description", "software_type", "metadata"],
                    "consumable_items": ["id", "name", "description", "consumable_type", "metadata"]
                }
                
                # Vérifier que toutes les colonnes requises sont présentes
                missing_columns = [col for col in required_columns.get(table, []) if col not in columns]
                
                if missing_columns:
                    logger.warning(f"Table {table} manque les colonnes: {', '.join(missing_columns)}")
                    results[table] = False
                else:
                    logger.info(f"Table {table} contient toutes les colonnes requises")
                    results[table] = True
                
            except sqlite3.Error as e:
                logger.error(f"Erreur lors de la vérification de la table {table}: {e}")
                results[table] = False
        
        return results

    def simulate_loading_items(self) -> Dict[str, Dict[str, bool]]:
        """
        Simule le chargement des objets par le jeu.
        
        Returns:
            Dictionnaire avec les résultats de simulation pour chaque type d'objet
        """
        logger.info("Simulation du chargement des objets par le jeu...")
        results = {}
        
        # Types d'objets à tester
        item_types = {
            "weapon": "weapon_items",
            "clothing": "clothing_items",
            "implant": "implant_items",
            "hardware": "hardware_items",
            "software": "software_items",
            "consumable": "consumable_items"
        }
        
        for item_type, table_name in item_types.items():
            item_results = {}
            
            try:
                # Récupérer quelques objets de ce type (max 5)
                self.cursor.execute(f"SELECT id, name, metadata FROM {table_name} LIMIT 5")
                items = self.cursor.fetchall()
                
                if not items:
                    logger.warning(f"Aucun objet trouvé dans la table {table_name}")
                    results[item_type] = {"success": False, "error": "No items found"}
                    continue
                
                for item_id, item_name, metadata_str in items:
                    try:
                        # Simuler le chargement de l'objet comme le ferait le jeu
                        metadata = json.loads(metadata_str) if metadata_str else {}
                        
                        # Vérifier les métadonnées essentielles selon le type d'objet
                        if item_type == "weapon":
                            required_fields = ["damage", "damage_type", "accuracy", "range"]
                        elif item_type == "clothing":
                            required_fields = ["protection", "armor_type", "slots"]
                        elif item_type == "implant":
                            required_fields = ["implant_type", "body_location"]
                        elif item_type == "hardware":
                            required_fields = ["hardware_type", "performance"]
                        elif item_type == "software":
                            required_fields = ["software_type", "version"]
                        elif item_type == "consumable":
                            required_fields = ["effect_type", "effect_power"]
                        else:
                            required_fields = []
                        
                        # Vérifier si toutes les métadonnées essentielles sont présentes
                        missing_fields = [field for field in required_fields if field not in metadata]
                        
                        if missing_fields:
                            logger.warning(f"Objet {item_name} (ID: {item_id}) manque les métadonnées: {', '.join(missing_fields)}")
                            item_results[item_id] = {"success": False, "missing_fields": missing_fields}
                        else:
                            logger.info(f"Objet {item_name} (ID: {item_id}) peut être chargé correctement")
                            item_results[item_id] = {"success": True}
                            
                    except json.JSONDecodeError:
                        logger.error(f"Erreur lors du décodage des métadonnées de l'objet {item_id}")
                        item_results[item_id] = {"success": False, "error": "Invalid JSON metadata"}
                    except Exception as e:
                        logger.error(f"Erreur lors de la simulation du chargement de l'objet {item_id}: {e}")
                        item_results[item_id] = {"success": False, "error": str(e)}
                
                # Récupérer le résultat global pour ce type d'objet
                success_count = sum(1 for result in item_results.values() if result["success"])
                total_count = len(item_results)
                
                results[item_type] = {
                    "success_rate": f"{success_count}/{total_count}",
                    "compatibility": success_count / total_count if total_count > 0 else 0,
                    "items": item_results
                }
                
            except sqlite3.Error as e:
                logger.error(f"Erreur lors de la simulation du chargement des objets de type {item_type}: {e}")
                results[item_type] = {"success": False, "error": str(e)}
        
        return results

    def test_metadata_json_compatibility(self) -> Dict[str, Any]:
        """
        Teste la compatibilité du format JSON des métadonnées.
        
        Returns:
            Résultats du test de compatibilité des métadonnées
        """
        logger.info("Test de compatibilité du format JSON des métadonnées...")
        results = {}
        
        # Tables à vérifier
        tables = ["weapon_items", "clothing_items", "implant_items", "hardware_items", "software_items", "consumable_items"]
        
        for table in tables:
            try:
                # Récupérer les métadonnées de quelques objets (max 5)
                self.cursor.execute(f"SELECT id, metadata FROM {table} LIMIT 5")
                items = self.cursor.fetchall()
                
                if not items:
                    logger.warning(f"Aucun objet trouvé dans la table {table}")
                    results[table] = {"success": False, "error": "No items found"}
                    continue
                
                item_results = {}
                for item_id, metadata_str in items:
                    try:
                        if metadata_str:
                            # Tenter de décoder le JSON
                            metadata = json.loads(metadata_str)
                            item_results[item_id] = {"success": True}
                        else:
                            logger.warning(f"Objet {item_id} n'a pas de métadonnées")
                            item_results[item_id] = {"success": False, "error": "No metadata"}
                    except json.JSONDecodeError:
                        logger.error(f"Erreur lors du décodage des métadonnées de l'objet {item_id}")
                        item_results[item_id] = {"success": False, "error": "Invalid JSON metadata"}
                
                # Récupérer le résultat global pour cette table
                success_count = sum(1 for result in item_results.values() if result["success"])
                total_count = len(item_results)
                
                results[table] = {
                    "success_rate": f"{success_count}/{total_count}",
                    "compatibility": success_count / total_count if total_count > 0 else 0,
                    "items": item_results
                }
                
            except sqlite3.Error as e:
                logger.error(f"Erreur lors du test des métadonnées pour la table {table}: {e}")
                results[table] = {"success": False, "error": str(e)}
        
        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Exécute tous les tests de compatibilité.
        
        Returns:
            Résultats de tous les tests
        """
        if not self.connect_to_db():
            return {"success": False, "error": "Failed to connect to database"}
        
        try:
            # 1. Vérifier la structure des tables
            table_structure_results = self.verify_table_structure()
            
            # 2. Simuler le chargement des objets
            loading_results = self.simulate_loading_items()
            
            # 3. Tester la compatibilité des métadonnées JSON
            metadata_results = self.test_metadata_json_compatibility()
            
            # Récupérer le résultat global
            structure_success = all(table_structure_results.values())
            loading_success_rate = sum(result["compatibility"] for result in loading_results.values() if isinstance(result, dict) and "compatibility" in result) / len(loading_results) if loading_results else 0
            metadata_success_rate = sum(result["compatibility"] for result in metadata_results.values() if isinstance(result, dict) and "compatibility" in result) / len(metadata_results) if metadata_results else 0
            
            overall_success = structure_success and loading_success_rate > 0.9 and metadata_success_rate > 0.9
            
            return {
                "success": overall_success,
                "summary": {
                    "table_structure": structure_success,
                    "loading_success_rate": loading_success_rate,
                    "metadata_success_rate": metadata_success_rate
                },
                "details": {
                    "table_structure": table_structure_results,
                    "loading_simulation": loading_results,
                    "metadata_compatibility": metadata_results
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des tests: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    tester = CompatibilityTester(DB_PATH)
    results = tester.run_all_tests()
    
    # Afficher un résumé des résultats
    if results.get("success"):
        logger.info("✅ TOUS LES TESTS DE COMPATIBILITÉ ONT RÉUSSI")
        logger.info(f"Structure des tables: {'✅ OK' if results['summary']['table_structure'] else '❌ ÉCHEC'}")
        logger.info(f"Simulation de chargement: {results['summary']['loading_success_rate']*100:.1f}% de réussite")
        logger.info(f"Compatibilité des métadonnées: {results['summary']['metadata_success_rate']*100:.1f}% de réussite")
    else:
        if "error" in results:
            logger.error(f"❌ ÉCHEC DES TESTS: {results['error']}")
        else:
            logger.error("❌ CERTAINS TESTS DE COMPATIBILITÉ ONT ÉCHOUÉ")
            logger.error(f"Structure des tables: {'✅ OK' if results['summary']['table_structure'] else '❌ ÉCHEC'}")
            logger.error(f"Simulation de chargement: {results['summary']['loading_success_rate']*100:.1f}% de réussite")
            logger.error(f"Compatibilité des métadonnées: {results['summary']['metadata_success_rate']*100:.1f}% de réussite")
    
    # Afficher les détails en cas d'échec
    if not results.get("success") and "details" in results:
        # Afficher les tables avec une structure incorrecte
        for table, success in results["details"]["table_structure"].items():
            if not success:
                logger.error(f"Table {table}: structure incorrecte")
        
        # Afficher les types d'objets avec des problèmes de chargement
        for item_type, loading_result in results["details"]["loading_simulation"].items():
            if isinstance(loading_result, dict) and "compatibility" in loading_result and loading_result["compatibility"] < 1.0:
                logger.error(f"Type d'objet {item_type}: problèmes de chargement ({loading_result['success_rate']})")
                # Afficher les objets problématiques
                for item_id, item_result in loading_result.get("items", {}).items():
                    if not item_result.get("success"):
                        logger.error(f"  - Objet {item_id}: {item_result.get('error', 'Champs manquants: ' + ', '.join(item_result.get('missing_fields', [])))}")
