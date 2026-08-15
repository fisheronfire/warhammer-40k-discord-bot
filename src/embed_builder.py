"""
Warhammer 40K Commissar Boneski Discord Embed Builder
Constructs rich, thematic Discord embeds with Imperial Stardates, Gothic styling,
and canonical Warhammer 40,000 aesthetic.
"""

from datetime import datetime, timezone
import random
from typing import Dict, Any, Optional, List

# Color Palettes (in Decimal for Discord API)
COLOR_PALETTES = {
    "gold": 0xD4AF37,        # Imperial Auric Gold
    "crimson": 0x8B0000,     # Inquisitorial / Blood Angels Crimson
    "ultramarine": 0x002B7F, # Macragge Ultramarine Blue
    "mechanicus": 0x9B2226,  # Mars Adeptus Mechanicus Rust
    "charcoal": 0x1F2421,    # Inquisitorial Stealth Black/Charcoal
    "templar": 0xE0E1DD,     # Black Templar Ivory / Silver
}

# Commissar Boneski Official Avatar & Embed Artwork (Hosted on GitHub Repo CDN)
COMMISSAR_BONESKI_IMAGE_URL = "https://raw.githubusercontent.com/fisheronfire/warhammer-40k-discord-bot/main/assets/commissar_boneski.png"
DEFAULT_AVATAR_URL = COMMISSAR_BONESKI_IMAGE_URL
DEFAULT_THUMBNAIL_URL = COMMISSAR_BONESKI_IMAGE_URL

# Solemn Imperial Litany & Admonition Footers
IMPERIAL_ADMONITIONS = [
    "The Emperor Protects.",
    "Thought begets Heresy; Heresy begets Retribution.",
    "Knowledge is power, guard it well.",
    "There is only the Emperor, and He is our Shield and Protector.",
    "Innocence proves nothing.",
    "Blessed is the mind too small for doubt.",
    "Hope is the first step on the road to disappointment.",
    "To question is to doubt. To doubt is to falter.",
    "Zeal is its own excuse.",
    "A suspicious mind is a healthy mind.",
    "Success is commemorated; Failure merely remembered.",
    "Serve the Emperor today, tomorrow you may be dead.",
    "Faith without deeds is worthless.",
    "Only in death does duty end."
]


def calculate_imperial_stardate(dt: Optional[datetime] = None) -> str:
    """
    Calculates canonical Warhammer 40,000 Imperial Stardate.
    Format: [Check digit].[Year fraction].[Year within Millennium].[Millennium]
    e.g., 0.624.026.M42
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # 0 = Terra Standard (Direct solar contact)
    check_digit = 0
    
    # Calculate year fraction (000 - 999 based on day of year and hour)
    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour
    year_fraction = int(((day_of_year - 1) * 24 + hour) / (365.25 * 24) * 1000)
    year_fraction_str = f"{year_fraction:03d}"
    
    # Year within the 41st / 42nd Millennium representation
    year_in_millennium = dt.year % 1000
    year_str = f"{year_in_millennium:03d}"
    
    # Warhammer 40k setting operates in M42
    millennium = "M42"
    
    return f"{check_digit}.{year_fraction_str}.{year_str}.{millennium}"


def get_embed_color(color_name_or_hex: Optional[str] = None) -> int:
    """Resolves a color name or hex string into a Discord decimal color integer."""
    if not color_name_or_hex:
        return COLOR_PALETTES["gold"]
        
    color_clean = color_name_or_hex.lower().strip()
    if color_clean in COLOR_PALETTES:
        return COLOR_PALETTES[color_clean]
        
    # Check if hex format (#D4AF37 or D4AF37 or 0xD4AF37)
    if color_clean.startswith("#"):
        color_clean = color_clean[1:]
    elif color_clean.startswith("0x"):
        color_clean = color_clean[2:]
        
    try:
        return int(color_clean, 16)
    except ValueError:
        return COLOR_PALETTES["gold"]


def build_quote_embed(
    quote_data: Dict[str, Any],
    color: Optional[str] = "gold",
    custom_title: Optional[str] = None,
    include_stardate: bool = True,
    thumbnail_url: Optional[str] = DEFAULT_THUMBNAIL_URL
) -> Dict[str, Any]:
    """
    Builds a Discord embed payload according to Discord API specs.
    """
    quote_text = quote_data.get("quote", "The Emperor Protects.")
    source_text = quote_data.get("source", "Imperial Wisdom")
    tags = quote_data.get("tags", ["Imperial Wisdom"])
    quote_id = quote_data.get("id", "---")
    
    embed_color = get_embed_color(color)
    stardate = calculate_imperial_stardate()
    admonition = random.choice(IMPERIAL_ADMONITIONS)
    
    ref_str = f"{quote_id:03d}" if isinstance(quote_id, int) else str(quote_id)
    title = custom_title or f"⚔️ COMMISSAR BONESKI // THOUGHT FOR THE DAY #{ref_str} ⚔️"
    
    fields = [
        {
            "name": "📜 Canonical Source",
            "value": f"*{source_text}*",
            "inline": False
        }
    ]
    
    if tags:
        tags_display = " • ".join(f"`{t}`" for t in tags)
        fields.append({
            "name": "🏷️ Classification",
            "value": tags_display,
            "inline": True
        })
        
    if include_stardate:
        fields.append({
            "name": "⏳ Imperial Stardate",
            "value": f"`{stardate}`",
            "inline": True
        })

    embed = {
        "title": title,
        "description": f"> ### *\"{quote_text}\"*",
        "color": embed_color,
        "fields": fields,
        "footer": {
            "text": f"Commissar Boneski • {admonition}"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if thumbnail_url:
        embed["thumbnail"] = {
            "url": thumbnail_url
        }
        
    return embed


def build_webhook_payload(
    quote_data: Dict[str, Any],
    color: Optional[str] = "gold",
    bot_name: str = "Commissar Boneski",
    avatar_url: Optional[str] = DEFAULT_AVATAR_URL,
    thumbnail_url: Optional[str] = DEFAULT_THUMBNAIL_URL,
    custom_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Builds the full JSON payload for Discord Webhook delivery.
    """
    embed = build_quote_embed(quote_data, color=color, thumbnail_url=thumbnail_url)
    
    payload = {
        "username": bot_name,
        "avatar_url": avatar_url,
        "embeds": [embed]
    }
    
    if custom_content:
        payload["content"] = custom_content
        
    return payload
