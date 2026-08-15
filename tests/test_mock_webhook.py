"""
Mock Discord Webhook Integration Test
Spins up a local HTTP server simulating Discord's Webhook API (HTTP 204 No Content),
executes the dispatcher against the mock webhook, and asserts the received payload.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import unittest
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_dir))

from post_quote import send_discord_webhook
from quotes_manager import QuotesManager
from embed_builder import build_webhook_payload


class MockDiscordHandler(BaseHTTPRequestHandler):
    received_payloads = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8"))
        MockDiscordHandler.received_payloads.append(payload)

        # Discord webhooks respond with 204 No Content on success
        self.send_response(204)
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress server logs during test
        pass


class TestDiscordWebhookIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MockDiscordHandler.received_payloads = []
        cls.server = HTTPServer(("127.0.0.1", 0), MockDiscordHandler)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_mock_webhook_dispatch(self):
        webhook_url = f"http://127.0.0.1:{self.port}/api/webhooks/123456/abcdef"
        mgr = QuotesManager()
        quote_data = mgr.get_by_id(1)  # "A broad mind lacks focus."
        payload = build_webhook_payload(quote_data, color="gold", bot_name="Commissar Boneski")

        # Dispatch via the webhook client
        success = send_discord_webhook(webhook_url, payload)
        self.assertTrue(success)

        # Verify received payload on mock Discord server
        self.assertEqual(len(MockDiscordHandler.received_payloads), 1)
        received = MockDiscordHandler.received_payloads[0]

        self.assertEqual(received["username"], "Commissar Boneski")
        self.assertIn("embeds", received)
        self.assertEqual(len(received["embeds"]), 1)

        embed = received["embeds"][0]
        self.assertIn("A broad mind lacks focus.", embed["description"])
        self.assertIn("Warhammer 40,000 4th Edition Rulebook", embed["fields"][0]["value"])
        self.assertEqual(embed["fields"][0]["name"], "📜 Canonical Source")

    def test_multi_webhook_parsing(self):
        from post_quote import parse_webhook_urls
        raw = "https://discord.com/api/webhooks/1/a, https://discord.com/api/webhooks/2/b\nhttps://discord.com/api/webhooks/3/c"
        urls = parse_webhook_urls(raw)
        self.assertEqual(len(urls), 3)
        self.assertEqual(urls[0], "https://discord.com/api/webhooks/1/a")
        self.assertEqual(urls[1], "https://discord.com/api/webhooks/2/b")
        self.assertEqual(urls[2], "https://discord.com/api/webhooks/3/c")


if __name__ == "__main__":
    unittest.main()
