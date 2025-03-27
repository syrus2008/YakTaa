#!/usr/bin/env python
"""
Script de test pour la génération de monde YakTaa
Ce script génère un monde de test et vérifie que tous les éléments sont correctement créés
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("YakTaa.TestWorldGenerator")

# Importer les modules nécessaires
try:
    from world_generator import WorldGenerator
    from database import get_database
except ImportError as e:
    logger.error(f"Erreur d'importation: {str(e)}")
    logger.error("Assurez-vous que ce script est exécuté depuis le répertoire du projet YakTaa")
    sys.exit(1)

class WorldGeneratorTester:
    """Classe pour tester la génération de monde YakTaa"""
    
    def __init__(self, db_path: Optional[str] = None, output_dir: Optional[str] = None,
                 complexity: int = 3, seed: Optional[int] = None):
        """
        Initialise le testeur
        
        Args:
            db_path: Chemin vers la base de données
            output_dir: Répertoire de sortie pour les rapports
            complexity: Niveau de complexité du monde (1-5)
            seed: Graine pour la génération aléatoire
        """
        self.db_path = db_path
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results")
        self.complexity = complexity
        self.seed = seed
        
        # Créer le répertoire de sortie si nécessaire
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Générer un timestamp unique pour ce test
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialiser le générateur de monde
        self.generator = WorldGenerator(db_path=self.db_path)
        
        # Initialiser les statistiques
        self.stats = {
            "timestamp": self.timestamp,
            "complexity": self.complexity,
            "seed": self.seed,
            "duration": 0,
            "world_info": {},
            "counts": {},
            "element_examples": {},
            "errors": []
        }
    
    def run_test(self) -> Dict[str, Any]:
        """
        Exécute le test de génération de monde
        
        Returns:
            Dictionnaire contenant les statistiques du test
        """
        logger.info(f"Démarrage du test de génération (complexité: {self.complexity}, seed: {self.seed})")
        
        start_time = time.time()
        
        try:
            # Générer un nouveau monde
            world_id = self.generator.generate_world(
                name=f"Monde de test {self.timestamp}",
                complexity=self.complexity,
                author="YakTaa TestGenerator",
                seed=self.seed
            )
            
            # Stocker l'ID du monde généré
            self.stats["world_id"] = world_id
            
            # Analyser le monde généré
            try:
                self._analyze_world(world_id)
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse: {str(e)}")
                self.stats["errors"].append({
                    "phase": "analyze",
                    "message": str(e),
                    "type": str(type(e).__name__)
                })
            
        except Exception as e:
            logger.error(f"Erreur lors du test: {str(e)}")
            self.stats["errors"].append({
                "phase": "generation",
                "message": str(e),
                "type": str(type(e).__name__)
            })
        
        # Calculer la durée du test
        end_time = time.time()
        duration = end_time - start_time
        self.stats["duration"] = duration
        
        logger.info(f"Test terminé en {duration:.2f} secondes")
        
        # Sauvegarder les résultats
        self._save_results()
        
        return self.stats
    
    def _analyze_world(self, world_id: str) -> None:
        """
        Analyse le monde généré et collecte des statistiques
        
        Args:
            world_id: ID du monde à analyser
        """
        logger.info(f"Analyse du monde généré (ID: {world_id})")
        db = get_database(self.db_path)
        cursor = db.conn.cursor()
        
        # Récupérer les informations du monde
        try:
            world_info = db.get_world(world_id)
            if world_info:
                # S'assurer que toutes les valeurs sont sérialisables
                sanitized_world_info = {}
                for key, value in world_info.items():
                    if isinstance(value, (str, int, float, bool)):
                        sanitized_world_info[key] = value
                    elif value is None:
                        sanitized_world_info[key] = ""
                    else:
                        sanitized_world_info[key] = str(value)
                self.stats["world_info"] = sanitized_world_info
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des informations du monde: {str(e)}")
            self.stats["world_info"] = {"id": world_id, "error": str(e)}
        
        # Collecter les statistiques des différents éléments
        elements_to_check = [
            ("cities", "SELECT COUNT(*) FROM locations WHERE world_id = ? AND location_type = 'city'"),
            ("districts", "SELECT COUNT(*) FROM locations WHERE world_id = ? AND location_type = 'district'"),
            ("special_locations", "SELECT COUNT(*) FROM locations WHERE world_id = ? AND location_type = 'special'"),
            ("buildings", "SELECT COUNT(*) FROM buildings WHERE world_id = ?"),
            ("connections", "SELECT COUNT(*) FROM connections WHERE world_id = ?"),
            ("characters", "SELECT COUNT(*) FROM characters WHERE world_id = ?"),
            ("devices", "SELECT COUNT(*) FROM devices WHERE world_id = ?"),
            ("networks", "SELECT COUNT(*) FROM networks WHERE world_id = ?"),
            ("files", "SELECT COUNT(*) FROM files WHERE world_id = ?"),
            ("equipment", "SELECT COUNT(*) FROM equipment WHERE world_id = ?"),
            ("hardware_items", "SELECT COUNT(*) FROM items WHERE world_id = ? AND item_type = 'hardware'"),
            ("consumable_items", "SELECT COUNT(*) FROM items WHERE world_id = ? AND item_type = 'consumable'"),
            ("shops", "SELECT COUNT(*) FROM shops WHERE world_id = ?"),
            ("shop_inventory", "SELECT COUNT(*) FROM shop_inventory WHERE shop_id IN (SELECT id FROM shops WHERE world_id = ?)"),
            ("implants", "SELECT COUNT(*) FROM implants WHERE world_id = ?"),
            ("vulnerabilities", "SELECT COUNT(*) FROM vulnerabilities WHERE world_id = ?"),
            ("software", "SELECT COUNT(*) FROM software WHERE world_id = ?"),
            ("status_effects", "SELECT COUNT(*) FROM status_effects WHERE world_id = ?")
        ]
        
        counts = {}
        for element_name, query in elements_to_check:
            try:
                cursor.execute(query, (world_id,))
                count = cursor.fetchone()[0]
                counts[element_name] = count
                logger.info(f"  - {element_name}: {count}")
            except Exception as e:
                logger.warning(f"Erreur lors du comptage des {element_name}: {str(e)}")
                counts[element_name] = 0
                self.stats["errors"].append({
                    "phase": "analyze",
                    "element": element_name,
                    "message": str(e),
                    "type": str(type(e).__name__)
                })
        
        self.stats["counts"] = counts
        
        # Collecter des exemples pour chaque type d'élément
        elements_examples = [
            ("characters", "SELECT id, name, description, faction, profession, enemy_type, health, damage, accuracy FROM characters WHERE world_id = ? LIMIT 3"),
            ("equipment", "SELECT id, name, description, type, subtype, rarity, price FROM equipment WHERE world_id = ? LIMIT 3"),
            ("implants", "SELECT id, name, description, type, manufacturer, price, rarity FROM implants WHERE world_id = ? LIMIT 3"),
            ("vulnerabilities", "SELECT id, name, description, type, difficulty, impact, rarity FROM vulnerabilities WHERE world_id = ? LIMIT 3"),
            ("software", "SELECT id, name, description, type, developer, price, is_malware FROM software WHERE world_id = ? LIMIT 3")
        ]
        
        examples = {}
        for element_name, query in elements_examples:
            try:
                cursor.execute(query, (world_id,))
                rows = cursor.fetchall()
                
                if rows:
                    # Récupérer les noms de colonnes
                    column_names = [desc[0] for desc in cursor.description]
                    
                    # Convertir les lignes en dictionnaires et s'assurer que les valeurs sont sérialisables
                    examples[element_name] = []
                    for row in rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            if value is None:
                                row_dict[column_names[i]] = ""
                            elif isinstance(value, (str, int, float, bool)):
                                row_dict[column_names[i]] = value
                            else:
                                row_dict[column_names[i]] = str(value)
                        examples[element_name].append(row_dict)
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des exemples de {element_name}: {str(e)}")
                self.stats["errors"].append({
                    "phase": "examples",
                    "element": element_name,
                    "message": str(e),
                    "type": str(type(e).__name__)
                })
        
        self.stats["element_examples"] = examples
        
        # Analyser les statistiques de combat des personnages
        try:
            cursor.execute("""
            SELECT enemy_type, COUNT(*) as count,
                   IFNULL(AVG(health), 0) as avg_health,
                   IFNULL(AVG(damage), 0) as avg_damage,
                   IFNULL(AVG(accuracy), 0) as avg_accuracy,
                   IFNULL(AVG(initiative), 0) as avg_initiative
            FROM characters
            WHERE world_id = ? AND enemy_type IS NOT NULL
            GROUP BY enemy_type
            """, (world_id,))
            
            rows = cursor.fetchall()
            if rows:
                column_names = [desc[0] for desc in cursor.description]
                combat_stats = []
                for row in rows:
                    # Créer un dictionnaire avec des valeurs par défaut pour les None
                    row_dict = {}
                    for i, value in enumerate(row):
                        if value is None:
                            # Utiliser une valeur par défaut appropriée selon le type de colonne
                            if column_names[i] in ["avg_health", "avg_damage", "avg_initiative", "count"]:
                                row_dict[column_names[i]] = 0
                            elif column_names[i] == "avg_accuracy":
                                row_dict[column_names[i]] = 0.0
                            elif column_names[i] == "enemy_type":
                                row_dict[column_names[i]] = "Inconnu"
                            else:
                                row_dict[column_names[i]] = ""
                        else:
                            row_dict[column_names[i]] = value
                    combat_stats.append(row_dict)
                self.stats["combat_stats"] = combat_stats
        except Exception as e:
            logger.warning(f"Erreur lors de l'analyse des statistiques de combat: {str(e)}")
            self.stats["errors"].append({
                "phase": "combat_stats",
                "message": str(e),
                "type": str(type(e).__name__)
            })
            # S'assurer que combat_stats existe pour éviter des erreurs ultérieures
            self.stats["combat_stats"] = []
    
    def _make_json_serializable(self, obj):
        """
        Convertit récursivement un objet en types JSON sérialisables
        """
        if obj is None:
            return ""
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        else:
            # Pour tout autre type d'objet, le convertir en chaîne
            try:
                return str(obj)
            except:
                return "Non-serializable object"

    def _save_results(self) -> None:
        """Sauvegarde les résultats du test dans un fichier JSON"""
        result_file = os.path.join(self.output_dir, f"test_results_{self.timestamp}.json")
        
        # S'assurer que toutes les données sont sérialisables en JSON
        serializable_stats = self._make_json_serializable(self.stats)
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Résultats du test sauvegardés dans {result_file}")
        
        # Générer un rapport HTML
        self._generate_html_report(result_file)
    
    def _generate_html_report(self, json_file: str) -> None:
        """
        Génère un rapport HTML à partir des résultats du test
        
        Args:
            json_file: Chemin vers le fichier JSON des résultats
        """
        html_file = os.path.splitext(json_file)[0] + ".html"
        
        # S'assurer que les données peuvent être sérialisées en JSON
        try:
            # Tester la sérialisation avant d'ouvrir le fichier
            json_data = json.dumps(self.stats, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sérialisation JSON: {str(e)}")
            return
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de génération YakTaa</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background-color: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .stats-card {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .error {
            color: #e74c3c;
        }
        .success {
            color: #2ecc71;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Rapport de génération YakTaa</h1>
            <p>Généré le {self.stats.get('timestamp')}</p>
        </div>
""")
            
            # Informations générales
            f.write(f"""
        <div class="stats-card">
            <h2>Informations générales</h2>
            <table>
                <tr>
                    <th>Propriété</th>
                    <th>Valeur</th>
                </tr>
                <tr>
                    <td>Complexité</td>
                    <td>{self.stats.get('complexity', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Seed</td>
                    <td>{self.stats.get('seed', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Durée</td>
                    <td>{self.stats.get('duration', 0):.2f} secondes</td>
                </tr>
            </table>
        </div>
""")
            
            # Informations sur le monde
            world_info = self.stats.get('world_info', {})
            if world_info:
                f.write(f"""
        <div class="stats-card">
            <h2>Informations sur le monde</h2>
            <table>
                <tr>
                    <th>Propriété</th>
                    <th>Valeur</th>
                </tr>
                <tr>
                    <td>Nom</td>
                    <td>{world_info.get('name', 'N/A')}</td>
                </tr>
                <tr>
                    <td>ID</td>
                    <td>{world_info.get('id', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Auteur</td>
                    <td>{world_info.get('author', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Date de création</td>
                    <td>{world_info.get('created_at', 'N/A')}</td>
                </tr>
            </table>
        </div>
""")
            
            # Statistiques des éléments
            counts = self.stats.get('counts', {})
            if counts:
                f.write("""
        <div class="stats-card">
            <h2>Statistiques des éléments</h2>
            <table>
                <tr>
                    <th>Élément</th>
                    <th>Nombre</th>
                </tr>""")
                
                for element, count in counts.items():
                    f.write(f"""
                <tr>
                    <td>{element}</td>
                    <td>{count}</td>
                </tr>""")
                
                f.write("""
            </table>
        </div>""")
            
            # Statistiques de combat
            if "combat_stats" in self.stats and self.stats["combat_stats"]:
                f.write("""
        <div class="stats-card">
            <h2>Statistiques de combat</h2>
            <table>
                <tr>
                    <th>Type d'ennemi</th>
                    <th>Nombre</th>
                    <th>Santé moyenne</th>
                    <th>Dégâts moyens</th>
                    <th>Précision moyenne</th>
                    <th>Initiative moyenne</th>
                </tr>""")
                
                for stat in self.stats["combat_stats"]:
                    f.write(f"""
                <tr>
                    <td>{stat.get('enemy_type', 'N/A')}</td>
                    <td>{stat.get('count', 0)}</td>
                    <td>{stat.get('avg_health', 0):.1f}</td>
                    <td>{stat.get('avg_damage', 0):.1f}</td>
                    <td>{stat.get('avg_accuracy', 0):.2f}</td>
                    <td>{stat.get('avg_initiative', 0):.1f}</td>
                </tr>""")
                
                f.write("""
            </table>
        </div>""")
            
            # Ajouter les erreurs si présentes
            if self.stats.get("errors"):
                f.write("""
        <div class="stats-card">
            <h2>Erreurs rencontrées</h2>
            <table>
                <tr>
                    <th>Phase</th>
                    <th>Élément</th>
                    <th>Type</th>
                    <th>Message</th>
                </tr>""")
                
                for error in self.stats["errors"]:
                    f.write(f"""
                <tr>
                    <td>{error.get('phase', 'N/A')}</td>
                    <td>{error.get('element', 'N/A')}</td>
                    <td>{error.get('type', 'N/A')}</td>
                    <td>{error.get('message', 'N/A')}</td>
                </tr>""")
                
                f.write("""
            </table>
        </div>""")
            
            # Pied de page
            f.write("""
    </div>
</body>
</html>
""")
        
        logger.info(f"Rapport HTML généré dans {html_file}")

def main():
    """Point d'entrée du script"""
    parser = argparse.ArgumentParser(description="Testeur de génération de monde YakTaa")
    parser.add_argument("--db-path", help="Chemin vers la base de données")
    parser.add_argument("--output-dir", help="Répertoire de sortie pour les rapports")
    parser.add_argument("--complexity", type=int, default=3, choices=[1, 2, 3, 4, 5],
                      help="Niveau de complexité du monde (1-5)")
    parser.add_argument("--seed", type=int, help="Seed pour la génération aléatoire")
    
    args = parser.parse_args()
    
    # Créer le testeur
    tester = WorldGeneratorTester(
        db_path=args.db_path,
        output_dir=args.output_dir,
        complexity=args.complexity,
        seed=args.seed
    )
    
    # Exécuter le test
    tester.run_test()

if __name__ == "__main__":
    main()
