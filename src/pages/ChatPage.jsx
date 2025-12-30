import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import ChatBox from "../components/ChatBox";
import InputBox from "../components/InputBox";
import "../styles.css";

// Comprehensive Knowledge Base - UPDATED FOR TEXT ANALYTICS
const knowledgeBase = {
  // Health Issues & Solutions (Keep existing)
  health: {
    fever: "🌡️ **Fever Treatment**:\n• Rest and sleep\n• Drink plenty of fluids (water, juice, broth)\n• Take paracetamol or ibuprofen as directed\n• Use cool compresses on forehead\n• Wear lightweight clothing\n\n⚠️ See a doctor if:\n- Fever > 103°F (39.4°C)\n- Lasts more than 3 days\n- Severe headache or stiff neck",
    
    headache: "🤕 **Headache Relief**:\n• Rest in a dark, quiet room\n• Apply cold or warm compress to forehead/neck\n• Drink plenty of water\n• Try over-the-counter pain relievers (ibuprofen, aspirin)\n• Massage temples and neck\n• Consider relaxation techniques\n\n💊 For migraines: Avoid triggers like bright lights, loud noises",
    
    cough: "🤧 **Cough Remedies**:\n• Drink warm liquids (honey lemon tea)\n• Use a humidifier or steam inhalation\n• Try cough drops or lozenges\n• Gargle with salt water\n• Avoid irritants (smoke, dust)\n• Elevate head while sleeping\n\n🏥 See doctor if:\n- Cough with blood\n- Lasts > 2 weeks\n- Difficulty breathing",
    
    cold: "😷 **Cold & Flu Care**:\n• Rest and stay hydrated\n• Vitamin C supplements\n• Warm salt water gargle\n• Chicken soup or warm broth\n• Use nasal saline spray\n• Take zinc supplements early\n\n📅 Symptoms usually improve in 7-10 days",
    
    stomach: "🤢 **Stomach Problems**:\n• BRAT diet: Bananas, Rice, Applesauce, Toast\n• Drink clear fluids (water, electrolyte drinks)\n• Avoid dairy, fatty, spicy foods\n• Ginger tea for nausea\n• Peppermint for indigestion\n• Small, frequent meals\n\n🚑 Emergency if: Severe pain, blood in stool, dehydration",
    
    stress: "🧠 **Stress Management**:\n• Practice deep breathing exercises\n• Regular physical activity (30 min daily)\n• Meditation or mindfulness\n• Adequate sleep (7-9 hours)\n• Talk to friends/family\n• Time management techniques\n• Professional counseling if needed",
    
    diabetes: "🩸 **Diabetes Care**:\n• Monitor blood sugar regularly\n• Balanced diet (low sugar, high fiber)\n• Regular exercise\n• Take medications as prescribed\n• Regular foot checks\n• Annual eye exams\n• Stay hydrated",
    
    covid: "🦠 **COVID-19 Care**:\n• Isolate for 5 days from symptoms\n• Rest and stay hydrated\n• Monitor oxygen levels\n• Take paracetamol for fever\n• Seek medical help if:\n  - Difficulty breathing\n  - Chest pain\n  - Oxygen < 94%\n• Get vaccinated and boosted",
  },
  
  // TEXT ANALYTICS & NLP KNOWLEDGE (UPDATED)
  textAnalytics: {
    // Introduction
    introduction: `📚 **Introduction to Text Analytics**\n\n**Definition:** Text Analytics involves extracting meaningful information from unstructured text using computational methods.\n\n**Significance:**\n• Converts text to structured data\n• Enables sentiment analysis, topic modeling\n• Powers search engines, chatbots\n\n**Applications:**\n1. **Business:** Customer feedback analysis\n2. **Healthcare:** Medical report analysis\n3. **Finance:** News sentiment for trading\n4. **Social Media:** Trend detection\n\n**Data Sources:**\n• Social media posts\n• Customer reviews\n• News articles\n• Research papers\n• Emails & documents`,

    // Preprocessing
    preprocessing: `🔧 **Text Preprocessing Techniques**\n\n**Tokenization:** Splitting text into words/tokens\n• Example: "Hello World!" → ["Hello", "World", "!"]\n\n**Stop-word Removal:** Removing common words\n• Removes: "the", "is", "and", "in"\n\n**Stemming:** Reducing words to root form\n• "running" → "run"\n• "better" → "better" (imperfect)\n\n**Lemmatization:** Proper word reduction using dictionary\n• "running" → "run"\n• "better" → "good"\n\n**Case Normalization:** Convert to lowercase\n**Text Cleaning:** Remove URLs, special characters\n**Noise Removal:** Handle HTML tags, extra spaces`,

    // Text Representation
    representation: `📊 **Text Representation Models**\n\n**1. Bag-of-Words (BoW):**\n• Creates vocabulary from all documents\n• Represents text as word frequency vectors\n• Simple but loses word order\n\n**2. TF-IDF (Term Frequency-Inverse Document Frequency):**\n• Weights words by importance\n• Common words get lower weights\n• Formula: TF × IDF\n\n**3. Word Embeddings:**\n**Word2Vec:** Neural network-based embeddings\n**GloVe:** Global co-occurrence statistics\n**BERT:** Contextual embeddings (state-of-the-art)\n\n**4. Advanced Models:**\n• **FastText:** Handles subwords\n• **ELMo:** Deep contextualized embeddings\n• **GPT Models:** Transformer-based`,

    // NLP Techniques
    nlpTechniques: `🎯 **NLP Techniques**\n\n**Part-of-Speech (POS) Tagging:**\n• Labels words with grammatical roles\n• Tags: Noun (NN), Verb (VB), Adjective (JJ)\n• Example: "The/DT quick/JJ brown/JJ fox/NN"\n\n**Named Entity Recognition (NER):**\n• Identifies entities in text\n• Categories: Person, Organization, Location, Date\n• Example: "[ORG Google] was founded by [PER Larry Page] in [LOC Mountain View]"\n\n**Syntactic Parsing:**\n• Analyzes grammatical structure\n• Creates parse trees\n• Helps in understanding relationships\n\n**Dependency Parsing:**\n• Shows word dependencies\n• Useful for information extraction`,

    // Books & References
    books: `📖 **Recommended Books & Links**\n\n**Textbooks:**\n1. **"Speech and Language Processing"** by Daniel Jurafsky & James H. Martin\n   📚 Amazon: https://amzn.to/3Wk2wPk\n   📘 PDF: https://web.stanford.edu/~jurafsky/slp3/\n\n2. **"Text Mining: Classification, Clustering, and Applications"** by Ashok Srivastava & Mehran Sahami\n   📚 Amazon: https://amzn.to/3YYA8vT\n   📘 CRC Press: https://www.routledge.com/9781420059452\n\n**Reference Books:**\n1. **"Pattern Recognition and Machine Learning"** by Christopher M. Bishop\n   📚 Amazon: https://amzn.to/4ax7sFN\n   📘 Springer: https://www.springer.com/gp/book/9780387310732\n\n2. **"Deep Learning for Natural Language Processing"** by Palash Goyal et al.\n   📚 Amazon: https://amzn.to/3WV32En\n   📘 Springer: https://www.springer.com/gp/book/9783030971734\n\n**Free Resources:**\n• Hugging Face: https://huggingface.co/\n• NLTK Documentation: https://www.nltk.org/\n• spaCy: https://spacy.io/`,

    // Example Code
    examples: `💻 **Code Examples**\n\n**Example 1: Text Preprocessing in Python**\n\`\`\`python
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-zA-Z\\s]', '', text)
    # Tokenize
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Example usage
sample_text = "Text Analytics is AMAZING! It helps in understanding text data."
print(preprocess_text(sample_text))
# Output: "text analytics amazing help understanding text data"
\`\`\`\n\n**Example 2: TF-IDF Implementation**\n\`\`\`python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "Text analytics is important for data science",
    "Natural language processing uses text analytics",
    "Machine learning and NLP are related fields"
]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

print("Vocabulary:", vectorizer.get_feature_names_out())
print("TF-IDF Matrix shape:", tfidf_matrix.shape)
\`\`\``,

    // Career & Projects
    career: `🚀 **Career & Projects**\n\n**Skills Required:**\n• Python programming\n• Statistics & Probability\n• Linguistics basics\n• Machine Learning\n• Deep Learning (for advanced NLP)\n\n**Career Paths:**\n1. **NLP Engineer:** Build text processing systems\n2. **Data Scientist (Text):** Analyze text data\n3. **Research Scientist:** Develop new NLP models\n4. **AI Product Manager:** NLP-based products\n\n**Project Ideas:**\n1. **Sentiment Analyzer:** Classify review sentiments\n2. **Chatbot:** Context-aware conversation\n3. **Text Summarizer:** Automatic document summarization\n4. **Named Entity Recognizer:** Extract entities from news\n5. **Topic Modeling:** Discover themes in documents\n\n**Learning Path:**\n1. Learn Python & NLP libraries (NLTK, spaCy)\n2. Understand text preprocessing\n3. Study ML algorithms for text\n4. Work with word embeddings\n5. Build projects and contribute to GitHub`,
  },
  
  // General Responses
  greeting: `👋 **Welcome to Health & Text Analytics Assistant!**\n\nI can help you with:\n\n🏥 **Health Issues:**\n• Fever, headache, cough\n• Cold, stomach problems\n• Stress, diabetes care\n• COVID-19 guidance\n\n📚 **Text Analytics & NLP:**\n• Introduction to Text Analytics\n• Text preprocessing techniques\n• Text representation (BoW, TF-IDF, Embeddings)\n• NLP techniques (POS, NER, Parsing)\n• Recommended books & resources\n• Code examples & projects\n\nWhat would you like to learn today?`,

  help: `ℹ️ **How I Can Help**\n\n**Health Topics:**\n• 'fever treatment'\n• 'headache remedies'\n• 'stress management'\n• 'diabetes care tips'\n\n**Text Analytics Topics:**\n• 'introduction to text analytics'\n• 'text preprocessing'\n• 'text representation models'\n• 'nlp techniques'\n• 'recommended books'\n• 'code examples'\n• 'career in text analytics'\n\nJust ask me anything from these topics!`,
};

// Smart Response Finder - UPDATED FOR TEXT ANALYTICS
const getAIResponse = (userMessage) => {
  const msg = userMessage.toLowerCase().trim();
  
  console.log("User asked:", msg);
  
  // Health queries (keep existing)
  if (msg.includes('fever') || msg.includes('temperature')) return knowledgeBase.health.fever;
  if (msg.includes('headache') || msg.includes('migraine')) return knowledgeBase.health.headache;
  if (msg.includes('cough')) return knowledgeBase.health.cough;
  if (msg.includes('cold') || msg.includes('flu')) return knowledgeBase.health.cold;
  if (msg.includes('stomach') || msg.includes('pain')) return knowledgeBase.health.stomach;
  if (msg.includes('stress') || msg.includes('anxiety')) return knowledgeBase.health.stress;
  if (msg.includes('diabet') || msg.includes('sugar')) return knowledgeBase.health.diabetes;
  if (msg.includes('covid') || msg.includes('corona')) return knowledgeBase.health.covid;
  
  // TEXT ANALYTICS queries (NEW)
  if (msg.includes('text analytics') || msg.includes('text mining') || msg.includes('nlp')) {
    if (msg.includes('intro') || msg.includes('what is') || msg.includes('definition')) 
      return knowledgeBase.textAnalytics.introduction;
    if (msg.includes('preprocess') || msg.includes('token') || msg.includes('stem') || msg.includes('lemma'))
      return knowledgeBase.textAnalytics.preprocessing;
    if (msg.includes('represent') || msg.includes('bow') || msg.includes('tfidf') || msg.includes('embedding') || msg.includes('word2vec') || msg.includes('bert'))
      return knowledgeBase.textAnalytics.representation;
    if (msg.includes('ner') || msg.includes('pos') || msg.includes('pars') || msg.includes('named entity') || msg.includes('part of speech'))
      return knowledgeBase.textAnalytics.nlpTechniques;
    if (msg.includes('book') || msg.includes('resource') || msg.includes('reference') || msg.includes('learn'))
      return knowledgeBase.textAnalytics.books;
    if (msg.includes('code') || msg.includes('example') || msg.includes('implement') || msg.includes('python'))
      return knowledgeBase.textAnalytics.examples;
    if (msg.includes('career') || msg.includes('job') || msg.includes('project') || msg.includes('skill'))
      return knowledgeBase.textAnalytics.career;
    
    // Default text analytics response
    return knowledgeBase.textAnalytics.introduction;
  }
  
  // General
  if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey') || msg.includes('welcome')) 
    return knowledgeBase.greeting;
  if (msg.includes('help') || msg.includes('what can you') || msg.includes('assist')) 
    return knowledgeBase.help;
  
  return `🤔 **I'm not sure I understood. Try asking about:**\n\n🏥 **Health:**\n• 'fever treatment'\n• 'headache remedies'\n• 'stress management'\n\n📚 **Text Analytics:**\n• 'introduction to text analytics'\n• 'text preprocessing techniques'\n• 'TF-IDF explained'\n• 'NER and POS tagging'\n• 'code examples for text preprocessing'\n• 'recommended books for NLP'`;
};

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      sender: "bot", 
      text: knowledgeBase.greeting,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
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
      
      // Check if user is admin
      const adminCheck = parsedUser.role === "Admin" || 
                        parsedUser.role === "Super Admin" || 
                        parsedUser.role === "Administrator" ||
                        parsedUser.role === "Premium User";
      setIsAdmin(adminCheck);
    } else {
      // Default user
      const guestUser = {
        name: "Guest User",
        email: "guest@example.com",
        role: "Guest",
        avatar: "G"
      };
      setUser(guestUser);
      setIsAdmin(false);
    }
  }, [navigate]);

  // Handle sending messages
  const handleSend = (text) => {
    if (!text.trim()) return;
    
    console.log("Sending:", text);
    
    // Add user message
    const userMessage = {
      id: messageIdRef.current++,
      sender: "user",
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);

    // Show typing indicator
    setIsTyping(true);
    
    // Generate AI response after delay
    setTimeout(() => {
      const aiResponse = getAIResponse(text);
      console.log("Bot response:", aiResponse);
      
      const botMessage = {
        id: messageIdRef.current++,
        sender: "bot",
        text: aiResponse,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 800);
  };

  // Test bot function with Text Analytics examples
  const testBot = () => {
    console.log("=== Testing Text Analytics Bot ===");
    handleSend("What is text analytics?");
    setTimeout(() => handleSend("Explain text preprocessing"), 1000);
    setTimeout(() => handleSend("Show me TF-IDF code"), 2000);
    setTimeout(() => handleSend("Recommended books for NLP"), 3000);
  };

  // Clear chat
  const clearChat = () => {
    setMessages([{
      id: 1,
      sender: "bot",
      text: "Chat cleared! How can I assist you with Health or Text Analytics today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    messageIdRef.current = 2;
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/");
  };

  // Go to admin panel
  const goToAdminPanel = () => {
    navigate("/admin");
  };

  // View user profile
  const viewProfile = () => {
    alert(`User Profile:\n\nName: ${user.name}\nEmail: ${user.email}\nRole: ${user.role}`);
  };

  // Quick actions - UPDATED FOR TEXT ANALYTICS
  const quickActions = [
    { icon: "🤒", text: "Fever Treatment", query: "fever treatment" },
    { icon: "🤕", text: "Headache Remedies", query: "headache remedies" },
    { icon: "📚", text: "Text Analytics Intro", query: "introduction to text analytics" },
    { icon: "🔧", text: "Text Preprocessing", query: "text preprocessing techniques" },
    { icon: "📊", text: "TF-IDF & Embeddings", query: "text representation models" },
    { icon: "💻", text: "NLP Code Examples", query: "code examples for text analytics" },
    { icon: "📖", text: "NLP Books", query: "recommended books for text analytics" },
    { icon: "🧠", text: "Stress Management", query: "stress management" },
  ];

  return (
    <div className="chat-app" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header with User Profile */}
      <div className="chat-header" style={{ flexShrink: 0 }}>
        <div className="header-content">
          <div className="header-left">
            <div className="app-logo">
              <span className="logo-icon">👨‍⚕️📚</span>
              <h1 className="logo-text">Health & Text Analytics Assistant</h1>
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
                    <span className={`role-tag ${user.role.toLowerCase().replace(' ', '-')}`}>
                      {user.role}
                    </span>
                    {isAdmin && <span className="admin-badge">👑 Admin</span>}
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
            <button onClick={testBot} className="header-btn test-btn">
              🔧 Test Bot
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
        {/* Sidebar - UPDATED */}
        <div className="chat-sidebar" style={{ flexShrink: 0 }}>
          <h2 className="sidebar-title">💡 Quick Topics</h2>
          
          <div className="assistant-info">
            <div className="assistant-icon">🤖📚</div>
            <h3 className="assistant-name">Health & Text Analytics Assistant</h3>
            <p className="assistant-desc">
              Expert in health remedies and text analytics/NLP concepts.
              Ask me about text preprocessing, NLP techniques, or health issues!
            </p>
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
            <h4 className="disclaimer-title">📚 Text Analytics Topics</h4>
            <p className="disclaimer-text">
              Covers: Text Preprocessing, TF-IDF, Word Embeddings, 
              POS Tagging, NER, Books & Code Examples
            </p>
          </div>

          {/* User Stats */}
          {user && user.role !== "Guest" && (
            <div className="user-stats">
              <h4 className="stats-title">📊 Your Activity</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-icon">💬</span>
                  <span className="stat-label">Chats Today:</span>
                  <span className="stat-value">5</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">⭐</span>
                  <span className="stat-label">Your Role:</span>
                  <span className="stat-value">{user.role}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Area */}
        <div className="chat-area" style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          minHeight: 0 
        }}>
          <div 
            className="messages-container" 
            style={{ 
              flex: 1,
              overflowY: 'auto',
              minHeight: 0,
              padding: '20px'
            }}
          >
            <ChatBox messages={messages} isTyping={isTyping} />
          </div>
          
          {/* Input Area */}
          <div className="input-area" style={{ flexShrink: 0 }}>
            <InputBox onSend={handleSend} />
            
            <div className="quick-buttons">
              <button className="quick-btn health-btn" onClick={() => handleSend("fever treatment")}>
                🤒 Fever
              </button>
              <button className="quick-btn health-btn" onClick={() => handleSend("headache remedies")}>
                🤕 Headache
              </button>
              <button className="quick-btn text-btn" onClick={() => handleSend("text preprocessing")}>
                🔧 Preprocessing
              </button>
              <button className="quick-btn text-btn" onClick={() => handleSend("TF-IDF explained")}>
                📊 TF-IDF
              </button>
              <button className="quick-btn text-btn" onClick={() => handleSend("NLP books")}>
                📖 NLP Books
              </button>
              <button className="quick-btn text-btn" onClick={() => handleSend("code examples")}>
                💻 Code Examples
              </button>
            </div>
            
            <p className="input-hint">
              💡 Try: "fever", "headache", "text analytics", "TF-IDF", "NER", "word embeddings", "python code"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}