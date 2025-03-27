"""
Système de combat en groupe pour YakTaa
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

logger = logging.getLogger("YakTaa.Combat.Advanced.Group")

class FormationType(Enum):
    """Types de formations de groupe"""
    LINE = auto()       # Ligne
    WEDGE = auto()      # Coin
    CIRCLE = auto()     # Cercle
    SCATTERED = auto()  # Dispersé
    FLANKING = auto()   # À revers

class RoleType(Enum):
    """Types de rôles dans un groupe"""
    TANK = auto()       # Encaisse les dégâts
    DAMAGE = auto()     # Inflige des dégâts
    SUPPORT = auto()    # Soutien et soins
    CONTROL = auto()    # Contrôle des ennemis
    UTILITY = auto()    # Utilitaire et soutien technique

class GroupCombatSystem:
    """
    Système qui gère le combat en groupe
    """
    
    def __init__(self):
        """Initialise le système de combat en groupe"""
        self.groups = {}  # ID -> groupe
        self.ally_bonuses = {}  # ID -> bonus d'allié
        self.synergy_effects = {}  # (ID1, ID2) -> effets de synergie
        self.threat_tables = {}  # ID -> table de menace
        
        logger.debug("Système de combat en groupe initialisé")
    
    def create_group(self, group_id: str, members: List[Any]) -> None:
        """
        Crée un groupe de combat
        
        Args:
            group_id: Identifiant du groupe
            members: Liste des membres
        """
        if group_id in self.groups:
            logger.warning(f"Le groupe {group_id} existe déjà")
            return
            
        # Déterminer les rôles automatiquement
        roles = self._assign_roles(members)
        
        # Créer le groupe
        self.groups[group_id] = {
            "id": group_id,
            "members": members,
            "roles": roles,
            "formation": FormationType.LINE,
            "leader": self._select_leader(members),
            "status": "active"
        }
        
        # Initialiser les bonus d'alliés
        self.ally_bonuses[group_id] = {}
        
        # Initialiser la table de menace
        self.threat_tables[group_id] = {}
        
        # Calculer les synergies
        self._calculate_synergies(group_id)
        
        logger.debug(f"Groupe {group_id} créé avec {len(members)} membres")
    
    def _assign_roles(self, members: List[Any]) -> Dict[Any, RoleType]:
        """Assigne des rôles aux membres du groupe"""
        roles = {}
        
        for member in members:
            # Déterminer le rôle en fonction des statistiques et de l'équipement
            if hasattr(member, "get_effective_stats"):
                stats = member.get_effective_stats()
                
                # Vérifier l'équipement
                has_healing = False
                has_control = False
                has_tech = False
                
                if hasattr(member, "abilities"):
                    for ability in member.abilities:
                        if "heal" in ability.lower() or "soin" in ability.lower():
                            has_healing = True
                        if "stun" in ability.lower() or "freeze" in ability.lower() or "control" in ability.lower():
                            has_control = True
                        if "hack" in ability.lower() or "tech" in ability.lower():
                            has_tech = True
                
                # Déterminer le rôle principal
                if has_healing:
                    roles[member] = RoleType.SUPPORT
                elif has_control:
                    roles[member] = RoleType.CONTROL
                elif has_tech:
                    roles[member] = RoleType.UTILITY
                elif stats.get("endurance", 0) > stats.get("strength", 0):
                    roles[member] = RoleType.TANK
                else:
                    roles[member] = RoleType.DAMAGE
            else:
                # Par défaut, assigner un rôle de dégâts
                roles[member] = RoleType.DAMAGE
        
        return roles
    
    def _select_leader(self, members: List[Any]) -> Optional[Any]:
        """Sélectionne le leader du groupe"""
        if not members:
            return None
            
        # Critères de sélection du leader
        leader_scores = {}
        
        for member in members:
            score = 0
            
            # Le niveau est un bon indicateur
            score += getattr(member, "level", 1) * 10
            
            # Les membres avec plus de PV sont de meilleurs leaders
            score += getattr(member, "max_health", 100) / 10
            
            # Les membres avec de meilleures statistiques mentales sont de meilleurs leaders
            if hasattr(member, "get_effective_stats"):
                stats = member.get_effective_stats()
                score += stats.get("intelligence", 0) * 5
                score += stats.get("charisma", 0) * 8
                score += stats.get("perception", 0) * 3
            
            leader_scores[member] = score
        
        # Sélectionner le membre avec le score le plus élevé
        return max(leader_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_synergies(self, group_id: str) -> None:
        """Calcule les synergies entre les membres du groupe"""
        if group_id not in self.groups:
            return
            
        group = self.groups[group_id]
        members = group["members"]
        roles = group["roles"]
        
        # Réinitialiser les synergies
        self.synergy_effects[group_id] = {}
        
        # Vérifier les synergies entre chaque paire de membres
        for i, member1 in enumerate(members):
            for j, member2 in enumerate(members[i+1:], i+1):
                # Vérifier les synergies de rôle
                role1 = roles.get(member1)
                role2 = roles.get(member2)
                
                synergy_effects = []
                
                # Synergies de rôle
                if role1 == RoleType.TANK and role2 == RoleType.SUPPORT:
                    # Synergie tank + support
                    synergy_effects.append({
                        "name": "Bastion",
                        "description": "Le tank reçoit plus de soins",
                        "effect": {"healing_received_multiplier": 1.2}
                    })
                elif role1 == RoleType.DAMAGE and role2 == RoleType.CONTROL:
                    # Synergie dégâts + contrôle
                    synergy_effects.append({
                        "name": "Cible vulnérable",
                        "description": "Dégâts augmentés contre les cibles contrôlées",
                        "effect": {"damage_vs_controlled_multiplier": 1.3}
                    })
                elif role1 == RoleType.SUPPORT and role2 == RoleType.UTILITY:
                    # Synergie support + utilitaire
                    synergy_effects.append({
                        "name": "Amplification technique",
                        "description": "Effets de soutien améliorés",
                        "effect": {"support_effect_duration": 1}  # +1 tour de durée
                    })
                
                # Synergies d'équipement
                if hasattr(member1, "active_equipment") and hasattr(member2, "active_equipment"):
                    weapon1 = member1.active_equipment.get("weapon")
                    weapon2 = member2.active_equipment.get("weapon")
                    
                    if weapon1 and weapon2:
                        # Synergie d'armes
                        if hasattr(weapon1, "damage_type") and hasattr(weapon2, "damage_type"):
                            if weapon1.damage_type == "EMP" and weapon2.damage_type == "PHYSICAL":
                                # Synergie EMP + physique
                                synergy_effects.append({
                                    "name": "Surcharge systèmes",
                                    "description": "Les cibles affectées par EMP subissent plus de dégâts physiques",
                                    "effect": {"physical_damage_vs_emp_multiplier": 1.25}
                                })
                            elif weapon1.damage_type == "THERMAL" and weapon2.damage_type == "CHEMICAL":
                                # Synergie thermique + chimique
                                synergy_effects.append({
                                    "name": "Réaction catalytique",
                                    "description": "Chance d'effet de statut supplémentaire",
                                    "effect": {"status_effect_chance": 0.2}
                                })
                
                # Enregistrer les synergies
                if synergy_effects:
                    pair_key = (id(member1), id(member2))
                    self.synergy_effects[group_id][pair_key] = synergy_effects
                    
                    logger.debug(f"Synergies calculées entre {getattr(member1, 'name', str(member1))} et {getattr(member2, 'name', str(member2))}: {len(synergy_effects)} effets")
    
    def set_formation(self, group_id: str, formation: FormationType) -> None:
        """
        Définit la formation du groupe
        
        Args:
            group_id: Identifiant du groupe
            formation: Type de formation
        """
        if group_id not in self.groups:
            logger.warning(f"Le groupe {group_id} n'existe pas")
            return
            
        self.groups[group_id]["formation"] = formation
        
        # Appliquer les bonus de formation
        self._apply_formation_bonuses(group_id)
        
        logger.debug(f"Formation du groupe {group_id} définie: {formation.name}")
    
    def _apply_formation_bonuses(self, group_id: str) -> None:
        """Applique les bonus liés à la formation"""
        if group_id not in self.groups:
            return
            
        group = self.groups[group_id]
        formation = group["formation"]
        members = group["members"]
        
        # Réinitialiser les bonus d'alliés
        self.ally_bonuses[group_id] = {}
        
        # Appliquer les bonus en fonction de la formation
        if formation == FormationType.LINE:
            # Bonus de ligne: meilleure défense frontale
            for member in members:
                self.ally_bonuses[group_id][member] = {
                    "front_damage_reduction": 0.2,  # -20% de dégâts frontaux
                    "rear_vulnerability": 0.2  # +20% de dégâts par derrière
                }
        elif formation == FormationType.WEDGE:
            # Bonus de coin: bonus d'attaque pour le leader
            leader = group["leader"]
            if leader:
                self.ally_bonuses[group_id][leader] = {
                    "damage_multiplier": 1.2,  # +20% de dégâts
                    "critical_chance": 0.1  # +10% de chance de critique
                }
                
            # Bonus pour les autres membres
            for member in members:
                if member != leader:
                    self.ally_bonuses[group_id][member] = {
                        "damage_multiplier": 1.1  # +10% de dégâts
                    }
        elif formation == FormationType.CIRCLE:
            # Bonus de cercle: défense omnidirectionnelle
            for member in members:
                self.ally_bonuses[group_id][member] = {
                    "damage_reduction": 0.15,  # -15% de dégâts de toutes directions
                    "attack_penalty": 0.1  # -10% aux attaques
                }
        elif formation == FormationType.SCATTERED:
            # Bonus dispersé: difficile à cibler
            for member in members:
                self.ally_bonuses[group_id][member] = {
                    "evasion_bonus": 0.15,  # +15% d'esquive
                    "coordination_penalty": 0.1  # -10% aux actions coordonnées
                }
        elif formation == FormationType.FLANKING:
            # Bonus à revers: bonus aux attaques à revers
            for member in members:
                self.ally_bonuses[group_id][member] = {
                    "flank_damage_multiplier": 1.3,  # +30% de dégâts à revers
                    "stealth_bonus": 0.2  # +20% de discrétion
                }
    
    def get_ally_bonuses(self, member: Any) -> Dict[str, Any]:
        """
        Récupère les bonus d'allié pour un membre
        
        Args:
            member: Le membre concerné
            
        Returns:
            Dictionnaire des bonus
        """
        # Trouver le groupe du membre
        for group_id, group in self.groups.items():
            if member in group["members"]:
                return self.ally_bonuses.get(group_id, {}).get(member, {})
                
        return {}
    
    def get_synergy_effects(self, member: Any, target: Any = None) -> List[Dict[str, Any]]:
        """
        Récupère les effets de synergie pour un membre
        
        Args:
            member: Le membre concerné
            target: La cible optionnelle
            
        Returns:
            Liste des effets de synergie
        """
        effects = []
        
        # Trouver le groupe du membre
        for group_id, group in self.groups.items():
            if member in group["members"]:
                # Récupérer toutes les synergies impliquant ce membre
                for pair_key, synergies in self.synergy_effects.get(group_id, {}).items():
                    member1_id, member2_id = pair_key
                    
                    # Vérifier si le membre est impliqué dans cette synergie
                    if id(member) == member1_id or id(member) == member2_id:
                        # Si une cible est spécifiée, filtrer les effets pertinents
                        if target:
                            relevant_effects = []
                            for effect in synergies:
                                effect_data = effect["effect"]
                                
                                # Vérifier si l'effet s'applique à la cible
                                if "damage_vs_controlled_multiplier" in effect_data and hasattr(target, "status_effects"):
                                    if any(status in ["stunned", "frozen", "confused"] for status in target.status_effects):
                                        relevant_effects.append(effect)
                                elif "physical_damage_vs_emp_multiplier" in effect_data and hasattr(target, "status_effects"):
                                    if "emp_affected" in target.status_effects:
                                        relevant_effects.append(effect)
                                else:
                                    # Effets génériques
                                    relevant_effects.append(effect)
                                    
                            effects.extend(relevant_effects)
                        else:
                            # Sans cible spécifiée, ajouter tous les effets
                            effects.extend(synergies)
                
                break
                
        return effects
    
    def update_threat_table(self, group_id: str, target: Any, threat_value: int) -> None:
        """
        Met à jour la table de menace pour un groupe
        
        Args:
            group_id: Identifiant du groupe
            target: La cible
            threat_value: Valeur de menace à ajouter
        """
        if group_id not in self.threat_tables:
            self.threat_tables[group_id] = {}
            
        # Mettre à jour la menace
        current_threat = self.threat_tables[group_id].get(target, 0)
        self.threat_tables[group_id][target] = max(0, current_threat + threat_value)
        
        logger.debug(f"Menace mise à jour pour {getattr(target, 'name', str(target))} dans le groupe {group_id}: {self.threat_tables[group_id][target]}")
    
    def get_highest_threat_target(self, group_id: str) -> Optional[Any]:
        """
        Récupère la cible avec la plus haute menace
        
        Args:
            group_id: Identifiant du groupe
            
        Returns:
            La cible avec la plus haute menace ou None
        """
        if group_id not in self.threat_tables or not self.threat_tables[group_id]:
            return None
            
        # Trouver la cible avec la plus haute menace
        return max(self.threat_tables[group_id].items(), key=lambda x: x[1])[0]
    
    def coordinate_attack(self, group_id: str, target: Any) -> Dict[str, Any]:
        """
        Coordonne une attaque de groupe sur une cible
        
        Args:
            group_id: Identifiant du groupe
            target: La cible
            
        Returns:
            Résultat de l'attaque coordonnée
        """
        if group_id not in self.groups:
            return {"success": False, "message": f"Le groupe {group_id} n'existe pas"}
            
        group = self.groups[group_id]
        members = group["members"]
        formation = group["formation"]
        
        # Bonus de coordination en fonction de la formation
        coordination_bonus = 1.0
        if formation == FormationType.WEDGE:
            coordination_bonus = 1.2  # +20% en formation coin
        elif formation == FormationType.SCATTERED:
            coordination_bonus = 0.9  # -10% en formation dispersée
            
        # Calculer les dégâts totaux
        total_damage = 0
        participants = []
        
        for member in members:
            # Vérifier si le membre peut attaquer
            if not hasattr(member, "calculate_weapon_damage"):
                continue
                
            # Calculer les dégâts
            damage_result = member.calculate_weapon_damage(target)
            base_damage = damage_result.get("damage", 0)
            
            # Appliquer les bonus d'allié
            ally_bonus = self.ally_bonuses.get(group_id, {}).get(member, {})
            damage_multiplier = ally_bonus.get("damage_multiplier", 1.0)
            
            # Vérifier si c'est une attaque à revers
            if formation == FormationType.FLANKING:
                damage_multiplier *= ally_bonus.get("flank_damage_multiplier", 1.0)
                
            # Appliquer les synergies
            synergy_effects = self.get_synergy_effects(member, target)
            for effect in synergy_effects:
                effect_data = effect["effect"]
                
                # Appliquer les multiplicateurs de dégâts pertinents
                if "damage_vs_controlled_multiplier" in effect_data and hasattr(target, "status_effects"):
                    if any(status in ["stunned", "frozen", "confused"] for status in target.status_effects):
                        damage_multiplier *= effect_data["damage_vs_controlled_multiplier"]
                elif "physical_damage_vs_emp_multiplier" in effect_data and hasattr(target, "status_effects"):
                    if "emp_affected" in target.status_effects and damage_result.get("type") == "PHYSICAL":
                        damage_multiplier *= effect_data["physical_damage_vs_emp_multiplier"]
            
            # Calculer les dégâts finaux
            final_damage = int(base_damage * damage_multiplier * coordination_bonus)
            
            # Ajouter aux dégâts totaux
            total_damage += final_damage
            
            participants.append({
                "member": member,
                "damage": final_damage,
                "critical": damage_result.get("critical", False)
            })
            
            # Mettre à jour la menace
            self.update_threat_table(group_id, target, final_damage)
        
        # Appliquer les dégâts à la cible
        if hasattr(target, "health"):
            target.health -= total_damage
        
        return {
            "success": True,
            "message": f"Attaque coordonnée du groupe {group_id} sur {getattr(target, 'name', str(target))}",
            "total_damage": total_damage,
            "participants": participants,
            "target_health": getattr(target, "health", 0)
        }
    
    def coordinate_defense(self, group_id: str, attacker: Any, target: Any) -> Dict[str, Any]:
        """
        Coordonne une défense de groupe pour un membre
        
        Args:
            group_id: Identifiant du groupe
            attacker: L'attaquant
            target: Le membre à défendre
            
        Returns:
            Résultat de la défense coordonnée
        """
        if group_id not in self.groups:
            return {"success": False, "message": f"Le groupe {group_id} n'existe pas"}
            
        group = self.groups[group_id]
        members = group["members"]
        formation = group["formation"]
        
        # Vérifier si la cible est un membre du groupe
        if target not in members:
            return {"success": False, "message": f"{getattr(target, 'name', str(target))} n'est pas membre du groupe {group_id}"}
            
        # Bonus de défense en fonction de la formation
        defense_bonus = 1.0
        if formation == FormationType.CIRCLE:
            defense_bonus = 1.2  # +20% en formation cercle
        elif formation == FormationType.LINE:
            defense_bonus = 1.15  # +15% en formation ligne
            
        # Trouver les défenseurs potentiels
        defenders = []
        for member in members:
            if member == target:
                continue
                
            # Vérifier si le membre peut défendre
            if hasattr(member, "health") and member.health > 0:
                # Calculer la probabilité de défense
                defense_chance = 0.3  # 30% de base
                
                # Bonus pour les tanks
                if group["roles"].get(member) == RoleType.TANK:
                    defense_chance += 0.3  # +30% pour les tanks
                    
                # Vérifier si le membre défend
                if random.random() < defense_chance:
                    defenders.append(member)
        
        # Si personne ne défend, échec
        if not defenders:
            return {
                "success": False,
                "message": f"Personne ne défend {getattr(target, 'name', str(target))}"
            }
            
        # Calculer la réduction de dégâts
        damage_reduction = 0.3 * len(defenders) * defense_bonus  # 30% par défenseur
        damage_reduction = min(0.9, damage_reduction)  # Maximum 90%
        
        # Mettre à jour la menace
        for defender in defenders:
            self.update_threat_table(group_id, attacker, 20)  # Générer de la menace en défendant
        
        return {
            "success": True,
            "message": f"{len(defenders)} membres défendent {getattr(target, 'name', str(target))}",
            "damage_reduction": damage_reduction,
            "defenders": defenders
        }
    
    def coordinate_support(self, group_id: str, target: Any = None) -> Dict[str, Any]:
        """
        Coordonne une action de soutien de groupe
        
        Args:
            group_id: Identifiant du groupe
            target: Le membre à soutenir (None pour auto-sélection)
            
        Returns:
            Résultat de l'action de soutien
        """
        if group_id not in self.groups:
            return {"success": False, "message": f"Le groupe {group_id} n'existe pas"}
            
        group = self.groups[group_id]
        members = group["members"]
        roles = group["roles"]
        
        # Trouver les membres de soutien
        supporters = [m for m in members if roles.get(m) == RoleType.SUPPORT]
        
        # Si pas de supporters, échec
        if not supporters:
            return {
                "success": False,
                "message": f"Pas de membres de soutien dans le groupe {group_id}"
            }
            
        # Si pas de cible spécifiée, sélectionner le membre avec le moins de PV
        if target is None:
            target = min(members, key=lambda m: getattr(m, "health", 0) / getattr(m, "max_health", 1))
            
        # Vérifier si la cible est un membre du groupe
        if target not in members:
            return {"success": False, "message": f"{getattr(target, 'name', str(target))} n'est pas membre du groupe {group_id}"}
            
        # Calculer les soins totaux
        total_healing = 0
        support_effects = []
        
        for supporter in supporters:
            # Vérifier si le supporter peut soigner
            if hasattr(supporter, "heal_target"):
                # Calculer les soins
                healing = supporter.heal_target(target)
                total_healing += healing
                
                support_effects.append({
                    "supporter": supporter,
                    "effect_type": "healing",
                    "value": healing
                })
            
            # Vérifier les autres effets de soutien
            if hasattr(supporter, "apply_buff"):
                buff_result = supporter.apply_buff(target)
                
                if buff_result.get("success", False):
                    support_effects.append({
                        "supporter": supporter,
                        "effect_type": "buff",
                        "buff_type": buff_result.get("buff_type", "unknown"),
                        "duration": buff_result.get("duration", 1)
                    })
        
        # Appliquer les synergies
        for supporter in supporters:
            synergy_effects = self.get_synergy_effects(supporter, target)
            for effect in synergy_effects:
                effect_data = effect["effect"]
                
                # Appliquer les bonus de durée
                if "support_effect_duration" in effect_data:
                    for support_effect in support_effects:
                        if support_effect["supporter"] == supporter and "duration" in support_effect:
                            support_effect["duration"] += effect_data["support_effect_duration"]
                            
                            support_effects.append({
                                "supporter": supporter,
                                "effect_type": "synergy",
                                "name": effect["name"],
                                "description": effect["description"]
                            })
        
        return {
            "success": True,
            "message": f"Action de soutien coordonnée pour {getattr(target, 'name', str(target))}",
            "total_healing": total_healing,
            "support_effects": support_effects,
            "target_health": getattr(target, "health", 0)
        }
    
    def reset_combat_group(self) -> None:
        """Réinitialise les données de groupe de combat"""
        self.ally_bonuses = {}
        self.threat_tables = {}
