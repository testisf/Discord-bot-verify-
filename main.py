import discord
from discord.ext import commands
import asyncio
import logging
import os
from aiohttp import web
from config import Config
from commands.military import MilitaryCommands
from commands.verification import VerificationCommands
from commands.tickets import TicketCommands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilitaryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        # Note: Without privileged intents, member status data is limited
        # We'll use approximate calculations based on guild statistics
        
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
        await self.add_cog(TicketCommands(self))
        
        # Sync slash commands globally and to guilds
        try:
            # Global sync (takes up to 1 hour to propagate)
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s) globally")
            
            # Guild-specific sync for immediate availability
            for guild in self.guilds:
                try:
                    guild_synced = await self.tree.sync(guild=guild)
                    logger.info(f"Synced {len(guild_synced)} command(s) to guild: {guild.name}")
                except Exception as guild_error:
                    logger.error(f"Failed to sync commands to guild {guild.name}: {guild_error}")
                    
            for command in synced:
                logger.info(f"  - {command.name}: {command.description}")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has landed on the battlefield!')
        logger.info(f'Bot is in {len(self.guilds)} servers')
        
        # Sync commands to all connected guilds for immediate availability
        for guild in self.guilds:
            try:
                guild_synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(guild_synced)} command(s) to guild: {guild.name}")
            except Exception as guild_error:
                logger.error(f"Failed to sync commands to guild {guild.name}: {guild_error}")
        
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

async def health_check(request):
    """Health check endpoint for hosting platforms"""
    return web.json_response({"status": "healthy", "bot": "online"})

async def start_web_server():
    """Start a simple web server for hosting platform health checks"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.environ.get('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Health check server started on port {port}")

async def main():
    """Main function to run the bot"""
    bot = MilitaryBot()
    
    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not found!")
        return
    
    try:
        # Start both web server and bot concurrently
        await asyncio.gather(
            start_web_server(),
            bot.start(token)
        )
    except discord.LoginFailure:
        logger.error("Invalid bot token!")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
