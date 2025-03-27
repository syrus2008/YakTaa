"""
Module pour la gestion du joueur dans YakTaa
Ce module étend la classe Character pour créer un joueur avec des fonctionnalités spécifiques.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import random

from .character import Character, Skill, Attribute

logger = logging.getLogger("Yak_Taa.Characters.Player")


class Player(Character):
    """
    Classe représentant le joueur dans le jeu
    Étend la classe Character avec des fonctionnalités spécifiques au joueur
    """

    def __init__(self, name: str):
        """Initialise un joueur"""
        super().__init__(name, "player")

        # Statistiques spécifiques au joueur
        self.missions_completed = 0
        self.missions_failed = 0
        self.systems_hacked = 0
        self.distance_traveled = 0  # en km
        self.time_played = 0  # en secondes

        # Équipement actif
        self.active_equipment = {
            # Matériel informatique
            "cpu": None,
            "memory": None,
            "storage": None,
            "network": None,
            "security": None,
            "tool": None,

            # Équipement de combat et implants
            "weapon": None,  # Arme principale
            "secondary_weapon": None,  # Arme secondaire
            "implant_cerebral": None,  # Implant cérébral
            "implant_ocular": None,  # Implant oculaire
            "implant_neural": None,  # Implant neural
            "implant_dermal": None,  # Implant cutané
            "implant_skeletal": None,  # Implant squelettique
            "implant_muscular": None,  # Implant musculaire
        }

        # Compétences débloquées
        self.unlocked_abilities: Set[str] = set()

        # Contacts et relations
        self.contacts: Dict[str, int] = {}  # nom du contact -> niveau de relation

        # Objectifs actuels
        self.current_objectives: List[Dict[str, Any]] = []

        logger.info(f"Nouveau joueur créé : {name}")

    def complete_mission(self, mission_id: str, reward_xp: int, reward_credits: int) -> None:
        """Marque une mission comme terminée et attribue les récompenses"""
        self.missions_completed += 1
        self.add_experience(reward_xp)
        self.add_credits(reward_credits)

        # Ajouter à l'historique des missions
        self.mission_history.append({
            "mission_id": mission_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "rewards": {
                "xp": reward_xp,
                "credits": reward_credits
            }
        })

        logger.info(f"Mission {mission_id} terminée. Récompenses : {reward_xp} XP, {reward_credits} crédits")

    def fail_mission(self, mission_id: str) -> None:
        """Marque une mission comme échouée"""
        self.missions_failed += 1

        # Ajouter à l'historique des missions
        self.mission_history.append({
            "mission_id": mission_id,
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Mission {mission_id} échouée.")

    def hack_system(self, system_id: str, difficulty: int) -> bool:
        """Simule le hacking d'un système et attribue de l'expérience en fonction de la difficulté"""
        # Calculer les chances de succès en fonction des compétences
        programming_skill = self.get_skill("programming")
        network_skill = self.get_skill("network_security")
        crypto_skill = self.get_skill("cryptography")

        if not programming_skill or not network_skill or not crypto_skill:
            logger.warning("Compétences de hacking manquantes")
            return False

        # Moyenne des compétences de hacking
        hacking_level = (programming_skill.level + network_skill.level + crypto_skill.level) / 3

        # Chance de succès basée sur le niveau de hacking et la difficulté
        success_chance = min(90, max(10, (hacking_level * 100 / difficulty)))
        success = random.random() * 100 < success_chance

        if success:
            # Attribuer de l'expérience en fonction de la difficulté
            xp_reward = difficulty * 10
            self.add_experience(xp_reward // 3)  # XP générale

            # Répartir l'XP entre les compétences de hacking
            programming_skill.add_experience(xp_reward)
            network_skill.add_experience(xp_reward)
            crypto_skill.add_experience(xp_reward)

            self.systems_hacked += 1
            logger.info(f"Système {system_id} hacké avec succès. Récompense : {xp_reward} XP")
        else:
            logger.info(f"Échec du hacking du système {system_id}")

        return success

    def travel(self, distance: float) -> None:
        """Enregistre un déplacement du joueur"""
        self.distance_traveled += distance
        logger.info(f"Déplacement de {distance} km. Distance totale : {self.distance_traveled} km")

    def add_contact(self, name: str, initial_relation: int = 0) -> None:
        """Ajoute un nouveau contact au réseau du joueur"""
        self.contacts[name] = initial_relation
        logger.info(f"Nouveau contact ajouté : {name}")

    def update_contact_relation(self, name: str, change: int) -> bool:
        """Met à jour la relation avec un contact"""
        if name not in self.contacts:
            logger.warning(f"Tentative de mettre à jour un contact inexistant : {name}")
            return False

        old_relation = self.contacts[name]
        self.contacts[name] = max(-100, min(100, old_relation + change))

        logger.info(f"Relation avec {name} mise à jour : {old_relation} -> {self.contacts[name]}")
        return True

    def add_objective(self, objective_id: str, title: str, description: str, reward_xp: int, reward_credits: int) -> None:
        """Ajoute un nouvel objectif à la liste des objectifs actuels"""
        objective = {
            "id": objective_id,
            "title": title,
            "description": description,
            "status": "active",
            "progress": 0,
            "rewards": {
                "xp": reward_xp,
                "credits": reward_credits
            },
            "created_at": datetime.now().isoformat()
        }

        self.current_objectives.append(objective)
        logger.info(f"Nouvel objectif ajouté : {title}")

    def complete_objective(self, objective_id: str) -> bool:
        """Marque un objectif comme terminé et attribue les récompenses"""
        for i, objective in enumerate(self.current_objectives):
            if objective["id"] == objective_id:
                # Attribuer les récompenses
                reward_xp = objective["rewards"]["xp"]
                reward_credits = objective["rewards"]["credits"]

                self.add_experience(reward_xp)
                self.add_credits(reward_credits)

                # Mettre à jour le statut de l'objectif
                self.current_objectives[i]["status"] = "completed"
                self.current_objectives[i]["completed_at"] = datetime.now().isoformat()

                logger.info(f"Objectif {objective['title']} terminé. Récompenses : {reward_xp} XP, {reward_credits} crédits")
                return True

        logger.warning(f"Tentative de terminer un objectif inexistant : {objective_id}")
        return False

    def update_objective_progress(self, objective_id: str, progress: int) -> bool:
        """Met à jour la progression d'un objectif"""
        for i, objective in enumerate(self.current_objectives):
            if objective["id"] == objective_id:
                old_progress = objective["progress"]
                self.current_objectives[i]["progress"] = min(100, max(0, progress))

                logger.info(f"Progression de l'objectif {objective['title']} mise à jour : {old_progress}% -> {progress}%")
                return True

        logger.warning(f"Tentative de mettre à jour un objectif inexistant : {objective_id}")
        return False

    def equip_item(self, slot: str, item: Any) -> bool:
        """Équipe un objet dans un slot d'équipement"""
        if slot not in self.active_equipment:
            logger.warning(f"Tentative d'équiper un objet dans un slot inexistant : {slot}")
            return False

        self.active_equipment[slot] = item
        logger.info(f"Objet équipé dans le slot {slot} : {item}")
        return True

    def unequip_item(self, slot: str) -> Any:
        """Déséquipe un objet d'un slot d'équipement"""
        if slot not in self.active_equipment:
            logger.warning(f"Tentative de déséquiper un objet d'un slot inexistant : {slot}")
            return None

        item = self.active_equipment[slot]
        self.active_equipment[slot] = None

        if item:
            logger.info(f"Objet déséquipé du slot {slot} : {item}")

        return item

    def unlock_ability(self, ability_id: str) -> bool:
        """Débloque une nouvelle capacité pour le joueur"""
        if ability_id in self.unlocked_abilities:
            logger.warning(f"Tentative de débloquer une capacité déjà débloquée : {ability_id}")
            return False

        self.unlocked_abilities.add(ability_id)
        logger.info(f"Nouvelle capacité débloquée : {ability_id}")
        return True

    def has_ability(self, ability_id: str) -> bool:
        """Vérifie si le joueur a débloqué une capacité"""
        return ability_id in self.unlocked_abilities

    def get_effective_stats(self) -> Dict[str, int]:
        """Calcule les statistiques effectives incluant les bonus d'équipement"""
        # Commencer avec les statistiques de base
        effective_stats = {
            attr_id: attr.value for attr_id, attr in self.attributes.items()
        }

        # Ajouter les compétences
        for skill_id, skill in self.skills.items():
            effective_stats[skill_id] = skill.level

        # Ajouter les bonus des équipements
        for slot, item in self.active_equipment.items():
            # Les implants ont des stats_bonus
            if item and hasattr(item, 'stats_bonus'):
                for stat, bonus in item.stats_bonus.items():
                    if stat in effective_stats:
                        effective_stats[stat] += bonus
                    else:
                        effective_stats[stat] = bonus

            # Le matériel hardware a des stats
            if item and hasattr(item, 'stats'):
                for stat, bonus in item.stats.items():
                    if stat in effective_stats:
                        effective_stats[stat] += bonus
                    else:
                        effective_stats[stat] = bonus

        logger.debug(f"Statistiques effectives calculées pour {self.name}: {effective_stats}")
        return effective_stats

    def calculate_weapon_damage(self, target=None) -> Dict[str, Any]:
        """Calcule les dégâts de l'arme équipée"""
        weapon = self.active_equipment.get("weapon")
        if not weapon:
            return {
                "damage": 0,
                "type": "PHYSICAL",
                "critical": False,
                "special_effects": [],
                "message": f"{self.name} attaque sans arme équipée"
            }
            
        # Récupérer les statistiques effectives incluant les bonus
        effective_stats = self.get_effective_stats()
        
        # Vérifier si l'arme est une arme spéciale en vérifiant son dictionnaire
        is_special_weapon = isinstance(weapon, dict) and "is_special" in weapon and weapon["is_special"]
        
        # Base de dégâts pour armes normales
        if not is_special_weapon:
            # Dégâts de base de l'arme
            base_damage = getattr(weapon, 'damage', 5)
            
            # Type de dégâts
            damage_type = getattr(weapon, 'damage_type', "PHYSICAL")
            
            # Bonus de dégâts basés sur les statistiques du joueur
            stat_bonus = 0
            if hasattr(weapon, 'damage_stat'):
                primary_stat = weapon.damage_stat
                stat_bonus = effective_stats.get(primary_stat, 0) // 5  # Chaque 5 points donne +1 dégât
        else:
            # Pour les armes spéciales, utiliser les données du dictionnaire
            base_damage = weapon.get("base_damage", 10)
            damage_type = weapon.get("damage_type", "PHYSICAL")
            
            # Les armes spéciales peuvent avoir leur propre logique de bonus de stats
            primary_stat = weapon.get("primary_stat", "strength")
            stat_bonus = effective_stats.get(primary_stat, 0) // 4  # Légèrement meilleur ratio
        
        # Appliquer le bonus de stats
        damage = base_damage + stat_bonus
        
        # Multiplicateur de dégâts (commence à 1.0)
        damage_multiplier = 1.0
        
        # Bonus de l'équipement/implants
        combat_bonuses = {}
        
        # Parcourir les implants et appliquer leurs bonus
        for slot, item in self.active_equipment.items():
            if item and slot.startswith("implant_") and hasattr(item, 'get_combat_bonus'):
                # Bonus au multiplicateur de dégâts
                damage_bonus = item.get_combat_bonus("damage_multiplier")
                if damage_bonus > 0:
                    damage_multiplier += (damage_bonus - 1.0)  # Convertir le multiplicateur en bonus
                    combat_bonuses["damage_multiplier"] = damage_bonus
                
                # Bonus aux chances de coup critique
                crit_bonus = item.get_combat_bonus("critical_chance")
                if crit_bonus > 0:
                    combat_bonuses["critical_chance"] = crit_bonus
                
                # Bonus au multiplicateur de dégâts critiques
                crit_damage_bonus = item.get_combat_bonus("critical_damage_multiplier")
                if crit_damage_bonus > 0:
                    combat_bonuses["critical_damage_multiplier"] = crit_damage_bonus
                
                # Bénéficie-t-on d'une pénétration d'armure ?
                armor_pen = item.get_combat_bonus("armor_penetration")
                if armor_pen > 0:
                    combat_bonuses["armor_penetration"] = armor_pen
        
        # Calculer les chances de coup critique (base + arme + implants)
        base_crit_chance = 0.05 + (effective_stats.get('reflexes', 0) / 100)  # 5% de base + bonus
        
        # Chance de critique différente selon le type d'arme
        if not is_special_weapon:
            weapon_crit_chance = getattr(weapon, 'critical_chance', 0.0)
        else:
            weapon_crit_chance = weapon.get("critical_chance", 0.1)  # Les armes spéciales ont une base de 10%
            
        final_crit_chance = base_crit_chance + weapon_crit_chance + combat_bonuses.get("critical_chance", 0.0)
        
        # Limiter la chance de critique à 75% maximum
        final_crit_chance = min(0.75, final_crit_chance)
        is_critical = random.random() < final_crit_chance
        
        # Calculer les dégâts finaux
        final_damage = damage * damage_multiplier
        
        # Appliquer le multiplicateur de dégâts critiques (1.5x par défaut, plus bonus des implants)
        if is_critical:
            if not is_special_weapon:
                crit_multiplier = 1.5 + combat_bonuses.get("critical_damage_multiplier", 0.0)
            else:
                # Les armes spéciales peuvent avoir un multiplicateur de critique personnalisé
                base_crit_multiplier = weapon.get("critical_damage_multiplier", 2.0)
                crit_multiplier = base_crit_multiplier + combat_bonuses.get("critical_damage_multiplier", 0.0) - 1.0
                
            final_damage *= crit_multiplier
        
        # Arrondir les dégâts
        final_damage = int(final_damage)
        
        # Récupérer les effets spéciaux
        if not is_special_weapon:
            special_effects = getattr(weapon, 'special_effects', [])
            weapon_name = getattr(weapon, 'name', "arme inconnue")
        else:
            special_effects = weapon.get("effects", [])
            weapon_name = weapon.get("name", "arme spéciale")
            
        # Message pour les logs
        message = f"{self.name} attaque avec {weapon_name} pour {final_damage} dégâts de type {damage_type}"
        if is_critical:
            message += " (CRITIQUE!)"
        
        # Ajouter des informations sur les bonus spéciaux si présents
        if special_effects:
            effect_names = [effect.get("name", "Effet inconnu") if isinstance(effect, dict) else effect for effect in special_effects]
            message += f" Effets: {', '.join(effect_names)}"
        
        logger.info(message)
        
        return {
            "damage": final_damage,
            "type": damage_type,
            "critical": is_critical,
            "special_effects": special_effects,
            "combat_bonuses": combat_bonuses,
            "is_special_weapon": is_special_weapon,
            "message": message
        }

    def apply_implant_effects(self, target=None) -> Dict[str, Any]:
        """Applique les effets spéciaux des implants
        
        Args:
            target: Cible optionnelle pour les effets qui en nécessitent une
            
        Returns:
            Dictionnaire contenant les résultats de l'application des effets
        """
        result = {
            "active_effects": [],
            "messages": [],
            "stats_modified": {},
            "target_effects": {}
        }

        # Parcourir tous les slots d'implants
        for slot, item in self.active_equipment.items():
            # Vérifier si c'est un implant avec la méthode apply_effects
            if item and slot.startswith("implant_") and hasattr(item, 'apply_effects'):
                # Appliquer les effets de l'implant
                effect_result = item.apply_effects(self, target)
                
                # Collecter les effets actifs
                if "applied_effects" in effect_result:
                    for effect in effect_result["applied_effects"]:
                        if effect not in result["active_effects"]:
                            result["active_effects"].append(effect)
                
                # Collecter les messages
                if "messages" in effect_result:
                    result["messages"].extend(effect_result["messages"])
                
                # Collecter les effets sur la cible
                if target and "target_analyzed" in effect_result and effect_result["target_analyzed"]:
                    result["target_effects"]["analyzed"] = True
                    
                if target and "target_visible" in effect_result and effect_result["target_visible"]:
                    result["target_effects"]["visible"] = True
                    
                # Collecter les chances d'esquive
                if "dodge_chance" in effect_result:
                    current_dodge = result["stats_modified"].get("dodge_chance", 0.0)
                    result["stats_modified"]["dodge_chance"] = max(current_dodge, effect_result["dodge_chance"])

        # Journaliser les effets appliqués
        if result["active_effects"]:
            logger.debug(f"Effets d'implants appliqués: {', '.join(result['active_effects'])}")
            
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le joueur en dictionnaire pour la sauvegarde"""
        data = super().to_dict()

        # Ajouter les données spécifiques au joueur
        data.update({
            "missions_completed": self.missions_completed,
            "missions_failed": self.missions_failed,
            "systems_hacked": self.systems_hacked,
            "distance_traveled": self.distance_traveled,
            "time_played": self.time_played,
            "active_equipment": self.active_equipment,
            "unlocked_abilities": list(self.unlocked_abilities),
            "contacts": self.contacts,
            "current_objectives": self.current_objectives,
            "mission_history": self.mission_history
        })

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Crée un joueur à partir d'un dictionnaire"""
        player = super(Player, cls).from_dict(data)

        # Charger les données spécifiques au joueur
        player.missions_completed = data.get("missions_completed", 0)
        player.missions_failed = data.get("missions_failed", 0)
        player.systems_hacked = data.get("systems_hacked", 0)
        player.distance_traveled = data.get("distance_traveled", 0)
        player.time_played = data.get("time_played", 0)
        player.active_equipment = data.get("active_equipment", {})
        player.unlocked_abilities = set(data.get("unlocked_abilities", []))
        player.contacts = data.get("contacts", {})
        player.current_objectives = data.get("current_objectives", [])
        player.mission_history = data.get("mission_history", [])

        return player


# Fonction pour créer un joueur de test
def create_test_player() -> Player:
    """Crée un joueur de test pour le développement"""
    player = Player("NetRunner")

    # Améliorer quelques compétences
    player.improve_skill("programming", 1000)
    player.improve_skill("network_security", 800)
    player.improve_skill("cryptography", 600)
    player.improve_skill("electronics", 400)

    # Ajouter de l'expérience
    player.add_experience(2000)

    # Ajouter des crédits
    player.add_credits(10000)

    # Ajouter de la réputation
    player.update_reputation("NetRunners", 75)
    player.update_reputation("Corporations", -50)
    player.update_reputation("Fixers", 30)

    # Ajouter des contacts
    player.add_contact("Fixer", 60)
    player.add_contact("Ripperdoc", 40)
    player.add_contact("Informateur", 20)

    # Ajouter des objectifs
    player.add_objective(
        "main_01",
        "Trouver l'informateur",
        "Localiser et rencontrer l'informateur dans le quartier de Shibuya.",
        500,
        1000
    )
    player.add_objective(
        "side_01",
        "Récupérer les données volées",
        "Hacker le système de Arasaka Corp pour récupérer les données volées.",
        300,
        800
    )

    # Débloquer des capacités
    player.unlock_ability("remote_hack")
    player.unlock_ability("stealth_mode")

    # Simuler quelques missions terminées
    player.complete_mission("tutorial", 100, 500)

    return player
