# Project: Death by AI

A multiplayer survival party game where players respond to AI-generated deadly scenarios. An AI judge evaluates survival strategies and determines who lives or dies. Features AI-generated scenario images and death scenes.

**Tech Stack:** React 19 frontend + FastAPI backend + Modal serverless deployment + OpenRouter LLM (Kimi K2) + FAL AI image generation

---

## Game Flow & Screens

### 1. Welcome Screen (`Lobby.jsx` - menu mode)
- Two options: "NEW GAME" or "JOIN GAME"
- New Game: Creates game with unique 4-character code, creator becomes admin (Cmd+Enter shortcut)
- Join Game: Enter game code + player name

### 2. Game Lobby (`App.jsx` - status: 'lobby')
- Displays all connected players
- Admin sees "START GAME" button
- Non-admins see "Waiting for {hostName} to start the game..."
- First player to join is automatically admin

### 3. Scenario View (`ScenarioView.jsx` - round status: 'scenario')
- Displays AI-generated deadly scenario
- Shows AI-generated scenario image
- Dead players see "WITNESS THE CARNAGE" spectator message

### 4. Strategy Input (`InputView.jsx` - round status: 'strategy')
- Textarea for survival strategy submission
- Keyboard shortcut: Cmd/Ctrl + Enter to submit
- Shows "TRANSMITTING..." during submission
- After submission: "STRATEGY UPLOADED. AWAITING JUDGEMENT."

### 5. Judgement State (`App.jsx` - round status: 'judgement')
- "JUDGING..." with glitch text animation
- AI evaluates all strategies in parallel
- Generates result images in parallel

### 6. Results View (`ResultsView.jsx` - round status: 'results')
- "JUDGEMENT DAY" title with glitch effect
- Player cards showing: name, strategy, death reason (if dead), points earned
- Leaderboard showing current standings
- Admin sees "NEXT ROUND" or "END GAME" button

### 7. Game Over (`App.jsx` - status: 'finished')
- Winner announcement with gold styling
- Final standings leaderboard
- "PLAY AGAIN" button

---

## Round Types

### Survival Mode (default)
- AI generates deadly scenario
- Players submit survival strategies
- AI judges each strategy and determines survival

### Blind Architect Mode
- Players design deadly scenarios for opponents
- Visual voting on trap images (no text shown)
- Winner's trap becomes the scenario
- Trap creator gets +500 bonus points

### Cooperative Mode
- Team-based survival round
- Players vote on best strategy
- Random +200/-200 point swings add chaos

---

## Game Mechanics

### Scoring
- **+100 points**: Survive a round
- **+500 points**: Win trap voting (Blind Architect mode)
- **+200/-200 points**: Random bonus/penalty (Cooperative mode)
- Winner: Highest score after all rounds

### Round Configuration
Rounds are configured via `round_config` array in GameState:
```python
round_config: List[str] = ["survival", "survival", "cooperative", "survival", "blind_architect"]
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
- Players "resurrected" between rounds (death is per-round, not permanent)

---

## Technical Architecture

### Frontend (`frontend/src/`)

| File | Purpose |
|------|---------|
| `App.jsx` | Main component, game state management, 2-second polling |
| `api.js` | API client (createGame, joinGame, getGameState, etc.) |
| `Lobby.jsx` | Welcome screen, create/join game |
| `ScenarioView.jsx` | Display scenario text + image |
| `InputView.jsx` | Strategy submission form |
| `TrapView.jsx` | Blind Architect trap creation |
| `VotingView.jsx` | Trap voting grid |
| `CoopVotingView.jsx` | Cooperative mode strategy voting |
| `ResultsView.jsx` | Round results display + leaderboard |
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
- **LLM**: OpenRouter API with Kimi K2 model (`moonshotai/kimi-k2-0905`)
- **Images**: FAL AI flux/krea model

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

**Cooperative Flow:**
```
strategy → coop_voting → coop_judgement → results
```

### Modal Serverless Architecture

**Secrets:** Stored in Modal's secret storage:
```bash
modal secret create ai-game-secrets MOONSHOT_API_KEY=xxx FAL_KEY=xxx --env ai-game
```

**Persistent Storage:** Uses `modal.Dict` for game state:
```python
games = modal.Dict.from_name("death-by-ai-games", create_if_missing=True)
```

**Async Functions:** Modal functions can be spawned with `.spawn()` for fire-and-forget execution.

### LLM Integration Notes

**JSON Response Handling:** OpenRouter models don't reliably support `response_format`. Instead:
1. Prompt explicitly requests JSON-only output
2. Response is parsed with regex to extract JSON from markdown code blocks
3. Fallback JSON is returned on any error

**Error Recovery:** If judgement fails for a player, they default to "dead" with a generic message so the game can continue.

---

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

---

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/create_game` | POST | Create new game, returns 4-char code |
| `/api/join_game?code={code}` | POST | Join game with `{ name }` body |
| `/api/get_game_state?code={code}&player_id={id}` | GET | Poll current state |
| `/api/start_game?code={code}` | POST | Admin starts game |
| `/api/submit_strategy?code={code}` | POST | Submit strategy `{ player_id, strategy }` |
| `/api/submit_trap?code={code}` | POST | Submit trap `{ player_id, trap_text }` |
| `/api/vote_trap?code={code}` | POST | Vote for trap `{ voter_id, target_id }` |
| `/api/vote_coop?code={code}` | POST | Vote in coop mode `{ voter_id, target_id }` |
| `/api/next_round?code={code}` | POST | Admin advances round |

---

## Data Models

### GameState
```python
id: str                    # UUID
code: str                  # 4-char join code
status: str                # "lobby" | "playing" | "finished"
players: dict              # player_id -> Player
rounds: list               # List of Round objects
current_round_idx: int
max_rounds: int            # Default: 5
round_config: list[str]    # Round types: ["survival", "survival", "cooperative", "survival", "blind_architect"]
```

### Player
```python
id: str              # UUID
name: str
score: int           # Accumulated points
is_admin: bool       # First joiner
is_alive: bool       # Current round status
death_reason: str    # From AI judge (if dead)
strategy: str        # Current round submission
result_image_url: str
last_active: float   # Heartbeat timestamp
```

### Round
```python
number: int          # 1-5
type: str            # "survival" | "blind_architect" | "cooperative"
status: str          # "scenario" | "strategy" | "judgement" | "results" | "trap_creation" | "trap_voting" | "coop_voting" | "coop_judgement"
scenario_text: str
scenario_image_url: str

# Blind Architect specific
architect_id: str
trap_proposals: dict
trap_images: dict
votes: dict

# Cooperative specific
strategy_images: dict
coop_votes: dict
coop_vote_points: dict
coop_team_winner_id: str
coop_team_loser_id: str
coop_winning_strategy_id: str
coop_team_survived: bool
```

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
