"""SVG illustrations for DeskPilot splash screen and UI.

All SVGs use template strings with color placeholders that can be filled
from theme colors. Required color keys:
- accent, accent_dark, accent_soft
- surface, bg, bg_alt
- border, border_soft
- text, text_muted
- tag_* colors
"""

# Main DeskPilot logo - friendly robot copilot mascot
LOGO_SVG = '''
<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{accent};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{accent_dark};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="screenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg};stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <!-- Shadow -->
  <ellipse cx="60" cy="105" rx="35" ry="8" fill="{border_soft}" opacity="0.3"/>
  <!-- Robot body -->
  <rect x="25" y="35" width="70" height="55" rx="12" fill="url(#bodyGrad)" />
  <!-- Screen face -->
  <rect x="32" y="42" width="56" height="35" rx="6" fill="url(#screenGrad)" />
  <!-- Eyes with glow -->
  <circle cx="48" cy="58" r="7" fill="{accent}" filter="url(#glow)" opacity="0.3"/>
  <circle cx="72" cy="58" r="7" fill="{accent}" filter="url(#glow)" opacity="0.3"/>
  <circle cx="48" cy="58" r="6" fill="{accent}" />
  <circle cx="72" cy="58" r="6" fill="{accent}" />
  <circle cx="50" cy="56" r="2.5" fill="{bg}" />
  <circle cx="74" cy="56" r="2.5" fill="{bg}" />
  <!-- Smile -->
  <path d="M50 68 Q60 78 70 68" stroke="{accent}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <!-- Antenna -->
  <rect x="56" y="18" width="8" height="20" rx="4" fill="{accent_dark}" />
  <circle cx="60" cy="16" r="7" fill="{accent}" />
  <circle cx="60" cy="16" r="4" fill="{bg}" opacity="0.4"/>
  <!-- Wings/Arms -->
  <ellipse cx="16" cy="58" rx="12" ry="22" fill="{accent}" opacity="0.6" />
  <ellipse cx="104" cy="58" rx="12" ry="22" fill="{accent}" opacity="0.6" />
  <!-- Wing details -->
  <path d="M12 48 Q8 58 12 68" stroke="{bg}" stroke-width="2" fill="none" opacity="0.4"/>
  <path d="M108 48 Q112 58 108 68" stroke="{bg}" stroke-width="2" fill="none" opacity="0.4"/>
  <!-- Base -->
  <rect x="35" y="88" width="50" height="14" rx="7" fill="{accent_dark}" />
  <rect x="42" y="91" width="36" height="4" rx="2" fill="{accent}" opacity="0.5"/>
</svg>
'''

# Actions icon - lightning bolt representing quick automation
ACTIONS_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="actionGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#actionGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Lightning bolt -->
  <path d="M36 12 L24 30 H32 L28 52 L44 28 H36 Z" fill="{accent}">
    <animate attributeName="opacity" values="1;0.7;1" dur="1.5s" repeatCount="indefinite"/>
  </path>
  <!-- Spark effects -->
  <circle cx="22" cy="20" r="2" fill="{accent}" opacity="0.6"/>
  <circle cx="46" cy="44" r="1.5" fill="{accent}" opacity="0.5"/>
</svg>
'''

# Launchers icon - rocket ship
LAUNCHERS_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="launchGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="flameGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{tag_orange};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{tag_red};stop-opacity:0.8" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#launchGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Rocket body -->
  <path d="M32 10 C22 20 18 32 20 46 L32 42 L44 46 C46 32 42 20 32 10Z" fill="{accent}" />
  <!-- Rocket highlight -->
  <path d="M32 10 C28 18 26 28 27 38 L32 36 L32 10Z" fill="{bg}" opacity="0.2"/>
  <!-- Window -->
  <circle cx="32" cy="26" r="6" fill="{bg}" stroke="{border_soft}" stroke-width="1"/>
  <circle cx="32" cy="26" r="3" fill="{accent_soft}"/>
  <!-- Fins -->
  <path d="M20 46 L12 54 L20 50 Z" fill="{accent_dark}" />
  <path d="M44 46 L52 54 L44 50 Z" fill="{accent_dark}" />
  <!-- Flame with animation -->
  <path d="M26 46 Q28 54 32 58 Q36 54 38 46 Q34 50 32 48 Q30 50 26 46" fill="url(#flameGrad)">
    <animate attributeName="d" 
      values="M26 46 Q28 54 32 58 Q36 54 38 46 Q34 50 32 48 Q30 50 26 46;
              M26 46 Q28 56 32 62 Q36 56 38 46 Q34 52 32 50 Q30 52 26 46;
              M26 46 Q28 54 32 58 Q36 54 38 46 Q34 50 32 48 Q30 50 26 46"
      dur="0.5s" repeatCount="indefinite"/>
  </path>
</svg>
'''

# Templates icon - document with magic sparkles
TEMPLATES_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="templateGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#templateGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Document -->
  <rect x="16" y="12" width="26" height="36" rx="3" fill="{bg}" stroke="{border}" stroke-width="1.5"/>
  <!-- Folded corner -->
  <path d="M36 12 L42 18 L36 18 Z" fill="{border_soft}"/>
  <!-- Lines on doc -->
  <line x1="20" y1="24" x2="38" y2="24" stroke="{text_muted}" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="30" x2="34" y2="30" stroke="{text_muted}" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="36" x2="36" y2="36" stroke="{text_muted}" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="42" x2="30" y2="42" stroke="{text_muted}" stroke-width="2" stroke-linecap="round"/>
  <!-- Magic wand -->
  <rect x="34" y="30" width="18" height="4" rx="2" fill="{tag_purple}" transform="rotate(-45 43 32)"/>
  <!-- Star tip -->
  <path d="M52 20 L54 24 L58 24 L55 27 L56 31 L52 28 L48 31 L49 27 L46 24 L50 24 Z" fill="{tag_purple}">
    <animate attributeName="opacity" values="1;0.5;1" dur="1s" repeatCount="indefinite"/>
  </path>
  <!-- Sparkles -->
  <circle cx="44" cy="16" r="2" fill="{tag_purple}" opacity="0.8">
    <animate attributeName="r" values="2;3;2" dur="1.2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="56" cy="36" r="1.5" fill="{tag_purple}" opacity="0.6"/>
  <circle cx="48" cy="42" r="1" fill="{tag_purple}" opacity="0.7"/>
</svg>
'''

# Macros icon - gear with play button (automation)
MACROS_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="macroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#macroGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Outer gear -->
  <path d="M32 14 L34 18 L38 16 L40 20 L44 20 L44 24 L48 26 L46 30 L48 34 L44 36 L44 40 L40 40 L38 44 L34 42 L32 46 L30 42 L26 44 L24 40 L20 40 L20 36 L16 34 L18 30 L16 26 L20 24 L20 20 L24 20 L26 16 L30 18 Z" 
        fill="{accent}">
    <animateTransform attributeName="transform" type="rotate" from="0 32 30" to="360 32 30" dur="8s" repeatCount="indefinite"/>
  </path>
  <!-- Inner gear hub -->
  <circle cx="32" cy="30" r="10" fill="{surface}" stroke="{border_soft}" stroke-width="1"/>
  <!-- Play symbol -->
  <path d="M29 26 L29 34 L37 30 Z" fill="{accent}" />
  <!-- Motion lines -->
  <path d="M10 32 Q14 30 10 28" stroke="{accent}" stroke-width="1.5" fill="none" opacity="0.5"/>
  <path d="M54 32 Q50 30 54 28" stroke="{accent}" stroke-width="1.5" fill="none" opacity="0.5"/>
</svg>
'''

# Settings icon - sliders and controls
SETTINGS_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="settingsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#settingsGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Slider tracks -->
  <line x1="16" y1="22" x2="48" y2="22" stroke="{border}" stroke-width="3" stroke-linecap="round"/>
  <line x1="16" y1="32" x2="48" y2="32" stroke="{border}" stroke-width="3" stroke-linecap="round"/>
  <line x1="16" y1="42" x2="48" y2="42" stroke="{border}" stroke-width="3" stroke-linecap="round"/>
  <!-- Active portions -->
  <line x1="16" y1="22" x2="36" y2="22" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <line x1="16" y1="32" x2="24" y2="32" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <line x1="16" y1="42" x2="40" y2="42" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <!-- Slider knobs -->
  <circle cx="36" cy="22" r="5" fill="{accent}" stroke="{bg}" stroke-width="2"/>
  <circle cx="24" cy="32" r="5" fill="{accent}" stroke="{bg}" stroke-width="2"/>
  <circle cx="40" cy="42" r="5" fill="{accent}" stroke="{bg}" stroke-width="2"/>
</svg>
'''

# Test/Debug icon - bug with magnifying glass
TEST_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="testGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#testGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Bug body -->
  <ellipse cx="28" cy="30" rx="10" ry="12" fill="{accent}"/>
  <!-- Bug head -->
  <circle cx="28" cy="18" r="6" fill="{accent}"/>
  <!-- Bug eyes -->
  <circle cx="26" cy="17" r="2" fill="{bg}"/>
  <circle cx="30" cy="17" r="2" fill="{bg}"/>
  <!-- Bug legs -->
  <path d="M18 26 L12 22" stroke="{accent_dark}" stroke-width="2" stroke-linecap="round"/>
  <path d="M18 32 L10 32" stroke="{accent_dark}" stroke-width="2" stroke-linecap="round"/>
  <path d="M18 38 L12 42" stroke="{accent_dark}" stroke-width="2" stroke-linecap="round"/>
  <path d="M38 26 L42 24" stroke="{accent_dark}" stroke-width="2" stroke-linecap="round"/>
  <path d="M38 32 L42 32" stroke="{accent_dark}" stroke-width="2" stroke-linecap="round"/>
  <!-- Magnifying glass -->
  <circle cx="44" cy="44" r="10" fill="none" stroke="{text_muted}" stroke-width="3"/>
  <line x1="51" y1="51" x2="58" y2="58" stroke="{text_muted}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="44" cy="44" r="7" fill="{bg}" opacity="0.3"/>
</svg>
'''

# Hotkey icon - keyboard key
HOTKEY_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="keyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <!-- Key base -->
  <rect x="6" y="10" width="36" height="28" rx="6" fill="url(#keyGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Key top surface -->
  <rect x="10" y="12" width="28" height="20" rx="4" fill="{surface}" stroke="{border_soft}" stroke-width="1"/>
  <!-- Key symbol -->
  <text x="24" y="27" font-size="12" font-weight="bold" text-anchor="middle" fill="{accent}">⌘</text>
</svg>
'''

# Success checkmark
SUCCESS_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="20" fill="{tag_green}" opacity="0.15"/>
  <circle cx="24" cy="24" r="16" fill="none" stroke="{tag_green}" stroke-width="3"/>
  <path d="M16 24 L21 29 L32 18" stroke="{tag_green}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''

# Error/Warning icon
ERROR_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="20" fill="{tag_red}" opacity="0.15"/>
  <circle cx="24" cy="24" r="16" fill="none" stroke="{tag_red}" stroke-width="3"/>
  <line x1="18" y1="18" x2="30" y2="30" stroke="{tag_red}" stroke-width="3" stroke-linecap="round"/>
  <line x1="30" y1="18" x2="18" y2="30" stroke="{tag_red}" stroke-width="3" stroke-linecap="round"/>
</svg>
'''

# Animated loading dots
LOADING_DOTS_SVG = '''
<svg viewBox="0 0 80 24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="12" r="6" fill="{accent}">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite" begin="0s"/>
    <animate attributeName="r" values="6;5;6" dur="1.2s" repeatCount="indefinite" begin="0s"/>
  </circle>
  <circle cx="40" cy="12" r="6" fill="{accent}">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite" begin="0.2s"/>
    <animate attributeName="r" values="6;5;6" dur="1.2s" repeatCount="indefinite" begin="0.2s"/>
  </circle>
  <circle cx="64" cy="12" r="6" fill="{accent}">
    <animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite" begin="0.4s"/>
    <animate attributeName="r" values="6;5;6" dur="1.2s" repeatCount="indefinite" begin="0.4s"/>
  </circle>
</svg>
'''

# Empty state - no items illustration
EMPTY_STATE_SVG = '''
<svg viewBox="0 0 200 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="emptyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <!-- Document stack -->
  <rect x="50" y="40" width="100" height="70" rx="8" fill="{border_soft}" opacity="0.3"/>
  <rect x="45" y="35" width="100" height="70" rx="8" fill="{border_soft}" opacity="0.5"/>
  <rect x="40" y="30" width="100" height="70" rx="8" fill="url(#emptyGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Document lines -->
  <rect x="50" y="45" width="60" height="6" rx="3" fill="{border}"/>
  <rect x="50" y="56" width="45" height="6" rx="3" fill="{border}" opacity="0.6"/>
  <rect x="50" y="67" width="55" height="6" rx="3" fill="{border}" opacity="0.4"/>
  <rect x="50" y="78" width="35" height="6" rx="3" fill="{border}" opacity="0.3"/>
  <!-- Add button -->
  <circle cx="155" cy="115" r="22" fill="{accent_soft}" stroke="{accent}" stroke-width="2"/>
  <line x1="155" y1="105" x2="155" y2="125" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <line x1="145" y1="115" x2="165" y2="115" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
  <!-- Text -->
  <text x="100" y="135" font-size="11" text-anchor="middle" fill="{text_muted}">No items yet</text>
  <text x="100" y="148" font-size="10" text-anchor="middle" fill="{text_muted}" opacity="0.7">Click + to add one</text>
</svg>
'''

# Workflow/Flow icon
FLOW_SVG = '''
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="flowBgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{surface};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_alt};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="28" fill="url(#flowBgGrad)" stroke="{border}" stroke-width="2"/>
  <!-- Flow nodes -->
  <circle cx="20" cy="20" r="7" fill="{flow_start}" stroke="{accent}" stroke-width="2"/>
  <rect x="40" y="14" width="14" height="12" rx="3" fill="{flow_step}" stroke="{accent}" stroke-width="2"/>
  <rect x="12" y="38" width="14" height="12" rx="3" fill="{flow_step}" stroke="{accent}" stroke-width="2"/>
  <circle cx="44" cy="44" r="7" fill="{flow_end}" stroke="{accent}" stroke-width="2"/>
  <!-- Arrows -->
  <path d="M27 20 L38 20" stroke="{flow_arrow}" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
  <path d="M47 28 L47 35" stroke="{flow_arrow}" stroke-width="2" fill="none"/>
  <path d="M20 28 L20 36" stroke="{flow_arrow}" stroke-width="2" fill="none"/>
  <path d="M28 44 L35 44" stroke="{flow_arrow}" stroke-width="2" fill="none"/>
  <!-- Arrow markers -->
  <defs>
    <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <polygon points="0 0, 6 3, 0 6" fill="{flow_arrow}"/>
    </marker>
  </defs>
</svg>
'''

# Clock/Schedule icon
SCHEDULE_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="18" fill="{surface}" stroke="{border}" stroke-width="2"/>
  <circle cx="24" cy="24" r="14" fill="none" stroke="{accent_soft}" stroke-width="1"/>
  <!-- Clock hands -->
  <line x1="24" y1="24" x2="24" y2="14" stroke="{accent}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="24" y1="24" x2="32" y2="28" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <!-- Center dot -->
  <circle cx="24" cy="24" r="3" fill="{accent}"/>
  <!-- Hour marks -->
  <circle cx="24" cy="10" r="1.5" fill="{text_muted}"/>
  <circle cx="38" cy="24" r="1.5" fill="{text_muted}"/>
  <circle cx="24" cy="38" r="1.5" fill="{text_muted}"/>
  <circle cx="10" cy="24" r="1.5" fill="{text_muted}"/>
</svg>
'''

# Run/Play icon
PLAY_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="18" fill="{accent}" opacity="0.15"/>
  <circle cx="24" cy="24" r="14" fill="{accent}"/>
  <path d="M20 16 L20 32 L34 24 Z" fill="{bg}"/>
</svg>
'''

# Stop icon
STOP_SVG = '''
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <circle cx="24" cy="24" r="18" fill="{tag_red}" opacity="0.15"/>
  <circle cx="24" cy="24" r="14" fill="{tag_red}"/>
  <rect x="17" y="17" width="14" height="14" rx="2" fill="{bg}"/>
</svg>
'''


def get_feature_icons(colors: dict) -> list[tuple[str, str]]:
    """Return list of (svg, label) tuples for the loading screen."""
    return [
        (ACTIONS_SVG.format(**colors), "Actions"),
        (LAUNCHERS_SVG.format(**colors), "Launchers"),
        (TEMPLATES_SVG.format(**colors), "Templates"),
        (MACROS_SVG.format(**colors), "Macros"),
    ]


def get_logo_svg(colors: dict) -> str:
    """Return the main logo SVG with colors applied."""
    return LOGO_SVG.format(**colors)


def get_loading_dots(colors: dict) -> str:
    """Return animated loading dots SVG."""
    return LOADING_DOTS_SVG.format(**colors)


def get_empty_state(colors: dict) -> str:
    """Return empty state illustration SVG."""
    return EMPTY_STATE_SVG.format(**colors)


def get_icon(name: str, colors: dict) -> str:
    """Get an icon SVG by name with colors applied."""
    icons = {
        "logo": LOGO_SVG,
        "actions": ACTIONS_SVG,
        "launchers": LAUNCHERS_SVG,
        "templates": TEMPLATES_SVG,
        "macros": MACROS_SVG,
        "settings": SETTINGS_SVG,
        "test": TEST_SVG,
        "hotkey": HOTKEY_SVG,
        "success": SUCCESS_SVG,
        "error": ERROR_SVG,
        "loading": LOADING_DOTS_SVG,
        "empty": EMPTY_STATE_SVG,
        "flow": FLOW_SVG,
        "schedule": SCHEDULE_SVG,
        "play": PLAY_SVG,
        "stop": STOP_SVG,
    }
    svg_template = icons.get(name, ACTIONS_SVG)
    return svg_template.format(**colors)
