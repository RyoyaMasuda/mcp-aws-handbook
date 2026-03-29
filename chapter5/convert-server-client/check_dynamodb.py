import boto3
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")


def check_table_exists(table_name: str, region: str = "us-west-2") -> bool:
    # 指定したDynamoDBテーブルが存在するか確認する
    client = boto3.client("dynamodb", region_name=region)
    try:
        client.describe_table(TableName=table_name)
        print(f"テーブル '{table_name}' は存在します（リージョン: {region}）")
        return True
    except client.exceptions.ResourceNotFoundException:
        print(f"テーブル '{table_name}' は存在しません（リージョン: {region}）")
        return False


if __name__ == "__main__":
    check_table_exists("tech-report")
