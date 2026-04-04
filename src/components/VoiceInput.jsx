import { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const VoiceInput = ({ onTranscriptChange, isListening, setIsListening }) => {
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
    setError('');
    onTranscriptChange(''); // Clear text box immediately
    resetTranscript(); // Clear any pending transcript
    
    if (!browserSupportsSpeechRecognition) {
      setError('Browser does not support speech recognition');
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
    <button
      type="button"
      onClick={handleVoiceClick}
      style={{
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
        transition: 'none'
      }}
    >
      🎤
    </button>
  );
};

export default VoiceInput;