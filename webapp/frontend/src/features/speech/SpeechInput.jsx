import React, { useState, useRef, useEffect } from 'react';

export default function SpeechInput({ onChange, initialValue = '' }) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser. Try using Google Chrome.');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const speechResult = event.results[0][0].transcript;
      onChange(prev => `${prev} ${speechResult}`);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
    setIsListening(true);
    recognitionRef.current = recognition;
  };

  return (
    <div style={{ marginTop: '1rem' }}>
      <button
        type="button"
        onClick={startListening}
        disabled={isListening}
        style={{
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          backgroundColor: isListening ? '#var(--button-hover-bg)' : 'var(--button-bg)',
          color: 'var(--button-text)',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: isListening ? 'default' : 'pointer',
        }}
      >
        🎤 {isListening ? 'Listening...' : 'Speak'}
      </button>
    </div>
  );
}
