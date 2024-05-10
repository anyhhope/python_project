import asyncio
from preprocessing.run import preprocess

async def main():
    await preprocess()

if __name__ == '__main__':
    asyncio.run(main())