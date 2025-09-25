import React from 'react';
import { useReadAloud } from '../contexts/ReadAloudContext';
import './ReadAloudButton.css';
import { useTranslation } from 'react-i18next';

const ReadAloudButton = () => {
    const { readAloud, isReading, stopReading } = useReadAloud();
    const { t } = useTranslation();

    const handleClick = () => {
        if (isReading) {
            stopReading();
        } else {
            readAloud();
        }
    };

    return (
        <button
            onClick={handleClick}
            className={`read-aloud-button ${isReading ? 'reading' : ''}`}
        >
            {isReading ? t('accessibility.stopReading') : t('accessibility.readAloudButton')}
        </button>
    );
};

export default ReadAloudButton;