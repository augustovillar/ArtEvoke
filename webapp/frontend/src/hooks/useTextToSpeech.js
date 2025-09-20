import { useState, useRef } from 'react';

export const useTextToSpeech = () => {
    const [isReading, setIsReading] = useState(false);
    const utteranceRef = useRef(null);

    const readAloud = (textBlocks = []) => {
        // Stop any global reading first
        window.speechSynthesis.cancel();

        const fullText = textBlocks.join('. ');
        if (!fullText) return;

        const utterance = new SpeechSynthesisUtterance(fullText);
        utterance.lang = 'en-US';

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