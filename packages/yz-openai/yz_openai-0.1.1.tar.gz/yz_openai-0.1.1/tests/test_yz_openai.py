import asyncio
import os
from yz_openai import YzOpenAI
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

async def main():
    # 使用 LiteLLM 提供商
    async with YzOpenAI(provider="litellm", api_key=os.getenv("LITELLM_API_KEY")) as client:
        result = await client.chat.completion(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "你好，介绍一下你自己"}
            ]
        )
        print(result.message.content)

asyncio.run(main())