import { useState } from "react";

export default function AdminSystem() {
  const [settings, setSettings] = useState({
    maxChatHistory: 100,
    chatSessionTimeout: 30,
    otpExpiry: 10,
    jwtExpiry: 24,
    enableEmail: false,
    enableAnalytics: true,
    rateLimit: 60
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = () => {
    alert("Settings saved successfully!");
    // Here you would send settings to backend
  };

  const handleResetSettings = () => {
    if (window.confirm("Are you sure you want to reset all settings to default?")) {
      setSettings({
        maxChatHistory: 100,
        chatSessionTimeout: 30,
        otpExpiry: 10,
        jwtExpiry: 24,
        enableEmail: false,
        enableAnalytics: true,
        rateLimit: 60
      });
    }
  };

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">
          <span className="title-icon">⚙️</span>
          System Settings
        </h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={handleResetSettings}>
            Reset to Default
          </button>
          <button className="btn-primary" onClick={handleSaveSettings}>
            Save Changes
          </button>
        </div>
      </div>

      <div className="settings-grid">
        {/* Chat Settings */}
        <div className="settings-card">
          <h3 className="settings-title">💬 Chat Settings</h3>
          <div className="setting-item">
            <label>Max Chat History per User</label>
            <div className="setting-control">
              <input 
                type="range" 
                min="10" 
                max="500" 
                value={settings.maxChatHistory}
                onChange={(e) => handleSettingChange('maxChatHistory', parseInt(e.target.value))}
              />
              <span className="setting-value">{settings.maxChatHistory} messages</span>
            </div>
          </div>
          <div className="setting-item">
            <label>Chat Session Timeout</label>
            <div className="setting-control">
              <input 
                type="range" 
                min="5" 
                max="120" 
                value={settings.chatSessionTimeout}
                onChange={(e) => handleSettingChange('chatSessionTimeout', parseInt(e.target.value))}
              />
              <span className="setting-value">{settings.chatSessionTimeout} minutes</span>
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="settings-card">
          <h3 className="settings-title">🔐 Security Settings</h3>
          <div className="setting-item">
            <label>OTP Expiry Time</label>
            <div className="setting-control">
              <input 
                type="range" 
                min="5" 
                max="60" 
                value={settings.otpExpiry}
                onChange={(e) => handleSettingChange('otpExpiry', parseInt(e.target.value))}
              />
              <span className="setting-value">{settings.otpExpiry} minutes</span>
            </div>
          </div>
          <div className="setting-item">
            <label>JWT Token Expiry</label>
            <div className="setting-control">
              <input 
                type="range" 
                min="1" 
                max="72" 
                value={settings.jwtExpiry}
                onChange={(e) => handleSettingChange('jwtExpiry', parseInt(e.target.value))}
              />
              <span className="setting-value">{settings.jwtExpiry} hours</span>
            </div>
          </div>
          <div className="setting-item">
            <label>Rate Limit per Minute</label>
            <div className="setting-control">
              <input 
                type="range" 
                min="10" 
                max="200" 
                value={settings.rateLimit}
                onChange={(e) => handleSettingChange('rateLimit', parseInt(e.target.value))}
              />
              <span className="setting-value">{settings.rateLimit} requests</span>
            </div>
          </div>
        </div>

        {/* Feature Toggles */}
        <div className="settings-card">
          <h3 className="settings-title">🚀 Feature Toggles</h3>
          <div className="toggle-item">
            <div className="toggle-info">
              <h4>Email Service</h4>
              <p>Enable sending real emails for OTP and notifications</p>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={settings.enableEmail}
                onChange={(e) => handleSettingChange('enableEmail', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <div className="toggle-item">
            <div className="toggle-info">
              <h4>Usage Analytics</h4>
              <p>Collect anonymous usage data for improvement</p>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={settings.enableAnalytics}
                onChange={(e) => handleSettingChange('enableAnalytics', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {/* System Info */}
        <div className="settings-card">
          <h3 className="settings-title">📊 System Information</h3>
          <div className="system-info">
            <div className="info-item">
              <span className="info-label">Application Version</span>
              <span className="info-value">v1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">Database Type</span>
              <span className="info-value">SQLite</span>
            </div>
            <div className="info-item">
              <span className="info-label">Environment</span>
              <span className="info-value">Development</span>
            </div>
            <div className="info-item">
              <span className="info-label">Uptime</span>
              <span className="info-value">2 days, 5 hours</span>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="settings-card danger">
          <h3 className="settings-title">⚠️ Danger Zone</h3>
          <p className="danger-warning">These actions are irreversible. Proceed with caution.</p>
          <div className="danger-actions">
            <button className="danger-btn" onClick={() => alert("Clear Database")}>
              Clear All Chat Data
            </button>
            <button className="danger-btn" onClick={() => alert("Delete Users")}>
              Delete Inactive Users
            </button>
            <button className="danger-btn" onClick={() => alert("Reset System")}>
              Factory Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}