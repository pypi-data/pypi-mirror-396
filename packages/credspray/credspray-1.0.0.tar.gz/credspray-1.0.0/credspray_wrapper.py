#!/usr/bin/env python3
"""
CredSpray wrapper - Executes the credspray.sh bash script
"""
import subprocess
import sys
import os

def main():
    """Main entry point for credspray command"""
    # Get the directory where this script is installed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'credspray.sh')
    
    # Check if script exists
    if not os.path.exists(script_path):
        print(f"Error: credspray.sh not found at {script_path}")
        sys.exit(1)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    # Run the bash script with all arguments passed to this command
    try:
        result = subprocess.run(['bash', script_path] + sys.argv[1:])
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error running credspray: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
