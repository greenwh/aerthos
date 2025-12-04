
¦ > In my aerthos AD&D game.  getting some errors:

  1) In the campaign in the shop when I try to buy something I get an error: Error: Error purchasing item: 'Inventory'
  object has no attribute 'can_carry'

  2) In game when I try to save using the save button in the web_ui I get:
    File "/mnt/d/Development/aerthos/web_ui/app.py", line 1412, in save_campaign_checkpoint
      campaign.last_played = datetime.now()
                             ^^^^^^^^
  NameError: name 'datetime' is not defined. Did you forget to import 'datetime'

  3) When starting a campaign selecting a party, the party says characters (0) but loads anyway