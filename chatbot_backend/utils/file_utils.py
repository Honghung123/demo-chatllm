from pathlib import Path

def get_root_path() -> str:
    # Get the root path of the project ("/chatbot_backend/")
    return str(Path(__file__).resolve().parent.parent)