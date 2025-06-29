import React, { useState, useEffect } from 'react';
import './NewsBox.css';

function NewsBox() {
    const [news, setNews] = useState([]);
    const [lastUpdated, setLastUpdated] = useState('');
    const [selectedArticle, setSelectedArticle] = useState(null);

    useEffect(() => {
        fetchNews();
        const interval = setInterval(fetchNews, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchNews = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/news');
            const data = await response.json();
            // Data is already sorted with latest news first
            setNews(data);
            setLastUpdated(new Date().toLocaleTimeString());
        } catch (error) {
            console.error('Error fetching news:', error);
        }
    };

    const handleNewsClick = (item) => {
        if (item.url) {
            // Open the original article in a new tab
            window.open(item.url, '_blank', 'noopener,noreferrer');
        } else {
            // If no URL, show a modal with more details
            setSelectedArticle(item);
        }
    };

    const closeModal = () => {
        setSelectedArticle(null);
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
                        {news.map((item, index) => (
                            <li key={`${item.id}-${index}`} className="news-item">
                                <div className="news-number">{item.id}</div>
                                <div className="news-content">
                                    <div 
                                        className={`news-title ${item.url ? 'clickable' : ''}`}
                                        onClick={() => handleNewsClick(item)}
                                        title={item.url ? 'Click to read full article' : 'Click for more details'}
                                    >
                                        {item.title}
                                        {item.isLatest && <span className="live-badge">LATEST</span>}
                                        {item.url && <span className="link-indicator">🔗</span>}
                                    </div>
                                    <div className="news-meta">
                                        <span className="timestamp">{item.timestamp}</span>
                                        <span className="source">Source: {item.source}</span>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                    
                    {/* Modal for article details */}
                    {selectedArticle && (
                        <div className="modal-overlay" onClick={closeModal}>
                            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                                <div className="modal-header">
                                    <h3>Article Details</h3>
                                    <button className="close-button" onClick={closeModal}>×</button>
                                </div>
                                <div className="modal-body">
                                    <h4>{selectedArticle.title}</h4>
                                    <div className="article-meta">
                                        <p><strong>Source:</strong> {selectedArticle.source}</p>
                                        <p><strong>Published:</strong> {selectedArticle.timestamp}</p>
                                    </div>
                                    <div className="article-actions">
                                        {selectedArticle.url ? (
                                            <a 
                                                href={selectedArticle.url} 
                                                target="_blank" 
                                                rel="noopener noreferrer"
                                                className="read-more-button"
                                            >
                                                Read Full Article 🔗
                                            </a>
                                        ) : (
                                            <p className="no-link">Full article link not available</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default NewsBox;
