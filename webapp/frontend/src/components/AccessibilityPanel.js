import React from 'react';
import './AccessibilityPanel.css';
import { useTheme } from './ThemeContext';
import FontSizeAdjuster from './FontSizeAdjuster';
import ReadAloudButton from './ReadAloudButton';

const AccessibilityPanel = ({ onClose }) => {
    const { toggleTheme } = useTheme();

    return (
        <div className="accessibility-overlay" onClick={onClose}>
            <div className="accessibility-panel" onClick={(e) => e.stopPropagation()}>
                <button className="close-panel-button" onClick={onClose}>&times;</button>
                <h2>Accessibility Options</h2>

                <h3>Change Color Theme</h3>
                <button id='toggle-theme-button' onClick={toggleTheme}>Toggle Theme</button>

                <FontSizeAdjuster />

                <h3>Read Page Aloud</h3>
                <ReadAloudButton />
            </div>
        </div>
    );
};

export default AccessibilityPanel;