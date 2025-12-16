import modal
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
import time
import uuid
import random
import os

# --- Image & Model Definitions ---
image = modal.Image.debian_slim().pip_install(
    "pydantic",
    "shortuuid",
    "pydantic",
    "shortuuid",
    "requests",
    "openai",
    "fastapi[standard]"
)

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
            model="meta-llama/llama-3.1-70b-instruct", 
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "You are trapped in a void. (AI Error)"

def judge_strategy_llm(scenario: str, strategy: str):
    client = get_llm_client()
    prompt = f"""
    Scenario: {scenario}
    Player Strategy: {strategy}
    
    Did the player survive? 
    Output JSON: {{ "survived": boolean, "reason": "short explanation", "visual_prompt": "description of the scene for generating an image" }}
    """
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        # Note: Kimi-K2 might not strictly follow json_object, so we might need parsing. 
        # For this prototype we assume it works or we fallback.
        # Actually OpenRouter/Moonshot supports JSON mode usually.
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM Judge Error: {e}")
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
    strategy: Optional[str] = None  # Current round strategy
    
class Round(BaseModel):
    number: int
    type: Literal["survival", "blind_architect"] = "survival"
    scenario_text: str = ""
    scenario_image_url: Optional[str] = None
    status: Literal["scenario", "strategy", "judgement", "results", "trap_creation", "trap_voting"] = "scenario"
    architect_id: Optional[str] = None # For blind architect
    
    # Blind Architect specific
    trap_proposals: Dict[str, str] = {} # player_id -> trap description
    trap_images: Dict[str, str] = {} # player_id -> image_url
    votes: Dict[str, str] = {} # voter_id -> target_player_id

class GameState(BaseModel):
    id: str
    code: str
    status: Literal["lobby", "playing", "finished"] = "lobby"
    players: Dict[str, Player] = {}
    rounds: List[Round] = []
    current_round_idx: int = -1
    max_rounds: int = 5
    created_at: float = Field(default_factory=time.time)

# --- Persistent Storage ---
# We use a Dict to store game states. Key=GameCode
games = modal.Dict.from_name("death-by-ai-games", create_if_missing=True)

# --- Secrets ---
from dotenv import load_dotenv
load_dotenv()

secrets = [
    modal.Secret.from_dict({
        "MOONSHOT_API_KEY": os.environ.get("MOONSHOT_API_KEY"),
        "FAL_KEY": os.environ.get("FAL_KEY")
    })
]

# --- Helper Functions ---
def get_game(code: str) -> Optional[GameState]:
    data = games.get(code)
    if data:
        return GameState.model_validate(data)
    return None

def save_game(game: GameState):
    games[game.code] = game.model_dump()

# --- Core Game Logic ---

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def create_game(data: Dict):
    import shortuuid
    code = shortuuid.ShortUUID().random(length=4).upper()
    game = GameState(id=str(uuid.uuid4()), code=code)
    save_game(game)
    return {"code": code, "game_id": game.id}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def join_game(code: str, data: Dict):
    player_name = data.get("name", "Unknown Player")
    game = get_game(code)
    
    if not game:
        return {"error": "Game not found"}, 404
        
    if game.status != "lobby":
        return {"error": "Game already started"}, 400
    
    player_id = str(uuid.uuid4())
    is_first = len(game.players) == 0
    player = Player(id=player_id, name=player_name, is_admin=is_first)
    
    game.players[player_id] = player
    save_game(game)
    
    return {"player_id": player_id, "is_admin": is_first}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET")
def get_game_state(code: str):
    game = get_game(code)
    if not game:
        return {"error": "Game not found"}, 404
    return game.model_dump()

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def start_game(code: str):
    game = get_game(code)
    if not game:
        return {"error": "Game not found"}, 404
        
    game.status = "playing"
    game.current_round_idx = 0
    
    # Create first round
    first_round = Round(number=1, type="survival")
    game.rounds.append(first_round)
    
    # Trigger scenario generation
    first_round.scenario_text = generate_scenario_llm(1)
    
    # Generate Scenario Image (Optional, keeps it fun)
    # first_round.scenario_image_url = generate_image_fal(first_round.scenario_text) 
    
    first_round.status = "strategy"
    
    save_game(game)
    return {"status": "started", "scenario": first_round.scenario_text}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def submit_strategy(code: str, data: Dict):
    game = get_game(code)
    player_id = data.get("player_id")
    strategy = data.get("strategy")
    
    if not game or not player_id:
        return {"error": "Invalid request"}, 400
        
    current_round = game.rounds[game.current_round_idx]
    
    if current_round.status != "strategy":
         return {"error": "Not in strategy phase"}, 400
         
    if player_id in game.players:
        game.players[player_id].strategy = strategy
        
    # Check if all alive players submitted
    alive_players = [p for p in game.players.values() if p.is_alive]
    strategies_submitted = sum(1 for p in alive_players if p.strategy)
    
    if strategies_submitted >= len(alive_players):
        # Move to judgement
        current_round.status = "judgement"
        save_game(game) # Save state before long running process
        
        # In a real app, use modal.spawn or a queue. Here we block for MVP.
        import json
        
        for pid in game.players:
            p = game.players[pid]
            if p.is_alive and p.strategy:
                # Judge
                result_json = judge_strategy_llm(current_round.scenario_text, p.strategy)
                try:
                    res = json.loads(result_json)
                    survived = res.get("survived", False)
                    reason = res.get("reason", "Unknown")
                    vis_prompt = res.get("visual_prompt", f"{p.name} facing {current_round.scenario_text}")
                    
                    p.is_alive = survived
                    if not survived:
                        p.death_reason = reason
                    else:
                        p.score += 100
                        
                    # Generate Result Image
                    # image_url = generate_image_fal(vis_prompt) 
                    # We can store image url on player for this round? 
                    # Player model doesn't have per-round image storage yet.
                    # Ideally we'd have a 'RoundResult' in the Round object.
                    # For MVP let's store it in a new field on Player or Round.
                    
                except Exception as e:
                    print(f"Judgement Parse Error: {e}")
                    
        current_round.status = "results"
        
    save_game(game)
    return {"status": "submitted"}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def submit_trap(code: str, data: Dict):
    game = get_game(code)
    player_id = data.get("player_id")
    trap_text = data.get("trap_text")
    
    if not game or not player_id: return {"error": "Invalid"}, 400
    
    current_round = game.rounds[game.current_round_idx]
    if current_round.type != "blind_architect" or current_round.status != "trap_creation":
        return {"error": "Not in trap creation phase"}, 400
        
    current_round.trap_proposals[player_id] = trap_text
    
    # Generate image for the trap immediately (or async)
    # Blocking for MVP
    img_url = generate_image_fal(trap_text)
    if img_url:
        current_round.trap_images[player_id] = img_url
        
    # Check if all submitted
    alive_players = [p for p in game.players.values() if p.is_alive]
    if len(current_round.trap_proposals) >= len(alive_players):
        current_round.status = "trap_voting"
        
    save_game(game)
    return {"status": "trap_submitted"}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def vote_trap(code: str, data: Dict):
    game = get_game(code)
    voter_id = data.get("voter_id")
    target_id = data.get("target_id")
    
    if not game or not voter_id: return {"error": "Invalid"}, 400
    
    current_round = game.rounds[game.current_round_idx]
    if current_round.status != "trap_voting": return {"error": "Not voting"}, 400
    
    current_round.votes[voter_id] = target_id
    
    # Check if all voted
    alive_players = [p for p in game.players.values() if p.is_alive]
    if len(current_round.votes) >= len(alive_players):
        # Tally votes
        vote_counts = {}
        for target in current_round.votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1
            
        winner_id = max(vote_counts, key=vote_counts.get)
        winning_trap = current_round.trap_proposals[winner_id]
        winning_image = current_round.trap_images.get(winner_id)
        
        # Proceed to survival phase with this trap
        current_round.scenario_text = winning_trap
        current_round.scenario_image_url = winning_image
        current_round.architect_id = winner_id
        current_round.status = "strategy" 
        
        # Give bonus points to architect?
        if winner_id in game.players:
            game.players[winner_id].score += 500
            
    save_game(game)
    return {"status": "voted"}

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST")
def next_round(code: str):
    game = get_game(code)
    if not game: return {"error": "Game not found"}, 404
    
    next_idx = game.current_round_idx + 1
    if next_idx >= 2: # Debug: Max 2 rounds
        game.status = "finished"
        save_game(game)
        return {"status": "finished"}
        
    game.current_round_idx = next_idx
    
    # Determine type
    is_blind_architect = (next_idx + 1) == 2 # Debug: Round 2 is Blind Architect
    round_type = "blind_architect" if is_blind_architect else "survival"
    
    new_round = Round(number=next_idx + 1, type=round_type)
    game.rounds.append(new_round)
    
    if is_blind_architect:
        new_round.status = "trap_creation"
        new_round.scenario_text = "DESIGN A DEADLY TRAP. Your trap will be visualized. The best one becomes reality."
    else:
        new_round.status = "strategy" # Skip scenario fetch for MVP speed? No, fetch it.
        new_round.scenario_text = generate_scenario_llm(next_idx + 1)
        # new_round.scenario_image_url = generate_image_fal(new_round.scenario_text)
        
    save_game(game)
    return {"status": "started_round", "round": next_idx + 1}

