"""
Système de fabrication d'armes spéciales pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

from .core import SpecialWeaponSystem, SpecialWeaponType, SpecialWeaponRarity

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialWeapons.Crafting")

class WeaponComponentType(Enum):
    """Types de composants d'armes spéciales"""
    FRAME = auto()        # Châssis/armature
    BARREL = auto()       # Canon
    POWER_SOURCE = auto() # Source d'énergie
    FOCUSING = auto()     # Système de ciblage/focalisation
    HANDLE = auto()       # Poignée
    MODIFIER = auto()     # Modificateur d'effets
    STABILIZER = auto()   # Stabilisateur
    AMPLIFIER = auto()    # Amplificateur

class WeaponCraftingSystem:
    """
    Système de fabrication d'armes spéciales
    """
    
    def __init__(self, special_weapon_system: SpecialWeaponSystem):
        """
        Initialise le système de fabrication d'armes
        
        Args:
            special_weapon_system: Le système d'armes spéciales à utiliser
        """
        self.weapon_system = special_weapon_system
        self.available_components = {}  # Type de composant -> liste de composants
        self.crafting_recipes = {}      # Recettes pour des armes prédéfinies
        self.crafted_weapons = {}       # (joueur_id, arme_id) -> info d'arme fabriquée
        
        # Initialiser les composants disponibles
        self._init_available_components()
        
        logger.debug("Système de fabrication d'armes spéciales initialisé")
    
    def _init_available_components(self) -> None:
        """Initialise les composants disponibles par défaut"""
        self.available_components = {
            WeaponComponentType.FRAME: [],
            WeaponComponentType.BARREL: [],
            WeaponComponentType.POWER_SOURCE: [],
            WeaponComponentType.FOCUSING: [],
            WeaponComponentType.HANDLE: [],
            WeaponComponentType.MODIFIER: [],
            WeaponComponentType.STABILIZER: [],
            WeaponComponentType.AMPLIFIER: []
        }
        
        # Ajouter les composants de base
        self._add_basic_frames()
        self._add_basic_barrels()
        self._add_basic_power_sources()
        self._add_basic_focusing_systems()
        self._add_basic_handles()
        self._add_basic_modifiers()
        
    def _add_basic_frames(self) -> None:
        """Ajoute les châssis de base"""
        frames = [
            {
                "id": "lightweight_frame",
                "name": "Châssis Léger",
                "description": "Châssis en alliage léger qui diminue le poids de l'arme",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "weight": -2,
                    "durability": -10
                },
                "crafting_difficulty": 2
            },
            {
                "id": "reinforced_frame",
                "name": "Châssis Renforcé",
                "description": "Châssis robuste qui augmente la durabilité de l'arme",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.MELEE, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "weight": 2,
                    "durability": 30
                },
                "crafting_difficulty": 3
            },
            {
                "id": "balanced_frame",
                "name": "Châssis Équilibré",
                "description": "Châssis avec une distribution optimale du poids",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.MELEE, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "accuracy": 0.05
                },
                "crafting_difficulty": 2
            },
            {
                "id": "adaptive_frame",
                "name": "Châssis Adaptatif",
                "description": "Châssis avec des composants intelligents qui s'adaptent à l'utilisation",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.TECH, SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "weight": 0,
                    "durability": 15,
                    "accuracy": 0.03
                },
                "crafting_difficulty": 5
            }
        ]
        
        for frame in frames:
            self.available_components[WeaponComponentType.FRAME].append(frame)
    
    def _add_basic_barrels(self) -> None:
        """Ajoute les canons de base"""
        barrels = [
            {
                "id": "precision_barrel",
                "name": "Canon de Précision",
                "description": "Canon finement usiné qui améliore la précision",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "accuracy": 0.1,
                    "range": 3
                },
                "crafting_difficulty": 3
            },
            {
                "id": "heavy_barrel",
                "name": "Canon Lourd",
                "description": "Canon épais qui augmente les dégâts et la portée",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.PROJECTILE],
                "effects": {
                    "weight": 3,
                    "base_damage": 5,
                    "range": 5,
                    "accuracy": -0.05
                },
                "crafting_difficulty": 3
            },
            {
                "id": "accelerator_barrel",
                "name": "Canon Accélérateur",
                "description": "Canon avec système d'accélération magnétique",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE, SpecialWeaponType.TECH],
                "effects": {
                    "base_damage": 8,
                    "armor_penetration": 0.1
                },
                "crafting_difficulty": 4
            },
            {
                "id": "phase_barrel",
                "name": "Canon à Phase",
                "description": "Canon qui module la phase des projectiles pour traverser partiellement la matière",
                "rarity": SpecialWeaponRarity.EPIC,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "armor_penetration": 0.25,
                    "base_damage": -3
                },
                "crafting_difficulty": 7
            }
        ]
        
        for barrel in barrels:
            self.available_components[WeaponComponentType.BARREL].append(barrel)
    
    def _add_basic_power_sources(self) -> None:
        """Ajoute les sources d'énergie de base"""
        power_sources = [
            {
                "id": "standard_battery",
                "name": "Batterie Standard",
                "description": "Source d'énergie fiable et équilibrée",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.TECH],
                "effects": {
                    "max_charge": 100,
                    "charge_rate": 10
                },
                "crafting_difficulty": 2
            },
            {
                "id": "high_capacity_cell",
                "name": "Cellule Haute Capacité",
                "description": "Stocke plus d'énergie mais se recharge plus lentement",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.TECH],
                "effects": {
                    "max_charge": 150,
                    "charge_rate": 5
                },
                "crafting_difficulty": 4
            },
            {
                "id": "fast_charge_module",
                "name": "Module de Charge Rapide",
                "description": "Se recharge rapidement mais avec une capacité réduite",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.TECH],
                "effects": {
                    "max_charge": 75,
                    "charge_rate": 20
                },
                "crafting_difficulty": 4
            },
            {
                "id": "exotic_power_core",
                "name": "Noyau d'Énergie Exotique",
                "description": "Source d'énergie instable mais très puissante",
                "rarity": SpecialWeaponRarity.EPIC,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "max_charge": 200,
                    "charge_rate": 15,
                    "durability": -20,
                    "base_damage": 10
                },
                "crafting_difficulty": 6
            }
        ]
        
        for power_source in power_sources:
            self.available_components[WeaponComponentType.POWER_SOURCE].append(power_source)
    
    def _add_basic_focusing_systems(self) -> None:
        """Ajoute les systèmes de ciblage de base"""
        focusing_systems = [
            {
                "id": "standard_sights",
                "name": "Viseur Standard",
                "description": "Système de visée basique mais fiable",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "accuracy": 0.05
                },
                "crafting_difficulty": 2
            },
            {
                "id": "targeting_computer",
                "name": "Ordinateur de Ciblage",
                "description": "Système informatisé qui calcule les trajectoires optimales",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE, SpecialWeaponType.TECH],
                "effects": {
                    "accuracy": 0.15,
                    "critical_chance": 0.05
                },
                "crafting_difficulty": 5
            },
            {
                "id": "quantum_targeting",
                "name": "Ciblage Quantique",
                "description": "Prévoit les mouvements de la cible à l'échelle quantique",
                "rarity": SpecialWeaponRarity.EPIC,
                "compatibility": [SpecialWeaponType.TECH, SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "accuracy": 0.25,
                    "critical_chance": 0.1
                },
                "crafting_difficulty": 7
            }
        ]
        
        for focusing in focusing_systems:
            self.available_components[WeaponComponentType.FOCUSING].append(focusing)
    
    def _add_basic_handles(self) -> None:
        """Ajoute les poignées de base"""
        handles = [
            {
                "id": "ergonomic_grip",
                "name": "Prise Ergonomique",
                "description": "Conçue pour un confort et une stabilité optimaux",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE, SpecialWeaponType.MELEE],
                "effects": {
                    "accuracy": 0.05,
                    "reload_speed": 0.1
                },
                "crafting_difficulty": 2
            },
            {
                "id": "shock_absorbing_grip",
                "name": "Prise Anti-Recul",
                "description": "Absorbe les reculs et vibrations",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE],
                "effects": {
                    "accuracy": 0.1,
                    "durability": 10
                },
                "crafting_difficulty": 3
            },
            {
                "id": "neural_interface",
                "name": "Interface Neurale",
                "description": "Se connecte directement aux implants du porteur",
                "rarity": SpecialWeaponRarity.EPIC,
                "compatibility": [SpecialWeaponType.TECH, SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "accuracy": 0.2,
                    "reload_speed": 0.2,
                    "critical_chance": 0.05
                },
                "crafting_difficulty": 6
            }
        ]
        
        for handle in handles:
            self.available_components[WeaponComponentType.HANDLE].append(handle)
    
    def _add_basic_modifiers(self) -> None:
        """Ajoute les modificateurs de base"""
        modifiers = [
            {
                "id": "damage_enhancer",
                "name": "Amplificateur de Dégâts",
                "description": "Augmente les dégâts globaux",
                "rarity": SpecialWeaponRarity.UNCOMMON,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.PROJECTILE, SpecialWeaponType.MELEE],
                "effects": {
                    "base_damage": 8,
                    "durability": -5
                },
                "crafting_difficulty": 3
            },
            {
                "id": "elemental_converter",
                "name": "Convertisseur Élémentaire",
                "description": "Ajoute des effets élémentaires aux attaques",
                "rarity": SpecialWeaponRarity.RARE,
                "compatibility": [SpecialWeaponType.ENERGY, SpecialWeaponType.TECH],
                "effects": {
                    "damage_type": "ELEMENTAL",
                    "new_effect": {
                        "id": "elemental_damage",
                        "name": "Dégâts Élémentaires",
                        "description": "Inflige des dégâts élémentaires supplémentaires",
                        "category": "status",
                        "status_type": "ELEMENTAL_BURN",
                        "status_duration": 3,
                        "status_strength": 2,
                        "application_chance": 0.4,
                        "trigger_conditions": {
                            "trigger_chance": 0.3
                        },
                        "cooldown": 4
                    }
                },
                "crafting_difficulty": 5
            },
            {
                "id": "reality_distorter",
                "name": "Distordeur de Réalité",
                "description": "Module expérimental qui altère légèrement les lois de la physique",
                "rarity": SpecialWeaponRarity.LEGENDARY,
                "compatibility": [SpecialWeaponType.EXPERIMENTAL],
                "effects": {
                    "armor_penetration": 0.3,
                    "critical_damage": 0.5,
                    "durability": -15,
                    "new_effect": {
                        "id": "reality_breach",
                        "name": "Brèche de Réalité",
                        "description": "Crée une fissure dans la réalité qui ignore les défenses",
                        "category": "damage",
                        "damage": 40,
                        "damage_multiplier": 1.5,
                        "armor_penetration": 0.8,
                        "trigger_conditions": {
                            "trigger_chance": 0.15,
                            "cooldown_ready": True
                        },
                        "cooldown": 10
                    }
                },
                "crafting_difficulty": 10
            }
        ]
        
        for modifier in modifiers:
            self.available_components[WeaponComponentType.MODIFIER].append(modifier)
    
    def register_component(self, component_type: WeaponComponentType, 
                          component_data: Dict[str, Any]) -> bool:
        """
        Enregistre un nouveau composant
        
        Args:
            component_type: Type du composant
            component_data: Données du composant
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        if component_type not in self.available_components:
            logger.error(f"Type de composant non reconnu: {component_type}")
            return False
        
        # Vérifier si un composant avec cet ID existe déjà
        component_id = component_data.get("id")
        if not component_id:
            logger.error("Impossible d'enregistrer un composant sans ID")
            return False
            
        for existing in self.available_components[component_type]:
            if existing.get("id") == component_id:
                logger.warning(f"Un composant avec l'ID {component_id} existe déjà")
                return False
                
        # Ajouter le composant
        self.available_components[component_type].append(component_data)
        logger.info(f"Composant {component_data.get('name')} enregistré avec succès")
        return True
    
    def get_components_by_type(self, component_type: WeaponComponentType) -> List[Dict[str, Any]]:
        """
        Récupère tous les composants d'un type donné
        
        Args:
            component_type: Type de composant à récupérer
            
        Returns:
            Liste des composants du type spécifié
        """
        return self.available_components.get(component_type, [])
    
    def find_component(self, component_type: WeaponComponentType, 
                      component_id: str) -> Optional[Dict[str, Any]]:
        """
        Trouve un composant spécifique
        
        Args:
            component_type: Type du composant
            component_id: ID du composant
            
        Returns:
            Données du composant ou None s'il n'est pas trouvé
        """
        components = self.available_components.get(component_type, [])
        
        for component in components:
            if component.get("id") == component_id:
                return component
                
        return None
        
    def craft_weapon(self, player_id: str, components: Dict[WeaponComponentType, str], 
                    weapon_name: str, weapon_description: str) -> Dict[str, Any]:
        """
        Fabrique une arme personnalisée à partir de composants
        
        Args:
            player_id: ID du joueur
            components: Dictionnaire des composants à utiliser (type -> ID)
            weapon_name: Nom de l'arme
            weapon_description: Description de l'arme
            
        Returns:
            Résultat de la fabrication
        """
        # Vérifier les composants requis minimum
        required_components = [WeaponComponentType.FRAME, WeaponComponentType.BARREL]
        
        for req_type in required_components:
            if req_type not in components or not components[req_type]:
                return {
                    "success": False,
                    "message": f"Composant requis manquant: {req_type.name}"
                }
        
        # Récupérer les données de tous les composants
        component_data = {}
        component_objects = {}
        
        for comp_type, comp_id in components.items():
            comp = self.find_component(comp_type, comp_id)
            if not comp:
                return {
                    "success": False,
                    "message": f"Composant introuvable: {comp_id} (type: {comp_type.name})"
                }
            
            component_data[comp_type] = comp
            component_objects[comp_type.name.lower()] = comp
            
        # Vérifier la compatibilité entre les composants
        weapon_type = self._determine_weapon_type(component_data)
        
        if not weapon_type:
            return {
                "success": False,
                "message": "Impossible de déterminer un type d'arme compatible avec ces composants"
            }
            
        compatibility_issues = self._check_component_compatibility(component_data, weapon_type)
        if compatibility_issues:
            return {
                "success": False,
                "message": f"Problèmes de compatibilité: {', '.join(compatibility_issues)}"
            }
            
        # Calculer la difficulté de fabrication
        crafting_difficulty = self._calculate_crafting_difficulty(component_data)
        
        # Déterminer la rareté de l'arme
        weapon_rarity = self._determine_weapon_rarity(component_data)
        
        # Générer les statistiques de base de l'arme
        base_stats = self._generate_base_stats(weapon_type)
        
        # Appliquer les effets des composants
        final_stats = self._apply_component_effects(base_stats, component_data)
        
        # Générer les effets spéciaux
        weapon_effects = self._generate_weapon_effects(component_data, weapon_type, weapon_rarity)
        
        # Créer l'arme
        weapon_data = {
            "id": f"crafted_{weapon_type.name.lower()}_{random.randint(1000, 9999)}",
            "name": weapon_name,
            "description": weapon_description,
            "type": weapon_type,
            "rarity": weapon_rarity,
            **final_stats,
            "effects": weapon_effects,
            "crafted": True,
            "crafting_info": {
                "player_id": player_id,
                "components": {k.name: v.get("name") for k, v in component_data.items()},
                "crafting_difficulty": crafting_difficulty,
                "crafting_date": self._get_current_timestamp()
            }
        }
        
        # Enregistrer l'arme dans le système
        success = self.weapon_system.register_special_weapon(weapon_data)
        
        if not success:
            return {
                "success": False,
                "message": "Erreur lors de l'enregistrement de l'arme"
            }
            
        # Attribuer l'arme au joueur
        weapon_instance = self.weapon_system.give_weapon_to_player(player_id, weapon_data["id"])
        
        # Enregistrer dans les armes fabriquées
        instance_key = (player_id, weapon_data["id"])
        self.crafted_weapons[instance_key] = {
            "weapon_data": weapon_data,
            "components": {k.name: v.get("id") for k, v in component_data.items()},
            "crafting_date": self._get_current_timestamp()
        }
        
        logger.info(f"Arme {weapon_name} fabriquée avec succès pour le joueur {player_id}")
        
        return {
            "success": True,
            "message": f"Arme {weapon_name} fabriquée avec succès",
            "weapon_data": weapon_data,
            "weapon_instance": weapon_instance
        }
        
    def _get_current_timestamp(self) -> str:
        """
        Récupère un timestamp pour la fabrication
        
        Returns:
            Timestamp sous forme de chaîne de caractères
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _determine_weapon_type(self, components: Dict[WeaponComponentType, Dict[str, Any]]) -> Optional[SpecialWeaponType]:
        """
        Détermine le type d'arme en fonction des composants
        
        Args:
            components: Dictionnaire des composants
            
        Returns:
            Type d'arme ou None si incompatible
        """
        # Le châssis et le canon déterminent principalement le type
        frame = components.get(WeaponComponentType.FRAME)
        barrel = components.get(WeaponComponentType.BARREL)
        
        if not frame or not barrel:
            return None
            
        # Vérifier les compatibilités
        frame_compat = frame.get("compatibility", [])
        barrel_compat = barrel.get("compatibility", [])
        
        # Trouver les types communs
        common_types = set(frame_compat).intersection(set(barrel_compat))
        
        if not common_types:
            return None
            
        # Vérifier les autres composants pour affiner le choix
        for comp_type, comp in components.items():
            if comp_type not in [WeaponComponentType.FRAME, WeaponComponentType.BARREL]:
                comp_compat = comp.get("compatibility", [])
                if comp_compat:
                    common_types = common_types.intersection(set(comp_compat))
                    
                    if not common_types:
                        return None
        
        # Prioriser certains types
        priority_order = [
            SpecialWeaponType.EXPERIMENTAL,
            SpecialWeaponType.TECH,
            SpecialWeaponType.ENERGY,
            SpecialWeaponType.PROJECTILE,
            SpecialWeaponType.MELEE
        ]
        
        for weapon_type in priority_order:
            if weapon_type in common_types:
                return weapon_type
                
        # Si on arrive ici, prendre le premier type disponible
        return list(common_types)[0] if common_types else None
    
    def _check_component_compatibility(self, components: Dict[WeaponComponentType, Dict[str, Any]], 
                                      weapon_type: SpecialWeaponType) -> List[str]:
        """
        Vérifie la compatibilité entre les composants
        
        Args:
            components: Dictionnaire des composants
            weapon_type: Type d'arme déterminé
            
        Returns:
            Liste des problèmes de compatibilité
        """
        issues = []
        
        for comp_type, comp in components.items():
            comp_compat = comp.get("compatibility", [])
            
            if comp_compat and weapon_type not in comp_compat:
                issues.append(f"{comp.get('name')} n'est pas compatible avec le type d'arme {weapon_type.name}")
                
        # Vérifier les incompatibilités spécifiques entre composants
        # (À étendre selon les règles du jeu)
        
        return issues
    
    def _calculate_crafting_difficulty(self, components: Dict[WeaponComponentType, Dict[str, Any]]) -> int:
        """
        Calcule la difficulté globale de fabrication
        
        Args:
            components: Dictionnaire des composants
            
        Returns:
            Niveau de difficulté (1-10)
        """
        total_difficulty = 0
        component_count = 0
        
        for comp in components.values():
            difficulty = comp.get("crafting_difficulty", 1)
            total_difficulty += difficulty
            component_count += 1
            
        avg_difficulty = total_difficulty / max(1, component_count)
        
        # Ajouter un bonus pour les combinaisons complexes
        complexity_bonus = 0
        if component_count >= 5:
            complexity_bonus = 2
        elif component_count >= 3:
            complexity_bonus = 1
            
        return min(10, int(avg_difficulty + complexity_bonus))
    
    def _determine_weapon_rarity(self, components: Dict[WeaponComponentType, Dict[str, Any]]) -> SpecialWeaponRarity:
        """
        Détermine la rareté de l'arme en fonction des composants
        
        Args:
            components: Dictionnaire des composants
            
        Returns:
            Rareté de l'arme
        """
        # Convertir les raretés en valeurs numériques
        rarity_values = {
            SpecialWeaponRarity.UNCOMMON: 1,
            SpecialWeaponRarity.RARE: 2,
            SpecialWeaponRarity.EPIC: 3,
            SpecialWeaponRarity.LEGENDARY: 4,
            SpecialWeaponRarity.ARTIFACT: 5
        }
        
        # Calculer la rareté moyenne
        total_rarity = 0
        highest_rarity = 0
        component_count = 0
        
        for comp in components.values():
            rarity = comp.get("rarity", SpecialWeaponRarity.UNCOMMON)
            rarity_value = rarity_values.get(rarity, 1)
            
            total_rarity += rarity_value
            highest_rarity = max(highest_rarity, rarity_value)
            component_count += 1
            
        # La rareté dépend de la moyenne des composants et du composant le plus rare
        avg_rarity = total_rarity / max(1, component_count)
        final_rarity_value = int((avg_rarity * 0.7) + (highest_rarity * 0.3))
        
        # Conversion inverse
        for rarity, value in rarity_values.items():
            if value >= final_rarity_value:
                return rarity
                
        return SpecialWeaponRarity.UNCOMMON

    def _generate_base_stats(self, weapon_type: SpecialWeaponType) -> Dict[str, Any]:
        """
        Génère les statistiques de base pour un type d'arme
        
        Args:
            weapon_type: Type d'arme
            
        Returns:
            Statistiques de base
        """
        # Valeurs par défaut selon le type d'arme
        if weapon_type == SpecialWeaponType.ENERGY:
            return {
                "base_damage": 20,
                "damage_type": "ENERGY",
                "range": 18,
                "accuracy": 0.8,
                "max_charge": 100,
                "charge_rate": 10,
                "durability": 100,
                "weight": 3
            }
        elif weapon_type == SpecialWeaponType.MELEE:
            return {
                "base_damage": 35,
                "damage_type": "PHYSICAL",
                "range": 2,
                "accuracy": 0.9,
                "durability": 120,
                "weight": 4
            }
        elif weapon_type == SpecialWeaponType.PROJECTILE:
            return {
                "base_damage": 25,
                "damage_type": "PHYSICAL",
                "range": 20,
                "accuracy": 0.75,
                "max_charge": 30,  # Munitions
                "charge_rate": 6,   # Taux de rechargement
                "durability": 110,
                "weight": 5
            }
        elif weapon_type == SpecialWeaponType.TECH:
            return {
                "base_damage": 18,
                "damage_type": "TECH",
                "range": 15,
                "accuracy": 0.85,
                "max_charge": 80,
                "charge_rate": 12,
                "durability": 90,
                "weight": 3
            }
        elif weapon_type == SpecialWeaponType.EXPERIMENTAL:
            return {
                "base_damage": 30,
                "damage_type": "VARIABLE",
                "range": 16,
                "accuracy": 0.7,
                "max_charge": 120,
                "charge_rate": 8,
                "durability": 70,
                "weight": 6
            }
        else:
            # Type inconnu, valeurs génériques
            return {
                "base_damage": 20,
                "damage_type": "PHYSICAL",
                "range": 10,
                "accuracy": 0.75,
                "durability": 100,
                "weight": 4
            }
    
    def _apply_component_effects(self, base_stats: Dict[str, Any], 
                                components: Dict[WeaponComponentType, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Applique les effets des composants aux statistiques de base
        
        Args:
            base_stats: Statistiques de base
            components: Dictionnaire des composants
            
        Returns:
            Statistiques finales
        """
        final_stats = base_stats.copy()
        
        # Appliquer les effets de chaque composant
        for comp_type, comp in components.items():
            effects = comp.get("effects", {})
            
            for stat, value in effects.items():
                # Ignorer les effets spéciaux qui sont traités séparément
                if stat in ["effects", "new_effect"]:
                    continue
                    
                if stat in final_stats:
                    # Pour les stats numériques
                    if isinstance(value, (int, float)) and isinstance(final_stats[stat], (int, float)):
                        final_stats[stat] += value
                    else:
                        # Pour les stats non numériques (comme damage_type)
                        final_stats[stat] = value
                else:
                    # Nouvelle stat
                    final_stats[stat] = value
        
        # S'assurer que les valeurs restent dans des limites raisonnables
        if "accuracy" in final_stats:
            final_stats["accuracy"] = max(0.1, min(0.98, final_stats["accuracy"]))
            
        if "durability" in final_stats:
            final_stats["durability"] = max(30, final_stats["durability"])
            
        if "base_damage" in final_stats:
            final_stats["base_damage"] = max(5, final_stats["base_damage"])
        
        return final_stats
    
    def _generate_weapon_effects(self, components: Dict[WeaponComponentType, Dict[str, Any]],
                                weapon_type: SpecialWeaponType, 
                                weapon_rarity: SpecialWeaponRarity) -> List[Dict[str, Any]]:
        """
        Génère les effets spéciaux de l'arme en fonction des composants
        
        Args:
            components: Dictionnaire des composants
            weapon_type: Type d'arme
            weapon_rarity: Rareté de l'arme
            
        Returns:
            Liste des effets spéciaux
        """
        effects = []
        
        # Récupérer les effets directement spécifiés par les composants
        for comp in components.values():
            comp_effects = comp.get("effects", {})
            
            # Ajouter les nouveaux effets
            if "new_effect" in comp_effects:
                effects.append(comp_effects["new_effect"])
        
        # Si aucun effet n'a été ajouté, créer un effet de base selon le type d'arme
        if not effects:
            # Effet de base selon le type d'arme
            if weapon_type == SpecialWeaponType.ENERGY:
                effects.append({
                    "id": "energy_discharge",
                    "name": "Décharge d'énergie",
                    "description": "Libère une décharge d'énergie concentrée",
                    "category": "damage",
                    "damage": 30,
                    "damage_multiplier": 1.0,
                    "damage_type": "ENERGY",
                    "max_targets": 1,
                    "trigger_conditions": {
                        "min_charge": 50,
                        "trigger_chance": 1.0
                    },
                    "costs": {
                        "charge": 50
                    },
                    "cooldown": 3,
                    "duration": 1
                })
            elif weapon_type == SpecialWeaponType.MELEE:
                effects.append({
                    "id": "power_strike",
                    "name": "Frappe puissante",
                    "description": "Frappe avec une force accrue",
                    "category": "damage",
                    "damage": 45,
                    "damage_multiplier": 1.2,
                    "damage_type": "PHYSICAL",
                    "max_targets": 1,
                    "trigger_conditions": {
                        "trigger_chance": 0.3,
                        "cooldown_ready": True
                    },
                    "cooldown": 3,
                    "duration": 1
                })
            elif weapon_type == SpecialWeaponType.PROJECTILE:
                effects.append({
                    "id": "precision_shot",
                    "name": "Tir de précision",
                    "description": "Tir ciblé avec une précision accrue",
                    "category": "damage",
                    "damage": 35,
                    "damage_multiplier": 1.5,
                    "damage_type": "PHYSICAL",
                    "max_targets": 1,
                    "critical_chance_bonus": 0.2,
                    "trigger_conditions": {
                        "trigger_chance": 1.0,
                        "cooldown_ready": True
                    },
                    "cooldown": 4,
                    "duration": 1
                })
            elif weapon_type == SpecialWeaponType.TECH:
                effects.append({
                    "id": "system_disruption",
                    "name": "Disruption système",
                    "description": "Perturbe temporairement les systèmes de la cible",
                    "category": "status",
                    "status_type": "DISRUPTED",
                    "status_duration": 3,
                    "status_strength": 2,
                    "application_chance": 0.7,
                    "max_targets": 1,
                    "trigger_conditions": {
                        "min_charge": 40,
                        "trigger_chance": 1.0
                    },
                    "costs": {
                        "charge": 40
                    },
                    "cooldown": 5,
                    "duration": 3
                })
            elif weapon_type == SpecialWeaponType.EXPERIMENTAL:
                effects.append({
                    "id": "reality_shift",
                    "name": "Décalage de réalité",
                    "description": "Manipule brièvement la réalité autour de la cible",
                    "category": "damage",
                    "damage": 40,
                    "damage_multiplier": 1.3,
                    "damage_type": "VOID",
                    "max_targets": 6,
                    "aoe_radius": 5,
                    "pull_strength": 3,
                    "continuous_damage": True,
                    "damage_per_second": 10,
                    "trigger_conditions": {
                        "min_charge": 70,
                        "trigger_chance": 1.0
                    },
                    "costs": {
                        "charge": 70,
                        "durability": 8
                    },
                    "cooldown": 6,
                    "duration": 3
                })
        
        # Ajouter des effets bonus en fonction de la rareté
        if weapon_rarity == SpecialWeaponRarity.RARE:
            # 50% de chance d'avoir un effet bonus pour les armes rares
            if random.random() < 0.5:
                self._add_bonus_effect(effects, weapon_type, "minor")
                
        elif weapon_rarity == SpecialWeaponRarity.EPIC:
            # 100% de chance d'avoir un effet bonus pour les armes épiques
            self._add_bonus_effect(effects, weapon_type, "minor")
            
        elif weapon_rarity == SpecialWeaponRarity.LEGENDARY:
            # 100% d'avoir un effet mineur et 50% d'avoir un effet majeur
            self._add_bonus_effect(effects, weapon_type, "minor")
            if random.random() < 0.5:
                self._add_bonus_effect(effects, weapon_type, "major")
                
        elif weapon_rarity == SpecialWeaponRarity.ARTIFACT:
            # 100% d'avoir un effet mineur et un effet majeur
            self._add_bonus_effect(effects, weapon_type, "minor")
            self._add_bonus_effect(effects, weapon_type, "major")
        
        return effects
    
    def _add_bonus_effect(self, effects: List[Dict[str, Any]], 
                        weapon_type: SpecialWeaponType, power_level: str) -> None:
        """
        Ajoute un effet bonus à la liste des effets
        
        Args:
            effects: Liste des effets existants
            weapon_type: Type d'arme
            power_level: Niveau de puissance de l'effet ("minor" ou "major")
        """
        effect_options = []
        
        # Générer des options d'effets selon le type d'arme et le niveau de puissance
        if weapon_type == SpecialWeaponType.ENERGY:
            if power_level == "minor":
                effect_options = [
                    {
                        "id": f"energy_feedback_{random.randint(1000, 9999)}",
                        "name": "Rétroaction énergétique",
                        "description": "Les attaques rechargent légèrement l'arme",
                        "category": "utility",
                        "utility_type": "CHARGE_REFUND",
                        "amount": 10,
                        "trigger_conditions": {
                            "trigger_chance": 0.4,
                            "cooldown_ready": True
                        },
                        "cooldown": 3,
                        "duration": 1
                    }
                ]
            else:  # major
                effect_options = [
                    {
                        "id": f"plasma_cascade_{random.randint(1000, 9999)}",
                        "name": "Cascade de plasma",
                        "description": "Crée une réaction en chaîne d'explosions de plasma",
                        "category": "damage",
                        "damage": 20,
                        "damage_multiplier": 1.0,
                        "damage_type": "ENERGY",
                        "max_targets": 3,
                        "aoe_radius": 4,
                        "chain_count": 3,
                        "trigger_conditions": {
                            "min_charge": 60,
                            "trigger_chance": 0.3,
                            "cooldown_ready": True
                        },
                        "costs": {
                            "charge": 60
                        },
                        "cooldown": 6,
                        "duration": 1
                    }
                ]
        elif weapon_type == SpecialWeaponType.MELEE:
            if power_level == "minor":
                effect_options = [
                    {
                        "id": f"stance_shift_{random.randint(1000, 9999)}",
                        "name": "Changement de posture",
                        "description": "Change brièvement de posture pour une attaque différente",
                        "category": "utility",
                        "utility_type": "STANCE",
                        "stance_bonus": {
                            "critical_chance": 0.15
                        },
                        "trigger_conditions": {
                            "trigger_chance": 0.3,
                            "cooldown_ready": True
                        },
                        "cooldown": 4,
                        "duration": 2
                    }
                ]
            else:  # major
                effect_options = [
                    {
                        "id": f"whirlwind_attack_{random.randint(1000, 9999)}",
                        "name": "Attaque tourbillonnante",
                        "description": "Frappe tous les ennemis à proximité dans un mouvement circulaire",
                        "category": "damage",
                        "damage": 30,
                        "damage_multiplier": 0.8,
                        "damage_type": "PHYSICAL",
                        "max_targets": 5,
                        "aoe_radius": 3,
                        "trigger_conditions": {
                            "trigger_chance": 0.2,
                            "cooldown_ready": True
                        },
                        "cooldown": 8,
                        "duration": 1
                    }
                ]
        elif weapon_type == SpecialWeaponType.PROJECTILE:
            if power_level == "minor":
                effect_options = [
                    {
                        "id": f"quick_reload_{random.randint(1000, 9999)}",
                        "name": "Rechargement rapide",
                        "description": "Chance de recharger plus rapidement après un tir",
                        "category": "utility",
                        "utility_type": "RELOAD_SPEED",
                        "reload_bonus": 0.5,  # 50% plus rapide
                        "trigger_conditions": {
                            "trigger_chance": 0.3,
                            "cooldown_ready": True
                        },
                        "cooldown": 4,
                        "duration": 1
                    }
                ]
            else:  # major
                effect_options = [
                    {
                        "id": f"explosive_round_{random.randint(1000, 9999)}",
                        "name": "Munition explosive",
                        "description": "Tire une munition qui explose à l'impact",
                        "category": "damage",
                        "damage": 25,
                        "damage_multiplier": 1.2,
                        "damage_type": "EXPLOSIVE",
                        "max_targets": 4,
                        "aoe_radius": 3,
                        "trigger_conditions": {
                            "trigger_chance": 0.2,
                            "cooldown_ready": True
                        },
                        "cooldown": 7,
                        "duration": 1
                    }
                ]
        elif weapon_type == SpecialWeaponType.TECH:
            if power_level == "minor":
                effect_options = [
                    {
                        "id": f"targeting_assist_{random.randint(1000, 9999)}",
                        "name": "Assistance au ciblage",
                        "description": "Le système d'aide au ciblage améliore temporairement la précision",
                        "category": "utility",
                        "utility_type": "ACCURACY_BOOST",
                        "accuracy_bonus": 0.15,
                        "trigger_conditions": {
                            "trigger_chance": 0.4,
                            "cooldown_ready": True
                        },
                        "cooldown": 5,
                        "duration": 2
                    }
                ]
            else:  # major
                effect_options = [
                    {
                        "id": f"system_overload_{random.randint(1000, 9999)}",
                        "name": "Surcharge système",
                        "description": "Surcharge tous les systèmes de l'arme pour un tir dévastateur",
                        "category": "damage",
                        "damage": 50,
                        "damage_multiplier": 1.5,
                        "damage_type": "TECH",
                        "max_targets": 1,
                        "armor_penetration": 0.3,
                        "trigger_conditions": {
                            "min_charge": 80,
                            "trigger_chance": 0.2,
                            "cooldown_ready": True
                        },
                        "costs": {
                            "charge": 80,
                            "durability": 5
                        },
                        "cooldown": 10,
                        "duration": 1
                    }
                ]
        elif weapon_type == SpecialWeaponType.EXPERIMENTAL:
            if power_level == "minor":
                effect_options = [
                    {
                        "id": f"unstable_flux_{random.randint(1000, 9999)}",
                        "name": "Flux instable",
                        "description": "L'arme émet un flux d'énergie instable qui peut créer des effets aléatoires",
                        "category": "status",
                        "status_type": "RANDOM_EFFECT",
                        "status_duration": 2,
                        "status_strength": 2,
                        "application_chance": 0.3,
                        "max_targets": 1,
                        "trigger_conditions": {
                            "trigger_chance": 0.2,
                            "cooldown_ready": True
                        },
                        "cooldown": 6,
                        "duration": 2
                    }
                ]
            else:  # major
                effect_options = [
                    {
                        "id": f"dimensional_rift_{random.randint(1000, 9999)}",
                        "name": "Faille dimensionnelle",
                        "description": "Ouvre une petite faille dans l'espace-temps qui aspire et endommage les ennemis",
                        "category": "damage",
                        "damage": 35,
                        "damage_multiplier": 1.3,
                        "damage_type": "VOID",
                        "max_targets": 6,
                        "aoe_radius": 5,
                        "pull_strength": 3,
                        "continuous_damage": True,
                        "damage_per_second": 10,
                        "trigger_conditions": {
                            "min_charge": 90,
                            "trigger_chance": 0.15,
                            "cooldown_ready": True
                        },
                        "costs": {
                            "charge": 90,
                            "durability": 8
                        },
                        "cooldown": 12,
                        "duration": 3
                    }
                ]
        
        # Sélectionner un effet aléatoire parmi les options
        if effect_options:
            effect = random.choice(effect_options)
            effects.append(effect)
            
    def disassemble_weapon(self, player_id: str, weapon_id: str) -> Dict[str, Any]:
        """
        Démonte une arme fabriquée pour récupérer certains composants
        
        Args:
            player_id: ID du joueur
            weapon_id: ID de l'arme
            
        Returns:
            Résultat du démontage
        """
        # Vérifier si l'arme existe et appartient au joueur
        weapon_instance = self.weapon_system.get_player_weapon(player_id, weapon_id)
        if not weapon_instance:
            return {
                "success": False,
                "message": "Arme non trouvée ou n'appartient pas au joueur"
            }
            
        # Vérifier si c'est une arme fabriquée
        weapon_data = weapon_instance.get("weapon_data", {})
        if not weapon_data.get("crafted", False):
            return {
                "success": False,
                "message": "Seules les armes fabriquées peuvent être démontées"
            }
            
        # Récupérer les informations de fabrication
        instance_key = (player_id, weapon_id)
        crafting_info = self.crafted_weapons.get(instance_key)
        
        if not crafting_info:
            return {
                "success": False,
                "message": "Informations de fabrication non trouvées"
            }
            
        # Déterminer les composants récupérables
        components = crafting_info.get("components", {})
        if not components:
            return {
                "success": False,
                "message": "Aucun composant trouvé pour cette arme"
            }
            
        # Calcul de chance de récupération pour chaque composant
        recovered_components = []
        
        for comp_type_name, comp_id in components.items():
            try:
                comp_type = WeaponComponentType[comp_type_name]
            except KeyError:
                continue
                
            # Chance de récupération basée sur la durabilité de l'arme
            durability_percent = weapon_instance.get("durability", 0) / weapon_data.get("durability", 100)
            recovery_chance = 0.3 + (durability_percent * 0.5)  # Entre 30% et 80% selon la durabilité
            
            if random.random() < recovery_chance:
                # Composant récupéré
                comp = self.find_component(comp_type, comp_id)
                if comp:
                    recovered_components.append({
                        "type": comp_type.name,
                        "id": comp_id,
                        "name": comp.get("name", "Composant inconnu")
                    })
        
        # Supprimer l'arme
        self.weapon_system.remove_weapon_from_player(player_id, weapon_id)
        
        if instance_key in self.crafted_weapons:
            del self.crafted_weapons[instance_key]
            
        if not recovered_components:
            return {
                "success": True,
                "message": "Arme démontée mais aucun composant récupéré",
                "recovered": []
            }
            
        logger.info(f"Arme {weapon_id} démontée, {len(recovered_components)} composants récupérés")
        
        return {
            "success": True,
            "message": f"Arme démontée, {len(recovered_components)} composants récupérés",
            "recovered": recovered_components
        }
