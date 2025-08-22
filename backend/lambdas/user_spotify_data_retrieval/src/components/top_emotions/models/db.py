from datetime import date
from src.shared.models.db import TopItemDBMixin
from src.components.top_emotions.models.domain import TopEmotion
from src.shared.spotify.enums import TimeRange
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.db import Base


class TopEmotionDB(TopItemDBMixin, Base):
    __tablename__ = "top_emotion"

    emotion_id: Mapped[str] = mapped_column(String, primary_key=True)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)

    @property
    def item_id(self) -> str:
        return self.emotion_id
    
    @classmethod
    def from_top_emotion(cls, user_id: str, top_emotion: TopEmotion, time_range: TimeRange, collection_date: date) -> "TopEmotionDB":
        return cls(
            user_id=user_id,
            emotion_id=top_emotion.id,
            time_range=time_range,
            collection_date=collection_date,
            position=top_emotion.position,
            position_change=top_emotion.position_change,
        )
