# Military Discord Bot with Roblox Verification

A Discord bot designed for military-themed roleplay servers with advanced Roblox verification and rank management capabilities.

## Features

- **Real Roblox Verification**: Integrates with Roblox API using cookie authentication
- **NATO Rank System**: Maps Roblox group ranks to NATO military codes
- **Dynamic Nicknames**: Automatically formats Discord nicknames based on rank ([HQ] for OF-9+)
- **Military Operations**: Schedule tryouts and training sessions with landing pad assignments
- **Avatar Display**: Shows host's Roblox avatar in event announcements
- **Interactive UI**: Button-based verification system with real-time feedback

## Commands

- `/verify <roblox_username>` - Link your Roblox account
- `/reverify <roblox_username>` - Update your verification status
- `/verification_status` - Check your current verification
- `/tryout <type> <start_time> <pad_number>` - Schedule military tryouts
- `/training <type> <start_time> <pad_number>` - Schedule training sessions
- `/schedule` - View your upcoming events

## Setup

1. Install dependencies:
```bash
pip install discord.py aiohttp requests
```

2. Configure environment variables:
- `DISCORD_TOKEN` - Your Discord bot token
- `ROBLOX_COOKIE` - Your Roblox .ROBLOSECURITY cookie

3. Update `config.py` with your Roblox group ID

4. Run the bot:
```bash
python main.py
```

## Deployment Commands

For hosting platforms like Render:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py` (note: lowercase 'python')

## Project Structure

- `main.py` - Bot entry point and initialization
- `config.py` - Configuration settings and constants
- `commands/` - Command modules (military operations, verification)
- `utils/` - Utility modules (rank mapping, Roblox API)
- `data/` - User data storage (JSON files)

## Rank System

The bot uses NATO rank codes mapped to your Roblox group hierarchy:
- Enlisted: OR-1 through OR-9
- Warrant Officers: WO-1 through WO-5
- Officers: OF-1 through OF-10
- High Command: OF-9+ displays as [HQ]

## Requirements

- Python 3.11+
- discord.py 2.5+
- Valid Discord bot token
- Roblox account with group access

## License

This project is open source and available under the MIT License.