copy gemini api key

open command prompt and run this command
set GEMINI_API_KEY="REPLACE WITH KEY"
python -m jupyterlab 

step 1: add the playwright command

%pip install playwright google-genai python-dotenv
!playwright install chromium

Step 2: 
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

pw = await async_playwright().start()
browser = await pw.chromium.launch(headless=False, slow_mo=700)
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
page = await context.new_page()
print("Chrome is ready!")

Step 3: Agent

from google.genai.errors import ServerError

async def open_amazon() -> str:
    """Opens Amazon India (amazon.in) in the Chrome browser."""
    print("  [CHROME] Opening amazon.in...")
    await page.goto("https://www.amazon.in", wait_until="domcontentloaded")
    return "Amazon India homepage is open."

async def search_product(keyword: str) -> str:
    """Searches for a product keyword on Amazon India."""
    print(f"  [CHROME] Searching Amazon.in for: '{keyword}'")
    await page.wait_for_selector("#twotabsearchtextbox", timeout=10000)
    await page.fill("#twotabsearchtextbox", keyword)
    await page.click("#nav-search-submit-button")
    await page.wait_for_selector("[data-component-type='s-search-result']", timeout=10000)
    return f"Search results loaded for '{keyword}'."

async def get_top_products(limit: int = 5) -> str:
    """Extracts the titles and prices of the top search results on Amazon India."""
    print(f"  [CHROME] Reading top {limit} products...")
    cards = await page.locator("[data-component-type='s-search-result']").all()
    results = []

    for card in cards[:limit]:
        title_loc = card.locator("h2 span").first
        price_loc = card.locator(".a-price .a-offscreen").first
        
        title = (await title_loc.inner_text()).strip() if await title_loc.count() > 0 else "No title"
        price = (await price_loc.inner_text()).strip() if await price_loc.count() > 0 else "Price unavailable"
        results.append(f"- {title} | {price}")

    return "\n".join(results)

tools = [open_amazon, search_product, get_top_products]

goal = """
Open Amazon India, search for 'wireless mouse under 1000', 
check the top 5 products, and recommend the best value option from the list.
"""

# Fallback list so a 503 spike never stalls your live class
models_to_try = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

for model_name in models_to_try:
    try:
        print(f"Trying {model_name}...")
        chat = client.aio.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(tools=tools, temperature=0.0)
        )
        response = await chat.send_message(goal)
        print(f"\nAgent Recommendation (via {model_name}):\n", response.text)
        break
    except ServerError as e:
        print(f"  [!] {model_name} busy ({e.code}), switching to fallback...") 