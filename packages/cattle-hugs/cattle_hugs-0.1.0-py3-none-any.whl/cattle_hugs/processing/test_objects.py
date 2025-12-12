from unittest.mock import MagicMock
import pytest
from .objects import determine_interaction_type


@pytest.mark.parametrize(
    "activity,expected",
    [
        (MagicMock(type="Like", content=None), "like"),
        (MagicMock(type="Like", content="🐮"), "emoji_reaction"),
        (MagicMock(type="Announce"), "share"),
    ],
)
def test_determine_interaction_type(activity, expected):
    result = determine_interaction_type(activity)

    assert str(result) == expected
