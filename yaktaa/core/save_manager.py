"""
Module de gestion des sauvegardes du jeu YakTaa
"""

import os
import json
import time
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("YakTaa.SaveManager")

class SaveManager:
    """Classe qui gère les sauvegardes du jeu"""
    
    def __init__(self, save_dir: Optional[str] = None):
        """Initialise le gestionnaire de sauvegardes"""
        self.save_dir = save_dir or self._get_default_save_path()
        
        # Création du répertoire de sauvegarde s'il n'existe pas
        os.makedirs(self.save_dir, exist_ok=True)
        
        logger.info(f"Gestionnaire de sauvegardes initialisé (dossier: {self.save_dir})")
    
    def _get_default_save_path(self) -> str:
        """Retourne le chemin par défaut du dossier de sauvegarde"""
        app_data = os.getenv('APPDATA') or os.path.expanduser('~/.config')
        save_dir = os.path.join(app_data, 'YakTaa', 'saves')
        return save_dir
    
    def _get_save_file_path(self, save_id: str) -> str:
        """Retourne le chemin complet d'un fichier de sauvegarde"""
        return os.path.join(self.save_dir, f"{save_id}.json")
    
    def save_game(self, save_data: Dict[str, Any], save_id: Optional[str] = None) -> str:
        """Sauvegarde les données du jeu dans un fichier"""
        try:
            # Génération d'un ID de sauvegarde si non fourni
            if not save_id:
                timestamp = int(time.time())
                player_name = save_data.get("player", {}).get("name", "unknown")
                save_id = f"{player_name}_{timestamp}"
            
            # Ajout de métadonnées à la sauvegarde
            save_data["meta"] = {
                "save_id": save_id,
                "timestamp": time.time(),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": save_data.get("version", "0.1.0")
            }
            
            # Sauvegarde des données dans un fichier
            save_path = self._get_save_file_path(save_id)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            
            logger.info(f"Partie sauvegardée avec succès (ID: {save_id})")
            return save_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la partie: {str(e)}", exc_info=True)
            return ""
    
    def load_game(self, save_id: str) -> Dict[str, Any]:
        """Charge les données d'une sauvegarde"""
        try:
            save_path = self._get_save_file_path(save_id)
            
            if not os.path.exists(save_path):
                logger.error(f"Fichier de sauvegarde introuvable: {save_path}")
                return {}
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            logger.info(f"Partie chargée avec succès (ID: {save_id})")
            return save_data
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la partie: {str(e)}", exc_info=True)
            return {}
    
    def delete_save(self, save_id: str) -> bool:
        """Supprime une sauvegarde"""
        try:
            save_path = self._get_save_file_path(save_id)
            
            if not os.path.exists(save_path):
                logger.warning(f"Tentative de suppression d'une sauvegarde inexistante: {save_id}")
                return False
            
            os.remove(save_path)
            logger.info(f"Sauvegarde supprimée avec succès (ID: {save_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la sauvegarde: {str(e)}", exc_info=True)
            return False
    
    def get_all_saves(self) -> List[Dict[str, Any]]:
        """Récupère la liste de toutes les sauvegardes avec leurs métadonnées"""
        try:
            saves = []
            
            # Parcours de tous les fichiers de sauvegarde
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    save_id = filename[:-5]  # Suppression de l'extension .json
                    save_path = self._get_save_file_path(save_id)
                    
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                            
                            # Extraction des métadonnées
                            meta = save_data.get("meta", {})
                            player = save_data.get("player", {})
                            
                            saves.append({
                                "id": save_id,
                                "player_name": player.get("name", "Unknown"),
                                "level": player.get("level", 1),
                                "date": meta.get("date", "Unknown"),
                                "timestamp": meta.get("timestamp", 0),
                                "game_time": save_data.get("game_time", 0),
                                "location": save_data.get("world", {}).get("current_location", "Unknown")
                            })
                    except Exception as e:
                        logger.warning(f"Erreur lors de la lecture de la sauvegarde {save_id}: {str(e)}")
            
            # Tri des sauvegardes par date (la plus récente en premier)
            saves.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            return saves
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sauvegardes: {str(e)}", exc_info=True)
            return []
    
    def create_backup(self, backup_name: Optional[str] = None) -> bool:
        """Crée une sauvegarde complète du dossier de sauvegardes"""
        try:
            if not backup_name:
                backup_name = f"backup_{int(time.time())}"
            
            backup_dir = os.path.join(os.path.dirname(self.save_dir), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, f"{backup_name}.zip")
            
            # Création de l'archive ZIP
            shutil.make_archive(
                os.path.splitext(backup_path)[0],  # Nom sans extension
                'zip',
                self.save_dir
            )
            
            logger.info(f"Sauvegarde complète créée avec succès: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde complète: {str(e)}", exc_info=True)
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restaure une sauvegarde complète"""
        try:
            backup_dir = os.path.join(os.path.dirname(self.save_dir), 'backups')
            backup_path = os.path.join(backup_dir, f"{backup_name}.zip")
            
            if not os.path.exists(backup_path):
                logger.error(f"Archive de sauvegarde introuvable: {backup_path}")
                return False
            
            # Sauvegarde du dossier actuel avant restauration
            self.create_backup("pre_restore_backup")
            
            # Suppression du contenu actuel
            shutil.rmtree(self.save_dir)
            os.makedirs(self.save_dir, exist_ok=True)
            
            # Extraction de l'archive
            shutil.unpack_archive(backup_path, self.save_dir)
            
            logger.info(f"Sauvegarde restaurée avec succès depuis: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la sauvegarde: {str(e)}", exc_info=True)
            return False
