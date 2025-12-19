# SurvAIve

A multiplayer survival party game where players respond to AI-generated deadly scenarios. An AI judge evaluates your survival strategies and decides who lives or dies. Inspired by [Death By AI](https://deathbyai.gg/).

## How to Play

### For the Host

1. **Start a New Game** - One person creates a new game and receives a 4-character game code
2. **Share the Code** - Give the code to your friends so they can join
3. **Wait in the Lobby** - See players join and optionally create their characters
4. **Start the Game** - Only the host can press "Start Game" when everyone is ready
5. **Control the Pace** - The host advances between rounds after viewing results

### For Players

1. **Join the Game** - Enter the game code shared by the host and pick a name
2. **Create Your Character** (optional) - Customize your survivor with traits and get an AI-generated avatar
3. **Wait for Host** - Hang out in the lobby until the host starts the game
4. **Survive!** - Each round, read the deadly scenario and submit your survival strategy
5. **See Your Fate** - The AI judge decides if your strategy was clever enough to survive

### Game Flow

Each round follows this pattern:
1. **Scenario** - A deadly situation is presented 
2. **Strategy** - All players submit their survival strategies (60 second timer)
3. **Judgement** - The AI evaluates each strategy and determines outcomes
4. **Results** - See who survived, who died, and why

The player with the highest score after all rounds wins!

---

## Configuration

| File | Purpose |
|------|---------|
| `config.yaml` | Game settings, LLM/image models, timeouts, scoring |
| `backend/prompts.py` | All LLM prompts with `{{variable}}` placeholders |

### Editing Prompts

All LLM prompts are in `backend/prompts.py`. To modify how the AI judges strategies, generates scenarios, etc., edit the prompt templates there:

```python
import prompts

# Example: format a prompt with variables
prompt = prompts.format_prompt(
    prompts.STRATEGY_JUDGEMENT,
    scenario="A monster attacks...",
    strategy="I fight back!"
)
```

## Development

### Debug Menu

Press **`Ctrl+Shift+.`** or **`Cmd+Shift+.`** to open the debug menu. This lets you skip to any game state, round type, or phase for testing without playing through the whole game.