import React from 'react';
import './AccessibilityPanel.css';
import { useTheme } from './ThemeContext';
import FontSizeAdjuster from './FontSizeAdjuster';
import ReadAloudButton from './ReadAloudButton';
import { useTranslation } from 'react-i18next';

const AccessibilityPanel = ({ onClose }) => {
    const { toggleTheme } = useTheme();
    const { t } = useTranslation();

    return (
        <div className="accessibility-overlay" onClick={onClose}>
            <div className="accessibility-panel" onClick={(e) => e.stopPropagation()}>
                <button className="close-panel-button" onClick={onClose}>&times;</button>
                <h2>{t('accessibility.title')}</h2>

                <h3>{t('accessibility.changeColorTheme')}</h3>
                <button id='toggle-theme-button' onClick={toggleTheme}>{t('accessibility.toggleTheme')}</button>

                <FontSizeAdjuster />

                <h3>{t('accessibility.readPageAloud')}</h3>
                <ReadAloudButton />
            </div>
        </div>
    );
};

export default AccessibilityPanel;