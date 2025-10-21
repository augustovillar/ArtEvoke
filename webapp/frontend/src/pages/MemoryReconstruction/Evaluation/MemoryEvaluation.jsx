import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
    const [evaluationData, setEvaluationData] = useState({
        imageRecognition: [],
        objectiveQuestions: []
    });
    const [isSaving, setIsSaving] = useState(false);

    // Perguntas objetivas mock
    const objectiveQuestions = [
        { 
            id: 'q1', 
            text: 'Como era o ambiente da história?', 
            type: 'multiple-choice',
            options: ['Aberto', 'Fechado', 'Urbano', 'Rural' ]
        },
        { 
            id: 'q2', 
            text: 'Que parte do dia era?', 
            type: 'multiple-choice', 
            options: ['Manhã', 'Tarde', 'Noite']
        },
        { 
            id: 'q3', 
            text: 'Qual emoção foi predominante na história?', 
            type: 'multiple-choice',
            options: ['Felicidade', 'Tristeza', 'Raiva', 'Surpresa', 'Nojo']
        }
    ];

    const totalSteps = (sessionData?.phase1?.sections?.length || 0) + objectiveQuestions.length;

    useEffect(() => {
        // Verificar se temos dados da sessão
        if (!sessionData) {
            alert('Dados da sessão não encontrados. Redirecionando...');
            navigate('/memory-reconstruction');
        }
    }, [sessionData, navigate]);

    const handleImageRecognitionAnswer = (sectionId, chosenImageUrl, isCorrect, timeSpent) => {
        const newAnswer = {
            sectionId,
            chosenImageUrl,
            isCorrect,
            timeSpent
        };

        setEvaluationData(prev => ({
            ...prev,
            imageRecognition: [...prev.imageRecognition, newAnswer]
        }));

        setCurrentStep(prev => prev + 1);
    };

    const handleObjectiveAnswer = (questionId, answer, timeSpent) => {
        const newAnswer = {
            questionId,
            answer,
            timeSpent
        };

        setEvaluationData(prev => ({
            ...prev,
            objectiveQuestions: [...prev.objectiveQuestions, newAnswer]
        }));

        setCurrentStep(prev => prev + 1);
    };

    const handleSaveSession = async () => {
        setIsSaving(true);

        const completeSession = {
            ...sessionData,
            evaluation: evaluationData,
            completedAt: new Date().toISOString()
        };

        try {
            console.log('Salvando sessão completa:', completeSession);
            
            // TODO: Implementar chamada à API
            // const response = await fetch('/api/sessions/memory-reconstruction', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(completeSession)
            // });
            // 
            // if (!response.ok) {
            //     throw new Error('Erro ao salvar sessão');
            // }

            alert('Sessão salva com sucesso!');
            navigate('/profile'); // ou página de sucesso
        } catch (error) {
            console.error('Erro ao salvar sessão:', error);
            alert('Erro ao salvar sessão. Tente novamente.');
        } finally {
            setIsSaving(false);
        }
    };

    const renderCurrentStep = () => {
        if (!sessionData?.phase1?.sections) {
            return <div>Carregando...</div>;
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
            return (
                <ObjectiveQuestions
                    question={objectiveQuestions[questionIndex]}
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

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>{t('evaluation.title') || 'Avaliação - Memory Reconstruction'}</h1>
                <ProgressBar current={currentStep + 1} total={totalSteps} />
            </div>
            
            <div className={styles.content}>
                {renderCurrentStep()}
            </div>
        </div>
    );
};

export default MemoryEvaluation;
