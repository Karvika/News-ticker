import React, { useState, useEffect } from 'react';
import './NewsBox.css';

function NewsBox() {
    const [news, setNews] = useState([]);
    const [lastUpdated, setLastUpdated] = useState('');

    useEffect(() => {
        fetchNews();
        const interval = setInterval(fetchNews, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchNews = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/news');
            const data = await response.json();
            setNews(data);
            setLastUpdated(new Date().toLocaleTimeString());
        } catch (error) {
            console.error('Error fetching news:', error);
        }
    };

    return (
        <div className="app-container">
            <div className="sidebar">
                <h2>AI Agent Options</h2>
                {/* Add sidebar menu items here */}
            </div>
            <div className="main-content">
                <div className="news-box">
                    <div className="header-badges">
                        <span className="badge google-adk">GOOGLE ADK</span>
                        <span className="badge live">LIVE UPDATES</span>
                        <span className="badge update">EVERY 5 SECONDS</span>
                        <span className="badge gemini">GEMINI FLASH</span>
                    </div>
                    
                    <p className="description">
                        Stay updated with the latest AI news and developments. Our AI news ticker uses
                        Google's ADK and Gemini to bring you real-time updates from the world of artificial intelligence.
                    </p>
                    
                    <div className="last-updated">
                        LAST UPDATED: {lastUpdated}
                    </div>
                    
                    <ul className="news-list">
                        {news.map((item) => (
                            <li key={item.id} className="news-item">
                                <div className="news-number">{item.id}</div>
                                <div className="news-content">
                                    <div className="news-title">
                                        {item.title}
                                        {item.isLatest && <span className="live-badge">LIVE</span>}
                                    </div>
                                    <div className="timestamp">{item.timestamp}</div>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default NewsBox;
