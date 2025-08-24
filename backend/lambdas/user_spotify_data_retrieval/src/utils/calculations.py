from backend.lambdas.user_spotify_data_retrieval.src.models.dto import TopItemBase
from backend.lambdas.user_spotify_data_retrieval.src.models.enums import PositionChange


def calculate_position_changes(current_items: list[TopItemBase], previous_items: list[TopItemBase]) -> None:
    """
    Updates the `position_change` field on each item in current_items based on previous_items.

    Rules:
    - UP if current position is higher (e.g., 3 -> 1)
    - DOWN if current position is lower (e.g., 1 -> 3)
    - NEW if the item was not in previous_items
    - None if same position or no previous data -  default so no action needed
    """
    
    if not previous_items:
        # No previous data; leave all position_change as None
        return

    # Map previous items by their unique ID
    prev_positions = {item.get_unique_id(): item.position for item in previous_items}

    for item in current_items:
        prev_pos = prev_positions.get(item.get_unique_id())

        if prev_pos is None:
            item.position_change = PositionChange.NEW
        elif item.position < prev_pos:
            item.position_change = PositionChange.UP
        elif item.position > prev_pos:
            item.position_change = PositionChange.DOWN
            