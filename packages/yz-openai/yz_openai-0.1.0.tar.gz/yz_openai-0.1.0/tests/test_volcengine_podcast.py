"""
Podcast TTS 使用示例
"""
import asyncio
import os
from yz_openai import YzOpenAI
from pathlib import Path

from dotenv import load_dotenv
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(_ENV_FILE)


async def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)

    # 初始化客户端
    client = YzOpenAI(
        provider="volcengine",
        api_key=os.getenv("VOLCENGINE_API_KEY"),  # Chat 用
        app_id=os.getenv("VOLCENGINE_APP_ID"),    # Podcast 用
        access_key=os.getenv("VOLCENGINE_ACCESS_KEY")  # Podcast 用
    )

    # 生成播客
    result = await client.podcast.create({
        "input_url": "https://file.yzcdn.cn/upload_files/yz-file/2025/12/05/FnpPrEb3Y6dMYPpHPle5EL1O2deV.pdf",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ]
    })

    print(f"✅ 播客生成成功！")
    print(f"   音频 URL: {result['audio_url']}")
    print(f"   音频大小: {len(result['audio_data'])} bytes")
    print(f"   总轮次: {result['total_rounds']}")
    print(f"   文本数量: {len(result['texts'])}")

    # 打印前3条文本
    print("\n前3条文本内容:")
    for i, text_item in enumerate(result['texts'][:3], 1):
        print(f"  {i}. [{text_item['speaker']}]: {text_item['text'][:50]}...")

    await client.close()


async def test_nlp_texts():
    """带选项的使用示例"""
    print("\n" + "=" * 60)
    print("示例 2: 自定义选项")
    print("=" * 60)

    client = YzOpenAI(
        provider="volcengine",
        app_id=os.getenv("VOLCENGINE_APP_ID"),
        access_key=os.getenv("VOLCENGINE_ACCESS_KEY")
    )

    result = await client.podcast.create({
        # "input_url": "https://file.yzcdn.cn/upload_files/yz-file/2025/12/05/FnpPrEb3Y6dMYPpHPle5EL1O2deV.pdf",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ],
        "action": 3,
        "nlp_texts": [
            {
                "speaker": "zh_male_dayixiansheng_v2_saturn_bigtts",
                "text": "今天呢我们要聊的呢是火山引擎在这个 FORCE 原动力大会上面的一些比较重磅的发布。"
            },
            {
                "speaker": "zh_female_mizaitongxue_v2_saturn_bigtts",
                "text": "来看看都有哪些亮点哈。"
            }
        ],
        "audio_format": "mp3",
        "sample_rate": 24000,
        "speech_rate": 0,  # 正常语速
        "use_head_music": False,
        "use_tail_music": False,
        "return_audio_url": True,
        "only_nlp_text": False,
        "max_retries": 5
    })

    print(f"✅ 播客生成成功（自定义选项）！")
    print(f"   音频格式: mp3")
    print(f"   采样率: 24000 Hz")
    print(f"   总轮次: {result.total_rounds}")
    print(f"   audio_url: {result.audio_url}")
    print(f"   usage: {result.usage}")

    await client.close()


async def example_save_audio():
    """保存音频文件示例"""
    print("\n" + "=" * 60)
    print("示例 3: 保存音频文件")
    print("=" * 60)

    client = YzOpenAI(
        provider="volcengine",
        app_id=os.getenv("VOLCENGINE_APP_ID"),
        access_key=os.getenv("VOLCENGINE_ACCESS_KEY")
    )

    result = await client.podcast.create({
        "input_url": "https://file.yzcdn.cn/upload_files/yz-file/2025/12/05/FnpPrEb3Y6dMYPpHPle5EL1O2deV.pdf",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ]
    })

    # 保存音频文件
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    audio_file = f"{output_dir}/podcast_example.mp3"
    with open(audio_file, "wb") as f:
        f.write(result['audio_data'])

    print(f"✅ 音频文件已保存: {audio_file}")
    print(f"   文件大小: {len(result['audio_data'])} bytes")

    # 保存文本文件
    import json
    text_file = f"{output_dir}/podcast_texts.json"
    with open(text_file, "w", encoding="utf-8") as f:
        json.dump(result['texts'], f, ensure_ascii=False, indent=2)

    print(f"✅ 文本文件已保存: {text_file}")

    await client.close()


async def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例 4: 错误处理")
    print("=" * 60)

    from yz_openai import PodcastError, PodcastConnectionError

    client = YzOpenAI(
        provider="volcengine",
        app_id=os.getenv("VOLCENGINE_APP_ID"),
        access_key=os.getenv("VOLCENGINE_ACCESS_KEY")
    )

    try:
        # 故意使用错误的参数
        result = await client.podcast.create({
            "input_url": "https://example.com/invalid.pdf",
            "speakers": ["speaker1"]  # 少于2个说话人
        })
    except PodcastError as e:
        print(f"❌ 捕获到 PodcastError: {e}")

    try:
        # 正确的调用
        result = await client.podcast.create({
            "input_url": "https://file.yzcdn.cn/upload_files/yz-file/2025/12/05/FnpPrEb3Y6dMYPpHPle5EL1O2deV.pdf",
            "speakers": [
                "zh_male_dayixiansheng_v2_saturn_bigtts",
                "zh_female_mizaitongxue_v2_saturn_bigtts"
            ]
        })
        print(f"✅ 正确的调用成功！")
    except PodcastError as e:
        print(f"❌ 意外错误: {e}")

    await client.close()


async def main():
    """运行所有示例"""
    print("\n🎙️  Podcast TTS 使用示例\n")

    # 检查环境变量
    if not os.getenv("VOLCENGINE_APP_ID") or not os.getenv("VOLCENGINE_ACCESS_KEY"):
        print("⚠️  请设置环境变量:")
        print("   export VOLCENGINE_APP_ID=your_app_id")
        print("   export VOLCENGINE_ACCESS_KEY=your_access_key")
        return

    try:
        # 运行示例
        await test_nlp_texts()
        # await example_with_options()
        # await example_save_audio()
        # await example_error_handling()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
