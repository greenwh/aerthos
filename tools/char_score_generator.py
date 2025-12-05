#!/usr/bin/env python3
"""
AD&D 1st Edition Ability Score Roller
Rolls ability scores and places them optimally based on character class
"""

import random
from typing import List, Tuple, Dict

# Optimal ability score priority for each class (most important to least)
CLASS_PRIORITIES = {
    'fighter': ['Strength', 'Constitution', 'Dexterity', 'Charisma', 'Wisdom', 'Intelligence'],
    'paladin': ['Strength', 'Charisma', 'Constitution', 'Wisdom', 'Dexterity', 'Intelligence'],
    'ranger': ['Strength', 'Constitution', 'Wisdom', 'Dexterity', 'Intelligence', 'Charisma'],
    'magic-user': ['Intelligence', 'Dexterity', 'Constitution', 'Wisdom', 'Strength', 'Charisma'],
    'illusionist': ['Intelligence', 'Dexterity', 'Constitution', 'Wisdom', 'Strength', 'Charisma'],
    'cleric': ['Wisdom', 'Constitution', 'Strength', 'Charisma', 'Dexterity', 'Intelligence'],
    'druid': ['Wisdom', 'Constitution', 'Charisma', 'Dexterity', 'Strength', 'Intelligence'],
    'thief': ['Dexterity', 'Intelligence', 'Constitution', 'Strength', 'Wisdom', 'Charisma'],
    'assassin': ['Dexterity', 'Strength', 'Intelligence', 'Constitution', 'Wisdom', 'Charisma'],
    'monk': ['Strength', 'Wisdom', 'Dexterity', 'Constitution', 'Intelligence', 'Charisma'],
}


def roll_ability_score() -> int:
    """Roll 3d6 for a single ability score"""
    return sum(random.randint(1, 6) for _ in range(3))


def roll_exceptional_strength() -> int:
    """Roll percentile dice for exceptional strength (00-99, displayed as 01-00)"""
    roll = random.randint(1, 100)
    return roll if roll != 100 else 0  # 100 is displayed as 00


def roll_six_scores() -> List[int]:
    """Roll six ability scores"""
    return sorted([roll_ability_score() for _ in range(6)], reverse=True)


def assign_scores(scores: List[int], char_class: str) -> Dict[str, int]:
    """Assign rolled scores to abilities based on class priorities"""
    priorities = CLASS_PRIORITIES[char_class]
    return {ability: score for ability, score in zip(priorities, scores)}


def display_character(char_class: str, abilities: Dict[str, int], exceptional_str: int = None) -> None:
    """Display a character's ability scores"""
    print(f"\n{char_class.upper()}:")
    
    # Display in standard order
    standard_order = ['Strength', 'Intelligence', 'Wisdom', 'Dexterity', 'Constitution', 'Charisma']
    
    for ability in standard_order:
        score = abilities[ability]
        if ability == 'Strength' and exceptional_str is not None and score == 18:
            print(f"  {ability:13s}: {score}/{'%02d' % exceptional_str if exceptional_str != 0 else '00'}")
        else:
            print(f"  {ability:13s}: {score}")


def display_all_characters(characters: List[Tuple[str, Dict[str, int], int]]) -> None:
    """Display all created characters in a table"""
    if not characters:
        return
    
    print("\n" + "="*80)
    print("CREATED CHARACTERS")
    print("="*80)
    
    # Header
    print(f"{'Class':<15} {'STR':<8} {'INT':<5} {'WIS':<5} {'DEX':<5} {'CON':<5} {'CHA':<5}")
    print("-"*80)
    
    # Each character
    for char_class, abilities, exceptional_str in characters:
        str_display = str(abilities['Strength'])
        if exceptional_str is not None and abilities['Strength'] == 18:
            str_display = f"18/{'%02d' % exceptional_str if exceptional_str != 0 else '00'}"
        
        print(f"{char_class:<15} {str_display:<8} {abilities['Intelligence']:<5} "
              f"{abilities['Wisdom']:<5} {abilities['Dexterity']:<5} "
              f"{abilities['Constitution']:<5} {abilities['Charisma']:<5}")
    
    print("="*80 + "\n")


def get_primary_ability(char_class: str) -> str:
    """Get the primary ability for a given class"""
    priorities = CLASS_PRIORITIES[char_class]
    return priorities[0]


def get_class_choice() -> str:
    """Get valid class choice from user"""
    print("\nAvailable classes:")
    classes = list(CLASS_PRIORITIES.keys())
    for i, cls in enumerate(classes, 1):
        print(f"  {i}. {cls.title()}")
    
    while True:
        choice = input("\nEnter class name or number (or 'quit' to exit): ").strip().lower()
        
        if choice in ['quit', 'q', 'exit', 'done']:
            return None
        
        # Check if it's a number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(classes):
                return classes[idx]
        
        # Check if it's a class name
        if choice in classes:
            return choice
        
        print("Invalid choice. Please try again.")


def get_minimum_score(prompt: str) -> int:
    """Get minimum ability score from user"""
    while True:
        try:
            min_score = input(f"\n{prompt} (3-18, or press Enter for no minimum): ").strip()
            
            if min_score == "":
                return 3  # No minimum, accept anything
            
            min_score = int(min_score)
            if 3 <= min_score <= 18:
                return min_score
            else:
                print("Score must be between 3 and 18.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Main program loop"""
    print("="*80)
    print("AD&D 1st Edition Ability Score Roller")
    print("="*80)
    
    characters = []
    
    while True:
        # Get class choice
        char_class = get_class_choice()
        if char_class is None:
            break
        
        # Get minimum primary ability score
        primary_ability = get_primary_ability(char_class)
        print(f"\nPrimary ability for {char_class.title()}: {primary_ability}")
        min_primary = get_minimum_score(f"Minimum {primary_ability} score")
        min_any = get_minimum_score("Minimum score for any ability")
        
        # Build description of requirements
        requirements = []
        if min_primary > 3:
            requirements.append(f"{primary_ability} >= {min_primary}")
        if min_any > 3:
            requirements.append(f"all abilities >= {min_any}")
        
        if requirements:
            print(f"\nRolling until {' and '.join(requirements)}...", end="", flush=True)
        
        while True:
            # Roll scores and assign - keep rolling until minimums are met
            roll_count = 0
            while True:
                scores = roll_six_scores()
                abilities = assign_scores(scores, char_class)
                roll_count += 1
                
                # Check if primary ability meets minimum
                if abilities[primary_ability] < min_primary:
                    continue
                
                # Check if all abilities meet minimum
                if min(abilities.values()) < min_any:
                    continue
                
                # All requirements met
                break
            
            if requirements:
                print(f" done! ({roll_count} roll{'s' if roll_count != 1 else ''} needed)")
            
            # Check for exceptional strength
            exceptional_str = None
            if char_class in ['fighter', 'paladin', 'ranger'] and abilities['Strength'] == 18:
                exceptional_str = roll_exceptional_strength()
            
            # Display the character
            print("\nRolled scores (sorted):", scores)
            display_character(char_class, abilities, exceptional_str)
            
            # Ask to keep or reroll
            while True:
                choice = input("\n(S)ave this character, (R)eroll, or (C)ancel this class? ").strip().lower()
                
                if choice in ['s', 'save']:
                    characters.append((char_class.title(), abilities, exceptional_str))
                    print(f"\n✓ {char_class.title()} saved!")
                    display_all_characters(characters)
                    break
                elif choice in ['r', 'reroll', 'roll']:
                    req_text = f" (with {' and '.join(requirements)})" if requirements else ""
                    print(f"\nRerolling{req_text}...")
                    break
                elif choice in ['c', 'cancel']:
                    print("\nCancelled.")
                    break
                else:
                    print("Please enter S, R, or C.")
            
            # Break out of reroll loop if saved or cancelled
            if choice in ['s', 'save', 'c', 'cancel']:
                break
        
        # Ask if they want to create another character
        if choice in ['s', 'save']:
            another = input("\nCreate another character? (Y/N): ").strip().lower()
            if another not in ['y', 'yes']:
                break
    
    # Final summary
    if characters:
        print("\n" + "="*80)
        print("FINAL CHARACTER ROSTER")
        print("="*80)
        display_all_characters(characters)
        print(f"Total characters created: {len(characters)}")
    else:
        print("\nNo characters created.")
    
    print("\nThanks for using the AD&D Ability Score Roller!")


if __name__ == "__main__":
    main()
