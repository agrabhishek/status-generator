"""
Preset Storage Management
==========================
Save/load/delete user presets for quick reuse.

Generated: 2025-10-19 19:02:26
"""

import json
import os
import streamlit as st
from typing import Optional, List, Dict


PRESETS_FILE = "jira_presets.json"


def save_criteria(preset_name: str, criteria: Dict) -> bool:
    """
    Save preset to JSON file.
    
    REQUIREMENT: Save and Load Criteria
    Stores user preferences for quick reuse.
    """
    try:
        if os.path.exists(PRESETS_FILE):
            with open(PRESETS_FILE, 'r') as f:
                presets = json.load(f)
        else:
            presets = {}
        
        presets[preset_name] = criteria
        
        with open(PRESETS_FILE, 'w') as f:
            json.dump(presets, f, indent=2)
        
        st.success(f"✅ Saved: {preset_name}")
        return True
    except Exception as e:
        st.error(f"❌ Save failed: {e}")
        return False


def load_criteria(preset_name: str) -> Optional[Dict]:
    """Load preset from JSON file"""
    if not os.path.exists(PRESETS_FILE):
        return None
    
    try:
        with open(PRESETS_FILE, 'r') as f:
            presets = json.load(f)
        return presets.get(preset_name)
    except Exception:
        return None


def get_all_presets() -> List[str]:
    """Get all preset names"""
    if not os.path.exists(PRESETS_FILE):
        return []
    
    try:
        with open(PRESETS_FILE, 'r') as f:
            presets = json.load(f)
        return list(presets.keys())
    except Exception:
        return []


def delete_preset(preset_name: str) -> None:
    """Delete preset from JSON file"""
    try:
        if not os.path.exists(PRESETS_FILE):
            return
        
        with open(PRESETS_FILE, 'r') as f:
            presets = json.load(f)
        
        if preset_name in presets:
            del presets[preset_name]
            
            with open(PRESETS_FILE, 'w') as f:
                json.dump(presets, f, indent=2)
            
            st.success(f"✅ Deleted: {preset_name}")
    except Exception as e:
        st.error(f"❌ Delete failed: {e}")
