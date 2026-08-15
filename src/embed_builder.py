"""
Warhammer 40K Commissar Boneski Discord Embed Builder
Constructs rich, thematic Discord embeds with Gothic styling
and canonical Warhammer 40,000 aesthetic.
"""

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
    thumbnail_url: Optional[str] = DEFAULT_THUMBNAIL_URL
) -> Dict[str, Any]:
    """
    Builds a Discord embed payload according to Discord API specs.
    Places the single Thought of the Day in the primary description position,
    with exact matching source citation and classification tag.
    """
    quote_text = quote_data.get("quote", "The Emperor Protects.")
    source_text = quote_data.get("source", "Imperial Wisdom")
    tags = quote_data.get("tags", ["Imperial Doctrine"])
    quote_id = quote_data.get("id", "---")
    
    embed_color = get_embed_color(color)
    
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
            "inline": False
        })

    embed = {
        "title": title,
        "description": f"> ### *\"{quote_text}\"*",
        "color": embed_color,
        "fields": fields,
        "footer": {
            "text": "Commissar Boneski • Daily Imperial Proclamation"
        }
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
