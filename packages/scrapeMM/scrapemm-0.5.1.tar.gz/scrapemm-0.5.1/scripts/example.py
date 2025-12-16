from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://www.youtube.com/shorts/cE0zgN6pYOc"
    result = asyncio.run(retrieve(url))
    if result.errors:
        print(result.errors)
    else:
        print(result.content)
