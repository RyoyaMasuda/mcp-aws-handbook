import asyncio
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval.test_case import LLMTestCase
from deepeval.models import AmazonBedrockModel
from deepeval import evaluate

async def eval_relevance():
    # 評価モデルを初期化
    deepeval_model = AmazonBedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-west-2"
    )

    # 評価メトリクスの設定
    metric = GEval(
        name="関連性チェック",
        evaluation_steps=[
            "LLMの回答がユーザー入力に直接関係している場合、関連性は高いと判断する",
            "LLMの回答の中に、ユーザー入力に関連しない内容が含まれている場合、関連性は低いと判断する",
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=deepeval_model
    )


    # テストケースの設定
    test_case = LLMTestCase(
        input="今日の天気を教えてくれますか？",
        actual_output="今日の天気は晴れです。外出しやすく洗濯日和でしょう。",
    )
    evaluate(test_cases=[test_case], metrics=[metric])


if __name__ == "__main__":
    asyncio.run(eval_relevance())
