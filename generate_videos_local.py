#!/usr/bin/env python3
"""
Generate character reaction videos using Kling 2.6 Pro - LOCAL VERSION.
Runs directly on your machine without Modal.

Usage:
    FAL_KEY="your-key" uv run python generate_videos_local.py
"""
import os
import time
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

# Get FAL key from environment (fal_client uses this automatically)
FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    print("ERROR: Set FAL_KEY environment variable or add to .env")
    exit(1)

print(f"Using FAL_KEY: {FAL_KEY[:20]}...")

# Character descriptions for image generation
CHARACTER_STYLES = [
    "young professional woman with brown hair in office attire, neutral expression, photorealistic portrait, high quality",
    "middle-aged man with glasses and beard, casual sweater, friendly face, photorealistic portrait, high quality",
    "young asian woman with short black hair, trendy streetwear, cool demeanor, photorealistic portrait, high quality",
    "athletic man in gym clothes, confident stance, photorealistic portrait, high quality",
    "quirky young person with colorful hair, artistic clothing, expressive face, photorealistic portrait, high quality",
]

# 30 Fun video scenarios
VIDEO_SCENARIOS = [
    # Comedy / Awkward
    {
        "id": "interview_gone_wrong",
        "scene": "A person sitting in a job interview chair, looking nervous, hands fidgeting",
        "offcam_voice": "deep serious male voice, stern HR interviewer",
        "offcam_line": "So it says here you listed 'professional napper' as your greatest strength. Care to elaborate?",
        "char_voice": "nervous stammering voice, caught off guard",
        "char_line": "I... I meant I'm good at... strategic rest optimization? For peak productivity?",
        "char_action": "eyes go wide, shifts uncomfortably, attempts a confident smile that comes out as a grimace",
        "background": "Office ambiance, air conditioning hum",
    },
    {
        "id": "surprise_party_fail",
        "scene": "A person walking through a door into a dark room, hand reaching for light switch",
        "offcam_voice": "loud chorus of excited voices, party crowd",
        "offcam_line": "SURPRISE! HAPPY BIRTHDAY!",
        "char_voice": "confused female voice, genuinely puzzled",
        "char_line": "But... my birthday was three months ago?",
        "char_action": "freezes mid-step, blinks in confusion, slowly looks around at the decorations",
        "background": "Party horns deflating, awkward silence, someone coughing",
    },
    {
        "id": "cooking_disaster",
        "scene": "A person proudly holding up a burnt unrecognizable dish in a smoky kitchen",
        "offcam_voice": "gentle female voice, trying not to laugh, supportive friend",
        "offcam_line": "So... what exactly was this supposed to be?",
        "char_voice": "defensive but cracking voice, slightly hurt pride",
        "char_line": "It's beef wellington! The black parts are... intentional! It's called charred!",
        "char_action": "holds the dish higher with forced confidence, a piece falls off onto the floor",
        "background": "Smoke alarm beeping faintly, fire crackling sounds",
    },
    {
        "id": "gaming_rage",
        "scene": "A gamer wearing headset, controller in hand, face illuminated by screen glow",
        "offcam_voice": "squeaky annoying young voice through headset, trash-talking kid",
        "offcam_line": "Get rekt noob! I'm only eight years old and I destroyed you!",
        "char_voice": "frustrated adult male voice, trying to stay calm but failing",
        "char_line": "That's it. I'm done. I need a break. A long break. Maybe forever.",
        "char_action": "stares at screen in disbelief, slowly removes headset, sets controller down with trembling restraint",
        "background": "Game over music, kid laughing through speakers",
    },
    {
        "id": "gym_awkward",
        "scene": "A person at the gym struggling with obviously too-heavy weights, face red",
        "offcam_voice": "smooth confident male voice, approaching gym bro",
        "offcam_line": "Hey bro, you need a spot? That's some serious weight you got there!",
        "char_voice": "strained squeaky voice, embarrassed, out of breath",
        "char_line": "Nope! All good! Just... warming up! This is light!",
        "char_action": "tries to lift the weight, arms shake violently, smile through obvious pain",
        "background": "Gym music, weights clanking in distance",
    },
    # Dramatic
    {
        "id": "plot_twist",
        "scene": "A person sitting across from someone at a dimly lit restaurant table, holding wine glass",
        "offcam_voice": "dramatic female voice, dropping a bombshell revelation",
        "offcam_line": "I need to tell you something. I'm actually your sister. We were separated at birth.",
        "char_voice": "shocked whisper building to disbelief, mind blown",
        "char_line": "Wait... WHAT? That explains why mom has two of everything!",
        "char_action": "wine glass slips from hand, catches it last second, mouth hanging open",
        "background": "Romantic violin music scratching to a halt",
    },
    {
        "id": "villain_reveal",
        "scene": "A person in dark dramatic lighting, shadows across face, standing confidently",
        "offcam_voice": "heroic determined male voice, confrontational hero",
        "offcam_line": "It was you all along! You were the mastermind behind everything!",
        "char_voice": "low sinister chuckle, theatrical villain voice",
        "char_line": "Took you long enough to figure it out. I've been planning this for fifteen years!",
        "char_action": "slowly turns to face camera, evil smile spreads across face, fingers steeple together",
        "background": "Thunder rumble, dramatic orchestral sting",
    },
    # Absurd
    {
        "id": "alien_contact",
        "scene": "A person in pajamas holding coffee mug, looking out window at bright light",
        "offcam_voice": "robotic alien voice with strange harmonics, extraterrestrial being",
        "offcam_line": "Human. We have traveled four thousand light years. Take us to your leader.",
        "char_voice": "tired unimpressed morning voice, too early for this",
        "char_line": "Can this wait until after coffee? I literally cannot process this right now.",
        "char_action": "takes a long sip of coffee, barely glances at the light, shuffles toward kitchen",
        "background": "UFO humming, dramatic space ambiance",
    },
    {
        "id": "talking_pet",
        "scene": "A person on couch watching TV, cat sitting next to them",
        "offcam_voice": "sophisticated British cat voice, judgmental feline",
        "offcam_line": "You know, I've been meaning to discuss the quality of my meals. They're frankly beneath me.",
        "char_voice": "stunned whisper, reality shattering, questioning sanity",
        "char_line": "Mr. Whiskers? Did you just... You can TALK? Since WHEN?",
        "char_action": "slowly turns to look at cat, remote falls from hand, jaw drops",
        "background": "TV static, dramatic reveal sting",
    },
    {
        "id": "demon_summoning",
        "scene": "A person in dark room with candles, ancient book open, pentagram on floor",
        "offcam_voice": "booming demonic voice, otherworldly entity",
        "offcam_line": "WHO DARES SUMMON ME FROM THE ETERNAL VOID?",
        "char_voice": "casual friendly voice, surprisingly unafraid",
        "char_line": "Oh hey! Yeah, quick question - do demons do taxes? I'm in a real bind here.",
        "char_action": "waves casually at the void, holds up tax forms, points at confusing section",
        "background": "Hellfire roaring, demonic chorus, dramatic bass",
    },
    # Game Show
    {
        "id": "million_dollar_question",
        "scene": "A contestant in game show hot seat, spotlight on them, sweating slightly",
        "offcam_voice": "smooth game show host voice, building tension",
        "offcam_line": "For one million dollars... What is the capital of your own country?",
        "char_voice": "panicking voice, brain completely blank under pressure",
        "char_line": "I... I know this! It's... wait... is it a trick question? Can I phone a friend?",
        "char_action": "wipes sweat from forehead, looks around desperately, fingers tap nervously",
        "background": "Tense game show music, clock ticking, audience murmuring",
    },
    {
        "id": "winner_announcement",
        "scene": "A person standing on stage, hands clasped, waiting for results",
        "offcam_voice": "dramatic announcer voice, building to crescendo",
        "offcam_line": "And the winner is... YOU! You've won the grand prize!",
        "char_voice": "disbelief turning to pure joy, emotional breakdown",
        "char_line": "ME? Are you serious? I've never won ANYTHING! Not even a raffle! OH MY GOD!",
        "char_action": "hands fly to face, knees buckle, tears streaming, jumping up and down",
        "background": "Confetti cannons, crowd cheering, triumphant music",
    },
    # Supernatural
    {
        "id": "ghost_roommate",
        "scene": "A person in bed at night, blanket pulled up, room dimly lit by phone",
        "offcam_voice": "ethereal whisper, friendly ghost voice",
        "offcam_line": "Hey, I noticed you left the fridge open. Also, I'm the ghost that lives here.",
        "char_voice": "high pitched terrified squeak, frozen in fear",
        "char_line": "The WHAT now? How long have you been here? Have you been watching me sleep?!",
        "char_action": "pulls blanket up to chin, eyes darting around room, perfectly still",
        "background": "Creaking floorboards, wind howling, eerie ambiance",
    },
    {
        "id": "fortune_teller",
        "scene": "A person sitting across from crystal ball, skeptical expression, arms crossed",
        "offcam_voice": "mysterious old woman voice, cryptic fortune teller",
        "offcam_line": "I see in your future... you will step in gum. Tomorrow. At exactly 2:47 PM.",
        "char_voice": "sarcastic disbelief, unimpressed customer",
        "char_line": "That's your big prediction? Gum? I paid forty dollars for gum prophecy?",
        "char_action": "leans back, rolls eyes, gestures at crystal ball dismissively",
        "background": "Mystical chimes, incense smoke swirling",
    },
    # Workplace
    {
        "id": "zoom_fail",
        "scene": "A person in professional top but clearly wearing pajama pants, on video call",
        "offcam_voice": "concerned colleague voice, trying to be helpful",
        "offcam_line": "Um, just so you know... your camera caught you standing up. Everyone saw the SpongeBob pants.",
        "char_voice": "horrified realization, career flashing before eyes",
        "char_line": "The investors saw? THE INVESTORS SAW THE SPONGEBOB PANTS?",
        "char_action": "face goes pale, looks down at pants, slowly sinks below frame",
        "background": "Video call notification sounds, muffled laughter",
    },
    {
        "id": "presentation_disaster",
        "scene": "A person at podium giving presentation, projector screen behind them",
        "offcam_voice": "horrified whisper from audience member",
        "offcam_line": "Uh, your screen is showing your browser history instead of the slides...",
        "char_voice": "panicked voice trying to stay professional, dying inside",
        "char_line": "And that's exactly the kind of... thorough research... we do here at the company!",
        "char_action": "slowly turns to look at screen, color drains from face, frozen smile",
        "background": "Murmuring audience, projector humming, someone gasping",
    },
    # Dating
    {
        "id": "first_date_truth",
        "scene": "Two people at dinner table, candlelit, romantic setting",
        "offcam_voice": "sweet earnest date voice, being vulnerable",
        "offcam_line": "I just feel like I can be honest with you. I still sleep with a stuffed animal. His name is Sir Fluffington.",
        "char_voice": "relieved excited voice, finding soulmate",
        "char_line": "Oh thank GOD! Mine is named Princess Snugglebottom! I thought I was the only one!",
        "char_action": "grabs date's hands across table, eyes light up, huge genuine smile",
        "background": "Romantic violin music, restaurant ambiance",
    },
    {
        "id": "ex_encounter",
        "scene": "A person at grocery store, frozen food section, cart full of ice cream",
        "offcam_voice": "surprised fake-pleasant voice, ex running into them",
        "offcam_line": "Oh wow, fancy seeing you here! You look... different. Are you okay?",
        "char_voice": "defensive voice, clearly not okay, in denial",
        "char_line": "Never better! This ice cream is for a party! A huge party! With all my cool new friends!",
        "char_action": "aggressively puts more ice cream in cart, maintains eye contact, forced smile",
        "background": "Supermarket music, freezer humming, shopping cart squeaking",
    },
    # Family
    {
        "id": "honest_kid",
        "scene": "A parent introducing friend to their small child in living room",
        "offcam_voice": "innocent high-pitched child voice, brutally honest kid",
        "offcam_line": "Mommy, why does your friend have a weird face? It's all bumpy and stuff.",
        "char_voice": "mortified parent voice, dying inside, apologetic",
        "char_line": "OKAY WE'RE GONNA GO TO ANOTHER ROOM NOW. So sorry. She's... learning... things.",
        "char_action": "eyes go wide, grabs child's hand, backs away while laughing nervously",
        "background": "Awkward silence, child giggling, door slamming",
    },
    {
        "id": "parent_discovery",
        "scene": "A teenager in their room, laptop hastily closed, looking guilty",
        "offcam_voice": "suspicious parent voice, arms crossed energy",
        "offcam_line": "What were you looking at just now? Why did you close that so fast?",
        "char_voice": "overly casual suspicious voice, terrible liar",
        "char_line": "Just... homework! So much homework! Math things! Numbers and... shapes?",
        "char_action": "sits on laptop protectively, sweating, avoiding eye contact at all costs",
        "background": "Computer fan whirring, tension music",
    },
    # Sports
    {
        "id": "sports_interview",
        "scene": "An athlete sweaty and exhausted, microphone being shoved in face",
        "offcam_voice": "energetic reporter voice, classic sports question",
        "offcam_line": "You just lost the championship by one point! How are you feeling right now?",
        "char_voice": "dead inside monotone, thousand yard stare",
        "char_line": "How do you THINK I'm feeling, Karen? I'm feeling like I lost by one point. Next question.",
        "char_action": "stares directly into camera, blinks slowly, single tear rolls down cheek",
        "background": "Crowd booing/cheering mix, camera flashes",
    },
    {
        "id": "coach_speech",
        "scene": "A player in locker room, head down, defeated posture",
        "offcam_voice": "inspiring gravelly coach voice, motivational speech",
        "offcam_line": "Listen to me. You're not a loser. You're a champion who just hasn't won yet!",
        "char_voice": "slowly building confidence voice, believing it",
        "char_line": "You're right. You're RIGHT! I'm gonna go out there and... probably lose again but BETTER!",
        "char_action": "lifts head, eyes fill with determination, stands up, almost falls over",
        "background": "Inspirational music swelling, lockers clanking",
    },
    # Food
    {
        "id": "spicy_challenge",
        "scene": "A person at table with extremely red, death-looking hot wings in front of them",
        "offcam_voice": "challenging restaurant owner voice, daring them",
        "offcam_line": "Nobody's ever finished our Death Reaper Challenge. Your meal is free if you do.",
        "char_voice": "overconfident voice about to regret everything",
        "char_line": "Free? Please. I put hot sauce on everything. This is gonna be easy mode.",
        "char_action": "cracks knuckles, picks up wing confidently, takes a bite, immediately regrets",
        "background": "Sizzling sounds, ominous music, other diners watching",
    },
    {
        "id": "diet_temptation",
        "scene": "A person staring at a beautiful cake through bakery window, hand on glass",
        "offcam_voice": "angelic tempting voice, the cake speaking",
        "offcam_line": "You've been so good all week. You deserve this. Just one little slice won't hurt.",
        "char_voice": "wavering willpower voice, losing the battle",
        "char_line": "NO! I'm strong! I'm... one slice? No! Maybe... NO! Okay fine ONE slice!",
        "char_action": "internal struggle visible on face, steps away, steps back, opens bakery door",
        "background": "Heavenly choir, bakery door chime, stomach growling",
    },
    {
        "id": "mystery_dish",
        "scene": "A person at fancy restaurant, waiter presenting covered dish dramatically",
        "offcam_voice": "pretentious French waiter voice, theatrical reveal",
        "offcam_line": "Tonight's special: deconstructed foam of essence with air-dried mist. Bon appetit.",
        "char_voice": "confused rich person voice, too proud to admit confusion",
        "char_line": "Ah yes. The foam. Of course. I eat this all the time. In... Europe.",
        "char_action": "stares at nearly empty plate, picks up tiny fork, pretends to know what to do",
        "background": "Soft jazz, plates clinking, pretentious murmuring",
    },
    # More Comedy
    {
        "id": "autocorrect_disaster",
        "scene": "A person staring at phone with horrified expression",
        "offcam_voice": "angry boss voice through phone speaker",
        "offcam_line": "You sent 'I quit this stupid job' to the entire company?! What were you thinking?!",
        "char_voice": "panicked voice, frantically explaining",
        "char_line": "No no NO! I typed 'I LOVE this job'! AUTOCORRECT! It was supposed to say I LOVE IT!",
        "char_action": "waves phone frantically, shows screen, face pure panic",
        "background": "Phone notification sounds piling up, dramatic music",
    },
    {
        "id": "wrong_funeral",
        "scene": "A person in black formal attire, standing awkwardly among mourners",
        "offcam_voice": "suspicious mourner voice, confrontational",
        "offcam_line": "Excuse me... how exactly did you know Margaret? I'm her daughter and I've never seen you before.",
        "char_voice": "awkward stammering voice, terrible at lying",
        "char_line": "Margaret! Yes! Good old Marge! We were... bowling partners? In the... war?",
        "char_action": "looks around desperately for exit, forced sad expression, sweating profusely",
        "background": "Somber organ music, whispered conversations",
    },
    {
        "id": "self_checkout_war",
        "scene": "A person at self-checkout machine, items scattered everywhere",
        "offcam_voice": "robotic monotone self-checkout machine voice",
        "offcam_line": "Unexpected item in bagging area. Please remove item and try again.",
        "char_voice": "increasingly unhinged voice, losing sanity",
        "char_line": "THERE IS NO ITEM! I'VE DONE NOTHING! WHY DO YOU HATE ME SPECIFICALLY?!",
        "char_action": "shakes fists at machine, looks at line of annoyed customers behind them",
        "background": "Beeping machines, impatient sighs from queue",
    },
    {
        "id": "uber_rating",
        "scene": "A person getting out of a car, looking back at driver",
        "offcam_voice": "passive-aggressive uber driver voice",
        "offcam_line": "So... you're giving me less than five stars because I didn't have your favorite music?",
        "char_voice": "defensive uncomfortable voice, trapped",
        "char_line": "I didn't say that! I mean... the silence was also fine! You're great! Five stars! FIVE!",
        "char_action": "frantically taps phone to change rating, fake smile, backs away slowly",
        "background": "Car engine idling, awkward tension",
    },
    {
        "id": "dentist_question",
        "scene": "A person in dentist chair with mouth full of dental tools",
        "offcam_voice": "cheerful dentist voice, asking questions at worst time",
        "offcam_line": "So, have you been flossing regularly? Be honest with me!",
        "char_voice": "muffled garbled voice, mouth full of equipment",
        "char_line": "Ahh... yesh... ehhery day... twish a day... shometimes more...",
        "char_action": "eyes dart guiltily, tries to nod, drool escapes",
        "background": "Dental drill whirring, suction sounds",
    },
]


def generate_character_image(prompt: str) -> str | None:
    """Generate a character image using FAL flux via fal_client."""
    import fal_client

    try:
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": prompt,
                "image_size": "landscape_16_9",
                "num_inference_steps": 4,
            },
            with_logs=False,
        )
        if result and "images" in result and len(result["images"]) > 0:
            return result["images"][0]["url"]
    except Exception as e:
        print(f"Image generation error: {e}")
    return None


def build_kling_prompt(scenario: dict) -> str:
    """Build a Kling v2.6 Pro formatted prompt."""
    prompt = f"""{scenario['scene']}. {scenario['char_action']}.

[Off-camera narrator, {scenario['offcam_voice']}]: "{scenario['offcam_line']}"

During this, the character remains silent, listening.

Immediately, the character reacts. [{scenario['char_voice']}]: "{scenario['char_line']}"

Background: {scenario['background']}."""
    return prompt


def generate_single_video(scenario: dict, image_url: str) -> dict:
    """Generate a single video using fal_client."""
    import fal_client

    vid_id = scenario["id"]
    prompt = build_kling_prompt(scenario)

    print(f"\n[{vid_id}] Starting...", flush=True)
    print(f"  Off-cam: {scenario['offcam_line'][:50]}...", flush=True)
    print(f"  Response: {scenario['char_line'][:50]}...", flush=True)

    start = time.time()

    try:
        result = fal_client.subscribe(
            "fal-ai/kling-video/v2.6/pro/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "duration": "10",
                "aspect_ratio": "16:9",
                "generate_audio": True,
            },
            with_logs=False,
        )

        elapsed = time.time() - start

        if result and "video" in result:
            video_url = result["video"]["url"]
            print(f"[{vid_id}] SUCCESS in {elapsed:.0f}s", flush=True)
            return {"id": vid_id, "url": video_url, "success": True, "elapsed": elapsed}
        else:
            print(f"[{vid_id}] No video in result after {elapsed:.0f}s", flush=True)
            return {"id": vid_id, "url": None, "success": False, "elapsed": elapsed, "error": "No video"}

    except Exception as e:
        elapsed = time.time() - start
        print(f"[{vid_id}] ERROR after {elapsed:.0f}s: {e}", flush=True)
        return {"id": vid_id, "url": None, "success": False, "elapsed": elapsed, "error": str(e)}


def main():
    print("=" * 70)
    print("KLING v2.6 PRO - Character Reaction Videos (LOCAL)")
    print("=" * 70)
    print(f"Total scenarios: {len(VIDEO_SCENARIOS)}")
    print()

    # Phase 1: Generate character images
    print("PHASE 1: Generating character images...")
    print("-" * 50)

    character_images = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(generate_character_image, style) for style in CHARACTER_STYLES]
        for i, future in enumerate(as_completed(futures)):
            url = future.result()
            if url:
                character_images.append(url)
                print(f"  Image {len(character_images)}/{len(CHARACTER_STYLES)}: OK")
            else:
                print(f"  Image {i+1}: FAILED")

    if not character_images:
        print("ERROR: No character images generated!")
        return

    print(f"\nGenerated {len(character_images)} character images")

    # Phase 2: Generate videos in batches
    print("\n" + "=" * 70)
    print("PHASE 2: Generating videos...")
    print("=" * 70)

    all_results = []
    batch_size = 5  # Smaller batches for local execution
    start_time = time.time()

    for batch_num, i in enumerate(range(0, len(VIDEO_SCENARIOS), batch_size)):
        batch = VIDEO_SCENARIOS[i:i + batch_size]
        print(f"\n--- BATCH {batch_num + 1} ({i+1} to {i+len(batch)}) ---")

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {
                executor.submit(
                    generate_single_video,
                    s,
                    character_images[(i + j) % len(character_images)]
                ): s["id"]
                for j, s in enumerate(batch)
            }

            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)

        # Pause between batches
        if i + batch_size < len(VIDEO_SCENARIOS):
            print("Pausing 3s...")
            time.sleep(3)

    total_elapsed = time.time() - start_time

    # Results summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total time: {total_elapsed:.0f}s ({total_elapsed/60:.1f} min)")

    successful = [r for r in all_results if r["success"]]
    failed = [r for r in all_results if not r["success"]]

    print(f"Success: {len(successful)}/{len(all_results)}")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for f in failed:
            print(f"  - {f['id']}: {f.get('error', 'Unknown')}")

    # Download videos
    print("\n" + "=" * 70)
    print("DOWNLOADING VIDEOS")
    print("=" * 70)

    output_dir = Path("generated_videos_30")
    output_dir.mkdir(exist_ok=True)

    for i, result in enumerate(successful):
        vid_id = result["id"]
        url = result["url"]
        output_path = output_dir / f"{vid_id}.mp4"

        print(f"  [{i+1}/{len(successful)}] {vid_id}...", end=" ", flush=True)
        try:
            urllib.request.urlretrieve(url, output_path)
            print(f"OK")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nVideos saved to: {output_dir.absolute()}")

    # Save URLs
    urls_file = output_dir / "video_urls.txt"
    with open(urls_file, "w") as f:
        for r in all_results:
            status = "OK" if r["success"] else "FAILED"
            url = r.get("url", "N/A")
            f.write(f"{r['id']}: [{status}] {url}\n")

    print(f"URL list: {urls_file}")


if __name__ == "__main__":
    main()
