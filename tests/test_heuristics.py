import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import heuristics


def test_heuristic_weights():
    assert heuristics.FP_WEIGHT == 0.7
    assert heuristics.TAG_WEIGHT == 0.2
    assert heuristics.FUZZY_WEIGHT == 0.1
