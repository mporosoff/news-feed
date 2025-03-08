import requests
import feedparser
from bs4 import BeautifulSoup

# Google News RSS URL for "Marc Porosoff University of Rochester"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=Marc+Porosoff+University+of+Rochester"

# University of Rochester Chemical Engineering News Page
UR_NEWS_URL = "https://www.hajim.rochester.edu/che/news/index.html"

def fetch_google_news():
    """Fetches latest news from Google News RSS"""
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    articles = feed.entries[:5]  # Get the latest 5 articles

    news_list = []
    for article in articles:
        image_url = "https://via.placeholder.com/600x200"  # Default placeholder image

        # Check if media_content exists
        if 'media_content' in article and len(article.media_content) > 0:
            image_url = article.media_content[0]['url']
        
        # If the article has an image in the 'summary', extract it (if available)
        elif 'summary' in article:
            soup = BeautifulSoup(article.summary, "html.parser")
            img_tag = soup.find("img")
            if img_tag and "src" in img_tag.attrs:
                image_url = img_tag["src"]

        news_list.append({
            "title": article.title,
            "link": article.link,
            "date": article.published,
            "image": image_url,
            "source": "Google News"
        })
    
    return news_list

def scrape_ur_news():
    """Scrapes the University of Rochester Chemical Engineering news page"""
    response = requests.get(UR_NEWS_URL)
    if response.status_code != 200:
        print("Failed to fetch UR news.")
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all("div", class_="news-item")[:5]  # Adjust selector if necessary

    news_list = []
    for article in articles:
        title = article.find("h3").text.strip() if article.find("h3") else "No Title"
        link = article.find("a")["href"] if article.find("a") else "#"
        link = f"https://www.hajim.rochester.edu{link}" if link.startswith("/") else link

        # Try to find an image inside the article
        image_url = "https://www.hajim.rochester.edu/che/images/banner.jpg"  # Default banner
        img_tag = article.find("img")
        if img_tag and "src" in img_tag.attrs:
            image_url = f"https://www.hajim.rochester.edu{img_tag['src']}" if img_tag['src'].startswith("/") else img_tag['src']

        news_list.append({
            "title": title,
            "link": link,
            "date": "University News",
            "image": image_url,
            "source": "UR Chem Eng News"
        })
    
    return news_list

def generate_news_feed():
    """Fetches news from multiple sources and generates an HTML file"""
    google_news = fetch_google_news()
    ur_news = scrape_ur_news()
    all_news = google_news + ur_news  # Merge both lists

    # Define CSS for styling
    html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Latest Research News</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
            h2 { text-align: center; color: #333; }
            .news-container { max-width: 700px; margin: auto; background: #fff; padding: 20px;
                              border-radius: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); }
            .news-item { border-bottom: 1px solid #ddd; padding: 15px 0; }
            .news-item:last-child { border-bottom: none; }
            .news-title { font-size: 18px; font-weight: bold; color: #0073e6; text-decoration: none; }
            .news-title:hover { text-decoration: underline; }
            .news-date { color: #777; font-size: 14px; }
            img { width: 100%; max-height: 200px; object-fit: cover; border-radius: 5px; margin-top: 10px; }
            .source { font-size: 12px; color: #555; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="news-container">
            <h2>Latest Research News</h2>
    """

    # Add articles to HTML
    for article in all_news:
        html_content += f"""
        <div class="news-item">
            <a class="news-title" href="{article['link']}" target="_blank">{article['title']}</a>
            <p class="news-date">{article['date']}</p>
            <img src="{article['image']}" alt="News Image">
            <p class="source">Source: {article['source']}</p>
        </div>
        """

    # Close HTML tags
    html_content += """
        </div>
    </body>
    </html>
    """

    # Save to file
    with open("news_feed.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("News feed updated and saved!")

# Run once and exit
generate_news_feed()
