import sqlite3
import os
import sys
import uuid

# Connect to the database
db_path = r'c:\Users\thibaut\Desktop\glata\yaktaa_world_editor\worlds.db'

print(f"Connecting to database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the food_items table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='food_items'")
if cursor.fetchone():
    print("food_items table already exists")
else:
    # Create the food_items table
    print("Creating food_items table...")
    cursor.execute('''
    CREATE TABLE food_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        food_type TEXT,
        price INTEGER,
        health_restore INTEGER,
        energy_restore INTEGER,
        mental_restore INTEGER,
        is_legal INTEGER DEFAULT 1,
        rarity TEXT DEFAULT 'COMMON',
        world_id TEXT,
        metadata TEXT,
        uses INTEGER DEFAULT 1
    )
    ''')
    conn.commit()
    print("food_items table created successfully")
    
    # Add some sample food items
    sample_foods = [
        {
            'id': f"food_{uuid.uuid4()}",
            'name': "NeuroCaf Coffee",
            'description': "Boisson énergisante populaire avec un boost de concentration",
            'food_type': 'DRINK',
            'price': 25,
            'health_restore': 0,
            'energy_restore': 15,
            'mental_restore': 10,
            'is_legal': 1,
            'rarity': 'COMMON',
            'uses': 1
        },
        {
            'id': f"food_{uuid.uuid4()}",
            'name': "SynthSteak",
            'description': "Steak cultivé en laboratoire avec des nutriments optimisés",
            'food_type': 'FOOD',
            'price': 75,
            'health_restore': 20,
            'energy_restore': 15,
            'mental_restore': 0,
            'is_legal': 1,
            'rarity': 'COMMON',
            'uses': 1
        },
        {
            'id': f"food_{uuid.uuid4()}",
            'name': "HyperEnergyDrink",
            'description': "Boisson énergisante extrême, légalement discutable",
            'food_type': 'DRINK',
            'price': 120,
            'health_restore': -5,
            'energy_restore': 40,
            'mental_restore': 15,
            'is_legal': 0,
            'rarity': 'UNCOMMON',
            'uses': 1
        },
        {
            'id': f"food_{uuid.uuid4()}",
            'name': "Ration de Survie",
            'description': "Ration militaire complète et nourrissante",
            'food_type': 'FOOD',
            'price': 150,
            'health_restore': 25,
            'energy_restore': 25,
            'mental_restore': 5,
            'is_legal': 1,
            'rarity': 'COMMON',
            'uses': 3
        },
        {
            'id': f"food_{uuid.uuid4()}",
            'name': "Pilule Nutritive",
            'description': "Substitut de repas technologique compact",
            'food_type': 'PILL',
            'price': 50,
            'health_restore': 15,
            'energy_restore': 10,
            'mental_restore': 0,
            'is_legal': 1,
            'rarity': 'COMMON',
            'uses': 1
        }
    ]
    
    # Insert the sample food items
    for food in sample_foods:
        cursor.execute('''
        INSERT INTO food_items (
            id, name, description, food_type, price, health_restore, energy_restore, 
            mental_restore, is_legal, rarity, uses
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            food['id'], food['name'], food['description'], food['food_type'], 
            food['price'], food['health_restore'], food['energy_restore'], 
            food['mental_restore'], food['is_legal'], food['rarity'], food['uses']
        ))
    
    conn.commit()
    print(f"Added {len(sample_foods)} sample food items to the database")

# Count items in each table
cursor.execute("SELECT COUNT(*) FROM hardware_items")
hardware_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM software_items")
software_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM food_items")
food_count = cursor.fetchone()[0]

print(f"\nDatabase item counts:")
print(f"- Hardware items: {hardware_count}")
print(f"- Software items: {software_count}")
print(f"- Food items: {food_count}")

conn.close()
print("Database operations completed")
