import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTextToSpeech } from '../../hooks/useTextToSpeech';
import './QuestionReadAloudButton.css';

const QuestionReadAloudButton = ({ text, className = '' }) => {
    const { t } = useTranslation();
    const { speak, stop, isPlaying } = useTextToSpeech();

    const handleClick = () => {
        if (isPlaying) {
            stop();
        } else {
            speak(text);
        }
    };

    if (!text || text.trim() === '') {
        return null;
    }

    return (
        <button
            onClick={handleClick}
            className={`question-read-aloud-button ${isPlaying ? 'reading' : ''} ${className}`}
            title={isPlaying ? t('accessibility.stopReading') : t('accessibility.readQuestion')}
        >
            <span className="icon">
                {isPlaying ? '🔊' : '🔉'}
            </span>
            <span className="text">
                {isPlaying 
                    ? (t('accessibility.stopReading') || 'Parar') 
                    : (t('accessibility.readQuestion') || 'Ler Pergunta')
                }
            </span>
        </button>
    );
};

export default QuestionReadAloudButton;