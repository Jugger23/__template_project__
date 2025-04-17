import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ALDI_BASE = 'https://www.aldi-nord.de'
ALDI_OFFERS = ALDI_BASE + '/angebote.html'
ROBOTS_URL = ALDI_BASE + '/robots.txt'

# 0. Dump der robots.txt zum Debugging
resp_robots = requests.get(ROBOTS_URL)
print('robots.txt Inahlt:')
print(resp_robots.text)

# 1. Prüfe robots.txt auf Erlaubnis
rp = urllib.robotparser.RobotFileParser()
rp.set_url(ROBOTS_URL)
rp.read()
if not rp.can_fetch('*', ALDI_OFFERS):
    print('Scraping laut robots.txt nicht erlaubt')
    exit(1)
else:
    print('Scraping laut robots.txt erlaubt')

# Variante A: Requests + BeautifulSoup
def fetch_offers():
    resp = requests.get(ALDI_OFFERS)
    print(f"Status Code: {resp.status_code}")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    container = soup.select_one('div.teaser-grid')
    if not container:
        print('Container nicht gefunden – dynamisches Laden vermutet')
        return []
    cards = container.select('article.teaser')
    print(f"Gefundene Karten (A): {len(cards)}")
    offers = []
    for card in cards:
        title = card.select_one('h2.teaser__title')
        price = card.select_one('span.price__value')
        if title and price:
            offers.append({
                'title': title.get_text(strip=True),
                'price': price.get_text(strip=True)
            })
    return offers

# Variante B: Dynamisches Rendering mit Playwright
def fetch_offers_dynamic():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(ALDI_OFFERS)
            try:
                page.wait_for_selector('article.teaser', timeout=10000)
            except PlaywrightTimeoutError:
                print('Timeout B: article.teaser nicht sichtbar')
                browser.close()
                return []
            cards = page.query_selector_all('article.teaser')
            print(f"Gefundene Karten (B): {len(cards)}")
            offers = []
            for card in cards:
                title_el = card.query_selector('h2.teaser__title')
                price_el = card.query_selector('span.price__value')
                if title_el and price_el:
                    offers.append({
                        'title': title_el.inner_text().strip(),
                        'price': price_el.inner_text().strip()
                    })
            browser.close()
            return offers
    except Exception as e:
        print(f'Error im B: {e}')
        return []

# Variante C: Reverse-Engineered JSON-Endpunkt
def fetch_offers_api():
    API_URL = ALDI_BASE + '/offers-api/offers?region=nord'
    resp = requests.get(API_URL)
    print(f"API Status: {resp.status_code}")

    if resp.status_code != 200:
        print("API-Endpunkt nicht verfügbar oder falsch.")
        print(resp.text)
        return []

    try:
        data = resp.json()
    except Exception as e:
        print(f"Fehler beim Parsen der API-Antwort als JSON: {e}")
        print(resp.text[:500])  # ersten 500 Zeichen als Vorschau
        return []

    offers = []
    for item in data.get('offers', []):
        offers.append({
            'title': item.get('productName'),
            'price': f"{item.get('price')} €",
            'discount': item.get('discountPercent')
        })
    print(f"Gefundene Karten (C): {len(offers)}")
    return offers

if __name__ == '__main__':
    offers = fetch_offers()
    if offers:
        print(offers)
    else:
        print('A leer, teste dynamisches B')
        offers = fetch_offers_dynamic()
        if offers:
            print(offers)
        else:
            print('B leer, teste API C')
            offers = fetch_offers_api()
            print(offers or 'Keine Angebote gefunden')