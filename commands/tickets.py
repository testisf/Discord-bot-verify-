import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime
from config import Config

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Never expires
        
    @discord.ui.button(label='🎫 Open Ticket', style=discord.ButtonStyle.success, emoji='🎫', custom_id='open_ticket')
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle ticket creation"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if command is used in a guild
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.followup.send(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return
        
        guild = interaction.guild
        user = interaction.user
        
        # Look for existing ticket channel
        existing_ticket = None
        for channel in guild.text_channels:
            if channel.name.startswith(f'ticket-{user.id}'):
                existing_ticket = channel
                break
        
        if existing_ticket:
            await interaction.followup.send(
                f"❌ You already have an open ticket: {existing_ticket.mention}",
                ephemeral=True
            )
            return
        
        # Create ticket category if it doesn't exist
        category = discord.utils.get(guild.categories, name="🎫 Support Tickets")
        if not category:
            category = await guild.create_category("🎫 Support Tickets")
        
        # Create ticket channel
        channel_name = f"ticket-{user.id}"
        
        # Set permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Add support role permissions
        support_role = guild.get_role(1385451612650344523)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True, 
                manage_messages=True
            )
        
        # Create the channel
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )
        
        # Create ticket embed
        embed = discord.Embed(
            title="🎫 Support Ticket Created",
            description=f"Thank you {user.mention} for creating a support ticket!\nA support team member will assist you shortly.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋 Ticket Information",
            value=f"**User:** {user.mention}\n**User ID:** {user.id}\n**Created:** <t:{int(datetime.utcnow().timestamp())}:F>",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Instructions",
            value="• Please describe your issue in detail\n• A support member will respond soon\n• Use the 🔒 button below to close this ticket",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        if guild.icon:
            embed.set_footer(text="Support Ticket System", icon_url=guild.icon.url)
        else:
            embed.set_footer(text="Support Ticket System")
        
        # Create close ticket view
        close_view = CloseTicketView()
        
        # Send ticket message
        await ticket_channel.send(
            content=f"{user.mention} {f'{support_role.mention}' if support_role else ''}",
            embed=embed,
            view=close_view
        )
        
        # Save ticket data
        ticket_data = {
            "user_id": user.id,
            "channel_id": ticket_channel.id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open"
        }
        
        await self.save_ticket_data(ticket_data)
        
        await interaction.followup.send(
            f"✅ Ticket created successfully! {ticket_channel.mention}",
            ephemeral=True
        )
    
    async def save_ticket_data(self, ticket_data):
        """Save ticket data to JSON file"""
        os.makedirs("data", exist_ok=True)
        tickets_file = "data/tickets.json"
        
        # Load existing tickets
        tickets = {}
        if os.path.exists(tickets_file):
            try:
                with open(tickets_file, 'r') as f:
                    tickets = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                tickets = {}
        
        # Add new ticket
        tickets[str(ticket_data["channel_id"])] = ticket_data
        
        # Save tickets
        with open(tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.danger, emoji='🔒', custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle ticket closure"""
        await interaction.response.defer()
        
        # Check if command is used in a guild
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.followup.send(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return
        
        guild = interaction.guild
        user = interaction.user
        support_role = guild.get_role(1385451612650344523)
        
        # Check if user is the ticket owner or has support role
        if isinstance(interaction.channel, discord.TextChannel):
            channel_name = interaction.channel.name
            if channel_name.startswith('ticket-'):
                ticket_user_id = channel_name.split('-')[1]
                is_ticket_owner = str(user.id) == ticket_user_id
                is_support = support_role in user.roles if support_role else False
                
                if not (is_ticket_owner or is_support):
                    await interaction.followup.send(
                        "❌ You don't have permission to close this ticket!",
                        ephemeral=True
                    )
                    return
        
        # Create transcript
        transcript_embed = discord.Embed(
            title="🎫 Ticket Closed",
            description=f"Ticket closed by {user.mention}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        transcript_embed.add_field(
            name="📊 Ticket Statistics",
            value=f"**Closed by:** {user.mention}\n**Closed at:** <t:{int(datetime.utcnow().timestamp())}:F>\n**Channel:** #{interaction.channel.name if hasattr(interaction.channel, 'name') else 'Unknown'}",
            inline=False
        )
        
        # Update ticket data
        if hasattr(interaction.channel, 'id'):
            await self.update_ticket_status(interaction.channel.id, "closed")
        
        # Send closing message
        await interaction.followup.send(embed=transcript_embed)
        
        # Wait a moment then delete the channel
        await interaction.followup.send("🔒 This ticket will be deleted in 10 seconds...")
        
        import asyncio
        await asyncio.sleep(10)
        
        try:
            if isinstance(interaction.channel, discord.TextChannel):
                await interaction.channel.delete(reason=f"Ticket closed by {user}")
        except (discord.NotFound, discord.Forbidden):
            pass  # Channel already deleted or no permission
    
    async def update_ticket_status(self, channel_id, status):
        """Update ticket status in JSON file"""
        tickets_file = "data/tickets.json"
        
        if os.path.exists(tickets_file):
            try:
                with open(tickets_file, 'r') as f:
                    tickets = json.load(f)
                
                if str(channel_id) in tickets:
                    tickets[str(channel_id)]["status"] = status
                    tickets[str(channel_id)]["closed_at"] = datetime.utcnow().isoformat()
                    
                    with open(tickets_file, 'w') as f:
                        json.dump(tickets, f, indent=2)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.member_count_channel_id = 1384582591516119151
        self.ticket_channel_id = 1384585517730893864
        self.update_member_count.start()
    
    async def cog_unload(self):
        self.update_member_count.cancel()
    
    @app_commands.command(name="setup_tickets", description="Setup the ticket system (Admin only)")
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup ticket system"""
        # Check if user has administrator permissions
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permissions to use this command!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get the ticket channel
        ticket_channel = self.bot.get_channel(self.ticket_channel_id)
        if not ticket_channel:
            await interaction.followup.send(
                f"❌ Could not find ticket channel with ID: {self.ticket_channel_id}",
                ephemeral=True
            )
            return
        
        # Create ticket embed
        embed = discord.Embed(
            title="🎫 Support Ticket System",
            description="Need help? Create a support ticket and our team will assist you!",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔧 How to create a ticket",
            value="Click the green **🎫 Open Ticket** button below to create a private support channel.",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Quick Response",
            value="Our support team will respond to your ticket as soon as possible.",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Privacy",
            value="Only you and support staff can see your ticket.",
            inline=True
        )
        
        embed.add_field(
            name="📋 Guidelines",
            value="• Be clear and detailed about your issue\n• Be patient while waiting for support\n• Close your ticket when your issue is resolved",
            inline=False
        )
        
        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.set_footer(text="Support Ticket System • Click button below to open ticket")
        else:
            embed.set_footer(text="Support Ticket System • Click button below to open ticket")
        
        # Create persistent view
        view = TicketView()
        
        # Send ticket message
        await ticket_channel.send(embed=embed, view=view)
        
        await interaction.followup.send(
            f"✅ Ticket system setup complete in {ticket_channel.mention}!",
            ephemeral=True
        )
    
    @tasks.loop(minutes=5)  # Update every 5 minutes
    async def update_member_count(self):
        """Update member count with server activity"""
        try:
            channel = self.bot.get_channel(self.member_count_channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                return
            
            guild = channel.guild
            
            # Calculate member statistics using available data
            total_members = guild.member_count or 0
            
            # Count voice channel members for active users
            voice_members = 0
            for voice_channel in guild.voice_channels:
                voice_members += len(voice_channel.members)
            
            # Use presence information when available
            online_count = 0
            idle_count = 0
            dnd_count = 0
            offline_count = 0
            
            # Count members we can see (limited without privileged intents)
            visible_members = 0
            for member in guild.members:
                visible_members += 1
                try:
                    if member.status == discord.Status.online:
                        online_count += 1
                    elif member.status == discord.Status.idle:
                        idle_count += 1
                    elif member.status == discord.Status.dnd:
                        dnd_count += 1
                    else:
                        offline_count += 1
                except:
                    # Status unavailable, count as offline
                    offline_count += 1
            
            # If we can't see many members, estimate based on voice activity and typical patterns
            if visible_members < total_members * 0.1:  # Less than 10% visible
                # Base estimate on voice channel activity and typical Discord usage patterns
                estimated_online = max(voice_members * 2, total_members * 0.15)  # At least 15% typically online
                estimated_online = min(estimated_online, total_members * 0.6)  # Cap at 60%
                
                online_count = int(estimated_online * 0.4)  # 40% fully online
                idle_count = int(estimated_online * 0.35)   # 35% idle
                dnd_count = int(estimated_online * 0.25)    # 25% DND
                offline_count = total_members - online_count - idle_count - dnd_count
                
                online_members = online_count + idle_count + dnd_count
            else:
                online_members = online_count + idle_count + dnd_count
            
            # Calculate activity percentage
            activity_percentage = (online_members / total_members * 100) if total_members > 0 else 0
            
            # Determine activity level and emoji
            if activity_percentage >= 70:
                activity_emoji = "🟢"
                activity_status = "Very Active"
            elif activity_percentage >= 50:
                activity_emoji = "🟡"
                activity_status = "Active"
            elif activity_percentage >= 30:
                activity_emoji = "🟠"
                activity_status = "Moderate"
            else:
                activity_emoji = "⚫"
                activity_status = "Low Activity"
            
            # Create member count embed
            embed = discord.Embed(
                title="📊 Server Statistics",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="👥 Total Members",
                value=f"```{total_members:,}```",
                inline=True
            )
            
            embed.add_field(
                name="🟢 Online Members",
                value=f"```{online_members:,}```",
                inline=True
            )
            
            embed.add_field(
                name=f"{activity_emoji} Server Activity",
                value=f"```{activity_percentage:.1f}% {activity_status}```",
                inline=True
            )
            
            # Add activity bar
            bar_length = 20
            filled_length = int(bar_length * (activity_percentage / 100))
            activity_bar = "🟢" * filled_length + "⚫" * (bar_length - filled_length)
            
            embed.add_field(
                name="📈 Activity Level",
                value=f"{activity_bar} {activity_percentage:.1f}%",
                inline=False
            )
            
            # Add member status breakdown using our calculated counts
            status_counts = {
                "🟢 Online": online_count,
                "🟡 Idle": idle_count,
                "🔴 DND": dnd_count,
                "⚫ Offline": offline_count
            }
            
            status_text = "\n".join([f"{emoji} {count:,}" for emoji, count in status_counts.items()])
            
            # Add debug info about data visibility
            if visible_members < total_members * 0.1:
                status_text += f"\n⚠️ Estimated (visible: {visible_members}/{total_members})"
                if voice_members > 0:
                    status_text += f"\n🎤 Voice active: {voice_members}"
            embed.add_field(
                name="👤 Member Status",
                value=f"```{status_text}```",
                inline=True
            )
            
            # Add timestamp info
            embed.add_field(
                name="🕐 Last Updated",
                value=f"<t:{int(datetime.utcnow().timestamp())}:R>",
                inline=True
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
                embed.set_footer(text=f"{guild.name} • Live Statistics", icon_url=guild.icon.url)
            else:
                embed.set_footer(text=f"{guild.name} • Live Statistics")
            
            # Get recent messages to edit or send new one
            try:
                async for message in channel.history(limit=10):
                    if message.author == self.bot.user and message.embeds:
                        if "Server Statistics" in message.embeds[0].title:
                            await message.edit(embed=embed)
                            return
                
                # If no existing message found, send new one
                await channel.send(embed=embed)
                
            except discord.HTTPException:
                pass  # Failed to update, will try again next loop
                
        except Exception as e:
            print(f"Error updating member count: {e}")
    
    @update_member_count.before_loop
    async def before_update_member_count(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))
    
    # Add persistent views
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())