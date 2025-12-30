import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles.css";

const API_BASE_URL = "http://localhost:5000/api";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: "",
    otp: "",
    newPassword: "",
    confirmPassword: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [resetToken, setResetToken] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError("");
  };

  // Request OTP
  const handleRequestOTP = async () => {
    if (!formData.email) {
      setError("Please enter your email");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/request-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.email })
      });

      const data = await response.json();
      
      if (response.ok) {
        // If in development mode, show OTP from response
        if (data.otp) {
          setMessage(`📧 OTP sent! Check Flask terminal for OTP: ${data.otp}`);
        } else {
          setMessage(`📧 OTP sent to ${formData.email}! Check your email.`);
        }
        setStep(2);
      } else {
        setError(data.error || "Failed to send OTP");
      }
    } catch (err) {
      setError("Unable to connect to server. Please try again.");
      console.error("OTP Request Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP
  const handleVerifyOTP = async () => {
    if (!formData.otp || formData.otp.length !== 6) {
      setError("Please enter a valid 6-digit OTP");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          otp: formData.otp
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setResetToken(data.reset_token);
        setMessage("✅ OTP verified! Set your new password.");
        setStep(3);
      } else {
        setError(data.error || "Invalid OTP");
      }
    } catch (err) {
      setError("Unable to connect to server. Please try again.");
      console.error("OTP Verify Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Reset Password
  const handleResetPassword = async () => {
    if (!formData.newPassword || !formData.confirmPassword) {
      setError("Please fill in all fields");
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    if (formData.newPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reset_token: resetToken,
          new_password: formData.newPassword
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage("✅ Password reset successful! Redirecting to login...");
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setError(data.error || "Failed to reset password");
      }
    } catch (err) {
      setError("Unable to connect to server. Please try again.");
      console.error("Reset Password Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <span className="auth-icon">🔑</span>
          <h1 className="auth-title">
            {step === 1 && "Reset Password"}
            {step === 2 && "Enter OTP"}
            {step === 3 && "New Password"}
          </h1>
          <p className="auth-subtitle">
            {step === 1 && "Enter your email to receive OTP"}
            {step === 2 && "Enter the 6-digit OTP sent to your email"}
            {step === 3 && "Create your new password"}
          </p>
        </div>

        {message && (
          <div className="success-message">
            <span>✅</span> {message}
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="auth-form">
          {/* Step 1: Email Input */}
          {step === 1 && (
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                name="email"
                className="form-input"
                placeholder="Enter your registered email"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
                autoComplete="email"
              />
              <button
                onClick={handleRequestOTP}
                className="auth-button login-btn"
                disabled={loading}
                style={{ marginTop: "20px" }}
              >
                {loading ? "Sending OTP..." : "Send OTP"}
              </button>
            </div>
          )}

          {/* Step 2: OTP Input */}
          {step === 2 && (
            <div className="form-group">
              <label className="form-label">6-Digit OTP</label>
              <input
                type="text"
                name="otp"
                className="form-input"
                placeholder="Enter 6-digit OTP"
                value={formData.otp}
                onChange={handleChange}
                maxLength="6"
                pattern="\d*"
                disabled={loading}
                style={{ textAlign: 'center', letterSpacing: '10px', fontSize: '24px' }}
              />
              <div className="otp-hint">
                <small>Check Flask terminal console for OTP (in development)</small>
              </div>
              <button
                onClick={handleVerifyOTP}
                className="auth-button login-btn"
                disabled={loading}
                style={{ marginTop: "20px" }}
              >
                {loading ? "Verifying..." : "Verify OTP"}
              </button>
              <div className="resend-otp" style={{ textAlign: 'center', marginTop: '15px' }}>
                <button 
                  onClick={handleRequestOTP} 
                  className="resend-btn"
                  disabled={loading}
                >
                  Resend OTP
                </button>
              </div>
            </div>
          )}

          {/* Step 3: New Password */}
          {step === 3 && (
            <>
              <div className="form-group">
                <label className="form-label">New Password</label>
                <input
                  type="password"
                  name="newPassword"
                  className="form-input"
                  placeholder="Enter new password"
                  value={formData.newPassword}
                  onChange={handleChange}
                  disabled={loading}
                  autoComplete="new-password"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  className="form-input"
                  placeholder="Confirm new password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  disabled={loading}
                  autoComplete="new-password"
                />
              </div>
              <button
                onClick={handleResetPassword}
                className="auth-button login-btn"
                disabled={loading}
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </>
          )}
        </div>

        <div className="auth-footer" style={{ marginTop: '20px' }}>
          <p>
            Remember your password?{" "}
            <Link to="/login" className="auth-link">
              Back to Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}