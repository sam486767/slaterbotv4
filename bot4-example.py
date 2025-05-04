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

# 📖 /help — List all commands with categories, emojis, and roadmap link
@bot.tree.command(name="help", description="Show a list of all commands.")
async def help_command(interaction: discord.Interaction):
    help_text = "**Slater Bot v4.0.1**\n\n"

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
    help_text += "- 🗯️ `/spam <message>` – Spam a message and auto-delete\n\n"
    help_text += "- 🌌 `/forcealign – Receive either the Jedi Master or Sith Lord role (cosmetic only) and learn a random fact about your side of the Force."
    
    help_text += "📌 *Want to know what’s coming next?* [The Road Ahead](https://github.com/sam486767/slaterbotv4/wiki/The-Road-Ahead)"

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
    await interaction.response.send_message("🤖 Slater Bot v4.0.2 — Star Wars.")

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

# 📩 PM Command — Sends a private message to a user (admin only)
@bot.tree.command(name="pm", description="Send a private message to a user (admin only).")
async def pm(interaction: discord.Interaction, user: discord.Member, message: str):
    # Check if the user is the owner/admin before sending a PM
    if interaction.user.id != OWNER_ID and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You are not authorized to send private messages.", ephemeral=True)
        return

    # Try sending the private message to the user
    try:
        await user.send(f"📬 You have a new message from the bot: {message}")
        await interaction.response.send_message(f"✅ Successfully sent a PM to {user.display_name}.")
    except discord.Forbidden:
        # If the user has DMs disabled, inform the admin
        await interaction.response.send_message(f"⚠️ Could not send a PM to {user.display_name} because they have DMs disabled.")

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

# 🔗 GitHub Command — Sends a link to the official Slater Bot repository
@bot.tree.command(name="github", description="Get the link to the bot's GitHub repository.")
async def github(interaction: discord.Interaction):
    await interaction.response.send_message("📂 View the Slater Bot code on GitHub:\nhttps://github.com/sam486767/slaterbotv4")

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

@bot.tree.command(name="forcebalance", description="Become a Jedi Master or Sith Lord and learn something new.")
async def forcebalance(interaction: discord.Interaction):
    import random  # Ensure you import random at the top

    guild = interaction.guild
    member = interaction.user

    # Role names
    jedi_name = "Jedi Master"
    sith_name = "Sith Lord"

    # Check if roles exist, create if missing
    jedi_role = discord.utils.get(guild.roles, name=jedi_name)
    sith_role = discord.utils.get(guild.roles, name=sith_name)

    if not jedi_role:
        jedi_role = await guild.create_role(name=jedi_name, colour=discord.Colour.blue())
    if not sith_role:
        sith_role = await guild.create_role(name=sith_name, colour=discord.Colour.red())

    # Check if user already has one of the roles
    if jedi_role in member.roles or sith_role in member.roles:
        await interaction.response.send_message(
            "You have already chosen your path. The Force does not allow switching sides.",
            ephemeral=True
        )
        return

    # Randomly assign Jedi or Sith
    side = random.choice(["jedi", "sith"])

    if side == "jedi":
        await member.add_roles(jedi_role)
        fact = random.choice([
            "Jedi use the light side of the Force for peace and knowledge.",
            "Yoda trained Jedi for over 800 years.",
            "The Jedi Code forbids emotional attachment."
        ])
        await interaction.response.send_message(f"You are now a **Jedi Master**. {fact}")
    else:
        await member.add_roles(sith_role)
        fact = random.choice([
            "The Sith use the dark side of the Force to gain power.",
            "Darth Bane established the Rule of Two.",
            "The Sith believe passion is strength."
        ])
        await interaction.response.send_message(f"You are now a **Sith Lord**. {fact}")

bot.run("BOT TOKEN HERE")
