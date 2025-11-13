import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useMemoryReconstructionEvaluation } from './hooks/useMemoryReconstructionEvaluation';
import ImageRecognitionQuestion from './components/ImageRecognitionQuestion';
import ObjectiveQuestions from './components/ObjectiveQuestions';
import ProgressBar from './components/ProgressBar';
import styles from './MemoryEvaluation.module.css';

const MemoryEvaluation = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { t } = useTranslation();
    const { sessionData } = location.state || {};

    const [currentStep, setCurrentStep] = useState(0);
    const [isSaving, setIsSaving] = useState(false);

    // Use Memory Reconstruction evaluation hook
    const {
        loading: evaluationLoading,
        saveSelectImageAnswer,
        saveObjectiveAnswer,
        completeEvaluation,
    } = useMemoryReconstructionEvaluation(sessionData?.sessionId);

    // Perguntas objetivas - mapeadas para os tipos do banco
    // TODO: Perguntas serão geradas por IA futuramente
    const objectiveQuestions = [
        { 
            id: 'environment',
            type: 'environment', 
            text: 'Como era o ambiente da história?', 
            questionType: 'multiple-choice',
            options: ['Aberto', 'Fechado', 'Urbano', 'Rural'],
            correctOption: 'Aberto'
        },
        { 
            id: 'period',
            type: 'period', 
            text: 'Que parte do dia era?', 
            questionType: 'multiple-choice', 
            options: ['Manhã', 'Tarde', 'Noite'],
            correctOption: 'Tarde'
        },
        { 
            id: 'emotion',
            type: 'emotion', 
            text: 'Qual emoção foi predominante na história?', 
            questionType: 'multiple-choice',
            options: ['Felicidade', 'Tristeza', 'Raiva', 'Surpresa', 'Nojo'],
            correctOption: 'Felicidade'
        }
    ];

    const totalSteps = (sessionData?.phase1?.sections?.length || 0) + objectiveQuestions.length;

    useEffect(() => {
        // Verificar se temos dados da sessão
        if (!sessionData) {
            alert(t('evaluation.sessionNotFound') || 'Dados da sessão não encontrados. Redirecionando...');
            navigate('/memory-reconstruction');
        }
    }, [sessionData, navigate, t]);

    const handleImageRecognitionAnswer = async (sectionId, chosenImageId, distractor0Id, distractor1Id, timeSpent) => {
        setIsSaving(true);
        try {
            await saveSelectImageAnswer(
                sectionId,
                chosenImageId,
                distractor0Id,
                distractor1Id,
                timeSpent
            );
            setCurrentStep(prev => prev + 1);
        } catch (error) {
            console.error('Error saving answer:', error);
            if (error.response?.status === 409) {
                // Already answered, just move to next
                alert(t('evaluation.alreadyAnswered') || 'Esta questão já foi respondida anteriormente.');
                setCurrentStep(prev => prev + 1);
            } else {
                alert(t('evaluation.errorSaving') || 'Erro ao salvar resposta. Tente novamente.');
            }
        } finally {
            setIsSaving(false);
        }
    };

    const handleObjectiveAnswer = async (questionType, options, selectedOption, correctOption, timeSpent) => {
        setIsSaving(true);
        try {
            await saveObjectiveAnswer(
                questionType,
                options,
                selectedOption,
                correctOption,
                timeSpent
            );
            setCurrentStep(prev => prev + 1);
        } catch (error) {
            console.error('Error saving answer:', error);
            alert(t('evaluation.errorSaving') || 'Erro ao salvar resposta. Tente novamente.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleSaveSession = async () => {
        setIsSaving(true);

        try {
            await completeEvaluation();
            alert(t('evaluation.sessionSaved') || 'Sessão salva com sucesso!');
            navigate('/sessions');
        } catch (error) {
            console.error('Erro ao salvar sessão:', error);
            alert(t('evaluation.errorSavingSession') || 'Erro ao salvar sessão. Tente novamente.');
        } finally {
            setIsSaving(false);
        }
    };

    const renderCurrentStep = () => {
        if (!sessionData?.phase1?.sections) {
            return <div>{t('evaluation.loading') || 'Carregando...'}</div>;
        }

        const numImageQuestions = sessionData.phase1.sections.length;

        // Fase 1: Perguntas de reconhecimento de imagem
        if (currentStep < numImageQuestions) {
            const section = sessionData.phase1.sections[currentStep];
            return (
                <ImageRecognitionQuestion
                    section={section}
                    sectionNumber={currentStep + 1}
                    totalSections={numImageQuestions}
                    onAnswer={handleImageRecognitionAnswer}
                />
            );
        }

        // Fase 2: Perguntas objetivas
        const questionIndex = currentStep - numImageQuestions;
        if (questionIndex < objectiveQuestions.length) {
            const question = objectiveQuestions[questionIndex];
            return (
                <ObjectiveQuestions
                    question={question}
                    questionNumber={questionIndex + 1}
                    totalQuestions={objectiveQuestions.length}
                    onAnswer={handleObjectiveAnswer}
                />
            );
        }

        // Fase 3: Finalização
        return (
            <div className={styles.completion}>
                <div className={styles.completionCard}>
                    <h2>{t('evaluation.completed') || 'Avaliação Completa!'}</h2>
                    <p>{t('evaluation.completedMessage') || 'Obrigado por completar a avaliação. Clique no botão abaixo para salvar sua sessão.'}</p>
                    <button 
                        onClick={handleSaveSession}
                        className={styles.saveButton}
                        disabled={isSaving}
                    >
                        {isSaving 
                            ? (t('evaluation.saving') || 'Salvando...') 
                            : (t('evaluation.saveSession') || 'Salvar Sessão')
                        }
                    </button>
                </div>
            </div>
        );
    };

    if (!sessionData) {
        return null;
    }

    if (evaluationLoading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    {t('evaluation.initializing') || 'Inicializando avaliação...'}
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>{t('evaluation.title') || 'Avaliação - Memory Reconstruction'}</h1>
                <ProgressBar current={currentStep + 1} total={totalSteps} />
            </div>
            
            <div className={styles.content}>
                {isSaving && (
                    <div className={styles.savingIndicator}>
                        {t('evaluation.saving') || 'Salvando resposta...'}
                    </div>
                )}
                {renderCurrentStep()}
            </div>
        </div>
    );
};

export default MemoryEvaluation;
