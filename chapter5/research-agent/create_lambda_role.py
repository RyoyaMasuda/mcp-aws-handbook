import boto3
import json

# AWSクライアント初期化
iam = boto3.client('iam')
sts = boto3.client('sts')
# 現在のAWSアカウントID取得
account_id = sts.get_caller_identity().get('Account')

# 設定
ROLE_NAME = 'ReseachAgentExecutionRole'
REGION = 'us-west-2'
FUNCTION_NAME = 'research-agent'

# 信頼ポリシー
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}


# 実行ポリシー（CloudWatch Logs + Bedrock）
execution_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": f"arn:aws:logs:{REGION}:{account_id}:*"
        },
        {
            "Effect": "Allow",
            "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
            "Resource": f"arn:aws:logs:{REGION}:{account_id}:log-group:/aws/lambda/{FUNCTION_NAME}:*"
        },
        {
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            "Resource": "*"
        }
    ]
}

# ロール作成
role = iam.create_role(
    RoleName=ROLE_NAME,
    AssumeRolePolicyDocument=json.dumps(trust_policy),
    Description='Lambda execution role with CloudWatch Logs and Bedrock'
)

# ポリシーアタッチ
iam.put_role_policy(
    RoleName=ROLE_NAME,
    PolicyName=f'{ROLE_NAME}-Policy',
    PolicyDocument=json.dumps(execution_policy)
)

# 結果出力
print(f"✓ ロール作成完了\nARN: {role['Role']['Arn']}")