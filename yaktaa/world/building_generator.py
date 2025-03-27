"""
Module pour la génération procédurale de bâtiments dans YakTaa
Ce module contient les fonctions et classes nécessaires pour générer
des bâtiments et des structures urbaines de manière procédurale.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from yaktaa.world.locations import Location, WorldMap
from yaktaa.world.travel import Building, BuildingType, CityManager

logger = logging.getLogger("YakTaa.World.BuildingGenerator")

# Noms génériques pour les bâtiments
CORPORATE_NAMES = [
    "NeoTech", "CyberCorp", "Digitex", "SynthSys", "QuantumDyne",
    "VirtuCorp", "MegaSoft", "ByteWave", "NetSphere", "DataNex",
    "TechFusion", "CyberLink", "NeoCortex", "SiliconEdge", "QuantumPulse"
]

RESIDENTIAL_NAMES = [
    "Résidence Azure", "Tours Horizon", "Complexe Stellaire", "Jardins Suspendus",
    "Appartements Néo-Moderne", "Habitat Luxe", "Résidence Élysée",
    "Domaine Crystal", "Lofts Urbains", "Terrasses Célestes"
]

SHOP_NAMES = [
    "Cyber Marché", "Néo Bazaar", "Tech Boutique", "Implant Center",
    "Marché Noir", "Échange Digital", "Galerie Virtuelle", "Comptoir Quantique",
    "Arcade Commerciale", "Emporium Futuriste"
]

MEDICAL_NAMES = [
    "Clinique Cybernétique", "Hôpital Central", "Centre Médical Avancé",
    "Institut de Biotech", "Laboratoire Génétique", "Clinique d'Augmentation",
    "Centre de Soins Intégrés", "Hôpital Virtuel", "Complexe Médical Néo",
    "Clinique Régénération"
]

ENTERTAINMENT_NAMES = [
    "Club Néon", "Arène Virtuelle", "Casino Quantique", "Théâtre Holographique",
    "Bar Cyberpunk", "Lounge Digital", "Salle VR Premium", "Discothèque Laser",
    "Cinéma Immersif", "Centre de Divertissement Futuriste"
]

GOVERNMENT_NAMES = [
    "Centre Administratif", "Complexe Gouvernemental", "Ministère de la Sécurité",
    "Bureau Central", "Département de Contrôle", "Agence de Régulation",
    "Quartier Général", "Palais de Justice", "Centre de Surveillance",
    "Administration Municipale"
]

SECURITY_NAMES = [
    "Poste de Police", "Centre de Sécurité", "Quartier Général des Forces",
    "Tour de Contrôle", "Complexe Militaire", "Centre de Défense",
    "Bunker Sécurisé", "Poste de Garde", "Centre d'Opérations",
    "Base de Sécurité Corporative"
]

EDUCATIONAL_NAMES = [
    "Académie Technique", "Université Virtuelle", "Institut de Recherche",
    "Centre d'Apprentissage", "École de Hacking", "Bibliothèque Numérique",
    "Campus Scientifique", "Centre de Formation", "Laboratoire Éducatif",
    "Conservatoire Digital"
]

# Descriptions génériques pour les bâtiments
BUILDING_DESCRIPTIONS = {
    BuildingType.RESIDENTIAL: [
        "Un complexe résidentiel moderne avec des appartements de différentes tailles.",
        "Une tour d'habitation luxueuse avec vue panoramique sur la ville.",
        "Un ensemble d'appartements abordables pour la classe moyenne.",
        "Un immeuble résidentiel sécurisé avec contrôle d'accès avancé.",
        "Un complexe d'habitations modulaires avec jardins suspendus."
    ],
    BuildingType.COMMERCIAL: [
        "Un centre commercial animé proposant une variété de boutiques et services.",
        "Un marché couvert où se mêlent vendeurs légitimes et marché noir.",
        "Une galerie marchande high-tech avec les dernières innovations.",
        "Un bazar cyberpunk où l'on trouve de tout, du légal à l'illégal.",
        "Un complexe commercial avec boutiques, restaurants et divertissements."
    ],
    BuildingType.CORPORATE: [
        "Un gratte-ciel imposant abritant le siège d'une mégacorporation.",
        "Un complexe de bureaux ultramoderne avec sécurité renforcée.",
        "Une tour corporative aux vitres teintées cachant des secrets bien gardés.",
        "Un bâtiment d'entreprise à l'architecture futuriste et intimidante.",
        "Un centre d'affaires abritant plusieurs filiales corporatives."
    ],
    BuildingType.MEDICAL: [
        "Un hôpital de pointe offrant des soins médicaux et augmentations cybernétiques.",
        "Une clinique spécialisée dans les implants et modifications corporelles.",
        "Un centre médical combinant médecine traditionnelle et technologies avancées.",
        "Un laboratoire de recherche médicale travaillant sur des traitements expérimentaux.",
        "Un complexe hospitalier avec différents départements spécialisés."
    ],
    BuildingType.ENTERTAINMENT: [
        "Un club nocturne populaire avec musique, danse et divertissements variés.",
        "Un casino high-tech proposant jeux traditionnels et expériences virtuelles.",
        "Un centre de réalité virtuelle offrant des simulations immersives.",
        "Un complexe de divertissement avec cinémas, restaurants et arcades.",
        "Une arène de jeux où se déroulent compétitions et spectacles."
    ],
    BuildingType.GOVERNMENT: [
        "Un bâtiment administratif gérant les affaires de la ville.",
        "Un centre gouvernemental fortement sécurisé et surveillé.",
        "Un complexe abritant divers services publics et administratifs.",
        "Un imposant édifice symbolisant l'autorité et le pouvoir en place.",
        "Un bâtiment officiel où sont prises les décisions politiques locales."
    ],
    BuildingType.SECURITY: [
        "Un poste de police équipé des dernières technologies de surveillance.",
        "Un centre de sécurité coordonnant les forces de l'ordre de la zone.",
        "Une base militaire ou paramilitaire avec équipement de pointe.",
        "Un bâtiment de sécurité privée protégeant les intérêts corporatifs.",
        "Un complexe de défense avec systèmes de sécurité avancés."
    ],
    BuildingType.EDUCATIONAL: [
        "Une académie formant aux technologies et compétences modernes.",
        "Un campus universitaire combinant enseignement traditionnel et virtuel.",
        "Un centre de recherche travaillant sur des projets innovants.",
        "Une bibliothèque numérique stockant d'immenses quantités de données.",
        "Un institut spécialisé dans un domaine technologique particulier."
    ],
    BuildingType.INDUSTRIAL: [
        "Une usine automatisée produisant des composants électroniques.",
        "Un complexe industriel avec chaînes de montage et entrepôts.",
        "Un centre de production d'implants cybernétiques et de prothèses.",
        "Une zone industrielle polluée abritant diverses manufactures.",
        "Un site de fabrication high-tech avec robots et IA de production."
    ],
    BuildingType.UNDERGROUND: [
        "Un bunker souterrain servant de refuge ou de base d'opérations.",
        "Un réseau de tunnels abritant un marché noir clandestin.",
        "Un complexe souterrain caché aux yeux des autorités.",
        "Une ancienne station de métro reconvertie en zone de commerce.",
        "Un laboratoire secret menant des expériences interdites."
    ]
}

# Noms génériques pour les pièces
ROOM_NAMES = {
    BuildingType.RESIDENTIAL: [
        "Salon", "Chambre", "Cuisine", "Salle de bain", "Bureau",
        "Balcon", "Salle à manger", "Vestibule", "Débarras", "Terrasse"
    ],
    BuildingType.COMMERCIAL: [
        "Boutique", "Entrepôt", "Salle d'exposition", "Comptoir", "Bureau de gérance",
        "Zone de stockage", "Espace clients", "Salle de réunion", "Cafétéria", "Salle de pause"
    ],
    BuildingType.CORPORATE: [
        "Bureau exécutif", "Salle de conférence", "Open space", "Laboratoire R&D", "Salle des serveurs",
        "Cafétéria", "Salle de sécurité", "Réception", "Archives", "Salle de repos"
    ],
    BuildingType.MEDICAL: [
        "Salle d'opération", "Laboratoire", "Salle d'examen", "Pharmacie", "Salle de récupération",
        "Bureau médical", "Salle d'attente", "Unité de soins intensifs", "Morgue", "Salle de stérilisation"
    ],
    BuildingType.ENTERTAINMENT: [
        "Piste de danse", "Bar", "Lounge VIP", "Salle de jeux", "Scène",
        "Cabines privées", "Salle de projection", "Zone VR", "Vestiaires", "Cuisine"
    ],
    BuildingType.GOVERNMENT: [
        "Bureau administratif", "Salle d'audience", "Archives", "Salle de réunion", "Bureau du directeur",
        "Réception", "Salle de contrôle", "Centre de communication", "Salle de conférence", "Cafétéria"
    ],
    BuildingType.SECURITY: [
        "Salle de contrôle", "Armurerie", "Cellules", "Bureau du chef", "Salle d'interrogatoire",
        "Vestiaires", "Salle de briefing", "Garage", "Centre de communication", "Salle de formation"
    ],
    BuildingType.EDUCATIONAL: [
        "Salle de classe", "Laboratoire", "Bibliothèque", "Bureau professoral", "Amphithéâtre",
        "Salle d'étude", "Cafétéria", "Salle informatique", "Centre de recherche", "Administration"
    ],
    BuildingType.INDUSTRIAL: [
        "Chaîne de montage", "Entrepôt", "Salle de contrôle", "Laboratoire", "Bureau de supervision",
        "Zone de chargement", "Atelier", "Salle des machines", "Stockage de matériaux", "Vestiaires"
    ],
    BuildingType.UNDERGROUND: [
        "Tunnel", "Salle commune", "Entrepôt", "Quartiers privés", "Poste de garde",
        "Salle des générateurs", "Réserve", "Infirmerie", "Salle de communication", "Armurerie"
    ]
}


class BuildingGenerator:
    """
    Générateur procédural de bâtiments pour YakTaa
    """
    
    def __init__(self, city_manager: CityManager):
        """Initialise le générateur de bâtiments"""
        self.city_manager = city_manager
        self.world_map = city_manager.world_map
        self.building_counter = 0
        
        logger.info("Générateur de bâtiments initialisé")
    
    def generate_building(self, location_id: str, building_type: BuildingType = None) -> Optional[Building]:
        """
        Génère un bâtiment procédural dans un lieu spécifique
        
        Args:
            location_id: ID du lieu où générer le bâtiment
            building_type: Type de bâtiment à générer (aléatoire si None)
            
        Returns:
            Le bâtiment généré, ou None en cas d'échec
        """
        location = self.world_map.get_location(location_id)
        if not location:
            logger.warning(f"Impossible de générer un bâtiment: lieu {location_id} introuvable")
            return None
        
        # Déterminer le type de bâtiment si non spécifié
        if building_type is None:
            building_type = random.choice(list(BuildingType))
        
        # Générer un ID unique
        self.building_counter += 1
        building_id = f"building_{location_id}_{building_type.name.lower()}_{self.building_counter}"
        
        # Générer un nom en fonction du type
        name = self._generate_building_name(building_type)
        
        # Générer une description
        description = random.choice(BUILDING_DESCRIPTIONS.get(building_type, ["Un bâtiment ordinaire."]))
        
        # Déterminer le nombre d'étages en fonction du type
        floors = self._determine_floors(building_type)
        
        # Déterminer le niveau de sécurité
        security_level = self._determine_security_level(building_type, location)
        
        # Déterminer les services disponibles
        services = self._determine_services(building_type)
        
        # Déterminer les tags
        tags = [building_type.name.lower()] + self._determine_tags(building_type)
        
        # Déterminer si le bâtiment nécessite un accès spécial
        requires_special_access = random.random() < 0.2
        requires_hacking = random.random() < 0.15
        
        # Créer le bâtiment
        building = Building(
            id=building_id,
            name=name,
            description=description,
            building_type=building_type,
            security_level=security_level,
            floors=floors,
            owner=self._generate_owner(building_type),
            services=services,
            tags=tags,
            parent_location_id=location_id,
            is_accessible=not requires_special_access,
            requires_hacking=requires_hacking,
            requires_special_access=requires_special_access
        )
        
        # Générer des pièces pour le bâtiment
        self._generate_rooms(building)
        
        # Ajouter le bâtiment au gestionnaire de villes
        if self.city_manager.add_building(building):
            logger.info(f"Bâtiment généré avec succès: {name} ({building_id})")
            return building
        else:
            logger.warning(f"Échec de l'ajout du bâtiment {name} au gestionnaire de villes")
            return None
    
    def _generate_building_name(self, building_type: BuildingType) -> str:
        """Génère un nom pour un bâtiment en fonction de son type"""
        if building_type == BuildingType.RESIDENTIAL:
            return random.choice(RESIDENTIAL_NAMES)
        elif building_type == BuildingType.COMMERCIAL:
            return random.choice(SHOP_NAMES)
        elif building_type == BuildingType.CORPORATE:
            return random.choice(CORPORATE_NAMES) + " " + random.choice(["Inc.", "Corp.", "Technologies", "Systems", "Industries"])
        elif building_type == BuildingType.MEDICAL:
            return random.choice(MEDICAL_NAMES)
        elif building_type == BuildingType.ENTERTAINMENT:
            return random.choice(ENTERTAINMENT_NAMES)
        elif building_type == BuildingType.GOVERNMENT:
            return random.choice(GOVERNMENT_NAMES)
        elif building_type == BuildingType.SECURITY:
            return random.choice(SECURITY_NAMES)
        elif building_type == BuildingType.EDUCATIONAL:
            return random.choice(EDUCATIONAL_NAMES)
        elif building_type == BuildingType.INDUSTRIAL:
            return random.choice(CORPORATE_NAMES) + " " + random.choice(["Industries", "Manufacturing", "Production", "Factory", "Works"])
        elif building_type == BuildingType.UNDERGROUND:
            return random.choice(["Le Bunker", "Souterrain", "Catacombes", "L'Abri", "Tunnels", "La Tanière", "Refuge"]) + " " + random.choice(["Secret", "Caché", "Oublié", "Interdit", "Clandestin"])
        else:
            return "Bâtiment " + str(random.randint(1000, 9999))
    
    def _determine_floors(self, building_type: BuildingType) -> int:
        """Détermine le nombre d'étages en fonction du type de bâtiment"""
        if building_type == BuildingType.RESIDENTIAL:
            return random.randint(5, 30)
        elif building_type == BuildingType.COMMERCIAL:
            return random.randint(1, 5)
        elif building_type == BuildingType.CORPORATE:
            return random.randint(20, 100)
        elif building_type == BuildingType.MEDICAL:
            return random.randint(3, 15)
        elif building_type == BuildingType.ENTERTAINMENT:
            return random.randint(1, 5)
        elif building_type == BuildingType.GOVERNMENT:
            return random.randint(3, 20)
        elif building_type == BuildingType.SECURITY:
            return random.randint(1, 10)
        elif building_type == BuildingType.EDUCATIONAL:
            return random.randint(2, 10)
        elif building_type == BuildingType.INDUSTRIAL:
            return random.randint(1, 5)
        elif building_type == BuildingType.UNDERGROUND:
            return random.randint(1, 5)  # Niveaux souterrains
        else:
            return random.randint(1, 10)
    
    def _determine_security_level(self, building_type: BuildingType, location: Location) -> int:
        """Détermine le niveau de sécurité en fonction du type de bâtiment et du lieu"""
        base_security = location.security_level
        
        if building_type == BuildingType.RESIDENTIAL:
            return max(1, min(10, base_security + random.randint(-1, 1)))
        elif building_type == BuildingType.COMMERCIAL:
            return max(1, min(10, base_security + random.randint(-1, 1)))
        elif building_type == BuildingType.CORPORATE:
            return max(1, min(10, base_security + random.randint(1, 3)))
        elif building_type == BuildingType.MEDICAL:
            return max(1, min(10, base_security + random.randint(0, 2)))
        elif building_type == BuildingType.ENTERTAINMENT:
            return max(1, min(10, base_security + random.randint(-2, 1)))
        elif building_type == BuildingType.GOVERNMENT:
            return max(1, min(10, base_security + random.randint(2, 4)))
        elif building_type == BuildingType.SECURITY:
            return max(1, min(10, base_security + random.randint(3, 5)))
        elif building_type == BuildingType.EDUCATIONAL:
            return max(1, min(10, base_security + random.randint(-1, 1)))
        elif building_type == BuildingType.INDUSTRIAL:
            return max(1, min(10, base_security + random.randint(0, 2)))
        elif building_type == BuildingType.UNDERGROUND:
            return max(1, min(10, base_security + random.randint(-3, 3)))
        else:
            return max(1, min(10, base_security))
    
    def _determine_services(self, building_type: BuildingType) -> List[str]:
        """Détermine les services disponibles en fonction du type de bâtiment"""
        services = []
        
        if building_type == BuildingType.RESIDENTIAL:
            possible_services = ["logement", "sécurité", "maintenance", "divertissement", "restauration"]
            services = random.sample(possible_services, random.randint(1, 3))
        elif building_type == BuildingType.COMMERCIAL:
            possible_services = ["vente", "réparation", "personnalisation", "échange", "information", "restauration"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.CORPORATE:
            possible_services = ["finance", "technologie", "sécurité", "recherche", "développement", "administration"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.MEDICAL:
            possible_services = ["soins", "chirurgie", "implants", "pharmacie", "réhabilitation", "diagnostic"]
            services = random.sample(possible_services, random.randint(2, 5))
        elif building_type == BuildingType.ENTERTAINMENT:
            possible_services = ["divertissement", "restauration", "boissons", "jeux", "spectacles", "réalité virtuelle"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.GOVERNMENT:
            possible_services = ["administration", "sécurité", "justice", "régulation", "surveillance", "information"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.SECURITY:
            possible_services = ["sécurité", "détention", "surveillance", "formation", "armement", "investigation"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.EDUCATIONAL:
            possible_services = ["éducation", "recherche", "information", "formation", "certification", "bibliothèque"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.INDUSTRIAL:
            possible_services = ["production", "assemblage", "stockage", "distribution", "maintenance", "recyclage"]
            services = random.sample(possible_services, random.randint(2, 4))
        elif building_type == BuildingType.UNDERGROUND:
            possible_services = ["marché noir", "refuge", "information", "contrebande", "réparation", "trafic"]
            services = random.sample(possible_services, random.randint(1, 3))
        
        return services
    
    def _determine_tags(self, building_type: BuildingType) -> List[str]:
        """Détermine les tags en fonction du type de bâtiment"""
        tags = []
        
        # Tags communs à tous les types
        common_tags = ["urbain", "moderne", "cyberpunk"]
        tags.append(random.choice(common_tags))
        
        # Tags spécifiques au type
        if building_type == BuildingType.RESIDENTIAL:
            specific_tags = ["habitation", "appartements", "logement", "domicile"]
        elif building_type == BuildingType.COMMERCIAL:
            specific_tags = ["commerce", "boutique", "marché", "vente"]
        elif building_type == BuildingType.CORPORATE:
            specific_tags = ["entreprise", "affaires", "bureau", "corporation"]
        elif building_type == BuildingType.MEDICAL:
            specific_tags = ["santé", "médical", "soins", "clinique", "hôpital"]
        elif building_type == BuildingType.ENTERTAINMENT:
            specific_tags = ["divertissement", "loisirs", "club", "bar", "casino"]
        elif building_type == BuildingType.GOVERNMENT:
            specific_tags = ["gouvernement", "administration", "officiel", "autorité"]
        elif building_type == BuildingType.SECURITY:
            specific_tags = ["sécurité", "police", "militaire", "surveillance"]
        elif building_type == BuildingType.EDUCATIONAL:
            specific_tags = ["éducation", "académique", "recherche", "formation"]
        elif building_type == BuildingType.INDUSTRIAL:
            specific_tags = ["industrie", "production", "usine", "manufacture"]
        elif building_type == BuildingType.UNDERGROUND:
            specific_tags = ["souterrain", "caché", "secret", "clandestin"]
        else:
            specific_tags = []
        
        if specific_tags:
            tags.append(random.choice(specific_tags))
        
        # Ajouter un tag aléatoire de qualité
        quality_tags = ["luxe", "standard", "délabré", "high-tech", "rétro", "abandonné", "rénové", "sécurisé"]
        tags.append(random.choice(quality_tags))
        
        return tags
    
    def _generate_owner(self, building_type: BuildingType) -> str:
        """Génère un propriétaire pour le bâtiment"""
        if building_type == BuildingType.CORPORATE:
            return random.choice(CORPORATE_NAMES)
        elif building_type == BuildingType.GOVERNMENT:
            return "Gouvernement"
        elif building_type == BuildingType.SECURITY:
            if random.random() < 0.5:
                return "Forces de l'ordre"
            else:
                return random.choice(CORPORATE_NAMES) + " Security"
        elif building_type == BuildingType.EDUCATIONAL:
            return "Institution Académique"
        else:
            if random.random() < 0.3:
                return random.choice(CORPORATE_NAMES)
            elif random.random() < 0.5:
                return "Propriétaire privé"
            else:
                return "Inconnu"
    
    def _generate_rooms(self, building: Building) -> None:
        """Génère des pièces pour un bâtiment"""
        # Déterminer le nombre de pièces par étage
        rooms_per_floor = random.randint(2, 6)
        
        # Générer des pièces pour chaque étage
        for floor in range(1, building.floors + 1):
            for i in range(rooms_per_floor):
                room_id = f"{building.id}_floor{floor}_room{i+1}"
                
                # Sélectionner un nom de pièce en fonction du type de bâtiment
                room_names = ROOM_NAMES.get(building.building_type, ["Pièce"])
                room_name = random.choice(room_names)
                
                # Déterminer si la pièce nécessite du hacking (plus probable aux étages supérieurs)
                requires_hacking = random.random() < (0.05 + (floor / building.floors) * 0.2)
                
                # Ajouter la pièce au bâtiment
                building.add_room(
                    room_id=room_id,
                    name=room_name,
                    floor=floor,
                    description=f"{room_name} au {floor}e étage de {building.name}.",
                    is_accessible=random.random() > 0.1,  # 10% de chance d'être inaccessible
                    requires_hacking=requires_hacking
                )
        
        logger.info(f"Généré {rooms_per_floor * building.floors} pièces pour le bâtiment {building.name}")


def populate_location_with_buildings(city_manager: CityManager, location_id: str, num_buildings: int = 10) -> List[Building]:
    """
    Peuple un lieu avec des bâtiments générés procéduralement
    
    Args:
        city_manager: Gestionnaire de villes
        location_id: ID du lieu à peupler
        num_buildings: Nombre de bâtiments à générer
        
    Returns:
        Liste des bâtiments générés
    """
    generator = BuildingGenerator(city_manager)
    buildings = []
    
    # Déterminer la distribution des types de bâtiments
    building_types = list(BuildingType)
    weights = [
        0.2,  # RESIDENTIAL
        0.15,  # COMMERCIAL
        0.1,   # INDUSTRIAL
        0.1,   # GOVERNMENT
        0.15,  # CORPORATE
        0.05,  # MEDICAL
        0.1,   # EDUCATIONAL
        0.1,   # ENTERTAINMENT
        0.03,  # SECURITY
        0.02   # UNDERGROUND
    ]
    
    for _ in range(num_buildings):
        building_type = random.choices(building_types, weights=weights, k=1)[0]
        building = generator.generate_building(location_id, building_type)
        if building:
            buildings.append(building)
    
    logger.info(f"Lieu {location_id} peuplé avec {len(buildings)} bâtiments")
    return buildings
