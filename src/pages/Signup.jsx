import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles.css";

const API_BASE_URL = "http://localhost:5000/api";

export default function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
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
    
    // Validation
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError("Please fill in all fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      // Try Flask backend
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
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
          avatar: data.user.name.charAt(0).toUpperCase(),
          token: data.token
        };
        
        localStorage.setItem("auth", "true");
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", data.token);
        
        navigate("/chat");
      } else {
        setError(data.error || "Registration failed");
      }
    } catch (err) {
      console.log("Backend not available, using fallback:", err);
      // Fallback to local storage
      const userData = {
        email: formData.email,
        name: formData.name,
        role: "Standard User",
        joined: new Date().toLocaleDateString(),
        avatar: formData.name.charAt(0).toUpperCase()
      };
      
      localStorage.setItem("auth", "true");
      localStorage.setItem("user", JSON.stringify(userData));
      
      setTimeout(() => {
        setLoading(false);
        navigate("/chat");
      }, 1500);
      return;
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <span className="auth-icon">✨</span>
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join Health & AI Assistant today</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              name="name"
              className="form-input"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={handleChange}
              required
              autoComplete="name"
            />
          </div>

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
              placeholder="Create a password (min 6 chars)"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              className="form-input"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="auth-button login-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="loading"></span>
                Creating Account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <button 
          type="button" 
          className="auth-button signup-btn"
          onClick={() => navigate("/login")}
        >
          Already have an account? Sign In
        </button>

        <div className="auth-footer">
          <p>
            By creating an account, you agree to our{" "}
            <Link to="#" className="auth-link">Terms of Service</Link> and{" "}
            <Link to="#" className="auth-link">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  );
}