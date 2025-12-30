import { useState } from "react";

export default function AdminFeedback() {
  const [filter, setFilter] = useState("all");
  
  const feedbacks = [
    { id: 1, user: "John Doe", email: "john@example.com", rating: 5, message: "Excellent chatbot! Very helpful for text analytics.", type: "feature", date: "2024-01-15" },
    { id: 2, user: "Jane Smith", email: "jane@example.com", rating: 4, message: "Health advice was accurate. Could use more details.", type: "general", date: "2024-01-14" },
    { id: 3, user: "Demo User", email: "demo@example.com", rating: 3, message: "Found a bug in the chat history saving.", type: "bug", date: "2024-01-13" },
    { id: 4, user: "Alex Johnson", email: "alex@example.com", rating: 5, message: "Love the text preprocessing examples!", type: "feature", date: "2024-01-12" },
    { id: 5, user: "Anonymous", email: null, rating: 2, message: "UI could be improved. Too many clicks.", type: "general", date: "2024-01-11" },
  ];

  const filteredFeedbacks = filter === "all" 
    ? feedbacks 
    : feedbacks.filter(f => f.type === filter);

  const stats = {
    total: feedbacks.length,
    averageRating: (feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length).toFixed(1),
    bugs: feedbacks.filter(f => f.type === 'bug').length,
    features: feedbacks.filter(f => f.type === 'feature').length,
  };

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">
          <span className="title-icon">📝</span>
          User Feedback
        </h1>
      </div>

      {/* Feedback Stats */}
      <div className="stats-cards">
        <div className="stat-card">
          <h3>Total Feedback</h3>
          <p className="stat-number">{stats.total}</p>
          <p className="stat-sub">All submissions</p>
        </div>
        <div className="stat-card">
          <h3>Avg. Rating</h3>
          <p className="stat-number">{stats.averageRating}/5</p>
          <p className="stat-sub">User satisfaction</p>
        </div>
        <div className="stat-card">
          <h3>Bug Reports</h3>
          <p className="stat-number">{stats.bugs}</p>
          <p className="stat-sub">Issues found</p>
        </div>
        <div className="stat-card">
          <h3>Feature Requests</h3>
          <p className="stat-number">{stats.features}</p>
          <p className="stat-sub">New ideas</p>
        </div>
      </div>

      {/* Filters */}
      <div className="feedback-filters">
        <button 
          className={`filter-btn ${filter === "all" ? "active" : ""}`}
          onClick={() => setFilter("all")}
        >
          All Feedback
        </button>
        <button 
          className={`filter-btn ${filter === "bug" ? "active" : ""}`}
          onClick={() => setFilter("bug")}
        >
          Bug Reports
        </button>
        <button 
          className={`filter-btn ${filter === "feature" ? "active" : ""}`}
          onClick={() => setFilter("feature")}
        >
          Feature Requests
        </button>
        <button 
          className={`filter-btn ${filter === "general" ? "active" : ""}`}
          onClick={() => setFilter("general")}
        >
          General Feedback
        </button>
      </div>

      {/* Feedback List */}
      <div className="feedback-list">
        {filteredFeedbacks.map(feedback => (
          <div key={feedback.id} className="feedback-card">
            <div className="feedback-header">
              <div className="feedback-user">
                <div className="feedback-avatar">
                  {feedback.user ? feedback.user.charAt(0) : "A"}
                </div>
                <div className="user-details">
                  <strong>{feedback.user || "Anonymous"}</strong>
                  <p>{feedback.email || "No email provided"}</p>
                </div>
              </div>
              <div className="feedback-meta">
                <div className="feedback-rating">
                  {"★".repeat(feedback.rating)}
                  {"☆".repeat(5 - feedback.rating)}
                </div>
                <span className={`feedback-type ${feedback.type}`}>
                  {feedback.type}
                </span>
                <span className="feedback-date">{feedback.date}</span>
              </div>
            </div>
            
            <div className="feedback-message">
              <p>{feedback.message}</p>
            </div>
            
            <div className="feedback-actions">
              <button className="action-btn primary">
                <span>✅</span> Mark as Resolved
              </button>
              <button className="action-btn">
                <span>📧</span> Reply
              </button>
              <button className="action-btn">
                <span>📋</span> Add Note
              </button>
              <button className="action-btn delete">
                <span>🗑️</span> Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* No Feedback */}
      {filteredFeedbacks.length === 0 && (
        <div className="no-feedback">
          <div className="no-data-icon">📝</div>
          <h3>No feedback found</h3>
          <p>No {filter !== "all" ? filter : ""} feedback submissions yet.</p>
        </div>
      )}
    </div>
  );
}