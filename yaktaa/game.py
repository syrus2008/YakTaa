"""
Module principal du jeu YakTaa
Ce module contient la classe Game qui gère l'état global du jeu.
"""

import logging
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger("YakTaa.Game")

class Game:
    """
    Classe principale du jeu YakTaa
    Gère l'état global du jeu, les ressources du joueur, et coordonne
    les différents systèmes du jeu.
    """
    
    def __init__(self):
        """Initialise une nouvelle instance de jeu"""
        # Informations du joueur
        self.player_name = "Hacker"
        self.player_credits = 1000
        self.player_reputation = 0
        self.player_hacking_level = 1
        self.player_inventory = {}
        
        # État du jeu
        self.game_time = time.time()  # Temps de jeu en secondes
        self.game_day = 1
        self.game_hour = 8  # Commence à 8h du matin
        
        # Paramètres
        self.time_scale = 60  # 1 seconde réelle = 60 secondes dans le jeu
        
        # Statistiques
        self.stats = {
            "distance_traveled": 0.0,
            "locations_visited": 0,
            "hacks_completed": 0,
            "missions_completed": 0,
            "credits_earned": 0,
            "credits_spent": 0
        }
        
        logger.info("Nouvelle instance de jeu créée")
    
    def update(self, delta_time: float):
        """
        Met à jour l'état du jeu
        
        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour en secondes
        """
        # Mettre à jour le temps de jeu
        game_delta_time = delta_time * self.time_scale
        self.game_time += game_delta_time
        
        # Mettre à jour le jour et l'heure dans le jeu
        self.game_hour += game_delta_time / 3600
        while self.game_hour >= 24:
            self.game_hour -= 24
            self.game_day += 1
        
        logger.debug(f"Jeu mis à jour: Jour {self.game_day}, {self.game_hour:.1f}h")
    
    def add_credits(self, amount: int) -> int:
        """
        Ajoute des crédits au joueur
        
        Args:
            amount: Montant à ajouter (peut être négatif)
            
        Returns:
            Nouveau solde de crédits
        """
        self.player_credits += amount
        
        # Mettre à jour les statistiques
        if amount > 0:
            self.stats["credits_earned"] += amount
        else:
            self.stats["credits_spent"] += abs(amount)
        
        logger.info(f"Crédits ajoutés: {amount} (nouveau solde: {self.player_credits})")
        return self.player_credits
    
    def add_reputation(self, amount: int) -> int:
        """
        Ajoute de la réputation au joueur
        
        Args:
            amount: Montant à ajouter (peut être négatif)
            
        Returns:
            Nouvelle réputation
        """
        self.player_reputation += amount
        logger.info(f"Réputation ajoutée: {amount} (nouvelle réputation: {self.player_reputation})")
        return self.player_reputation
    
    def set_hacking_level(self, level: int) -> int:
        """
        Définit le niveau de hacking du joueur
        
        Args:
            level: Nouveau niveau de hacking
            
        Returns:
            Nouveau niveau de hacking
        """
        self.player_hacking_level = max(1, level)
        logger.info(f"Niveau de hacking défini: {self.player_hacking_level}")
        return self.player_hacking_level
    
    def get_formatted_time(self) -> str:
        """
        Renvoie l'heure du jeu formatée
        
        Returns:
            Heure formatée (ex: "Jour 1, 08:30")
        """
        hours = int(self.game_hour)
        minutes = int((self.game_hour - hours) * 60)
        return f"Jour {self.game_day}, {hours:02d}:{minutes:02d}"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Renvoie les statistiques du jeu
        
        Returns:
            Dictionnaire des statistiques
        """
        return self.stats
    
    def add_to_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """
        Ajoute un objet à l'inventaire du joueur
        
        Args:
            item_id: Identifiant de l'objet
            quantity: Quantité à ajouter
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        if item_id in self.player_inventory:
            self.player_inventory[item_id] += quantity
        else:
            self.player_inventory[item_id] = quantity
        
        logger.info(f"Objet ajouté à l'inventaire: {item_id} x{quantity}")
        return True
    
    def remove_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """
        Retire un objet de l'inventaire du joueur
        
        Args:
            item_id: Identifiant de l'objet
            quantity: Quantité à retirer
            
        Returns:
            True si le retrait a réussi, False sinon
        """
        if item_id not in self.player_inventory:
            logger.warning(f"Impossible de retirer l'objet {item_id}: non présent dans l'inventaire")
            return False
        
        if self.player_inventory[item_id] < quantity:
            logger.warning(f"Impossible de retirer {quantity} x {item_id}: quantité insuffisante")
            return False
        
        self.player_inventory[item_id] -= quantity
        
        # Supprimer l'entrée si la quantité est nulle
        if self.player_inventory[item_id] <= 0:
            del self.player_inventory[item_id]
        
        logger.info(f"Objet retiré de l'inventaire: {item_id} x{quantity}")
        return True
    
    def get_inventory(self) -> Dict[str, int]:
        """
        Renvoie l'inventaire du joueur
        
        Returns:
            Dictionnaire des objets et leurs quantités
        """
        return self.player_inventory.copy()
