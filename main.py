from fastapi import FastAPI
from aiohttp import ClientSession
import xml.etree.ElementTree as ET
from fastapi.responses import StreamingResponse

app = FastAPI()

RSS_FEED_URL = "https://engineering.fb.com/feed/"

async def fetch_rss_feed():
    async with ClientSession() as session:
        async with session.get(RSS_FEED_URL) as response:
            return await response.text()

def parse_rss(feed_content):
    root = ET.fromstring(feed_content)
    items = []
    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        description = item.find("description").text
        items.append({"title": title, "link": link, "description": description})
    return items

async def generate_feed_stream():
    feed_content = await fetch_rss_feed()
    parsed_items = parse_rss(feed_content)
    for item in parsed_items:
        yield f"Title: {item['title']}\nLink: {item['link']}\nDescription: {item['description']}\n\n"

@app.get("/rss-stream")
async def stream_rss_feed():
    return StreamingResponse(generate_feed_stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
