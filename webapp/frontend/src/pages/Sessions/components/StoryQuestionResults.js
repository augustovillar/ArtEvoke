import React from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionSection, TimeSpentBadge } from './ResultsComponents';
import './ResultsLayout.css';

/**
 * StoryQuestion - Displays the open-ended story question result
 * Used by Art Exploration
 */
export const StoryQuestion = ({ question }) => {
    const { t } = useTranslation('common');

    return (
        <div className="question-card">
            <div className="question-header">
                <div className="header-left">
                    <h4>{t('results.storyQuestion')}</h4>
                </div>
                <TimeSpentBadge time={question.time_spent} />
            </div>

            <div className="story-question-content">
                <div className="story-prompt-section">
                    <h5>{t('results.prompt')}:</h5>
                    <p className="story-prompt-text">
                        {question.question_text || t('results.storyPromptDefault')}
                    </p>
                </div>

                <div className="story-answer-section">
                    <h5>{t('results.yourStory')}:</h5>
                    <div className="story-answer-box">
                        {question.user_answer ? (
                            <p className="story-answer-text">{question.user_answer}</p>
                        ) : (
                            <p className="story-no-answer">{t('results.noAnswerProvided')}</p>
                        )}
                    </div>
                </div>

                {question.reference_story && (
                    <div className="story-reference-section">
                        <h5>{t('results.referenceStory')}:</h5>
                        <div className="story-reference-box">
                            <p className="story-reference-text">{question.reference_story}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Story questions don't have a right/wrong answer, just completion */}
            <div className="story-completion-note">
                <span className="completion-icon">ℹ️</span>
                <span>{t('results.storyQuestionNote')}</span>
            </div>
        </div>
    );
};

/**
 * StoryQuestionSection - Wraps the story question
 */
export const StoryQuestionSection = ({ question }) => {
    const { t } = useTranslation('common');

    if (!question) return null;

    return (
        <QuestionSection 
            title={t('results.creativeStory')} 
            borderColor="green"
        >
            <StoryQuestion question={question} />
        </QuestionSection>
    );
};
