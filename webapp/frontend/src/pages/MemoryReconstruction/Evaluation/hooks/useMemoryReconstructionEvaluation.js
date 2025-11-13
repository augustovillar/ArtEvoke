import { useState, useEffect, useCallback } from 'react';
import { millisecondsToTimeString } from '../../../../utils/timeFormatter';

/**
 * Hook to manage Memory Reconstruction evaluation progress and answer submission
 */
export const useMemoryReconstructionEvaluation = (sessionId) => {
    const [evaluationId, setEvaluationId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [progress, setProgress] = useState(null);

    // Function to fetch progress
    const fetchProgress = useCallback(async () => {
        if (!sessionId) return null;
        
        const token = localStorage.getItem('token');
        const progressResponse = await fetch(
            `/api/evaluation/progress/${sessionId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        if (!progressResponse.ok) {
            throw new Error(`HTTP error! status: ${progressResponse.status}`);
        }

        const progressData = await progressResponse.json();
        setProgress(progressData);
        return progressData;
    }, [sessionId]);

    // Initialize evaluation and get progress on mount
    useEffect(() => {
        if (!sessionId) {
            setLoading(false);
            return;
        }

        const initializeEvaluation = async () => {
            try {
                setLoading(true);
                
                // Fetch progress (evaluation should already exist from button click)
                const progressData = await fetchProgress();

                if (progressData && progressData.evaluation_started) {
                    setEvaluationId(progressData.eval_id);
                } else {
                    throw new Error('Evaluation not found - should have been created');
                }
            } catch (err) {
                console.error('[Evaluation Hook] Error initializing evaluation:', err);
            } finally {
                setLoading(false);
            }
        };

        initializeEvaluation();
    }, [sessionId, fetchProgress]);

    /**
     * Save a select image question answer
     */
    const saveSelectImageAnswer = async (sectionId, imageSelectedId, distractor0Id, distractor1Id, elapsedTime) => {
        const token = localStorage.getItem('token');
        
        const response = await fetch(
            `/api/evaluation/memory-reconstruction/select-image-question`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    eval_id: evaluationId,
                    section_id: sectionId,
                    image_selected_id: imageSelectedId,
                    image_distractor_0_id: distractor0Id,
                    image_distractor_1_id: distractor1Id,
                    elapsed_time: millisecondsToTimeString(elapsedTime)
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Refresh progress after saving
        await fetchProgress();
        
        return result;
    };

    /**
     * Save an objective question answer
     */
    const saveObjectiveAnswer = async (questionType, options, selectedOption, correctOption, elapsedTime) => {
        const token = localStorage.getItem('token');
        
        const response = await fetch(
            `/api/evaluation/objective-question`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    eval_id: evaluationId,
                    question_type: questionType,
                    options: options,
                    selected_option: selectedOption,
                    correct_option: correctOption,
                    elapsed_time: millisecondsToTimeString(elapsedTime)
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Refresh progress after saving
        await fetchProgress();
        
        return result;
    };

    /**
     * Complete the evaluation
     */
    const completeEvaluation = async () => {
        const token = localStorage.getItem('token');
        
        const response = await fetch(
            `/api/evaluation/memory-reconstruction/complete/${sessionId}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    };

    return {
        evaluationId,
        loading,
        progress,
        refreshProgress: fetchProgress,
        saveSelectImageAnswer,
        saveObjectiveAnswer,
        completeEvaluation,
    };
};
