from typing import TYPE_CHECKING

from typing_extensions import NotRequired, TypedDict, Unpack

if TYPE_CHECKING:
    from types_boto3_sqs import SQSServiceResource
    from types_boto3_sqs.type_defs import SendMessageRequestTypeDef


class SendMessage(TypedDict):
    message_body: str
    message_group_id: NotRequired[str]
    message_deduplication_id: NotRequired[str]


class SQSResource:
    def __init__(self, resource: "SQSServiceResource") -> None:
        self.resource = resource
        self.client = resource.meta.client

    # region: Composition
    def Message(self, queue_url: str, receipt_handle: str): return self.resource.Message(queue_url, receipt_handle)  # NOSONAR
    def Queue(self, url: str): return self.resource.Queue(url)  # NOSONAR
    def __getattr__(self, name: str): return getattr(self.resource, name)
    # endregion

    def send_message(self, queue_url: str, **kwargs: Unpack[SendMessage]):
        """
        Sends a message to the specified SQS queue.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs/client/send_message.html)
        [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_sqs/client/#sendmessage-method)
        """
        request_body: "SendMessageRequestTypeDef" = {
            "QueueUrl": queue_url,
            "MessageBody": kwargs["message_body"],
        }
        if "message_group_id" in kwargs:
            request_body["MessageGroupId"] = kwargs["message_group_id"]
        if "message_deduplication_id" in kwargs:
            request_body["MessageDeduplicationId"] = kwargs["message_deduplication_id"]
        return self.client.send_message(**request_body)
