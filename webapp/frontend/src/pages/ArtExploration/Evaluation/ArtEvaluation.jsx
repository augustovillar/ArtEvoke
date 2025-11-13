import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { StoryWritingQuestion, ChronologyOrderQuestion } from './components';
import { useEvaluationSubmit } from './hooks';
import ObjectiveQuestions from '../../MemoryReconstruction/Evaluation/components/ObjectiveQuestions';
import ProgressBar from '../../MemoryReconstruction/Evaluation/components/ProgressBar';
import styles from './ArtEvaluation.module.css';

const ArtEvaluation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation('common');
  const { sessionData } = location.state || {};
  const { createEvaluation, submitStoryOpenQuestion, fetchChronologyEvents, submitChronologicalOrderQuestion, isLoading } = useEvaluationSubmit();
  const hasInitialized = useRef(false);

  const [currentStep, setCurrentStep] = useState(0);
  const [evalId, setEvalId] = useState(null);
  const [chronologyEvents, setChronologyEvents] = useState(null);
  const [evaluationData, setEvaluationData] = useState({
    storyWriting: null,
    chronologyOrder: null,
    objectiveQuestions: []
  });
  const [isSaving, setIsSaving] = useState(false);

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

  const totalSteps = 2 + objectiveQuestions.length;

  useEffect(() => {
    const initializeEvaluation = async () => {
      if (hasInitialized.current) return;
      hasInitialized.current = true;

      try {
        const sessionId = sessionData.sessionId;
        const evaluationId = await createEvaluation(sessionId);
        setEvalId(evaluationId);
      } catch (err) {
        console.error('Error creating evaluation:', err);
        alert(t('evaluation.errorInitializing'));
        navigate('/sessions');
      }
    };

    if (!sessionData) {
      console.error('No sessionData found in location.state');
      alert(t('evaluation.sessionDataNotFound'));
      navigate('/sessions');
    } else {
      initializeEvaluation();
    }
  }, [sessionData, navigate, createEvaluation, t]);

  const handleStoryWritingAnswer = async (questionId, story, timeSpent) => {
    try {
      const elapsedTimeFormatted = formatElapsedTime(timeSpent);
      const savedQuestionId = await submitStoryOpenQuestion(evalId, story, elapsedTimeFormatted);
      
      const storyAnswer = { questionId: savedQuestionId, story, timeSpent };
      setEvaluationData(prev => ({ ...prev, storyWriting: storyAnswer }));
      
      const events = await fetchChronologyEvents(evalId);
      setChronologyEvents(events);
      
      setCurrentStep(prev => prev + 1);
    } catch (err) {
      console.error('Error submitting story:', err);
      alert(t('evaluation.errorSavingStory'));
    }
  };

  const formatElapsedTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };

  const handleChronologyOrderAnswer = async (questionId, answer, timeSpent) => {
    try {
      const elapsedTimeFormatted = formatElapsedTime(timeSpent);
      const savedQuestionId = await submitChronologicalOrderQuestion(
        evalId, 
        answer.userOrder, 
        elapsedTimeFormatted
      );
      
      const chronologyAnswer = { questionId: savedQuestionId, ...answer, timeSpent };
      setEvaluationData(prev => ({ ...prev, chronologyOrder: chronologyAnswer }));
      setCurrentStep(prev => prev + 1);
    } catch (err) {
      console.error('Error submitting chronological order question:', err);
      alert(t('evaluation.errorSavingQuestion'));
    }
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
      alert(t('evaluation.completed'));
      navigate('/sessions');
    } catch (err) {
      console.error('Erro ao salvar sessão de Art Exploration:', err);
      alert(t('evaluation.errorSavingStory'));
    } finally {
      setIsSaving(false);
    }
  };

  const renderCurrentStep = () => {
    if (!sessionData) { return <div>{t('evaluation.loading')}</div>; }

    if (!evalId) {
      return <div>{t('evaluation.loading')}</div>;
    }

    if (currentStep === 0) {
      return (
        <StoryWritingQuestion
          onAnswer={handleStoryWritingAnswer}
          isSubmitting={isLoading}
        />
      );
    }

    // Step 2: Chronology Order
    if (currentStep === 1) {
      if (!chronologyEvents) {
        return <div>{t('evaluation.loading')}</div>;
      }
      
      return (
        <ChronologyOrderQuestion
          events={chronologyEvents}
          onAnswer={handleChronologyOrderAnswer}
          isSubmitting={isLoading}
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
          <h2>{t('evaluation.completed')}</h2>
          <p>{t('evaluation.completedMessage')}</p>
          <button onClick={handleSaveSession} className={styles.saveButton} disabled={isSaving}>
            {isSaving ? t('evaluation.saving') : t('evaluation.saveSession')}
          </button>
        </div>
      </div>
    );
  };

  if (!sessionData) return null;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>{t('evaluation.titleArtExploration')}</h1>
        <ProgressBar current={currentStep + 1} total={totalSteps} />
      </div>
      <div className={styles.content}>{renderCurrentStep()}</div>
    </div>
  );
};

export default ArtEvaluation;
