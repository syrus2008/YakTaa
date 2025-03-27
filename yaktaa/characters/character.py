"""
Module pour la gestion des personnages dans YakTaa
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("YakTaa.Characters.Character")

@dataclass
class Skill:
    """Classe représentant une compétence de personnage"""
    id: str
    name: str
    description: str
    level: int = 0
    max_level: int = 100
    experience: int = 0
    category: str = "general"  # hacking, social, combat, etc.
    
    def add_experience(self, amount: int) -> bool:
        """Ajoute de l'expérience à la compétence et augmente le niveau si nécessaire"""
        if self.level >= self.max_level:
            return False
        
        self.experience += amount
        
        # Calcul du niveau basé sur l'expérience
        # Formule simple : niveau = racine carrée de l'expérience / 10
        import math
        new_level = min(self.max_level, int(math.sqrt(self.experience) / 10))
        
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            logger.info(f"Compétence {self.name} améliorée : {old_level} -> {self.level}")
            return True
        
        return False


@dataclass
class Attribute:
    """Classe représentant un attribut de personnage"""
    id: str
    name: str
    description: str
    value: int = 10
    min_value: int = 1
    max_value: int = 20
    
    def increase(self, amount: int = 1) -> bool:
        """Augmente la valeur de l'attribut"""
        if self.value >= self.max_value:
            return False
        
        old_value = self.value
        self.value = min(self.max_value, self.value + amount)
        logger.info(f"Attribut {self.name} augmenté : {old_value} -> {self.value}")
        return True
    
    def decrease(self, amount: int = 1) -> bool:
        """Diminue la valeur de l'attribut"""
        if self.value <= self.min_value:
            return False
        
        old_value = self.value
        self.value = max(self.min_value, self.value - amount)
        logger.info(f"Attribut {self.name} diminué : {old_value} -> {self.value}")
        return True


class Character:
    """Classe représentant un personnage dans le jeu"""
    
    def __init__(self, name: str, character_type: str = "player"):
        """Initialise un personnage"""
        self.id = str(uuid.uuid4())  # Identifiant unique pour le personnage
        self.name = name
        self.character_type = character_type  # player, npc
        self.level = 1
        self.experience = 0
        self.credits = 1000
        self.reputation = {}  # Réputation auprès des différentes factions
        
        # Attributs de base
        self.attributes: Dict[str, Attribute] = {}
        self._init_attributes()
        
        # Compétences
        self.skills: Dict[str, Skill] = {}
        self._init_skills()
        
        # Inventaire
        self.inventory: List[Any] = []
        
        # Historique des missions
        self.mission_history: List[Any] = []
        
        # Date de création
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        
        # Localisation
        self.location_id = None
        
        # Description
        self.description = ""
    
    def _init_attributes(self):
        """Initialise les attributs de base du personnage"""
        base_attributes = [
            Attribute(
                id="intelligence",
                name="Intelligence",
                description="Capacité à résoudre des problèmes complexes et à comprendre des systèmes.",
                value=10
            ),
            Attribute(
                id="reflexes",
                name="Réflexes",
                description="Rapidité de réaction et coordination.",
                value=10
            ),
            Attribute(
                id="technique",
                name="Technique",
                description="Maîtrise des outils et technologies.",
                value=10
            ),
            Attribute(
                id="charisme",
                name="Charisme",
                description="Capacité à influencer et à communiquer avec les autres.",
                value=10
            ),
            Attribute(
                id="constitution",
                name="Constitution",
                description="Résistance physique et mentale.",
                value=10
            )
        ]
        
        for attr in base_attributes:
            self.attributes[attr.id] = attr
    
    def _init_skills(self):
        """Initialise les compétences de base du personnage"""
        base_skills = [
            # Compétences de hacking
            Skill(
                id="programming",
                name="Programmation",
                description="Capacité à écrire et comprendre du code.",
                level=1,
                category="hacking"
            ),
            Skill(
                id="network_security",
                name="Sécurité réseau",
                description="Connaissance des protocoles et failles de sécurité.",
                level=1,
                category="hacking"
            ),
            Skill(
                id="cryptography",
                name="Cryptographie",
                description="Capacité à chiffrer et déchiffrer des données.",
                level=1,
                category="hacking"
            ),
            
            # Compétences sociales
            Skill(
                id="negotiation",
                name="Négociation",
                description="Capacité à obtenir des conditions favorables lors d'échanges.",
                level=1,
                category="social"
            ),
            Skill(
                id="persuasion",
                name="Persuasion",
                description="Capacité à convaincre les autres.",
                level=1,
                category="social"
            ),
            
            # Compétences techniques
            Skill(
                id="electronics",
                name="Électronique",
                description="Connaissance des circuits et appareils électroniques.",
                level=1,
                category="technical"
            ),
            Skill(
                id="hardware",
                name="Matériel informatique",
                description="Capacité à manipuler et réparer du matériel informatique.",
                level=1,
                category="technical"
            )
        ]
        
        for skill in base_skills:
            self.skills[skill.id] = skill
    
    def add_attribute(self, attribute_id: str, value: int) -> bool:
        """
        Définit la valeur d'un attribut existant
        
        Args:
            attribute_id: Identifiant de l'attribut
            value: Nouvelle valeur de l'attribut
            
        Returns:
            bool: True si l'attribut a été modifié, False sinon
        """
        if attribute_id in self.attributes:
            attr = self.attributes[attribute_id]
            old_value = attr.value
            attr.value = max(attr.min_value, min(attr.max_value, value))
            logger.info(f"Attribut {attr.name} modifié pour {self.name}: {old_value} -> {attr.value}")
            return True
        else:
            logger.warning(f"Tentative de modifier un attribut inexistant: {attribute_id}")
            return False
    
    def improve_skill(self, skill_id: str, experience: int) -> bool:
        """
        Améliore une compétence en ajoutant de l'expérience
        
        Args:
            skill_id: Identifiant de la compétence
            experience: Quantité d'expérience à ajouter
            
        Returns:
            bool: True si la compétence a été améliorée, False sinon
        """
        # Vérifier si la compétence existe, sinon la créer
        if skill_id not in self.skills:
            # Créer une compétence générique
            skill_name = skill_id.replace("_", " ").title()
            self.skills[skill_id] = Skill(
                id=skill_id,
                name=skill_name,
                description=f"Compétence en {skill_name}",
                level=0
            )
            logger.info(f"Nouvelle compétence créée pour {self.name}: {skill_name}")
        
        # Ajouter l'expérience
        return self.skills[skill_id].add_experience(experience)
    
    def add_experience(self, amount: int) -> bool:
        """Ajoute de l'expérience au personnage et augmente le niveau si nécessaire"""
        self.experience += amount
        
        # Calcul du niveau basé sur l'expérience
        # Formule simple : niveau = racine cubique de l'expérience / 5
        import math
        new_level = max(1, int(math.pow(self.experience, 1/3) / 5))
        
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            logger.info(f"Personnage {self.name} a gagné un niveau : {old_level} -> {self.level}")
            return True
        
        return False
    
    def get_attribute(self, attribute_id: str) -> Optional[Attribute]:
        """Récupère un attribut par son ID"""
        return self.attributes.get(attribute_id)
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Récupère une compétence par son ID"""
        return self.skills.get(skill_id)
    
    def add_skill(self, skill: Skill) -> None:
        """Ajoute une nouvelle compétence au personnage"""
        self.skills[skill.id] = skill
        logger.info(f"Nouvelle compétence acquise : {skill.name}")
    
    def add_credits(self, amount: int) -> None:
        """Ajoute des crédits au personnage"""
        if amount < 0:
            logger.warning(f"Tentative d'ajouter un montant négatif de crédits : {amount}")
            return
        
        self.credits += amount
        logger.info(f"{amount} crédits ajoutés. Nouveau solde : {self.credits}")
    
    def remove_credits(self, amount: int) -> bool:
        """Retire des crédits au personnage"""
        if amount < 0:
            logger.warning(f"Tentative de retirer un montant négatif de crédits : {amount}")
            return False
        
        if self.credits < amount:
            logger.warning(f"Fonds insuffisants. Solde actuel : {self.credits}, montant demandé : {amount}")
            return False
        
        self.credits -= amount
        logger.info(f"{amount} crédits retirés. Nouveau solde : {self.credits}")
        return True
    
    def update_reputation(self, faction: str, change: int) -> None:
        """Met à jour la réputation du personnage auprès d'une faction"""
        current = self.reputation.get(faction, 0)
        new_rep = max(-100, min(100, current + change))
        self.reputation[faction] = new_rep
        
        if change > 0:
            logger.info(f"Réputation augmentée auprès de {faction} : {current} -> {new_rep}")
        else:
            logger.info(f"Réputation diminuée auprès de {faction} : {current} -> {new_rep}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le personnage en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.character_type,
            "level": self.level,
            "experience": self.experience,
            "credits": self.credits,
            "reputation": self.reputation,
            "attributes": {attr_id: attr.__dict__ for attr_id, attr in self.attributes.items()},
            "skills": {skill_id: skill.__dict__ for skill_id, skill in self.skills.items()},
            "created_at": self.created_at.isoformat(),
            "last_active": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Crée un personnage à partir d'un dictionnaire"""
        character = cls(data["name"], data["type"])
        character.id = data["id"]
        character.level = data["level"]
        character.experience = data["experience"]
        character.credits = data["credits"]
        character.reputation = data["reputation"]
        
        # Charger les attributs
        character.attributes = {}
        for attr_id, attr_data in data["attributes"].items():
            character.attributes[attr_id] = Attribute(**attr_data)
        
        # Charger les compétences
        character.skills = {}
        for skill_id, skill_data in data["skills"].items():
            character.skills[skill_id] = Skill(**skill_data)
        
        # Charger les dates
        from datetime import datetime
        character.created_at = datetime.fromisoformat(data["created_at"])
        character.last_active = datetime.now()
        
        return character


# Fonction pour créer un personnage de test
def create_test_character() -> Character:
    """Crée un personnage de test pour le développement"""
    character = Character("Hacker X")
    
    # Améliorer quelques compétences
    character.improve_skill("programming", 500)
    character.improve_skill("network_security", 300)
    character.improve_skill("cryptography", 200)
    
    # Ajouter de l'expérience
    character.add_experience(1000)
    
    # Ajouter des crédits
    character.add_credits(5000)
    
    # Ajouter de la réputation
    character.update_reputation("NetRunners", 50)
    character.update_reputation("Corporations", -30)
    
    return character
