from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from types_boto3_sns import SNSServiceResource
    from types_boto3_sns.type_defs import PublishInputTypeDef


class SNSResource:
    def __init__(self, resource: "SNSServiceResource"):
        self.resource = resource
        self.client = resource.meta.client

    # region: Composition
    def PlatformApplication(self, arn: str): return self.resource.PlatformApplication(arn)  # NOSONAR
    def PlatformEndpoint(self, arn: str): return self.resource.PlatformEndpoint(arn)  # NOSONAR
    def Subscription(self, arn: str): return self.resource.Subscription(arn)  # NOSONAR
    def Topic(self, arn: str): return self.resource.Topic(arn)  # NOSONAR
    def __getattr__(self, name: str): return getattr(self.client, name)
    # endregion

    def publish_message(
        self, topic_arn: str, message: str, subject: Optional[str] = None
    ):
        """
        Publishes a message to an SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish)

        Args:
            topic_arn (str): The ARN of the SNS topic.
            message (str): The message to publish.
            subject (str, optional): The subject of the message. Defaults to None.

        Returns:
            dict: Response from the publish action.
        """
        kwargs: "PublishInputTypeDef" = {
            "TopicArn": topic_arn,
            "Message": message,
        }
        if subject:
            kwargs["Subject"] = subject

        return self.client.publish(**kwargs)

    def create_topic(self, name: str):
        """
        Creates an SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.create_topic)

        Args:
            name (str): The name of the topic.

        Returns:
            dict: Response from the create topic action.
        """
        return self.client.create_topic(Name=name)

    def subscribe(self, topic_arn: str, protocol: str, endpoint: str):
        """
        Subscribes an endpoint to an SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.subscribe)

        Args:
            topic_arn (str): The ARN of the SNS topic.
            protocol (str): The protocol to use (e.g., 'email', 'sms', 'lambda', etc.).
            endpoint (str): The endpoint to receive notifications.

        Returns:
            dict: Response from the subscribe action.
        """
        return self.client.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,
            Endpoint=endpoint,
        )

    def get_topic_attributes(self, topic_arn: str):
        return self.client.get_topic_attributes(TopicArn=topic_arn)["Attributes"]

    def get_topic_arn(self, name: str) -> str:
        return self.client.create_topic(Name=name)["TopicArn"]

    def unsubscribe(self, subscription_arn: str):
        return self.client.unsubscribe(SubscriptionArn=subscription_arn)

    def list_topics(self):
        return self.client.list_topics()["Topics"]

    def list_subscriptions_by_topic(self, topic_arn: str):
        return self.client.list_subscriptions_by_topic(TopicArn=topic_arn)["Subscriptions"]

    def set_topic_attributes(
        self,
        topic_arn: str,
        attribute_name: str,
        attribute_value: str,
    ):
        return self.client.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName=attribute_name,
            AttributeValue=attribute_value,
        )

    def confirm_subscription(
        self,
        topic_arn: str,
        token: str,
        authenticate_on_unsubscribe: str = "true",
    ):
        return self.client.confirm_subscription(
            TopicArn=topic_arn,
            Token=token,
            AuthenticateOnUnsubscribe=authenticate_on_unsubscribe,
        )

    def delete_topic(self, topic_arn: str):
        return self.client.delete_topic(TopicArn=topic_arn)
