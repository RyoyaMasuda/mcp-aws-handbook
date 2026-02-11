# AWSではじめるMCP実践ガイド サンプルコード

技術評論社出版「**AWSではじめるMCP実践ガイド -基礎からAIエージェント構築まで徹底解説-**」のハンズオンで使用するコードを公開しています。

更新情報があれば、本リポジトリで更新していきます

## 📖 書籍について

- **書籍名**: AWSではじめるMCP実践ガイド -基礎からAIエージェント構築まで徹底解説-
- **著者**: 塚田真規、森田和明
- **出版社**: 技術評論社
- **発売日**: 2026年2月26日
- **ISBN**: 978-4-297-15458-5
- **ページ数**: 304ページ
- **価格**: 3,520円（本体3,200円＋税10%）

書籍の詳細情報: https://gihyo.jp/book/2026/978-4-297-15458-5

## 🎯 リポジトリについて

以下の章のハンズオン用サンプルコードが含まれています:

### 第4章: MCPを触ってみよう
- Claude CodeをMCPホストとして使う
- MCPサーバー側プリミティブの実装
- MCPクライアント側プリミティブの実装

### 第5章: AWSとMCPによる実践アプリケーション開発
- AWS公式MCPサーバーを使ったインフラ構築と運用分析
- MCPサーバーを組み合わせたRAGチャットアプリの開発
- MCPサーバー連携によるリサーチエージェント基盤の構築

### 第6章: MCPの実運用に向けて
- MCPサーバーと連携したAIエージェントの評価
- AgentCore GatewayによるMCPの管理

## 📁 ディレクトリ構成
```
.
├── chapter4/                      # 第4章: MCPを触ってみよう
│   ├── claude-code-mcp/          # 4.1節: Claude CodeをMCPホストとして使う
│   ├── server_primitives/        # 4.2節: MCPサーバー側プリミティブの実装
│   └── client_primitives/        # 4.3節: MCPクライアント側プリミティブの実装
│
├── chapter5/                      # 第5章: AWSとMCPによる実践アプリケーション開発
│   ├── kiro-mcp/                 # 5.1節: AWS公式MCPサーバーでインフラ構築
│   ├── rag-agent/                # 5.2節: RAGチャットアプリの開発
│   ├── research-agent/           # 5.3節: リサーチエージェント基盤
│   ├── convert-server/           # 5.3節: ドキュメント変換MCPサーバー
│   └── convert-server-client/    # 5.3節: 変換サーバークライアント
│
└── chapter6/                      # 第6章: MCPの実運用に向けて
    ├── llm-as-a-judge/           # 6.1節: LLM-as-a-Judgeによる評価
    ├── eval-agent/               # 6.1節: AIエージェントの評価
    ├── gateway-client/           # 6.2節: AgentCore Gatewayクライアント
    ├── target-lambda/            # 6.2節: Lambda関数ターゲット
    └── target-mcp-server/        # 6.2節: MCPサーバーターゲット
```

## 👥 著者

- **塚田真規** ([@ma_tsukada](https://x.com/ma_tsukada))

- **森田和明** ([@moritalous](https://x.com/moritalous))

## ⚠️ 注意事項

- ハンズオンの実行にはAWSアカウントの作成やTavily APIキーの作成が必要です
- ハンズオンコードを実行すると、AWSなどのサービス利用料が発生します
- ハンズオンで使用する認証情報やAPIキーは流出しないようにしてください

## 💬 フィードバック・質問

本サンプルコードに関するフィードバックや質問は、GitHubのIssues、または[技術評論社のお問い合わせフォーム](https://gihyo.jp/site/inquiry/form?type=book-content&isbn=978-4-297-15458-5)をご利用ください。

---
