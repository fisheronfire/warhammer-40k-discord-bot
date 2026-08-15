"""
Warhammer 40K Thought of the Day - Discord Dispatcher
Supports single and multi-server Discord Webhook broadcasting,
Discord Bot REST API, and Dry-run terminal preview.
Designed for GitHub Actions scheduled execution.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

# Ensure UTF-8 output encoding for cross-platform terminals (Windows/Linux/macOS)
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from quotes_manager import QuotesManager
from embed_builder import build_webhook_payload, build_quote_embed


def parse_webhook_urls(raw_input: Optional[str]) -> List[str]:
    """Parses single, comma-separated, newline-separated, or JSON list of webhook URLs."""
    if not raw_input:
        return []
    
    clean = raw_input.strip()
    if clean.startswith("[") and clean.endswith("]"):
        try:
            parsed = json.loads(clean)
            if isinstance(parsed, list):
                return [u.strip() for u in parsed if isinstance(u, str) and u.strip()]
        except Exception:
            pass

    # Split by comma or newline
    urls = []
    for line in clean.replace(",", "\n").splitlines():
        u = line.strip()
        if u and u.startswith("http"):
            urls.append(u)
    return urls


def send_discord_webhook(webhook_url: str, payload: Dict[str, Any], max_retries: int = 3) -> bool:
    """Sends payload to Discord Webhook with retry backoff."""
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Warhammer40k-CommissarBoneski/1.0"
    }

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(webhook_url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in (200, 204):
                    print(f"[+] Thought for the Day successfully dispatched by Commissar Boneski! (HTTP {response.status})")
                    return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[!] HTTP Error {e.code} on attempt {attempt}/{max_retries}: {err_body}")
            if e.code == 429:
                # Rate limited
                try:
                    retry_info = json.loads(err_body)
                    retry_after = retry_info.get("retry_after", 5)
                except Exception:
                    retry_after = 5
                print(f"[~] Rate limited by Discord. Waiting {retry_after}s...")
                time.sleep(retry_after)
            elif 500 <= e.code < 600:
                time.sleep(attempt * 2)
            else:
                return False
        except Exception as e:
            print(f"[!] Network error on attempt {attempt}/{max_retries}: {e}")
            time.sleep(attempt * 2)

    print("[-] Failed to dispatch webhook after maximum retry attempts.")
    return False


def broadcast_discord_webhooks(webhook_urls: List[str], payload: Dict[str, Any]) -> int:
    """Broadcasts embed payload across multiple Discord server webhooks."""
    success_count = 0
    print(f"[*] Broadcasting Thought for the Day to {len(webhook_urls)} Discord server(s)...")
    for i, url in enumerate(webhook_urls, 1):
        # Mask webhook token for clean logs
        masked = url[:35] + "..." + url[-6:] if len(url) > 45 else url
        print(f" -> [{i}/{len(webhook_urls)}] Transmitting to server: {masked}")
        if send_discord_webhook(url, payload):
            success_count += 1
        time.sleep(0.5)  # Friendly spacing between servers
    print(f"[+] Broadcast complete: {success_count}/{len(webhook_urls)} servers successfully received the transmission.")
    return success_count


def send_discord_bot_rest(bot_token: str, channel_id: str, payload: Dict[str, Any], max_retries: int = 3) -> bool:
    """Sends embed to Discord channel via Discord Bot REST API."""
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    body = {"embeds": payload.get("embeds", [])}
    if payload.get("content"):
        body["content"] = payload["content"]

    data = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "Warhammer40k-CommissarBoneski/1.0"
    }

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in (200, 201):
                    print(f"[+] Thought for the Day successfully posted by Commissar Boneski via REST API! (HTTP {response.status})")
                    return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[!] Bot REST HTTP Error {e.code} on attempt {attempt}/{max_retries}: {err_body}")
            if e.code == 429:
                time.sleep(5)
            elif 500 <= e.code < 600:
                time.sleep(attempt * 2)
            else:
                return False
        except Exception as e:
            print(f"[!] Bot REST error on attempt {attempt}/{max_retries}: {e}")
            time.sleep(attempt * 2)

    return False


def print_terminal_preview(quote_data: Dict[str, Any], color: str) -> None:
    """Prints a styled representation of the Commissar Boneski transmission."""
    q_id = quote_data.get("id", "---")
    quote = quote_data.get("quote", "")
    source = quote_data.get("source", "Imperial Wisdom")
    tags = ", ".join(quote_data.get("tags", []))

    print("\n" + "=" * 70)
    print(" === COMMISSAR BONESKI // IMPERIAL TRANSMISSION === ")
    print("=" * 70)
    print(f" Thought ID    : #{q_id}")
    print(f" Classification: {tags}")
    print(f" Embed Color   : {color.upper()}")
    print("-" * 70)
    print(f"\n   \"{quote}\"\n")
    print(f"   — Source: {source}")
    print("-" * 70)
    print(" \"THOUGHT BEGETS HERESY; HERESY BEGETS RETRIBUTION\"")
    print("=" * 70 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Warhammer 40K Thought for the Day Discord Poster")
    parser.add_argument("--webhook", type=str, default=os.getenv("DISCORD_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK_URLS"),
                        help="Discord Webhook URL or comma-separated URLs (or set DISCORD_WEBHOOK_URL env var)")
    parser.add_argument("--token", type=str, default=os.getenv("DISCORD_BOT_TOKEN"),
                        help="Discord Bot Token (or set DISCORD_BOT_TOKEN env var)")
    parser.add_argument("--channel", type=str, default=os.getenv("DISCORD_CHANNEL_ID"),
                        help="Discord Channel ID (or set DISCORD_CHANNEL_ID env var)")
    parser.add_argument("--mode", type=str, default=os.getenv("SELECTION_MODE", "daily"),
                        choices=["daily", "random", "id"], help="Quote selection mode")
    parser.add_argument("--id", type=int, default=int(os.getenv("QUOTE_ID")) if os.getenv("QUOTE_ID") else None,
                        help="Select specific quote by ID (1-402)")
    parser.add_argument("--tag", type=str, default=os.getenv("TAG"),
                        help="Filter random quote by tag")
    parser.add_argument("--color", type=str, default=os.getenv("EMBED_COLOR", "gold"),
                        help="Embed color theme (gold, crimson, ultramarine, mechanicus, charcoal, or hex)")
    parser.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "").lower() in ("true", "1"),
                        help="Preview quote without sending to Discord")
    parser.add_argument("--list-tags", action="store_true", help="List all available quote tags and exit")

    args = parser.parse_args()

    # Load dataset
    mgr = QuotesManager()

    if args.list_tags:
        print("Available Warhammer 40K Quote Tags:")
        for tag in mgr.get_all_tags():
            count = len(mgr.get_quotes_by_tag(tag))
            print(f"  • {tag} ({count} quotes)")
        return 0

    # Determine Quote
    if args.id:
        quote_data = mgr.get_by_id(args.id)
        if not quote_data:
            print(f"[-] Error: Quote ID #{args.id} not found (Valid range: 1 to {mgr.total_count()})")
            return 1
    elif args.mode == "random":
        quote_data = mgr.get_random_quote(tag=args.tag)
    else:  # Daily deterministic
        quote_data = mgr.get_daily_quote()

    # Build Payload
    payload = build_webhook_payload(quote_data, color=args.color)
    webhook_urls = parse_webhook_urls(args.webhook)

    # If dry-run or no credentials provided
    if args.dry_run or (not webhook_urls and not (args.token and args.channel)):
        print("[*] [DRY RUN MODE] No webhook dispatched.")
        print_terminal_preview(quote_data, args.color)
        print("Embed JSON Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        if not args.dry_run:
            print("\n[i] To send to Discord, provide --webhook <URL> or set DISCORD_WEBHOOK_URL secret.")
        return 0

    # Dispatch to Discord
    print_terminal_preview(quote_data, args.color)

    if webhook_urls:
        success_count = broadcast_discord_webhooks(webhook_urls, payload)
        return 0 if success_count > 0 else 1
    elif args.token and args.channel:
        success = send_discord_bot_rest(args.token, args.channel, payload)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
