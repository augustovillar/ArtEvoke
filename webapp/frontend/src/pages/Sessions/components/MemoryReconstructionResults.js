import React from 'react';
import { useTranslation } from 'react-i18next';
import './MemoryReconstructionResults.css';

const MemoryReconstructionResults = ({ data }) => {
    const { t } = useTranslation('common');

    const renderImageQuestion = (question, index) => {
        return (
            <div key={index} className="question-card image-question-card">
                <div className="question-header">
                    <h3>{t('results.imageQuestion')} {index + 1} {t('results.of')} {data.total_image_questions}</h3>
                    {question.time_spent && (
                        <span className="time-spent">
                            ⏱️ {question.time_spent}
                        </span>
                    )}
                </div>

                <div className="section-text">
                    <p>{question.section_text}</p>
                </div>

                <div className="images-grid">
                    {question.shown_images.map((image, imgIndex) => {
                        const isUserSelected = image.id === question.user_selected_image_id;
                        const isCorrect = image.id === question.correct_image_id;
                        const isDistractor = question.distractor_images.some(d => d.id === image.id);

                        let cardClass = 'image-card';
                        if (isUserSelected && isCorrect) {
                            cardClass += ' correct-answer user-selected';
                        } else if (isUserSelected && !isCorrect) {
                            cardClass += ' wrong-answer user-selected';
                        } else if (isCorrect) {
                            cardClass += ' correct-answer';
                        }

                        return (
                            <div key={imgIndex} className={cardClass}>
                                <img 
                                    src={image.image_url} 
                                    alt={image.art_name}
                                    onError={(e) => {
                                        e.target.src = '/placeholder-image.png';
                                    }}
                                />
                                <div className="image-info">
                                    <p className="image-name">{image.art_name}</p>
                                </div>
                                {isUserSelected && (
                                    <div className="selection-badge user-badge">
                                        {isCorrect ? '✓' : '✗'} {t('results.yourAnswer')}
                                    </div>
                                )}
                                {isCorrect && !isUserSelected && (
                                    <div className="selection-badge correct-badge">
                                        ✓ {t('results.correctAnswer')}
                                    </div>
                                )}
                                {isDistractor && (
                                    <div className="distractor-badge">
                                        {t('results.distractor')}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                <div className={`answer-summary ${question.is_correct ? 'correct' : 'incorrect'}`}>
                    {question.is_correct ? (
                        <p>✓ {t('results.correctlyAnswered')}</p>
                    ) : (
                        <p>✗ {t('results.incorrectlyAnswered')}</p>
                    )}
                </div>
            </div>
        );
    };

    const renderObjectiveQuestion = (question, index) => {
        const questionTypeLabels = {
            environment: t('results.questionTypes.environment'),
            period: t('results.questionTypes.period'),
            emotion: t('results.questionTypes.emotion')
        };

        return (
            <div key={index} className="question-card objective-question-card">
                <div className="question-header">
                    <h3>{questionTypeLabels[question.question_type] || question.question_type}</h3>
                    {question.time_spent && (
                        <span className="time-spent">
                            ⏱️ {question.time_spent}
                        </span>
                    )}
                </div>

                <div className="question-text">
                    <p>{question.question_text}</p>
                </div>

                <div className="options-list">
                    {question.options.map((option, optIndex) => {
                        const isUserAnswer = option === question.user_answer;
                        const isCorrectAnswer = option === question.correct_answer;

                        let optionClass = 'option-item';
                        if (isUserAnswer && isCorrectAnswer) {
                            optionClass += ' correct-option user-selected';
                        } else if (isUserAnswer && !isCorrectAnswer) {
                            optionClass += ' wrong-option user-selected';
                        } else if (isCorrectAnswer) {
                            optionClass += ' correct-option';
                        }

                        return (
                            <div key={optIndex} className={optionClass}>
                                <span className="option-text">{option}</span>
                                <div className="option-badges">
                                    {isUserAnswer && (
                                        <span className="badge user-badge">
                                            {isCorrectAnswer ? '✓' : '✗'} {t('results.yourAnswer')}
                                        </span>
                                    )}
                                    {isCorrectAnswer && !isUserAnswer && (
                                        <span className="badge correct-badge">
                                            ✓ {t('results.correctAnswer')}
                                        </span>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className={`answer-summary ${question.is_correct ? 'correct' : 'incorrect'}`}>
                    {question.is_correct ? (
                        <p>✓ {t('results.correctlyAnswered')}</p>
                    ) : (
                        <p>✗ {t('results.incorrectlyAnswered')}</p>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="memory-reconstruction-results">
            {/* Statistics Summary */}
            <div className="results-summary">
                <h2>{t('results.summaryTitle')}</h2>
                <div className="summary-cards">
                    <div className="summary-card">
                        <h3>{t('results.imageQuestions')}</h3>
                        <div className="summary-stats">
                            <span className="stat-value">{data.correct_image_answers}/{data.total_image_questions}</span>
                            <span className="stat-percentage">{data.image_accuracy}%</span>
                        </div>
                    </div>
                    <div className="summary-card">
                        <h3>{t('results.objectiveQuestions')}</h3>
                        <div className="summary-stats">
                            <span className="stat-value">{data.correct_objective_answers}/{data.total_objective_questions}</span>
                            <span className="stat-percentage">{data.objective_accuracy}%</span>
                        </div>
                    </div>
                    <div className="summary-card overall">
                        <h3>{t('results.overallAccuracy')}</h3>
                        <div className="summary-stats">
                            <span className="stat-value">
                                {data.correct_image_answers + data.correct_objective_answers}/
                                {data.total_image_questions + data.total_objective_questions}
                            </span>
                            <span className="stat-percentage large">{data.overall_accuracy}%</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Image Recognition Questions */}
            {data.image_questions && data.image_questions.length > 0 && (
                <div className="questions-section">
                    <h2>{t('results.imageRecognitionQuestions')}</h2>
                    <div className="questions-list">
                        {data.image_questions.map((question, index) => 
                            renderImageQuestion(question, index)
                        )}
                    </div>
                </div>
            )}

            {/* Objective Questions */}
            {data.objective_questions && data.objective_questions.length > 0 && (
                <div className="questions-section">
                    <h2>{t('results.objectiveQuestionsTitle')}</h2>
                    <div className="questions-list">
                        {data.objective_questions.map((question, index) => 
                            renderObjectiveQuestion(question, index)
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MemoryReconstructionResults;
