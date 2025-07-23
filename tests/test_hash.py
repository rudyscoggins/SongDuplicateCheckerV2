import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hash import path_hash


def test_path_hash_deterministic():
    p = Path('a/b/c.mp3')
    assert path_hash(p) == 'ca92091e97794429e492680080d17066653c96e3'
