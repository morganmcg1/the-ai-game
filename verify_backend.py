import requests
import time
import sys

# Constants matching api.js logic
PROJECT_NAME = "weightsandbiases-ai-game--survaive"
ENV = "dev"
DOMAIN = "modal.run"

def get_url(func_name):
    return f"https://{PROJECT_NAME}-{func_name.replace('_', '-')}-{ENV}.{DOMAIN}"

def run_test():
    print(">>> 1. Creating Game...")
    try:
        res = requests.post(get_url("create_game"), json={})
        res.raise_for_status()
        data = res.json()
        code = data["code"]
        print(f"Game Created: {code}")
    except Exception as e:
        print(f"FAILED to join game: {e}")
        return

    print(">>> 2. Joining Game...")
    try:
        # Join as Admin
        res = requests.post(get_url("join_game"), params={"code": code}, json={"name": "Admin"})
        res.raise_for_status()
        print("Admin Joined.")
        
        # Join as Player 2
        res = requests.post(get_url("join_game"), params={"code": code}, json={"name": "Player2"})
        res.raise_for_status()
        print("Player2 Joined.")
    except Exception as e:
        print(f"FAILED to join game: {e}")
        return

    print(">>> 3. Checking Lobby State...")
    state = requests.get(get_url("get_game_state"), params={"code": code}).json()
    print(f"State: {state['status']}, Players: {len(state['players'])}")
    if state['status'] != "lobby":
        print("ERROR: Should be in lobby")
        return

    print(">>> 4. Starting Game (Triggering LLM)...")
    try:
        res = requests.post(get_url("start_game"), params={"code": code})
        res.raise_for_status()
        print("Start Game Request Sent.")
    except Exception as e:
        print(f"FAILED to start game: {e}")
        # Check if 500
        if hasattr(e, 'response') and e.response:
             print(e.response.text)
        return

    print(">>> 5. Polling for 'playing' state...")
    succeeded = False
    for i in range(10):
        state = requests.get(get_url("get_game_state"), params={"code": code}).json()
        status = state['status']
        print(f"Poll {i}: Status={status}")
        if status == "playing":
            succeeded = True
            print("SUCCESS: Game is playing!")
            # Check scenario
            round_idx = state['current_round_idx']
            current_round = state['rounds'][round_idx]
            print(f"Scenario: {current_round['scenario_text']}")
            break
        time.sleep(1)
        
    if not succeeded:
        print("FAILED: Game did not transition to playing.")

if __name__ == "__main__":
    run_test()
