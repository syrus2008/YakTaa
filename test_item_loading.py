import os
import sqlite3
import sys
import logging

# Add the parent directory to the Python path so that yaktaa can be imported as top-level
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import necessary modules from yaktaa with absolute imports
from yaktaa.items.shop_manager import ShopManager
from yaktaa.world.world_loader import WorldLoader
from yaktaa.items.hardware import HardwareItem
from yaktaa.items.software import SoftwareItem
from yaktaa.items.food import FoodItem

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('item_test')

def test_load_items():
    """Test loading items from the database"""
    
    try:
        # Create instances
        world_loader = WorldLoader()
        shop_manager = ShopManager(world_loader)
        
        # Get the DB path
        db_path = world_loader._get_editor_db_path()
        logger.info(f"Using database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Test loading a hardware item
        logger.info("\n--- Testing Hardware Item Loading ---")
        cursor.execute("SELECT id, name FROM hardware_items LIMIT 3")
        hardware_items = cursor.fetchall()
        
        for hw_id, hw_name in hardware_items:
            logger.info(f"Attempting to load hardware item: {hw_id} ({hw_name})")
            item = shop_manager._load_item_details(conn, "hardware", hw_id)
            
            if item:
                logger.info(f"SUCCESS: Loaded item {item.name} (ID: {item.id})")
                if isinstance(item, HardwareItem):
                    logger.info(f"  Type: HardwareItem - {item.type}")
                    logger.info(f"  Description: {item.description[:50]}...")
                    logger.info(f"  Price: {item.price}")
                else:
                    logger.warning(f"  WRONG TYPE: Expected HardwareItem but got {type(item)}")
            else:
                logger.error(f"FAILED: Could not load hardware item {hw_id}")
        
        # 2. Test loading a software item
        logger.info("\n--- Testing Software Item Loading ---")
        cursor.execute("SELECT id, name FROM software_items LIMIT 3")
        software_items = cursor.fetchall()
        
        for sw_id, sw_name in software_items:
            logger.info(f"Attempting to load software item: {sw_id} ({sw_name})")
            item = shop_manager._load_item_details(conn, "software", sw_id)
            
            if item:
                logger.info(f"SUCCESS: Loaded item {item.name} (ID: {item.id})")
                if isinstance(item, SoftwareItem):
                    logger.info(f"  Type: SoftwareItem - {item.software_type}")
                    logger.info(f"  Description: {item.description[:50]}...")
                    logger.info(f"  Price: {item.price}")
                else:
                    logger.warning(f"  WRONG TYPE: Expected SoftwareItem but got {type(item)}")
            else:
                logger.error(f"FAILED: Could not load software item {sw_id}")
        
        # 3. Test loading food items
        logger.info("\n--- Testing Food Item Loading ---")
        cursor.execute("SELECT id, name FROM food_items")
        food_items = cursor.fetchall()
        
        for food_id, food_name in food_items:
            logger.info(f"Attempting to load food item: {food_id} ({food_name})")
            item = shop_manager._load_item_details(conn, "food", food_id)
            
            if item:
                logger.info(f"SUCCESS: Loaded item {item.name} (ID: {item.id})")
                if isinstance(item, FoodItem):
                    logger.info(f"  Type: FoodItem - {item.food_type}")
                    logger.info(f"  Description: {item.description[:50]}...")
                    logger.info(f"  Price: {item.price}")
                    logger.info(f"  Restore values - Health: {item.health_restore}, Energy: {item.energy_restore}, Mental: {item.mental_restore}")
                else:
                    logger.warning(f"  WRONG TYPE: Expected FoodItem but got {type(item)}")
            else:
                logger.error(f"FAILED: Could not load food item {food_id}")
                
        # 4. Test loading from shop inventory
        logger.info("\n--- Testing Shop Inventory Loading ---")
        cursor.execute("""
            SELECT si.shop_id, si.item_id, si.item_type, s.name 
            FROM shop_inventory si
            JOIN shops s ON si.shop_id = s.id
            WHERE (si.item_type = 'HARDWARE' OR si.item_type = 'SOFTWARE')
            LIMIT 5
        """)
        inventory_items = cursor.fetchall()
        
        for shop_id, item_id, item_type, shop_name in inventory_items:
            logger.info(f"Loading from shop '{shop_name}': {item_type} item {item_id}")
            item = shop_manager._load_item_details(conn, item_type, item_id)
            
            if item:
                logger.info(f"SUCCESS: Loaded {item_type} item {item.name} (ID: {item.id})")
                logger.info(f"  Item class: {item.__class__.__name__}")
                logger.info(f"  Description: {item.description[:50]}...")
                logger.info(f"  Price: {item.price}")
            else:
                logger.error(f"FAILED: Could not load {item_type} item {item_id}")
        
        conn.close()
        logger.info("Tests completed.")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)

if __name__ == "__main__":
    test_load_items()
