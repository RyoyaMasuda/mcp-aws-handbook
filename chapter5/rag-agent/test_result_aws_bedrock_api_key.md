# テスト結果: AWS Bedrock API Keyについて教えて

## テスト情報

- **アプリ**: `app_with_kb.py` (RAGチャットアプリ)
- **テスト日時**: 2026-03-22
- **テスト入力**: AWS Bedrock API Keyについて教えて

---

## アシスタントの回答

AWS Bedrock API Keyについて、詳しく説明いたします。

## AWS Bedrock API Keyの概要

**参考元**: [API keys - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)

### API Keyとは

AWS Bedrock API Keyは、Amazon Bedrock APIへのアクセスを認証するための認証情報です。従来のIAMユーザー設定やポリシー管理の複雑さを回避し、より簡単に開発を進められます。

### 2つのタイプのAPI Key

#### 1. **短期API Key (Short-term Keys)**

- **有効期間**: 最大12時間、またはコンソールセッションの期間のいずれか短い方
- **特徴**:
  - IAMプリンシパルがセッションから生成
  - そのプリンシパルの権限を継承
  - 生成されたAWSリージョンでのみ使用可能
  - CloudTrailに記録されない
  - より安全

#### 2. **長期API Key (Long-term Keys)**

- **有効期間**: 1日～無制限（設定可能）
- **特徴**:
  - IAMユーザーとして自動作成される
  - Amazon Bedrock用の基本的な権限を付与
  - AWS IAMコンソールから管理可能
  - 最大2つまで作成可能
  - CloudTrailで監視可能
  - セキュリティリスクが高い（本番環境では使用を避けるべき）

### 利用可能なリージョン

Amazon Bedrock API Keyは以下の20以上のAWSリージョンで利用可能です：

- **アジア太平洋**: ハイデラバード、ムンバイ、大阪、ソウル、シンガポール、シドニー、東京
- **カナダ**: カナダ中部
- **ヨーロッパ**: フランクフルト、アイルランド、ロンドン、ミラノ、パリ、スペイン、ストックホルム、チューリッヒ
- **南米**: サンパウロ
- **米国**: 米国東部（バージニア北部、オハイオ）、米国西部（オレゴン）
- **GovCloud**: AWS GovCloud (US)地域でも利用可能

### 制限事項

- Amazon BedrockおよびAmazon Bedrock Runtimeのアクションにのみ使用可能
- 特定のAPI操作には使用不可
- CloudTrailには記録されない（短期キー）

---

## セキュリティベストプラクティス

**参考元**: [Securing Amazon Bedrock API keys: Best practices for implementation and management](https://aws.amazon.com/blogs/security/securing-amazon-bedrock-api-keys-best-practices-for-implementation-and-management/)

### 推奨される認証方法の優先順位

1. **AWS STS一時認証情報**（最も安全）
2. **短期API Key**（中程度のセキュリティ）
3. **長期API Key**（最低限のセキュリティ、探索用のみ）

### セキュリティ対策

- **長期キーは探索目的のみ**で使用し、本番環境ではIAMロールまたは一時認証情報を使用
- **AWS Secrets Manager**での長期キーの安全な保存
- **Service Control Policies (SCPs)** でAPI Key生成を制限
- **CloudTrailとEventBridge**での長期キー使用の監視
- **定期的なキーローテーション**の実施

---

## API Keyの使用方法

**参考元**: [Use an Amazon Bedrock API key - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html)

API Keyは以下の3つの方法で設定可能です：

1. **環境変数として設定**
2. **コード内で指定**
3. **Authorization ヘッダーに含める**

例（Python）:

```python
import os
os.environ["AWS_BEDROCK_API_KEY"] = "your-api-key"
```

---

API Keyの詳細設定や権限管理についてご質問があれば、さらに詳しく説明いたします。
