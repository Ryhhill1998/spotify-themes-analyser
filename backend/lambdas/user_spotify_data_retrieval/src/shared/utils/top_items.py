from src.shared.models.domain import TopItem


def calculate_and_populate_position_changes(previous_top_items: list[TopItem], current_top_items: list[TopItem]) -> None:
    previous_item_id_to_position_map = {artist.id: artist.position for artist in previous_top_items}

    for current_item in current_top_items:
        previous_position = previous_item_id_to_position_map.get(current_item.id)
        current_position = current_item.position

        if previous_position is not None:
            if current_position < previous_position:
                current_item.position_change = "up"
            elif current_position > previous_position:
                current_item.position_change = "down"
            else:
                current_item.position_change = None
        else:
            current_item.position_change = "new"
            