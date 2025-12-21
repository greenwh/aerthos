** NOT FIXED - Selling items for 50% yields 0 gold:
This did not fix the issue.  
RESOLVED: Items now properly track gp_value from equipment.json.
- _create_item_from_name() now sets gp_value from cost_gp in JSON
- Properties list converted to dict format for consistency
- File modified: game_state.py

** Minor - special attacks have no effect:

Rats use disease bite but players don't get diseased.  Check special attacks.
Centipede, Giant injects toxic venom - deals poison damage!
Skeleton uses undead!
Skeleton uses immune_to_charm!
Grukk, Hobgoblin Chieftain uses command_presence!
Grukk, Hobgoblin Chieftain uses tactical_genius!
Cult Torturer uses intimidation!
Silas the Corrupt Merchant uses cunning_defense!
Silas's Elite Bodyguard uses loyal_unto_death!
Silas's Elite Bodyguard uses shield_wall!
Silas's Elite Bodyguard uses loyal_unto_death!
Bound Demon uses magic_resistance!
Duergar (Gray Dwarf) uses enlarge!
Duergar (Gray Dwarf) uses invisibility!
Duergar Elite Warrior uses infravision!
Duergar Dark Priest uses serpent_cult_powers!
Duergar Dark Priest uses turn_undead_reversed!

