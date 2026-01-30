
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Target URL
url = 'https://en.setopati.com/'

# Fetch the page
response = requests.get(url) 
soup = BeautifulSoup(response.text, features='html.parser') 

# Find trending/featured articles - Based on the HTML you provided
# The main breaking news section
breaking_news_section = soup.find('section', class_='breaking-news')
breaking_articles = []
if breaking_news_section:
    # Get the main breaking news
    main_article = breaking_news_section.find('a')
    if main_article and main_article.get('href'):
        breaking_articles.append(main_article)
    
    # Get the triple news items
    more_news_section = soup.find('section', class_='more-breaking-news')
    if more_news_section:
        triple_articles = more_news_section.find_all('a')
        breaking_articles.extend(triple_articles)

# Find all articles in the "Special" and "News" sections
special_news_section = soup.find('section', class_='samachar-section')
special_articles = []
if special_news_section:
    # Find all article links in the special section
    special_links = special_news_section.find_all('a', href=True)
    special_articles.extend(special_links)

# Combine all articles and get unique URLs
all_articles = breaking_articles + special_articles
trending_urls = []

for article in all_articles[:15]:  # Limit to 15 articles initially
    href = article.get('href')
    if href:
        # Skip non-article links
        if 'javascript' in href or '#' in href or 'category' in href or 'author' in href:
            continue
            
        # Construct full URL
        if href.startswith('/'):
            full_url = 'https://en.setopati.com' + href
        elif 'http' not in href:
            full_url = 'https://en.setopati.com/' + href
        else:
            full_url = href
        
        # Only add Setopati article URLs and avoid duplicates
        if 'setopati.com' in full_url and '/view/' not in full_url and full_url not in trending_urls:
            trending_urls.append(full_url)

# Limit to 10 articles
trending_urls = trending_urls[:10]
print(f"Found {len(trending_urls)} article URLs")

# Visit articles and extract data
articles_data = []
for article_url in trending_urls:
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, features='html.parser')
    
    # Extract title - look for h1 or other title elements
    title = "Title not found"
    title_elem = article_soup.find('h1')
    if not title_elem:
        title_elem = article_soup.find('h2')
    if not title_elem:
        title_elem = article_soup.find('div', class_='main-title')
    
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    # Extract content - look for article content
    content = ""
    content_div = article_soup.find('article')
    if not content_div:
        content_div = article_soup.find('div', class_='post-content')
    if not content_div:
        content_div = article_soup.find('div', class_='article-content')
    
    if content_div:
        content_paragraphs = content_div.find_all('p')
        content = '\n'.join(p.get_text(strip=True) for p in content_paragraphs)
    else:
        # Fallback: get all paragraphs in the main content area
        main_content = article_soup.find('div', id='content')
        if main_content:
            content_paragraphs = main_content.find_all('p')
            content = '\n'.join(p.get_text(strip=True) for p in content_paragraphs[:10])  # Limit paragraphs
    
    articles_data.append({
        'title': title,
        'content': content[:500] + "..." if len(content) > 500 else content,  # Truncate long content
        'url': article_url,
        'scraped_at': datetime.now().isoformat()
    })

print(articles_data)

# Save to file
filename = "seto_pati.json"
with open(filename, 'w') as f:
    json.dump(articles_data, f, indent=4)
