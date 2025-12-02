import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

export default function SpeechInput({ onChange, initialValue = '', onInterimText, onProcessingChange, improveText = true }) {
  const { t, i18n } = useTranslation();
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef(null);
  const accumulatedTextRef = useRef('');
  const baseTextRef = useRef(initialValue || '');

  const correctText = async (text, language) => {
    try {
      setIsProcessing(true);
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
      
      const response = await fetch('/api/memory/improve-text', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          raw_text: text,
          language: language
        })
      });

      if (!response.ok) {
        throw new Error('Failed to correct text');
      }

      const data = await response.json();
      return data.processed_text;
    } catch (error) {
      console.error('Error correcting text:', error);
      // Return original text if correction fails
      return text;
    } finally {
      setIsProcessing(false);
    }
  };

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser. Try using Google Chrome.');
      return;
    }

    const currentLang = i18n.language.split('-')[0];
    const recognitionLang = currentLang === 'pt' ? 'pt-BR' : 'en-US';
    
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = recognitionLang;
    recognition.interimResults = true; // Enable interim results for real-time updates
    recognition.maxAlternatives = 1;
    recognition.continuous = true;

    accumulatedTextRef.current = '';
    baseTextRef.current = initialValue || '';

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        } else {
          interimTranscript += event.results[i][0].transcript + ' ';
        }
      }
      
      // Accumulate final results (don't add to base yet, wait until processing)
      if (finalTranscript.trim()) {
        accumulatedTextRef.current += finalTranscript;
      }
      
      // Show text in real-time (base + accumulated final + interim)
      const currentText = baseTextRef.current;
      const totalText = (currentText + ' ' + accumulatedTextRef.current + ' ' + interimTranscript).trim();
      
      if (onInterimText) {
        onInterimText(totalText, false);
      } else {
        onChange(totalText);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.onend = async () => {
      setIsListening(false);
      
      // Process accumulated text when recording ends
      const textToProcess = accumulatedTextRef.current.trim();
      if (textToProcess) {
        const currentText = baseTextRef.current;
        const fullText = currentText ? `${currentText} ${textToProcess}` : textToProcess;
        
        // Show the text that will be processed (before correction)
        if (onInterimText) {
          onInterimText(fullText, false); // Show text first
        } else {
          onChange(fullText);
        }
        
        // If text improvement is disabled, just add the text directly
        if (!improveText) {
          // Update base text with new text (no correction)
          baseTextRef.current = fullText;
          onChange(fullText);
          accumulatedTextRef.current = '';
          return;
        }
        
        // Small delay to ensure text is displayed before processing
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Notify parent that we're processing (to gray out the text)
        setIsProcessing(true);
        if (onProcessingChange) {
          onProcessingChange(true);
        }
        if (onInterimText) {
          onInterimText(fullText, true); // true = isProcessing (gray out)
        }
        
        // Process and get corrected text
        const correctedText = await correctText(textToProcess, currentLang);
        
        // Update base text with corrected text
        const newBaseText = currentText ? `${currentText} ${correctedText}` : correctedText;
        baseTextRef.current = newBaseText;
        
        // Update with corrected text
        onChange(newBaseText);
        
        // Clear processing state
        setIsProcessing(false);
        if (onProcessingChange) {
          onProcessingChange(false);
        }
        if (onInterimText) {
          onInterimText(newBaseText, false);
        }
        
        accumulatedTextRef.current = '';
      }
    };

    recognition.start();
    setIsListening(true);
    recognitionRef.current = recognition;
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  return (
    <div style={{ marginTop: '1rem', position: 'relative' }}>
      {isListening ? (
        <button
          type="button"
          onClick={stopListening}
          disabled={isProcessing}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
          }}
        >
          ⏹️ {t('speech.stop') || 'Stop'}
        </button>
      ) : (
        <button
          type="button"
          onClick={startListening}
          disabled={isProcessing}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1rem',
            backgroundColor: isProcessing ? '#ccc' : 'var(--button-bg)',
            color: 'var(--button-text)',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: isProcessing ? 'default' : 'pointer',
          }}
        >
          🎤 {isProcessing ? (t('speech.processing') || 'Processing...') : t('speech.speak')}
        </button>
      )}
    </div>
  );
}
