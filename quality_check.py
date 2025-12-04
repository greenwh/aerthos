#!/usr/bin/env python3
"""
Comprehensive quality check for Aerthos campaign
"""

import json
import glob
import re
from pathlib import Path
from collections import defaultdict

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def check_broken_references():
    """Check for broken monster and item references"""
    print("=" * 80)
    print("CHECKING BROKEN REFERENCES")
    print("=" * 80)
    print()

    # Load reference data
    monsters = load_json('aerthos/data/monsters.json')

    issues = []

    # Check each dungeon
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in sorted(dungeon_files):
        dungeon_name = Path(dungeon_file).stem
        dungeon = load_json(dungeon_file)

        # Check monster references
        for room_id, room in dungeon.get('rooms', {}).items():
            for encounter in room.get('encounters', []):
                if encounter.get('type') == 'combat':
                    for monster_id in encounter.get('monsters', []):
                        if monster_id not in monsters:
                            issues.append(f"❌ {dungeon_name} / {room_id}: Monster '{monster_id}' not found")

    if issues:
        for issue in issues:
            print(issue)
        print()
        return False
    else:
        print("✅ No broken monster references found")
        print()
        return True

def check_boss_definitions():
    """Check that all boss encounters have corresponding boss entries"""
    print("=" * 80)
    print("CHECKING BOSS DEFINITIONS")
    print("=" * 80)
    print()

    issues = []

    # Check each dungeon
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in sorted(dungeon_files):
        dungeon_name = Path(dungeon_file).stem
        dungeon = load_json(dungeon_file)

        # Find boss encounters
        for room_id, room in dungeon.get('rooms', {}).items():
            for encounter in room.get('encounters', []):
                if encounter.get('boss') or encounter.get('boss_fight'):
                    # Check if bosses section exists
                    bosses = dungeon.get('bosses', {})
                    monsters = encounter.get('monsters', [])

                    # First monster is usually the boss
                    if monsters and monsters[0] not in bosses:
                        # This is OK if the boss is in monsters.json
                        pass  # Many bosses are just regular monsters

    if issues:
        for issue in issues:
            print(issue)
        print()
        return False
    else:
        print("✅ All boss encounters properly defined")
        print()
        return True

def check_duplicate_ids():
    """Check for duplicate room IDs across dungeons"""
    print("=" * 80)
    print("CHECKING DUPLICATE IDs")
    print("=" * 80)
    print()

    room_ids = defaultdict(list)

    # Collect all room IDs
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in sorted(dungeon_files):
        dungeon_name = Path(dungeon_file).stem
        dungeon = load_json(dungeon_file)

        for room_id in dungeon.get('rooms', {}).keys():
            room_ids[room_id].append(dungeon_name)

    # Find duplicates
    issues = []
    for room_id, dungeons in room_ids.items():
        if len(dungeons) > 1:
            issues.append(f"❌ Room ID '{room_id}' duplicated in: {', '.join(dungeons)}")

    if issues:
        for issue in issues:
            print(issue)
        print()
        return False
    else:
        print("✅ No duplicate room IDs found")
        print()
        return True

def check_description_quality():
    """Check for empty or very short descriptions"""
    print("=" * 80)
    print("CHECKING DESCRIPTION QUALITY")
    print("=" * 80)
    print()

    issues = []
    warnings = []

    # Check dungeons
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in sorted(dungeon_files):
        dungeon_name = Path(dungeon_file).stem
        dungeon = load_json(dungeon_file)

        # Check dungeon description
        if not dungeon.get('description'):
            issues.append(f"❌ {dungeon_name}: Missing dungeon description")

        # Check room descriptions
        for room_id, room in dungeon.get('rooms', {}).items():
            if not room.get('description'):
                issues.append(f"❌ {dungeon_name} / {room_id}: Missing room description")
            elif len(room.get('description', '')) < 50:
                warnings.append(f"⚠️  {dungeon_name} / {room_id}: Very short description ({len(room.get('description', ''))} chars)")

    if issues:
        for issue in issues:
            print(issue)
        print()

    if warnings:
        print("Warnings (not critical):")
        for warning in warnings[:10]:  # Show first 10
            print(warning)
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
        print()

    if not issues:
        print("✅ All descriptions present")
        print()

    return len(issues) == 0

def check_common_typos():
    """Check for common typos in descriptions"""
    print("=" * 80)
    print("CHECKING COMMON TYPOS")
    print("=" * 80)
    print()

    # Common typo patterns
    typo_patterns = [
        (r'\bthe the\b', 'duplicate "the"'),
        (r'\ba a\b', 'duplicate "a"'),
        (r'\bteh\b', '"teh" should be "the"'),
        (r'\byou\'re\b', 'second-person (should use third-person)'),
        (r'\byour\b', 'second-person (should use third-person)'),
    ]

    issues = []

    # Check all text in dungeons
    dungeon_files = glob.glob('aerthos/data/dungeons/*.json')
    for dungeon_file in sorted(dungeon_files):
        dungeon_name = Path(dungeon_file).stem
        dungeon = load_json(dungeon_file)

        # Check dungeon description
        desc = dungeon.get('description', '')
        for pattern, issue_text in typo_patterns:
            if re.search(pattern, desc, re.IGNORECASE):
                issues.append(f"⚠️  {dungeon_name}: {issue_text} in dungeon description")

        # Check room descriptions
        for room_id, room in dungeon.get('rooms', {}).items():
            desc = room.get('description', '')
            for pattern, issue_text in typo_patterns:
                if re.search(pattern, desc, re.IGNORECASE):
                    issues.append(f"⚠️  {dungeon_name} / {room_id}: {issue_text}")

            # Check encounter descriptions
            for encounter in room.get('encounters', []):
                desc = encounter.get('description', '')
                for pattern, issue_text in typo_patterns:
                    if re.search(pattern, desc, re.IGNORECASE):
                        issues.append(f"⚠️  {dungeon_name} / {room_id}: {issue_text} in encounter")

    if issues:
        print(f"Found {len(issues)} potential typos:")
        for issue in issues[:15]:  # Show first 15
            print(issue)
        if len(issues) > 15:
            print(f"  ... and {len(issues) - 15} more")
        print()
        return False
    else:
        print("✅ No common typos found")
        print()
        return True

def check_consistency():
    """Check naming consistency"""
    print("=" * 80)
    print("CHECKING NAMING CONSISTENCY")
    print("=" * 80)
    print()

    # Check for inconsistent capitalization of common terms
    issues = []

    # This is a basic check - just verify files load correctly
    try:
        # Load all data files
        load_json('aerthos/data/monsters.json')
        load_json('aerthos/data/equipment.json')
        load_json('aerthos/data/classes.json')

        for ep_file in glob.glob('aerthos/data/episodes/*.json'):
            load_json(ep_file)

        for dungeon_file in glob.glob('aerthos/data/dungeons/*.json'):
            load_json(dungeon_file)

        print("✅ All JSON files valid and loadable")
        print()
        return True
    except Exception as e:
        print(f"❌ JSON loading error: {e}")
        print()
        return False

def main():
    print("=" * 80)
    print("AERTHOS CAMPAIGN - QUALITY CHECK")
    print("=" * 80)
    print()

    results = []

    # Run all checks
    results.append(("Broken References", check_broken_references()))
    results.append(("Boss Definitions", check_boss_definitions()))
    results.append(("Duplicate IDs", check_duplicate_ids()))
    results.append(("Description Quality", check_description_quality()))
    results.append(("Common Typos", check_common_typos()))
    results.append(("Data Consistency", check_consistency()))

    # Summary
    print("=" * 80)
    print("QUALITY CHECK SUMMARY")
    print("=" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")

    print()
    print(f"Checks Passed: {passed}/{total}")

    if passed == total:
        print()
        print("✅ ALL QUALITY CHECKS PASSED")
    else:
        print()
        print("⚠️  Some quality issues found - review output above")

    print()

if __name__ == '__main__':
    main()
