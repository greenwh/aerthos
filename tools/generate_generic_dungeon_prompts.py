import json
import os

def generate_generic_prompts():
    output_dir = 'docs/images/world'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "generic_dungeon_images.json")
    
    prompts = []
    
    # Define generic scenes
    scenes = [
        ("corridor_stone", "A long, dark stone corridor in a dungeon. Torchlight flickers on the damp walls."),
        ("corridor_arched", "An arched hallway made of ancient brick. Shadows dance in the distance."),
        ("corridor_cobwebs", "A narrow dungeon passage filled with thick cobwebs. Dusty and abandoned."),
        ("intersection_4way", "A four-way intersection in a stone dungeon. Dark passages lead in all directions."),
        ("intersection_t", "A T-junction in a dungeon corridor. The stone floor is worn smooth."),
        ("room_empty_stone", "An empty square room with stone walls and floor. Cold and silent."),
        ("room_columns", "A large dungeon chamber supported by thick stone columns. Debris litters the floor."),
        ("room_rubble", "A ruined dungeon room filled with piles of rubble and collapsed masonry."),
        ("room_pool", "A dark dungeon chamber with a stagnant pool of black water in the center."),
        ("door_iron", "A heavy iron-reinforced door set into a stone archway. Rusty and imposing."),
        ("door_wooden", "A rotting wooden door with iron hinges, slightly ajar."),
        ("stairs_down", "A stone staircase spiraling down into the darkness. Damp and slippery."),
        ("stairs_up", "A narrow flight of stone steps leading upward, covered in moss."),
        ("dead_end", "A dead end in a dungeon corridor. The wall is solid stone."),
        ("alcove", "A small alcove in the dungeon wall, perhaps for a statue that is no longer there."),
        ("bridge_chasm", "A narrow stone bridge spanning a dark chasm in the dungeon."),
        ("prison_cells", "A row of rusted iron bars forming prison cells in a damp dungeon block."),
        ("torchlit_hall", "A hallway lined with sconces, though only a few torches still burn."),
        ("ancient_statue", "A crumbling statue of a forgotten deity standing in a dusty corner."),
        ("collapsed_tunnel", "A tunnel blocked by a massive cave-in of rocks and earth.")
    ]
    
    for i, (key, desc) in enumerate(scenes):
        prompts.append({
            "asset_id": f"generic_dungeon_{key}",
            "name": f"Generic Dungeon - {key.replace('_', ' ').title()}",
            "type": "Location",
            "visual_tags": ["fantasy", "dungeon", "generic", "interior", "realistic"],
            "image_prompt": f"Fantasy concept art of {desc} Realistic fantasy oil painting style, detailed textures, atmospheric lighting.",
            "view_context": "Generic dungeon fallback image"
        })
            
    with open(output_file, 'w') as f:
        json.dump(prompts, f, indent=2)
        print(f"Generated {output_file} with {len(prompts)} prompts.")

if __name__ == "__main__":
    generate_generic_prompts()
