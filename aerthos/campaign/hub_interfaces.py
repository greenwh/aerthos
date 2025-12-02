"""
Interface classes that bridge existing Shop/Inn/Temple systems with Party in campaign mode
"""

from typing import Tuple, List, Dict, Optional
from ..entities.party import Party
from ..entities.player import PlayerCharacter, Item
from ..world.shop import Shop
from ..world.inn import Inn
from ..systems.magic_item_factory import MagicItemFactory


class ShopInterface:
    """Bridge between Shop system and Party for campaign mode

    Handles gold management, inventory updates, and transactions
    across party members in a campaign context.
    """

    def __init__(self, shop: Shop, party: Party, price_modifier: float = 1.0, buy_rate: float = 0.4):
        """Initialize shop interface

        Args:
            shop: The shop instance
            party: The party doing the shopping
            price_modifier: Price multiplier (e.g., 1.5 = 50% more expensive)
            buy_rate: How much shop pays for items (default 40%)
        """
        self.shop = shop
        self.party = party
        self.price_modifier = price_modifier
        self.buy_rate = buy_rate
        self.active_character_index = 0
        # Initialize item factory for creating items
        self.item_factory = MagicItemFactory()

    @property
    def active_character(self) -> PlayerCharacter:
        """Get the currently active character for transactions"""
        return self.party.members[self.active_character_index]

    def set_active_character(self, index: int) -> bool:
        """Set which party member is actively shopping

        Args:
            index: Index of party member

        Returns:
            True if successful, False if invalid index
        """
        if 0 <= index < len(self.party.members):
            self.active_character_index = index
            return True
        return False

    def get_party_gold(self) -> float:
        """Get total gold value across all party members"""
        return sum(m.get_total_money() for m in self.party.members)

    def get_item_price(self, item_id: str) -> Optional[int]:
        """Get the price of an item with modifier applied

        Args:
            item_id: Item identifier

        Returns:
            Modified price, or None if item not found
        """
        base_price = self.shop.get_item_price(item_id)
        if base_price is None:
            return None
        return int(base_price * self.price_modifier)

    def buy_item(self, item_id: str) -> Tuple[bool, str]:
        """Purchase item and add to active character's inventory

        Args:
            item_id: Item to purchase

        Returns:
            (success, message) tuple
        """
        # Check if item is available
        if not self.shop.has_item(item_id):
            return False, f"Item not in stock."

        # Get price
        price = self.get_item_price(item_id)
        if price is None:
            return False, "Item not found."

        # Check if character can afford it (in gold pieces)
        if self.active_character.get_total_money() < price:
            return False, f"Not enough gold. Need {price}gp, have {self.active_character.get_total_money():.1f}gp."

        # Create the item from item factory
        try:
            # Check if item exists in the factory's base items
            if item_id not in self.item_factory.base_items:
                return False, f"Item data not found: {item_id}"

            item_data = self.item_factory.base_items[item_id]

            # Check weight capacity
            item_weight = item_data.get('weight_gp', item_data.get('weight', 0))
            if not self.active_character.inventory.can_carry(item_weight):
                return False, "Too heavy to carry."

            # Deduct gold from character (try exact gp first, then convert)
            if self.active_character.gold_pieces >= price:
                self.active_character.gold_pieces -= price
            elif self.active_character.subtract_money(gp=price):
                pass  # Successfully subtracted
            else:
                # Need to convert coins
                total_gp_value = self.active_character.get_total_money()
                if total_gp_value >= price:
                    # Convert all to gold and subtract
                    self.active_character.copper_pieces = 0
                    self.active_character.silver_pieces = 0
                    self.active_character.electrum_pieces = 0
                    self.active_character.gold_pieces = int(total_gp_value - price)
                    self.active_character.platinum_pieces = 0
                else:
                    return False, f"Not enough gold. Need {price}gp, have {total_gp_value:.1f}gp."

            # Reduce shop stock
            self.shop.buy_item(item_id)

            # Add to inventory
            self.active_character.inventory.add_item(item_id, item_data)

            return True, f"Purchased {item_data['name']} for {price}gp."

        except Exception as e:
            # Rollback not possible with coin conversion, so just report error
            return False, f"Error purchasing item: {e}"

    def sell_item(self, item_id: str) -> Tuple[bool, str]:
        """Sell item from active character's inventory

        Args:
            item_id: Item to sell

        Returns:
            (success, message) tuple
        """
        # Check if character has the item
        if not self.active_character.inventory.has_item(item_id):
            return False, "You don't have that item."

        # Get item from inventory to determine value
        item = self.active_character.inventory.get_item(item_id)
        if item is None:
            return False, "Item not found in inventory."

        # Calculate sell price (shop pays buy_rate * base_value)
        base_value = item.get('cost_gp', item.get('cost', 0))
        sell_price = int(base_value * self.buy_rate)

        # Remove from inventory
        self.active_character.inventory.remove_item(item_id)

        # Add gold to character
        self.active_character.add_money(gp=sell_price)

        return True, f"Sold {item['name']} for {sell_price}gp."

    def list_shop_inventory(self) -> List[Dict]:
        """Get shop inventory with modified prices

        Returns:
            List of item dictionaries with prices
        """
        items = self.shop.list_items()
        for item in items:
            item['price'] = int(item['price'] * self.price_modifier)
        return items


class InnInterface:
    """Bridge between Inn system and Party for campaign mode

    Handles rest, healing, and service purchases for the entire party.
    """

    def __init__(self, inn: Inn, party: Party, rate_per_night: int = 10):
        """Initialize inn interface

        Args:
            inn: The inn instance
            party: The party resting
            rate_per_night: Cost per person per night
        """
        self.inn = inn
        self.party = party
        self.rate_per_night = rate_per_night

    def rest(self, nights: int = 1) -> Tuple[bool, str]:
        """Rest party at inn

        Args:
            nights: Number of nights to rest

        Returns:
            (success, message) tuple
        """
        # Calculate total cost
        living_members = [m for m in self.party.members if m.is_alive]
        if not living_members:
            return False, "No living party members to rest."

        total_cost = self.rate_per_night * nights * len(living_members)

        # Check if party has enough gold
        party_gold = sum(m.get_total_money() for m in self.party.members)
        if party_gold < total_cost:
            return False, f"Not enough gold. Need {total_cost}gp for {nights} night(s)."

        # Deduct gold from members (try to take from their gold_pieces)
        remaining_cost = total_cost
        for member in living_members:
            if remaining_cost <= 0:
                break

            member_gold = member.get_total_money()
            deduct = min(member_gold, remaining_cost)

            # Try to subtract exact gold pieces first
            if member.gold_pieces >= deduct:
                member.gold_pieces -= int(deduct)
            else:
                # Convert all coins to gold and subtract
                member.copper_pieces = 0
                member.silver_pieces = 0
                member.electrum_pieces = 0
                member.gold_pieces = int(member_gold - deduct)
                member.platinum_pieces = 0

            remaining_cost -= deduct

        # Restore HP and spells for all living members
        for member in living_members:
            member.hp_current = member.hp_max
            # Restore all spell slots
            if hasattr(member, 'spells_memorized'):
                member.restore_all_spells()

        return True, f"Rested for {nights} night(s). Party fully restored. Cost: {total_cost}gp"

    def get_cost_for_party(self, nights: int = 1) -> int:
        """Calculate cost for entire party to rest

        Args:
            nights: Number of nights

        Returns:
            Total cost in gold
        """
        living_members = [m for m in self.party.members if m.is_alive]
        return self.rate_per_night * nights * len(living_members)


class TempleInterface:
    """Bridge between Temple services and Party for campaign mode

    Handles healing, curse removal, and resurrection services.
    """

    # Standard temple service costs (can be overridden per temple)
    SERVICES = {
        'cure_light': {
            'cost': 10,
            'effect': 'heal',
            'amount': '1d8',
            'description': 'Cure Light Wounds (heal 1d8 HP)'
        },
        'cure_serious': {
            'cost': 50,
            'effect': 'heal',
            'amount': '2d8+1',
            'description': 'Cure Serious Wounds (heal 2d8+1 HP)'
        },
        'remove_curse': {
            'cost': 100,
            'effect': 'remove_condition',
            'condition': 'cursed',
            'description': 'Remove Curse'
        },
        'cure_disease': {
            'cost': 150,
            'effect': 'remove_condition',
            'condition': 'diseased',
            'description': 'Cure Disease'
        },
        'raise_dead': {
            'cost': 1000,
            'effect': 'resurrect',
            'requirements': 'body_present',
            'description': 'Raise Dead (requires body, character below level 10)'
        },
    }

    def __init__(self, party: Party, available_services: List[str], donation_based: bool = False):
        """Initialize temple interface

        Args:
            party: The party receiving services
            available_services: List of service IDs this temple offers
            donation_based: If True, costs are suggested donations
        """
        self.party = party
        self.available_services = available_services
        self.donation_based = donation_based

    def get_available_services(self) -> List[Dict]:
        """Get list of services this temple offers

        Returns:
            List of service dictionaries
        """
        return [
            {**service, 'name': name}
            for name, service in self.SERVICES.items()
            if name in self.available_services
        ]

    def purchase_service(self, service_name: str, target_character_index: int,
                        paid_amount: Optional[int] = None) -> Tuple[bool, str]:
        """Purchase a temple service for a party member

        Args:
            service_name: Service identifier
            target_character_index: Index of party member to receive service
            paid_amount: Optional custom payment (for donation-based)

        Returns:
            (success, message) tuple
        """
        # Validate service
        if service_name not in self.SERVICES:
            return False, "Service not available."

        if service_name not in self.available_services:
            return False, "This temple does not offer that service."

        # Validate target
        if target_character_index < 0 or target_character_index >= len(self.party.members):
            return False, "Invalid party member."

        target = self.party.members[target_character_index]
        service = self.SERVICES[service_name]

        # Determine cost
        cost = paid_amount if self.donation_based and paid_amount is not None else service['cost']

        # Check if party can afford
        party_gold = sum(m.get_total_money() for m in self.party.members)
        if party_gold < cost:
            return False, f"Not enough gold. Need {cost}gp."

        # Deduct gold from party members
        remaining = cost
        for member in self.party.members:
            if remaining <= 0:
                break
            member_gold = member.get_total_money()
            deduct = min(member_gold, remaining)

            # Try to subtract exact gold pieces first
            if member.gold_pieces >= deduct:
                member.gold_pieces -= int(deduct)
            else:
                # Convert all coins to gold and subtract
                member.copper_pieces = 0
                member.silver_pieces = 0
                member.electrum_pieces = 0
                member.gold_pieces = int(member_gold - deduct)
                member.platinum_pieces = 0

            remaining -= deduct

        # Apply effect
        effect = service['effect']

        if effect == 'heal':
            # Simple healing (would need dice roller for actual implementation)
            # For now, use middle value
            if service['amount'] == '1d8':
                heal_amount = 5
            elif service['amount'] == '2d8+1':
                heal_amount = 10
            else:
                heal_amount = 5

            target.hp_current = min(target.hp_current + heal_amount, target.hp_max)
            return True, f"{target.name} healed for {heal_amount} HP. Cost: {cost}gp"

        elif effect == 'remove_condition':
            condition = service['condition']
            # Would need to implement conditions system
            return True, f"{condition.capitalize()} removed from {target.name}. Cost: {cost}gp"

        elif effect == 'resurrect':
            if target.is_alive:
                return False, f"{target.name} is already alive."

            target.is_alive = True
            target.hp_current = 1
            return True, f"{target.name} has been raised from the dead! Cost: {cost}gp"

        return False, "Unknown service effect."
