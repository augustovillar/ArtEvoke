import React from 'react';
import { useTranslation } from 'react-i18next';
import ResultsLayout from './ResultsLayout';
import { StoryQuestionSection } from './StoryQuestionResults';
import { ChronologicalOrderSection } from './ChronologicalOrderResults';
import { ObjectiveQuestionsSection } from './ObjectiveQuestionsResults';
import './ResultsLayout.css';

const ArtExplorationResults = ({ data }) => {
    const { t } = useTranslation('common');

    // Prepare summary cards data
    const summaryCards = [
        {
            title: t('results.summary.chronologicalOrder'),
            correct: data.chronological_positions_correct,
            total: data.chronological_total_positions,
            accuracy: data.chronological_accuracy,
            color: 'purple'
        },
        {
            title: t('results.summary.objectiveQuestions'),
            correct: data.correct_objective_answers,
            total: data.total_objective_questions,
            accuracy: data.objective_accuracy,
            color: 'blue'
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
            {/* Story Question */}
            <StoryQuestionSection question={data.story_question} />

            {/* Chronological Order */}
            <ChronologicalOrderSection question={data.chronological_order_question} />

            {/* Objective Questions */}
            <ObjectiveQuestionsSection questions={data.objective_questions} />
        </ResultsLayout>
    );
};

export default ArtExplorationResults;
