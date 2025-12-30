import { useState, useEffect } from "react";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRole, setSelectedRole] = useState("all");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("auth");
      const response = await fetch("http://localhost:5000/api/admin/users", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      // Mock data for demo
      setUsers([
        { id: 1, name: "Admin User", email: "admin@example.com", role: "Admin", is_active: true, chat_count: 0 },
        { id: 2, name: "Demo User", email: "demo@example.com", role: "Premium User", is_active: true, chat_count: 45 },
        { id: 3, name: "John Doe", email: "john@example.com", role: "Standard User", is_active: true, chat_count: 12 },
        { id: 4, name: "Jane Smith", email: "jane@example.com", role: "Standard User", is_active: false, chat_count: 8 },
        { id: 5, name: "Alex Johnson", email: "alex@example.com", role: "Standard User", is_active: true, chat_count: 3 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === "all" || user.role === selectedRole;
    return matchesSearch && matchesRole;
  });

  const handleUserAction = (userId, action) => {
    alert(`${action} user ${userId}`);
    // Implement user actions here
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Loading users...</p>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">
          <span className="title-icon">👥</span>
          User Management
        </h1>
        <button className="btn-primary" onClick={fetchUsers}>
          <span>🔄</span> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        <div className="filter-options">
          <select 
            value={selectedRole} 
            onChange={(e) => setSelectedRole(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Roles</option>
            <option value="Admin">Admin</option>
            <option value="Premium User">Premium</option>
            <option value="Standard User">Standard</option>
          </select>
          
          <button className="btn-secondary">
            <span>➕</span> Add New User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Chats</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map(user => (
              <tr key={user.id}>
                <td className="user-id">#{user.id}</td>
                <td>
                  <div className="user-cell">
                    <div className="user-avatar-small">
                      {user.name.charAt(0)}
                    </div>
                    <div className="user-info">
                      <strong>{user.name}</strong>
                    </div>
                  </div>
                </td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role.toLowerCase().replace(" ", "-")}`}>
                    {user.role}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <div className="chat-count">
                    <span className="count-number">{user.chat_count || 0}</span>
                    <span className="count-label">chats</span>
                  </div>
                </td>
                <td>
                  <div className="action-buttons">
                    <button 
                      className="action-btn view-btn"
                      onClick={() => handleUserAction(user.id, 'view')}
                    >
                      👁️ View
                    </button>
                    <button 
                      className="action-btn edit-btn"
                      onClick={() => handleUserAction(user.id, 'edit')}
                    >
                      ✏️ Edit
                    </button>
                    <button 
                      className="action-btn delete-btn"
                      onClick={() => handleUserAction(user.id, 'delete')}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Stats */}
      <div className="stats-summary">
        <div className="stat-item">
          <span className="stat-label">Total Users:</span>
          <span className="stat-value">{users.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Active:</span>
          <span className="stat-value">
            {users.filter(u => u.is_active).length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Premium:</span>
          <span className="stat-value">
            {users.filter(u => u.role === 'Premium User').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Standard:</span>
          <span className="stat-value">
            {users.filter(u => u.role === 'Standard User').length}
          </span>
        </div>
      </div>
    </div>
  );
}