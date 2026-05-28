import { useNavigate } from "react-router-dom";
import "../styles.css";
import logo from "../assets/project-logo.png";

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
        
        {/* Logo Section */}
        <div className="logo-section">
          <div className="logo-wrapper">
            <div className="custom-logo-container">
              <img
                src={logo}
                alt="Health & AI Assistant Logo"
                className="custom-logo"
                style={{
                  width: "200px",
                  height: "200px",
                  objectFit: "contain",
                }}
              />
            </div>
          </div>

          <h1 className="logo-title">Health & AI Assistant</h1>
          <p className="logo-subtitle">
            Your Personal Medical & Machine Learning Expert
          </p>
        </div>

        {/* Action Buttons Section */}
        <div className="action-section">
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
        </div>
      </div>
    </div>
  );
}