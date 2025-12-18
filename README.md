# the-ai-game

A multiplayer survival party game where players respond to AI-generated deadly scenarios. Inspired by [Death By AI](https://deathbyai.gg/)

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