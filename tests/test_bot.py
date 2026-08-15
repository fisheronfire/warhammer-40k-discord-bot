"""
Unit Test Suite for Warhammer 40K Discord Bot
"""

import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add src/ to path
src_dir = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_dir))

from quotes_manager import QuotesManager
from embed_builder import (
    build_quote_embed,
    build_webhook_payload,
    calculate_imperial_stardate,
    get_embed_color,
    COLOR_PALETTES
)
from scraper import clean_text, extract_tags


class TestQuotesManager(unittest.TestCase):
    """Test suite for QuotesManager dataset operations."""

    def setUp(self):
        self.mgr = QuotesManager()

    def test_quotes_loaded(self):
        """Verify dataset has loaded > 400 canonical quotes."""
        self.assertGreaterEqual(self.mgr.total_count(), 400)

    def test_get_by_id(self):
        """Verify quote retrieval by 1-indexed ID."""
        q1 = self.mgr.get_by_id(1)
        self.assertIsNotNone(q1)
        self.assertEqual(q1["id"], 1)
        self.assertIn("quote", q1)
        self.assertIn("source", q1)

        # Out of bounds
        self.assertIsNone(self.mgr.get_by_id(0))
        self.assertIsNone(self.mgr.get_by_id(99999))

    def test_deterministic_daily_quote(self):
        """Verify deterministic selection is consistent on same date and rotates daily."""
        date_a = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
        date_b = datetime(2026, 8, 15, 18, 30, 0, tzinfo=timezone.utc)
        date_next_day = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

        quote_a = self.mgr.get_daily_quote(date_a)
        quote_b = self.mgr.get_daily_quote(date_b)
        quote_next = self.mgr.get_daily_quote(date_next_day)

        # Same calendar date -> identical quote
        self.assertEqual(quote_a["id"], quote_b["id"])
        # Next calendar day -> rotated quote
        self.assertNotEqual(quote_a["id"], quote_next["id"])

    def test_random_quote(self):
        """Verify random quote retrieval."""
        quote = self.mgr.get_random_quote()
        self.assertIsNotNone(quote)
        self.assertIn("quote", quote)

    def test_tag_filtering(self):
        """Verify filtering quotes by category tags."""
        heresy_quotes = self.mgr.get_quotes_by_tag("Inquisitorial Admonition")
        self.assertGreater(len(heresy_quotes), 0)
        for q in heresy_quotes:
            self.assertTrue(any("inquisitorial" in t.lower() or "admonition" in t.lower() for t in q["tags"]))

    def test_search_quotes(self):
        """Verify keyword search in quotes and sources."""
        results = self.mgr.search_quotes("Emperor")
        self.assertGreater(len(results), 0)
        for r in results:
            match = "emperor" in r["quote"].lower() or "emperor" in r["source"].lower()
            self.assertTrue(match)


class TestEmbedBuilder(unittest.TestCase):
    """Test suite for Discord embed creation and formatting."""

    def test_stardate_format(self):
        """Verify Imperial Stardate matches canonical format (e.g. 0.621.026.M42)."""
        dt = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
        stardate = calculate_imperial_stardate(dt)
        parts = stardate.split(".")
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "0")       # Terra Standard Check digit
        self.assertEqual(len(parts[1]), 3)    # Year fraction
        self.assertEqual(parts[2], "026")     # Year within millennium
        self.assertEqual(parts[3], "M42")     # 42nd Millennium

    def test_embed_colors(self):
        """Verify embed color resolution for names and hex codes."""
        self.assertEqual(get_embed_color("gold"), COLOR_PALETTES["gold"])
        self.assertEqual(get_embed_color("crimson"), COLOR_PALETTES["crimson"])
        self.assertEqual(get_embed_color("#D4AF37"), 0xD4AF37)
        self.assertEqual(get_embed_color("0xD4AF37"), 0xD4AF37)
        # Invalid fallback
        self.assertEqual(get_embed_color("invalid_color"), COLOR_PALETTES["gold"])

    def test_embed_structure_and_limits(self):
        """Verify Discord embed complies with Discord API limits."""
        quote_sample = {
            "id": 42,
            "quote": "Be grateful of your Master's favour!",
            "source": "Warhammer 40,000 4th Edition Rulebook, pg. 238",
            "tags": ["Imperial Cult & Faith"]
        }
        embed = build_quote_embed(quote_sample, color="crimson")

        # Title limits (< 256 chars)
        self.assertIn("title", embed)
        self.assertLessEqual(len(embed["title"]), 256)
        self.assertIn("#042", embed["title"])

        # Description limits (< 4096 chars)
        self.assertIn("description", embed)
        self.assertLessEqual(len(embed["description"]), 4096)
        self.assertIn("Be grateful", embed["description"])

        # Fields (< 25 fields, value < 1024 chars)
        self.assertIn("fields", embed)
        self.assertLessEqual(len(embed["fields"]), 25)
        for field in embed["fields"]:
            self.assertLessEqual(len(field["name"]), 256)
            self.assertLessEqual(len(field["value"]), 1024)

        # Color
        self.assertEqual(embed["color"], COLOR_PALETTES["crimson"])

    def test_webhook_payload(self):
        """Verify webhook payload structure."""
        quote_sample = {
            "id": 1,
            "quote": "A broad mind lacks focus.",
            "source": "Warhammer 40,000 4th Edition Rulebook, pg. 120",
            "tags": ["Mind & Philosophy"]
        }
        payload = build_webhook_payload(quote_sample, bot_name="Commissar Boneski")
        self.assertEqual(payload["username"], "Commissar Boneski")
        self.assertIn("avatar_url", payload)
        self.assertEqual(len(payload["embeds"]), 1)


class TestScraperCleaner(unittest.TestCase):
    """Test suite for text cleaning and tag extraction."""

    def test_clean_text_removes_citations(self):
        raw = 'A good soldier obeys.<sup><a href="#cite_note-1">[1]</a></sup>'
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "A good soldier obeys.")

    def test_clean_text_handles_html_entities(self):
        raw = "A coward&apos;s reward &amp; compromise"
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "A coward's reward & compromise")

    def test_extract_tags(self):
        tags = extract_tags("Heresy must be purged in holy fire", "Inquisitor Eisenhorn")
        self.assertIn("Inquisitorial Admonition", tags)


if __name__ == "__main__":
    unittest.main()
