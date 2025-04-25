import asyncio
import time


async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)


async def main():
    task1 = asyncio.create_task(say_after(1, "hello"))
    task2 = asyncio.create_task(say_after(2, "world"))

    print(f"started at {time.strftime('%X')}")

    await task1  # Wait until task1 is done
    await task2  # Wait until task2 is done

    print(f"finished at {time.strftime('%X')}")


if __name__ == "__main__":
    asyncio.run(main())
