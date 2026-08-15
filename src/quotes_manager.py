"""
Warhammer 40K Quotes Manager
Handles dataset loading, deterministic daily rotation, search, and filtering.
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


class QuotesManager:
    """Manages the Warhammer 40K Thought for the Day dataset."""

    DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "quotes.json"

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.quotes: List[Dict[str, Any]] = []
        self.version: str = "1.0"
        self.load_quotes()

    def load_quotes(self) -> None:
        """Loads quotes from the JSON data file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Quotes data file not found at: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.quotes = data.get("quotes", [])
            self.version = data.get("version", "1.0")

        if not self.quotes:
            raise ValueError("Quotes dataset is empty.")

    def total_count(self) -> int:
        """Returns the total number of quotes."""
        return len(self.quotes)

    def get_by_id(self, quote_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a quote by its 1-indexed ID."""
        if 1 <= quote_id <= len(self.quotes):
            return self.quotes[quote_id - 1]
        return None

    def get_random_quote(self, tag: Optional[str] = None) -> Dict[str, Any]:
        """Returns a random quote, optionally filtered by tag."""
        if tag:
            filtered = self.get_quotes_by_tag(tag)
            if filtered:
                return random.choice(filtered)
        return random.choice(self.quotes)

    def get_daily_quote(self, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Deterministically selects a Thought for the Day for a given date.
        Guarantees that all servers receive the exact same quote on a given date,
        and cycles sequentially through all quotes without repeats until full cycle.
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)

        # Use days since epoch (1970-01-01) for consistent, non-repeating daily progression
        days_since_epoch = (target_date.date() - datetime(1970, 1, 1).date()).days
        quote_index = days_since_epoch % len(self.quotes)
        return self.quotes[quote_index]

    def get_quotes_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Returns all quotes containing the given tag (case-insensitive)."""
        tag_lower = tag.lower().strip()
        return [
            q for q in self.quotes
            if any(t.lower() == tag_lower for t in q.get("tags", []))
        ]

    def search_quotes(self, query: str) -> List[Dict[str, Any]]:
        """Searches quotes by keyword in quote text or source."""
        q_lower = query.lower().strip()
        return [
            q for q in self.quotes
            if q_lower in q.get("quote", "").lower() or q_lower in q.get("source", "").lower()
        ]

    def get_all_tags(self) -> List[str]:
        """Returns a sorted list of unique tags in the dataset."""
        unique_tags = set()
        for q in self.quotes:
            for tag in q.get("tags", []):
                unique_tags.add(tag)
        return sorted(list(unique_tags))
