import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import SpeechInput from '../../../../features/speech';
import styles from './StoryWritingQuestion.module.css';

const StoryWritingQuestion = ({ onAnswer, isSubmitting = false }) => {
    const { t } = useTranslation();
    const [story, setStory] = useState('');
    const [startTime] = useState(Date.now());

    const handleSubmit = () => {
        if (story.trim() === '') {
            alert(t('evaluation.pleaseWriteStory'));
            return;
        }

        const timeSpent = Date.now() - startTime;
        onAnswer('story-writing', story.trim(), timeSpent);
    };

    const questionText = t('evaluation.storyWritingInstruction') ;

    return (
        <div className={styles.container}>
            <div className={styles.questionHeader}>
                <h2>
                    {t('evaluation.storyWritingTitle')}
                    <QuestionReadAloudButton 
                        text={`${t('evaluation.storyWritingTitle')}. ${questionText}`}
                    />
                </h2>
            </div>

            <div className={styles.instructionSection}>
                <p className={styles.instruction}>
                    {questionText}
                </p>
            </div>

            <div className={styles.textareaContainer}>
                <textarea
                    value={story}
                    onChange={(e) => setStory(e.target.value)}
                    className={styles.storyTextarea}
                    rows="12"
                    placeholder={t('evaluation.storyPlaceholder')}
                />
                <div className={styles.charCount}>
                    {story.length} {t('evaluation.characters')}
                </div>
                <SpeechInput onChange={setStory} initialValue={story} improveText={false} />
            </div>

            <div className={styles.buttonContainer}>
                <button
                    onClick={handleSubmit}
                    className={styles.submitButton}
                    disabled={story.trim() === '' || isSubmitting}
                >
                    {isSubmitting 
                        ? (t('evaluation.submitting') || 'Enviando...')
                        : (t('evaluation.continueToQuestions') || 'Continuar para Perguntas')
                    }
                </button>
            </div>
        </div>
    );
};

export default StoryWritingQuestion;