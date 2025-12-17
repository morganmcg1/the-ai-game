import os

# Enforce the 'ai-game' environment
os.environ["MODAL_ENVIRONMENT"] = "ai-game"

import modal
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
import time
import uuid
import random

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

def generate_scenario_llm(round_num: int):
    client = get_llm_client()
    prompt = f"Generate a short, deadly, creative survival scenario for round {round_num} of a game (max 2 sentences). Example: 'You have fallen into a pit of snakes.'."
    try:
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-0905", 
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "You are trapped in a void. (AI Error)"

async def judge_strategy_llm_async(scenario: str, strategy: str):
    """Async version of judge_strategy_llm for parallel execution."""
    import re
    import httpx

    prompt = f"""Scenario: {scenario}
Player Strategy: {strategy}

Did the player survive? You must respond with ONLY a JSON object, no markdown or extra text.
Format: {{"survived": true/false, "reason": "short explanation", "visual_prompt": "description of the scene for generating an image"}}"""
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
        return '{"survived": false, "reason": "AI Error during judgement", "visual_prompt": "Glitchy screen"}'


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


# Keep sync versions for backwards compatibility
def judge_strategy_llm(scenario: str, strategy: str):
    import re
    client = get_llm_client()
    prompt = f"""Scenario: {scenario}
Player Strategy: {strategy}

Did the player survive? You must respond with ONLY a JSON object, no markdown or extra text.
Format: {{"survived": true/false, "reason": "short explanation", "visual_prompt": "description of the scene for generating an image"}}"""
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
        return '{"survived": false, "reason": "AI Error during judgement", "visual_prompt": "Glitchy screen"}'

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


# --- State Models ---
class Player(BaseModel):
    id: str
    name: str
    score: int = 0
    is_admin: bool = False
    is_alive: bool = True
    death_reason: Optional[str] = None
    survival_reason: Optional[str] = None  # How they survived
    strategy: Optional[str] = None  # Current round strategy
    result_image_url: Optional[str] = None # Image of death or glory
    last_active: float = Field(default_factory=time.time) # Heartbeat

class Round(BaseModel):
    number: int
    type: Literal["survival", "blind_architect", "cooperative"] = "survival"
    scenario_text: str = ""
    scenario_image_url: Optional[str] = None
    status: Literal["scenario", "strategy", "judgement", "results", "trap_creation", "trap_voting", "coop_voting", "coop_judgement"] = "scenario"
    architect_id: Optional[str] = None # For blind architect

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
    return {"code": code, "game_id": game.id}

@web_app.post("/api/join_game")
async def api_join_game(request: Request):
    code = request.query_params.get("code")
    data = await request.json()
    player_name = data.get("name", "Unknown Player")
    game = get_game(code)
    
    if not game: raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "lobby": raise HTTPException(status_code=400, detail="Game started")
    
    player_id = str(uuid.uuid4())
    is_first = len(game.players) == 0
    player = Player(id=player_id, name=player_name, is_admin=is_first)
    game.players[player_id] = player
    save_game(game)
    return {"player_id": player_id, "is_admin": is_first}

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

@web_app.post("/api/start_game")
async def api_start_game(request: Request):
    print("API: Start Game Called")
    code = request.query_params.get("code")
    # Quick check first
    game = get_game(code)
    if not game: 
        print("API: Game not found")
        raise HTTPException(status_code=404, detail="Game not found")
    
    print("API: Generating Scenario...")
    # Generate scenario first (slow operation)
    scenario_text = generate_scenario_llm(1)
    print(f"API: Scenario Generated: {scenario_text}")
    
    # Re-fetch game state to avoid overwriting updates (heartbeats) that happened during generation
    game = get_game(code)
    if not game: raise HTTPException(status_code=404, detail="Game disappeared")

    print(f"API: Starting game {code}")
    game.status = "playing"
    game.current_round_idx = 0

    # Use round_config to determine first round type
    first_round_type = game.round_config[0] if game.round_config else "survival"
    first_round = Round(number=1, type=first_round_type)
    first_round.scenario_text = scenario_text
    first_round.status = "strategy"  # Both survival and cooperative start with strategy
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
def run_round_judgement(game_code: str):
    """Run judgement for all players in parallel using asyncio."""
    import json
    import asyncio

    async def judge_and_generate(pid: str, player_name: str, strategy: str, scenario: str):
        """Judge a single player and generate their result image."""
        try:
            # Judge the strategy
            result_json = await judge_strategy_llm_async(scenario, strategy)
            print(f"JUDGEMENT: Got result for {player_name}: {result_json[:100]}...", flush=True)
            res = json.loads(result_json)
            survived = res.get("survived", False)
            reason = res.get("reason", "Unknown")
            vis_prompt = res.get("visual_prompt", "A generic scene.")

            # Generate image (in parallel with other players)
            image_url = await generate_image_fal_async(vis_prompt)

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
                tasks.append(judge_and_generate(pid, p.name, p.strategy, current_round.scenario_text))
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
                prompt = f"Survival strategy illustration: {player.strategy[:200]}. Dramatic scene, cinematic lighting, vivid colors."
                tasks.append(generate_image_fal_async(prompt))
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

            # Generate team result image
            vis_prompt = res.get("visual_prompt", "Team survival scene")
            image_url = await generate_image_fal_async(vis_prompt)
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

        # Filter for active players (active in last 60s)
        cutoff = time.time() - 60

        alive_players = []
        for pid, p in game.players.items():
            is_active = p.last_active > cutoff
            # print(f"API: Player {pid} ...") # Reduce noise
            if p.is_alive and is_active:
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
    
    img_url = generate_image_fal(trap_text)
    if img_url: current_round.trap_images[player_id] = img_url
        
    alive_players = [p for p in game.players.values() if p.is_alive]
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
    
    alive_players = [p for p in game.players.values() if p.is_alive]
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

    # Check if all alive players have voted
    alive_players = [p for p in game.players.values() if p.is_alive]
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
        new_round.scenario_text = "DESIGN A TRAP"
    else:
        # Both survival and cooperative start with strategy phase
        new_round.status = "strategy"
        new_round.scenario_text = generate_scenario_llm(next_idx + 1)

    save_game(game)
    return {"status": "started_round", "round": next_idx + 1, "type": round_type}

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


