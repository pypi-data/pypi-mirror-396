import sys
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from types_boto3_logs import CloudWatchLogsClient
    from types_boto3_logs.type_defs import (
        EntityTypeDef,
        InputLogEventTypeDef,
        PutLogEventsRequestTypeDef,
    )

if sys.version_info <= (3, 10):
    from datetime import timezone
    UTC = timezone.utc
else:
    from datetime import UTC


class AWSLogClient:
    def __init__(self, client: "CloudWatchLogsClient") -> None:
        self.client = client

    # region: Composition
    def __getattr__(self, name: str): return getattr(self.client, name)
    # endregion

    def try_create_log_group(self, log_group_name: str):
        try:
            self.client.create_log_group(logGroupName=log_group_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def try_create_log_stream(self, log_group_name: str, log_stream_name: str):
        try:
            self.client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def put_log_events(
        self,
        log_group_name: str,
        log_stream_name: str,
        log_events: Sequence["InputLogEventTypeDef"],
        sequence_token: Optional[str] = None,
        key_attributes: Optional[Mapping[str, str]] = None,
        attributes: Optional[Mapping[str, str]] = None,
    ):
        """
        The `PutLogEvents` operation writes log events to a log stream in a log group.
        
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_log_events)
        """
        kwargs: "PutLogEventsRequestTypeDef" = {
            "logGroupName": log_group_name,
            "logStreamName": log_stream_name,
            "logEvents": log_events,
        }
        entity: "EntityTypeDef" = {}
        if sequence_token:
            kwargs["sequenceToken"] = sequence_token
        if key_attributes:
            entity["keyAttributes"] = key_attributes
        if attributes:
            entity["attributes"] = attributes

        if entity:
            kwargs["entity"] = entity
            
        return self.client.put_log_events(**kwargs)
    
    def put_log_event(
        self,
        log_group_name: str,
        log_stream_name: str,
        message: str,
        timestamp: Optional[datetime] = None,
        key_attributes: Optional[Mapping[str, str]] = None,
        attributes: Optional[Mapping[str, str]] = None,
    ):
        """
        Put a single log event into the log stream.
        """
        timestamp = timestamp or datetime.now(UTC)
        return self.put_log_events(
            log_group_name=log_group_name,
            log_stream_name=log_stream_name,
            log_events=[{
                "message": message,
                "timestamp": int(timestamp.timestamp()),
            }],
            key_attributes=key_attributes,
            attributes=attributes,
        )
