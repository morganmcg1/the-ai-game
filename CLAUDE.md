# Project: SurvAIve

A multiplayer survival party game where players respond to AI-generated deadly scenarios. An AI judge evaluates survival strategies and determines who lives or dies. Features AI-generated scenario images, death scenes, character avatars, and personalized end-game videos.

**Tech Stack:** React 19 frontend + FastAPI backend + Modal serverless deployment + OpenRouter LLM (Kimi K2) + FAL AI image/video generation

---

## Game Flow & Screens

### 1. Welcome Screen (`Lobby.jsx` - menu mode)
- Two options: "NEW GAME" or "JOIN GAME"
- New Game: Creates game with unique 4-character code, creator becomes admin (Cmd+Enter shortcut)
- Join Game: Enter game code + player name

### 2. Character Creation (`Lobby.jsx` - character mode)
- Optional 5-field character customization:
  - Physical Vibe, Signature Weapon, Hidden Talent, Fatal Flaw, Catchphrase
- Can skip character creation entirely
- If provided, generates AI character avatar asynchronously
- Preview mode shows generated avatar before entering lobby
- Can regenerate avatar with different visual style

### 3. Game Lobby (`App.jsx` - status: 'lobby')
- Displays all connected players with avatars (if created)
- Players only visible once they complete character preview (`in_lobby` gate)
- Admin sees "START GAME" button
- Non-admins see "Waiting for {hostName} to start the game..."
- First player to join is automatically admin

### 4. Scenario View (`ScenarioView.jsx` - round status: 'scenario')
- Displays AI-generated deadly scenario with narrative framing
- Shows AI-generated scenario image
- System message displays round progression (e.g., "CALIBRATION MODE // ANOMALIES DETECTED")
- Dead players see "WITNESS THE CARNAGE" spectator message

### 5. Strategy Input (`InputView.jsx` - round status: 'strategy')
- Textarea for survival strategy submission
- Keyboard shortcut: Cmd/Ctrl + Enter to submit
- Shows "TRANSMITTING..." during submission
- After submission: "STRATEGY UPLOADED. AWAITING JUDGEMENT."

### 6. Judgement State (`App.jsx` - round status: 'judgement')
- "JUDGING..." with glitch text animation
- AI evaluates all strategies in parallel
- Generates result images in parallel

### 7. Results View (`ResultsView.jsx` - round status: 'results')
- "JUDGEMENT DAY" title with glitch effect
- Player cards showing: name, strategy, death/survival reason, result image, points earned
- Leaderboard showing current standings
- Admin sees "NEXT ROUND" or "END GAME" button

### 8. Game Over (`App.jsx` - status: 'finished')
- Video generation starts asynchronously (4-phase parallel pipeline)
- Shows "EXTRACTING CONSCIOUSNESS DATA..." during video generation
- Video carousel displays personalized 10-second videos for all players
- Winner gets triumphant message, others get consoling/humorous messages
- Final standings leaderboard
- "RE-ENTER SIMULATION" button to play again

---

## Round Types

### Survival Mode (default)
- AI generates deadly scenario with narrative framing
- Players submit survival strategies
- AI judges each strategy and determines survival
- +100 points for surviving

### Blind Architect Mode
- Players design deadly scenarios for opponents
- Visual voting on trap images (no text shown)
- Winner's trap becomes the scenario
- Trap creator gets +500 bonus points
- Then proceeds to standard strategy/judgement phase

### Ranked Mode
- All strategies are compared and ranked by the LLM judge
- Everyone survives, but points awarded based on rank position
- Must wait for ALL submissions before judging (comparative evaluation)
- Ranking criteria: creativity, effectiveness, entertainment value, specificity
- **Scoring** (4+ players): 1st: 300, 2nd: 200, 3rd: 100, 4th: 50, 5th+: 25
- **Scoring** (3 players): 1st: 250, 2nd: 125, 3rd: 25
- **Scoring** (2 players): 1st: 200, 2nd: 50
- Images generated in parallel after ranking is determined

### Cooperative Mode
- Team-based survival round
- Players submit strategies and AI generates images for each
- Players vote on best strategy image
- Vote points distributed: +200 (1st), +100 (2nd), 0 (middle), -100 (last)
- Team survives/fails based on highest-voted strategy judgement
- If survived: Random player gets +200 bonus
- If failed: All alive players lose -100 points

### Sacrifice Mode
- One player must die heroically so others survive
- **Volunteer Phase**: Players click "I VOLUNTEER AS TRIBUTE" to nominate themselves
- **Voting Phase**: All players vote on who becomes the martyr
  - If volunteers exist: vote only among volunteers
  - If NO volunteers: everyone is eligible (cowards get drafted)
- **Submission Phase**: Chosen martyr writes their epic death speech/action
- **Judgement Phase**: AI judges how epic the death was
- **Results**:
  - Epic death → Martyr: +500 pts, all others survive with +100 pts each
  - Lame death → Everyone dies, no points awarded

### Last Stand Mode (Final Boss)
- Brutal final round with harsh AI judgement (~20-30% survival rate)
- **Strategy Phase**: Standard strategy submission
- **Judgement Phase**: AI judges harshly - only exceptional strategies survive
- **Revival Phase** (if survivors AND dead players exist):
  - Survivors vote to revive ONE dead player
  - Must be **unanimous** (all survivors pick same person)
  - Dead players' strategies are visible to help decide
  - If unanimous: Revived player's strategy gets re-judged with teamwork bonus
  - If not unanimous: No revival, dead stay dead
- Skips revival if everyone survived or everyone died

---

## Game Mechanics

### Scoring
- **+100 points**: Survive a survival/last_stand round
- **+500 points**: Win trap voting (Blind Architect mode)
- **+500 points**: Epic sacrifice death (Sacrifice mode - martyr only)
- **+100 points**: Saved by epic sacrifice (Sacrifice mode - survivors)
- **Cooperative voting**: +200 (1st), +100 (2nd), 0 (middle), -100 (last)
- **Cooperative team outcome**: +200 random bonus if survived, -100 all if failed
- **Ranked mode** (4+ players): 1st: 300, 2nd: 200, 3rd: 100, 4th: 50, 5th+: 25
- Winner: Highest score after all rounds

### Round Configuration
Rounds are configured via `round_config` array in GameState:
```python
round_config: list[str] = ["survival", "survival", "cooperative", "sacrifice", "last_stand"]
```
The last round type in the array is always used for the final round.

### Phase Progression
- Automatic advancement when all active players submit
- 60-second heartbeat timeout for inactive players
- Inactive players skipped in progression checks
- Admin manually advances from results to next round

### Player States
- `is_alive`: Tracked per round
- `is_admin`: First player to join
- `in_lobby`: Controls visibility during lobby (set after character preview)
- Players "resurrected" between rounds (death is per-round, not permanent)

### Narrative Progression
System messages displayed based on round progression:
- Round 1: "SYSTEM BOOT // LEVEL 1 INITIALIZED"
- Round 2: "CALIBRATION MODE // ANOMALIES DETECTED"
- Final: "EXIT PROTOCOL // FINAL LEVEL"
- Mid rounds: "WARNING: CORRUPTION AT X% // REALITY UNSTABLE"
- Blind Architect: "SECURITY BREACH DETECTED // ARCHITECT PROTOCOL ACTIVATED"
- Ranked: "PERFORMANCE EVALUATION // SURVIVAL EFFICIENCY RANKING PROTOCOL"
- Cooperative: "CRITICAL ERROR // COLLABORATIVE SUBROUTINE REQUIRED"
- Sacrifice: "CRITICAL FAILURE // ONE MUST FALL FOR OTHERS TO SURVIVE"
- Last Stand: "EXIT PROTOCOL // FINAL LEVEL // MAXIMUM DIFFICULTY"

---

## Technical Architecture

### Frontend (`frontend/src/`)

| File | Purpose |
|------|---------|
| `App.jsx` | Main component, game state management, 2-second polling |
| `api.js` | API client (createGame, joinGame, getGameState, etc.) |
| `Lobby.jsx` | Welcome screen, create/join game, character creation |
| `ScenarioView.jsx` | Display scenario text + image + system message |
| `InputView.jsx` | Strategy submission form |
| `TrapView.jsx` | Blind Architect trap creation |
| `VotingView.jsx` | Trap voting grid |
| `CoopVotingView.jsx` | Cooperative mode strategy voting |
| `SacrificeVolunteerView.jsx` | Sacrifice round volunteer phase |
| `SacrificeVotingView.jsx` | Sacrifice round martyr voting |
| `SacrificeSubmissionView.jsx` | Martyr death speech submission |
| `RevivalVotingView.jsx` | Last Stand revival voting |
| `ResultsView.jsx` | Round results display + leaderboard |
| `DebugMenu.jsx` | Debug menu overlay (Ctrl/Cmd+Shift+. to open) |
| `index.css` | Global styles (neon/dark theme) |

**Key Frontend Patterns:**
- Polling-based state sync (2-second interval)
- Optimistic UI updates with `pendingStrategyRef` to prevent race conditions
- Framer Motion for animations
- Lucide React for icons
- Keyboard shortcuts (Cmd+Enter) on key buttons

### Backend (`backend/app.py`)

**Framework:** FastAPI with Modal serverless deployment

**Storage:** `modal.Dict` for game state persistence

**AI Services:**
- **LLM (Scenarios/Judgement)**: OpenRouter API with Kimi K2 model (`moonshotai/kimi-k2-0905`)
- **LLM (Video Scripts)**: Mistral Small (`mistralai/mistral-small-3.1-24b-instruct`)
- **Images**: FAL AI flux/krea model
- **Videos**: FAL AI Kling 2.6 Pro (`kling-video/v2.6/pro/image-to-video`)

### Centralized Prompts (`backend/prompts.py`)

All LLM prompts are centralized in `prompts.py` for easy editing. Prompts use `{{variable}}` placeholders.

**Usage:**
```python
import prompts

prompt = prompts.format_prompt(
    prompts.STRATEGY_JUDGEMENT,
    scenario="A monster attacks...",
    strategy="I run away!"
)
```

**Available Prompts:**

| Prompt | Purpose |
|--------|---------|
| `SCENARIO_GENERATION` | Generate deadly survival scenarios |
| `LAST_STAND_SCENARIO` | Generate Evil Santa final boss scenario |
| `STRATEGY_JUDGEMENT` | Judge if survival strategies work |
| `RANKED_JUDGEMENT` | Rank all strategies comparatively |
| `SACRIFICE_JUDGEMENT` | Judge how epic a martyr's death was |
| `LAST_STAND_JUDGEMENT` | Harsh Evil Santa judgement (~20-30% survival) |
| `REVIVAL_JUDGEMENT` | Re-judge revived player with leniency |
| `VIDEO_SCRIPT_GENERATION` | Generate personalized end-game video scripts |
| `CHARACTER_IMAGE` | Full character image prompt with action scene |
| `CHARACTER_SIMPLE` | Simple character portrait prompt |

**Image Prompts:**
- `TIMEOUT_IMAGE_OPTIONS` - List of timeout failure scene descriptions
- `TIMEOUT_IMAGE_SUFFIX` - Suffix added to timeout prompts
- `COOP_STRATEGY_IMAGE` - Strategy illustration template
- `VIDEO_BASE_IMAGE` - Video base image template

**Fallback Responses:**
- `FALLBACK_SCENARIO`, `FALLBACK_LAST_STAND_SCENARIO`
- `FALLBACK_STRATEGY_JUDGEMENT`, `FALLBACK_SACRIFICE_JUDGEMENT`
- `FALLBACK_LAST_STAND_JUDGEMENT`, `FALLBACK_REVIVAL_JUDGEMENT`
- `FALLBACK_RANKED_COMMENTARY`, `FALLBACK_RANKED_VISUAL`
- `FALLBACK_VIDEO_SCRIPT`

**Helper Functions:**
- `format_prompt(template, **kwargs)` - Replace `{{var}}` placeholders
- `build_video_context(player_name, rank, total_players, score)` - Returns `(context, tone)` for video scripts

### Configuration (`config.yaml`)

All configurable values are centralized in `config.yaml`:

| Section | Settings |
|---------|----------|
| `game` | Timers, round count, heartbeat timeout |
| `llm` | API URLs, timeouts |
| `models` | LLM model names per use case |
| `image_generation` | FAL settings, image size, inference steps |
| `image_models` | Image model per use case |
| `video_generation` | Video model, duration, polling settings |
| `scoring` | Points for survival, sacrifice, coop, ranked |

---

## Implementation Patterns

### Parallel Async Execution

LLM judging and image generation run in parallel using `asyncio.gather()`:

```python
async def run_all_judgements():
    tasks = []
    for pid, p in game.players.items():
        if p.strategy and p.is_alive:
            tasks.append(judge_and_generate(pid, p.name, p.strategy, scenario))

    # All LLM + image calls run concurrently
    results = await asyncio.gather(*tasks)
```

Uses `httpx.AsyncClient` for non-blocking HTTP requests to OpenRouter and FAL APIs.

### Pre-warmed Scenarios

Scenarios are generated in parallel when game is created:
```python
@app.function()
async def prewarm_all_scenarios(game_code: str, num_rounds: int, round_config: list[str]):
    # Generates all survival scenarios concurrently
    # Skips blind_architect rounds (scenario comes from player trap)
```

### End-Game Video Generation

4-phase parallel pipeline when game finishes:
1. **Phase 1**: Generate LLM prompts for all players in parallel (personalized scripts)
2. **Phase 2**: Generate base images for all players in parallel
3. **Phase 3**: Submit video requests in parallel (async queue)
4. **Phase 4**: Poll all video statuses in parallel (5-second intervals, max 7.5 min)

Videos stored in `game.player_videos` dict, status tracked via `game.videos_status`.

### Frontend Polling & State Sync

The frontend uses a 2-second polling interval to sync game state:

**Race Condition Prevention:** When a player submits a strategy, there's a race between the optimistic UI update and the next poll response. This is handled with `pendingStrategyRef`:

1. On submit: Store strategy in `pendingStrategyRef.current`
2. On poll: If server state doesn't have our strategy yet, inject it locally
3. Once server confirms: Clear the pending ref

### Backend State Transitions

**Survival Round Flow:**
```
strategy → judgement → results
```

**Blind Architect Flow:**
```
trap_creation → trap_voting → strategy → judgement → results
```

**Ranked Flow:**
```
strategy (wait for ALL) → ranked_judgement → results
```

**Cooperative Flow:**
```
strategy → coop_voting → coop_judgement → results
```

**Sacrifice Flow:**
```
sacrifice_volunteer → sacrifice_voting → sacrifice_submission → sacrifice_judgement → results
```

**Last Stand Flow:**
```
strategy → judgement → last_stand_revival → revival_judgement → results
```
(Revival phase skipped if everyone survived or everyone died)

### Modal Serverless Architecture

**Secrets:** Stored in Modal's secret storage:
```bash
modal secret create ai-game-secrets MOONSHOT_API_KEY=xxx FAL_KEY=xxx --env ai-game
```

**Persistent Storage:** Uses `modal.Dict` for game state:
```python
games = modal.Dict.from_name("mas-ai-games", create_if_missing=True)
```

**Async Functions:** Modal functions can be spawned with `.spawn()` for fire-and-forget execution:
- `prewarm_all_scenarios.spawn()` - Pre-generate scenarios at game creation
- `generate_character_image.spawn()` - Generate character avatars
- `generate_coop_strategy_images.spawn()` - Generate coop strategy images
- `run_round_judgement.spawn()` - Run judgement phase
- `run_ranked_judgement.spawn()` - Comparative ranking judgement
- `run_coop_judgement.spawn()` - Run cooperative judgement
- `run_sacrifice_judgement.spawn()` - Judge martyr's death (epic or lame)
- `run_last_stand_judgement.spawn()` - Harsh final boss judgement
- `run_revival_judgement.spawn()` - Re-judge revived player with bonus
- `generate_all_player_videos.spawn()` - Generate end-game videos

### LLM Integration Notes

**JSON Response Handling:** OpenRouter models don't reliably support `response_format`. Instead:
1. Prompt explicitly requests JSON-only output
2. Response is parsed with regex to extract JSON from markdown code blocks
3. Fallback JSON is returned on any error

**Error Recovery:** If judgement fails for a player, they default to "dead" with a generic message so the game can continue.

---

## Debugging

### Debug Menu (Keyboard Shortcut)

Press **`Ctrl+Shift+.`** or **`Cmd+Shift+.`** to open the debug menu. This allows you to:

- **Skip to any game state**: Lobby, Playing, or Finished
- **Jump to specific round types**: Survival, Blind Architect, Cooperative, Sacrifice, Last Stand, Ranked
- **Jump to specific round phases**: scenario, strategy, judgement, results, voting phases, etc.
- **Set round number**: Test any round 1-10
- **Add dummy players**: Spawn 0-10 test bots with placeholder avatars

The debug menu automatically sets up all required game state (players, rounds, metadata) so screens render correctly without playing through the whole game. Dummy players use a placeholder avatar image.

**Backend endpoint:** `/api/debug_skip_to_state`

### Modal Logs

You can check the deployments logs on Modal to help with deployment issues like console errors or hung processes due to race conditions.

## Known Issues & Pitfalls

### Modal Dict Eventual Consistency

**Problem:** `modal.Dict` may have eventual consistency. If you save data and immediately re-fetch, you might not see your changes.

**Solution:** After modifying game state, continue using the same object for subsequent logic. Don't re-fetch unless absolutely necessary.

```python
# GOOD - Use the same object
game.players[player_id].strategy = strategy
if all_strategies_submitted(game):
    advance_to_judgement()
save_game(game)  # Save once at the end
```

### Frontend Polling Race Conditions

**Problem:** After submitting data, the next poll response might arrive before the server has processed/saved the submission.

**Solution:** Use optimistic updates with refs to track pending operations. See `App.jsx` for the `pendingStrategyRef` implementation.

### Timeout Handling - Game Hangs

**Problem:** When a phase times out, if the code doesn't explicitly advance `current_round.status`, the game hangs indefinitely. This has affected multiple phases:
- `strategy` - Players who don't submit are marked dead but round stays in "strategy"
- `trap_creation` - Same issue
- `sacrifice_volunteer` - Had NO timeout handling at all

**Solution:** Every timeout handler in `api_get_game_state` MUST:
1. Mark timed-out players appropriately (dead, etc.)
2. Clear `submission_start_time = None`
3. Check if round should advance and set new `status`
4. Spawn appropriate judgement/next phase function

**Edge Case - All Players Dead:** If ALL players timeout, skip directly to `"results"` instead of `"judgement"` (nothing to judge). For cooperative mode, also set `coop_team_survived = False`.

```python
# After handling timeouts, check if everyone is dead
all_dead = all(not p.is_alive for p in lobby_players)
if all_dead:
    current_round.status = "results"  # Skip judgement
else:
    current_round.status = "judgement"
    run_round_judgement.spawn(game.code)
```

### Timeout Images

Timeout images are generated for ALL round types (not just cooperative) via `generate_timeout_image.spawn()`. The images show characters "doing nothing" while death approaches - see `TIMEOUT_IMAGE_OPTIONS` in `prompts.py` for the prompt options.

---

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/create_game` | POST | Create new game, returns 4-char code |
| `/api/join_game?code={code}` | POST | Join game with `{ name, character_description? }` body |
| `/api/enter_lobby?code={code}` | POST | Mark player as ready for lobby `{ player_id }` |
| `/api/get_game_state?code={code}&player_id={id}` | GET | Poll current state |
| `/api/start_game?code={code}` | POST | Admin starts game |
| `/api/submit_strategy?code={code}` | POST | Submit strategy `{ player_id, strategy }` |
| `/api/submit_trap?code={code}` | POST | Submit trap `{ player_id, trap_text }` |
| `/api/vote_trap?code={code}` | POST | Vote for trap `{ voter_id, target_id }` |
| `/api/vote_coop?code={code}` | POST | Vote in coop mode `{ voter_id, target_id }` |
| `/api/volunteer_sacrifice?code={code}` | POST | Volunteer as tribute `{ player_id }` |
| `/api/advance_sacrifice_volunteer?code={code}` | POST | Admin advances to voting `{ player_id }` |
| `/api/vote_sacrifice?code={code}` | POST | Vote for martyr `{ voter_id, target_id }` |
| `/api/submit_sacrifice_speech?code={code}` | POST | Martyr submits death speech `{ player_id, speech }` |
| `/api/vote_revival?code={code}` | POST | Survivor votes to revive `{ voter_id, target_id }` |
| `/api/advance_revival?code={code}` | POST | Admin advances from revival `{ player_id }` |
| `/api/next_round?code={code}` | POST | Admin advances round |
| `/api/regenerate_character_image?code={code}` | POST | Regenerate avatar `{ player_id }` |
| `/api/retry_player_videos?code={code}` | POST | Retry failed video generation |
| `/api/debug_skip_to_state?code={code}` | POST | Debug: skip to game state `{ player_id, game_status, round_type, round_status, round_number, num_dummy_players }` |

---

## Data Models

### GameState
```python
id: str                      # UUID
code: str                    # 4-char join code
status: str                  # "lobby" | "playing" | "finished"
players: dict                # player_id -> Player
rounds: list                 # List of Round objects
current_round_idx: int
max_rounds: int              # Default: 5
round_config: list[str]      # Round types
created_at: float
prewarmed_scenarios: list[str | None]  # Pre-generated scenarios
player_videos: dict[str, str]          # player_id -> video URL
videos_status: str           # "pending" | "generating" | "ready" | "failed"
video_theme: str | None      # Consistent theme for all videos
winner_id: str | None
```

### Player
```python
id: str                      # UUID
name: str
score: int                   # Accumulated points
is_admin: bool               # First joiner
is_alive: bool               # Current round status
in_lobby: bool               # Has completed character preview
death_reason: str | None     # From AI judge (if dead)
survival_reason: str | None  # From AI judge (if survived)
strategy: str | None         # Current round submission
result_image_url: str | None
last_active: float           # Heartbeat timestamp
character_description: str | None  # Character creation fields
character_image_url: str | None    # AI-generated avatar
```

### Round
```python
number: int                  # 1-5
type: str                    # "survival" | "blind_architect" | "cooperative" | "sacrifice" | "last_stand" | "ranked"
status: str                  # "scenario" | "strategy" | "judgement" | "results" | "trap_creation" | "trap_voting" | "coop_voting" | "coop_judgement" | "sacrifice_volunteer" | "sacrifice_voting" | "sacrifice_submission" | "sacrifice_judgement" | "last_stand_revival" | "revival_judgement" | "ranked_judgement"
scenario_text: str
scenario_image_url: str | None
style_theme: str | None      # Visual style for all images in round
system_message: str | None   # Narrative progression text

# Blind Architect specific
architect_id: str | None
trap_proposals: dict
trap_images: dict
votes: dict

# Cooperative specific
strategy_images: dict
coop_votes: dict
coop_vote_points: dict
coop_team_winner_id: str | None
coop_team_loser_id: str | None
coop_winning_strategy_id: str | None
coop_team_survived: bool | None
coop_team_reason: str | None

# Sacrifice specific
sacrifice_volunteers: dict   # player_id -> bool
sacrifice_votes: dict        # voter_id -> volunteer_id
martyr_id: str | None
martyr_speech: str | None
martyr_epic: bool | None     # was the death epic?
martyr_reason: str | None
martyr_image_url: str | None

# Last Stand revival specific
revival_votes: dict          # survivor_id -> dead_player_id
revived_player_id: str | None
revival_survived: bool | None
revival_reason: str | None
revival_image_url: str | None

# Ranked round specific
ranked_results: dict         # player_id -> rank (1 = first)
ranked_points: dict          # player_id -> points awarded
ranked_commentary: dict      # player_id -> LLM commentary
```

---

## Visual Styles

### Image Style Themes (20 options)
16-bit pixel art, 8-bit NES, claymation, vaporwave, comic book, anime, dark souls, borderlands, synthwave, Studio Ghibli, low-poly 3D, tarot card, ukiyo-e, cyberpunk 2077, Tim Burton, Mad Max, stained glass, Rick and Morty, medieval manuscript, noir

### Video Style Themes (10 options)
Epic fantasy awards ceremony, Cyberpunk neon awards show, Retro 80s game show, Underwater atlantis celebration, Space station victory ceremony, Ancient colosseum triumph, Haunted victorian mansion celebration, Jungle temple discovery, Steampunk airship deck, Anime tournament finals

### Character Generation
Random visual elements combined:
- Look: cute, fierce, nerdy, punk, goth, hipster, gamer, cyberpunk
- Moment: laughing, fighting, drinking, eating, sleeping, dancing, singing, playing with animals
- Style: cyberpunk, noir, anime, vaporwave, pixel art, low poly, retro, 1960s space art, steampunk, lego movie

---

## Deployment

**Build & Deploy:**
```bash
cd frontend && npm run build && cd ..
uv run modal deploy backend/app.py
```

**Cache Busting:** Vite generates hashed filenames. Force browser refresh with `Cmd+Shift+R` after deploys.

**Environment:** The app uses Modal environment `ai-game` (set via `os.environ["MODAL_ENVIRONMENT"] = "ai-game"` at top of `app.py`).

---

## Development Guidelines

- Generate code that is simple and readable, avoid unnecessary abstractions
- Avoid overly defensive coding - let errors surface so they can be fixed
- Use `uv` for Python dependency management (`uv run script.py`)
- Use modern Python 3.12+ typing (`dict`, `list`, `a | None`)
