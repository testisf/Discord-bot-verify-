import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import string
import asyncio
from datetime import datetime, timedelta
from config import Config
from utils.ranks import get_nato_rank, RANK_MAPPING, format_nickname
from utils.roblox_api import verify_roblox_user

class VerificationView(discord.ui.View):
    def __init__(self, verification_code, user_id, roblox_username):
        super().__init__(timeout=Config.VERIFICATION_TIMEOUT)
        self.verification_code = verification_code
        self.user_id = user_id
        self.roblox_username = roblox_username
        self.verified = False
    
    @discord.ui.button(label='Verify', style=discord.ButtonStyle.success, emoji='✅')
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You can only verify your own account!",
                ephemeral=True
            )
            return
        
        # Import config and start verification
        from config import Config
        
        await interaction.response.send_message(
            "🔍 Starting verification process...",
            ephemeral=True
        )
        
        # Check if Roblox cookie is configured
        if not Config.ROBLOX_COOKIE:
            await interaction.followup.send(
                "❌ Roblox API is not configured. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            "🔍 Checking your Roblox description for the verification code...",
            ephemeral=True
        )
        
        # Use real Roblox API to verify user
        try:
            verification_result = await verify_roblox_user(
                Config.ROBLOX_COOKIE, 
                self.roblox_username, 
                self.verification_code, 
                Config.ROBLOX_GROUP_ID
            )
            
            if not verification_result or not verification_result.get('success'):
                error_message = verification_result.get('error', 'Unknown error') if verification_result else 'API connection failed'
                await interaction.followup.send(
                    f"❌ Verification failed: {error_message}",
                    ephemeral=True
                )
                return
        except Exception as e:
            await interaction.followup.send(
                f"❌ API Error: {str(e)}",
                ephemeral=True
            )
            return
        
        # Get NATO rank from Roblox rank ID
        roblox_rank_id = verification_result['rank_id']
        nato_rank = get_nato_rank(roblox_rank_id)
        
        # Use the actual username from Roblox API response
        actual_username = verification_result['username']
        
        embed = discord.Embed(
            title="✅ Verification Successful!",
            color=0x00ff00,  # Green color
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Roblox Username", value=actual_username, inline=True)
        embed.add_field(name="Rank", value=f"{nato_rank} ({verification_result['rank_name']})", inline=True)
        embed.add_field(name="Group ID", value=str(Config.ROBLOX_GROUP_ID), inline=True)
        
        new_nickname = format_nickname(nato_rank, actual_username)
        embed.add_field(name="New Nickname", value=new_nickname, inline=False)
        
        # Attempt to change nickname
        try:
            if interaction.guild:
                # Try to get member from interaction first, then fallback to guild lookup
                member = getattr(interaction, 'user', None)
                if hasattr(member, 'nick'):  # This is a Member object
                    target_member = member
                else:
                    # Fallback to guild member lookup
                    target_member = interaction.guild.get_member(interaction.user.id)
                
                if target_member:
                    await target_member.edit(nick=new_nickname)
                    embed.add_field(name="Status", value="Nickname updated successfully!", inline=False)
                else:
                    embed.add_field(name="Status", value="Could not find member in guild. Try running the command in the server.", inline=False)
            else:
                embed.add_field(name="Status", value="Command must be used in a server", inline=False)
        except discord.Forbidden:
            embed.add_field(name="Status", value="Could not update nickname (bot needs 'Manage Nicknames' permission)", inline=False)
        except Exception as e:
            embed.add_field(name="Status", value=f"Error updating nickname: {str(e)}", inline=False)
        
        # Save verification data
        try:
            import json
            import os
            
            # Ensure data file exists
            os.makedirs("data", exist_ok=True)
            if not os.path.exists(Config.USER_DATA_FILE):
                with open(Config.USER_DATA_FILE, 'w') as f:
                    json.dump({}, f)
            
            # Load, update, and save user data
            with open(Config.USER_DATA_FILE, 'r') as f:
                user_data = json.load(f)
            
            user_id = str(interaction.user.id)
            user_data[user_id] = user_data.get(user_id, {})
            user_data[user_id]["verification"] = {
                "verified": True,
                "roblox_username": actual_username,
                "roblox_user_id": verification_result['user_id'],
                "rank": nato_rank,
                "rank_name": verification_result['rank_name'],
                "rank_id": verification_result['rank_id'],
                "verification_date": datetime.utcnow().isoformat(),
                "guild_id": str(interaction.guild.id) if interaction.guild else "unknown"
            }
            
            with open(Config.USER_DATA_FILE, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving verification data: {e}")
        
        self.verified = True
        # Disable the button after verification
        button.disabled = True
        
        # Send the success message via followup
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def on_timeout(self):
        if not self.verified:
            # Disable all buttons on timeout
            pass  # The view automatically disables items on timeout

class VerificationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_verifications = {}
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure the data directory and file exist"""
        import os
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
    
    def generate_verification_code(self):
        """Generate a random verification code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=Config.VERIFICATION_CODE_LENGTH))
    
    @app_commands.command(name="verify", description="Start the verification process to link your Roblox account")
    @app_commands.describe(roblox_username="Your Roblox username")
    async def verify(self, interaction: discord.Interaction, roblox_username: str):
        """Handle verification command"""
        user_id = str(interaction.user.id)
        
        # Check if user is already verified
        user_data = self.load_user_data()
        if user_id in user_data and user_data[user_id].get("verification", {}).get("verified", False):
            await interaction.response.send_message(
                "✅ You are already verified! Use `/reverify` if you need to update your verification.",
                ephemeral=True
            )
            return
        
        # Generate verification code
        verification_code = self.generate_verification_code()
        self.pending_verifications[user_id] = {
            "code": verification_code,
            "timestamp": datetime.utcnow(),
            "guild_id": str(interaction.guild.id) if interaction.guild else "unknown",
            "roblox_username": roblox_username
        }
        
        # Create embed with instructions
        embed = discord.Embed(
            title="🔐 Military Verification Process",
            description="Follow these steps to verify your Roblox account:",
            color=Config.COLORS['warning'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Step 1",
            value="Copy the verification code below",
            inline=False
        )
        
        embed.add_field(
            name="Step 2",
            value="Go to your Roblox profile and edit your description",
            inline=False
        )
        
        embed.add_field(
            name="Step 3",
            value=f"Add this code to your description: `{verification_code}`",
            inline=False
        )
        
        embed.add_field(
            name="Step 4",
            value="Click the 'Verify' button below",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Important",
            value=f"You have {Config.VERIFICATION_TIMEOUT//60} minutes to complete verification.\nMake sure you're in group `{Config.ROBLOX_GROUP_ID}`!",
            inline=False
        )
        
        embed.set_footer(text="Your rank will be automatically detected from the group")
        
        # Create view with verify button
        view = VerificationView(verification_code, interaction.user.id, roblox_username)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="reverify", description="Re-verify your Roblox account (updates rank)")
    @app_commands.describe(roblox_username="Your Roblox username")
    async def reverify(self, interaction: discord.Interaction, roblox_username: str):
        """Handle reverification command"""
        
        user_id = str(interaction.user.id)
        
        # Generate new verification code
        verification_code = self.generate_verification_code()
        self.pending_verifications[user_id] = {
            "code": verification_code,
            "timestamp": datetime.utcnow(),
            "guild_id": str(interaction.guild.id) if interaction.guild else "unknown",
            "roblox_username": roblox_username
        }
        
        # Create embed with instructions
        embed = discord.Embed(
            title="🔄 Military Re-verification Process",
            description="Update your verification and rank:",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Step 1",
            value="Copy the new verification code below",
            inline=False
        )
        
        embed.add_field(
            name="Step 2",
            value="Update your Roblox profile description",
            inline=False
        )
        
        embed.add_field(
            name="Step 3",
            value=f"Replace old code with: `{verification_code}`",
            inline=False
        )
        
        embed.add_field(
            name="Step 4",
            value="Click the 'Verify' button below",
            inline=False
        )
        
        embed.add_field(
            name="📋 Note",
            value="This will update your nickname with your current rank.",
            inline=False
        )
        
        # Create view with verify button
        view = VerificationView(verification_code, interaction.user.id, roblox_username)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="verification_status", description="Check your verification status")
    async def verification_status(self, interaction: discord.Interaction):
        """Check user's verification status"""
        user_data = self.load_user_data()
        user_id = str(interaction.user.id)
        
        embed = discord.Embed(
            title="🔍 Verification Status",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        if user_id in user_data and user_data[user_id].get("verification", {}).get("verified", False):
            verification = user_data[user_id]["verification"]
            embed.color = Config.COLORS['success']
            embed.add_field(name="Status", value="✅ Verified", inline=True)
            embed.add_field(name="Roblox Username", value=verification.get("roblox_username", "Unknown"), inline=True)
            embed.add_field(name="Rank", value=verification.get("rank", "Unknown"), inline=True)
            embed.add_field(name="Verified On", value=verification.get("verification_date", "Unknown"), inline=False)
        else:
            embed.color = Config.COLORS['error']
            embed.add_field(name="Status", value="❌ Not Verified", inline=True)
            embed.add_field(name="Action", value="Use `/verify` to start verification", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerificationCommands(bot))
