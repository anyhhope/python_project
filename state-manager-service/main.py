import asyncio
from state.run import track_states


async def main():
    await track_states()

if __name__ == '__main__':
    asyncio.run(main())