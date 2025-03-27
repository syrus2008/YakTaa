import sqlite3
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
import random

# Chemin vers la base de donnu00e9es
db_path = os.path.join(os.path.dirname(__file__), 'worlds.db')

# Vu00e9rifier si le fichier existe
if not os.path.exists(db_path):
    print(f"La base de donnu00e9es n'existe pas u00e0 l'emplacement: {db_path}")
    sys.exit(1)

# Connexion u00e0 la base de donnu00e9es
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ru00e9cupu00e9rer l'ID du monde actif
cursor.execute("SELECT id FROM worlds WHERE is_active = 1 LIMIT 1")
world_result = cursor.fetchone()
if world_result:
    world_id = world_result[0]
else:
    # Si aucun monde actif, prendre le premier monde disponible
    cursor.execute("SELECT id FROM worlds LIMIT 1")
    world_result = cursor.fetchone()
    if world_result:
        world_id = world_result[0]
    else:
        print("Aucun monde trouvé dans la base de données.")
        sys.exit(1)

print(f"Utilisation du monde avec l'ID: {world_id}")

# Fonction pour générer un ID unique au format UUID
def generate_uuid():
    return str(uuid.uuid4())

# Ru00e9cupu00e9rer tous les articles ru00e9fu00e9rencu00e9s dans shop_inventory
cursor.execute("SELECT item_id, item_type, price FROM shop_inventory")
shop_items = cursor.fetchall()

# Dictionnaire pour stocker les articles manquants par type
missing_items = {}
for item_id, item_type, price in shop_items:
    # Du00e9terminer la table correspondante au type d'article
    type_to_table = {
        'hardware': 'hardware_items',
        'software': 'software_items',
        'consumable': 'consumable_items',
        'implant': 'implant_items',
        'weapon': 'weapon_items',
        'armor': 'armors',
        'data_broker': 'software_items',
        'vpn': 'software_items',
        'crypto': 'software_items',
        'cloud_storage': 'software_items',
        'neural': 'implant_items',
        'cpu': 'hardware_items',
        'ram': 'hardware_items',
        'ssd': 'hardware_items',
        'os': 'software_items',
        'firewall': 'software_items',
        'drink': 'consumable_items',
        'stimulant': 'consumable_items',
        'pistol': 'weapon_items',
        'power_supply': 'hardware_items',
        'motherboard': 'hardware_items',
        'storage': 'hardware_items',
        'ai_assistant': 'software_items'
    }
    
    table_name = type_to_table.get(item_type.lower(), None)
    
    if not table_name:
        # Si le type n'est pas reconnu, on le considu00e8re comme un article gu00e9nu00e9rique de type software
        table_name = 'software_items'
    
    # Vu00e9rifier si l'article existe du00e9ju00e0 dans la table correspondante
    cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        if table_name not in missing_items:
            missing_items[table_name] = []
        missing_items[table_name].append((item_id, item_type, price))

# Cru00e9er les articles manquants dans les tables correspondantes
for table_name, items in missing_items.items():
    print(f"Cru00e9ation de {len(items)} articles manquants dans la table {table_name}...")
    
    for item_id, item_type, price in items:
        # Gu00e9nu00e9rer un nom alu00e9atoire basu00e9 sur le type
        item_names = {
            'hardware': ["Processeur quantique", "Module RAM cristallin", "Disque SSD holographique", "Carte mu00e8re nu00e9urale", "Alimentation u00e0 fusion"],
            'software': ["Systu00e8me d'exploitation NeoOS", "Firewall Quantum", "Antivirus Synapse", "Suite bureautique CyberOffice", "Compilateur Neural"],
            'consumable': ["Booster d'u00e9nergie", "Stimulant cognitif", "Nano-ru00e9parateur", "Boost mu00e9tabolique", "Stabilisateur synaptique"],
            'implant': ["Implant cortical", "Interface neurale", "Amplificateur synaptique", "Processeur cu00e9ru00e9bral", "Ru00e9tinoplastie"],
            'weapon': ["Pistolet u00e0 impulsion", "Fusil u00e0 plasma", "Lame monofilament", "Canon u00e0 particules", "Gantelet u00e9nergu00e9tique"],
            'data_broker': ["Service d'information Nexus", "Courtier de donnu00e9es Shadow", "Ru00e9seau d'informateurs", "Base de donnu00e9es cryptu00e9e", "Analyseur de mu00e9tadonnu00e9es"],
            'vpn': ["Ru00e9seau privu00e9 Ghost", "Tunnel su00e9curisu00e9 Phantom", "Routage anonyme Specter", "Masque IP Stealth", "Protection d'identitu00e9 digitale"],
            'crypto': ["Portefeuille quantique", "Monnaie numu00e9rique su00e9curisu00e9e", "Jeton blockchain avancu00e9", "Crypto-devise anonyme", "Systu00e8me de paiement du00e9centralisu00e9"],
            'cloud_storage': ["Stockage cloud su00e9curisu00e9", "Coffre-fort numu00e9rique", "Archive quantique", "Serveur virtuel privu00e9", "Sauvegarde holographique"],
            'neural': ["Interface cu00e9ru00e9brale", "Processeur synaptique", "Amplificateur cognitif", "Implant mu00e9moriel", "Accu00e9lu00e9rateur neuronal"],
            'cpu': ["Processeur quantique", "CPU multi-noyaux", "Unitu00e9 de calcul avancu00e9e", "Processeur neuromorphique", "Puce bio-synthu00e9tique"],
            'ram': ["Mu00e9moire cristalline", "RAM quantique", "Module mu00e9moriel avancu00e9", "Cache neuronal", "Mu00e9moire holographique"],
            'ssd': ["Stockage molu00e9culaire", "Disque quantique", "Mu00e9moire flash avancu00e9e", "Stockage holographique", "Cristal de donnu00e9es"],
            'os': ["Systu00e8me NeoOS", "Environnement Quantum", "Interface neurale", "OS su00e9curisu00e9 Fortress", "Plateforme Nexus"],
            'firewall': ["Barriu00e8re quantique", "Protection adaptative", "Bouclier numu00e9rique", "Du00e9fense proactive", "Gardien ru00e9seau"],
            'drink': ["Boisson u00e9nergu00e9tique Surge", "Elixir de concentration", "Tonique neural", "Boost synaptique", "Rafrau00eechissement quantique"],
            'stimulant': ["Amplificateur cognitif", "Booster neuronal", "Accu00e9lu00e9rateur synaptique", "Catalyseur cu00e9ru00e9bral", "Stimulant ru00e9flexe"],
            'pistol': ["Pistolet u00e0 impulsion", "Arme de poing u00e9nergu00e9tique", "Blaster compact", "Pistolet u00e0 plasma", "Neutralisateur de poche"],
            'power_supply': ["Alimentation quantique", "Gu00e9nu00e9rateur compact", "Cellule d'u00e9nergie", "Convertisseur de puissance", "Source d'u00e9nergie stable"],
            'motherboard': ["Carte mu00e8re avancu00e9e", "Plateforme systu00e8me", "Circuit intu00e9gru00e9 principal", "Base computationnelle", "Architecture quantique"],
            'storage': ["Stockage molu00e9culaire", "Disque quantique", "Matrice de donnu00e9es", "Archive compacte", "Cristal mu00e9moriel"],
            'ai_assistant': ["Assistant IA personnel", "Conseiller numu00e9rique", "Intelligence synthu00e9tique", "Compagnon algorithmique", "Aide cognitive"]
        }
        
        # Su00e9lectionner un nom alu00e9atoire basu00e9 sur le type
        name_list = item_names.get(item_type.lower(), [f"Article {item_type.capitalize()}"])
        item_name = random.choice(name_list)
        if len(name_list) > 1:
            item_name += f" {random.choice(['MK', 'v', 'Gen', 'Type', 'Series'])}{random.randint(1, 9)}"
        
        # Gu00e9nu00e9rer une description
        descriptions = {
            'hardware': ["Un u00e9quipement matu00e9riel de haute technologie.", "Composant hardware de qualitu00e9 supu00e9rieure.", "Piu00e8ce d'u00e9quipement essentielle pour tout systu00e8me."],
            'software': ["Un logiciel avancu00e9 avec des fonctionnalitu00e9s uniques.", "Programme informatique de derniu00e8re gu00e9nu00e9ration.", "Solution logicielle optimisu00e9e pour les performances."],
            'consumable': ["Un produit consommable aux effets immu00e9diats.", "Substance qui amu00e9liore temporairement les capacitu00e9s.", "Consommable de qualitu00e9 pour des ru00e9sultats garantis."],
            'implant': ["Un implant cybernu00e9tique de pointe.", "Amu00e9lioration corporelle avec intu00e9gration neurale.", "Augmentation cybernu00e9tique pour des capacitu00e9s surhumaines."],
            'weapon': ["Une arme puissante et pru00e9cise.", "Outil de combat avancu00e9 avec technologie de pointe.", "Armement lu00e9tal concu pour l'efficacitu00e9 maximale."]
        }
        
        # Obtenir une catu00e9gorie gu00e9nu00e9rale pour le type spu00e9cifique
        general_type = item_type.lower()
        for category in ['hardware', 'software', 'consumable', 'implant', 'weapon']:
            if general_type in type_to_table and type_to_table[general_type] == f"{category}_items":
                general_type = category
                break
        
        description_list = descriptions.get(general_type, [f"Un article de type {item_type} de haute qualitu00e9."])
        item_description = random.choice(description_list)
        
        # Insu00e9rer l'article dans la table correspondante en fonction de sa structure
        if table_name == 'hardware_items':
            level = random.randint(1, 5)
            quality = random.choice(['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'])
            rarity = quality.lower()
            stats = json.dumps({"performance": random.randint(10, 100), "reliability": random.randint(10, 100)})
            hardware_type = item_type.upper()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, world_id, name, description, hardware_type, quality, rarity, level, stats, price, is_available, type, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, world_id, item_name, item_description, hardware_type, quality, rarity, level, stats, price, 1, item_type, 1))
            
        elif table_name == 'software_items':
            level = random.randint(1, 5)
            version = f"{random.randint(1, 5)}.{random.randint(0, 9)}"
            features = json.dumps({"efficiency": random.randint(10, 100), "security": random.randint(10, 100)})
            software_type = item_type.upper()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, name, description, software_type, level, features, price, world_id, is_legal, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, item_description, software_type, level, features, price, world_id, 1, version))
            
        elif table_name == 'consumable_items':
            effects = json.dumps({"health": random.randint(10, 50), "energy": random.randint(10, 50), "duration": random.randint(60, 600)})
            rarity = random.choice(['common', 'uncommon', 'rare', 'epic', 'legendary'])
            uses = random.randint(1, 3)
            consumable_type = 'HEALTH' if 'health' in item_type.lower() else 'BUFF'
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, world_id, name, description, item_type, rarity, uses, effects, price, is_available, consumable_type, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, world_id, item_name, item_description, item_type, rarity, uses, effects, price, 1, consumable_type, 1))
            
        elif table_name == 'implant_items':
            level = random.randint(1, 5)
            stats = json.dumps({"intelligence": random.randint(1, 10), "reflexes": random.randint(1, 10)})
            grade = random.choice(['Standard', 'Enhanced', 'Military', 'Prototype', 'Experimental'])
            implant_type = item_type.upper()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, name, description, implant_type, grade, level, stats, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, item_description, implant_type, grade, level, stats, price, world_id, 1))
            
        elif table_name == 'weapon_items':
            level = random.randint(1, 5)
            stats = json.dumps({"damage": random.randint(10, 50), "range": random.randint(5, 30), "accuracy": random.randint(50, 95)})
            rarity = random.choice(['common', 'uncommon', 'rare', 'epic', 'legendary'])
            weapon_type = item_type.upper()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, name, description, weapon_type, rarity, level, stats, price, world_id, is_legal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item_name, item_description, weapon_type, rarity, level, stats, price, world_id, 1))
            
        elif table_name == 'armors':
            defense = random.randint(10, 50)
            defense_type = random.choice(['PHYSICAL', 'ENERGY', 'THERMAL', 'EMP'])
            slots = json.dumps(["TORSO"])
            weight = random.randint(1, 10)
            durability = random.randint(50, 100)
            mod_slots = random.randint(0, 3)
            rarity = random.choice(['common', 'uncommon', 'rare', 'epic', 'legendary'])
            
            cursor.execute(f"""
                INSERT INTO {table_name} (id, world_id, name, description, defense, defense_type, slots, weight, durability, mod_slots, rarity, value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, world_id, item_name, item_description, defense, defense_type, slots, weight, durability, mod_slots, rarity, price))

# Valider les modifications
conn.commit()

# Compter le nombre d'articles cru00e9u00e9s
total_created = sum(len(items) for items in missing_items.values())
print(f"\nCru00e9ation terminu00e9e. {total_created} articles ont u00e9tu00e9 ajoutu00e9s u00e0 la base de donnu00e9es.")

# Fermer la connexion
conn.close()
