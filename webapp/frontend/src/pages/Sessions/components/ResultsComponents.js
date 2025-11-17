import React from 'react';
import { useTranslation } from 'react-i18next';
import './ResultsLayout.css';

/**
 * SummaryCard - Reusable summary statistics card component
 */
export const SummaryCard = ({ 
    title, 
    correct, 
    total, 
    accuracy, 
    color = 'blue',
    isOverall = false 
}) => {
    const { t } = useTranslation('common');

    return (
        <div className={`summary-card ${color}`}>
            <h3>{title}</h3>
            <div className="card-content">
                {!isOverall ? (
                    <>
                        <div className="stat-row">
                            <span className="stat-label">{t('results.summary.correct')}:</span>
                            <span className="stat-value">{correct}/{total}</span>
                        </div>
                        <div className="accuracy-bar">
                            <div 
                                className="accuracy-fill"
                                style={{ width: `${accuracy}%` }}
                            />
                        </div>
                        <div className="accuracy-text">
                            {accuracy.toFixed(1)}%
                        </div>
                    </>
                ) : (
                    <div className="overall-score">
                        {accuracy.toFixed(1)}%
                    </div>
                )}
            </div>
        </div>
    );
};

/**
 * QuestionSection - Wrapper for question groups
 */
export const QuestionSection = ({ title, children, borderColor = 'blue' }) => {
    return (
        <div className={`question-section border-${borderColor}`}>
            <h3>{title}</h3>
            {children}
        </div>
    );
};

/**
 * TimeSpentBadge - Display time spent on a question
 */
export const TimeSpentBadge = ({ time }) => {
    if (!time) return null;
    return <span className="time-badge">⏱️ {time}</span>;
};

/**
 * AnswerSummary - Shows if answer was correct or incorrect
 */
export const AnswerSummary = ({ isCorrect, correctText, incorrectText }) => {
    return (
        <div className={`answer-summary ${isCorrect ? 'correct' : 'incorrect'}`}>
            <p>{isCorrect ? `✓ ${correctText}` : `✗ ${incorrectText}`}</p>
        </div>
    );
};
