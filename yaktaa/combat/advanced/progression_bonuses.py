"""
Système de calcul des bonus de progression de combat pour YakTaa
"""

import logging
from typing import Dict, List, Any, Optional

from .progression import CombatProgressionSystem, CombatStyle, CombatRank

logger = logging.getLogger("YakTaa.Combat.Advanced.ProgressionBonuses")

class CombatProgressionBonuses:
    """
    Système qui gère les bonus de combat liés à la progression
    """
    
    def __init__(self, progression_system: CombatProgressionSystem):
        """
        Initialise le système de bonus de progression
        
        Args:
            progression_system: Le système de progression principal
        """
        self.progression_system = progression_system
        logger.debug("Système de bonus de progression de combat initialisé")
    
    def get_combat_profile(self, character_id: str) -> Dict[str, Any]:
        """
        Récupère le profil de combat complet d'un personnage
        
        Args:
            character_id: Identifiant du personnage
            
        Returns:
            Profil de combat
        """
        if character_id not in self.progression_system.combat_experience:
            return {"success": False, "message": "Personnage non initialisé"}
            
        return {
            "success": True,
            "character_id": character_id,
            "experience": self.progression_system.combat_experience.get(character_id, 0),
            "rank": self.progression_system.combat_ranks.get(character_id, CombatRank.NOVICE),
            "style": self.progression_system.combat_styles.get(character_id, CombatStyle.BALANCED),
            "skills": self.progression_system.combat_skills.get(character_id, {}),
            "perks": self.progression_system.combat_perks.get(character_id, [])
        }
    
    def get_combat_bonuses(self, character_id: str) -> Dict[str, Any]:
        """
        Calcule les bonus de combat en fonction du profil
        
        Args:
            character_id: Identifiant du personnage
            
        Returns:
            Bonus de combat
        """
        if character_id not in self.progression_system.combat_experience:
            return {}
            
        # Récupérer le profil
        profile = self.get_combat_profile(character_id)
        if not profile["success"]:
            return {}
            
        # Initialiser les bonus
        bonuses = {
            "damage_multiplier": 1.0,
            "critical_chance": 0.0,
            "critical_multiplier": 1.5,
            "hit_chance": 0.0,
            "evasion": 0.0,
            "damage_reduction": 0.0,
            "initiative": 0
        }
        
        # Bonus de compétences
        skills = profile["skills"]
        bonuses["damage_multiplier"] += (skills.get("melee", 1) - 1) * 0.05  # +5% par niveau
        bonuses["hit_chance"] += (skills.get("ranged", 1) - 1) * 0.02  # +2% par niveau
        bonuses["damage_reduction"] += (skills.get("defense", 1) - 1) * 0.02  # +2% par niveau
        bonuses["critical_chance"] += (skills.get("tactics", 1) - 1) * 0.01  # +1% par niveau
        bonuses["evasion"] += (skills.get("perception", 1) - 1) * 0.02  # +2% par niveau
        
        # Bonus de style
        style = profile["style"]
        if style == CombatStyle.AGGRESSIVE:
            bonuses["damage_multiplier"] += 0.2  # +20% de dégâts
            bonuses["damage_reduction"] -= 0.1  # -10% de réduction de dégâts
        elif style == CombatStyle.DEFENSIVE:
            bonuses["damage_multiplier"] -= 0.1  # -10% de dégâts
            bonuses["damage_reduction"] += 0.2  # +20% de réduction de dégâts
        elif style == CombatStyle.TECHNICAL:
            bonuses["critical_chance"] += 0.1  # +10% de chance critique
            bonuses["critical_multiplier"] += 0.5  # +0.5 au multiplicateur critique
        elif style == CombatStyle.EVASIVE:
            bonuses["evasion"] += 0.15  # +15% d'esquive
            bonuses["initiative"] += 2  # +2 en initiative
        elif style == CombatStyle.PRECISE:
            bonuses["hit_chance"] += 0.15  # +15% de chance de toucher
            bonuses["damage_multiplier"] += 0.1  # +10% de dégâts
        
        # Bonus d'avantages
        perks = profile["perks"]
        for perk in perks:
            perk_id = perk["id"]
            
            if perk_id == "quick_reflexes":
                bonuses["evasion"] += 0.05  # +5% d'esquive
            elif perk_id == "steady_aim":
                bonuses["hit_chance"] += 0.05  # +5% de chance de toucher
            elif perk_id == "combat_focus":
                bonuses["critical_multiplier"] += 0.2  # +0.2 au multiplicateur critique
            elif perk_id == "tactical_movement":
                bonuses["initiative"] += 1  # +1 en initiative
            elif perk_id == "counter_strike":
                bonuses["counter_attack_chance"] = 0.3  # 30% de chance de contre-attaque
            elif perk_id == "weapon_specialist":
                bonuses["weapon_specialist_bonus"] = 0.15  # +15% avec l'arme préférée
            elif perk_id == "combat_intuition":
                bonuses["evasion"] += 0.1  # +10% d'esquive
            elif perk_id == "precision_strikes":
                bonuses["armor_penetration"] = 0.2  # 20% de pénétration d'armure
            elif perk_id == "battle_trance":
                bonuses["battle_trance_available"] = True  # Transe de bataille disponible
            elif perk_id == "tactical_genius":
                bonuses["team_bonus"] = 0.1  # +10% pour l'équipe
            elif perk_id == "legendary_fighter":
                bonuses["devastating_attack_chance"] = 0.05  # 5% de chance d'attaque dévastatrice
            elif perk_id == "combat_mastery":
                bonuses["special_technique_cost_reduction"] = 0.3  # -30% de coût
        
        return bonuses
    
    def apply_experience_for_action(self, character_id: str, action_type: str, 
                                   success: bool, difficulty: int = 1) -> Dict[str, Any]:
        """
        Attribue de l'expérience en fonction d'une action de combat
        
        Args:
            character_id: Identifiant du personnage
            action_type: Type d'action (attack, defend, special, etc.)
            success: Si l'action a réussi
            difficulty: Difficulté de l'action (1-10)
            
        Returns:
            Résultat de l'attribution d'expérience
        """
        if character_id not in self.progression_system.combat_experience:
            self.progression_system.initialize_character(character_id)
            
        # Calculer l'expérience de base
        base_exp = difficulty * 5  # 5 XP par niveau de difficulté
        
        # Modificateur de réussite
        success_modifier = 1.5 if success else 0.5  # +50% si réussite, -50% si échec
        
        # Modificateur de type d'action
        action_modifiers = {
            "attack": 1.0,
            "defend": 0.8,
            "special": 1.2,
            "support": 0.9,
            "tactical": 1.1
        }
        
        action_modifier = action_modifiers.get(action_type, 1.0)
        
        # Calculer l'expérience finale
        exp_amount = int(base_exp * success_modifier * action_modifier)
        
        # Attribuer l'expérience
        return self.progression_system.award_combat_experience(character_id, exp_amount)
    
    def calculate_rank_up_requirements(self, character_id: str) -> Dict[str, Any]:
        """
        Calcule les exigences pour monter en rang
        
        Args:
            character_id: Identifiant du personnage
            
        Returns:
            Exigences pour monter en rang
        """
        if character_id not in self.progression_system.combat_experience:
            return {"success": False, "message": "Personnage non initialisé"}
            
        # Récupérer le profil
        profile = self.get_combat_profile(character_id)
        if not profile["success"]:
            return {"success": False, "message": "Échec de récupération du profil"}
            
        # Récupérer le rang et l'expérience actuels
        current_rank = profile["rank"]
        current_exp = profile["experience"]
        
        # Vérifier si le personnage est déjà au rang maximum
        if current_rank == CombatRank.GRANDMASTER:
            return {
                "success": True,
                "character_id": character_id,
                "current_rank": current_rank,
                "current_exp": current_exp,
                "is_max_rank": True,
                "next_rank": None,
                "exp_required": 0,
                "exp_remaining": 0,
                "percent_complete": 100
            }
            
        # Seuils d'expérience pour chaque rang
        rank_thresholds = {
            CombatRank.NOVICE: 0,
            CombatRank.APPRENTICE: 1000,
            CombatRank.ADEPT: 3000,
            CombatRank.EXPERT: 7000,
            CombatRank.MASTER: 15000,
            CombatRank.GRANDMASTER: 30000
        }
        
        # Déterminer le prochain rang
        next_rank = None
        for r in CombatRank:
            if r.value == current_rank.value + 1:
                next_rank = r
                break
                
        if not next_rank:
            return {"success": False, "message": "Impossible de déterminer le prochain rang"}
            
        # Calculer l'expérience requise et restante
        exp_required = rank_thresholds[next_rank] - rank_thresholds[current_rank]
        current_tier_exp = current_exp - rank_thresholds[current_rank]
        exp_remaining = exp_required - current_tier_exp
        
        # Calculer le pourcentage de progression
        percent_complete = min(100, int((current_tier_exp / exp_required) * 100))
        
        return {
            "success": True,
            "character_id": character_id,
            "current_rank": current_rank,
            "current_exp": current_exp,
            "is_max_rank": False,
            "next_rank": next_rank,
            "exp_required": exp_required,
            "exp_remaining": exp_remaining,
            "percent_complete": percent_complete
        }
    
    def set_combat_style(self, character_id: str, style: CombatStyle) -> Dict[str, Any]:
        """
        Définit le style de combat d'un personnage
        
        Args:
            character_id: Identifiant du personnage
            style: Nouveau style de combat
            
        Returns:
            Résultat du changement de style
        """
        return self.progression_system.set_combat_style(character_id, style)
    
    def get_perk_effects(self, character_id: str, combat_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Récupère les effets des avantages de combat dans un contexte donné
        
        Args:
            character_id: Identifiant du personnage
            combat_context: Contexte de combat (optionnel)
            
        Returns:
            Effets des avantages
        """
        if character_id not in self.progression_system.combat_perks:
            return {"success": False, "message": "Personnage non initialisé"}
            
        # Récupérer les avantages
        perks = self.progression_system.combat_perks.get(character_id, [])
        
        # Initialiser les effets
        effects = {
            "passive_effects": [],
            "active_abilities": [],
            "conditional_effects": []
        }
        
        # Classer les avantages
        for perk in perks:
            perk_id = perk["id"]
            
            # Avantages passifs
            if perk_id in ["quick_reflexes", "steady_aim", "combat_focus", "tactical_movement", 
                          "combat_intuition", "precision_strikes"]:
                effects["passive_effects"].append(perk)
                
            # Capacités actives
            elif perk_id in ["battle_trance", "combat_mastery"]:
                effects["active_abilities"].append(perk)
                
            # Effets conditionnels
            elif perk_id in ["counter_strike", "weapon_specialist", "tactical_genius", 
                            "legendary_fighter"]:
                effects["conditional_effects"].append(perk)
        
        # Si un contexte de combat est fourni, filtrer les effets pertinents
        if combat_context:
            # Filtrer les effets conditionnels pertinents
            filtered_conditionals = []
            
            for perk in effects["conditional_effects"]:
                perk_id = perk["id"]
                
                if perk_id == "counter_strike" and combat_context.get("is_defending", False):
                    # Pertinent en défense
                    filtered_conditionals.append(perk)
                elif perk_id == "weapon_specialist" and combat_context.get("weapon_type") == combat_context.get("preferred_weapon_type"):
                    # Pertinent si utilisation de l'arme préférée
                    filtered_conditionals.append(perk)
                elif perk_id == "tactical_genius" and combat_context.get("in_group", False):
                    # Pertinent en groupe
                    filtered_conditionals.append(perk)
                elif perk_id == "legendary_fighter" and combat_context.get("is_attacking", False):
                    # Pertinent en attaque
                    filtered_conditionals.append(perk)
            
            effects["conditional_effects"] = filtered_conditionals
        
        return {
            "success": True,
            "character_id": character_id,
            "effects": effects
        }
    
    def get_skill_levels(self, character_id: str) -> Dict[str, Any]:
        """
        Récupère les niveaux de compétence d'un personnage
        
        Args:
            character_id: Identifiant du personnage
            
        Returns:
            Niveaux de compétence
        """
        if character_id not in self.progression_system.combat_skills:
            return {"success": False, "message": "Personnage non initialisé"}
            
        return {
            "success": True,
            "character_id": character_id,
            "skills": self.progression_system.combat_skills[character_id],
            "total_skill_level": sum(self.progression_system.combat_skills[character_id].values())
        }
