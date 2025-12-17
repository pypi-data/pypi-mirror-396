from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://web.archive.org/web/20210604181412/https://www.tiktok.com/@realstewpeters/video/6969789589590379781?is_copy_url=1"
    result = asyncio.run(retrieve(url))
    if result.errors:
        print(result.errors)
    else:
        print(result.content)
