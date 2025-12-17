import sys
from .verify import run as verify_run
from .apps.cli import main_menu

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_run()
    else:
        # Default behavior: Launch Interactive Suite
        main_menu()

if __name__ == "__main__":
    main()
