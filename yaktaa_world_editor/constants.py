
# constants.py

"""
Constantes pour la génération aléatoire de mondes pour YakTaa
Ce fichier contient toutes les constantes utilisées par le générateur de monde
"""

# Constantes pour la génération
CITY_PREFIXES = ["Neo-", "Cyber-", "Mega-", "Tech-", "Digi-", "Synth-", "Quantum-", "Hyper-"]
CITY_NAMES = ["Tokyo", "Shanghai", "New York", "Berlin", "London", "Paris", "Moscow", "Sydney", 
              "Seoul", "Mumbai", "Cairo", "Rio", "Lagos", "Singapore", "Dubai", "Bangkok"]

DISTRICT_TYPES = ["Financial", "Industrial", "Residential", "Entertainment", "Commercial", 
                 "Research", "Military", "Slums", "Underground", "Port", "Corporate"]

BUILDING_TYPES = [
    "Corporate HQ", "Apartment Complex", "Shopping Mall", "Research Lab", 
    "Data Center", "Hospital", "Police Station", "Nightclub", "Restaurant",
    "Hotel", "Factory", "Warehouse", "Government Building", "School", "University",
    "Military Base"
]

DEVICE_TYPES = [
    "Desktop PC", "Laptop", "Smartphone", "Tablet", "Server", 
    "Security System", "Smart Device", "Terminal", "ATM", "Router"
]

OS_TYPES = [
    "Windows 11", "Windows 10", "Linux Debian", "Linux Ubuntu", "Linux Kali",
    "macOS", "Android", "iOS", "Custom OS", "Legacy System"
]

# Constantes pour les réseaux et hacking
NETWORK_TYPES = [
    "WiFi", "LAN", "WAN", "VPN", "IoT", "Corporate", "Secured", "Public"
]

SECURITY_LEVELS = [
    "WEP", "WPA", "WPA2", "WPA3", "Enterprise", "None", "Custom"
]

ENCRYPTION_TYPES = [
    "None", "WEP", "TKIP", "AES-128", "AES-256", "Custom", "Military-Grade"
]

HACKING_PUZZLE_TYPES = [
    "PasswordBruteforce", "BufferOverflow", "SequenceMatching", 
    "NetworkRerouting", "BasicTerminal", "CodeInjection", "FirewallBypass"
]

HACKING_PUZZLE_DIFFICULTIES = [
    "Easy", "Medium", "Hard", "Expert", "Master"
]

FACTION_NAMES = ["NetRunners", "Corporate Security", "Street Gangs", "Hacktivists", 
                "Black Market", "Government Agents", "Mercenaries", "AI Collective", 
                "Resistance", "Cyber Cultists", "Tech Nomads", "Data Pirates"]

CHARACTER_ROLES = ["Hacker", "Corporate Executive", "Street Vendor", "Mercenary", "Doctor", 
                  "Engineer", "Journalist", "Smuggler", "Police Officer", "Bartender", 
                  "Fixer", "Information Broker", "Cyber Surgeon", "Tech Dealer", "Assassin"]

CHARACTER_PROFESSIONS = ["Hacker", "Security Specialist", "Programmer", "Engineer", "Corporate Executive", 
                         "Government Agent", "Police Officer", "Mercenary", "Smuggler", "Fixer", 
                         "Information Broker", "Journalist", "Doctor", "Bartender", "Street Vendor"]

FILE_TYPES = ["text", "document", "spreadsheet", "image", "audio", "video", 
             "executable", "archive", "database", "script", "log", "config"]

MISSION_TYPES = ["Hacking", "Retrieval", "Assassination", "Protection", "Infiltration", 
                "Escort", "Sabotage", "Investigation", "Delivery", "Heist", "Rescue"]

MISSION_DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert", "Legendary"]

OBJECTIVE_TYPES = ["Hack", "Retrieve", "Eliminate", "Protect", "Infiltrate", 
                  "Escort", "Sabotage", "Investigate", "Deliver", "Steal", "Rescue"]

STORY_ELEMENT_TYPES = ["Background", "Main Plot", "Side Plot", "Character Story", 
                      "Location History", "World Event", "Lore", "Faction Conflict"]

DIFFICULTY_LEVELS = [
    "Very Easy", "Easy", "Medium", "Hard", "Very Hard"
]

# Constantes pour les hardware et objets
HARDWARE_TYPES = [
    "CPU", "RAM", "GPU", "Motherboard", "HDD", "SSD", "Network Card", 
    "Cooling System", "Power Supply", "USB Drive", "External HDD",
    "Router", "Bluetooth Adapter", "WiFi Antenna", "Raspberry Pi"
]

HARDWARE_QUALITIES = [
    "Broken", "Poor", "Standard", "High-End", "Military-Grade", "Prototype", "Custom"
]

HARDWARE_RARITIES = [
    "Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"
]

CONSUMABLE_TYPES = [
    "Data Chip", "Neural Booster", "Code Fragment", "Crypto Key", 
    "Access Card", "Security Token", "Firewall Bypass", "Signal Jammer",
    "Decryption Tool", "Memory Cleaner", "Battery Pack", "FOOD"
]

# Constantes pour les boutiques
SHOP_TYPES = [
    "hardware", "software", "black_market", "consumables", 
    "weapons", "implants", "general", "electronics", 
    "digital_services", "datachips", "cybernetics"
]

SHOP_NAME_PREFIXES = [
    "Neo", "Cyber", "Digital", "Tech", "Quantum", "Synth", "Hyper", 
    "Mega", "Nano", "Net", "Data", "Pulse", "Virtual", "Chrome", "Holo"
]

SHOP_NAME_SUFFIXES = [
    "Shop", "Mart", "Market", "Store", "Hub", "Center", "Emporium", 
    "Outlet", "Depot", "Exchange", "Haven", "Corner", "Bazaar", "Bay"
]

SHOP_BRANDS = [
    "NeoCorp", "CyberTech", "QuantumByte", "SynthWare", "ChromeLogic", 
    "DataPulse", "NanoSystems", "VirtualEdge", "MegaByte", "NetDynamics", 
    "HyperLink", "DigiForge", "TechNexus", "PulseSoft", "ByteHaven"
]
