import datetime
import json
import pydantic
import typing
from aws_lambda_typing import events

from src.models.enums import TimeRange


class RunConfig(pydantic.BaseModel):
    """Configuration for running the data collection pipeline"""

    access_token: str
    time_range: typing.Annotated[
        TimeRange, pydantic.BeforeValidator(lambda v: TimeRange(v))
    ]
    collection_date: typing.Annotated[
        datetime.date,
        pydantic.BeforeValidator(lambda v: datetime.date.fromisoformat(v)),
    ] = pydantic.Field(default_factory=datetime.date.today)


class ParseEventException(Exception):
    """Exception raised when event parsing fails"""

    pass


# AWS Lambda event types
SQSEvent = events.SQSEvent
DirectEvent = typing.Dict[str, typing.Any]
LambdaEvent = typing.Union[SQSEvent, DirectEvent]


def parse_event(event: LambdaEvent) -> RunConfig:
    """Parse Lambda event and return RunConfig"""
    try:
        config_data = event

        if "Records" in event and len(event["Records"]) > 0:
            message_body = event["Records"][0]["body"]
            config_data = json.loads(message_body)

        return RunConfig.model_validate(config_data)
    except (json.JSONDecodeError, pydantic.ValidationError) as e:
        raise ParseEventException(f"Failed to parse event: {str(e)}") from e
