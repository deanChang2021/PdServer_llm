import asyncio

import aiofiles
import os

current_directory = os.getcwd()
print(f"当前工作目录: {current_directory}")

async def loads_banned_words():
    prompt = set()
    filename = "./server/banned_words.txt"
    async with aiofiles.open(filename, "r") as r:
        for line in await r.readlines():
            prompt.add(line.strip())

    return prompt

BANNED_PROMPT = asyncio.run(loads_banned_words())
