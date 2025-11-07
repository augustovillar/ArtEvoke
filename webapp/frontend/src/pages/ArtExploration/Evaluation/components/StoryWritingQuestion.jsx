import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import styles from './StoryWritingQuestion.module.css';

const StoryWritingQuestion = ({ onAnswer }) => {
    const { t } = useTranslation();
    const [story, setStory] = useState('');
    const [startTime] = useState(Date.now());

    const handleSubmit = () => {
        if (story.trim() === '') {
            alert(t('evaluation.pleaseWriteStory') || 'Por favor, escreva uma história antes de continuar.');
            return;
        }

        const timeSpent = Date.now() - startTime;
        
        // TODO: Integrate with speech evaluation software recommended by professor
        // This story text should be analyzed using discourse analysis tools
        
        onAnswer('story-writing', story.trim(), timeSpent);
    };

    const questionText = t('evaluation.storyWritingInstruction') || 
        'Tente recontar a história que você recebeu anteriormente com suas palavras, seja o mais rico possível em detalhes.';

    return (
        <div className={styles.container}>
            <div className={styles.questionHeader}>
                <h2>
                    {t('evaluation.storyWritingTitle') || 'Escreva Sua História'}
                    <QuestionReadAloudButton 
                        text={`${t('evaluation.storyWritingTitle') || 'Escreva Sua História'}. ${questionText}`}
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
                    placeholder={t('evaluation.storyPlaceholder') || 'Comece a escrever sua história aqui...'}
                />
                <div className={styles.charCount}>
                    {story.length} {t('evaluation.characters') || 'caracteres'}
                </div>
            </div>

            <div className={styles.buttonContainer}>
                <button
                    onClick={handleSubmit}
                    className={styles.submitButton}
                    disabled={story.trim() === ''}
                >
                    {t('evaluation.continueToQuestions') || 'Continuar para Perguntas'}
                </button>
            </div>
        </div>
    );
};

export default StoryWritingQuestion;