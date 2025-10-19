import pytest
from unittest.mock import Mock

from src.models.enums import PositionChange
from src.utils.calculations import calculate_position_changes


class MockTopItem:
    """Mock implementation of TopItemBase for testing"""

    def __init__(self, item_id: str, position: int):
        self.item_id = item_id
        self.position = position
        self.position_change = None


def test_no_previous_items_returns_early():
    """Test that function returns early when no previous items provided"""
    current_items = [MockTopItem("item1", 1), MockTopItem("item2", 2)]

    calculate_position_changes([], current_items)

    # Should not modify position_change when no previous items
    assert current_items[0].position_change is None
    assert current_items[1].position_change is None


def test_all_new_items():
    """Test that all items are marked as NEW when none existed before"""
    previous_items = [MockTopItem("old1", 1), MockTopItem("old2", 2)]
    current_items = [
        MockTopItem("new1", 1),
        MockTopItem("new2", 2),
        MockTopItem("new3", 3),
    ]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.NEW
    assert current_items[1].position_change == PositionChange.NEW
    assert current_items[2].position_change == PositionChange.NEW


def test_position_moved_up():
    """Test that items moving to higher positions are marked as UP"""
    previous_items = [
        MockTopItem("item1", 3),
        MockTopItem("item2", 1),
        MockTopItem("item3", 2),
    ]
    current_items = [
        MockTopItem("item1", 1),  # 3 -> 1 (UP)
        MockTopItem("item2", 2),  # 1 -> 2 (DOWN)
        MockTopItem("item3", 3),  # 2 -> 3 (DOWN)
    ]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.UP
    assert current_items[1].position_change == PositionChange.DOWN
    assert current_items[2].position_change == PositionChange.DOWN


def test_position_moved_down():
    """Test that items moving to lower positions are marked as DOWN"""
    previous_items = [
        MockTopItem("item1", 1),
        MockTopItem("item2", 2),
        MockTopItem("item3", 3),
    ]
    current_items = [
        MockTopItem("item1", 3),  # 1 -> 3 (DOWN)
        MockTopItem("item2", 1),  # 2 -> 1 (UP)
        MockTopItem("item3", 2),  # 3 -> 2 (UP)
    ]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.DOWN
    assert current_items[1].position_change == PositionChange.UP
    assert current_items[2].position_change == PositionChange.UP


def test_same_position_unchanged():
    """Test that items with same position remain unchanged (None)"""
    previous_items = [
        MockTopItem("item1", 1),
        MockTopItem("item2", 2),
        MockTopItem("item3", 3),
    ]
    current_items = [
        MockTopItem("item1", 1),  # Same position
        MockTopItem("item2", 2),  # Same position
        MockTopItem("item3", 3),  # Same position
    ]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change is None
    assert current_items[1].position_change is None
    assert current_items[2].position_change is None


def test_mixed_changes():
    """Test complex scenario with mixed position changes"""
    previous_items = [
        MockTopItem("item1", 1),
        MockTopItem("item2", 2),
        MockTopItem("item3", 3),
        MockTopItem("item4", 4),
    ]
    current_items = [
        MockTopItem("item1", 2),  # 1 -> 2 (DOWN)
        MockTopItem("item2", 1),  # 2 -> 1 (UP)
        MockTopItem("item5", 3),  # NEW item
        MockTopItem("item4", 4),  # 4 -> 4 (SAME)
    ]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.DOWN
    assert current_items[1].position_change == PositionChange.UP
    assert current_items[2].position_change == PositionChange.NEW
    assert current_items[3].position_change is None


def test_empty_current_items():
    """Test that function handles empty current items gracefully"""
    previous_items = [MockTopItem("item1", 1)]
    current_items = []

    # Should not raise an exception
    calculate_position_changes(previous_items, current_items)


def test_duplicate_item_ids_in_previous():
    """Test behavior when previous items have duplicate IDs (edge case)"""
    previous_items = [
        MockTopItem("item1", 1),
        MockTopItem("item1", 2),  # Duplicate ID - should use last occurrence
    ]
    current_items = [MockTopItem("item1", 3)]  # Should compare against position 2

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.DOWN


def test_large_position_numbers():
    """Test with large position numbers to ensure no overflow issues"""
    previous_items = [MockTopItem("item1", 1000)]
    current_items = [MockTopItem("item1", 999)]

    calculate_position_changes(previous_items, current_items)

    assert current_items[0].position_change == PositionChange.UP
