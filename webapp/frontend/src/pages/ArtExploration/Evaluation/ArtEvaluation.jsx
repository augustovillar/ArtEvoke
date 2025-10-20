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
      text: 'Como você descreveria o tema principal das imagens selecionadas?',
      type: 'text'
    },
    {
      id: 'q2',
      text: 'As imagens escolhidas evocaram alguma emoção específica?',
      type: 'yes-no'
    },
    {
      id: 'q3',
      text: 'Quais estilos melhor descrevem as imagens escolhidas?',
      type: 'multi-select',
      options: ['Realismo', 'Impressionismo', 'Abstrato', 'Expressionismo', 'Surrealismo']
    }
  ];

  const totalSteps = 2 + objectiveQuestions.length; // 1 story writing + 1 chronology + objective questions

  useEffect(() => {
    if (!sessionData) {
      alert('Dados da sessão não encontrados. Redirecionando...');
      navigate('/artsearch');
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
      // TODO: Implement API call to persist Art Exploration session
      // await fetch('/api/sessions/art-exploration', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(completeSession) });
      console.log('Saving Art Exploration session:', completeSession);
      alert('Sessão salva com sucesso!');
      navigate('/profile');
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
          <h2>{t('evaluation.completed') || 'Avaliação Completa!'}</h2>
          <p>{t('evaluation.completedMessage') || 'Obrigado por completar a avaliação. Clique no botão abaixo para salvar sua sessão.'}</p>
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
        <h1>{t('evaluation.titleArtExploration') || 'Avaliação - Art Exploration'}</h1>
        <ProgressBar current={currentStep + 1} total={totalSteps} />
      </div>
      <div className={styles.content}>{renderCurrentStep()}</div>
    </div>
  );
};

export default ArtEvaluation;
