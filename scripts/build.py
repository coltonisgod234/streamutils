import os
import sys
import subprocess
import importlib.resources
import emoji

def get_resource_path():
    with importlib.resources.path(emoji, "unicode_codes/emoji.json") as path:
        p = path

    return p

# Get the path to the emoji.json file using importlib.resources

# Function to run the pyinstaller command programmatically
def run_pyinstaller():
    # Get the path to the emoji.json resource
    emoji_json_path = get_resource_path()

    # Construct the PyInstaller command
    pyinstaller_command = [
        'pyinstaller',
        '--onefile',
        '--add-data', f"{emoji_json_path}:emoji/unicode_codes",  # Adding the emoji.json file
        '../src/ttsfront.py'  # Your main Python script
    ]

    # Run PyInstaller with the command
    subprocess.run(pyinstaller_command, check=True)

if __name__ == "__main__":
    run_pyinstaller()
