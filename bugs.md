Rats use disease bite but players don't get diseased.  Check special attacks.

● ⚠️ Found the Real Bug: Magic Bonus Applied TWICE!

  You're absolutely right - there's a magic bonus problem! Here's what I found:

  The Issue:

  The armor.json database stores the WRONG AC values for magic armor.

  Compare these two entries:
  - Normal Plate Mail: "ac": 3 (base AC)
  - Plate Mail +1: "ac": 2 (effective AC with bonus already applied)

  How the Code Works:

  The Armor class has a get_effective_ac() method (player.py:55-57):
  def get_effective_ac(self) -> int:
      """Get effective AC including magic bonus"""
      return self.ac - self.magic_bonus

  This means the code expects:
  - armor.ac = BASE AC (3 for plate mail)
  - armor.magic_bonus = bonus (1 for +1)
  - get_effective_ac() = 3 - 1 = 2 ✅

  What's Actually Happening:

  With current database (ac=2, magic_bonus=1):
  - get_effective_ac() returns: 2 - 1 = 1 ❌ (WRONG! Magic bonus applied twice!)

  With user's character (ac=3, magic_bonus=1):
  - get_effective_ac() returns: 3 - 1 = 2 ✅ (CORRECT!)

  Your character shows ac: 3 because it was created before my fix, using the old parsing code that correctly set the base AC to 3.

  The Fix Needed:

  The armor.json database needs all magic armor AC values changed to BASE AC, not effective AC:

  | Armor             | Current AC  | Should Be | Magic Bonus |
  |-------------------|-------------|-----------|-------------|
  | Leather +1/+2     | 7, 6        | 8         | 1, 2        |
  | Chain +1/+2/+3    | 4, 3, 2     | 5         | 1, 2, 3     |
  | Plate +1/+2/+3/+4 | 2, 1, 0, -1 | 3         | 1, 2, 3, 4  |

  This way get_effective_ac() will correctly apply the magic bonus once.

  Summary: Your character with ac:3 is actually CORRECT. The database is wrong - it pre-calculated the magic bonus into the AC field, but the code expects to calculate it dynamically.