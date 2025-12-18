Rats use disease bite but players don't get diseased.  Check special attacks.

Centipede, Giant injects toxic venom - deals poison damage!

When a character get to 0 (slain in dungeon) but character is healed at the temple (Still Alive).  Not marked dead?

Skeleton uses undead!

Skeleton uses immune_to_charm!

Grukk, Hobgoblin Chieftain uses command_presence!

Grukk, Hobgoblin Chieftain uses tactical_genius!

When trying to sell items: Error: 'Weapon'(or 'Armor') object has no attribute 'get'
Traceback (most recent call last):
  File "/mnt/d/Development/aerthos/web_ui/app.py", line 1268, in shop_sell
    success, message = shop_interface.sell_item(item_id)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Development/aerthos/web_ui/../aerthos/campaign/hub_interfaces.py", line 160, in sell_item
    base_value = item.get('cost_gp', item.get('cost', 0))
                 ^^^^^^^^
AttributeError: 'Weapon' object has no attribute 'get'
127.0.0.1 - - [17/Dec/2025 11:30:32] "POST /api/campaigns/329dac52-01e2-4bba-bfa0-0355b31d8ae8/shop/sell HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/mnt/d/Development/aerthos/web_ui/app.py", line 1268, in shop_sell
    success, message = shop_interface.sell_item(item_id)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Development/aerthos/web_ui/../aerthos/campaign/hub_interfaces.py", line 160, in sell_item
    base_value = item.get('cost_gp', item.get('cost', 0))
                 ^^^^^^^^
AttributeError: 'Weapon' object has no attribute 'get'
127.0.0.1 - - [17/Dec/2025 11:30:33] "POST /api/campaigns/329dac52-01e2-4bba-bfa0-0355b31d8ae8/shop/sell HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/mnt/d/Development/aerthos/web_ui/app.py", line 1268, in shop_sell
    success, message = shop_interface.sell_item(item_id)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Development/aerthos/web_ui/../aerthos/campaign/hub_interfaces.py", line 160, in sell_item
    base_value = item.get('cost_gp', item.get('cost', 0))
                 ^^^^^^^^
AttributeError: 'Weapon' object has no attribute 'get'
127.0.0.1 - - [17/Dec/2025 11:30:41] "POST /api/campaigns/329dac52-01e2-4bba-bfa0-0355b31d8ae8/shop/sell HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/mnt/d/Development/aerthos/web_ui/app.py", line 1268, in shop_sell
    success, message = shop_interface.sell_item(item_id)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Development/aerthos/web_ui/../aerthos/campaign/hub_interfaces.py", line 160, in sell_item
    base_value = item.get('cost_gp', item.get('cost', 0))
                 ^^^^^^^^
AttributeError: 'Armor' object has no attribute 'get'