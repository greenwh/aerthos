#!/usr/bin/env python3
"""
Script to implement all magic items from magic_items.json into the functional databases.
Based on MAGIC_ITEMS_IMPLEMENTATION_PLAN.md and ANSWERS.md (from DM Guide).

This script generates JSON entries for equipment.json to add all missing magic items.
"""

import json

def generate_potions():
    """Generate all 17 potions from ANSWERS.md"""
    potions = {
        # CRITICAL - Healing Potions
        "potion_extra_healing": {
            "name": "Potion of Extra-Healing",
            "type": "consumable",
            "cost_gp": 800,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "healing"],
            "effect": {
                "type": "heal",
                "amount": "3d8+3",
                "duration": "instant"
            },
            "xp_value": 400,
            "description": "A potent red liquid that restores 3d8+3 hit points when consumed. More powerful than a standard healing potion."
        },

        # CRITICAL - Combat Enhancement
        "potion_giant_strength": {
            "name": "Potion of Giant Strength",
            "type": "consumable",
            "cost_gp": 1000,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "strength"],
            "effect": {
                "type": "ability_boost",
                "ability": "strength",
                "strength_type": "random",  # d20 roll: 1-6 Hill, 7-10 Stone, 11-14 Frost, 15-17 Fire, 18-19 Cloud, 20 Storm
                "damage_bonus_range": [7, 12],  # Hill +7 to Storm +12
                "duration_turns": "4+1d4"
            },
            "xp_value": 600,
            "description": "A thick, viscous potion that grants the strength of a giant. Type determined randomly: Hill (+7 damage), Stone (+8), Frost (+9), Fire (+10), Cloud (+11), or Storm (+12). Duration: 4+1d4 turns."
        },

        "potion_speed": {
            "name": "Potion of Speed",
            "type": "consumable",
            "cost_gp": 900,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "haste"],
            "effect": {
                "type": "haste",
                "movement_multiplier": 2,
                "attacks_multiplier": 2,
                "duration_rounds": "5d4",  # 5-20 rounds
                "side_effect": "ages_1_year"
            },
            "xp_value": 450,
            "description": "A silvery potion that doubles movement and attacks for 5-20 rounds. Side effect: ages the drinker 1 year permanently."
        },

        "potion_heroism": {
            "name": "Potion of Heroism",
            "type": "consumable",
            "cost_gp": 500,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "enhancement"],
            "effect": {
                "type": "temporary_levels",
                "levels_by_current": {
                    0: {"levels": 4, "hp": "4d10"},
                    "1-3": {"levels": 3, "hp": "3d10+1"},
                    "4-6": {"levels": 2, "hp": "2d10+2"},
                    "7-9": {"levels": 1, "hp": "1d10+3"}
                },
                "duration_turns": "4+1d4"
            },
            "xp_value": 300,
            "description": "A golden potion that grants temporary levels and HP. 0-level gains 4 levels (4d10 HP), 1st-3rd gain 3 levels (3d10+1 HP), 4th-6th gain 2 levels (2d10+2 HP), 7th-9th gain 1 level (1d10+3 HP). Duration: 4+1d4 turns."
        },

        # IMPORTANT - Movement Potions
        "potion_flying": {
            "name": "Potion of Flying",
            "type": "consumable",
            "cost_gp": 750,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "flight"],
            "effect": {
                "type": "flight",
                "movement_rate": "as_fly_spell",
                "duration_turns": "4+1d4"
            },
            "xp_value": 500,
            "description": "A feather-light potion that grants the ability to fly as per the 3rd level magic-user spell. Duration: 4+1d4 turns."
        },

        "potion_levitation": {
            "name": "Potion of Levitation",
            "type": "consumable",
            "cost_gp": 400,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "levitation"],
            "effect": {
                "type": "levitation",
                "max_weight_gp": 6000,  # 600 lbs
                "duration_turns": "4+1d4"
            },
            "xp_value": 250,
            "description": "A light blue potion that allows levitation as per the 2nd level magic-user spell. Max weight: 6,000 gp (600 lbs). Duration: 4+1d4 turns."
        },

        "potion_climbing": {
            "name": "Potion of Climbing",
            "type": "consumable",
            "cost_gp": 500,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "climbing"],
            "effect": {
                "type": "climbing",
                "base_fail_chance": 1,  # 1% base
                "weight_penalty_per_100gp": 1,
                "armor_penalties": {
                    "studded_leather": 1.5,
                    "ring_mail": 1.5,
                    "scale_mail": 4,
                    "chain_mail": 7,
                    "plate_mail": 10
                },
                "duration_turns": 1,
                "duration_rounds": "1d4+1"  # 1 turn + 5-20 rounds
            },
            "xp_value": 300,
            "description": "A sticky potion that grants superior climbing ability. Base 1% fail chance + 1% per 100gp weight + armor penalties. Duration: 1 turn + 1d4+1 rounds."
        },

        # IMPORTANT - Stealth/Detection
        "potion_invisibility": {
            "name": "Potion of Invisibility",
            "type": "consumable",
            "cost_gp": 500,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "invisibility"],
            "effect": {
                "type": "invisibility",
                "breaks_on_attack": True,
                "duration_turns": "4+1d4"  # or single gulp for 3-6 turns
            },
            "xp_value": 250,
            "description": "A clear, shimmering potion that grants invisibility as per the spell. Breaks when attacking. Duration: 4+1d4 turns (or 3-6 turns if drunk in one gulp)."
        },

        "potion_esp": {
            "name": "Potion of ESP",
            "type": "consumable",
            "cost_gp": 850,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "telepathy"],
            "effect": {
                "type": "esp",
                "duration_rounds": "5d8"  # 5-40 rounds
            },
            "xp_value": 500,
            "description": "A purple potion that grants ESP (telepathy) as per the spell. Duration: 5-40 rounds."
        },

        "potion_clairaudience": {
            "name": "Potion of Clairaudience",
            "type": "consumable",
            "cost_gp": 400,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "divination"],
            "effect": {
                "type": "clairaudience",
                "range_inches": 3,  # 30 yards indoors / 30 yards outdoors
                "duration_turns": 2
            },
            "xp_value": 250,
            "description": "A potion that grants the ability to hear unknown areas within 3\" (30 yards). Duration: 2 turns."
        },

        "potion_clairvoyance": {
            "name": "Potion of Clairvoyance",
            "type": "consumable",
            "cost_gp": 500,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "divination"],
            "effect": {
                "type": "clairvoyance",
                "range_inches": 3,  # 30 yards
                "duration_turns": 1
            },
            "xp_value": 300,
            "description": "A crystal-clear potion that grants the ability to see unknown areas up to 3\" (30 yards) distant. Duration: 1 turn."
        },

        # OPTIONAL - Transformation & Utility
        "potion_diminution": {
            "name": "Potion of Diminution",
            "type": "consumable",
            "cost_gp": 500,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "transformation"],
            "effect": {
                "type": "size_change",
                "size_percent": 5,  # 5% of normal size
                "duration_turns": "6+2d4+1"  # 6 turns + 2-5 additional turns
            },
            "xp_value": 300,
            "description": "A shrinking potion that reduces the drinker to 5% of normal size. Duration: 6 + 2-5 additional turns."
        },

        "potion_gaseous_form": {
            "name": "Potion of Gaseous Form",
            "type": "consumable",
            "cost_gp": 400,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "transformation"],
            "effect": {
                "type": "gaseous_form",
                "movement_rate_inches": 3,  # 3"/round
                "duration_turns": "4+1d4"
            },
            "xp_value": 300,
            "description": "A smoky potion that transforms the drinker into gaseous form. Movement: 3\"/round. Can enter any non-airtight space. Duration: 4+1d4 turns."
        },

        "potion_animal_control": {
            "name": "Potion of Animal Control",
            "type": "consumable",
            "cost_gp": 400,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "control"],
            "effect": {
                "type": "animal_control",
                "animals_controlled": "5-20 giant rats, 3-12 man-sized, or 1-4 weighing 1/2 ton+",
                "animal_type_d20": {
                    "1-4": "Mammal/Marsupial",
                    "5-8": "Avian",
                    "9-12": "Reptile/Amphibian",
                    "13-15": "Fish",
                    "16-17": "Mammal/Avian",
                    "18-19": "Reptile/Fish",
                    "20": "All"
                },
                "save_intelligence_5_plus": True,
                "duration_turns": "4+1d4"
            },
            "xp_value": 250,
            "description": "A musky potion that allows control over animals. Controls 5-20 small, 3-12 man-sized, or 1-4 large animals. Type determined by d20 roll. Animals with INT 5+ get a save. Duration: 4+1d4 turns."
        },

        "potion_water_breathing": {
            "name": "Potion of Water Breathing",
            "type": "consumable",
            "cost_gp": 900,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "waterbreathing"],
            "effect": {
                "type": "water_breathing",
                "duration_minutes": 60,
                "duration_rounds_per_dose": "1d10",  # +1-10 rounds per dose
                "doses": "75% 2 doses, 25% 4 doses"
            },
            "xp_value": 400,
            "description": "A blue-green potion that allows breathing underwater. Duration: 1 hour + 1-10 rounds per dose. 75% chance of 2 doses, 25% chance of 4 doses."
        },

        "potion_poison": {
            "name": "Potion of Poison",
            "type": "consumable",
            "cost_gp": 0,
            "weight_gp": 0.5,
            "properties": ["magic", "potion", "poison", "cursed"],
            "effect": {
                "type": "poison",
                "effect": "death",
                "save_modifiers": {
                    "weak": 4,
                    "average": 0,
                    "deadly": -4
                }
            },
            "xp_value": 0,
            "description": "A deadly poisonous potion disguised as a beneficial one. Effect: Death. Save varies: Weak (+4), Average (normal), or Deadly (-4)."
        }
    }
    return potions

def generate_protection_scrolls():
    """Generate protection scrolls from ANSWERS.md"""
    scrolls = {
        "scroll_protection_demons": {
            "name": "Scroll of Protection from Demons",
            "type": "scroll",
            "cost_gp": 1000,
            "weight_gp": 0.1,
            "properties": ["magic", "scroll", "protection"],
            "effect": {
                "type": "protection_circle",
                "radius_feet": 10,
                "duration_rounds": "1d4+1",  # 5-20 rounds
                "protection_from": ["demons"],
                "moves_with_reader": True
            },
            "xp_value": 2500,
            "description": "Creates a 10-foot radius circle that demons cannot enter. Duration: 5-20 rounds. Circle moves with the reader."
        },

        "scroll_protection_devils": {
            "name": "Scroll of Protection from Devils",
            "type": "scroll",
            "cost_gp": 1500,
            "weight_gp": 0.1,
            "properties": ["magic", "scroll", "protection"],
            "effect": {
                "type": "protection_circle",
                "radius_feet": 10,
                "duration_rounds": "1d4+1",  # 5-20 rounds
                "protection_from": ["devils"],
                "moves_with_reader": True
            },
            "xp_value": 2500,
            "description": "Creates a 10-foot radius circle that devils cannot enter. Duration: 5-20 rounds. Circle moves with the reader."
        },

        "scroll_protection_lycanthropes": {
            "name": "Scroll of Protection from Lycanthropes",
            "type": "scroll",
            "cost_gp": 1000,
            "weight_gp": 0.1,
            "properties": ["magic", "scroll", "protection"],
            "effect": {
                "type": "protection_circle",
                "radius_feet": 10,
                "duration_rounds": "1d6+5",  # 5-30 rounds
                "protection_from": ["lycanthropes"],
                "max_hd": 49,
                "moves_with_reader": True
            },
            "xp_value": 1000,
            "description": "Creates a 10-foot radius circle that lycanthropes cannot enter. Affects up to 49 HD of lycanthropes. Duration: 5-30 rounds. Circle moves with the reader."
        },

        "scroll_protection_magic": {
            "name": "Scroll of Protection from Magic",
            "type": "scroll",
            "cost_gp": 2500,
            "weight_gp": 0.1,
            "properties": ["magic", "scroll", "protection"],
            "effect": {
                "type": "protection_circle",
                "radius_feet": 5,  # Smaller radius for this one
                "duration_rounds": "1d6+5",  # 5-30 rounds
                "protection_from": ["all_magic"],
                "blocks_outgoing": True,
                "drains_magic_items_50_percent": True,
                "moves_with_reader": True
            },
            "xp_value": 1500,
            "description": "Creates a 5-foot radius circle that blocks ALL magic (in and out). Magic items touching the globe must save (50%) or be drained. Duration: 5-30 rounds."
        },

        "scroll_protection_undead": {
            "name": "Scroll of Protection from Undead",
            "type": "scroll",
            "cost_gp": 1000,
            "weight_gp": 0.1,
            "properties": ["magic", "scroll", "protection"],
            "effect": {
                "type": "protection_circle",
                "radius_feet": 5,
                "duration_rounds": "10d8",  # 10-80 rounds
                "protection_from": ["undead"],
                "max_hd": 35,
                "moves_with_reader": True
            },
            "xp_value": 1500,
            "description": "Creates a 5-foot radius circle that restrains up to 35 HD of undead. Duration: 10-80 rounds. Circle moves with the reader."
        }
    }
    return scrolls

def generate_magic_armor_for_equipment():
    """Generate entries for equipment.json - armor already in armor.json"""
    # These are just references for treasure tables, actual mechanics in armor.json
    armor_items = {}

    # Leather Armor
    for bonus in [1, 2]:
        armor_items[f"leather_armor_plus_{bonus}"] = {
            "name": f"Leather Armor +{bonus}",
            "type": "magic_item",
            "cost_gp": 2500 * bonus,
            "weight_gp": 0,  # Magic armor is weightless
            "properties": ["magic", "armor"],
            "xp_value": 500 * bonus,
            "description": f"Enchanted leather armor. See armor.json for full stats. AC {8-bonus}."
        }

    # Chain Mail
    for bonus in [1, 2, 3]:
        armor_items[f"chain_mail_plus_{bonus}"] = {
            "name": f"Chain Mail +{bonus}",
            "type": "magic_item",
            "cost_gp": 2500 if bonus == 1 else (5000 if bonus == 2 else 7500),
            "weight_gp": 0,
            "properties": ["magic", "armor"],
            "xp_value": 500 * bonus,
            "description": f"Enchanted chain mail. See armor.json for full stats. AC {5-bonus}."
        }

    # Plate Mail
    for bonus in [1, 2, 3, 4]:
        armor_items[f"plate_mail_plus_{bonus}"] = {
            "name": f"Plate Mail +{bonus}",
            "type": "magic_item",
            "cost_gp": 5000 * bonus,
            "weight_gp": 0,
            "properties": ["magic", "armor"],
            "xp_value": 800 * bonus,
            "description": f"Enchanted plate mail. See armor.json for full stats. AC {3-bonus}."
        }

    # Shields
    for bonus in [1, 2, 3]:
        armor_items[f"shield_plus_{bonus}"] = {
            "name": f"Shield +{bonus}",
            "type": "magic_item",
            "cost_gp": 2500 * bonus,
            "weight_gp": 0,
            "properties": ["magic", "shield"],
            "xp_value": 500 * bonus,
            "description": f"Enchanted shield. See armor.json for full stats. AC bonus: +{bonus+1}."
        }

    return armor_items

def generate_magic_weapons_for_equipment():
    """Generate entries for equipment.json - weapons already in weapons.json"""
    weapon_items = {}

    # Swords
    for weapon_type in ["longsword", "short_sword", "broad_sword", "bastard_sword", "two_handed_sword"]:
        for bonus in [1, 2, 3]:
            if weapon_type == "longsword" or bonus == 1:  # All get +1, only longsword gets +2/+3
                name = weapon_type.replace("_", " ").title()
                weapon_items[f"{weapon_type}_plus_{bonus}"] = {
                    "name": f"{name} +{bonus}",
                    "type": "magic_item",
                    "cost_gp": 2000 * bonus if weapon_type != "longsword" else (2000 if bonus == 1 else (4000 if bonus == 2 else 7000)),
                    "weight_gp": 10 if "short" in weapon_type else (60 if "long" in weapon_type else (75 if "broad" in weapon_type else (100 if "bastard" in weapon_type else 250))),
                    "properties": ["magic", "weapon", "sword"],
                    "xp_value": 400 * bonus if weapon_type != "longsword" else (400 if bonus == 1 else (800 if bonus == 2 else 1400)),
                    "description": f"Enchanted {weapon_type.replace('_', ' ')}. See weapons.json for full stats. +{bonus} to attack and damage."
                }

    # Other weapons
    for weapon in ["dagger", "mace", "battle_axe", "hammer", "spear"]:
        for bonus in [1, 2]:
            name = weapon.replace("_", " ").title()
            if weapon == "hammer":
                name = "War Hammer"
            weapon_items[f"{weapon}_plus_{bonus}"] = {
                "name": f"{name} +{bonus}",
                "type": "magic_item",
                "cost_gp": 1500 * bonus if weapon != "dagger" else 1000 * bonus,
                "weight_gp": 10 if weapon == "dagger" else (50 if weapon in ["hammer", "spear"] else (75 if weapon == "battle_axe" else 100)),
                "properties": ["magic", "weapon"],
                "xp_value": 300 * bonus if weapon != "dagger" else (200 if bonus == 1 else 400),
                "description": f"Enchanted {weapon.replace('_', ' ')}. See weapons.json for full stats. +{bonus} to attack and damage."
            }

    # Bow
    weapon_items["long_bow_plus_1"] = {
        "name": "Long Bow +1",
        "type": "magic_item",
        "cost_gp": 2500,
        "weight_gp": 100,
        "properties": ["magic", "weapon", "bow"],
        "xp_value": 500,
        "description": "Enchanted longbow. See weapons.json for full stats. +1 to attack rolls."
    }

    return weapon_items

def generate_rings():
    """Generate remaining rings from ANSWERS.md"""
    rings = {
        "ring_feather_falling": {
            "name": "Ring of Feather Falling",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "protection"],
            "effect": {
                "type": "feather_fall",
                "activation": "automatic",
                "trigger": "falling_5_feet_or_more"
            },
            "xp_value": 1000,
            "description": "A delicate ring that automatically activates when falling 5' or more, causing the wearer to fall slowly and safely."
        },

        "ring_fire_resistance": {
            "name": "Ring of Fire Resistance",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "resistance"],
            "effect": {
                "type": "fire_resistance",
                "normal_fire": "immune",
                "very_hot_fire": "10_dmg_per_round",
                "exceptional_fire": "save_plus_4_half_damage_minus_2_per_die"
            },
            "xp_value": 1000,
            "description": "Grants immunity to normal fires. Very hot fires (lava, hell hound): 10 dmg/round. Exceptionally hot fires (dragon breath, fireball): save at +4, -2 damage per die."
        },

        "ring_invisibility": {
            "name": "Ring of Invisibility",
            "type": "magic_item",
            "cost_gp": 7500,
            "weight_gp": 0,
            "properties": ["magic", "ring", "invisibility"],
            "effect": {
                "type": "invisibility",
                "activation": "at_will",
                "breaks_on_attack": True,
                "inaudible_chance": 10
            },
            "xp_value": 1500,
            "description": "Grants invisibility at will (as spell). Breaks when attacking. 10% are also inaudible."
        },

        "ring_regeneration": {
            "name": "Ring of Regeneration",
            "type": "magic_item",
            "cost_gp": 20000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "healing"],
            "effect": {
                "type": "regeneration",
                "hp_per_turn": 1,
                "regrows_limbs": True,
                "reverses_death": True,
                "vampiric_variant_50_percent": "regenerates_half_damage_dealt"
            },
            "xp_value": 4000,
            "description": "Restores 1 HP per turn. Will replace lost limbs/organs. Can reverse death (unless poison). 50% chance of vampiric version that regenerates 1/2 damage dealt."
        },

        "ring_spell_storing": {
            "name": "Ring of Spell Storing",
            "type": "magic_item",
            "cost_gp": 22500,
            "weight_gp": 0,
            "properties": ["magic", "ring", "spellcasting"],
            "effect": {
                "type": "spell_storing",
                "spells_stored": "2d4+1",
                "spell_classes": ["Cleric_d6", "Druid_d4", "Magic-User_d8", "Illusionist_d6"],
                "rechargeable": True
            },
            "xp_value": 3500,
            "description": "Contains 2-5 (d4+1) spells. Class and level determined randomly. Rechargeable by caster of appropriate level."
        },

        "ring_water_walking": {
            "name": "Ring of Water Walking",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "movement"],
            "effect": {
                "type": "water_walking",
                "surfaces": ["water", "mud", "snow", "quicksand"],
                "max_weight_lbs": 1200,
                "activation": "automatic"
            },
            "xp_value": 1000,
            "description": "Walk on any liquid (mud, snow, quicksand). Max weight 1,200 lbs. Always active."
        },

        "ring_xray_vision": {
            "name": "Ring of X-Ray Vision",
            "type": "magic_item",
            "cost_gp": 17500,
            "weight_gp": 0,
            "properties": ["magic", "ring", "divination"],
            "effect": {
                "type": "xray_vision",
                "range_feet": 20,
                "penetration": {
                    "wood_cloth": "20_feet",
                    "stone": "10_feet",
                    "metal": "1_inch",
                    "blocked_by": ["lead", "gold", "platinum"]
                },
                "scan_rate": "100_sq_ft_per_turn",
                "max_duration": "1_turn_before_constitution_drain"
            },
            "xp_value": 3500,
            "description": "Range 20'. Penetrates 20' wood/cloth, 10' stone, 1\" metal (blocked by lead/gold/platinum). Scan 100 sq ft per turn. Max 1 turn before CON drain."
        },

        "ring_wishes_1d2": {
            "name": "Ring of Wishes (Multiple)",
            "type": "magic_item",
            "cost_gp": 24000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "artifact"],
            "effect": {
                "type": "wishes",
                "wish_count": "2d4",
                "wish_type": "standard"
            },
            "xp_value": 12000,
            "description": "Contains 2-8 wishes (2d4). Standard wish spell rules apply."
        },

        "ring_wishes_3": {
            "name": "Ring of Three Wishes",
            "type": "magic_item",
            "cost_gp": 15000,
            "weight_gp": 0,
            "properties": ["magic", "ring", "artifact"],
            "effect": {
                "type": "wishes",
                "wish_count": 3,
                "limited_wish_chance": 25
            },
            "xp_value": 15000,
            "description": "Contains 3 wishes. 25% chance they are limited wishes instead of full wishes."
        },

        "ring_contrariness": {
            "name": "Ring of Contrariness",
            "type": "magic_item",
            "cost_gp": 0,
            "weight_gp": 0,
            "properties": ["magic", "ring", "cursed"],
            "effect": {
                "type": "curse",
                "effect": "cannot_agree",
                "cannot_remove": True
            },
            "xp_value": 0,
            "description": "Cursed ring. Wearer cannot agree with any idea/statement/action. Cannot be removed."
        },

        "ring_delusion": {
            "name": "Ring of Delusion",
            "type": "magic_item",
            "cost_gp": 0,
            "weight_gp": 0,
            "properties": ["magic", "ring", "cursed"],
            "effect": {
                "type": "curse",
                "effect": "delusion",
                "appears_as": "whatever_wearer_desires"
            },
            "xp_value": 0,
            "description": "Cursed ring. Convinces wearer it is a different ring (whatever they desire). Actually does nothing."
        },

        "ring_weakness": {
            "name": "Ring of Weakness",
            "type": "magic_item",
            "cost_gp": 0,
            "weight_gp": 0,
            "properties": ["magic", "ring", "cursed"],
            "effect": {
                "type": "curse",
                "effect": "ability_drain",
                "str_loss_per_turn": 1,
                "con_loss_per_turn": 1,
                "minimum": 3
            },
            "xp_value": 0,
            "description": "Cursed ring. Drains 1 point of STR and CON per turn until reaching 3. Permanent while worn."
        }
    }
    return rings

def generate_misc_magic():
    """Generate miscellaneous magic items from ANSWERS.md"""
    misc = {
        "bag_of_holding_250": {
            "name": "Bag of Holding (250 lbs)",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 15,
            "properties": ["magic", "container"],
            "effect": {
                "type": "extradimensional_storage",
                "capacity_lbs": 250,
                "volume_cubic_ft": 30,
                "overload": "ruptures_contents_lost"
            },
            "xp_value": 5000,
            "description": "Magical bag holds 250 lbs in 30 cubic ft. Bag weighs 15 lbs. Overloading ruptures bag, contents lost in nilspace."
        },

        "bag_of_holding_500": {
            "name": "Bag of Holding (500 lbs)",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 15,
            "properties": ["magic", "container"],
            "effect": {
                "type": "extradimensional_storage",
                "capacity_lbs": 500,
                "volume_cubic_ft": 70
            },
            "xp_value": 5000,
            "description": "Magical bag holds 500 lbs in 70 cubic ft. Bag weighs 15 lbs."
        },

        "bag_of_holding_1000": {
            "name": "Bag of Holding (1000 lbs)",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 35,
            "properties": ["magic", "container"],
            "effect": {
                "type": "extradimensional_storage",
                "capacity_lbs": 1000,
                "volume_cubic_ft": 150
            },
            "xp_value": 5000,
            "description": "Magical bag holds 1,000 lbs in 150 cubic ft. Bag weighs 35 lbs."
        },

        "bag_of_holding_1500": {
            "name": "Bag of Holding (1500 lbs)",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 60,
            "properties": ["magic", "container"],
            "effect": {
                "type": "extradimensional_storage",
                "capacity_lbs": 1500,
                "volume_cubic_ft": 250
            },
            "xp_value": 5000,
            "description": "Magical bag holds 1,500 lbs in 250 cubic ft. Bag weighs 60 lbs."
        },

        "boots_elvenkind": {
            "name": "Boots of Elvenkind",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 1,
            "properties": ["magic", "boots", "stealth"],
            "effect": {
                "type": "silent_movement",
                "silence_chance": 95,
                "best_conditions": 100
            },
            "xp_value": 1000,
            "description": "95% chance of silent movement (100% in best conditions)."
        },

        "boots_speed": {
            "name": "Boots of Speed",
            "type": "magic_item",
            "cost_gp": 20000,
            "weight_gp": 1,
            "properties": ["magic", "boots", "haste"],
            "effect": {
                "type": "speed",
                "base_move": 24,
                "ac_bonus": 2,
                "rest_required": "1_hour_per_hour_use"
            },
            "xp_value": 2500,
            "description": "Base move 24\". +2 AC benefit. Requires 1 hour rest for every 1 hour use."
        },

        "bracers_defense_ac6": {
            "name": "Bracers of Defense AC 6",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 1,
            "properties": ["magic", "bracers", "armor"],
            "effect": {
                "type": "armor_class",
                "ac": 6,
                "stacks_with_armor": False
            },
            "xp_value": 1000,
            "description": "Set AC to 6. Do not stack with armor. See armor.json for armor integration."
        },

        "bracers_defense_ac4": {
            "name": "Bracers of Defense AC 4",
            "type": "magic_item",
            "cost_gp": 10000,
            "weight_gp": 1,
            "properties": ["magic", "bracers", "armor"],
            "effect": {
                "type": "armor_class",
                "ac": 4,
                "stacks_with_armor": False
            },
            "xp_value": 2000,
            "description": "Set AC to 4. Do not stack with armor. See armor.json for armor integration."
        },

        "cloak_displacement": {
            "name": "Cloak of Displacement",
            "type": "magic_item",
            "cost_gp": 17500,
            "weight_gp": 1,
            "properties": ["magic", "cloak", "protection"],
            "effect": {
                "type": "displacement",
                "first_attack": "always_misses",
                "ac_bonus": 2,
                "save_bonus": 2
            },
            "xp_value": 3000,
            "description": "First attack always misses. Thereafter +2 bonus to AC and saving throws."
        },

        "cloak_elvenkind": {
            "name": "Cloak of Elvenkind",
            "type": "magic_item",
            "cost_gp": 6000,
            "weight_gp": 1,
            "properties": ["magic", "cloak", "stealth"],
            "effect": {
                "type": "camouflage",
                "invisibility_outdoors": "90-100_percent",
                "invisibility_bright_light": "50_percent"
            },
            "xp_value": 1000,
            "description": "Invisibility: 90-100% outdoors/natural settings, 50% in bright light."
        },

        "gauntlets_ogre_power": {
            "name": "Gauntlets of Ogre Power",
            "type": "magic_item",
            "cost_gp": 15000,
            "weight_gp": 1,
            "properties": ["magic", "gauntlets", "strength"],
            "effect": {
                "type": "strength_boost",
                "str_value": "18/00",
                "to_hit_bonus": 3,
                "damage_bonus": 6
            },
            "xp_value": 1000,
            "description": "Sets STR to 18/00. +3 to hit, +6 damage. Permanent while worn."
        },

        "helm_telepathy": {
            "name": "Helm of Telepathy",
            "type": "magic_item",
            "cost_gp": 35000,
            "weight_gp": 3,
            "properties": ["magic", "helm", "telepathy"],
            "effect": {
                "type": "telepathy",
                "range_inches": 6,
                "read_thoughts": True,
                "suggestion": "save_modified_by_int"
            },
            "xp_value": 3000,
            "description": "Range 6\". Read surface thoughts. Suggestion (save modified by Intelligence)."
        },

        "rope_climbing": {
            "name": "Rope of Climbing",
            "type": "magic_item",
            "cost_gp": 10000,
            "weight_gp": 3,
            "properties": ["magic", "rope", "utility"],
            "effect": {
                "type": "animated_rope",
                "length_feet": 60,
                "weight_capacity_lbs": 3000,
                "movement_rate": "10_feet_per_round"
            },
            "xp_value": 1000,
            "description": "60' long. Strong enough to hold 3,000 lbs. Snakes forward/up 10'/round on command."
        },

        "rope_entanglement": {
            "name": "Rope of Entanglement",
            "type": "magic_item",
            "cost_gp": 12000,
            "weight_gp": 3,
            "properties": ["magic", "rope", "combat"],
            "effect": {
                "type": "entangle",
                "movement_rate": "20_feet_forward_10_feet_up",
                "ac": -2,
                "hp": 22,
                "entangles": "8_man_sized",
                "damage_per_round": "2d6"
            },
            "xp_value": 1500,
            "description": "20' forward / 10' up. AC -2, HP 22. Entangles up to 8 man-sized creatures. Damage 2-12 per round constriction."
        }
    }
    return misc

def generate_wands_staves_rods():
    """Generate wands, staves, and rods from ANSWERS.md"""
    items = {
        "wand_enemy_detection": {
            "name": "Wand of Enemy Detection",
            "type": "magic_item",
            "cost_gp": 10000,
            "weight_gp": 1,
            "properties": ["magic", "wand", "divination"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "detect_enemies",
                "range_inches": 6,
                "duration_turns": 1,
                "charges_per_use": 1
            },
            "xp_value": 2000,
            "description": "Detects enemies in 6\" sphere for 1 turn. Charges: 100 - (1d20-1). Cost: 1 charge per use."
        },

        "wand_fear": {
            "name": "Wand of Fear",
            "type": "magic_item",
            "cost_gp": 15000,
            "weight_gp": 1,
            "properties": ["magic", "wand", "enchantment"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "fear",
                "cone_length_inches": 6,
                "cone_base_inches": 2,
                "duration_rounds": 6,
                "save": "vs_wand",
                "charges_per_use": 1
            },
            "xp_value": 3000,
            "description": "Cone 6\" long, 2\" base. Duration 6 rounds. Save vs Wand. Charges: 100 - (1d20-1). Cost: 1 charge."
        },

        "wand_magic_detection": {
            "name": "Wand of Magic Detection",
            "type": "magic_item",
            "cost_gp": 12500,
            "weight_gp": 1,
            "properties": ["magic", "wand", "divination"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "detect_magic",
                "range_inches": 3,
                "duration_turns": 1,
                "charges_per_use": 1
            },
            "xp_value": 2500,
            "description": "Range 3\" radius. Duration 1 turn. Charges: 100 - (1d20-1). Cost: 1 charge."
        },

        "wand_magic_missiles": {
            "name": "Wand of Magic Missiles",
            "type": "magic_item",
            "cost_gp": 35000,
            "weight_gp": 1,
            "properties": ["magic", "wand", "evocation"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "magic_missile",
                "damage_per_missile": "1d4+1",
                "missiles_per_charge": 1,
                "charges_per_use": 1
            },
            "xp_value": 4000,
            "description": "Damage 1d4+1 per missile. Charges: 100 - (1d20-1). Cost: 1 charge per missile."
        },

        "wand_paralyzation": {
            "name": "Wand of Paralyzation",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 1,
            "properties": ["magic", "wand", "enchantment"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "paralyzation",
                "range_inches": 6,
                "duration_rounds": "5d4",
                "save": "vs_wand",
                "charges_per_use": 1
            },
            "xp_value": 3500,
            "description": "Ray, range 6\". Duration 5-20 rounds. Save vs Wand. Charges: 100 - (1d20-1). Cost: 1 charge."
        },

        "wand_secret_door_detection": {
            "name": "Wand of Secret Door Detection",
            "type": "magic_item",
            "cost_gp": 40000,
            "weight_gp": 1,
            "properties": ["magic", "wand", "divination"],
            "charges": "100-1d20+1",
            "effect": {
                "type": "detect_secret_doors",
                "range_doors_inches": 1.5,
                "range_traps_inches": 3,
                "charges_per_use": 1
            },
            "xp_value": 5000,
            "description": "Range 1.5\" (doors) or 3\" (traps). Charges: 100 - (1d20-1). Cost: 1 charge."
        },

        "staff_healing": {
            "name": "Staff of Healing",
            "type": "magic_item",
            "cost_gp": 25000,
            "weight_gp": 4,
            "properties": ["magic", "staff", "healing"],
            "charges": "25-1d6+1",
            "effect": {
                "type": "heal",
                "hp_healed": "3d6+3",
                "cures": ["blindness", "disease", "insanity"],
                "usage_limit": "1_per_day_per_person",
                "charges_per_use": 1
            },
            "xp_value": 5000,
            "description": "Restores 3d6+3 HP. Cures blindness/disease/insanity. Usage limit: 1/day per person. Charges: 25 - (1d6-1). Cost: 1 charge."
        },

        "staff_striking": {
            "name": "Staff of Striking",
            "type": "magic_item",
            "cost_gp": 15000,
            "weight_gp": 4,
            "properties": ["magic", "staff", "weapon"],
            "charges": "25-1d6+1",
            "effect": {
                "type": "striking",
                "base_damage": "1d6+3",
                "charge_options": {
                    "1_charge": "1d6+3",
                    "2_charges": "1d6+6",
                    "3_charges": "1d6+9"
                }
            },
            "xp_value": 3500,
            "description": "+3 weapon. Damage 1d6+3. Use 1 charge = standard. 2 charges = double dmg (1d6+6). 3 charges = triple dmg (1d6+9). See weapons.json."
        },

        "rod_cancellation": {
            "name": "Rod of Cancellation",
            "type": "magic_item",
            "cost_gp": 15000,
            "weight_gp": 2,
            "properties": ["magic", "rod", "abjuration"],
            "charges": "50-1d10+1",
            "effect": {
                "type": "drain_magic",
                "drains": "all_magic",
                "touch_attack": "drains_item",
                "rod_becomes_brittle": "after_use"
            },
            "xp_value": 10000,
            "description": "Drains item of ALL magical properties. Touching enemy in combat drains item. Rod becomes brittle/useless after use. Charges: 50 - (1d10-1)."
        }
    }
    return items

def generate_special_weapons():
    """Generate special weapons from ANSWERS.md and magic_items.json"""
    weapons = {
        # Special Swords
        "sword_plus_1_vs_magic_users": {
            "name": "Sword +1, +2 vs Magic-Using Creatures",
            "type": "magic_item",
            "cost_gp": 3500,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special"],
            "effect": {
                "type": "bonus_vs_creature_type",
                "base_bonus": 1,
                "vs_magic_users": 2,
                "affects": ["magic-users", "monsters_that_cast_spells", "created_conjured_gated_summoned"]
            },
            "xp_value": 600,
            "description": "+1 sword, +2 vs magic-users and monsters which can cast spells. See weapons.json for combat stats."
        },

        "sword_plus_1_vs_lycanthropes": {
            "name": "Sword +1, +3 vs Lycanthropes",
            "type": "magic_item",
            "cost_gp": 4000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special"],
            "effect": {
                "type": "bonus_vs_creature_type",
                "base_bonus": 1,
                "vs_lycanthropes": 3,
                "affects": ["were-creatures", "polymorph_shape_change_affected"]
            },
            "xp_value": 700,
            "description": "+1 sword, +3 vs lycanthropes and any creature under polymorph/shape change. See weapons.json."
        },

        "sword_plus_1_vs_regenerating": {
            "name": "Sword +1, +3 vs Regenerating Creatures",
            "type": "magic_item",
            "cost_gp": 4500,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special"],
            "effect": {
                "type": "bonus_vs_creature_type",
                "base_bonus": 1,
                "vs_regenerating": 3,
                "affects": ["creatures_with_regeneration", "ring_of_regeneration_wearers"]
            },
            "xp_value": 800,
            "description": "+1 sword, +3 vs creatures that regenerate (trolls, vampires, etc.). See weapons.json."
        },

        "sword_flame_tongue": {
            "name": "Sword +1, Flame Tongue",
            "type": "magic_item",
            "cost_gp": 4500,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special", "fire"],
            "effect": {
                "type": "elemental_damage",
                "base_bonus": 1,
                "bonuses": {
                    "vs_regenerating": 2,
                    "vs_cold_using_inflammable_avian": 3,
                    "vs_undead": 4
                },
                "light": "illuminates_as_torch",
                "ignites": ["oil", "webs", "paper", "dry_wood"]
            },
            "xp_value": 900,
            "description": "+1 base, +2 vs regenerating, +3 vs cold-using/inflammable/avian, +4 vs undead. Illuminates as torch. Ignites flammables. See weapons.json."
        },

        "sword_luck_blade": {
            "name": "Sword +1, Luck Blade",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special", "artifact"],
            "effect": {
                "type": "luck_and_wishes",
                "base_bonus": 1,
                "save_bonus": 1,
                "wishes": "1d4+1"
            },
            "xp_value": 1000,
            "description": "+1 sword. Gives +1 to all saving throws. Contains 2-5 wishes (d4+1). See weapons.json."
        },

        "sword_plus_2_giant_slayer": {
            "name": "Sword +2, Giant Slayer",
            "type": "magic_item",
            "cost_gp": 5000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special"],
            "effect": {
                "type": "bonus_vs_creature_type",
                "base_bonus": 2,
                "vs_giants": 3,
                "vs_true_giants": "double_damage",
                "affects": ["giants", "ettins", "ogre_mages", "titans"]
            },
            "xp_value": 900,
            "description": "+2 sword, +3 vs any giant/ettin/ogre mage/titan. Double damage (1d8+1d8+3) vs true giants. See weapons.json."
        },

        "sword_plus_2_dragon_slayer": {
            "name": "Sword +2, Dragon Slayer",
            "type": "magic_item",
            "cost_gp": 4500,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special"],
            "effect": {
                "type": "bonus_vs_creature_type",
                "base_bonus": 2,
                "vs_dragons": 4,
                "vs_specific_dragon": "triple_damage",
                "dragon_type": "random"
            },
            "xp_value": 900,
            "description": "+2 sword, +4 vs any true dragon. Triple damage (3d8+4) vs specific dragon type (random). See weapons.json."
        },

        "sword_frost_brand": {
            "name": "Sword +3, Frost Brand",
            "type": "magic_item",
            "cost_gp": 8000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "special", "cold"],
            "effect": {
                "type": "elemental_damage",
                "base_bonus": 3,
                "vs_fire_using_dwelling": 6,
                "extinguish_fires": "50_percent_chance_10_foot_radius",
                "fire_resistance": "as_ring"
            },
            "xp_value": 1600,
            "description": "+3 sword, +6 vs fire-using/dwelling creatures. 50% extinguish fires in 10' radius. Protects wielder as Ring of Fire Resistance. See weapons.json."
        },

        "sword_plus_4": {
            "name": "Sword +4",
            "type": "magic_item",
            "cost_gp": 10000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword"],
            "xp_value": 2000,
            "description": "+4 sword. Extremely rare and powerful. See weapons.json."
        },

        "sword_plus_5": {
            "name": "Sword +5",
            "type": "magic_item",
            "cost_gp": 13000,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword"],
            "xp_value": 2600,
            "description": "+5 sword. Legendary artifact-level power. See weapons.json."
        },

        "sword_plus_1_cursed": {
            "name": "Sword +1, Cursed",
            "type": "magic_item",
            "cost_gp": 0,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "cursed"],
            "effect": {
                "type": "curse",
                "appears_as": "+1",
                "cannot_remove": True
            },
            "xp_value": 0,
            "description": "Cursed sword. Appears as +1 but has penalties. Cannot be unequipped willingly once wielded. See weapons.json."
        },

        "sword_minus_2_cursed": {
            "name": "Sword -2, Cursed",
            "type": "magic_item",
            "cost_gp": 0,
            "weight_gp": 60,
            "properties": ["magic", "weapon", "sword", "cursed"],
            "effect": {
                "type": "curse",
                "penalty": -2,
                "cannot_remove": True
            },
            "xp_value": 0,
            "description": "Cursed sword with -2 penalty to hit and damage. Cannot be unequipped. See weapons.json."
        },

        # Magic Ammunition
        "arrows_plus_1": {
            "name": "Arrows +1 (2d6)",
            "type": "magic_item",
            "cost_gp": 15,
            "weight_gp": 0.3,
            "properties": ["magic", "ammunition", "arrow"],
            "quantity": "2d6",
            "effect": {
                "type": "magic_ammunition",
                "bonus": 1,
                "stacks_with_bow": True,
                "miss_chance_destroyed": 50,
                "hit_always_destroyed": True
            },
            "xp_value": 6,
            "description": "2d6 magic arrows with +1 bonus. Bonuses stack with bow. 50% broken if miss, always destroyed on hit."
        },

        "arrows_plus_2": {
            "name": "Arrows +2 (1d6)",
            "type": "magic_item",
            "cost_gp": 30,
            "weight_gp": 0.3,
            "properties": ["magic", "ammunition", "arrow"],
            "quantity": "1d6",
            "effect": {
                "type": "magic_ammunition",
                "bonus": 2,
                "stacks_with_bow": True,
                "miss_chance_destroyed": 50,
                "hit_always_destroyed": True
            },
            "xp_value": 12,
            "description": "1d6 magic arrows with +2 bonus. Bonuses stack with bow. 50% broken if miss, always destroyed on hit."
        },

        "arrows_plus_3": {
            "name": "Arrows +3 (1d3)",
            "type": "magic_item",
            "cost_gp": 45,
            "weight_gp": 0.3,
            "properties": ["magic", "ammunition", "arrow"],
            "quantity": "1d3",
            "effect": {
                "type": "magic_ammunition",
                "bonus": 3,
                "stacks_with_bow": True,
                "miss_chance_destroyed": 50,
                "hit_always_destroyed": True
            },
            "xp_value": 18,
            "description": "1d3 magic arrows with +3 bonus. Bonuses stack with bow. 50% broken if miss, always destroyed on hit."
        },

        "bolts_plus_1": {
            "name": "Bolts +1 (2d6)",
            "type": "magic_item",
            "cost_gp": 15,
            "weight_gp": 0.1,
            "properties": ["magic", "ammunition", "bolt"],
            "quantity": "2d6",
            "effect": {
                "type": "magic_ammunition",
                "bonus": 1,
                "stacks_with_crossbow": True,
                "miss_chance_destroyed": 50,
                "hit_always_destroyed": True
            },
            "xp_value": 6,
            "description": "2d6 magic crossbow bolts with +1 bonus. Bonuses stack with crossbow. 50% broken if miss, always destroyed on hit."
        },

        "bolts_plus_2": {
            "name": "Bolts +2 (1d6)",
            "type": "magic_item",
            "cost_gp": 30,
            "weight_gp": 0.1,
            "properties": ["magic", "ammunition", "bolt"],
            "quantity": "1d6",
            "effect": {
                "type": "magic_ammunition",
                "bonus": 2,
                "stacks_with_crossbow": True,
                "miss_chance_destroyed": 50,
                "hit_always_destroyed": True
            },
            "xp_value": 12,
            "description": "1d6 magic crossbow bolts with +2 bonus. Bonuses stack with crossbow. 50% broken if miss, always destroyed on hit."
        }
    }
    return weapons

def main():
    """Generate all magic items JSON"""
    print("Generating magic items for equipment.json...")

    all_items = {}

    # Phase 1: Quick Wins (armor and weapons)
    print("\nPhase 1: Magic Armor and Weapons...")
    all_items.update(generate_magic_armor_for_equipment())
    all_items.update(generate_magic_weapons_for_equipment())
    print(f"  Added {len(all_items)} Phase 1 items")

    # Phase 2: Potions
    print("\nPhase 2: Potions...")
    potions = generate_potions()
    all_items.update(potions)
    print(f"  Added {len(potions)} potions")

    # Phase 3: Protection Scrolls
    print("\nPhase 3: Protection Scrolls...")
    scrolls = generate_protection_scrolls()
    all_items.update(scrolls)
    print(f"  Added {len(scrolls)} protection scrolls")

    # Phase 4: Rings
    print("\nPhase 4: Rings...")
    rings = generate_rings()
    all_items.update(rings)
    print(f"  Added {len(rings)} rings")

    # Phase 5: Wands/Staves/Rods
    print("\nPhase 5: Wands/Staves/Rods...")
    wands = generate_wands_staves_rods()
    all_items.update(wands)
    print(f"  Added {len(wands)} wands/staves/rods")

    # Phase 6: Misc Magic
    print("\nPhase 6: Miscellaneous Magic...")
    misc = generate_misc_magic()
    all_items.update(misc)
    print(f"  Added {len(misc)} miscellaneous items")

    # Phase 7: Special Weapons
    print("\nPhase 7: Special Weapons...")
    special = generate_special_weapons()
    all_items.update(special)
    print(f"  Added {len(special)} special weapons")

    # Output JSON
    output = json.dumps(all_items, indent=2)
    print(f"\nTotal items generated: {len(all_items)}")
    print("\n" + "="*80)
    print("JSON OUTPUT:")
    print("="*80)
    print(f"Items by phase:")
    print(f"  Phase 1 (Basic +1/+2/+3): 30 items")
    print(f"  Phase 2 (Potions): {len(potions)} items")
    print(f"  Phase 3 (Scrolls): {len(scrolls)} items")
    print(f"  Phase 4 (Rings): {len(rings)} items")
    print(f"  Phase 5 (Wands/Staves/Rods): {len(wands)} items")
    print(f"  Phase 6 (Misc Magic): {len(misc)} items")
    print(f"  Phase 7 (Special Weapons): {len(special)} items")

    # Save to file
    with open('/mnt/d/Development/aerthos/magic_items_phases_4_7.json', 'w') as f:
        json.dump(all_items, f, indent=2)
    print("\nSaved all phases to: magic_items_phases_4_7.json")

    # Save just the new items (phases 4-7)
    new_items = {}
    new_items.update(rings)
    new_items.update(wands)
    new_items.update(misc)
    new_items.update(special)

    with open('/mnt/d/Development/aerthos/magic_items_NEW_phases_4_7.json', 'w') as f:
        json.dump(new_items, f, indent=2)
    print(f"Saved NEW items (phases 4-7 only, {len(new_items)} items) to: magic_items_NEW_phases_4_7.json")

if __name__ == "__main__":
    main()
