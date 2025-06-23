from pathlib import Path

def get_root_path() -> str:
    # Get the current file path     
    return str(Path(__file__).resolve().parent .parent)