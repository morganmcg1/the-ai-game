import requests
import time
import sys
import json

# Constants
PROJECT_NAME = "weightsandbiases-ai-game--mas-ai"
ENV = "dev"
DOMAIN = "modal.run"

def get_url(func_name):
    return f"https://{PROJECT_NAME}-{func_name.replace('_', '-')}-{ENV}.{DOMAIN}"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def poll_for_status(code, target_status, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        res = requests.get(get_url("get_game_state"), params={"code": code})
        state = res.json()
        
        # Check round status if playing
        current_status = state['status']
        round_status = "N/A"
        if state['rounds'] and state['current_round_idx'] >= 0:
             round_status = state['rounds'][state['current_round_idx']]['status']
        
        # log(f"Polling: Game={current_status}, Round={round_status}")
        
        if current_status == "finished" and target_status == "finished":
            return state
            
        if current_status == "playing":
             # We want to match round status if provided
             if round_status == target_status:
                 return state
             # Special case: waiting for results means we are past judgement
             if target_status == "results" and round_status == "results":
                 return state
                 
        time.sleep(1)
    return None

def run_full_walkthrough():
    log(">>> STARTING 2-ROUND WALKTHROUGH")
    
    # 1. Create Game
    log("1. Creating Game...")
    res = requests.post(get_url("create_game"), json={})
    res.raise_for_status()
    code = res.json()["code"]
    log(f"   Game Created: {code}")

    # 2. Join Players
    log("2. Joining Players...")
    p1 = requests.post(get_url("join_game"), params={"code": code}, json={"name": "Alice"}).json()
    p1_id = p1["player_id"]
    p2 = requests.post(get_url("join_game"), params={"code": code}, json={"name": "Bob"}).json()
    p2_id = p2["player_id"]
    log(f"   Alice ({p1_id[:4]}) and Bob ({p2_id[:4]}) joined.")

    # 3. Start Game
    log("3. Starting Game...")
    requests.post(get_url("start_game"), params={"code": code})
    
    # --- ROUND 1: SURVIVAL ---
    log(">>> ROUND 1: Waiting for Scenario...")
    state = poll_for_status(code, "strategy", timeout=45)
    if not state:
        log("FAIL: Timed out waiting for Round 1 Strategy phase.")
        return
        
    r1 = state['rounds'][0]
    log(f"   Scenario: {r1['scenario_text']}")
    
    log("4. Submitting Strategies...")
    requests.post(get_url("submit_strategy"), params={"code": code}, json={"player_id": p1_id, "strategy": "I use the scuba gear I found to breathe and swim to the surface through the designated exit."})
    requests.post(get_url("submit_strategy"), params={"code": code}, json={"player_id": p2_id, "strategy": "I use a submarine to navigate the hazards safely."})
    
    log(">>> ROUND 1: Waiting for Judgement Results...")
    # This triggers LLM judgement
    state = poll_for_status(code, "results", timeout=60)
    if not state:
        log("FAIL: Timed out waiting for Round 1 Results.")
        return
        
    p1_alive = state['players'][p1_id]['is_alive']
    p2_alive = state['players'][p2_id]['is_alive']
    log(f"   Results: Alice Alive? {p1_alive}, Bob Alive? {p2_alive}")
    
    # --- NEXT ROUND (BLIND ARCHITECT) ---
    log("5. Moving to Round 2 (Blind Architect)...")
    requests.post(get_url("next_round"), params={"code": code})
    
    log(">>> ROUND 2: Waiting for Trap Creation...")
    state = poll_for_status(code, "trap_creation", timeout=30)
    if not state:
        log("FAIL: Timed out waiting for Trap Creation.")
        return
        
    log("6. Submitting Traps...")
    # Submit Trap P1
    requests.post(get_url("submit_trap"), params={"code": code}, json={"player_id": p1_id, "trap_text": "A pit of spikes with lasers."})
    # Submit Trap P2
    requests.post(get_url("submit_trap"), params={"code": code}, json={"player_id": p2_id, "trap_text": "A giant rolling boulder."})
    
    log(">>> ROUND 2: Waiting for Voting (Image Gen active)...")
    # This might take time due to image generation
    state = poll_for_status(code, "trap_voting", timeout=60)
    if not state:
        log("FAIL: Timed out waiting for Voting phase.")
        return
        
    r2 = state['rounds'][1]
    log(f"   Trap Images Generated. Candidates: {len(r2['trap_proposals'])}")
    
    log("7. Voting...")
    # Alice votes for Bob, Bob votes for Alice (Tie? Or logic handles it)
    requests.post(get_url("vote_trap"), params={"code": code}, json={"voter_id": p1_id, "target_id": p2_id, "player_id": p1_id}) # Note: api might need checking params
    requests.post(get_url("vote_trap"), params={"code": code}, json={"voter_id": p2_id, "target_id": p2_id, "player_id": p2_id}) # Bob votes for self?
    
    # Logic in app.py: vote_trap(code, data: {voter_id, target_id})
    # Voting moves to 'strategy' phase of the trap round immediately if all voted
    
    log(">>> ROUND 2: Waiting for Final Strategy Phase (Trap Selected)...")
    state = poll_for_status(code, "strategy", timeout=30)
    if not state:
        log("FAIL: Timed out waiting for Strategy phase after voting.")
        return
        
    r2 = state['rounds'][1]
    log(f"   Winning Trap Scenario: {r2['scenario_text']}")
    
    log("8. Submitting Strategy for Trap...")
    requests.post(get_url("submit_strategy"), params={"code": code}, json={"player_id": p1_id, "strategy": "Dodge."})
    requests.post(get_url("submit_strategy"), params={"code": code}, json={"player_id": p2_id, "strategy": "Hide."})
    
    log(">>> ROUND 2: Waiting for Results...")
    state = poll_for_status(code, "results", timeout=60)
    
    log("9. Finishing Game...")
    requests.post(get_url("next_round"), params={"code": code})
    
    log(">>> Waiting for Game Finish...")
    state = poll_for_status(code, "finished", timeout=10)
    if state and state['status'] == 'finished':
        log("SUCCESS: Game Finished Correctly.")
    else:
        log("FAIL: Game did not finish.")

if __name__ == "__main__":
    run_full_walkthrough()
