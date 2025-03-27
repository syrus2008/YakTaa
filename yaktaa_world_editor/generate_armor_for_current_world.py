import sqlite3
import uuid
import random
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_armor_id():
    """Génère un ID unique pour une armure"""
    return f"armor_{uuid.uuid4()}"

def generate_armors(world_id, count=20):
    """
    Génère un certain nombre d'armures pour le monde spécifié
    """
    # Connecter à la base de données
    conn = sqlite3.connect('worlds.db')
    cursor = conn.cursor()
    
    # Vérifier si la table armors existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='armors'")
    if not cursor.fetchone():
        logger.error("La table armors n'existe pas. Cela est improbable car elle devrait déjà exister.")
        conn.close()
        return []
    
    # Vérifier la structure de la table
    cursor.execute("PRAGMA table_info(armors)")
    columns = [col[1] for col in cursor.fetchall()]
    logger.info(f"Colonnes existantes dans la table armors: {columns}")
    
    # Données pour la génération aléatoire
    armor_names = [
        "Veste Blindée", "Gilet Tactique", "Combinaison Renforcée", "Armure Composite", 
        "Plaque de Kevlar", "Blindage Corporel", "Exosquelette Léger", "Carapace Urbaine",
        "Protection Balistique", "Manteau Anti-Frag", "Nano-Weave", "Tenue Anti-Émeute",
        "Armure Réactive", "Bouclier Cutané", "Peau Polymère", "Armure Légère",
        "Armure Moyenne", "Armure Lourde", "Cuirasse Tactique", "Armure Militaire"
    ]
    
    defense_types = ["PHYSICAL", "BALLISTIC", "ENERGY", "THERMAL", "CHEMICAL", "EMP"]
    slots = ["HEAD", "TORSO", "ARMS", "LEGS", "FULL_BODY"]
    rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
    
    # Générer les armures
    armors = []
    for _ in range(count):
        armor_id = generate_armor_id()
        name = random.choice(armor_names)
        description = f"Une {name.lower()} offrant une protection de qualité."
        defense = random.randint(5, 50)
        defense_type = random.choice(defense_types)
        slot = random.choice(slots)
        weight = random.randint(1, 15)
        durability = random.randint(50, 150)
        mod_slots = random.randint(0, 3)
        rarity = random.choices(rarities, weights=[50, 30, 15, 4, 1])[0]
        value = defense * 100 + durability * 10 + mod_slots * 500
        
        # Ajouter des variations au nom selon la rareté
        if rarity == "UNCOMMON":
            name = name + " +"
        elif rarity == "RARE":
            name = name + " ++"
        elif rarity == "EPIC":
            name = "Supérieure " + name
        elif rarity == "LEGENDARY":
            name = name + " Légendaire"
        
        # Création de l'enregistrement selon la structure réelle de la base de données
        armor = (
            armor_id,              # id
            world_id,              # world_id
            name,                  # name
            description,           # description
            defense,               # defense
            defense_type,          # defense_type
            slot,                  # slots
            weight,                # weight
            durability,            # durability
            mod_slots,             # mod_slots
            rarity,                # rarity
            value,                 # value
            None,                  # location_type
            None,                  # location_id
            None                   # metadata
        )
        
        armors.append(armor)
    
    # Insérer les armures dans la base de données
    try:
        cursor.executemany('''
        INSERT INTO armors (
            id, world_id, name, description, defense, defense_type, slots, 
            weight, durability, mod_slots, rarity, value, location_type, 
            location_id, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', armors)
        
        # Valider les changements
        conn.commit()
        logger.info(f"{count} armures générées pour le monde {world_id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des armures: {e}")
        conn.rollback()
    finally:
        # Fermer la connexion
        conn.close()
    
    return armors

if __name__ == "__main__":
    # Monde cible - Utilisez l'ID du monde actuellement ouvert
    target_world_id = "10ac4af3-21bc-437d-b34f-11b4af004f8f"
    
    # Générer 20 armures pour ce monde
    generated_armors = generate_armors(target_world_id, 20)
    
    # Afficher les armures générées
    for i, armor in enumerate(generated_armors):
        logger.info(f"Armure {i+1}: {armor[2]} - Défense: {armor[4]} - Rareté: {armor[10]}")
