import discord
from discord.ext import commands
import asyncio
import logging
import os
from config import Config
from commands.military import MilitaryCommands
from commands.verification import VerificationCommands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilitaryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        # Remove privileged intents that require approval
        # intents.message_content = True  # Only needed for prefix commands
        # intents.members = True  # Only needed for member operations
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Add cogs
        await self.add_cog(MilitaryCommands(self))
        await self.add_cog(VerificationCommands(self))
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has landed on the battlefield!')
        logger.info(f'Bot is in {len(self.guilds)} servers')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name="British Army"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        else:
            logger.error(f"Unexpected error: {error}")
            await ctx.send("❌ An unexpected error occurred!")

async def main():
    """Main function to run the bot"""
    bot = MilitaryBot()
    
    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not found!")
        return
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token!")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
