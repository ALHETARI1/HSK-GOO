import asyncio
import json
import os
import edge_tts

VOICE = "zh-CN-XiaoxiaoNeural"  # صوت أنثى صيني واضح؛ بديل: zh-CN-YunxiNeural (ذكر)
OUTPUT_DIR = "audio"
CONCURRENCY = 5  # عدد الطلبات المتزامنة لتسريع التوليد دون إغراق الخدمة


async def generate_one(sem, word_id, text):
    filename = f"{OUTPUT_DIR}/{word_id:04d}.mp3"
    if os.path.exists(filename):
        return  # تخطي أي ملف تم توليده مسبقًا (يسمح بإعادة التشغيل بأمان)
    async with sem:
        try:
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(filename)
            print(f"OK  {word_id:04d}: {text}")
        except Exception as e:
            print(f"FAIL {word_id:04d}: {text} -> {e}")


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open("tts/words.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [generate_one(sem, w["id"], w["ch"]) for w in words]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
