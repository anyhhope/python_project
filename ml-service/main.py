from ml.run import consume_frames_to_ml
import asyncio 

async def main():
    await consume_frames_to_ml()

if __name__ == '__main__':
    asyncio.run(main())