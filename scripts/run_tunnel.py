"""Auto-restarting tunnel supervisor for BuildLens 4D.
Keeps the public HTTPS tunnel active and reconnects immediately if the remote socket resets.
"""
import subprocess
import time
import sys

def main():
    print("[Tunnel Supervisor] Initializing BuildLens 4D Tunnel...")
    while True:
        try:
            print("[Tunnel Supervisor] Spawning localtunnel on port 8000 (subdomain: buildlens4d)...")
            proc = subprocess.Popen(
                ["cmd.exe", "/c", "npx -y localtunnel --port 8000 --subdomain buildlens4d"],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            proc.wait()
            print(f"[Tunnel Supervisor] Tunnel process exited with code {proc.returncode}. Reconnecting in 3s...")
        except KeyboardInterrupt:
            print("[Tunnel Supervisor] Stopping supervisor cleanly.")
            break
        except Exception as e:
            print(f"[Tunnel Supervisor] Error: {e}. Reconnecting in 5s...")
            time.sleep(5)
        time.sleep(3)

if __name__ == "__main__":
    main()
