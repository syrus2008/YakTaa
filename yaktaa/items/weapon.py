# Ce fichier est un alias pour permettre la compatibilitu00e9 avec le code existant
import logging
from typing import Dict, List, Optional, Any
import uuid
import random

from .item import Item

# Configuration du logging
logger = logging.getLogger("YakTaa.Items.Weapon")
logger.debug("Module weapon.py chargu00e9 (module substitutu00e9)")


class WeaponItem(Item):
    """
    Classe repru00e9sentant une arme dans le jeu
    Cette classe est une mise en place temporaire pour u00e9viter les erreurs d'importation
    """
    
    WEAPON_TYPES = ["MELEE", "RANGED", "SMART", "CYBER"]
    DAMAGE_TYPES = ["PHYSICAL", "ENERGY", "EMP", "THERMAL", "CHEMICAL", "SHOCK", "QUANTUM"]
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Arme standard", 
                 description: str = "Une arme de base", 
                 weapon_type: str = "MELEE",
                 damage: int = 10,
                 damage_type: str = "PHYSICAL",
                 accuracy: int = 70,
                 range: int = 5,
                 level: int = 1,
                 price: int = 100,
                 weight: float = 1.0,
                 icon: str = "weapon",
                 is_illegal: bool = False,
                 rarity: str = "COMMON",
                 stats_bonus: Dict[str, int] = None,
                 special_effects: List[str] = None):
        """
        Initialise un objet arme
        
        Args:
            id: Identifiant unique de l'arme
            name: Nom de l'arme
            description: Description de l'arme
            weapon_type: Type d'arme (MELEE, RANGED, SMART, CYBER)
            damage: Du00e9gu00e2ts infligiu00e9s par l'arme
            damage_type: Type de du00e9gu00e2ts (PHYSICAL, ENERGY, EMP, THERMAL, CHEMICAL, SHOCK, QUANTUM)
            accuracy: Pru00e9cision de l'arme (0-100)
            range: Portu00e9e de l'arme
            level: Niveau requis pour utiliser l'arme
            price: Prix de l'arme
            weight: Poids de l'arme
            icon: Icu00f4ne de l'arme
            is_illegal: Indique si l'arme est illu00e9gale
            rarity: Raretu00e9 de l'arme
            stats_bonus: Dictionnaire de bonus de statistiques
            special_effects: Liste d'effets spu00e9ciaux de l'arme
        """
        super().__init__(
            id=id or str(uuid.uuid4()),
            name=name,
            description=description,
            item_type="weapon",
            level=level,
            price=price,
            weight=weight,
            icon=icon,
            is_illegal=is_illegal,
            rarity=rarity
        )
        
        # Valider le type d'arme
        if weapon_type.upper() in [t.upper() for t in self.WEAPON_TYPES]:
            for t in self.WEAPON_TYPES:
                if weapon_type.upper() == t.upper():
                    weapon_type = t
                    break
        else:
            weapon_type = "MELEE"  # Type par du00e9faut
        
        # Valider le type de du00e9gu00e2ts
        if damage_type.upper() in [t.upper() for t in self.DAMAGE_TYPES]:
            for t in self.DAMAGE_TYPES:
                if damage_type.upper() == t.upper():
                    damage_type = t
                    break
        else:
            damage_type = "PHYSICAL"  # Type par du00e9faut
            
        # Propriu00e9tu00e9s spu00e9cifiques aux armes
        self.weapon_type = weapon_type
        self.damage = damage
        self.damage_type = damage_type
        self.accuracy = max(0, min(100, accuracy))  # Limiter u00e0 0-100
        self.range = range
        self.stats_bonus = stats_bonus or {}
        self.special_effects = special_effects or []
        
        logger.debug(f"Nouvel item arme cru00e9u00e9 : {name} (Type: {weapon_type}, Damage: {damage}, DamageType: {damage_type})")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Ru00e9cupu00e8re les informations de l'arme sous forme de dictionnaire
        
        Returns:
            Dictionnaire d'informations
        """
        base_info = super().get_info()
        
        weapon_info = {
            "type": f"Weapon - {self.weapon_type}",
            "damage": f"{self.damage} ({self.damage_type})",
            "accuracy": f"{self.accuracy}%",
            "range": self.range
        }
        
        # Ajouter les bonus de stats si pru00e9sents
        if self.stats_bonus:
            bonus_info = {f"bonus_{stat}": value for stat, value in self.stats_bonus.items()}
            weapon_info.update(bonus_info)
        
        # Ajouter les effets spu00e9ciaux si pru00e9sents
        if self.special_effects:
            weapon_info["special_effects"] = ", ".join(self.special_effects)
        
        return {**base_info, **weapon_info}
    
    def use(self) -> Dict[str, Any]:
        """
        Utilise l'arme (u00e9quiper)
        
        Returns:
            Ru00e9sultat de l'utilisation
        """
        return {
            "success": True,
            "message": f"Vous avez u00e9quipu00e9 {self.name}.",
            "effect": "equip_weapon",
            "data": {
                "weapon_id": self.id,
                "damage": self.damage,
                "damage_type": self.damage_type,
                "weapon_type": self.weapon_type,
                "special_effects": self.special_effects
            }
        }
    
    def calculate_critical_chance(self) -> float:
        """
        Calcule la chance de coup critique de cette arme
        
        Returns:
            Pourcentage de chance (0.0 - 1.0)
        """
        # Base sur la pru00e9cision et la raretu00e9
        base_chance = self.accuracy / 200  # 0.5 au maximum avec 100% de pru00e9cision
        
        # Bonus par raretu00e9
        rarity_bonus = {
            "COMMON": 0.0,
            "UNCOMMON": 0.02,
            "RARE": 0.05,
            "EPIC": 0.08,
            "LEGENDARY": 0.15
        }
        
        return base_chance + rarity_bonus.get(self.rarity, 0.0)
    
    @classmethod
    def generate_random(cls, level: int = 1, weapon_type: Optional[str] = None) -> 'WeaponItem':
        """
        Gu00e9nu00e8re une arme alu00e9atoire de niveau et type spu00e9cifiu00e9s
        
        Args:
            level: Niveau de l'arme
            weapon_type: Type d'arme (optionnel)
            
        Returns:
            Une nouvelle arme alu00e9atoire
        """
        # Du00e9terminer le type d'arme si non spu00e9cifiu00e9
        if weapon_type is None:
            weapon_type = random.choice(cls.WEAPON_TYPES)
            
        # Du00e9terminer la raretu00e9 en fonction du niveau
        rarity_chances = {
            "COMMON": 0.6 if level < 5 else (0.4 if level < 10 else 0.2),
            "UNCOMMON": 0.3 if level < 5 else (0.3 if level < 10 else 0.3),
            "RARE": 0.08 if level < 5 else (0.2 if level < 10 else 0.3),
            "EPIC": 0.02 if level < 5 else (0.08 if level < 10 else 0.15),
            "LEGENDARY": 0.0 if level < 5 else (0.02 if level < 10 else 0.05)
        }
        
        # Su00e9lectionner la raretu00e9 en fonction des chances
        rarity = random.choices(
            list(rarity_chances.keys()),
            weights=list(rarity_chances.values()),
            k=1
        )[0]
        
        # Ajuster les statistiques en fonction du niveau et de la raretu00e9
        rarity_modifiers = {
            "COMMON": 1.0,
            "UNCOMMON": 1.2,
            "RARE": 1.5,
            "EPIC": 2.0,
            "LEGENDARY": 3.0
        }
        
        modifier = rarity_modifiers.get(rarity, 1.0)
        
        # Calculer les statistiques de base
        base_damage = int(10 * level * modifier)
        base_accuracy = min(95, 60 + level * 2)
        base_range = int(5 * (1 + (level - 1) * 0.2) * modifier)
        
        # Du00e9terminer le type de du00e9gu00e2ts en fonction du type d'arme
        damage_type_weights = {
            "MELEE": {"PHYSICAL": 0.8, "THERMAL": 0.1, "CHEMICAL": 0.05, "SHOCK": 0.05},
            "RANGED": {"PHYSICAL": 0.7, "ENERGY": 0.15, "THERMAL": 0.1, "CHEMICAL": 0.05},
            "SMART": {"PHYSICAL": 0.4, "ENERGY": 0.3, "EMP": 0.2, "QUANTUM": 0.1},
            "CYBER": {"PHYSICAL": 0.3, "ENERGY": 0.3, "EMP": 0.2, "SHOCK": 0.1, "QUANTUM": 0.1}
        }
        
        weights = damage_type_weights.get(weapon_type, {"PHYSICAL": 1.0})
        damage_type = random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]
        
        # Ajuster en fonction du type d'arme
        if weapon_type == "MELEE":
            damage = int(base_damage * 1.3)
            accuracy = int(base_accuracy * 0.9)
            range = int(base_range * 0.5)
            is_illegal = False
        elif weapon_type == "RANGED":
            damage = base_damage
            accuracy = base_accuracy
            range = base_range
            is_illegal = random.random() < 0.3
        elif weapon_type == "SMART":
            damage = int(base_damage * 0.9)
            accuracy = int(base_accuracy * 1.2)
            range = int(base_range * 1.1)
            is_illegal = random.random() < 0.5
        elif weapon_type == "CYBER":
            damage = int(base_damage * 1.1)
            accuracy = int(base_accuracy * 1.1)
            range = int(base_range * 1.2)
            is_illegal = random.random() < 0.7
        else:
            damage = base_damage
            accuracy = base_accuracy
            range = base_range
            is_illegal = False
            
        # Gu00e9nu00e9rer un prix en fonction des statistiques
        price = int((damage + accuracy + range) * level * modifier * (2 if is_illegal else 1))
        
        # Listes de noms par type d'arme
        type_names = {
            "MELEE": ["Lame", "Batte", "Poing", "Griffes", "Machette", "Couteau"],
            "RANGED": ["Pistolet", "Fusil", "Carabine", "Revolver", "Mitraillette"],
            "SMART": ["PistoGuide", "ArmeTraceur", "Viseur", "NeuroCible", "SynchroShot"],
            "CYBER": ["ImplantLame", "NeuroFusil", "DronetArm", "NanoLame", "PulseCannon"]
        }
        
        # Listes d'adjectifs par raretu00e9
        rarity_adjectives = {
            "COMMON": ["Standard", "Basique", "Simple", "Ordinaire"],
            "UNCOMMON": ["Amu00e9lioru00e9", "Efficace", "Travaillu00e9", "Utile"],
            "RARE": ["Sophistiqu00e9", "Pru00e9cis", "Avanciu00e9", "Puissant"],
            "EPIC": ["Exceptionnel", "Formidable", "Extraordinaire", "Ultime"],
            "LEGENDARY": ["Lu00e9gendaire", "Mythique", "Divin", "Transcendant", "Absolu"]
        }
        
        # Fabricants d'armes
        manufacturers = [
            "ArasaCorp", "Militech", "Tsunami", "BlackHand", "Dynalar", 
            "Nokota", "Kendachi", "Sternmeyer", "Constitutional", "Malorian"
        ]
        
        # Gu00e9nu00e9rer un nom alu00e9atoire
        name_base = random.choice(type_names.get(weapon_type, ["Arme"]))
        adjective = random.choice(rarity_adjectives.get(rarity, ["Standard"]))
        manufacturer = random.choice(manufacturers)
        
        name = f"{adjective} {name_base} {manufacturer}"
        
        # Gu00e9nu00e9rer une description
        descriptions = {
            "MELEE": ["Une arme tranchante pour le combat rapprochiu00e9.", 
                    "Une lame affutiu00e9e qui ne pardonne pas.", 
                    "Un outil de persuasion efficace dans les ruelles."],
            "RANGED": ["Une arme u00e0 feu pru00e9cise et mortelle.", 
                       "Un instrument de mort u00e0 distance.", 
                       "Frappe lu00e0 ouu00e8 vos yeux peuvent voir."],
            "SMART": ["Une arme connectu00e9e u00e0 votre ru00e9seau neural.", 
                      "Vise automatiquement les points faibles.", 
                      "La technologie de visue avanciu00e9e au service de la destruction."],
            "CYBER": ["Une fusion de chair et de mu00e9tal mortel.", 
                      "Du00e9ploiement fulgurant depuis vos implants.", 
                      "Un armement directement connectu00e9 u00e0 votre systu00e8me nerveux."]
        }
        
        description = random.choice(descriptions.get(weapon_type, ["Une arme efficace et mortelle."]))        
        description += f" [Niveau {level}, {rarity}, Du00e9gu00e2ts de type {damage_type}]"
        
        # Gu00e9nu00e9rer des bonus de statistiques
        stats_bonus = {}
        if rarity != "COMMON":  # Les armes communes n'ont pas de bonus
            num_bonuses = {
                "UNCOMMON": 1,
                "RARE": 2,
                "EPIC": 3,
                "LEGENDARY": 4
            }.get(rarity, 0)
            
            possible_stats = ["strength", "precision", "reflexes", "intelligence"]
            
            # Ajouter des bonus alu00e9atoires
            for _ in range(num_bonuses):
                if not possible_stats:  # Si toutes les stats ont u00e9tu00e9 utilisu00e9es
                    break
                    
                stat = random.choice(possible_stats)
                possible_stats.remove(stat)  # u00c9viter les doublons
                
                # Valeur du bonus du00e9pendant de la raretu00e9 et du niveau
                max_bonus = int(level * rarity_modifiers.get(rarity, 1.0) / 2)
                stats_bonus[stat] = random.randint(1, max(1, max_bonus))
        
        # Gu00e9nu00e9rer des effets spu00e9ciaux pour les armes rares ou meilleures
        special_effects = []
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            possible_effects = [
                "saignement",        # Du00e9gu00e2ts sur la duru00e9e
                "u00e9tourdissement",    # Chance de paralyser la cible
                "perforant",         # Ignore une partie de l'armure
                "ru00e9tractable",      # Peut u00eatre dissimulu00e9 facilement
                "silencieux",        # Ne fait pas de bruit
                "choc",              # Chance d'u00e9lectrocuter la cible
                "explosion",         # Du00e9gu00e2ts de zone
                "pru00e9cision",        # Bonus de pru00e9cision
                "chargement",        # Du00e9gu00e2ts augmentu00e9s si chargement
                "tir_multiple"      # Tirs multiples
            ]
            
            # Nombre d'effets spu00e9ciaux selon la raretu00e9
            num_effects = {
                "RARE": 1,
                "EPIC": 2,
                "LEGENDARY": 3
            }.get(rarity, 0)
            
            for _ in range(num_effects):
                if not possible_effects:  # Si tous les effets ont u00e9tu00e9 utilisu00e9s
                    break
                    
                effect = random.choice(possible_effects)
                possible_effects.remove(effect)  # u00c9viter les doublons
                special_effects.append(effect)
        
        # Gu00e9niu00e9rer une nouvelle arme
        return cls(
            name=name,
            description=description,
            weapon_type=weapon_type,
            damage=damage,
            damage_type=damage_type,
            accuracy=accuracy,
            range=range,
            level=level,
            price=price,
            weight=random.uniform(0.5, 5.0),
            icon=f"weapon_{weapon_type.lower()}",
            is_illegal=is_illegal,
            rarity=rarity,
            stats_bonus=stats_bonus,
            special_effects=special_effects
        )
