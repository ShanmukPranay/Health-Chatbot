import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles.css";

// Your Render backend URL
const API_BASE_URL = "https://health-chatbot-backend-w4dl.onrender.com";

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
      console.log("Logging in with:", formData.email);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        const userData = {
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          role: data.user.role,
          avatar: data.user.avatar || data.user.name.charAt(0).toUpperCase(),
          token: data.token
        };
        
        localStorage.setItem("auth", "true");
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", data.token);
        
        console.log("✅ Login successful:", userData.email);
        
        setLoading(false);
        navigate("/chat");
      } else {
        setError(data.error || "Login failed. Please check your credentials.");
        setLoading(false);
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Cannot connect to server. Please try again.");
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setFormData({
      email: "demo@example.com",
      password: "demo123"
    });
    setTimeout(() => {
      handleSubmit(new Event("submit"));
    }, 100);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <span className="auth-icon">👨‍⚕️</span>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your Personal Health Assistant</p>
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
            />
            <div className="forgot-password">
              <Link to="/forgot-password" className="auth-link">
                Forgot password?
              </Link>
            </div>
          </div>
          
          <button type="submit" className="auth-button login-btn" disabled={loading}>
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>

        <button onClick={handleDemoLogin} className="auth-button demo-btn" style={{
          marginTop: '15px',
          background: 'rgba(16, 185, 129, 0.1)',
          color: '#10b981',
          border: '2px solid rgba(16, 185, 129, 0.3)'
        }}>
          🚀 Use Demo Account
        </button>
        
        <div className="auth-divider">
          <span>New to Health Assistant?</span>
        </div>
        
        <button onClick={() => navigate("/signup")} className="auth-button signup-btn">
          Create New Account
        </button>
        
        <p className="auth-footer">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}