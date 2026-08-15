"""
Warhammer 40K Discord Bot - Interactive Gateway (Optional)
Provides live slash commands if hosted continuously on a server or locally.
"""

import os
import sys
from typing import Optional

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError:
    # discord.py is an optional dependency for 24/7 gateway bots
    discord = None

from quotes_manager import QuotesManager
from embed_builder import (
    build_quote_embed,
    calculate_imperial_stardate,
    COLOR_PALETTES
)


def create_bot():
    if discord is None:
        raise ImportError("discord.py is required to run the interactive gateway bot. Install it with: pip install discord.py")

    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    mgr = QuotesManager()

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

    @bot.tree.command(name="thought", description="Receive the canonical Warhammer 40K Thought for the Day")
    @app_commands.describe(color="Embed color theme (gold, crimson, ultramarine, mechanicus, charcoal)")
    async def thought_command(interaction: "discord.Interaction", color: Optional[str] = "gold"):
        quote = mgr.get_daily_quote()
        embed_dict = build_quote_embed(quote, color=color)
        embed = discord.Embed.from_dict(embed_dict)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="random_thought", description="Receive a random Imperial Thought for the Day")
    @app_commands.describe(
        tag="Filter by category (e.g. Heresy, Emperor, Space Marines, War & Battle)",
        color="Embed color theme"
    )
    async def random_command(interaction: "discord.Interaction", tag: Optional[str] = None, color: Optional[str] = "gold"):
        quote = mgr.get_random_quote(tag=tag)
        embed_dict = build_quote_embed(quote, color=color)
        embed = discord.Embed.from_dict(embed_dict)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="quote_id", description="Look up a specific Thought for the Day by ID (1-402)")
    @app_commands.describe(quote_id="Quote ID number between 1 and 402")
    async def quote_id_command(interaction: "discord.Interaction", quote_id: int):
        quote = mgr.get_by_id(quote_id)
        if not quote:
            await interaction.response.send_message(
                f"❌ Thought #{quote_id} not found in the Imperial Archives. (Valid: 1-{mgr.total_count()})",
                ephemeral=True
            )
            return
        embed_dict = build_quote_embed(quote)
        embed = discord.Embed.from_dict(embed_dict)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="search_thoughts", description="Search Imperial thoughts by keyword")
    @app_commands.describe(query="Keyword to search in quotes and sources")
    async def search_command(interaction: "discord.Interaction", query: str):
        results = mgr.search_quotes(query)
        if not results:
            await interaction.response.send_message(f"No records found for query: `{query}`", ephemeral=True)
            return

        preview = results[:5]
        text_lines = [f"**Found {len(results)} Imperial records matching `{query}`:**\n"]
        for q in preview:
            text_lines.append(f"• **#{q['id']}**: *\"{q['quote']}\"* — `{q['source']}`")
        if len(results) > 5:
            text_lines.append(f"\n*...and {len(results) - 5} more. Use `/quote_id` to inspect any record.*")

        await interaction.response.send_message("\n".join(text_lines), ephemeral=True)

    @bot.tree.command(name="stardate", description="Calculate the current Imperial Stardate")
    async def stardate_command(interaction: "discord.Interaction"):
        stardate = calculate_imperial_stardate()
        await interaction.response.send_message(
            f"⏳ **Current Imperial Stardate (Terra Standard):** `{stardate}`\n*\"The Emperor Protects.\"*",
            ephemeral=False
        )

    return bot


if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable is not set.")
        print("For daily scheduled posting via GitHub Actions, use src/post_quote.py with DISCORD_WEBHOOK_URL instead.")
        sys.exit(1)

    bot = create_bot()
    bot.run(token)
