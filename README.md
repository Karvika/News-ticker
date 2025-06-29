# AI News Ticker - Google ADK Application

## What is this Project?

This AI News Ticker is a real-time news application built with **Google ADK (Agent Development Kit)** that fetches and displays the latest AI-related news headlines. The application combines:
- **Real-time news fetching** from multiple sources (RSS feeds, NewsAPI)
- **Google ADK agent architecture** for scalable AI tool integration
- **React frontend** for modern, responsive UI
- **Flask backend** for API services
- **Gemini AI integration** for intelligent content processing

## Architecture Overview

```
React Frontend (Port 3000) ↔ Flask API (Port 5000) ↔ Google ADK Agent ↔ News Sources
     ↓                           ↓                       ↓                   ↓
 NewsBox UI              /api/news endpoint      RealNewsUpdateTool    RSS Feeds + NewsAPI
```

The application uses Google ADK's `LlmAgent` with a custom tool (`RealNewsUpdateTool`) that:
- Fetches news from multiple RSS feeds and NewsAPI
- Filters content for AI-related keywords
- Sorts articles chronologically (latest first)
- Maintains a FIFO queue of 5 most recent articles
- Provides fallback headlines when sources fail

## Project Structure

This AI News Ticker follows the ADK agent structure requirements:

```
News-ticker/
├── 1-basic-agent/
│   └── greeting_agent/           # ADK Agent package directory
│       ├── __init__.py          # Imports agent module
│       ├── agent.py             # Defines root_agent with RealNewsUpdateTool
│       ├── app.py               # Flask API server
│       ├── .env                 # Environment variables (API keys)
│       ├── .env.example         # Environment template
│       └── frontend/            # React application
│           ├── package.json
│           ├── public/
│           │   ├── index.html
│           │   └── manifest.json
│           └── src/
│               ├── index.js
│               ├── index.css
│               ├── NewsBox.js   # Main news component
│               └── NewsBox.css  # Styling
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

### Essential Components:

1. **`agent.py`** - Contains the Google ADK agent with RealNewsUpdateTool
2. **`app.py`** - Flask server that integrates with the ADK agent
3. **`frontend/`** - React application for the news ticker UI
4. **`.env`** - Contains API keys for Google AI and NewsAPI

## Key Google ADK Components

### 1. Agent Configuration (`root_agent`)
```python
root_agent = Agent(
    name="real_ai_news_agent",
    model="gemini-pro",                    # Gemini AI model
    description="Real AI News headlines agent using live news sources",
    instruction="Fetch and return the latest real AI news headlines from news APIs and RSS feeds.",
    tools=[real_news_tool_instance]        # Custom news fetching tool
)
```

### 2. Custom Tool (`RealNewsUpdateTool`)
Inherits from `google.adk.tools.base_tool.BaseTool` and implements:
- **News Source Integration**: RSS feeds (TechCrunch, Ars Technica, ZDNet, etc.) and NewsAPI
- **AI Content Filtering**: Searches for AI-related keywords (OpenAI, ChatGPT, machine learning, etc.)
- **Date Filtering**: Only includes articles from the last 30 days
- **Chronological Sorting**: Most recent articles first
- **FIFO Queue Management**: Maintains exactly 5 news items
- **Error Handling**: SSL bypass, retry logic, fallback content

### 3. Gemini AI Integration
- **Model**: `gemini-pro` for intelligent content processing
- **Configuration**: Via `google.generativeai.configure()`
- **Purpose**: Potential content enhancement and fallback generation
- **API Key**: Secured via environment variables

### 4. Tool Execution Flow
```python
def execute(self, inputs=None):
    # 1. Fetch from RSS feeds and NewsAPI
    # 2. Filter by AI keywords and recent dates
    # 3. Sort chronologically
    # 4. Build FIFO queue with 5 items
    # 5. Return JSON formatted news
```

## Features

### 🔄 Real-Time News Updates
- Fetches latest AI news every 5 seconds
- Displays the most recent article with "LATEST" badge
- Chronological ordering (newest to oldest)

### 📰 Interactive News Experience
- **Clickable Headlines**: Click any news title to read the full article
- **External Links**: Direct links to original news sources (🔗 indicator)
- **Article Details Modal**: Shows source, timestamp, and link when URL unavailable
- **Source Attribution**: Clear source identification for each article

### 📡 Multiple News Sources
- **RSS Feeds**: TechCrunch, Ars Technica, ZDNet, VentureBeat, Wired, etc.
- **NewsAPI**: Additional coverage from major tech publications
- **Fallback Headlines**: Curated content with working links when sources fail

### 🤖 AI-Powered Content Filtering
- Smart keyword matching for AI-related content
- Filters for: OpenAI, ChatGPT, machine learning, AI research, etc.
- Recent content only (last 30 days)

### 📱 Modern UI/UX
- Responsive React frontend with smooth animations
- Clean, modern design with gradient backgrounds
- FIFO queue visualization (5 items maximum)
- Real publication timestamps and source information
- **Interactive Elements**: Clickable headlines with hover effects
- **Article Access**: Direct links to full articles in new tabs
- **Modal Details**: Popup with article metadata and actions
- **Visual Indicators**: Link icons and hover animations

### 🛡️ Robust Error Handling
- SSL certificate bypass for problematic feeds
- Retry mechanisms for network failures
- Graceful fallback to curated content
- Comprehensive logging and debugging

## How It Works

### Data Flow
```
1. Frontend (React) requests news every 5 seconds
   ↓
2. Flask API calls ADK agent's tool
   ↓
3. RealNewsUpdateTool fetches from multiple sources
   ↓
4. Content is filtered, sorted, and formatted
   ↓
5. JSON response returns to frontend
   ↓
6. UI updates with latest news in FIFO order
```

### News Processing Pipeline
1. **Fetch**: Retrieve articles from RSS feeds and NewsAPI
2. **Filter**: Apply AI keyword matching and date filtering
3. **Sort**: Order by actual publication date (most recent first)
4. **Queue**: Maintain FIFO queue with exactly 5 items
5. **Format**: Structure data for frontend consumption
6. **Serve**: Return JSON response via Flask API

## API Endpoints

### GET /api/news
Returns the current news queue as JSON:

```json
[
  {
    "id": "1",
    "title": "OpenAI releases GPT-4 Turbo with enhanced capabilities",
    "timestamp": "Released: 02:30 PM - Jun 29",
    "isLatest": true,
    "source": "TechCrunch",
    "url": "https://techcrunch.com/article-url"
  },
  // ... 4 more items
]
```

### User Interactions

- **Click Headlines**: Clicking a news title opens the full article in a new tab
- **Link Indicators**: Headlines with available links show a 🔗 icon
- **Modal Fallback**: If no direct link, clicking shows an article details modal
- **Hover Effects**: Visual feedback when hovering over clickable elements

## Getting Started

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Node.js**: Required for the React frontend (Node 14+ recommended)
3. **API Keys**: 
   - Google AI API key (required)
   - NewsAPI key (optional, for additional news sources)

### Installation & Setup

1. **Clone and Navigate**:
```bash
cd News-ticker/1-basic-agent/greeting_agent
```

2. **Install Python Dependencies**:
```bash
pip install -r ../../../requirements.txt
```

3. **Set up Environment Variables**:
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your API keys:
GOOGLE_API_KEY=your_google_ai_api_key_here
NEWS_API_KEY=your_newsapi_key_here  # Optional
```

4. **Install Frontend Dependencies**:
```bash
cd frontend
npm install
```

### Running the Application

#### Method 1: Full Stack Application (Recommended)

1. **Start the Flask Backend**:
```bash
# From greeting_agent directory
python app.py
```
The Flask API will run on `http://localhost:5000`

2. **Start the React Frontend** (in a new terminal):
```bash
# From greeting_agent/frontend directory
npm start
```
The React app will run on `http://localhost:3000`

3. **Access the Application**:
Open `http://localhost:3000` in your browser to see the AI News Ticker in action!

#### Method 2: ADK Development Mode

You can also test the agent using ADK's built-in tools:

1. **ADK Web UI**:
```bash
# From 1-basic-agent directory
adk web
```
Access at `http://localhost:8000`

2. **ADK Terminal**:
```bash
adk run real_ai_news_agent
```

3. **ADK API Server**:
```bash
adk api_server
```

## Troubleshooting

### Common Issues

1. **No News Appearing**:
   - Check if Flask server is running on port 5000
   - Verify internet connection for RSS feeds
   - Check console for error messages

2. **API Key Errors**:
   - Ensure `.env` file exists with valid `GOOGLE_API_KEY`
   - NewsAPI key is optional but recommended

3. **SSL Certificate Errors**:
   - The app includes SSL bypass mechanisms
   - Check terminal output for specific feed failures

4. **Old News Appearing**:
   - The app filters for articles from last 30 days
   - Some RSS feeds may have stale content
   - Fallback headlines provide fresh content when needed

### Development Tips

- **Backend Debugging**: Check Flask terminal for detailed logs
- **Frontend Debugging**: Open browser developer tools
- **ADK Testing**: Use `adk web` for direct agent interaction
- **API Testing**: Test `/api/news` endpoint directly in browser

## Technical Stack

- **Backend**: Python, Flask, Google ADK, Gemini AI
- **Frontend**: React, JavaScript, CSS
- **News Sources**: RSS feeds, NewsAPI
- **Development**: Git, Environment variables
- **Deployment**: Local development server

## Contributing

To extend this application:

1. **Add News Sources**: Modify the `reliable_feeds` list in `agent.py`
2. **Enhance Filtering**: Update `ai_keywords` for better content matching
3. **UI Improvements**: Modify React components in `frontend/src/`
4. **New Features**: Add additional tools to the ADK agent

This AI News Ticker demonstrates the power of Google ADK for building intelligent, real-time applications with modern web technologies.
