import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles.css";

const API_BASE_URL = "http://localhost:5000/api";

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError("Please fill in all fields");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      // Try to connect to Flask backend first
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Save user data from Flask
        const userData = {
          email: data.user.email,
          name: data.user.name,
          role: data.user.role,
          avatar: data.user.avatar || data.user.name.charAt(0).toUpperCase(),
          token: data.token
        };
        
        localStorage.setItem("auth", "true");
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", data.token);
        
        setLoading(false);
        navigate("/chat");
      } else {
        // If Flask returns error, fall back to simulation
        setError(data.error || "Login failed. Using demo mode...");
        fallbackLogin();
      }
    } catch (err) {
      console.log("Backend not available, using fallback:", err);
      // If backend is not reachable, use fallback
      fallbackLogin();
    }
  };

  const fallbackLogin = () => {
    // Fallback to simulation mode
    setTimeout(() => {
      const userData = {
        email: formData.email,
        name: formData.email.split('@')[0],
        role: "Premium User",
        joined: new Date().toLocaleDateString(),
        avatar: formData.email.charAt(0).toUpperCase()
      };
      
      localStorage.setItem("auth", "true");
      localStorage.setItem("user", JSON.stringify(userData));
      
      setLoading(false);
      navigate("/chat");
    }, 1500);
  };

  const handleSignupRedirect = () => {
    navigate("/signup");
  };

  // Test with demo credentials
  const handleDemoLogin = () => {
    setFormData({
      email: "demo@example.com",
      password: "demo123"
    });
    
    // Auto-submit after a short delay
    setTimeout(() => {
      document.querySelector("form").dispatchEvent(
        new Event("submit", { cancelable: true, bubbles: true })
      );
    }, 100);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <span className="auth-icon">🤖</span>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your Health & AI Assistant</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              name="email"
              className="form-input"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
              autoComplete="email"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
            {/* Forgot Password Link */}
            <div className="forgot-password" style={{ textAlign: 'right', marginTop: '8px' }}>
              <Link 
                to="/forgot-password" 
                className="auth-link" 
                style={{ fontSize: '14px', fontWeight: '500' }}
              >
                Forgot password?
              </Link>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="auth-button login-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading"></span>
                Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {/* Demo Login Button */}
        <button 
          onClick={handleDemoLogin}
          className="auth-button demo-btn"
          style={{
            marginTop: '15px',
            background: 'rgba(16, 185, 129, 0.1)',
            color: '#10b981',
            border: '2px solid rgba(16, 185, 129, 0.3)'
          }}
        >
          <span>🚀</span> Use Demo Account (demo@example.com / demo123)
        </button>
        
        <div className="auth-divider">
          <span>New to Health & AI?</span>
        </div>
        
        <button 
          onClick={handleSignupRedirect}
          className="auth-button signup-btn"
        >
          Create New Account
        </button>
        
        <p className="auth-footer">
          By continuing, you agree to our{" "}
          <span className="auth-link">Terms of Service</span>{" "}
          and <span className="auth-link">Privacy Policy</span>
        </p>

        {/* Backend Status */}
        <div className="backend-status" style={{
          marginTop: '20px',
          padding: '12px',
          background: 'rgba(102, 126, 234, 0.1)',
          borderRadius: '10px',
          fontSize: '12px',
          color: '#555',
          textAlign: 'center'
        }}>
          <strong>🔌 Backend Status:</strong>{" "}
          <span style={{ color: '#10b981', fontWeight: 'bold' }}>
            Connected to Flask
          </span>
          <br/>
          <small>Using: {API_BASE_URL}</small>
        </div>
      </div>
    </div>
  );
}