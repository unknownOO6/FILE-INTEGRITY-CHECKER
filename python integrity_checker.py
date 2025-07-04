import hashlib
import os
import json
import time
from datetime import datetime


BASELINE_FILE = "hashes.json"

def calculate_hash(filepath):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
         
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Warning: File not found during hashing: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def get_hashes_from_directory(directory):
    """Walks through a directory and calculates hashes for all files."""
    hashes = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            
            if filename == BASELINE_FILE:
                continue
            filepath = os.path.join(root, filename)
            file_hash = calculate_hash(filepath)
            if file_hash:
                
                relative_path = os.path.relpath(filepath, directory)
                hashes[relative_path] = file_hash
    return hashes

def create_baseline(directory):
    """Creates a baseline of file hashes for a directory."""
    print(f"Creating a new baseline for '{directory}'...")
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    hashes = get_hashes_from_directory(directory)
    
    baseline_data = {
        "timestamp": datetime.now().isoformat(),
        "directory": os.path.abspath(directory),
        "hashes": hashes
    }

    try:
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline_data, f, indent=4)
        print(f"Successfully created baseline in '{BASELINE_FILE}'.")
        print(f"Monitored {len(hashes)} files.")
    except Exception as e:
        print(f"Error writing baseline file: {e}")


def check_integrity(directory):
    """Checks the integrity of a directory against the stored baseline."""
    print(f"Checking integrity for '{directory}'...")
    if not os.path.exists(BASELINE_FILE):
        print("Error: Baseline file not found. Please create a baseline first (Option 1).")
        return

    try:
        with open(BASELINE_FILE, "r") as f:
            baseline_data = json.load(f)
        baseline_hashes = baseline_data.get("hashes", {})
        baseline_dir = baseline_data.get("directory")
        print(f"Baseline from {baseline_data.get('timestamp')} for directory '{baseline_dir}'")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading baseline file: {e}")
        return

    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    current_hashes = get_hashes_from_directory(directory)

    modified_files = []
    new_files = []
    
 
    for filepath, current_hash in current_hashes.items():
        if filepath not in baseline_hashes:
            new_files.append(filepath)
        elif baseline_hashes[filepath] != current_hash:
            modified_files.append(filepath)


    deleted_files = [
        filepath for filepath in baseline_hashes 
        if filepath not in current_hashes
    ]

    print("\n--- Integrity Check Report ---")
    if not modified_files and not new_files and not deleted_files:
        print("✅ SUCCESS: All files are verified. No changes detected.")
    else:
        if modified_files:
            print(f"\n🚨 MODIFIED FILES ({len(modified_files)}):")
            for f in modified_files:
                print(f"  - {f}")
        
        if new_files:
            print(f"\n✨ NEW FILES ({len(new_files)}):")
            for f in new_files:
                print(f"  - {f}")

        if deleted_files:
            print(f"\n🗑️ DELETED FILES ({len(deleted_files)}):")
            for f in deleted_files:
                print(f"  - {f}")
    print("----------------------------\n")


def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n--- Directory Integrity Monitor ---")
        print("1. Create a new baseline for a directory")
        print("2. Check integrity of a directory")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            directory = input("Enter the path of the directory to monitor: ")
            create_baseline(directory)
        elif choice == '2':
            directory = input("Enter the path of the directory to check: ")
            check_integrity(directory)
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()
