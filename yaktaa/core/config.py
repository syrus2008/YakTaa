"""
Module de gestion de la configuration du jeu YakTaa
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("YakTaa.Config")

class Config:
    """Classe qui gère la configuration du jeu"""
    
    DEFAULT_CONFIG = {
        # Paramètres généraux
        "language": "fr",
        "fullscreen": False,
        "resolution": (1280, 720),
        "fps_limit": 60,
        "vsync": True,
        "show_fps": False,
        
        # Paramètres audio
        "master_volume": 0.8,
        "music_volume": 0.7,
        "sfx_volume": 0.9,
        "voice_volume": 1.0,
        "mute": False,
        
        # Paramètres de gameplay
        "difficulty": "normal",
        "auto_save": True,
        "auto_save_interval": 15,  # minutes
        "auto_save_on_quit": True,
        
        # Paramètres d'interface
        "ui_scale": 1.0,
        "ui_theme": "cyberpunk_dark",
        "terminal_font_size": 12,
        "terminal_font": "Cascadia Code",
        "terminal_opacity": 0.9,
        "show_tooltips": True,
        "animation_speed": 1.0,
        
        # Paramètres de développement
        "debug_mode": False,
        "dev_console": False,
        "log_level": "INFO"
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialise la configuration du jeu"""
        self.config_data = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file or self._get_default_config_path()
        
        # Chargement de la configuration existante
        self.load()
        
        logger.info("Configuration initialisée")
    
    def _get_default_config_path(self) -> str:
        """Retourne le chemin par défaut du fichier de configuration"""
        app_data = os.getenv('APPDATA') or os.path.expanduser('~/.config')
        config_dir = os.path.join(app_data, 'YakTaa')
        
        # Création du répertoire de configuration s'il n'existe pas
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, 'config.json')
    
    def load(self) -> bool:
        """Charge la configuration depuis le fichier"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                    # Mise à jour de la configuration avec les valeurs chargées
                    self.config_data.update(loaded_config)
                
                logger.info(f"Configuration chargée depuis {self.config_file}")
                return True
            else:
                logger.info("Aucun fichier de configuration trouvé, utilisation des valeurs par défaut")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}", exc_info=True)
            return False
    
    def save(self) -> bool:
        """Sauvegarde la configuration dans le fichier"""
        try:
            # Création du répertoire parent si nécessaire
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4)
            
            logger.info(f"Configuration sauvegardée dans {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}", exc_info=True)
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        self.config_data[key] = value
        
        # Sauvegarde automatique après modification
        self.save()
    
    def reset(self, key: Optional[str] = None) -> None:
        """Réinitialise une ou toutes les valeurs de configuration"""
        if key:
            if key in self.DEFAULT_CONFIG:
                self.config_data[key] = self.DEFAULT_CONFIG[key]
                logger.info(f"Configuration '{key}' réinitialisée à la valeur par défaut")
            else:
                logger.warning(f"Clé de configuration inconnue: {key}")
        else:
            self.config_data = self.DEFAULT_CONFIG.copy()
            logger.info("Configuration entièrement réinitialisée aux valeurs par défaut")
        
        # Sauvegarde après réinitialisation
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Retourne toutes les valeurs de configuration"""
        return self.config_data.copy()
