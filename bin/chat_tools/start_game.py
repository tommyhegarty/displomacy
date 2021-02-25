import asyncio

async def start_waiting():
    await asyncio.sleep(60 * 60)
    print('finished waiting')