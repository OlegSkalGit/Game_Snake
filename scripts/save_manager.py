"""
Save Manager for 3D Snake Adventure.
Handles persistent saving and loading of game progression (unlocked levels and high scores)
to save_data.json.
"""
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_FILE_PATH = os.path.join(PROJECT_ROOT, "save_data.json")

def load_save_data():
    """Loads saved game progression or returns default state."""
    default_data = {
        "unlocked_world": 0,      # Index of highest unlocked world (0 = World 1 unlocked)
        "high_score": 0,
        "completed_worlds": []
    }
    if os.path.exists(SAVE_FILE_PATH):
        try:
            with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "unlocked_world": max(0, min(17, int(data.get("unlocked_world", 0)))),
                    "high_score": max(0, int(data.get("high_score", 0))),
                    "completed_worlds": list(data.get("completed_worlds", []))
                }
        except Exception as e:
            print("Error loading save data, using defaults:", e)
    return default_data

def save_game_data(unlocked_world, high_score=0, completed_worlds=None):
    """Saves game progression to save_data.json."""
    if completed_worlds is None:
        completed_worlds = []
    data = {
        "unlocked_world": max(0, min(17, int(unlocked_world))),
        "high_score": max(0, int(high_score)),
        "completed_worlds": list(completed_worlds)
    }
    try:
        with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("Error writing save data:", e)
        return False
