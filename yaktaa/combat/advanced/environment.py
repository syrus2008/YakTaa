"""
Système d'environnement de combat pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.Environment")

class EnvironmentType(Enum):
    """Types d'environnements de combat"""
    URBAN = auto()      # Environnement urbain
    CORPORATE = auto()  # Intérieur d'entreprise
    INDUSTRIAL = auto() # Zone industrielle
    DIGITAL = auto()    # Environnement virtuel
    WASTELAND = auto()  # Terrain vague
    UNDERGROUND = auto() # Souterrain

class InteractableType(Enum):
    """Types d'éléments interactifs"""
    COVER = auto()      # Couverture
    TERMINAL = auto()   # Terminal informatique
    EXPLOSIVE = auto()  # Élément explosif
    TRAP = auto()       # Piège
    HEALTH = auto()     # Station de soins
    WEAPON = auto()     # Arme ou munitions
    UTILITY = auto()    # Utilitaire divers

class CombatEnvironmentSystem:
    """
    Système qui gère l'environnement de combat et ses interactions
    """
    
    def __init__(self):
        """Initialise le système d'environnement de combat"""
        self.environment_type = EnvironmentType.URBAN
        self.interactables = {}  # ID -> élément interactif
        self.destructibles = {}  # ID -> élément destructible
        self.environment_effects = {}  # Type -> effet
        self.terrain_modifiers = {}  # Position -> modificateur
        
        logger.debug("Système d'environnement de combat initialisé")
    
    def set_environment_type(self, env_type: EnvironmentType) -> None:
        """
        Définit le type d'environnement de combat
        
        Args:
            env_type: Type d'environnement
        """
        self.environment_type = env_type
        
        # Appliquer les effets spécifiques à l'environnement
        self._apply_environment_effects(env_type)
        
        logger.debug(f"Environnement de combat défini: {env_type.name}")
    
    def _apply_environment_effects(self, env_type: EnvironmentType) -> None:
        """Applique les effets spécifiques à un type d'environnement"""
        # Réinitialiser les effets
        self.environment_effects = {}
        
        # Définir les effets en fonction du type d'environnement
        if env_type == EnvironmentType.URBAN:
            self.environment_effects = {
                "cover_density": 0.7,  # Densité de couvertures
                "visibility": 0.8,     # Visibilité
                "movement_penalty": 0.1,  # Pénalité de mouvement
                "ambient_effects": ["rain", "night"]  # Effets ambiants possibles
            }
        elif env_type == EnvironmentType.CORPORATE:
            self.environment_effects = {
                "cover_density": 0.5,
                "visibility": 1.0,
                "movement_penalty": 0.0,
                "hackable_density": 0.8,  # Densité d'éléments piratables
                "ambient_effects": ["alarm", "security_cameras"]
            }
        elif env_type == EnvironmentType.INDUSTRIAL:
            self.environment_effects = {
                "cover_density": 0.6,
                "visibility": 0.7,
                "movement_penalty": 0.2,
                "hazard_density": 0.6,  # Densité de dangers
                "ambient_effects": ["toxic", "machinery", "fire"]
            }
        elif env_type == EnvironmentType.DIGITAL:
            self.environment_effects = {
                "cover_density": 0.3,
                "visibility": 1.0,
                "movement_penalty": 0.0,
                "data_streams": 0.9,  # Densité de flux de données
                "ambient_effects": ["glitches", "firewalls", "data_corruption"]
            }
        elif env_type == EnvironmentType.WASTELAND:
            self.environment_effects = {
                "cover_density": 0.3,
                "visibility": 0.9,
                "movement_penalty": 0.3,
                "radiation": 0.5,  # Niveau de radiation
                "ambient_effects": ["dust", "radiation", "extreme_weather"]
            }
        elif env_type == EnvironmentType.UNDERGROUND:
            self.environment_effects = {
                "cover_density": 0.4,
                "visibility": 0.5,
                "movement_penalty": 0.2,
                "ambient_effects": ["darkness", "confined", "echoes"]
            }
    
    def add_interactable(self, interactable_id: str, interactable_type: InteractableType, 
                        position: Tuple[int, int], properties: Dict[str, Any]) -> None:
        """
        Ajoute un élément interactif à l'environnement
        
        Args:
            interactable_id: Identifiant de l'élément
            interactable_type: Type d'élément
            position: Position (x, y)
            properties: Propriétés spécifiques
        """
        self.interactables[interactable_id] = {
            "id": interactable_id,
            "type": interactable_type,
            "position": position,
            "properties": properties,
            "used": False,
            "health": properties.get("health", 100)
        }
        
        logger.debug(f"Élément interactif ajouté: {interactable_id} ({interactable_type.name})")
    
    def add_destructible(self, destructible_id: str, position: Tuple[int, int], 
                        health: int, properties: Dict[str, Any]) -> None:
        """
        Ajoute un élément destructible à l'environnement
        
        Args:
            destructible_id: Identifiant de l'élément
            position: Position (x, y)
            health: Points de vie
            properties: Propriétés spécifiques
        """
        self.destructibles[destructible_id] = {
            "id": destructible_id,
            "position": position,
            "health": health,
            "max_health": health,
            "properties": properties,
            "destroyed": False
        }
        
        logger.debug(f"Élément destructible ajouté: {destructible_id}")
    
    def add_terrain_modifier(self, position: Tuple[int, int], modifier_type: str, 
                           strength: float, radius: int = 1) -> None:
        """
        Ajoute un modificateur de terrain
        
        Args:
            position: Position centrale (x, y)
            modifier_type: Type de modificateur
            strength: Force du modificateur
            radius: Rayon d'effet
        """
        # Générer les positions affectées
        affected_positions = []
        for x in range(position[0] - radius, position[0] + radius + 1):
            for y in range(position[1] - radius, position[1] + radius + 1):
                # Vérifier si la position est dans le rayon
                if ((x - position[0]) ** 2 + (y - position[1]) ** 2) <= radius ** 2:
                    affected_positions.append((x, y))
        
        # Ajouter le modificateur pour chaque position
        for pos in affected_positions:
            if pos not in self.terrain_modifiers:
                self.terrain_modifiers[pos] = {}
                
            self.terrain_modifiers[pos][modifier_type] = strength
        
        logger.debug(f"Modificateur de terrain ajouté: {modifier_type} (force: {strength}, rayon: {radius})")
    
    def get_interactable_at_position(self, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """
        Récupère l'élément interactif à une position
        
        Args:
            position: Position (x, y)
            
        Returns:
            Élément interactif ou None
        """
        for interactable_id, interactable in self.interactables.items():
            if interactable["position"] == position:
                return interactable
        return None
    
    def get_destructible_at_position(self, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """
        Récupère l'élément destructible à une position
        
        Args:
            position: Position (x, y)
            
        Returns:
            Élément destructible ou None
        """
        for destructible_id, destructible in self.destructibles.items():
            if destructible["position"] == position:
                return destructible
        return None
    
    def get_terrain_modifiers_at_position(self, position: Tuple[int, int]) -> Dict[str, float]:
        """
        Récupère les modificateurs de terrain à une position
        
        Args:
            position: Position (x, y)
            
        Returns:
            Dictionnaire des modificateurs
        """
        return self.terrain_modifiers.get(position, {})
    
    def interact_with(self, actor: Any, interactable_id: str) -> Dict[str, Any]:
        """
        Interagit avec un élément de l'environnement
        
        Args:
            actor: L'acteur qui interagit
            interactable_id: Identifiant de l'élément
            
        Returns:
            Résultat de l'interaction
        """
        # Vérifier si l'élément existe
        if interactable_id not in self.interactables:
            return {"success": False, "message": f"Élément {interactable_id} introuvable"}
            
        interactable = self.interactables[interactable_id]
        
        # Vérifier si l'élément a déjà été utilisé
        if interactable.get("used", False) and not interactable["properties"].get("reusable", False):
            return {"success": False, "message": f"Élément {interactable_id} déjà utilisé"}
            
        # Traiter l'interaction en fonction du type
        interactable_type = interactable["type"]
        
        if interactable_type == InteractableType.COVER:
            # Utiliser une couverture
            return self._use_cover(actor, interactable)
        elif interactable_type == InteractableType.TERMINAL:
            # Utiliser un terminal
            return self._use_terminal(actor, interactable)
        elif interactable_type == InteractableType.EXPLOSIVE:
            # Déclencher un explosif
            return self._trigger_explosive(actor, interactable)
        elif interactable_type == InteractableType.TRAP:
            # Désarmer un piège
            return self._disarm_trap(actor, interactable)
        elif interactable_type == InteractableType.HEALTH:
            # Utiliser une station de soins
            return self._use_health_station(actor, interactable)
        elif interactable_type == InteractableType.WEAPON:
            # Récupérer une arme ou des munitions
            return self._pickup_weapon(actor, interactable)
        elif interactable_type == InteractableType.UTILITY:
            # Utiliser un élément utilitaire
            return self._use_utility(actor, interactable)
        else:
            return {"success": False, "message": f"Type d'interaction non pris en charge: {interactable_type}"}
    
    def _use_cover(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Utilise une couverture"""
        cover_quality = interactable["properties"].get("quality", "medium")
        
        # Déterminer le niveau de couverture
        cover_levels = {
            "low": 0.25,    # 25% de réduction des dégâts
            "medium": 0.5,  # 50% de réduction des dégâts
            "high": 0.75    # 75% de réduction des dégâts
        }
        
        damage_reduction = cover_levels.get(cover_quality, 0.5)
        
        # Appliquer l'effet de couverture à l'acteur
        if hasattr(actor, "combat_modifiers"):
            actor.combat_modifiers["cover_damage_reduction"] = damage_reduction
            
        # Marquer comme utilisé si nécessaire
        if not interactable["properties"].get("reusable", True):
            interactable["used"] = True
            
        return {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} utilise une couverture ({cover_quality})",
            "damage_reduction": damage_reduction
        }
    
    def _use_terminal(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Utilise un terminal informatique"""
        terminal_type = interactable["properties"].get("terminal_type", "standard")
        security_level = interactable["properties"].get("security_level", 1)
        
        # Vérifier les compétences en hacking
        hacking_skill = 0
        if hasattr(actor, "get_effective_stats"):
            hacking_skill = actor.get_effective_stats().get("hacking", 0)
        elif hasattr(actor, "hacking"):
            hacking_skill = actor.hacking
            
        # Déterminer si le hacking réussit
        success_chance = min(0.9, 0.5 + (hacking_skill - security_level) * 0.1)
        success = random.random() < success_chance
        
        if success:
            # Effets possibles du terminal
            effects = interactable["properties"].get("effects", {})
            
            result = {
                "success": True,
                "message": f"{getattr(actor, 'name', str(actor))} pirate le terminal avec succès",
                "effects": []
            }
            
            # Appliquer les effets
            for effect_type, effect_data in effects.items():
                if effect_type == "disable_security":
                    # Désactiver les systèmes de sécurité
                    result["effects"].append("Systèmes de sécurité désactivés")
                elif effect_type == "unlock_doors":
                    # Déverrouiller des portes
                    result["effects"].append("Portes déverrouillées")
                elif effect_type == "reveal_enemies":
                    # Révéler les positions ennemies
                    result["effects"].append("Positions ennemies révélées")
                elif effect_type == "activate_turret":
                    # Activer une tourelle
                    result["effects"].append("Tourelle activée")
                    
            # Marquer comme utilisé
            interactable["used"] = True
            
            return result
        else:
            # Échec du hacking
            alarm_triggered = random.random() < 0.5
            
            result = {
                "success": False,
                "message": f"{getattr(actor, 'name', str(actor))} échoue à pirater le terminal",
                "alarm_triggered": alarm_triggered
            }
            
            if alarm_triggered:
                result["message"] += " et déclenche une alarme"
                
            return result
    
    def _trigger_explosive(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Déclenche un élément explosif"""
        explosive_power = interactable["properties"].get("power", 50)
        radius = interactable["properties"].get("radius", 2)
        position = interactable["position"]
        
        # Marquer comme utilisé
        interactable["used"] = True
        
        # Créer l'explosion
        return {
            "success": True,
            "message": f"{getattr(actor, 'name', str(actor))} déclenche une explosion",
            "explosion": {
                "position": position,
                "power": explosive_power,
                "radius": radius,
                "damage_type": "EXPLOSIVE"
            }
        }
    
    def _disarm_trap(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Désarme un piège"""
        trap_type = interactable["properties"].get("trap_type", "standard")
        difficulty = interactable["properties"].get("difficulty", 5)
        
        # Vérifier les compétences en désarmement
        disarm_skill = 0
        if hasattr(actor, "get_effective_stats"):
            disarm_skill = actor.get_effective_stats().get("security", 0)
        elif hasattr(actor, "security"):
            disarm_skill = actor.security
            
        # Déterminer si le désarmement réussit
        success_chance = min(0.9, 0.5 + (disarm_skill - difficulty) * 0.1)
        success = random.random() < success_chance
        
        if success:
            # Marquer comme utilisé
            interactable["used"] = True
            
            return {
                "success": True,
                "message": f"{getattr(actor, 'name', str(actor))} désarme le piège avec succès"
            }
        else:
            # Le piège se déclenche
            trap_damage = interactable["properties"].get("damage", 20)
            
            # Appliquer les dégâts à l'acteur
            if hasattr(actor, "health"):
                actor.health -= trap_damage
                
            return {
                "success": False,
                "message": f"{getattr(actor, 'name', str(actor))} échoue à désarmer le piège et subit {trap_damage} dégâts",
                "damage": trap_damage
            }
    
    def _use_health_station(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Utilise une station de soins"""
        heal_amount = interactable["properties"].get("heal_amount", 50)
        charges = interactable["properties"].get("charges", 1)
        
        # Vérifier s'il reste des charges
        if charges <= 0:
            return {
                "success": False,
                "message": "La station de soins est vide"
            }
            
        # Appliquer les soins
        if hasattr(actor, "health") and hasattr(actor, "max_health"):
            old_health = actor.health
            actor.health = min(actor.health + heal_amount, actor.max_health)
            actual_healing = actor.health - old_health
            
            # Réduire le nombre de charges
            interactable["properties"]["charges"] = charges - 1
            
            # Marquer comme utilisé si plus de charges
            if interactable["properties"]["charges"] <= 0:
                interactable["used"] = True
                
            return {
                "success": True,
                "message": f"{getattr(actor, 'name', str(actor))} récupère {actual_healing} points de vie",
                "healing": actual_healing,
                "charges_left": interactable["properties"]["charges"]
            }
        else:
            return {
                "success": False,
                "message": "Impossible d'appliquer les soins"
            }
    
    def _pickup_weapon(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère une arme ou des munitions"""
        item_type = interactable["properties"].get("item_type", "weapon")
        item_id = interactable["properties"].get("item_id", None)
        
        if item_type == "weapon" and item_id:
            # Ajouter l'arme à l'inventaire
            if hasattr(actor, "add_item"):
                actor.add_item(item_id)
                
                # Marquer comme utilisé
                interactable["used"] = True
                
                return {
                    "success": True,
                    "message": f"{getattr(actor, 'name', str(actor))} récupère {item_id}",
                    "item_id": item_id
                }
        elif item_type == "ammo":
            # Ajouter des munitions
            ammo_type = interactable["properties"].get("ammo_type", "standard")
            ammo_amount = interactable["properties"].get("amount", 10)
            
            if hasattr(actor, "add_ammo"):
                actor.add_ammo(ammo_type, ammo_amount)
                
                # Marquer comme utilisé
                interactable["used"] = True
                
                return {
                    "success": True,
                    "message": f"{getattr(actor, 'name', str(actor))} récupère {ammo_amount} munitions {ammo_type}",
                    "ammo_type": ammo_type,
                    "amount": ammo_amount
                }
                
        return {
            "success": False,
            "message": "Impossible de récupérer l'objet"
        }
    
    def _use_utility(self, actor: Any, interactable: Dict[str, Any]) -> Dict[str, Any]:
        """Utilise un élément utilitaire"""
        utility_type = interactable["properties"].get("utility_type", "generic")
        
        # Effets en fonction du type d'utilitaire
        if utility_type == "generator":
            # Générateur d'énergie
            energy_amount = interactable["properties"].get("energy", 50)
            
            if hasattr(actor, "energy"):
                actor.energy = min(actor.energy + energy_amount, getattr(actor, "max_energy", 100))
                
                # Marquer comme utilisé
                interactable["used"] = True
                
                return {
                    "success": True,
                    "message": f"{getattr(actor, 'name', str(actor))} récupère {energy_amount} points d'énergie",
                    "energy": energy_amount
                }
        elif utility_type == "scanner":
            # Scanner de zone
            scan_radius = interactable["properties"].get("radius", 5)
            
            # Marquer comme utilisé
            interactable["used"] = True
            
            return {
                "success": True,
                "message": f"{getattr(actor, 'name', str(actor))} active un scanner",
                "scan_radius": scan_radius,
                "position": interactable["position"]
            }
                
        return {
            "success": False,
            "message": f"Type d'utilitaire non pris en charge: {utility_type}"
        }
    
    def damage_destructible(self, destructible_id: str, damage: int, damage_type: str = "PHYSICAL") -> Dict[str, Any]:
        """
        Endommage un élément destructible
        
        Args:
            destructible_id: Identifiant de l'élément
            damage: Quantité de dégâts
            damage_type: Type de dégâts
            
        Returns:
            Résultat des dégâts
        """
        # Vérifier si l'élément existe
        if destructible_id not in self.destructibles:
            return {"success": False, "message": f"Élément {destructible_id} introuvable"}
            
        destructible = self.destructibles[destructible_id]
        
        # Vérifier si l'élément est déjà détruit
        if destructible.get("destroyed", False):
            return {"success": False, "message": f"Élément {destructible_id} déjà détruit"}
            
        # Appliquer les résistances si spécifiées
        resistance = destructible["properties"].get(f"resistance_{damage_type.lower()}", 0)
        final_damage = max(1, int(damage * (1 - resistance / 100)))
        
        # Appliquer les dégâts
        destructible["health"] -= final_damage
        
        # Vérifier si l'élément est détruit
        if destructible["health"] <= 0:
            destructible["destroyed"] = True
            
            # Effets de destruction
            destruction_effects = destructible["properties"].get("destruction_effects", {})
            
            result = {
                "success": True,
                "message": f"Élément {destructible_id} détruit",
                "destroyed": True,
                "effects": []
            }
            
            # Appliquer les effets de destruction
            for effect_type, effect_data in destruction_effects.items():
                if effect_type == "explosion":
                    # Créer une explosion
                    result["effects"].append({
                        "type": "explosion",
                        "position": destructible["position"],
                        "power": effect_data.get("power", 30),
                        "radius": effect_data.get("radius", 2)
                    })
                elif effect_type == "debris":
                    # Créer des débris
                    result["effects"].append({
                        "type": "debris",
                        "position": destructible["position"],
                        "damage": effect_data.get("damage", 10),
                        "radius": effect_data.get("radius", 1)
                    })
                elif effect_type == "smoke":
                    # Créer de la fumée
                    result["effects"].append({
                        "type": "smoke",
                        "position": destructible["position"],
                        "radius": effect_data.get("radius", 2),
                        "duration": effect_data.get("duration", 3)
                    })
                    
                    # Ajouter un modificateur de terrain pour la fumée
                    self.add_terrain_modifier(
                        destructible["position"],
                        "visibility",
                        -0.5,  # Réduction de 50% de la visibilité
                        effect_data.get("radius", 2)
                    )
                    
            return result
        else:
            # L'élément est endommagé mais pas détruit
            return {
                "success": True,
                "message": f"Élément {destructible_id} endommagé",
                "damage": final_damage,
                "health_remaining": destructible["health"],
                "health_percentage": destructible["health"] / destructible["max_health"] * 100
            }
    
    def apply_environment_damage(self, position: Tuple[int, int], radius: int, 
                               damage: int, damage_type: str) -> Dict[str, Any]:
        """
        Applique des dégâts environnementaux dans une zone
        
        Args:
            position: Position centrale (x, y)
            radius: Rayon d'effet
            damage: Quantité de dégâts
            damage_type: Type de dégâts
            
        Returns:
            Résultat des dégâts
        """
        affected_destructibles = []
        
        # Trouver les éléments destructibles dans la zone
        for destructible_id, destructible in self.destructibles.items():
            # Calculer la distance
            dest_pos = destructible["position"]
            distance = ((dest_pos[0] - position[0]) ** 2 + (dest_pos[1] - position[1]) ** 2) ** 0.5
            
            # Vérifier si l'élément est dans le rayon
            if distance <= radius:
                # Calculer les dégâts en fonction de la distance
                distance_factor = 1 - (distance / radius)
                final_damage = int(damage * distance_factor)
                
                # Appliquer les dégâts
                result = self.damage_destructible(destructible_id, final_damage, damage_type)
                
                affected_destructibles.append({
                    "id": destructible_id,
                    "damage": final_damage,
                    "destroyed": result.get("destroyed", False)
                })
        
        return {
            "success": True,
            "message": f"Dégâts environnementaux appliqués ({damage} {damage_type})",
            "affected_destructibles": affected_destructibles
        }
    
    def get_environment_modifiers(self) -> Dict[str, Any]:
        """
        Récupère les modificateurs globaux de l'environnement
        
        Returns:
            Dictionnaire des modificateurs
        """
        return self.environment_effects
    
    def reset_combat_environment(self) -> None:
        """Réinitialise l'environnement de combat"""
        self.interactables = {}
        self.destructibles = {}
        self.terrain_modifiers = {}
