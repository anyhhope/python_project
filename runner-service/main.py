import asyncio
from preprocessing.run import preprocess
from postprocessing.run import postprocess

async def main():
    await asyncio.gather(preprocess(), postprocess())

if __name__ == '__main__':
    asyncio.run(main())