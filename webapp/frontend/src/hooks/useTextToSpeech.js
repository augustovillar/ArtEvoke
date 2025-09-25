import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

export const useTextToSpeech = () => {
    const { i18n } = useTranslation();
    const [isReading, setIsReading] = useState(false);
    const utteranceRef = useRef(null);

    const readAloud = (textBlocks = []) => {
        // Stop any global reading first
        window.speechSynthesis.cancel();

        const fullText = textBlocks.join('. ');
        if (!fullText) return;

        const utterance = new SpeechSynthesisUtterance(fullText);

        // Set language dynamically
        const currentLang = i18n.language;
        if (currentLang === 'pt') {
            utterance.lang = 'pt-BR';
        } else if (currentLang === 'en') {
            utterance.lang = 'en-US';
        } else {
            utterance.lang = 'en-US'; // Default
        }

        utterance.onend = () => setIsReading(false);
        utterance.onerror = () => setIsReading(false);

        utteranceRef.current = utterance;
        setIsReading(true);
        window.speechSynthesis.speak(utterance);
    };

    const cancel = () => {
        window.speechSynthesis.cancel();
        setIsReading(false);
    };

    return { isReading, readAloud, cancel };
};