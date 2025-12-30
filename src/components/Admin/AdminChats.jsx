import { useState } from "react";

export default function AdminChats() {
  const [activeTab, setActiveTab] = useState("all");
  
  const chatStats = {
    total: 124,
    today: 15,
    health: 67,
    textAnalytics: 43,
    general: 14
  };

  const recentChats = [
    { id: 1, user: "Demo User", message: "What is text analytics?", category: "text_analytics", time: "2 mins ago" },
    { id: 2, user: "John Doe", message: "Headache remedies please", category: "health", time: "5 mins ago" },
    { id: 3, user: "Jane Smith", message: "How to preprocess text?", category: "text_analytics", time: "10 mins ago" },
    { id: 4, user: "Alex Johnson", message: "Fever treatment options", category: "health", time: "15 mins ago" },
    { id: 5, user: "Sam Wilson", message: "Hello there!", category: "general", time: "20 mins ago" },
  ];

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">
          <span className="title-icon">💬</span>
          Chat Analytics
        </h1>
      </div>

      {/* Chat Stats */}
      <div className="stats-cards">
        <div className="stat-card">
          <h3>Total Chats</h3>
          <p className="stat-number">{chatStats.total}</p>
          <p className="stat-sub">All time</p>
        </div>
        <div className="stat-card">
          <h3>Today</h3>
          <p className="stat-number">{chatStats.today}</p>
          <p className="stat-sub">Last 24 hours</p>
        </div>
        <div className="stat-card">
          <h3>Health Topics</h3>
          <p className="stat-number">{chatStats.health}</p>
          <p className="stat-sub">54% of total</p>
        </div>
        <div className="stat-card">
          <h3>Text Analytics</h3>
          <p className="stat-number">{chatStats.textAnalytics}</p>
          <p className="stat-sub">35% of total</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === "all" ? "active" : ""}`}
          onClick={() => setActiveTab("all")}
        >
          All Chats
        </button>
        <button 
          className={`tab ${activeTab === "health" ? "active" : ""}`}
          onClick={() => setActiveTab("health")}
        >
          Health Topics
        </button>
        <button 
          className={`tab ${activeTab === "text" ? "active" : ""}`}
          onClick={() => setActiveTab("text")}
        >
          Text Analytics
        </button>
        <button 
          className={`tab ${activeTab === "monitoring" ? "active" : ""}`}
          onClick={() => setActiveTab("monitoring")}
        >
          Live Monitoring
        </button>
      </div>

      {/* Recent Chats */}
      <div className="content-card">
        <h3>Recent Chat Activity</h3>
        <div className="chats-list">
          {recentChats.map(chat => (
            <div key={chat.id} className="chat-item">
              <div className="chat-header">
                <div className="chat-user">
                  <div className="chat-avatar">{chat.user.charAt(0)}</div>
                  <strong>{chat.user}</strong>
                </div>
                <div className="chat-meta">
                  <span className={`category-badge ${chat.category}`}>
                    {chat.category.replace("_", " ")}
                  </span>
                  <span className="chat-time">{chat.time}</span>
                </div>
              </div>
              <p className="chat-message">{chat.message}</p>
              <div className="chat-actions">
                <button className="action-btn">View Details</button>
                <button className="action-btn">Export</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Category Distribution */}
      <div className="content-card">
        <h3>Category Distribution</h3>
        <div className="distribution-chart">
          <div className="chart-item health">
            <div className="chart-bar" style={{width: `${(chatStats.health / chatStats.total) * 100}%`}}></div>
            <div className="chart-label">Health Topics</div>
            <div className="chart-value">{chatStats.health} ({Math.round((chatStats.health / chatStats.total) * 100)}%)</div>
          </div>
          <div className="chart-item text">
            <div className="chart-bar" style={{width: `${(chatStats.textAnalytics / chatStats.total) * 100}%`}}></div>
            <div className="chart-label">Text Analytics</div>
            <div className="chart-value">{chatStats.textAnalytics} ({Math.round((chatStats.textAnalytics / chatStats.total) * 100)}%)</div>
          </div>
          <div className="chart-item general">
            <div className="chart-bar" style={{width: `${(chatStats.general / chatStats.total) * 100}%`}}></div>
            <div className="chart-label">General</div>
            <div className="chart-value">{chatStats.general} ({Math.round((chatStats.general / chatStats.total) * 100)}%)</div>
          </div>
        </div>
      </div>
    </div>
  );
}