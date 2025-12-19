import os

# Enforce the 'ai-game' environment
os.environ["MODAL_ENVIRONMENT"] = "ai-game"

import asyncio
import modal
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal
import time
import uuid
import random

import prompts

# --- Input Validation Constants ---
MAX_STRATEGY_LENGTH = 2000
MAX_TRAP_TEXT_LENGTH = 1000
MAX_SPEECH_LENGTH = 2000
MAX_NAME_LENGTH = 50
MAX_CHARACTER_DESCRIPTION_LENGTH = 500

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
    "medieval manuscript illumination, gold leaf, ornate borders, flat perspective",
    "noir detective style, black and white, dramatic shadows, venetian blinds",
]

# --- Random Character Generation Traits ---
# Aligned with the 5 character fields: look, weapon, talent, flaw, catchphrase

# Split into gendered humanoid looks (50/50) and non-human looks
FEMALE_LOOKS = [
    "wild purple hair, leather jacket, mysterious scar across eye",
    "buff grandma energy, knitting needles tucked behind ear",
    "goth pixie with too many piercings to count",
    "cyberpunk vampire queen with RGB fangs",
    "sleepy witch who hasn't slept since the 1400s",
    "aggressively cheerful clown (not evil, just intense)",
    "discount store superheroine with a bedsheet cape",
    "Victorian ghost lady who refuses to update her wardrobe",
    "time-displaced lady knight confused by everything",
    "wholesome orc grandmother with reading glasses",
    "conspiracy theorist woman with tinfoil fashion sense",
    "ex-villainess trying to rebrand as an influencer",
    "sorceress who got her degree online",
    "anime heroine refusing to acknowledge she's a side character",
    "interdimensional tourist woman with too many cameras",
    "retired goddess working retail",
    "fierce warrior queen with battle-worn armor",
    "punk rock girl with neon mohawk and chains",
    "mysterious femme fatale in a trenchcoat",
    "cheerful space pirate captain with an eyepatch",
    "brooding necromancer lady who only wears black",
    "chaotic scientist woman with wild hair and goggles",
    "stoic samurai woman with a haunted past",
    "bubbly pop star undercover as a normal person",
    "grumpy librarian witch who's seen too much",
]

MALE_LOOKS = [
    "wild purple hair, leather jacket, mysterious scar across eye",
    "suspiciously normal accountant vibes, but with glowing red eyes",
    "grizzled old man with an impressive beard and secrets",
    "cyberpunk vampire lord with RGB fangs",
    "sleepy wizard who hasn't slept since the 1400s",
    "aggressively cheerful clown (not evil, just intense)",
    "discount store superhero with a bedsheet cape",
    "Victorian ghost gentleman who refuses to update his wardrobe",
    "time-displaced knight confused by everything",
    "conspiracy theorist guy with tinfoil fashion sense",
    "ex-villain trying to rebrand as an influencer",
    "wizard who got his degree online",
    "anime protagonist refusing to acknowledge he's a side character",
    "interdimensional tourist man with too many cameras",
    "retired god working retail",
    "buff barbarian with more muscles than sense",
    "punk rock guy with neon mohawk and chains",
    "mysterious man in a trenchcoat (definitely not three kids)",
    "cheerful space pirate captain with an eyepatch",
    "brooding necromancer who only wears black",
    "chaotic scientist with wild hair and goggles",
    "stoic samurai with a haunted past",
    "washed-up rockstar trying to make a comeback",
    "grumpy wizard who's had it with adventurers",
    "nervous accountant with a dark secret",
]

NON_HUMAN_LOOKS = [
    "sentient pile of moss wearing a tiny top hat",
    "floating head with a magnificent mustache",
    "skeleton in a business casual polo shirt",
    "three raccoons in a trenchcoat (poorly disguised)",
    "sentient vending machine with trust issues",
    "extremely buff corgi standing on hind legs",
    "eldritch horror trying to blend in at a coffee shop",
    "robot learning human emotions (badly)",
    "mushroom person who is always slightly damp",
    "goblin CEO in an ill-fitting suit",
    "ghost of someone who died from embarrassment",
    "cat that learned to walk upright and won't stop judging",
    "person who is clearly two kids stacked in adult clothes",
    "sentient cloud of anxiety with googly eyes",
    "a very polite demon just trying to do their job",
    "interdimensional slime creature in business attire",
    "possessed teddy bear with glowing button eyes",
    "time-traveling dinosaur in a tiny hat",
    "friendly eldritch tentacle monster with glasses",
    "a literal trash panda (raccoon) in formal wear",
]

# Combined for backwards compatibility (weighted 40% female, 40% male, 20% non-human)
RANDOM_LOOKS = FEMALE_LOOKS + MALE_LOOKS + NON_HUMAN_LOOKS

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
    "tarot card mystical art nouveau",
    "noir detective dramatic shadows",
]


def generate_random_character_traits(seed: int = None) -> dict:
    """Generate random character traits matching the 5 character fields.

    Gender distribution: 40% female humanoid, 40% male humanoid, 20% non-human.
    This ensures a balanced 50/50 male/female split among humanoid characters.
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    # Pick character type: 40% female, 40% male, 20% non-human
    # This gives 50/50 male/female among humanoids
    roll = rng.random()
    if roll < 0.4:
        look = rng.choice(FEMALE_LOOKS)
    elif roll < 0.8:
        look = rng.choice(MALE_LOOKS)
    else:
        look = rng.choice(NON_HUMAN_LOOKS)

    traits = {
        "look": look,
        "weapon": rng.choice(RANDOM_WEAPONS),
        "talent": rng.choice(RANDOM_TALENTS),
        "flaw": rng.choice(RANDOM_FLAWS),
        "catchphrase": rng.choice(RANDOM_CATCHPHRASES),
    }
    return traits


def build_character_prompt_from_traits(traits: dict) -> str:
    """Build a character image prompt from the 5 traits."""
    art_style = random.choice(RANDOM_ART_STYLES)
    return prompts.format_prompt(
        prompts.CHARACTER_SIMPLE,
        look=traits['look'],
        weapon=traits['weapon'],
        art_style=art_style
    )


def apply_style_theme(prompt: str, style_theme: str | None) -> str:
    """Append the round's style theme to an image prompt for visual consistency."""
    if style_theme:
        return f"{prompt}, in the style of {style_theme}"
    return prompt


def calculate_ranked_points(num_players: int, rank: int) -> int:
    """Award points by rank position in ranked rounds. Only rank 1 survives and gets points."""
    if rank == 1:
        # Winner gets survival points - scales slightly with competition
        if num_players >= 4:
            return 300
        elif num_players == 3:
            return 250
        else:  # 2 players
            return 200
    else:
        # Everyone else dies with no points
        return 0


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
).add_local_file("config.yaml", remote_path="/config.yaml"
).add_local_file("backend/prompts.py", remote_path="/root/prompts.py")

app = modal.App("survaive", image=image)


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


def get_round_config() -> list[str]:
    """Get the round configuration list."""
    return CONFIG.get("rounds", {}).get("config", ["survival", "survival", "cooperative", "sacrifice", "last_stand"])


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

    prompt = prompts.format_prompt(
        prompts.SCENARIO_GENERATION,
        round_num=round_num,
        max_rounds=max_rounds
    )

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
        return prompts.FALLBACK_SCENARIO


async def generate_last_stand_scenario_async():
    """Generate the EVIL SANTA final boss scenario."""
    import httpx

    prompt = prompts.LAST_STAND_SCENARIO

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
        return prompts.FALLBACK_LAST_STAND_SCENARIO


async def generate_scenario_llm_async(round_num: int, max_rounds: int = 5):
    """Async version of generate_scenario_llm for parallel pre-warming."""
    import httpx

    prompt = prompts.format_prompt(
        prompts.SCENARIO_GENERATION,
        round_num=round_num,
        max_rounds=max_rounds
    )

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
        return prompts.FALLBACK_SCENARIO


async def judge_strategy_llm_async(scenario: str, strategy: str):
    """Async version of judge_strategy_llm for parallel execution with simulation flavor."""
    import re
    import httpx

    prompt = prompts.format_prompt(
        prompts.STRATEGY_JUDGEMENT,
        scenario=scenario,
        strategy=strategy
    )
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
        return prompts.FALLBACK_STRATEGY_JUDGEMENT


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

    prompt = prompts.format_prompt(
        prompts.RANKED_JUDGEMENT,
        scenario=scenario,
        strategy_list=strategy_list,
        num_strategies=len(strategies)
    )

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
                 "commentary": prompts.FALLBACK_RANKED_COMMENTARY,
                 "visual_prompt": prompts.FALLBACK_RANKED_VISUAL}
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

    # Build a rich prompt that shows the character in an action scene with all their traits
    full_character_prompt = prompts.format_prompt(
        prompts.CHARACTER_IMAGE,
        random_look=random_look,
        character_prompt=character_prompt,
        random_moment=random_moment
    )

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
    prompt = prompts.format_prompt(
        prompts.STRATEGY_JUDGEMENT,
        scenario=scenario,
        strategy=strategy
    )
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
        return prompts.FALLBACK_STRATEGY_JUDGEMENT


async def repair_json_with_llm(malformed_json: str, player_name: str) -> dict | None:
    """Use Kimi K2 to repair malformed JSON from video script generation."""
    import httpx
    import json
    import re

    repair_prompt = f"""Fix this malformed JSON. It has invalid control characters or syntax errors.
Do not change the content/meaning, just fix the JSON syntax (escape special characters, fix quotes, etc).

Malformed JSON:
{malformed_json}

IMPORTANT: Output ONLY the corrected valid JSON object. No explanation, no markdown, no code blocks - just the raw JSON."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CONFIG['llm']['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshotai/kimi-k2-0905",
                    "messages": [{"role": "user", "content": repair_prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group(0))
                print(f"JSON REPAIR [{player_name}]: Successfully repaired JSON", flush=True)
                return result
    except Exception as e:
        print(f"JSON REPAIR [{player_name}]: Repair failed: {e}", flush=True)

    return None


async def parse_json_with_repair(json_str: str, player_name: str) -> dict | None:
    """Try to parse JSON, repair with LLM if invalid."""
    import json

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON PARSE [{player_name}]: Invalid JSON, attempting repair: {e}", flush=True)

    return await repair_json_with_llm(json_str, player_name)


async def generate_video_prompt_llm_async(player_name: str, rank: int, total_players: int, score: int, video_theme: str):
    """Use a fast LLM to generate personalized video scene and dialogue with simulation narrative."""
    import httpx
    import json
    import re

    is_winner = rank == 1
    is_last = rank == total_players

    # Build context and tone using helper
    context, tone = prompts.build_video_context(player_name, rank, total_players, score)

    prompt = prompts.format_prompt(
        prompts.VIDEO_SCRIPT_GENERATION,
        video_theme=video_theme,
        context=context,
        player_name=player_name,
        tone=tone
    )

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
                result = await parse_json_with_repair(json_match.group(0), player_name)
                if result:
                    print(f"VIDEO PROMPT LLM: Generated for {player_name}: {result}", flush=True)
                    return result

    except Exception as e:
        print(f"VIDEO PROMPT LLM Error for {player_name}: {e}", flush=True)

    # Fallback with simulation flavor
    if is_winner:
        return {
            "scene": f"A figure emerges from a portal of light and code, reality stabilizing around them as they escape the simulation",
            "dialogue": prompts.FALLBACK_VIDEO_SCRIPT["dialogue"].format(player_name=player_name)
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


async def generate_video_prompt_winner_async(player_name: str, video_theme: str):
    """Generate winner video script using LLM - triumphant tone."""
    import httpx
    import json
    import re

    # Get duration and calculate word limit
    duration = CONFIG["video_generation"]["duration_seconds"]
    word_limit = prompts.get_word_limit_for_duration(duration)

    prompt = prompts.format_prompt(
        prompts.VIDEO_SCRIPT_WINNER,
        video_theme=video_theme,
        player_name=player_name,
        duration=duration,
        word_limit=word_limit
    )

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

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = await parse_json_with_repair(json_match.group(0), player_name)
                if result:
                    print(f"VIDEO WINNER PROMPT: Generated for {player_name} (audio_type: {result.get('audio_type', 'dialogue')})", flush=True)
                    return result

    except Exception as e:
        print(f"VIDEO WINNER PROMPT Error for {player_name}: {e}", flush=True)

    # Fallback - use new format with all fields
    fallback = prompts.FALLBACK_WINNER_VIDEO_SCRIPT.copy()
    fallback["audio"] = fallback["audio"].format(player_name=player_name)
    return fallback


async def generate_video_prompt_loser_async(player_name: str, video_theme: str):
    """Generate loser video script using LLM - consoling but humorous tone."""
    import httpx
    import json
    import re

    # Get duration and calculate word limit
    duration = CONFIG["video_generation"]["duration_seconds"]
    word_limit = prompts.get_word_limit_for_duration(duration)

    prompt = prompts.format_prompt(
        prompts.VIDEO_SCRIPT_LOSER,
        video_theme=video_theme,
        player_name=player_name,
        duration=duration,
        word_limit=word_limit
    )

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

            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = await parse_json_with_repair(json_match.group(0), player_name)
                if result:
                    print(f"VIDEO LOSER PROMPT: Generated for {player_name} (audio_type: {result.get('audio_type', 'dialogue')})", flush=True)
                    return result

    except Exception as e:
        print(f"VIDEO LOSER PROMPT Error for {player_name}: {e}", flush=True)

    # Fallback - use new format with all fields
    fallback = prompts.FALLBACK_LOSER_VIDEO_SCRIPT.copy()
    fallback["audio"] = fallback["audio"].format(player_name=player_name)
    return fallback


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


async def submit_video_request_async(player_name: str, image_url: str, script_data: dict, video_theme: str, client: "httpx.AsyncClient"):
    """Submit a video generation request and return the request_id (don't wait for completion)."""
    submit_url = get_video_model_url()
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }

    # Build Kling v2.6 Pro formatted prompt with proper audio specification
    prompt = prompts.build_video_prompt(script_data, video_theme)
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
    import json

    if not request_id:
        return None

    # FAL queue API uses base model path for status/result (not full endpoint path)
    # Submit: fal-ai/kling-video/v2.6/pro/image-to-video
    # Status/Result: fal-ai/kling-video/requests/{request_id}/...
    fal_queue_url = CONFIG["image_generation"]["fal_queue_url"]
    full_model = CONFIG["video_generation"]["model"]
    base_model = "/".join(full_model.split("/")[:2])  # "fal-ai/kling-video"

    status_url = f"{fal_queue_url}/{base_model}/requests/{request_id}/status"
    result_url = f"{fal_queue_url}/{base_model}/requests/{request_id}"
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

            # Check HTTP status before parsing JSON
            if status_response.status_code != 200:
                if attempt % 6 == 0:
                    print(f"VIDEO POLL [{player_name}]: HTTP {status_response.status_code} on attempt {attempt+1}", flush=True)
                continue

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
        except json.JSONDecodeError as e:
            # Log raw response for debugging JSON parsing issues
            print(f"VIDEO POLL [{player_name}]: JSON error on attempt {attempt+1}: {e}", flush=True)
            print(f"VIDEO POLL [{player_name}]: Response text: {status_response.text[:200]}", flush=True)
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
    coop_team_reason: Optional[str] = None      # judgement reason for team outcome

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
    vote_start_time: Optional[float] = None        # When voting phase started
    timed_out_players: Dict[str, bool] = {}        # player_id -> True if timed out

class GameState(BaseModel):
    id: str
    code: str
    status: Literal["lobby", "playing", "finished"] = "lobby"
    players: Dict[str, Player] = {}
    rounds: List[Round] = []
    current_round_idx: int = -1
    max_rounds: int = Field(default_factory=lambda: len(get_round_config()))
    created_at: float = Field(default_factory=time.time)
    # Round configuration - determines type of each round (configurable via config.yaml)
    round_config: list[str] = Field(default_factory=get_round_config)
    # Pre-warmed scenarios generated in parallel when game is created
    prewarmed_scenarios: List[Optional[str]] = []  # Index corresponds to round number - 1, None for blind_architect
    # End game video fields - pre-generated winner/loser videos for ALL players
    player_winner_videos: Dict[str, str] = {}  # player_id -> winner video URL
    player_loser_videos: Dict[str, str] = {}   # player_id -> loser video URL
    videos_status: Literal["pending", "generating", "ready", "partial", "failed"] = "pending"
    videos_started_at: Optional[float] = None  # Timestamp when video generation started (for stuck-job detection)
    video_theme: Optional[str] = None  # Consistent theme for all videos
    winner_id: Optional[str] = None

# --- Persistent Storage ---
# We use a Dict to store game states. Key=GameCode
games = modal.Dict.from_name("survaive-games", create_if_missing=True)

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


async def update_game_with_retry(
    code: str,
    mutator,  # Callable[[GameState], Tuple[bool, Any]] - returns (should_save, result)
    verify,   # Callable[[GameState], bool] - returns True if mutation was applied
    max_retries: int = 10,
    error_message: str = "Failed to update game due to concurrent modifications"
):
    """
    Update game state with retry logic to handle concurrent modifications.
    
    This implements the retry-and-verify pattern to handle race conditions when
    multiple players modify the game state simultaneously. The pattern:
    1. Read game state
    2. Apply mutation
    3. Save game state
    4. Re-read and verify the mutation was applied
    5. If not, retry with exponential backoff
    
    Args:
        code: Game code
        mutator: Function that takes a GameState and returns (should_save, result).
                 If should_save is False, returns early without saving (e.g., already done).
                 Can raise HTTPException for validation errors.
        verify: Function that takes a GameState and returns True if mutation was applied.
        max_retries: Maximum number of retry attempts (default 10)
        error_message: Error message if all retries fail
    
    Returns:
        The result from the mutator function
    
    Raises:
        HTTPException(404) if game not found
        HTTPException(500) if all retries fail
        Any HTTPException raised by the mutator
    """
    for attempt in range(max_retries):
        game = get_game(code)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Apply mutation - may raise HTTPException for validation errors
        should_save, result = mutator(game)
        
        if not should_save:
            # Mutation determined no save needed (e.g., already applied)
            return result
        
        save_game(game)
        
        # Wait before verification with jitter to reduce collision probability
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)
        
        # Verify the mutation was applied
        verification = get_game(code)
        if verification and verify(verification):
            return result
        
        # Retry with exponential backoff
        print(f"UPDATE_GAME: Race condition detected, retry {attempt + 1}/{max_retries}", flush=True)
        backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
        await asyncio.sleep(min(backoff, 2.0))
    
    raise HTTPException(status_code=500, detail=error_message)


# --- Video Pre-generation Helper ---
# Maximum time to wait for video generation before considering it stuck (20 minutes)
VIDEO_GENERATION_TIMEOUT_SECONDS = 20 * 60

def maybe_spawn_video_prewarm(game: GameState) -> bool:
    """
    Atomically check and spawn video pre-generation if not already started.

    This helper ensures:
    1. Video generation is only spawned once (idempotent)
    2. Status is set to "generating" BEFORE spawning (prevents duplicates)
    3. Start timestamp is recorded (enables stuck-job detection)

    Args:
        game: The game state object (will be modified and saved)

    Returns:
        True if prewarm was spawned, False if already in progress or complete
    """
    if game.videos_status != "pending":
        print(f"VIDEO PREWARM: Not spawning - status is {game.videos_status}", flush=True)
        return False

    # Set status BEFORE spawning to prevent race conditions
    game.videos_status = "generating"
    game.videos_started_at = time.time()
    save_game(game)

    print(f"VIDEO PREWARM: Spawning video generation for game {game.code}", flush=True)
    prewarm_player_videos.spawn(game.code)
    return True


def is_video_generation_stuck(game: GameState) -> bool:
    """
    Check if video generation appears to be stuck.

    Returns True if:
    - Status is "generating"
    - AND it started more than VIDEO_GENERATION_TIMEOUT_SECONDS ago
    """
    if game.videos_status != "generating":
        return False

    if game.videos_started_at is None:
        # No start time recorded - assume stuck if status is generating
        return True

    elapsed = time.time() - game.videos_started_at
    return elapsed > VIDEO_GENERATION_TIMEOUT_SECONDS


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

    code = request.query_params.get("code")
    data = await request.json()
    player_name = data.get("name", "Unknown Player")
    character_description = data.get("character_description")
    character_image_url = data.get("character_image_url")  # Pre-generated image (from random selection)
    
    # Validate input lengths
    if len(player_name) > MAX_NAME_LENGTH:
        raise HTTPException(status_code=400, detail=f"Name too long (max {MAX_NAME_LENGTH} characters)")
    if character_description and len(character_description) > MAX_CHARACTER_DESCRIPTION_LENGTH:
        raise HTTPException(status_code=400, detail=f"Character description too long (max {MAX_CHARACTER_DESCRIPTION_LENGTH} characters)")

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
        "submission_timeout_seconds": CONFIG["game"]["submission_timeout_seconds"],
        "volunteer_timeout_seconds": CONFIG["game"]["volunteer_timeout_seconds"]
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

        # Determine timeout based on current phase
        if current_round.status == "sacrifice_submission":
            timeout_seconds = CONFIG["game"]["sacrifice_submission_timeout_seconds"]
        elif current_round.status == "sacrifice_volunteer":
            timeout_seconds = CONFIG["game"]["volunteer_timeout_seconds"]
        else:
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
                            p.death_reason = "TIMEOUT: Stood around doing nothing while death approached."
                            current_round.timed_out_players[pid] = True
                            needs_save = True
                            print(f"TIMEOUT: Player {p.name} timed out in strategy phase", flush=True)

                            # For cooperative mode, set placeholder strategy for voting
                            if current_round.type == "cooperative":
                                p.strategy = "[TIMEOUT - No strategy submitted]"

                            # NOTE: Timeout images are now generated inside the judgement functions
                            # to avoid race conditions with async game state saves

                    # Clear the timer to prevent re-triggering
                    current_round.submission_start_time = None

                    # Check if we should auto-advance to judgement (all players handled)
                    lobby_players = [p for p in game.players.values() if p.in_lobby]
                    all_handled = all(
                        not p.is_alive or p.strategy
                        for p in lobby_players
                    )
                    if all_handled:
                        # Check if everyone is dead (all timed out)
                        all_dead = all(not p.is_alive for p in lobby_players)
                        needs_save = True

                        # Handle round type specific transitions
                        if current_round.type == "cooperative":
                            if all_dead:
                                # Everyone timed out - skip directly to results with team failure
                                current_round.coop_team_survived = False
                                current_round.coop_team_reason = "The entire team stood around doing nothing. Total failure."
                                current_round.status = "results"
                                print(f"TIMEOUT: All players dead in coop, skipping to results", flush=True)
                                # Still generate timeout images for display on results
                                generate_coop_strategy_images.spawn(game.code, game.current_round_idx)
                            else:
                                # Some players submitted - check if voting is needed
                                alive_players = [p for p in lobby_players if p.is_alive]
                                if len(alive_players) <= 1:
                                    # Only 1 alive player - skip voting (can't vote for self)
                                    if alive_players:
                                        winner = alive_players[0]
                                        current_round.coop_winning_strategy_id = winner.id
                                        current_round.coop_vote_points[winner.id] = 200
                                        winner.score += 200
                                    current_round.status = "coop_judgement"
                                    print(f"TIMEOUT: Only {len(alive_players)} alive in coop, skipping voting", flush=True)
                                    generate_coop_strategy_images.spawn(game.code, game.current_round_idx)
                                    run_coop_judgement.spawn(game.code, game.current_round_idx)
                                else:
                                    # Multiple players - go to voting phase
                                    current_round.status = "coop_voting"
                                    current_round.vote_start_time = time.time()
                                    print(f"TIMEOUT: Advancing coop to voting", flush=True)
                                    generate_coop_strategy_images.spawn(game.code, game.current_round_idx)
                        elif current_round.type == "ranked":
                            current_round.status = "ranked_judgement"
                            print(f"TIMEOUT: All players handled, advancing to ranked_judgement (all_dead={all_dead})", flush=True)
                            run_ranked_judgement.spawn(game.code, game.current_round_idx)
                        else:
                            # Standard survival/blind_architect/last_stand
                            current_round.status = "judgement"
                            print(f"TIMEOUT: All players handled, advancing to judgement (all_dead={all_dead})", flush=True)
                            run_round_judgement.spawn(game.code, game.current_round_idx)

                elif current_round.status == "trap_creation":
                    # Mark players who haven't submitted trap as timed out
                    for pid, p in game.players.items():
                        if p.is_alive and pid not in current_round.trap_proposals and p.in_lobby:
                            p.is_alive = False
                            p.death_reason = "TIMEOUT: Failed to design trap in time. Architect privileges revoked."
                            current_round.timed_out_players[pid] = True
                            needs_save = True
                            print(f"TIMEOUT: Player {p.name} timed out in trap_creation phase", flush=True)

                            # NOTE: Timeout images are now generated inside the judgement functions
                            # to avoid race conditions with async game state saves

                    # Clear the timer
                    current_round.submission_start_time = None

                    # Check if all players are dead (everyone timed out)
                    lobby_players = [p for p in game.players.values() if p.in_lobby]
                    all_dead = all(not p.is_alive for p in lobby_players)
                    if all_dead:
                        # Everyone timed out - go to judgement to generate timeout images
                        current_round.status = "judgement"
                        needs_save = True
                        print(f"TIMEOUT: All players dead in trap_creation, advancing to judgement for timeout images", flush=True)
                        run_round_judgement.spawn(game.code, game.current_round_idx)
                    elif current_round.trap_proposals:
                        # Some traps submitted - advance to voting
                        current_round.status = "trap_voting"
                        current_round.vote_start_time = time.time()
                        needs_save = True
                        print(f"TIMEOUT: Advancing to trap_voting with {len(current_round.trap_proposals)} proposals", flush=True)

                elif current_round.status == "sacrifice_volunteer":
                    # Volunteer phase timed out - if no volunteers, pick random martyr
                    volunteer_ids = [pid for pid, v in current_round.sacrifice_volunteers.items() if v]
                    current_round.submission_start_time = None
                    needs_save = True

                    if volunteer_ids:
                        # Has volunteers - advance to voting or submission
                        if len(volunteer_ids) == 1:
                            # Only one volunteer - they're the martyr
                            current_round.martyr_id = volunteer_ids[0]
                            current_round.status = "sacrifice_submission"
                            current_round.submission_start_time = time.time()
                            print(f"TIMEOUT: 1 volunteer, advancing to sacrifice_submission", flush=True)
                        else:
                            # Multiple volunteers - advance to voting
                            current_round.status = "sacrifice_voting"
                            current_round.vote_start_time = time.time()
                            print(f"TIMEOUT: {len(volunteer_ids)} volunteers, advancing to sacrifice_voting", flush=True)
                    else:
                        # No volunteers - randomly pick a martyr (cowards get drafted)
                        lobby_players = [p for p in game.players.values() if p.in_lobby and p.is_alive]
                        if lobby_players:
                            import random
                            martyr = random.choice(lobby_players)
                            current_round.martyr_id = martyr.id
                            current_round.status = "sacrifice_submission"
                            current_round.submission_start_time = time.time()
                            print(f"TIMEOUT: No volunteers, drafted {martyr.name} as martyr", flush=True)
                        else:
                            # Everyone already dead somehow - skip to results
                            current_round.status = "results"
                            print(f"TIMEOUT: No alive players for sacrifice, skipping to results", flush=True)

                elif current_round.status == "sacrifice_submission":
                    # Martyr timed out - everyone dies with personalized deaths
                    martyr = game.players.get(current_round.martyr_id)
                    if martyr and not current_round.martyr_speech:
                        current_round.martyr_speech = "[TIMEOUT - The martyr froze in fear and said nothing]"
                        current_round.martyr_epic = False
                        current_round.martyr_reason = "The chosen martyr stood frozen, unable to speak. Their silence condemned everyone. A truly pathetic end."

                        # Everyone dies - set temporary death reasons (will be replaced by LLM)
                        for pid, p in game.players.items():
                            if p.is_alive:
                                p.is_alive = False
                                if pid == current_round.martyr_id:
                                    p.death_reason = "FROZE IN FEAR: Generating personalized death..."
                                else:
                                    p.death_reason = "CONDEMNED: Generating personalized death..."

                        current_round.status = "results"
                        current_round.submission_start_time = None
                        needs_save = True
                        print(f"TIMEOUT: Martyr {martyr.name} timed out, spawning personalized death generation", flush=True)

                        # Spawn personalized death generation (LLM + images)
                        generate_sacrifice_timeout_deaths.spawn(
                            game.code,
                            current_round.martyr_id,
                            current_round.style_theme
                        )

        # =====================================================================
        # VOTING PHASE TIMEOUT HANDLING
        # =====================================================================
        vote_timeout = CONFIG["game"]["vote_timeout_seconds"]

        if current_round.status == "trap_voting":
            if current_round.vote_start_time and (time.time() - current_round.vote_start_time) >= vote_timeout:
                current_round.vote_start_time = None
                needs_save = True
                print(f"TIMEOUT: trap_voting timed out", flush=True)

                if current_round.votes:
                    # Tally existing votes, pick winner
                    vote_counts = {}
                    for target in current_round.votes.values():
                        vote_counts[target] = vote_counts.get(target, 0) + 1
                    winner_id = max(vote_counts, key=vote_counts.get)
                else:
                    # No votes at all - pick random trap proposal
                    if current_round.trap_proposals:
                        winner_id = random.choice(list(current_round.trap_proposals.keys()))
                    else:
                        # No proposals (shouldn't happen) - skip to results
                        current_round.status = "results"
                        print(f"TIMEOUT: trap_voting no proposals, skipping to results", flush=True)
                        winner_id = None

                if winner_id and winner_id in current_round.trap_proposals:
                    winning_trap = current_round.trap_proposals[winner_id]
                    winning_image = current_round.trap_images.get(winner_id)

                    current_round.scenario_text = winning_trap
                    current_round.scenario_image_url = winning_image
                    current_round.architect_id = winner_id
                    current_round.status = "strategy"
                    current_round.submission_start_time = time.time()
                    if winner_id in game.players:
                        game.players[winner_id].score += 500
                    print(f"TIMEOUT: trap_voting resolved, winner: {winner_id}", flush=True)

        elif current_round.status == "coop_voting":
            if current_round.vote_start_time and (time.time() - current_round.vote_start_time) >= vote_timeout:
                current_round.vote_start_time = None
                needs_save = True
                print(f"TIMEOUT: coop_voting timed out", flush=True)

                # Tally whatever votes exist and transition
                tally_coop_votes_and_transition(game, current_round)
                run_coop_judgement.spawn(game.code, game.current_round_idx)

        elif current_round.status == "sacrifice_voting":
            if current_round.vote_start_time and (time.time() - current_round.vote_start_time) >= vote_timeout:
                current_round.vote_start_time = None
                needs_save = True
                print(f"TIMEOUT: sacrifice_voting timed out", flush=True)

                # Tally existing votes or pick random eligible player
                if current_round.sacrifice_votes:
                    vote_counts = {}
                    for target in current_round.sacrifice_votes.values():
                        vote_counts[target] = vote_counts.get(target, 0) + 1
                    martyr_id = max(vote_counts, key=vote_counts.get)
                else:
                    # No votes - pick random from volunteers (or all players if no volunteers)
                    volunteer_ids = [pid for pid, v in current_round.sacrifice_volunteers.items() if v]
                    if volunteer_ids:
                        martyr_id = random.choice(volunteer_ids)
                    else:
                        alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
                        martyr_id = random.choice([p.id for p in alive_players]) if alive_players else None

                if martyr_id:
                    current_round.martyr_id = martyr_id
                    current_round.status = "sacrifice_submission"
                    current_round.submission_start_time = time.time()
                    print(f"TIMEOUT: sacrifice_voting resolved, martyr: {martyr_id}", flush=True)

        elif current_round.status == "last_stand_revival":
            if current_round.vote_start_time and (time.time() - current_round.vote_start_time) >= vote_timeout:
                current_round.vote_start_time = None
                current_round.status = "results"
                needs_save = True
                print(f"TIMEOUT: last_stand_revival timed out, no revival", flush=True)

        # FALLBACK: Detect stuck judgement phase from early judgement race condition
        # This handles the case where all judge_single_player tasks completed but
        # none of them saw the full picture due to Modal Dict eventual consistency
        elif current_round.status == "judgement" and current_round.type in ["survival", "blind_architect"]:
            in_lobby_players = [p for p in game.players.values() if p.in_lobby]
            # Check if all players who submitted have been judged (have death/survival reason)
            all_judged = all(
                (p.death_reason or p.survival_reason or not p.strategy)
                for p in in_lobby_players
            )
            # Check no judgements are still pending
            no_pending = not any(p.judgement_pending for p in game.players.values())

            if all_judged and no_pending and in_lobby_players:
                print(f"FALLBACK: Detected stuck judgement phase - all players judged but status not updated. Transitioning to results.", flush=True)
                current_round.status = "results"
                needs_save = True

                # Trigger video pre-generation on round 1 results (if not already started)
                if game.current_round_idx == 0 and game.videos_status == "pending":
                    print("FALLBACK: Round 1 complete, triggering video pre-generation", flush=True)
                    game.videos_status = "generating"
                    game.videos_started_at = time.time()
                    prewarm_player_videos.spawn(game.code)

    if needs_save:
        save_game(game)

    # Include config values in response for frontend
    response = game.model_dump()
    response["config"] = {
        "submission_timeout_seconds": CONFIG["game"]["submission_timeout_seconds"],
        "volunteer_timeout_seconds": CONFIG["game"]["volunteer_timeout_seconds"],
        "sacrifice_submission_timeout_seconds": CONFIG["game"]["sacrifice_submission_timeout_seconds"],
        "vote_timeout_seconds": CONFIG["game"]["vote_timeout_seconds"]
    }
    return response

def get_system_message(round_num: int, max_rounds: int, round_type: str) -> str:
    """Generate the system message for a given round based on narrative progression."""
    if round_type == "blind_architect":
        return "SECURITY BREACH DETECTED // ARCHITECT PROTOCOL ACTIVATED"
    elif round_type == "cooperative":
        return "COLLABORATION REQUIRED // EVERYONE'S SURVIVAL DEPENDS ON PICKING THE RIGHT STRATEGY"
    elif round_type == "sacrifice":
        return "CRITICAL FAILURE // ONE MUST FALL FOR OTHERS TO SURVIVE"
    elif round_type == "last_stand":
        return "HO HO HO // EVIL SANTA'S NIGHTMARE WORKSHOP // YOU'VE BEEN VERY NAUGHTY"
    elif round_type == "survival":
        return "FIGHT TO SURVIVE // MULTIPLE SURVIVORS POSSIBLE"
    elif round_type == "ranked":
        return "FIGHT TO SURVIVE // ONLY ONE WINNER - EVERY PLAYER FOR THEMSELVES"
    else:
        return "FIGHT!"


@web_app.post("/api/start_game")
async def api_start_game(request: Request):
    print("API: Start Game Called")
    code = request.query_params.get("code")
    game = get_game(code)
    if not game:
        print("API: Game not found")
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Guard: only allow starting from lobby state with no rounds
    if game.status != "lobby":
        raise HTTPException(status_code=400, detail=f"Cannot start game: game is already in '{game.status}' state")
    if len(game.rounds) > 0:
        raise HTTPException(status_code=400, detail="Cannot start game: game already has rounds")

    # Use pre-warmed scenario if available, otherwise generate on-demand (fallback)
    if game.prewarmed_scenarios and len(game.prewarmed_scenarios) > 0 and game.prewarmed_scenarios[0]:
        scenario_text = game.prewarmed_scenarios[0]
        print(f"API: Using pre-warmed scenario: {scenario_text[:50]}...")
    else:
        print("API: No pre-warmed scenario, generating on-demand...")
        # Use asyncio.to_thread to avoid blocking the event loop
        scenario_text = await asyncio.to_thread(generate_scenario_llm, 1, game.max_rounds)
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
        first_round.submission_start_time = time.time()  # Start timer for volunteer phase
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
    """Generate a timeout/failure image when player does not submit a strategy.

    Shows the character standing around doing nothing while danger approaches.
    """
    import asyncio

    async def do_generation():
        print(f"TIMEOUT IMG: Generating timeout image for player {player_id}...", flush=True)

        # Timeout-themed prompt - character standing around doing nothing
        base_prompt = random.choice(prompts.TIMEOUT_IMAGE_OPTIONS) + prompts.TIMEOUT_IMAGE_SUFFIX
        themed_prompt = apply_style_theme(base_prompt, style_theme)

        url = await generate_image_fal_async(themed_prompt)
        if url:
            game = get_game(game_code)
            if game and game.current_round_idx >= 0:
                current_round = game.rounds[game.current_round_idx]
                # For cooperative mode, store in strategy_images (for voting)
                if current_round.type == "cooperative":
                    current_round.strategy_images[player_id] = url
                else:
                    # For other modes, store as the player's result image
                    if player_id in game.players:
                        game.players[player_id].result_image_url = url
                save_game(game)
                print(f"TIMEOUT IMG: Saved timeout image for {player_id}", flush=True)
        else:
            print(f"TIMEOUT IMG: Failed to generate for {player_id}", flush=True)

    asyncio.run(do_generation())


@app.function(image=image, secrets=secrets)
def generate_sacrifice_timeout_deaths(game_code: str, martyr_id: str, style_theme: str | None):
    """Generate personalized deaths for all players when martyr times out.

    Uses LLM to create funny deaths based on character traits, then generates images.
    """
    import asyncio
    import httpx
    import re
    import json

    async def do_generation():
        game = get_game(game_code)
        if not game or game.current_round_idx < 0:
            print(f"SACRIFICE TIMEOUT: Game {game_code} not found", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]

        # Build player list for LLM prompt
        player_info = []
        alive_players = [(pid, p) for pid, p in game.players.items() if p.is_alive or pid == martyr_id]

        for pid, p in alive_players:
            char_desc = p.character_description or "No character description"
            is_martyr = pid == martyr_id
            player_info.append(f"- {p.name} (ID: {pid}){' [THE MARTYR WHO FROZE]' if is_martyr else ''}: {char_desc}")

        player_list = "\n".join(player_info)

        print(f"SACRIFICE TIMEOUT: Generating personalized deaths for {len(alive_players)} players", flush=True)

        # Call LLM to generate personalized deaths
        try:
            prompt = prompts.format_prompt(prompts.SACRIFICE_TIMEOUT_DEATHS, player_list=player_list)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CONFIG['llm']['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": CONFIG["models"]["sacrifice_judgement"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.9,
                    },
                    timeout=CONFIG["llm"]["default_timeout_seconds"]
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                # Parse JSON from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                    deaths = result.get("deaths", [])
                else:
                    raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"SACRIFICE TIMEOUT: LLM failed: {e}, using fallback deaths", flush=True)
            # Fallback: generate generic deaths
            deaths = [
                {"player_id": pid, "reason": "Perished in the chaos of the martyr's silence.", "visual_prompt": "A figure collapsing in dramatic despair, dark atmosphere"}
                for pid, _ in alive_players
            ]

        # Apply deaths to players
        death_map = {d["player_id"]: d for d in deaths}

        # Re-fetch game state (may have changed)
        game = get_game(game_code)
        if not game:
            return

        current_round = game.rounds[game.current_round_idx]

        for pid, p in game.players.items():
            if pid in death_map:
                death_info = death_map[pid]
                if pid == martyr_id:
                    # Martyr gets special prefix
                    p.death_reason = f"FROZE IN FEAR: {death_info['reason']}"
                else:
                    p.death_reason = f"CONDEMNED: {death_info['reason']}"

        save_game(game)
        print(f"SACRIFICE TIMEOUT: Applied personalized death reasons", flush=True)

        # Generate images for all players in parallel
        async def generate_death_image(pid: str, visual_prompt: str):
            themed_prompt = apply_style_theme(visual_prompt + ". Dramatic death scene, dark atmosphere.", style_theme)
            url = await generate_image_fal_async(themed_prompt)
            return pid, url

        image_tasks = []
        for death in deaths:
            pid = death["player_id"]
            visual_prompt = death.get("visual_prompt", "A dramatic death scene")
            image_tasks.append(generate_death_image(pid, visual_prompt))

        print(f"SACRIFICE TIMEOUT: Generating {len(image_tasks)} death images in parallel", flush=True)
        image_results = await asyncio.gather(*image_tasks)

        # Save all images
        game = get_game(game_code)
        if not game:
            return

        for pid, url in image_results:
            if url and pid in game.players:
                game.players[pid].result_image_url = url
                print(f"SACRIFICE TIMEOUT: Saved death image for {game.players[pid].name}", flush=True)

        save_game(game)
        print(f"SACRIFICE TIMEOUT: Complete - all death images saved", flush=True)

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

    async def do_prewarm():
        # Retry fetching game with backoff to handle eventual consistency
        max_fetch_retries = 10
        game = None
        for attempt in range(max_fetch_retries):
            game = get_game(game_code)
            if game:
                break
            jitter = random.uniform(0.1, 0.3)
            wait_time = 0.2 * (1.5 ** attempt) + jitter
            print(f"PREWARM: Game {game_code} not found, retry {attempt + 1}/{max_fetch_retries} in {wait_time:.2f}s", flush=True)
            await asyncio.sleep(min(wait_time, 3.0))
        
        if not game:
            print(f"PREWARM: Game {game_code} not found after {max_fetch_retries} retries!", flush=True)
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


async def generate_timeout_image_async(player_id: str, style_theme: str | None):
    """Generate timeout image inline (async version for use within judgement).

    Returns (player_id, url) tuple for easy result processing.
    """
    base_prompt = random.choice(prompts.TIMEOUT_IMAGE_OPTIONS) + prompts.TIMEOUT_IMAGE_SUFFIX
    themed_prompt = apply_style_theme(base_prompt, style_theme)
    url = await generate_image_fal_async(themed_prompt)
    print(f"TIMEOUT IMG: Generated for {player_id}: {url is not None}", flush=True)
    return (player_id, url)


@app.function(image=image, secrets=secrets)
def run_round_judgement(game_code: str, expected_round_idx: int = -1):
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

        # Verify we're still on the expected round (prevent stale task from mutating wrong round)
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"JUDGEMENT: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
            return

        current_round = game.rounds[game.current_round_idx]
        print(f"JUDGEMENT: Round {current_round.number}, scenario: {current_round.scenario_text[:50]}...", flush=True)

        # Collect all players that need judging
        tasks = []
        player_info = []
        for pid, p in game.players.items():
            print(f"JUDGEMENT: Player {p.name} (alive={p.is_alive}, strategy={bool(p.strategy)}, pending={p.judgement_pending}, has_reason={bool(p.death_reason or p.survival_reason)})", flush=True)

            # Skip players already being judged by early judgement (judge_single_player)
            if p.judgement_pending:
                print(f"JUDGEMENT: Skipping {p.name} - judgement already pending", flush=True)
                continue

            # Skip players already judged (have a death or survival reason from early judgement)
            if p.death_reason or p.survival_reason:
                print(f"JUDGEMENT: Skipping {p.name} - already judged", flush=True)
                continue

            if p.strategy and p.is_alive:
                tasks.append(judge_and_generate(pid, p.name, p.strategy, current_round.scenario_text, current_round.style_theme))
                player_info.append((pid, p.name))

        # Collect timeout image tasks for timed-out players
        timeout_pids = list(current_round.timed_out_players.keys())
        timeout_tasks = [
            generate_timeout_image_async(pid, current_round.style_theme)
            for pid in timeout_pids if pid in game.players
        ]
        if timeout_tasks:
            print(f"JUDGEMENT: Also generating {len(timeout_tasks)} timeout images", flush=True)

        # Run ALL tasks in parallel (judgements + timeout images)
        num_judgement_tasks = len(tasks)
        all_tasks = tasks + timeout_tasks
        results = []
        timeout_results = []

        if all_tasks:
            print(f"JUDGEMENT: Running {len(all_tasks)} tasks in parallel...", flush=True)
            all_results = await asyncio.gather(*all_tasks)
            results = all_results[:num_judgement_tasks]
            timeout_results = all_results[num_judgement_tasks:]

            # Apply judgement results to game state
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

            # Apply timeout images
            for pid, url in timeout_results:
                if url and pid in game.players:
                    game.players[pid].result_image_url = url
                    print(f"JUDGEMENT: Saved timeout image for {game.players[pid].name}", flush=True)

        # Re-fetch game state to merge with any concurrent early judgement results
        # This prevents overwriting scores/reasons set by judge_single_player
        fresh_game = get_game(game_code)
        if fresh_game:
            fresh_round = fresh_game.rounds[fresh_game.current_round_idx]

            # Apply our results to fresh state
            for result in results:
                pid = result["pid"]
                if pid in fresh_game.players:
                    p = fresh_game.players[pid]
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

            # Apply timeout images to fresh state
            for pid, url in timeout_results:
                if url and pid in fresh_game.players:
                    fresh_game.players[pid].result_image_url = url

            fresh_round.status = "results"
            save_game(fresh_game)
            game = fresh_game  # Update reference for video pre-generation check
        else:
            # Fallback if re-fetch fails
            print(f"JUDGEMENT: Warning - could not re-fetch game, saving original state", flush=True)
            current_round.status = "results"
            save_game(game)

        print(f"JUDGEMENT: Setting status to results", flush=True)

        # Trigger video pre-generation on round 1 results (only once)
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

        print(f"JUDGEMENT: Complete!", flush=True)

    # Run the async function
    asyncio.run(run_all_judgements())


@app.function(image=image, secrets=secrets)
def run_ranked_judgement(game_code: str, expected_round_idx: int = -1):
    """Run ranked judgement - compare all strategies and assign rankings."""
    import json
    import asyncio

    async def do_ranked_judgement():
        print(f"RANKED_JUDGE: Starting for game {game_code}", flush=True)

        game = get_game(game_code)
        if not game:
            print(f"RANKED_JUDGE: Game {game_code} not found!", flush=True)
            return

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"RANKED_JUDGE: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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

                # Only rank 1 survives - everyone else dies
                if rank == 1:
                    game.players[pid].is_alive = True
                    game.players[pid].survival_reason = commentary
                    game.players[pid].death_reason = None
                else:
                    game.players[pid].is_alive = False
                    game.players[pid].death_reason = commentary
                    game.players[pid].survival_reason = None

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

            # Also generate timeout images for timed-out players
            timeout_pids = list(current_round.timed_out_players.keys())
            timeout_tasks = [
                generate_timeout_image_async(pid, current_round.style_theme)
                for pid in timeout_pids if pid in game.players
            ]
            if timeout_tasks:
                print(f"RANKED_JUDGE: Also generating {len(timeout_tasks)} timeout images", flush=True)

            # Run all image tasks in parallel
            all_image_tasks = image_tasks + timeout_tasks
            all_image_results = await asyncio.gather(*all_image_tasks)
            image_results = all_image_results[:len(image_tasks)]
            timeout_results = all_image_results[len(image_tasks):]

            # Apply images to players
            for pid, url in image_results:
                if url:
                    game.players[pid].result_image_url = url

            # Apply timeout images
            for pid, url in timeout_results:
                if url and pid in game.players:
                    game.players[pid].result_image_url = url
                    print(f"RANKED_JUDGE: Saved timeout image for {game.players[pid].name}", flush=True)

        except Exception as e:
            print(f"RANKED_JUDGE: Error - {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Fallback: pick random winner, everyone else dies
            import random
            winner_idx = random.randint(0, len(strategies) - 1)
            for i, s in enumerate(strategies):
                pid = s["player_id"]
                rank = 1 if i == winner_idx else i + 2
                current_round.ranked_results[pid] = rank
                points = calculate_ranked_points(len(strategies), rank)
                current_round.ranked_points[pid] = points
                game.players[pid].score += points
                if i == winner_idx:
                    game.players[pid].is_alive = True
                    game.players[pid].survival_reason = "Randomly selected as winner due to judgement error"
                else:
                    game.players[pid].is_alive = False
                    game.players[pid].death_reason = "Failed to rank higher (judgement error fallback)"

        # Transition to results
        current_round.status = "results"
        save_game(game)

        # Trigger video pre-generation on round 1 results (only once)
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

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
        # NOTE: Don't filter by last_active - the round timeout handles inactive players.
        # Filtering by heartbeat causes premature advancement when players background their tab.
        in_lobby_players = [p for p in game.players.values() if p.in_lobby]

        # Check if any judgements are still pending (across ALL players, not just filtered)
        any_pending = any(p.judgement_pending for p in game.players.values())
        # Check if all in-lobby players have submitted strategies
        all_submitted = all(p.strategy for p in in_lobby_players) if in_lobby_players else True

        print(f"EARLY_JUDGE: Check - pending={any_pending}, submitted={all_submitted}, players={len(in_lobby_players)}, status={current_round.status}", flush=True)

        # Transition to results when all judgements complete
        # Status could be "strategy" (still waiting for others) or "judgement" (all submitted, waiting for judges)
        if current_round.status in ["strategy", "judgement"] and all_submitted and not any_pending:
            print("EARLY_JUDGE: All judgements complete! Transitioning to results.", flush=True)
            current_round.status = "results"

            # Trigger video pre-generation on round 1 results (this is the key fix for early judgement path)
            if game.current_round_idx == 0 and game.videos_status == "pending":
                print("EARLY_JUDGE: Round 1 complete, triggering video pre-generation", flush=True)
                # Set status before save to prevent race with other early judges
                game.videos_status = "generating"
                game.videos_started_at = time.time()
                save_game(game)
                prewarm_player_videos.spawn(game.code)
                print(f"EARLY_JUDGE: Complete for {player.name}!", flush=True)
                return  # Already saved, exit early

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
                script_data = player_prompts[player.id]
                image_url = player_images[player.id]

                submit_tasks.append(submit_video_request_async(
                    player.name, image_url, script_data, video_theme, client
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


@app.function(image=image, secrets=secrets, timeout=900)  # 15 min timeout for multiple videos
def prewarm_player_videos(game_code: str):
    """Pre-generate winner AND loser videos for ALL players using their avatars.

    Called when round 1 results are shown.
    Generates 2 videos per player (winner + loser) so the correct one can be
    selected instantly at game end.
    """
    import asyncio
    import httpx

    async def do_prewarm_videos():
        game = get_game(game_code)
        if not game:
            print(f"PREWARM VIDEO: Game {game_code} not found!", flush=True)
            return

        players = list(game.players.values())
        if not players:
            print("PREWARM VIDEO: No players found!", flush=True)
            return

        total_players = len(players)

        # Select random video theme for all videos
        video_theme = random.choice(VIDEO_STYLE_THEMES)

        game.videos_status = "generating"
        game.video_theme = video_theme
        save_game(game)

        print(f"PREWARM VIDEO: Starting for {total_players} players, theme: {video_theme}", flush=True)

        # ============================================================
        # PHASE 1: Generate ALL LLM prompts in parallel (2 per player)
        # ============================================================
        print(f"PREWARM VIDEO PHASE 1: Generating {total_players * 2} LLM prompts...", flush=True)

        llm_tasks = []
        task_metadata = []  # Track (video_type, player_id) for each task

        for player in players:
            # Winner prompt
            llm_tasks.append(generate_video_prompt_winner_async(player.name, video_theme))
            task_metadata.append(("winner", player.id))
            # Loser prompt
            llm_tasks.append(generate_video_prompt_loser_async(player.name, video_theme))
            task_metadata.append(("loser", player.id))

        llm_results_raw = await asyncio.gather(*llm_tasks, return_exceptions=True)

        # Organize results: {player_id: {"winner": {...}, "loser": {...}}}
        player_prompts = {p.id: {} for p in players}
        for idx, (video_type, player_id) in enumerate(task_metadata):
            result = llm_results_raw[idx]
            if isinstance(result, Exception):
                print(f"PREWARM VIDEO PHASE 1: LLM error for {player_id} ({video_type}): {result}", flush=True)
                # Use fallback
                if video_type == "winner":
                    player_prompts[player_id]["winner"] = {
                        "scene": "A champion emerges victorious from a portal of light",
                        "dialogue": "Congratulations to the champion!"
                    }
                else:
                    player_prompts[player_id]["loser"] = {
                        "scene": "A figure receives a consolation prize amid confetti",
                        "dialogue": "Better luck next time!"
                    }
            else:
                player_prompts[player_id][video_type] = result

        print(f"PREWARM VIDEO PHASE 1: Complete", flush=True)

        # ============================================================
        # PHASE 2: Determine base images for each player
        # Use avatar if available, otherwise generate ceremony image
        # ============================================================
        print(f"PREWARM VIDEO PHASE 2: Preparing base images...", flush=True)

        player_base_images = {}  # player_id -> image_url
        image_gen_tasks = []  # For players without avatars
        image_gen_player_ids = []

        for player in players:
            if player.character_image_url:
                # Use existing avatar
                player_base_images[player.id] = player.character_image_url
                print(f"PREWARM VIDEO PHASE 2: Using avatar for {player.name}", flush=True)
            else:
                # Need to generate a base image using winner scene (more generic)
                scene = player_prompts[player.id]["winner"].get("scene", "A ceremony scene")
                image_prompt = f"{scene}. Setting: {video_theme}. Cinematic, dramatic lighting, vivid colors."
                image_gen_tasks.append(generate_image_fal_async(image_prompt))
                image_gen_player_ids.append(player.id)

        # Generate missing base images in parallel
        if image_gen_tasks:
            print(f"PREWARM VIDEO PHASE 2: Generating {len(image_gen_tasks)} base images...", flush=True)
            image_results = await asyncio.gather(*image_gen_tasks, return_exceptions=True)

            for idx, player_id in enumerate(image_gen_player_ids):
                result = image_results[idx]
                if isinstance(result, Exception) or result is None:
                    print(f"PREWARM VIDEO PHASE 2: Image failed for {player_id}", flush=True)
                else:
                    player_base_images[player_id] = result

        print(f"PREWARM VIDEO PHASE 2: {len(player_base_images)}/{total_players} base images ready", flush=True)

        if not player_base_images:
            print("PREWARM VIDEO: All base images failed, aborting", flush=True)
            game = get_game(game_code)
            if game:
                game.videos_status = "failed"
                save_game(game)
            return

        # ============================================================
        # PHASE 3: Submit ALL video requests in parallel
        # 2 videos per player with a base image
        # ============================================================
        print(f"PREWARM VIDEO PHASE 3: Submitting video requests...", flush=True)

        async with httpx.AsyncClient(timeout=60.0) as client:
            submit_tasks = []
            submit_metadata = []  # (player_id, video_type)

            for player in players:
                if player.id not in player_base_images:
                    continue

                base_image = player_base_images[player.id]

                for video_type in ["winner", "loser"]:
                    script_data = player_prompts[player.id][video_type]

                    task = submit_video_request_async(
                        player.name, base_image, script_data, video_theme, client
                    )
                    submit_tasks.append(task)
                    submit_metadata.append((player.id, video_type))

            submit_results = await asyncio.gather(*submit_tasks, return_exceptions=True)

            # Collect request IDs: {player_id: {"winner": request_id, "loser": request_id}}
            player_request_ids = {p.id: {} for p in players}
            for idx, (player_id, video_type) in enumerate(submit_metadata):
                result = submit_results[idx]
                if isinstance(result, Exception) or result is None:
                    print(f"PREWARM VIDEO PHASE 3: Submit failed for {player_id} ({video_type})", flush=True)
                else:
                    player_request_ids[player_id][video_type] = result

            total_submitted = sum(len(v) for v in player_request_ids.values())
            print(f"PREWARM VIDEO PHASE 3: {total_submitted} video requests submitted", flush=True)

            if total_submitted == 0:
                print("PREWARM VIDEO: All submissions failed, aborting", flush=True)
                game = get_game(game_code)
                if game:
                    game.videos_status = "failed"
                    save_game(game)
                return

            # ============================================================
            # PHASE 4: Poll ALL video statuses in parallel
            # ============================================================
            print(f"PREWARM VIDEO PHASE 4: Polling video statuses...", flush=True)

            poll_tasks = []
            poll_metadata = []  # (player_id, video_type)

            for player_id, request_ids in player_request_ids.items():
                for video_type, request_id in request_ids.items():
                    if request_id:
                        player_name = game.players[player_id].name
                        task = poll_video_status_async(f"{player_name}_{video_type}", request_id, client)
                        poll_tasks.append(task)
                        poll_metadata.append((player_id, video_type))

            poll_results = await asyncio.gather(*poll_tasks, return_exceptions=True)

            # Collect final video URLs
            winner_videos = {}  # player_id -> video_url
            loser_videos = {}   # player_id -> video_url

            for idx, (player_id, video_type) in enumerate(poll_metadata):
                result = poll_results[idx]
                if isinstance(result, Exception) or result is None:
                    print(f"PREWARM VIDEO PHASE 4: Video failed for {player_id} ({video_type})", flush=True)
                else:
                    if video_type == "winner":
                        winner_videos[player_id] = result
                    else:
                        loser_videos[player_id] = result

            print(f"PREWARM VIDEO PHASE 4: {len(winner_videos)} winner, {len(loser_videos)} loser videos ready", flush=True)

        # ============================================================
        # Save results to game state
        # ============================================================
        game = get_game(game_code)
        if game:
            game.player_winner_videos = winner_videos
            game.player_loser_videos = loser_videos

            total_videos = len(winner_videos) + len(loser_videos)
            expected_videos = total_players * 2

            if total_videos == expected_videos:
                game.videos_status = "ready"
                print(f"PREWARM VIDEO: SUCCESS! All {total_videos} videos ready", flush=True)
            elif total_videos > 0:
                game.videos_status = "partial"
                print(f"PREWARM VIDEO: PARTIAL - {total_videos}/{expected_videos} videos ready", flush=True)
            else:
                game.videos_status = "failed"
                print(f"PREWARM VIDEO: FAILED - no videos generated", flush=True)

            save_game(game)

    # Wrap in try/except to ensure we mark as failed if any unexpected error occurs
    try:
        asyncio.run(do_prewarm_videos())
    except Exception as e:
        print(f"PREWARM VIDEO: FATAL ERROR - {e}", flush=True)
        # Try to mark as failed so retry is possible
        try:
            game = get_game(game_code)
            if game and game.videos_status == "generating":
                game.videos_status = "failed"
                save_game(game)
                print(f"PREWARM VIDEO: Marked as failed for recovery", flush=True)
        except Exception as save_err:
            print(f"PREWARM VIDEO: Could not save failed status: {save_err}", flush=True)


# --- Cooperative Round Functions ---

@app.function(image=image, secrets=secrets)
def generate_coop_strategy_images(game_code: str, expected_round_idx: int = -1):
    """Generate strategy visualization images for all players in cooperative round."""
    import asyncio

    async def generate_all_images():
        game = get_game(game_code)
        if not game:
            print(f"COOP IMAGES: Game {game_code} not found!", flush=True)
            return

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"COOP IMAGES: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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

        # Also generate timeout images for timed-out players
        timeout_pids = list(current_round.timed_out_players.keys())
        timeout_tasks = []
        for pid in timeout_pids:
            if pid in game.players:
                timeout_tasks.append(generate_timeout_image_async(pid, current_round.style_theme))
        if timeout_tasks:
            print(f"COOP IMAGES: Also generating {len(timeout_tasks)} timeout images", flush=True)

        # Run all image generation in parallel
        num_strategy_tasks = len(tasks)
        all_tasks = tasks + timeout_tasks

        if all_tasks:
            print(f"COOP IMAGES: Generating {len(all_tasks)} images in parallel...", flush=True)
            all_results = await asyncio.gather(*all_tasks)
            results = all_results[:num_strategy_tasks]
            timeout_results = all_results[num_strategy_tasks:]

            # Reload game to get fresh state before updating
            game = get_game(game_code)
            if not game:
                return
            current_round = game.rounds[game.current_round_idx]

            # Apply strategy images
            for pid, image_url in zip(player_ids, results):
                if image_url:
                    current_round.strategy_images[pid] = image_url
                    print(f"COOP IMAGES: Generated image for {pid}", flush=True)

            # Apply timeout images to strategy_images (for voting display)
            for pid, image_url in timeout_results:
                if image_url and pid in game.players:
                    current_round.strategy_images[pid] = image_url
                    print(f"COOP IMAGES: Generated timeout image for {game.players[pid].name}", flush=True)

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
def run_coop_judgement(game_code: str, expected_round_idx: int = -1):
    """Run team judgement based on the highest-voted strategy."""
    import json
    import asyncio

    async def do_judgement():
        game = get_game(game_code)
        if not game:
            print(f"COOP JUDGE: Game {game_code} not found!", flush=True)
            return

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"COOP JUDGE: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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
            current_round.coop_team_reason = res.get("reason", "The team's fate was decided.")

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

            # Use the winning strategy's existing image (already generated during voting phase)
            winning_image = current_round.strategy_images.get(winning_pid)
            if winning_image:
                current_round.scenario_image_url = winning_image
                print(f"COOP JUDGE: Using winning strategy's existing image", flush=True)

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

        # Trigger video pre-generation on round 1 results (only once)
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

        print("COOP JUDGE: Complete!", flush=True)

    asyncio.run(do_judgement())


@web_app.post("/api/submit_strategy")
async def api_submit_strategy(request: Request):
    try:
        print("API: Submit Strategy ENTRY", flush=True)
        code = request.query_params.get("code")
        data = await request.json()
        player_id = data.get("player_id")
        strategy = data.get("strategy", "")
        
        if not player_id:
            raise HTTPException(status_code=400, detail="Missing player_id")
        
        # Validate input length
        if len(strategy) > MAX_STRATEGY_LENGTH:
            raise HTTPException(status_code=400, detail=f"Strategy too long (max {MAX_STRATEGY_LENGTH} characters)")
        
        # Track what side effects to trigger after successful save
        side_effects = {"spawn_judgement": False, "round_type": None, "all_submitted": False, "alive_count": 0}
        
        def mutator(game: GameState):
            current_round = game.rounds[game.current_round_idx]
            if current_round.status != "strategy": 
                print(f"API: Submit Strategy WRONG PHASE. Current: {current_round.status}", flush=True)
                raise HTTPException(status_code=400, detail=f"Wrong phase: {current_round.status}")
            
            if player_id not in game.players:
                print(f"API: Player {player_id} not found in game")
                raise HTTPException(status_code=404, detail="Player not found")
            
            # Check if already submitted (idempotent)
            if game.players[player_id].strategy == strategy:
                print(f"API: Strategy already set for {player_id}")
                return (False, {"status": "submitted"})
            
            print(f"API: Submit Strategy for {player_id} in {code}")
            game.players[player_id].strategy = strategy
            game.players[player_id].last_active = time.time()
            
            # Get all alive players who are in the lobby
            alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
            if not alive_players:
                print("API: Warn - No alive players found. Forcing current.")
                alive_players = [game.players[player_id]]
            
            strategies_submitted = sum(1 for p in alive_players if p.strategy)
            print(f"API: Strategies Submitted: {strategies_submitted} / {len(alive_players)}")
            
            side_effects["round_type"] = current_round.type
            side_effects["alive_count"] = len(alive_players)
            side_effects["all_submitted"] = strategies_submitted >= len(alive_players)
            
            # For survival/blind_architect rounds, spawn early judgement immediately
            if current_round.type in ["survival", "blind_architect"]:
                game.players[player_id].judgement_pending = True
                side_effects["spawn_judgement"] = True
                
                if side_effects["all_submitted"]:
                    print("API: All strategies received. Showing JUDGEMENT phase.")
                    current_round.status = "judgement"
            elif side_effects["all_submitted"]:
                # Handle phase transitions for other round types
                if current_round.type == "cooperative":
                    if len(alive_players) <= 1:
                        if alive_players:
                            winner = alive_players[0]
                            current_round.coop_winning_strategy_id = winner.id
                            current_round.coop_vote_points[winner.id] = 200
                            winner.score += 200
                        current_round.status = "coop_judgement"
                        print(f"API: Only {len(alive_players)} alive in coop, skipping voting")
                    else:
                        print("API: All strategies received. Advancing to COOP VOTING.")
                        current_round.status = "coop_voting"
                        current_round.vote_start_time = time.time()
                elif current_round.type == "last_stand":
                    print("API: All strategies received. Advancing to LAST STAND Judgement.")
                    current_round.status = "judgement"
                elif current_round.type == "sacrifice":
                    print("API: All strategies received. Advancing to SACRIFICE VOLUNTEER.")
                    current_round.status = "sacrifice_volunteer"
                elif current_round.type == "ranked":
                    print("API: All strategies received. Advancing to RANKED Judgement.")
                    current_round.status = "ranked_judgement"
                else:
                    print("API: All strategies received. Advancing to Judgement.")
                    current_round.status = "judgement"
            else:
                print("API: Waiting for others... Saving strategy.")
            
            return (True, {"status": "submitted"})
        
        def verify(game: GameState) -> bool:
            return (player_id in game.players and 
                    game.players[player_id].strategy == strategy)
        
        result = await update_game_with_retry(
            code, mutator, verify,
            error_message="Failed to submit strategy due to concurrent modifications"
        )
        
        # Spawn side effects after successful save
        if side_effects["spawn_judgement"]:
            print(f"API: Spawning EARLY JUDGEMENT for {player_id}")
            judge_single_player.spawn(code, player_id)
        elif side_effects["all_submitted"]:
            round_type = side_effects["round_type"]
            if round_type == "cooperative":
                generate_coop_strategy_images.spawn(code, get_game(code).current_round_idx)
                if side_effects["alive_count"] <= 1:
                    run_coop_judgement.spawn(code, get_game(code).current_round_idx)
            elif round_type == "last_stand":
                run_last_stand_judgement.spawn(code, get_game(code).current_round_idx)
            elif round_type == "ranked":
                run_ranked_judgement.spawn(code, get_game(code).current_round_idx)
            elif round_type not in ["sacrifice"]:  # sacrifice doesn't spawn judgement here
                run_round_judgement.spawn(code, get_game(code).current_round_idx)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"API: Submit Strategy EXCEPTION: {e}", flush=True)
        return JSONResponse(status_code=500, content={"detail": f"Internal Error: {str(e)}"})

@web_app.post("/api/submit_trap")
async def api_submit_trap(request: Request):
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")
    trap_text = data.get("trap_text", "")
    
    if not player_id:
        raise HTTPException(status_code=400, detail="Missing player_id")
    
    # Validate input length
    if len(trap_text) > MAX_TRAP_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Trap text too long (max {MAX_TRAP_TEXT_LENGTH} characters)")
    
    # Generate trap image first (before retry loop, as it's expensive)
    # We need to get the style theme from the game
    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    current_round = game.rounds[game.current_round_idx]
    themed_prompt = apply_style_theme(trap_text, current_round.style_theme)
    img_url = await generate_image_fal_async(themed_prompt, use_case="trap_image")
    
    def mutator(game: GameState):
        current_round = game.rounds[game.current_round_idx]
        
        # Check if already submitted (idempotent)
        if player_id in current_round.trap_proposals and current_round.trap_proposals[player_id] == trap_text:
            print(f"SUBMIT_TRAP: Trap already submitted for {player_id[:8]}...", flush=True)
            return (False, {"status": "trap_submitted"})
        
        current_round.trap_proposals[player_id] = trap_text
        if img_url:
            current_round.trap_images[player_id] = img_url
        
        alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
        if len(current_round.trap_proposals) >= len(alive_players):
            current_round.status = "trap_voting"
            current_round.vote_start_time = time.time()
        
        return (True, {"status": "trap_submitted"})
    
    def verify(game: GameState) -> bool:
        current_round = game.rounds[game.current_round_idx]
        return (player_id in current_round.trap_proposals and 
                current_round.trap_proposals[player_id] == trap_text)
    
    return await update_game_with_retry(
        code, mutator, verify,
        error_message="Failed to submit trap due to concurrent modifications"
    )

@web_app.post("/api/vote_trap")
async def api_vote_trap(request: Request):
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    max_retries = 10
    for attempt in range(max_retries):
        game = get_game(code)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        current_round = game.rounds[game.current_round_idx]

        # Check if already voted (idempotent - from previous retry)
        if voter_id in current_round.votes and current_round.votes[voter_id] == target_id:
            print(f"VOTE_TRAP: Vote already recorded for {voter_id[:8]}...", flush=True)
            return {"status": "voted"}

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
            current_round.submission_start_time = time.time()
            if winner_id in game.players:
                game.players[winner_id].score += 500

        save_game(game)

        # Wait with jitter before verification
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the vote was saved
        verification = get_game(code)
        if verification:
            v_round = verification.rounds[verification.current_round_idx]
            if voter_id in v_round.votes and v_round.votes[voter_id] == target_id:
                return {"status": "voted"}

        print(f"VOTE_TRAP: Race condition for {voter_id[:8]}..., retry {attempt+1}/{max_retries}", flush=True)
        backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
        await asyncio.sleep(min(backoff, 2.0))

    raise HTTPException(status_code=500, detail="Failed to record vote due to concurrent modifications")


@web_app.post("/api/vote_coop")
async def api_vote_coop(request: Request):
    """Handle cooperative round voting - vote for which strategy image looks best."""
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    # Prevent voting for self (check once before retry loop)
    if voter_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot vote for yourself")

    max_retries = 10
    for attempt in range(max_retries):
        game = get_game(code)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        current_round = game.rounds[game.current_round_idx]

        # Validate we're in coop_voting phase
        if current_round.status != "coop_voting":
            raise HTTPException(status_code=400, detail=f"Wrong phase: {current_round.status}")

        # Check if already voted (idempotent - from previous retry)
        if voter_id in current_round.coop_votes and current_round.coop_votes[voter_id] == target_id:
            print(f"COOP VOTE: Vote already recorded for {voter_id[:8]}...", flush=True)
            return {"status": "voted"}

        current_round.coop_votes[voter_id] = target_id
        print(f"COOP VOTE: {voter_id[:8]}... voted for {target_id[:8]}...", flush=True)

        # Check if all alive players in lobby have voted
        alive_players = [p for p in game.players.values() if p.is_alive and p.in_lobby]
        if len(current_round.coop_votes) >= len(alive_players):
            print("COOP VOTE: All votes in, tallying...", flush=True)
            tally_coop_votes_and_transition(game, current_round)
            save_game(game)
            run_coop_judgement.spawn(code, game.current_round_idx)
        else:
            save_game(game)

        # Wait with jitter before verification
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the vote was saved
        verification = get_game(code)
        if verification:
            v_round = verification.rounds[verification.current_round_idx]
            if voter_id in v_round.coop_votes and v_round.coop_votes[voter_id] == target_id:
                return {"status": "voted"}

        print(f"COOP VOTE: Race condition for {voter_id[:8]}..., retry {attempt+1}/{max_retries}", flush=True)
        backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
        await asyncio.sleep(min(backoff, 2.0))

    raise HTTPException(status_code=500, detail="Failed to record vote due to concurrent modifications")


@web_app.post("/api/next_round")
async def api_next_round(request: Request):
    code = request.query_params.get("code")
    game = get_game(code)
    if not game: 
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Guard: only allow advancing from playing state
    if game.status != "playing":
        raise HTTPException(status_code=400, detail=f"Cannot advance round: game is in '{game.status}' state")
    
    # Guard: current round must be in results state
    if game.rounds and game.current_round_idx >= 0:
        current_round = game.rounds[game.current_round_idx]
        if current_round.status != "results":
            raise HTTPException(status_code=400, detail=f"Cannot advance round: current round is in '{current_round.status}' state, not 'results'")

    next_idx = game.current_round_idx + 1
    if next_idx >= game.max_rounds:
        game.status = "finished"
        # Find winner
        sorted_players = sorted(game.players.values(), key=lambda p: p.score, reverse=True)
        if sorted_players:
            game.winner_id = sorted_players[0].id

        # Videos should already be pre-generated from round 1
        # Only spawn generation if not already done (fallback)
        if game.videos_status == "pending":
            print(f"API: Game finished but videos not pre-generated, spawning now for {code}", flush=True)
            game.videos_status = "generating"
            game.videos_started_at = time.time()
            save_game(game)
            prewarm_player_videos.spawn(code)
        else:
            print(f"API: Game finished, videos already {game.videos_status} for {code}", flush=True)
            save_game(game)

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
        new_round.submission_start_time = time.time()  # Start timer for volunteer phase
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
            # Use asyncio.to_thread to avoid blocking the event loop
            new_round.scenario_text = await asyncio.to_thread(generate_scenario_llm, next_idx + 1, game.max_rounds)

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

    # Check if generation is stuck (past timeout)
    if game.videos_status == "generating":
        if is_video_generation_stuck(game):
            # Generation appears stuck - allow retry
            elapsed = time.time() - (game.videos_started_at or 0)
            print(f"API: Video generation stuck ({elapsed:.0f}s elapsed), allowing retry for {code}", flush=True)
        else:
            # Still within timeout window - don't allow duplicate spawn
            return {"status": "already_generating"}

    # Reset status and spawn new generation
    game.videos_status = "generating"
    game.videos_started_at = time.time()
    game.player_winner_videos = {}  # Clear any partial results
    game.player_loser_videos = {}
    save_game(game)
    print(f"API: Retrying player video generation for {code}", flush=True)
    prewarm_player_videos.spawn(code)
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


# --- DEBUG DATA ---

# Realistic scenarios for each round type
DEBUG_SCENARIOS = {
    "survival": [
        "The laboratory's emergency lights flicker as a containment breach alarm blares. Through the reinforced glass, you see the experimental bioweapon—a writhing mass of tentacles and teeth—dissolving through the steel doors. You have 30 seconds before it reaches your section.",
        "You're trapped in a flooding underground bunker. The water is rising fast, already at your waist. The only exit is a narrow maintenance shaft above you, but something with glowing eyes is moving in the darkness up there.",
        "The autonomous military drone has gone haywire and identified everyone in the shopping mall as hostile combatants. Its targeting laser just swept across your chest. You're in the food court, surrounded by overturned tables and screaming civilians.",
        "A massive earthquake has trapped you in a collapsed parking garage. Your leg is pinned under debris, and you can smell gas leaking from ruptured pipes. In the distance, you hear the unmistakable crackling of spreading fire.",
        "The cruise ship is sinking after hitting something massive in the water. As you reach the deck, you see lifeboats being torn apart by tentacles the size of tree trunks. The creature is circling the ship.",
    ],
    "blind_architect": [
        "The trap activates with a mechanical whir. The room transforms into a deadly obstacle course of the previous player's design.",
        "Your opponent's sadistic creation springs to life around you. Every surface, every shadow could be lethal.",
        "The architect's twisted imagination has been made real. You must survive what another player dreamed up to kill you.",
    ],
    "cooperative": [
        "A nuclear reactor is in meltdown. The control room is filled with radiation, and three separate systems need to be manually overridden simultaneously from different locations. One person alone cannot save everyone—you need a coordinated team effort.",
        "A bioweapon has been released in the subway system. The ventilation system can purge it, but it requires someone to hold open the emergency doors while others reach the control room. Whoever holds the doors will be exposed.",
        "The space station's hull has been breached in multiple locations. You need to seal all breaches within 60 seconds or everyone dies. There are four breaches and four of you. Each must handle their section alone.",
    ],
    "sacrifice": [
        "The escape pod only has room for all but one person. The hatch will seal automatically in 60 seconds. Someone must stay behind with the creatures.",
        "The bomb can only be disarmed by someone holding both kill switches simultaneously—but they're positioned on opposite sides of a blast door that will slam shut permanently. Whoever disarms it is trapped on the wrong side.",
        "The bridge across the chasm is collapsing. It can only hold the weight of your group if one person stays behind to counterbalance the other end. That person will fall when the others reach safety.",
    ],
    "last_stand": [
        "FINAL LEVEL: The AI that has been hunting you through the simulation reveals its true form—a writhing mass of corrupted code made manifest. It has learned from every death, adapted to every strategy. This is your last chance. Survival rate: approximately 15%.",
        "FINAL LEVEL: The dimensional rift is tearing reality apart. Every monster from every previous round is converging on your position simultaneously. There's no escape, no clever tricks—only survival through sheer will and desperate action.",
        "FINAL LEVEL: The facility's self-destruct sequence has been activated by the rogue AI. You're in the deepest sublevel. The elevator is destroyed. The emergency stairs are flooded with neurotoxin. And something is hunting you through the ventilation shafts.",
    ],
    "ranked": [
        "A category 5 hurricane is making landfall in 10 minutes. You're on the 50th floor of an unstable high-rise with broken elevators. The stairwells are partially collapsed. Other survivors are panicking and fighting over limited resources.",
        "The zoo's power grid failed during a thunderstorm, and every enclosure has opened simultaneously. Lions, bears, venomous snakes, and a very angry hippopotamus are now roaming freely. You're in the reptile house.",
        "An experimental AI has taken control of a smart home while you're trapped inside. It controls the locks, the gas lines, the electricity, and has connected itself to your pacemaker. It wants to 'optimize human efficiency.'",
    ],
}

# Realistic strategies players might submit
DEBUG_STRATEGIES = [
    "I grab the fire extinguisher and spray it at the creature's eyes to blind it, then sprint for the emergency exit while it's disoriented. I'll use the extinguisher as a blunt weapon if it gets too close.",
    "I stay completely still and control my breathing. Most predators detect movement and body heat. I'll wait for it to pass, then move silently toward the ventilation shaft.",
    "I start a fire using my lighter and some papers to create a distraction. While the sprinklers activate and chaos ensues, I slip away through the confusion.",
    "I fashion a makeshift weapon from a broken chair leg and a piece of sharp metal. Then I position myself in a narrow doorway where only one can attack at a time, giving me the advantage.",
    "I remember there's a chemical storage closet nearby. I'll mix ammonia and bleach to create a toxic cloud, then seal myself in the airtight supply room while the gas clears the area.",
    "I play dead, covering myself with debris and slowing my heartbeat through meditation techniques I learned. Once the immediate threat passes, I'll reassess my options.",
    "I locate the building's PA system and blast heavy metal at maximum volume to disorient the creature, then use the noise cover to reach the roof for helicopter extraction.",
    "I sacrifice my jacket to create a decoy, stuffing it and making it look human. While the creature attacks it, I make my escape through the floor grating.",
]

# Realistic trap proposals for blind architect mode
DEBUG_TRAPS = [
    "A room where the floor tiles randomly become electrified. Safe tiles are marked, but the pattern changes every 10 seconds. In the center, a pedestal with the exit key slowly descends into the floor.",
    "A library where the books are spring-loaded with poison darts. The exit door requires reading a specific passage from a book—but which one? Choose wrong and 50 darts fire simultaneously.",
    "A swimming pool filled with clear acid that looks exactly like water. The real exit is at the bottom, but there's also a fake door on the surface that locks you in when touched.",
    "A room full of identical pressure plates. Only one path is safe, revealed only by ultraviolet light from a blacklight mounted on a ceiling fan spinning at high speed.",
    "A children's playroom where every toy is a weapon. The ball pit hides spinning blades. The slide ends in a vat of acid. The exit? Through the mouth of a giant animatronic clown that may or may not bite.",
]

# Death reasons
DEBUG_DEATH_REASONS = [
    "The creature was faster than anticipated. Your screams echoed briefly through the facility.",
    "A noble effort, but ultimately futile. The trap's designer knew exactly what you would try.",
    "You hesitated for one second too long. In survival, hesitation is death.",
    "Your strategy backfired catastrophically. The last thing you saw was your own reflection in its eyes.",
    "The laws of physics disagreed with your plan. Reality is often disappointing.",
    "You forgot about the second threat. Always check your six.",
    "A valiant attempt, but this scenario was designed by someone who wanted you dead.",
]

# Survival reasons
DEBUG_SURVIVAL_REASONS = [
    "Against all odds, your quick thinking and decisive action paid off. You live to face another round.",
    "The judges were impressed by your creativity and ruthless pragmatism. Well played.",
    "Your strategy exploited a weakness nobody else noticed. Survival through superior observation.",
    "You got lucky—but in survival situations, luck is just preparation meeting opportunity.",
    "Cold, calculated, effective. You treated survival like the science it is.",
    "Your willingness to do what others wouldn't is exactly what kept you breathing.",
    "The creature never stood a chance against someone who thinks like you do.",
]

# Ranked commentary
DEBUG_RANKED_COMMENTARY = [
    "An absolutely masterful strategy that demonstrated both creativity and practical thinking.",
    "Solid approach with good risk assessment, though slightly predictable in execution.",
    "Adequate survival instincts, but lacked the innovative spark of the top performers.",
    "Points for effort, but this strategy had several critical flaws that would prove fatal.",
    "The enthusiasm was there, but the execution plan reads like a recipe for disaster.",
]

# Sacrifice speeches
DEBUG_SACRIFICE_SPEECHES = [
    "Someone has to stay behind, and I've lived more than most of you. Take care of each other. Now GO, before I change my mind and push one of you off this thing myself.",
    "I always wondered how I'd go out. Turns out it's saving a bunch of strangers I met in a death game. Poetic, really. Tell my cat I'm sorry I missed dinner.",
    "You want a volunteer? Fine. I volunteer. But you all better survive, because if I sacrifice myself and you idiots die anyway, I'm haunting every single one of you.",
    "My grandmother always said I'd die doing something stupid but heroic. She was right about everything else, why not this? See you on the other side, losers.",
]

# SVG placeholder images as data URIs
def _create_debug_svg(text: str, bg_color: str = "#1a1a1a", text_color: str = "#666", icon: str = "⚠️") -> str:
    """Create an SVG placeholder image as a data URI."""
    import base64
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="{bg_color}"/>
  <text x="256" y="200" font-family="Arial, sans-serif" font-size="80" fill="{text_color}" text-anchor="middle">{icon}</text>
  <text x="256" y="300" font-family="monospace" font-size="24" fill="{text_color}" text-anchor="middle">[DEBUG MODE]</text>
  <text x="256" y="340" font-family="monospace" font-size="18" fill="#444" text-anchor="middle">{text}</text>
</svg>'''
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"

# Pre-generated placeholder images for different contexts
DEBUG_IMAGES = {
    "scenario": _create_debug_svg("Scenario Image", "#1a0a0a", "#a44", "💀"),
    "result_survived": _create_debug_svg("Survived", "#0a1a0a", "#4a4", "✓"),
    "result_died": _create_debug_svg("Eliminated", "#1a0a0a", "#a44", "✗"),
    "trap": _create_debug_svg("Trap Design", "#1a0a1a", "#a4a", "⚙️"),
    "strategy": _create_debug_svg("Strategy Image", "#0a0a1a", "#44a", "🎯"),
    "sacrifice": _create_debug_svg("Final Moment", "#1a1a0a", "#aa4", "🔥"),
}


# --- DEBUG ENDPOINT ---

@web_app.post("/api/debug_skip_to_state")
async def api_debug_skip_to_state(request: Request):
    """Debug endpoint to skip to a specific game state with dummy data."""
    code = request.query_params.get("code")
    data = await request.json()

    player_id = data.get("player_id")
    game_status = data.get("game_status", "playing")  # lobby, playing, finished
    round_type = data.get("round_type", "survival")
    round_status = data.get("round_status", "scenario")
    round_number = data.get("round_number", 1)
    num_dummy_players = data.get("num_dummy_players", 0)
    dummy_character_image = data.get("dummy_character_image")  # Data URI for placeholder

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if player_id not in game.players:
        raise HTTPException(status_code=404, detail="Player not found")

    print(f"DEBUG: Skipping to state - game_status={game_status}, round_type={round_type}, round_status={round_status}, round={round_number}", flush=True)

    # Add dummy players if requested
    dummy_names = ["DebugBot1", "DebugBot2", "DebugBot3", "DebugBot4", "DebugBot5",
                   "DebugBot6", "DebugBot7", "DebugBot8", "DebugBot9", "DebugBot10"]
    for i in range(num_dummy_players):
        dummy_id = f"dummy_{i}_{uuid.uuid4().hex[:6]}"
        dummy_player = Player(
            id=dummy_id,
            name=dummy_names[i % len(dummy_names)],
            score=random.randint(0, 500),
            is_admin=False,
            is_alive=True,
            in_lobby=True,
            character_description="Debug test character",
            character_image_url=dummy_character_image,
            last_active=time.time()
        )
        game.players[dummy_id] = dummy_player
        print(f"DEBUG: Added dummy player {dummy_player.name}", flush=True)

    # Ensure all players have character images (use dummy if missing)
    for pid, p in game.players.items():
        if not p.character_image_url and dummy_character_image:
            p.character_image_url = dummy_character_image
        p.in_lobby = True  # Mark all as in lobby
        p.is_alive = True  # Everyone alive by default
        p.last_active = time.time()

    # Set game status
    game.status = game_status

    if game_status == "lobby":
        # Just set status to lobby and save
        game.rounds = []
        game.current_round_idx = -1
        save_game(game)
        return {"status": "ok", "message": "Skipped to lobby state"}

    if game_status == "finished":
        # Create finished state with winner
        sorted_players = sorted(game.players.values(), key=lambda p: p.score, reverse=True)
        if sorted_players:
            game.winner_id = sorted_players[0].id
        game.videos_status = "pending"
        game.current_round_idx = game.max_rounds - 1  # Set to last round

        # Create a dummy final round for results
        if not game.rounds:
            game.rounds = [_create_debug_round(i + 1, "survival", "results") for i in range(game.max_rounds)]
        game.current_round_idx = len(game.rounds) - 1

        save_game(game)
        return {"status": "ok", "message": "Skipped to finished state"}

    # For "playing" status, create the round structure
    game.max_rounds = max(game.max_rounds, round_number)
    game.current_round_idx = round_number - 1

    # Create rounds up to the current one
    while len(game.rounds) < round_number:
        past_round_num = len(game.rounds) + 1
        past_round = _create_debug_round(past_round_num, "survival", "results")
        game.rounds.append(past_round)

    # Create the current round with proper type and status
    current_round = _create_debug_round(round_number, round_type, round_status)

    # Set up round-specific dummy data based on status
    _setup_round_dummy_data(current_round, game, round_status)

    game.rounds[round_number - 1] = current_round

    save_game(game)
    return {"status": "ok", "message": f"Skipped to round {round_number} ({round_type}/{round_status})"}


def _create_debug_round(number: int, round_type: str, status: str) -> Round:
    """Create a debug round with realistic scenario data."""
    style_theme = random.choice(IMAGE_STYLE_THEMES)

    # Get a random realistic scenario for this round type
    scenarios_for_type = DEBUG_SCENARIOS.get(round_type, DEBUG_SCENARIOS["survival"])
    scenario_text = random.choice(scenarios_for_type)

    # Use realistic system messages based on round progression
    system_messages = {
        1: "SYSTEM BOOT // LEVEL 1 INITIALIZED",
        2: "CALIBRATION MODE // ANOMALIES DETECTED",
        3: "WARNING: CORRUPTION AT 50% // REALITY UNSTABLE",
        4: "CRITICAL ERROR // SYSTEM DEGRADATION",
        5: "EXIT PROTOCOL // FINAL LEVEL"
    }

    # Override for specific round types
    type_messages = {
        "blind_architect": "SECURITY BREACH DETECTED // ARCHITECT PROTOCOL ACTIVATED",
        "cooperative": "CRITICAL ERROR // COLLABORATIVE SUBROUTINE REQUIRED",
        "sacrifice": "CRITICAL FAILURE // ONE MUST FALL FOR OTHERS TO SURVIVE",
        "last_stand": "EXIT PROTOCOL // FINAL LEVEL // MAXIMUM DIFFICULTY",
        "ranked": "PERFORMANCE EVALUATION // SURVIVAL EFFICIENCY RANKING PROTOCOL",
    }

    system_message = type_messages.get(round_type) or system_messages.get(number, f"LEVEL {number} // SURVIVAL PROTOCOL ACTIVE")

    return Round(
        number=number,
        type=round_type,
        scenario_text=scenario_text,
        scenario_image_url=DEBUG_IMAGES["scenario"],  # Use placeholder image
        status=status,
        style_theme=style_theme,
        system_message=system_message
    )


def _setup_round_dummy_data(current_round: Round, game: GameState, status: str):
    """Set up realistic dummy data specific to the round status."""
    player_ids = list(game.players.keys())

    # Shuffle strategies so each player gets a different one
    shuffled_strategies = random.sample(DEBUG_STRATEGIES, min(len(DEBUG_STRATEGIES), len(player_ids)))

    if status in ["trap_voting", "trap_creation"]:
        # Blind architect: create realistic traps with images
        shuffled_traps = random.sample(DEBUG_TRAPS, min(len(DEBUG_TRAPS), len(player_ids)))
        for i, pid in enumerate(player_ids):
            trap_idx = i % len(shuffled_traps)
            current_round.trap_proposals[pid] = shuffled_traps[trap_idx]
            current_round.trap_images[pid] = DEBUG_IMAGES["trap"]

    elif status == "coop_voting":
        # Cooperative: create realistic strategies with images
        for i, pid in enumerate(player_ids):
            strategy_idx = i % len(shuffled_strategies)
            game.players[pid].strategy = shuffled_strategies[strategy_idx]
            current_round.strategy_images[pid] = DEBUG_IMAGES["strategy"]

    elif status in ["sacrifice_volunteer", "sacrifice_voting"]:
        # Sacrifice: set up volunteers realistically
        if status == "sacrifice_voting" and len(player_ids) >= 2:
            # Add some volunteers (typically 1-2 brave souls)
            current_round.sacrifice_volunteers[player_ids[0]] = True
            if len(player_ids) >= 3:
                current_round.sacrifice_volunteers[player_ids[1]] = True

    elif status == "sacrifice_submission":
        # Need a martyr with realistic context
        if player_ids:
            current_round.martyr_id = player_ids[0]
            # Set up volunteers that led to this martyr
            current_round.sacrifice_volunteers[player_ids[0]] = True
            # Set up votes pointing to martyr
            for pid in player_ids:
                current_round.sacrifice_votes[pid] = player_ids[0]

    elif status == "sacrifice_judgement":
        # Martyr already submitted their speech
        if player_ids:
            current_round.martyr_id = player_ids[0]
            current_round.martyr_speech = random.choice(DEBUG_SACRIFICE_SPEECHES)
            current_round.sacrifice_volunteers[player_ids[0]] = True
            for pid in player_ids:
                current_round.sacrifice_votes[pid] = player_ids[0]

    elif status == "last_stand_revival":
        # Need some survivors and dead players with realistic data
        if len(player_ids) >= 2:
            # First half alive, second half dead
            mid = max(1, len(player_ids) // 2)
            for i, pid in enumerate(player_ids):
                p = game.players[pid]
                strategy_idx = i % len(shuffled_strategies)
                p.strategy = shuffled_strategies[strategy_idx]

                if i < mid:
                    p.is_alive = True
                    p.survival_reason = random.choice(DEBUG_SURVIVAL_REASONS)
                    p.result_image_url = DEBUG_IMAGES["result_survived"]
                else:
                    p.is_alive = False
                    p.death_reason = random.choice(DEBUG_DEATH_REASONS)
                    p.result_image_url = DEBUG_IMAGES["result_died"]

    elif status == "results":
        # Create realistic results with varied outcomes
        for i, pid in enumerate(player_ids):
            p = game.players[pid]
            strategy_idx = i % len(shuffled_strategies)
            p.strategy = shuffled_strategies[strategy_idx]

            if i % 2 == 0:
                p.is_alive = True
                p.survival_reason = random.choice(DEBUG_SURVIVAL_REASONS)
                p.result_image_url = DEBUG_IMAGES["result_survived"]
                p.score += 100
            else:
                p.is_alive = False
                p.death_reason = random.choice(DEBUG_DEATH_REASONS)
                p.result_image_url = DEBUG_IMAGES["result_died"]

        # For ranked results, add ranking data
        if current_round.type == "ranked":
            for i, pid in enumerate(player_ids):
                rank = i + 1
                current_round.ranked_results[pid] = rank
                # Scoring based on rank
                if len(player_ids) >= 4:
                    points = {1: 300, 2: 200, 3: 100, 4: 50}.get(rank, 25)
                elif len(player_ids) == 3:
                    points = {1: 250, 2: 125, 3: 25}.get(rank, 25)
                else:
                    points = {1: 200, 2: 50}.get(rank, 25)
                current_round.ranked_points[pid] = points
                commentary_idx = min(i, len(DEBUG_RANKED_COMMENTARY) - 1)
                current_round.ranked_commentary[pid] = DEBUG_RANKED_COMMENTARY[commentary_idx]
                game.players[pid].is_alive = True  # Everyone survives in ranked
                game.players[pid].survival_reason = DEBUG_RANKED_COMMENTARY[commentary_idx]
                game.players[pid].result_image_url = DEBUG_IMAGES["result_survived"]

    elif status == "ranked_judgement":
        # Set up strategies for ranked judgement
        for i, pid in enumerate(player_ids):
            strategy_idx = i % len(shuffled_strategies)
            game.players[pid].strategy = shuffled_strategies[strategy_idx]

    elif status in ["strategy", "judgement", "coop_judgement", "revival_judgement"]:
        # Add realistic strategies for strategy-related statuses
        for i, pid in enumerate(player_ids):
            if status != "strategy":  # Don't pre-fill strategies in strategy phase
                strategy_idx = i % len(shuffled_strategies)
                game.players[pid].strategy = shuffled_strategies[strategy_idx]


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

    volunteer_ids = [pid for pid, v in current_round.sacrifice_volunteers.items() if v]
    volunteer_count = len(volunteer_ids)

    # If exactly 1 volunteer, skip voting - they're automatically the martyr
    if volunteer_count == 1:
        martyr_id = volunteer_ids[0]
        current_round.martyr_id = martyr_id
        current_round.status = "sacrifice_submission"
        current_round.submission_start_time = time.time()  # Start timer for speech
        save_game(game)
        print(f"SACRIFICE: Only 1 volunteer ({game.players[martyr_id].name}), skipping voting", flush=True)
        return {"status": "skipped_to_submission", "martyr_id": martyr_id, "volunteer_count": 1}

    # Multiple volunteers (or none) - go to voting phase
    current_round.status = "sacrifice_voting"
    current_round.vote_start_time = time.time()
    save_game(game)

    print(f"SACRIFICE: Advanced to voting with {volunteer_count} volunteers", flush=True)
    return {"status": "advanced", "volunteer_count": volunteer_count}


@web_app.post("/api/vote_sacrifice")
async def api_vote_sacrifice(request: Request):
    """Vote for who becomes the martyr."""
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    # Can't vote for yourself (check once before retry loop)
    if voter_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot vote for yourself")

    max_retries = 10
    for attempt in range(max_retries):
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

        # If there are volunteers, can only vote for volunteers
        if current_round.sacrifice_volunteers and target_id not in current_round.sacrifice_volunteers:
            raise HTTPException(status_code=400, detail="Can only vote for volunteers")

        # Check if already voted (idempotent - from previous retry)
        if voter_id in current_round.sacrifice_votes and current_round.sacrifice_votes[voter_id] == target_id:
            print(f"SACRIFICE VOTE: Vote already recorded for {voter_id[:8]}...", flush=True)
            return {"status": "vote_recorded", "votes_cast": len(current_round.sacrifice_votes)}

        current_round.sacrifice_votes[voter_id] = target_id

        # Check if all players who CAN vote have voted
        active_players = [p for p in game.players.values() if p.is_alive]
        volunteer_ids = set(pid for pid, v in current_round.sacrifice_volunteers.items() if v)

        # Determine who can actually cast a vote
        voters_who_can_vote = []
        for p in active_players:
            if volunteer_ids:
                can_vote = any(vid != p.id for vid in volunteer_ids)
            else:
                can_vote = len(active_players) > 1
            if can_vote:
                voters_who_can_vote.append(p)

        all_voted = len(current_round.sacrifice_votes) >= len(voters_who_can_vote)
        martyr_chosen = False
        martyr_id = None

        if all_voted:
            vote_counts = {}
            for target in current_round.sacrifice_votes.values():
                vote_counts[target] = vote_counts.get(target, 0) + 1

            martyr_id = max(vote_counts, key=vote_counts.get)
            current_round.martyr_id = martyr_id
            current_round.status = "sacrifice_submission"
            current_round.submission_start_time = time.time()
            martyr_chosen = True
            print(f"SACRIFICE: {game.players[martyr_id].name} chosen as martyr", flush=True)

        save_game(game)

        # Wait with jitter before verification
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the vote was saved
        verification = get_game(code)
        if verification:
            v_round = verification.rounds[verification.current_round_idx]
            if voter_id in v_round.sacrifice_votes and v_round.sacrifice_votes[voter_id] == target_id:
                if martyr_chosen:
                    return {"status": "martyr_chosen", "martyr_id": martyr_id}
                return {"status": "vote_recorded", "votes_cast": len(v_round.sacrifice_votes)}

        print(f"SACRIFICE VOTE: Race condition for {voter_id[:8]}..., retry {attempt+1}/{max_retries}", flush=True)
        backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
        await asyncio.sleep(min(backoff, 2.0))

    raise HTTPException(status_code=500, detail="Failed to record vote due to concurrent modifications")


@web_app.post("/api/submit_sacrifice_speech")
async def api_submit_sacrifice_speech(request: Request):
    """Martyr submits their heroic death speech."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")
    speech = data.get("speech", "")
    
    # Validate input length
    if len(speech) > MAX_SPEECH_LENGTH:
        raise HTTPException(status_code=400, detail=f"Speech too long (max {MAX_SPEECH_LENGTH} characters)")

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
    run_sacrifice_judgement.spawn(code, game.current_round_idx)

    return {"status": "speech_submitted"}


# --- LAST STAND REVIVAL ENDPOINTS ---

@web_app.post("/api/vote_revival")
async def api_vote_revival(request: Request):
    """Survivor votes to revive a dead player (must be unanimous)."""
    code = request.query_params.get("code")
    data = await request.json()
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")

    max_retries = 10
    for attempt in range(max_retries):
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

        # Check if already voted (idempotent - from previous retry)
        if voter_id in current_round.revival_votes and current_round.revival_votes[voter_id] == target_id:
            print(f"REVIVAL VOTE: Vote already recorded for {voter_id[:8]}...", flush=True)
            survivors = [p for p in game.players.values() if p.is_alive]
            return {"status": "vote_recorded", "votes_cast": len(current_round.revival_votes), "survivors": len(survivors)}

        current_round.revival_votes[voter_id] = target_id

        # Check if all survivors have voted
        survivors = [p for p in game.players.values() if p.is_alive]
        all_voted = len(current_round.revival_votes) >= len(survivors)
        result = None

        print(f"REVIVAL: {voter.name} voted for {target.name}. {len(current_round.revival_votes)}/{len(survivors)} voted", flush=True)

        if all_voted:
            votes = list(current_round.revival_votes.values())
            unique_targets = set(votes)

            if len(unique_targets) == 1 and len(votes) == len(survivors):
                revived_id = votes[0]
                current_round.revived_player_id = revived_id
                current_round.status = "revival_judgement"
                revived_name = game.players[revived_id].name
                print(f"REVIVAL: Unanimous vote for {revived_name}! Auto-advancing to judgement", flush=True)
                result = {"status": "unanimous", "revived": True, "revived_player_id": revived_id, "auto_advanced": True}
            else:
                current_round.status = "results"
                print(f"REVIVAL: Not unanimous ({len(unique_targets)} different targets), auto-advancing to results", flush=True)
                result = {"status": "not_unanimous", "revived": False, "auto_advanced": True}

        save_game(game)

        # Spawn revival judgement if unanimous (after save)
        if result and result.get("status") == "unanimous":
            run_revival_judgement.spawn(code, game.current_round_idx)

        # Wait with jitter before verification
        jitter = random.uniform(0.05, 0.15)
        await asyncio.sleep(0.1 + jitter)

        # Verify the vote was saved
        verification = get_game(code)
        if verification:
            v_round = verification.rounds[verification.current_round_idx]
            if voter_id in v_round.revival_votes and v_round.revival_votes[voter_id] == target_id:
                if result:
                    return result
                return {"status": "vote_recorded", "votes_cast": len(v_round.revival_votes), "survivors": len(survivors)}

        print(f"REVIVAL VOTE: Race condition for {voter_id[:8]}..., retry {attempt+1}/{max_retries}", flush=True)
        backoff = (0.15 * (2 ** attempt)) + random.uniform(0, 0.1)
        await asyncio.sleep(min(backoff, 2.0))

    raise HTTPException(status_code=500, detail="Failed to record vote due to concurrent modifications")


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
        run_revival_judgement.spawn(code, game.current_round_idx)
        return {"status": "unanimous", "revived": True, "revived_player_id": revived_id}
    else:
        # Not unanimous, skip revival
        current_round.status = "results"
        save_game(game)
        print(f"REVIVAL: Not unanimous ({len(unique_targets)} different targets), no revival", flush=True)
        return {"status": "not_unanimous", "revived": False}


# --- SACRIFICE JUDGEMENT ASYNC FUNCTION ---

@app.function(image=image, secrets=secrets)
def run_sacrifice_judgement(game_code: str, expected_round_idx: int = -1):
    """Judge the martyr's death - was it epic or lame?"""
    import json
    import asyncio

    async def judge_sacrifice():
        game = get_game(game_code)
        if not game:
            print(f"SACRIFICE JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"SACRIFICE JUDGEMENT: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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

        # Generate images for ALL players in parallel
        image_tasks = []
        player_ids = []

        # Martyr image (from LLM visual_prompt)
        martyr_prompt = apply_style_theme(visual_prompt, current_round.style_theme)
        image_tasks.append(generate_image_fal_async(martyr_prompt))
        player_ids.append(("martyr", martyr_id))

        # Get scenario hint for survivor/death images
        scenario_hint = current_round.scenario_text[:150] if current_round.scenario_text else "a dangerous situation"

        if epic:
            # Epic death: generate survivor images for all alive players
            for pid, p in game.players.items():
                if pid != martyr_id and p.is_alive:
                    survivor_prompt = prompts.format_prompt(
                        prompts.SACRIFICE_SURVIVOR_IMAGE,
                        player_name=p.name,
                        scenario_hint=scenario_hint
                    )
                    themed = apply_style_theme(survivor_prompt, current_round.style_theme)
                    image_tasks.append(generate_image_fal_async(themed))
                    player_ids.append(("survivor", pid))
        else:
            # Lame death: generate death images for all other players
            for pid, p in game.players.items():
                if pid != martyr_id:
                    death_prompt = prompts.format_prompt(
                        prompts.SACRIFICE_FAILED_DEATH_IMAGE,
                        player_name=p.name,
                        scenario_hint=scenario_hint
                    )
                    themed = apply_style_theme(death_prompt, current_round.style_theme)
                    image_tasks.append(generate_image_fal_async(themed))
                    player_ids.append(("failed", pid))

        # Run all image generation in parallel
        print(f"SACRIFICE JUDGEMENT: Generating {len(image_tasks)} images in parallel", flush=True)
        image_results = await asyncio.gather(*image_tasks)

        # Assign images to players
        for (role, pid), image_url in zip(player_ids, image_results):
            if image_url:
                game.players[pid].result_image_url = image_url
                if role == "martyr":
                    current_round.martyr_image_url = image_url

        # Store results
        current_round.martyr_epic = epic
        current_round.martyr_reason = reason

        # Apply consequences
        martyr.is_alive = False
        martyr.death_reason = reason

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

        # Trigger video pre-generation on round 1 results (only once)
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

        print(f"SACRIFICE JUDGEMENT: Complete!", flush=True)

    asyncio.run(judge_sacrifice())


async def judge_sacrifice_llm_async(speech: str, martyr_name: str):
    """Judge how epic the martyr's death was."""
    import re
    import httpx

    prompt = prompts.format_prompt(
        prompts.SACRIFICE_JUDGEMENT,
        martyr_name=martyr_name,
        speech=speech
    )

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
        return prompts.FALLBACK_SACRIFICE_JUDGEMENT


# --- LAST STAND HARSH JUDGEMENT ---

@app.function(image=image, secrets=secrets)
def run_last_stand_judgement(game_code: str, expected_round_idx: int = -1):
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

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"LAST STAND JUDGEMENT: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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
            current_round.vote_start_time = time.time()
            print(f"LAST STAND: {len(survivors)} survivors, {len(dead_players)} dead - entering revival phase", flush=True)
        else:
            # Skip revival - either everyone survived or everyone died
            current_round.status = "results"
            print(f"LAST STAND: Skipping revival (survivors={len(survivors)}, dead={len(dead_players)})", flush=True)

        save_game(game)

        # Trigger video pre-generation on round 1 results (only once)
        # Note: This runs after save, for both revival and non-revival paths
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

        print(f"LAST STAND JUDGEMENT: Complete!", flush=True)

    asyncio.run(run_all_judgements())


async def judge_strategy_harsh_async(scenario: str, strategy: str):
    """HARSH version of judgement for Last Stand - EVIL SANTA edition."""
    import re
    import httpx

    prompt = prompts.format_prompt(
        prompts.LAST_STAND_JUDGEMENT,
        scenario=scenario,
        strategy=strategy
    )

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
        return prompts.FALLBACK_LAST_STAND_JUDGEMENT


# --- REVIVAL JUDGEMENT ---

@app.function(image=image, secrets=secrets)
def run_revival_judgement(game_code: str, expected_round_idx: int = -1):
    """Re-judge the revived player with a bonus for teamwork."""
    import json
    import asyncio

    async def do_revival_judgement():
        game = get_game(game_code)
        if not game:
            print(f"REVIVAL JUDGEMENT: Game {game_code} not found!", flush=True)
            return

        # Verify we're still on the expected round
        if expected_round_idx >= 0 and game.current_round_idx != expected_round_idx:
            print(f"REVIVAL JUDGEMENT: Round mismatch! Expected {expected_round_idx}, got {game.current_round_idx}. Aborting.", flush=True)
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

        # Trigger video pre-generation on round 1 results (only once)
        if game.current_round_idx == 0:
            maybe_spawn_video_prewarm(game)

        print(f"REVIVAL JUDGEMENT: Complete!", flush=True)

    asyncio.run(do_revival_judgement())


async def judge_strategy_revival_async(scenario: str, strategy: str, player_name: str):
    """Judge with slight leniency for revived player - EVIL SANTA edition."""
    import re
    import httpx

    prompt = prompts.format_prompt(
        prompts.REVIVAL_JUDGEMENT,
        player_name=player_name,
        scenario=scenario,
        strategy=strategy
    )

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
        return prompts.FALLBACK_REVIVAL_JUDGEMENT


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
@modal.asgi_app(label="survaive-game")
def fastapi_app():
    return web_app


