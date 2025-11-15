import React from 'react';
import { useTranslation } from 'react-i18next';
import './ArtExplorationResults.css';

const ArtExplorationResults = ({ data }) => {
    const { t } = useTranslation('common');

    const renderSummaryCards = () => {
        return (
            <div className="summary-cards">
                <div className="summary-card objective-card">
                    <h3>{t('results.summary.objectiveQuestions')}</h3>
                    <div className="card-content">
                        <div className="stat-row">
                            <span className="stat-label">{t('results.summary.correct')}:</span>
                            <span className="stat-value">{data.correct_objective_answers}/{data.total_objective_questions}</span>
                        </div>
                        <div className="accuracy-bar">
                            <div 
                                className="accuracy-fill objective-fill"
                                style={{ width: `${data.objective_accuracy}%` }}
                            />
                        </div>
                        <div className="accuracy-text">{data.objective_accuracy.toFixed(1)}%</div>
                    </div>
                </div>

                <div className="summary-card chronological-card">
                    <h3>{t('results.summary.chronologicalOrder')}</h3>
                    <div className="card-content">
                        <div className="stat-row">
                            <span className="stat-label">{t('results.summary.correctPositions')}:</span>
                            <span className="stat-value">
                                {data.chronological_positions_correct}/{data.chronological_total_positions}
                            </span>
                        </div>
                        <div className="accuracy-bar">
                            <div 
                                className="accuracy-fill chronological-fill"
                                style={{ width: `${data.chronological_accuracy}%` }}
                            />
                        </div>
                        <div className="accuracy-text">{data.chronological_accuracy.toFixed(1)}%</div>
                    </div>
                </div>

                <div className="summary-card overall-card">
                    <h3>{t('results.summary.overallAccuracy')}</h3>
                    <div className="card-content">
                        <div className="overall-score">{data.overall_accuracy.toFixed(1)}%</div>
                    </div>
                </div>
            </div>
        );
    };

    const renderStoryQuestion = () => {
        if (!data.story_question) return null;

        return (
            <div className="question-section story-section">
                <h3>{t('results.artExploration.storyQuestion')}</h3>
                <div className="story-answer">
                    <div className="answer-header">
                        <span className="answer-label">{t('results.patientAnswer')}:</span>
                        {data.story_question.time_spent && (
                            <span className="time-badge">{data.story_question.time_spent}</span>
                        )}
                    </div>
                    <p className="answer-text">{data.story_question.user_answer}</p>
                </div>
            </div>
        );
    };

    const renderChronologicalOrder = () => {
        if (!data.chronological_order_question) return null;

        const chronoData = data.chronological_order_question;

        return (
            <div className="question-section chronological-section">
                <h3>{t('results.artExploration.chronologicalOrder')}</h3>
                
                <div className="chronological-header">
                    {chronoData.time_spent && (
                        <span className="time-badge">{chronoData.time_spent}</span>
                    )}
                    {chronoData.is_fully_correct ? (
                        <span className="result-badge correct-badge">
                            ✓ {t('results.allCorrect')}
                        </span>
                    ) : (
                        <span className="result-badge partial-badge">
                            {chronoData.correct_positions_count}/4 {t('results.correctPositions')}
                        </span>
                    )}
                </div>

                <div className="chronological-comparison">
                    <div className="order-column">
                        <h4>{t('results.artExploration.patientOrder')}</h4>
                        <div className="order-list">
                            {chronoData.user_events.map((event, position) => {
                                const isCorrect = chronoData.is_correct_per_position[position];
                                
                                return (
                                    <div key={position} className={`order-item ${isCorrect ? 'correct' : 'incorrect'}`}>
                                        <span className="position-number">{position + 1}.</span>
                                        <div className="order-event-info">
                                            <p className="event-text">{event}</p>
                                        </div>
                                        <span className={`position-indicator ${isCorrect ? 'correct' : 'incorrect'}`}>
                                            {isCorrect ? '✓' : '✗'}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="order-column">
                        <h4>{t('results.artExploration.correctOrder')}</h4>
                        <div className="order-list">
                            {chronoData.correct_events.map((event, position) => {
                                return (
                                    <div key={position} className="order-item correct">
                                        <span className="position-number">{position + 1}.</span>
                                        <div className="order-event-info">
                                            <p className="event-text">{event}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderObjectiveQuestions = () => {
        if (!data.objective_questions || data.objective_questions.length === 0) {
            return null;
        }

        return (
            <div className="question-section objective-section">
                <h3>{t('results.objectiveQuestions')}</h3>
                <div className="objective-questions-list">
                    {data.objective_questions.map((question, index) => (
                        <div key={index} className={`objective-question ${question.is_correct ? 'correct' : 'incorrect'}`}>
                            <div className="question-header">
                                <span className="question-number">{index + 1}.</span>
                                <span className="question-text">{question.question_text}</span>
                                {question.time_spent && (
                                    <span className="time-badge">{question.time_spent}</span>
                                )}
                            </div>
                            
                            <div className="options-list">
                                {question.options.map((option, optIndex) => {
                                    const isUserAnswer = option === question.user_answer;
                                    const isCorrectAnswer = option === question.correct_answer;
                                    
                                    let className = 'option-item';
                                    if (isUserAnswer && isCorrectAnswer) {
                                        className += ' user-correct';
                                    } else if (isUserAnswer) {
                                        className += ' user-incorrect';
                                    } else if (isCorrectAnswer) {
                                        className += ' correct-answer';
                                    }
                                    
                                    return (
                                        <div key={optIndex} className={className}>
                                            <span className="option-text">{option}</span>
                                            {isUserAnswer && <span className="selection-badge">{t('results.selected')}</span>}
                                            {isCorrectAnswer && <span className="correct-badge">✓</span>}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="art-exploration-results">
            <div className="results-header">
                <h2>{t('results.title')}</h2>
                <div className="results-meta">
                    <span className="meta-item">{t('results.dataset')}: {data.dataset}</span>
                    <span className="meta-item">{t('results.language')}: {data.language}</span>
                </div>
            </div>

            {renderSummaryCards()}
            {renderStoryQuestion()}
            {renderChronologicalOrder()}
            {renderObjectiveQuestions()}
        </div>
    );
};

export default ArtExplorationResults;
