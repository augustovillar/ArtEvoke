import React from 'react';
import { useReadAloud } from '../contexts/ReadAloudContext';
import './ReadAloudButton.css';

const ReadAloudButton = () => {
    const { readAloud, isReading, stopReading } = useReadAloud();

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
            {isReading ? 'Stop Reading' : 'Read Aloud'}
        </button>
    );
};

export default ReadAloudButton;