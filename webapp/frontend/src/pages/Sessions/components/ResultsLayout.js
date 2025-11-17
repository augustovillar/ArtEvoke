import React from 'react';
import { useTranslation } from 'react-i18next';
import { SummaryCard } from './ResultsComponents';
import './ResultsLayout.css';

/**
 * ResultsLayout - Base component for displaying session results
 * Provides consistent structure and styling for both Memory Reconstruction and Art Exploration results
 */
const ResultsLayout = ({ 
    title,
    dataset, 
    language, 
    story,
    summaryCards, 
    children 
}) => {
    const { t } = useTranslation('common');

    return (
        <div className="results-layout">
            {/* Header with metadata */}
            <div className="results-header">
                <h2>{title || t('results.title')}</h2>
                <div className="results-meta">
                    <span className="meta-item">
                        <strong>{t('results.dataset')}:</strong> {dataset}
                    </span>
                    <span className="meta-item">
                        <strong>{t('results.language')}:</strong> {language}
                    </span>
                </div>
            </div>

            {/* Story Section (if provided) */}
            {story && (
                <div className="results-story-section">
                    <h3>{t('results.generatedStory')}</h3>
                    <div className="story-content">
                        <p>{story}</p>
                    </div>
                </div>
            )}

            {/* Summary Statistics Cards */}
            {summaryCards && summaryCards.length > 0 && (
                <div className="summary-cards-section">
                    <div className="summary-cards">
                        {summaryCards.map((card, index) => (
                            <SummaryCard 
                                key={index}
                                title={card.title}
                                correct={card.correct}
                                total={card.total}
                                accuracy={card.accuracy}
                                color={card.color}
                                isOverall={card.isOverall}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Question Results Content */}
            <div className="results-questions-section">
                {children}
            </div>
        </div>
    );
};

export default ResultsLayout;
