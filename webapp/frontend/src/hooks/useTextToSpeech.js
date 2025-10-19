import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

export const useTextToSpeech = () => {
    const { i18n } = useTranslation();
    const [isPlaying, setIsPlaying] = useState(false);
    const utteranceRef = useRef(null);

    const speak = (text) => {
        // Stop any ongoing speech
        window.speechSynthesis.cancel();

        if (!text || text.trim() === '') return;

        const utterance = new SpeechSynthesisUtterance(text.trim());

        // Set language dynamically
        const currentLang = i18n.language;
        if (currentLang === 'pt') {
            utterance.lang = 'pt-BR';
        } else if (currentLang === 'en') {
            utterance.lang = 'en-US';
        } else {
            utterance.lang = 'en-US'; // Default
        }

        utterance.onstart = () => setIsPlaying(true);
        utterance.onend = () => setIsPlaying(false);
        utterance.onerror = () => setIsPlaying(false);

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    const stop = () => {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
    };

    // Legacy support
    const readAloud = (textBlocks = []) => {
        const fullText = textBlocks.join('. ');
        speak(fullText);
    };

    const cancel = stop; // Legacy support

    return { 
        isPlaying, 
        isReading: isPlaying, // Legacy support
        speak, 
        stop, 
        readAloud, // Legacy support
        cancel // Legacy support
    };
};