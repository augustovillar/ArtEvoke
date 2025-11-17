import React from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionSection, TimeSpentBadge, AnswerSummary } from './ResultsComponents';
import './ResultsLayout.css';

/**
 * ObjectiveQuestionCard - Displays a single objective question result
 * Used by both Memory Reconstruction and Art Exploration
 */
export const ObjectiveQuestionCard = ({ question, index }) => {
    const { t } = useTranslation('common');

    const questionTypeLabels = {
        environment: t('results.questionTypes.environment'),
        period: t('results.questionTypes.period'),
        emotion: t('results.questionTypes.emotion')
    };

    return (
        <div className="question-card">
            <div className="question-header">
                <div className="header-left">
                    <span className="question-number">{index + 1}.</span>
                    <h4>{questionTypeLabels[question.question_type] || question.question_type}</h4>
                </div>
                <TimeSpentBadge time={question.time_spent} />
            </div>

            <div className="question-text-box">
                <p>{question.question_text}</p>
            </div>

            <div className="options-list">
                {question.options.map((option, optIndex) => {
                    const isUserAnswer = option === question.user_answer;
                    const isCorrectAnswer = option === question.correct_answer;

                    let optionClass = 'option-item';
                    if (isUserAnswer && isCorrectAnswer) {
                        optionClass += ' option-user-correct';
                    } else if (isUserAnswer) {
                        optionClass += ' option-user-incorrect';
                    } else if (isCorrectAnswer) {
                        optionClass += ' option-correct';
                    }

                    return (
                        <div key={optIndex} className={optionClass}>
                            <span className="option-text">{option}</span>
                            <div className="option-badges">
                                {isUserAnswer && (
                                    <span className="badge badge-user">
                                        {isCorrectAnswer ? '✓' : '✗'} {t('results.yourAnswer')}
                                    </span>
                                )}
                                {isCorrectAnswer && !isUserAnswer && (
                                    <span className="badge badge-correct">
                                        ✓ {t('results.correctAnswer')}
                                    </span>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <AnswerSummary 
                isCorrect={question.is_correct}
                correctText={t('results.correctlyAnswered')}
                incorrectText={t('results.incorrectlyAnswered')}
            />
        </div>
    );
};

/**
 * ObjectiveQuestionsSection - Groups all objective questions
 */
export const ObjectiveQuestionsSection = ({ questions }) => {
    const { t } = useTranslation('common');

    if (!questions || questions.length === 0) return null;

    return (
        <QuestionSection 
            title={t('results.objectiveQuestionsTitle')} 
            borderColor="red"
        >
            <div className="questions-list">
                {questions.map((question, index) => (
                    <ObjectiveQuestionCard 
                        key={index} 
                        question={question} 
                        index={index} 
                    />
                ))}
            </div>
        </QuestionSection>
    );
};
