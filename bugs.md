Rats use disease bite but players don't get diseased.  Check special attacks.

Most spells not implemented (23/333 currently implemented - see SPELL_FIXES_SUMMARY.md for list)

✅ FIXED (2025-12-14): Spell slot progression issue
- cure serious wounds and cure critical wounds both said "You don't have any empty level 1 spell slots!" when I tried to memorize
- check spell slots, i.e getting "no level 4 slots" when trying kevel 5 memorization
- Root cause: classes.json missing spell_slots_level_X for levels 2-10
- Fix: Added proper AD&D 1e spell progression for all caster classes
- See SPELL_FIXES_SUMMARY.md for details
