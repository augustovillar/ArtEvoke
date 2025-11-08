import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { StoryWritingQuestion, ChronologyOrderQuestion } from './components';
// Reuse shared components from Memory Reconstruction evaluation
import ObjectiveQuestions from '../../MemoryReconstruction/Evaluation/components/ObjectiveQuestions';
import ProgressBar from '../../MemoryReconstruction/Evaluation/components/ProgressBar';
import styles from './ArtEvaluation.module.css';

const ArtEvaluation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation('common');
  const { sessionData } = location.state || {};

  const [currentStep, setCurrentStep] = useState(0);
  const [evaluationData, setEvaluationData] = useState({
    storyWriting: null,
    chronologyOrder: null,
    objectiveQuestions: []
  });
  const [isSaving, setIsSaving] = useState(false);

  // Example objective questions (can be adapted per UX research)
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

  const totalSteps = 2 + objectiveQuestions.length; // 1 story writing + 1 chronology + objective questions

  useEffect(() => {
    if (!sessionData) {
      console.error('No sessionData found in location.state');
      alert('Dados da sessão não encontrados. Redirecionando...');
      navigate('/sessions');
    } else {
      console.log('SessionData found, proceeding with evaluation');
    }
  }, [sessionData, navigate]);

  const handleStoryWritingAnswer = (questionId, story, timeSpent) => {
    const storyAnswer = { questionId, story, timeSpent };
    setEvaluationData(prev => ({ ...prev, storyWriting: storyAnswer }));
    setCurrentStep(prev => prev + 1);
  };

  const handleChronologyOrderAnswer = (questionId, answer, timeSpent) => {
    const chronologyAnswer = { questionId, ...answer, timeSpent };
    setEvaluationData(prev => ({ ...prev, chronologyOrder: chronologyAnswer }));
    setCurrentStep(prev => prev + 1);
  };

  const handleObjectiveAnswer = (questionId, answer, timeSpent) => {
    const newAnswer = { questionId, answer, timeSpent };
    setEvaluationData(prev => ({ ...prev, objectiveQuestions: [...prev.objectiveQuestions, newAnswer] }));
    setCurrentStep(prev => prev + 1);
  };

  const handleSaveSession = async () => {
    setIsSaving(true);
    const completeSession = { ...sessionData, evaluation: evaluationData, completedAt: new Date().toISOString() };
    try {
      const token = localStorage.getItem('token');
      
      // Extract sessionId from sessionData
      const sessionId = sessionData.sessionId;
      
      if (sessionId) {
        // Mark session as completed
        await fetch(`/api/sessions/${sessionId}/complete`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
      
      // TODO: Implement API call to persist Art Exploration evaluation data
      // await fetch('/api/sessions/art-exploration/evaluation', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(completeSession) });
      console.log('Saving Art Exploration session:', completeSession);
      alert('Sessão salva com sucesso!');
      navigate('/sessions');
    } catch (err) {
      console.error('Erro ao salvar sessão de Art Exploration:', err);
      alert('Erro ao salvar sessão. Tente novamente.');
    } finally {
      setIsSaving(false);
    }
  };

  const renderCurrentStep = () => {
    if (!sessionData) { return <div>Carregando...</div>; }

    // Step 1: Story Writing
    if (currentStep === 0) {
      return (
        <StoryWritingQuestion
          onAnswer={handleStoryWritingAnswer}
        />
      );
    }

    // Step 2: Chronology Order
    if (currentStep === 1) {
      return (
        <ChronologyOrderQuestion
          onAnswer={handleChronologyOrderAnswer}
        />
      );
    }

    // Step 3+: Objective Questions
    const questionIndex = currentStep - 2;
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

    return (
      <div className={styles.completion}>
        <div className={styles.completionCard}>
          <h2>{t('evaluation.completed') || 'Recapitulação Completa!'}</h2>
          <p>{t('evaluation.completedMessage') || 'Obrigado por completar a recapitulação. Clique no botão abaixo para salvar sua sessão.'}</p>
          <button onClick={handleSaveSession} className={styles.saveButton} disabled={isSaving}>
            {isSaving ? (t('evaluation.saving') || 'Salvando...') : (t('evaluation.saveSession') || 'Salvar Sessão')}
          </button>
        </div>
      </div>
    );
  };

  if (!sessionData) return null;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>{t('evaluation.titleArtExploration') || 'Recapitulação - Art Exploration'}</h1>
        <ProgressBar current={currentStep + 1} total={totalSteps} />
      </div>
      <div className={styles.content}>{renderCurrentStep()}</div>
    </div>
  );
};

export default ArtEvaluation;
