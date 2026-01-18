import subprocess
import time
import os
import sys

def start_backend():
    print("Starting Backend (Uvicorn)...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--reload", "--port", "8000"],
        cwd=os.getcwd(),
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
            
def main():
    cleanup_ports()
    time.sleep(2) # Wait for release
    
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
