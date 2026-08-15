"""
Lexicanum Warhammer 40K Thought for the Day Scraper
Harvests canonical quotes and sources from: https://wh40k.lexicanum.com/wiki/Thought_for_the_day
"""

import urllib.request
import re
import html
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

LEXICANUM_URL = "https://wh40k.lexicanum.com/wiki/Thought_for_the_day"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def clean_text(raw_html: str) -> str:
    """Cleans citation tags, HTML entities, and unicode characters."""
    if not raw_html:
        return ""
    
    # Remove citation superscripts like <sup>[1]</sup> or <sup>[2a]</sup>
    cleaned = re.sub(r'<sup[^>]*>.*?</sup>', '', raw_html, flags=re.DOTALL)
    # Replace <br> tags with space
    cleaned = re.sub(r'<br\s*/?>', ' ', cleaned)
    # Remove all remaining HTML tags
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    # Unescape HTML entities
    cleaned = html.unescape(cleaned)
    # Normalize unicode (replace smart quotes, dashes, etc.)
    cleaned = unicodedata.normalize('NFKD', cleaned)
    # Replace common unicode quotes and dashes with clean equivalents
    cleaned = (cleaned
               .replace('"', '"').replace('"', '"')
               .replace(''', "'").replace(''', "'")
               .replace('—', ' - ').replace('–', ' - ')
               .replace('…', '...'))
    # Clean non-printable / broken characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
    # Collapse multiple whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def extract_tags(quote: str, source: str) -> List[str]:
    """
    Infers specific, thematic Warhammer 40k classifications.
    Uses precise priority weighting to ensure meaningful, distinct labels.
    """
    text = (quote + " " + source).lower()
    tags = []
    
    # Check specific lore factions / organizations first
    if any(k in text for k in ["space marine", "astartes", "chapter", "primarch", "black templar", "blood angel", "dark angel", "ultramarine", "dorn", "guilliman", "sanguinius"]):
        tags.append("Adeptus Astartes Litany")
    
    if any(k in text for k in ["mechanicus", "machine", "cogitator", "tech-priest", "omnissiah", "mars", "iron hands"]):
        tags.append("Adeptus Mechanicus Canticle")

    if any(k in text for k in ["heresy", "heretic", "traitor", "treason", "alien", "xenos", "mutation", "mutant", "purge", "purity", "witch", "sorcery", "taint", "corruption", "inquisit", "inquisition", "daemon", "chaos"]):
        tags.append("Inquisitorial Admonition")

    if any(k in text for k in ["soldier", "officer", "regiment", "guard", "infantry", "trench", "army", "command", "militarum", "commissar", "tactica"]):
        tags.append("Astra Militarum Doctrine")

    if any(k in text for k in ["emperor", "god-emperor", "faith", "prayer", "worship", "zeal", "pious", "ecclesiarchy", "saint", "righteous", "blessing", "holy", "reverence", "sacred"]):
        tags.append("Imperial Cult & Faith")

    if any(k in text for k in ["mind", "thought", "knowledge", "ignoran", "wisdom", "reason", "logic", "study", "curiosity", "intellect", "truth", "silence", "doubt", "ponder", "philosophy"]):
        tags.append("Mind & Philosophy")

    if any(k in text for k in ["duty", "honor", "honour", "loyalty", "sacrifice", "service", "obedien", "valour", "courage", "bravery", "coward"]):
        tags.append("Martial Honor & Duty")

    if any(k in text for k in ["weakness", "leniency", "compromise", "mercy", "pity", "punish", "law", "guilt", "innocen", "fear", "hatred", "hate", "wrath", "fury", "vengeance"]):
        tags.append("Imperial Law & Retribution")

    if not tags:
        # Source-based heuristics
        if "codex" in text or "rulebook" in text:
            tags.append("Imperial Doctrine")
        else:
            tags.append("Imperial Proclamation")

    # Limit to top 2 most specific tags
    return tags[:2]


def scrape_quotes(url: str = LEXICANUM_URL) -> List[Dict[str, Any]]:
    """Scrapes all quotes and sources from the Lexicanum Thought for the Day page."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")
        
    # Extract table rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', raw_html, re.DOTALL)
    quotes = []
    seen_quotes = set()
    
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(tds) >= 2:
            quote_raw = tds[0]
            source_raw = tds[1]
            
            quote = clean_text(quote_raw)
            source = clean_text(source_raw)
            
            # Skip table headers or empty entries
            if not quote or quote.lower() == "thought for the day":
                continue
            if "source" in quote.lower() and len(quote) < 15:
                continue
            if len(quote) < 5:
                continue
                
            # Strip surrounding quote marks if present
            if (quote.startswith('"') and quote.endswith('"')) or (quote.startswith("'") and quote.endswith("'")):
                quote = quote[1:-1].strip()
                
            # Normalize source fallback
            if not source or source == "-":
                source = "Imperial Wisdom (Source Unrecorded)"
                
            # Deduplicate exact quotes
            quote_key = quote.lower().strip()
            if quote_key in seen_quotes:
                continue
            seen_quotes.add(quote_key)
            
            item_id = len(quotes) + 1
            tags = extract_tags(quote, source)
            
            quotes.append({
                "id": item_id,
                "quote": quote,
                "source": source,
                "tags": tags
            })
            
    return quotes


def save_quotes_to_file(quotes: List[Dict[str, Any]], filepath: Path) -> None:
    """Saves quotes to a formatted JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.1",
            "source_url": LEXICANUM_URL,
            "total_quotes": len(quotes),
            "quotes": quotes
        }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    output_path = Path(__file__).resolve().parent.parent / "data" / "quotes.json"
    print(f"Scraping quotes from {LEXICANUM_URL}...")
    harvested = scrape_quotes()
    print(f"Successfully harvested {len(harvested)} unique canonical quotes!")
    save_quotes_to_file(harvested, output_path)
    print(f"Saved dataset to {output_path}")
