from src.models.domain import TopItemBase
from src.models.enums import PositionChange


def calculate_position_changes(
    previous_items: list[TopItemBase], current_items: list[TopItemBase]
) -> None:
    """
    Updates the `position_change` field on each item in current_items based on previous_items.

    Rules:
    - UP if current position is higher (e.g., 3 -> 1)
    - DOWN if current position is lower (e.g., 1 -> 3)
    - NEW if the item was not in previous_items
    - None if same position or no previous data -  default so no action needed
    """

    if not previous_items:
        return

    # Map previous items by their unique ID
    item_id_to_previous_positions_map = {
        item.item_id: item.position for item in previous_items
    }

    for item in current_items:
        previous_position = item_id_to_previous_positions_map.get(item.item_id)

        if previous_position is None:
            item.position_change = PositionChange.NEW
        elif item.position < previous_position:
            item.position_change = PositionChange.UP
        elif item.position > previous_position:
            item.position_change = PositionChange.DOWN
