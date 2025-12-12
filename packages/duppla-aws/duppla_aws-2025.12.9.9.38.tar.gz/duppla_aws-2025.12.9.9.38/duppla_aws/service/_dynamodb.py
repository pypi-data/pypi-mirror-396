import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Union

from duppla_aws.utils.encoder import JSON, jsonable_dumps

if TYPE_CHECKING:
    from types_boto3_dynamodb import DynamoDBServiceResource
    from types_boto3_dynamodb.type_defs import (
        ConditionBaseImportTypeDef,
        TableAttributeValueTypeDef,
    )


class DynamoDBResource:
    def __init__(self, resource: "DynamoDBServiceResource") -> None:
        self.resource = resource
        # self.client = resource.meta.client unused for now, let's avoid confusion

    # region: Composition
    def Table(self, name: str): return self.resource.Table(name)  # NOSONAR
    def __getattr__(self, name: str): return getattr(self.resource, name)
    # endregion

    get_table = Table

    def query(
        self,
        tablename: str,
        *,
        index: str,
        condition_expression: "ConditionBaseImportTypeDef",
        expression_values: dict[str, "TableAttributeValueTypeDef"],
    ):
        """
        Query items from a DynamoDB table using a specified index and condition expression.

        Args:
            tablename (str): The name of the DynamoDB table.
            index (str): The name of the index to query.
            condition_expression (ConditionBaseImportTypeDef): The condition expression to filter the query.
            expression_values (dict[str, TableAttributeValueTypeDef]): A dictionary of attribute values to use in the condition expression.
        """
        return self.Table(tablename).query(
            IndexName=index,
            KeyConditionExpression=condition_expression,
            ExpressionAttributeValues=expression_values,
        )

    def scan(
        self,
        tablename: str,
        *,
        filter: "ConditionBaseImportTypeDef",
        expression_values: dict[str, "TableAttributeValueTypeDef"],
    ):
        """
        The `Scan` operation returns one or more items and item attributes
        by accessing every item in a table or a secondary index.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/scan.html)
        [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_dynamodb/service_resource/#tablescan-method)
        """
        return self.Table(tablename).scan(
            FilterExpression=filter,
            ExpressionAttributeValues=expression_values,
        )

    def get_item(
        self,
        table: str,
        key: dict[str, "TableAttributeValueTypeDef"],
        **kwargs: "TableAttributeValueTypeDef",
    ):
        """
        The `GetItem` operation returns a set of attributes for the item
        with the given primary key.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/get_item.html)
        [Show types-boto3-full documentation](https://youtype.github.io/types_boto3_docs/types_boto3_dynamodb/service_resource/#tableget_item-method)
        """
        return self.Table(table).get_item(Key={**key, **kwargs})

    @staticmethod
    def _convert_to_table_attribute(
        obj: Union[JSON, dict[str, "TableAttributeValueTypeDef"]],
    ) -> JSON:
        if isinstance(obj, dict):
            return {
                k: DynamoDBResource._convert_to_table_attribute(v)  # type: ignore
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [
                DynamoDBResource._convert_to_table_attribute(element) for element in obj
            ]
        elif isinstance(obj, float):
            return Decimal(str(obj))  # pyright: ignore[reportReturnType]
        else:
            return obj

    def insert(
        self,
        tablename: str,
        item: Union[JSON, dict[str, "TableAttributeValueTypeDef"]],
    ):
        """
        Inserts an item or a list of items into the specified DynamoDB table.
        Args:
            tablename (str): The name of the DynamoDB table.
            item (Union[JSON, dict[str, TableAttributeValueTypeDef]]): The item or list of items to insert.
                The item can be a JSON object or a dictionary with attribute values.
        Returns:
            dict: A dictionary containing the response metadata or a success status.
        Raises:
            IOError: If there is an error inserting the item into the table.
            ValueError: If the item is not a structured JSON object or list.
        """
        if len(jsonable_dumps(item)) >= 40_000:
            self.insert_over_40kb(tablename, item)
            return {"status": "success"}

        tableobj = self.get_table(tablename)
        item = self._convert_to_table_attribute(item)

        if isinstance(item, dict):
            response = tableobj.put_item(Item=item, ReturnValues="ALL_OLD")  # pyright:ignore[reportArgumentType]
            status_code = response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code != 200:
                raise IOError(f"Error inserting item into table {tablename}")
            return response["ResponseMetadata"]
        elif isinstance(item, list):
            with tableobj.batch_writer() as batch:
                for i in item:
                    batch.put_item(Item=i)  # pyright:ignore[reportArgumentType]
                return {"status": "success"}
        else:
            raise ValueError("Item must be a structured json")

    def insert_over_40kb(
        self,
        tablename: str,
        item: Union[JSON, dict[str, "TableAttributeValueTypeDef"]],
    ):
        if isinstance(item, list):
            for i, item_obj in enumerate(item):
                self.insert_over_40kb(f"{tablename}_{i}", item_obj)
        elif isinstance(item, dict):
            for key, value in item.items():
                if len(jsonable_dumps(value)) > 40000:
                    self._upload_and_insert(tablename, key, value)  # type: ignore
                else:
                    self.insert(tablename, value)  # type: ignore
        else:
            self._upload_and_insert(tablename, str(uuid.uuid4()), item)

    def _upload_and_insert(self, tablename: str, key: str, value: JSON):
        filename = f"{key.removesuffix('.json')}_{datetime.now().isoformat()}.json"
        DynamoDBResource._upload_and_insert.f_put_object(  # pyright: ignore[reportFunctionMemberAccess]
            tablename, filename, jsonable_dumps(value)
        )
        self.insert(
            filename,
            {"id": filename, "data_location": f"s3://{tablename}/{filename}"},
        )
