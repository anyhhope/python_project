import asyncio

async def task1():
    while True:
        print("Task 1 is running")
        # await asyncio.sleep(1) #без sleep не работает очевидно

async def task2():
    while True:
        print("Task 2 is running")
        # await asyncio.sleep(2)

async def main():
    # Создаем задачи для выполнения
    t1 = asyncio.create_task(task1())
    t2 = asyncio.create_task(task2())

    # Ждем, пока обе задачи не завершатся (хотя они никогда не завершатся)
    await t1
    await t2

# Запускаем основную функцию asyncio
asyncio.run(main())
