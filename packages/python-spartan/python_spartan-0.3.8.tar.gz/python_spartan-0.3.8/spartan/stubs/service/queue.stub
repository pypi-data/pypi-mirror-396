import json

import boto3


class QueueService:
    def __init__(self) -> None:
        self.sqs = boto3.client("sqs")

    def send(
        self, url: str, message: dict, group_id: int, deduplication_id: int
    ) -> dict:
        response = self.sqs.send_message(
            QueueUrl=url,
            MessageBody=json.dumps(message),
            MessageGroupId=str(group_id),
            MessageDeduplicationId=str(deduplication_id),
        )

        return response

    def receive(self, url: str):
        response = self.sqs.receive_message(
            QueueUrl=url, AttributeNames=["All"], MessageAttributeNames=["All"]
        )

        return response

    def delete(self, url: str, receipt_handle: str):
        response = self.sqs.delete_message(QueueUrl=url, ReceiptHandle=receipt_handle)

        return response
