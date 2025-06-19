import subprocess
import time
import sys

def run_bot():
    while True:
        try:
            result = subprocess.run(["python", "session_poll_bot.py"])
            exit_code = result.returncode

            if exit_code == 0:
                print("Bot exited normally. Restarting...")
            else:
                print(f"Bot exited with code {exit_code}. Restarting...")

        except Exception as e:
            print(f"Bot crashed with exception: {e}. Restarting...")

        time.sleep(0.5)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("Launcher manually interrupted. Exiting cleanly.")
        sys.exit(0)