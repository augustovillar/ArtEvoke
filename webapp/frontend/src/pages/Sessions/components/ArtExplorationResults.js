import React from 'react';
import { useTranslation } from 'react-i18next';
import './ArtExplorationResults.css';

const ArtExplorationResults = ({ data }) => {
    const { t } = useTranslation('common');

    return (
        <div className="art-exploration-results">
            <div className="results-placeholder">
                <h2>{t('results.artExploration.notImplemented')}</h2>
                <p>{data.message || t('results.artExploration.comingSoon')}</p>
            </div>
        </div>
    );
};

export default ArtExplorationResults;
