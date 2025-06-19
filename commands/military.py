import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from config import Config
from utils.ranks import get_nato_rank
from utils.roblox_api import RobloxAPI

class MilitaryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure the data directory and file exist"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(Config.USER_DATA_FILE):
            with open(Config.USER_DATA_FILE, 'w') as f:
                json.dump({}, f)
    
    def load_user_data(self):
        """Load user data from JSON file"""
        try:
            with open(Config.USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_user_data(self, data):
        """Save user data to JSON file"""
        with open(Config.USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def get_host_avatar(self, user_id: str) -> str:
        """Get the host's Roblox avatar URL"""
        try:
            user_data = self.load_user_data()
            if user_id in user_data and 'roblox_user_id' in user_data[user_id]:
                roblox_user_id = user_data[user_id]['roblox_user_id']
                
                async with RobloxAPI(Config.ROBLOX_COOKIE) as api:
                    avatar_url = await api.get_user_avatar_url(roblox_user_id)
                    if avatar_url:
                        return avatar_url
            
            # Default avatar if not found
            return "https://cdn.jsdelivr.net/gh/feathericons/feather/icons/user.svg"
        except Exception as e:
            print(f"Error getting host avatar: {e}")
            return "https://cdn.jsdelivr.net/gh/feathericons/feather/icons/user.svg"
    
    @app_commands.command(name="tryout", description="Schedule a military tryout")
    @app_commands.describe(
        tryout_type="Type of tryout (e.g., Infantry, Armor, Aviation)",
        starts="When the tryout starts (e.g., '2pm EST', 'in 30 minutes')",
        pad_number="Landing pad number (1-9)"
    )
    async def tryout(self, interaction: discord.Interaction, tryout_type: str, starts: str, pad_number: int):
        """Handle tryout command"""
        
        # Validate pad number
        if not (Config.MIN_PAD_NUMBER <= pad_number <= Config.MAX_PAD_NUMBER):
            await interaction.response.send_message(
                f"❌ Pad number must be between {Config.MIN_PAD_NUMBER} and {Config.MAX_PAD_NUMBER}!",
                ephemeral=True
            )
            return
        
        # Get host avatar
        host_avatar_url = await self.get_host_avatar(str(interaction.user.id))
        
        # Create embed
        embed = discord.Embed(
            title="🎖️ Military Tryout Scheduled",
            color=Config.COLORS['military'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Tryout Type", value=f"**{tryout_type}**", inline=True)
        embed.add_field(name="Start Time", value=f"**{starts}**", inline=True)
        embed.add_field(name="Landing Pad", value=f"**Pad {pad_number}**", inline=True)
        embed.add_field(name="Organizer", value=interaction.user.mention, inline=False)
        
        embed.set_footer(text="Report to the designated pad on time!")
        embed.set_thumbnail(url=host_avatar_url)
        
        # Save tryout data
        user_data = self.load_user_data()
        user_id = str(interaction.user.id)
        
        if user_id not in user_data:
            user_data[user_id] = {"tryouts": [], "trainings": []}
        
        # Ensure tryouts array exists for existing users
        if "tryouts" not in user_data[user_id]:
            user_data[user_id]["tryouts"] = []
        
        tryout_data = {
            "type": tryout_type,
            "starts": starts,
            "pad": pad_number,
            "timestamp": datetime.utcnow().isoformat(),
            "guild_id": str(interaction.guild.id) if interaction.guild else "Unknown"
        }
        
        user_data[user_id]["tryouts"].append(tryout_data)
        self.save_user_data(user_data)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="training", description="Schedule military training")
    @app_commands.describe(
        training_type="Type of training (e.g., Combat, Tactical, Physical)",
        starts="When the training starts (e.g., '3pm EST', 'tomorrow')",
        pad_number="Training pad number (1-9)"
    )
    async def training(self, interaction: discord.Interaction, training_type: str, starts: str, pad_number: int):
        """Handle training command"""
        
        # Validate pad number
        if not (Config.MIN_PAD_NUMBER <= pad_number <= Config.MAX_PAD_NUMBER):
            await interaction.response.send_message(
                f"❌ Pad number must be between {Config.MIN_PAD_NUMBER} and {Config.MAX_PAD_NUMBER}!",
                ephemeral=True
            )
            return
        
        # Get host avatar
        host_avatar_url = await self.get_host_avatar(str(interaction.user.id))
        
        # Create embed
        embed = discord.Embed(
            title="🏋️ Military Training Scheduled",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Training Type", value=f"**{training_type}**", inline=True)
        embed.add_field(name="Start Time", value=f"**{starts}**", inline=True)
        embed.add_field(name="Training Pad", value=f"**Pad {pad_number}**", inline=True)
        embed.add_field(name="Instructor", value=interaction.user.mention, inline=False)
        
        embed.set_footer(text="Come prepared and ready to train!")
        embed.set_thumbnail(url=host_avatar_url)
        
        # Save training data
        user_data = self.load_user_data()
        user_id = str(interaction.user.id)
        
        if user_id not in user_data:
            user_data[user_id] = {"tryouts": [], "trainings": []}
        
        # Ensure trainings array exists for existing users
        if "trainings" not in user_data[user_id]:
            user_data[user_id]["trainings"] = []
        
        training_data = {
            "type": training_type,
            "starts": starts,
            "pad": pad_number,
            "timestamp": datetime.utcnow().isoformat(),
            "guild_id": str(interaction.guild.id) if interaction.guild else "Unknown"
        }
        
        user_data[user_id]["trainings"].append(training_data)
        self.save_user_data(user_data)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="schedule", description="View your scheduled tryouts and trainings")
    async def schedule(self, interaction: discord.Interaction):
        """View user's scheduled events"""
        user_data = self.load_user_data()
        user_id = str(interaction.user.id)
        
        if user_id not in user_data:
            await interaction.response.send_message(
                "📅 You haven't scheduled any tryouts or trainings yet!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"📅 {interaction.user.display_name}'s Military Schedule",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        tryouts = user_data[user_id].get("tryouts", [])
        trainings = user_data[user_id].get("trainings", [])
        
        if tryouts:
            tryout_list = []
            for i, tryout in enumerate(tryouts[-5:], 1):  # Show last 5
                tryout_list.append(f"{i}. **{tryout['type']}** - {tryout['starts']} (Pad {tryout['pad']})")
            embed.add_field(
                name="🎖️ Recent Tryouts",
                value="\n".join(tryout_list),
                inline=False
            )
        
        if trainings:
            training_list = []
            for i, training in enumerate(trainings[-5:], 1):  # Show last 5
                training_list.append(f"{i}. **{training['type']}** - {training['starts']} (Pad {training['pad']})")
            embed.add_field(
                name="🏋️ Recent Trainings",
                value="\n".join(training_list),
                inline=False
            )
        
        if not tryouts and not trainings:
            embed.description = "No scheduled events found."
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MilitaryCommands(bot))
