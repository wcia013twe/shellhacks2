import sys

for line in sys.stdin:
    if line.strip() == "ping":
        print("pong from python", flush=True)