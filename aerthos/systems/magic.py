"""
Vancian Magic System - AD&D 1e spell memorization and casting
"""

import random
from typing import Dict, List, Optional
from ..entities.player import PlayerCharacter, Spell
from ..entities.character import Character
from ..systems.saving_throws import SavingThrowResolver


class MagicSystem:
    """Handles spell memorization and casting"""

    def __init__(self):
        self.save_resolver = SavingThrowResolver()

    def cast_spell(self, caster: PlayerCharacter, spell_name: str,
                   targets: List[Character]) -> Dict:
        """
        Cast a memorized spell

        Args:
            caster: Character casting the spell
            spell_name: Name of the spell
            targets: List of potential targets

        Returns:
            Dict with: success, narrative, effect_results
        """

        # Check if spell is memorized and available
        spell = caster.use_spell_slot(spell_name)

        if not spell:
            return {
                'success': False,
                'narrative': f"You don't have {spell_name} memorized or it's already been cast!",
                'effect_results': {}
            }

        # Execute spell effect
        effect_results = self._execute_spell_effect(spell, caster, targets)

        return {
            'success': True,
            'narrative': f"You cast {spell.name}! {effect_results['narrative']}",
            'effect_results': effect_results
        }

    def _execute_spell_effect(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """
        Execute spell-specific logic

        Args:
            spell: The spell being cast
            caster: Character casting the spell
            targets: List of potential targets

        Returns:
            Dict with narrative and mechanical results
        """

        # Dispatch to spell-specific handlers
        spell_key = spell.name.lower().replace(' ', '_').replace('-', '_')

        handlers = {
            'sleep': self._spell_sleep,
            'magic_missile': self._spell_magic_missile,
            'cure_light_wounds': self._spell_cure_light_wounds,
            'protection_from_evil': self._spell_protection_from_evil,
            'detect_magic': self._spell_detect_magic,
            'burning_hands': self._spell_burning_hands,
            'charm_person': self._spell_charm_person,
            'fireball': self._spell_fireball,
            'lightning_bolt': self._spell_lightning_bolt,
            'cone_of_cold': self._spell_cone_of_cold,
            'cure_serious_wounds': self._spell_cure_serious_wounds,
            'heal': self._spell_heal,
            'haste': self._spell_haste,
            'slow': self._spell_slow,
            'bless': self._spell_bless,
            'web': self._spell_web,
            'hold_person': self._spell_hold_person,
            'invisibility': self._spell_invisibility,
            'knock': self._spell_knock,
            'find_traps': self._spell_find_traps,
            'cloudkill': self._spell_cloudkill,
            'chain_lightning': self._spell_chain_lightning,
            'raise_dead': self._spell_raise_dead
        }

        handler = handlers.get(spell_key)
        if handler:
            result = handler(spell, caster, targets)
            return result
        else:
            return {
                'narrative': f"{spell.name} fizzles - effect not yet implemented.",
                'affected': []
            }

    def _spell_sleep(self, spell: Spell, caster: PlayerCharacter,
                     targets: List[Character]) -> Dict:
        """Sleep spell: affects 2d4 HD of creatures"""

        total_hd = random.randint(2, 8)  # 2d4

        # Sort targets by level/HD (lowest first)
        sorted_targets = sorted(targets, key=lambda t: t.level)

        affected = []
        hd_count = 0

        for target in sorted_targets:
            # Check immunity
            if hasattr(target, 'is_immune_to') and target.is_immune_to('sleep'):
                continue

            # Check if we have enough HD left
            if hd_count + target.level <= total_hd and target.is_alive:
                target.add_condition('sleeping')
                affected.append(target.name)
                hd_count += target.level

        if affected:
            narrative = f"The following creatures fall into a magical slumber: {', '.join(affected)}"
        else:
            narrative = "The spell fails to affect any creatures."

        return {
            'narrative': narrative,
            'affected': affected,
            'hd_affected': hd_count
        }

    def _spell_magic_missile(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Magic Missile: 1d4+1 damage per missile, auto-hit"""

        # Number of missiles based on caster level
        num_missiles = 1 + (caster.level - 1) // 2
        num_missiles = min(5, num_missiles)  # Max 5 missiles

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target!",
                'affected': [],
                'total_damage': 0
            }

        target = targets[0]  # Magic missile targets one creature
        total_damage = 0

        for i in range(num_missiles):
            damage = random.randint(1, 4) + 1
            total_damage += damage

        target.take_damage(total_damage)

        narrative = f"{num_missiles} glowing missile{'s' if num_missiles > 1 else ''} "
        narrative += f"strike {target.name} for {total_damage} damage!"

        if not target.is_alive:
            narrative += f" {target.name} is slain!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'total_damage': total_damage
        }

    def _spell_cure_light_wounds(self, spell: Spell, caster: PlayerCharacter,
                                 targets: List[Character]) -> Dict:
        """Cure Light Wounds: heal 1d8 HP"""

        if not targets:
            return {
                'narrative': "No target to heal!",
                'affected': [],
                'healing': 0
            }

        target = targets[0]
        healing = random.randint(1, 8)

        old_hp = target.hp_current
        target.heal(healing)
        actual_healing = target.hp_current - old_hp

        narrative = f"{target.name} is healed for {actual_healing} HP!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'healing': actual_healing
        }

    def _spell_protection_from_evil(self, spell: Spell, caster: PlayerCharacter,
                                   targets: List[Character]) -> Dict:
        """Protection from Evil: +2 AC and saves vs evil"""

        if not targets:
            target = caster
        else:
            target = targets[0]

        target.add_condition('protected_from_evil')
        # In a full implementation, this would give +2 AC and save bonuses

        narrative = f"{target.name} is surrounded by a protective aura!"

        return {
            'narrative': narrative,
            'affected': [target.name]
        }

    def _spell_detect_magic(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Detect Magic: reveals magical auras"""

        # In the game context, this would check for magic items in room/inventory
        narrative = "Your eyes glow with eldritch sight. You can sense magical auras..."

        return {
            'narrative': narrative,
            'affected': [],
            'duration': 2 * caster.level  # rounds
        }

    def _spell_burning_hands(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Burning Hands: cone of fire, 1d3+1 per level"""

        damage_per_target = caster.level + random.randint(1, 3)

        affected = []
        for target in targets:
            if target.is_alive:
                # Saving throw for half damage
                save_result = self.save_resolver.save_for_half_damage(
                    target, damage_per_target, 'spell'
                )
                affected.append(f"{target.name} ({save_result['final_damage']} dmg)")

        narrative = f"A cone of flame erupts from your hands! {', '.join(affected)}"

        return {
            'narrative': narrative,
            'affected': affected
        }

    def _spell_charm_person(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Charm Person: make target friendly"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target!",
                'affected': []
            }

        target = targets[0]

        # Check if target is person (humanoid)
        if target.size not in ['S', 'M']:
            return {
                'narrative': f"{target.name} is not a person - spell fails!",
                'affected': []
            }

        # Saving throw
        save_result = self.save_resolver.make_save(target, 'spell')

        if save_result['success']:
            narrative = f"{target.name} resists the charm!"
        else:
            target.add_condition('charmed')
            narrative = f"{target.name} is charmed! They see you as a trusted friend."

        return {
            'narrative': narrative,
            'affected': [target.name] if not save_result['success'] else []
        }

    def _spell_fireball(self, spell: Spell, caster: PlayerCharacter,
                        targets: List[Character]) -> Dict:
        """Fireball: Explodes for 1d6 damage per caster level (max 10d6), save for half"""

        # Calculate damage: 1d6 per caster level, max 10d6
        num_dice = min(caster.level, 10)
        total_damage = sum(random.randint(1, 6) for _ in range(num_dice))

        if not targets:
            return {
                'narrative': "The fireball explodes harmlessly in the air!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets in area (20-foot radius)
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                # Saving throw for half damage
                save_result = self.save_resolver.save_for_half_damage(
                    target, total_damage, 'spell'
                )

                final_damage = save_result['final_damage']
                saved = save_result['success']

                # Check if target died
                if not target.is_alive:
                    affected.append(f"{target.name} ({final_damage} dmg - SLAIN!)")
                    total_kills += 1
                else:
                    save_str = " (saved)" if saved else ""
                    affected.append(f"{target.name} ({final_damage} dmg{save_str})")

        # Build narrative
        narrative = f"A massive fireball explodes for {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n💀 {total_kills} {'enemy' if total_kills == 1 else 'enemies'} slain!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills
        }

    def _spell_lightning_bolt(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """Lightning Bolt: Line of electricity, 1d6 damage per caster level (max 10d6), save for half"""

        # Calculate damage: 1d6 per caster level, max 10d6
        num_dice = min(caster.level, 10)
        total_damage = sum(random.randint(1, 6) for _ in range(num_dice))

        if not targets:
            return {
                'narrative': "The lightning bolt crackles through empty air!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets in line
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                # Saving throw for half damage
                save_result = self.save_resolver.save_for_half_damage(
                    target, total_damage, 'spell'
                )

                final_damage = save_result['final_damage']
                saved = save_result['success']

                # Check if target died
                if not target.is_alive:
                    affected.append(f"{target.name} ({final_damage} dmg - SLAIN!)")
                    total_kills += 1
                else:
                    save_str = " (saved)" if saved else ""
                    affected.append(f"{target.name} ({final_damage} dmg{save_str})")

        # Build narrative
        narrative = f"A crackling lightning bolt streaks forth for {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n⚡ {total_kills} {'enemy' if total_kills == 1 else 'enemies'} slain!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills
        }

    def _spell_cone_of_cold(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Cone of Cold: Cone of freezing cold, 1d4+1 damage per caster level, save for half"""

        # Calculate damage: (1d4+1) per caster level
        total_damage = sum(random.randint(1, 4) + 1 for _ in range(caster.level))

        if not targets:
            return {
                'narrative': "The cone of cold freezes the air harmlessly!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets in cone
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                # Saving throw for half damage
                save_result = self.save_resolver.save_for_half_damage(
                    target, total_damage, 'spell'
                )

                final_damage = save_result['final_damage']
                saved = save_result['success']

                # Check if target died
                if not target.is_alive:
                    affected.append(f"{target.name} ({final_damage} dmg - FROZEN SOLID!)")
                    total_kills += 1
                else:
                    save_str = " (saved)" if saved else ""
                    affected.append(f"{target.name} ({final_damage} dmg{save_str})")

        # Build narrative
        narrative = f"A freezing cone of cold blasts forth for {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n❄️  {total_kills} {'enemy' if total_kills == 1 else 'enemies'} frozen!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills
        }

    def _spell_cure_serious_wounds(self, spell: Spell, caster: PlayerCharacter,
                                   targets: List[Character]) -> Dict:
        """Cure Serious Wounds: heal 2d8+1 HP"""

        if not targets:
            return {
                'narrative': "No target to heal!",
                'affected': [],
                'healing': 0
            }

        target = targets[0]
        healing = random.randint(2, 16) + 1  # 2d8+1

        old_hp = target.hp_current
        target.heal(healing)
        actual_healing = target.hp_current - old_hp

        narrative = f"{target.name} is healed for {actual_healing} HP!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'healing': actual_healing
        }

    def _spell_heal(self, spell: Spell, caster: PlayerCharacter,
                   targets: List[Character]) -> Dict:
        """Heal: restore all HP and cure blindness, disease, etc."""

        if not targets:
            return {
                'narrative': "No target to heal!",
                'affected': [],
                'healing': 0
            }

        target = targets[0]
        old_hp = target.hp_current

        # Fully restore HP
        target.hp_current = target.hp_max
        actual_healing = target.hp_current - old_hp

        # Remove negative conditions
        conditions_removed = []
        if hasattr(target, 'conditions') and target.conditions:
            negative_conditions = ['poisoned', 'diseased', 'blinded', 'weakened', 'paralyzed']
            for condition in negative_conditions:
                if condition in target.conditions:
                    target.conditions.remove(condition)
                    conditions_removed.append(condition)

        narrative = f"{target.name} is fully healed for {actual_healing} HP!"
        if conditions_removed:
            narrative += f" Conditions removed: {', '.join(conditions_removed)}."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'healing': actual_healing,
            'conditions_removed': conditions_removed
        }

    def _spell_haste(self, spell: Spell, caster: PlayerCharacter,
                    targets: List[Character]) -> Dict:
        """Haste: Double movement and attacks, +1 AC (1 creature per level)"""

        if not targets:
            return {
                'narrative': "No targets to haste!",
                'affected': []
            }

        # Can affect 1 creature per caster level
        max_targets = caster.level
        targets_to_haste = targets[:max_targets]

        affected = []
        for target in targets_to_haste:
            if target.is_alive:
                target.add_condition('hasted')
                # In a full implementation, this would give +1 AC and double attacks
                affected.append(target.name)

        narrative = f"Time accelerates around {', '.join(affected)}! They move with supernatural speed!"

        return {
            'narrative': narrative,
            'affected': affected,
            'duration': 3 + caster.level  # rounds
        }

    def _spell_slow(self, spell: Spell, caster: PlayerCharacter,
                   targets: List[Character]) -> Dict:
        """Slow: Half movement and attacks, -1 AC, saving throw negates"""

        if not targets:
            return {
                'narrative': "No targets to slow!",
                'affected': []
            }

        affected = []
        resisted = []

        for target in targets:
            if target.is_alive:
                # Saving throw to resist
                save_result = self.save_resolver.make_save(target, 'spell')

                if save_result['success']:
                    resisted.append(target.name)
                else:
                    target.add_condition('slowed')
                    # In a full implementation, this would halve attacks and give -1 AC
                    affected.append(target.name)

        narrative_parts = []
        if affected:
            narrative_parts.append(f"Time slows around {', '.join(affected)}! They move like they're in molasses!")
        if resisted:
            narrative_parts.append(f"{', '.join(resisted)} resisted the effect!")

        narrative = ' '.join(narrative_parts) if narrative_parts else "The spell fails to affect anyone!"

        return {
            'narrative': narrative,
            'affected': affected,
            'resisted': resisted,
            'duration': 3 + caster.level  # rounds
        }

    def _spell_bless(self, spell: Spell, caster: PlayerCharacter,
                    targets: List[Character]) -> Dict:
        """Bless: +1 to attack rolls and morale for all allies"""

        # Bless affects all party members
        affected = []
        for target in targets:
            if target.is_alive:
                target.add_condition('blessed')
                # In a full implementation, this would give +1 to hit and saves
                affected.append(target.name)

        narrative = f"Divine blessing descends upon {', '.join(affected)}! Their weapons gleam with holy light!"

        return {
            'narrative': narrative,
            'affected': affected,
            'duration': 6  # rounds
        }

    def _spell_web(self, spell: Spell, caster: PlayerCharacter,
                  targets: List[Character]) -> Dict:
        """Web: Creates sticky webs that entangle creatures, save to avoid"""

        if not targets:
            return {
                'narrative': "Sticky webs fill the area, but catch nothing!",
                'affected': []
            }

        affected = []
        avoided = []

        for target in targets:
            if target.is_alive:
                # Saving throw to avoid being entangled
                # Stronger creatures (high STR) get bonus
                save_result = self.save_resolver.make_save(target, 'petrify_paralyze')

                if save_result['success']:
                    avoided.append(target.name)
                else:
                    target.add_condition('webbed')
                    # In a full implementation, this would prevent movement and give penalties
                    affected.append(target.name)

        narrative_parts = []
        if affected:
            narrative_parts.append(f"Sticky webs entangle {', '.join(affected)}! They struggle helplessly!")
        if avoided:
            narrative_parts.append(f"{', '.join(avoided)} broke free of the webs!")

        narrative = ' '.join(narrative_parts) if narrative_parts else "The spell fails to entangle anyone!"

        return {
            'narrative': narrative,
            'affected': affected,
            'avoided': avoided,
            'duration': 2 * caster.level  # turns (10 min each)
        }

    def _spell_hold_person(self, spell: Spell, caster: PlayerCharacter,
                          targets: List[Character]) -> Dict:
        """Hold Person: Paralyzes 1-4 humanoid creatures, save negates"""

        if not targets:
            return {
                'narrative': "No valid targets for Hold Person!",
                'affected': []
            }

        # Can affect 1-4 humanoids
        max_targets = random.randint(1, 4)
        potential_targets = targets[:max_targets]

        affected = []
        resisted = []
        immune = []

        for target in potential_targets:
            if not target.is_alive:
                continue

            # Check if target is humanoid (size S or M)
            if target.size not in ['S', 'M']:
                immune.append(target.name)
                continue

            # Saving throw to resist
            save_result = self.save_resolver.make_save(target, 'spell')

            if save_result['success']:
                resisted.append(target.name)
            else:
                target.add_condition('paralyzed')
                # In a full implementation, this would prevent all actions
                affected.append(target.name)

        narrative_parts = []
        if affected:
            narrative_parts.append(f"{', '.join(affected)} frozen in place, unable to move!")
        if resisted:
            narrative_parts.append(f"{', '.join(resisted)} resisted the paralysis!")
        if immune:
            narrative_parts.append(f"{', '.join(immune)} are not humanoid - spell has no effect!")

        narrative = ' '.join(narrative_parts) if narrative_parts else "The spell fails to paralyze anyone!"

        return {
            'narrative': narrative,
            'affected': affected,
            'resisted': resisted,
            'immune': immune,
            'duration': 2 * caster.level  # rounds
        }

    def _spell_invisibility(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Invisibility: Target becomes invisible until they attack, grants +4 AC and surprise"""

        if not targets:
            target = caster
        else:
            target = targets[0]

        if not target.is_alive:
            return {
                'narrative': "Cannot make a dead creature invisible!",
                'affected': []
            }

        target.add_condition('invisible')
        # In a full implementation, this would grant +4 AC and automatic surprise

        narrative = f"{target.name} fades from sight, becoming invisible! The effect will last until they attack."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'duration': 'Until attack'
        }

    def _spell_knock(self, spell: Spell, caster: PlayerCharacter,
                    targets: List[Character]) -> Dict:
        """Knock: Opens locked, barred, or wizard-locked doors"""

        # This spell affects the environment, not creatures
        # In the game context, it would unlock a door or container

        narrative = "You speak the word of opening! Locks click and bars slide aside with a resounding *knock*!"

        return {
            'narrative': narrative,
            'affected': [],
            'effect': 'unlock_door'  # Game state can check this flag
        }

    def _spell_find_traps(self, spell: Spell, caster: PlayerCharacter,
                         targets: List[Character]) -> Dict:
        """Find Traps: Reveals the presence of traps within range"""

        # This spell affects the caster's perception, not targets
        # In the game context, it would reveal traps in the current area

        narrative = "Your senses sharpen as divine insight reveals hidden dangers! "
        narrative += "You can now detect traps within 30 feet for the next 3 turns."

        # Add a condition to the caster to track the effect
        caster.add_condition('detecting_traps')

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': 3  # turns (30 minutes)
        }

    def _spell_cloudkill(self, spell: Spell, caster: PlayerCharacter,
                        targets: List[Character]) -> Dict:
        """Cloudkill: Deadly cloud that slays creatures with < 4+1 HD, others save vs poison or die"""

        if not targets:
            return {
                'narrative': "A billowing cloud of yellowish-green vapor fills the area, but finds no victims!",
                'affected': [],
                'total_kills': 0
            }

        affected = []
        total_kills = 0
        survived = []

        for target in targets:
            if not target.is_alive:
                continue

            # Creatures with < 5 HD/levels are instantly slain
            if target.level < 5:
                target.take_damage(9999)  # Instant death
                affected.append(f"{target.name} (SLAIN INSTANTLY!)")
                total_kills += 1
            # Creatures with 5-6 HD/levels must save vs poison or die
            elif target.level <= 6:
                save_result = self.save_resolver.make_save(target, 'poison')

                if save_result['success']:
                    survived.append(target.name)
                else:
                    target.take_damage(9999)  # Death by poison
                    affected.append(f"{target.name} (POISONED - SLAIN!)")
                    total_kills += 1
            # Creatures with > 6 HD are unaffected
            else:
                survived.append(target.name)

        # Build narrative
        narrative = "A billowing cloud of yellowish-green vapors fills the air!\n"

        if affected:
            narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if survived:
            narrative += f"\n\n{', '.join(survived)} survived the poison cloud!"

        if total_kills > 0:
            narrative += f"\n\n☠️  {total_kills} {'creature' if total_kills == 1 else 'creatures'} slain by the deadly vapors!"

        return {
            'narrative': narrative,
            'affected': affected,
            'survived': survived,
            'total_kills': total_kills,
            'duration': caster.level  # rounds
        }

    def _spell_chain_lightning(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """Chain Lightning: Arcs between targets, each taking half damage of previous"""

        if not targets:
            return {
                'narrative': "The lightning crackles through empty air!",
                'affected': [],
                'total_damage': 0
            }

        # Primary target damage: 1d6 per caster level (max 12d6)
        num_dice = min(caster.level, 12)
        primary_damage = sum(random.randint(1, 6) for _ in range(num_dice))

        affected = []
        total_kills = 0

        # Can chain to 1 target per caster level
        max_targets = min(len(targets), caster.level)
        current_damage = primary_damage

        for i, target in enumerate(targets[:max_targets]):
            if not target.is_alive:
                continue

            # Saving throw for half damage
            save_result = self.save_resolver.save_for_half_damage(
                target, current_damage, 'spell'
            )

            final_damage = save_result['final_damage']
            saved = save_result['success']

            # Check if target died
            if not target.is_alive:
                if i == 0:
                    affected.append(f"{target.name} [PRIMARY] ({final_damage} dmg - SLAIN!)")
                else:
                    affected.append(f"{target.name} ({final_damage} dmg - SLAIN!)")
                total_kills += 1
            else:
                save_str = " (saved)" if saved else ""
                if i == 0:
                    affected.append(f"{target.name} [PRIMARY] ({final_damage} dmg{save_str})")
                else:
                    affected.append(f"{target.name} ({final_damage} dmg{save_str})")

            # Each subsequent arc does half damage of previous
            current_damage = current_damage // 2
            if current_damage < 1:
                break

        # Build narrative
        narrative = f"A stroke of lightning leaps forth, chaining between targets!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n⚡ {total_kills} {'enemy' if total_kills == 1 else 'enemies'} slain!"

        return {
            'narrative': narrative,
            'affected': affected,
            'primary_damage': primary_damage,
            'total_kills': total_kills
        }

    def _spell_raise_dead(self, spell: Spell, caster: PlayerCharacter,
                         targets: List[Character]) -> Dict:
        """Raise Dead: Restores life to a dead character"""

        if not targets:
            return {
                'narrative': "No target to raise from the dead!",
                'affected': []
            }

        target = targets[0]

        # Check if target is already alive
        if target.is_alive:
            return {
                'narrative': f"{target.name} is already alive!",
                'affected': []
            }

        # Check if target is a valid race (dwarf, gnome, half-elf, halfling, human)
        valid_races = ['human', 'dwarf', 'halfling', 'half-elf', 'elf']
        if hasattr(target, 'race') and target.race.lower() not in valid_races:
            return {
                'narrative': f"{target.name}'s race cannot be raised from the dead!",
                'affected': []
            }

        # Restore to life with 1 HP
        target.is_alive = True
        target.hp_current = 1

        # Remove death-related conditions
        if hasattr(target, 'conditions'):
            death_conditions = ['dead', 'dying', 'slain']
            for condition in death_conditions:
                if condition in target.conditions:
                    target.conditions.remove(condition)

        narrative = f"Divine power flows through {target.name}! "
        narrative += f"Their eyes open as life returns to their body. "
        narrative += f"They are weak (1 HP) but alive!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'restored_hp': 1
        }
