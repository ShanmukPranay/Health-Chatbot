import { useState, useEffect } from "react";
import VoiceInput from "./VoiceInput";

export default function InputBox({ onSend }) {
  const [text, setText] = useState("");
  const [isListening, setIsListening] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    console.log("InputBox sending:", text);
    onSend(text);
    setText("");
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

  return (
    <form onSubmit={handleSubmit} className="message-form">
      <div className="input-container">
        <input
          type="text"
          className="message-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isListening ? "🎤 Listening... Click microphone again to stop" : "Type your question here..."}
          autoFocus
        />
        <VoiceInput 
          onTranscriptChange={handleVoiceTranscript}
          isListening={isListening}
          setIsListening={setIsListening}
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={!text.trim()}
        >
          Send 📤
        </button>
      </div>
    </form>
  );
}