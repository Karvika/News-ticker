import React, { useState, useEffect } from 'react';
import './NewsBox.css';

function FastNewsBox() {
    const [news, setNews] = useState([]);
    const [lastUpdated, setLastUpdated] = useState('');
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchNews();
        const interval = setInterval(fetchNews, 30000); // Every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchNews = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/news');
            const data = await response.json();
            if (data && Array.isArray(data)) {
                setNews(data.slice(0, 5)); // Ensure only 5 latest items
                setLastUpdated(new Date().toLocaleTimeString());
            }
        } catch (error) {
            console.error('Error fetching news:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleNewsClick = (article) => {
        if (article.url) {
            window.open(article.url, '_blank', 'noopener,noreferrer');
        }
    };

    return (
        <div className="app-container">
            <div className="news-box">
                <div className="header-badges">
                    <span className="badge google-adk">GOOGLE ADK</span>
                    <span className="badge live">LIVE</span>
                    <span className="badge update">30s UPDATE</span>
                    <span className="badge gemini">GEMINI</span>
                </div>
                
                <p className="description">
                    Global technology news ticker bringing you the latest updates from around the world.
                </p>
                
                <div className="last-updated">
                    Last updated: {lastUpdated}
                </div>

                <ul className="news-list">
                    {news.map((item, index) => (
                        <li key={index} className="news-item">
                            <div className="news-content">
                                <div 
                                    className={`news-title ${item.url ? 'clickable' : ''}`}
                                    onClick={() => handleNewsClick(item)}
                                    title={item.url ? 'Click to read full article' : ''}
                                >
                                    {item.title}
                                    {item.url && <span className="link-indicator">🔗</span>}
                                </div>
                                <div className="news-meta">
                                    <span className="source">{item.source}</span>
                                    {item.timestamp && (
                                        <span className="timestamp">{item.timestamp}</span>
                                    )}
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
                
                {loading && <div className="loading">Updating...</div>}
            </div>
        </div>
    );
}

export default FastNewsBox;
