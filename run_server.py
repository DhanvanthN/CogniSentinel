#!/usr/bin/env python
"""
Run Server Script for CogniSentinel Mental Health Chatbot

This script starts the Rasa server and connects it to the frontend.
It provides a convenient way to start all necessary components.
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

# Define colors for terminal output
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m'
}

# Define paths
BASE_DIR = Path(__file__).resolve().parent
ACTIONS_SERVER_PORT = 5055
RASA_SERVER_PORT = 5005
FRONTEND_PORT = 8000

# Process holders
processes = []

def print_colored(message, color='GREEN', bold=False):
    """Print colored messages to the terminal."""
    if bold:
        print(f"{COLORS['BOLD']}{COLORS[color]}{message}{COLORS['ENDC']}")
    else:
        print(f"{COLORS[color]}{message}{COLORS['ENDC']}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import rasa
        import flair
        print_colored("✓ All dependencies are installed.", "GREEN")
        return True
    except ImportError as e:
        print_colored(f"✗ Missing dependency: {e}", "RED")
        print_colored("Please install required packages using: pip install rasa flair", "YELLOW")
        return False

def start_actions_server():
    """Start the Rasa Actions Server."""
    print_colored("Starting Rasa Actions Server...", "BLUE")
    cmd = [sys.executable, "-m", "rasa", "run", "actions", "--port", str(ACTIONS_SERVER_PORT)]
    process = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(process)
    print_colored(f"✓ Rasa Actions Server started on port {ACTIONS_SERVER_PORT}", "GREEN")
    return process

def start_rasa_server():
    """Start the Rasa Server."""
    print_colored("Starting Rasa Server...", "BLUE")
    cmd = [sys.executable, "-m", "rasa", "run", 
           "--enable-api", 
           "--cors", "*", 
           "--port", str(RASA_SERVER_PORT),
           "--endpoints", "endpoints.yml",
           "--credentials", "credentials.yml"]
    process = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(process)
    print_colored(f"✓ Rasa Server started on port {RASA_SERVER_PORT}", "GREEN")
    return process

def start_frontend_server():
    """Start a simple HTTP server for the frontend."""
    print_colored("Starting Frontend Server...", "BLUE")
    cmd = [sys.executable, "-m", "http.server", str(FRONTEND_PORT)]
    process = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes.append(process)
    print_colored(f"✓ Frontend Server started on port {FRONTEND_PORT}", "GREEN")
    return process

def open_browser():
    """Open the browser with the frontend."""
    url = f"http://localhost:{FRONTEND_PORT}/new_interface.html"
    print_colored(f"Opening browser at {url}", "BLUE")
    webbrowser.open(url)

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shut down all processes."""
    print_colored("\nShutting down all servers...", "YELLOW")
    for process in processes:
        process.terminate()
    print_colored("All servers have been stopped.", "GREEN")
    sys.exit(0)

def main():
    """Main function to start all servers."""
    print_colored("=== CogniSentinel Mental Health Chatbot ===\n", "BLUE", bold=True)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start all servers
        start_actions_server()
        time.sleep(3)  # Wait for actions server to start
        
        start_rasa_server()
        time.sleep(5)  # Wait for Rasa server to start
        
        start_frontend_server()
        time.sleep(2)  # Wait for frontend server to start
        
        # Open browser
        open_browser()
        
        print_colored("\nAll servers are running. Press Ctrl+C to stop.", "GREEN", bold=True)
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print_colored(f"Error: {e}", "RED")
        signal_handler(None, None)

if __name__ == "__main__":
    main()