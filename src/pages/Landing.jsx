import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Background Animation */}
      <div className="bg-animation">
        <div className="circle circle-1"></div>
        <div className="circle circle-2"></div>
        <div className="circle circle-3"></div>
        <div className="circle circle-4"></div>
      </div>

      {/* Main Content */}
      <div className="landing-container">
        {/* Logo Section - UPDATED */}
        <div className="logo-section">
          <div className="logo-wrapper">
            <div className="custom-logo-container">
              <img 
                src="/project logo.png"  // Your image path
                alt="Health & AI Assistant Logo" 
                className="custom-logo"
                style={{
                  width: "180px",  // Reduced from default
                  height: "180px", // Reduced from default
                  objectFit: "contain"
                }}
              />
              <div className="logo-overlay-text"></div>
            </div>
          </div>
          
          <h1 className="logo-title">Health & AI Assistant</h1>
          <p className="logo-subtitle">Your Personal Medical & Machine Learning Expert</p>
        </div>

        {/* Welcome Message */}
        <div className="welcome-section">
          <h2 className="welcome-title">Welcome</h2>
          <p className="welcome-description">
            Get instant health advice and learn machine learning concepts 
            from our intelligent AI assistant. Your one-stop solution for 
            medical guidance and AI education.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="action-section">
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">👨‍⚕️</div>
              <h3>Health Assistant</h3>
              <p>Get instant medical advice for common symptoms</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>ML Expert</h3>
              <p>Learn machine learning concepts & programming</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">💬</div>
              <h3>24/7 Chat</h3>
              <p>Always available to answer your questions</p>
            </div>
          </div>

          <div className="action-buttons">
            <button 
              onClick={() => navigate("/login")}
              className="action-btn primary-btn"
            >
              <span className="btn-icon"></span>
              Login to Your Account
            </button>
            
            <button 
              onClick={() => navigate("/signup")}
              className="action-btn secondary-btn"
            >
              <span className="btn-icon"></span>
              Create New Account
            </button>
            
            <button 
              onClick={() => navigate("/chat")}
              className="action-btn guest-btn"
            >
              <span className="btn-icon"></span>
              Try as Guest
            </button>
          </div>

          {/* Quick Stats */}
          <div className="stats-section">
            <div className="stat-item">
              <div className="stat-number">500+</div>
              <div className="stat-label">Health Topics</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">200+</div>
              <div className="stat-label">ML Concepts</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">24/7</div>
              <div className="stat-label">Availability</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="landing-footer">
          <p className="footer-text">
            © 2024 Health & AI Assistant. All rights reserved.
          </p>
          <p className="footer-links">
            <span>Privacy Policy</span>
            <span>•</span>
            <span>Terms of Service</span>
            <span>•</span>
            <span>Contact Us</span>
          </p>
        </div>
      </div>
    </div>
  );
}