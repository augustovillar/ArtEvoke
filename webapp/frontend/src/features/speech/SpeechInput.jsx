import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

export default function SpeechInput({ onChange, initialValue = '', onInterimText, onProcessingChange, improveText = true }) {
  const { t, i18n } = useTranslation();
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef(null);
  const accumulatedTextRef = useRef('');
  const baseTextRef = useRef(initialValue || '');
  const processedResultsRef = useRef(new Set()); // Track processed result indices
  const lastInterimRef = useRef(''); // Track last interim result to avoid duplicates

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
    processedResultsRef.current = new Set();
    lastInterimRef.current = '';

    recognition.onresult = (event) => {
      let currentInterim = '';
      
      // Process all results
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript.trim();
        
        if (!transcript) continue;
        
        const resultKey = `${i}-${transcript}`;
        
        if (result.isFinal) {
          if (!processedResultsRef.current.has(resultKey)) {
            processedResultsRef.current.add(resultKey);
            
            const normalizedNew = transcript.toLowerCase().replace(/\s+/g, ' ').trim();
            const normalizedAccumulated = accumulatedTextRef.current.toLowerCase().replace(/\s+/g, ' ').trim();
            
            if (normalizedAccumulated) {
              if (normalizedNew.startsWith(normalizedAccumulated)) {
                accumulatedTextRef.current = transcript + ' ';
              } 
              else if (!normalizedAccumulated.startsWith(normalizedNew)) {
                const newWords = normalizedNew.split(' ');
                const accumulatedWords = normalizedAccumulated.split(' ');
                
                let overlapLength = 0;
                for (let j = 1; j <= Math.min(accumulatedWords.length, newWords.length); j++) {
                  const accumulatedEnd = accumulatedWords.slice(-j).join(' ');
                  const newStart = newWords.slice(0, j).join(' ');
                  if (accumulatedEnd === newStart) {
                    overlapLength = j;
                  }
                }
                
                if (overlapLength > 0) {
                  const mergedWords = [
                    ...accumulatedWords,
                    ...newWords.slice(overlapLength)
                  ].join(' ');
                  accumulatedTextRef.current = mergedWords + ' ';
                } else {
                  accumulatedTextRef.current += transcript + ' ';
                }
              }
            } else {
              accumulatedTextRef.current = transcript + ' ';
            }
          }
        } else {
          const normalizedInterim = transcript.toLowerCase().replace(/\s+/g, ' ').trim();
          const normalizedLastInterim = lastInterimRef.current.toLowerCase().replace(/\s+/g, ' ').trim();
          
          if (normalizedInterim !== normalizedLastInterim && 
              normalizedInterim.length >= normalizedLastInterim.length) {
            currentInterim = transcript;
            lastInterimRef.current = transcript;
          } else if (normalizedInterim === normalizedLastInterim) {
            currentInterim = lastInterimRef.current;
          }
        }
      }
      
      const currentText = baseTextRef.current;
      const accumulatedFinal = accumulatedTextRef.current.trim();
      const interimToShow = currentInterim.trim();
      
      let totalText = currentText;
      if (accumulatedFinal) {
        totalText = totalText ? `${totalText} ${accumulatedFinal}` : accumulatedFinal;
      }
      if (interimToShow) {
        totalText = totalText ? `${totalText} ${interimToShow}` : interimToShow;
      }
      totalText = totalText.trim();
      
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
      
      processedResultsRef.current = new Set();
      lastInterimRef.current = '';
      
      const textToProcess = accumulatedTextRef.current.trim();
      if (textToProcess) {
        const currentText = baseTextRef.current;
        const fullText = currentText ? `${currentText} ${textToProcess}` : textToProcess;
        
        if (onInterimText) {
          onInterimText(fullText, false); // Show text first
        } else {
          onChange(fullText);
        }
        
        if (!improveText) {
          baseTextRef.current = fullText;
          onChange(fullText);
          accumulatedTextRef.current = '';
          return;
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        setIsProcessing(true);
        if (onProcessingChange) {
          onProcessingChange(true);
        }
        if (onInterimText) {
          onInterimText(fullText, true); // true = isProcessing (gray out)
        }
        
        const correctedText = await correctText(textToProcess, currentLang);
        
        const newBaseText = currentText ? `${currentText} ${correctedText}` : correctedText;
        baseTextRef.current = newBaseText;
        
        onChange(newBaseText);
        
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
