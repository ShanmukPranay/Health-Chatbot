import React from "react";

export default function Header({ onLogout }) {
  return (
    <div className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="header-avatar">
            <span className="avatar-icon">👨‍⚕️🤖</span>
          </div>
          <div>
            <h1 className="header-title">Health & AI Assistant</h1>
            <p className="header-subtitle">Medical Guidance • Machine Learning Expert</p>
          </div>
        </div>
        <div className="header-right">
          <div className="expertise-tags">
            <span className="tag health-tag">🏥 Health</span>
            <span className="tag ml-tag">🤖 ML/AI</span>
          </div>
          <button 
            onClick={onLogout} 
            className="logout-button"
          >
            <span className="logout-icon">↩</span>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}