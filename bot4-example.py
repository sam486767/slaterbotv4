import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import time
import random
import aiohttp
import asyncio
import sqlite3

OWNER_ID =   # Your Discord user ID

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()

# --- Database helpers ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            signup_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")
    init_db()  # Initialize DB on start
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name="signup", description="Register yourself and get the Verified role.")
async def signup(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    username = str(interaction.user)

    if user_exists(user_id):
        await interaction.response.send_message("✅ You are already signed up!", ephemeral=True)
        return

    add_user(user_id, username)

    verified_role = discord.utils.get(interaction.guild.roles, name="Verified")
    if not verified_role:
        verified_role = await interaction.guild.create_role(name="Verified", colour=discord.Colour.green())
    try:
        await interaction.user.add_roles(verified_role)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to add roles.", ephemeral=True)
        return

    await interaction.response.send_message("🎉 You have been signed up and granted the Verified role!", ephemeral=True)

# Example hello command:
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, Active Developer!")
# 📖 Help Command
@bot.tree.command(name="help", description="Show a list of all commands.")
async def help_command(interaction: discord.Interaction):
    help_text = "**Slater Bot v4.1.0-pre-release-2**\n\n"

    help_text += "🔧 **Core**\n"
    help_text += "- 🏓 `/ping` – Check latency and uptime\n"
    help_text += "- 🔢 `/version` – Show the current version\n"
    help_text += "- 📖 `/help` – Show this list\n\n"

    help_text += "👑 **Admin**\n"
    help_text += "- 📴 `/shutdown` – Shut down the bot (owner only)\n"
    help_text += "- 🧹 `/clear <amount>` – Purge messages\n"
    help_text += "- 📩 `/pm <user> <message>` – Send a private message to a user\n\n"

    help_text += "🧰 **Utility**\n"
    help_text += "- 🧑 `/userinfo <user>` – Get user info\n"
    help_text += "- 🏠 `/serverinfo` – Show server details\n"
    help_text += "- 🧬 `/github` – Link to the bot’s GitHub repo\n\n"

    help_text += "🎲 **Fun**\n"
    help_text += "- 💰 `/coinflip` – Flip a coin\n"
    help_text += "- 🎱 `/8ball <question>` – Ask the magic 8-ball\n"
    help_text += "- 🗯️ `/spam <message>` – Spam a message and auto-delete\n"
    help_text += "- 🔫 `/kill <user>` – Eliminate someone for 60 seconds\n\n"

    help_text += "📌 *Want to know what’s coming next?* [The Road Ahead](https://github.com/sam486767/slaterbotv4/wiki/The-Road-Ahead)"
    await interaction.response.send_message(help_text, ephemeral=True)

# 🏓 Ping
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    uptime = round(time.time() - start_time)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms\n⏳ Uptime: {uptime} seconds")

# 🤖 Version
@bot.tree.command(name="version", description="Display the bot's version.")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Slater Bot v4.1.0 — Pre-Release-2.")

# 🛑 Shutdown
@bot.tree.command(name="shutdown", description="Shuts down the bot (owner only).")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You are not authorized to shut down the bot.", ephemeral=True)
        return
    await interaction.response.send_message("🛑 Shutting down...")
    await bot.close()

# 🧹 Clear
@bot.tree.command(name="clear", description="Clear messages from the channel.")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don’t have permission to clear messages.", ephemeral=True)
        return
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Please provide a number between 1 and 100.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {len(deleted)} messages.", ephemeral=True)

# 📩 PM
@bot.tree.command(name="pm", description="Send a private message to a user (admin only).")
async def pm(interaction: discord.Interaction, user: discord.Member, message: str):
    if interaction.user.id != OWNER_ID and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You are not authorized to send private messages.", ephemeral=True)
        return
    try:
        await user.send(f"📬 You have a new message from the bot: {message}")
        await interaction.response.send_message(f"✅ Successfully sent a PM to {user.display_name}.")
    except discord.Forbidden:
        await interaction.response.send_message(f"⚠️ Could not send a PM to {user.display_name} because they have DMs disabled.")

# 🧑 Userinfo
@bot.tree.command(name="userinfo", description="Get information about a user.")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"User Info — {user.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles if role.name != "@everyone"]), inline=False)
    await interaction.response.send_message(embed=embed)

# 🏠 Serverinfo
@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(title=f"Server Info: {interaction.guild.name}", color=discord.Color.green())
    embed.add_field(name="ID", value=interaction.guild.id, inline=True)
    embed.add_field(name="Owner", value=interaction.guild.owner, inline=True)
    embed.add_field(name="Member Count", value=interaction.guild.member_count, inline=True)
    embed.add_field(name="Creation Date", value=interaction.guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    await interaction.response.send_message(embed=embed)

# 🔗 GitHub
@bot.tree.command(name="github", description="Get the link to the bot's GitHub repository.")
async def github(interaction: discord.Interaction):
    await interaction.response.send_message("📂 View the Slater Bot code on GitHub:\nhttps://github.com/sam486767/slaterbotv4")

# 🪙 Coinflip
@bot.tree.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on: **{result}**")

# 🎱 8ball
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question.")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "Yes.", "No.", "Maybe.", "Absolutely!", "Definitely not.",
        "Ask again later.", "It is certain.", "I doubt it.", "Cannot predict now."
    ]
    result = random.choice(responses)
    await interaction.response.send_message(f"🎱 You asked: _{question}_\nAnswer: **{result}**")

# 📣 Spam
@bot.tree.command(name="spam", description="Spam a message 100 times and summarize it later.")
async def spam(interaction: discord.Interaction, message: str):
    sent_messages = []
    await interaction.response.send_message("📣 Spamming your message 100 times...")
    for _ in range(100):
        msg = await interaction.channel.send(message)
        sent_messages.append(msg)
    await asyncio.sleep(300)
    for msg in sent_messages:
        try:
            if msg.author == bot.user:
                await msg.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
    await interaction.channel.send(f"📢 The message '**{message}**' was spammed 100 times.\n@everyone")

# 🔫 Kill
@bot.tree.command(name="kill", description="Temporarily eliminate a user (1 minute timeout).")
@app_commands.describe(user="The user you want to eliminate.")
async def kill(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.user:
        await interaction.response.send_message("❌ You can't eliminate yourself.", ephemeral=True)
        return
    if user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You can't eliminate an admin.", ephemeral=True)
        return
    if user == bot.user:
        await interaction.response.send_message("🤖 You dare challenge me? I am immortal.", ephemeral=True)
        return
    try:
        await user.timeout(until=datetime.utcnow() + timedelta(minutes=1))
        await interaction.response.send_message(f"💀 {user.display_name} has been eliminated for 60 seconds!")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to eliminate that user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ An error occurred: {str(e)}", ephemeral=True)

bot.run("YOUR_BOT_TOKEN")
