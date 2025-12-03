import json
import os
import glob

def generate_prompts():
    os.makedirs('docs/images/world', exist_ok=True)
    
    # 1. Process All Dungeons
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in dungeon_files:
        filename = os.path.basename(dungeon_file)
        dungeon_id = os.path.splitext(filename)[0]
        output_file = f"docs/images/world/{dungeon_id}_images.json"
        
        try:
            with open(dungeon_file, 'r') as f:
                dungeon_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping {dungeon_file}: Invalid JSON")
            continue
            
        dungeon_prompts = []
        
        # Dungeon Overview/Map (if name and description exist)
        if 'name' in dungeon_data and 'description' in dungeon_data:
            dungeon_prompts.append({
                "asset_id": f"{dungeon_id}_map",
                "name": "Map of " + dungeon_data['name'],
                "type": "Map",
                "visual_tags": ["fantasy map", "dungeon", "blueprint"],
                "image_prompt": f"A fantasy map of {dungeon_data['name']}. {dungeon_data['description']}. The map should look like aged parchment or a magically projected hologram.",
                "view_context": f"{dungeon_file}"
            })

        for room_id, room in dungeon_data.get('rooms', {}).items():
            # Handle cases where room might be just a string (though unlikely in this schema, good to be safe) or missing fields
            if not isinstance(room, dict): continue
            
            title = room.get('title', room.get('name', f"Room {room_id}"))
            desc = room.get('description', '')
            light = room.get('light_level', 'dim')
            
            prompt = {
                "asset_id": f"{dungeon_id}_{room_id}",
                "name": title,
                "type": "Location",
                "visual_tags": ["fantasy", "dungeon", "interior", f"{light} lighting"],
                "image_prompt": f"Fantasy concept art of {title}. {desc} The scene is lit with {light} lighting. Visual style: Realistic fantasy oil painting.",
                "view_context": f"{dungeon_file} - Room: {room_id}"
            }
            if 'tags' in room:
                prompt['visual_tags'].extend(room['tags'])
                
            dungeon_prompts.append(prompt)
            
        with open(output_file, 'w') as f:
            json.dump(dungeon_prompts, f, indent=2)
            print(f"Generated {output_file}")

    # 2. Process All Cities
    city_files = glob.glob('aerthos/data/cities/*.json')
    for city_file in city_files:
        filename = os.path.basename(city_file)
        city_id = os.path.splitext(filename)[0]
        output_file = f"docs/images/world/{city_id}_images.json"
        
        try:
            with open(city_file, 'r') as f:
                city_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping {city_file}: Invalid JSON")
            continue
            
        city_prompts = []
        
        # City Overview
        if 'name' in city_data and 'description' in city_data:
            city_prompts.append({
                "asset_id": city_data.get('id', city_id),
                "name": city_data['name'],
                "type": "City",
                "visual_tags": ["city", "fantasy", "exterior"],
                "image_prompt": f"Fantasy concept art of {city_data['name']}. {city_data['description']}",
                "view_context": f"{city_file}"
            })
        
        # City Shops/Locations
        for shop in city_data.get('shops', []) or []:
            shop_id = shop.get('id', 'unknown')
            shop_name = shop.get('name', 'Unknown Shop')
            shop_specialty = shop.get('specialty', 'General goods')
            
            city_prompts.append({
                "asset_id": f"{city_data.get('id', city_id)}_{shop_id}",
                "name": shop_name,
                "type": "Shop",
                "visual_tags": ["shop", "fantasy", "interior", "merchant"],
                "image_prompt": f"Interior of a fantasy shop named {shop_name}. Specialty: {shop_specialty}. Detailed fantasy interior, warm lighting.",
                "view_context": f"{city_file} - Shop: {shop_id}"
            })
            
        inn = city_data.get('inn')
        if inn and isinstance(inn, dict):
            inn_id = inn.get('id', 'inn')
            inn_name = inn.get('name', 'The Inn')
            inn_desc = inn.get('description', 'A cozy inn.')
            
            city_prompts.append({
                "asset_id": f"{city_data.get('id', city_id)}_{inn_id}",
                "name": inn_name,
                "type": "Inn",
                "visual_tags": ["inn", "tavern", "fantasy", "interior"],
                "image_prompt": f"Interior of a fantasy tavern named {inn_name}. {inn_desc} Warm hearth fire, wooden tables, lively atmosphere.",
                "view_context": f"{city_file} - Inn: {inn_id}"
            })

        temple = city_data.get('temple')
        if temple and isinstance(temple, dict):
            temple_id = temple.get('id', 'temple')
            temple_name = temple.get('name', 'The Temple')
            deity = temple.get('deity', 'a god')
            
            city_prompts.append({
                "asset_id": f"{city_data.get('id', city_id)}_{temple_id}",
                "name": temple_name,
                "type": "Temple",
                "visual_tags": ["temple", "fantasy", "shrine", "religious"],
                "image_prompt": f"A fantasy shrine or temple named {temple_name}, dedicated to {deity}. Peaceful, divine atmosphere.",
                "view_context": f"{city_file} - Temple: {temple_id}"
            })

        # NPCs
        for npc_id, npc in city_data.get('npcs', {}).items():
            npc_name = npc.get('name', 'NPC')
            npc_role = npc.get('role', 'Villager')
            npc_desc = npc.get('description', '')
            
            city_prompts.append({
                "asset_id": f"{city_data.get('id', city_id)}_npc_{npc_id}",
                "name": npc_name,
                "type": "NPC",
                "visual_tags": ["character", "portrait", "fantasy"],
                "image_prompt": f"Fantasy character portrait of {npc_name}, {npc_role}. {npc_desc}",
                "view_context": f"{city_file} - NPC: {npc_id}"
            })

        with open(output_file, 'w') as f:
            json.dump(city_prompts, f, indent=2)
            print(f"Generated {output_file}")

    # 3. Generic Shops (unchanged, just re-writing to ensure it exists)
    with open('aerthos/data/shops.json', 'r') as f:
        shops_data = json.load(f)
        
    shop_prompts = []
    for shop_key, shop in shops_data.items():
        shop_prompts.append({
            "asset_id": f"generic_shop_{shop_key}",
            "name": shop['name'],
            "type": "Shop",
            "visual_tags": ["shop", "fantasy", "interior", shop['type']],
            "image_prompt": f"Interior of a fantasy {shop['type']} shop named {shop['name']}. {shop['description']}.",
            "view_context": f"aerthos/data/shops.json - Shop: {shop_key}"
        })
        
    with open('docs/images/world/shops_images.json', 'w') as f:
        json.dump(shop_prompts, f, indent=2)
        print("Generated docs/images/world/shops_images.json")

if __name__ == "__main__":
    generate_prompts()
