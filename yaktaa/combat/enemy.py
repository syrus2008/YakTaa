# YakTaa - Système d'ennemis pour le combat
import random
import logging
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union

# Configurer le logger
logger = logging.getLogger(__name__)

class EnemyType(Enum):
    """Types d'ennemis disponibles dans le jeu"""
    HUMAN = auto()       # Humain non augmenté
    GUARD = auto()       # Garde de sécurité légèrement augmenté
    CYBORG = auto()      # Humain fortement augmenté
    DRONE = auto()       # Drone autonome
    ROBOT = auto()       # Robot militaire ou de sécurité
    NETRUNNER = auto()   # Hacker spécialisé dans la cyberguerre
    MILITECH = auto()    # Soldat équipé de technologie militaire avancée
    BEAST = auto()       # Créature mutante ou biomodifiée

class Enemy:
    """Classe représentant un ennemi dans le jeu"""
    
    def __init__(self, name: str, enemy_type: EnemyType, level: int = 1):
        """Initialise un nouvel ennemi
        
        Args:
            name: Nom de l'ennemi
            enemy_type: Type d'ennemi
            level: Niveau de l'ennemi, affecte ses statistiques
        """
        self.name = name
        self.enemy_type = enemy_type
        self.level = level
        
        # Statistiques de base
        self.max_health = 50 + (level * 10)
        self.health = self.max_health
        self.damage = 5 + (level * 2)
        self.accuracy = 0.7 + (level * 0.02)  # entre 0 et 1
        self.initiative = 5 + (level // 2)
        
        # Résistances par défaut (pourcentage de réduction des dégâts)
        self.resistance_physical = 0
        self.resistance_energy = 0
        self.resistance_emp = 0
        self.resistance_biohazard = 0
        self.resistance_cyber = 0
        self.resistance_viral = 0
        self.resistance_nanite = 0
        
        # Vulnérabilités (multiplicateur de dégâts reçus)
        self.vulnerabilities = {}
        
        # Arme et équipement
        self.weapon = None
        self.implants = []
        
        # Initialiser les statistiques spécifiques au type
        self._initialize_type_specifics()
        
        # Mets à jour les métadonnées
        self.metadata = {}
        
        logger.info(f"Ennemi créé: {self.name} ({self.enemy_type.name}) niveau {self.level}")
    
    def _initialize_type_specifics(self):
        """Initialise les statistiques spécifiques au type d'ennemi"""
        if self.enemy_type == EnemyType.HUMAN:
            # Les humains sont équilibrés mais sans résistances spéciales
            pass
            
        elif self.enemy_type == EnemyType.GUARD:
            # Les gardes ont de meilleures armes et une légère résistance physique
            self.damage += 3
            self.resistance_physical = 10
            
        elif self.enemy_type == EnemyType.CYBORG:
            # Les cyborgs ont de bonnes résistances physiques mais sont vulnérables aux EMPs
            self.max_health += 20
            self.health = self.max_health
            self.resistance_physical = 20
            self.resistance_energy = 10
            self.vulnerabilities["EMP"] = 1.5  # +50% de dégâts EMP
            
        elif self.enemy_type == EnemyType.DRONE:
            # Les drones sont rapides et précis mais fragiles
            self.accuracy += 0.1
            self.initiative += 3
            self.resistance_physical = 5
            self.vulnerabilities["EMP"] = 2.0  # +100% de dégâts EMP
            self.vulnerabilities["VIRAL"] = 1.5  # +50% de dégâts viraux
            
        elif self.enemy_type == EnemyType.ROBOT:
            # Les robots sont résistants mais lents
            self.max_health += 30
            self.health = self.max_health
            self.initiative -= 2
            self.resistance_physical = 30
            self.resistance_energy = 15
            self.resistance_biohazard = 100  # Immunisé aux toxines
            self.vulnerabilities["EMP"] = 1.7  # +70% de dégâts EMP
            
        elif self.enemy_type == EnemyType.NETRUNNER:
            # Les netrunners sont spécialisés dans les attaques cyber
            self.damage -= 2  # Moins de dégâts physiques
            self.resistance_cyber = 50  # Forte résistance aux attaques cyber
            # Ils auront des capacités spéciales de piratage
            
        elif self.enemy_type == EnemyType.MILITECH:
            # Soldats avec équipement militaire de pointe
            self.max_health += 15
            self.health = self.max_health
            self.damage += 5
            self.accuracy += 0.05
            self.resistance_physical = 25
            self.resistance_energy = 25
            
        elif self.enemy_type == EnemyType.BEAST:
            # Créatures mutantes, fortes mais vulnérables à certaines attaques
            self.max_health += 40
            self.health = self.max_health
            self.damage += 7
            self.resistance_physical = 15
            self.resistance_viral = -20  # Vulnérabilité aux attaques virales (-20%)
            self.vulnerabilities["BIOHAZARD"] = 1.5  # +50% de dégâts biologiques
    
    def attack(self, target: Any) -> Dict[str, Any]:
        """Fait attaquer l'ennemi contre une cible
        
        Args:
            target: Cible de l'attaque (généralement le joueur)
            
        Returns:
            Résultat de l'attaque
        """
        # Vérifier si l'attaque touche (basé sur la précision)
        hit_roll = random.random()
        if hit_roll > self.accuracy:
            return {
                "success": False,
                "message": f"{self.name} rate son attaque contre {target.name}!",
                "damage": 0
            }
        
        # Calculer les dégâts de base
        base_damage = self.damage
        if self.weapon and hasattr(self.weapon, 'damage'):
            base_damage = self.weapon.damage
        
        # Vérifier s'il y a un coup critique (5% de chance de base)
        is_critical = random.random() < 0.05
        damage_multiplier = 1.5 if is_critical else 1.0
        
        # Calculer les dégâts finaux
        final_damage = int(base_damage * damage_multiplier)
        
        # Créer le message de résultat
        message = f"{self.name} attaque {target.name} et inflige {final_damage} dégâts"
        if is_critical:
            message += " (CRITIQUE!)"
        
        return {
            "success": True,
            "message": message,
            "damage": final_damage,
            "critical": is_critical,
            "type": "PHYSICAL"  # Type de dégâts par défaut
        }
    
    def take_damage(self, damage: int, damage_type: str = "PHYSICAL") -> Dict[str, Any]:
        """Fait subir des dégâts à l'ennemi
        
        Args:
            damage: Quantité de dégâts infligés
            damage_type: Type de dégâts (PHYSICAL, ENERGY, EMP, etc.)
            
        Returns:
            Résultat des dégâts appliqués
        """
        # Appliquer les résistances et vulnérabilités
        damage_multiplier = 1.0
        
        # Résistance spécifique au type
        resistance_attr = f"resistance_{damage_type.lower()}"
        if hasattr(self, resistance_attr):
            resistance = getattr(self, resistance_attr)
            damage_multiplier -= resistance / 100
        
        # Vulnérabilité spécifique au type
        if damage_type in self.vulnerabilities:
            damage_multiplier *= self.vulnerabilities[damage_type]
        
        # Calculer les dégâts finaux (minimum 1)
        final_damage = max(1, int(damage * damage_multiplier))
        self.health -= final_damage
        
        # Assurer que la santé ne descend pas en dessous de 0
        self.health = max(0, self.health)
        
        # Créer le message de résultat
        message = f"{self.name} subit {final_damage} dégâts de type {damage_type}"
        
        # Ajouter des détails sur les résistances/vulnérabilités
        if damage_multiplier != 1.0:
            if damage_multiplier < 1.0:
                message += f" (Résistance: {int((1-damage_multiplier)*100)}%)"
            else:
                message += f" (Vulnérabilité: +{int((damage_multiplier-1)*100)}%)"
        
        # Vérifier si l'ennemi est vaincu
        is_defeated = self.health <= 0
        if is_defeated:
            message += f" {self.name} est vaincu!"
        
        logger.info(message)
        
        return {
            "damage_taken": final_damage,
            "health_remaining": self.health,
            "is_defeated": is_defeated,
            "message": message
        }
    
    def get_special_action(self, target: Any) -> Optional[Dict[str, Any]]:
        """Renvoie une action spéciale que l'ennemi peut effectuer
        
        Certains types d'ennemis ont des capacités spéciales qu'ils peuvent utiliser
        de temps en temps pendant le combat.
        
        Args:
            target: Cible potentielle de l'action spéciale
            
        Returns:
            Détails de l'action spéciale, ou None si aucune action disponible
        """
        # Chance de base d'utiliser une capacité spéciale (20%)
        if random.random() > 0.2:
            return None
            
        # Actions spéciales selon le type d'ennemi
        if self.enemy_type == EnemyType.NETRUNNER:
            # Les netrunners peuvent tenter de pirater les implants
            return {
                "name": "Piratage d'implant",
                "type": "CYBER",
                "effect": "disable_implant",
                "duration": 2,  # tours
                "message": f"{self.name} tente de pirater les implants de {target.name}!"
            }
            
        elif self.enemy_type == EnemyType.ROBOT:
            # Les robots peuvent tirer une rafale (attaque sur zone)
            return {
                "name": "Tir en rafale",
                "type": "PHYSICAL",
                "damage": int(self.damage * 0.7),  # Moins de dégâts mais touche plusieurs fois
                "hits": random.randint(2, 4),
                "message": f"{self.name} effectue un tir en rafale!"
            }
            
        elif self.enemy_type == EnemyType.CYBORG:
            # Les cyborgs peuvent suralimenter leurs implants pour un boost temporaire
            return {
                "name": "Suralimentation",
                "type": "SELF_BUFF",
                "effect": "damage_boost",
                "multiplier": 1.5,
                "duration": 2,  # tours
                "message": f"{self.name} surcharge ses implants de combat!"
            }
            
        elif self.enemy_type == EnemyType.BEAST:
            # Les créatures peuvent faire une attaque dévastatrice
            return {
                "name": "Attaque sauvage",
                "type": "PHYSICAL",
                "damage": int(self.damage * 1.8),  # Plus de dégâts
                "accuracy_penalty": 0.2,  # Mais moins précise
                "message": f"{self.name} se déchaîne avec une attaque sauvage!"
            }
            
        # Par défaut, pas d'action spéciale
        return None
    
    def can_be_hacked(self) -> bool:
        """Détermine si l'ennemi peut être piraté"""
        # Les ennemis électroniques ou cyber-augmentés peuvent être piratés
        hackable_types = [EnemyType.ROBOT, EnemyType.DRONE, EnemyType.CYBORG, EnemyType.MILITECH]
        return self.enemy_type in hackable_types
    
    def get_loot(self) -> List[Dict[str, Any]]:
        """Génère le butin que l'ennemi peut laisser après sa défaite"""
        # TODO: Implémenter un système de butin plus élaboré
        loot = []
        
        # Chance de base d'obtenir de l'argent
        money = self.level * random.randint(5, 15)
        loot.append({
            "type": "money",
            "amount": money,
            "name": f"{money} ¥"
        })
        
        # Chance de loot basée sur le type et le niveau
        loot_chance = 0.3 + (self.level * 0.05)  # 30% + 5% par niveau
        
        if random.random() < loot_chance:
            # Déterminer le type d'objet à générer
            item_types = ["weapon", "implant", "consumable"]
            weights = [0.3, 0.3, 0.4]  # Probabilités pour chaque type
            item_type = random.choices(item_types, weights=weights, k=1)[0]
            
            if item_type == "weapon":
                # Loot d'arme basé sur le type d'ennemi
                if self.enemy_type in [EnemyType.GUARD, EnemyType.MILITECH]:
                    # Meilleure chance d'armes de qualité
                    weapon_tier = min(5, 1 + self.level // 2)
                else:
                    weapon_tier = min(3, 1 + self.level // 3)
                    
                loot.append({
                    "type": "weapon",
                    "tier": weapon_tier,
                    "name": f"Arme de niveau {weapon_tier}"
                })
                
            elif item_type == "implant":
                # Loot d'implant
                if self.enemy_type in [EnemyType.CYBORG, EnemyType.NETRUNNER]:
                    # Meilleure chance d'implants de qualité
                    implant_tier = min(5, 1 + self.level // 2)
                else:
                    implant_tier = min(3, 1 + self.level // 3)
                    
                loot.append({
                    "type": "implant",
                    "tier": implant_tier,
                    "name": f"Implant de niveau {implant_tier}"
                })
                
            elif item_type == "consumable":
                # Consommables divers (stims, boosters, etc.)
                consumable_types = ["health", "boost", "hack"]
                consumable_type = random.choice(consumable_types)
                
                loot.append({
                    "type": "consumable",
                    "consumable_type": consumable_type,
                    "name": f"Consommable de type {consumable_type}"
                })
        
        return loot

# Fonction pour générer un ennemi aléatoire de niveau approprié
def generate_random_enemy(difficulty: int = 1, location_type: str = None) -> Enemy:
    """
    Génère un ennemi aléatoire
    
    Args:
        difficulty: Niveau de difficulté qui influence le niveau de l'ennemi
        location_type: Type d'emplacement qui influence le type d'ennemi généré
        
    Returns:
        Un ennemi généré aléatoirement
    """
    import random
    
    # Ajuster la difficulté pour obtenir un niveau d'ennemi
    level = max(1, min(10, random.randint(difficulty - 1, difficulty + 2)))
    
    # Déterminer le type d'ennemi en fonction du lieu
    if location_type == "corporate":
        enemy_types = [EnemyType.GUARD, EnemyType.ROBOT, EnemyType.MILITECH]
        weights = [0.5, 0.3, 0.2]
    elif location_type == "slums":
        enemy_types = [EnemyType.HUMAN, EnemyType.BEAST, EnemyType.NETRUNNER]
        weights = [0.6, 0.3, 0.1]
    elif location_type == "industrial":
        enemy_types = [EnemyType.ROBOT, EnemyType.DRONE, EnemyType.GUARD]
        weights = [0.4, 0.4, 0.2]
    else:
        # Par défaut, mélange de tous les types
        enemy_types = list(EnemyType)
        weights = [1.0 / len(enemy_types)] * len(enemy_types)
    
    # Choisir un type d'ennemi
    enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
    
    # Noms par type d'ennemi
    name_prefixes = {
        EnemyType.HUMAN: ["Voyou", "Vagabond", "Délinquant", "Brigand"],
        EnemyType.GUARD: ["Agent", "Garde", "Vigile", "Sentinelle"],
        EnemyType.CYBORG: ["Augmenté", "Cyborg", "Hybride", "Mécanisé"],
        EnemyType.DRONE: ["Drone", "UAV", "Aéronef", "Sentinelle"],
        EnemyType.ROBOT: ["Robot", "Automate", "Exosquelette", "Unité"],
        EnemyType.NETRUNNER: ["Netrunner", "Hacker", "Opérateur", "Infiltrateur"],
        EnemyType.MILITECH: ["Soldat", "Commando", "OpSpec", "Élite"],
        EnemyType.BEAST: ["Mutant", "Bête", "Créature", "Aberration"]
    }
    
    name_suffixes = {
        EnemyType.HUMAN: ["des rues", "du gang", "du quartier", "sans-abri"],
        EnemyType.GUARD: ["de sécurité", "corporatif", "d'élite", "lourd"],
        EnemyType.CYBORG: ["modifié", "augmenté", "de combat", "expérimental"],
        EnemyType.DRONE: ["de surveillance", "d'attaque", "tactique", "militaire"],
        EnemyType.ROBOT: ["de défense", "de combat", "d'assaut", "tactique"],
        EnemyType.NETRUNNER: ["black hat", "de combat", "ice breaker", "d'élite"],
        EnemyType.MILITECH: ["tactique", "d'élite", "augmenté", "de combat"],
        EnemyType.BEAST: ["mutant", "génétiquement modifié", "sauvage", "cybernétique"]
    }
    
    prefix = random.choice(name_prefixes.get(enemy_type, ["Ennemi"]))
    suffix = random.choice(name_suffixes.get(enemy_type, ["inconnu"]))
    
    name = f"{prefix} {suffix}"
    
    # Créer l'ennemi
    enemy = Enemy(name, enemy_type, level)
    
    return enemy


def generate_enemy_from_npc(npc_data: dict) -> Enemy:
    """
    Génère un ennemi à partir des données d'un PNJ
    
    Args:
        npc_data: Dictionnaire contenant les données du PNJ
        
    Returns:
        Un ennemi basé sur le PNJ
    """
    # Extraire les données du PNJ
    npc_id = npc_data.get("id", "unknown")
    name = npc_data.get("name", f"Ennemi-{npc_id}")
    
    # Déterminer le type d'ennemi en fonction du type de PNJ
    npc_type = npc_data.get("type", "neutral")
    
    if npc_type == "hostile":
        # Les PNJ hostiles ont plus de chances d'être des ennemis dangereux
        enemy_types = [
            EnemyType.HUMAN, 
            EnemyType.GUARD, 
            EnemyType.CYBORG, 
            EnemyType.MILITECH
        ]
        weights = [0.3, 0.3, 0.2, 0.2]
    elif npc_type == "vendor":
        # Les vendeurs sont généralement des humains ou des cyborgs
        enemy_types = [
            EnemyType.HUMAN, 
            EnemyType.CYBORG, 
            EnemyType.NETRUNNER
        ]
        weights = [0.5, 0.3, 0.2]
    else:
        # Autres types de PNJ
        enemy_types = [
            EnemyType.HUMAN, 
            EnemyType.GUARD, 
            EnemyType.NETRUNNER
        ]
        weights = [0.6, 0.2, 0.2]
    
    # Déterminer le niveau en fonction des métadonnées du PNJ
    base_level = npc_data.get("level", 1)
    
    # Ajuster le niveau en fonction du type et de la "dangérosité"
    danger_level = npc_data.get("hostility", 50) / 20  # Entre 0 et 5 approximativement
    if npc_type == "hostile":
        level = base_level + round(danger_level)
    else:
        level = max(1, base_level)
    
    # Choisir un type d'ennemi
    import random
    enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
    
    # Créer l'ennemi de base
    enemy = Enemy(name, enemy_type, level)
    
    # Personnaliser les statistiques en fonction des attributs du PNJ
    if "strength" in npc_data:
        enemy.damage = max(5, int(5 + (npc_data["strength"] * 0.5)))
    
    if "health" in npc_data:
        enemy.max_health = npc_data["health"]
        enemy.health = enemy.max_health
    
    if "defense" in npc_data:
        enemy.resistance_physical = min(80, npc_data.get("defense", 0) * 2)
    
    if "tech_skill" in npc_data:
        enemy.resistance_cyber = min(80, npc_data.get("tech_skill", 0) * 2)
    
    # Appliquer des modifications aléatoires pour la variété
    enemy.accuracy = min(0.95, max(0.5, enemy.accuracy + random.uniform(-0.1, 0.1)))
    enemy.initiative = max(1, enemy.initiative + random.randint(-2, 2))
    
    # Ajouter l'identifiant du PNJ aux métadonnées de l'ennemi
    enemy.metadata["npc_id"] = npc_id
    
    return enemy


def generate_enemies_from_npcs(npc_data_list: list) -> list:
    """
    Génère des ennemis à partir d'une liste de données de PNJ
    
    Args:
        npc_data_list: Liste de dictionnaires contenant les données des PNJ
        
    Returns:
        Une liste d'ennemis basés sur les PNJ
    """
    enemies = []
    
    for npc_data in npc_data_list:
        enemy = generate_enemy_from_npc(npc_data)
        enemies.append(enemy)
    
    return enemies
