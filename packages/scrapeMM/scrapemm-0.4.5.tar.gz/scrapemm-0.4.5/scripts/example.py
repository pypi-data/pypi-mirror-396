from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://babame.com"
    result = asyncio.run(retrieve(url, methods=["firecrawl"]))
    if result.errors:
        print(result.errors)
    else:
        print(result.content)
