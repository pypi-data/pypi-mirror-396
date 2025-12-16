import os

import dotenv
from huggingface_hub import InferenceClient


def create_hf_client(api_key: str | None = None) -> InferenceClient:
    if api_key is None:
        dotenv.load_dotenv()
        api_key = os.environ.get("HF_TOKEN")

    return InferenceClient(
        api_key=api_key,
    )


def hf_summarize(client: InferenceClient, text: str) -> str:
    result = client.summarization(
        text,
        model="csebuetnlp/mT5_multilingual_XLSum",
    )
    return result.summary_text


def hf_summarize_deep_seek(client: InferenceClient, text: str) -> str:
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {
                "role": "user",
                "content": f"摘要以下文章，字數150字內，摘要語言用文章所用語言來寫:\n\n{text}",
            }
        ],
    )

    return completion.choices[0].message.content
