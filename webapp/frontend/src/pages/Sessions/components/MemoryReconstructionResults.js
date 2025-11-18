import React from 'react';
import { useTranslation } from 'react-i18next';
import ResultsLayout from './ResultsLayout';
import { ImageSelectionQuestionsSection } from './ImageSelectionResults';
import { ObjectiveQuestionsSection } from './ObjectiveQuestionsResults';
import './ResultsLayout.css';

const MemoryReconstructionResults = ({ data }) => {
    const { t } = useTranslation('common');

    // Prepare summary cards data
    const summaryCards = [
        {
            title: t('results.summary.imageQuestions'),
            correct: data.correct_image_answers,
            total: data.total_image_questions,
            accuracy: data.image_accuracy,
            color: 'blue'
        },
        {
            title: t('results.summary.objectiveQuestions'),
            correct: data.correct_objective_answers,
            total: data.total_objective_questions,
            accuracy: data.objective_accuracy,
            color: 'purple'
        },
        {
            title: t('results.summary.overallAccuracy'),
            accuracy: data.overall_accuracy,
            color: 'gradient',
            isOverall: true
        }
    ];

    return (
        <ResultsLayout
            title={t('results.title')}
            dataset={data.dataset}
            language={data.language}
            story={data.story}
            summaryCards={summaryCards}
        >
            {/* Image Recognition Questions */}
            <ImageSelectionQuestionsSection questions={data.image_questions} />

            {/* Objective Questions */}
            <ObjectiveQuestionsSection questions={data.objective_questions} />
        </ResultsLayout>
    );
};

export default MemoryReconstructionResults;
