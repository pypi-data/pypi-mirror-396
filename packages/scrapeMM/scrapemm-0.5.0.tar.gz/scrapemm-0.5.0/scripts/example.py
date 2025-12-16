from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://www.facebook.com/reel/2038221060315031"
    result = asyncio.run(retrieve(url))
    if result.errors:
        print(result.errors)
    else:
        print(result.content)
