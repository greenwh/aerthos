#!/usr/bin/env python3
"""
Script to complete Episode 1 and add the serpent medallion to the party leader's inventory.
This script fixes the issue where the player completed the dungeon but couldn't save due to
a KeyError in the character roster deserialization.
"""

import sys
from pathlib import Path

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.campaign.campaign_manager import CampaignManager
from aerthos.storage.character_roster import CharacterRoster
from aerthos.entities.player import Item

def main():
    """Complete Episode 1 and add the serpent medallion"""

    # Campaign ID (from the user's save file)
    campaign_id = "329dac52-01e2-4bba-bfa0-0355b31d8ae8"

    # Initialize managers
    campaign_mgr = CampaignManager()
    char_roster = CharacterRoster()

    print("Loading campaign...")
    campaign = campaign_mgr.load_campaign(campaign_id)

    # Check if episode is already completed
    if campaign.is_episode_completed("episode_01"):
        print("Episode 01 is already marked as complete.")
    else:
        print("Marking Episode 01 as complete...")

        # Define rewards from episode_01.json
        rewards = {
            'unlocks': ['episode_02'],
            'story_flags': ['found_serpent_medallion', 'goblin_threat_ended']
        }

        # Complete the episode
        campaign.complete_episode("episode_01", rewards)
        print("✓ Episode 01 marked as complete")
        print("✓ Episode 02 unlocked")
        print("✓ Story flags set: found_serpent_medallion, goblin_threat_ended")

    # Load party leader (Grim - character ID c1658b4c)
    print("\nLoading party leader (Grim)...")
    grim_id = "c1658b4c"
    grim = char_roster.load_character(character_id=grim_id)

    if grim is None:
        print(f"Error: Could not load character {grim_id}")
        return 1

    # Check if Grim already has the serpent medallion
    has_medallion = any(item.name == "Serpent Medallion" for item in grim.inventory.items)

    if has_medallion:
        print("Grim already has the Serpent Medallion in inventory.")
    else:
        print("Adding Serpent Medallion to Grim's inventory...")

        # Create the serpent medallion item
        serpent_medallion = Item(
            name="Serpent Medallion",
            item_type="quest_item",
            weight=0.5
        )

        # Add to inventory
        grim.inventory.add_item(serpent_medallion)
        print("✓ Serpent Medallion added to Grim's inventory")

    # Save changes
    print("\nSaving changes...")
    campaign_mgr.save_campaign(campaign)
    char_roster.save_character(grim, grim_id)

    print("\n✓ All changes saved successfully!")
    print("\nSummary:")
    print(f"  Episode 01: {'Complete' if campaign.is_episode_completed('episode_01') else 'Incomplete'}")
    print(f"  Episode 02: {'Unlocked' if campaign.is_episode_unlocked('episode_02') else 'Locked'}")
    print(f"  Story flags: {list(campaign.story_flags.keys())}")
    print(f"  Grim's inventory items: {len(grim.inventory.items)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
