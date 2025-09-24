import urllib.request, sys

URL = "http://84.62.167.117:8501/ping"

def main():
    try:
        with urllib.request.urlopen(URL, timeout=3) as r:
            print(f"OK {r.status}: {r.read().decode().strip()}")
            return 0
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

