import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta

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


OWNER_ID =   # Your Discord user ID

@bot.tree.command(name="start_election", description="Start a new election with candidates.")
async def start_election(interaction: discord.Interaction,
                         candidate1: discord.Member,
                         candidate2: discord.Member,
                         candidate3: discord.Member = None,
                         candidate4: discord.Member = None,
                         candidate5: discord.Member = None):
    
    # Restrict command to you only
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You don't have permission to start an election.", ephemeral=True)
        return

    # Build list of candidates
    candidates = [candidate1, candidate2]
    if candidate3: candidates.append(candidate3)
    if candidate4: candidates.append(candidate4)
    if candidate5: candidates.append(candidate5)

    # Set up role weights (based on role names)
    role_weights = {
        "Alpha Male in Charge": 10,
        "Veteran": 3,
        "Member": 1,
        "Cosmetic Gang": 0.5
        # Add more as needed
    }

    # Create election data
    election_data = {
        "candidates": {str(c.id): 0 for c in candidates},
        "voters": [],
        "active": True,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
        "role_weights": role_weights
    }

    # Save to JSON
    with open("election.json", "w") as f:
        json.dump(election_data, f, indent=4)

    # Confirmation message
    names = ", ".join([c.display_name for c in candidates])
    await interaction.response.send_message(f"✅ Election started!\n**Candidates:** {names}\n**Voting ends in 12 hours.**")
@bot.tree.command(name="set_role_weight", description="Set or modify the weight of a role in elections.")
async def set_role_weight(interaction: discord.Interaction, role: discord.Role, weight: float):
    # Ensure only the bot owner can run this command
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You don't have permission to modify role weights.", ephemeral=True)
        return

    # Load the current election data from the JSON file
    try:
        with open("election.json", "r") as f:
            election_data = json.load(f)
    except FileNotFoundError:
        await interaction.response.send_message("❌ No election data found. Start an election first.", ephemeral=True)
        return

    # Update the role weight in the role_weights section
    role_name = role.name
    role_weights = election_data.get("role_weights", {})

    # Add the role if it doesn't exist, or update its weight if it does
    role_weights[role_name] = weight

    # Save the updated election data back to the JSON file
    election_data["role_weights"] = role_weights
    with open("election.json", "w") as f:
        json.dump(election_data, f, indent=4)

    # Confirm the update
    await interaction.response.send_message(f"✅ Role weight for {role_name} set to {weight}.")
@bot.tree.command(name="vote", description="Vote for a candidate in the election.")
async def vote(interaction: discord.Interaction, candidate: discord.Member):
    # Load election data
    try:
        with open("election.json", "r") as f:
            election_data = json.load(f)
    except FileNotFoundError:
        await interaction.response.send_message("❌ No election data found. Start an election first.", ephemeral=True)
        return

    # Check if the election is active
    if not election_data["active"]:
        await interaction.response.send_message("❌ The election is no longer active.", ephemeral=True)
        return

    # Check if the user has already voted
    if str(interaction.user.id) in election_data["voters"]:
        await interaction.response.send_message("❌ You have already voted!", ephemeral=True)
        return

    # Calculate the user's vote weight based on their roles
    total_weight = 1  # Base vote
    role_weights = election_data.get("role_weights", {})

    for role in interaction.user.roles:
        if role.name in role_weights:
            total_weight += role_weights[role.name]

    # Add the vote to the selected candidate
    candidate_id = str(candidate.id)
    if candidate_id not in election_data["candidates"]:
        await interaction.response.send_message("❌ Invalid candidate selected.", ephemeral=True)
        return

    election_data["candidates"][candidate_id] += total_weight
    election_data["voters"].append(str(interaction.user.id))  # Mark the user as having voted

    # Save updated election data
    with open("election.json", "w") as f:
        json.dump(election_data, f, indent=4)

    # Ephemeral confirmation message (only visible to the user who voted)
    await interaction.response.send_message(f"✅ You voted for {candidate.display_name} with a total vote weight of {total_weight}.", ephemeral=True)
@bot.tree.command(name="end_election", description="Forcefully end the election and announce the winner.")
async def end_election(interaction: discord.Interaction):
    # Ensure only the bot owner can run this command
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You don't have permission to end the election.", ephemeral=True)
        return

    # Load the current election data from the JSON file
    try:
        with open("election.json", "r") as f:
            election_data = json.load(f)
    except FileNotFoundError:
        await interaction.response.send_message("❌ No election data found. Start an election first.", ephemeral=True)
        return

    # Check if the election is active
    if not election_data["active"]:
        await interaction.response.send_message("❌ The election is already over.", ephemeral=True)
        return

    # Find the winner (candidate with the most votes)
    winner_id = max(election_data["candidates"], key=election_data["candidates"].get)
    winner = await bot.fetch_user(int(winner_id))

    # Get the reward from the election data
    reward = election_data.get("reward", "No reward set")

    # Announce the winner
    channel = bot.get_channel()  # Replace with your announcement channel ID
    await channel.send(f"🎉 The winner is {winner.display_name}! They won: {reward}")

    # Apply the reward (e.g., giving the winner a role)
    role_name = reward.split(" ")[0]  # Example: if reward is "Admin role", it takes "Admin"
    role = discord.utils.get(winner.guild.roles, name=role_name)

    if role:
        await winner.add_roles(role)
        await channel.send(f"✅ {winner.display_name} has been given the {role_name} role!")

    # Mark the election as inactive in the JSON file
    election_data["active"] = False
    with open("election.json", "w") as f:
        json.dump(election_data, f, indent=4)

    # Confirmation message
    await interaction.response.send_message(f"✅ Election ended! The winner is {winner.display_name} and the reward has been applied.")
bot.run("BOT TOKEN HERE")
