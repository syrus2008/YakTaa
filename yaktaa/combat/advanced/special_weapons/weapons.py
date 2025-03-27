"""
Catalogue d'armes spéciales pour le système de combat avancé
"""

import logging
from typing import Dict, List, Any
from .core import SpecialWeaponSystem, SpecialWeaponType, SpecialWeaponRarity

logger = logging.getLogger("YakTaa.Combat.Advanced.SpecialWeapons.Weapons")

def initialize_special_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """
    Initialise le catalogue d'armes spéciales
    
    Args:
        weapon_system: Le système d'armes spéciales
    """
    # Enregistrer toutes les armes spéciales
    _register_energy_weapons(weapon_system)
    _register_melee_weapons(weapon_system)
    _register_projectile_weapons(weapon_system)
    _register_tech_weapons(weapon_system)
    _register_experimental_weapons(weapon_system)
    
    logger.info(f"Catalogue d'armes spéciales initialisé avec {len(weapon_system.weapons_catalog)} armes")

def _register_energy_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """Enregistre les armes à énergie"""
    
    # Nova Blaster
    nova_blaster = {
        "id": "nova_blaster",
        "name": "Nova Blaster",
        "description": "Pistolet à énergie qui accumule de la charge et peut libérer une explosion dévastatrice",
        "type": SpecialWeaponType.ENERGY,
        "rarity": SpecialWeaponRarity.RARE,
        "base_damage": 25,
        "damage_type": "ENERGY",
        "range": 15,
        "accuracy": 0.8,
        "max_charge": 100,
        "charge_rate": 10,  # Points de charge par tir
        "durability": 100,
        "effects": [
            {
                "id": "energy_burst",
                "name": "Décharge d'énergie",
                "description": "Libère une puissante décharge d'énergie",
                "category": "damage",
                "damage": 50,
                "damage_multiplier": 1.0,
                "damage_type": "ENERGY",
                "max_targets": 1,
                "trigger_conditions": {
                    "min_charge": 50,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 50
                },
                "cooldown": 3,
                "duration": 1
            },
            {
                "id": "nova_explosion",
                "name": "Explosion Nova",
                "description": "Crée une explosion d'énergie qui affecte tous les ennemis à proximité",
                "category": "damage",
                "damage": 40,
                "damage_multiplier": 1.2,
                "damage_type": "ENERGY",
                "max_targets": 5,
                "aoe_radius": 5,
                "trigger_conditions": {
                    "min_charge": 100,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 100,
                    "durability": 5
                },
                "cooldown": 6,
                "duration": 1
            }
        ],
        "evolution_paths": [
            {
                "id": "improved_capacitors",
                "name": "Condensateurs améliorés",
                "description": "Augmente la charge maximale",
                "level_requirement": 3,
                "effects": {
                    "max_charge": 150,
                    "charge_rate": 15
                }
            },
            {
                "id": "focused_emitter",
                "name": "Émetteur focalisé",
                "description": "Augmente les dégâts et la précision",
                "level_requirement": 6,
                "effects": {
                    "base_damage": 35,
                    "accuracy": 0.9
                }
            },
            {
                "id": "overcharge_module",
                "name": "Module de surcharge",
                "description": "Permet d'accumuler plus de charge pour des effets plus puissants",
                "level_requirement": 9,
                "effects": {
                    "max_charge": 200,
                    "new_effect": {
                        "id": "overcharge_beam",
                        "name": "Rayon de surcharge",
                        "description": "Tire un rayon concentré qui inflige d'énormes dégâts",
                        "category": "damage",
                        "damage": 120,
                        "damage_multiplier": 1.5,
                        "damage_type": "ENERGY",
                        "armor_penetration": 0.3,
                        "max_targets": 1,
                        "trigger_conditions": {
                            "min_charge": 200,
                            "trigger_chance": 1.0
                        },
                        "costs": {
                            "charge": 200,
                            "durability": 10
                        },
                        "cooldown": 10,
                        "duration": 1
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(nova_blaster)
    
    # Plasma Repeater
    plasma_repeater = {
        "id": "plasma_repeater",
        "name": "Répéteur à plasma",
        "description": "Fusil automatique qui tire des projectiles de plasma à cadence élevée",
        "type": SpecialWeaponType.ENERGY,
        "rarity": SpecialWeaponRarity.UNCOMMON,
        "base_damage": 15,
        "damage_type": "ENERGY",
        "range": 20,
        "accuracy": 0.75,
        "max_charge": 100,
        "charge_rate": 5,  # Points de charge par tir
        "durability": 120,
        "effects": [
            {
                "id": "rapid_fire",
                "name": "Tir rapide",
                "description": "Tire une rafale rapide de projectiles plasma",
                "category": "damage",
                "damage": 10,
                "damage_multiplier": 0.8,
                "damage_type": "ENERGY",
                "max_targets": 1,
                "hits": 5,  # Nombre de projectiles
                "trigger_conditions": {
                    "min_charge": 30,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 30
                },
                "cooldown": 4,
                "duration": 1
            },
            {
                "id": "plasma_field",
                "name": "Champ de plasma",
                "description": "Crée un champ de plasma qui inflige des dégâts au fil du temps",
                "category": "status",
                "status_type": "PLASMA_BURN",
                "status_duration": 3,
                "status_strength": 2,
                "application_chance": 0.8,
                "max_targets": 3,
                "aoe_radius": 3,
                "trigger_conditions": {
                    "min_charge": 60,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 60,
                    "durability": 3
                },
                "cooldown": 5,
                "duration": 3
            }
        ],
        "evolution_paths": [
            {
                "id": "extended_barrel",
                "name": "Canon allongé",
                "description": "Augmente la portée et la précision",
                "level_requirement": 3,
                "effects": {
                    "range": 25,
                    "accuracy": 0.85
                }
            },
            {
                "id": "plasma_accelerator",
                "name": "Accélérateur de plasma",
                "description": "Augmente les dégâts des projectiles plasma",
                "level_requirement": 6,
                "effects": {
                    "base_damage": 20,
                    "effects": {
                        "rapid_fire": {
                            "damage": 15
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(plasma_repeater)
    
    # Void Lance
    void_lance = {
        "id": "void_lance",
        "name": "Lance du Néant",
        "description": "Lance d'énergie qui puise dans le vide quantique pour déchirer la réalité",
        "type": SpecialWeaponType.ENERGY,
        "rarity": SpecialWeaponRarity.EPIC,
        "base_damage": 40,
        "damage_type": "ENERGY",
        "range": 12,
        "accuracy": 0.9,
        "max_charge": 100,
        "charge_rate": 5,
        "durability": 80,
        "effects": [
            {
                "id": "void_pierce",
                "name": "Perforation du Néant",
                "description": "Transperce les ennemis avec une lance d'énergie du vide",
                "category": "damage",
                "damage": 65,
                "damage_multiplier": 1.0,
                "damage_type": "ENERGY",
                "armor_penetration": 0.5,
                "max_targets": 3,  # Peut traverser plusieurs ennemis
                "trigger_conditions": {
                    "min_charge": 50,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 50,
                    "durability": 2
                },
                "cooldown": 4,
                "duration": 1
            },
            {
                "id": "reality_tear",
                "name": "Déchirure de Réalité",
                "description": "Crée une fissure dans l'espace qui aspire les ennemis et les endommage",
                "category": "damage",
                "damage": 30,
                "damage_multiplier": 1.5,
                "damage_type": "ENERGY",
                "max_targets": 5,
                "aoe_radius": 4,
                "trigger_conditions": {
                    "min_charge": 100,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 100,
                    "durability": 5
                },
                "cooldown": 8,
                "duration": 2
            }
        ],
        "evolution_paths": [
            {
                "id": "void_attunement",
                "name": "Harmonisation au Néant",
                "description": "Améliore la connexion avec le vide quantique",
                "level_requirement": 5,
                "effects": {
                    "base_damage": 50,
                    "effects": {
                        "void_pierce": {
                            "damage": 80,
                            "armor_penetration": 0.6
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(void_lance)

def _register_melee_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """Enregistre les armes de corps à corps"""
    
    # Quantum Blade
    quantum_blade = {
        "id": "quantum_blade",
        "name": "Lame Quantique",
        "description": "Épée qui oscille entre différentes phases quantiques, ignorant partiellement les armures",
        "type": SpecialWeaponType.MELEE,
        "rarity": SpecialWeaponRarity.EPIC,
        "base_damage": 35,
        "damage_type": "PHYSICAL",
        "range": 2,
        "durability": 100,
        "effects": [
            {
                "id": "phase_strike",
                "name": "Frappe Phasique",
                "description": "Attaque qui traverse partiellement les armures et boucliers",
                "category": "damage",
                "damage": 45,
                "damage_multiplier": 1.2,
                "damage_type": "PHYSICAL",
                "armor_penetration": 0.7,
                "max_targets": 1,
                "trigger_conditions": {
                    "trigger_chance": 0.3,  # 30% de chance à chaque coup
                    "cooldown_ready": True
                },
                "cooldown": 3,
                "duration": 1
            },
            {
                "id": "quantum_shift",
                "name": "Décalage Quantique",
                "description": "Téléporte le joueur derrière sa cible pour une attaque surprise",
                "category": "utility",
                "utility_type": "TELEPORT",
                "direction": "BEHIND_TARGET",
                "distance": 3,
                "followed_by": {
                    "category": "damage",
                    "damage": 60,
                    "damage_multiplier": 1.5,
                    "damage_type": "PHYSICAL",
                    "critical_chance_bonus": 0.5
                },
                "trigger_conditions": {
                    "trigger_chance": 1.0,
                    "cooldown_ready": True
                },
                "costs": {
                    "durability": 3
                },
                "cooldown": 6,
                "duration": 1
            }
        ],
        "evolution_paths": [
            {
                "id": "superposition_edge",
                "name": "Tranchant en Superposition",
                "description": "La lame existe dans plusieurs états quantiques simultanément",
                "level_requirement": 4,
                "effects": {
                    "base_damage": 45,
                    "effects": {
                        "phase_strike": {
                            "trigger_chance": 0.4,
                            "armor_penetration": 0.8
                        }
                    }
                }
            },
            {
                "id": "quantum_entanglement",
                "name": "Intrication Quantique",
                "description": "Les frappes peuvent affecter plusieurs cibles intriquées",
                "level_requirement": 8,
                "effects": {
                    "new_effect": {
                        "id": "entangled_slash",
                        "name": "Entaille Intriquée",
                        "description": "Frappe jusqu'à 3 ennemis proches en même temps",
                        "category": "damage",
                        "damage": 40,
                        "damage_multiplier": 1.0,
                        "damage_type": "PHYSICAL",
                        "armor_penetration": 0.5,
                        "max_targets": 3,
                        "aoe_radius": 4,
                        "trigger_conditions": {
                            "trigger_chance": 1.0,
                            "cooldown_ready": True
                        },
                        "costs": {
                            "durability": 4
                        },
                        "cooldown": 7,
                        "duration": 1
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(quantum_blade)
    
    # Graviton Hammer
    graviton_hammer = {
        "id": "graviton_hammer",
        "name": "Marteau Gravitonique",
        "description": "Massue qui manipule la gravité, créant des ondes de choc et attirant les ennemis",
        "type": SpecialWeaponType.MELEE,
        "rarity": SpecialWeaponRarity.RARE,
        "base_damage": 50,
        "damage_type": "PHYSICAL",
        "range": 3,
        "durability": 150,
        "effects": [
            {
                "id": "gravity_slam",
                "name": "Frappe Gravitationnelle",
                "description": "Frappe le sol pour créer une onde de choc qui endommage et repousse les ennemis",
                "category": "damage",
                "damage": 60,
                "damage_multiplier": 1.2,
                "damage_type": "PHYSICAL",
                "max_targets": 5,
                "aoe_radius": 5,
                "knockback": 3,
                "trigger_conditions": {
                    "trigger_chance": 1.0,
                    "cooldown_ready": True
                },
                "costs": {
                    "durability": 2
                },
                "cooldown": 5,
                "duration": 1
            },
            {
                "id": "gravity_pull",
                "name": "Attraction Gravitationnelle",
                "description": "Attire les ennemis proches vers le joueur pour les frapper",
                "category": "utility",
                "utility_type": "PULL",
                "pull_strength": 5,
                "max_targets": 3,
                "aoe_radius": 7,
                "followed_by": {
                    "category": "damage",
                    "damage": 40,
                    "damage_multiplier": 1.0,
                    "damage_type": "PHYSICAL",
                    "max_targets": 3
                },
                "trigger_conditions": {
                    "trigger_chance": 1.0,
                    "cooldown_ready": True
                },
                "costs": {
                    "durability": 3
                },
                "cooldown": 7,
                "duration": 1
            }
        ],
        "evolution_paths": [
            {
                "id": "increased_mass",
                "name": "Masse Augmentée",
                "description": "Augmente la masse du marteau pour des frappes plus puissantes",
                "level_requirement": 3,
                "effects": {
                    "base_damage": 60,
                    "effects": {
                        "gravity_slam": {
                            "damage": 75,
                            "knockback": 4
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(graviton_hammer)

def _register_projectile_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """Enregistre les armes à projectiles"""
    
    # Nanite Pistol
    nanite_pistol = {
        "id": "nanite_pistol",
        "name": "Pistolet à Nanites",
        "description": "Tire des projectiles contenant des nanites qui continuent d'infliger des dégâts au fil du temps",
        "type": SpecialWeaponType.PROJECTILE,
        "rarity": SpecialWeaponRarity.RARE,
        "base_damage": 20,
        "damage_type": "PHYSICAL",
        "range": 18,
        "accuracy": 0.85,
        "max_charge": 100,
        "charge_rate": 10,
        "durability": 100,
        "effects": [
            {
                "id": "nanite_swarm",
                "name": "Essaim de Nanites",
                "description": "Injecte des nanites qui dévorent la cible de l'intérieur",
                "category": "status",
                "status_type": "NANITE_INFECTION",
                "status_duration": 5,
                "status_strength": 3,
                "application_chance": 0.75,
                "max_targets": 1,
                "trigger_conditions": {
                    "min_charge": 40,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 40
                },
                "cooldown": 4,
                "duration": 5
            },
            {
                "id": "nanite_explosion",
                "name": "Explosion de Nanites",
                "description": "Les nanites se répandent et explosent, infligeant des dégâts aux ennemis proches",
                "category": "damage",
                "damage": 35,
                "damage_multiplier": 1.0,
                "damage_type": "PHYSICAL",
                "max_targets": 4,
                "aoe_radius": 4,
                "trigger_conditions": {
                    "min_charge": 80,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 80,
                    "durability": 3
                },
                "cooldown": 6,
                "duration": 1
            }
        ],
        "evolution_paths": [
            {
                "id": "enhanced_nanites",
                "name": "Nanites Améliorées",
                "description": "Les nanites sont plus efficaces et causent plus de dégâts",
                "level_requirement": 4,
                "effects": {
                    "base_damage": 25,
                    "effects": {
                        "nanite_swarm": {
                            "status_strength": 5,
                            "status_duration": 6
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(nanite_pistol)

def _register_tech_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """Enregistre les armes technologiques"""
    
    # EMP Coilgun
    emp_coilgun = {
        "id": "emp_coilgun",
        "name": "Fusil à Bobine EMP",
        "description": "Tire des impulsions électromagnétiques qui désactivent temporairement les appareils électroniques et implants",
        "type": SpecialWeaponType.TECH,
        "rarity": SpecialWeaponRarity.RARE,
        "base_damage": 15,
        "damage_type": "EMP",
        "range": 22,
        "accuracy": 0.8,
        "max_charge": 100,
        "charge_rate": 15,
        "durability": 90,
        "effects": [
            {
                "id": "system_shutdown",
                "name": "Arrêt Système",
                "description": "Désactive temporairement les implants et équipements électroniques de la cible",
                "category": "status",
                "status_type": "EMP_DISABLED",
                "status_duration": 3,
                "status_strength": 2,
                "application_chance": 0.8,
                "max_targets": 1,
                "trigger_conditions": {
                    "min_charge": 50,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 50
                },
                "cooldown": 5,
                "duration": 3
            },
            {
                "id": "emp_pulse",
                "name": "Impulsion EMP",
                "description": "Crée une impulsion qui affecte tous les appareils électroniques dans la zone",
                "category": "status",
                "status_type": "EMP_DISABLED",
                "status_duration": 2,
                "status_strength": 1,
                "application_chance": 0.7,
                "max_targets": 6,
                "aoe_radius": 6,
                "trigger_conditions": {
                    "min_charge": 100,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 100,
                    "durability": 3
                },
                "cooldown": 8,
                "duration": 2
            }
        ],
        "evolution_paths": [
            {
                "id": "focused_discharge",
                "name": "Décharge Focalisée",
                "description": "Concentre l'impulsion EMP pour des effets plus puissants",
                "level_requirement": 3,
                "effects": {
                    "base_damage": 20,
                    "effects": {
                        "system_shutdown": {
                            "status_duration": 4,
                            "status_strength": 3,
                            "application_chance": 0.9
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(emp_coilgun)

def _register_experimental_weapons(weapon_system: SpecialWeaponSystem) -> None:
    """Enregistre les armes expérimentales"""
    
    # Chronofreezer
    chronofreezer = {
        "id": "chronofreezer",
        "name": "Chronogélateur",
        "description": "Arme expérimentale qui ralentit temporairement le temps autour des cibles",
        "type": SpecialWeaponType.EXPERIMENTAL,
        "rarity": SpecialWeaponRarity.LEGENDARY,
        "base_damage": 30,
        "damage_type": "TEMPORAL",
        "range": 15,
        "accuracy": 0.75,
        "max_charge": 100,
        "charge_rate": 5,
        "durability": 70,
        "effects": [
            {
                "id": "time_dilation",
                "name": "Dilatation Temporelle",
                "description": "Ralentit considérablement une cible en affectant son flux temporel",
                "category": "status",
                "status_type": "TIME_SLOWED",
                "status_duration": 3,
                "status_strength": 3,
                "application_chance": 0.8,
                "max_targets": 1,
                "trigger_conditions": {
                    "min_charge": 50,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 50,
                    "durability": 2
                },
                "cooldown": 5,
                "duration": 3
            },
            {
                "id": "temporal_stasis",
                "name": "Stase Temporelle",
                "description": "Fige complètement une cible dans le temps pendant une courte durée",
                "category": "status",
                "status_type": "TIME_FROZEN",
                "status_duration": 2,
                "status_strength": 5,
                "application_chance": 0.6,
                "max_targets": 1,
                "trigger_conditions": {
                    "min_charge": 100,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 100,
                    "durability": 5
                },
                "cooldown": 10,
                "duration": 2
            }
        ],
        "evolution_paths": [
            {
                "id": "chrono_stabilizer",
                "name": "Stabilisateur Chronologique",
                "description": "Stabilise les effets temporels pour une meilleure fiabilité",
                "level_requirement": 5,
                "effects": {
                    "effects": {
                        "time_dilation": {
                            "application_chance": 0.9,
                            "status_duration": 4
                        },
                        "temporal_stasis": {
                            "application_chance": 0.7
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(chronofreezer)
    
    # Singularity Projector
    singularity_projector = {
        "id": "singularity_projector",
        "name": "Projecteur de Singularité",
        "description": "Crée des mini trous noirs qui attirent et déchirent tout ce qui est à proximité",
        "type": SpecialWeaponType.EXPERIMENTAL,
        "rarity": SpecialWeaponRarity.ARTIFACT,
        "base_damage": 45,
        "damage_type": "GRAVITATIONAL",
        "range": 20,
        "accuracy": 0.7,
        "max_charge": 100,
        "charge_rate": 3,
        "durability": 60,
        "effects": [
            {
                "id": "gravity_well",
                "name": "Puits Gravitationnel",
                "description": "Crée un puits qui attire les ennemis et leur inflige des dégâts continus",
                "category": "damage",
                "damage": 20,
                "damage_multiplier": 1.0,
                "damage_type": "GRAVITATIONAL",
                "max_targets": 8,
                "aoe_radius": 8,
                "pull_strength": 3,
                "continuous_damage": True,
                "damage_per_second": 10,
                "trigger_conditions": {
                    "min_charge": 70,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 70,
                    "durability": 3
                },
                "cooldown": 8,
                "duration": 5
            },
            {
                "id": "micro_singularity",
                "name": "Micro-Singularité",
                "description": "Crée une singularité qui déchire tout ce qui est à proximité",
                "category": "damage",
                "damage": 100,
                "damage_multiplier": 2.0,
                "damage_type": "GRAVITATIONAL",
                "max_targets": 10,
                "aoe_radius": 5,
                "armor_penetration": 0.8,
                "trigger_conditions": {
                    "min_charge": 100,
                    "trigger_chance": 1.0
                },
                "costs": {
                    "charge": 100,
                    "durability": 8
                },
                "cooldown": 15,
                "duration": 2
            }
        ],
        "evolution_paths": [
            {
                "id": "stable_singularity",
                "name": "Singularité Stable",
                "description": "Stabilise la singularité pour une plus longue durée et moins de dégâts à l'arme",
                "level_requirement": 7,
                "effects": {
                    "effects": {
                        "gravity_well": {
                            "duration": 7,
                            "costs": {
                                "durability": 2
                            }
                        },
                        "micro_singularity": {
                            "duration": 3,
                            "costs": {
                                "durability": 6
                            }
                        }
                    }
                }
            }
        ]
    }
    weapon_system.register_special_weapon(singularity_projector)
