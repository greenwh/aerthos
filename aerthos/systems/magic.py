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
            'cure_serious_wounds': self._spell_cure_serious_wounds,
            'cure_critical_wounds': self._spell_cure_critical_wounds,
            'protection_from_evil': self._spell_protection_from_evil,
            'detect_magic': self._spell_detect_magic,
            'burning_hands': self._spell_burning_hands,
            'charm_person': self._spell_charm_person,
            'fireball': self._spell_fireball,
            'lightning_bolt': self._spell_lightning_bolt,
            'cone_of_cold': self._spell_cone_of_cold,
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
            'raise_dead': self._spell_raise_dead,
            'spiritual_hammer': self._spell_spiritual_hammer,
            'prayer': self._spell_prayer,
            'flame_strike': self._spell_flame_strike,
            'blade_barrier': self._spell_blade_barrier,
            'ice_storm': self._spell_ice_storm,
            'disintegrate': self._spell_disintegrate,
            'light': self._spell_light,
            'silence_15_radius': self._spell_silence_15_radius,
            'continual_light': self._spell_continual_light,
            'locate_object': self._spell_locate_object,
            'clairvoyance': self._spell_clairvoyance,
            'dispel_magic': self._spell_dispel_magic,
            'dimension_door': self._spell_dimension_door,
            'teleport': self._spell_teleport,
            'shield': self._spell_shield,
            'enlarge': self._spell_enlarge,
            'reduce': self._spell_reduce,
            'strength': self._spell_strength,
            'slow_poison': self._spell_slow_poison,
            'polymorph_self': self._spell_polymorph_self,
            'polymorph_other': self._spell_polymorph_other,
            'shocking_grasp': self._spell_shocking_grasp,
            'color_spray': self._spell_color_spray,
            'stinking_cloud': self._spell_stinking_cloud,
            'mirror_image': self._spell_mirror_image,
            'wall_of_fire': self._spell_wall_of_fire,
            'wall_of_ice': self._spell_wall_of_ice,
            'cure_disease': self._spell_cure_disease,
            'cure_blindness': self._spell_cure_blindness,
            'neutralize_poison': self._spell_neutralize_poison,
            'regenerate': self._spell_regenerate,
            'blur': self._spell_blur,
            'barkskin': self._spell_barkskin
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

    def _spell_cure_critical_wounds(self, spell: Spell, caster: PlayerCharacter,
                                    targets: List[Character]) -> Dict:
        """Cure Critical Wounds: heal 3d8+3 HP"""

        if not targets:
            return {
                'narrative': "No target to heal!",
                'affected': [],
                'healing': 0
            }

        target = targets[0]
        healing = sum(random.randint(1, 8) for _ in range(3)) + 3  # 3d8+3

        old_hp = target.hp_current
        target.heal(healing)
        actual_healing = target.hp_current - old_hp

        narrative = f"Powerful healing energy flows into {target.name}, restoring {actual_healing} HP!"

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

    def _spell_spiritual_hammer(self, spell: Spell, caster: PlayerCharacter,
                               targets: List[Character]) -> Dict:
        """Spiritual Hammer: Creates a magical hammer that attacks, 1d4+1 damage"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target for the spiritual hammer!",
                'affected': [],
                'damage': 0
            }

        target = targets[0]
        damage = random.randint(1, 4) + 1  # 1d4+1

        target.take_damage(damage)

        narrative = f"A glowing hammer of pure force materializes and strikes {target.name} for {damage} damage!"

        if not target.is_alive:
            narrative += f" {target.name} is slain!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'damage': damage,
            'duration': 3 * caster.level  # rounds
        }

    def _spell_prayer(self, spell: Spell, caster: PlayerCharacter,
                     targets: List[Character]) -> Dict:
        """Prayer: Allies gain +1 to attack, damage, and saves. Enemies get -1."""

        # In a typical combat scenario, targets would be all combatants
        # Allies = party members, Enemies = monsters
        # For this implementation, we'll apply the blessing to party members

        affected_allies = []
        affected_enemies = []

        # Note: In the game context, this would be determined by who's in the party
        # For now, we'll apply 'prayer_blessed' condition to all targets
        for target in targets:
            if target.is_alive:
                # Check if target is a party member or enemy
                # This would typically be determined by checking if target is a PlayerCharacter
                if isinstance(target, PlayerCharacter):
                    target.add_condition('prayer_blessed')
                    affected_allies.append(target.name)
                else:
                    target.add_condition('prayer_cursed')
                    affected_enemies.append(target.name)

        narrative_parts = []
        if affected_allies:
            narrative_parts.append(f"Divine favor descends upon {', '.join(affected_allies)}! (+1 to attack, damage, and saves)")
        if affected_enemies:
            narrative_parts.append(f"Divine disfavor strikes {', '.join(affected_enemies)}! (-1 to attack, damage, and saves)")

        narrative = ' '.join(narrative_parts) if narrative_parts else "The prayer echoes unanswered."

        return {
            'narrative': narrative,
            'affected': affected_allies + affected_enemies,
            'allies_blessed': affected_allies,
            'enemies_cursed': affected_enemies,
            'duration': caster.level  # rounds
        }

    def _spell_flame_strike(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Flame Strike: Column of divine fire, 6d8 damage, save for half"""

        # Calculate damage: 6d8
        total_damage = sum(random.randint(1, 8) for _ in range(6))

        if not targets:
            return {
                'narrative': "A column of divine flame roars down from the heavens, but strikes nothing!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets in area
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
                    affected.append(f"{target.name} ({final_damage} dmg - INCINERATED!)")
                    total_kills += 1
                else:
                    save_str = " (saved)" if saved else ""
                    affected.append(f"{target.name} ({final_damage} dmg{save_str})")

        # Build narrative
        narrative = f"A roaring column of divine fire descends from above, dealing {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n🔥 {total_kills} {'enemy' if total_kills == 1 else 'enemies'} consumed by holy fire!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills
        }

    def _spell_blade_barrier(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Blade Barrier: Wall of whirling blades, 8d8 damage to those passing through"""

        # Calculate damage: 8d8
        total_damage = sum(random.randint(1, 8) for _ in range(8))

        if not targets:
            return {
                'narrative': "A shimmering wall of razor-sharp blades materializes, whirling with deadly precision!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets attempting to pass through
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                # No saving throw - the barrier cuts all who enter
                target.take_damage(total_damage)

                # Check if target died
                if not target.is_alive:
                    affected.append(f"{target.name} ({total_damage} dmg - SHREDDED!)")
                    total_kills += 1
                else:
                    affected.append(f"{target.name} ({total_damage} dmg)")

        # Build narrative
        narrative = f"A wall of whirling, razor-sharp blades materializes, dealing {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n⚔️  {total_kills} {'enemy' if total_kills == 1 else 'enemies'} torn apart by the blades!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills,
            'duration': 3 * caster.level  # rounds
        }

    def _spell_ice_storm(self, spell: Spell, caster: PlayerCharacter,
                        targets: List[Character]) -> Dict:
        """Ice Storm: Great hailstones dealing 3d10 damage"""

        # Calculate damage: 3d10
        total_damage = sum(random.randint(1, 10) for _ in range(3))

        if not targets:
            return {
                'narrative': "Great hailstones fall from above, pounding the ground with tremendous force!",
                'affected': [],
                'total_damage': 0
            }

        # Apply damage to all targets in area
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                # No saving throw - hailstones strike all in the area
                target.take_damage(total_damage)

                # Check if target died
                if not target.is_alive:
                    affected.append(f"{target.name} ({total_damage} dmg - CRUSHED!)")
                    total_kills += 1
                else:
                    affected.append(f"{target.name} ({total_damage} dmg)")

        # Build narrative
        narrative = f"Great hailstones the size of fists rain down, dealing {total_damage} damage!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n❄️  {total_kills} {'enemy' if total_kills == 1 else 'enemies'} battered to death!"

        return {
            'narrative': narrative,
            'affected': affected,
            'total_damage': total_damage,
            'kills': total_kills
        }

    def _spell_disintegrate(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Disintegrate: Target vanishes if they fail their save"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "A thin green ray shoots forth but finds no target!",
                'affected': []
            }

        target = targets[0]

        # Saving throw to resist - if successful, no effect
        save_result = self.save_resolver.make_save(target, 'spell')

        if save_result['success']:
            narrative = f"A thin green ray strikes {target.name}, but they resist the spell's power!"
            affected = []
        else:
            # Target is disintegrated - instant death
            target.take_damage(9999)
            narrative = f"A thin green ray strikes {target.name}! "
            narrative += f"Their form shimmers for a moment, then they vanish completely - disintegrated into fine dust! "
            narrative += f"Not even a trace remains."
            affected = [f"{target.name} (DISINTEGRATED!)"]

        return {
            'narrative': narrative,
            'affected': affected,
            'disintegrated': not save_result['success']
        }

    def _spell_light(self, spell: Spell, caster: PlayerCharacter,
                    targets: List[Character]) -> Dict:
        """Light: Creates a bright light like a torch, 1 turn/level"""

        # In the game context, this would affect the room's light level
        # For now, we'll add a condition to track the effect

        narrative = "A globe of bright light appears, illuminating the area like a torch! "
        narrative += f"The light will last for {caster.level} turns (10 minutes each)."

        # Add condition to caster to track light source
        caster.add_condition('light_source')

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': caster.level,  # turns
            'effect': 'light_created'
        }

    def _spell_silence_15_radius(self, spell: Spell, caster: PlayerCharacter,
                                 targets: List[Character]) -> Dict:
        """Silence 15' Radius: No sound in area, prevents spellcasting"""

        if not targets:
            return {
                'narrative': "An area of absolute silence descends, but affects no one!",
                'affected': []
            }

        # Apply silence to all targets in the area
        affected = []
        for target in targets:
            if target.is_alive:
                target.add_condition('silenced')
                affected.append(target.name)

        narrative = f"A zone of absolute silence descends! {', '.join(affected)} cannot make any sound or cast spells! "
        narrative += f"Duration: {2 * caster.level} rounds."

        return {
            'narrative': narrative,
            'affected': affected,
            'duration': 2 * caster.level,  # rounds
            'effect': 'silence_created'
        }

    def _spell_continual_light(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """Continual Light: Creates permanent bright light"""

        # This spell creates a permanent light source
        narrative = "A brilliant, permanent light springs into existence! "
        narrative += "The area is illuminated with the brightness of full daylight. "
        narrative += "This light will remain until dispelled."

        return {
            'narrative': narrative,
            'affected': [],
            'duration': 'Permanent',
            'effect': 'continual_light_created'
        }

    def _spell_locate_object(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Locate Object: Aids in finding a known object by direction"""

        # In the game context, this would reveal the direction to a specific object
        # For now, we'll add a condition to track the divination effect

        narrative = "Your mind's eye opens, granting you the ability to sense the direction of a known object! "
        narrative += "You will be able to locate objects within range for the duration of the spell."

        caster.add_condition('locating_object')

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': 3,  # turns
            'effect': 'locate_object_active'
        }

    def _spell_clairvoyance(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Clairvoyance: See a known locale remotely"""

        # This spell allows remote viewing of a known location
        narrative = "Your vision expands beyond your physical eyes! "
        narrative += "You can now see a known locale as if you were standing there. "
        narrative += "Images form in your mind, revealing the area within sight range of that location."

        caster.add_condition('clairvoyant')

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': caster.level,  # rounds
            'effect': 'clairvoyance_active'
        }

    def _spell_dispel_magic(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Dispel Magic: Negates magical effects based on caster level"""

        if not targets:
            return {
                'narrative': "You attempt to dispel magic, but there are no targets!",
                'affected': []
            }

        # Dispel magic removes magical conditions from targets
        affected = []
        conditions_removed = []

        for target in targets:
            if target.is_alive and hasattr(target, 'conditions') and target.conditions:
                # Remove magical conditions
                magical_conditions = [
                    'blessed', 'prayer_blessed', 'prayer_cursed', 'hasted', 'slowed',
                    'protected_from_evil', 'invisible', 'charmed', 'webbed',
                    'paralyzed', 'silenced', 'light_source', 'clairvoyant',
                    'locating_object', 'detecting_traps'
                ]

                removed = []
                for condition in magical_conditions:
                    if condition in target.conditions:
                        target.conditions.remove(condition)
                        removed.append(condition)

                if removed:
                    affected.append(target.name)
                    conditions_removed.extend(removed)

        if affected:
            narrative = f"Magical energy unravels! {', '.join(affected)} have their magical effects dispelled! "
            narrative += f"Conditions removed: {', '.join(set(conditions_removed))}"
        else:
            narrative = "You attempt to dispel magic, but no magical effects are present!"

        return {
            'narrative': narrative,
            'affected': affected,
            'conditions_removed': list(set(conditions_removed))
        }

    def _spell_dimension_door(self, spell: Spell, caster: PlayerCharacter,
                             targets: List[Character]) -> Dict:
        """Dimension Door: Instantly teleport to a nearby well-known location"""

        # In the game context, this would move the caster to another room
        # For now, we'll provide a narrative that the spell was cast successfully

        narrative = "Reality bends around you! "
        narrative += "In an instant, you step through an invisible doorway in space itself. "
        narrative += "You can now teleport to a well-known location within range (no chance of error). "
        narrative += "You may bring up to 5,000 gp weight with you."

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'effect': 'dimension_door_ready',
            'note': 'Use this to move to another location in the dungeon'
        }

    def _spell_teleport(self, spell: Spell, caster: PlayerCharacter,
                       targets: List[Character]) -> Dict:
        """Teleport: Instantly transport to a distant well-known location"""

        # In the game context, this would move the caster to a distant location
        # The chance of error depends on familiarity with the destination

        # Roll for teleport accuracy (simplified)
        # In full AD&D, this would depend on knowledge of destination
        accuracy_roll = random.randint(1, 100)

        if accuracy_roll <= 95:
            # Successful teleport
            narrative = "Space itself warps around you! "
            narrative += "In a flash of light and a rush of displaced air, you vanish from this location "
            narrative += "and instantly appear at your intended destination! "
            narrative += "You may bring additional weight with you."
            success = True
        else:
            # Teleport mishap (very rare in this simplified version)
            narrative = "You invoke the teleportation magic, but something goes wrong! "
            narrative += "The spell fizzles and fails to transport you. "
            narrative += "You remain where you are, shaken but unharmed."
            success = False

        return {
            'narrative': narrative,
            'affected': [caster.name] if success else [],
            'success': success,
            'effect': 'teleport_attempted',
            'note': 'Use this to travel to distant known locations'
        }

    def _spell_shield(self, spell: Spell, caster: PlayerCharacter,
                     targets: List[Character]) -> Dict:
        """Shield: Creates an invisible barrier granting AC 2 vs missiles, AC 4 vs other attacks"""

        # Apply shield buff to caster
        caster.add_condition('shielded')

        # In a full implementation, this would modify AC calculations
        # AC 2 vs missiles, AC 4 vs other attacks

        narrative = "An invisible barrier of force materializes in front of you! "
        narrative += "You gain AC 2 against missiles and AC 4 against other attacks. "
        narrative += f"Duration: {5 * caster.level} rounds."

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': 5 * caster.level,  # rounds
            'ac_bonus_missiles': 2,
            'ac_bonus_melee': 4
        }

    def _spell_enlarge(self, spell: Spell, caster: PlayerCharacter,
                      targets: List[Character]) -> Dict:
        """Enlarge: Increases creature/object size by 20% per caster level"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target to enlarge!",
                'affected': []
            }

        target = targets[0]

        # Calculate size increase: 20% per caster level
        size_increase_percent = 20 * caster.level
        max_increase = 200  # Maximum 200% for creatures

        actual_increase = min(size_increase_percent, max_increase)

        target.add_condition('enlarged')

        narrative = f"{target.name} grows rapidly, increasing in size by {actual_increase}%! "
        narrative += f"They are now much larger and more imposing. "
        narrative += "This grants increased strength and reach in combat."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'size_increase_percent': actual_increase,
            'duration': 'Special'  # Varies in AD&D
        }

    def _spell_reduce(self, spell: Spell, caster: PlayerCharacter,
                     targets: List[Character]) -> Dict:
        """Reduce: Decreases creature/object size (reverse of Enlarge)"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target to reduce!",
                'affected': []
            }

        target = targets[0]

        # Calculate size decrease: 20% per caster level
        size_decrease_percent = 20 * caster.level
        max_decrease = 200  # Can shrink significantly

        actual_decrease = min(size_decrease_percent, max_decrease)

        target.add_condition('reduced')

        narrative = f"{target.name} shrinks rapidly, decreasing in size by {actual_decrease}%! "
        narrative += f"They are now much smaller and less threatening. "
        narrative += "This reduces their combat effectiveness."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'size_decrease_percent': actual_decrease,
            'duration': 'Special'  # Varies in AD&D
        }

    def _spell_strength(self, spell: Spell, caster: PlayerCharacter,
                       targets: List[Character]) -> Dict:
        """Strength: Increases creature's Strength score by 1-6 points for 6 turns/level"""

        if not targets:
            target = caster
        else:
            target = targets[0]

        if not target.is_alive:
            return {
                'narrative': "Cannot strengthen a dead creature!",
                'affected': []
            }

        # Roll for strength increase: 1d6
        str_increase = random.randint(1, 6)

        # Store original strength (in a full implementation)
        target.add_condition('strengthened')

        narrative = f"Magical power flows into {target.name}'s muscles! "
        narrative += f"Their Strength increases by {str_increase} points. "
        narrative += f"They feel incredibly powerful! "
        narrative += f"Duration: {6 * caster.level} turns."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'str_increase': str_increase,
            'duration': 6 * caster.level  # turns
        }

    def _spell_slow_poison(self, spell: Spell, caster: PlayerCharacter,
                          targets: List[Character]) -> Dict:
        """Slow Poison: Greatly slows poison effects, preventing death"""

        if not targets:
            return {
                'narrative': "No poisoned creature to help!",
                'affected': []
            }

        target = targets[0]

        # Check if target has poison condition
        has_poison = hasattr(target, 'conditions') and 'poisoned' in target.conditions

        if has_poison:
            # Remove immediate poison threat, add slowed_poison condition
            target.conditions.remove('poisoned')
            target.add_condition('slowed_poison')

            narrative = f"Divine power flows through {target.name}! "
            narrative += "The deadly poison is slowed to a crawl. "
            narrative += f"{target.name} will lose only 1 HP per turn but will never drop below 1 HP. "
            narrative += "This buys precious time to find a cure!"
        else:
            # Can be cast prophylactically
            target.add_condition('slowed_poison')
            narrative = f"You invoke divine protection over {target.name}! "
            narrative += "If they are poisoned, the effects will be greatly slowed."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'duration': 10  # turns
        }

    def _spell_polymorph_self(self, spell: Spell, caster: PlayerCharacter,
                             targets: List[Character]) -> Dict:
        """Polymorph Self: Caster assumes form of any creature (2 turns/level)"""

        # In a full implementation, this would allow the caster to transform
        # For now, we'll track the condition and provide narrative

        caster.add_condition('polymorphed_self')

        narrative = "Your form shifts and changes! "
        narrative += "You can now assume the form of any creature from a wren to a hippopotamus. "
        narrative += "You gain the creature's form of locomotion (flying, swimming, etc.) "
        narrative += "but retain your own mind and abilities. "
        narrative += f"Duration: {2 * caster.level} turns."

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': 2 * caster.level,  # turns
            'note': 'Choose your new form carefully!'
        }

    def _spell_polymorph_other(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """Polymorph Other: Completely alters target's form, ability, personality"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target to polymorph!",
                'affected': []
            }

        target = targets[0]

        # System shock save based on Constitution
        # Simplified: use spell save
        save_result = self.save_resolver.make_save(target, 'spell')

        if save_result['success']:
            narrative = f"{target.name} resists the polymorph! "
            narrative += "Their form shimmers but remains unchanged."
            affected = []
        else:
            # Target is polymorphed
            target.add_condition('polymorphed_other')

            narrative = f"{target.name}'s form twists and changes completely! "
            narrative += "They are transformed into an entirely different creature, "
            narrative += "with new abilities, personality, and mentality. "
            narrative += "The transformation is complete and potentially permanent!"
            affected = [target.name]

        return {
            'narrative': narrative,
            'affected': affected,
            'duration': 'Permanent or until dispelled',
            'resisted': save_result['success']
        }

    def _spell_shocking_grasp(self, spell: Spell, caster: PlayerCharacter,
                             targets: List[Character]) -> Dict:
        """Shocking Grasp: Touch attack for 1d8 + 1/level electrical damage"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "Your hand crackles with electricity, but finds no target!",
                'affected': [],
                'damage': 0
            }

        target = targets[0]

        # Calculate damage: 1d8 + 1 per caster level
        base_damage = random.randint(1, 8)
        level_bonus = caster.level
        total_damage = base_damage + level_bonus

        target.take_damage(total_damage)

        narrative = f"Electricity surges through your hand as you touch {target.name}! "
        narrative += f"A powerful shock deals {total_damage} damage!"

        if not target.is_alive:
            narrative += f" {target.name} is electrocuted to death!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'damage': total_damage
        }

    def _spell_color_spray(self, spell: Spell, caster: PlayerCharacter,
                          targets: List[Character]) -> Dict:
        """Color Spray: Fan of colors that stuns/blinds/knocks unconscious based on HD"""

        if not targets:
            return {
                'narrative': "A vivid spray of colors bursts forth, but affects no one!",
                'affected': []
            }

        # Affects 1d6 creatures
        num_affected = min(random.randint(1, 6), len(targets))

        knocked_out = []
        blinded = []
        stunned = []

        for target in targets[:num_affected]:
            if not target.is_alive:
                continue

            # Effect based on HD/level:
            # 2 HD or less: unconscious 2d4 rounds
            # 3-4 HD: blinded 1d4 rounds
            # 5+ HD: stunned 1 round

            if target.level <= 2:
                target.add_condition('unconscious')
                knocked_out.append(target.name)
            elif target.level <= 4:
                target.add_condition('blinded')
                blinded.append(target.name)
            else:
                target.add_condition('stunned')
                stunned.append(target.name)

        narrative = "A vivid, fan-shaped spray of clashing colors erupts from your hands!\n"

        if knocked_out:
            narrative += f"  • Knocked unconscious: {', '.join(knocked_out)}\n"
        if blinded:
            narrative += f"  • Blinded: {', '.join(blinded)}\n"
        if stunned:
            narrative += f"  • Stunned: {', '.join(stunned)}"

        return {
            'narrative': narrative,
            'affected': knocked_out + blinded + stunned,
            'knocked_out': knocked_out,
            'blinded': blinded,
            'stunned': stunned
        }

    def _spell_stinking_cloud(self, spell: Spell, caster: PlayerCharacter,
                             targets: List[Character]) -> Dict:
        """Stinking Cloud: Nauseous vapors make creatures helpless"""

        if not targets:
            return {
                'narrative': "A billowing cloud of nauseous vapors fills the area!",
                'affected': []
            }

        affected = []
        resisted = []

        for target in targets:
            if target.is_alive:
                # Saving throw to resist
                save_result = self.save_resolver.make_save(target, 'poison')

                if save_result['success']:
                    resisted.append(target.name)
                else:
                    target.add_condition('nauseated')
                    affected.append(target.name)

        narrative = "A billowing cloud of yellowish-green, nauseous vapors fills the area!\n"

        if affected:
            narrative += f"  • Helpless from nausea: {', '.join(affected)}\n"
        if resisted:
            narrative += f"  • Resisted: {', '.join(resisted)}"

        return {
            'narrative': narrative,
            'affected': affected,
            'resisted': resisted
        }

    def _spell_mirror_image(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Mirror Image: Creates 1d4+1 illusory duplicates"""

        # Roll for number of images
        num_images = random.randint(1, 4) + 1

        caster.add_condition('mirror_images')

        narrative = f"Illusory duplicates of yourself spring into existence! "
        narrative += f"{num_images} identical images surround you, confusing attackers. "
        narrative += f"Duration: {3 * caster.level} rounds."

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'num_images': num_images,
            'duration': 3 * caster.level  # rounds
        }

    def _spell_wall_of_fire(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Wall of Fire: Blazing curtain, 4d4 damage passing through"""

        # Calculate damage: 4d4 for passing through, 2d4 for being near
        pass_through_damage = sum(random.randint(1, 4) for _ in range(4))

        if not targets:
            return {
                'narrative': "A blazing curtain of magical fire springs into existence! "
                             "The wall burns with intense heat.",
                'affected': [],
                'damage': 0
            }

        # Damage targets that pass through
        affected = []
        total_kills = 0

        for target in targets:
            if target.is_alive:
                target.take_damage(pass_through_damage)

                if not target.is_alive:
                    affected.append(f"{target.name} ({pass_through_damage} dmg - BURNED ALIVE!)")
                    total_kills += 1
                else:
                    affected.append(f"{target.name} ({pass_through_damage} dmg)")

        narrative = f"A blazing curtain of magical fire erupts!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        if total_kills > 0:
            narrative += f"\n\n🔥 {total_kills} {'enemy' if total_kills == 1 else 'enemies'} burned to death!"

        return {
            'narrative': narrative,
            'affected': affected,
            'damage': pass_through_damage,
            'kills': total_kills,
            'duration': caster.level  # rounds
        }

    def _spell_wall_of_ice(self, spell: Spell, caster: PlayerCharacter,
                          targets: List[Character]) -> Dict:
        """Wall of Ice: Strong ice barrier, 2 HP/inch damage breaking through"""

        # Wall thickness: 1 inch per caster level
        thickness_inches = caster.level
        break_through_damage = 2 * thickness_inches

        if not targets:
            return {
                'narrative': f"A sheet of strong, flexible ice materializes! "
                             f"The wall is {thickness_inches} inches thick.",
                'affected': [],
                'damage': 0
            }

        # Damage targets that break through
        affected = []

        for target in targets:
            if target.is_alive:
                target.take_damage(break_through_damage)

                if not target.is_alive:
                    affected.append(f"{target.name} ({break_through_damage} dmg - FROZEN!)")
                else:
                    affected.append(f"{target.name} ({break_through_damage} dmg)")

        narrative = f"A wall of ice {thickness_inches}\" thick blocks the way!\n"
        narrative += '\n'.join(f"  • {entry}" for entry in affected)

        return {
            'narrative': narrative,
            'affected': affected,
            'damage': break_through_damage,
            'duration': caster.level  # rounds
        }

    def _spell_cure_disease(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Cure Disease: Removes any disease from target"""

        if not targets:
            return {
                'narrative': "No diseased creature to cure!",
                'affected': []
            }

        target = targets[0]

        # Check for disease condition
        has_disease = hasattr(target, 'conditions') and 'diseased' in target.conditions

        if has_disease:
            target.conditions.remove('diseased')
            narrative = f"Divine power flows through {target.name}! "
            narrative += "The disease is purged from their body, leaving them clean and healthy."
        else:
            narrative = f"You invoke divine healing upon {target.name}, "
            narrative += "but they are not afflicted with any disease."

        return {
            'narrative': narrative,
            'affected': [target.name] if has_disease else []
        }

    def _spell_cure_blindness(self, spell: Spell, caster: PlayerCharacter,
                             targets: List[Character]) -> Dict:
        """Cure Blindness: Permanently cures blindness"""

        if not targets:
            return {
                'narrative': "No blind creature to cure!",
                'affected': []
            }

        target = targets[0]

        # Check for blindness condition
        has_blindness = hasattr(target, 'conditions') and 'blinded' in target.conditions

        if has_blindness:
            target.conditions.remove('blinded')
            narrative = f"Divine power touches {target.name}'s eyes! "
            narrative += "Their vision is restored, and they can see clearly once more."
        else:
            narrative = f"You invoke divine healing upon {target.name}, "
            narrative += "but they are not afflicted with blindness."

        return {
            'narrative': narrative,
            'affected': [target.name] if has_blindness else []
        }

    def _spell_neutralize_poison(self, spell: Spell, caster: PlayerCharacter,
                                targets: List[Character]) -> Dict:
        """Neutralize Poison: Removes poison, can revive recently poisoned"""

        if not targets:
            return {
                'narrative': "No poisoned creature or object to neutralize!",
                'affected': []
            }

        target = targets[0]

        # Check for poison conditions
        has_poison = hasattr(target, 'conditions') and (
            'poisoned' in target.conditions or 'slowed_poison' in target.conditions
        )

        if has_poison:
            if 'poisoned' in target.conditions:
                target.conditions.remove('poisoned')
            if 'slowed_poison' in target.conditions:
                target.conditions.remove('slowed_poison')

            narrative = f"Divine power flows through {target.name}! "
            narrative += "The poison is completely neutralized and purged from their system."

            # Can revive if recently poisoned (alive but with very low HP)
            if target.is_alive and target.hp_current < 3:
                heal_amount = random.randint(1, 4)
                target.heal(heal_amount)
                narrative += f" They recover {heal_amount} HP."
        else:
            narrative = f"You invoke divine power over {target.name}, "
            narrative += "but they are not afflicted with poison."

        return {
            'narrative': narrative,
            'affected': [target.name] if has_poison else []
        }

    def _spell_regenerate(self, spell: Spell, caster: PlayerCharacter,
                         targets: List[Character]) -> Dict:
        """Regenerate: Regrows body members, bones, organs"""

        if not targets:
            return {
                'narrative': "No creature to regenerate!",
                'affected': []
            }

        target = targets[0]

        if not target.is_alive:
            return {
                'narrative': f"{target.name} is dead - regeneration cannot restore life!",
                'affected': []
            }

        # Restore significant HP (represents regrowing body parts)
        heal_amount = sum(random.randint(1, 8) for _ in range(4))  # 4d8
        old_hp = target.hp_current
        target.heal(heal_amount)
        actual_healing = target.hp_current - old_hp

        narrative = f"Powerful regenerative magic flows through {target.name}! "
        narrative += "Lost body members, bones, and organs begin to grow back. "
        narrative += f"They recover {actual_healing} HP as their body regenerates!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'healing': actual_healing
        }

    def _spell_blur(self, spell: Spell, caster: PlayerCharacter,
                   targets: List[Character]) -> Dict:
        """Blur: Makes caster's form blurred and wavery, penalizing attacks"""

        caster.add_condition('blurred')

        narrative = "Your form becomes blurred, shifting, and wavery! "
        narrative += "Missile and melee attacks against you suffer penalties as your outline becomes indistinct."

        return {
            'narrative': narrative,
            'affected': [caster.name],
            'duration': 'Special'  # Varies in AD&D
        }

    def _spell_barkskin(self, spell: Spell, caster: PlayerCharacter,
                       targets: List[Character]) -> Dict:
        """Barkskin: Improves AC by 1 and grants +1 to saves"""

        if not targets:
            target = caster
        else:
            target = targets[0]

        if not target.is_alive:
            return {
                'narrative': "Cannot cast barkskin on a dead creature!",
                'affected': []
            }

        target.add_condition('barkskin')

        narrative = f"{target.name}'s skin takes on the texture and toughness of bark! "
        narrative += "Their AC improves by 1 and they gain +1 to all saving throws versus attack forms (except magic)."

        return {
            'narrative': narrative,
            'affected': [target.name],
            'ac_bonus': 1,
            'save_bonus': 1,
            'duration': 'Special'  # Varies in AD&D
        }
