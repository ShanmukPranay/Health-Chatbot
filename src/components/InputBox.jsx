import { useState, useEffect, useRef } from "react";
import VoiceInput from "./VoiceInput";

export default function InputBox({ onSend, isConnected = true }) {
  const [text, setText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef(null);
  const maxChars = 500; // Maximum characters allowed

  // Update character count
  useEffect(() => {
    setCharCount(text.length);
  }, [text]);

  // Handle typing indicator
  useEffect(() => {
    if (text.length > 0) {
      setIsTyping(true);
      
      // Clear previous timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Set timeout to stop typing indicator after 1 second of no typing
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
      }, 1000);
    } else {
      setIsTyping(false);
    }
    
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [text]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    
    // Check connection status before sending
    if (!isConnected) {
      alert("⚠️ Not connected to server. Please check your internet connection.");
      return;
    }
    
    // Check character limit
    if (text.length > maxChars) {
      alert(`⚠️ Message exceeds ${maxChars} characters. Please shorten your message.`);
      return;
    }
    
    console.log("InputBox sending:", text);
    onSend(text);
    setText("");
    setCharCount(0);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleVoiceTranscript = (transcript) => {
    console.log("Voice transcript received:", transcript);
    // This REPLACES the text instead of appending
    setText(transcript);
  };

  // Clear text when starting to listen
  useEffect(() => {
    if (isListening) {
      setText("");
    }
  }, [isListening]);

  const handleClearText = () => {
    setText("");
  };

  const handlePaste = async (e) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text');
    const currentText = text;
    const newText = currentText + pastedText;
    
    if (newText.length <= maxChars) {
      setText(newText);
    } else {
      alert(`⚠️ Cannot paste. Message would exceed ${maxChars} characters.`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="message-form">
      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            className="message-input"
            value={text}
            onChange={(e) => {
              if (e.target.value.length <= maxChars) {
                setText(e.target.value);
              }
            }}
            onKeyPress={handleKeyPress}
            onPaste={handlePaste}
            placeholder={
              !isConnected 
                ? "🔌 Connecting to server..." 
                : isListening 
                  ? "🎤 Listening... Click microphone again to stop" 
                  : "Type your question here..."
            }
            disabled={!isConnected}
            rows={Math.min(3, Math.ceil(text.length / 50) || 1)}
            autoFocus
          />
          
          {/* Character counter */}
          {text.length > 0 && (
            <div className={`char-counter ${text.length > maxChars * 0.8 ? 'warning' : ''} ${text.length > maxChars * 0.9 ? 'danger' : ''}`}>
              {text.length}/{maxChars}
            </div>
          )}
          
          {/* Clear text button */}
          {text.length > 0 && !isListening && (
            <button
              type="button"
              className="clear-text-btn"
              onClick={handleClearText}
              title="Clear text"
            >
              ✖
            </button>
          )}
        </div>
        
        <div className="input-actions">
          <VoiceInput 
            onTranscriptChange={handleVoiceTranscript}
            isListening={isListening}
            setIsListening={setIsListening}
            isConnected={isConnected}
          />
          
          <button 
            type="submit" 
            className="send-btn"
            disabled={!text.trim() || !isConnected}
            title={!isConnected ? "Waiting for connection" : "Send message"}
          >
            <span className="send-icon">📤</span>
            <span className="send-text">Send</span>
          </button>
        </div>
      </div>
      
      {/* Typing indicator */}
      {isTyping && isConnected && (
        <div className="user-typing-indicator">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-text">Typing...</span>
        </div>
      )}
      
      {/* Connection warning */}
      {!isConnected && (
        <div className="connection-warning">
          <span className="warning-icon">⚠️</span>
          <span className="warning-text">Offline mode - Reconnecting...</span>
          <div className="reconnection-spinner"></div>
        </div>
      )}
      
      {/* Quick action hints */}
      {isConnected && text.length === 0 && !isListening && (
        <div className="input-hints">
          <span className="hint">💡 Press Enter to send</span>
          <span className="hint">🎤 Click microphone for voice input</span>
          <span className="hint">📋 Paste images not supported</span>
        </div>
      )}
    </form>
  );
}