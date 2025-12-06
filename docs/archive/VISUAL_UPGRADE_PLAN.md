# Aerthos Visual Upgrade & Analysis Report

## 1. Codebase Analysis

### Strengths
*   **Faithful Core Mechanics:** The engine (`GameState`, `CombatResolver`, `MagicSystem`) accurately implements AD&D 1st Edition rules, including THAC0, descending AC, Vancian magic memorization, and initiative segments. This provides a distinct "Old School" tactical feel.
*   **Scalable Architecture:** The hierarchy of **Campaign > Episode > Dungeon** allows for infinite content expansion. You can add new adventures via JSON without touching the core engine code.
*   **Data-Driven Design:** Almost all content (monsters, items, spells, rooms) is defined in JSON. This makes the game highly moddable and easy to balance by tweaking data files.
*   **Hybrid Interface:** The dual support for a robust CLI and a Flask-based Web UI is excellent. It allows for quick testing/debugging in CLI while offering a more accessible interface for players.

### Weaknesses & Opportunities
*   **Visual Immersion:** Currently, the game relies entirely on text descriptions. While the writing is good, modern (and even retro) players expect visual context. The "Gold Box" aesthetic is currently just layout-based; it lacks the iconic first-person viewports and monster visualizations.
*   **"God Object" Risks:** The `GameState` class is becoming a central dependency for routing, logic, and state management. As complexity grows (e.g., adding faction reputation, complex puzzles), this class might become hard to maintain.
*   **Web UI Reliance:** The frontend (`game.html`) relies on a single massive JSON payload (`get_game_state_json`). While simple, this creates tight coupling. Changing the backend state structure breaks the frontend.

---

## 2. Visual Upgrade Plan

**Objective:** Transform Aerthos from a text adventure into a graphical RPG by integrating generated world and monster images into the Web UI.

### Phase 1: Asset Pipeline
*Goal: Make the images accessible to the Flask application.*

1.  **Directory Structure:**
    *   Do not move the original `docs/images` folders (keep them as the source of truth).
    *   Create symbolic links or copy scripts to expose these assets to Flask.
    *   **Action:** Create `web_ui/static/images/world/` and link it to `docs/images/world/`.
    *   **Action:** Create `web_ui/static/images/monsters/` and link it to `docs/images/monsters/`.
    *   *Note:* Flask serves static files from the `static` folder by default. This will automatically expose the nested `campaign_monsters` directory as well.

2.  **Naming Convention Verification:**
    *   **World:** Ensure `[dungeon_id]_[room_id].jpeg` matches game data.
    *   **Monsters:** Ensure file names match monster IDs (e.g., `aboleth_spawn.jpeg`).
    *   *Requirement:* The game engine needs to know the `dungeon_id` explicitly.

### Phase 2: Backend Logic (`web_ui/app.py`)
*Goal: Tell the frontend which images to show.*

1.  **Update `get_game_state_json` function (World):**
    *   Calculate the expected image path based on current state.
    *   **Logic:**
        ```python
        # Pseudo-code for app.py
        dungeon_id = game_state.dungeon.id
        room_id = game_state.current_room.id
        image_path = f"images/world/{dungeon_id}/{dungeon_id}_{room_id}.jpeg"
        
        return {
            'room': {
                'image_url': image_path,
                # ...
            }
        }
        ```

2.  **Update Combat Logic (Monsters):**
    *   When constructing the combat state, resolve monster images.
    *   **Priority Logic:**
        1.  Check `static/images/monsters/campaign_monsters/{monster_id}.jpeg`
        2.  Check `static/images/monsters/{monster_id}.jpeg` (or .png)
        3.  Fallback to `static/images/monsters/generic_monster.jpeg`
    *   **JSON Output:**
        ```json
        "combat": {
            "active": true,
            "opponents": [
                {
                    "name": "Aboleth Spawn",
                    "id": "aboleth_spawn",
                    "image_url": "images/monsters/campaign_monsters/aboleth_spawn.jpeg",
                    "hp_status": "Wounded"
                }
            ]
        }
        ```

3.  **Hub/City Support:**
    *   Extend logic to handle Cities (`CampaignManager` state).
    *   If `current_hub_id` is active, look for `[city_id]_[shop_id].jpeg` or `[city_id]_overview.jpeg`.

### Phase 3: Frontend Implementation (`web_ui/templates/game.html`)
*Goal: Display the images in the "Gold Box" layout.*

1.  **Layout Modification (World View):**
    *   Insert an image container within the `.main-display`.
    *   **CSS:**
        ```css
        .scene-view {
            position: relative;
            width: 100%;
            height: 300px;
            background-color: #000;
            border-bottom: 2px solid #0f0;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .scene-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
        }
        ```

2.  **Layout Modification (Combat/Monster View):**
    *   Overlay monster sprites on top of the scene image or display them in a "Picture-in-Picture" style.
    *   **CSS:**
        ```css
        .combat-view {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            height: 80%; /* Large sprite */
            z-index: 10;
            pointer-events: none; /* Let clicks pass through if needed */
        }
        ```

3.  **JavaScript Update (`updateDisplay` function):**
    *   Bind the image URL from the JSON state to the DOM elements.
    *   Handle both room/scene images and combat/monster images.
    *   **Logic:**
        ```javascript
        // Update Scene
        const imgEl = document.getElementById('scene-image');
        if (state.room.image_url) {
            imgEl.src = '/static/' + state.room.image_url;
            imgEl.style.display = 'block';
        } else {
            imgEl.style.display = 'none';
        }

        // Update Combat
        const combatEl = document.getElementById('combat-sprite');
        if (state.combat.active && state.combat.opponents.length > 0) {
            combatEl.src = '/static/' + state.combat.opponents[0].image_url;
            combatEl.style.display = 'block';
        } else {
            combatEl.style.display = 'none';
        }
        ```

### Phase 4: Polish & Fallbacks
*Goal: Ensure the game looks good even when images are missing.*

1.  **Default Placeholders:**
    *   Create generic images for: `generic_dungeon.jpeg`, `generic_shop.jpeg`, `generic_monster.jpeg`.
    *   Use these as fallbacks in the Python logic if specific images don't exist.

2.  **Transition Effects:**
    *   Add a simple CSS fade-in effect when the image changes to smooth out movement between rooms.

## 3. Execution Checklist

- [ ] **Backup:** Commit current stable state to git.
- [ ] **Assets:** Symlink `docs/images/world` to `web_ui/static/images/world`.
- [ ] **Assets:** Symlink `docs/images/monsters` to `web_ui/static/images/monsters`.
- [ ] **Backend:** Edit `aerthos/world/dungeon.py` to ensure `id` is accessible.
- [ ] **Backend:** Edit `web_ui/app.py` to generate and send `image_url` for rooms.
- [ ] **Backend:** Edit `web_ui/app.py` (or helper) to resolve and send `image_url` for combat opponents.
- [ ] **Frontend:** Edit `web_ui/templates/game.html` to add the `.scene-view` and combat overlay containers.
- [ ] **Frontend:** Edit `web_ui/templates/game.html` JS to handle image updates for both world and monsters.
- [ ] **Test:** Verify Drowned Ruins loads correct room images.
- [ ] **Test:** Verify combat triggers display of monster images.