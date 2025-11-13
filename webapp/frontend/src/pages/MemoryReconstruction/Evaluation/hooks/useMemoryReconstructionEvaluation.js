import { useState, useEffect } from 'react';

/**
 * Hook to manage Memory Reconstruction evaluation progress and answer submission
 */
export const useMemoryReconstructionEvaluation = (sessionId) => {
    const [evaluationId, setEvaluationId] = useState(null);
    const [loading, setLoading] = useState(true);

    // Initialize evaluation on mount
    useEffect(() => {
        if (!sessionId) {
            setLoading(false);
            return;
        }

        const initializeEvaluation = async () => {
            try {
                setLoading(true);
                const token = localStorage.getItem('token');
                
                // Create evaluation record
                const response = await fetch(
                    `/api/evaluation/memory-reconstruction/start/${sessionId}`,
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

                const data = await response.json();
                setEvaluationId(data.eval_id);
            } catch (err) {
                console.error('[Evaluation Hook] Error initializing evaluation:', err);
            } finally {
                setLoading(false);
            }
        };

        initializeEvaluation();
    }, [sessionId]);

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
                    elapsed_time: elapsedTime
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    };

    /**
     * Save an objective question answer
     */
    const saveObjectiveAnswer = async (questionType, options, selectedOption, correctOption, elapsedTime) => {
        const token = localStorage.getItem('token');
        
        const response = await fetch(
            `/api/evaluation/memory-reconstruction/objective-question`,
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
                    elapsed_time: elapsedTime
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
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
        saveSelectImageAnswer,
        saveObjectiveAnswer,
        completeEvaluation,
    };
};
