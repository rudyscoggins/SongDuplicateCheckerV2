from pathlib import Path
import sys

# Ensure src is on path to import the real sdc package
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

from sdc.__main__ import main

if __name__ == '__main__':
    main()
