import React from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionSection, TimeSpentBadge, AnswerSummary } from './ResultsComponents';
import './ResultsLayout.css';

/**
 * ImageSelectionQuestion - Displays a single image selection question result
 * Used by Memory Reconstruction
 */
export const ImageSelectionQuestion = ({ question, index, totalQuestions }) => {
    const { t } = useTranslation('common');

    return (
        <div className="question-card">
            <div className="question-header">
                <div className="header-left">
                    <h4>
                        {t('results.imageQuestion')} {index + 1} {t('results.of')} {totalQuestions}
                    </h4>
                </div>
                <TimeSpentBadge time={question.time_spent} />
            </div>

            <div className="section-text-box">
                <p>{question.section_text}</p>
            </div>

            <div className="images-grid">
                {question.shown_images.map((image, imgIndex) => {
                    const isUserSelected = image.id === question.user_selected_image_id;
                    const isCorrect = image.id === question.correct_image_id;
                    const isDistractor = question.distractor_images.some(d => d.id === image.id);

                    let cardClass = 'image-card';
                    if (isUserSelected && isCorrect) {
                        cardClass += ' image-card-user-correct';
                    } else if (isUserSelected) {
                        cardClass += ' image-card-user-incorrect';
                    } else if (isCorrect) {
                        cardClass += ' image-card-correct';
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
                                <div className="image-badge badge-user">
                                    {isCorrect ? '✓' : '✗'} {t('results.yourAnswer')}
                                </div>
                            )}
                            {isCorrect && !isUserSelected && (
                                <div className="image-badge badge-correct">
                                    ✓ {t('results.correctAnswer')}
                                </div>
                            )}
                            {isDistractor && (
                                <div className="image-badge badge-distractor">
                                    {t('results.distractor')}
                                </div>
                            )}
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
 * ImageSelectionQuestionsSection - Groups all image selection questions
 */
export const ImageSelectionQuestionsSection = ({ questions }) => {
    const { t } = useTranslation('common');

    if (!questions || questions.length === 0) return null;

    return (
        <QuestionSection 
            title={t('results.imageRecognitionQuestions')} 
            borderColor="blue"
        >
            <div className="questions-list">
                {questions.map((question, index) => (
                    <ImageSelectionQuestion 
                        key={index} 
                        question={question} 
                        index={index}
                        totalQuestions={questions.length}
                    />
                ))}
            </div>
        </QuestionSection>
    );
};
