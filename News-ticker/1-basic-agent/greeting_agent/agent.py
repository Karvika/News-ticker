from google.adk.agents import Agent
import google.generativeai as genai
from google.adk.tools.base_tool import BaseTool
from datetime import datetime, timedelta
import json
import os
import requests
import feedparser
from newsapi import NewsApiClient
from dotenv import load_dotenv
import ssl
import urllib3
import certifi

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a custom SSL context for better certificate handling
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Load environment variables from .env file
load_dotenv()

# Get API keys
google_api_key = os.getenv('GOOGLE_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini API (for fallback processing if needed)
genai.configure(api_key=google_api_key)

class RealNewsUpdateTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="real_news_update",
            description="Fetch real AI news headlines from multiple news sources"
        )
        self.schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Store news queue (exactly 5 items, chronologically sorted)
        self.news_queue = [] 
        self.max_news_items = 5  # Fixed to show exactly 5 news items
        
        # Initialize news sources with custom session
        self.newsapi_client = None
        if news_api_key:
            try:
                # Create a session with SSL verification disabled
                session = requests.Session()
                session.verify = False
                
                # Create the NewsAPI client with our custom session
                self.newsapi_client = NewsApiClient(
                    api_key=news_api_key,
                    session=session
                )
                print("NewsAPI client initialized successfully with custom SSL handling")
            except Exception as e:
                print(f"NewsAPI initialization failed: {str(e)}")
        
        # RSS feeds for tech news and innovations
        self.rss_feeds = [
            # Tech Innovation News
            "https://www.techradar.com/rss",  # TechRadar
            "https://www.engadget.com/rss.xml",  # Engadget
            "https://www.theverge.com/rss/index.xml",  # The Verge
            "https://feeds.feedburner.com/TechCrunch",  # TechCrunch
            "https://www.wired.com/feed/rss",  # Wired
            "https://www.zdnet.com/news/rss.xml",  # ZDNet
            "https://www.digitaltrends.com/feed",  # Digital Trends
            "https://gizmodo.com/rss",  # Gizmodo
            
            # Enterprise & Innovation
            "https://www.computerworld.com/index.rss",  # ComputerWorld
            "https://www.cnet.com/rss/news/",  # CNET News
            "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat
            "https://www.techspot.com/backend.xml",  # TechSpot
            
            # Emerging Tech
            "https://www.newscientist.com/subject/technology/feed/",  # New Scientist Tech
            "https://spectrum.ieee.org/rss",  # IEEE Spectrum
            "https://www.technologyreview.com/feed/",  # MIT Technology Review
            "https://www.scientificamerican.com/tech.rss",  # Scientific American Tech
            
            # Gadgets & Consumer Tech
            "https://www.slashgear.com/feed/",  # SlashGear
            "https://www.tomsguide.com/feeds/all",  # Tom's Guide
            "https://www.androidcentral.com/feed",  # Android Central
            "https://appleinsider.com/rss/news/",  # AppleInsider
        ]

    def fetch_from_newsapi(self):
        """Fetch technology news from NewsAPI"""
        if not self.newsapi_client:
            print("NewsAPI client not available, skipping...")
            return []
        
        try:
            print("Fetching from NewsAPI...")
            
            # Simple query for all tech news with optimized parameters
            tech_articles = self.newsapi_client.get_everything(
                q='technology OR innovation OR software OR hardware OR gadget OR app OR startup',
                language='en',
                sort_by='publishedAt',
                page_size=10  # Keep this small for faster response
            )
            
            news_items = []
            if 'articles' in tech_articles:
                for article in tech_articles['articles'][:5]:  # Only process what we need
                    if not article.get('title') or article['title'].lower() == '[removed]':
                        continue
                        
                    try:
                        pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                        local_time = pub_date.replace(tzinfo=None)
                        
                        # Use Gemini to categorize the news
                        description = article.get('description', '')
                        category = self.categorize_with_gemini(article['title'], description)
                        print(f"🏷️ Categorized '{article['title'][:50]}...' as '{category}'")
                        
                        news_item = {
                            'title': article['title'],
                            'timestamp': local_time.strftime("%I:%M %p - %b %d"),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'url': article['url'],
                            'pub_date': local_time,
                            'category': category
                        }
                        news_items.append(news_item)
                        
                        if len(news_items) >= 5:
                            break
                    except Exception as e:
                        print(f"Error processing article: {str(e)}")
                        continue
            
            print(f"Successfully fetched {len(news_items)} articles from NewsAPI")
            return news_items
            
        except Exception as e:
            print(f"NewsAPI fetch error: {str(e)}")
            return []

    def fetch_from_rss(self):
        """Fetch technology news from RSS feeds"""
        print("Fetching from RSS feeds...")
        news_items = []
        used_titles = set()  # Track unique titles across all feeds
        
        # Main tech news sources
        reliable_feeds = [
            ("https://feeds.feedburner.com/TechCrunch", "TechCrunch"),
            ("https://www.theverge.com/rss/index.xml", "The Verge"),
            ("https://www.wired.com/feed/rss", "Wired"),
            ("https://www.engadget.com/rss.xml", "Engadget"),
            ("https://feeds.arstechnica.com/arstechnica/index", "Ars Technica"),
            ("https://www.cnet.com/rss/news/", "CNET"),
            ("https://www.digitaltrends.com/feed", "Digital Trends"),
            ("https://gizmodo.com/rss", "Gizmodo")
        ]
        
        # Create a session with SSL verification disabled
        session = requests.Session()
        session.verify = False
        
        for feed_url, feed_name in reliable_feeds:
            try:
                print(f"Checking {feed_name}...")
                
                # Use the session with disabled SSL verification
                response = session.get(feed_url, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch {feed_name}: HTTP {response.status_code}")
                    continue
                    
                feed = feedparser.parse(response.content)
                
                if not feed.entries:
                    print(f"No entries found in {feed_name}")
                    continue
                
                # Only take up to 2 unique articles from each feed
                feed_count = 0
                for entry in feed.entries:
                    try:
                        # Skip if we already have this title
                        if entry.title in used_titles:
                            continue
                            
                        # Get publication date
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            pub_date = datetime(*entry.updated_parsed[:6])
                        else:
                            pub_date = datetime.now()                            # Use Gemini to categorize the news
                        description = getattr(entry, 'description', '')
                        category = self.categorize_with_gemini(entry.title, description)
                        print(f"🏷️ Categorized '{entry.title[:50]}...' as '{category}'")
                        
                        news_item = {
                            'title': entry.title,
                            'timestamp': pub_date.strftime("%I:%M %p - %b %d"),
                            'source': feed_name,
                            'url': getattr(entry, 'link', ''),
                            'pub_date': pub_date,
                            'category': category
                        }
                        news_items.append(news_item)
                        used_titles.add(entry.title)
                        print(f"✅ Added from {feed_name}: {entry.title[:50]}...")
                        
                        feed_count += 1
                        if feed_count >= 2:  # Only get max 2 items from each feed
                            break
                            
                    except Exception as e:
                        print(f"Error processing entry from {feed_name}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error fetching {feed_name}: {str(e)}")
                continue
        
        # Sort by publication date and take only top 5
        news_items.sort(key=lambda x: x.get('pub_date', datetime.now()), reverse=True)
        final_items = news_items[:5]
        print(f"📰 Successfully fetched {len(final_items)} items from RSS feeds")
        return final_items

    def format_news_item(self, news_data, position):
        """Format news item for the queue with more detailed timestamp"""
        pub_date = news_data.get('pub_date', datetime.now())
        hours_old = (datetime.now() - pub_date).total_seconds() / 3600
        
        if hours_old < 1:
            time_ago = f"{int(hours_old * 60)} minutes ago"
        else:
            time_ago = f"{int(hours_old)} hours ago"
            
        return {
            "id": str(position),
            "title": news_data['title'],
            "timestamp": f"Released: {news_data['timestamp']} ({time_ago})",
            "isLatest": position == 1,
            "source": news_data.get('source', 'Unknown'),
            "url": news_data.get('url', ''),
            "category": news_data.get('category', 'Technology')
        }

    def get_fallback_headlines(self):
        """Enhanced fallback headlines when real news APIs fail - Based on current AI trends"""
        now = datetime.now()
        # Create realistic current headlines based on actual recent AI news trends
        fallback_data = [
            {
                'title': 'OpenAI launches new GPT-4 Turbo with vision capabilities and reduced pricing',
                'timestamp': (now - timedelta(hours=2)).strftime("%I:%M %p - %b %d"),
                'source': 'AI News',
                'url': 'https://openai.com/blog'
            },
            {
                'title': 'Google DeepMind announces breakthrough in protein folding with AlphaFold 3',
                'timestamp': (now - timedelta(hours=4)).strftime("%I:%M %p - %b %d"),
                'source': 'Tech Daily',
                'url': 'https://deepmind.google/research/'
            },
            {
                'title': 'Microsoft integrates advanced AI copilot features across Office 365 suite',
                'timestamp': (now - timedelta(hours=6)).strftime("%I:%M %p - %b %d"),
                'source': 'Enterprise Tech',
                'url': 'https://blogs.microsoft.com/ai/'
            },
            {
                'title': 'Meta releases Llama 3 with improved multilingual support and reasoning',
                'timestamp': (now - timedelta(hours=8)).strftime("%I:%M %p - %b %d"),
                'source': 'ML Research',
                'url': 'https://ai.meta.com/blog/'
            },
            {
                'title': 'Anthropic Claude 3 achieves new benchmarks in safety and helpfulness metrics',
                'timestamp': (now - timedelta(hours=10)).strftime("%I:%M %p - %b %d"),
                'source': 'AI Safety News',
                'url': 'https://www.anthropic.com/news'
            }
        ]
        
        return [self.format_news_item(item, i+1) for i, item in enumerate(fallback_data)]

    def execute(self, inputs=None):
        try:
            print("🔄 Fetching latest technology news...")
            
            # Try NewsAPI first
            print("📰 Fetching from NewsAPI...")
            real_news = self.fetch_from_newsapi()
            
            # Only use RSS feeds if NewsAPI didn't return enough items
            if len(real_news) < 5:
                print(f"📰 NewsAPI only returned {len(real_news)} items, adding RSS feed news...")
                rss_results = self.fetch_from_rss()
                real_news.extend(rss_results)
            
            # If we got real news, build a proper chronological queue
            if real_news:
                print("📰 Building chronological news queue...")
                
                # Sort by actual datetime, not string timestamp
                real_news.sort(key=lambda x: x.get('pub_date', datetime.now()), reverse=True)
                
                # Take exactly 5 most recent different articles
                self.news_queue = []
                used_titles = set()
                
                # Process articles and ensure we get exactly 5 unique ones
                for idx, news_item in enumerate(real_news):
                    title_lower = news_item['title'].lower().strip()
                    if title_lower not in used_titles and len(self.news_queue) < 5:
                        position = len(self.news_queue) + 1  # This ensures sequential numbering
                        formatted_item = {
                            "id": str(position),  # Sequential number from 1 to 5
                            "title": news_item['title'],
                            "timestamp": f"Released: {news_item['timestamp']}",
                            "isLatest": position == 1,  # First item is always latest
                            "source": news_item.get('source', 'Unknown'),
                            "url": news_item.get('url', ''),
                            "category": news_item.get('category', 'Technology')
                        }
                        self.news_queue.append(formatted_item)
                        used_titles.add(title_lower)
                        print(f"📅 Added #{position}: {news_item['title'][:50]}...")
                
                # Fill remaining slots with fallback if we don't have 5 items
                while len(self.news_queue) < 5:
                    position = len(self.news_queue) + 1
                    fallback_item = {
                        "id": str(position),
                        "title": f"Technology Update {position}",
                        "timestamp": f"Released: {datetime.now().strftime('%I:%M %p - %b %d')}",
                        "isLatest": position == 1,
                        "source": "Tech News",
                        "url": "",
                        "category": "Technology"
                    }
                    self.news_queue.append(fallback_item)
                    print(f"📅 Added fallback #{position}")
                
                print(f"✅ Built queue with {len(self.news_queue)} chronologically sorted articles")
                return json.dumps(self.news_queue)
            
            # Use fallback if no real news available
            print("📰 Using fallback headlines...")
            self.news_queue = self.get_fallback_headlines()
            return json.dumps(self.news_queue)
                
        except Exception as e:
            print(f"❌ Error in RealNewsUpdateTool: {str(e)}")
            
            # Initialize with fallback headlines if queue is empty
            if not self.news_queue:
                print("🔄 Initializing with fallback headlines due to error...")
                self.news_queue = self.get_fallback_headlines()
            
            return json.dumps(self.news_queue)

    def __call__(self, args):
        """Execute the tool"""
        try:
            print("\n=== Starting News Fetch Process ===")
            
            # Fetch from both sources simultaneously
            print("\nFetching from both NewsAPI and RSS feeds...")
            newsapi_items = self.fetch_from_newsapi()
            rss_items = self.fetch_from_rss()
            
            print(f"NewsAPI returned {len(newsapi_items)} items")
            print(f"RSS feeds returned {len(rss_items)} items")
            
            # AI keywords for filtering
            ai_keywords = [
                'ai', 'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'chatgpt', 'gpt-4', 'gpt-3', 'llm', 'language model',
                'openai', 'anthropic', 'claude', 'gemini', 'copilot', 'robot',
                'automation', 'computer vision', 'nlp', 'autonomous', 'ml'
            ]
            
            # Function to score AI relevance
            def get_ai_score(item):
                title = item['title'].lower()
                score = sum(2 if kw in title else 0 for kw in ai_keywords)  # Double weight for title matches
                if 'description' in item:
                    desc = item['description'].lower()
                    score += sum(1 if kw in desc else 0 for kw in ai_keywords)
                return score

            # Score and filter both sets of results
            all_news = []
            
            # Process NewsAPI items
            for item in newsapi_items:
                score = get_ai_score(item)
                if score > 0:  # Only include items with some AI relevance
                    item['ai_score'] = score
                    item['source_type'] = 'NewsAPI'
                    all_news.append(item)
            
            # Process RSS items
            for item in rss_items:
                score = get_ai_score(item)
                if score > 0:  # Only include items with some AI relevance
                    item['ai_score'] = score
                    item['source_type'] = 'RSS Feed'
                    all_news.append(item)
            
            if not all_news:
                print("No AI-focused news items found!")
                return []
            
            # Sort by publication date first, then by AI relevance score
            print("\nSorting news by date and AI relevance...")
            try:
                all_news.sort(key=lambda x: (x.get('pub_date', datetime.now()), x.get('ai_score', 0)), reverse=True)
            except Exception as e:
                print(f"Sorting error: {e}")
                # Fallback to timestamp-based sorting
                all_news.sort(key=lambda x: datetime.strptime(x['timestamp'], "%I:%M %p - %b %d"), reverse=True)
            
            # Take top 5 most recent, most AI-relevant items
            final_news = []
            used_titles = set()
            
            for item in all_news:
                if item['title'].lower() not in used_titles:
                    news_item = self.format_news_item(item, len(final_news) + 1)
                    final_news.append(news_item)
                    used_titles.add(item['title'].lower())
                    
                    print(f"\nNews {len(final_news)}: {news_item['title']}")
                    print(f"Source: {news_item['source']}")
                    print(f"From: {item['source_type']}")
                    print(f"AI Relevance Score: {item.get('ai_score', 0)}")
                    
                    if len(final_news) >= 5:
                        break
            
            return final_news
            
        except Exception as e:
            print(f"Error in news tool: {str(e)}")
            return []

    def categorize_with_gemini(self, title, description=""):
        """Categorize news using Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""Analyze this technology news article and categorize it into ONE of these categories:
            - AI & Machine Learning
            - Software Development
            - Hardware & Gadgets
            - Cybersecurity
            - Business Tech
            - Gaming
            - Innovation
            - Digital Culture

            Title: {title}
            Description: {description}

            Return only the category name, nothing else."""

            response = model.generate_content(prompt)
            category = response.text.strip()
            print(f"🏷️ Gemini categorized: '{title[:50]}...' as '{category}'")
            return category
        except Exception as e:
            print(f"⚠️ Categorization error: {e}")
            return "Technology" # Default category

# Create a global instance to maintain state across requests
real_news_tool_instance = RealNewsUpdateTool()

root_agent = Agent(
    name="real_ai_news_agent",
    model="gemini-pro",
    description="Real AI News headlines agent using live news sources",
    instruction="Fetch and return the latest real AI news headlines from news APIs and RSS feeds.",
    tools=[real_news_tool_instance]
)
