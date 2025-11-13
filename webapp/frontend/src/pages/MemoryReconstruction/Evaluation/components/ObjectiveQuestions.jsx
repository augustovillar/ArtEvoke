import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionReadAloudButton } from '../../../../components/ui';
import styles from './ObjectiveQuestions.module.css';

const ObjectiveQuestions = ({ question, questionNumber, totalQuestions, onAnswer }) => {
    const { t } = useTranslation();
    const [answer, setAnswer] = useState('');
    const [startTime, setStartTime] = useState(Date.now());

    // Reset state when question changes
    useEffect(() => {
        if (question?.type === 'multi-select') {
            setAnswer([]);
        } else {
            setAnswer('');
        }
        setStartTime(Date.now());
    }, [question?.id, question?.type]);

    const handleSubmit = () => {
        const isValid = (() => {
            if (question.questionType === 'text') return typeof answer === 'string' && answer.trim() !== '';
            if (question.questionType === 'multi-select') return Array.isArray(answer) && answer.length > 0;
            if (typeof answer === 'string') return answer.trim() !== '';
            return !!answer;
        })();

        if (!isValid) {
            alert(t('evaluation.pleaseAnswer') || 'Por favor, responda a pergunta antes de continuar.');
            return;
        }

        const timeSpent = Date.now() - startTime;
        
        // Call onAnswer with the format expected by the API
        onAnswer(
            question.type,  // question type (environment, period, emotion)
            question.options,  // all options
            answer,  // selected option
            question.correctOption,  // correct option
            timeSpent
        );
    };

    const renderQuestionInput = () => {
        switch (question.questionType) {
            case 'scale':
                return (
                    <div className={styles.scaleContainer}>
                        <div className={styles.scaleOptions}>
                            {question.labels.map((label, index) => (
                                <label key={index} className={styles.scaleOption}>
                                    <input
                                        type="radio"
                                        name={`question-${question.id}`}
                                        value={index + 1}
                                        checked={answer === String(index + 1)}
                                        onChange={(e) => setAnswer(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    <span className={styles.scaleLabel}>
                                        <span className={styles.scaleNumber}>{index + 1}</span>
                                        <span className={styles.scaleLabelText}>{label}</span>
                                    </span>
                                </label>
                            ))}
                        </div>
                    </div>
                );

            case 'multiple-choice': // Seleção única via alternativas fornecidas
                return (
                    <div className={styles.optionsContainer}>
                        {(question.options || []).map((opt, index) => (
                            <label key={index} className={styles.optionItem}>
                                <input
                                    type="radio"
                                    name={`question-${question.id}`}
                                    value={String(opt.value ?? opt)}
                                    checked={answer === String(opt.value ?? opt)}
                                    onChange={(e) => setAnswer(e.target.value)}
                                    className={styles.radioInput}
                                />
                                <span className={styles.optionLabelText}>{String(opt.label ?? opt)}</span>
                            </label>
                        ))}
                    </div>
                );

            case 'multi-select': // Seleção múltipla via alternativas fornecidas
                return (
                    <div className={styles.optionsContainer}>
                        {(question.options || []).map((opt, index) => {
                            const value = String(opt.value ?? opt);
                            const checked = Array.isArray(answer) && answer.includes(value);
                            const toggle = () => {
                                setAnswer(prev => {
                                    const prevArr = Array.isArray(prev) ? prev : [];
                                    if (prevArr.includes(value)) {
                                        return prevArr.filter(v => v !== value);
                                    }
                                    return [...prevArr, value];
                                });
                            };
                            return (
                                <label key={index} className={styles.optionItem}>
                                    <input
                                        type="checkbox"
                                        name={`question-${question.id}`}
                                        value={value}
                                        checked={checked}
                                        onChange={toggle}
                                        className={styles.checkboxInput}
                                    />
                                    <span className={styles.optionLabelText}>{String(opt.label ?? opt)}</span>
                                </label>
                            );
                        })}
                    </div>
                );

            case 'yes-no':
                return (
                    <div className={styles.yesNoContainer}>
                        <label className={styles.yesNoOption}>
                            <input
                                type="radio"
                                name={`question-${question.id}`}
                                value="yes"
                                checked={answer === 'yes'}
                                onChange={(e) => setAnswer(e.target.value)}
                                className={styles.radioInput}
                            />
                            <span className={styles.optionLabel}>
                                {t('evaluation.yes') || 'Sim'}
                            </span>
                        </label>
                        <label className={styles.yesNoOption}>
                            <input
                                type="radio"
                                name={`question-${question.id}`}
                                value="no"
                                checked={answer === 'no'}
                                onChange={(e) => setAnswer(e.target.value)}
                                className={styles.radioInput}
                            />
                            <span className={styles.optionLabel}>
                                {t('evaluation.no') || 'Não'}
                            </span>
                        </label>
                    </div>
                );

            case 'text':
                return (
                    <div className={styles.textContainer}>
                        <textarea
                            value={answer}
                            onChange={(e) => setAnswer(e.target.value)}
                            className={styles.textarea}
                            rows="5"
                            placeholder={t('evaluation.textPlaceholder') || 'Digite sua resposta aqui...'}
                        />
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.questionHeader}>
                <h2>
                    {t('evaluation.question') || 'Pergunta'} {questionNumber}/{totalQuestions}
                    <QuestionReadAloudButton 
                        text={`${t('evaluation.question') || 'Pergunta'} ${questionNumber} de ${totalQuestions}. ${question.text}`}
                    />
                </h2>
            </div>

            <div className={styles.questionText}>
                <p>{question.text}</p>
            </div>

            <div className={styles.answerSection}>
                {renderQuestionInput()}
            </div>

            <div className={styles.buttonContainer}>
                <button
                    onClick={handleSubmit}
                    className={styles.submitButton}
                    disabled={(() => {
                        if (question.questionType === 'text') return !(typeof answer === 'string' && answer.trim() !== '');
                        if (question.questionType === 'multi-select') return !(Array.isArray(answer) && answer.length > 0);
                        if (typeof answer === 'string') return answer.trim() === '';
                        return !answer;
                    })()}
                >
                    {questionNumber === totalQuestions
                        ? (t('evaluation.finish') || 'Finalizar')
                        : (t('evaluation.nextQuestion') || 'Próxima Pergunta')
                    }
                </button>
            </div>
        </div>
    );
};

export default ObjectiveQuestions;
