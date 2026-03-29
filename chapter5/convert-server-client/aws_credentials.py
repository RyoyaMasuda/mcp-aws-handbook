import boto3
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def get_aws_credentials() -> Dict[str, str]:
    # boto3のデフォルト認証チェーンから認証情報を取得する
    # 優先順位: 環境変数 → ~/.aws/credentials → IAMロール の順に自動探索する
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    creds = {
        "AWS_ACCESS_KEY_ID": credentials.access_key,
        "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
    }
    # 一時認証情報（STS/AssumeRole）の場合はセッショントークンも追加する
    if credentials.token:
        creds["AWS_SESSION_TOKEN"] = credentials.token
    return creds
