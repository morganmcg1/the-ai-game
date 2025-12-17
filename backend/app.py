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


def apply_style_theme(prompt: str, style_theme: str | None) -> str:
    """Append the round's style theme to an image prompt for visual consistency."""
    if style_theme:
        return f"{prompt}, in the style of {style_theme}"
    return prompt


# --- Image & Model Definitions ---
image = modal.Image.debian_slim().pip_install(
    "pydantic",
    "shortuuid",
    "requests",
    "openai",
    "fastapi[standard]",
    "httpx"  # For async HTTP requests
).add_local_dir("frontend/dist", remote_path="/assets")

app = modal.App("death-by-ai-clone", image=image)

# --- Clients ---
def get_llm_client():
    import openai
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
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
            model="moonshotai/kimi-k2-0905",
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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshotai/kimi-k2-0905",
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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshotai/kimi-k2-0905",
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


async def generate_image_fal_async(prompt: str):
    """Async version of generate_image_fal for parallel execution."""
    import httpx

    url = "https://fal.run/fal-ai/flux/krea"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "image_size": "landscape_4_3",
        "num_inference_steps": 28
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
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

    url = "https://fal.run/fal-ai/flux/krea"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": full_character_prompt,
        "image_size": "square",  # Square for avatars
        "num_inference_steps": 28
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
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
            model="moonshotai/kimi-k2-0905",
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

    prompt = f"""You are writing a very short video script for a game called "Death by AI".
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
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-small-3.1-24b-instruct",
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


def generate_image_fal(prompt: str):
    import requests
    url = "https://fal.run/fal-ai/flux/krea"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "image_size": "landscape_4_3",
        "num_inference_steps": 28
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["images"][0]["url"]
    except Exception as e:
        print(f"FAL Error: {e}")
        return None


async def submit_video_request_async(player_name: str, image_url: str, scene: str, dialogue: str, video_theme: str, client: "httpx.AsyncClient"):
    """Submit a video generation request and return the request_id (don't wait for completion)."""
    submit_url = "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }

    # Create prompt with LLM-generated scene and dialogue, plus hardcoded theme
    prompt = f'{scene} An announcer says "{dialogue}" Setting: {video_theme}'

    payload = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": "10",  # 10 second videos
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

    status_url = f"https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video/requests/{request_id}/status"
    result_url = f"https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video/requests/{request_id}"
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }

    max_attempts = 90  # 7.5 minutes max (5 second intervals)
    for attempt in range(max_attempts):
        await asyncio.sleep(5)

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
    last_active: float = Field(default_factory=time.time) # Heartbeat
    # Character creation fields
    character_description: Optional[str] = None  # Combined prompt for image gen
    character_image_url: Optional[str] = None  # Generated character avatar

class Round(BaseModel):
    number: int
    type: Literal["survival", "blind_architect", "cooperative"] = "survival"
    scenario_text: str = ""
    scenario_image_url: Optional[str] = None
    status: Literal["scenario", "strategy", "judgement", "results", "trap_creation", "trap_voting", "coop_voting", "coop_judgement"] = "scenario"
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
        "survival", "survival", "cooperative", "survival", "blind_architect"
    ])
    # Pre-warmed scenarios generated in parallel when game is created
    prewarmed_scenarios: List[str] = []  # Index corresponds to round number - 1
    # End game video fields - videos for ALL players
    player_videos: Dict[str, str] = {}  # player_id -> video URL
    videos_status: Literal["pending", "generating", "ready", "failed"] = "pending"
    video_theme: Optional[str] = None  # Consistent theme for all videos
    winner_id: Optional[str] = None

# --- Persistent Storage ---
# We use a Dict to store game states. Key=GameCode
games = modal.Dict.from_name("death-by-ai-games", create_if_missing=True)

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
    code = request.query_params.get("code")
    data = await request.json()
    player_name = data.get("name", "Unknown Player")
    character_description = data.get("character_description")
    game = get_game(code)

    if not game: raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "lobby": raise HTTPException(status_code=400, detail="Game started")

    player_id = str(uuid.uuid4())
    is_first = len(game.players) == 0
    player = Player(
        id=player_id,
        name=player_name,
        is_admin=is_first,
        character_description=character_description
    )
    game.players[player_id] = player
    save_game(game)

    # Spawn async character image generation if description provided
    if character_description:
        print(f"API: Spawning character image generation for {player_name}", flush=True)
        generate_character_image.spawn(code, player_id, character_description)
    else:
        # No character description means they skip preview, so auto-enter lobby
        game.players[player_id].in_lobby = True
        save_game(game)

    return {"player_id": player_id, "is_admin": is_first}


@web_app.post("/api/enter_lobby")
async def api_enter_lobby(request: Request):
    """Mark a player as having entered the lobby (after avatar preview)."""
    code = request.query_params.get("code")
    data = await request.json()
    player_id = data.get("player_id")

    game = get_game(code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if player_id not in game.players:
        raise HTTPException(status_code=404, detail="Player not found")

    game.players[player_id].in_lobby = True
    save_game(game)
    return {"status": "entered"}

@web_app.get("/api/get_game_state")
async def api_get_game_state(request: Request):
    code = request.query_params.get("code")
    game = get_game(code)
    if not game: raise HTTPException(status_code=404, detail="Game not found")
    
    # Heartbeat update only if 'player_id' cookie/header present? 
    # Actually, the polling works by fetching state. We don't distinguish WHO calls it in GET usually.
    # But we can try to infer or require player_id check? 
    # Simpler: The client usually doesn't send player_id in GET query params in current api.js.
    # We won't update heartbeat here unless we change API.
    # Let's change api.js to send player_id too?
    # Or, we update heartbeat on ANY action. 
    # But if they are just waiting...
    # We MUST update `api.js` to send `player_id` in `getGameState` query param.
    
    # Check for player_id in query
    player_id = request.query_params.get("player_id")
    if player_id and player_id in game.players:
        game.players[player_id].last_active = time.time()
        save_game(game)
        
    return game.model_dump()

def get_system_message(round_num: int, max_rounds: int, round_type: str) -> str:
    """Generate the system message for a given round based on narrative progression."""
    if round_type == "blind_architect":
        return "SECURITY BREACH DETECTED // ARCHITECT PROTOCOL ACTIVATED"
    elif round_type == "cooperative":
        return "CRITICAL ERROR // COLLABORATIVE SUBROUTINE REQUIRED"

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
    first_round.status = "strategy"  # Both survival and cooperative start with strategy
    first_round.style_theme = random.choice(IMAGE_STYLE_THEMES)
    first_round.system_message = get_system_message(1, game.max_rounds, first_round_type)
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
def generate_character_image(game_code: str, player_id: str, character_prompt: str):
    """Generate character avatar and update player state."""
    import asyncio

    async def do_generation():
        print(f"CHARACTER IMG: Generating for player {player_id}...", flush=True)
        url = await generate_character_image_async(character_prompt)
        if url:
            game = get_game(game_code)
            if game and player_id in game.players:
                game.players[player_id].character_image_url = url
                save_game(game)
                print(f"CHARACTER IMG: Saved image for {player_id}", flush=True)
        else:
            print(f"CHARACTER IMG: Failed to generate for {player_id}", flush=True)

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

        # Determine which rounds need scenarios (survival and cooperative, not blind_architect)
        tasks = []
        round_indices = []
        for i in range(max_rounds):
            round_type = round_config[i] if i < len(round_config) else "survival"
            if round_type != "blind_architect":
                # Generate scenario for this round
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

        # Filter for active players who are in the lobby (active in last 60s)
        cutoff = time.time() - 60

        alive_players = []
        for pid, p in game.players.items():
            is_active = p.last_active > cutoff
            # Only count players who have entered the lobby (not still in avatar preview)
            if p.is_alive and is_active and p.in_lobby:
                alive_players.append(p)
        
        if not alive_players:
            print("API: Warn - No alive players found. Forcing current.")
            alive_players = [game.players[player_id]]
            
        strategies_submitted = sum(1 for p in alive_players if p.strategy)
        print(f"API: Strategies Submitted: {strategies_submitted} / {len(alive_players)}")

        if strategies_submitted >= len(alive_players):
            current_round = game.rounds[game.current_round_idx]

            if current_round.type == "cooperative":
                # Cooperative round: transition to image voting phase
                print("API: All strategies received. Advancing to COOP VOTING.")
                current_round.status = "coop_voting"
                save_game(game)
                # Spawn async image generation for all strategies
                generate_coop_strategy_images.spawn(code)
            else:
                # Survival/Blind Architect: go to judgement
                print("API: All strategies received. Advancing to Judgement.")
                current_round.status = "judgement"
                save_game(game)
                # Trigger async judgement
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

    if round_type == "blind_architect":
        new_round.status = "trap_creation"
        new_round.scenario_text = "ARCHITECT MODE: Design a deadly scenario for your opponents."
    else:
        # Both survival and cooperative start with strategy phase
        new_round.status = "strategy"
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
@modal.asgi_app(label="death-by-ai-game")
def fastapi_app():
    return web_app


