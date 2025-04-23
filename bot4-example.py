import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
import time
import random
import asyncio
OWNER_ID =   # Your Discord user ID

intents = discord.Intents.default()
intents.members = True  # For user info, roles, etc.
intents.message_content = True  # To read message content
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()  # Track when the bot starts

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, Active Developer!")

# 📖 Help command
@bot.tree.command(name="help", description="Lists available commands.")
async def help_command(interaction: discord.Interaction):
    help_text = """
    **Available Commands (v4.0.0-pre3)**

    🔧 Core:
    - /ping – Check bot latency and uptime
    - /version – Display bot version
    - /help – Show this list

    👑 Admin:
    - /shutdown – Shut down the bot (owner only)
    - /clear <amount> – Clear recent messages

    🧰 Utility:
    - /userinfo <user> – Get user info
    - /serverinfo – Server details

    🎲 Fun:
    - /coinflip – Flip a coin
    - /8ball <question> – Ask the magic 8-ball
    - /spam <message> – Spam message 100 times
    """
    await interaction.response.send_message(help_text, ephemeral=True)


# 🏓 Ping command — checks bot latency 
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # Convert to ms
    uptime = round(time.time() - start_time)  # Track bot uptime
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms\n⏳ Uptime: {uptime} seconds")

# 🤖 Version command — shows the current version
@bot.tree.command(name="version", description="Display the bot's version.")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Slater Bot v4.0.0-pre3 — command framework build.")

# 🛑 Shutdown — only works for the owner 
@bot.tree.command(name="shutdown", description="Shuts down the bot (owner only).")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You are not authorized to shut down the bot.", ephemeral=True)
        return
    await interaction.response.send_message("🛑 Shutting down...")
    await bot.close()
    

# 🧹 Clear — removes messages 
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

# ℹ️ Userinfo — provides member details 
@bot.tree.command(name="userinfo", description="Get information about a user.")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"User Info — {user.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles if role.name != "@everyone"]), inline=False)
    await interaction.response.send_message(embed=embed)
    
# 🏠 Serverinfo — general server stats 
@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(title=f"Server Info: {interaction.guild.name}", color=discord.Color.green())
    embed.add_field(name="ID", value=interaction.guild.id, inline=True)
    embed.add_field(name="Owner", value=interaction.guild.owner, inline=True)
    embed.add_field(name="Member Count", value=interaction.guild.member_count, inline=True)
    embed.add_field(name="Creation Date", value=interaction.guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    await interaction.response.send_message(embed=embed)

# 🪙 Coinflip — basic RNG response
@bot.tree.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on: **{result}**")
    
# 🎱 8ball — answers yes/no questions 
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question.")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "Yes.", "No.", "Maybe.", "Absolutely!", "Definitely not.",
        "Ask again later.", "It is certain.", "I doubt it.", "Cannot predict now."
    ]
    result = random.choice(responses)
    await interaction.response.send_message(f"🎱 You asked: _{question}_\nAnswer: **{result}**")
    
# 📣 Spam — spams 100x then deletes all for cleanness
@bot.tree.command(name="spam", description="Spam a message 100 times and summarize it later.")
async def spam(interaction: discord.Interaction, message: str):
    sent_messages = []
    await interaction.response.send_message("📣 Spamming your message 100 times...")

    # Send 100 spam messages, keep track of those
    for _ in range(100):
        msg = await interaction.channel.send(message)
        sent_messages.append(msg)

    # Wait for 5 minutes (300 seconds)
    await asyncio.sleep(300)

    # Delete only the messages sent by the bot itself
    for msg in sent_messages:
        try:
            if msg.author == bot.user:  # Only delete the bot's messages
                await msg.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")

    # Announce the spam result after deletion
    await interaction.channel.send(f"📢 The message '**{message}**' was spammed 100 times.\n@everyone")

bot.run("BOT TOKEN HERE")
