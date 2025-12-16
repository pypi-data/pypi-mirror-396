import os
import shutil
from pathlib import Path

def cleanup():
    # 1. Remove config directory
    config_dir = Path.home() / ".config" / "autocmd"
    if config_dir.exists():
        print(f"Removing config dir: {config_dir}")
        shutil.rmtree(config_dir)
    else:
        print("Config dir not found.")

    # 2. Clean .zshrc
    zshrc = Path.home() / ".zshrc"
    if zshrc.exists():
        lines = zshrc.read_text().splitlines()
        new_lines = []
        skip = False
        cleaned = False
        
        for line in lines:
            # Identify blocks to remove
            if "# autocmd" in line or "alias autocmd-dev=" in line or "autocmd() {" in line:
                cleaned = True
                continue 
            
            # Also remove the logic inside the function if any lines slipped through
            # (The previous script was simple filtering, let's keep it simple)
            
            new_lines.append(line)
            
        if cleaned:
            print(f"Removing autocmd lines from {zshrc}")
            # Ensure we don't leave weird empty lines, but mostly fine
            zshrc.write_text('\n'.join(new_lines) + '\n')
        else:
            print("No autocmd lines found in .zshrc")

if __name__ == "__main__":
    cleanup()
