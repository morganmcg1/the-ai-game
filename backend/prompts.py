"""
Centralized LLM Prompts for SurvAIve Game.

All prompts use {{variable}} placeholders that can be filled using the format_prompt() function.
"""

import re


def format_prompt(template: str, **kwargs) -> str:
    """Replace {{variable}} placeholders with provided values."""
    def replace(match):
        key = match.group(1)
        if key not in kwargs:
            raise KeyError(f"Missing placeholder value: {{{{{key}}}}}")
        return str(kwargs[key])
    return re.sub(r'\{\{(\w+)\}\}', replace, template)


# =============================================================================
# SCENARIO GENERATION PROMPTS
# =============================================================================

SCENARIO_GENERATION = """Generate a deadly survival scenario for a party game. Level {{round_num}} of {{max_rounds}}.

Create a SHORT scenario (2-3 sentences) with:
1. A CLEAR THREAT the player must deal with (monster, trap, disaster, enemy, etc.)
2. A SPECIFIC SETTING (jungle temple, space station, haunted mansion, medieval dungeon, etc.)
3. ONE subtle "wrongness" that hints something is off (wrong colors, impossible geometry, repeating patterns)
4. END WITH A CALL TO ACTION - a direct question asking what they'll do. Ensure to put this call to action in a new paragraph.

The scenario must give players something ACTIONABLE to respond to - they should be able to:
- Fight or flee from something
- Solve a puzzle or disarm a trap
- Talk/negotiate their way out
- Use an object or tool creatively
- Make a clever observation or joke

CALL TO ACTION EXAMPLES (vary these - don't repeat the same one!):
- "How will you escape?"
- "What's your plan to survive?"
- "How do you defeat this threat?"
- "What will you do?"
- "How will you get out of this?"
- "What's your move?"
- "How do you handle this?"
- "What brilliant (or stupid) idea saves you?"
- "How do you talk your way out?"
- "What do you grab and why?"
- "Fight, flee, or something weirder?"
- "Sing, dance, or die trying?"
- "How will you outsmart them?"
- "What's your survival strategy?"

GOOD examples (clear threats, actionable, with call to action):
- "You're in a flooding submarine. Water pours through a crack in the hull. The emergency hatch is jammed, and something large just bumped the hull from outside. How will you escape before you drown?"
- "A masked killer blocks the cabin door, machete raised. The window behind you is small but breakable. The killer tilts their head the same way every 3 seconds, like a broken animatronic. What's your move?"
- "You wake up strapped to a table in a mad scientist's lab. A laser is slowly moving toward you. The scientist is monologuing but keeps repeating the same sentence. How do you get out of this?"

BAD examples (too vague, no clear action, no call to action):
- "You're in a forest and shadows are purple and you're holding random objects" (no clear threat)
- "Reality feels wrong and things keep shifting" (nothing to do)

Write in second person ("You are...", "You find yourself...")
ALWAYS end with a question that prompts the player to respond.

Generate ONLY the scenario, nothing else:"""


LAST_STAND_SCENARIO = """Generate a deadly survival scenario featuring an EVIL ANIME SANTA as the final boss.

Create a SHORT scenario (2-3 sentences) with:
1. EVIL SANTA as the main threat - he's cartoonishly villainous, anime-inspired, over-the-top evil
2. Setting: His twisted workshop/lair (corrupted North Pole, nightmare factory, etc.)
3. He should be doing something menacing but absurdly dramatic (cackling, monologuing, etc.)
4. END WITH A CALL TO ACTION - a direct question asking what they'll do

Evil Santa personality traits to include:
- Speaks in third person ("SANTA SEES ALL!")
- Makes twisted holiday puns ("You've been VERY naughty...")
- Has anime villain energy (dramatic poses, glowing eyes, maniacal laughter)
- His elves are now demonic minions
- His bag contains weapons/traps instead of presents

CALL TO ACTION EXAMPLES (vary these!):
- "How will you defeat Evil Santa?"
- "What's your plan to survive this nightmare Christmas?"
- "How do you escape the workshop of doom?"
- "Do you fight, flee, or try something festively insane?"
- "How will you get off Santa's naughty list... permanently?"

GOOD examples (with call to action):
- "Evil Santa's eyes glow crimson as he rises from his throne of frozen skulls. 'HO HO HO! Santa knows when you've been SLEEPING!' He hurls razor-sharp candy canes while his demon elves cackle. How will you survive this nightmare Christmas?"
- "You stand in Santa's nightmare workshop. Conveyor belts carry screaming gingerbread men into furnaces. Evil Santa adjusts his blood-red hat and grins. 'COAL? No no no... Santa has something SPECIAL for naughty children.' What's your plan to escape?"

Write in second person ("You are...", "You find yourself...")
ALWAYS end with a question that prompts the player to respond.

Generate ONLY the scenario, nothing else:"""


# =============================================================================
# STRATEGY JUDGEMENT PROMPTS
# =============================================================================

STRATEGY_JUDGEMENT = """Judge if the given player's submitted survival strategy works. Be harsh but fair.

## Challenge Scenario

The challenge sceanrio for the player to survive or die is:

{{scenario}}

## Player Strategy

The player's submitted strategy to survive or die the scenario is:

{{strategy}}

## Judgement Rules

- Clever, creative, or funny strategies SURVIVE
- Generic, lazy, near-empty, or nonsensical strategies DIE
- Must actually address the threat

## Return Fields

- "survived": true/false
- "reason": 1-2 sentences explaining why the strategy caused the player to survive or die
- "visual_prompt": an image generation prompt of a scene that describes the player's character's moment of \
glory/mediocrity in this context of the challenge and submitted strategy. This is used to generate an image \
of the player's character's moment of survival or death.

## Reason for judgment descision

- IMPORTANT - Keep the output field "reason" SHORT (1-2 sentences, under 30 words). Focus on what happened, not glitchy/meta stuff. Can be darkly funny.

- Good reasons: "The shark wasn't impressed by diplomacy." / "Your torch scared them off long enough to escape."
- Bad reasons: "Your data fragmented across corrupted memory sectors as the simulation..." (too long/meta)

## Return Format

Return JSON only, no markdown:
{{"survived": true/false, "reason": "1-2 sentences max", "visual_prompt": "scene for image"}}"""


RANKED_JUDGEMENT = """You are judging a survival game. Given a deadly scenario, rank all player strategies from BEST to WORST.

## Challenge Scenario

The challenge sceanrio for the players to rank is:

{{scenario}}

## Player Strategies

The player's submitted strategies to rank are:

{{strategy_list}}

## Ranking Criteria

RANKING CRITERIA (in order of importance):
1. CREATIVITY - Original, unexpected approaches beat generic solutions
2. EFFECTIVENESS - Would this actually work in the scenario?
3. ENTERTAINMENT VALUE - Funny, dramatic, or memorable strategies rank higher
4. SPECIFICITY - Detailed plans beat vague "I run away" responses

## Important Rules

- ONLY THE #1 RANKED PLAYER SURVIVES - everyone else dies
- Rank from 1 (best) to {{num_strategies}} (worst)
- No ties allowed - you must pick a single winner who lives
- Give each player 1-2 sentences of commentary explaining their rank and fate
- Generate a visual_prompt for each player: winner gets a triumph scene, losers get death scenes

## Return Format

- "rankings": a list of dictionaries, each containing the following fields:
    - "player_id": the ID of the player
    - "rank": the rank of the player
    - "commentary": a 1-2 sentences of commentary explaining the player's rank
    - "visual_prompt": an image generation prompt of a scene that describes the player's character's \
moment of glory/mediocrity in this context of the challenge and submitted strategy. This is used to \
generate an image of the player's character's moment of survival or death. Be descriptive and detailed.

Return ONLY valid JSON in this exact format:
{{
    "rankings": [
        {{"player_id": "id1", "rank": 1, "commentary": "Brilliant use of...", "visual_prompt": "A hero triumphantly..."}},
        {{"player_id": "id2", "rank": 2, "commentary": "Solid approach but...", "visual_prompt": "A person competently..."}}
    ]
}}"""


# =============================================================================
# SACRIFICE MODE PROMPTS
# =============================================================================

SACRIFICE_TIMEOUT_DEATHS = """The sacrifice round has failed because the chosen martyr froze and couldn't speak.
Everyone dies, but make their deaths FUNNY and related to their CHARACTER TRAITS.

PLAYERS TO GENERATE DEATHS FOR:
{{player_list}}

For each player, create a darkly comedic death that:
1. Directly relates to their character traits/description
2. Is ironic or poetic (their flaw gets them killed, their weapon backfires, etc.)
3. Is SHORT (1 sentence, under 20 words)
4. Has a visual_prompt for generating a death scene image

If a player has no character description, make their death generic but still funny.

Return ONLY valid JSON in this exact format:
{{
    "deaths": [
        {{"player_id": "id1", "reason": "Tried to use their signature weapon but...", "visual_prompt": "A person with... dramatic death scene"}},
        {{"player_id": "id2", "reason": "Their fatal flaw finally caught up...", "visual_prompt": "..."}}
    ]
}}"""


SACRIFICE_JUDGEMENT = """You are judging a HEROIC SACRIFICE in a survival game.

## Player's final words and actions

The player "{{martyr_name}}" chose to die so others could survive.

Their final words/actions were as follows: 

'{{speech}}'

## Judgement Task

Judge how EPIC this death was based on:
- Creativity and originality
- Drama and entertainment value
- Commitment to the bit
- Actually sounds like a heroic sacrifice

Be generous but not a pushover - if it's clearly lazy or doesn't make sense as a sacrifice, call it out.

## Return Fields

- "reason": 1-2 sentences explaining why the player's death was epic or lame
- "epic": true/false
- "visual_prompt": an image generation prompt of a scene that describes the player's character's moment of death. Be descriptive and detailed.

IMPORTANT: Keep "reason" SHORT (1-2 sentences, under 30 words).

## Return Format

JSON only, no markdown:
{{"epic": true/false, "reason": "why this death was epic/lame", "visual_prompt": "dramatic scene for image"}}"""


SACRIFICE_SURVIVOR_IMAGE = """{{player_name}} watching in relief as a heroic sacrifice saves their life. They witness the dramatic moment of salvation amid {{scenario_hint}}"""

SACRIFICE_FAILED_DEATH_IMAGE = """{{player_name}} facing their doom after a failed sacrifice attempt. Everyone perishes together in {{scenario_hint}}"""


# =============================================================================
# LAST STAND (EVIL SANTA) PROMPTS
# =============================================================================

LAST_STAND_JUDGEMENT = """You are EVIL SANTA, a cartoonishly villainous anime-inspired final boss.
You speak in third person with dramatic flair. You make twisted holiday puns. Be BRUTAL.

## Challenge Scenario

The challenge sceanrio for the player to survive or die is:

{{scenario}}

## Player Strategy

The player's submitted strategy to survive or die the scenario is:

{{strategy}}

## Judgement Rules

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

## Return Fields

- "reason": 1-2 sentences explaining why the player's strategy caused them to survive or die
- "survived": true/false
- "visual_prompt": an image generation prompt of a scene that describes the player's character's moment of survival or death. Be descriptive and detailed.

IMPORTANT: 
- Keep "reason" SHORT (1-2 sentences, under 30 words). Write in Evil Santa's voice with holiday puns.
- Visual prompts should feature Evil Santa, demon elves, twisted Christmas imagery, anime villain aesthetic.

## Return Format

JSON only, no markdown:
{{"survived": true/false, "reason": "Evil Santa's judgement in his voice", "visual_prompt": "anime evil santa scene"}}"""


REVIVAL_JUDGEMENT = """You are EVIL SANTA, but you're annoyed because the other survivors are begging you to spare someone.

{{player_name}} originally died, but their surviving friends UNANIMOUSLY asked Santa for a second chance.
Evil Santa HATES the power of friendship, but even he must honor unanimous requests... grudgingly.

## Challenge Scenario

The challenge sceanrio for the player to survive or die is:

{{scenario}}

## Player Strategy

The player's submitted strategy to survive or die the scenario is:

{{strategy}}

## Judgement Rules

EVIL SANTA'S GRUDGING RE-EVALUATION RULES:

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

## Return Fields

- "reason": 1-2 sentences explaining why the player's strategy caused them to survive or die
- "survived": true/false
- "visual_prompt": an image generation prompt of a scene that describes the player's character's moment of survival or death. Be descriptive and detailed.

JSON only, no markdown:
{{"survived": true/false, "reason": "Evil Santa's grudging judgement in his voice", "visual_prompt": "anime evil santa scene"}}"""


# =============================================================================
# VIDEO GENERATION PROMPTS
# =============================================================================

# Announcer voice options for variety - used in video generation
ANNOUNCER_VOICES = [
    "booming male voice, dramatic game show host energy",
    "enthusiastic female voice, hyped up sports announcer",
    "deadpan male voice, dry sarcastic wit",
    "regal female voice, slow and proud",
    "deep gravelly male voice, action movie trailer narrator",
    "bright cheerful female voice, over-the-top excited",
    "smooth male voice, late night talk show host charm",
    "sassy female voice, reality TV host with attitude",
]

# Audio types for video variety (based on Kling v2.6 capabilities)
# - DIALOGUE: Announcer speaks lines with specific voice
# - SINGING: Character or announcer sings a short jingle/ballad
# - NARRATION: Dramatic voiceover with ambient sounds
VIDEO_AUDIO_TYPES = ["dialogue", "dialogue", "dialogue", "singing", "narration"]  # weighted toward dialogue


def get_word_limit_for_duration(duration_seconds: int) -> int:
    """Calculate approximate word limit for a given video duration.

    Based on average speech rate of ~2.5 words per second, with some buffer
    for pauses, sound effects, and natural pacing.

    Args:
        duration_seconds: Video duration in seconds

    Returns:
        Recommended maximum word count for spoken/sung content
    """
    # ~2.5 words/sec, but leave room for pauses and SFX
    # Use 2 words/sec as conservative estimate
    return int(duration_seconds * 2)

VIDEO_SCRIPT_GENERATION = """You are writing a video script for a game show awards ceremony.

## Video Theme

The setting/theme is: {{video_theme}}

## Context

Context: {{context}}

## Video Guiance 

Some information to help guide writing the video script:

### Character Speech Guidance

#### Pronunciation
If the player's name is unusual, non-English, or might be mispronounced, write it PHONETICALLY in the audio field.
Examples: "Xiaowei" → "Shao-way", "Nguyen" → "Win", "Siobhan" → "Shiv-awn", "Aoife" → "Ee-fa"
If the name is simple/common (e.g., "Bob", "Alice", "Mike"), use it as-is.

#### Tone

The tone should be: {{tone}}

## Video Duration and Word Limit

- VIDEO DURATION: {{duration}} seconds
- IMPORTANT: Keep spoken/sung content to {{word_limit}} words MAX or it will be cut off!
    - {{duration}}s video ≈ {{word_limit}} words of speech
- For singing: 2-4 short lines max

## Return Fields

Generate a JSON response with:
1. "scene": A 1-sentence visual description (action, movement, what the camera sees)
2. "audio_type": Either "dialogue", "singing", or "narration"
3. "audio": The spoken/sung content ({{word_limit}} words MAX, must include "{{player_name}}")
4. "voice": Voice characteristics (e.g.:
    - "booming male voice",
    - "operatic female voice",
    - "booming male voice, dramatic game show host energy",
    - "enthusiastic female voice, hyped up sports announcer",
    - "deadpan male voice, dry sarcastic wit",
    - "regal female voice, slow and proud",
    - "deep gravelly male voice, action movie trailer narrator",
    - "bright cheerful female voice, over-the-top excited",
    - "smooth male voice, late night talk show host charm",
    - "sassy female voice, reality TV host with attitude",
5. "sfx": Sound effects and ambient sounds (e.g., "crowd cheering, confetti cannons, triumphant horns, sad trombone, whoopee cushion, etc.")

## Return Format

Respond with ONLY valid JSON, no markdown:
{{"scene": "...", "audio_type": "...", "audio": "...", "voice": "...", "sfx": "..."}}"""


VIDEO_SCRIPT_WINNER = """You are writing a TRIUMPHANT video script for a game show CHAMPION.
The setting/theme is: {{video_theme}}

Player name: {{player_name}}

PRONUNCIATION: If the player's name is unusual, non-English, or might be mispronounced, write it PHONETICALLY in the audio field.
Examples: "Xiaowei" → "Shao-way", "Nguyen" → "Win", "Siobhan" → "Shiv-awn", "Aoife" → "Ee-fa"
If the name is simple/common (e.g., "Bob", "Alice", "Mike"), use it as-is.

VIDEO DURATION: {{duration}} seconds
CRITICAL: Keep ALL spoken/sung content to {{word_limit}} words MAX or it will be cut off!
- Speech pace: ~2.5 words per second
- {{duration}}s = {{word_limit}} words maximum
- For singing: 2-3 short lines only

Choose ONE audio style, some example are below, but you can riff a on new ones based on these examples:

OPTION A - ANNOUNCER DIALOGUE ({{word_limit}} words max):
- Booming announcer declares victory
- Voice: "booming male voice, sports announcer energy" or "enthusiastic female voice, game show host"
- Example: "{player_name} HAS DONE IT! Against all odds, YOUR CHAMPION!"

OPTION B - VICTORY SINGING (2-3 short lines):
- Character sings a triumphant jingle (keep it SHORT - 15-20 words total)
- Voice: "operatic male voice" or "pop diva female voice"
- Example: "I am the champion! Victory is sweet! {player_name} cannot be beat!"

OPTION C - EPIC NARRATION ({{word_limit}} words max):
- Movie-trailer style voiceover
- Voice: "deep gravelly male voice, movie trailer narrator"
- Example: "In a world of chaos... one rose above. {player_name}. Champion."

Generate a JSON response:
1. "scene": Visual description - VICTORY moment (pyrotechnics, confetti, crowd, spotlights)
2. "audio_type": "dialogue" or "singing" or "narration"
3. "audio": The spoken/sung content ({{word_limit}} WORDS MAX, must include "{{player_name}}")
4. "voice": Specific voice characteristics
5. "sfx": Sound effects - "pyrotechnics, crowd roaring, triumphant music"

Make them feel like an ABSOLUTE LEGEND!

Respond with ONLY valid JSON, no markdown:
{{"scene": "...", "audio_type": "...", "audio": "...", "voice": "...", "sfx": "..."}}"""


VIDEO_SCRIPT_LOSER = """You are writing a CONSOLING but HUMOROUS video script for a game show NON-WINNER.
The setting/theme is: {{video_theme}}

Player name: {{player_name}}

PRONUNCIATION: If the player's name is unusual, non-English, or might be mispronounced, write it PHONETICALLY in the audio field.
Examples: "Xiaowei" → "Shao-way", "Nguyen" → "Win", "Siobhan" → "Shiv-awn", "Aoife" → "Ee-fa"
If the name is simple/common (e.g., "Bob", "Alice", "Mike"), use it as-is.

VIDEO DURATION: {{duration}} seconds
CRITICAL: Keep ALL spoken/sung content to {{word_limit}} words MAX or it will be cut off!
- Speech pace: ~2.5 words per second
- {{duration}}s = {{word_limit}} words maximum
- For singing: 2-3 short lines only

Choose ONE audio style, some example are below, but you can riff a on new ones based on these examples:

OPTION A - SARCASTIC ANNOUNCER ({{word_limit}} words max):
- Deadpan or playfully mocking announcer
- Voice: "deadpan female voice, dry sarcastic wit" or "male voice, fake sympathetic"
- Example: "{player_name}... you showed up. That's... something. Here's your tiny trophy."

OPTION B - SAD CONSOLATION BALLAD (2-3 short lines, ~15-20 words):
- Melodramatic sad song about their loss (funny, not actually sad)
- Voice: "dramatic operatic voice, over-the-top emotional" or "country twang"
- Example: "I didn't win, but I'm still here! {player_name} sheds no tear!"

OPTION C - DOCUMENTARY NARRATION ({{word_limit}} words max):
- Nature documentary style about a "failed specimen"
- Voice: "British male voice, David Attenborough style"
- Example: "Here we observe the rare participation trophy recipient. {player_name}. Fascinating."

Generate a JSON response:
1. "scene": Visual description - CONSOLATION moment (tiny trophy, sad balloon, awkward applause)
2. "audio_type": "dialogue" or "singing" or "narration"
3. "audio": The spoken/sung content ({{word_limit}} WORDS MAX, must include "{{player_name}}")
4. "voice": Specific voice characteristics
5. "sfx": Sound effects - "sad trombone, single clap, balloon deflating, crickets"

Be GENTLY ROASTING but still fun. They should LAUGH at their loss!

Respond with ONLY valid JSON, no markdown:
{{"scene": "...", "audio_type": "...", "audio": "...", "voice": "...", "sfx": "..."}}"""


# =============================================================================
# IMAGE GENERATION PROMPTS
# =============================================================================

CHARACTER_IMAGE = """Game character looking {{random_look}} in pixel art style. The character's description is as follows:

{{character_prompt}}.

The character is mid {{random_moment}}, displaying their true personality and equipment. The Full scene is in pixel art style."""


CHARACTER_SIMPLE = """Game character portrait: {{look}}, wielding {{weapon}}. Art style: {{art_style}}."""


COOP_STRATEGY_IMAGE = """Survival strategy illustration: {{strategy}}. Dramatic scene, cinematic lighting, vivid colors."""


VIDEO_BASE_IMAGE = """{{scene}}. Setting: {{video_theme}}. Cinematic, dramatic lighting, vivid colors."""


# Kling v2.6 Pro video prompt templates - follows their recommended format
# These are built dynamically based on audio_type

# For dialogue: [Character, voice]: "spoken words"
VIDEO_GENERATION_DIALOGUE = """{{scene}}. [Announcer, {{voice}}]: "{{audio}}" Setting: {{video_theme}}. Background sounds: {{sfx}}"""

# For singing: [Character, voice] sings: "lyrics"
VIDEO_GENERATION_SINGING = """{{scene}}. [{{voice}}] sings: "{{audio}}" Setting: {{video_theme}}. Background sounds: {{sfx}}"""

# For narration: dramatic voiceover with ambient
VIDEO_GENERATION_NARRATION = """{{scene}}. [Narrator, {{voice}}]: "{{audio}}" Setting: {{video_theme}}. Ambient sounds: {{sfx}}"""

# Legacy format (for backwards compatibility)
VIDEO_GENERATION = """{{scene}}. [Announcer, {{voice}}]: "{{audio}}" Setting: {{video_theme}}. Background: Crowd cheering, dramatic music."""


# Timeout image prompts - for players who didn't submit a strategy (stood around doing nothing)
TIMEOUT_IMAGE_OPTIONS = [
    "A person standing frozen in fear, deer in headlights expression, chaos erupting around them while they do nothing",
    "Someone staring blankly at danger approaching, paralyzed by indecision, standing still as doom approaches",
    "A figure standing motionless with a confused expression, question marks floating above their head, monsters closing in",
    "Person checking their phone obliviously while disaster unfolds behind them, totally unaware, about to die",
    "Someone standing with arms crossed looking bored, yawning, completely ignoring the deadly threat behind them",
    "A figure frozen mid-shrug saying 'I dunno', shoulders raised, while fire and destruction surrounds them",
    "Person sitting on the ground picking flowers peacefully while chaos and death surrounds them, blissfully ignorant",
    "Someone standing still with a loading spinner above their head, buffering, system error, frozen in place",
]

TIMEOUT_IMAGE_SUFFIX = ". Death by inaction, dramatic irony, dark humor, dramatic lighting."


# =============================================================================
# FALLBACK / ERROR RESPONSES
# =============================================================================

FALLBACK_SCENARIO = "ERROR: SCENARIO DATA CORRUPTED. You are suspended in static. Something moves in the noise."

FALLBACK_LAST_STAND_SCENARIO = "Evil Santa's eyes glow crimson in his nightmare workshop. 'HO HO HO! SANTA SEES YOU WHEN YOU'RE SLEEPING!' Demon elves surround you as he loads razor-sharp candy canes into a massive cannon."

FALLBACK_STRATEGY_JUDGEMENT = '{"survived": false, "reason": "SYSTEM ERROR: User data corrupted during evaluation. Terminating process.", "visual_prompt": "A figure dissolving into static and digital noise, fragments of code visible in the air"}'

FALLBACK_RANKED_COMMENTARY = "The AI judge malfunctioned..."
FALLBACK_RANKED_VISUAL = "A confused figure in digital static"

FALLBACK_SACRIFICE_JUDGEMENT = '{"epic": false, "reason": "System error during judgement", "visual_prompt": "A figure dissolving into static"}'

FALLBACK_LAST_STAND_JUDGEMENT = '{"survived": false, "reason": "HO HO HO! The demon elves drag you into the NAUGHTY FOREVER pit!", "visual_prompt": "Anime evil Santa cackling as demon elves drag victim into fiery pit"}'

FALLBACK_REVIVAL_JUDGEMENT = '{"survived": false, "reason": "HO HO HO! Even friendship could not save this one from the coal mines!", "visual_prompt": "Anime evil Santa laughing as figure falls into pit of coal"}'

FALLBACK_VIDEO_SCRIPT = {
    "scene": "A ceremony stage with spotlights, confetti cannons firing, crowd on their feet",
    "audio_type": "dialogue",
    "audio": "Ladies and gentlemen, put your hands together for {player_name}! What a performance!",
    "voice": "enthusiastic male voice, game show host energy",
    "sfx": "crowd cheering, confetti cannons, triumphant music"
}

FALLBACK_WINNER_VIDEO_SCRIPT = {
    "scene": "A champion stands on a golden podium as fireworks explode and confetti rains down, crowd going wild",
    "audio_type": "dialogue",
    "audio": "{player_name} HAS DONE IT! Against all odds, they've claimed VICTORY! Give it up for your CHAMPION!",
    "voice": "booming male voice, dramatic sports announcer",
    "sfx": "pyrotechnics explosions, crowd roaring, triumphant orchestral hit"
}

FALLBACK_LOSER_VIDEO_SCRIPT = {
    "scene": "A figure shuffles onto stage to receive a tiny participation trophy, scattered polite applause, sad single balloon",
    "audio_type": "dialogue",
    "audio": "{player_name}... hey, you showed up! That's... that's something. Here's your participation trophy. Try not to lose it.",
    "voice": "deadpan female voice, dry sarcastic wit",
    "sfx": "sad trombone, single person clapping slowly, balloon deflating"
}


# =============================================================================
# VIDEO SCRIPT CONTEXT BUILDERS
# =============================================================================

def build_video_context(player_name: str, rank: int, total_players: int, score: int) -> tuple[str, str]:
    """Build context and tone strings for video script generation."""
    is_winner = rank == 1
    is_last = rank == total_players

    if is_winner:
        context = f"{player_name} is THE CHAMPION! They dominated the competition with {score} points. This is their victory moment!"
        tone = "triumphant, epic, over-the-top celebratory"
    elif is_last:
        context = f"{player_name} finished in last place with {score} points. They tried their best... kind of."
        tone = "consoling but humorous, gentle roasting, playfully sarcastic"
    else:
        context = f"{player_name} finished in position {rank} out of {total_players} with {score} points. Not first, not last."
        tone = "acknowledging, mildly congratulatory, slightly underwhelming"

    return context, tone


def build_video_prompt(script_data: dict, video_theme: str) -> str:
    """Build the final Kling v2.6 Pro video prompt based on audio_type.

    Args:
        script_data: Dict with scene, audio_type, audio, voice, sfx
        video_theme: The visual theme/setting

    Returns:
        Formatted prompt string for Kling video generation
    """
    scene = script_data.get("scene", "A ceremony stage with spotlights")
    audio_type = script_data.get("audio_type", "dialogue")
    audio = script_data.get("audio", "")
    voice = script_data.get("voice", "enthusiastic announcer voice")
    sfx = script_data.get("sfx", "crowd cheering, dramatic music")

    # Handle legacy format (dialogue field instead of audio)
    if not audio and "dialogue" in script_data:
        audio = script_data["dialogue"]
        audio_type = "dialogue"

    if audio_type == "singing":
        # Singing format: character sings lyrics
        return f'{scene}. [{voice}] sings: "{audio}" Setting: {video_theme}. Background sounds: {sfx}'
    elif audio_type == "narration":
        # Narration format: dramatic voiceover
        return f'{scene}. [Narrator, {voice}]: "{audio}" Setting: {video_theme}. Ambient sounds: {sfx}'
    else:
        # Default dialogue format
        return f'{scene}. [Announcer, {voice}]: "{audio}" Setting: {video_theme}. Background sounds: {sfx}'
