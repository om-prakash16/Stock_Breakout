import subprocess
import time
import os
import sys
from pathlib import Path

def start_backend():
    print("Starting Backend (Uvicorn)...")
    backend_dir = os.path.join(os.getcwd(), "backend")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--reload", "--port", "8000"],
        cwd=backend_dir,
        shell=True
    )

def start_frontend():
    print("Starting Frontend (Next.js)...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )

def cleanup_ports():
    """Kills processes running on ports 8000 (Backend) and 3000 (Frontend)."""
    print("Checking for existing processes on ports 8000 and 3000...")
    for port in [8000, 3000]:
        try:
            # Find PID using netstat
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True).decode()
            if output:
                lines = output.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) > 0:
                        print(f"Killing process {pid} on port {port}...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass # No process found

def check_and_seed_data():
    """
    Checks if essential data exists. If not, runs initial data generation.
    """
    backend_dir = os.path.join(os.getcwd(), "backend")
    processed_dir = Path(backend_dir) / "data" / "processed"
    universe_file = processed_dir / "universe.parquet"

    if not universe_file.exists():
        print("\n[!] Initial Setup: Data not found.")
        print("--- Step 1: Building Stock Universe (This is quick)...")
        
        # Run Phase 1 (Universe) Synchronously
        try:
            subprocess.run(
                [sys.executable, "main.py", "--mode", "universe"],
                cwd=backend_dir,
                check=True
            )
            print("--- Universe built successfully.")
        except subprocess.CalledProcessError:
            print("[x] Failed to build universe. Application may be empty.")
            return

        print("\n--- Step 2: Starting Background Historical Data Fetch...")
        print("    (This creates a background process. Data will populate in 5-10 mins.)")
        print("    (You can use the dashboard immediately.)")
        
        # Run Phase 2 (History) Asynchronously
        # We use Popen to let it run in background without blocking this script
        creation_flags = 0
        if os.name == 'nt':
            # Detach process on Windows (CREATE_NEW_CONSOLE = 0x00000010)
            creation_flags = 0x00000010
            
        subprocess.Popen(
            [sys.executable, "main.py", "--mode", "history"],
            cwd=backend_dir,
            creationflags=creation_flags
        )
        print("--- Background fetch initiated.\n")
    else:
        print("[+] Data checks passed. Starting servers...\n")
            
def main():
    cleanup_ports()
    time.sleep(2) # Wait for release
    
    check_and_seed_data()
    
    backend = start_backend()
    frontend = start_frontend()
    
    try:
        while True:
            time.sleep(1)
            
            # Check Backend
            if backend.poll() is not None:
                print(f"Backend crashed (Exit Code: {backend.returncode}). Restarting...")
                backend = start_backend()
                
            # Check Frontend
            if frontend.poll() is not None:
                print(f"Frontend crashed (Exit Code: {frontend.returncode}). Restarting...")
                frontend = start_frontend()
                
    except KeyboardInterrupt:
        print("Stopping servers...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
