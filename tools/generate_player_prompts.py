import json
import os

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("Loading game data...")
    try:
        races_data = load_json('aerthos/data/races.json')
        classes_data = load_json('aerthos/data/classes.json')
        armor_data = load_json('aerthos/data/armor.json')
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return

    prompts = []
    
    # Process each race
    for race_name, race_info in races_data.items():
        # Process each class
        for class_name, class_info in classes_data.items():
            
            # 1. Check Race Restrictions
            # races.json: "class_restrictions": ["Class1", "Class2"] means BANNED
            if class_name in race_info.get('class_restrictions', []):
                continue

            # 2. Determine Valid Armor for this Class
            valid_armors = []
            
            # Special handling for classes that typically wear no armor or robes
            if class_name in ["Magic-User", "Illusionist"]:
                valid_armors.append(("Wizard Robes", "robes"))
            elif class_name == "Monk":
                valid_armors.append(("Monk Robes", "monk_robes"))
            else:
                # Check armor.json for allowed classes
                # Iterate through all armor definitions
                found_armor = False
                if 'armor' in armor_data:
                    for armor_key, armor_def in armor_data['armor'].items():
                        allowed = armor_def.get('allowed_classes', [])
                        
                        # Special case: "Any" or explicit list
                        # In the provided JSON, it's a list: ["Fighter", ...]
                        if class_name in allowed:
                            valid_armors.append((armor_def['name'], armor_key))
                            found_armor = True
                            
                # If class can wear armor but none found (unlikely), or strictly for classes like Thief
                # that might have "leather_only" logic elsewhere but data says "allowed_classes".
                # Let's trust armor.json's allowed_classes list.
                
                # Add a "No Armor" / "Clothing" option for all classes? 
                # The user asked for "all combinations possible", usually implies valid equipment loadouts.
                # A Fighter in clothes is valid but rare. Let's stick to the armor list + robes for casters.

            # 3. Generate Prompts for each valid Race + Class + Armor combo
            for armor_name, armor_id in valid_armors:
                # Construct asset ID
                # Clean strings for filename: "Half-Orc" -> "half_orc"
                safe_race = race_name.lower().replace('-', '_').replace(' ', '_')
                safe_class = class_name.lower().replace('-', '_').replace(' ', '_')
                safe_armor = armor_id.lower().replace('-', '_').replace(' ', '_')
                
                asset_id = f"{safe_race}_{safe_class}_{safe_armor}"
                
                # Construct prompt
                # Add specific visual details based on race/class
                race_desc = race_info.get('description', '')
                class_desc = class_info.get('description', '')
                
                prompt_text = (
                    f"Full body fantasy character portrait of a {race_name} {class_name} wearing {armor_name}. "
                    f"Visual style: Realistic fantasy oil painting, detailed, cinematic lighting. "
                    f"Background: A dark, atmospheric dungeon environment. "
                    f"Character details: {race_desc}. {class_desc}."
                )

                prompt = {
                    "asset_id": asset_id,
                    "name": f"{race_name} {class_name} - {armor_name}",
                    "type": "PlayerCharacter",
                    "visual_tags": ["character", "portrait", race_name, class_name, armor_name],
                    "image_prompt": prompt_text,
                    "view_context": "Player Character Generation"
                }
                
                prompts.append(prompt)

    # Save output
    output_dir = 'docs/images/players'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'player_prompts.json')
    
    with open(output_file, 'w') as f:
        json.dump(prompts, f, indent=2)
        
    print(f"Generated {len(prompts)} prompts in {output_file}")

if __name__ == "__main__":
    main()
