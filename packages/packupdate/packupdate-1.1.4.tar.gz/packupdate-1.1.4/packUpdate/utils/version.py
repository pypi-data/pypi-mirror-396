"""
Version comparison utilities
"""
import re

def is_minor_update(current, latest):
    """Check if the update is a minor version update (same major version)."""
    current_clean = re.sub(r'[^0-9.]', '', current)
    latest_clean = re.sub(r'[^0-9.]', '', latest)
    
    current_parts = [int(x) for x in current_clean.split('.') if x.isdigit()]
    latest_parts = [int(x) for x in latest_clean.split('.') if x.isdigit()]
    
    if len(current_parts) < 2 or len(latest_parts) < 2:
        return False
    
    # Same major version, different minor or patch
    return (current_parts[0] == latest_parts[0] and 
            (len(current_parts) < 2 or len(latest_parts) < 2 or 
             current_parts[1] != latest_parts[1] or 
             (len(current_parts) > 2 and len(latest_parts) > 2 and current_parts[2] != latest_parts[2])))
