#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour la base de données avec les tables d'équipement de combat
"""

import os
import logging
import sqlite3
from database import get_database

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("YakTaa.WorldEditor.DBUpdateEquipment")

def update_equipment_schema():
    """
    Met à jour le schéma de la base de données pour inclure les tables d'équipement
    
    Returns:
        bool: True si la mise à jour est réussie, False sinon
    """
    # Chemin explicite vers la base de données de l'application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds.db")
    
    # Vérifier que la base de données existe
    if not os.path.exists(db_path):
        logger.error(f"La base de données n'existe pas: {db_path}")
        return False, None
    
    # Ouvrir la connexion à la base de données
    db = get_database(db_path)
    
    try:
        cursor = db.conn.cursor()
        
        # 1. Table d'équipements (armes, armures, etc.)
        logger.info("Création de la table 'equipment'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            equipment_type TEXT NOT NULL,
            subtype TEXT,
            rarity TEXT,
            price INTEGER DEFAULT 0,
            level_requirement INTEGER DEFAULT 1,
            damage INTEGER DEFAULT 0,
            damage_type TEXT,
            accuracy REAL DEFAULT 0,
            critical_chance REAL DEFAULT 0,
            critical_multiplier REAL DEFAULT 1.5,
            range_max INTEGER DEFAULT 0,
            defense INTEGER DEFAULT 0,
            armor_type TEXT,
            health_bonus INTEGER DEFAULT 0,
            initiative_modifier INTEGER DEFAULT 0,
            stealth_modifier REAL DEFAULT 0,
            resistance_physical INTEGER DEFAULT 0,
            resistance_energy INTEGER DEFAULT 0,
            resistance_emp INTEGER DEFAULT 0,
            resistance_biohazard INTEGER DEFAULT 0,
            resistance_cyber INTEGER DEFAULT 0,
            resistance_viral INTEGER DEFAULT 0,
            resistance_nanite INTEGER DEFAULT 0,
            special_abilities TEXT,
            is_cybernetic BOOLEAN DEFAULT 0,
            is_unique BOOLEAN DEFAULT 0,
            icon_path TEXT,
            model_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
        )
        """)
        
        # 2. Table d'association entre personnages et équipements
        logger.info("Création de la table 'character_equipment'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS character_equipment (
            id TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            equipment_id TEXT NOT NULL,
            slot TEXT NOT NULL,
            is_equipped BOOLEAN DEFAULT 0,
            condition INTEGER DEFAULT 100,
            modification_level INTEGER DEFAULT 0,
            custom_name TEXT,
            custom_stats TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
            UNIQUE(character_id, equipment_id)
        )
        """)
        
        # 3. Table de modifications d'équipement (mods)
        logger.info("Création de la table 'equipment_mods'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_mods (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            mod_type TEXT NOT NULL,
            compatibility TEXT NOT NULL,
            rarity TEXT,
            price INTEGER DEFAULT 0,
            level_requirement INTEGER DEFAULT 1,
            damage_modifier INTEGER DEFAULT 0,
            accuracy_modifier REAL DEFAULT 0,
            critical_chance_modifier REAL DEFAULT 0,
            critical_multiplier_modifier REAL DEFAULT 0,
            range_modifier INTEGER DEFAULT 0,
            defense_modifier INTEGER DEFAULT 0,
            health_modifier INTEGER DEFAULT 0,
            initiative_modifier INTEGER DEFAULT 0,
            stealth_modifier REAL DEFAULT 0,
            resistance_physical_modifier INTEGER DEFAULT 0,
            resistance_energy_modifier INTEGER DEFAULT 0,
            resistance_emp_modifier INTEGER DEFAULT 0,
            resistance_biohazard_modifier INTEGER DEFAULT 0,
            resistance_cyber_modifier INTEGER DEFAULT 0,
            resistance_viral_modifier INTEGER DEFAULT 0,
            resistance_nanite_modifier INTEGER DEFAULT 0,
            special_effect TEXT,
            icon_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
        )
        """)
        
        # 4. Table d'association entre équipements et mods
        logger.info("Création de la table 'equipment_installed_mods'")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_installed_mods (
            id TEXT PRIMARY KEY,
            character_equipment_id TEXT NOT NULL,
            mod_id TEXT NOT NULL,
            slot INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_equipment_id) REFERENCES character_equipment(id) ON DELETE CASCADE,
            FOREIGN KEY (mod_id) REFERENCES equipment_mods(id) ON DELETE CASCADE,
            UNIQUE(character_equipment_id, mod_id)
        )
        """)
        
        # 5. Index pour améliorer les performances
        logger.info("Création des index pour les tables d'équipement")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_world_id ON equipment(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment_rarity ON equipment(rarity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_equip_char_id ON character_equipment(character_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_char_equip_is_equipped ON character_equipment(is_equipped)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_mods_world_id ON equipment_mods(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_mods_compatibility ON equipment_mods(compatibility)")
        
        # 6. Mettre à jour la table des personnages pour ajouter un champ de slots d'équipement
        logger.info("Ajout de la colonne 'equipment_slots' à la table 'characters'")
        try:
            cursor.execute("ALTER TABLE characters ADD COLUMN equipment_slots TEXT")
        except sqlite3.OperationalError:
            logger.info("La colonne 'equipment_slots' existe déjà dans la table 'characters'")
        
        # Enregistrer les modifications
        db.conn.commit()
        logger.info("Mise à jour du schéma d'équipement terminée avec succès")
        
        return True, db
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du schéma d'équipement: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False, None

def insert_default_equipment(world_id=None, db=None):
    """
    Insère des équipements par défaut dans la base de données
    
    Args:
        world_id: ID du monde pour lequel créer les équipements (optionnel)
                Si None, utilise le monde actif
        db: Instance de la base de données (optionnel)
                
    Returns:
        bool: True si l'insertion est réussie, False sinon
    """
    if db is None:
        db = get_database()
    
    try:
        cursor = db.conn.cursor()
        
        # Trouver un monde valide si non spécifié
        if not world_id:
            cursor.execute("SELECT id FROM worlds WHERE is_active = 1 LIMIT 1")
            active_world = cursor.fetchone()
            
            if active_world:
                world_id = active_world["id"]
            else:
                cursor.execute("SELECT id FROM worlds LIMIT 1")
                world = cursor.fetchone()
                
                if not world:
                    logger.error("Aucun monde trouvé dans la base de données")
                    return False
                    
                world_id = world["id"]
        
        # Vérifier si des équipements existent déjà pour ce monde
        cursor.execute("SELECT COUNT(*) as count FROM equipment WHERE world_id = ?", (world_id,))
        existing_count = cursor.fetchone()["count"]
        
        if existing_count > 0:
            logger.info(f"{existing_count} équipements existent déjà pour ce monde")
            return True
        
        # Liste des équipements par défaut à créer
        import uuid
        
        # Armes de mêlée
        melee_weapons = [
            {
                "id": str(uuid.uuid4()),
                "name": "Batte de combat",
                "description": "Une batte renforcée avec des plaques métalliques.",
                "equipment_type": "WEAPON",
                "subtype": "MELEE",
                "rarity": "COMMON",
                "price": 500,
                "damage": 15,
                "damage_type": "PHYSICAL",
                "accuracy": 0.85,
                "critical_chance": 0.1,
                "range_max": 1,
                "special_abilities": "stun"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Lame monofilaire",
                "description": "Une lame ultra-fine capable de trancher presque n'importe quoi.",
                "equipment_type": "WEAPON",
                "subtype": "MELEE",
                "rarity": "RARE",
                "price": 3500,
                "damage": 25,
                "damage_type": "PHYSICAL",
                "accuracy": 0.9,
                "critical_chance": 0.2,
                "critical_multiplier": 2.0,
                "range_max": 1,
                "special_abilities": "bleeding"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Matraque à décharge",
                "description": "Une matraque qui délivre une décharge électrique lors de l'impact.",
                "equipment_type": "WEAPON",
                "subtype": "MELEE",
                "rarity": "UNCOMMON",
                "price": 1200,
                "damage": 12,
                "damage_type": "ENERGY",
                "accuracy": 0.8,
                "critical_chance": 0.15,
                "range_max": 1,
                "special_abilities": "emp_burst,stun"
            }
        ]
        
        # Armes à distance
        ranged_weapons = [
            {
                "id": str(uuid.uuid4()),
                "name": "Pistolet Kang Tao P-45",
                "description": "Un pistolet compact et fiable, utilisé par les forces de sécurité.",
                "equipment_type": "WEAPON",
                "subtype": "PISTOL",
                "rarity": "COMMON",
                "price": 1000,
                "damage": 18,
                "damage_type": "PHYSICAL",
                "accuracy": 0.75,
                "critical_chance": 0.05,
                "range_max": 20,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Fusil d'assaut Militech M-31",
                "description": "Arme standard des forces militaires, robuste et polyvalente.",
                "equipment_type": "WEAPON",
                "subtype": "ASSAULT_RIFLE",
                "rarity": "UNCOMMON",
                "price": 2500,
                "damage": 22,
                "damage_type": "PHYSICAL",
                "accuracy": 0.7,
                "critical_chance": 0.05,
                "range_max": 40,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Fusil de précision Tsunami Nekomata",
                "description": "Un fusil de précision haute technologie avec optique avancée.",
                "equipment_type": "WEAPON",
                "subtype": "SNIPER_RIFLE",
                "rarity": "RARE",
                "price": 4000,
                "damage": 45,
                "damage_type": "PHYSICAL",
                "accuracy": 0.95,
                "critical_chance": 0.25,
                "critical_multiplier": 2.5,
                "range_max": 100,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Pistolet énergétique Arasaka",
                "description": "Un pistolet qui tire des décharges d'énergie concentrée.",
                "equipment_type": "WEAPON",
                "subtype": "ENERGY_PISTOL",
                "rarity": "RARE",
                "price": 3800,
                "damage": 20,
                "damage_type": "ENERGY",
                "accuracy": 0.85,
                "critical_chance": 0.1,
                "range_max": 25,
                "special_abilities": "shield_pierce"
            }
        ]
        
        # Armes spéciales
        special_weapons = [
            {
                "id": str(uuid.uuid4()),
                "name": "Lanceur de nanites",
                "description": "Arme expérimentale qui projette des essaims de nanites dévorant toute matière.",
                "equipment_type": "WEAPON",
                "subtype": "SPECIAL",
                "rarity": "LEGENDARY",
                "price": 12000,
                "damage": 30,
                "damage_type": "NANITE",
                "accuracy": 0.6,
                "critical_chance": 0.15,
                "range_max": 15,
                "special_abilities": "dot_nanite,armor_decay"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Déchiqueteur neuronal",
                "description": "Un dispositif qui émet des ondes causant des dommages au système nerveux.",
                "equipment_type": "WEAPON",
                "subtype": "SPECIAL",
                "rarity": "EPIC",
                "price": 8000,
                "damage": 25,
                "damage_type": "CYBER",
                "accuracy": 0.7,
                "critical_chance": 0.1,
                "range_max": 10,
                "special_abilities": "stun,initiative_reduction"
            }
        ]
        
        # Armures
        armors = [
            {
                "id": str(uuid.uuid4()),
                "name": "Veste tactique",
                "description": "Une veste renforcée offrant une protection basique.",
                "equipment_type": "ARMOR",
                "subtype": "LIGHT",
                "rarity": "COMMON",
                "price": 800,
                "defense": 10,
                "resistance_physical": 15,
                "resistance_energy": 5,
                "resistance_emp": 0,
                "resistance_biohazard": 5,
                "stealth_modifier": 0.0
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Armure composite militaire",
                "description": "Armure militaire standard offrant une bonne protection contre diverses menaces.",
                "equipment_type": "ARMOR",
                "subtype": "MEDIUM",
                "rarity": "UNCOMMON",
                "price": 2500,
                "defense": 20,
                "resistance_physical": 25,
                "resistance_energy": 15,
                "resistance_emp": 5,
                "resistance_biohazard": 10,
                "initiative_modifier": -1,
                "stealth_modifier": -0.1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Exosquelette de combat",
                "description": "Un exosquelette complet qui améliore la force et offre une excellente protection.",
                "equipment_type": "ARMOR",
                "subtype": "HEAVY",
                "rarity": "RARE",
                "price": 6000,
                "defense": 35,
                "health_bonus": 20,
                "resistance_physical": 40,
                "resistance_energy": 25,
                "resistance_emp": 0,
                "resistance_biohazard": 15,
                "initiative_modifier": -2,
                "stealth_modifier": -0.3
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Armure polymère adaptative",
                "description": "Armure avancée qui s'adapte aux types d'attaques reçues.",
                "equipment_type": "ARMOR",
                "subtype": "MEDIUM",
                "rarity": "EPIC",
                "price": 8500,
                "defense": 25,
                "resistance_physical": 30,
                "resistance_energy": 30,
                "resistance_emp": 20,
                "resistance_biohazard": 25,
                "resistance_cyber": 25,
                "resistance_viral": 25,
                "resistance_nanite": 15,
                "special_abilities": "adaptive_defense",
                "stealth_modifier": -0.05
            }
        ]
        
        # Implants cybernétiques
        implants = [
            {
                "id": str(uuid.uuid4()),
                "name": "Réflexes renforcés",
                "description": "Implant neural qui améliore les réflexes et la vitesse de réaction.",
                "equipment_type": "IMPLANT",
                "subtype": "NEURAL",
                "rarity": "UNCOMMON",
                "price": 3000,
                "initiative_modifier": 3,
                "accuracy": 0.05,
                "is_cybernetic": 1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Dermalarmure",
                "description": "Implant sous-cutané qui renforce la peau contre les impacts et les brûlures.",
                "equipment_type": "IMPLANT",
                "subtype": "DERMAL",
                "rarity": "UNCOMMON",
                "price": 3500,
                "defense": 8,
                "resistance_physical": 15,
                "resistance_energy": 10,
                "is_cybernetic": 1
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Processeur de combat",
                "description": "Implant cérébral qui analyse les situations de combat en temps réel.",
                "equipment_type": "IMPLANT",
                "subtype": "NEURAL",
                "rarity": "RARE",
                "price": 6000,
                "accuracy": 0.1,
                "critical_chance": 0.1,
                "initiative_modifier": 2,
                "is_cybernetic": 1,
                "special_abilities": "threat_analysis"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Filtres sanguins avancés",
                "description": "Système de filtration qui neutralise les toxines et agents pathogènes.",
                "equipment_type": "IMPLANT",
                "subtype": "INTERNAL",
                "rarity": "RARE",
                "price": 4500,
                "resistance_biohazard": 40,
                "resistance_viral": 35,
                "resistance_nanite": 20,
                "is_cybernetic": 1,
                "special_abilities": "toxin_immunity"
            }
        ]
        
        # Regrouper tous les équipements
        all_equipment = melee_weapons + ranged_weapons + special_weapons + armors + implants
        
        # Insérer les équipements dans la base de données
        for item in all_equipment:
            # Ajouter l'ID du monde
            item["world_id"] = world_id
            
            # Créer la partie des champs et valeurs de la requête SQL
            fields = ", ".join(item.keys())
            placeholders = ", ".join(["?" for _ in item.keys()])
            values = list(item.values())
            
            # Exécuter la requête
            cursor.execute(f"INSERT INTO equipment ({fields}) VALUES ({placeholders})", values)
        
        # Enregistrer les modifications
        db.conn.commit()
        logger.info(f"{len(all_equipment)} équipements par défaut ont été insérés dans la base de données")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des équipements par défaut: {e}")
        if db and db.conn:
            db.conn.rollback()
        return False

def main():
    """Fonction principale"""
    logger.info("Début de la mise à jour du schéma d'équipement")
    success, db = update_equipment_schema()
    if success:
        logger.info("Insertion des équipements par défaut")
        try:
            insert_default_equipment(db=db)
        finally:
            if db and db.conn:
                db.conn.close()
        logger.info("Mise à jour du schéma d'équipement terminée avec succès")
    else:
        logger.error("Échec de la mise à jour du schéma d'équipement")

if __name__ == "__main__":
    main()
