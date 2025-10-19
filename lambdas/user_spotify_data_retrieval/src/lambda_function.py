import asyncio

from aws_lambda_typing import context as context_

from src.core.config import Settings
from src.models.event import LambdaEvent, parse_event
from src.services.data_collection_service import DataCollectionService

settings = Settings()
data_collection_service = DataCollectionService(settings)


def handler(event: LambdaEvent, _: context_.Context) -> None:
    try:
        config = parse_event(event)

        asyncio.run(
            data_collection_service.collect_user_data(
                access_token=config.access_token,
                time_range=config.time_range,
                collection_date=config.collection_date,
            )
        )
    except Exception as e:
        print(f"Lambda execution failed: {str(e)}")
        raise
