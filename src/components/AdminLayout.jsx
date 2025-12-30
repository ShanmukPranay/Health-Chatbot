import { useEffect, useState } from "react";
import { useNavigate, Outlet } from "react-router-dom";
import "../styles/admin.css";

export default function AdminLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication and admin status
    const checkAdminAccess = async () => {
      const auth = localStorage.getItem("auth");
      const userData = localStorage.getItem("user");
      
      if (!auth) {
        navigate("/login");
        return;
      }
      
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        
        // Check if user is admin
        const isUserAdmin = parsedUser.role === "Admin" || 
                           parsedUser.role === "Super Admin" || 
                           parsedUser.role === "Administrator" ||
                           parsedUser.role === "Premium User";
        
        if (!isUserAdmin) {
          alert("❌ Access Denied: Admin privileges required");
          navigate("/chat");
          return;
        }
        
        setIsAdmin(true);
      }
      
      setLoading(false);
    };
    
    checkAdminAccess();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleBackToChat = () => {
    navigate("/chat");
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Checking admin privileges...</p>
      </div>
    );
  }

  if (!isAdmin || !user) {
    return null;
  }

  return (
    <div className="admin-container">
      {/* Admin Sidebar */}
      <div className="admin-sidebar">
        <div className="admin-header">
          <h2 className="admin-title">
            <span className="admin-icon">👑</span>
            Admin Dashboard
          </h2>
          <p className="admin-subtitle">Health & AI Assistant</p>
        </div>
        
        <div className="admin-user-info">
          <div className="admin-avatar">
            {user.avatar || user.name?.charAt(0) || "A"}
          </div>
          <div className="admin-user-details">
            <h3 className="admin-user-name">{user.name}</h3>
            <p className="admin-user-role">
              <span className={`role-badge ${user.role.toLowerCase().replace(" ", "-")}`}>
                {user.role}
              </span>
            </p>
            <p className="admin-user-email">{user.email}</p>
          </div>
        </div>
        
        <nav className="admin-nav">
          <ul>
            <li>
              <a href="/admin/dashboard" className="nav-link active">
                <span className="nav-icon">📊</span>
                Dashboard
              </a>
            </li>
            <li>
              <a href="/admin/users" className="nav-link">
                <span className="nav-icon">👥</span>
                User Management
              </a>
            </li>
            <li>
              <a href="/admin/chats" className="nav-link">
                <span className="nav-icon">💬</span>
                Chat Analytics
              </a>
            </li>
            <li>
              <a href="/admin/system" className="nav-link">
                <span className="nav-icon">⚙️</span>
                System Settings
              </a>
            </li>
            <li>
              <a href="/admin/feedback" className="nav-link">
                <span className="nav-icon">📝</span>
                User Feedback
              </a>
            </li>
          </ul>
        </nav>
        
        <div className="admin-actions">
          <button onClick={handleBackToChat} className="action-btn back-btn">
            <span>←</span> Back to Chat
          </button>
          <button onClick={handleLogout} className="action-btn logout-btn">
            <span>🚪</span> Logout
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="admin-main">
        <div className="admin-content">
          <Outlet />
        </div>
        
        <div className="admin-footer">
          <p>© 2024 Health & AI Assistant Admin Panel</p>
          <p className="footer-note">Restricted Access - For Administrators Only</p>
        </div>
      </div>
    </div>
  );
}