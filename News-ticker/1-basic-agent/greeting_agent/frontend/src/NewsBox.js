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
            console.log('News API Response:', data);
            setNews(data);
            setLastUpdated(new Date().toLocaleTimeString());
        } catch (error) {
            console.error('Error fetching news:', error);
        }
    };

    return (
        <div className="app-container">
            <div className="news-box">
                <div className="header-badges">
                    <span className="badge google-adk">🤖 GOOGLE ADK</span>
                    <span className="badge live">⭕ LIVE</span>
                    <span className="badge update">⚡ REAL-TIME</span>
                    <span className="badge gemini">✨ GEMINI</span>
                </div>
                
                <p className="description">
                    Your real-time window into the world of technology. Get instant updates on software development, AI
                    breakthroughs, and tech innovations as they happen.
                </p>
                
                <div className="last-updated">
                    <span className="time-icon">⏰</span> Last Refresh: {lastUpdated}
                </div>
                
                <div className="news-list">
                    {news.map((item, index) => (
                        <a 
                            key={index} 
                            href={item.url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="news-item"
                            style={{ textDecoration: 'none' }}
                        >
                            <div className="number-badge">{index + 1}</div>
                            <div className="news-content">
                                <div className="news-title clickable">
                                    {item.title}
                                    {item.isLatest && <span className="latest">LATEST</span>}
                                    <span className="link-icon">🔗</span>
                                </div>
                                <div className="news-meta">
                                    <span className="news-timestamp">{item.timestamp}</span>
                                    <span className="news-source">Source: {item.source}</span>
                                </div>
                            </div>
                        </a>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default NewsBox;
