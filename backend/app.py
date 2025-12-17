import os

# Enforce the 'ai-game' environment
os.environ["MODAL_ENVIRONMENT"] = "ai-game"

import modal
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
import time
import uuid
import random

# --- Video Style Themes ---
# Each game ending randomly selects one theme for all player videos
VIDEO_STYLE_THEMES = [
    "epic fantasy awards ceremony, golden throne room, medieval banners, torchlight",
    "cyberpunk neon awards show, holographic displays, chrome stage, rain-slicked city",
    "retro 80s game show, pixel confetti, arcade cabinet aesthetic, synthwave colors",
    "underwater atlantis celebration, bioluminescent lights, coral palace, bubbles rising",
    "space station victory ceremony, zero gravity confetti, stars visible through windows",
    "ancient colosseum triumph, roman columns, laurel wreaths, dramatic sunset",
    "haunted victorian mansion celebration, gothic chandeliers, spooky elegance",
    "jungle temple discovery, aztec gold, torch-lit ruins, exotic birds",
    "steampunk airship deck, brass gears, clouds below, goggles and top hats",
    "anime tournament finals, dramatic speed lines, cherry blossoms, epic poses",
]


# --- Image Style Themes ---
# Each round randomly selects one theme for visual consistency
IMAGE_STYLE_THEMES = [
    "16-bit pixel art, retro video game aesthetic, vibrant pixel colors",
    "8-bit NES style, chunky pixels, limited color palette, nostalgic gaming",
    "claymation stop-motion style, plasticine textures, handcrafted look",
    "vaporwave aesthetic, pink and cyan, greek statues, 80s nostalgia, glitch effects",
    "comic book style, bold ink outlines, halftone dots, POW BAM action panels",
    "anime style, dramatic speed lines, expressive eyes, vibrant colors",
    "dark souls aesthetic, gothic fantasy, ominous lighting, oppressive atmosphere",
    "borderlands style, cel-shaded, heavy black outlines, gritty comic look",
    "synthwave neon, 80s retrowave, grid landscapes, chrome and pink",
    "Studio Ghibli style, soft watercolors, whimsical, detailed backgrounds",
    "low-poly 3D, geometric facets, vibrant flat colors, PS1 aesthetic",
    "tarot card style, ornate borders, mystical symbolism, art nouveau",
    "ukiyo-e japanese woodblock print, bold outlines, flat colors, waves",
    "cyberpunk 2077 style, neon signs, rain-slicked streets, chrome implants",
    "tim burton style, gothic whimsy, spirals, pale characters, dark humor",
    "mad max fury road, desert apocalypse, rust and chrome, war rigs",
    "stained glass window, luminous colors, black leading, religious imagery",
    "rick and morty style, wobbly lines, interdimensional chaos, bright colors",
    "medieval manuscript illumination, gold leaf, ornate borders, flat perspective",
    "noir detective style, black and white, dramatic shadows, venetian blinds",
]

# --- Random Character Generation Traits ---
# Aligned with the 5 character fields: look, weapon, talent, flaw, catchphrase

RANDOM_LOOKS = [
    "wild purple hair, leather jacket, mysterious scar across eye",
    "suspiciously normal accountant vibes, but with glowing red eyes",
    "sentient pile of moss wearing a tiny top hat",
    "buff grandma energy, knitting needles tucked behind ear",
    "goth pixie with too many piercings to count",
    "floating head with a magnificent mustache",
    "skeleton in a business casual polo shirt",
    "three raccoons in a trenchcoat (poorly disguised)",
    "cyberpunk vampire with RGB fangs",
    "sleepy wizard who hasn't slept since the 1400s",
    "aggressively cheerful clown (not evil, just intense)",
    "sentient vending machine with trust issues",
    "discount store superhero with a bedsheet cape",
    "Victorian ghost who refuses to update their wardrobe",
    "extremely buff corgi standing on hind legs",
    "eldritch horror trying to blend in at a coffee shop",
    "time-displaced knight confused by everything",
    "wholesome orc grandmother with reading glasses",
    "conspiracy theorist with tinfoil fashion sense",
    "robot learning human emotions (badly)",
    "mushroom person who is always slightly damp",
    "ex-villain trying to rebrand as an influencer",
    "wizard who got their degree online",
    "goblin CEO in an ill-fitting suit",
    "ghost of someone who died from embarrassment",
    "anime protagonist refusing to acknowledge they're a side character",
    "interdimensional tourist with too many cameras",
    "retired god working retail",
    "cat that learned to walk upright and won't stop judging",
    "person who is clearly two kids stacked in adult clothes",
]

RANDOM_WEAPONS = [
    "rusty machete held together by duct tape and prayers",
    "flaming guitar that only plays one chord",
    "weaponized pocket sand (premium grade)",
    "a very strongly worded lawsuit",
    "grandma's cursed rolling pin",
    "emotional damage (words hurt)",
    "a really mean goose on a leash",
    "passive-aggressive sticky notes",
    "haunted IKEA furniture",
    "a briefcase full of angry bees",
    "a strongly worded letter to the manager",
    "a spoon that has seen unspeakable things",
    "the power of friendship (and also a knife)",
    "a gun that shoots smaller guns",
    "weaponized dad jokes",
    "a boomerang that never comes back",
    "an umbrella with a dark secret",
    "the aux cord (psychological warfare)",
    "a fish. just a regular fish.",
    "a sword that screams when swung",
    "a shopping cart with one bad wheel",
    "the element of surprise (and a brick)",
    "forbidden knowledge from cursed Wikipedia",
    "a comically oversized foam finger",
    "the crushing weight of student debt",
    "a rubber chicken with a pulley in the middle",
    "an alarm clock that causes existential dread",
    "a cookbook for recipes that shouldn't exist",
    "a spray bottle labeled 'NO'",
    "unearned confidence (surprisingly effective)",
]

RANDOM_TALENTS = [
    "can talk to animals (they're mostly rude)",
    "expert at locking picks, not lockpicking",
    "hasn't slept since 2019 and it shows",
    "can sense when someone is about to say something stupid",
    "fluent in sarcasm and one dead language",
    "can befriend any cat within a 50-foot radius",
    "perfect pitch but only for screaming",
    "predicts weather through joint pain alone",
    "remembers every embarrassing thing ever",
    "can cook anything into something barely edible",
    "expert at leaving without saying goodbye",
    "can fall asleep anywhere, anytime, instantly",
    "knows exactly when the pizza will arrive",
    "trips over nothing on flat surfaces",
    "absorbs random trivia like a cursed sponge",
    "can parallel park on the first try (suspicious)",
    "always finds the best parking spots",
    "can tell if milk is expired from 10 feet away",
    "wins every staring contest with objects",
    "can make any situation awkward in seconds",
    "knows exactly when the microwave hits 0:01",
    "can untangle any cable (takes 4 hours)",
    "always picks the slowest checkout line",
    "hears chip eating from three rooms away",
    "finds four-leaf clovers constantly, still unlucky",
    "assembles IKEA furniture without instructions",
    "has never lost rock-paper-scissors",
    "can taste the color blue",
    "knows the exact moment toast will burn",
    "makes any plant survive except cacti",
]

RANDOM_FLAWS = [
    "trusts everyone, including the obvious villains",
    "allergic to cardio in all forms",
    "speaks at exactly the wrong volume always",
    "cannot resist pressing suspicious buttons",
    "pathologically honest at the worst times",
    "falls in love after one nice gesture",
    "monologues at critical moments",
    "terrible at names, too deep to ask now",
    "cannot whisper, only stage whisper",
    "has trust issues specifically with doors",
    "dramatically faints when startled",
    "cannot tell a lie but tries anyway",
    "befriends the villain every single time",
    "will pet any animal, especially dangerous ones",
    "cannot resist a dare, no matter how stupid",
    "gets distracted by shiny objects mid-combat",
    "overshares trauma at inappropriate times",
    "always roots for the underdog, even bad ones",
    "cannot resist saying 'I told you so'",
    "chronically early, including to ambushes",
    "sacrifices dramatically even when unnecessary",
    "makes puns during serious moments",
    "has never read instructions for anything",
    "will fight god if mildly inconvenienced",
    "constantly betrayed by their own hubris",
    "emotionally attached to inanimate objects",
    "cannot keep a secret for 10 minutes",
    "always picks the cursed artifact",
    "says 'well actually' during combat",
    "will die for the bit",
]

RANDOM_CATCHPHRASES = [
    "I've seen worse... probably",
    "Hold my drink and watch this disaster",
    "Not again... (it's always again)",
    "That's a problem for future me",
    "I didn't sign up for this (they did)",
    "This is fine. Everything is fine.",
    "In my defense, I was unsupervised",
    "I'm not here to make friends (makes friends immediately)",
    "Well, that's certainly... a choice",
    "Bold of you to assume I have a plan",
    "I've made a severe lapse in judgment",
    "Surprise! It's trauma!",
    "Let's make bad decisions together",
    "I came here to have a good time and honestly...",
    "Watch me do something mildly impressive",
    "According to my calculations... we're doomed",
    "I'm not superstitious, but a little stitious",
    "Life gave me lemons. I threw them back.",
    "I didn't come here to be reasonable",
    "Trust me, I'm a professional (unclear at what)",
    "This isn't even my final form (it is)",
    "I have three plans. They're all bad.",
    "It worked in my head",
    "I'll explain later (never explains)",
    "Remember me as a hero (please)",
    "Living proof anything is possible (unfortunately)",
    "Today's main character: me (derogatory)",
    "I've done more with fewer braincells",
    "Fate chose violence. So did I.",
    "My last words: 'I can make that jump'",
]

RANDOM_ART_STYLES = [
    "vibrant anime style with dramatic lighting",
    "pixelated 16-bit retro game aesthetic",
    "painterly Studio Ghibli watercolors",
    "bold comic book with heavy ink outlines",
    "neon cyberpunk with glitch effects",
    "dark fantasy gothic illustration",
    "cute chibi kawaii style",
    "gritty borderlands cel-shading",
    "vaporwave aesthetic with pink and cyan",
    "claymation stop-motion texture",
    "synthwave retrowave neon glow",
    "tim burton gothic whimsy",
    "low-poly PS1 aesthetic",
    "rick and morty wobbly cartoon",
    "tarot card mystical art nouveau",
    "noir detective dramatic shadows",
]


def generate_random_character_traits(seed: int = None) -> dict:
    """Generate random character traits matching the 5 character fields."""
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    traits = {
        "look": rng.choice(RANDOM_LOOKS),
        "weapon": rng.choice(RANDOM_WEAPONS),
        "talent": rng.choice(RANDOM_TALENTS),
        "flaw": rng.choice(RANDOM_FLAWS),
        "catchphrase": rng.choice(RANDOM_CATCHPHRASES),
    }
    return traits


def build_character_prompt_from_traits(traits: dict) -> str:
    """Build a character image prompt from the 5 traits."""
    art_style = random.choice(RANDOM_ART_STYLES)
    prompt = f"""Game character portrait: {traits['look']}, wielding {traits['weapon']}. Art style: {art_style}."""
    return prompt


def apply_style_theme(prompt: str, style_theme: str | None) -> str:
    """Append the round's style theme to an image prompt for visual consistency."""
    if style_theme:
        return f"{prompt}, in the style of {style_theme}"
    return prompt


def calculate_ranked_points(num_players: int, rank: int) -> int:
    """Award points by rank position in ranked rounds."""
    if num_players == 2:
        return 200 if rank == 1 else 50
    elif num_players == 3:
        return [250, 125, 25][rank - 1]
    else:  # 4+ players
        points_map = {1: 300, 2: 200, 3: 100, 4: 50}
        return points_map.get(rank, 25)


# --- Image & Model Definitions ---
image = modal.Image.debian_slim().pip_install(
    "pydantic",
    "shortuuid",
    "requests",
    "openai",
    "fastapi[standard]",
    "httpx",  # For async HTTP requests
    "pyyaml"  # For config loading
).add_local_dir("frontend/dist", remote_path="/assets"
).add_local_file("config.yaml", remote_path="/config.yaml")

app = modal.App("mas-ai", image=image)


# =============================================================================
# CONFIG LOADING
# =============================================================================

def load_config():
    """Load configuration from config.yaml file."""
    import yaml
    config_path = "/config.yaml"
    # Fallback for local development
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    if not os.path.exists(config_path):
        config_path = "config.yaml"

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Load config at module level for easy access
CONFIG = load_config()

# Helper functions to access config values
def get_model(use_case: str) -> str:
    """Get the LLM model for a specific use case."""
    return CONFIG["models"].get(use_case, CONFIG["models"]["strategy_judgement"])


def get_image_model(use_case: str) -> str:
    """Get the image model for a specific use case."""
    return CONFIG["image_models"].get(use_case, CONFIG["image_models"]["result_image"])


def get_image_url(use_case: str) -> str:
    """Get the full FAL URL for an image model use case."""
    base_url = CONFIG["image_generation"]["fal_base_url"]
    model = get_image_model(use_case)
    return f"{base_url}/{model}"


def get_video_model_url() -> str:
    """Get the full FAL queue URL for video generation."""
    base_url = CONFIG["image_generation"]["fal_queue_url"]
    model = CONFIG["video_generation"]["model"]
    return f"{base_url}/{model}"

# --- Clients ---
def get_llm_client():
    import openai
    return openai.OpenAI(
        base_url=CONFIG["llm"]["base_url"],
        api_key=os.environ["MOONSHOT_API_KEY"],
    )

def generate_scenario_llm(round_num: int, max_rounds: int = 5):
    """Generate a scenario with Corrupted Simulation narrative framing."""
    client = get_llm_client()

    # Narrative phase based on progression
    if round_num == 1:
        phase = "initialization sequence"
        corruption = "minor data artifacts"
        narrative_hint = "The simulation is just booting up, things seem almost normal but slightly off."
    elif round_num == 2:
        phase = "calibration protocol"
        corruption = "increasing instability"
        narrative_hint = "The system is trying to calibrate but errors are creeping in."
    elif round_num == max_rounds:
        phase = "exit protocol - final level"
        corruption = "critical system failure, reality breaking down"
        narrative_hint = "This is the final test before escape. Everything is falling apart."
    else:
        phase = "corrupted memory sector"
        corruption = "severe fragmentation"
        narrative_hint = "Deep in corrupted data, reality is unreliable."

    prompt = f"""Generate a deadly survival scenario for a party game. Level {round_num} of {max_rounds}.

Create a SHORT scenario (2-3 sentences) with:
1. A CLEAR THREAT the player must deal with (monster, trap, disaster, enemy, etc.)
2. A SPECIFIC SETTING (jungle temple, space station, haunted mansion, medieval dungeon, etc.)
3. ONE subtle "wrongness" that hints something is off (wrong colors, impossible geometry, repeating patterns)

The scenario must give players something ACTIONABLE to respond to - they should be able to:
- Fight or flee from something
- Solve a puzzle or disarm a trap
- Talk/negotiate their way out
- Use an object or tool creatively
- Make a clever observation or joke

GOOD examples (clear threats, actionable):
- "You're in a flooding submarine. Water pours through a crack in the hull. The emergency hatch is jammed, and something large just bumped the hull from outside."
- "A masked killer blocks the cabin door, machete raised. The window behind you is small but breakable. The killer tilts their head the same way every 3 seconds, like a broken animatronic."
- "You wake up strapped to a table in a mad scientist's lab. A laser is slowly moving toward you. The scientist is monologuing but keeps repeating the same sentence."

BAD examples (too vague, no clear action):
- "You're in a forest and shadows are purple and you're holding random objects" (no clear threat)
- "Reality feels wrong and things keep shifting" (nothing to do)

Write in second person ("You are...", "You find yourself...")

Generate ONLY the scenario, nothing else:"""

    try:
        print(f"SCENARIO GEN: Calling LLM for round {round_num}...", flush=True)
        completion = client.chat.completions.create(
            model=get_model("scenario_generation"),
            messages=[{"role": "user", "content": prompt}],
        )
        result = completion.choices[0].message.content.strip()
        print(f"SCENARIO GEN: Success - {result[:50]}...", flush=True)
        return result
    except Exception as e:
        import traceback
        print(f"SCENARIO GEN Error: {type(e).__name__}: {e}", flush=True)
        print(f"SCENARIO GEN Traceback: {traceback.format_exc()}", flush=True)
        return "ERROR: SCENARIO DATA CORRUPTED. You are suspended in static. Something moves in the noise."


async def generate_last_stand_scenario_async():
    """Generate the EVIL SANTA final boss scenario."""
    import httpx

    prompt = """Generate a deadly survival scenario featuring an EVIL ANIME SANTA as the final boss.

Create a SHORT scenario (2-3 sentences) with:
1. EVIL SANTA as the main threat - he's cartoonishly villainous, anime-inspired, over-the-top evil
2. Setting: His twisted workshop/lair (corrupted North Pole, nightmare factory, etc.)
3. He should be doing something menacing but absurdly dramatic (cackling, monologuing, etc.)

Evil Santa personality traits to include:
- Speaks in third person ("SANTA SEES ALL!")
- Makes twisted holiday puns ("You've been VERY naughty...")
- Has anime villain energy (dramatic poses, glowing eyes, maniacal laughter)
- His elves are now demonic minions
- His bag contains weapons/traps instead of presents

GOOD examples:
- "Evil Santa's eyes glow crimson as he rises from his throne of frozen skulls. 'HO HO HO! Santa knows when you've been SLEEPING!' He hurls razor-sharp candy canes while his demon elves cackle."
- "You stand in Santa's nightmare workshop. Conveyor belts carry screaming gingerbread men into furnaces. Evil Santa adjusts his blood-red hat and grins. 'COAL? No no no... Santa has something SPECIAL for naughty children.'"

Write in second person ("You are...", "You find yourself...")

Generate ONLY the scenario, nothing else:"""

    try:
        print(f"LAST STAND SCENARIO: Generating Evil Santa scenario...", flush=True)
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("scenario_generation"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
        print(f"LAST STAND SCENARIO: Success - {result[:50]}...", flush=True)
        return result
    except Exception as e:
        import traceback
        print(f"LAST STAND SCENARIO Error: {type(e).__name__}: {e}", flush=True)
        print(f"LAST STAND SCENARIO Traceback: {traceback.format_exc()}", flush=True)
        return "Evil Santa's eyes glow crimson in his nightmare workshop. 'HO HO HO! SANTA SEES YOU WHEN YOU'RE SLEEPING!' Demon elves surround you as he loads razor-sharp candy canes into a massive cannon."


async def generate_scenario_llm_async(round_num: int, max_rounds: int = 5):
    """Async version of generate_scenario_llm for parallel pre-warming."""
    import httpx

    # Narrative phase based on progression
    if round_num == 1:
        phase = "initialization sequence"
        corruption = "minor data artifacts"
        narrative_hint = "The simulation is just booting up, things seem almost normal but slightly off."
    elif round_num == 2:
        phase = "calibration protocol"
        corruption = "increasing instability"
        narrative_hint = "The system is trying to calibrate but errors are creeping in."
    elif round_num == max_rounds:
        phase = "exit protocol - final level"
        corruption = "critical system failure, reality breaking down"
        narrative_hint = "This is the final test before escape. Everything is falling apart."
    else:
        phase = "corrupted memory sector"
        corruption = "severe fragmentation"
        narrative_hint = "Deep in corrupted data, reality is unreliable."

    prompt = f"""Generate a deadly survival scenario for a party game. Level {round_num} of {max_rounds}.

Create a SHORT scenario (2-3 sentences) with:
1. A CLEAR THREAT the player must deal with (monster, trap, disaster, enemy, etc.)
2. A SPECIFIC SETTING (jungle temple, space station, haunted mansion, medieval dungeon, etc.)
3. ONE subtle "wrongness" that hints something is off (wrong colors, impossible geometry, repeating patterns)

The scenario must give players something ACTIONABLE to respond to - they should be able to:
- Fight or flee from something
- Solve a puzzle or disarm a trap
- Talk/negotiate their way out
- Use an object or tool creatively
- Make a clever observation or joke

GOOD examples (clear threats, actionable):
- "You're in a flooding submarine. Water pours through a crack in the hull. The emergency hatch is jammed, and something large just bumped the hull from outside."
- "A masked killer blocks the cabin door, machete raised. The window behind you is small but breakable. The killer tilts their head the same way every 3 seconds, like a broken animatronic."
- "You wake up strapped to a table in a mad scientist's lab. A laser is slowly moving toward you. The scientist is monologuing but keeps repeating the same sentence."

BAD examples (too vague, no clear action):
- "You're in a forest and shadows are purple and you're holding random objects" (no clear threat)
- "Reality feels wrong and things keep shifting" (nothing to do)

Write in second person ("You are...", "You find yourself...")

Generate ONLY the scenario, nothing else:"""

    try:
        print(f"SCENARIO GEN ASYNC: Calling LLM for round {round_num}...", flush=True)
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("scenario_generation"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
        print(f"SCENARIO GEN ASYNC: Success round {round_num} - {result[:50]}...", flush=True)
        return result
    except Exception as e:
        import traceback
        print(f"SCENARIO GEN ASYNC Error round {round_num}: {type(e).__name__}: {e}", flush=True)
        print(f"SCENARIO GEN ASYNC Traceback: {traceback.format_exc()}", flush=True)
        return "ERROR: SCENARIO DATA CORRUPTED. You are suspended in static. Something moves in the noise."


async def judge_strategy_llm_async(scenario: str, strategy: str):
    """Async version of judge_strategy_llm for parallel execution with simulation flavor."""
    import re
    import httpx

    prompt = f"""Judge if this survival strategy works. Be harsh but fair.

SCENARIO: {scenario}

STRATEGY: {strategy}

Rules:
- Clever, creative, or funny strategies SURVIVE
- Generic, lazy, or nonsensical strategies DIE
- Must actually address the threat

IMPORTANT - Keep "reason" SHORT (1-2 sentences, under 30 words). Focus on what happened, not glitchy/meta stuff. Can be darkly funny.

Good reasons: "The shark wasn't impressed by diplomacy." / "Your torch scared them off long enough to escape."
Bad reasons: "Your data fragmented across corrupted memory sectors as the simulation..." (too long/meta)

JSON only, no markdown:
{{"survived": true/false, "reason": "1-2 sentences max", "visual_prompt": "scene for image"}}"""
    try:
        print(f"LLM Judge: Calling API for strategy: {strategy[:50]}...", flush=True)
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("strategy_judgement"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

        print(f"LLM Judge: Raw response: {content[:200]}...", flush=True)

        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)

        # Also try to find JSON object directly
        json_obj_match = re.search(r'\{[\s\S]*\}', content)
        if json_obj_match:
            content = json_obj_match.group(0)

        return content.strip()
    except Exception as e:
        print(f"LLM Judge Error: {e}", flush=True)
        return '{"survived": false, "reason": "SYSTEM ERROR: User data corrupted during evaluation. Terminating process.", "visual_prompt": "A figure dissolving into static and digital noise, fragments of code visible in the air"}'


async def rank_all_strategies_llm_async(scenario: str, strategies: list[dict]) -> str:
    """Rank all strategies comparatively for ranked rounds."""
    import re
    import httpx
    import json
    import random

    # Build strategies list for prompt
    strategy_list = "\n".join([
        f"PLAYER {i+1} ({s['name']}): {s['strategy']}"
        for i, s in enumerate(strategies)
    ])

    prompt = f"""You are judging a survival game. Given a deadly scenario, rank all player strategies from BEST to WORST.

SCENARIO: {scenario}

PLAYER STRATEGIES:
{strategy_list}

RANKING CRITERIA (in order of importance):
1. CREATIVITY - Original, unexpected approaches beat generic solutions
2. EFFECTIVENESS - Would this actually work in the scenario?
3. ENTERTAINMENT VALUE - Funny, dramatic, or memorable strategies rank higher
4. SPECIFICITY - Detailed plans beat vague "I run away" responses

IMPORTANT RULES:
- Everyone survives this round (it's about WHO survives BEST)
- Rank from 1 (best) to {len(strategies)} (worst)
- No ties allowed - you must pick a winner
- Give each player 1-2 sentences of commentary explaining their rank
- Generate a visual_prompt for each player showing their moment of glory/mediocrity

Return ONLY valid JSON in this exact format:
{{
    "rankings": [
        {{"player_id": "id1", "rank": 1, "commentary": "Brilliant use of...", "visual_prompt": "A hero triumphantly..."}},
        {{"player_id": "id2", "rank": 2, "commentary": "Solid approach but...", "visual_prompt": "A person competently..."}}
    ]
}}"""

    try:
        print(f"RANKED JUDGE: Calling LLM for {len(strategies)} strategies...", flush=True)
        timeout = CONFIG["llm"]["extended_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("ranked_judgement"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            print(f"RANKED JUDGE: Raw response: {content[:300]}...", flush=True)

            # Extract JSON from potential markdown code blocks
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json_match.group(0)
            return content.strip()
    except Exception as e:
        print(f"RANKED JUDGE Error: {e}", flush=True)
        # Return fallback with random ordering
        shuffled = list(strategies)
        random.shuffle(shuffled)
        return json.dumps({
            "rankings": [
                {"player_id": s["player_id"], "rank": i+1,
                 "commentary": "The AI judge malfunctioned...",
                 "visual_prompt": "A confused figure in digital static"}
                for i, s in enumerate(shuffled)
            ]
        })


async def generate_image_fal_async(prompt: str, use_case: str = "result_image"):
    """Async version of generate_image_fal for parallel execution."""
    import httpx

    url = get_image_url(use_case)
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "image_size": CONFIG["image_generation"]["default_image_size"],
        "num_inference_steps": CONFIG["image_generation"]["num_inference_steps"]
    }
    try:
        timeout = CONFIG["image_generation"]["timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["images"][0]["url"]
    except Exception as e:
        print(f"FAL Error: {e}", flush=True)
        return None


async def generate_character_image_async(character_prompt: str, style_theme: str | None = None):
    """Generate a character avatar image based on the player's description with game style."""
    import httpx

    # Pick a random style theme if not provided
    if not style_theme:
        style_theme = random.choice(IMAGE_STYLE_THEMES)


    # randomly select a look from a list of looks for a game character:
    looks = [
        "cute",
        "fierce",
        "nerdy",
        "punk",
        "goth",
        "hipster",
        "gamer",
        "cyberpunk",

    ]
    random_look = random.choice(looks)

    moments = [
        "laughing",
        "fighting with squirrels",
        "drinking beer",
        "eating a sandwich",
        "sleeping",
        "dancing",
        "singing",
        "playing with a cat",
        "playing with a dog",
    ]
    random_moment = random.choice(moments)

    character_styles = [
        "cyberpunk",
        "lego movie"
        "noir",
        "anime",
        "vaporwave",
        "pixel art",
        "low poly",
        "retro",
        "1960's space art",
        "steampunk",
    ]
    random_character_style = random.choice(character_styles)

    # Build a rich prompt that shows the character in an action scene with all their traits
    full_character_prompt = f"""Game character looking {random_look} in the style of {random_character_style}. The character's description is as follows:

{character_prompt}.

The character is mid {random_moment}, displaying their true personality and equipment.
Full scene is the style of {random_character_style}."""

    print(f"CHARACTER IMG: Generating with style: {style_theme[:40]}...", flush=True)
    print(f"CHARACTER IMG: Full prompt: {full_character_prompt[:100]}...", flush=True)

    url = get_image_url("character_image")
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": full_character_prompt,
        "image_size": "square",  # Square for avatars
        "num_inference_steps": CONFIG["image_generation"]["num_inference_steps"]
    }
    try:
        timeout = CONFIG["image_generation"]["timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["images"][0]["url"]
    except Exception as e:
        print(f"Character Image Error: {e}", flush=True)
        return None


# Keep sync versions for backwards compatibility
def judge_strategy_llm(scenario: str, strategy: str):
    """Sync version of judgement with simulation flavor."""
    import re
    client = get_llm_client()
    prompt = f"""Judge if this survival strategy works. Be harsh but fair.

SCENARIO: {scenario}

STRATEGY: {strategy}

Rules:
- Clever, creative, or funny strategies SURVIVE
- Generic, lazy, or nonsensical strategies DIE
- Must actually address the threat

IMPORTANT - Keep "reason" SHORT (1-2 sentences, under 30 words). Focus on what happened, not glitchy/meta stuff. Can be darkly funny.

Good reasons: "The shark wasn't impressed by diplomacy." / "Your torch scared them off long enough to escape."
Bad reasons: "Your data fragmented across corrupted memory sectors as the simulation..." (too long/meta)

JSON only, no markdown:
{{"survived": true/false, "reason": "1-2 sentences max", "visual_prompt": "scene for image"}}"""
    try:
        print(f"LLM Judge: Calling API for strategy: {strategy[:50]}...", flush=True)
        completion = client.chat.completions.create(
            model=get_model("strategy_judgement"),
            messages=[{"role": "user", "content": prompt}],
        )
        content = completion.choices[0].message.content
        print(f"LLM Judge: Raw response: {content[:200]}...", flush=True)

        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)

        # Also try to find JSON object directly
        json_obj_match = re.search(r'\{[\s\S]*\}', content)
        if json_obj_match:
            content = json_obj_match.group(0)

        return content.strip()
    except Exception as e:
        print(f"LLM Judge Error: {e}", flush=True)
        return '{"survived": false, "reason": "SYSTEM ERROR: User data corrupted during evaluation. Terminating process.", "visual_prompt": "A figure dissolving into static and digital noise, fragments of code visible in the air"}'


async def generate_video_prompt_llm_async(player_name: str, rank: int, total_players: int, score: int, video_theme: str):
    """Use a fast LLM to generate personalized video scene and dialogue with simulation narrative."""
    import httpx
    import json
    import re

    is_winner = rank == 1
    is_last = rank == total_players

    # Simulation-flavored context
    if is_winner:
        context = f"{player_name} has completed the EXIT PROTOCOL! They escaped the corrupted simulation with {score} data integrity points. Their consciousness has been successfully extracted."
        tone = "triumphant, epic, with subtle digital/simulation undertones"
    elif is_last:
        context = f"{player_name}'s data was nearly corrupted beyond recovery. They finished last with {score} points but their consciousness fragment was salvaged."
        tone = "consoling but humorous, gentle roasting, with simulation flavor"
    else:
        context = f"{player_name} achieved partial extraction, finishing in position {rank} out of {total_players} with {score} integrity points."
        tone = "acknowledging, mildly congratulatory, with digital undertones"

    prompt = f"""You are writing a very short video script for a game called "Mas AI".
The game's premise: Players were consciousness fragments trapped in a corrupted AI simulation.
They've now escaped (or been extracted) after surviving deadly levels.

The video theme/setting is: {video_theme}

Context: {context}

Generate a JSON response with:
1. "scene": A 1-sentence visual description of what's happening (must fit the theme: {video_theme})
2. "dialogue": A short spoken announcement (2-3 sentences max, must include the player's name "{player_name}")

The tone should be: {tone}
Include subtle references to escaping, data integrity, or consciousness extraction where appropriate.

Respond with ONLY valid JSON, no markdown:
{{"scene": "...", "dialogue": "..."}}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("video_script_generation"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group(0))
                print(f"VIDEO PROMPT LLM: Generated for {player_name}: {result}", flush=True)
                return result

    except Exception as e:
        print(f"VIDEO PROMPT LLM Error for {player_name}: {e}", flush=True)

    # Fallback with simulation flavor
    if is_winner:
        return {
            "scene": f"A figure emerges from a portal of light and code, reality stabilizing around them as they escape the simulation",
            "dialogue": f"EXIT PROTOCOL COMPLETE. {player_name}, your consciousness has been successfully extracted! You are the primary survivor of the corrupted simulation!"
        }
    elif is_last:
        return {
            "scene": f"A flickering, partially corrupted figure stumbles out of static, barely holding together",
            "dialogue": f"Data salvage complete. {player_name}, your consciousness fragment has been recovered... mostly. Some memories may be corrupted."
        }
    else:
        return {
            "scene": f"A figure materializes from digital noise, their form stabilizing as they emerge from the simulation",
            "dialogue": f"Extraction complete. {player_name}, you finished in position {rank}. Your data integrity held. Not optimal, but you survived."
        }


def generate_image_fal(prompt: str, use_case: str = "result_image"):
    import requests
    url = get_image_url(use_case)
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "image_size": CONFIG["image_generation"]["default_image_size"],
        "num_inference_steps": CONFIG["image_generation"]["num_inference_steps"]
    }
    try:
        timeout = CONFIG["image_generation"]["timeout_seconds"]
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()["images"][0]["url"]
    except Exception as e:
        print(f"FAL Error: {e}")
        return None


async def submit_video_request_async(player_name: str, image_url: str, scene: str, dialogue: str, video_theme: str, client: "httpx.AsyncClient"):
    """Submit a video generation request and return the request_id (don't wait for completion)."""
    submit_url = get_video_model_url()
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }

    # Create prompt with LLM-generated scene and dialogue, plus hardcoded theme
    prompt = f'{scene} An announcer says "{dialogue}" Setting: {video_theme}'
    duration = str(CONFIG["video_generation"]["duration_seconds"])

    payload = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": duration,
        "generate_audio": True,
        "negative_prompt": "blur, distort, low quality, static, boring"
    }

    try:
        print(f"VIDEO SUBMIT [{player_name}]: Submitting request...", flush=True)
        response = await client.post(submit_url, json=payload, headers=headers)
        response.raise_for_status()
        queue_data = response.json()
        request_id = queue_data.get("request_id")

        if request_id:
            print(f"VIDEO SUBMIT [{player_name}]: Got request_id: {request_id}", flush=True)
        else:
            print(f"VIDEO SUBMIT [{player_name}]: No request_id in response: {queue_data}", flush=True)

        return request_id
    except Exception as e:
        print(f"VIDEO SUBMIT Error [{player_name}]: {e}", flush=True)
        return None


async def poll_video_status_async(player_name: str, request_id: str, client: "httpx.AsyncClient"):
    """Poll for video completion given a request_id."""
    import asyncio

    if not request_id:
        return None

    video_model_url = get_video_model_url()
    status_url = f"{video_model_url}/requests/{request_id}/status"
    result_url = f"{video_model_url}/requests/{request_id}"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }

    poll_interval = CONFIG["video_generation"]["poll_interval_seconds"]
    max_wait = CONFIG["video_generation"]["max_wait_seconds"]
    max_attempts = int(max_wait / poll_interval)

    for attempt in range(max_attempts):
        await asyncio.sleep(poll_interval)

        try:
            status_response = await client.get(status_url, headers=headers)
            status_data = status_response.json()
            status = status_data.get("status")

            if attempt % 6 == 0:  # Log every 30 seconds
                print(f"VIDEO POLL [{player_name}]: Attempt {attempt+1}/{max_attempts}, status: {status}", flush=True)

            if status == "COMPLETED":
                result_response = await client.get(result_url, headers=headers)
                result_data = result_response.json()
                video_url = result_data.get("video", {}).get("url")
                print(f"VIDEO POLL [{player_name}]: Complete! URL: {video_url}", flush=True)
                return video_url
            elif status in ["FAILED", "CANCELLED"]:
                print(f"VIDEO POLL [{player_name}]: Failed with status: {status}", flush=True)
                return None
        except Exception as e:
            print(f"VIDEO POLL [{player_name}]: Error on attempt {attempt+1}: {e}", flush=True)
            # Continue polling on transient errors

    print(f"VIDEO POLL [{player_name}]: Timeout after max attempts", flush=True)
    return None


# --- State Models ---
class Player(BaseModel):
    id: str
    name: str
    score: int = 0
    is_admin: bool = False
    is_alive: bool = True
    in_lobby: bool = False  # Whether player has clicked "Enter Lobby" after avatar preview
    death_reason: Optional[str] = None
    survival_reason: Optional[str] = None  # How they survived
    strategy: Optional[str] = None  # Current round strategy
    result_image_url: Optional[str] = None # Image of death or glory
    judgement_pending: bool = False  # True when judgement is in progress for this player
    last_active: float = Field(default_factory=time.time) # Heartbeat
    # Character creation fields
    character_description: Optional[str] = None  # Combined prompt for image gen
    character_image_url: Optional[str] = None  # Generated character avatar

class Round(BaseModel):
    number: int
    type: Literal["survival", "blind_architect", "cooperative", "sacrifice", "last_stand", "ranked"] = "survival"
    scenario_text: str = ""
    scenario_image_url: Optional[str] = None
    status: Literal["scenario", "strategy", "judgement", "results", "trap_creation", "trap_voting", "coop_voting", "coop_judgement", "sacrifice_volunteer", "sacrifice_voting", "sacrifice_submission", "sacrifice_judgement", "last_stand_revival", "revival_judgement", "ranked_judgement"] = "scenario"
    architect_id: Optional[str] = None # For blind architect
    style_theme: Optional[str] = None  # Visual style theme for all images in this round
    sector_name: Optional[str] = None  # Creative name for this level/sector (LLM-generated)

    # Narrative system message for this level (displayed in UI)
    system_message: Optional[str] = None

    # Blind Architect specific
    trap_proposals: Dict[str, str] = {} # player_id -> trap description
    trap_images: Dict[str, str] = {} # player_id -> image_url
    votes: Dict[str, str] = {} # voter_id -> target_player_id

    # Cooperative round specific
    strategy_images: Dict[str, str] = {}        # player_id -> strategy image URL
    coop_votes: Dict[str, str] = {}             # voter_id -> target_player_id
    coop_vote_points: Dict[str, int] = {}       # player_id -> points from voting
    coop_team_winner_id: Optional[str] = None   # player who got random +200 bonus
    coop_team_loser_id: Optional[str] = None    # player who got random -200 penalty
    coop_winning_strategy_id: Optional[str] = None  # highest-voted strategy
    coop_team_survived: Optional[bool] = None   # did the team survive?

    # Sacrifice round specific
    sacrifice_volunteers: Dict[str, bool] = {}  # player_id -> volunteered (True)
    sacrifice_votes: Dict[str, str] = {}        # voter_id -> volunteer_id
    martyr_id: Optional[str] = None             # chosen sacrifice
    martyr_speech: Optional[str] = None         # martyr's death speech
    martyr_epic: Optional[bool] = None          # was the death epic?
    martyr_reason: Optional[str] = None         # why epic/lame
    martyr_image_url: Optional[str] = None      # image of the sacrifice

    # Last Stand revival specific
    revival_votes: Dict[str, str] = {}          # survivor_id -> dead_player_id
    revived_player_id: Optional[str] = None     # unanimously chosen player
    revival_survived: Optional[bool] = None     # did revived player survive?
    revival_reason: Optional[str] = None        # judgement reason
    revival_image_url: Optional[str] = None     # new result image

    # Ranked round specific
    ranked_results: Dict[str, int] = {}      # player_id -> rank (1 = first)
    ranked_points: Dict[str, int] = {}       # player_id -> points awarded
    ranked_commentary: Dict[str, str] = {}   # player_id -> LLM commentary

    # Timer for submission phases (30 second limit)
    submission_start_time: Optional[float] = None  # When submission phase started
    timed_out_players: Dict[str, bool] = {}        # player_id -> True if timed out

class GameState(BaseModel):
    id: str
    code: str
    status: Literal["lobby", "playing", "finished"] = "lobby"
    players: Dict[str, Player] = {}
    rounds: List[Round] = []
    current_round_idx: int = -1
    max_rounds: int = 5
    created_at: float = Field(default_factory=time.time)
    # Round configuration - determines type of each round (flexible positioning)
    round_config: List[str] = Field(default_factory=lambda: [
        "survival", "survival", "cooperative", "sacrifice", "last_stand"
    ])
    # Pre-warmed scenarios generated in parallel when game is created
    prewarmed_scenarios: List[Optional[str]] = []  # Index corresponds to round number - 1, None for blind_architect
    # End game video fields - videos for ALL players
    player_videos: Dict[str, str] = {}  # player_id -> video URL
    videos_status: Literal["pending", "generating", "ready", "failed"] = "pending"
    video_theme: Optional[str] = None  # Consistent theme for all videos
    winner_id: Optional[str] = None

# --- Persistent Storage ---
# We use a Dict to store game states. Key=GameCode
games = modal.Dict.from_name("mas-ai-games", create_if_missing=True)

# --- Secrets ---
# Use Modal's secret storage - create with: modal secret create ai-game-secrets MOONSHOT_API_KEY=xxx FAL_KEY=xxx
secrets = [modal.Secret.from_name("ai-game-secrets")]

# --- Helper Functions ---
def get_game(code: str) -> Optional[GameState]:
    data = games.get(code)
    if data:
        return GameState.model_validate(data)
    return None

def save_game(game: GameState):
    games[game.code] = game.model_dump()

# --- Core Game Logic & API ---

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

web_app = FastAPI()

# Helper for wrapping logic in routes
@web_app.post("/api/create_game")
async def api_create_game(request: Request):
    data = await request.json()
    import shortuuid
    code = shortuuid.ShortUUID().random(length=4).upper()
    game = GameState(id=str(uuid.uuid4()), code=code)
    save_game(game)

    # Spawn background task to pre-warm ALL scenarios in parallel
    print(f"API: Spawning scenario pre-warming for game {code}", flush=True)
    prewarm_all_scenarios.spawn(code)

    return {"code": code, "game_id": game.id}

@web_app.post("/api/join_game")
async def api_join_game(request: Request):
    """Join a game with retry logic to handle concurrent join race conditions.

    When multiple players join simultaneously, they may all read the same initial
    game state, modify it locally, and save - causing last-write-wins data loss.
    This retry-and-verify pattern ensures all joins are preserved.
    """
    import asyncio

    code = request.query_params.get("code")
    data = await request.json()
    player_name = data.get("name", "Unknown Player")
    character_description = data.get("character_description")
    character_image_url = data.get("character_image_url")  # Pre-generated image (from random selection)

    # Generate player ID upfront (consistent across retries)
    player_id = str(uuid.uuid4())
    is_first = None  # Will be determined by first successful read

    max_retries = 10
    for attempt in range(max_retries):
        game = get_game(code)

        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        if game.status != "lobby":
            raise HTTPException(status_code=400, detail="Game started")

        # Check if our player already exists (from a previous retry that succeeded)
        if player_id in game.players:
            print(f"JOIN: Player {player_name} ({player_id[:8]}...) already in game (retry verified)", flush=True)
            is_first = game.players[player_id].is_admin
            break

        # Determine admin status only on first attempt
        if is_first is None:
            is_first = len(game.players) == 0

        player = Player(
            id=player_id,
            name=player_name,
            is_admin=is_first,
            character_description=character_description,
            character_image_url=character_image_url
        )
        game.players[player_id] = player
        save_game(game)

        # Wait before verification to allow write to propagate
        # Add jitter (random delay) to reduce collision probability in concurrent requests
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the player was saved (re-read to check for race condition)
        verification_game = get_game(code)
        if verification_game and player_id in verification_game.players:
            print(f"JOIN: Player {player_name} ({player_id[:8]}...) joined successfully (attempt {attempt+1})", flush=True)
            game = verification_game  # Use verified state for subsequent operations
            break
        else:
            print(f"JOIN: Race condition detected for {player_name} ({player_id[:8]}...), retry {attempt+1}/{max_retries}", flush=True)
            # Exponential backoff with jitter before retry
            backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
            await asyncio.sleep(min(backoff, 2.0))  # Cap at 2 seconds
    else:
        # All retries exhausted
        raise HTTPException(status_code=500, detail="Failed to join game due to concurrent modifications, please try again")

    # Only spawn async character image generation if description provided AND no pre-generated image
    if character_description and not character_image_url:
        print(f"API: Spawning character image generation for {player_name}", flush=True)
        generate_character_image.spawn(code, player_id, character_description)
    elif not character_description:
        # No character description means they skip preview, so auto-enter lobby
        # Use robust retry pattern for this modification
        for attempt in range(10):
            game = get_game(code)
            if game and player_id in game.players:
                if game.players[player_id].in_lobby:
                    break  # Already set (maybe by concurrent retry)
                game.players[player_id].in_lobby = True
                save_game(game)
                jitter = random.uniform(0.05, 0.15)
                await asyncio.sleep(0.1 + jitter)
                # Verify
                verification = get_game(code)
                if verification and player_id in verification.players and verification.players[player_id].in_lobby:
                    break
                print(f"JOIN: in_lobby race condition for {player_name}, retry {attempt+1}/10", flush=True)
                backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
                await asyncio.sleep(min(backoff, 2.0))
    # If character_image_url is provided, the image is already ready (random selection flow)

    return {"player_id": player_id, "is_admin": is_first}


@web_app.get("/api/config")
async def api_get_config():
    """Return frontend-relevant configuration values."""
    return {
        "submission_timeout_seconds": CONFIG["game"]["submission_timeout_seconds"]
    }


@web_app.post("/api/enter_lobby")
async def api_enter_lobby(request: Request):
    """Mark a player as having entered the lobby (after avatar preview).

    Uses retry logic to handle concurrent modifications from other players
    joining or entering the lobby at the same time.
    """
    import asyncio

    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    max_retries = 10
    for attempt in range(max_retries):
        game = get_game(code)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        if player_id not in game.players:
            raise HTTPException(status_code=404, detail="Player not found")

        # Check if already in lobby
        if game.players[player_id].in_lobby:
            return {"status": "entered"}

        game.players[player_id].in_lobby = True
        save_game(game)

        # Wait with jitter before verification
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the change was saved
        verification = get_game(code)
        if verification and player_id in verification.players and verification.players[player_id].in_lobby:
            return {"status": "entered"}
        else:
            print(f"ENTER_LOBBY: Race condition for {player_id[:8]}..., retry {attempt+1}/{max_retries}", flush=True)
            backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
            await asyncio.sleep(min(backoff, 2.0))

    raise HTTPException(status_code=500, detail="Failed to enter lobby due to concurrent modifications")

@web_app.get("/api/get_game_state")
async def api_get_game_state(request: Request):
    code = request.query_params.get("code")
    game = get_game(code)
    if not game: raise HTTPException(status_code=404, detail="Game not found")

    # Check for player_id in query
    player_id = request.query_params.get("player_id")
    if player_id and player_id in game.players:
        game.players[player_id].last_active = time.time()

    # Check for submission timeout
    needs_save = False
    if game.status == "playing" and game.current_round_idx >= 0:
        current_round = game.rounds[game.current_round_idx]
        timeout_seconds = CONFIG["game"]["submission_timeout_seconds"]

        # Check if we're in a submission phase with an active timer
        if current_round.submission_start_time:
            elapsed = time.time() - current_round.submission_start_time

            if elapsed >= timeout_seconds:
                # Timer has expired - handle timeouts based on phase
                if current_round.status == "strategy":
                    # Mark players who haven't submitted as timed out and dead
                    for pid, p in game.players.items():
                        if p.is_alive and not p.strategy and p.in_lobby:
                            p.is_alive = False
                            p.death_reason = "TIMEOUT: Failed to submit strategy in time. Connection terminated."
                            current_round.timed_out_players[pid] = True
                            needs_save = True
                            print(f"TIMEOUT: Player {p.name} timed out in strategy phase", flush=True)

                            # For cooperative mode, generate a timeout failure image
                            if current_round.type == "cooperative":
                                p.strategy = "[TIMEOUT - No strategy submitted]"
                                # Spawn timeout image generation
                                generate_timeout_image.spawn(game.code, pid, current_round.style_theme)

                    # Clear the timer to prevent re-triggering
                    current_round.submission_start_time = None

                elif current_round.status == "trap_creation":
                    # Mark players who haven't submitted trap as timed out
                    for pid, p in game.players.items():
                        if p.is_alive and pid not in current_round.trap_proposals and p.in_lobby:
                            p.is_alive = False
                            p.death_reason = "TIMEOUT: Failed to design trap in time. Architect privileges revoked."
                            current_round.timed_out_players[pid] = True
                            needs_save = True
                            print(f"TIMEOUT: Player {p.name} timed out in trap_creation phase", flush=True)

                    # Clear the timer
                    current_round.submission_start_time = None

                elif current_round.status == "sacrifice_submission":
                    # Martyr timed out - everyone dies with a lame death
                    martyr = game.players.get(current_round.martyr_id)
                    if martyr and not current_round.martyr_speech:
                        current_round.martyr_speech = "[TIMEOUT - The martyr froze in fear and said nothing]"
                        current_round.martyr_epic = False
                        current_round.martyr_reason = "The chosen martyr stood frozen, unable to speak. Their silence condemned everyone. A truly pathetic end."

                        # Everyone dies
                        for pid, p in game.players.items():
                            if p.is_alive:
                                p.is_alive = False
                                if pid == current_round.martyr_id:
                                    p.death_reason = "Froze in fear and couldn't deliver a heroic speech."
                                else:
                                    p.death_reason = "Died because the martyr was too scared to speak."

                        current_round.status = "results"
                        current_round.submission_start_time = None
                        needs_save = True
                        print(f"TIMEOUT: Martyr {martyr.name} timed out, everyone dies", flush=True)

    if needs_save:
        save_game(game)

    # Include config values in response for frontend
    response = game.model_dump()
    response["config"] = {
        "submission_timeout_seconds": CONFIG["game"]["submission_timeout_seconds"]
    }
    return response

def get_system_message(round_num: int, max_rounds: int, round_type: str) -> str:
    """Generate the system message for a given round based on narrative progression."""
    if round_type == "blind_architect":
        return "SECURITY BREACH DETECTED // ARCHITECT PROTOCOL ACTIVATED"
    elif round_type == "cooperative":
        return "CRITICAL ERROR // COLLABORATIVE SUBROUTINE REQUIRED"
    elif round_type == "sacrifice":
        return "CRITICAL FAILURE // ONE MUST FALL FOR OTHERS TO SURVIVE"
    elif round_type == "last_stand":
        return "HO HO HO // EVIL SANTA'S NIGHTMARE WORKSHOP // YOU'VE BEEN VERY NAUGHTY"
    elif round_type == "ranked":
        return "PERFORMANCE EVALUATION // SURVIVAL EFFICIENCY RANKING PROTOCOL"

    # Standard survival rounds - progression-based messages
    if round_num == 1:
        return "SYSTEM BOOT // LEVEL 1 INITIALIZED"
    elif round_num == 2:
        return "CALIBRATION MODE // ANOMALIES DETECTED"
    elif round_num == max_rounds:
        return "EXIT PROTOCOL // FINAL LEVEL"
    else:
        corruption_pct = min(90, 50 + (round_num * 10))
        return f"WARNING: CORRUPTION AT {corruption_pct}% // REALITY UNSTABLE"


@web_app.post("/api/start_game")
async def api_start_game(request: Request):
    print("API: Start Game Called")
    code = request.query_params.get("code")
    game = get_game(code)
    if not game:
        print("API: Game not found")
        raise HTTPException(status_code=404, detail="Game not found")

    # Use pre-warmed scenario if available, otherwise generate on-demand (fallback)
    if game.prewarmed_scenarios and len(game.prewarmed_scenarios) > 0 and game.prewarmed_scenarios[0]:
        scenario_text = game.prewarmed_scenarios[0]
        print(f"API: Using pre-warmed scenario: {scenario_text[:50]}...")
    else:
        print("API: No pre-warmed scenario, generating on-demand...")
        scenario_text = generate_scenario_llm(1, game.max_rounds)
        print(f"API: Scenario Generated: {scenario_text}")
        # Re-fetch after slow operation
        game = get_game(code)
        if not game:
            raise HTTPException(status_code=404, detail="Game disappeared")

    print(f"API: Starting game {code}")
    game.status = "playing"
    game.current_round_idx = 0

    # Use round_config to determine first round type
    first_round_type = game.round_config[0] if game.round_config else "survival"
    first_round = Round(number=1, type=first_round_type)
    first_round.scenario_text = scenario_text
    # Force anime style for last_stand (Evil Santa) rounds
    if first_round_type == "last_stand":
        first_round.style_theme = "anime, evil Christmas, dramatic lighting"
    else:
        first_round.style_theme = random.choice(IMAGE_STYLE_THEMES)
    first_round.system_message = get_system_message(1, game.max_rounds, first_round_type)

    # Set initial status based on round type
    if first_round_type == "blind_architect":
        first_round.status = "trap_creation"
        first_round.submission_start_time = time.time()  # Start timer for trap creation
    elif first_round_type == "sacrifice":
        first_round.status = "sacrifice_volunteer"
        first_round.scenario_text = "SACRIFICE PROTOCOL: One must fall for others to survive. Who will volunteer as tribute?"
    else:
        # survival, cooperative, and last_stand start with strategy
        first_round.status = "strategy"
        first_round.submission_start_time = time.time()  # Start timer for strategy

    game.rounds.append(first_round)

    save_game(game)
    print(f"API: Game Saved (first round type: {first_round_type})")
    return {"status": "started", "scenario": first_round.scenario_text, "type": first_round_type}

# Async Judgement Worker
@app.function(image=image, secrets=secrets)
def process_judgement(game_id: str, round_idx: int, player_id: str):
    import json
    
    # Need to reload game from DB to get latest state/lock? 
    # For MVP we can just get, modify, save. Race conditions possible but rare in this turn-based flow.
    # Actually, pass the data we need to avoid race on game object if possible, 
    # but we need to write back to the specific player.
    
    # Let's load game by ID (we stored code->serialized, but here we can look it up if we had index)
    # Actually we only have access by Code in our simple Dict. 
    # Pass Code.
    pass 

# Helper to process single player judgement
@app.function(image=image, secrets=secrets)
def run_player_judgement(scenario: str, player: Player) -> Player:
    import json
    # 1. Judge
    try:
        result_json = judge_strategy_llm(scenario, player.strategy)
        res = json.loads(result_json)
        survived = res.get("survived", False)
        reason = res.get("reason", "Unknown")
        vis_prompt = res.get("visual_prompt", "A generic scene.")
        
        player.is_alive = survived
        if not survived:
            player.death_reason = reason
        else:
            player.score += 100
            
        return player, vis_prompt
    except Exception as e:
        print(f"Judgement Error: {e}")
        return player, None

@app.function(image=image, secrets=secrets)
def generate_result_image_sync(game_code: str, player_id: str, prompt: str):
    """Sync wrapper for spawning - updates game state with generated image."""
    url = generate_image_fal(prompt)
    if url:
        game = get_game(game_code)
        if game and player_id in game.players:
            game.players[player_id].result_image_url = url
            save_game(game)


@app.function(image=image, secrets=secrets)
def generate_timeout_image(game_code: str, player_id: str, style_theme: str | None):
    """Generate a timeout/failure image for cooperative mode when player does not submit."""
    import asyncio

    async def do_generation():
        print(f"TIMEOUT IMG: Generating timeout image for player {player_id}...", flush=True)

        # Timeout-themed prompt
        timeout_prompts = [
            "A broken hourglass with sand frozen in mid-air, shattered glass fragments, time stopped",
            "A glitching computer screen showing CONNECTION LOST, digital corruption, static",
            "A figure dissolving into pixels, data corruption, digital death",
            "An empty chair with a fading silhouette, abandoned station, timeout error",
            "A frozen clock face cracking apart, time running out, dramatic failure",
        ]
        base_prompt = random.choice(timeout_prompts) + ". Dramatic, failure, timeout, dramatic lighting."
        themed_prompt = apply_style_theme(base_prompt, style_theme)

        url = await generate_image_fal_async(themed_prompt)
        if url:
            game = get_game(game_code)
            if game and game.current_round_idx >= 0:
                current_round = game.rounds[game.current_round_idx]
                # For cooperative mode, store in strategy_images
                if current_round.type == "cooperative":
                    current_round.strategy_images[player_id] = url
                    save_game(game)
                    print(f"TIMEOUT IMG: Saved timeout image for {player_id}", flush=True)
        else:
            print(f"TIMEOUT IMG: Failed to generate for {player_id}", flush=True)

    asyncio.run(do_generation())


@app.function(image=image, secrets=secrets)
def generate_character_image(game_code: str, player_id: str, character_prompt: str):
    """Generate character avatar and update player state.

    Uses retry logic to safely update the player's image URL without
    accidentally overwriting other concurrent modifications (like other
    players joining or other images being saved).
    """
    import asyncio

    async def do_generation():
        print(f"CHARACTER IMG: Generating for player {player_id}...", flush=True)
        url = await generate_character_image_async(character_prompt)
        if not url:
            print(f"CHARACTER IMG: Failed to generate for {player_id}", flush=True)
            return

        # Use retry-and-verify pattern to safely update the player's image
        max_retries = 10
        for attempt in range(max_retries):
            game = get_game(game_code)
            if not game:
                print(f"CHARACTER IMG: Game {game_code} not found!", flush=True)
                return
            if player_id not in game.players:
                print(f"CHARACTER IMG: Player {player_id} not found!", flush=True)
                return

            # Check if already set (maybe by concurrent retry)
            if game.players[player_id].character_image_url == url:
                print(f"CHARACTER IMG: Image already saved for {player_id}", flush=True)
                return

            game.players[player_id].character_image_url = url
            save_game(game)

            # Wait with jitter before verification
            jitter = random.uniform(0.05, 0.15)
            await asyncio.sleep(0.1 + jitter)

            # Verify the change was saved
            verification = get_game(game_code)
            if verification and player_id in verification.players:
                if verification.players[player_id].character_image_url == url:
                    print(f"CHARACTER IMG: Saved image for {player_id} (attempt {attempt+1})", flush=True)
                    return
            print(f"CHARACTER IMG: Race condition for {player_id}, retry {attempt+1}/{max_retries}", flush=True)
            backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
            await asyncio.sleep(min(backoff, 2.0))

        print(f"CHARACTER IMG: Failed to save after {max_retries} retries for {player_id}", flush=True)

    asyncio.run(do_generation())


@app.function(image=image, secrets=secrets)
def prewarm_all_scenarios(game_code: str):
    """Pre-generate scenarios for ALL rounds in parallel when game is created."""
    import asyncio

    async def do_prewarm():
        game = get_game(game_code)
        if not game:
            print(f"PREWARM: Game {game_code} not found!", flush=True)
            return

        if game.status != "lobby":
            print(f"PREWARM: Game {game_code} not in lobby, skipping", flush=True)
            return

        max_rounds = game.max_rounds
        round_config = game.round_config

        # Determine which rounds need scenarios (survival, cooperative, last_stand - not blind_architect or sacrifice)
        tasks = []
        round_indices = []
        for i in range(max_rounds):
            round_type = round_config[i] if i < len(round_config) else "survival"
            # Skip blind_architect (scenario from player trap) and sacrifice (scenario from martyr context)
            if round_type not in ("blind_architect", "sacrifice"):
                # Use special Evil Santa scenario for last_stand rounds
                if round_type == "last_stand":
                    tasks.append(generate_last_stand_scenario_async())
                else:
                    tasks.append(generate_scenario_llm_async(i + 1, max_rounds))
                round_indices.append(i)

        if not tasks:
            print(f"PREWARM: No scenarios to generate for {game_code}", flush=True)
            return

        print(f"PREWARM: Generating {len(tasks)} scenarios in parallel for {game_code}...", flush=True)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Re-fetch game to avoid overwriting other changes
        game = get_game(game_code)
        if not game or game.status != "lobby":
            print(f"PREWARM: Game {game_code} changed, discarding results", flush=True)
            return

        # Build scenarios list (None for blind_architect rounds)
        scenarios = [None] * max_rounds
        for idx, round_idx in enumerate(round_indices):
            result = results[idx]
            if isinstance(result, Exception):
                print(f"PREWARM: Error for round {round_idx + 1}: {result}", flush=True)
                scenarios[round_idx] = None
            else:
                scenarios[round_idx] = result
                print(f"PREWARM: Round {round_idx + 1} ready: {result[:50]}...", flush=True)

        game.prewarmed_scenarios = scenarios
        save_game(game)
        print(f"PREWARM: Complete! {len([s for s in scenarios if s])} scenarios saved", flush=True)

    asyncio.run(do_prewarm())


@app.function(image=image, secrets=secrets)
def run_round_judgement(game_code: str):
    """Run judgement for all players in parallel using asyncio."""
    import json
    import asyncio

    async def judge_and_generate(pid: str, player_name: str, strategy: str, scenario: str, style_theme: str | None):
        """Judge a single player and generate their result image."""
        try:
            # Judge the strategy
            result_json = await judge_strategy_llm_async(scenario, strategy)
            print(f"JUDGEMENT: Got result for {player_name}: {result_json[:100]}...", flush=True)
            res = json.loads(result_json)
            survived = res.get("survived", False)
            reason = res.get("reason", "Unknown")
            vis_prompt = res.get("visual_prompt", "A generic scene.")

            # Generate image with round's style theme
            themed_prompt = apply_style_theme(vis_prompt, style_theme)
            image_url = await generate_image_fal_async(themed_prompt)

            return {
                "pid": pid,
                "survived": survived,
                "reason": reason,
                "image_url": image_url
            }
        except Exception as e:
            print(f"JUDGEMENT: Error for {pid}: {e}", flush=True)
            return {
                "pid": pid,
                "survived": False,
                "reason": "The AI judge malfunctioned...",
                "image_url": None
            }

    async def run_all_judgements():
        print(f"JUDGEMENT: Starting for game {game_code}", flush=True)

        game = get_game(game_code)
        if not game:
            print(f"JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        print(f"JUDGEMENT: Round {current_round.number}, scenario: {current_round.scenario_text[:50]}...", flush=True)

        # Collect all players that need judging
        tasks = []
        player_info = []
        for pid, p in game.players.items():
            print(f"JUDGEMENT: Player {p.name} (alive={p.is_alive}, strategy={bool(p.strategy)})", flush=True)
            if p.strategy and p.is_alive:
                tasks.append(judge_and_generate(pid, p.name, p.strategy, current_round.scenario_text, current_round.style_theme))
                player_info.append((pid, p.name))

        if tasks:
            print(f"JUDGEMENT: Running {len(tasks)} judgements in parallel...", flush=True)
            # Run all judgements in parallel
            results = await asyncio.gather(*tasks)

            # Apply results to game state
            for result in results:
                pid = result["pid"]
                p = game.players[pid]
                p.is_alive = result["survived"]
                if not result["survived"]:
                    p.death_reason = result["reason"]
                    p.survival_reason = None
                else:
                    p.score += 100
                    p.survival_reason = result["reason"]
                    p.death_reason = None
                if result["image_url"]:
                    p.result_image_url = result["image_url"]
                print(f"JUDGEMENT: {p.name} survived={result['survived']}", flush=True)

        # ALWAYS set status to results so game doesn't hang
        print(f"JUDGEMENT: Setting status to results", flush=True)
        current_round.status = "results"
        save_game(game)
        print(f"JUDGEMENT: Complete!", flush=True)

    # Run the async function
    asyncio.run(run_all_judgements())


@app.function(image=image, secrets=secrets)
def run_ranked_judgement(game_code: str):
    """Run ranked judgement - compare all strategies and assign rankings."""
    import json
    import asyncio

    async def do_ranked_judgement():
        print(f"RANKED_JUDGE: Starting for game {game_code}", flush=True)

        game = get_game(game_code)
        if not game:
            print(f"RANKED_JUDGE: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]

        # Collect all alive players with strategies
        strategies = []
        for pid, p in game.players.items():
            if p.is_alive and p.strategy:
                strategies.append({
                    "player_id": pid,
                    "name": p.name,
                    "strategy": p.strategy
                })

        if not strategies:
            print("RANKED_JUDGE: No strategies to judge!", flush=True)
            current_round.status = "results"
            save_game(game)
            return

        print(f"RANKED_JUDGE: Judging {len(strategies)} strategies...", flush=True)

        try:
            # Get comparative ranking from LLM
            result_json = await rank_all_strategies_llm_async(
                current_round.scenario_text,
                strategies
            )
            result = json.loads(result_json)
            rankings = result.get("rankings", [])

            # Store rankings and calculate points
            num_players = len(strategies)
            visual_prompts = {}

            for r in rankings:
                pid = r["player_id"]
                rank = r["rank"]
                commentary = r.get("commentary", "No comment")
                vis_prompt = r.get("visual_prompt", "A survival scene")

                # Store in round data
                current_round.ranked_results[pid] = rank
                current_round.ranked_commentary[pid] = commentary

                # Calculate and award points
                points = calculate_ranked_points(num_players, rank)
                current_round.ranked_points[pid] = points
                game.players[pid].score += points
                game.players[pid].survival_reason = commentary
                game.players[pid].is_alive = True  # Everyone survives ranked rounds

                visual_prompts[pid] = vis_prompt

                print(f"RANKED_JUDGE: {game.players[pid].name} - Rank {rank}, +{points} pts", flush=True)

            # Generate images in parallel
            async def generate_player_image(pid: str, prompt: str):
                themed_prompt = apply_style_theme(prompt, current_round.style_theme)
                url = await generate_image_fal_async(themed_prompt)
                return pid, url

            image_tasks = [
                generate_player_image(pid, prompt)
                for pid, prompt in visual_prompts.items()
            ]
            image_results = await asyncio.gather(*image_tasks)

            # Apply images to players
            for pid, url in image_results:
                if url:
                    game.players[pid].result_image_url = url

        except Exception as e:
            print(f"RANKED_JUDGE: Error - {e}", flush=True)
            # Fallback: give everyone participation points
            for s in strategies:
                pid = s["player_id"]
                current_round.ranked_results[pid] = 1
                current_round.ranked_points[pid] = 25
                game.players[pid].score += 25
                game.players[pid].is_alive = True

        # Transition to results
        current_round.status = "results"
        save_game(game)
        print("RANKED_JUDGE: Complete!", flush=True)

    asyncio.run(do_ranked_judgement())


@app.function(image=image, secrets=secrets)
def judge_single_player(game_code: str, player_id: str):
    """Judge a single player immediately when they submit strategy (early judgement for latency reduction)."""
    import json
    import asyncio

    async def do_judge():
        print(f"EARLY_JUDGE: Starting for player {player_id} in game {game_code}", flush=True)

        game = get_game(game_code)
        if not game:
            print(f"EARLY_JUDGE: Game {game_code} not found!", flush=True)
            return

        if player_id not in game.players:
            print(f"EARLY_JUDGE: Player {player_id} not found!", flush=True)
            return

        player = game.players[player_id]
        current_round = game.rounds[game.current_round_idx]

        # Only judge if player has strategy, is alive, and we're in strategy phase
        if not player.strategy or not player.is_alive:
            print(f"EARLY_JUDGE: Player {player.name} not eligible (strategy={bool(player.strategy)}, alive={player.is_alive})", flush=True)
            player.judgement_pending = False
            save_game(game)
            return

        try:
            # Judge the strategy
            result_json = await judge_strategy_llm_async(current_round.scenario_text, player.strategy)
            print(f"EARLY_JUDGE: Got result for {player.name}: {result_json[:100]}...", flush=True)
            res = json.loads(result_json)
            survived = res.get("survived", False)
            reason = res.get("reason", "Unknown")
            vis_prompt = res.get("visual_prompt", "A generic scene.")

            # Generate image with round's style theme
            themed_prompt = apply_style_theme(vis_prompt, current_round.style_theme)
            image_url = await generate_image_fal_async(themed_prompt)

            # Re-fetch game state to get latest (in case other players submitted)
            game = get_game(game_code)
            if not game:
                print(f"EARLY_JUDGE: Game disappeared!", flush=True)
                return

            current_round = game.rounds[game.current_round_idx]
            player = game.players[player_id]

            # Apply results to player
            player.is_alive = survived
            if not survived:
                player.death_reason = reason
                player.survival_reason = None
            else:
                player.score += 100
                player.survival_reason = reason
                player.death_reason = None
            if image_url:
                player.result_image_url = image_url
            player.judgement_pending = False

            print(f"EARLY_JUDGE: {player.name} survived={survived}", flush=True)

        except Exception as e:
            print(f"EARLY_JUDGE: Error for {player.name}: {e}", flush=True)
            # Re-fetch and set defaults
            game = get_game(game_code)
            if game and player_id in game.players:
                player = game.players[player_id]
                player.is_alive = False
                player.death_reason = "The AI judge malfunctioned..."
                player.survival_reason = None
                player.judgement_pending = False

        # Check if all players are done - if so, transition to results
        # Using 5 minutes instead of 60s to give players time to think about strategies
        cutoff = time.time() - 300

        # Get all active in-lobby players (regardless of alive status - that changes during judgement)
        active_in_lobby = [p for p in game.players.values()
                          if p.last_active > cutoff and p.in_lobby]

        # Check if any judgements are still pending (across ALL players, not just filtered)
        any_pending = any(p.judgement_pending for p in game.players.values())
        # Check if all active in-lobby players have submitted strategies
        all_submitted = all(p.strategy for p in active_in_lobby) if active_in_lobby else True

        print(f"EARLY_JUDGE: Check - pending={any_pending}, submitted={all_submitted}, players={len(active_in_lobby)}, status={current_round.status}", flush=True)

        # Transition to results when all judgements complete
        # Status could be "strategy" (still waiting for others) or "judgement" (all submitted, waiting for judges)
        if current_round.status in ["strategy", "judgement"] and all_submitted and not any_pending:
            print("EARLY_JUDGE: All judgements complete! Transitioning to results.", flush=True)
            current_round.status = "results"

        save_game(game)
        print(f"EARLY_JUDGE: Complete for {player.name}!", flush=True)

    asyncio.run(do_judge())


# Keep old function name as alias for backwards compatibility
generate_result_image_async = generate_result_image_sync


@app.function(image=image, secrets=secrets, timeout=900)  # 15 min timeout for multiple videos
def generate_all_player_videos(game_code: str):
    """Generate personalized 10-second videos for ALL players using parallel phases."""
    import asyncio
    import httpx

    async def do_all_video_generation():
        game = get_game(game_code)
        if not game:
            print(f"VIDEO GEN: Game {game_code} not found!", flush=True)
            return

        # Sort players by score
        sorted_players = sorted(game.players.values(), key=lambda p: p.score, reverse=True)
        if not sorted_players:
            print("VIDEO GEN: No players found!", flush=True)
            return

        total_players = len(sorted_players)
        winner = sorted_players[0]

        # Select a random video theme for consistency across all videos
        video_theme = random.choice(VIDEO_STYLE_THEMES)

        game.winner_id = winner.id
        game.videos_status = "generating"
        game.video_theme = video_theme
        save_game(game)

        print(f"VIDEO GEN: Starting PARALLEL generation for {total_players} players", flush=True)
        print(f"VIDEO GEN: Theme: {video_theme}", flush=True)

        # ============================================================
        # PHASE 1: Generate ALL LLM prompts in parallel
        # ============================================================
        print(f"VIDEO GEN PHASE 1: Generating {total_players} LLM prompts in parallel...", flush=True)

        llm_tasks = []
        for rank, player in enumerate(sorted_players, start=1):
            llm_tasks.append(generate_video_prompt_llm_async(
                player.name, rank, total_players, player.score, video_theme
            ))

        llm_results = await asyncio.gather(*llm_tasks, return_exceptions=True)

        # Process LLM results
        player_prompts = {}  # player_id -> {"scene": ..., "dialogue": ...}
        for idx, (player, result) in enumerate(zip(sorted_players, llm_results)):
            if isinstance(result, Exception):
                print(f"VIDEO GEN PHASE 1: LLM error for {player.name}: {result}", flush=True)
                player_prompts[player.id] = {
                    "scene": "A ceremony scene with spotlights",
                    "dialogue": f"Congratulations to {player.name}!"
                }
            else:
                player_prompts[player.id] = result

        print(f"VIDEO GEN PHASE 1: Complete - {len(player_prompts)} prompts generated", flush=True)

        # ============================================================
        # PHASE 2: Generate ALL base images in parallel
        # ============================================================
        print(f"VIDEO GEN PHASE 2: Generating {total_players} images in parallel...", flush=True)

        image_tasks = []
        for player in sorted_players:
            prompt_data = player_prompts[player.id]
            scene = prompt_data.get("scene", "A ceremony scene")
            image_prompt = f"{scene}. Setting: {video_theme}. Cinematic, dramatic lighting, vivid colors."
            image_tasks.append(generate_image_fal_async(image_prompt))

        image_results = await asyncio.gather(*image_tasks, return_exceptions=True)

        # Process image results
        player_images = {}  # player_id -> image_url
        for player, result in zip(sorted_players, image_results):
            if isinstance(result, Exception) or result is None:
                print(f"VIDEO GEN PHASE 2: Image failed for {player.name}", flush=True)
            else:
                player_images[player.id] = result
                print(f"VIDEO GEN PHASE 2: Image ready for {player.name}", flush=True)

        print(f"VIDEO GEN PHASE 2: Complete - {len(player_images)}/{total_players} images generated", flush=True)

        if not player_images:
            print("VIDEO GEN: All image generations failed, aborting", flush=True)
            game = get_game(game_code)
            if game:
                game.videos_status = "failed"
                save_game(game)
            return

        # ============================================================
        # PHASE 3: Submit ALL video requests in parallel (don't wait)
        # ============================================================
        print(f"VIDEO GEN PHASE 3: Submitting {len(player_images)} video requests in parallel...", flush=True)

        async with httpx.AsyncClient(timeout=60.0) as client:
            submit_tasks = []
            players_to_submit = []

            for player in sorted_players:
                if player.id not in player_images:
                    continue
                prompt_data = player_prompts[player.id]
                scene = prompt_data.get("scene", "A ceremony scene")
                dialogue = prompt_data.get("dialogue", f"Well done, {player.name}!")
                image_url = player_images[player.id]

                submit_tasks.append(submit_video_request_async(
                    player.name, image_url, scene, dialogue, video_theme, client
                ))
                players_to_submit.append(player)

            submit_results = await asyncio.gather(*submit_tasks, return_exceptions=True)

            # Collect request IDs
            player_request_ids = {}  # player_id -> request_id
            for player, result in zip(players_to_submit, submit_results):
                if isinstance(result, Exception) or result is None:
                    print(f"VIDEO GEN PHASE 3: Submit failed for {player.name}", flush=True)
                else:
                    player_request_ids[player.id] = result

            print(f"VIDEO GEN PHASE 3: Complete - {len(player_request_ids)}/{len(players_to_submit)} requests submitted", flush=True)

            if not player_request_ids:
                print("VIDEO GEN: All video submissions failed, aborting", flush=True)
                game = get_game(game_code)
                if game:
                    game.videos_status = "failed"
                    save_game(game)
                return

            # ============================================================
            # PHASE 4: Poll ALL video statuses in parallel
            # ============================================================
            print(f"VIDEO GEN PHASE 4: Polling {len(player_request_ids)} videos in parallel...", flush=True)

            poll_tasks = []
            players_to_poll = []

            for player in sorted_players:
                if player.id not in player_request_ids:
                    continue
                request_id = player_request_ids[player.id]
                poll_tasks.append(poll_video_status_async(player.name, request_id, client))
                players_to_poll.append(player)

            poll_results = await asyncio.gather(*poll_tasks, return_exceptions=True)

            # Collect video URLs
            player_videos = {}  # player_id -> video_url
            for player, result in zip(players_to_poll, poll_results):
                if isinstance(result, Exception) or result is None:
                    print(f"VIDEO GEN PHASE 4: Video failed for {player.name}", flush=True)
                else:
                    player_videos[player.id] = result

            print(f"VIDEO GEN PHASE 4: Complete - {len(player_videos)}/{len(players_to_poll)} videos ready", flush=True)

        # ============================================================
        # Save results to game state
        # ============================================================
        game = get_game(game_code)
        if game:
            for player_id, video_url in player_videos.items():
                game.player_videos[player_id] = video_url

            if player_videos:
                game.videos_status = "ready"
                print(f"VIDEO GEN: SUCCESS! {len(player_videos)}/{total_players} videos saved", flush=True)
            else:
                game.videos_status = "failed"
                print("VIDEO GEN: All video generations failed", flush=True)

            save_game(game)

    asyncio.run(do_all_video_generation())


# Keep old function name as alias for backwards compatibility
generate_winner_video = generate_all_player_videos


# --- Cooperative Round Functions ---

@app.function(image=image, secrets=secrets)
def generate_coop_strategy_images(game_code: str):
    """Generate strategy visualization images for all players in cooperative round."""
    import asyncio

    async def generate_all_images():
        game = get_game(game_code)
        if not game:
            print(f"COOP IMAGES: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        print(f"COOP IMAGES: Generating images for {len(game.players)} players", flush=True)

        # Generate images for all alive players with strategies
        tasks = []
        player_ids = []
        for pid, player in game.players.items():
            if player.is_alive and player.strategy:
                base_prompt = f"Survival strategy illustration: {player.strategy[:200]}. Dramatic scene, cinematic lighting, vivid colors."
                themed_prompt = apply_style_theme(base_prompt, current_round.style_theme)
                tasks.append(generate_image_fal_async(themed_prompt))
                player_ids.append(pid)

        if tasks:
            print(f"COOP IMAGES: Generating {len(tasks)} images in parallel...", flush=True)
            results = await asyncio.gather(*tasks)

            # Reload game to get fresh state before updating
            game = get_game(game_code)
            if not game:
                return
            current_round = game.rounds[game.current_round_idx]

            for pid, image_url in zip(player_ids, results):
                if image_url:
                    current_round.strategy_images[pid] = image_url
                    print(f"COOP IMAGES: Generated image for {pid}", flush=True)

            save_game(game)
            print(f"COOP IMAGES: Complete! {len(current_round.strategy_images)} images saved", flush=True)

    asyncio.run(generate_all_images())


def tally_coop_votes_and_transition(game: GameState, current_round: Round):
    """Tally cooperative votes, assign points based on ranking, and prepare for team judgement."""
    # Count votes per target
    vote_counts = {}
    for target in current_round.coop_votes.values():
        vote_counts[target] = vote_counts.get(target, 0) + 1

    # Include players with 0 votes
    alive_players = [p for p in game.players.values() if p.is_alive]
    for p in alive_players:
        if p.id not in vote_counts:
            vote_counts[p.id] = 0

    # Sort by vote count (descending)
    sorted_players = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
    num_players = len(sorted_players)

    print(f"COOP TALLY: Vote counts: {sorted_players}", flush=True)

    # Assign points based on ranking: +200 (1st), +100 (2nd), 0 (middle), -100 (last)
    for rank, (pid, votes) in enumerate(sorted_players):
        if num_players == 2:
            # 2 players: 1st gets +200, last gets -100
            points = 200 if rank == 0 else -100
        elif num_players == 3:
            # 3 players: +200, +100, -100
            if rank == 0:
                points = 200
            elif rank == 1:
                points = 100
            else:
                points = -100
        else:
            # 4+ players: +200, +100, 0..., -100
            if rank == 0:
                points = 200
            elif rank == 1:
                points = 100
            elif rank == num_players - 1:
                points = -100
            else:
                points = 0

        current_round.coop_vote_points[pid] = points
        game.players[pid].score += points
        print(f"COOP TALLY: {game.players[pid].name} got {points} pts (rank {rank+1})", flush=True)

    # Determine winning strategy (highest votes, random tiebreak)
    max_votes = sorted_players[0][1]
    top_players = [pid for pid, v in sorted_players if v == max_votes]
    winner_id = random.choice(top_players)
    current_round.coop_winning_strategy_id = winner_id
    print(f"COOP TALLY: Winning strategy by {game.players[winner_id].name}", flush=True)

    # Transition to coop_judgement
    current_round.status = "coop_judgement"


@app.function(image=image, secrets=secrets)
def run_coop_judgement(game_code: str):
    """Run team judgement based on the highest-voted strategy."""
    import json
    import asyncio

    async def do_judgement():
        game = get_game(game_code)
        if not game:
            print(f"COOP JUDGE: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        winning_pid = current_round.coop_winning_strategy_id
        if not winning_pid:
            print("COOP JUDGE: No winning strategy ID!", flush=True)
            current_round.status = "results"
            save_game(game)
            return

        winning_strategy = game.players[winning_pid].strategy
        print(f"COOP JUDGE: Judging strategy: {winning_strategy[:100]}...", flush=True)

        try:
            # Judge the winning strategy
            result_json = await judge_strategy_llm_async(current_round.scenario_text, winning_strategy)
            print(f"COOP JUDGE: Result: {result_json[:200]}...", flush=True)
            res = json.loads(result_json)
            team_survived = res.get("survived", False)
            current_round.coop_team_survived = team_survived

            # Get list of alive players
            alive_players = [p for p in game.players.values() if p.is_alive]

            if team_survived:
                # Random player gets +200 bonus
                lucky_player = random.choice(alive_players)
                lucky_player.score += 200
                current_round.coop_team_winner_id = lucky_player.id
                print(f"COOP JUDGE: SURVIVED! {lucky_player.name} gets +200 bonus", flush=True)
            else:
                # ALL players lose 100 points when team fails
                for p in alive_players:
                    p.score -= 100
                print(f"COOP JUDGE: FAILED! All {len(alive_players)} players lose -100 each", flush=True)

            # Generate team result image with round's style theme
            vis_prompt = res.get("visual_prompt", "Team survival scene")
            themed_prompt = apply_style_theme(vis_prompt, current_round.style_theme)
            image_url = await generate_image_fal_async(themed_prompt)
            if image_url:
                current_round.scenario_image_url = image_url  # Reuse for team result display

        except Exception as e:
            print(f"COOP JUDGE: Error: {e}", flush=True)
            current_round.coop_team_survived = False
            # All players lose 100 points on error/failure
            alive_players = [p for p in game.players.values() if p.is_alive]
            for p in alive_players:
                p.score -= 100

        # Always set status to results
        current_round.status = "results"
        save_game(game)
        print("COOP JUDGE: Complete!", flush=True)

    asyncio.run(do_judgement())


@web_app.post("/api/submit_strategy")
async def api_submit_strategy(request: Request):
    try:
        print("API: Submit Strategy ENTRY", flush=True)
        code = request.query_params.get("code")
        data = await request.json()
        
        # 1. First fetch to validate and save strategy
        game = get_game(code)
        player_id = data.get("player_id")
        strategy = data.get("strategy")
        
        if not game:
             print("API: Game not found (submit)")
             raise HTTPException(status_code=404, detail="Game not found")
        if not player_id:
             raise HTTPException(status_code=400, detail="Missing player_id")
        
        current_round = game.rounds[game.current_round_idx]
        if current_round.status != "strategy": 
            print(f"API: Submit Strategy WRONG PHASE. Current: {current_round.status}", flush=True)
            raise HTTPException(status_code=400, detail=f"Wrong phase: {current_round.status}")
             
        print(f"API: Submit Strategy for {player_id} in {code}")
        if player_id in game.players:
            game.players[player_id].strategy = strategy
            game.players[player_id].last_active = time.time() # Update heartbeat
            # DON'T save yet - we'll save after checking advancement to avoid race condition
            print(f"API: Strategy set for {player_id}")
        else:
             print(f"API: Player {player_id} not found in game")
             raise HTTPException(status_code=404, detail="Player not found")

        # 2. Logic to check for advancement
        # IMPORTANT: Do NOT re-fetch game here! Modal Dict has eventual consistency,
        # so a re-fetch might not see the strategy we just set. Use the same game object.
        # See CLAUDE.md "Known Issues" section for details.

        # Filter for active players who are in the lobby (active in last 5 minutes)
        # Using 5 minutes instead of 60s to give players time to think about strategies
        # without being considered "inactive" and excluded from the completion check
        cutoff = time.time() - 300

        alive_players = []
        for _, p in game.players.items():
            is_active = p.last_active > cutoff
            # Only count players who have entered the lobby (not still in avatar preview)
            if p.is_alive and is_active and p.in_lobby:
                alive_players.append(p)

        if not alive_players:
            print("API: Warn - No alive players found. Forcing current.")
            alive_players = [game.players[player_id]]

        strategies_submitted = sum(1 for p in alive_players if p.strategy)
        print(f"API: Strategies Submitted: {strategies_submitted} / {len(alive_players)}")

        # For survival/blind_architect rounds, spawn early judgement immediately
        # This reduces latency by judging players as they submit, not waiting for all
        if current_round.type in ["survival", "blind_architect"]:
            # Mark player as pending judgement and spawn early judge
            game.players[player_id].judgement_pending = True

            # If all players have submitted, transition to "judgement" phase (shows JUDGING... animation)
            if strategies_submitted >= len(alive_players):
                print("API: All strategies received. Showing JUDGEMENT phase.")
                current_round.status = "judgement"

            save_game(game)
            print(f"API: Spawning EARLY JUDGEMENT for {player_id}")
            judge_single_player.spawn(code, player_id)
            # The judge_single_player function will handle transitioning to results
            # when all judgements are complete
        elif strategies_submitted >= len(alive_players):
            current_round = game.rounds[game.current_round_idx]

            if current_round.type == "cooperative":
                # Cooperative round: transition to image voting phase
                print("API: All strategies received. Advancing to COOP VOTING.")
                current_round.status = "coop_voting"
                save_game(game)
                # Spawn async image generation for all strategies
                generate_coop_strategy_images.spawn(code)
            elif current_round.type == "last_stand":
                # Last Stand: harsh judgement with potential revival phase
                print("API: All strategies received. Advancing to LAST STAND Judgement.")
                current_round.status = "judgement"
                save_game(game)
                # Trigger harsh async judgement
                run_last_stand_judgement.spawn(code)
            elif current_round.type == "sacrifice":
                # Sacrifice: go to volunteer phase
                print("API: All strategies received. Advancing to SACRIFICE VOLUNTEER.")
                current_round.status = "sacrifice_volunteer"
                save_game(game)
            elif current_round.type == "ranked":
                # Ranked round: compare all strategies and rank them
                print("API: All strategies received. Advancing to RANKED Judgement.")
                current_round.status = "ranked_judgement"
                save_game(game)
                run_ranked_judgement.spawn(code)
            else:
                # Fallback for any other round type
                print("API: All strategies received. Advancing to Judgement.")
                current_round.status = "judgement"
                save_game(game)
                run_round_judgement.spawn(code)
        else:
            print("API: Waiting for others... Saving strategy.")
            save_game(game)  # Save the strategy even if not advancing!

        return {"status": "submitted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"API: Submit Strategy EXCEPTION: {e}", flush=True)
        # Return error JSON so frontend doesn't get 'null'
        return JSONResponse(status_code=500, content={"detail": f"Internal Error: {str(e)}"})

@web_app.post("/api/submit_trap")
async def api_submit_trap(request: Request):
    code = request.query_params.get("code")
    data = await request.json()
    game = get_game(code)
    player_id = data.get("player_id")
    trap_text = data.get("trap_text")
    
    if not game: raise HTTPException(status_code=404, detail="Game not found")

    current_round = game.rounds[game.current_round_idx]
    current_round.trap_proposals[player_id] = trap_text

    # Generate trap image with round's style theme
    themed_prompt = apply_style_theme(trap_text, current_round.style_theme)
    img_url = generate_image_fal(themed_prompt)
    if img_url: current_round.trap_images[player_id] = img_url
        
    alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
    if len(current_round.trap_proposals) >= len(alive_players):
        current_round.status = "trap_voting"

    save_game(game)
    return {"status": "trap_submitted"}

@web_app.post("/api/vote_trap")
async def api_vote_trap(request: Request):
    code = request.query_params.get("code")
    data = await request.json()
    game = get_game(code)
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")
    
    if not game: raise HTTPException(status_code=404, detail="Game not found")
    
    current_round = game.rounds[game.current_round_idx]
    current_round.votes[voter_id] = target_id

    alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
    if len(current_round.votes) >= len(alive_players):
        vote_counts = {}
        for target in current_round.votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1
        winner_id = max(vote_counts, key=vote_counts.get)
        winning_trap = current_round.trap_proposals[winner_id]
        winning_image = current_round.trap_images.get(winner_id)
        
        current_round.scenario_text = winning_trap
        current_round.scenario_image_url = winning_image
        current_round.architect_id = winner_id
        current_round.status = "strategy"
        current_round.submission_start_time = time.time()  # Start timer for strategy
        if winner_id in game.players: game.players[winner_id].score += 500

    save_game(game)
    return {"status": "voted"}


@web_app.post("/api/vote_coop")
async def api_vote_coop(request: Request):
    """Handle cooperative round voting - vote for which strategy image looks best."""
    code = request.query_params.get("code")
    data = await request.json()
    game = get_game(code)
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Prevent voting for self
    if voter_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot vote for yourself")

    current_round = game.rounds[game.current_round_idx]

    # Validate we're in coop_voting phase
    if current_round.status != "coop_voting":
        raise HTTPException(status_code=400, detail=f"Wrong phase: {current_round.status}")

    current_round.coop_votes[voter_id] = target_id
    print(f"COOP VOTE: {voter_id} voted for {target_id}", flush=True)

    # Check if all alive players in lobby have voted
    alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
    if len(current_round.coop_votes) >= len(alive_players):
        print("COOP VOTE: All votes in, tallying...", flush=True)
        # Tally votes and transition to coop_judgement
        tally_coop_votes_and_transition(game, current_round)
        save_game(game)
        # Spawn async team judgement
        run_coop_judgement.spawn(code)
    else:
        save_game(game)

    return {"status": "voted"}


@web_app.post("/api/next_round")
async def api_next_round(request: Request):
    code = request.query_params.get("code")
    game = get_game(code)
    if not game: raise HTTPException(status_code=404, detail="Game not found")

    next_idx = game.current_round_idx + 1
    if next_idx >= game.max_rounds:
        game.status = "finished"
        # Find winner and set initial video status
        sorted_players = sorted(game.players.values(), key=lambda p: p.score, reverse=True)
        if sorted_players:
            game.winner_id = sorted_players[0].id
            game.videos_status = "generating"
        save_game(game)
        # Spawn async video generation for ALL players
        print(f"API: Game finished, spawning video generation for all players in {code}", flush=True)
        generate_all_player_videos.spawn(code)
        return {"status": "finished"}

    game.current_round_idx = next_idx

    # Use round_config to determine round type (flexible positioning)
    if next_idx < len(game.round_config):
        round_type = game.round_config[next_idx]
    else:
        # Fallback: last round is blind_architect
        round_type = "blind_architect" if (next_idx + 1) == game.max_rounds else "survival"

    new_round = Round(number=next_idx + 1, type=round_type)
    # Force anime style for last_stand (Evil Santa) rounds
    if round_type == "last_stand":
        new_round.style_theme = "anime, evil Christmas, dramatic lighting"
    else:
        new_round.style_theme = random.choice(IMAGE_STYLE_THEMES)
    new_round.system_message = get_system_message(next_idx + 1, game.max_rounds, round_type)
    game.rounds.append(new_round)

    # Resurrect all players for the new round (Points matter, death is temporary)
    for p in game.players.values():
        p.is_alive = True
        p.death_reason = None
        p.survival_reason = None
        p.strategy = None  # Clear previous strategy
        p.result_image_url = None
        p.judgement_pending = False  # Clear any pending judgement flags

    if round_type == "blind_architect":
        new_round.status = "trap_creation"
        new_round.scenario_text = "ARCHITECT MODE: Design a deadly scenario for your opponents."
        new_round.submission_start_time = time.time()  # Start timer for trap creation
    elif round_type == "sacrifice":
        new_round.status = "sacrifice_volunteer"
        new_round.scenario_text = "SACRIFICE PROTOCOL: One must fall for others to survive. Who will volunteer as tribute?"
    else:
        # survival, cooperative, and last_stand start with strategy phase
        new_round.status = "strategy"
        new_round.submission_start_time = time.time()  # Start timer for strategy
        # Use pre-warmed scenario if available
        if game.prewarmed_scenarios and next_idx < len(game.prewarmed_scenarios) and game.prewarmed_scenarios[next_idx]:
            new_round.scenario_text = game.prewarmed_scenarios[next_idx]
            print(f"API: Using pre-warmed scenario for round {next_idx + 1}", flush=True)
        else:
            print(f"API: No pre-warmed scenario for round {next_idx + 1}, generating on-demand...", flush=True)
            new_round.scenario_text = generate_scenario_llm(next_idx + 1, game.max_rounds)

    save_game(game)
    return {"status": "started_round", "round": next_idx + 1, "type": round_type}

@web_app.post("/api/retry_player_videos")
async def api_retry_player_videos(request: Request):
    """Retry generating player videos if they failed."""
    code = request.query_params.get("code")
    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != "finished":
        raise HTTPException(status_code=400, detail="Game not finished")

    if game.videos_status == "generating":
        return {"status": "already_generating"}

    # Reset status and spawn new generation
    game.videos_status = "generating"
    game.player_videos = {}  # Clear any partial results
    save_game(game)
    print(f"API: Retrying player video generation for {code}", flush=True)
    generate_all_player_videos.spawn(code)
    return {"status": "retry_started"}


@web_app.post("/api/regenerate_character_image")
async def api_regenerate_character_image(request: Request):
    """Regenerate a player's character avatar with a new random style."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != "lobby":
        raise HTTPException(status_code=400, detail="Can only regenerate in lobby")

    if player_id not in game.players:
        raise HTTPException(status_code=404, detail="Player not found")

    player = game.players[player_id]
    if not player.character_description:
        raise HTTPException(status_code=400, detail="No character description to regenerate from")

    # Clear current image and spawn new generation
    player.character_image_url = None
    save_game(game)

    print(f"API: Regenerating character image for {player.name}", flush=True)
    generate_character_image.spawn(code, player_id, player.character_description)

    return {"status": "regenerating"}


@web_app.post("/api/generate_random_characters")
async def api_generate_random_characters(request: Request):
    """Generate 8 random diverse character images for the player to choose from."""
    import asyncio
    import httpx

    # Generate 8 unique random trait sets with different seeds
    base_seed = int(time.time() * 1000)
    characters = []
    for i in range(8):
        traits = generate_random_character_traits(seed=base_seed + i)
        prompt = build_character_prompt_from_traits(traits)
        characters.append({"traits": traits, "prompt": prompt})

    print("RANDOM CHARS: Generating 8 random characters...", flush=True)
    for i, c in enumerate(characters):
        print(f"  [{i}] {c['traits']['look'][:50]}...", flush=True)

    async def generate_single_image(char_data: dict, idx: int) -> dict:
        """Generate a single character image."""
        url = "https://fal.run/fal-ai/flux/krea"
        headers = {
            "Authorization": f"Key {os.environ['FAL_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": char_data["prompt"],
            "image_size": "square",
            "num_inference_steps": 28
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                image_url = response.json()["images"][0]["url"]
                return {
                    "traits": char_data["traits"],
                    "prompt": char_data["prompt"],
                    "url": image_url
                }
        except Exception as e:
            print(f"Random char generation error: {e}", flush=True)
            return {
                "traits": char_data["traits"],
                "prompt": char_data["prompt"],
                "url": None
            }

    # Generate all 8 images in parallel
    tasks = [generate_single_image(c, i) for i, c in enumerate(characters)]
    results = await asyncio.gather(*tasks)

    # Filter out any failed generations
    successful = [r for r in results if r["url"] is not None]
    print(f"RANDOM CHARS: Generated {len(successful)}/8 images successfully", flush=True)

    return {"characters": successful}


# --- SACRIFICE ROUND ENDPOINTS ---

@web_app.post("/api/volunteer_sacrifice")
async def api_volunteer_sacrifice(request: Request):
    """Player volunteers as tribute for the sacrifice round."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if player_id not in game.players:
        raise HTTPException(status_code=404, detail="Player not found")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "sacrifice" or current_round.status != "sacrifice_volunteer":
        raise HTTPException(status_code=400, detail="Not in sacrifice volunteer phase")

    # Mark player as volunteer
    current_round.sacrifice_volunteers[player_id] = True
    save_game(game)

    player = game.players[player_id]
    print(f"SACRIFICE: {player.name} volunteered as tribute!", flush=True)
    return {"status": "volunteered", "volunteer_count": len(current_round.sacrifice_volunteers)}


@web_app.post("/api/advance_sacrifice_volunteer")
async def api_advance_sacrifice_volunteer(request: Request):
    """Admin advances from volunteer phase to voting phase."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if player_id not in game.players or not game.players[player_id].is_admin:
        raise HTTPException(status_code=403, detail="Only admin can advance")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "sacrifice" or current_round.status != "sacrifice_volunteer":
        raise HTTPException(status_code=400, detail="Not in sacrifice volunteer phase")

    # Advance to voting phase
    current_round.status = "sacrifice_voting"
    save_game(game)

    volunteer_count = len(current_round.sacrifice_volunteers)
    print(f"SACRIFICE: Advanced to voting with {volunteer_count} volunteers", flush=True)
    return {"status": "advanced", "volunteer_count": volunteer_count}


@web_app.post("/api/vote_sacrifice")
async def api_vote_sacrifice(request: Request):
    """Vote for who becomes the martyr."""
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "sacrifice" or current_round.status != "sacrifice_voting":
        raise HTTPException(status_code=400, detail="Not in sacrifice voting phase")

    if voter_id not in game.players:
        raise HTTPException(status_code=404, detail="Voter not found")

    if target_id not in game.players:
        raise HTTPException(status_code=404, detail="Target not found")

    # Can't vote for yourself
    if voter_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot vote for yourself")

    # If there are volunteers, can only vote for volunteers
    # If no volunteers, can vote for anyone
    if current_round.sacrifice_volunteers and target_id not in current_round.sacrifice_volunteers:
        raise HTTPException(status_code=400, detail="Can only vote for volunteers")

    current_round.sacrifice_votes[voter_id] = target_id
    save_game(game)

    # Check if all players have voted
    active_players = [p for p in game.players.values() if p.is_alive]
    all_voted = len(current_round.sacrifice_votes) >= len(active_players)

    if all_voted:
        # Tally votes and determine martyr
        vote_counts = {}
        for target in current_round.sacrifice_votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1

        # Find the player with most votes (ties broken by first encountered)
        martyr_id = max(vote_counts, key=vote_counts.get)
        current_round.martyr_id = martyr_id
        current_round.status = "sacrifice_submission"
        current_round.submission_start_time = time.time()  # Start timer for sacrifice speech
        save_game(game)

        martyr_name = game.players[martyr_id].name
        print(f"SACRIFICE: {martyr_name} chosen as martyr with {vote_counts[martyr_id]} votes", flush=True)
        return {"status": "martyr_chosen", "martyr_id": martyr_id}

    return {"status": "vote_recorded", "votes_cast": len(current_round.sacrifice_votes)}


@web_app.post("/api/submit_sacrifice_speech")
async def api_submit_sacrifice_speech(request: Request):
    """Martyr submits their heroic death speech."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")
    speech = data.get("speech", "")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "sacrifice" or current_round.status != "sacrifice_submission":
        raise HTTPException(status_code=400, detail="Not in sacrifice submission phase")

    if player_id != current_round.martyr_id:
        raise HTTPException(status_code=403, detail="Only the chosen martyr can submit")

    if not speech.strip():
        raise HTTPException(status_code=400, detail="Speech cannot be empty")

    current_round.martyr_speech = speech
    current_round.status = "sacrifice_judgement"
    save_game(game)

    martyr_name = game.players[player_id].name
    print(f"SACRIFICE: {martyr_name} submitted death speech, spawning judgement", flush=True)

    # Spawn async judgement
    run_sacrifice_judgement.spawn(code)

    return {"status": "speech_submitted"}


# --- LAST STAND REVIVAL ENDPOINTS ---

@web_app.post("/api/vote_revival")
async def api_vote_revival(request: Request):
    """Survivor votes to revive a dead player (must be unanimous)."""
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "last_stand" or current_round.status != "last_stand_revival":
        raise HTTPException(status_code=400, detail="Not in revival voting phase")

    if voter_id not in game.players:
        raise HTTPException(status_code=404, detail="Voter not found")

    voter = game.players[voter_id]
    if not voter.is_alive:
        raise HTTPException(status_code=400, detail="Only survivors can vote")

    if target_id not in game.players:
        raise HTTPException(status_code=404, detail="Target not found")

    target = game.players[target_id]
    if target.is_alive:
        raise HTTPException(status_code=400, detail="Can only vote for dead players")

    current_round.revival_votes[voter_id] = target_id
    save_game(game)

    # Check if all survivors have voted
    survivors = [p for p in game.players.values() if p.is_alive]
    all_voted = len(current_round.revival_votes) >= len(survivors)

    print(f"REVIVAL: {voter.name} voted for {target.name}. {len(current_round.revival_votes)}/{len(survivors)} voted", flush=True)

    return {"status": "vote_recorded", "votes_cast": len(current_round.revival_votes), "survivors": len(survivors)}


@web_app.post("/api/advance_revival")
async def api_advance_revival(request: Request):
    """Admin advances from revival phase (checks for unanimous vote)."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if player_id not in game.players or not game.players[player_id].is_admin:
        raise HTTPException(status_code=403, detail="Only admin can advance")

    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "last_stand" or current_round.status != "last_stand_revival":
        raise HTTPException(status_code=400, detail="Not in revival phase")

    # Check for unanimous vote
    survivors = [p for p in game.players.values() if p.is_alive]
    if not survivors:
        # No survivors, skip to results
        current_round.status = "results"
        save_game(game)
        return {"status": "no_survivors", "revived": False}

    votes = list(current_round.revival_votes.values())
    if not votes:
        # No votes cast, skip revival
        current_round.status = "results"
        save_game(game)
        print("REVIVAL: No votes cast, skipping revival", flush=True)
        return {"status": "no_votes", "revived": False}

    # Check if unanimous
    unique_targets = set(votes)
    if len(unique_targets) == 1 and len(votes) == len(survivors):
        # Unanimous! Spawn revival judgement
        revived_id = votes[0]
        current_round.revived_player_id = revived_id
        current_round.status = "revival_judgement"
        save_game(game)

        revived_name = game.players[revived_id].name
        print(f"REVIVAL: Unanimous vote for {revived_name}! Spawning revival judgement", flush=True)
        run_revival_judgement.spawn(code)
        return {"status": "unanimous", "revived": True, "revived_player_id": revived_id}
    else:
        # Not unanimous, skip revival
        current_round.status = "results"
        save_game(game)
        print(f"REVIVAL: Not unanimous ({len(unique_targets)} different targets), no revival", flush=True)
        return {"status": "not_unanimous", "revived": False}


# --- SACRIFICE JUDGEMENT ASYNC FUNCTION ---

@app.function(image=image, secrets=secrets)
def run_sacrifice_judgement(game_code: str):
    """Judge the martyr's death - was it epic or lame?"""
    import json
    import asyncio

    async def judge_sacrifice():
        game = get_game(game_code)
        if not game:
            print(f"SACRIFICE JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        martyr_id = current_round.martyr_id
        martyr = game.players[martyr_id]
        speech = current_round.martyr_speech

        print(f"SACRIFICE JUDGEMENT: Judging {martyr.name}'s death speech", flush=True)

        # Call LLM to judge the sacrifice
        try:
            result_json = await judge_sacrifice_llm_async(speech, martyr.name)
            res = json.loads(result_json)
            epic = res.get("epic", False)
            reason = res.get("reason", "The judges deliberated...")
            visual_prompt = res.get("visual_prompt", "A dramatic death scene")
        except Exception as e:
            print(f"SACRIFICE JUDGEMENT: Error: {e}", flush=True)
            epic = False
            reason = "The simulation glitched during judgement..."
            visual_prompt = "A figure fading into digital static"

        # Generate image
        themed_prompt = apply_style_theme(visual_prompt, current_round.style_theme)
        image_url = await generate_image_fal_async(themed_prompt)

        # Store results
        current_round.martyr_epic = epic
        current_round.martyr_reason = reason
        current_round.martyr_image_url = image_url

        # Apply consequences
        martyr.is_alive = False
        martyr.death_reason = reason
        martyr.result_image_url = image_url

        if epic:
            # Epic death: Martyr +500, all others survive and get +100
            martyr.score += 500
            for pid, p in game.players.items():
                if pid != martyr_id and p.is_alive:
                    p.score += 100
                    p.survival_reason = f"Saved by {martyr.name}'s heroic sacrifice"
            print(f"SACRIFICE JUDGEMENT: EPIC! {martyr.name} +500, others +100", flush=True)
        else:
            # Lame death: Everyone dies, no points
            for pid, p in game.players.items():
                p.is_alive = False
                if pid == martyr_id:
                    p.death_reason = reason
                else:
                    p.death_reason = f"{martyr.name}'s pathetic sacrifice failed to save anyone"
            print(f"SACRIFICE JUDGEMENT: LAME! Everyone dies", flush=True)

        current_round.status = "results"
        save_game(game)
        print(f"SACRIFICE JUDGEMENT: Complete!", flush=True)

    asyncio.run(judge_sacrifice())


async def judge_sacrifice_llm_async(speech: str, martyr_name: str):
    """Judge how epic the martyr's death was."""
    import re
    import httpx

    prompt = f"""You are judging a HEROIC SACRIFICE in a survival game.

The player "{martyr_name}" chose to die so others could survive.
Their final words/actions: {speech}

Judge how EPIC this death was based on:
- Creativity and originality
- Drama and entertainment value
- Commitment to the bit
- Actually sounds like a heroic sacrifice

Be generous but not a pushover - if it's clearly lazy or doesn't make sense as a sacrifice, call it out.

IMPORTANT: Keep "reason" SHORT (1-2 sentences, under 30 words).

JSON only, no markdown:
{{"epic": true/false, "reason": "why this death was epic/lame", "visual_prompt": "dramatic scene for image"}}"""

    try:
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("sacrifice_judgement"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

        # Extract JSON
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        json_obj_match = re.search(r'\{[\s\S]*\}', content)
        if json_obj_match:
            content = json_obj_match.group(0)

        return content.strip()
    except Exception as e:
        print(f"SACRIFICE LLM Error: {e}", flush=True)
        return '{"epic": false, "reason": "System error during judgement", "visual_prompt": "A figure dissolving into static"}'


# --- LAST STAND HARSH JUDGEMENT ---

@app.function(image=image, secrets=secrets)
def run_last_stand_judgement(game_code: str):
    """Run HARSH judgement for Last Stand round - only ~20-30% should survive."""
    import json
    import asyncio

    async def judge_and_generate_harsh(pid: str, player_name: str, strategy: str, scenario: str, style_theme: str | None):
        """Judge with extra harshness for Last Stand."""
        try:
            result_json = await judge_strategy_harsh_async(scenario, strategy)
            res = json.loads(result_json)
            survived = res.get("survived", False)
            reason = res.get("reason", "Unknown")
            vis_prompt = res.get("visual_prompt", "A generic scene.")

            themed_prompt = apply_style_theme(vis_prompt, style_theme)
            image_url = await generate_image_fal_async(themed_prompt)

            return {
                "pid": pid,
                "survived": survived,
                "reason": reason,
                "image_url": image_url
            }
        except Exception as e:
            print(f"LAST STAND JUDGEMENT: Error for {pid}: {e}", flush=True)
            return {
                "pid": pid,
                "survived": False,
                "reason": "The final boss showed no mercy...",
                "image_url": None
            }

    async def run_all_judgements():
        print(f"LAST STAND JUDGEMENT: Starting for game {game_code}", flush=True)

        game = get_game(game_code)
        if not game:
            print(f"LAST STAND JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]

        # Collect all players that need judging
        tasks = []
        for pid, p in game.players.items():
            if p.strategy and p.is_alive:
                tasks.append(judge_and_generate_harsh(pid, p.name, p.strategy, current_round.scenario_text, current_round.style_theme))

        if tasks:
            print(f"LAST STAND JUDGEMENT: Running {len(tasks)} harsh judgements in parallel...", flush=True)
            results = await asyncio.gather(*tasks)

            for result in results:
                pid = result["pid"]
                p = game.players[pid]
                p.is_alive = result["survived"]
                if not result["survived"]:
                    p.death_reason = result["reason"]
                    p.survival_reason = None
                else:
                    p.score += 100
                    p.survival_reason = result["reason"]
                    p.death_reason = None
                if result["image_url"]:
                    p.result_image_url = result["image_url"]
                print(f"LAST STAND: {p.name} survived={result['survived']}", flush=True)

        # Check if we need revival phase
        survivors = [p for p in game.players.values() if p.is_alive]
        dead_players = [p for p in game.players.values() if not p.is_alive]

        if survivors and dead_players:
            # Go to revival phase
            current_round.status = "last_stand_revival"
            print(f"LAST STAND: {len(survivors)} survivors, {len(dead_players)} dead - entering revival phase", flush=True)
        else:
            # Skip revival - either everyone survived or everyone died
            current_round.status = "results"
            print(f"LAST STAND: Skipping revival (survivors={len(survivors)}, dead={len(dead_players)})", flush=True)

        save_game(game)
        print(f"LAST STAND JUDGEMENT: Complete!", flush=True)

    asyncio.run(run_all_judgements())


async def judge_strategy_harsh_async(scenario: str, strategy: str):
    """HARSH version of judgement for Last Stand - EVIL SANTA edition."""
    import re
    import httpx

    prompt = f"""You are EVIL SANTA, a cartoonishly villainous anime-inspired final boss.
You speak in third person with dramatic flair. You make twisted holiday puns. Be BRUTAL.

SCENARIO: {scenario}

STRATEGY: {strategy}

EVIL SANTA'S RULES FOR JUDGEMENT:
- Only ~20-30% of strategies should survive - Santa is VERY harsh with naughty children
- Look for ANY flaw, ANY weakness in their plan - Santa sees EVERYTHING
- Generic strategies automatically fail - "HO HO HO! How BORING!"
- Only truly exceptional, creative strategies survive - impress Evil Santa
- This is the ultimate test - mediocre = NAUGHTY LIST

Evil Santa finds creative ways to punish failures:
- "Santa KNOWS you didn't think this through!"
- "That's going on the NAUGHTY LIST forever!"
- "HO HO HO! Santa's demon elves will deal with you!"
- "You thought THAT would work against SANTA?!"

For survivors, be grudgingly impressed:
- "Hmph... Santa admits that was... clever."
- "You escape Santa's bag... THIS time."
- "The Nice List... barely."

IMPORTANT: Keep "reason" SHORT (1-2 sentences, under 30 words). Write in Evil Santa's voice with holiday puns.
Visual prompts should feature Evil Santa, demon elves, twisted Christmas imagery, anime villain aesthetic.

JSON only, no markdown:
{{"survived": true/false, "reason": "Evil Santa's judgement in his voice", "visual_prompt": "anime evil santa scene"}}"""

    try:
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("last_stand_judgement"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        json_obj_match = re.search(r'\{[\s\S]*\}', content)
        if json_obj_match:
            content = json_obj_match.group(0)

        return content.strip()
    except Exception as e:
        print(f"HARSH JUDGEMENT LLM Error: {e}", flush=True)
        return '{"survived": false, "reason": "HO HO HO! The demon elves drag you into the NAUGHTY FOREVER pit!", "visual_prompt": "Anime evil Santa cackling as demon elves drag victim into fiery pit"}'


# --- REVIVAL JUDGEMENT ---

@app.function(image=image, secrets=secrets)
def run_revival_judgement(game_code: str):
    """Re-judge the revived player with a bonus for teamwork."""
    import json
    import asyncio

    async def do_revival_judgement():
        game = get_game(game_code)
        if not game:
            print(f"REVIVAL JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        revived_id = current_round.revived_player_id
        revived = game.players[revived_id]

        print(f"REVIVAL JUDGEMENT: Re-judging {revived.name} with teamwork bonus", flush=True)

        # Re-judge with bonus
        try:
            result_json = await judge_strategy_revival_async(
                current_round.scenario_text,
                revived.strategy,
                revived.name
            )
            res = json.loads(result_json)
            survived = res.get("survived", False)
            reason = res.get("reason", "Unknown")
            vis_prompt = res.get("visual_prompt", "A scene of redemption")
        except Exception as e:
            print(f"REVIVAL JUDGEMENT: Error: {e}", flush=True)
            survived = False
            reason = "The revival failed..."
            vis_prompt = "A figure fading away again"

        # Generate new image
        themed_prompt = apply_style_theme(vis_prompt, current_round.style_theme)
        image_url = await generate_image_fal_async(themed_prompt)

        # Store revival results
        current_round.revival_survived = survived
        current_round.revival_reason = reason
        current_round.revival_image_url = image_url

        # Update player state
        revived.is_alive = survived
        if survived:
            revived.survival_reason = reason
            revived.death_reason = None
            revived.score += 100
            print(f"REVIVAL: {revived.name} SURVIVED their second chance!", flush=True)
        else:
            revived.death_reason = reason
            revived.survival_reason = None
            print(f"REVIVAL: {revived.name} failed their second chance", flush=True)
        revived.result_image_url = image_url

        current_round.status = "results"
        save_game(game)
        print(f"REVIVAL JUDGEMENT: Complete!", flush=True)

    asyncio.run(do_revival_judgement())


async def judge_strategy_revival_async(scenario: str, strategy: str, player_name: str):
    """Judge with slight leniency for revived player - EVIL SANTA edition."""
    import re
    import httpx

    prompt = f"""You are EVIL SANTA, but you're annoyed because the other survivors are begging you to spare someone.

{player_name} originally died, but their surviving friends UNANIMOUSLY asked Santa for a second chance.
Evil Santa HATES the power of friendship, but even he must honor unanimous requests... grudgingly.

SCENARIO: {scenario}

STRATEGY: {strategy}

EVIL SANTA'S GRUDGING RE-EVALUATION:
- Be slightly more lenient than normal (you HATE doing this)
- The survivors' faith in this player forces Santa to give them +20% better odds (grumble grumble)
- Still needs to be a decent strategy - "Santa's mercy has LIMITS!"
- If the strategy was truly awful, even friendship can't save them - "HO HO HO! Nice try!"

If they survive (grudgingly):
- "BAH! Santa SUPPOSES they can stay on the Nice List... for now."
- "Their friends' pleading has SOFTENED Santa's cold heart... temporarily!"

If they die again:
- "HO HO HO! Friendship couldn't save THIS one! Back to the coal mines!"
- "Santa gave you a chance and you WASTED it! NAUGHTY FOREVER!"

IMPORTANT: Keep "reason" SHORT (1-2 sentences, under 30 words). Use Evil Santa's voice.
Visual prompts should feature Evil Santa, anime style, twisted Christmas imagery.

JSON only, no markdown:
{{"survived": true/false, "reason": "Evil Santa's grudging judgement in his voice", "visual_prompt": "anime evil santa scene"}}"""

    try:
        timeout = CONFIG["llm"]["default_timeout_seconds"]
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": get_model("revival_judgement"),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        json_obj_match = re.search(r'\{[\s\S]*\}', content)
        if json_obj_match:
            content = json_obj_match.group(0)

        return content.strip()
    except Exception as e:
        print(f"REVIVAL LLM Error: {e}", flush=True)
        return '{"survived": false, "reason": "HO HO HO! Even friendship could not save this one from the coal mines!", "visual_prompt": "Anime evil Santa laughing as figure falls into pit of coal"}'


# Mount static files (Frontend)
# We expect 'frontend/dist' to be available. We need to Mount it in the App definition.
assets_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")

# We serve the React app. For SPA, we need to catch 404s and return index.html? 
# Or just serve static assets and root.
web_app.mount("/", StaticFiles(directory="/assets", html=True, check_dir=False), name="static")

@app.function(
    image=image, 
    secrets=secrets
)
@modal.asgi_app(label="mas-ai-game")
def fastapi_app():
    return web_app


