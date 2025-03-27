"""
Module pour la gestion de l'inventaire du joueur dans YakTaa
Ce module permet de gérer les objets et le matériel du joueur.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import uuid
import json
import os

from yaktaa.items.hardware import Hardware, HardwareType, generate_hardware_catalog
from yaktaa.characters.player import Player

logger = logging.getLogger("YakTaa.Items.InventoryManager")

class InventoryItem:
    """Classe représentant un objet dans l'inventaire"""
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Objet inconnu", 
                 description: str = "Un objet mystérieux", 
                 type: str = "misc", 
                 quantity: int = 1,
                 value: int = 0,
                 icon: str = "default_item",
                 properties: Dict[str, Any] = None):
        """Initialise un objet d'inventaire"""
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.type = type
        self.quantity = quantity
        self.value = value
        self.icon = icon
        self.properties = properties or {}
    
    def use(self) -> Dict[str, Any]:
        """Utilise l'objet et retourne le résultat"""
        # Cette méthode serait implémentée par les sous-classes
        return {
            "success": False,
            "message": "Cet objet ne peut pas être utilisé directement."
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour la sauvegarde"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "quantity": self.quantity,
            "value": self.value,
            "icon": self.icon,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Crée un objet à partir d'un dictionnaire"""
        return cls(
            id=data.get("id"),
            name=data.get("name", "Objet inconnu"),
            description=data.get("description", "Un objet mystérieux"),
            type=data.get("type", "misc"),
            quantity=data.get("quantity", 1),
            value=data.get("value", 0),
            icon=data.get("icon", "default_item"),
            properties=data.get("properties", {})
        )

class Consumable(InventoryItem):
    """Classe représentant un objet consommable"""
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Consommable", 
                 description: str = "Un objet consommable", 
                 quantity: int = 1,
                 value: int = 10,
                 icon: str = "consumable",
                 effect_type: str = "none",
                 effect_value: int = 0,
                 duration: int = 0,
                 properties: Dict[str, Any] = None):
        """Initialise un consommable"""
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="consumable",
            quantity=quantity,
            value=value,
            icon=icon,
            properties=properties or {}
        )
        
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.duration = duration
        
        # Ajout des propriétés spécifiques
        self.properties.update({
            "effect_type": effect_type,
            "effect_value": effect_value,
            "duration": duration
        })
    
    def use(self) -> Dict[str, Any]:
        """Utilise le consommable"""
        if self.quantity <= 0:
            return {
                "success": False,
                "message": f"Vous n'avez plus de {self.name}."
            }
        
        self.quantity -= 1
        
        return {
            "success": True,
            "message": f"Vous avez utilisé {self.name}.",
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "duration": self.duration
        }

class Tool(InventoryItem):
    """Classe représentant un outil"""
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Outil", 
                 description: str = "Un outil utile", 
                 quantity: int = 1,
                 value: int = 50,
                 icon: str = "tool",
                 tool_type: str = "generic",
                 durability: int = 100,
                 properties: Dict[str, Any] = None):
        """Initialise un outil"""
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="tool",
            quantity=quantity,
            value=value,
            icon=icon,
            properties=properties or {}
        )
        
        self.tool_type = tool_type
        self.durability = durability
        
        # Ajout des propriétés spécifiques
        self.properties.update({
            "tool_type": tool_type,
            "durability": durability
        })
    
    def use(self) -> Dict[str, Any]:
        """Utilise l'outil"""
        if self.durability <= 0:
            return {
                "success": False,
                "message": f"{self.name} est cassé et ne peut plus être utilisé."
            }
        
        self.durability -= 1
        
        return {
            "success": True,
            "message": f"Vous avez utilisé {self.name}.",
            "tool_type": self.tool_type,
            "durability": self.durability
        }

class DataItem(InventoryItem):
    """Classe représentant un élément de données (fichier, programme, etc.)"""
    
    def __init__(self, 
                 id: str = None, 
                 name: str = "Données", 
                 description: str = "Un fichier de données", 
                 quantity: int = 1,
                 value: int = 20,
                 icon: str = "data",
                 data_type: str = "file",
                 size: int = 1,  # en MB
                 encrypted: bool = False,
                 content: str = "",
                 properties: Dict[str, Any] = None):
        """Initialise un élément de données"""
        super().__init__(
            id=id,
            name=name,
            description=description,
            type="data",
            quantity=quantity,
            value=value,
            icon=icon,
            properties=properties or {}
        )
        
        self.data_type = data_type
        self.size = size
        self.encrypted = encrypted
        self.content = content
        
        # Ajout des propriétés spécifiques
        self.properties.update({
            "data_type": data_type,
            "size": size,
            "encrypted": encrypted
        })
    
    def use(self) -> Dict[str, Any]:
        """Utilise l'élément de données"""
        if self.encrypted:
            return {
                "success": False,
                "message": f"{self.name} est chiffré et ne peut pas être lu directement."
            }
        
        return {
            "success": True,
            "message": f"Vous avez ouvert {self.name}.",
            "content": self.content
        }

class InventoryManager:
    """Gestionnaire d'inventaire pour le joueur"""
    
    def __init__(self, player: Player):
        """Initialise le gestionnaire d'inventaire"""
        self.player = player
        self.items: Dict[str, InventoryItem] = {}  # id -> item
        self.hardware: Dict[str, Hardware] = {}  # id -> hardware
        
        # Catalogue de matériel disponible
        self.hardware_catalog = generate_hardware_catalog()
        
        logger.info(f"Gestionnaire d'inventaire initialisé pour {player.name}")
    
    def add_item(self, item: InventoryItem) -> bool:
        """
        Ajoute un objet à l'inventaire
        
        Args:
            item: Objet à ajouter
            
        Returns:
            True si l'objet a été ajouté, False sinon
        """
        # Vérifier si l'objet existe déjà
        if item.id in self.items:
            existing_item = self.items[item.id]
            existing_item.quantity += item.quantity
            logger.debug(f"Quantité de {item.name} augmentée à {existing_item.quantity}")
            return True
        
        # Ajouter le nouvel objet
        self.items[item.id] = item
        logger.debug(f"Objet ajouté à l'inventaire: {item.name} (x{item.quantity})")
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Retire un objet de l'inventaire
        
        Args:
            item_id: ID de l'objet à retirer
            quantity: Quantité à retirer
            
        Returns:
            True si l'objet a été retiré, False sinon
        """
        if item_id not in self.items:
            logger.warning(f"Tentative de retirer un objet inexistant: {item_id}")
            return False
        
        item = self.items[item_id]
        
        if item.quantity <= quantity:
            # Retirer complètement l'objet
            del self.items[item_id]
            logger.debug(f"Objet retiré de l'inventaire: {item.name}")
        else:
            # Réduire la quantité
            item.quantity -= quantity
            logger.debug(f"Quantité de {item.name} réduite à {item.quantity}")
        
        return True
    
    def use_item(self, item_id: str) -> Dict[str, Any]:
        """
        Utilise un objet de l'inventaire
        
        Args:
            item_id: ID de l'objet à utiliser
            
        Returns:
            Résultat de l'utilisation
        """
        if item_id not in self.items:
            logger.warning(f"Tentative d'utiliser un objet inexistant: {item_id}")
            return {
                "success": False,
                "message": "Cet objet n'existe pas dans votre inventaire."
            }
        
        item = self.items[item_id]
        
        # Déterminer l'action en fonction du type d'objet
        item_type = item.type.lower() if hasattr(item, 'type') else "unknown"
        
        # Traitement spécifique selon le type d'objet
        if item_type == "hardware_component":
            # Composant PC à installer dans le hardware du joueur
            return self._install_hardware_component(item)
        elif item_type == "weapon":
            # Arme à équiper
            return self._equip_weapon(item)
        elif item_type == "armor":
            # Armure à équiper
            return self._equip_armor(item)
        elif item_type == "implant":
            # Implant cybernétique à installer
            return self._install_implant(item)
        elif item_type == "software":
            # Logiciel à installer
            return self._install_software(item)
        elif item_type == "consumable":
            # Consommable à utiliser immédiatement
            result = item.use()
            
            # Si l'objet a été consommé et qu'il n'en reste plus
            if result.get("success", False) and item.quantity <= 0:
                del self.items[item_id]
                logger.debug(f"Objet épuisé et retiré de l'inventaire: {item.name}")
            
            return result
        else:
            # Comportement par défaut pour les autres types d'objets
            result = item.use()
            
            # Si l'objet a été consommé et qu'il n'en reste plus
            if result.get("success", False) and item.quantity <= 0:
                del self.items[item_id]
                logger.debug(f"Objet épuisé et retiré de l'inventaire: {item.name}")
            
            return result
    
    def _install_hardware_component(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Installe un composant hardware dans l'équipement du joueur
        
        Args:
            item: Composant à installer
            
        Returns:
            Résultat de l'installation
        """
        # Vérifier si le joueur a un attribut computer ou hardware
        if not hasattr(self.player, 'computer') and not hasattr(self.player, 'hardware'):
            return {
                "success": False,
                "message": "Vous n'avez pas d'ordinateur pour installer ce composant."
            }
        
        # Déterminer le type de composant
        component_type = item.properties.get('component_type', 'unknown')
        
        # Créer un objet Hardware à partir de l'item
        try:
            # Convertir l'item en Hardware
            from yaktaa.items.hardware import Hardware, HardwareType
            
            # Déterminer le type de hardware
            hw_type = HardwareType.CPU
            if component_type == "cpu":
                hw_type = HardwareType.CPU
            elif component_type == "gpu":
                hw_type = HardwareType.GPU
            elif component_type == "ram":
                hw_type = HardwareType.RAM
            elif component_type == "storage":
                hw_type = HardwareType.STORAGE
            elif component_type == "network":
                hw_type = HardwareType.NETWORK
            elif component_type == "cooling":
                hw_type = HardwareType.COOLING
            
            # Créer le composant hardware
            hardware = Hardware(
                id=item.id,
                name=item.name,
                description=item.description,
                type=hw_type,
                performance=item.properties.get('performance', 1),
                power_consumption=item.properties.get('power_consumption', 1),
                heat_generation=item.properties.get('heat_generation', 1),
                price=item.value
            )
            
            # Ajouter le hardware à l'inventaire
            self.add_hardware(hardware)
            
            # Retirer l'item de l'inventaire
            self.remove_item(item.id)
            
            return {
                "success": True,
                "message": f"{item.name} a été converti en composant hardware et ajouté à votre inventaire de matériel.",
                "hardware_id": hardware.id
            }
        except Exception as e:
            logger.error(f"Erreur lors de la conversion en hardware: {str(e)}")
            return {
                "success": False,
                "message": f"Impossible d'installer ce composant: {str(e)}"
            }
    
    def _equip_weapon(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Équipe une arme
        
        Args:
            item: Arme à équiper
            
        Returns:
            Résultat de l'équipement
        """
        # Vérifier si le joueur a un attribut equipment
        if not hasattr(self.player, 'equipment'):
            return {
                "success": False,
                "message": "Vous ne pouvez pas équiper d'armes."
            }
        
        # Déterminer l'emplacement d'équipement
        slot = "weapon"
        
        # Équiper l'arme
        try:
            # Si un objet est déjà équipé dans cet emplacement, le déséquiper
            if hasattr(self.player.equipment, slot) and getattr(self.player.equipment, slot):
                current_weapon_id = getattr(self.player.equipment, slot)
                # Réinitialiser l'emplacement
                setattr(self.player.equipment, slot, None)
                logger.debug(f"Arme déséquipée: {current_weapon_id}")
            
            # Équiper la nouvelle arme
            setattr(self.player.equipment, slot, item.id)
            logger.debug(f"Arme équipée: {item.name}")
            
            return {
                "success": True,
                "message": f"Vous avez équipé {item.name}.",
                "slot": slot
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'équipement de l'arme: {str(e)}")
            return {
                "success": False,
                "message": f"Impossible d'équiper cette arme: {str(e)}"
            }
    
    def _equip_armor(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Équipe une armure
        
        Args:
            item: Armure à équiper
            
        Returns:
            Résultat de l'équipement
        """
        # Vérifier si le joueur a un attribut equipment
        if not hasattr(self.player, 'equipment'):
            return {
                "success": False,
                "message": "Vous ne pouvez pas équiper d'armure."
            }
        
        # Déterminer l'emplacement d'équipement
        armor_type = item.properties.get('armor_type', 'body')
        slot = armor_type  # head, body, legs, etc.
        
        # Équiper l'armure
        try:
            # Si un objet est déjà équipé dans cet emplacement, le déséquiper
            if hasattr(self.player.equipment, slot) and getattr(self.player.equipment, slot):
                current_armor_id = getattr(self.player.equipment, slot)
                # Réinitialiser l'emplacement
                setattr(self.player.equipment, slot, None)
                logger.debug(f"Armure déséquipée: {current_armor_id}")
            
            # Équiper la nouvelle armure
            setattr(self.player.equipment, slot, item.id)
            logger.debug(f"Armure équipée: {item.name}")
            
            return {
                "success": True,
                "message": f"Vous avez équipé {item.name}.",
                "slot": slot
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'équipement de l'armure: {str(e)}")
            return {
                "success": False,
                "message": f"Impossible d'équiper cette armure: {str(e)}"
            }
    
    def _install_implant(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Installe un implant cybernétique
        
        Args:
            item: Implant à installer
            
        Returns:
            Résultat de l'installation
        """
        # Vérifier si le joueur a un attribut implants
        if not hasattr(self.player, 'implants'):
            return {
                "success": False,
                "message": "Vous ne pouvez pas installer d'implants cybernétiques."
            }
        
        # Déterminer l'emplacement d'implant
        implant_location = item.properties.get('body_location', 'unknown')
        
        # Installer l'implant
        try:
            # Si un implant est déjà installé à cet emplacement, le retirer
            if implant_location in self.player.implants:
                current_implant_id = self.player.implants[implant_location]
                # Retirer l'implant actuel
                del self.player.implants[implant_location]
                logger.debug(f"Implant retiré: {current_implant_id}")
            
            # Installer le nouvel implant
            self.player.implants[implant_location] = item.id
            logger.debug(f"Implant installé: {item.name}")
            
            return {
                "success": True,
                "message": f"Vous avez installé l'implant {item.name}.",
                "location": implant_location
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'installation de l'implant: {str(e)}")
            return {
                "success": False,
                "message": f"Impossible d'installer cet implant: {str(e)}"
            }
    
    def _install_software(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Installe un logiciel
        
        Args:
            item: Logiciel à installer
            
        Returns:
            Résultat de l'installation
        """
        # Vérifier si le joueur a un attribut software
        if not hasattr(self.player, 'software'):
            return {
                "success": False,
                "message": "Vous n'avez pas de système pour installer ce logiciel."
            }
        
        # Déterminer le type de logiciel
        software_type = item.properties.get('software_type', 'unknown')
        
        # Installer le logiciel
        try:
            # Ajouter le logiciel à la collection du joueur
            if software_type not in self.player.software:
                self.player.software[software_type] = []
            
            # Vérifier si le logiciel est déjà installé
            if item.id in self.player.software[software_type]:
                return {
                    "success": False,
                    "message": f"{item.name} est déjà installé."
                }
            
            # Installer le logiciel
            self.player.software[software_type].append(item.id)
            logger.debug(f"Logiciel installé: {item.name}")
            
            return {
                "success": True,
                "message": f"Vous avez installé {item.name}.",
                "software_type": software_type
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'installation du logiciel: {str(e)}")
            return {
                "success": False,
                "message": f"Impossible d'installer ce logiciel: {str(e)}"
            }
    
    def add_hardware(self, hardware: Hardware) -> bool:
        """
        Ajoute un composant matériel à l'inventaire
        
        Args:
            hardware: Composant à ajouter
            
        Returns:
            True si le composant a été ajouté, False sinon
        """
        self.hardware[hardware.id] = hardware
        logger.debug(f"Composant matériel ajouté à l'inventaire: {hardware.name}")
        return True
    
    def remove_hardware(self, hardware_id: str) -> bool:
        """
        Retire un composant matériel de l'inventaire
        
        Args:
            hardware_id: ID du composant à retirer
            
        Returns:
            True si le composant a été retiré, False sinon
        """
        if hardware_id not in self.hardware:
            logger.warning(f"Tentative de retirer un composant inexistant: {hardware_id}")
            return False
        
        # Vérifier si le composant est équipé
        for slot, equipped in self.player.active_equipment.items():
            if equipped and equipped.id == hardware_id:
                logger.warning(f"Tentative de retirer un composant équipé: {hardware_id}")
                return False
        
        hardware = self.hardware[hardware_id]
        del self.hardware[hardware_id]
        logger.debug(f"Composant matériel retiré de l'inventaire: {hardware.name}")
        return True
    
    def equip_hardware(self, hardware_id: str) -> Dict[str, Any]:
        """
        Équipe un composant matériel
        
        Args:
            hardware_id: ID du composant à équiper
            
        Returns:
            Résultat de l'équipement
        """
        if hardware_id not in self.hardware:
            logger.warning(f"Tentative d'équiper un composant inexistant: {hardware_id}")
            return {
                "success": False,
                "message": "Ce composant n'existe pas dans votre inventaire."
            }
        
        hardware = self.hardware[hardware_id]
        slot = hardware.type.value
        
        # Déséquiper le composant actuel
        current = self.player.active_equipment.get(slot)
        if current:
            self.player.active_equipment[slot] = None
            logger.debug(f"Composant déséquipé: {current.name}")
        
        # Équiper le nouveau composant
        self.player.active_equipment[slot] = hardware
        logger.debug(f"Composant équipé: {hardware.name}")
        
        return {
            "success": True,
            "message": f"Vous avez équipé {hardware.name}.",
            "slot": slot,
            "hardware": hardware.name
        }
    
    def unequip_hardware(self, slot: str) -> Dict[str, Any]:
        """
        Déséquipe un composant matériel
        
        Args:
            slot: Emplacement à déséquiper
            
        Returns:
            Résultat du déséquipement
        """
        if slot not in self.player.active_equipment:
            logger.warning(f"Tentative de déséquiper un emplacement inexistant: {slot}")
            return {
                "success": False,
                "message": f"L'emplacement {slot} n'existe pas."
            }
        
        current = self.player.active_equipment.get(slot)
        if not current:
            return {
                "success": False,
                "message": f"Aucun composant n'est équipé dans l'emplacement {slot}."
            }
        
        # Déséquiper le composant
        hardware_name = current.name
        self.player.active_equipment[slot] = None
        logger.debug(f"Composant déséquipé: {hardware_name}")
        
        return {
            "success": True,
            "message": f"Vous avez déséquipé {hardware_name}.",
            "slot": slot
        }
    
    def get_hardware_stats(self) -> Dict[str, int]:
        """
        Calcule les statistiques totales du matériel équipé
        
        Returns:
            Dictionnaire des statistiques
        """
        stats = {
            # CPU
            "processing_power": 0,
            "hack_speed_bonus": 0,
            
            # Mémoire
            "multitasking": 0,
            "buffer_size": 0,
            
            # Stockage
            "capacity": 0,
            "download_speed": 0,
            "upload_speed": 0,
            
            # Réseau
            "bandwidth": 0,
            "range": 0,
            "connection_strength": 0,
            "signal_boost": 0,
            
            # Sécurité
            "encryption": 0,
            "firewall": 0,
            "stealth": 0,
            "detection_resistance": 0
        }
        
        # Additionner les statistiques de chaque composant équipé
        for slot, hardware in self.player.active_equipment.items():
            if hardware:
                for stat, value in hardware.stats.items():
                    if stat in stats:
                        stats[stat] += value
        
        return stats
    
    def get_hardware_abilities(self) -> List[str]:
        """
        Récupère toutes les capacités du matériel équipé
        
        Returns:
            Liste des capacités
        """
        abilities = set()
        
        for slot, hardware in self.player.active_equipment.items():
            if hardware and hasattr(hardware, "abilities"):
                abilities.update(hardware.abilities)
        
        return list(abilities)
    
    def get_items(self):
        """
        Récupère tous les objets de l'inventaire
        
        Returns:
            Dictionnaire des objets (id -> objet)
        """
        return self.items
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """
        Récupère un objet spécifique de l'inventaire par son ID
        
        Args:
            item_id: ID de l'objet à récupérer
            
        Returns:
            L'objet s'il existe, None sinon
        """
        return self.items.get(item_id)
    
    def get_hardware(self):
        """
        Récupère tout le matériel de l'inventaire
        """
        return self.hardware
    
    def get_items_by_type(self, item_type: str) -> List[InventoryItem]:
        """
        Récupère tous les objets d'un type spécifique
        
        Args:
            item_type: Type d'objet à récupérer
            
        Returns:
            Liste des objets du type spécifié
        """
        return [item for item in self.items.values() if item.type == item_type]
    
    def get_hardware_by_type(self, hardware_type: str) -> List[Hardware]:
        """
        Récupère tous les composants d'un type spécifique
        
        Args:
            hardware_type: Type de composant à récupérer
            
        Returns:
            Liste des composants du type spécifié
        """
        return [hw for hw in self.hardware.values() if hw.type.value == hardware_type]
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Sauvegarde l'inventaire dans un fichier
        
        Args:
            filepath: Chemin du fichier de sauvegarde
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Préparer les données
            data = {
                "items": [item.to_dict() for item in self.items.values()],
                "hardware": [hw.to_dict() for hw in self.hardware.values()],
                "equipped": {
                    slot: (hw.id if hw else None) 
                    for slot, hw in self.player.active_equipment.items()
                }
            }
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder les données
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Inventaire sauvegardé dans {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'inventaire: {str(e)}", exc_info=True)
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Charge l'inventaire depuis un fichier
        
        Args:
            filepath: Chemin du fichier de sauvegarde
            
        Returns:
            True si le chargement a réussi, False sinon
        """
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(filepath):
                logger.warning(f"Fichier d'inventaire inexistant: {filepath}")
                return False
            
            # Charger les données
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Réinitialiser l'inventaire
            self.items = {}
            self.hardware = {}
            
            # Charger les objets
            for item_data in data.get("items", []):
                item = InventoryItem.from_dict(item_data)
                self.items[item.id] = item
            
            # Charger le matériel
            for hw_data in data.get("hardware", []):
                hardware = Hardware.from_dict(hw_data)
                self.hardware[hardware.id] = hardware
            
            # Équiper le matériel
            for slot, hw_id in data.get("equipped", {}).items():
                if hw_id and hw_id in self.hardware:
                    self.player.active_equipment[slot] = self.hardware[hw_id]
                else:
                    self.player.active_equipment[slot] = None
            
            logger.info(f"Inventaire chargé depuis {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'inventaire: {str(e)}", exc_info=True)
            return False
    
    def generate_starter_inventory(self) -> None:
        """Génère un inventaire de départ pour un nouveau joueur"""
        # Ajouter des objets de base
        self.add_item(Consumable(
            name="Stimulant de base",
            description="Un stimulant qui augmente temporairement vos capacités de hacking.",
            effect_type="hack_speed",
            effect_value=10,
            duration=60,
            quantity=3,
            value=50
        ))
        
        self.add_item(Tool(
            name="Kit de réparation",
            description="Un kit basique pour réparer votre matériel endommagé.",
            tool_type="repair",
            durability=5,
            value=100
        ))
        
        self.add_item(DataItem(
            name="Guide du débutant",
            description="Un guide pour les nouveaux hackers.",
            data_type="document",
            size=2,
            content="Bienvenue dans le monde du hacking! Ce guide vous aidera à comprendre les bases."
        ))
        
        # Ajouter du matériel de base
        for hw_type, hw_list in self.hardware_catalog.items():
            if hw_list:
                # Ajouter le premier composant de chaque type
                self.add_hardware(hw_list[0])
                
                # Équiper automatiquement
                self.equip_hardware(hw_list[0].id)
        
        logger.info("Inventaire de départ généré")
    
    def equip_item(self, item_id: str, slot: str = None) -> bool:
        """
        Équipe un objet (arme, armure, etc.)
        
        Args:
            item_id: ID de l'objet à équiper
            slot: Emplacement spécifique où équiper l'objet (optionnel)
            
        Returns:
            True si l'objet a été équipé avec succès, False sinon
        """
        item = self.get_item(item_id)
        if not item:
            logger.warning(f"Tentative d'équiper un objet inexistant : {item_id}")
            return False
            
        # Déterminer le type d'objet
        item_type = item.type.lower() if hasattr(item, 'type') else "unknown"
        
        # Équiper selon le type
        if item_type == "weapon":
            # Si slot n'est pas spécifié, utiliser "primary" par défaut
            weapon_slot = slot or "primary"
            if weapon_slot not in ["primary", "secondary"]:
                logger.warning(f"Slot d'arme invalide : {weapon_slot}")
                return False
                
            # Vérifier si une arme est déjà équipée dans ce slot
            current_weapon = self.player.active_equipment.get(weapon_slot)
            if current_weapon:
                logger.info(f"Remplacement de l'arme dans le slot {weapon_slot}")
                
            # Équiper l'arme
            success = self.player.equip_item(weapon_slot, item)
            if success:
                logger.info(f"Arme équipée avec succès : {item.name} dans {weapon_slot}")
            return success
            
        elif item_type == "armor":
            # Si slot n'est pas spécifié, essayer de déterminer le slot en fonction des propriétés
            armor_slot = slot
            if not armor_slot and hasattr(item, 'properties') and 'slot' in item.properties:
                armor_slot = item.properties['slot']
            
            # Si toujours pas de slot, utiliser "torso" par défaut
            armor_slot = armor_slot or "torso"
            
            if armor_slot not in ["head", "torso", "arms", "legs"]:
                logger.warning(f"Slot d'armure invalide : {armor_slot}")
                return False
                
            # Vérifier si une armure est déjà équipée dans ce slot
            current_armor = self.player.active_equipment.get(armor_slot)
            if current_armor:
                logger.info(f"Remplacement de l'armure dans le slot {armor_slot}")
                
            # Équiper l'armure
            success = self.player.equip_item(armor_slot, item)
            if success:
                logger.info(f"Armure équipée avec succès : {item.name} dans {armor_slot}")
            return success
            
        elif item_type == "implant":
            # Si slot n'est pas spécifié, essayer de déterminer le slot en fonction des propriétés
            implant_slot = slot
            if not implant_slot and hasattr(item, 'properties') and 'slot' in item.properties:
                implant_slot = item.properties['slot']
            
            # Si toujours pas de slot, impossible d'équiper
            if not implant_slot:
                logger.warning(f"Impossible de déterminer le slot pour l'implant : {item.name}")
                return False
                
            if implant_slot not in ["implant_cerebral", "implant_ocular", "implant_neural", "implant_dermal", "implant_skeletal", "implant_muscular"]:
                logger.warning(f"Slot d'implant invalide : {implant_slot}")
                return False
                
            # Vérifier si un implant est déjà installé dans ce slot
            current_implant = self.player.active_equipment.get(implant_slot)
            if current_implant:
                logger.info(f"Remplacement de l'implant dans le slot {implant_slot}")
                
            # Installer l'implant
            success = self.player.equip_item(implant_slot, item)
            if success:
                logger.info(f"Implant installé avec succès : {item.name} dans {implant_slot}")
            return success
            
        else:
            logger.warning(f"Type d'objet non équipable : {item_type}")
            return False

# Fonctions utilitaires
def create_test_inventory(player: Player) -> InventoryManager:
    """
    Crée un inventaire de test avec des objets variés
    
    Args:
        player: Joueur pour lequel créer l'inventaire
        
    Returns:
        Gestionnaire d'inventaire avec des objets de test
    """
    inventory = InventoryManager(player)
    
    # Générer l'inventaire de départ
    inventory.generate_starter_inventory()
    
    # Ajouter des objets supplémentaires pour les tests
    inventory.add_item(Consumable(
        name="Booster de mémoire",
        description="Augmente temporairement votre capacité de multitâche.",
        effect_type="multitasking",
        effect_value=20,
        duration=120,
        quantity=2,
        value=150
    ))
    
    inventory.add_item(Consumable(
        name="Nano-réparateur",
        description="Répare automatiquement votre matériel endommagé.",
        effect_type="repair",
        effect_value=50,
        duration=0,
        quantity=1,
        value=300
    ))
    
    inventory.add_item(Tool(
        name="Analyseur de réseau avancé",
        description="Un outil permettant d'analyser les réseaux en profondeur.",
        tool_type="network_analysis",
        durability=10,
        value=500
    ))
    
    inventory.add_item(DataItem(
        name="Schémas de sécurité NeoTokyo",
        description="Plans détaillés des systèmes de sécurité de NeoTokyo.",
        data_type="blueprint",
        size=15,
        encrypted=True,
        value=1000
    ))
    
    # Ajouter du matériel avancé
    for hw_type, hw_list in inventory.hardware_catalog.items():
        if len(hw_list) >= 2:
            # Ajouter le deuxième composant de chaque type
            inventory.add_hardware(hw_list[1])
    
    logger.info("Inventaire de test créé")
    return inventory
