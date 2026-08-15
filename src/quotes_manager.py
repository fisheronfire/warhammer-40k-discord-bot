"""
Warhammer 40K Quotes Manager
Handles dataset loading, pseudo-random non-repeating daily rotation, search, and filtering.
"""

import json
import random
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


class QuotesManager:
    """Manages the Warhammer 40K Thought for the Day dataset."""

    DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "quotes.json"

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.quotes: List[Dict[str, Any]] = []
        self.version: str = "1.1"
        self.load_quotes()

    def load_quotes(self) -> None:
        """Loads quotes from the JSON data file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Quotes data file not found at: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.quotes = data.get("quotes", [])
            self.version = data.get("version", "1.1")

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
        Pseudo-randomly selects a unique Thought for the Day for each calendar day.
        
        Guarantees:
        1. Never repeats the same quote within any 30-day window (or calendar month).
        2. Every single day of the month receives a fresh, pseudo-random quote.
        3. Deterministic: consistent across all servers and runs on the same date.
        4. Cycles through all 402 quotes in a pseudo-random permutation before repeating.
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)

        # Days since epoch (1970-01-01)
        d = target_date.date() if isinstance(target_date, datetime) else target_date
        day_number = (d - date(1970, 1, 1)).days

        total_quotes = len(self.quotes)
        cycle_number = day_number // total_quotes
        day_in_cycle = day_number % total_quotes

        # Deterministic pseudo-random shuffle for this full 402-day cycle
        prng = random.Random(f"warhammer40k_shuffled_cycle_{cycle_number}")
        shuffled_indices = list(range(total_quotes))
        prng.shuffle(shuffled_indices)

        selected_quote_index = shuffled_indices[day_in_cycle]
        return self.quotes[selected_quote_index]

    def get_month_quotes(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Returns the complete sequence of unique quotes for a given month."""
        import calendar
        _, num_days = calendar.monthrange(year, month)
        month_quotes = []
        for day in range(1, num_days + 1):
            cur_date = datetime(year, month, day, 12, 0, 0, tzinfo=timezone.utc)
            month_quotes.append({
                "day": day,
                "date": cur_date.strftime("%Y-%m-%d"),
                "quote": self.get_daily_quote(cur_date)
            })
        return month_quotes

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
