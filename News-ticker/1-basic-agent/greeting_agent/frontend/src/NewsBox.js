import React, { useState, useEffect, useCallback } from 'react';
import './NewsBox.css';

function NewsBox() {
    const [news, setNews] = useState([]);
    const [lastUpdated, setLastUpdated] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const getCategoryIcon = (category) => {
        const icons = {
            'AI & Machine Learning': '🧠',
            'Software Development': '💻',
            'Hardware & Gadgets': '🔧',
            'Cybersecurity': '🔒',
            'Business Tech': '💼',
            'Gaming': '🎮',
            'Innovation': '💡',
            'Digital Culture': '🌐'
        };
        return icons[category] || '📱';
    };

    const fetchNews = useCallback(async () => {
        try {
            // Only show loading on initial fetch
            if (!news.length) {
                setIsLoading(true);
            }
            // Show subtle refresh indicator for subsequent fetches
            setIsRefreshing(true);
            
            const response = await fetch('http://localhost:5000/api/news');
            if (!response.ok) {
                throw new Error('Failed to fetch news');
            }

            const data = await response.json();
            
            if (Array.isArray(data) && data.length > 0) {
                setNews(data);
                setLastUpdated(new Date().toLocaleTimeString());
                setError(null);
            }
        } catch (error) {
            console.error('Error fetching news:', error);
            setError('Failed to update news');
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    }, []); // Remove news.length dependency to prevent unnecessary re-renders

    useEffect(() => {
        // Initial fetch
        fetchNews();

        // Set up interval for subsequent fetches
        const interval = setInterval(() => {
            if (!isRefreshing) {
                fetchNews();
            }
        }, 5000);

        // Cleanup on unmount
        return () => clearInterval(interval);
    }, []); // Empty dependency array since we handle isRefreshing check inside the interval

    if (isLoading) {
        return (
            <div className="app-container">
                <div className="news-box">
                    <div className="loading-overlay">
                        <div className="loading-spinner"></div>
                        <span>Loading latest news...</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="app-container">
            <div className="news-box">
                <div className="header-badges">
                    <span className="badge google-adk">🤖 GOOGLE ADK</span>
                    <span className="badge live">⚡ LIVE</span>
                    <span className="badge update">📰 NEWS</span>
                    <span className="badge gemini">✨ GEMINI</span>
                </div>
                
                <p className="description">
                    Your real-time window into the world of technology. Get instant updates on software development, AI
                    breakthroughs, and tech innovations as they happen.
                </p>
                
                <div className="last-updated">
                    <span className="time-icon">⏰</span>
                    Last Refresh: {lastUpdated}
                    {isRefreshing && <span className="refresh-indicator">⟳</span>}
                    {error && <span className="error-message">{error}</span>}
                </div>
                
                <div className="news-list">
                    {news.map((item, index) => (
                        <a 
                            key={item.id || index} 
                            href={item.url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="news-item"
                        >
                            <div className="number-badge">{index + 1}</div>
                            <div className="news-content">
                                <div className="news-title">
                                    {item.title}
                                    {item.isLatest && <span className="latest">NEW</span>}
                                    <span className="link-icon">↗</span>
                                </div>
                                <div className="news-meta">
                                    <span className="news-timestamp">
                                        <span className="meta-icon">🕒</span> {item.timestamp}
                                    </span>
                                    <span className="news-source">
                                        <span className="meta-icon">📰</span> {item.source}
                                    </span>
                                    <span 
                                        className="news-category" 
                                        data-category={item.category}
                                    >
                                        {getCategoryIcon(item.category)} {item.category}
                                    </span>
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
