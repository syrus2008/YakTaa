"""
Module pour standardiser les métadonnées dans les générateurs d'objets YakTaa.
Ce module fournit des fonctions pour garantir que tous les générateurs utilisent
le même format de métadonnées conforme aux schémas définis.
"""

import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

from metadata_schema import (
    METADATA_SCHEMAS, get_schema_for_item_type, MetadataSchema,
    WeaponMetadataSchema, ArmorMetadataSchema, ImplantMetadataSchema,
    ConsumableMetadataSchema, FoodMetadataSchema, HardwareMetadataSchema,
    SoftwareMetadataSchema
)

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MetadataStandardizer:
    """
    Classe pour standardiser les métadonnées dans les générateurs d'objets.
    """
    
    @staticmethod
    def standardize_weapon_metadata(
        weapon_type: str,
        damage: int = 10,
        damage_type: str = "PHYSICAL",
        accuracy: int = 70,
        range_val: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'une arme.
        
        Args:
            weapon_type: Type d'arme
            damage: Dégâts de base
            damage_type: Type de dégâts
            accuracy: Précision
            range_val: Portée
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = WeaponMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        metadata.update({
            "damage_type": damage_type.upper(),
            "damage": damage,
            "accuracy": accuracy,
            "range": range_val
        })
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in WeaponMetadataSchema.OPTIONAL_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_armor_metadata(
        armor_type: str,
        defense: int = 5,
        defense_type: str = "PHYSICAL",
        durability: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'une armure.
        
        Args:
            armor_type: Type d'armure
            defense: Défense de base
            defense_type: Type de défense
            durability: Durabilité
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = ArmorMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        metadata.update({
            "defense_type": defense_type.upper(),
            "defense": defense,
            "durability": durability
        })
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in ArmorMetadataSchema.OPTIONAL_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_implant_metadata(
        implant_type: str,
        stats_bonus: Dict[str, int] = None,
        humanity_cost: int = 5,
        surgery_difficulty: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'un implant.
        
        Args:
            implant_type: Type d'implant
            stats_bonus: Bonus de statistiques
            humanity_cost: Coût en humanité
            surgery_difficulty: Difficulté de chirurgie
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = ImplantMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        if stats_bonus:
            metadata["stats_bonus"].update(stats_bonus)
        
        metadata.update({
            "humanity_cost": humanity_cost,
            "surgery_difficulty": surgery_difficulty
        })
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in ImplantMetadataSchema.OPTIONAL_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_food_metadata(
        food_type: str,
        calories: int = 100,
        nutrition_value: int = 5,
        taste: str = "NEUTRAL",
        shelf_life: int = 30,
        effects: List[Dict[str, Any]] = None,
        side_effects: List[str] = None,
        manufacturer: str = "Generic",
        weight: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'un aliment.
        
        Args:
            food_type: Type d'aliment (MEAL, SNACK, DRINK, SUPPLEMENT)
            calories: Nombre de calories
            nutrition_value: Valeur nutritive (1-10)
            taste: Goût (SWEET, SALTY, SOUR, BITTER, UMAMI, NEUTRAL)
            shelf_life: Durée de conservation en jours
            effects: Liste des effets bénéfiques
            side_effects: Liste des effets secondaires
            manufacturer: Fabricant
            weight: Poids en kg
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = FoodMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        metadata.update({
            "food_type": food_type,
            "calories": calories,
            "nutrition_value": nutrition_value,
            "taste": taste,
            "shelf_life": shelf_life,
            "manufacturer": manufacturer,
            "weight": weight
        })
        
        # Ajouter les effets
        if effects:
            metadata["effects"] = effects
        
        # Ajouter les effets secondaires
        if side_effects:
            metadata["side_effects"] = side_effects
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in FoodMetadataSchema.OPTIONAL_FIELDS or key in FoodMetadataSchema.REQUIRED_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_consumable_metadata(
        consumable_type: str,
        effects: List[Dict[str, Any]] = None,
        duration: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'un consommable.
        
        Args:
            consumable_type: Type de consommable
            effects: Liste des effets
            duration: Durée des effets
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Déterminer le schéma approprié
        if consumable_type.upper() in ["FOOD", "DRINK"]:
            schema_class = FoodMetadataSchema
        else:
            schema_class = ConsumableMetadataSchema
        
        # Récupérer les métadonnées par défaut
        metadata = schema_class.get_default()
        
        # Mettre à jour avec les valeurs fournies
        if effects:
            metadata["effects"] = effects
        
        metadata.update({
            "duration": duration
        })
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in schema_class.OPTIONAL_FIELDS or key in schema_class.REQUIRED_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_hardware_metadata(
        hardware_type: str,
        stats: Dict[str, int] = None,
        power_consumption: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'un matériel informatique.
        
        Args:
            hardware_type: Type de matériel
            stats: Statistiques du matériel
            power_consumption: Consommation d'énergie
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = HardwareMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        if stats:
            metadata["stats"].update(stats)
        
        metadata.update({
            "power_consumption": power_consumption
        })
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in HardwareMetadataSchema.OPTIONAL_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def standardize_software_metadata(
        software_type: str,
        features: List[str] = None,
        system_requirements: Dict[str, int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Standardise les métadonnées d'un logiciel.
        
        Args:
            software_type: Type de logiciel
            features: Fonctionnalités du logiciel
            system_requirements: Configuration requise
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire de métadonnées standardisé
        """
        # Récupérer les métadonnées par défaut
        metadata = SoftwareMetadataSchema.get_default()
        
        # Mettre à jour avec les valeurs fournies
        if features:
            metadata["features"] = features
        
        if system_requirements:
            metadata["system_requirements"].update(system_requirements)
        
        # Ajouter les paramètres supplémentaires
        for key, value in kwargs.items():
            if key in SoftwareMetadataSchema.OPTIONAL_FIELDS:
                metadata[key] = value
        
        return metadata
    
    @staticmethod
    def to_json(metadata: Dict[str, Any]) -> str:
        """
        Convertit un dictionnaire de métadonnées en chaîne JSON.
        
        Args:
            metadata: Dictionnaire de métadonnées
            
        Returns:
            Chaîne JSON
        """
        return MetadataSchema.to_json(metadata)


# Fonctions d'aide pour les générateurs d'objets

def get_standardized_metadata(item_type: str, **kwargs) -> str:
    """
    Obtient des métadonnées standardisées pour un type d'objet donné.
    
    Args:
        item_type: Type d'objet (weapon, armor, implant, etc.)
        **kwargs: Paramètres spécifiques au type d'objet
        
    Returns:
        Chaîne JSON des métadonnées standardisées
    """
    item_type = item_type.lower()
    
    if item_type in ["weapon", "pistol", "rifle", "melee", "shotgun", "smg", "sniper"]:
        metadata = MetadataStandardizer.standardize_weapon_metadata(item_type, **kwargs)
    elif item_type in ["armor", "helmet", "chest", "legs", "boots", "gloves"]:
        metadata = MetadataStandardizer.standardize_armor_metadata(item_type, **kwargs)
    elif item_type in ["implant", "neural", "optical", "skeletal", "dermal", "circulatory"]:
        metadata = MetadataStandardizer.standardize_implant_metadata(item_type, **kwargs)
    elif item_type in ["consumable", "stimulant", "medicine", "drug", "food", "drink"]:
        metadata = MetadataStandardizer.standardize_consumable_metadata(item_type, **kwargs)
    elif item_type in ["hardware", "cpu", "ram", "ssd", "tool", "peripheral"]:
        metadata = MetadataStandardizer.standardize_hardware_metadata(item_type, **kwargs)
    elif item_type in ["software", "os", "firewall", "antivirus", "utility", "hacking_tool"]:
        metadata = MetadataStandardizer.standardize_software_metadata(item_type, **kwargs)
    else:
        # Type non reconnu, utiliser le schéma par défaut
        schema_class = get_schema_for_item_type(item_type)
        metadata = schema_class.get_default()
        
        # Ajouter les paramètres supplémentaires
        metadata.update(kwargs)
    
    return MetadataSchema.to_json(metadata)


def update_item_metadata(db_path: str, table_name: str, item_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Met à jour les métadonnées d'un objet dans la base de données.
    
    Args:
        db_path: Chemin vers la base de données
        table_name: Nom de la table
        item_id: ID de l'objet
        metadata: Dictionnaire de métadonnées
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            logger.error(f"Table {table_name} non trouvée dans la base de données")
            conn.close()
            return False
        
        # Vérifier si la colonne metadata existe
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        if "metadata" not in columns:
            logger.error(f"Colonne 'metadata' non trouvée dans la table {table_name}")
            conn.close()
            return False
        
        # Mettre à jour les métadonnées
        metadata_json = MetadataSchema.to_json(metadata)
        cursor.execute(f"UPDATE {table_name} SET metadata = ? WHERE id = ?", (metadata_json, item_id))
        conn.commit()
        
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées: {e}")
        return False


def main():
    """Fonction principale pour tester le standardiseur de métadonnées"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standardiseur de métadonnées YakTaa")
    parser.add_argument("--db", required=True, help="Chemin vers la base de données")
    parser.add_argument("--table", required=True, help="Nom de la table")
    parser.add_argument("--type", required=True, help="Type d'objet")
    parser.add_argument("--standardize-all", action="store_true", help="Standardiser tous les objets du type spécifié")
    
    args = parser.parse_args()
    
    if args.standardize_all:
        try:
            conn = sqlite3.connect(args.db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{args.table}'")
            if not cursor.fetchone():
                logger.error(f"Table {args.table} non trouvée dans la base de données")
                conn.close()
                return 1
            
            # Récupérer tous les objets de la table
            cursor.execute(f"SELECT id FROM {args.table}")
            rows = cursor.fetchall()
            
            success_count = 0
            for row in rows:
                item_id = row["id"]
                
                # Obtenir des métadonnées standardisées
                metadata = get_schema_for_item_type(args.type).get_default()
                
                # Mettre à jour les métadonnées
                if update_item_metadata(args.db, args.table, item_id, metadata):
                    success_count += 1
            
            conn.close()
            
            print(f"Métadonnées standardisées pour {success_count}/{len(rows)} objets")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la standardisation des métadonnées: {e}")
            return 1
    else:
        # Exemple d'utilisation
        weapon_metadata = MetadataStandardizer.standardize_weapon_metadata(
            "pistol", damage=15, accuracy=80, critical_chance=10
        )
        print(f"Métadonnées d'arme standardisées: {MetadataSchema.to_json(weapon_metadata)}")
        
        implant_metadata = MetadataStandardizer.standardize_implant_metadata(
            "neural", stats_bonus={"INTELLIGENCE": 2, "PERCEPTION": 1}, side_effects=["Headaches"]
        )
        print(f"Métadonnées d'implant standardisées: {MetadataSchema.to_json(implant_metadata)}")
    
    return 0


if __name__ == "__main__":
    main()
