import React from "react";

export default function QuickReplies({ replies, onQuickReply }) {
  return (
    <div className="quick-replies">
      <p className="quick-replies-label">Quick questions:</p>
      <div className="quick-replies-container">
        {replies.map((reply, index) => (
          <button
            key={index}
            className="quick-reply-btn"
            onClick={() => onQuickReply(reply)}
          >
            {reply}
          </button>
        ))}
      </div>
    </div>
  );
}