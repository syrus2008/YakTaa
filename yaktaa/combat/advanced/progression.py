"""
Système de progression de combat pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.Progression")

class CombatRank(Enum):
    """Rangs de compétence de combat"""
    NOVICE = 0
    APPRENTICE = 1
    ADEPT = 2
    EXPERT = 3
    MASTER = 4
    GRANDMASTER = 5

class CombatStyle(Enum):
    """Styles de combat"""
    BALANCED = auto()    # Équilibré
    AGGRESSIVE = auto()  # Agressif
    DEFENSIVE = auto()   # Défensif
    TECHNICAL = auto()   # Technique
    EVASIVE = auto()     # Évasif
    PRECISE = auto()     # Précis

class CombatProgressionSystem:
    """
    Système qui gère la progression des compétences de combat
    """
    
    def __init__(self):
        """Initialise le système de progression de combat"""
        self.combat_experience = {}  # ID -> expérience
        self.combat_ranks = {}       # ID -> rang
        self.combat_styles = {}      # ID -> style
        self.combat_skills = {}      # ID -> compétences
        self.combat_perks = {}       # ID -> avantages
        
        logger.debug("Système de progression de combat initialisé")
    
    def initialize_character(self, character_id: str, initial_rank: CombatRank = CombatRank.NOVICE,
                            initial_style: CombatStyle = CombatStyle.BALANCED) -> None:
        """
        Initialise un personnage dans le système de progression
        
        Args:
            character_id: Identifiant du personnage
            initial_rank: Rang initial
            initial_style: Style de combat initial
        """
        if character_id in self.combat_experience:
            logger.warning(f"Le personnage {character_id} est déjà initialisé")
            return
            
        # Initialiser l'expérience
        self.combat_experience[character_id] = 0
        
        # Initialiser le rang
        self.combat_ranks[character_id] = initial_rank
        
        # Initialiser le style
        self.combat_styles[character_id] = initial_style
        
        # Initialiser les compétences
        self.combat_skills[character_id] = {
            "melee": 1,
            "ranged": 1,
            "defense": 1,
            "tactics": 1,
            "perception": 1
        }
        
        # Initialiser les avantages
        self.combat_perks[character_id] = []
        
        logger.debug(f"Personnage {character_id} initialisé avec rang {initial_rank.name} et style {initial_style.name}")
    
    def award_combat_experience(self, character_id: str, amount: int, 
                               combat_type: str = "standard") -> Dict[str, Any]:
        """
        Attribue de l'expérience de combat à un personnage
        
        Args:
            character_id: Identifiant du personnage
            amount: Quantité d'expérience
            combat_type: Type de combat (standard, boss, training, etc.)
            
        Returns:
            Résultat de l'attribution d'expérience
        """
        if character_id not in self.combat_experience:
            self.initialize_character(character_id)
            
        # Appliquer des modificateurs en fonction du type de combat
        modified_amount = amount
        if combat_type == "boss":
            modified_amount = int(amount * 1.5)  # +50% pour les boss
        elif combat_type == "training":
            modified_amount = int(amount * 0.5)  # -50% pour l'entraînement
            
        # Ajouter l'expérience
        previous_exp = self.combat_experience[character_id]
        self.combat_experience[character_id] += modified_amount
        
        # Vérifier les niveaux
        previous_rank = self.combat_ranks[character_id]
        self._update_combat_rank(character_id)
        current_rank = self.combat_ranks[character_id]
        
        # Vérifier si le rang a changé
        rank_changed = previous_rank != current_rank
        
        # Si le rang a changé, attribuer de nouvelles compétences et avantages
        new_skills = []
        new_perks = []
        
        if rank_changed:
            # Améliorer les compétences
            skill_improvements = self._improve_combat_skills(character_id)
            new_skills = skill_improvements["improved_skills"]
            
            # Attribuer de nouveaux avantages
            perk_result = self._award_combat_perk(character_id)
            if perk_result["success"]:
                new_perks = [perk_result["perk"]]
        
        return {
            "success": True,
            "character_id": character_id,
            "previous_exp": previous_exp,
            "gained_exp": modified_amount,
            "current_exp": self.combat_experience[character_id],
            "previous_rank": previous_rank,
            "current_rank": current_rank,
            "rank_changed": rank_changed,
            "new_skills": new_skills,
            "new_perks": new_perks
        }
    
    def _update_combat_rank(self, character_id: str) -> None:
        """Met à jour le rang de combat en fonction de l'expérience"""
        if character_id not in self.combat_experience:
            return
            
        exp = self.combat_experience[character_id]
        
        # Seuils d'expérience pour chaque rang
        rank_thresholds = {
            CombatRank.NOVICE: 0,
            CombatRank.APPRENTICE: 1000,
            CombatRank.ADEPT: 3000,
            CombatRank.EXPERT: 7000,
            CombatRank.MASTER: 15000,
            CombatRank.GRANDMASTER: 30000
        }
        
        # Déterminer le nouveau rang
        new_rank = CombatRank.NOVICE
        for rank, threshold in rank_thresholds.items():
            if exp >= threshold:
                new_rank = rank
        
        # Mettre à jour le rang
        old_rank = self.combat_ranks.get(character_id, CombatRank.NOVICE)
        if new_rank != old_rank:
            self.combat_ranks[character_id] = new_rank
            logger.info(f"Personnage {character_id} a progressé du rang {old_rank.name} au rang {new_rank.name}")
    
    def _improve_combat_skills(self, character_id: str) -> Dict[str, Any]:
        """Améliore les compétences de combat lors d'un changement de rang"""
        if character_id not in self.combat_skills:
            return {"success": False, "message": "Personnage non initialisé"}
            
        # Récupérer le style de combat
        style = self.combat_styles.get(character_id, CombatStyle.BALANCED)
        
        # Déterminer les compétences à améliorer en fonction du style
        skill_weights = {
            "melee": 1,
            "ranged": 1,
            "defense": 1,
            "tactics": 1,
            "perception": 1
        }
        
        # Ajuster les poids en fonction du style
        if style == CombatStyle.AGGRESSIVE:
            skill_weights["melee"] = 3
            skill_weights["ranged"] = 2
        elif style == CombatStyle.DEFENSIVE:
            skill_weights["defense"] = 3
            skill_weights["tactics"] = 2
        elif style == CombatStyle.TECHNICAL:
            skill_weights["tactics"] = 3
            skill_weights["perception"] = 2
        elif style == CombatStyle.EVASIVE:
            skill_weights["perception"] = 3
            skill_weights["defense"] = 2
        elif style == CombatStyle.PRECISE:
            skill_weights["ranged"] = 3
            skill_weights["perception"] = 2
        
        # Sélectionner les compétences à améliorer
        num_improvements = 2  # 2 compétences par rang
        improved_skills = []
        
        # Créer une liste pondérée pour la sélection
        weighted_skills = []
        for skill, weight in skill_weights.items():
            weighted_skills.extend([skill] * weight)
            
        # Sélectionner les compétences à améliorer
        for _ in range(num_improvements):
            if not weighted_skills:
                break
                
            # Sélectionner une compétence
            selected_skill = random.choice(weighted_skills)
            
            # Supprimer toutes les occurrences de cette compétence
            weighted_skills = [s for s in weighted_skills if s != selected_skill]
            
            # Améliorer la compétence
            self.combat_skills[character_id][selected_skill] += 1
            
            improved_skills.append({
                "skill": selected_skill,
                "new_level": self.combat_skills[character_id][selected_skill]
            })
        
        return {
            "success": True,
            "improved_skills": improved_skills
        }
    
    def _award_combat_perk(self, character_id: str) -> Dict[str, Any]:
        """Attribue un avantage de combat lors d'un changement de rang"""
        if character_id not in self.combat_perks:
            return {"success": False, "message": "Personnage non initialisé"}
            
        # Récupérer le rang actuel
        rank = self.combat_ranks.get(character_id, CombatRank.NOVICE)
        
        # Liste des avantages disponibles par rang
        available_perks = {
            CombatRank.NOVICE: [
                {"id": "quick_reflexes", "name": "Réflexes rapides", "description": "Augmente légèrement la chance d'esquiver"},
                {"id": "steady_aim", "name": "Visée stable", "description": "Augmente légèrement la précision des attaques à distance"}
            ],
            CombatRank.APPRENTICE: [
                {"id": "combat_focus", "name": "Concentration au combat", "description": "Augmente les dégâts critiques"},
                {"id": "tactical_movement", "name": "Mouvement tactique", "description": "Réduit les pénalités de mouvement en combat"}
            ],
            CombatRank.ADEPT: [
                {"id": "counter_strike", "name": "Contre-attaque", "description": "Chance de contre-attaquer après une esquive réussie"},
                {"id": "weapon_specialist", "name": "Spécialiste d'armes", "description": "Bonus de dégâts avec le type d'arme préféré"}
            ],
            CombatRank.EXPERT: [
                {"id": "combat_intuition", "name": "Intuition de combat", "description": "Prévoit les attaques ennemies, augmentant l'esquive"},
                {"id": "precision_strikes", "name": "Frappes de précision", "description": "Ignore une partie de l'armure ennemie"}
            ],
            CombatRank.MASTER: [
                {"id": "battle_trance", "name": "Transe de bataille", "description": "Augmente toutes les statistiques de combat pendant un court moment"},
                {"id": "tactical_genius", "name": "Génie tactique", "description": "Bonus de combat pour toute l'équipe"}
            ],
            CombatRank.GRANDMASTER: [
                {"id": "legendary_fighter", "name": "Combattant légendaire", "description": "Chance de réaliser une attaque dévastatrice"},
                {"id": "combat_mastery", "name": "Maîtrise du combat", "description": "Réduit le coût en énergie des techniques spéciales"}
            ]
        }
        
        # Filtrer les avantages déjà obtenus
        current_perks = self.combat_perks[character_id]
        current_perk_ids = [p["id"] for p in current_perks]
        
        # Récupérer les avantages disponibles pour le rang actuel et les rangs inférieurs
        available_rank_perks = []
        for r in CombatRank:
            if r.value <= rank.value:
                available_rank_perks.extend(available_perks.get(r, []))
        
        # Filtrer les avantages déjà obtenus
        available_rank_perks = [p for p in available_rank_perks if p["id"] not in current_perk_ids]
        
        # Si aucun avantage disponible, retourner un échec
        if not available_rank_perks:
            return {"success": False, "message": "Aucun avantage disponible"}
            
        # Sélectionner un avantage aléatoire
        selected_perk = random.choice(available_rank_perks)
        
        # Ajouter l'avantage
        self.combat_perks[character_id].append(selected_perk)
        
        return {
            "success": True,
            "perk": selected_perk
        }
