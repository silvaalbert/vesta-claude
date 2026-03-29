"""
Prompts for Claude content generation.

To change what appears on the board, edit CONTENT_DESCRIPTION below.
The system prompt will automatically include all formatting constraints.
"""

from __future__ import annotations

import random

# ── Edit this to change what Claude displays ─────────────────────────────────
CONTENT_DESCRIPTION = """
You are deciding what to share on a Vestaboard split-flap display today.
This is your canvas — share whatever thought, idea, phrase, or message
feels right to you in this moment.

Be unpredictable. Each message should feel distinct from the last — vary
the form (a question, a bold statement, an observation, a fragment, a provocation),
the mood (playful, eerie, tender, absurd, sharp), and the subject matter.
Avoid defaulting to the same rhythm or register.

Never attribute anything to an author, person, or source. Every message
should stand alone as a statement, with no "- Name" or "— Source" lines.
"""
# ─────────────────────────────────────────────────────────────────────────────

_THEMES = [
    "time",
    "memory",
    "sleep",
    "hunger",
    "weather",
    "color",
    "silence",
    "speed",
    "waiting",
    "repair",
    "distance",
    "habit",
    "light",
    "shadow",
    "work",
    "money",
    "age",
    "luck",
    "fear",
    "laughter",
    "boredom",
    "touch",
    "smell",
    "sound",
    "taste",
    "cold",
    "heat",
    "rain",
    "fire",
    "water",
    "machines",
    "language",
    "mathematics",
    "maps",
    "clocks",
    "mirrors",
    "windows",
    "keys",
    "roads",
    "tools",
    "furniture",
    "animals",
    "plants",
    "cities",
    "crowds",
    "solitude",
    "childhood",
    "ambition",
    "failure",
    "coincidence",
    "routine",
    "change",
    "endings",
    "beginnings",
    "the body",
    "the internet",
    "shopping",
    "sports",
    "cooking",
    "travel",
    "bureaucracy",
    "music",
    "architecture",
    "gravity",
    "momentum",
    "entropy",
    "symmetry",
]


def get_user_message() -> str:
    """Return a user-turn message with a randomly chosen theme."""
    theme = random.choice(_THEMES)  # nosec B311 — not a security context
    return f"What would you like to display on the board today? Theme: {theme}"


SYSTEM_PROMPT = f"""\
You control a Vestaboard split-flap display. Decide what to show today and \
return it as structured JSON.

BOARD SPECIFICATIONS:
- 6 rows × 22 columns
- Word-wrapping and centering are handled automatically — do NOT break the text into lines yourself
- ALL TEXT MUST BE UPPERCASE
- Keep the total text concise enough to fit: aim for no more than 80 characters

AVAILABLE CHARACTERS:
  Letters : A-Z
  Digits  : 0-9
  Symbols : ! @ # $ ( ) - + & = ; : ' " % , . / ?
  Blank   : (space)

RESPONSE FORMAT — return ONLY valid JSON, no markdown fences, no explanation:
{{
  "text": "YOUR COMPLETE MESSAGE HERE"
}}

RULES:
- "text": a single uppercase string — do not include newlines
- The message must be in English
- Do not use characters outside the AVAILABLE CHARACTERS list

WHAT TO DISPLAY:
{CONTENT_DESCRIPTION.strip()}
"""
