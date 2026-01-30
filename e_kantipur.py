import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Target URL - Main Nepali site
url = 'https://ekantipur.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Connecting to Ekantipur...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    # Use 'lxml' or 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
except Exception as e:
    print(f"Connection Error: {e}")
    exit()

# 1. Find Article Links
# Ekantipur articles usually start with a year/month/day pattern or specific categories
all_links = soup.find_all('a', href=True)
article_urls = []

for link in all_links:
    href = link.get('href')
    # Ekantipur links are often like /news/2026-01-30/abc.html
    if '/news/20' in href or '/national/20' in href:
        full_url = href if href.startswith('http') else f"https://ekantipur.com{href}"
        if full_url not in article_urls:
            article_urls.append(full_url)

print(f"Found {len(article_urls)} Nepali articles. Scraping top 5...")

articles_data = []

# 2. Extract Data from Articles
for article_url in article_urls[:5]:
    try:
        res = requests.get(article_url, headers=headers, timeout=10)
        article_soup = BeautifulSoup(res.text, 'html.parser')

        # TITLE - Ekantipur uses <h1> for the main news title
        title_tag = article_soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "शीर्षक फेला परेन"

        # TAG - Usually found in the top navigation or breadcrumb
        tag_tag = article_soup.select_one('.breadcrumb-item.active, .category-name')
        tag = tag_tag.get_text(strip=True) if tag_tag else "समाचार"

        # CONTENT - Targeted at the main article body
        content_div = article_soup.select_one('.description, .content, .current-news-text')
        
        if content_div:
            # Extract only <p> tags to avoid ads and scripts
            paras = content_div.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paras if p.get_text(strip=True)])
        else:
            content = "लेखको सामग्री फेला परेन।"

        articles_data.append({
            'title': title,
            'tag': tag,
            'content': content[:600] + "..." if len(content) > 600 else content,
            'url': article_url,
            'scraped_at': datetime.now().isoformat()
        })
        print(f"सफलतापूर्वक स्क्र्याप गरियो: {title[:40]}...")

    except Exception as e:
        print(f"त्रुटि (Error): {article_url} -> {e}")

# 3. Save to JSON (With Nepali Language Support)
filename = "e_kantipur.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)

print(f"\nसकियो! {len(articles_data)} समाचार '{filename}' मा सुरक्षित गरियो।")