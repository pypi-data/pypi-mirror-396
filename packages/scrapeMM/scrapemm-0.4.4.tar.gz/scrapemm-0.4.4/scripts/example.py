from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2Fphoto%3Ffbid%3D860758296160977%26set%3Da.513585680878242"
    result = asyncio.run(retrieve(url))
    if result.errors:
        print(result.errors)
    else:
        print(result.content)
