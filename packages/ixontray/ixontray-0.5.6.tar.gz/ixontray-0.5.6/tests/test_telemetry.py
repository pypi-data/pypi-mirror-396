# ------------------------------------------------------------------
# Copyright (C) Smart Robotics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly
# prohibited. All information contained herein is, and remains
# the property of Smart Robotics.
# ------------------------------------------------------------------
from functools import reduce

import numpy

from ixontray.telemetry import FunctionCall


def test_function_call_addition() -> None:
    """Test adding two Function call objects."""

    durations = [2.1, 3.1, 5.1, 2.1, 5.1, 7.1]
    calls = [FunctionCall(name=f"fun_{i}", duration=d) for i, d in enumerate(durations)]

    result = reduce(lambda x, y: x + y, calls)

    assert result.duration == numpy.average(durations), "Averages should match"
    assert result.min_duration == min(durations), "Min should match"
    assert result.max_duration == max(durations), "Max should match"


def test_function_call() -> None:
    """Test creation of function call."""
    expected_duration = 10
    fc = FunctionCall(name="fun_1", duration=expected_duration)
    assert fc.duration == expected_duration
    assert fc.min_duration == expected_duration
    assert fc.max_duration == expected_duration
