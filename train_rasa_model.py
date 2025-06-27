import subprocess
import os
import time

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {str(e)}")
        return False

def main():
    print("=== Starting IPC Data Pipeline ===")
    
    # Step 1: Scrape and update IPC sections
    print("\n1. Scraping and updating IPC sections...")
    if not run_command("python update_ipc_prioritized.py"):
        print("Failed to update IPC sections. Exiting...")
        return
    
    # Step 2: Export to Rasa format
    print("\n2. Exporting data to Rasa format...")
    if not run_command("python export_to_rasa.py"):
        print("Failed to export data to Rasa format. Exiting...")
        return
    
    # Step 3: Train Rasa model
    print("\n3. Training Rasa model...")
    if not run_command("rasa train"):
        print("Failed to train Rasa model. Exiting...")
        return
    
    print("\n=== Pipeline completed successfully! ===")
    print("\nTo start the Rasa server, run: rasa run")
    print("To test the model, run: rasa shell")

if __name__ == "__main__":
    main() 