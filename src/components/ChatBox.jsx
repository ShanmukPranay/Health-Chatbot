import React, { useEffect, useRef } from "react";

export default function ChatBox({ messages, isTyping }) {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Get user from localStorage
  const getUser = () => {
    const userData = localStorage.getItem("user");
    return userData ? JSON.parse(userData) : { name: "You", avatar: "Y" };
  };

  const user = getUser();

  // Function to format message text with code blocks
  const formatMessageText = (text) => {
    if (!text) return text;

    // Split text by code blocks
    const parts = text.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      // If it's a code block
      if (part.startsWith('```') && part.endsWith('```')) {
        const codeContent = part.slice(3, -3).trim();
        
        // Extract language if specified
        const languageMatch = codeContent.match(/^(\w+)\n/);
        const language = languageMatch ? languageMatch[1] : 'python';
        const code = languageMatch ? codeContent.slice(languageMatch[0].length) : codeContent;
        
        // Handle expected output sections
        if (code.includes('**EXPECTED OUTPUT:**')) {
          const [mainCode, expectedOutput] = code.split('**EXPECTED OUTPUT:**');
          return (
            <div key={index} className="code-section">
              <div className="code-block">
                <div className="code-header">
                  <span className="code-language">{language}</span>
                </div>
                <pre className="code-content">
                  <code>{mainCode.trim()}</code>
                </pre>
              </div>
              
              <div className="output-block">
                <div className="output-header">Expected Output</div>
                <pre className="output-content">
                  <code>{expectedOutput.trim()}</code>
                </pre>
              </div>
            </div>
          );
        }
        
        // Regular code block
        return (
          <div key={index} className="code-block">
            <div className="code-header">
              <span className="code-language">{language}</span>
            </div>
            <pre className="code-content">
              <code>{code}</code>
            </pre>
          </div>
        );
      }
      
      // Regular text - preserve line breaks and markdown bold
      const formattedText = part.split('\n').map((line, lineIndex) => {
        // Handle bold text with ** **
        const boldParts = line.split(/(\*\*.*?\*\*)/g);
        const formattedLine = boldParts.map((boldPart, boldIndex) => {
          if (boldPart.startsWith('**') && boldPart.endsWith('**')) {
            return <strong key={boldIndex}>{boldPart.slice(2, -2)}</strong>;
          }
          return <span key={boldIndex}>{boldPart}</span>;
        });
        
        return (
          <React.Fragment key={lineIndex}>
            {formattedLine}
            {lineIndex < part.split('\n').length - 1 && <br />}
          </React.Fragment>
        );
      });
      
      return <span key={index}>{formattedText}</span>;
    });
  };

  return (
    <div className="chat-messages">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`message-bubble ${msg.sender === "user" ? "user-bubble" : "bot-bubble"}`}
        >
          <div className="bubble-content">
            <div className="message-header">
              <div className="message-avatar">
                {msg.sender === "user" ? (
                  <div className="user-avatar-circle">
                    {user.avatar || user.name?.charAt(0) || "Y"}
                  </div>
                ) : (
                  <div className="bot-avatar">🤖</div>
                )}
              </div>
              <div className="message-sender">
                {msg.sender === "user" ? user.name || "You" : "Health & Text Analytics Assistant"}
                {msg.sender === "bot" && (
                  <span className="bot-badge">AI</span>
                )}
              </div>
            </div>
            <div className="message-text">
              {formatMessageText(msg.text)}
            </div>
            <div className="message-time">{msg.timestamp}</div>
          </div>
        </div>
      ))}
      
      {isTyping && (
        <div className="typing-indicator">
          <div className="typing-dots">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
          <span className="typing-text">Assistant is typing...</span>
        </div>
      )}
      
      <div ref={chatEndRef} />
    </div>
  );
}