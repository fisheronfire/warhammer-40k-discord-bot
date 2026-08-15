# 📨 How to Add Commissar Boneski to Other Discord Servers

There are two easy methods to add **Commissar Boneski** to any other Discord server:

---

## ⚡ Method 1: Webhook Link (Easiest — Takes 30 Seconds)

You do **not** need server admin privileges or bot verification. Simply send the template below to the owner of the other Discord server.

### 📋 Copy & Paste Message to Send to the Server Owner:

> **Hey! Want to add Commissar Boneski (Warhammer 40K Thought for the Day) to our server?**
>
> It posts one canonical Warhammer 40,000 Imperial quote every day with official lore citations and servo-skull artwork.
>
> **How to set it up (30 seconds):**
> 1. Right-click the channel you want quotes in (e.g. `#warhammer-40k` or `#general`) ➡️ **Edit Channel**.
> 2. Go to **Integrations** ➡️ **Webhooks** ➡️ **New Webhook**.
> 3. Name it **Commissar Boneski** and click **Copy Webhook URL**.
> 4. Send me the Webhook URL, and Commissar Boneski will start broadcasting daily!

---

### 🔧 How You Connect Their Webhook to Your GitHub Actions:

1. Copy the webhook URL they send you.
2. Go to your GitHub repository: [https://github.com/fisheronfire/warhammer-40k-discord-bot/settings/secrets/actions](https://github.com/fisheronfire/warhammer-40k-discord-bot/settings/secrets/actions)
3. Edit the `DISCORD_WEBHOOK_URL` secret.
4. Add their webhook URL separated by a comma (or on a new line):
   ```
   https://discord.com/api/webhooks/YOUR_SERVER/...,https://discord.com/api/webhooks/THEIR_SERVER/...
   ```
5. Click **Update secret**.

**Done!** Commissar Boneski will now broadcast the Thought of the Day to both servers simultaneously! You can add unlimited servers this way.

---

## 🤖 Method 2: 1-Click Discord Bot OAuth2 Invite Link

If you create a Discord Bot application in the Discord Developer Portal, you can generate a single URL that any server owner can click to add the bot with 1 click:

### 1. Create your Discord Bot Application (2 minutes):
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** ➡️ Name it **Commissar Boneski**.
3. Upload `assets/commissar_boneski.png` as the App Icon.
4. Copy your **Application ID (Client ID)** from the General Information page.

### 2. Generate your 1-Click Shareable Invite URL:
Replace `YOUR_CLIENT_ID` with your Application ID:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=2048
```

### 3. Share the Link:
Send this link to any server owner. When they click it, Discord will show a dropdown of their servers to add Commissar Boneski instantly!
