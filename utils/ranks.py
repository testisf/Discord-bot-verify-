"""
Military rank utilities for NATO rank structure mapping
"""

# NATO rank codes mapping to Roblox group ranks
# This is a mock mapping - in reality this would be based on actual group ranks
RANK_MAPPING = {
    1: "OR-1",    # Private
    2: "OR-2",    # Private First Class
    3: "OR-3",    # Lance Corporal
    4: "OR-4",    # Corporal
    5: "OR-5",    # Sergeant
    6: "OR-6",    # Staff Sergeant
    7: "OR-7",    # Sergeant First Class
    8: "OR-8",    # Master Sergeant
    9: "OR-9",    # Sergeant Major
    10: "WO-1",   # Warrant Officer 1
    11: "WO-2",   # Warrant Officer 2
    12: "WO-3",   # Warrant Officer 3
    13: "WO-4",   # Warrant Officer 4
    14: "WO-5",   # Warrant Officer 5
    15: "OF-1",   # Second Lieutenant
    16: "OF-2",   # First Lieutenant
    17: "OF-3",   # Captain
    18: "OF-4",   # Major
    19: "OF-5",   # Lieutenant Colonel
    20: "OF-6",   # Colonel
    21: "OF-7",   # Brigadier General
    22: "OF-8",   # Major General
    23: "OF-9",   # Lieutenant General
    24: "OF-10",  # General
    25: "OF-11",  # General of the Army
    26: "OF-12",  # Field Marshal
    27: "OF-13",  # Supreme Commander
}

# Full rank names for reference
RANK_NAMES = {
    "OR-1": "Private",
    "OR-2": "Private First Class",
    "OR-3": "Lance Corporal",
    "OR-4": "Corporal",
    "OR-5": "Sergeant",
    "OR-6": "Staff Sergeant",
    "OR-7": "Sergeant First Class",
    "OR-8": "Master Sergeant",
    "OR-9": "Sergeant Major",
    "WO-1": "Warrant Officer 1",
    "WO-2": "Warrant Officer 2",
    "WO-3": "Warrant Officer 3",
    "WO-4": "Warrant Officer 4",
    "WO-5": "Warrant Officer 5",
    "OF-1": "Second Lieutenant",
    "OF-2": "First Lieutenant",
    "OF-3": "Captain",
    "OF-4": "Major",
    "OF-5": "Lieutenant Colonel",
    "OF-6": "Colonel",
    "OF-7": "Brigadier General",
    "OF-8": "Major General",
    "OF-9": "Lieutenant General",
    "OF-10": "General",
    "OF-11": "General of the Army",
    "OF-12": "Field Marshal",
    "OF-13": "Supreme Commander",
}

def get_nato_rank(roblox_rank_id):
    """
    Convert Roblox group rank ID to NATO rank code
    
    Args:
        roblox_rank_id (int): The rank ID from Roblox group
        
    Returns:
        str: NATO rank code (e.g., "OR-1", "OF-3")
    """
    # Check if it's a mapped rank
    if roblox_rank_id in RANK_MAPPING:
        return RANK_MAPPING[roblox_rank_id]
    
    # For higher ranks not in mapping, assume they are high command
    if roblox_rank_id >= 23:  # 23 is OF-9 (Lieutenant General)
        return f"OF-{min(roblox_rank_id - 14, 13)}"  # Cap at OF-13
    
    # Default fallback
    return "OR-1"

def get_rank_name(nato_code):
    """
    Get full rank name from NATO code
    
    Args:
        nato_code (str): NATO rank code (e.g., "OR-1", "OF-3")
        
    Returns:
        str: Full rank name
    """
    return RANK_NAMES.get(nato_code, "Unknown Rank")

def is_officer_rank(nato_code):
    """
    Check if the rank is an officer rank
    
    Args:
        nato_code (str): NATO rank code
        
    Returns:
        bool: True if officer rank, False otherwise
    """
    return nato_code.startswith("OF-")

def is_warrant_officer_rank(nato_code):
    """
    Check if the rank is a warrant officer rank
    
    Args:
        nato_code (str): NATO rank code
        
    Returns:
        bool: True if warrant officer rank, False otherwise
    """
    return nato_code.startswith("WO-")

def is_enlisted_rank(nato_code):
    """
    Check if the rank is an enlisted rank
    
    Args:
        nato_code (str): NATO rank code
        
    Returns:
        bool: True if enlisted rank, False otherwise
    """
    return nato_code.startswith("OR-")

def get_rank_category(nato_code):
    """
    Get the category of the rank
    
    Args:
        nato_code (str): NATO rank code
        
    Returns:
        str: "Enlisted", "Warrant Officer", "Officer", or "Unknown"
    """
    if is_enlisted_rank(nato_code):
        return "Enlisted"
    elif is_warrant_officer_rank(nato_code):
        return "Warrant Officer"
    elif is_officer_rank(nato_code):
        return "Officer"
    else:
        return "Unknown"

def get_rank_initialism(nato_code):
    """
    Get rank initialism for higher ranks (above OR-9)
    
    Args:
        nato_code (str): NATO rank code
        
    Returns:
        str: Rank initialism or full NATO code
    """
    # Map higher ranks to their initialisms
    rank_initialisms = {
        # Warrant Officers
        "WO-1": "WO1",
        "WO-2": "WO2", 
        "WO-3": "WO3",
        "WO-4": "WO4",
        "WO-5": "WO5",
        
        # Officers (only for ranks above General OF-9)
        "OF-10": "GEN",   # General
        "OF-11": "GOA",   # General of the Army
        "OF-12": "FM",    # Field Marshal
        "OF-13": "SC"     # Supreme Commander
    }
    
    return rank_initialisms.get(nato_code, nato_code)

def format_nickname(nato_rank, roblox_username):
    """
    Format the Discord nickname according to military standards
    Use [HQ] for ranks OF-9 and above
    
    Args:
        nato_rank (str): NATO rank code
        roblox_username (str): Roblox username
        
    Returns:
        str: Formatted nickname
    """
    # Use [HQ] for ranks OF-9 and above
    if nato_rank.startswith("OF-"):
        rank_num = int(nato_rank.split("-")[1])
        if rank_num >= 9:
            # Use [HQ] for OF-9 and above
            return f"[HQ] {roblox_username}"
        else:
            return f"[{nato_rank}] {roblox_username}"
    else:
        # All other ranks use NATO code
        return f"[{nato_rank}] {roblox_username}"
