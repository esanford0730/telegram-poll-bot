import subprocess
import time

while True:
    try:
        subprocess.run(["python", "session_poll_bot.py"])
    except Exception as e:
        print(f"Bot crashed with error: {e}. Restarting...")
    time.sleep(0.5)