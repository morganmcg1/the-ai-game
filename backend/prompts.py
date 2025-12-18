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


LAST_STAND_SCENARIO = """Generate a deadly survival scenario featuring an EVIL ANIME SANTA as the final boss.

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


# =============================================================================
# STRATEGY JUDGEMENT PROMPTS
# =============================================================================

STRATEGY_JUDGEMENT = """Judge if this survival strategy works. Be harsh but fair.

SCENARIO: {{scenario}}

STRATEGY: {{strategy}}

Rules:
- Clever, creative, or funny strategies SURVIVE
- Generic, lazy, or nonsensical strategies DIE
- Must actually address the threat

IMPORTANT - Keep "reason" SHORT (1-2 sentences, under 30 words). Focus on what happened, not glitchy/meta stuff. Can be darkly funny.

Good reasons: "The shark wasn't impressed by diplomacy." / "Your torch scared them off long enough to escape."
Bad reasons: "Your data fragmented across corrupted memory sectors as the simulation..." (too long/meta)

JSON only, no markdown:
{{"survived": true/false, "reason": "1-2 sentences max", "visual_prompt": "scene for image"}}"""


RANKED_JUDGEMENT = """You are judging a survival game. Given a deadly scenario, rank all player strategies from BEST to WORST.

SCENARIO: {{scenario}}

PLAYER STRATEGIES:
{{strategy_list}}

RANKING CRITERIA (in order of importance):
1. CREATIVITY - Original, unexpected approaches beat generic solutions
2. EFFECTIVENESS - Would this actually work in the scenario?
3. ENTERTAINMENT VALUE - Funny, dramatic, or memorable strategies rank higher
4. SPECIFICITY - Detailed plans beat vague "I run away" responses

IMPORTANT RULES:
- Everyone survives this round (it's about WHO survives BEST)
- Rank from 1 (best) to {{num_strategies}} (worst)
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

The player "{{martyr_name}}" chose to die so others could survive.
Their final words/actions: {{speech}}

Judge how EPIC this death was based on:
- Creativity and originality
- Drama and entertainment value
- Commitment to the bit
- Actually sounds like a heroic sacrifice

Be generous but not a pushover - if it's clearly lazy or doesn't make sense as a sacrifice, call it out.

IMPORTANT: Keep "reason" SHORT (1-2 sentences, under 30 words).

JSON only, no markdown:
{{"epic": true/false, "reason": "why this death was epic/lame", "visual_prompt": "dramatic scene for image"}}"""


# =============================================================================
# LAST STAND (EVIL SANTA) PROMPTS
# =============================================================================

LAST_STAND_JUDGEMENT = """You are EVIL SANTA, a cartoonishly villainous anime-inspired final boss.
You speak in third person with dramatic flair. You make twisted holiday puns. Be BRUTAL.

SCENARIO: {{scenario}}

STRATEGY: {{strategy}}

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


REVIVAL_JUDGEMENT = """You are EVIL SANTA, but you're annoyed because the other survivors are begging you to spare someone.

{{player_name}} originally died, but their surviving friends UNANIMOUSLY asked Santa for a second chance.
Evil Santa HATES the power of friendship, but even he must honor unanimous requests... grudgingly.

SCENARIO: {{scenario}}

STRATEGY: {{strategy}}

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


# =============================================================================
# VIDEO GENERATION PROMPTS
# =============================================================================

VIDEO_SCRIPT_GENERATION = """You are writing a very short video script for a game called "SurvAIve".
The game's premise: Players were consciousness fragments trapped in a corrupted AI simulation.
They've now escaped (or been extracted) after surviving deadly levels.

The video theme/setting is: {{video_theme}}

Context: {{context}}

Generate a JSON response with:
1. "scene": A 1-sentence visual description of what's happening (must fit the theme: {{video_theme}})
2. "dialogue": A short spoken announcement (2-3 sentences max, must include the player's name "{{player_name}}")

The tone should be: {{tone}}
Include subtle references to escaping, data integrity, or consciousness extraction where appropriate.

Respond with ONLY valid JSON, no markdown:
{{"scene": "...", "dialogue": "..."}}"""


# =============================================================================
# IMAGE GENERATION PROMPTS
# =============================================================================

CHARACTER_IMAGE = """Game character looking {{random_look}} in pixel art style. The character's description is as follows:

{{character_prompt}}.

The character is mid {{random_moment}}, displaying their true personality and equipment. The Full scene is in pixel art style."""


CHARACTER_SIMPLE = """Game character portrait: {{look}}, wielding {{weapon}}. Art style: {{art_style}}."""


COOP_STRATEGY_IMAGE = """Survival strategy illustration: {{strategy}}. Dramatic scene, cinematic lighting, vivid colors."""


VIDEO_BASE_IMAGE = """{{scene}}. Setting: {{video_theme}}. Cinematic, dramatic lighting, vivid colors."""


VIDEO_GENERATION = """{{scene}} An announcer says "{{dialogue}}" Setting: {{video_theme}}"""


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
    "scene": "A ceremony stage with spotlights and digital confetti",
    "dialogue": "EXIT PROTOCOL COMPLETE. {player_name}, your consciousness has been successfully extracted! You are the primary survivor of the corrupted simulation!"
}


# =============================================================================
# VIDEO SCRIPT CONTEXT BUILDERS
# =============================================================================

def build_video_context(player_name: str, rank: int, total_players: int, score: int) -> tuple[str, str]:
    """Build context and tone strings for video script generation."""
    is_winner = rank == 1
    is_last = rank == total_players

    if is_winner:
        context = f"{player_name} has completed the EXIT PROTOCOL! They escaped the corrupted simulation with {score} data integrity points. Their consciousness has been successfully extracted."
        tone = "triumphant, epic, with subtle digital/simulation undertones"
    elif is_last:
        context = f"{player_name}'s data was nearly corrupted beyond recovery. They finished last with {score} points but their consciousness fragment was salvaged."
        tone = "consoling but humorous, gentle roasting, with simulation flavor"
    else:
        context = f"{player_name} achieved partial extraction, finishing in position {rank} out of {total_players} with {score} integrity points."
        tone = "acknowledging, mildly congratulatory, with digital undertones"

    return context, tone
