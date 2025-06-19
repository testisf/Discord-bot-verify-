"""
Roblox API client for group rank verification
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RobloxAPI:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.base_url = "https://groups.roblox.com/v1"
        self.users_url = "https://users.roblox.com/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Cookie': f'.ROBLOSECURITY={self.cookie}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user info by username"""
        try:
            if not self.session:
                return None
            url = f"{self.users_url}/usernames/users"
            data = {
                "usernames": [username],
                "excludeBannedUsers": True
            }
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('data') and len(result['data']) > 0:
                        return result['data'][0]
                return None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_groups(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's group memberships"""
        try:
            if not self.session:
                return None
            url = f"{self.base_url}/users/{user_id}/groups/roles"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting user groups: {e}")
            return None
    
    async def get_user_rank_in_group(self, user_id: int, group_id: int) -> Optional[Dict[str, Any]]:
        """Get user's rank in specific group"""
        try:
            groups_data = await self.get_user_groups(user_id)
            if groups_data and 'data' in groups_data:
                for group in groups_data['data']:
                    if group['group']['id'] == group_id:
                        return {
                            'rank_id': group['role']['rank'],
                            'rank_name': group['role']['name'],
                            'group_id': group_id,
                            'user_id': user_id
                        }
            return None
        except Exception as e:
            logger.error(f"Error getting user rank in group: {e}")
            return None
    
    async def get_user_description(self, user_id: int) -> Optional[str]:
        """Get user's profile description"""
        try:
            if not self.session:
                return None
            url = f"{self.users_url}/users/{user_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('description', '')
                return None
        except Exception as e:
            logger.error(f"Error getting user description: {e}")
            return None
    
    async def get_user_avatar_url(self, user_id: int) -> Optional[str]:
        """Get user's avatar image URL"""
        try:
            if not self.session:
                return None
            url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('data') and len(result['data']) > 0:
                        return result['data'][0].get('imageUrl')
                return None
        except Exception as e:
            logger.error(f"Error getting user avatar: {e}")
            return None
    
    async def verify_user_code(self, username: str, verification_code: str, group_id: int) -> Optional[Dict[str, Any]]:
        """Verify user has the code in their description and get their rank"""
        try:
            # Get user info
            user_info = await self.get_user_by_username(username)
            if not user_info:
                return None
            
            user_id = user_info['id']
            
            # Check if verification code is in description
            description = await self.get_user_description(user_id)
            if not description or verification_code not in description:
                return {
                    'success': False,
                    'error': 'Verification code not found in profile description'
                }
            
            # Get user's rank in the group
            rank_info = await self.get_user_rank_in_group(user_id, group_id)
            if not rank_info:
                return {
                    'success': False,
                    'error': 'User not found in the specified group'
                }
            
            return {
                'success': True,
                'user_id': user_id,
                'username': user_info['name'],
                'display_name': user_info.get('displayName', user_info['name']),
                'rank_id': rank_info['rank_id'],
                'rank_name': rank_info['rank_name'],
                'group_id': group_id
            }
            
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }

async def verify_roblox_user(cookie: str, username: str, verification_code: str, group_id: int) -> Optional[Dict[str, Any]]:
    """Convenience function to verify a Roblox user"""
    async with RobloxAPI(cookie) as api:
        return await api.verify_user_code(username, verification_code, group_id)