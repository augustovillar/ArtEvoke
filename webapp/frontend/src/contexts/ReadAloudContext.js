import React, { createContext, useState, useContext, useRef, useEffect, useCallback } from 'react';

const ReadAloudContext = createContext();

export const useReadAloud = () => {
    const context = useContext(ReadAloudContext);
    if (context === undefined) {
        throw new Error('useReadAloud must be used within a ReadAloudProvider');
    }
    return context;
};

export const ReadAloudProvider = ({ children }) => {
    const [currentContentRef, setCurrentContentRef] = useState(null);
    const [extraText, setExtraText] = useState([]);

    const [isReading, setIsReading] = useState(false);
    const synthRef = useRef(window.speechSynthesis);
    const utteranceRef = useRef(null);

    const registerContent = useCallback((ref, textArray = []) => {
        setCurrentContentRef(ref);
        setExtraText(textArray);
    }, []);

    const readAloud = useCallback(() => {
        if (!currentContentRef || !currentContentRef.current) {
            console.warn("No content reference registered for Read Aloud.");
            return;
        }

        const synth = synthRef.current;
        if (!synth) {
            console.error("Speech synthesis not supported in this browser.");
            return;
        }

        // Stop any ongoing speech
        if (isReading) {
            synth.cancel();
            setIsReading(false);
            return;
        }

        // Get text from the ref's content
        let textToSpeak = '';
        if (currentContentRef.current.innerText) {
            textToSpeak += currentContentRef.current.innerText;
        } else if (currentContentRef.current.textContent) {
            textToSpeak += currentContentRef.current.textContent;
        }

        // Add any extra text provided by the component
        if (extraText.length > 0) {
            textToSpeak += "\n\n" + extraText.join("\n");
        }

        if (textToSpeak.trim() === '') {
            console.warn("No text to speak from the registered content.");
            return;
        }

        // Clean up text (remove excessive whitespace/newlines)
        textToSpeak = textToSpeak.replace(/\s\s+/g, ' ').trim();

        utteranceRef.current = new SpeechSynthesisUtterance(textToSpeak);

        utteranceRef.current.onstart = () => setIsReading(true);
        utteranceRef.current.onend = () => setIsReading(false);
        utteranceRef.current.onerror = (event) => {
            console.error('SpeechSynthesisUtterance.onerror', event);
            setIsReading(false);
        };

        synth.speak(utteranceRef.current);
    }, [currentContentRef, extraText, isReading]);

    useEffect(() => {
        const synth = synthRef.current;
        return () => {
            if (synth && utteranceRef.current && isReading) { // Only cancel if currently speaking
                synth.cancel();
            }
        };
    }, [isReading]);

    // Added a specific stopReading function
    const stopReading = useCallback(() => {
        const synth = synthRef.current;
        if (synth && isReading) {
            synth.cancel();
            setIsReading(false);
        }
    }, [isReading]);

    return (
        <ReadAloudContext.Provider value={{ registerContent, readAloud, stopReading, isReading }}>
            {children}
        </ReadAloudContext.Provider>
    );
};