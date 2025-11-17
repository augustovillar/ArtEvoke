import React from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionSection, TimeSpentBadge, AnswerSummary } from './ResultsComponents';
import './ResultsLayout.css';

/**
 * ChronologicalOrderQuestion - Displays the chronological ordering question result
 * Used by Art Exploration
 */
export const ChronologicalOrderQuestion = ({ question }) => {
    const { t } = useTranslation('common');

    return (
        <div className="question-card">
            <div className="question-header">
                <div className="header-left">
                    <h4>{t('results.chronologicalOrderQuestion')}</h4>
                </div>
                <TimeSpentBadge time={question.time_spent} />
            </div>

            <p className="question-instructions">{t('results.orderArtsByDate')}</p>

            <div className="chronological-comparison">
                {/* User's Order */}
                <div className="order-column">
                    <h5 className="order-title">{t('results.yourOrder')}</h5>
                    <div className="arts-order-list">
                        {question.user_events && question.user_events.map((event, index) => {
                            const isInCorrectPosition = question.is_correct_per_position?.[index];
                            
                            return (
                                <div 
                                    key={index}
                                    className={`art-order-item ${
                                        isInCorrectPosition 
                                            ? 'art-order-correct' 
                                            : 'art-order-incorrect'
                                    }`}
                                >
                                    <div className="order-number">{index + 1}</div>
                                    <div className="order-art-info">
                                        <p className="order-art-name">{event}</p>
                                    </div>
                                    {isInCorrectPosition ? (
                                        <span className="position-badge badge-correct-position">✓</span>
                                    ) : (
                                        <span className="position-badge badge-incorrect-position">✗</span>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Correct Order */}
                <div className="order-column">
                    <h5 className="order-title">{t('results.artExploration.correctOrder')}</h5>
                    <div className="arts-order-list">
                        {question.correct_events && question.correct_events.map((event, index) => (
                            <div key={index} className="art-order-item art-order-reference">
                                <div className="order-number">{index + 1}</div>
                                <div className="order-art-info">
                                    <p className="order-art-name">{event}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <AnswerSummary 
                isCorrect={question.is_fully_correct}
                correctText={t('results.chronologicalOrderCorrect')}
                incorrectText={t('results.chronologicalOrderIncorrect')}
            />
        </div>
    );
};

/**
 * ChronologicalOrderSection - Wraps the chronological ordering question
 */
export const ChronologicalOrderSection = ({ question }) => {
    const { t } = useTranslation('common');

    if (!question) return null;

    return (
        <QuestionSection 
            title={t('results.chronologicalOrder')} 
            borderColor="purple"
        >
            <ChronologicalOrderQuestion question={question} />
        </QuestionSection>
    );
};
