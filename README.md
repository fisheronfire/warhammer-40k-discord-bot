# ⚔️ Commissar Bonski - Warhammer 40K "Thought for the Day" Discord Bot ⚔️

[![Warhammer 40K Thought of the Day](https://img.shields.io/badge/Warhammer%2040K-Commissar%20Bonski-gold.svg)](https://wh40k.lexicanum.com/wiki/Thought_for_the_day)
[![Hosted on GitHub Actions](https://img.shields.io/badge/Hosted%20On-GitHub%20Actions%20(100%25%20Free)-2088FF.svg?logo=github-actions)](.github/workflows/daily_quote.yml)
[![Quotes Harvested](https://img.shields.io/badge/Canon%20Quotes-402%2B%20from%20Lexicanum-red.svg)](data/quotes.json)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An automated, serverless Discord bot hosted **100% free on GitHub** via **GitHub Actions**. Every 24 hours, **Commissar Bonski** transmits a canonical Warhammer 40,000 *"Thought for the Day"* (with official lore citations and calculated Imperial Stardates) directly to your Discord server.

Harvested directly from the official [Lexicanum Warhammer 40K Wiki: Thought for the Day](https://wh40k.lexicanum.com/wiki/Thought_for_the_day).

---

## 🏛️ Features

- **📜 402+ Canonical Quotes**: Complete archive of Imperial wisdom, admonitions, and litanies across Warhammer 40K Rulebooks, Codexes, White Dwarf issues, and Black Library novels.
- **⚡ 100% Free & Zero Server Maintenance**: Runs on GitHub Actions scheduled cron jobs. No VPS, no cloud hosting bills, no 24/7 server needed.
- **🎨 Grimdark Imperial Aesthetic**:
  - Imperial Double-Headed Aquila crest.
  - Calculated canonical **Imperial Stardate** (e.g. `0.621.026.M42`).
  - Canonical lore source citations (*Codex: Space Marines*, *Tactica Imperialis*, *Dawn of War*, etc.).
  - Solemn Inquisitorial admonition footers (*"Thought begets Heresy; Heresy begets Retribution"*).
  - Customizable color themes (Auric Gold, Inquisitorial Crimson, Ultramarine Blue, Mechanicus Rust, Charcoal).
- **🔄 Deterministic Daily Rotation**: Guarantees a unique, non-repeating quote every day across 400+ days.
- **🤖 Dual Support**:
  - **Discord Webhook** (Recommended - 30 second setup, zero bot permissions required).
  - **Discord Bot REST API** (For bot accounts posting into specific channel IDs).
  - **Interactive Gateway Bot** (Optional slash commands like `/thought`, `/random_thought`, `/search_thoughts`, `/stardate`).
- **🔄 Automated Wiki Sync**: Built-in GitHub Action that checks Lexicanum monthly and commits newly added wiki quotes automatically.

---

## 🖼️ Discord Transmission Preview

```
======================================================================
 === COMMISSAR BONSKI // IMPERIAL TRANSMISSION === 
======================================================================
 Stardate      : 0.621.026.M42
 Thought ID    : #179
 Classification: War & Battle
 Embed Color   : GOLD
----------------------------------------------------------------------

   "Leniency is a sign of weakness!"

   — Source: Warhammer 40,000 4th Edition Rulebook, pg. 251
----------------------------------------------------------------------
 "THOUGHT BEGETS HERESY; HERESY BEGETS RETRIBUTION"
======================================================================
```

---

## 🚀 3-Minute Quickstart Guide

### Step 1: Create a Discord Webhook (30 seconds)
1. In your Discord server, go to the text channel where you want quotes posted (e.g. `#thought-for-the-day` or `#general`).
2. Click **⚙️ Edit Channel** (channel settings) ➡️ **Integrations** ➡️ **Webhooks** ➡️ **New Webhook**.
3. Name it **Commissar Bonski** and click **Copy Webhook URL**.

---

### Step 2: Fork or Push this Repository to GitHub
1. Push this repository to your GitHub account (or Fork it).
2. Go to your repository on GitHub.

---

### Step 3: Add your Discord Webhook URL to GitHub Secrets
1. In your GitHub repository, click **Settings** (top navigation bar).
2. On the left sidebar, expand **Secrets and variables** ➡️ click **Actions**.
3. Click **New repository secret**.
4. Set:
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: *Paste your Discord Webhook URL here*
5. Click **Add secret**.

---

### Step 4: Test & Trigger Manually!
1. Go to the **Actions** tab on your GitHub repository.
2. In the left menu, select **Warhammer 40K Thought for the Day**.
3. Click the **Run workflow** dropdown button on the right ➡️ click **Run workflow**.
4. Check your Discord channel — your Imperial Thought for the Day will arrive in seconds!

---

## ⚙️ Configuration & Customization

### Changing the Daily Post Time
By default, quotes are posted daily at **12:00 UTC** (8:00 AM EST / 5:00 AM PST).

To change the time, edit `.github/workflows/daily_quote.yml`:
```yaml
schedule:
  - cron: '0 14 * * *'  # Runs daily at 14:00 UTC (10:00 AM EST)
```
*(Cron format: `minute hour day month day-of-week` in UTC)*

---

### Environment Variables & Customization Options

| Variable | Description | Options / Default |
| :--- | :--- | :--- |
| `DISCORD_WEBHOOK_URL` | **(Required)** Discord Webhook URL for posting | `https://discord.com/api/webhooks/...` |
| `SELECTION_MODE` | Quote selection strategy | `daily` *(default)*, `random`, `id` |
| `EMBED_COLOR` | Theme color of the Discord Embed | `gold` *(default)*, `crimson`, `ultramarine`, `mechanicus`, `charcoal`, or hex like `#D4AF37` |
| `QUOTE_ID` | Post a specific quote ID (1 - 402) | Integer (e.g. `42`) |
| `TAG` | Filter random quotes by theme tag | `Emperor`, `Heresy`, `Duty & Honor`, `War & Battle`, `Wisdom & Mind`, `Space Marines`, `Inquisition`, `Adeptus Mechanicus` |
| `DRY_RUN` | Test locally without sending to Discord | `false` *(default)* / `true` |

You can also set any of these in your **GitHub Repository Variables** or pass them as inputs when manually triggering the workflow in the GitHub Actions tab.

---

## 💻 Local Usage & Development

### 1. Clone & Test Locally
```bash
git clone https://github.com/YOUR_USERNAME/warhammer-40k-discord-bot.git
cd warhammer-40k-discord-bot

# Run dry run preview
python src/post_quote.py --dry-run

# List available quote tags
python src/post_quote.py --list-tags

# Inspect a specific quote ID
python src/post_quote.py --id 42 --dry-run
```

### 2. Test with Live Webhook locally
```bash
# Set webhook in terminal or .env file
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/URL"
python src/post_quote.py --color crimson
```

### 3. Run Unit Tests
```bash
python -m unittest discover tests
```

### 4. Re-harvest / Update Quotes from Lexicanum
```bash
python src/scraper.py
```

---

## 🤖 Optional: Running as an Interactive Gateway Bot

If you prefer to host an interactive 24/7 Discord bot with slash commands on your own server or VPS:

1. Install `discord.py`:
   ```bash
   pip install discord.py
   ```
2. Set your Bot Token:
   ```bash
   export DISCORD_BOT_TOKEN="your_bot_token_here"
   ```
3. Launch the bot:
   ```bash
   python src/bot_gateway.py
   ```

### Available Slash Commands:
- `/thought` — Transmits the canonical daily Imperial Thought.
- `/random_thought [tag] [color]` — Generates a random Imperial thought (optionally filtered by category).
- `/quote_id [id]` — Retrieves quote by reference number (1-402).
- `/search_thoughts [query]` — Searches Lexicanum quotes and canon sources.
- `/stardate` — Calculates the current Imperial Stardate according to Terra Standard.

---

## 🛡️ License

This project is licensed under the MIT License.
Warhammer 40,000, Lexicanum, and all associated lore, quotes, and names are the intellectual property of Games Workshop Ltd.
