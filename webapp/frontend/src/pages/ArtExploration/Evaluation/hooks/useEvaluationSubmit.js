import { useState } from 'react';

export const useEvaluationSubmit = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createEvaluation = async (sessionId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/evaluation/create?session_id=${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to create evaluation');
      }

      const data = await response.json();
      return data.id;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const submitStoryOpenQuestion = async (evalId, text, elapsedTime) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/evaluation/art-exploration/story-open-question', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eval_id: evalId,
          text,
          elapsed_time: elapsedTime,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit story question');
      }

      const data = await response.json();
      return data.question_id;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const fetchChronologyEvents = async (evalId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/evaluation/art-exploration/chronology-events/${evalId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch chronology events');
      }

      const data = await response.json();
      return data.events;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const submitChronologicalOrderQuestion = async (evalId, selectedOptions, elapsedTime) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/evaluation/art-exploration/chronological-order-question', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eval_id: evalId,
          selected_option_0: selectedOptions[0] || null,
          selected_option_1: selectedOptions[1] || null,
          selected_option_2: selectedOptions[2] || null,
          selected_option_3: selectedOptions[3] || null,
          elapsed_time: elapsedTime,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit chronological order question');
      }

      const data = await response.json();
      return data.question_id;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const submitObjectiveQuestion = async (evalId, questionType, options, selectedOption, correctOption, elapsedTime) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/evaluation/objective-question', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eval_id: evalId,
          question_type: questionType,
          options: options,
          selected_option: selectedOption,
          correct_option: correctOption,
          elapsed_time: elapsedTime,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit objective question');
      }

      const data = await response.json();
      return data.id;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProgress = async (sessionId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/evaluation/progress/${sessionId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch progress');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    createEvaluation,
    submitStoryOpenQuestion,
    fetchChronologyEvents,
    submitChronologicalOrderQuestion,
    submitObjectiveQuestion,
    fetchProgress,
    isLoading,
    error,
  };
};
