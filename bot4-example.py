import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
OWNER_ID =   # Your Discord user ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, Active Developer!")

# 📖 Help command — will eventually list all commands in detail
@bot.tree.command(name="help", description="Lists available commands.")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("📖 Command list will be available soon.")

# 🏓 Ping command — checks bot latency (placeholder only)
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! (Stub version)")

# 🤖 Version command — shows the current version
@bot.tree.command(name="version", description="Display the bot's version.")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Slater Bot v4.0.0-pre2 — command framework build.")

# 🛑 Shutdown — only works for the owner (stub, not functional)
@bot.tree.command(name="shutdown", description="Shuts down the bot (owner only).")
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("🛑 Shutdown command triggered. (Stub — no shutdown)")

# 🧠 Eval — allows owner to run Python code (locked, stubbed)
@bot.tree.command(name="eval", description="Evaluate Python code (owner only).")
async def eval_code(interaction: discord.Interaction, code: str):
    await interaction.response.send_message("🧠 Eval command stub. No code execution happening yet.")

# 🧹 Clear — removes messages (not active yet)
@bot.tree.command(name="clear", description="Clear messages from the channel.")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"🧹 Would clear {amount} messages... eventually.")

# ℹ️ Userinfo — provides member details (basic placeholder)
@bot.tree.command(name="userinfo", description="Get information about a user.")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"ℹ️ User info for {user.display_name} coming soon.")

# 🏠 Serverinfo — general server stats (stub)
@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.send_message("🏠 Server info is a work in progress.")

# 🪙 Coinflip — basic RNG response
@bot.tree.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message("🪙 The coin flip command is still being minted.")

# 🎱 8ball — answers yes/no questions (placeholder)
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question.")
async def eightball(interaction: discord.Interaction, question: str):
    await interaction.response.send_message(f"🎱 You asked: {question}\nAnswer: Thinking... (stub)")

# 📣 Spam — eventually spams 100x, currently just acknowledges
@bot.tree.command(name="spam", description="Spam a message 100 times.")
async def spam(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"📣 Spam command stub — won't flood you yet.")

bot.run("BOT TOKEN HERE")
