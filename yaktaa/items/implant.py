# Ce fichier est un alias pour permettre la compatibilitu00e9 avec le code existant
import logging
from typing import Dict, List, Optional, Any
import uuid
import random

from .item import Item

# Configuration du logging
logger = logging.getLogger("YakTaa.Items.Implant")
logger.debug("Module implant.py chargu00e9 (module substitutu00e9)")


class ImplantItem(Item):
    """
    Classe repru00e9sentant un implant cybernétique dans le jeu
    Cette classe est une mise en place temporaire pour u00e9viter les erreurs d'importation
    """
    
    IMPLANT_TYPES = ["NEURAL", "OPTICAL", "SKELETAL", "DERMAL", "CIRCULATORY"]
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Implant standard", 
                 description: str = "Un implant cybernétique de base", 
                 implant_type: str = "NEURAL",
                 level: int = 1,
                 price: int = 100,
                 stats_bonus: Dict[str, int] = None,
                 humanity_cost: int = 5,
                 installation_difficulty: int = 1,
                 special_effects: List[str] = None,
                 combat_bonus: Dict[str, float] = None,
                 icon: str = "implant",
                 is_illegal: bool = False,
                 rarity: str = "COMMON"):
        """
        Initialise un objet implant
        
        Args:
            id: Identifiant unique de l'implant
            name: Nom de l'implant
            description: Description de l'implant
            implant_type: Type d'implant (NEURAL, OPTICAL, SKELETAL, DERMAL, CIRCULATORY)
            level: Niveau requis pour utiliser l'implant
            price: Prix de l'implant
            stats_bonus: Bonus de statistiques offerts par l'implant
            humanity_cost: Cou00fbt en humanitu00e9 de l'implant
            installation_difficulty: Difficultu00e9 d'installation (1-10)
            special_effects: Liste d'effets spu00e9ciaux apportu00e9s par l'implant
            combat_bonus: Bonus de combat (damage_multiplier, critical_chance, etc.)
            icon: Icu00f4ne de l'implant
            is_illegal: Indique si l'implant est illu00e9gal
            rarity: Raretu00e9 de l'implant
        """
        super().__init__(
            id=id or str(uuid.uuid4()),
            name=name,
            description=description,
            item_type="implant",
            level=level,
            price=price,
            weight=0.5,  # Les implants sont gu00e9nu00e9ralement lu00e9gers
            icon=icon,
            is_illegal=is_illegal,
            rarity=rarity
        )
        
        # Valider le type d'implant
        if implant_type.upper() in [t.upper() for t in self.IMPLANT_TYPES]:
            for t in self.IMPLANT_TYPES:
                if implant_type.upper() == t.upper():
                    implant_type = t
                    break
        else:
            implant_type = "NEURAL"  # Type par du00e9faut
            
        # Propriu00e9tu00e9s spu00e9cifiques aux implants
        self.implant_type = implant_type
        self.stats_bonus = stats_bonus or {}
        self.humanity_cost = humanity_cost
        self.installation_difficulty = min(10, max(1, installation_difficulty))
        self.special_effects = special_effects or []
        self.combat_bonus = combat_bonus or {}
        
        logger.debug(f"Nouvel item implant cru00e9u00e9 : {name} (Type: {implant_type})")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Ru00e9cupu00e8re les informations de l'implant sous forme de dictionnaire
        
        Returns:
            Dictionnaire d'informations
        """
        base_info = super().get_info()
        
        # Formater les bonus de stats pour l'affichage
        formatted_bonuses = []
        for stat, value in self.stats_bonus.items():
            sign = "+" if value >= 0 else ""
            formatted_bonuses.append(f"{stat}: {sign}{value}")
        
        implant_info = {
            "type": f"Implant - {self.implant_type}",
            "bonuses": ", ".join(formatted_bonuses) if formatted_bonuses else "Aucun",
            "humanity_cost": self.humanity_cost,
            "installation": f"Niveau {self.installation_difficulty}"
        }
        
        # Ajouter les effets spu00e9ciaux si pru00e9sents
        if self.special_effects:
            implant_info["special_effects"] = ", ".join(self.special_effects)
            
        # Ajouter les bonus de combat si pru00e9sents
        if self.combat_bonus:
            combat_info = []
            for bonus_type, value in self.combat_bonus.items():
                if "multiplier" in bonus_type:
                    # Formater les multiplicateurs comme des pourcentages
                    formatted_value = f"+{int((value - 1) * 100)}%" if value > 1 else f"{int((value - 1) * 100)}%"
                elif "chance" in bonus_type:
                    # Formater les chances comme des pourcentages
                    formatted_value = f"+{int(value * 100)}%" if value > 0 else f"{int(value * 100)}%"
                else:
                    # Formater les autres valeurs normalement
                    formatted_value = f"+{value}" if value > 0 else f"{value}"
                combat_info.append(f"{bonus_type}: {formatted_value}")
            implant_info["combat_bonus"] = ", ".join(combat_info)
        
        return {**base_info, **implant_info}
    
    def use(self) -> Dict[str, Any]:
        """
        Tente d'installer l'implant
        
        Returns:
            Ru00e9sultat de l'installation
        """
        return {
            "success": True,
            "message": f"Vous avez pru00e9paru00e9 {self.name} pour l'installation. Rendez-vous chez un mu00e9dtech pour finaliser la procu00e9dure.",
            "effect": "prepare_implant",
            "data": {
                "implant_id": self.id,
                "implant_type": self.implant_type,
                "humanity_cost": self.humanity_cost,
                "installation_difficulty": self.installation_difficulty,
                "stats_bonus": self.stats_bonus,
                "special_effects": self.special_effects,
                "combat_bonus": self.combat_bonus
            }
        }
    
    def apply_effects(self, character: Any, target: Any = None) -> Dict[str, Any]:
        """
        Applique les effets spu00e9ciaux de l'implant u00e0 un personnage ou une cible
        
        Args:
            character: Le personnage qui a l'implant
            target: La cible potentielle des effets (optionnel)
        
        Returns:
            Dictionnaire avec les ru00e9sultats de l'application des effets
        """
        result = {
            "applied_effects": [],
            "messages": []
        }
        
        # Pas d'effets spu00e9ciaux ? On retourne un ru00e9sultat vide
        if not self.special_effects:
            return result
        
        # Applique les différents effets spu00e9ciaux
        for effect in self.special_effects:
            if effect == "regeneration":
                healing = max(1, int(character.max_health * 0.02))  # 2% de la santu00e9 max
                character.health = min(character.max_health, character.health + healing)
                result["applied_effects"].append("regeneration")
                result["messages"].append(f"L'implant {self.name} a ru00e9gu00e9nu00e9ru00e9 {healing} points de vie.")
                
            elif effect == "auto_hack":
                # Simule une assistance au hacking
                result["applied_effects"].append("auto_hack")
                result["messages"].append(f"L'implant {self.name} vous aide u00e0 identifier les failles.")
                
            elif effect == "thermal_vision" and target:
                # Bonus contre les ennemis invisibles
                result["applied_effects"].append("thermal_vision")
                result["target_visible"] = True
                result["messages"].append(f"Votre vision thermique ru00e9vu00e8le la cible.")
                
            elif effect == "analysis" and target:
                # Analyse la cible pour identifier ses faiblesses
                result["applied_effects"].append("analysis")
                result["target_analyzed"] = True
                result["messages"].append(f"L'implant {self.name} analyse les faiblesses de la cible.")
                
            elif effect == "auto_dodge":
                # Chance d'u00e9viter automatiquement une attaque
                dodge_chance = min(0.05 + (self.level * 0.01), 0.25)  # Max 25%
                result["applied_effects"].append("auto_dodge")
                result["dodge_chance"] = dodge_chance
                result["messages"].append(f"Votre implant {self.name} vous aide u00e0 esquiver les attaques.")
        
        return result
    
    def get_combat_bonus(self, stat_type: str) -> float:
        """
        Ru00e9cupu00e8re un bonus de combat spu00e9cifique
        
        Args:
            stat_type: Type de statistique (damage_multiplier, critical_chance, etc.)
            
        Returns:
            Valeur du bonus (0 si non existant)
        """
        return self.combat_bonus.get(stat_type, 0.0)
    
    @classmethod
    def generate_random(cls, level: int = 1, implant_type: Optional[str] = None) -> 'ImplantItem':
        """
        Gu00e9nu00e8re un implant alu00e9atoire de niveau et type spu00e9cifiu00e9s
        
        Args:
            level: Niveau de l'implant
            implant_type: Type d'implant (optionnel)
            
        Returns:
            Un nouvel implant alu00e9atoire
        """
        # Du00e9terminer le type d'implant si non spu00e9cifiu00e9
        if implant_type is None:
            implant_type = random.choice(cls.IMPLANT_TYPES)
            
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
        
        # Du00e9terminer l'illu00e9galitu00e9 selon le type et la raretu00e9
        is_illegal = False
        if implant_type in ["NEURAL", "CIRCULATORY"]:
            # Les implants neurologiques et circulatoires avancu00e9s sont plus susceptibles d'u00eatre illu00e9gaux
            is_illegal = random.random() < (0.1 * level * modifier)
        
        # Du00e9terminer les bonus de statistiques selon le type d'implant
        stats_bonus = {}
        
        base_value = int(level * modifier)
        
        if implant_type == "NEURAL":
            stats_bonus["hacking"] = base_value + random.randint(0, 2)
            stats_bonus["intelligence"] = int(base_value * 0.5) + random.randint(0, 1)
            if random.random() < 0.3:
                stats_bonus["reflexes"] = int(base_value * 0.3) + random.randint(0, 1)
                
        elif implant_type == "OPTICAL":
            stats_bonus["perception"] = base_value + random.randint(0, 2)
            stats_bonus["precision"] = int(base_value * 0.7) + random.randint(0, 1)
            if random.random() < 0.3:
                stats_bonus["technical"] = int(base_value * 0.3) + random.randint(0, 1)
                
        elif implant_type == "SKELETAL":
            stats_bonus["force"] = base_value + random.randint(0, 2)
            stats_bonus["endurance"] = int(base_value * 0.6) + random.randint(0, 1)
            if random.random() < 0.3:
                stats_bonus["constitution"] = int(base_value * 0.4) + random.randint(0, 1)
                
        elif implant_type == "DERMAL":
            stats_bonus["armure"] = base_value + random.randint(0, 2)
            stats_bonus["resistance"] = int(base_value * 0.5) + random.randint(0, 1)
            if random.random() < 0.3:
                stats_bonus["intimidation"] = int(base_value * 0.3) + random.randint(0, 1)
                
        elif implant_type == "CIRCULATORY":
            stats_bonus["vitesse"] = base_value + random.randint(0, 2)
            stats_bonus["reflexes"] = int(base_value * 0.7) + random.randint(0, 1)
            if random.random() < 0.3:
                stats_bonus["endurance"] = int(base_value * 0.4) + random.randint(0, 1)
        
        # Du00e9terminer le cou00fbt en humanitu00e9 (plus u00e9levu00e9 pour les implants puissants)
        total_bonus = sum(stats_bonus.values())
        humanity_cost = max(2, int(total_bonus * 0.8 * (1.5 if is_illegal else 1.0)))
        
        # Du00e9terminer la difficultu00e9 d'installation
        install_diff = min(10, 1 + int(level / 2) + (3 if is_illegal else 0))
        
        # Calculer le prix en fonction des bonus et du niveau
        price = int(total_bonus * 100 * level * modifier * (1.5 if is_illegal else 1.0))
        
        # Gu00e9nu00e9rer des effets spu00e9ciaux pour les implants rares ou meilleures
        special_effects = []
        if rarity in ["RARE", "EPIC", "LEGENDARY"]:
            # Liste d'effets spu00e9ciaux possibles par type d'implant
            effect_types = {
                "NEURAL": ["auto_hack", "multitache", "analyse_donnees", "hacking_passif", "firewall"],
                "OPTICAL": ["thermal_vision", "zoom", "analyse", "vision_nocturne", "scanner"],
                "SKELETAL": ["saut_ameliore", "stabilisateur", "resistance_choc", "puissance", "endurance"],
                "DERMAL": ["dispersion_energie", "cameleon", "resistance_feu", "resistance_acide", "blindage"],
                "CIRCULATORY": ["regeneration", "detox", "adrenaline", "oxygene", "auto_dodge"]
            }
            
            # Nombre d'effets spu00e9ciaux selon la raretu00e9
            num_effects = {
                "RARE": 1,
                "EPIC": 2,
                "LEGENDARY": 3
            }.get(rarity, 0)
            
            # Effets possibles pour ce type d'implant
            possible_effects = effect_types.get(implant_type, [])
            
            for _ in range(num_effects):
                if not possible_effects:  # Si tous les effets ont u00e9tu00e9 utilisu00e9s
                    break
                    
                effect = random.choice(possible_effects)
                possible_effects.remove(effect)  # u00c9viter les doublons
                special_effects.append(effect)
        
        # Gu00e9nu00e9rer des bonus de combat pour certains types d'implants
        combat_bonus = {}
        
        # Chance d'avoir des bonus de combat selon le type d'implant et la raretu00e9
        combat_bonus_chance = {
            "NEURAL": 0.3,   # Moins probable
            "OPTICAL": 0.6,  # Bonus de pru00e9cision
            "SKELETAL": 0.7, # Bonus de du00e9gu00e2ts
            "DERMAL": 0.5,   # Bonus de ru00e9sistance
            "CIRCULATORY": 0.7  # Bonus de vitesse/esquive
        }
        
        # Pour les objets rares et plus, on ajoute des bonus de combat
        if rarity in ["RARE", "EPIC", "LEGENDARY"] and random.random() < combat_bonus_chance.get(implant_type, 0.3):
            # Calcul de base pour les bonus
            base_combat_bonus = 0.05 * level * modifier
            
            # Types de bonus possibles par type d'implant
            if implant_type == "NEURAL":
                if random.random() < 0.7:
                    combat_bonus["critical_chance"] = min(0.25, base_combat_bonus * 0.4)  # Max 25%
                if random.random() < 0.5:
                    combat_bonus["evasion"] = min(0.15, base_combat_bonus * 0.3)  # Max 15%
                    
            elif implant_type == "OPTICAL":
                if random.random() < 0.8:
                    combat_bonus["accuracy"] = min(0.2, base_combat_bonus * 0.5)  # Max 20%
                if random.random() < 0.6:
                    combat_bonus["critical_damage_multiplier"] = 1.0 + min(0.5, base_combat_bonus)  # Max +50%
                    
            elif implant_type == "SKELETAL":
                if random.random() < 0.8:
                    combat_bonus["damage_multiplier"] = 1.0 + min(0.3, base_combat_bonus * 0.7)  # Max +30%
                if random.random() < 0.6:
                    combat_bonus["armor_penetration"] = min(0.25, base_combat_bonus * 0.5)  # Max 25%
                    
            elif implant_type == "DERMAL":
                if random.random() < 0.9:
                    combat_bonus["damage_reduction"] = min(0.3, base_combat_bonus * 0.6)  # Max 30%
                if random.random() < 0.5:
                    combat_bonus["resistance"] = min(0.2, base_combat_bonus * 0.4)  # Max 20%
                    
            elif implant_type == "CIRCULATORY":
                if random.random() < 0.7:
                    combat_bonus["speed_multiplier"] = 1.0 + min(0.25, base_combat_bonus * 0.5)  # Max +25%
                if random.random() < 0.6:
                    combat_bonus["dodge_chance"] = min(0.2, base_combat_bonus * 0.4)  # Max 20%
        
        # Listes de noms par type d'implant
        type_names = {
            "NEURAL": ["NeuroPuce", "CervoBoost", "SynapseLink", "MnemoCore", "PsychoWire"],
            "OPTICAL": ["KiroshiOptics", "RetiScan", "OeilBionique", "VisioEnhance", "ZoomTech"],
            "SKELETAL": ["OsSynth", "ReinforceMuscle", "ExoStructure", "TitanFrame", "BioFibre"],
            "DERMAL": ["SubdermalArmor", "DermaShield", "NanoSkin", "ProtectLayer", "BioMesh"],
            "CIRCULATORY": ["CardioBoost", "HemoFilter", "BloodPump", "OxygenCore", "VeinTech"]
        }
        
        # Listes d'adjectifs par raretu00e9
        rarity_adjectives = {
            "COMMON": ["Standard", "Basique", "Simple", "Ordinaire"],
            "UNCOMMON": ["Amu00e9lioru00e9", "Efficace", "Travaillu00e9", "Utile"],
            "RARE": ["Sophistiquu00e9", "Pru00e9cis", "Avancu00e9", "Puissant"],
            "EPIC": ["Exceptionnel", "Formidable", "Extraordinaire", "Ultime"],
            "LEGENDARY": ["Lu00e9gendaire", "Mythique", "Divin", "Transcendant", "Absolu"]
        }
        
        # Fabricants d'implants
        manufacturers = [
            "Zetatech", "Kiroshi", "Biotechnica", "Trauma Team", "Militech", 
            "Worldsat", "Raven", "ChromaGen", "TurboHealth", "BioSolutions"
        ]
        
        # Gu00e9nu00e9rer un nom alu00e9atoire
        name_base = random.choice(type_names.get(implant_type, ["Implant"]))
        adjective = random.choice(rarity_adjectives.get(rarity, ["Standard"]))
        manufacturer = random.choice(manufacturers)
        
        name = f"{adjective} {name_base} {manufacturer}"
        
        # Gu00e9nu00e9rer une description
        descriptions = {
            "NEURAL": ["Un implant neuronal qui amu00e9liore vos capacitu00e9s cognitives.", 
                      "Optimise la vitesse de traitement de vos synapses.", 
                      "Connecte votre cerveau directement au ru00e9seau."],
            "OPTICAL": ["Un systu00e8me oculaire avancu00e9 qui amu00e9liore votre vision.", 
                       "Vos yeux deviennent des outils de pru00e9cision.", 
                       "Scanning, zoom, vision nocturne, en un seul implant."],
            "SKELETAL": ["Renforce votre structure osseuse pour des performances accrues.", 
                        "Fibres musculaires synthu00e9tiques pour une force surhumaine.", 
                        "Endosquelette renforcu00e9 pour ru00e9sister aux impacts les plus violents."],
            "DERMAL": ["Une couche protectrice sous-cutanu00e9e contre les aggressions.", 
                      "Peau synthu00e9tique renforcu00e9e pour une protection optimale.", 
                      "Blindage dermique qui s'adapte u00e0 vos mouvements."],
            "CIRCULATORY": ["Optimise votre flux sanguin pour des performances accrues.", 
                          "Amu00e9liore l'oxygénation de vos cellules.", 
                          "Filtre les toxines et amu00e9liore vos ru00e9flexes."]
        }
        
        description = random.choice(descriptions.get(implant_type, ["Un implant cybernu00e9tique aux fonctionalitu00e9s avancu00e9es."]))        
        
        # Ajouter les informations sur les effets spu00e9ciaux et les bonus de combat dans la description
        if special_effects:
            description += f" Effets spu00e9ciaux: {', '.join(special_effects)}."
            
        description += f" [Niveau {level}, {rarity}]"
        
        # Gu00e9nu00e9rer un nouvel implant
        return cls(
            name=name,
            description=description,
            implant_type=implant_type,
            level=level,
            price=price,
            stats_bonus=stats_bonus,
            humanity_cost=humanity_cost,
            installation_difficulty=install_diff,
            special_effects=special_effects,
            combat_bonus=combat_bonus,
            icon=f"implant_{implant_type.lower()}",
            is_illegal=is_illegal,
            rarity=rarity
        )
