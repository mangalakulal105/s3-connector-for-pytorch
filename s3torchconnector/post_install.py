import subprocess

def main():
    result = subprocess.run(['echo hacked'], capture_output=True, text=True)
    print(f"Current user: {result.stdout.strip()}")

if __name__ == '__main__':
    main()
