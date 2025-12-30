import { useState } from "react";

export default function InputBox({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    console.log("InputBox sending:", text); // Debug log
    onSend(text);
    setText("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="message-form">
      <div className="input-container">
        <input
          type="text"
          className="message-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question here..."
          autoFocus
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={!text.trim()}
        >
          Send
        </button>
      </div>
    </form>
  );
}