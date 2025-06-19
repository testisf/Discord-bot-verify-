import os

class Config:
    """Configuration settings for the Discord bot"""
    
    # Discord settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '')
    
    # Roblox group settings
    ROBLOX_GROUP_ID = 11925205  # Convert to int for API
    ROBLOX_COOKIE = os.getenv('ROBLOX_COOKIE', '')
    
    # Bot settings
    COMMAND_PREFIX = "!"
    
    # File paths
    USER_DATA_FILE = "data/users.json"
    
    # Verification settings
    VERIFICATION_CODE_LENGTH = 8
    VERIFICATION_TIMEOUT = 300  # 5 minutes
    
    # Military settings
    MAX_PAD_NUMBER = 9
    MIN_PAD_NUMBER = 1
    
    # Colors for embeds
    COLORS = {
        'success': 0x00ff00,
        'error': 0xff0000,
        'warning': 0xffff00,
        'info': 0x0099ff,
        'military': 0x4B0082
    }
