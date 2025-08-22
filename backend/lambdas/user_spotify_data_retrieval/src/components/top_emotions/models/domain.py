from src.shared.models.domain import TopItem


class TopEmotion(TopItem):
    name: str
    percentage: float
    