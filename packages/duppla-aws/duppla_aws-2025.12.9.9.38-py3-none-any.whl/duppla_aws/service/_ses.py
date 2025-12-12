from typing import TYPE_CHECKING, Literal, Sequence

from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from types_boto3_ses import SESClient

_UNKNOWN_ERROR = "Unknown error"


class SESResource:
    def __init__(self, client: "SESClient"):
        self.client = client

    # region: Composition
    def __getattr__(self, name: str): return getattr(self.client, name)
    # endregion

    def send_email(
        self,
        source: str,
        to_addresses: Sequence[str],
        subject: str,
        body: str,
        body_type: Literal["Text", "Html"] = "Text",
    ):
        """
        Sends an email using AWS SES.

        Args:
            source (str): The email address that is sending the email.
            to_addresses (list): A list of email addresses to send the email to.
            subject (str): The subject of the email.
            body (str): The body of the email.
            body_type (str, optional): The type of the email body (Text or Html). Defaults to "Text".

        Returns:
            dict: Response from the send email action.
        """
        try:
            response = self.client.send_email(
                Source=source,
                Destination={"ToAddresses": to_addresses},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {body_type: {"Data": body}}, # type: ignore
                },
            )
            return response
        except ClientError as e:
            msg = e.response.get("Error", {}).get("Message", _UNKNOWN_ERROR)
            raise RuntimeError(f"Failed to send email: {msg}")

    def verify_email_identity(self, email: str):
        """
        Verifies an email address.

        Args:
            email (str): The email address to verify.

        Returns:
            dict: Response from the verify email identity action.
        """
        try:
            response = self.client.verify_email_identity(EmailAddress=email)
            return response
        except ClientError as e:
            msg = e.response.get("Error", {}).get("Message", _UNKNOWN_ERROR)
            raise RuntimeError(f"Failed to send email: {msg}")

    def list_verified_email_addresses(self):
        """
        Lists all verified email addresses.

        Returns:
            list: A list of verified email addresses.
        """
        try:
            response = self.client.list_verified_email_addresses()
            return response.get("VerifiedEmailAddresses", [])
        except ClientError as e:
            msg = e.response.get("Error", {}).get("Message", _UNKNOWN_ERROR)
            raise RuntimeError(f"Failed to send email: {msg}")

    def delete_verified_email_address(self, email: str):
        """
        Deletes a verified email address.

        Args:
            email (str): The email address to delete.

        Returns:
            dict: Response from the delete verified email address action.
        """
        try:
            response = self.client.delete_verified_email_address(EmailAddress=email)
            return response
        except ClientError as e:
            msg = e.response.get("Error", {}).get("Message", _UNKNOWN_ERROR)
            raise RuntimeError(f"Failed to send email: {msg}")
