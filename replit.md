# Military Discord Bot

## Overview

This is a Discord bot designed for military-themed servers with Roblox group integration. The bot provides military operations management, user verification through Roblox, and rank-based functionality using NATO rank structures. Built with Python and discord.py, it features slash commands and interactive UI components for enhanced user experience.

## System Architecture

### Frontend Architecture
- **Discord Interface**: Primary user interface through Discord's slash commands and interactive buttons
- **Embed System**: Rich message formatting using Discord embeds for better visual presentation
- **Interactive UI**: Custom Discord UI views with buttons for verification and other operations

### Backend Architecture
- **Command Pattern**: Modular cog-based architecture using discord.py's extension system
- **Event-Driven**: Asynchronous event handling for Discord interactions
- **JSON Data Storage**: Simple file-based storage for user data and configurations

### Core Components
- **Main Bot Class**: Central bot instance managing connections and cog loading
- **Military Commands**: Handles military operations like tryouts and pad assignments
- **Verification System**: Roblox account verification with temporary codes
- **Rank Management**: NATO rank mapping system for military hierarchy

## Key Components

### Bot Core (`main.py`)
- **MilitaryBot Class**: Extends discord.py's commands.Bot with custom initialization
- **Cog Management**: Automatic loading of command modules
- **Status Management**: Dynamic bot presence and activity updates
- **Command Syncing**: Slash command registration and synchronization

### Configuration Management (`config.py`)
- **Environment Variables**: Secure token management through environment variables
- **Bot Settings**: Centralized configuration for prefixes, timeouts, and file paths
- **Roblox Integration**: Group ID and verification settings
- **Color Schemes**: Consistent embed coloring for different message types

### Command Modules
- **Military Operations**: Tryout scheduling with pad number validation
- **Verification System**: Interactive Roblox account verification with UI components
- **Rank Utilities**: NATO rank code mapping and conversion functions

### Data Management
- **JSON Storage**: Simple file-based user data persistence
- **Data Validation**: Input validation for pad numbers and verification codes
- **File System Management**: Automatic directory and file creation

## Data Flow

### Verification Process
1. User initiates verification command
2. Bot generates random verification code
3. User adds code to Roblox description
4. Bot validates code through mock API call (placeholder for real Roblox API)
5. User data stored locally with rank information

### Military Operations
1. User schedules tryout with type, time, and pad number
2. System validates pad number range (1-9)
3. Tryout information formatted and announced
4. Landing pad assignment managed through configuration

### Rank Management
1. Roblox group rank retrieved during verification
2. Rank ID mapped to NATO code system
3. Permissions and access determined by rank level
4. Rank information displayed in user profiles

## External Dependencies

### Discord Integration
- **discord.py**: Primary Discord API wrapper for bot functionality
- **Async Support**: Built-in asyncio support for concurrent operations
- **Slash Commands**: Modern Discord interaction system implementation

### Roblox Integration (Planned)
- **Roblox API**: Group membership and rank verification (currently mocked)
- **User Verification**: Profile description validation for account linking
- **Group Management**: Rank retrieval and permission validation

### Python Dependencies
- **asyncio**: Asynchronous programming support
- **json**: Data serialization and storage
- **logging**: Comprehensive logging system
- **os**: Environment variable and file system management

## Deployment Strategy

### Replit Deployment
- **Automatic Dependencies**: UV package manager with pyproject.toml configuration
- **Environment Management**: Secure token storage through Replit secrets
- **Continuous Running**: Workflow configuration for persistent bot operation
- **Development Workflow**: Integrated development and deployment pipeline

### Configuration Requirements
- **Discord Bot Token**: Required environment variable for bot authentication
- **Roblox Group ID**: Target group for verification and rank management
- **Data Directory**: Local storage for user data and configurations

### Scalability Considerations
- **File-Based Storage**: Simple JSON storage suitable for small to medium deployments
- **Cog Architecture**: Modular design allows easy feature addition and maintenance
- **Async Design**: Non-blocking operations support multiple concurrent users

## Changelog

- June 19, 2025: Advanced Ticket Support System and Live Member Counter
  - Built comprehensive ticket support system with persistent green button interface
  - Implemented never-expiring ticket buttons with custom IDs for reliability
  - Added automatic ticket channel creation with proper permissions for support role ID 1385451612650344523
  - Created live member count display in channel ID 1384582591516119151 with activity percentage
  - Built advanced server statistics with online/offline ratios and visual activity bars
  - Added ticket management for support staff with close ticket functionality
  - Implemented automatic ticket cleanup after 10 seconds of closure confirmation
  - Created ticket setup command for administrators to deploy system in channel ID 1384585517730893864

- June 19, 2025: Fixed Discord Timeout Issues for Hosting Platforms
  - Fixed /reverify command "application did not respond" error on hosting platforms like Render
  - Added immediate response deferral to prevent Discord 3-second timeout issues
  - Implemented comprehensive error handling with detailed logging for debugging
  - Enhanced reverify command with proper async/await flow using followup messages
  - Added graceful fallback error messages for both interaction states
  - Improved hosting platform compatibility with timeout-safe command responses

- June 19, 2025: Real Roblox API Integration and Enhanced Rank System
  - Fixed /reverify command hanging issue with proper followup message flow
  - Integrated real Roblox API authentication using ROBLOX_COOKIE environment variable
  - Implemented actual rank detection from Roblox group membership
  - Fixed rank mapping bug where high ranks defaulted to OR-1
  - Updated nickname formatting: ranks OF-9 and above show as [HQ] Username
  - Lower ranks show as [NATO-CODE] Username (e.g., [OF-3] Username)
  - Enhanced verification process with real profile description checking
  - Improved rank detection logic for unmapped high command positions
  - Added host Roblox avatar display in tryout and training announcements

- June 18, 2025: Initial setup and complete implementation
  - Created Discord bot with military roleplay functionality
  - Implemented /tryout and /training commands with pad number validation (1-9)
  - Built verification system with /verify and /reverify commands
  - Added interactive button-based verification process
  - Integrated NATO rank mapping system for Roblox group "11925205"
  - Configured automatic nickname formatting as [NATO-RANK] Username
  - Fixed privileged intents configuration for easier deployment
  - Bot successfully deployed and running

## User Preferences

Preferred communication style: Simple, everyday language.