
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Target URL
url = 'https://kathmandupost.com/'

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')

# Inside ul having class trending-topics-list, all li elements having a tags, extract their url
trending_topics_section = soup.find('ul', class_='trending-topics-list')
trending_topics = trending_topics_section.find_all('li')

trending_paths = []
for each_topic in trending_topics:
    a_tag = each_topic.find('a')
    if a_tag:
        trending_paths.append(a_tag['href'])

trending_articles_urls = []
for each_path in trending_paths:
    full_url = 'https://kathmandupost.com' + each_path
    trending_articles_urls.append(full_url)


# print("Trending Articles URLs:", trending_articles_urls)
# Visit trending articles and extract title, author, date and content
articles_data = []
for article_url in trending_articles_urls:
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, features='html.parser')

    tag_mark = article_soup.find('h4', class_='title--line__red')
    tag = None
    if tag_mark:
        tag = tag_mark.find('a').get_text(strip=True)
    
    title = tag_mark.find_next('h1').get_text(strip=True)
    content_paragraphs = article_soup.find('section', class_='story-section').find_all('p')
    content = '\n'.join(p.get_text(strip=True) for p in content_paragraphs)
    
    articles_data.append({
        'title': title,
        'tag': tag,
        'content': content,
        'url': article_url,
        'scraped_at': datetime.now().isoformat()
    })

print(articles_data)
# File name
file_name = 'kathmandu_post.json'

# Write to JSON file
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)

print("Data saved to", file_name)
