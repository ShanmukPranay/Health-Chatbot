import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import ChatBox from "../components/ChatBox";
import InputBox from "../components/InputBox";
import socketService from "../components/socketService";
import "../styles.css";

// Comprehensive Knowledge Base - HEALTH ONLY
const knowledgeBase = {
  // Health Issues & Solutions
  health: {
    fever: "🌡️ **Fever Treatment**:\n• Rest and sleep\n• Drink plenty of fluids (water, juice, broth)\n• Take paracetamol or ibuprofen as directed\n• Use cool compresses on forehead\n• Wear lightweight clothing\n\n⚠️ **See a doctor if:**\n- Fever > 103°F (39.4°C)\n- Lasts more than 3 days\n- Severe headache or stiff neck\n- Difficulty breathing",
    
    headache: "🤕 **Headache Relief**:\n• Rest in a dark, quiet room\n• Apply cold or warm compress to forehead/neck\n• Drink plenty of water\n• Try over-the-counter pain relievers (ibuprofen, aspirin)\n• Massage temples and neck\n• Consider relaxation techniques\n\n💊 **For migraines:** Avoid triggers like bright lights, loud noises, and certain foods",
    
    cough: "🤧 **Cough Remedies**:\n• Drink warm liquids (honey lemon tea)\n• Use a humidifier or steam inhalation\n• Try cough drops or lozenges\n• Gargle with salt water\n• Avoid irritants (smoke, dust)\n• Elevate head while sleeping\n\n🏥 **See doctor if:**\n- Cough with blood\n- Lasts > 2 weeks\n- Difficulty breathing\n- Chest pain",
    
    cold: "😷 **Cold & Flu Care**:\n• Rest and stay hydrated\n• Vitamin C supplements\n• Warm salt water gargle\n• Chicken soup or warm broth\n• Use nasal saline spray\n• Take zinc supplements early\n\n📅 **Symptoms usually improve in 7-10 days**\n\n⚠️ **Seek medical help if:**\n- High fever > 101°F (38.3°C)\n- Symptoms worsen after 5 days\n- Difficulty breathing",
    
    stomach: "🤢 **Stomach Problems**:\n• BRAT diet: Bananas, Rice, Applesauce, Toast\n• Drink clear fluids (water, electrolyte drinks)\n• Avoid dairy, fatty, spicy foods\n• Ginger tea for nausea\n• Peppermint for indigestion\n• Small, frequent meals\n\n🚑 **Emergency if:** Severe pain, blood in stool, dehydration",
    
    stress: "🧠 **Stress Management**:\n• Practice deep breathing exercises\n• Regular physical activity (30 min daily)\n• Meditation or mindfulness\n• Adequate sleep (7-9 hours)\n• Talk to friends/family\n• Time management techniques\n• Professional counseling if needed\n\n🌿 **Quick relaxation:** Take 5 deep breaths, go for a short walk, listen to calming music",
    
    diabetes: "🩸 **Diabetes Care**:\n• Monitor blood sugar regularly\n• Balanced diet (low sugar, high fiber)\n• Regular exercise\n• Take medications as prescribed\n• Regular foot checks\n• Annual eye exams\n• Stay hydrated\n\n📊 **Target blood sugar:** 80-130 mg/dL before meals",
    
    covid: "🦠 **COVID-19 Care**:\n• Isolate for 5 days from symptoms\n• Rest and stay hydrated\n• Monitor oxygen levels with pulse oximeter\n• Take paracetamol for fever\n• Inform close contacts\n\n🚑 **Emergency signs:**\n- Difficulty breathing\n- Chest pain or pressure\n- Oxygen < 94%\n- Confusion\n- Bluish lips/face\n\n💉 **Get vaccinated and boosted!**",
    
    blood_pressure: "❤️ **Blood Pressure Management**:\n• Reduce salt intake (less than 2,300mg daily)\n• Eat potassium-rich foods (bananas, spinach)\n• Maintain healthy weight\n• Exercise regularly (30 min daily)\n• Limit alcohol consumption\n• Quit smoking\n• Manage stress\n\n📊 **Normal range:** Below 120/80 mmHg",
    
    allergy: "🤧 **Allergy Relief**:\n• Identify and avoid triggers\n• Take antihistamines as directed\n• Use nasal sprays for congestion\n• Keep windows closed during high pollen\n• Shower after outdoor activities\n• Use air purifiers at home\n\n⚠️ **See doctor if:** Severe reactions, difficulty breathing",
    
    back_pain: "🦴 **Back Pain Relief**:\n• Apply heat or cold packs\n• Maintain good posture\n• Gentle stretching exercises\n• Use proper lifting techniques\n• Sleep on firm mattress\n• Over-the-counter pain relievers\n\n🏥 **See doctor if:** Pain lasts >2 weeks, numbness, loss of bladder control",
    
    insomnia: "😴 **Sleep Tips (Insomnia)**:\n• Stick to consistent sleep schedule\n• Create dark, quiet bedroom environment\n• Avoid screens 1 hour before bed\n• Limit caffeine after 2 PM\n• Try relaxation techniques\n• Avoid large meals before bedtime\n\n🩺 **Consult doctor if:** Sleep problems persist >3 weeks",
    
    heartburn: "🔥 **Heartburn/GERD Relief**:\n• Avoid trigger foods (spicy, fatty, citrus)\n• Eat smaller, frequent meals\n• Don't lie down after eating\n• Elevate head while sleeping\n• Avoid tight clothing\n• Try OTC antacids\n\n⚠️ **Seek help if:** Chest pain, difficulty swallowing, black stools",
    
    constipation: "🚽 **Constipation Relief**:\n• Increase fiber intake (fruits, vegetables)\n• Drink plenty of water (8-10 glasses)\n• Exercise regularly\n• Don't ignore urge to go\n• Try prune juice or fiber supplements\n\n⚠️ **See doctor if:** >3 weeks, blood in stool, severe pain",
    
    dehydration: "💧 **Dehydration Signs & Treatment**:\n• Drink water or oral rehydration solutions\n• Avoid caffeine and alcohol\n• Eat water-rich foods (watermelon, cucumber)\n• Rest in cool environment\n\n🚨 **Emergency signs:**\n- Severe thirst\n- Dry mouth and skin\n- Little or no urination\n- Dizziness\n- Rapid heartbeat"
  },
  
  // General Responses - HEALTH ONLY
  greeting: "👋 **Welcome to Your Personal Health Assistant!**\n\nI can help you with:\n\n🏥 **Health Issues & Remedies:**\n• Fever, headache, cough\n• Cold, flu, stomach problems\n• Stress, anxiety, depression\n• Diabetes care, blood pressure\n• Allergies, back pain, insomnia\n• Heartburn, constipation, dehydration\n• COVID-19 guidance\n\n💡 **Try asking:**\n• 'fever treatment'\n• 'headache relief'\n• 'stress management'\n• 'diabetes care tips'\n• 'covid symptoms'\n\nHow can I help you today?",
  
  help: "ℹ️ **How I Can Help**\n\n**🏥 Health Topics I Cover:**\n• 'fever treatment' - Fever remedies and when to see doctor\n• 'headache relief' - Headache and migraine relief\n• 'cough remedies' - Natural cough remedies\n• 'cold and flu' - Cold and flu care\n• 'stomach pain' - Digestive issues relief\n• 'stress management' - Stress and anxiety reduction\n• 'diabetes care' - Diabetes management tips\n• 'covid care' - COVID-19 guidance\n• 'blood pressure' - BP management\n• 'allergy relief' - Allergy symptoms relief\n• 'back pain' - Back pain relief exercises\n• 'insomnia' - Sleep tips\n• 'heartburn' - GERD relief\n• 'constipation' - Constipation relief\n• 'dehydration' - Dehydration signs\n\nJust type your health question and I'll help!",
  
  disclaimer: "⚠️ **Medical Disclaimer**\n\nI am an AI health assistant, NOT a substitute for professional medical advice. The information provided is for educational purposes only.\n\n**Always consult a qualified healthcare provider for:**\n• Medical emergencies (call emergency services)\n• Persistent or worsening symptoms\n• Prescription medications\n• Proper diagnosis and treatment\n\n**Emergency? Call your local emergency number immediately.**"
};

// Smart Response Finder - Health only
const getAIResponse = (userMessage) => {
  const msg = userMessage.toLowerCase().trim();
  
  // Health queries
  if (msg.includes('fever') || msg.includes('temperature')) return knowledgeBase.health.fever;
  if (msg.includes('headache') || msg.includes('migraine')) return knowledgeBase.health.headache;
  if (msg.includes('cough')) return knowledgeBase.health.cough;
  if (msg.includes('cold') || msg.includes('flu')) return knowledgeBase.health.cold;
  if (msg.includes('stomach') || msg.includes('pain')) return knowledgeBase.health.stomach;
  if (msg.includes('stress') || msg.includes('anxiety')) return knowledgeBase.health.stress;
  if (msg.includes('diabet') || msg.includes('sugar')) return knowledgeBase.health.diabetes;
  if (msg.includes('covid') || msg.includes('corona')) return knowledgeBase.health.covid;
  if (msg.includes('blood pressure') || msg.includes('bp')) return knowledgeBase.health.blood_pressure;
  if (msg.includes('allergy') || msg.includes('allergic')) return knowledgeBase.health.allergy;
  if (msg.includes('back pain') || msg.includes('backache')) return knowledgeBase.health.back_pain;
  if (msg.includes('sleep') || msg.includes('insomnia')) return knowledgeBase.health.insomnia;
  if (msg.includes('heartburn') || msg.includes('gerd') || msg.includes('acidity')) return knowledgeBase.health.heartburn;
  if (msg.includes('constipation')) return knowledgeBase.health.constipation;
  if (msg.includes('dehydration') || msg.includes('thirsty')) return knowledgeBase.health.dehydration;
  
  // Greetings
  if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey') || msg.includes('greetings')) 
    return knowledgeBase.greeting;
  
  // Help
  if (msg.includes('help') || msg.includes('what can you do') || msg.includes('capabilities')) 
    return knowledgeBase.help;
  
  // Disclaimer
  if (msg.includes('disclaimer') || msg.includes('medical advice')) 
    return knowledgeBase.disclaimer;
  
  // Default response
  return `🤔 **I'm not sure I understood.**\n\nTry asking about:\n\n🏥 **Health Topics:**\n• 'fever treatment'\n• 'headache relief'\n• 'cough remedies'\n• 'stress management'\n• 'diabetes care'\n• 'blood pressure'\n• 'allergy relief'\n• 'back pain'\n• 'insomnia help'\n• 'heartburn relief'\n• 'constipation relief'\n• 'dehydration signs'\n\n⚠️ Remember: I provide health information only, not medical advice.`;
};

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messageIdRef = useRef(2);

  // Check authentication and load user
  useEffect(() => {
    const auth = localStorage.getItem("auth");
    const userData = localStorage.getItem("user");
    
    if (!auth) {
      navigate("/login");
    } else if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Only true for exact "Admin" role
      const adminCheck = parsedUser.role === "Admin" || 
                        parsedUser.role === "Super Admin" || 
                        parsedUser.role === "Administrator";
      setIsAdmin(adminCheck);
      
      console.log("User loaded:", parsedUser.email, "Role:", parsedUser.role, "IsAdmin:", adminCheck);
      
      // Add welcome message if no messages
      if (messages.length === 0) {
        setTimeout(() => {
          setMessages([{
            id: 1,
            sender: "bot",
            text: knowledgeBase.greeting,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
          messageIdRef.current = 2;
        }, 500);
      }
    } else {
      const guestUser = {
        name: "Guest User",
        email: "guest@example.com",
        role: "Guest",
        avatar: "G"
      };
      setUser(guestUser);
      setIsAdmin(false);
    }

    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, [navigate]);

  // Initialize Socket Connection
  useEffect(() => {
    if (!user) return;

    const userId = user.id || user.email || 'guest';
    const userName = user.name || user.email?.split('@')[0] || 'Guest';
    const userRole = user.role || 'user';

    socketService.connect(userId, userName, userRole);

    socketService.on('connect', () => {
      setIsConnected(true);
      console.log('✅ Connected to server via WebSocket');
    });

    socketService.on('disconnect', () => {
      setIsConnected(false);
      console.log('❌ Disconnected from server');
    });

    socketService.on('bot_response', (data) => {
      setIsTyping(false);
      const botMessage = {
        id: messageIdRef.current++,
        sender: "bot",
        text: data.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
    });

    socketService.on('bot_typing', () => {
      setIsTyping(true);
    });

    socketService.on('error', (error) => {
      console.error('Server error:', error);
      setIsTyping(false);
      const errorMessage = {
        id: messageIdRef.current++,
        sender: "bot",
        text: `❌ **Error:** ${error.message || 'Something went wrong. Using offline mode.'}\n\n${getAIResponse('help')}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    });

    return () => {
      socketService.off('connect');
      socketService.off('disconnect');
      socketService.off('bot_response');
      socketService.off('bot_typing');
      socketService.off('error');
    };
  }, [user]);

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0 && user) {
      localStorage.setItem(
        `chat_history_${user.id || user.email || 'guest'}`,
        JSON.stringify(messages.slice(-100))
      );
    }
  }, [messages, user]);

  // Load previous chat history
  useEffect(() => {
    if (user) {
      const savedMessages = localStorage.getItem(`chat_history_${user.id || user.email || 'guest'}`);
      if (savedMessages && JSON.parse(savedMessages).length > 1) {
        try {
          const parsed = JSON.parse(savedMessages);
          setMessages(parsed);
          messageIdRef.current = parsed.length + 1;
        } catch (e) {
          console.error('Failed to load chat history', e);
        }
      }
    }
  }, [user]);

  // Handle sending messages
  const handleSend = (text) => {
    if (!text.trim()) return;
    
    const userMessage = {
      id: messageIdRef.current++,
      sender: "user",
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);

    if (socketService.getConnectionStatus()) {
      setIsTyping(true);
      socketService.emit('user_message', {
        message: text,
        userId: user?.id || user?.email || 'guest',
        userName: user?.name || 'Guest',
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
        context: {
          previousMessages: messages.slice(-5).map(m => ({
            text: m.text,
            sender: m.sender
          }))
        }
      });
    } else {
      setIsTyping(true);
      setTimeout(() => {
        const aiResponse = getAIResponse(text);
        const botMessage = {
          id: messageIdRef.current++,
          sender: "bot",
          text: aiResponse + "\n\n⚠️ *Running in offline mode. Connect to server for enhanced responses.*",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }, 800);
    }
  };

  const clearChat = () => {
    setMessages([{
      id: 1,
      sender: "bot",
      text: "Chat cleared! How can I assist you with your health concerns today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    messageIdRef.current = 2;
    if (user) {
      localStorage.removeItem(`chat_history_${user.id || user.email || 'guest'}`);
    }
  };

  const handleLogout = () => {
    socketService.disconnect();
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/");
  };

  const goToAdminPanel = () => {
    navigate("/admin");
  };

  const viewProfile = () => {
    alert(`User Profile:\n\nName: ${user?.name || 'Guest'}\nEmail: ${user?.email || 'guest@example.com'}\nRole: ${user?.role || 'Guest'}`);
  };

  // Quick actions - HEALTH ONLY
  const quickActions = [
    { icon: "🤒", text: "Fever Treatment", query: "fever treatment" },
    { icon: "🤕", text: "Headache Relief", query: "headache relief" },
    { icon: "🤧", text: "Cough Remedies", query: "cough remedies" },
    { icon: "😷", text: "Cold & Flu", query: "cold and flu" },
    { icon: "🤢", text: "Stomach Pain", query: "stomach pain" },
    { icon: "🧠", text: "Stress Management", query: "stress management" },
    { icon: "🩸", text: "Diabetes Care", query: "diabetes care" },
    { icon: "❤️", text: "Blood Pressure", query: "blood pressure" },
  ];

  return (
    <div className="chat-app" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <div className="chat-header" style={{ flexShrink: 0 }}>
        <div className="header-content">
          <div className="header-left">
            <div className="app-logo">
              <span className="logo-icon">👨‍⚕️🏥</span>
              <h1 className="logo-text">Personal Health Assistant</h1>
            </div>
            
            <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-text">{isConnected ? 'Live' : 'Offline'}</span>
            </div>
            
            {user && (
              <div className="user-profile">
                <div className="user-avatar">
                  {user.avatar || user.name?.charAt(0) || "U"}
                </div>
                <div className="user-info">
                  <div className="user-name">{user.name || "User"}</div>
                  <div className="user-email">{user.email || "user@example.com"}</div>
                  <div className="user-role-badge">
                    <span className={`role-tag ${user.role?.toLowerCase().replace(' ', '-') || 'guest'}`}>
                      {user.role === 'Admin' ? 'Admin' : (user.role === 'Premium User' ? 'Premium User' : 'Regular User')}
                    </span>
                    {user.role === 'Admin' && <span className="admin-badge">👑 Admin</span>}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="header-right">
            {isAdmin && (
              <button onClick={goToAdminPanel} className="header-btn admin-btn">
                👑 Admin Panel
              </button>
            )}
            <button onClick={viewProfile} className="header-btn profile-btn">
              👤 Profile
            </button>
            <button onClick={clearChat} className="header-btn clear-btn">
              🗑️ Clear Chat
            </button>
            <button onClick={handleLogout} className="header-btn logout-btn">
              🚪 Logout
            </button>
          </div>
        </div>
      </div>
      
      {/* Main Chat Area */}
      <div className="chat-main" style={{ flex: 1, display: 'flex', overflow: 'hidden', minHeight: 0 }}>
        {/* Sidebar */}
        <div className="chat-sidebar" style={{ flexShrink: 0 }}>
          <h2 className="sidebar-title">💡 Health Topics</h2>
          
          <div className="assistant-info">
            <div className="assistant-icon">👨‍⚕️🏥</div>
            <h3 className="assistant-name">Your Personal Health Assistant</h3>
            <p className="assistant-desc">
              Get reliable health information, remedies, and wellness tips.
              Always consult a doctor for medical advice.
            </p>
            {!isConnected && (
              <div className="offline-warning">
                ⚠️ Offline Mode - Using local responses
              </div>
            )}
          </div>
          
          <div className="quick-actions">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="action-btn"
                onClick={() => handleSend(action.query)}
              >
                <span>{action.icon}</span>
                {action.text}
              </button>
            ))}
          </div>
          
          <div className="disclaimer-box">
            <h4 className="disclaimer-title">⚠️ Medical Disclaimer</h4>
            <p className="disclaimer-text">
              I'm an AI assistant providing health information only. 
              Not a substitute for professional medical advice.
              Always consult a healthcare provider for medical concerns.
            </p>
          </div>

          {user && user.role !== "Guest" && (
            <div className="user-stats">
              <h4 className="stats-title">📊 Your Activity</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-icon">💬</span>
                  <span className="stat-label">Health Queries:</span>
                  <span className="stat-value">{messages.filter(m => m.sender === 'user').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">🔌</span>
                  <span className="stat-label">Mode:</span>
                  <span className="stat-value">{isConnected ? 'Online' : 'Offline'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Area */}
        <div className="chat-area" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div className="messages-container" style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: '20px' }}>
            <ChatBox messages={messages} isTyping={isTyping} />
          </div>
          
          <div className="input-area" style={{ flexShrink: 0 }}>
            <InputBox onSend={handleSend} isConnected={isConnected} />
            
            <div className="quick-buttons">
              <button className="quick-btn health-btn" onClick={() => handleSend("fever treatment")}>
                🤒 Fever
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("headache relief")}>
                🤕 Headache
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("cough remedies")}>
                🤧 Cough
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("stress management")}>
                🧠 Stress
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("diabetes care")}>
                🩸 Diabetes
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("blood pressure")}>
                ❤️ BP
              </button>
            </div>
            
            <p className="input-hint">
              💡 Try: "fever", "headache", "cough", "stress", "diabetes", "blood pressure", "covid", "allergy"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}