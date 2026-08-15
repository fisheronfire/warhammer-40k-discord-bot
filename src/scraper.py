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
    """Infers thematic Warhammer 40k tags for categorization and filtering."""
    text = (quote + " " + source).lower()
    tags = []
    
    keywords = {
        "Emperor": ["emperor", "imperium", "imperial", "throne"],
        "Heresy": ["heresy", "heretic", "traitor", "treason", "taint", "corruption"],
        "Duty & Honor": ["duty", "honor", "honour", "loyalty", "service", "obedien"],
        "War & Battle": ["war", "battle", "sword", "weapon", "kill", "fight", "victory", "death", "blood"],
        "Faith & Zeal": ["faith", "zeal", "prayer", "reverence", "blessing", "righteous"],
        "Wisdom & Mind": ["mind", "thought", "knowledge", "ignoran", "reason", "logic", "wisdom"],
        "Space Marines": ["astartes", "space marine", "chapter", "primarch", "blood angels", "black templars"],
        "Inquisition": ["inquisition", "inquisitor", "purge", "purity", "sin", "guilt"],
        "Adeptus Mechanicus": ["machine", "cogitator", "tech", "omnissiah", "mechanicus", "mars"],
    }
    
    for tag, terms in keywords.items():
        if any(term in text for term in terms):
            tags.append(tag)
            
    if not tags:
        tags.append("Imperial Wisdom")
        
    return tags


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
            "version": "1.0",
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
