import { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const VoiceInput = ({ onTranscriptChange, isListening, setIsListening, isConnected = true }) => {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const [error, setError] = useState('');

  useEffect(() => {
    console.log('Transcript changed:', transcript);
    
    // Only send final transcript when not listening anymore
    if (transcript && !listening) {
      console.log('Sending final transcript:', transcript);
      onTranscriptChange(transcript);
      resetTranscript(); // Reset after sending
    }
  }, [transcript, listening, onTranscriptChange, resetTranscript]);

  useEffect(() => {
    console.log('Listening state changed:', listening);
    setIsListening(listening);
    
    // Clear text when starting to listen
    if (listening) {
      onTranscriptChange('');
    }
  }, [listening, setIsListening, onTranscriptChange]);

  const startListening = () => {
    console.log('Starting listening...');
    
    // Check connection before starting voice input
    if (!isConnected) {
      setError('Cannot use voice input: Not connected to server');
      setTimeout(() => setError(''), 3000);
      return;
    }
    
    setError('');
    onTranscriptChange(''); // Clear text box immediately
    resetTranscript(); // Clear any pending transcript
    
    if (!browserSupportsSpeechRecognition) {
      setError('Browser does not support speech recognition');
      setTimeout(() => setError(''), 3000);
      return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        console.log('Microphone permission granted');
        stream.getTracks().forEach(track => track.stop());
        
        SpeechRecognition.startListening({ 
          continuous: true,
          language: 'en-US',
          interimResults: true
        });
      })
      .catch(err => {
        console.error('Microphone error:', err);
        setError('Microphone access denied. Please allow microphone access.');
        setTimeout(() => setError(''), 3000);
      });
  };

  const stopListening = () => {
    console.log('Stopping listening...');
    SpeechRecognition.stopListening();
  };

  const handleVoiceClick = () => {
    if (listening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Get button styles based on state
  const getButtonStyles = () => {
    if (!isConnected) {
      return {
        width: '45px',
        height: '45px',
        borderRadius: '50%',
        border: 'none',
        background: '#ccc',
        color: '#999',
        fontSize: '20px',
        cursor: 'not-allowed',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        margin: 0,
        padding: 0,
        opacity: 0.5
      };
    }
    
    if (listening) {
      return {
        width: '45px',
        height: '45px',
        borderRadius: '50%',
        border: 'none',
        background: '#ef4444',
        color: 'white',
        fontSize: '20px',
        cursor: 'pointer',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        margin: 0,
        padding: 0,
        animation: 'pulse 1.5s infinite',
        boxShadow: '0 0 10px rgba(239, 68, 68, 0.5)'
      };
    }
    
    return {
      width: '45px',
      height: '45px',
      borderRadius: '50%',
      border: 'none',
      background: '#646cff',
      color: 'white',
      fontSize: '20px',
      cursor: 'pointer',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
      margin: 0,
      padding: 0,
      transition: 'all 0.3s ease'
    };
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <button 
        type="button"
        className="voice-btn-disabled"
        title="Speech recognition not supported"
        style={{
          width: '45px',
          height: '45px',
          borderRadius: '50%',
          border: 'none',
          background: '#ccc',
          color: 'white',
          fontSize: '20px',
          cursor: 'not-allowed',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}
      >
        🎤
      </button>
    );
  }

  return (
    <>
      <button
        type="button"
        onClick={handleVoiceClick}
        style={getButtonStyles()}
        title={
          !isConnected 
            ? "Waiting for connection..." 
            : listening 
              ? "Stop listening" 
              : "Start voice input"
        }
        disabled={!isConnected}
      >
        {listening ? '🔴' : '🎤'}
      </button>
      {error && (
        <div style={{
          position: 'absolute',
          bottom: '70px',
          right: '20px',
          background: '#ef4444',
          color: 'white',
          padding: '8px 12px',
          borderRadius: '8px',
          fontSize: '12px',
          zIndex: 1000
        }}>
          {error}
        </div>
      )}
    </>
  );
};

export default VoiceInput;