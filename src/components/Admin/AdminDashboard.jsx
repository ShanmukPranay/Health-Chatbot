import { useState, useEffect } from "react";
import "../../styles/admin.css";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [recentUsers, setRecentUsers] = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem("auth");
      
      // Fetch admin dashboard data
      const response = await fetch("http://localhost:5000/api/admin/dashboard", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
        
        // Get recent users (first 5)
        if (data.users) {
          setRecentUsers(data.users.slice(0, 5));
        }
        
        // For demo, create sample chat data
        setRecentChats([
          { id: 1, user: "John Doe", message: "Headache remedies?", time: "2 mins ago" },
          { id: 2, user: "Jane Smith", message: "Text analytics intro", time: "5 mins ago" },
          { id: 3, user: "Demo User", message: "Fever treatment", time: "10 mins ago" },
          { id: 4, user: "Alex Johnson", message: "TF-IDF explanation", time: "15 mins ago" },
        ]);
      }
    } catch (error) {
      console.error("Error fetching admin data:", error);
      // For demo purposes, create mock data
      setStats({
        statistics: {
          total_users: 15,
          active_users: 8,
          total_chats: 124,
          premium_users: 3,
          standard_users: 12
        },
        users: [
          { id: 1, name: "Demo User", email: "demo@example.com", role: "Premium User", chat_count: 45 },
          { id: 2, name: "John Doe", email: "john@example.com", role: "Standard User", chat_count: 12 },
          { id: 3, name: "Jane Smith", email: "jane@example.com", role: "Standard User", chat_count: 8 },
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    fetchAdminData();
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">Admin Dashboard</h1>
        <div className="dashboard-actions">
          <button onClick={handleRefresh} className="refresh-btn">
            <span className="refresh-icon">🔄</span> Refresh
          </button>
          <div className="last-updated">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3 className="stat-title">Total Users</h3>
            <p className="stat-value">{stats?.statistics?.total_users || 0}</p>
            <p className="stat-change">
              <span className="positive">+{stats?.statistics?.active_users || 0} active</span>
            </p>
          </div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3 className="stat-title">Total Chats</h3>
            <p className="stat-value">{stats?.statistics?.total_chats || 0}</p>
            <p className="stat-change">
              <span className="positive">Today: {Math.floor((stats?.statistics?.total_chats || 0) / 10)}</span>
            </p>
          </div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-icon">👑</div>
          <div className="stat-content">
            <h3 className="stat-title">Premium Users</h3>
            <p className="stat-value">{stats?.statistics?.premium_users || 0}</p>
            <p className="stat-change">
              <span className="neutral">{Math.round(((stats?.statistics?.premium_users || 0) / (stats?.statistics?.total_users || 1)) * 100)}% of total</span>
            </p>
          </div>
        </div>
        
        <div className="stat-card info">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3 className="stat-title">Avg. Chats/User</h3>
            <p className="stat-value">
              {stats?.statistics?.total_users ? 
                Math.round((stats.statistics.total_chats || 0) / stats.statistics.total_users) : 0}
            </p>
            <p className="stat-change">
              <span className="positive">Engagement Rate</span>
            </p>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === "users" ? "active" : ""}`}
          onClick={() => setActiveTab("users")}
        >
          👥 Users
        </button>
        <button 
          className={`tab-btn ${activeTab === "chats" ? "active" : ""}`}
          onClick={() => setActiveTab("chats")}
        >
          💬 Chats
        </button>
        <button 
          className={`tab-btn ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          📈 Analytics
        </button>
      </div>
      
      {/* Content based on active tab */}
      <div className="tab-content">
        {activeTab === "overview" && (
          <div className="overview-content">
            <div className="content-grid">
              {/* Recent Users */}
              <div className="content-card">
                <h3 className="content-title">
                  <span className="title-icon">👥</span>
                  Recent Users
                </h3>
                <div className="users-list">
                  {recentUsers.length > 0 ? (
                    recentUsers.map(user => (
                      <div key={user.id} className="user-item">
                        <div className="user-avatar-small">
                          {user.name?.charAt(0) || "U"}
                        </div>
                        <div className="user-info">
                          <h4 className="user-name">{user.name}</h4>
                          <p className="user-email">{user.email}</p>
                          <div className="user-meta">
                            <span className="user-role">{user.role}</span>
                            <span className="user-chats">{user.chat_count || 0} chats</span>
                          </div>
                        </div>
                        <button className="user-action-btn">
                          View
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="no-data">No users found</p>
                  )}
                </div>
                <a href="/admin/users" className="view-all-link">
                  View all users →
                </a>
              </div>
              
              {/* Recent Chats */}
              <div className="content-card">
                <h3 className="content-title">
                  <span className="title-icon">💬</span>
                  Recent Chats
                </h3>
                <div className="chats-list">
                  {recentChats.map(chat => (
                    <div key={chat.id} className="chat-item">
                      <div className="chat-user">
                        <div className="chat-avatar">{chat.user.charAt(0)}</div>
                        <span className="chat-username">{chat.user}</span>
                      </div>
                      <p className="chat-message">{chat.message}</p>
                      <span className="chat-time">{chat.time}</span>
                    </div>
                  ))}
                </div>
                <a href="/admin/chats" className="view-all-link">
                  View all chats →
                </a>
              </div>
              
              {/* System Health */}
              <div className="content-card">
                <h3 className="content-title">
                  <span className="title-icon">🏥</span>
                  System Health
                </h3>
                <div className="health-status">
                  <div className="health-item healthy">
                    <span className="health-indicator">●</span>
                    <span className="health-label">API Server</span>
                    <span className="health-value">Online</span>
                  </div>
                  <div className="health-item healthy">
                    <span className="health-indicator">●</span>
                    <span className="health-label">Database</span>
                    <span className="health-value">Connected</span>
                  </div>
                  <div className="health-item healthy">
                    <span className="health-indicator">●</span>
                    <span className="health-label">Email Service</span>
                    <span className="health-value">Simulation Mode</span>
                  </div>
                  <div className="health-item warning">
                    <span className="health-indicator">●</span>
                    <span className="health-label">Storage</span>
                    <span className="health-value">85% Used</span>
                  </div>
                </div>
                <div className="health-actions">
                  <button className="health-btn primary">Run Diagnostics</button>
                  <button className="health-btn secondary">View Logs</button>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="content-card">
                <h3 className="content-title">
                  <span className="title-icon">⚡</span>
                  Quick Actions
                </h3>
                <div className="quick-actions-grid">
                  <button className="quick-action-btn">
                    <span className="action-icon">➕</span>
                    Add New User
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">📧</span>
                    Send Announcement
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">📊</span>
                    Generate Report
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">🔧</span>
                    System Settings
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">🔄</span>
                    Clear Cache
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">📋</span>
                    View Logs
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === "users" && (
          <div className="users-content">
            <h2>User Management</h2>
            <p>This section will show detailed user management features.</p>
          </div>
        )}
        
        {activeTab === "chats" && (
          <div className="chats-content">
            <h2>Chat Analytics</h2>
            <p>This section will show chat statistics and monitoring.</p>
          </div>
        )}
        
        {activeTab === "analytics" && (
          <div className="analytics-content">
            <h2>System Analytics</h2>
            <p>This section will show detailed analytics and reports.</p>
          </div>
        )}
      </div>
    </div>
  );
}